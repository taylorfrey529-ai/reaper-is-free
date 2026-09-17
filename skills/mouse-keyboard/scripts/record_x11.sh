#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
usage() { echo 'usage: record_x11.sh start OUTPUT.mp4 [DISPLAY] [FPS] | stop OUTPUT.mp4' >&2; exit 2; }
[[ $# -ge 2 ]] || usage
mode=$1
output=$2
pidfile="${output}.pid"
case "$mode" in
  start)
    display=${3:-${DISPLAY:-:88}}
    fps=${4:-15}
    eval "$("$script_dir/desktop_context.sh" --shell "$display")"
    size=$(xdpyinfo -display "$DISPLAY" 2>/dev/null | awk '/dimensions:/{print $2; exit}')
    [[ -n "$size" ]] || { echo "cannot determine dimensions for $DISPLAY" >&2; exit 3; }
    if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
      echo "recorder already running for $output" >&2
      exit 4
    fi
    mkdir -p "$(dirname "$output")"
    nohup ffmpeg -nostdin -y -f x11grab -framerate "$fps" -video_size "$size" -i "$DISPLAY" -c:v libx264 -preset ultrafast -pix_fmt yuv420p "$output" >"${output}.log" 2>&1 &
    pid=$!
    printf '%s\n' "$pid" > "$pidfile"
    sleep 0.6
    kill -0 "$pid" 2>/dev/null || { cat "${output}.log" >&2; rm -f "$pidfile"; exit 5; }
    printf '%s\n' "$pid"
    ;;
  stop)
    [[ -f "$pidfile" ]] || { echo "no pidfile for $output" >&2; exit 4; }
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      kill -INT "$pid"
      for _ in $(seq 1 80); do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.1
      done
    fi
    rm -f "$pidfile"
    test -s "$output"
    ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate -show_entries format=duration -of default=nw=1 "$output"
    ;;
  *) usage ;;
esac
