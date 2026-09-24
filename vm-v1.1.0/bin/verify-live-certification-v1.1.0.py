#!/usr/bin/env python3
"""Fail-closed evidence verifier for REAPER 7.79 vm-v1.1.0 live certification.

This tool never edits the REAPER project, repairs assets, selects models, or
promotes a release. It verifies a fresh live session against the pinned
permanence contract and the eight approved instrument/NAM audition windows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import time
import wave

CHUNK = 8 * 1024 * 1024
BASE = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "config" / "permanence-v1.1.0.json"
EXPECTED_AUDIO = (
    "drums",
    "bass-di",
    "rhythm-l-neural",
    "rhythm-r-neural",
    "lead-neural",
    "strings-high",
    "strings-low",
    "horns",
)


class EvidenceError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise EvidenceError(message)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def load_config(path: pathlib.Path) -> dict:
    data = json.loads(path.read_text())
    if data.get("version") != "vm-v1.1.0":
        fail("unexpected permanence manifest version")
    return data


def require_file(path: pathlib.Path, label: str) -> pathlib.Path:
    if not path.is_file():
        fail(f"{label} missing: {path}")
    return path


def require_fresh(path: pathlib.Path, started_at_epoch: float, label: str) -> None:
    require_file(path, label)
    if path.stat().st_mtime + 1.0 < started_at_epoch:
        fail(f"{label} predates certification session: {path}")


def parse_summary_report(path: pathlib.Path, expected_pass: int, label: str) -> dict:
    text = require_file(path, label).read_text(errors="replace")
    if "[FAIL]" in text:
        fail(f"{label} contains FAIL entries")
    m = re.search(r"^SUMMARY pass=(\d+) fail=(\d+)\s*$", text, re.M)
    if not m:
        fail(f"{label} summary missing")
    passed, failed = int(m.group(1)), int(m.group(2))
    if passed != expected_pass or failed != 0:
        fail(f"{label} summary {passed}/{failed}, expected {expected_pass}/0")
    if label == "REAPER regression" and "RESULT PASS" not in text:
        fail("REAPER regression result is not PASS")
    return {"pass": passed, "fail": failed, "sha256": sha256(path), "path": str(path)}


def decode_pcm_sample(raw: bytes, width: int) -> int:
    if width == 1:
        return raw[0] - 128
    if width == 2:
        return struct.unpack("<h", raw)[0]
    if width == 3:
        value = raw[0] | (raw[1] << 8) | (raw[2] << 16)
        if value & 0x800000:
            value -= 1 << 24
        return value
    if width == 4:
        return struct.unpack("<i", raw)[0]
    fail(f"unsupported PCM sample width: {width}")


def analyze_wav(path: pathlib.Path) -> dict:
    require_file(path, "audio capture")
    try:
        w = wave.open(str(path), "rb")
    except wave.Error as exc:
        fail(f"WAV open failed for {path}: {exc}")
    with w:
        channels = w.getnchannels()
        rate = w.getframerate()
        width = w.getsampwidth()
        frames = w.getnframes()
        comptype = w.getcomptype()
        if channels != 2:
            fail(f"{path.name}: channels={channels}, expected 2")
        if rate != 48000:
            fail(f"{path.name}: sample_rate={rate}, expected 48000")
        if comptype != "NONE":
            fail(f"{path.name}: compressed WAV is not admitted")
        if width not in (1, 2, 3, 4):
            fail(f"{path.name}: unsupported PCM width {width}")
        if frames < 12000:
            fail(f"{path.name}: capture shorter than 0.25 seconds")

        peak = [0, 0]
        sumsq = [0.0, 0.0]
        total = 0
        frame_bytes = channels * width
        while True:
            data = w.readframes(65536)
            if not data:
                break
            usable = len(data) - (len(data) % frame_bytes)
            for off in range(0, usable, frame_bytes):
                for ch in (0, 1):
                    start = off + ch * width
                    value = decode_pcm_sample(data[start:start + width], width)
                    av = abs(value)
                    if av > peak[ch]:
                        peak[ch] = av
                    sumsq[ch] += float(value) * float(value)
                total += 1

    if total == 0:
        fail(f"{path.name}: no PCM frames decoded")
    full_scale = float((1 << (8 * width - 1)) - 1) if width > 1 else 127.0
    peak_norm = [x / full_scale for x in peak]
    rms_norm = [math.sqrt(x / total) / full_scale for x in sumsq]

    overall_peak = max(peak_norm)
    overall_rms = math.sqrt((rms_norm[0] ** 2 + rms_norm[1] ** 2) / 2.0)
    peak_dbfs = 20.0 * math.log10(max(overall_peak, 1e-12))
    rms_dbfs = 20.0 * math.log10(max(overall_rms, 1e-12))
    if peak_dbfs <= -70.0 or rms_dbfs <= -80.0:
        fail(f"{path.name}: capture is effectively silent (peak={peak_dbfs:.2f} dBFS rms={rms_dbfs:.2f} dBFS)")

    return {
        "path": str(path),
        "sha256": sha256(path),
        "sample_rate_hz": rate,
        "channels": channels,
        "sample_width_bytes": width,
        "frames": frames,
        "duration_seconds": frames / float(rate),
        "peak_dbfs": peak_dbfs,
        "rms_dbfs": rms_dbfs,
        "channel_rms": rms_norm,
    }


def validate_audio_set(entries: list[str], started_at_epoch: float) -> dict:
    found: dict[str, pathlib.Path] = {}
    for item in entries:
        if "=" not in item:
            fail("--audio entries must be LABEL=/path/to/capture.wav")
        label, raw_path = item.split("=", 1)
        if label in found:
            fail(f"duplicate audio label: {label}")
        found[label] = pathlib.Path(raw_path).resolve()

    if set(found) != set(EXPECTED_AUDIO):
        missing = sorted(set(EXPECTED_AUDIO) - set(found))
        extra = sorted(set(found) - set(EXPECTED_AUDIO))
        fail(f"audio label set mismatch missing={missing} extra={extra}")

    result = {}
    for label in EXPECTED_AUDIO:
        path = found[label]
        require_fresh(path, started_at_epoch, f"audio capture {label}")
        result[label] = analyze_wav(path)

    left = result["rhythm-l-neural"]["channel_rms"]
    right = result["rhythm-r-neural"]["channel_rms"]
    if left[0] <= max(left[1] * 1.9952623149688795, 1e-12):
        fail("rhythm-l-neural does not demonstrate >=6 dB left dominance")
    if right[1] <= max(right[0] * 1.9952623149688795, 1e-12):
        fail("rhythm-r-neural does not demonstrate >=6 dB right dominance")
    return result


def session_audio_entries(session: pathlib.Path, started_at_epoch: float) -> list[str]:
    audio_dir = session / "audio"
    entries = []
    for label in EXPECTED_AUDIO:
        wav = audio_dir / (label + ".wav")
        sidecar = audio_dir / (label + ".capture.json")
        require_fresh(wav, started_at_epoch, f"audio capture {label}")
        require_fresh(sidecar, started_at_epoch, f"audio provenance {label}")
        meta = json.loads(sidecar.read_text())
        if meta.get("label") != label:
            fail(f"{label}: provenance label mismatch")
        if meta.get("device") != "apollo_spdif_capture":
            fail(f"{label}: provenance device is not apollo_spdif_capture")
        if meta.get("format") != "S32_LE" or meta.get("sample_rate_hz") != 48000 or meta.get("channels") != 2:
            fail(f"{label}: provenance PCM contract mismatch")
        if meta.get("wav_sha256") != sha256(wav):
            fail(f"{label}: provenance WAV hash mismatch")
        entries.append(f"{label}={wav}")
    return entries


def capture_audio(args) -> int:
    session = args.session.resolve()
    data = json.loads(require_file(session / "session.json", "session manifest").read_text())
    if data.get("version") != "vm-v1.1.0":
        fail("session manifest version mismatch")
    started = float(data["started_at_epoch"])
    config = load_config(args.config)
    expected_device = config["runtime"]["underlying_capture"]
    if args.device != expected_device or args.device != "apollo_spdif_capture":
        fail(f"capture device must be pinned Virtual Apollo boundary {expected_device}")
    if args.label not in EXPECTED_AUDIO:
        fail("unapproved audio label: " + args.label)
    if args.seconds < 1 or args.seconds > 30:
        fail("capture duration must be between 1 and 30 seconds")

    audio_dir = session / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    wav = audio_dir / (args.label + ".wav")
    sidecar = audio_dir / (args.label + ".capture.json")
    if wav.exists() or sidecar.exists():
        fail(f"capture already exists for label {args.label}; do not overwrite certification evidence")

    arecord = shutil.which("arecord")
    if not arecord:
        fail("arecord unavailable for Virtual Apollo boundary capture")
    cmd = [
        arecord, "-q", "-D", args.device, "-f", "S32_LE",
        "-r", "48000", "-c", "2", "-d", str(args.seconds), str(wav),
    ]
    captured_at = time.time()
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        fail("Virtual Apollo arecord capture failed: " + proc.stderr[-4000:].strip())
    require_fresh(wav, max(started, captured_at - 2.0), f"audio capture {args.label}")
    analysis = analyze_wav(wav)
    meta = {
        "schema_version": 1,
        "version": "vm-v1.1.0",
        "label": args.label,
        "device": args.device,
        "format": "S32_LE",
        "sample_rate_hz": 48000,
        "channels": 2,
        "seconds_requested": args.seconds,
        "captured_at_epoch": captured_at,
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(captured_at)),
        "wav_path": str(wav),
        "wav_sha256": analysis["sha256"],
        "analysis": analysis,
        "command": cmd,
        "policy": "direct Virtual Apollo ALSA capture; no normalization or processing",
    }
    sidecar.write_text(json.dumps(meta, indent=2) + "\n")
    print("VIRTUAL APOLLO CAPTURE: PASS")
    print("label=" + args.label)
    print("wav=" + str(wav))
    print("provenance=" + str(sidecar))
    return 0


def png_geometry(path: pathlib.Path) -> tuple[int, int]:
    require_file(path, "final screenshot")
    with path.open("rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        fail("final screenshot is not a valid PNG header")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def validate_screenshot(path: pathlib.Path, started_at_epoch: float) -> dict:
    require_fresh(path, started_at_epoch, "final screenshot")
    width, height = png_geometry(path)
    if (width, height) != (2560, 1440):
        fail(f"final screenshot geometry={width}x{height}, expected 2560x1440")
    if path.stat().st_size < 4096:
        fail("final screenshot is implausibly small")
    return {"path": str(path), "sha256": sha256(path), "width": width, "height": height}


def validate_recording(path: pathlib.Path, started_at_epoch: float) -> dict:
    require_fresh(path, started_at_epoch, "screen recording")
    if path.stat().st_size < 100000:
        fail("screen recording is implausibly small")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        fail("ffprobe unavailable for finalized screen-recording validation")
    p = subprocess.run(
        [
            ffprobe, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height:format=duration",
            "-of", "json", str(path),
        ],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if p.returncode != 0:
        fail("ffprobe failed for screen recording: " + p.stderr.strip())
    try:
        info = json.loads(p.stdout)
        stream = info["streams"][0]
        duration = float(info["format"]["duration"])
        width = int(stream["width"])
        height = int(stream["height"])
    except Exception as exc:
        fail(f"invalid ffprobe result: {exc}")
    if (width, height) != (2560, 1440):
        fail(f"screen recording geometry={width}x{height}, expected 2560x1440")
    if duration <= 1.0:
        fail("screen recording duration is too short")
    return {
        "path": str(path),
        "sha256": sha256(path),
        "codec": stream.get("codec_name"),
        "width": width,
        "height": height,
        "duration_seconds": duration,
        "bytes": path.stat().st_size,
    }


def verify_project(root: pathlib.Path, config: dict) -> dict:
    project = root / config["project"]["path"]
    require_file(project, "canonical retained project")
    got = sha256(project)
    expected = config["project"]["sha256"]
    if got != expected:
        fail(f"canonical retained project hash mismatch {got} != {expected}")
    return {"path": str(project), "sha256": got}


def run_permanence(root: pathlib.Path) -> dict:
    gate = root / "vm-v1.1.0/bin/verify-permanence-v1.1.0.sh"
    require_file(gate, "installed permanence gate")
    p = subprocess.run(
        ["bash", str(gate)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
        env={**os.environ, "SUNWELL_ROOT": str(root)},
    )
    if p.returncode != 0:
        fail("full permanence gate failed:\n" + p.stdout[-8000:])
    m = re.search(r"SUMMARY pass=(\d+) fail=(\d+)(?: skip=(\d+))?", p.stdout)
    if not m:
        fail("full permanence gate summary missing")
    if int(m.group(2)) != 0:
        fail("full permanence gate contains failures")
    return {
        "returncode": p.returncode,
        "pass": int(m.group(1)),
        "fail": int(m.group(2)),
        "skip": int(m.group(3) or 0),
        "tail": p.stdout[-4000:],
    }


def run_live_gate(root: pathlib.Path, display_num: int, report: pathlib.Path) -> dict:
    gate = root / "vm-v1.1.0/bin/verify-live.sh"
    require_file(gate, "installed live gate")
    report.parent.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "SUNWELL_ROOT": str(root),
        "DISPLAY_NUM": str(display_num),
        "DISPLAY": f":{display_num}",
        "HOME": str(root / "home"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XAUTHORITY": str(root / f"home/.X11/xauthority-{display_num}"),
    }
    p = subprocess.run(
        ["bash", str(gate), str(report)],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, env=env,
    )
    if p.returncode != 0:
        fail("live gate failed:\n" + p.stdout[-8000:])
    return parse_summary_report(report, 9, "live gate")


def begin(args) -> int:
    root = args.root.resolve()
    config = load_config(args.config)
    if not root.is_dir():
        fail(f"workspace root missing: {root}")
    session = args.session.resolve()
    if session.exists():
        fail(f"session directory already exists: {session}")
    session.mkdir(parents=True)
    project = verify_project(root, config)
    started = time.time()
    manifest = {
        "schema_version": 1,
        "version": "vm-v1.1.0",
        "started_at_epoch": started,
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "source_head": args.source_head,
        "root": str(root),
        "project": project,
        "expected_audio_labels": list(EXPECTED_AUDIO),
        "policy": "verify-only/fail-closed/owner-promotion-required",
    }
    (session / "session.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("LIVE CERTIFICATION SESSION: BEGUN")
    print("session=" + str(session))
    print("source_head=" + args.source_head)
    print("record the GUI before launching or changing REAPER state")
    return 0


def verify(args) -> int:
    session = args.session.resolve()
    session_file = session / "session.json"
    data = json.loads(require_file(session_file, "session manifest").read_text())
    if data.get("version") != "vm-v1.1.0":
        fail("session manifest version mismatch")
    started = float(data["started_at_epoch"])
    root = pathlib.Path(data["root"]).resolve()
    config = load_config(args.config)

    result = {
        "schema_version": 1,
        "version": "vm-v1.1.0",
        "source_head": data.get("source_head"),
        "started_at_utc": data.get("started_at_utc"),
        "verified_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "owner_release_gate": True,
        "project": verify_project(root, config),
    }

    result["permanence"] = run_permanence(root)

    live_report = session / "vm-v1.1.0-live.txt"
    result["live_gate"] = run_live_gate(root, args.display_num, live_report)

    regression = pathlib.Path(args.regression_report).resolve()
    require_fresh(regression, started, "REAPER regression")
    result["reaper_regression"] = parse_summary_report(regression, 78, "REAPER regression")

    result["audio"] = validate_audio_set(session_audio_entries(session, started), started)
    screenshot = pathlib.Path(args.screenshot).resolve()
    result["screenshot"] = validate_screenshot(screenshot, started)

    if args.recording:
        recording = pathlib.Path(args.recording).resolve()
        result["recording"] = validate_recording(recording, started)
        result["status"] = "PASS"
    elif args.allow_recording_pending:
        result["recording"] = {"status": "PENDING_FINALIZATION"}
        result["status"] = "LIVE_PASS_RECORDING_PENDING"
    else:
        fail("final certification requires --recording, or use --allow-recording-pending before stopping the recorder")

    result_path = session / "vm-v1.1.0-live-certification.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print("VM v1.1.0 LIVE CERTIFICATION: " + result["status"])
    print("evidence=" + str(result_path))
    print("owner promotion required")
    return 0


def build_parser():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    b = sub.add_parser("begin")
    b.add_argument("--root", type=pathlib.Path, default=pathlib.Path("/mnt/data/ubuntu-desktop-workspace"))
    b.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    b.add_argument("--session", type=pathlib.Path, required=True)
    b.add_argument("--source-head", required=True)
    b.set_defaults(func=begin)

    a = sub.add_parser("capture")
    a.add_argument("--session", type=pathlib.Path, required=True)
    a.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    a.add_argument("--label", required=True, choices=EXPECTED_AUDIO)
    a.add_argument("--seconds", type=int, default=3)
    a.add_argument("--device", default="apollo_spdif_capture")
    a.set_defaults(func=capture_audio)

    v = sub.add_parser("verify")
    v.add_argument("--session", type=pathlib.Path, required=True)
    v.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG)
    v.add_argument("--display-num", type=int, default=88)
    v.add_argument("--regression-report", required=True)
    v.add_argument("--screenshot", required=True)
    v.add_argument("--recording")
    v.add_argument("--allow-recording-pending", action="store_true")
    v.set_defaults(func=verify)
    return ap


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(4)
