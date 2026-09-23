#!/usr/bin/env bash
set -euo pipefail

ROOT="${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}"
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MANIFEST="${VM_V110_MANIFEST:-$HERE/../config/permanence-v1.1.0.json}"
REPORT="${VM_V110_REPORT:-$ROOT/logs/vm-v1.1.0-permanence-report.txt}"
mkdir -p "$(dirname "$REPORT")"

python3 - "$ROOT" "$MANIFEST" "$REPORT" <<'PY'
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
report_path = Path(sys.argv[3])
fast = os.environ.get("VM_V110_FAST", "0") == "1"

lines = []
passes = 0
fails = 0
skips = 0

def emit(kind, label, detail=""):
    global passes, fails, skips
    if kind == "PASS":
        passes += 1
    elif kind == "FAIL":
        fails += 1
    else:
        skips += 1
    suffix = f" - {detail}" if detail else ""
    lines.append(f"[{kind}] {label}{suffix}")

def check(label, ok, detail=""):
    emit("PASS" if ok else "FAIL", label, detail)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def check_hash(label, rel, expected):
    p = root / rel
    if not p.is_file():
        emit("FAIL", label, f"missing {p}")
        return
    actual = sha256(p)
    check(label, actual == expected, f"sha256={actual}")

def stats(base, suffixes):
    files = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in suffixes]
    return len(files), sum(p.stat().st_size for p in files)

def check_stats(label, rel, suffixes, expected):
    p = root / rel
    if not p.is_dir():
        emit("FAIL", label, f"missing {p}")
        return
    count, size = stats(p, suffixes)
    check(label, count == expected["files"] and size == expected["bytes"],
          f"files={count}/{expected['files']} bytes={size}/{expected['bytes']}")

