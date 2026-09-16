#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/data/ubuntu-desktop-workspace
SCREEN_WIDTH=${SCREEN_WIDTH:-2560}
SCREEN_HEIGHT=${SCREEN_HEIGHT:-1440}
DISPLAY=${DISPLAY:-$(cat "$ROOT/run/display" 2>/dev/null || echo ':88')}
export DISPLAY
xdpyinfo >/dev/null
xwininfo -root -tree | grep -q '"Astra Workbench Desktop"'
for f in xvfb openbox desktop-shell; do
  p=$(cat "$ROOT/run/$f.pid")
  kill -0 "$p"
done
OUT="$ROOT/ubuntu-desktop.png"
scrot "$OUT"
DEPTH_LAYERS=${DESKTOP_DEPTH_LAYERS:-24}
SCREEN_WIDTH="$SCREEN_WIDTH" SCREEN_HEIGHT="$SCREEN_HEIGHT" DEPTH_LAYERS="$DEPTH_LAYERS" python3 - "$OUT" <<'PY'
import json
from pathlib import Path
from PIL import Image, ImageStat
import os
import sys
p=sys.argv[1]
im=Image.open(p).convert('RGB')
expected=(int(os.environ['SCREEN_WIDTH']), int(os.environ['SCREEN_HEIGHT']))
assert im.size==expected, (im.size, expected)
stat=ImageStat.Stat(im)
spread=sum(stat.var)
assert spread>100.0, spread
root=Path('/mnt/data/ubuntu-desktop-workspace')
stack=root/'assets'/'depth'
manifest=json.loads((stack/'manifest.json').read_text())
layers=int(os.environ['DEPTH_LAYERS'])
assert manifest['canvas']==[expected[0],expected[1]], manifest['canvas']
assert manifest['depth_layers']==layers, manifest['depth_layers']
assert manifest['step_pixels']==1, manifest['step_pixels']
assert len(manifest['layers'])==layers, len(manifest['layers'])
composite=Image.open(root/'assets'/'desktop-3d-composite.png')
assert composite.size==expected, composite.size
assert composite.mode=='RGBA', composite.mode
for record in manifest['layers']:
    layer=Image.open(stack/record['file'])
    assert layer.size==expected, (record['file'], layer.size)
    assert layer.mode=='RGBA', (record['file'], layer.mode)
    alpha=layer.getchannel('A').getextrema()
    if record['index']==1:
        assert alpha==(198,198), (record['file'], alpha)
    else:
        assert alpha[0]==0 and alpha[1]>0, (record['file'], alpha)
print(f'PASS {im.size[0]}x{im.size[1]} variance={spread:.1f} file={p}')
print(f'PASS depth-layers={layers} step-pixels=1 composite={root/"assets/desktop-3d-composite.png"}')
PY
