#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
output=${1:-/mnt/data/mouse-keyboard-screenshot.png}
display=${2:-${DISPLAY:-:88}}
eval "$("$script_dir/desktop_context.sh" --shell "$display")"
size=$(xdpyinfo -display "$DISPLAY" 2>/dev/null | awk '/dimensions:/{print $2; exit}')
[[ -n "$size" ]] || { echo "cannot determine dimensions for $DISPLAY" >&2; exit 3; }
mkdir -p "$(dirname "$output")"
ffmpeg -nostdin -loglevel error -y -f x11grab -video_size "$size" -i "$DISPLAY" -frames:v 1 "$output"
test -s "$output"
printf '%s\n' "$output"
