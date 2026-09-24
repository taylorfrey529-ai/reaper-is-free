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

# Cross-manifest identity locks: durable custody must restore exactly the runtime
# identities admitted by the active permanence contract.
pa = manifest["assets"]
da = durable["assets"]
require(da["sforzando"]["source_archive_sha256"] == pa["sforzando"]["recovery"]["sha256"],
        "sforzando recovery hash agrees across manifests")
require(da["sforzando"]["binary_sha256"] == pa["sforzando"]["sha256"],
        "sforzando binary hash agrees across manifests")
require(da["avldrums"]["binary_sha256"] == pa["avldrums"]["plugin_sha256"],
        "AVL binary hash agrees across manifests")
require(da["avldrums"]["black_pearl_sha256"] == pa["avldrums"]["black_pearl_sha256"],
        "AVL Black Pearl hash agrees across manifests")
require(da["avldrums"]["recovery_tar_sha256"] == pa["avldrums"]["recovery"]["sha256"],
        "AVL recovery archive hash agrees across manifests")
require(da["black_and_blue"]["source_commit"] == pa["black_and_blue"]["source_commit"],
        "BlackBlue source commit agrees across manifests")
require(da["black_and_blue"]["logical_tar_sha256"] == pa["black_and_blue"]["recovery"]["sha256"],
        "BlackBlue recovery archive hash agrees across manifests")
require(da["black_and_blue"]["sample_files"] == pa["black_and_blue"]["samples"]["files"],
        "BlackBlue sample count agrees across manifests")
require(da["black_and_blue"]["sample_bytes"] == pa["black_and_blue"]["samples"]["bytes"],
        "BlackBlue sample bytes agree across manifests")
require(da["black_and_blue"]["sfz_files"] == pa["black_and_blue"]["sfz"]["files"],
        "BlackBlue SFZ count agrees across manifests")
require(da["black_and_blue"]["dark_black_sha256"] == pa["black_and_blue"]["dark_black"]["sha256"],
        "Dark Black hash agrees across manifests")
require(da["metal_gtx"]["logical_archive_sha256"] == pa["metal_gtx"]["recovery_bridge"]["logical_archive_sha256"],
        "Metal GTX logical archive agrees across manifests")
require(da["metal_gtx"]["authoritative_source_sha256"] == pa["metal_gtx"]["authoritative_source_sha256"],
        "Metal GTX source authority agrees across manifests")

metal_derivation = pa["metal_gtx"]["clean_di_xtracking"]["recovery_derivation"]
require(metal_derivation["source"] == "stock_xtracking",
        "Metal GTX Clean DI recovery derives only from stock XTracking")
require(metal_derivation["source_sha256"] == pa["metal_gtx"]["stock_xtracking"]["sha256"],
        "Metal GTX Clean DI recovery source hash pinned")
require(metal_derivation["exact_replacement_from"] == "set_cc48=64"
        and metal_derivation["exact_replacement_to"] == "set_cc48=0"
        and metal_derivation["exact_replacement_count"] == 1,
        "Metal GTX Clean DI recovery transform pinned")
require(metal_derivation["derived_sha256"] == pa["metal_gtx"]["clean_di_xtracking"]["sha256"],
        "Metal GTX Clean DI recovery result hash pinned")
durable_metal_derivation = da["metal_gtx"]["clean_di_derivative"]
require(durable_metal_derivation["source_sha256"] == metal_derivation["source_sha256"],
        "Metal GTX durable Clean DI source hash agrees")
require(durable_metal_derivation["exact_replacement_from"] == metal_derivation["exact_replacement_from"]
        and durable_metal_derivation["exact_replacement_to"] == metal_derivation["exact_replacement_to"]
        and durable_metal_derivation["exact_replacement_count"] == metal_derivation["exact_replacement_count"],
        "Metal GTX durable Clean DI transform agrees")
require(durable_metal_derivation["derived_sha256"] == metal_derivation["derived_sha256"],
        "Metal GTX durable Clean DI result hash agrees")
require(da["vsco_2_ce"]["archive_sha256"] == pa["vsco_2_ce"]["archive_sha256"],
        "VSCO archive hash agrees across manifests")
require(da["vsco_2_ce"]["sfz_files"] == pa["vsco_2_ce"]["sfz_files"],
        "VSCO SFZ count agrees across manifests")
