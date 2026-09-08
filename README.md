# REAPER workspace backup

This repository is the recovery and continuity authority for the custom REAPER 7.79 production workspace and its agent-assisted audio tooling.

## Start here

- [`RECALL.md`](RECALL.md) — fresh-session repository recovery card.
- [`linux-ububtu-vm-workspace/RECALL.md`](linux-ububtu-vm-workspace/RECALL.md) — live Linux/X11/Openbox/REAPER boot card.
- [`linux-ububtu-vm-workspace/BOOT-HANDOFF-CURRENT.md`](linux-ububtu-vm-workspace/BOOT-HANDOFF-CURRENT.md) — current detailed boot authority.
- [`linux-ububtu-vm-workspace/SNAPSHOT-INTEGRITY.md`](linux-ububtu-vm-workspace/SNAPSHOT-INTEGRITY.md) — admitted, historical, reconstructed, and rejected snapshot identities.
- [`audio/SETUP.md`](audio/SETUP.md) — audio workspace setup details.

## Included

- Workspace setup, package metadata, source/config recovery payloads, and SHA-256 provenance.
- X11/Openbox live-session recovery and REAPER 7.79 launcher behavior.
- Virtual Apollo / `apollo_spdif` ALSA continuity configuration.
- `AI_Phase_align_drum_shells_to_overheads.lua` ReaScript.
- `AI_Drum_Shell_Phase_Align` JSFX processor.
- Agent collaboration protocol under `agentic-collaboration/`.
- CI regression checks for snapshot reconstruction and canonical audio locks.

The drum alignment workflow keeps the stereo overheads fixed and non-destructively time-aligns close drum shells to their corresponding overhead arrivals. Tom 1 remains explicitly self-anchored to Tom 1 transients in the stereo overheads.

## Continuity locks

```text
REAPER: 7.79 Linux x86_64
Desktop: X11 / Openbox
Display: :88
Audio backend: ALSA (linux_audio_mode=1)
Interface: apollo_spdif
S/PDIF: stereo 2-in / 2-out
Sample rate: 48000 Hz
Buffer: 256 samples x 3
Project: ASIO-Routing-Project
Tempo: 120 BPM / 4/4
```

Never regress `linux_audio_mode` to `0` (JACK). Preserve REAPER's legitimate license/evaluation UI; detect and report it without suppressing or bypassing it.

## Snapshot authority

```text
Full local backup SHA-256:
c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a

Current reconstructed GitHub source/config snapshot SHA-256:
be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac

Rejected corrupt historical GitHub blob:
8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28
```

The current GitHub source/config recovery payload is stored as independently hashed UTF-8 base64 parts under `linux-ububtu-vm-workspace/source-snapshot.parts/` and is rebuilt/validated by `restore.sh`.

## Regression gate

Run before promoting workspace changes:

```bash
bash linux-ububtu-vm-workspace/scripts/verify-regression.sh
```

GitHub Actions runs the same gate on both `main` and `linux-ububtu-vm-workspace` when the recovery surface changes.

## Not included

REAPER application binaries, bundled REAPER resources, Ubuntu `.deb` packages, large SDK/toolchain archives, and other third-party binary assets are intentionally not ordinary Git blobs. Exact admitted external runtime bundle hashes are recorded in `linux-ububtu-vm-workspace/RUNTIME-BUNDLES.md`.

REAPER remains subject to Cockos' own license and distribution terms.
