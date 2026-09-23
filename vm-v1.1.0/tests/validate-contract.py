#!/usr/bin/env python3
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((BASE / "config/permanence-v1.1.0.json").read_text())
durable = json.loads((BASE / "config/durable-recovery-v1.1.0.json").read_text())

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
require(manifest.get("contract", {}).get("no_silent_substitution", True) is True, "no silent substitution")
require(manifest.get("contract", {}).get("no_auto_heal", True) is True, "no automatic healing")

require(durable["version"] == "vm-v1.1.0", "durable-recovery version pin")
require(durable["policy"]["durable_custody_required"] is True, "durable custody required")
require(durable["policy"]["upstream_network_is_not_permanence"] is True, "upstream network is not permanence")
require(durable["policy"]["actions_artifacts_are_staging_only"] is True, "Actions artifacts are staging only")
require(durable["policy"]["owner_release_gate"] is True, "durable recovery preserves owner gate")
required_durable_assets = {
    "sforzando", "avldrums", "black_and_blue", "metal_gtx", "vsco_2_ce", "nam", "obsidian"
}
require(set(durable["assets"]) == required_durable_assets, "durable asset set is exact")
for asset_name in sorted(required_durable_assets):
    asset = durable["assets"][asset_name]
    require(asset.get("status") == "DURABLE", f"{asset_name} durable custody")
    has_drive_object = bool(asset.get("drive_objects"))
    has_drive_folder = bool(asset.get("drive_folder_id"))
    require(has_drive_object or has_drive_folder, f"{asset_name} has durable Drive identity")
require(durable["admission"]["require_all_assets_durable"] is True, "all assets required durable")
require(durable["admission"]["cold_restore_required"] is True, "cold restore required")
require(durable["admission"]["live_reaper_required"] is True, "live REAPER required")
require(durable["admission"]["virtual_apollo_non_silent_required"] is True, "non-silent Virtual Apollo required")

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
collect(durable)
for key, value in hashes:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            f"valid SHA-256 field {key}")

for path in sorted((BASE / "bin").glob("*.sh")):
    text = path.read_text()
    require(
        re.search(r"\b(curl|wget)\b|git\s+clone|apt(-get)?\s+install|dnf\s+install|yum\s+install", text, re.I) is None,
        f"{path.relative_to(BASE)} contains no downloader/package-install path",
    )

lua = (BASE / "reaper/Scripts/Sunwell/Sunwell_VM_v1_1_0_Regression.lua").read_text()
require("owner promotion required" in lua.lower(), "REAPER action preserves owner gate")
lua_code = re.sub(r"--.*", "", lua)
require(
    re.search(r"\b(curl|wget)\b|git\s+clone|apt(-get)?\s+install|dnf\s+install|yum\s+install", lua_code, re.I) is None,
    "REAPER action contains no downloader/package-install command",
)

print("VM v1.1.0 source contract: PASS")
