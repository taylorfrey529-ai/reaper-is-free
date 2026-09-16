# Display :88 / 2560x1440x24 recovery overlay

This overlay is the current effective display/depth layer for `linux-ububtu-vm-workspace`.

## Contract

- Canonical X11 display: `:88`
- Geometry: `2560x1440x24`
- Wallpaper: RGBA depth layer 01, alpha `198/255`
- Desktop depth: 24 transparent RGBA planes
- Plane step: one pixel per layer
- Generated assets: `assets/depth/layer-01-wallpaper.png` through `layer-24-desktop-depth.png`
- Composite: `assets/desktop-3d-composite.png`
- Manifest: `assets/depth/manifest.json`

## Recovery behavior

`restore.sh` first verifies the hash-locked source snapshot and tar stream. Only after those checks pass does it copy the text overlay into the restored `ubuntu-desktop-workspace`. `scripts/start-live-session.py` passes the display/depth values into `start-desktop.sh`, and the shell regenerates the RGBA stack when its manifest is absent or stale.

The overlay intentionally leaves the historical snapshot hashes and rejected-payload records unchanged. It is a deterministic, auditable evolution layer, not a replacement for the admitted snapshot authority.
