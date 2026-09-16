# linux-ububtu-vm-workspace — recall card

## Identity

```text
Repository: taylorfrey529-ai/reaper-is-free
Branch: linux-ububtu-vm-workspace
Historical backup commit: 350f07895fbca399dfe0c50ca1e4c5723e9a9a58
Full backup SHA-256: c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a
Current GitHub source snapshot: be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac
Rejected corrupt GitHub blob: 8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28
```

Read `BOOT-HANDOFF-CURRENT.md`, `SNAPSHOT-INTEGRITY.md`, and `OVERLAY-MANIFEST.md` first. The legacy `BOOT-HANDOFF.md` is historical detail only where its snapshot-transport wording conflicts.

## Fresh start

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
git checkout linux-ububtu-vm-workspace
cd linux-ububtu-vm-workspace
bash scripts/verify-regression.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
bash verify-runtime-bundles.sh /mnt/data
# restore.sh applies the current display/depth overlay after snapshot verification
```

Reconcile restored source/config into:

```text
/mnt/data/ubuntu-desktop-workspace
/mnt/data/graphics-workspace
/mnt/data/virtual-apollo
```

Then boot:

```bash
REAPER_SCREEN_WIDTH=2560 REAPER_SCREEN_HEIGHT=1440 REAPER_SCREEN_DEPTH=24 \\
REAPER_DESKTOP_DEPTH_LAYERS=24 REAPER_DESKTOP_DEPTH_STEP_PIXELS=1 \\
python3 scripts/start-live-session.py
```

## Continuity locks

```text
X11/Openbox :88, 2560x1440x24
Desktop depth: 24 transparent RGBA planes; wallpaper layer 01 alpha 198/255; layers 02-24 use one-pixel steps
REAPER 7.79 Linux x86_64
ASIO-Routing-Project
ALSA: linux_audio_mode=1
apollo_spdif
2-in / 2-out stereo S/PDIF
48000 Hz
256 samples x 3
120 BPM / 4/4
```

Never regress `linux_audio_mode` to `0` (JACK). Preserve the legitimate REAPER evaluation/license UI; detect/report it without bypassing it.

## Effective display/depth overlay

The recovery overlay is applied by `restore.sh` after the hash-verified source snapshot is reconstructed. It installs the 2560x1440x24 desktop launcher/shell/verifier and the deterministic 24-plane RGBA depth builder; generated depth PNGs are recreated locally at boot.

See `OVERLAY-MANIFEST.md` for the exact overlay contract.

## Vocabulary

- Restored = checksum-admitted backup/snapshot state recovered.
- Reconstructed = recreated from an admitted authority.
- Verified live = actually executed and observed in the current runtime.

## Custom desktop surface — Astra Workbench

- Theme: dark studio glass with restrained cyan, magenta, amber, and lime signal accents.
- Surface: four raised work cards — launch, session telemetry, REAPER production, and workspace modules.
- Functional identity: REAPER 7.79 / ASIO-Routing-Project / 48 kHz / Apollo S/PDIF remains primary.
- Restore: the custom shell and depth renderer are copied from the overlay after the hash-verified snapshot is reconstructed.
- Feature branch: `feature/astra-workbench-custom-desktop-20260916`, based on the display/depth recall branch.
