#!/usr/bin/env python3
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((BASE / "config/permanence-v1.1.0.json").read_text())

expected_tracks = [
    ["Drum Buss","FFF468"],["Kick","0070DD"],["Snare","00FF98"],["Tom 1","F48CBA"],
    ["Tom 2","3FC7EB"],["Tom 3","8788EE"],["OH","FF7C0A"],["Room","C69B6D"],
    ["Bass Buss","FFF468"],["Bass DI","AAD372"],["Bass Neural","AAD372"],
    ["Guitar Buss","FFF468"],["L Guitar DI","C41E3A"],["R Guitar DI","C41E3A"],
    ["L Guitar Neural","C41E3A"],["R Guitar Neural","C41E3A"],["Lead Buss","FFF468"],
    ["Lead Guitar DI","A330C9"],["Lead Guitar Neural","A330C9"],["Orchestra Buss","FFF468"],
    ["Strings High","33937F"],["Strings Low","33937F"],["Horns","33937F"],
]

def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)
    print("PASS:", message)

require(manifest["version"] == "vm-v1.1.0", "version pin")
require(manifest["policy"]["mode"] == "fail-closed", "fail-closed policy")
require(manifest["policy"]["automatic_download"] is False, "automatic download disabled")
require(manifest["policy"]["automatic_reinstall"] is False, "automatic reinstall disabled")
require(manifest["policy"]["owner_release_gate"] is True, "owner release gate")
require(manifest["tracks"] == expected_tracks, "exact 23-track name/color contract")
require(len({x[0] for x in manifest["tracks"]}) == 23, "track names unique")
require(manifest["assets"]["metal_gtx"]["clean_di_xtracking"]["magnet_cc48"] == 0, "Metal GTX Magnet CC48=0")
require(manifest["assets"]["metal_gtx"]["clean_di_xtracking"]["mute_time_cc22"] == 51, "Metal GTX Mute_Time CC22=51")
require(manifest["assets"]["nam"]["guitar_model_ref_count"] == 3, "three guitar NAM model references")
require(manifest["assets"]["nam"]["bass_model_policy"] == "unassigned", "Bass Neural remains owner-select")

hashes = []
def collect(v):
    if isinstance(v, dict):
        for k, x in v.items():
            if k.endswith("sha256"):
                hashes.append((k, x))
            collect(x)
    elif isinstance(v, list):
        for x in v:
            collect(x)
collect(manifest)
for key, value in hashes:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, f"valid SHA-256 field {key}")

for rel in [
    "bin/verify-permanence-v1.1.0.sh",
    "bin/enter-v1.1.0.sh",
    "bin/install-v1.1.0.sh",
]:
    text = (BASE / rel).read_text()
    require(re.search(r"\b(curl|wget)\b|git\s+clone|apt(-get)?\s+install|dnf\s+install|yum\s+install", text) is None,
            f"{rel} contains no downloader/package-install path")

lua = (BASE / "reaper/Scripts/Sunwell/Sunwell_VM_v1_1_0_Regression.lua").read_text()
require("owner promotion required" in lua.lower(), "REAPER action preserves owner gate")
require("install" not in re.sub(r"--.*", "", lua).lower(), "REAPER action performs no install command")

print("VM v1.1.0 source contract: PASS")
