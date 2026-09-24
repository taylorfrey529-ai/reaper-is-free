#!/usr/bin/env python3
"""Offline, fail-closed vm-v1.1.0 instrument/NAM rehydration.

Default mode verifies durable-custody bytes only. --apply is required to write the
workspace. No network access, package installation, model substitution, or
REAPER project mutation is performed.
"""
import argparse
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

CHUNK = 8 * 1024 * 1024
BASE = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DURABLE = BASE / "config" / "durable-recovery-v1.1.0.json"
DEFAULT_PERMANENCE = BASE / "config" / "permanence-v1.1.0.json"
DEFAULT_VERIFIER = BASE / "bin" / "verify-durable-recovery-v1.1.0.py"


def fail(message):
    raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def digest_bytes(blob):
    return hashlib.sha256(blob).hexdigest()


def zip_member(zf, suffix=None):
    names = [
        n for n in zf.namelist()
        if not n.endswith("/") and (suffix is None or n.endswith(suffix))
    ]
    if len(names) != 1:
        fail("ZIP member selection failed: " + repr(names))
    return names[0]


def safe_zip_extract(zf, dest):
    dest = pathlib.Path(dest).resolve()
    for info in zf.infolist():
        p = pathlib.PurePosixPath(info.filename)
        if p.is_absolute() or ".." in p.parts:
            fail("unsafe ZIP path: " + info.filename)
        mode = (info.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            fail("ZIP symlink rejected: " + info.filename)
        target = (dest / pathlib.Path(*p.parts)).resolve()
        if target != dest and dest not in target.parents:
            fail("ZIP path escapes destination: " + info.filename)
    zf.extractall(dest)


def safe_tar_extract(tf, dest):
    dest = pathlib.Path(dest).resolve()
    for member in tf.getmembers():
        p = pathlib.PurePosixPath(member.name)
        if p.is_absolute() or ".." in p.parts:
            fail("unsafe TAR path: " + member.name)
        if member.issym() or member.islnk() or member.isdev():
            fail("TAR link/device rejected: " + member.name)
        target = (dest / pathlib.Path(*p.parts)).resolve()
        if target != dest and dest not in target.parents:
            fail("TAR path escapes destination: " + member.name)
    tf.extractall(dest)


def staged_file(staging, obj):
    p = pathlib.Path(staging) / obj["name"]
    if not p.is_file():
        fail("missing staged object: " + obj["name"])
    if obj.get("bytes") is not None and p.stat().st_size != obj["bytes"]:
        fail("staged size mismatch: " + obj["name"])
    if obj.get("wrapper_sha256") and sha256(p) != obj["wrapper_sha256"]:
        fail("staged wrapper hash mismatch: " + obj["name"])
    return p


def verify_durable_set(staging, durable_config, verifier):
    cmd = [
        sys.executable,
        str(verifier),
        "--staging", str(staging),
        "--config", str(durable_config),
    ]
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        fail("durable-custody verifier failed with exit " + str(proc.returncode))


def reaper_running(root):
    expected = str(pathlib.Path(root) / "apps" / "REAPER" / "reaper")
    proc_root = pathlib.Path("/proc")
    if not proc_root.is_dir():
        return False
    for p in proc_root.iterdir():
        if not p.name.isdigit():
            continue
        try:
            raw = (p / "cmdline").read_bytes()
        except OSError:
            continue
        if not raw:
            continue
        argv0 = raw.split(b"\0", 1)[0].decode(errors="ignore")
        if argv0 == expected:
            return True
    return False


def reconstruct_manifest_chunks(staging, asset, logical_key, output):
    manifest_wrapper = staged_file(staging, asset["manifest"])
    with zipfile.ZipFile(manifest_wrapper) as zf:
        manifest = json.loads(zf.read(zip_member(zf, "manifest.json")))
    objects = asset["drive_objects"]
    parts = manifest["parts"]
    if len(objects) != len(parts):
        fail("chunk count mismatch")
    h = hashlib.sha256()
    total = 0
    with pathlib.Path(output).open("wb") as sink:
        for obj, part in zip(objects, parts):
            wrapper = staged_file(staging, obj)
            with zipfile.ZipFile(wrapper) as zf:
                member = zip_member(zf)
                ph = hashlib.sha256()
                count = 0
                with zf.open(member) as src:
                    while True:
                        block = src.read(CHUNK)
                        if not block:
                            break
                        sink.write(block)
                        h.update(block)
                        ph.update(block)
                        count += len(block)
                        total += len(block)
            if pathlib.PurePosixPath(member).name != part["name"]:
                fail("inner part name mismatch: " + part["name"])
            if count != part["size"] or ph.hexdigest() != part["sha256"]:
                fail("inner part validation failed: " + part["name"])
    got = h.hexdigest()
    if got != manifest["logical_sha256"] or got != asset[logical_key]:
        fail("logical reconstruction hash mismatch")
    if total != manifest["logical_size"]:
        fail("logical reconstruction size mismatch")
    return pathlib.Path(output)


def reconstruct_metal(staging, asset, output):
    manifest_wrapper = staged_file(staging, asset["drive_manifest"])
    with zipfile.ZipFile(manifest_wrapper) as zf:
        sums = zf.read("SHA256SUMS").decode()
        recovery = zf.read("RECOVERY.txt").decode()
    expected = {}
    for line in sums.splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+(.+)$", line.strip())
        if m:
            expected[pathlib.PurePosixPath(m.group(2)).name] = m.group(1)
    logical = hashlib.sha256()
    with pathlib.Path(output).open("wb") as sink:
        for obj in asset["drive_objects"]:
            wrapper = staged_file(staging, obj)
            with zipfile.ZipFile(wrapper) as zf:
                member = zip_member(zf)
                name = pathlib.PurePosixPath(member).name
                ph = hashlib.sha256()
                with zf.open(member) as src:
                    while True:
                        block = src.read(CHUNK)
                        if not block:
                            break
                        sink.write(block)
                        ph.update(block)
                        logical.update(block)
            if expected.get(name) != ph.hexdigest():
                fail("Metal GTX part hash mismatch: " + name)
    got = logical.hexdigest()
    if got != asset["logical_archive_sha256"] or got not in recovery:
        fail("Metal GTX logical reconstruction mismatch")
    return pathlib.Path(output)


def read_inner_wrapper(staging, asset, suffix, expected_hash):
    wrapper = staged_file(staging, asset["drive_objects"][0])
    with zipfile.ZipFile(wrapper) as zf:
        member = zip_member(zf, suffix)
        blob = zf.read(member)
    if digest_bytes(blob) != expected_hash:
        fail("inner wrapper hash mismatch: " + suffix)
    return blob


def find_named_dir(root, name):
    hits = [p for p in pathlib.Path(root).rglob(name) if p.is_dir()]
    if len(hits) != 1:
        fail("expected one directory named %s, got %d" % (name, len(hits)))
    return hits[0]


def count_inventory(root, suffixes):
    suffixes = {s.lower() for s in suffixes}
    files = [p for p in pathlib.Path(root).rglob("*") if p.is_file() and p.suffix.lower() in suffixes]
    return len(files), sum(p.stat().st_size for p in files)


def find_ancestor_matching(start, stop, predicate):
    p = pathlib.Path(start)
    stop = pathlib.Path(stop).resolve()
    while True:
        if predicate(p):
            return p
        rp = p.resolve()
        if rp == stop or stop not in rp.parents:
            break
        p = p.parent
    fail("no extracted root matched the pinned inventory")


def copy_file(src, dst):
    dst = pathlib.Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def stage_sforzando(staging, durable, payload, scratch):
    asset = durable["assets"]["sforzando"]
    source_zip = read_inner_wrapper(
        staging, asset, "LINUX_plogue-sforzando_1.982_x86_64.zip", asset["source_archive_sha256"]
    )
    recovery = payload / "packages/gm2-runtimes/sforzando/LINUX_plogue-sforzando_1.982_x86_64.zip"
    recovery.parent.mkdir(parents=True, exist_ok=True)
    recovery.write_bytes(source_zip)

    source_dir = scratch / "sforzando-source"
    source_dir.mkdir()
    with zipfile.ZipFile(io.BytesIO(source_zip)) as zf:
        safe_zip_extract(zf, source_dir)
    debs = list(source_dir.rglob("plogue-sforzando_1.982_amd64.deb"))
    if len(debs) != 1:
        fail("sforzando DEB selection failed")
    debroot = scratch / "sforzando-debroot"
    debroot.mkdir()
    proc = subprocess.run(
        ["dpkg-deb", "-x", str(debs[0]), str(debroot)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        fail("dpkg-deb extraction failed")
    bundle = find_named_dir(debroot, "sforzando.vst3")
    target = payload / "home/.vst3/sforzando.vst3"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle, target)


def stage_avl(staging, durable, payload, scratch):
    asset = durable["assets"]["avldrums"]
    blob = read_inner_wrapper(staging, asset, "avldrums-exact.tar.gz", asset["recovery_tar_sha256"])
    recovery = payload / "packages/gm2-runtimes/avldrums/avldrums-exact-9389f16.tar.gz"
    recovery.parent.mkdir(parents=True, exist_ok=True)
    recovery.write_bytes(blob)
    extract = scratch / "avl"
    extract.mkdir()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        safe_tar_extract(tf, extract)
    bundle = find_named_dir(extract, "avldrums.lv2")
    target = payload / "home/.lv2/avldrums.lv2"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle, target)


def stage_blackblue(staging, durable, payload, scratch):
    asset = durable["assets"]["black_and_blue"]
    archive = reconstruct_manifest_chunks(
        staging, asset, "logical_tar_sha256", scratch / "blackblue.tar"
    )
    copy_file(archive, payload / "packages/source-archives/black-and-blue-basses-v1.1.0.tar")
    extract = scratch / "blackblue"
    extract.mkdir()
    with tarfile.open(archive, mode="r:") as tf:
        safe_tar_extract(tf, extract)
    dark_hits = list(extract.rglob("01-darkblack_keysw.sfz"))
    if len(dark_hits) != 1:
        fail("Dark Black program selection failed")

    def match(candidate):
        audio_count, audio_bytes = count_inventory(candidate, {".wav", ".flac", ".aif", ".aiff"})
        sfz_count, _ = count_inventory(candidate, {".sfz"})
        return (
            audio_count == asset["sample_files"]
            and audio_bytes == asset["sample_bytes"]
            and sfz_count == asset["sfz_files"]
        )

    root = find_ancestor_matching(dark_hits[0].parent, extract, match)
    target = payload / "instruments/Black-And-Blue-Basses-Upstream"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(root), str(target))


