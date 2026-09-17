#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
display=${1:-${DISPLAY:-:88}}
out=${2:-/mnt/data/mouse-keyboard-selftest}
mkdir -p "$out"
"$script_dir/preflight.sh" "$display" | tee "$out/preflight.json"
eval "$("$script_dir/desktop_context.sh" --shell "$display")"
python3 "$script_dir/input_driver.py" --display "$DISPLAY" position | tee "$out/position-before.json"
recording="$out/selftest.mp4"
"$script_dir/record_x11.sh" start "$recording" "$DISPLAY" 15 >/dev/null
sleep 0.4
before=$(python3 "$script_dir/input_driver.py" --display "$DISPLAY" position)
bx=$(printf '%s' "$before" | python3 -c 'import json,sys; print(json.load(sys.stdin)["x"])')
by=$(printf '%s' "$before" | python3 -c 'import json,sys; print(json.load(sys.stdin)["y"])')
python3 "$script_dir/input_driver.py" --display "$DISPLAY" move-human --x $((bx+96)) --y $((by+42)) --duration 0.55 --amplitude 18 --waves 1.25
python3 "$script_dir/input_driver.py" --display "$DISPLAY" move-human --x "$bx" --y "$by" --duration 0.55 --amplitude 18 --waves 1.25
"$script_dir/capture_x11.sh" "$out/screenshot.png" "$DISPLAY" >/dev/null
sleep 0.4
"$script_dir/record_x11.sh" stop "$recording" >/dev/null
python3 "$script_dir/input_driver.py" --display "$DISPLAY" position | tee "$out/position-after.json"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -show_entries format=duration -of json "$recording" > "$out/video.json"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json "$out/screenshot.png" > "$out/screenshot.json"
printf '{"ok":true,"display":"%s","recording":"%s","screenshot":"%s"}\n' "$DISPLAY" "$recording" "$out/screenshot.png"
