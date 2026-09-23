#!/usr/bin/env bash
set -euo pipefail

ROOT=${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MANIFEST=${VM110_MANIFEST:-$HERE/config/permanence-v1.1.0.json}
REPORT=${1:-$ROOT/logs/vm-v1.1.0-permanence.txt}

mkdir -p "$(dirname "$REPORT")"

python3 - "$ROOT" "$MANIFEST" "$REPORT" <<'PY'
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
report_path = Path(sys.argv[3])

checks = []
def rec(label, ok, detail=""):
    checks.append((label, bool(ok), str(detail)))

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def resolve(spec):
    p = Path(spec)
    return p if p.is_absolute() else root / p

def hash_check(label, rel, expected):
    p = resolve(rel)
    if not p.is_file():
        rec(label, False, f"missing: {p}")
        return
    got = sha256(p)
    rec(label, got == expected, f"{got}  {p}")

def ext_stats(path, exts):
    files = [p for p in Path(path).rglob("*") if p.is_file() and p.suffix.lower() in exts]
    return len(files), sum(p.stat().st_size for p in files)

def deps_check(label, path):
    p = resolve(path)
    if not p.is_file():
        rec(label, False, f"missing: {p}")
        return
    try:
        cp = subprocess.run(["ldd", str(p)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    except FileNotFoundError:
        rec(label, False, "ldd unavailable")
        return
    rec(label, cp.returncode == 0 and "not found" not in cp.stdout, cp.stdout.strip().replace("\n", " | ")[:1200])

if not manifest_path.is_file():
    print(f"VM-V1.1.0 PERMANENCE: FAIL\nmanifest missing: {manifest_path}")
    raise SystemExit(2)

m = json.loads(manifest_path.read_text())
rec("manifest version", m.get("version") == "vm-v1.1.0", m.get("version"))
p = m["policy"]
rec("fail-closed policy", p.get("mode") == "fail-closed")
rec("automatic download disabled", p.get("automatic_download") is False)
rec("automatic reinstall disabled", p.get("automatic_reinstall") is False)
rec("owner release gate", p.get("owner_release_gate") is True)

a = m["assets"]

hash_check("sforzando active binary", a["sforzando"]["path"], a["sforzando"]["sha256"])
hash_check("sforzando recovery ZIP", a["sforzando"]["recovery"]["path"], a["sforzando"]["recovery"]["sha256"])

hash_check("AVLDrums active binary", a["avldrums"]["plugin_path"], a["avldrums"]["plugin_sha256"])
hash_check("AVL Black Pearl sample set", a["avldrums"]["black_pearl_path"], a["avldrums"]["black_pearl_sha256"])
avl_recovery = resolve(a["avldrums"]["recovery"]["directory"])
rec("AVL recovery cache", avl_recovery.is_dir() and any(x.is_file() for x in avl_recovery.rglob("*")), avl_recovery)

bb = a["black_and_blue"]
bbroot = resolve(bb["root"])
rec("Black & Blue root", bbroot.is_dir(), bbroot)
if bbroot.is_dir():
    n, b = ext_stats(bbroot, {".wav", ".flac", ".aif", ".aiff"})
    rec("Black & Blue exact sample count/bytes", n == bb["samples"]["files"] and b == bb["samples"]["bytes"], f"files={n} bytes={b}")
    n, b = ext_stats(bbroot, {".sfz"})
    rec("Black & Blue exact SFZ count/bytes", n == bb["sfz"]["files"] and b == bb["sfz"]["bytes"], f"files={n} bytes={b}")
hash_check("Dark Black SFZ", bb["dark_black"]["path"], bb["dark_black"]["sha256"])
hash_check("Black & Blue recovery TAR", bb["recovery"]["path"], bb["recovery"]["sha256"])

mg = a["metal_gtx"]
mgroot = resolve(mg["root"])
rec("Metal GTX root", mgroot.is_dir(), mgroot)
if mgroot.is_dir():
    n, b = ext_stats(mgroot, {".wav", ".flac", ".aif", ".aiff"})
    rec("Metal GTX exact sample count/bytes", n == mg["samples"]["files"] and b == mg["samples"]["bytes"], f"files={n} bytes={b}")
    n, b = ext_stats(mgroot, {".sfz"})
    rec("Metal GTX exact SFZ count/bytes", n == mg["sfz"]["files"] and b == mg["sfz"]["bytes"], f"files={n} bytes={b}")
hash_check("Metal GTX stock XTracking", mg["stock_xtracking"]["path"], mg["stock_xtracking"]["sha256"])
hash_check("Metal GTX Clean DI XTracking", mg["clean_di_xtracking"]["path"], mg["clean_di_xtracking"]["sha256"])
rec("Metal GTX Clean DI Magnet CC48", mg["clean_di_xtracking"].get("magnet_cc48") == 0, mg["clean_di_xtracking"].get("magnet_cc48"))
rec("Metal GTX Clean DI Mute_Time CC22", mg["clean_di_xtracking"].get("mute_time_cc22") == 51, mg["clean_di_xtracking"].get("mute_time_cc22"))
rec("Metal GTX recovery bridge pinned", len(mg["recovery_bridge"].get("artifacts", [])) == mg["recovery_bridge"]["chunk_count"], mg["recovery_bridge"])

vs = a["vsco_2_ce"]
vsroot = resolve(vs["root"])
stable = resolve(vs["stable_path"])
rec("VSCO 2 CE versioned root", vsroot.is_dir(), vsroot)
rec("VSCO 2 CE stable path", stable.exists(), stable)
if vsroot.is_dir():
    n, _ = ext_stats(vsroot, {".sfz"})
    rec("VSCO exact SFZ count", n == vs["sfz_files"], n)
    n, _ = ext_stats(vsroot, {".wav"})
    rec("VSCO exact WAV count", n == vs["wav_files"], n)
    basenames = {p.name for p in vsroot.rglob("*.sfz")}
    for patch in vs["patches"]:
        rec(f"VSCO patch {patch}", patch in basenames, patch)
hash_check("VSCO recovery archive", vs["archive_path"], vs["archive_sha256"])

nam = a["nam"]
hash_check("NAM active binary", nam["plugin_path"], nam["plugin_sha256"])
hash_check("NAM Obsidian model", nam["model_path"], nam["model_sha256"])
nam_recovery = resolve(nam["recovery_dir"])
found_nam_recovery = False
if nam_recovery.is_dir():
    for q in nam_recovery.rglob("*"):
        if q.is_file():
            try:
                if sha256(q) == nam["recovery_artifact_sha256"]:
                    found_nam_recovery = True
                    break
            except OSError:
                pass
rec("NAM recovery artifact", found_nam_recovery, nam_recovery)

deps_check("sforzando dependencies", a["sforzando"]["path"])
deps_check("AVLDrums dependencies", a["avldrums"]["plugin_path"])
deps_check("NAM dependencies", nam["plugin_path"])

vst_cache = root / "config/REAPER/reaper-vstplugins64.ini"
cache_text = vst_cache.read_text(errors="ignore") if vst_cache.is_file() else ""
rec("REAPER sforzando cache", "sforzando" in cache_text.lower(), vst_cache)

ini = root / "config/REAPER/reaper.ini"
ini_text = ini.read_text(errors="ignore") if ini.is_file() else ""
rt = m["runtime"]
rec("REAPER sample rate 48 kHz", "linux_audio_srate=48000" in ini_text, ini)
rec("REAPER Apollo input", f'alsa_indev={rt["input_device"]}' in ini_text, rt["input_device"])
rec("REAPER Apollo output", f'alsa_outdev={rt["output_device"]}' in ini_text, rt["output_device"])

proj = m["project"]
project = resolve(proj["path"])
hash_check("Ultra Realism NAM-retained project", proj["path"], proj["sha256"])
if project.is_file() and sha256(project) == proj["sha256"]:
    text = project.read_text(errors="ignore")
    names = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith('NAME "') and s.endswith('"'):
            names.append(s[6:-1])
    expected_names = [row[0] for row in m["tracks"]]
    if len(names) >= len(expected_names):
        rec("exact 23-track ordered name contract", names[:len(expected_names)] == expected_names and len(expected_names) == 23, f"first={names[:23]}")
    else:
        rec("exact 23-track ordered name contract", False, f"found={len(names)} names")
    rec("three guitar NAM Obsidian refs", text.count(str(root / nam["model_path"])) == m["contract"]["exact_nam_guitar_model_refs"], text.count(str(root / nam["model_path"])))
    rec("three Metal GTX Clean DI refs", text.count(str(root / mg["clean_di_xtracking"]["path"])) == m["contract"]["exact_metal_gtx_clean_di_instances"], text.count(str(root / mg["clean_di_xtracking"]["path"])))
else:
    rec("serialized project contract", False, "project hash not authoritative")

passed = sum(1 for _, ok, _ in checks if ok)
failed = len(checks) - passed
lines = [f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else "") for label, ok, detail in checks]
lines += [
    f"SUMMARY pass={passed} fail={failed}",
    f"manifest={manifest_path}",
    f"root={root}",
    "policy=verify-only; no download, reinstall, substitution, or project mutation",
]
report_path.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
raise SystemExit(0 if failed == 0 else 7)
PY