def stage_metal(staging, durable, permanence, payload, scratch):
    asset = durable["assets"]["metal_gtx"]
    pm = permanence["assets"]["metal_gtx"]
    archive = reconstruct_metal(staging, asset, scratch / "metal-gtx.tar.gz")
    extract = scratch / "metal-gtx"
    extract.mkdir()
    with tarfile.open(archive, mode="r:gz") as tf:
        safe_tar_extract(tf, extract)
    clean_hits = list(extract.rglob("03-METAL-GTX XTracking Clean DI.sfz"))
    if len(clean_hits) != 1:
        fail("Metal GTX Clean DI derivative is not present exactly once in durable archive")

    def match(candidate):
        audio_count, audio_bytes = count_inventory(candidate, {".wav", ".flac", ".aif", ".aiff"})
        sfz_count, sfz_bytes = count_inventory(candidate, {".sfz"})
        return (
            audio_count == pm["samples"]["files"]
            and audio_bytes == pm["samples"]["bytes"]
            and sfz_count == pm["sfz"]["files"]
            and sfz_bytes == pm["sfz"]["bytes"]
        )

    root = find_ancestor_matching(clean_hits[0].parent, extract, match)
    target = payload / "instruments/Metal-GTX"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(root), str(target))


def stage_vsco(staging, durable, payload, scratch):
    asset = durable["assets"]["vsco_2_ce"]
    archive = reconstruct_manifest_chunks(staging, asset, "archive_sha256", scratch / "vsco-2-ce-1.1.0.tar.gz")
    copy_file(archive, payload / "packages/source-archives/vsco-2-ce-1.1.0.tar.gz")
    extract = scratch / "vsco"
    extract.mkdir()
    with tarfile.open(archive, mode="r:gz") as tf:
        safe_tar_extract(tf, extract)
    hits = list(extract.rglob("ViolinEnsSusVib.sfz"))
    if not hits:
        fail("VSCO ViolinEnsSusVib.sfz not found")

    def match(candidate):
        sfz_count, _ = count_inventory(candidate, {".sfz"})
        wav_count, _ = count_inventory(candidate, {".wav"})
        names = {p.name for p in pathlib.Path(candidate).rglob("*.sfz") if p.is_file()}
        return (
            sfz_count == asset["sfz_files"]
            and wav_count == asset["wav_files"]
            and {"ViolinEnsSusVib.sfz", "CelloEnsSusVib.sfz", "FHornSus.sfz"} <= names
        )

    root = find_ancestor_matching(hits[0].parent, extract, match)
    version_target = payload / "instruments/VSCO-2-CE-1.1.0"
    version_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(root), str(version_target))
    stable = payload / "instruments/VSCO-2-CE"
    os.symlink("VSCO-2-CE-1.1.0", stable)


