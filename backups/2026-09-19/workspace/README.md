# Ubuntu Workspace Desktop

A functional offline desktop session for the local ChatGPT workspace, assembled around the supplied Ubuntu 24.04.4 netboot media and the graphics/audio workspaces already configured in this project.

## Start

```bash
/mnt/data/ubuntu-desktop-workspace/start-desktop.sh
```

The default virtual display is `:88` at 1440x900x24.

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
- Ubuntu-style top bar and left dock
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

The VM exposes no `/dev/snd` hardware, so REAPER is configured for Dummy Audio at 44.1 kHz / 512 samples. This avoids JACK/ALSA device errors while keeping the DAW fully usable for project editing, routing, FX setup, and offline rendering in the workspace. Switch to ALSA/JACK/PulseAudio when real audio hardware or a server is attached.