# Astra Workbench Desktop

A functional offline studio desktop for the local ChatGPT workspace, assembled around the supplied Ubuntu 24.04.4 netboot media and the graphics/audio workspaces already configured in this project.

The visual shell is deliberately dark and minimal: navy glass surfaces, crisp
cyan/magenta signal edges, and a production-first hierarchy for REAPER, audio,
graphics, and local tools. It remains an ordinary Tk/Openbox session so it can
be reconstructed on Xvfb without a compositor.

## Start

```bash
/mnt/data/ubuntu-desktop-workspace/start-desktop.sh
```

The default virtual display is `:88` at 2560x1440x24.

## 24-plane desktop depth

The desktop scene is built from a deterministic 24-plane RGBA stack with
one-pixel increments. `assets/depth/layer-01-wallpaper.png` is the wallpaper
base plane at alpha `198/255`; planes 02–24 are transparent extrusion and
perspective-guide layers. The shell composites them into
`assets/desktop-3d-composite.png` at startup, and `assets/depth/manifest.json`
records the canvas, layer order, and transparency contract.

## Verify / screenshot

```bash
DISPLAY=:88 /mnt/data/ubuntu-desktop-workspace/verify-desktop.sh
```

## Stop

```bash
/mnt/data/ubuntu-desktop-workspace/stop-desktop.sh
```

## Included desktop functions

- Openbox window management
- Astra top panel and left launch rail
- Studio telemetry for X11, depth, audio clock, and Apollo S/PDIF
- REAPER production desk for ASIO-Routing-Project
- Workspace file browser
- XTerm launcher
- Chromium launcher with local offline home page
- Vulkan `vkcube` launcher using `/mnt/data/graphics-workspace`
- About/settings panel
- Real X11 screenshot verification

## Installation boundary

The supplied operating-system archive contains Ubuntu 24.04.4 **netboot** media, not a full offline desktop filesystem. The current container has no outbound network and no QEMU package installed, so a native Ubuntu guest installation cannot be completed from that media alone. The desktop session here is therefore a local functional shell on the workspace host, with the Ubuntu netboot payload staged for a future native VM install when Ubuntu package media or network access is available.

## REAPER 7.79

REAPER 7.79 for Linux x86_64 is installed at:

`/mnt/data/ubuntu-desktop-workspace/apps/REAPER`

Launch it from the REAPER dock button or run:

`/mnt/data/ubuntu-desktop-workspace/bin/launch-reaper.sh`

The Astra launch path keeps REAPER on the local Virtual Apollo ALSA boundary:
`apollo_spdif`, 48 kHz, stereo, and a 256×3 buffer. This keeps the existing
ASIO-Routing-Project routing contract intact even though the container exposes
no physical `/dev/snd` device. REAPER uses the persisted Astra native theme
and SWELL palette from `config/REAPER`, so the track control, arrange, mixer,
transport, and native dialogs share the workbench's navy/cyan/magenta system.

### Floating DAW bay

REAPER is intentionally composed as a floating instrument surface inside the
desktop depth scene rather than maximized over it. The persisted client geometry
is `2200×1240` at `(170,78)`; the Openbox Astra frame leaves the 24-plane bay
rails, dock, and wallpaper visible around the DAW. `desktop_depth.py` draws the
DAW bay as another stepped transparent surface and labels it at depth plane 24.

The theme installer also builds same-size Astra control art for REAPER's 100%,
150%, and 200% density buckets: 25-frame cyan/magenta knob stacks, glass
fader grips, pan rails, transport knobs, and miniature meter grips. The source
generator is `scripts/install-astra-reaper-theme.py`; the visual control atlas
is `assets/astra-control-atlas.png`.

With the session running, verify the composition and asset buckets with:

`/mnt/data/ubuntu-desktop-workspace/scripts/verify-astra-daw-bay.sh`