def stage_nam(staging, durable, payload, scratch):
    asset = durable["assets"]["nam"]
    wrapper = staged_file(staging, asset["drive_objects"][0])
    copy_file(wrapper, payload / "packages/gm2-runtimes/nam/astra-nam-gm2-linux.zip")
    with zipfile.ZipFile(wrapper) as zf:
        member = zip_member(zf, "astra-nam-gm2-linux.tar.gz")
        blob = zf.read(member)
    if digest_bytes(blob) != asset["inner_tar_sha256"]:
        fail("NAM inner TAR hash mismatch")
    extract = scratch / "nam"
    extract.mkdir()
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        safe_tar_extract(tf, extract)
    bundle = find_named_dir(extract, "neural_amp_modeler.lv2")
    target = payload / "home/.lv2/neural_amp_modeler.lv2"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle, target)

    obs = durable["assets"]["obsidian"]
    model = staged_file(staging, obs["drive_objects"][0])
    if sha256(model) != obs["model_sha256"]:
        fail("Obsidian model hash mismatch")
    copy_file(model, payload / "nam-models/Obsidian.nam")


def validate_payload(root, permanence):
    root = pathlib.Path(root)
    a = permanence["assets"]

    checks = [
        (a["sforzando"]["path"], a["sforzando"]["sha256"]),
        (a["sforzando"]["recovery"]["path"], a["sforzando"]["recovery"]["sha256"]),
        (a["avldrums"]["plugin_path"], a["avldrums"]["plugin_sha256"]),
        (a["avldrums"]["black_pearl_path"], a["avldrums"]["black_pearl_sha256"]),
        (a["avldrums"]["recovery"]["path"], a["avldrums"]["recovery"]["sha256"]),
        (a["black_and_blue"]["dark_black"]["path"], a["black_and_blue"]["dark_black"]["sha256"]),
        (a["black_and_blue"]["recovery"]["path"], a["black_and_blue"]["recovery"]["sha256"]),
        (a["metal_gtx"]["stock_xtracking"]["path"], a["metal_gtx"]["stock_xtracking"]["sha256"]),
        (a["metal_gtx"]["clean_di_xtracking"]["path"], a["metal_gtx"]["clean_di_xtracking"]["sha256"]),
        (a["vsco_2_ce"]["archive_path"], a["vsco_2_ce"]["archive_sha256"]),
        (a["nam"]["plugin_path"], a["nam"]["plugin_sha256"]),
        (a["nam"]["model_path"], a["nam"]["model_sha256"]),
    ]
    for rel, expected in checks:
        p = root / rel
        if not p.is_file() or sha256(p) != expected:
            fail("staged runtime hash mismatch: " + rel)

    count, size = count_inventory(root / a["black_and_blue"]["root"], {".wav", ".flac", ".aif", ".aiff"})
    if count != a["black_and_blue"]["samples"]["files"] or size != a["black_and_blue"]["samples"]["bytes"]:
        fail("Black & Blue staged sample inventory mismatch")
    count, size = count_inventory(root / a["black_and_blue"]["root"], {".sfz"})
    if count != a["black_and_blue"]["sfz"]["files"] or size != a["black_and_blue"]["sfz"]["bytes"]:
        fail("Black & Blue staged SFZ inventory mismatch")

    count, size = count_inventory(root / a["metal_gtx"]["root"], {".wav", ".flac", ".aif", ".aiff"})
    if count != a["metal_gtx"]["samples"]["files"] or size != a["metal_gtx"]["samples"]["bytes"]:
        fail("Metal GTX staged sample inventory mismatch")
    count, size = count_inventory(root / a["metal_gtx"]["root"], {".sfz"})
    if count != a["metal_gtx"]["sfz"]["files"] or size != a["metal_gtx"]["sfz"]["bytes"]:
        fail("Metal GTX staged SFZ inventory mismatch")

    vsco_root = root / a["vsco_2_ce"]["root"]
    sfz_count, _ = count_inventory(vsco_root, {".sfz"})
    wav_count, _ = count_inventory(vsco_root, {".wav"})
    if sfz_count != a["vsco_2_ce"]["sfz_files"] or wav_count != a["vsco_2_ce"]["wav_files"]:
        fail("VSCO staged inventory mismatch")
    names = {p.name for p in vsco_root.rglob("*.sfz") if p.is_file()}
    if not set(a["vsco_2_ce"]["patches"]) <= names:
        fail("VSCO required patch missing")
    stable = root / a["vsco_2_ce"]["stable_path"]
    if not stable.is_symlink() or stable.resolve() != vsco_root.resolve():
        fail("VSCO stable symlink mismatch")

    nam_recovery = root / a["nam"]["recovery_dir"] / "astra-nam-gm2-linux.zip"
    if not nam_recovery.is_file() or sha256(nam_recovery) != a["nam"]["recovery_artifact_sha256"]:
        fail("NAM recovery artifact mismatch")


