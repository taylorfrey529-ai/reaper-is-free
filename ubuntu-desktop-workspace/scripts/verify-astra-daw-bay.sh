#!/usr/bin/env bash
set -euo pipefail

ROOT=/mnt/data/ubuntu-desktop-workspace
DISPLAY=${DISPLAY:-127.0.0.1:88}
export DISPLAY

xdpyinfo -display "$DISPLAY" >/dev/null
TREE=$(xwininfo -root -tree)
LINE=$(printf '%s\n' "$TREE" | grep 'ASIO-Routing-Project - REAPER' | head -1 || true)
if [ -z "$LINE" ]; then
  echo 'FAIL REAPER window not found on the Astra display' >&2
  exit 1
fi

python3 - "$LINE" <<'PY'
import re
import sys
line=sys.argv[1]
match=re.search(r'\s(\d+)x(\d+)\+(-?\d+)\+(-?\d+)\s+\+(-?\d+)\+(-?\d+)', line)
assert match, line
width,height,_,_,x,y=map(int, match.groups())
assert (width,height)==(2200,1240), (width,height)
assert (x,y)==(172,102), (x,y)
print(f'PASS REAPER floating client={width}x{height} screen={x},{y}')
PY

python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile
root=Path('/mnt/data/ubuntu-desktop-workspace')
theme=root/'config/REAPER/ColorThemes/Astra_Workbench.ReaperThemeZip'
assert theme.is_file(), theme
with ZipFile(theme) as z:
    names=set(z.namelist())
required=[]
for scale in ('', '150/', '200/'):
    required.extend([
        f'Default_7.0_unpacked/{scale}mcp_volthumb.png',
        f'Default_7.0_unpacked/{scale}mcp_fxparm_knob_stack.png',
        f'Default_7.0_unpacked/{scale}mcp_send_knob_stack.png',
        f'Default_7.0_unpacked/{scale}tcp_vol_knob_stack.png',
    ])
missing=[name for name in required if name not in names]
assert not missing, missing
print('PASS Astra control assets 100/150/200 present')
PY

printf 'PASS Astra DAW bay verified on display %s\n' "$DISPLAY"
