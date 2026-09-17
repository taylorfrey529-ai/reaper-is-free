#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
display=${1:-${DISPLAY:-:88}}
missing=()
for bin in python3 xdpyinfo xwininfo ffmpeg ffprobe; do
  command -v "$bin" >/dev/null 2>&1 || missing+=("$bin")
done
libs=$(python3 - <<'PY'
import ctypes.util, json
print(json.dumps({"X11": ctypes.util.find_library("X11"), "Xtst": ctypes.util.find_library("Xtst")}))
PY
)
if [[ "$libs" == *'"X11": null'* ]]; then missing+=(libX11); fi
if [[ "$libs" == *'"Xtst": null'* ]]; then missing+=(libXtst); fi
reachable=false
context='{}'
if context=$("$script_dir/desktop_context.sh" --json "$display" 2>/dev/null); then reachable=true; fi
if ((${#missing[@]})); then
  printf '{"ok":false,"display":"%s","reachable":%s,"missing":"%s","libraries":%s,"context":%s}\n' "$display" "$reachable" "${missing[*]}" "$libs" "$context"
  exit 4
fi
printf '{"ok":true,"display":"%s","reachable":%s,"missing":"","libraries":%s,"context":%s}\n' "$display" "$reachable" "$libs" "$context"
[[ "$reachable" == true ]]
