#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
display=${1:-${DISPLAY:-:88}}
eval "$("$script_dir/desktop_context.sh" --shell "$display")"
echo "DISPLAY=$DISPLAY"
echo '--- root geometry ---'
xwininfo -display "$DISPLAY" -root | sed -n '/Width:/p;/Height:/p;/Depth:/p'
echo '--- windows ---'
xwininfo -display "$DISPLAY" -root -tree
