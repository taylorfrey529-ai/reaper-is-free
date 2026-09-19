#!/usr/bin/env python3
import argparse
import json
import math
import struct
import wave


def decode(raw, width):
    if width == 1:
        return [b - 128 for b in raw], 128.0
    if width == 2:
        n = len(raw) // 2
        return struct.unpack("<" + "h" * n, raw), 32768.0
    if width == 3:
        out = []
        for i in range(0, len(raw) - 2, 3):
            v = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if v & 0x800000:
                v -= 1 << 24
            out.append(v)
        return out, 8388608.0
    if width == 4:
        n = len(raw) // 4
        return struct.unpack("<" + "i" * n, raw), 2147483648.0
    raise ValueError(f"unsupported PCM width: {width} bytes")


def dbfs(v):
    return -120.0 if v <= 0 else max(-120.0, 20.0 * math.log10(v))


def main():
    ap = argparse.ArgumentParser(description="Measure stereo PCM WAV L/R correlation.")
    ap.add_argument("wav")
    ap.add_argument("--target", type=float)
    ap.add_argument("--tolerance", type=float, default=0.02)
    args = ap.parse_args()

    with wave.open(args.wav, "rb") as wf:
        ch = wf.getnchannels()
        rate = wf.getframerate()
        width = wf.getsampwidth()
        frames = wf.getnframes()
        if ch != 2:
            raise SystemExit("expected stereo WAV")
        sx = sy = sxx = syy = sxy = 0.0
        n = 0
        peaks = [0.0, 0.0]
        sums = [0.0, 0.0]
        while True:
            raw = wf.readframes(8192)
            if not raw:
                break
            vals, denom = decode(raw, width)
            usable = len(vals) - (len(vals) % 2)
            for i in range(0, usable, 2):
                x = vals[i] / denom
                y = vals[i+1] / denom
                n += 1
                sx += x; sy += y
                sxx += x*x; syy += y*y; sxy += x*y
                peaks[0] = max(peaks[0], abs(x)); peaks[1] = max(peaks[1], abs(y))
                sums[0] += x*x; sums[1] += y*y
    cov = sxy - sx * sy / n
    vx = sxx - sx * sx / n
    vy = syy - sy * sy / n
    corr = cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else None
    errors = []
    if args.target is not None:
        if corr is None or abs(corr - args.target) > args.tolerance:
            errors.append(f"correlation {corr} outside target {args.target} +/- {args.tolerance}")
    result = {
        "ok": not errors,
        "wav": args.wav,
        "sample_rate": rate,
        "channels": ch,
        "sample_width_bits": width * 8,
        "frames": frames,
        "duration_seconds": frames / rate,
        "peak_dbfs": [round(dbfs(p), 4) for p in peaks],
        "rms_dbfs": [round(dbfs(math.sqrt(s / n)), 4) for s in sums],
        "correlation_lr": None if corr is None else round(corr, 6),
        "target": args.target,
        "tolerance": args.tolerance if args.target is not None else None,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