require(da["vsco_2_ce"]["wav_files"] == pa["vsco_2_ce"]["wav_files"],
        "VSCO WAV count agrees across manifests")
require(da["nam"]["artifact_sha256"] == pa["nam"]["recovery_artifact_sha256"],
        "NAM recovery artifact agrees across manifests")
require(da["nam"]["plugin_sha256"] == pa["nam"]["plugin_sha256"],
        "NAM plugin hash agrees across manifests")
require(da["obsidian"]["model_sha256"] == pa["nam"]["model_sha256"],
        "Obsidian model hash agrees across manifests")

require(len(durable["assets"]["sforzando"]["drive_objects"]) == 1, "one durable sforzando wrapper")
require(len(durable["assets"]["avldrums"]["drive_objects"]) == 1, "one durable AVL wrapper")
require(len(durable["assets"]["black_and_blue"]["drive_objects"]) == 13, "Black & Blue 13-part durable set")
require("manifest" in durable["assets"]["black_and_blue"], "Black & Blue durable manifest")
require(len(durable["assets"]["metal_gtx"]["drive_objects"]) == 15, "Metal GTX 15-part durable set")
require("drive_manifest" in durable["assets"]["metal_gtx"], "Metal GTX durable manifest")
require(len(durable["assets"]["vsco_2_ce"]["drive_objects"]) == 25, "VSCO 25-part durable set")
require("manifest" in durable["assets"]["vsco_2_ce"], "VSCO durable manifest")
require(len(durable["assets"]["nam"]["drive_objects"]) == 1, "one durable NAM wrapper")
require(len(durable["assets"]["obsidian"]["drive_objects"]) == 1, "one durable Obsidian model")
require(str(durable["evidence"]["black_and_blue_stream_reconstruction"]).startswith("PASS"), "Black & Blue streamed reconstruction evidence")
require(durable["evidence"]["vsco_stream_reconstruction"] == "PASS", "VSCO streamed reconstruction evidence")
require((BASE / "bin/verify-durable-recovery-v1.1.0.py").is_file(), "offline durable recovery verifier present")

rehydrator = BASE / "bin/rehydrate-offline-v1.1.0.py"
require(rehydrator.is_file(), "offline durable rehydrator present")
rehydrate_text = rehydrator.read_text()
require('ap.add_argument("--apply", action="store_true"' in rehydrate_text,
        "offline rehydrator requires explicit --apply")
require("verify_durable_set(" in rehydrate_text,
        "offline rehydrator verifies durable custody before promotion")
require("reaper_running(root)" in rehydrate_text,
        "offline rehydrator refuses a live REAPER workspace")
require("rollback(root, backup, rels)" in rehydrate_text,
        "offline rehydrator retains rollback path")
require("recovery-backups" in rehydrate_text,
        "offline rehydrator preserves displaced runtime bytes")

require('source_token = b"set_cc48=64"' in rehydrate_text
        and 'target_token = b"set_cc48=0"' in rehydrate_text,
        "offline rehydrator implements the pinned Metal GTX Clean DI transform")
require("Metal GTX carried Clean DI derivative hash mismatch" in rehydrate_text,
        "offline rehydrator rejects a mismatched carried Clean DI derivative")
require(
    re.search(r"\b(requests|urllib3|httpx|aiohttp|ftplib)\b|\burlopen\b|\bsocket\.(create_connection|socket)\b|\b(curl|wget)\b|git\s+clone|apt(-get)?\s+install|dnf\s+install|yum\s+install",
              rehydrate_text, re.I) is None,
    "offline rehydrator contains no network/downloader/package-install path",
)
require("projects/" not in rehydrate_text and "/projects/" not in rehydrate_text,
        "offline rehydrator does not mutate REAPER project files")

installer_text = (BASE / "bin/install-v1.1.0.sh").read_text()
require("durable-recovery-v1.1.0.json" in installer_text,
        "installed vm layer retains durable custody manifest")
require("verify-durable-recovery-v1.1.0.py" in installer_text,
        "installed vm layer retains durable verifier")
require("rehydrate-offline-v1.1.0.py" in installer_text,
        "installed vm layer retains explicit offline rehydrator")

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
