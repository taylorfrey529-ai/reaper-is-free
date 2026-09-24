#!/usr/bin/env python3
import importlib.util
import math
import os
import pathlib
import struct
import tempfile
import time
import wave

BASE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = BASE / "bin" / "verify-live-certification-v1.1.0.py"

spec = importlib.util.spec_from_file_location("vm_v110_live_cert", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def write_stereo_wav(path, left_amp, right_amp, seconds=0.5, rate=48000):
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        data = bytearray()
        for i in range(frames):
            s = math.sin(2.0 * math.pi * 440.0 * i / rate)
            l = int(max(-1.0, min(1.0, s * left_amp)) * 32767)
            r = int(max(-1.0, min(1.0, s * right_amp)) * 32767)
            data += struct.pack("<hh", l, r)
        w.writeframes(bytes(data))


def expect_fail(fn, contains):
    try:
        fn()
    except mod.EvidenceError as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError("expected EvidenceError containing " + contains)


def test_non_silent_wav_passes():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-wav-") as td:
        p = pathlib.Path(td) / "audio.wav"
        write_stereo_wav(p, 0.25, 0.25)
        a = mod.analyze_wav(p)
        assert a["sample_rate_hz"] == 48000
        assert a["channels"] == 2
        assert a["duration_seconds"] >= 0.49
        assert a["peak_dbfs"] > -20.0
        print("PASS: non-silent 48 kHz stereo WAV admitted")


def test_silence_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-silence-") as td:
        p = pathlib.Path(td) / "silent.wav"
        write_stereo_wav(p, 0.0, 0.0)
        expect_fail(lambda: mod.analyze_wav(p), "effectively silent")
        print("PASS: silent WAV rejected")


def make_audio_set(root, bad_left=False):
    paths = {}
    for label in mod.EXPECTED_AUDIO:
        p = root / (label + ".wav")
        if label == "rhythm-l-neural":
            amps = (0.10, 0.10) if bad_left else (0.30, 0.03)
        elif label == "rhythm-r-neural":
            amps = (0.03, 0.30)
        else:
            amps = (0.20, 0.20)
        write_stereo_wav(p, *amps)
        paths[label] = p
    return paths


def test_audio_label_set_and_pan_dominance():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-set-") as td:
        root = pathlib.Path(td)
        paths = make_audio_set(root)
        entries = [f"{k}={v}" for k, v in paths.items()]
        result = mod.validate_audio_set(entries, time.time() - 2.0)
        assert tuple(result) == mod.EXPECTED_AUDIO
        print("PASS: exact eight-window audio set admitted with rhythm pan dominance")


def test_wrong_left_dominance_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-pan-") as td:
        root = pathlib.Path(td)
        paths = make_audio_set(root, bad_left=True)
        entries = [f"{k}={v}" for k, v in paths.items()]
        expect_fail(
            lambda: mod.validate_audio_set(entries, time.time() - 2.0),
            "rhythm-l-neural does not demonstrate",
        )
        print("PASS: incorrect left-rhythm dominance rejected")


def test_missing_audio_label_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-missing-") as td:
        root = pathlib.Path(td)
        paths = make_audio_set(root)
        paths.pop("horns")
        entries = [f"{k}={v}" for k, v in paths.items()]
        expect_fail(
            lambda: mod.validate_audio_set(entries, time.time() - 2.0),
            "audio label set mismatch",
        )
        print("PASS: incomplete eight-window audio set rejected")


def test_stale_evidence_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-stale-") as td:
        p = pathlib.Path(td) / "report.txt"
        p.write_text("SUMMARY pass=9 fail=0\n")
        old = time.time() - 120.0
        os.utime(p, (old, old))
        expect_fail(
            lambda: mod.require_fresh(p, time.time(), "test report"),
            "predates certification session",
        )
        print("PASS: stale evidence rejected")


def test_report_fail_entry_rejected():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-report-") as td:
        p = pathlib.Path(td) / "report.txt"
        p.write_text("[PASS] one\n[FAIL] two\nSUMMARY pass=1 fail=1\n")
        expect_fail(
            lambda: mod.parse_summary_report(p, 1, "live gate"),
            "contains FAIL entries",
        )
        print("PASS: report containing FAIL entry rejected")


def test_png_geometry_validation():
    with tempfile.TemporaryDirectory(prefix="vm-v110-live-png-") as td:
        p = pathlib.Path(td) / "shot.png"
        # Minimal PNG signature + IHDR geometry bytes are sufficient for the
        # verifier's geometry check; pad above its plausibility-size floor.
        p.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">II", 2560, 1440)
            + b"\x08\x02\x00\x00\x00"
            + b"X" * 5000
        )
        got = mod.validate_screenshot(p, time.time() - 2.0)
        assert got["width"] == 2560 and got["height"] == 1440
        print("PASS: 2560x1440 screenshot geometry admitted")


def main():
    test_non_silent_wav_passes()
    test_silence_rejected()
    test_audio_label_set_and_pan_dominance()
    test_wrong_left_dominance_rejected()
    test_missing_audio_label_rejected()
    test_stale_evidence_rejected()
    test_report_fail_entry_rejected()
    test_png_geometry_validation()
    print("VM v1.1.0 live certification unit tests: PASS")


if __name__ == "__main__":
    main()