def target_relpaths():
    return [
        pathlib.Path("home/.vst3/sforzando.vst3"),
        pathlib.Path("packages/gm2-runtimes/sforzando/LINUX_plogue-sforzando_1.982_x86_64.zip"),
        pathlib.Path("home/.lv2/avldrums.lv2"),
        pathlib.Path("packages/gm2-runtimes/avldrums/avldrums-exact-9389f16.tar.gz"),
        pathlib.Path("instruments/Black-And-Blue-Basses-Upstream"),
        pathlib.Path("packages/source-archives/black-and-blue-basses-v1.1.0.tar"),
        pathlib.Path("instruments/Metal-GTX"),
        pathlib.Path("instruments/VSCO-2-CE-1.1.0"),
        pathlib.Path("instruments/VSCO-2-CE"),
        pathlib.Path("packages/source-archives/vsco-2-ce-1.1.0.tar.gz"),
        pathlib.Path("home/.lv2/neural_amp_modeler.lv2"),
        pathlib.Path("packages/gm2-runtimes/nam/astra-nam-gm2-linux.zip"),
        pathlib.Path("nam-models/Obsidian.nam"),
    ]


def remove_path(path):
    path = pathlib.Path(path)
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def promote(payload, root, backup):
    rels = target_relpaths()
    moved_old = []
    installed = []
    try:
        for rel in rels:
            src = payload / rel
            if not (src.exists() or src.is_symlink()):
                fail("staged promotion target missing: " + str(rel))
            dst = root / rel
            if dst.exists() or dst.is_symlink():
                b = backup / rel
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(b))
                moved_old.append((rel, b))
        for rel in rels:
            src = payload / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.replace(src, dst)
            installed.append(rel)
    except Exception:
        for rel in reversed(installed):
            dst = root / rel
            if dst.exists() or dst.is_symlink():
                remove_path(dst)
        for rel, b in reversed(moved_old):
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if b.exists() or b.is_symlink():
                os.replace(b, dst)
        raise
    return rels


