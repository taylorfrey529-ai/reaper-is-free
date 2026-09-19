#!/usr/bin/env python3
import argparse
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_MAP = Path(__file__).resolve().parent.parent / "references" / "mtpdk-midi-map.json"


def vlq(data, pos):
    value = 0
    for _ in range(4):
        if pos >= len(data):
            raise ValueError("truncated variable-length quantity")
        b = data[pos]
        pos += 1
        value = (value << 7) | (b & 0x7F)
        if not (b & 0x80):
            return value, pos
    raise ValueError("invalid variable-length quantity")


def parse_midi(path, note_channel, cc_channel):
    data = Path(path).read_bytes()
    if data[:4] != b"MThd":
        raise ValueError("not a Standard MIDI File")
    hlen = struct.unpack(">I", data[4:8])[0]
    if hlen < 6:
        raise ValueError("invalid MIDI header length")
    fmt, ntrks, division = struct.unpack(">HHH", data[8:14])
    pos = 8 + hlen
    notes = Counter()
    ccs = Counter()
    total_note_on = 0
    total_cc = 0

    for _ in range(ntrks):
        if data[pos:pos+4] != b"MTrk":
            raise ValueError("missing MTrk chunk")
        tlen = struct.unpack(">I", data[pos+4:pos+8])[0]
        pos += 8
        end = pos + tlen
        running = None
        while pos < end:
            _, pos = vlq(data, pos)
            if pos >= end:
                break
            b = data[pos]
            if b & 0x80:
                status = b
                pos += 1
                if status < 0xF0:
                    running = status
            else:
                if running is None:
                    raise ValueError("running status without prior channel status")
                status = running

            if status == 0xFF:
                if pos >= end:
                    raise ValueError("truncated meta event")
                pos += 1
                length, pos = vlq(data, pos)
                pos += length
                running = None
                continue
            if status in (0xF0, 0xF7):
                length, pos = vlq(data, pos)
                pos += length
                running = None
                continue

            typ = status & 0xF0
            chan = (status & 0x0F) + 1
            need = 1 if typ in (0xC0, 0xD0) else 2
            if pos + need > end:
                raise ValueError("truncated channel event")
            d1 = data[pos]
            d2 = data[pos+1] if need == 2 else None
            pos += need

            if typ == 0x90 and d2 and chan == note_channel:
                notes[d1] += 1
                total_note_on += 1
            elif typ == 0xB0 and chan == cc_channel:
                ccs[d1] += 1
                total_cc += 1
        pos = end

    return {
        "format": fmt,
        "tracks": ntrks,
        "division": division,
        "notes": notes,
        "ccs": ccs,
        "total_note_on": total_note_on,
        "total_cc": total_cc,
    }


def main():
    ap = argparse.ArgumentParser(description="Inspect a Standard MIDI File against the canonical MTPDK map.")
    ap.add_argument("midi")
    ap.add_argument("--map", dest="map_json", default=str(DEFAULT_MAP))
    ap.add_argument("--require-kick", action="store_true")
    ap.add_argument("--strict-unmapped", action="store_true")
    args = ap.parse_args()

    mapping = json.loads(Path(args.map_json).read_text())
    note_channel = int(mapping.get("note_channel", 1))
    cc_channel = int(mapping.get("cc_channel", 16))
    note_to_names = defaultdict(list)
    for row in mapping.get("notes", []):
        for key in ("main", "alt1", "alt2"):
            n = row.get(key)
            if isinstance(n, int):
                note_to_names[n].append(row.get("instrument", "unknown"))

    parsed = parse_midi(args.midi, note_channel, cc_channel)
    articulation_counts = {}
    unmapped = {}
    for note, count in sorted(parsed["notes"].items()):
        names = note_to_names.get(note)
        if names:
            articulation_counts[f"{note}:{'/'.join(names)}"] = count
        else:
            unmapped[str(note)] = count

    errors = []
    warnings = []
    kick = parsed["notes"].get(36, 0)
    side = parsed["notes"].get(37, 0)
    snare = parsed["notes"].get(38, 0)
    if args.require_kick and kick == 0:
        errors.append("no Kick note 36 events found")
    if side > kick and kick > 0:
        warnings.append(f"SideStick count {side} exceeds Kick count {kick}; confirm this is intentional")
    if args.strict_unmapped and unmapped:
        errors.append(f"unmapped note-ons present: {unmapped}")

    result = {
        "ok": not errors,
        "midi": str(args.midi),
        "format": parsed["format"],
        "tracks": parsed["tracks"],
        "division": parsed["division"],
        "note_channel": note_channel,
        "cc_channel": cc_channel,
        "total_note_on": parsed["total_note_on"],
        "total_cc": parsed["total_cc"],
        "core_counts": {"Kick_36": kick, "SideStick_37": side, "Snare_38": snare},
        "articulation_counts": articulation_counts,
        "unmapped_note_ons": unmapped,
        "cc_numbers_present": sorted(parsed["ccs"]),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
