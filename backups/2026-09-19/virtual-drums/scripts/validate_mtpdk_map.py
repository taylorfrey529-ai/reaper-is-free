#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

DEFAULT_MAP = Path(__file__).resolve().parent.parent / "references" / "mtpdk-midi-map.json"
CORE = {"Kick": 36, "SideStick": 37, "Snare": 38}


def main():
    ap = argparse.ArgumentParser(description="Validate corrected MTPDK note and CC mapping.")
    ap.add_argument("map_json", nargs="?", default=str(DEFAULT_MAP))
    args = ap.parse_args()

    path = Path(args.map_json)
    data = json.loads(path.read_text())
    errors = []
    warnings = []

    if data.get("note_channel") != 1:
        errors.append(f"note_channel={data.get('note_channel')} expected 1")
    if data.get("cc_channel") != 16:
        errors.append(f"cc_channel={data.get('cc_channel')} expected 16")

    notes = {row.get("instrument"): row for row in data.get("notes", [])}
    for name, expected in CORE.items():
        got = notes.get(name, {}).get("main")
        if got != expected:
            errors.append(f"{name} main={got} expected {expected}")

    encoding = str(data.get("note_encoding", ""))
    if "stored_value - 1" not in encoding and "stored value - 1" not in encoding:
        warnings.append("note_encoding does not explicitly document stored-value minus one")

    cc_map = data.get("cc_map", [])
    if len(cc_map) != 128:
        errors.append(f"cc_map entries={len(cc_map)} expected 128")
    seen = set()
    for row in cc_map:
        cc = row.get("cc")
        seen.add(cc)
        if row.get("midi_channel") != 16:
            errors.append(f"CC {cc}: midi_channel={row.get('midi_channel')} expected 16")
        if row.get("parameter_index") != cc:
            errors.append(f"CC {cc}: parameter_index={row.get('parameter_index')} expected {cc}")
    if seen != set(range(128)):
        missing = sorted(set(range(128)) - seen)
        extra = sorted(x for x in seen if not isinstance(x, int) or x < 0 or x > 127)
        errors.append(f"CC domain mismatch missing={missing} extra={extra}")

    result = {
        "ok": not errors,
        "map": str(path),
        "plugin": data.get("plugin"),
        "core_notes": {k: notes.get(k, {}).get("main") for k in CORE},
        "cc_entries": len(cc_map),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
