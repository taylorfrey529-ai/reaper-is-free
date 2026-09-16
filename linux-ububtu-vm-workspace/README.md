# linux-ububtu-vm-workspace

GitHub recovery authority for the ChatGPT Linux/Ubuntu-style REAPER 7.79 workspace.

## Start here

- [`RECALL.md`](RECALL.md) — short fresh-session recovery card.
- [`BOOT-HANDOFF-CURRENT.md`](BOOT-HANDOFF-CURRENT.md) — current recovery/boot/acceptance sequence.
- [`SNAPSHOT-INTEGRITY.md`](SNAPSHOT-INTEGRITY.md) — authoritative snapshot provenance, including the rejected corrupt historical GitHub payload.
- [`OVERLAY-MANIFEST.md`](OVERLAY-MANIFEST.md) — current 2560x1440x24 display/depth overlay applied during restore.
- [`BOOT-HANDOFF.md`](BOOT-HANDOFF.md) — retained historical detailed handoff; current snapshot transport instructions supersede it.
- [`RUNTIME-BUNDLES.md`](RUNTIME-BUNDLES.md) — exact external runtime payload identities.

## Regression-safe restore

```bash
bash scripts/verify-regression.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
```

The valid current GitHub source/config snapshot is reconstructed from the checksum-verified full backup and stored as independently hashed textual parts under `source-snapshot.parts/`. Its deterministic archive SHA-256 is:

`be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac`

The exact full backup remains the strongest byte authority:

`c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`

The former `.b64` GitHub payload was proven corrupt and is not admitted for restore. See `SNAPSHOT-INTEGRITY.md`.

## Current X11 display recall

The effective recovery baseline is X11/Openbox display `:88` at `2560x1440x24`. The restored desktop builds a 24-plane transparent RGBA depth stack: wallpaper is layer 01 at alpha `198/255`, followed by one-pixel transparent planes 02-24. `restore.sh` applies the versioned overlay after validating the hash-locked source snapshot.

```bash
REAPER_SCREEN_WIDTH=2560 REAPER_SCREEN_HEIGHT=1440 REAPER_SCREEN_DEPTH=24 \\
REAPER_DESKTOP_DEPTH_LAYERS=24 REAPER_DESKTOP_DEPTH_STEP_PIXELS=1 \\
python3 scripts/start-live-session.py
```

## Runtime bundles

```bash
bash verify-runtime-bundles.sh /mnt/data
```

Filename alone is not authority; runtime hashes must match `RUNTIME-BUNDLES.md`.

## Live boot

Once the canonical live roots and exact runtime dependencies are present:

```bash
python3 scripts/start-live-session.py
```

The launcher starts/reuses X11/Openbox on `:88`, starts Virtual Apollo, enforces the canonical ALSA/S/PDIF settings, opens `ASIO-Routing-Project`, and reports the real REAPER license/evaluation UI without bypassing it.

## Canonical audio state

```text
REAPER backend: ALSA (linux_audio_mode=1)
Interface: apollo_spdif
Stereo S/PDIF: 2 input / 2 output
Sample rate: 48 kHz
Buffer: 256 samples x 3
Project tempo: 120 BPM
```

## Astra Workbench custom desktop

The effective desktop shell is Astra Workbench: a dark navy studio surface with thin cyan/magenta signal edges, four raised work cards, a production-first REAPER desk, and live telemetry for the authenticated `:88` display, 24-plane depth stack, 48 kHz clock, and Apollo S/PDIF route.

The source snapshot remains hash-locked. `restore.sh` applies the text overlay after snapshot verification; the overlay contains the reconstructable shell, wallpaper/depth renderer, Openbox title contract, and matching local handoff files.