def ldd_clean(label, rel):
    p = root / rel
    if not p.is_file():
        emit("FAIL", label, f"missing {p}")
        return
    try:
        proc = subprocess.run(["ldd", str(p)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        ok = proc.returncode == 0 and "not found" not in proc.stdout
        check(label, ok, f"returncode={proc.returncode}")
    except FileNotFoundError:
        emit("FAIL", label, "ldd unavailable")

if not manifest_path.is_file():
    print(f"VM-V1.1.0 PERMANENCE: FAIL - manifest missing: {manifest_path}")
    raise SystemExit(2)

m = json.loads(manifest_path.read_text(encoding="utf-8"))
check("manifest version", m.get("version") == "vm-v1.1.0")
check("fail-closed policy", m["policy"].get("mode") == "fail-closed")
check("automatic download disabled", m["policy"].get("automatic_download") is False)
check("automatic reinstall disabled", m["policy"].get("automatic_reinstall") is False)

a = m["assets"]
check_hash("sforzando binary", a["sforzando"]["path"], a["sforzando"]["sha256"])
check_hash("AVLDrums LV2 binary", a["avldrums"]["plugin_path"], a["avldrums"]["plugin_sha256"])
check_hash("AVL Black Pearl kit", a["avldrums"]["black_pearl_path"], a["avldrums"]["black_pearl_sha256"])
check_hash("Black & Blue Dark Black", a["black_and_blue"]["dark_black"]["path"], a["black_and_blue"]["dark_black"]["sha256"])
check_stats("Black & Blue sample inventory", a["black_and_blue"]["root"], {".wav", ".flac", ".aif", ".aiff"}, a["black_and_blue"]["samples"])
check_stats("Black & Blue SFZ inventory", a["black_and_blue"]["root"], {".sfz"}, a["black_and_blue"]["sfz"])
check_hash("Metal GTX stock XTracking", a["metal_gtx"]["stock_xtracking"]["path"], a["metal_gtx"]["stock_xtracking"]["sha256"])
check_hash("Metal GTX Clean DI XTracking", a["metal_gtx"]["clean_di_xtracking"]["path"], a["metal_gtx"]["clean_di_xtracking"]["sha256"])
check_stats("Metal GTX sample inventory", a["metal_gtx"]["root"], {".wav", ".flac", ".aif", ".aiff"}, a["metal_gtx"]["samples"])
check_stats("Metal GTX SFZ inventory", a["metal_gtx"]["root"], {".sfz"}, a["metal_gtx"]["sfz"])
check_hash("NAM LV2 binary", a["nam"]["plugin_path"], a["nam"]["plugin_sha256"])
check_hash("NAM Obsidian model", a["nam"]["model_path"], a["nam"]["model_sha256"])
ldd_clean("AVLDrums dependency closure", a["avldrums"]["plugin_path"])
ldd_clean("NAM dependency closure", a["nam"]["plugin_path"])

vsco = a["vsco_2_ce"]
vsco_root = root / vsco["root"]
stable = root / vsco["stable_path"]
check("VSCO 2 CE version root", vsco_root.is_dir(), str(vsco_root))
check("VSCO 2 CE stable path", stable.exists() and stable.resolve() == vsco_root.resolve(), str(stable))
if vsco_root.is_dir():
    sfz_count = sum(1 for p in vsco_root.rglob("*.sfz") if p.is_file())
    wav_count = sum(1 for p in vsco_root.rglob("*.wav") if p.is_file())
    check("VSCO 2 CE SFZ inventory", sfz_count == vsco["sfz_files"], f"{sfz_count}/{vsco['sfz_files']}")
    check("VSCO 2 CE WAV inventory", wav_count == vsco["wav_files"], f"{wav_count}/{vsco['wav_files']}")
    names = {p.name for p in vsco_root.rglob("*.sfz") if p.is_file()}
    for patch in vsco["patches"]:
        check(f"VSCO patch {patch}", patch in names)
archive = root / vsco["archive_path"]
if fast:
    emit("SKIP", "VSCO recovery archive full SHA-256", "VM_V110_FAST=1")
    check("VSCO recovery archive present", archive.is_file(), str(archive))
else:
    check_hash("VSCO recovery archive", vsco["archive_path"], vsco["archive_sha256"])

cache = root / "config/REAPER/reaper-vstplugins64.ini"
if cache.is_file():
    txt = cache.read_text(errors="ignore").lower()
    check("REAPER sforzando cache", "sforzando" in txt)
else:
    emit("FAIL", "REAPER sforzando cache", f"missing {cache}")

rpp = root / m["project"]["path"]
check("Ultra Realism retained project", rpp.is_file(), str(rpp))
if rpp.is_file():
    text = rpp.read_text(errors="ignore")
    starts = [x.start() for x in re.finditer(r"(?m)^<TRACK(?:\s|$)", text)]
    blocks = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        block = text[start:end]
        nm = re.search(r'(?m)^\s*NAME "(.*)"\s*$', block)
        pc = re.search(r"(?m)^\s*PEAKCOL\s+(-?\d+)\s*$", block)
        if nm:
            blocks.append((nm.group(1), int(pc.group(1)) if pc else None, block))
    expected = m["tracks"]
    names = [x[0] for x in blocks]
    expected_names = [x[0] for x in expected]
    check("exact 23-track name/order contract", names == expected_names,
          f"actual={len(names)} expected={len(expected_names)}")
    by_name = {name: (color, block) for name, color, block in blocks}
    def native_color(rgb):
        v = int(rgb, 16)
        r = (v >> 16) & 255
        g = (v >> 8) & 255
        b = v & 255
        return 0x01000000 | r | (g << 8) | (b << 16)
    for name, rgb in expected:
        actual = by_name.get(name, (None, ""))[0]
        check(f"track color {name}", actual == native_color(rgb),
              f"actual={actual} expected={native_color(rgb)} #{rgb}")
    # Structural/plugin-role guardrails. These are deliberately name-based rather than preset-name guesses.
    role_terms = {
        "Drum Buss": ("AVL", "drum"),
        "Bass DI": ("sforzando",),
        "Bass Neural": ("NAM", "Neural"),
        "L Guitar DI": ("sforzando",),
        "R Guitar DI": ("sforzando",),
        "Lead Guitar DI": ("sforzando",),
        "L Guitar Neural": ("NAM", "Neural"),
        "R Guitar Neural": ("NAM", "Neural"),
        "Lead Guitar Neural": ("NAM", "Neural"),
        "Strings High": ("sforzando",),
        "Strings Low": ("sforzando",),
        "Horns": ("sforzando",),
    }
    for track, terms in role_terms.items():
        block = by_name.get(track, (None, ""))[1].lower()
        check(f"serialized FX role {track}", any(t.lower() in block for t in terms))
    obsidian = str(root / a["nam"]["model_path"])
    check("three guitar Obsidian references", text.count(obsidian) == a["nam"]["guitar_model_ref_count"],
          f"count={text.count(obsidian)}")
    bass_block = by_name.get("Bass Neural", (None, ""))[1]
    check("Bass Neural model remains owner-select", obsidian not in bass_block)

report = "\n".join([
    "REAPER 7.79 - VM v1.1.0 PERMANENCE / REGRESSION GATE",
    f"root={root}",
    f"manifest={manifest_path}",
    f"mode={'FAST' if fast else 'FULL'}",
    *lines,
    f"SUMMARY pass={passes} fail={fails} skip={skips}",
    "POLICY verify-only; no download, clone, install, repair, or model substitution is performed.",
    "OWNER GATE release/promotion remains manual.",
]) + "\n"
report_path.write_text(report, encoding="utf-8")
print(report, end="")
raise SystemExit(0 if fails == 0 else 3)
PY
