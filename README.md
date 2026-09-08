# REAPER workspace backup

This repository backs up the custom tooling and reproducibility notes for the local REAPER 7.79 audio workspace.

## Included

- Workspace setup and package metadata.
- Workspace-local activation and REAPER launcher scripts.
- SHA-256 provenance for the source archive/runtime used in the workspace.
- `AI_Phase_align_drum_shells_to_overheads.lua` ReaScript.
- `AI_Drum_Shell_Phase_Align` JSFX processor.

The drum alignment workflow keeps the stereo overheads fixed and non-destructively time-aligns close drum shells to their corresponding overhead arrivals. Tom 1 is explicitly self-anchored to Tom 1 transients in the stereo overheads.

## Not included

REAPER application binaries, bundled REAPER resources, Ubuntu `.deb` packages, and other third-party binary assets are intentionally not committed here. REAPER remains subject to Cockos' own license and distribution terms.

See `audio/SETUP.md` for the workspace snapshot details.