def rollback(root, backup, rels):
    for rel in reversed(rels):
        dst = root / rel
        if dst.exists() or dst.is_symlink():
            remove_path(dst)
        b = backup / rel
        if b.exists() or b.is_symlink():
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.replace(b, dst)


def main():
    ap = argparse.ArgumentParser(description="Offline vm-v1.1.0 durable rehydration")
    ap.add_argument("--staging", required=True, type=pathlib.Path, help="directory containing every Drive object named by the durable manifest")
    ap.add_argument("--root", type=pathlib.Path, default=pathlib.Path("/mnt/data/ubuntu-desktop-workspace"))
    ap.add_argument("--durable-config", type=pathlib.Path, default=DEFAULT_DURABLE)
    ap.add_argument("--permanence-config", type=pathlib.Path, default=DEFAULT_PERMANENCE)
    ap.add_argument("--verifier", type=pathlib.Path, default=DEFAULT_VERIFIER)
    ap.add_argument("--apply", action="store_true", help="write the workspace after full offline verification; default is verify-only")
    args = ap.parse_args()

    staging = args.staging.resolve()
    root = args.root.resolve()
    if not staging.is_dir():
        fail("staging directory missing: " + str(staging))
    if not root.is_dir():
        fail("workspace root missing: " + str(root))

    durable = json.loads(args.durable_config.read_text())
    permanence = json.loads(args.permanence_config.read_text())
    if durable.get("version") != "vm-v1.1.0" or permanence.get("version") != "vm-v1.1.0":
        fail("manifest version mismatch")

    verify_durable_set(staging, args.durable_config, args.verifier)
    print("PASS: all durable-custody bytes verified offline")

    if not args.apply:
        print("DRY RUN: no workspace bytes changed; re-run with --apply for an explicit cold restore")
        return 0

    if reaper_running(root):
        fail("REAPER is running; offline rehydration requires a cold workspace")

    work = pathlib.Path(tempfile.mkdtemp(prefix=".vm-v1.1.0-rehydrate-", dir=root))
    payload = work / "payload"
    scratch = work / "scratch"
    payload.mkdir()
    scratch.mkdir()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup = root / "recovery-backups" / "vm-v1.1.0" / stamp
    rels = []

    try:
        stage_sforzando(staging, durable, payload, scratch)
        stage_avl(staging, durable, payload, scratch)
        stage_blackblue(staging, durable, payload, scratch)
        stage_metal(staging, durable, permanence, payload, scratch)
        stage_vsco(staging, durable, payload, scratch)
        stage_nam(staging, durable, payload, scratch)
        validate_payload(payload, permanence)
        print("PASS: complete replacement payload validated before promotion")

        backup.mkdir(parents=True, exist_ok=False)
        rels = promote(payload, root, backup)
        try:
            validate_payload(root, permanence)
        except Exception:
            rollback(root, backup, rels)
            raise

        report = root / "logs" / "vm-v1.1.0-offline-rehydrate.txt"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "\n".join([
                "REAPER 7.79 - VM v1.1.0 OFFLINE REHYDRATION",
                "RESULT PASS",
                "policy=offline/fail-closed/explicit-apply/no-network/no-substitution",
                "staging=" + str(staging),
                "root=" + str(root),
                "backup=" + str(backup),
                "targets=" + str(len(rels)),
                "next=run install-v1.1.0.sh, permanence gate, REAPER live regression, and non-silent Virtual Apollo proof",
                "",
            ]),
            encoding="utf-8",
        )
        print("PASS: vm-v1.1.0 instrument/NAM runtime rehydrated")
        print("Backup:", backup)
        print("Report:", report)
        return 0
    finally:
        if work.exists():
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(3)
