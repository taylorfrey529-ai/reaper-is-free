# REAPER workspace backup

This repository is the recovery and continuity authority for the custom REAPER 7.79 production workspace and its agent-assisted audio tooling.

## Start here

- [`RECALL.md`](RECALL.md) — fresh-session repository recovery card.
- [`GOLDEN-MASTER.md`](GOLDEN-MASTER.md) — exact byte-preserved binary recovery tier and admission rules.
- [`golden-master/MANIFEST.json`](golden-master/MANIFEST.json) — machine-readable payload/storage map.
- [`linux-ububtu-vm-workspace/RECALL.md`](linux-ububtu-vm-workspace/RECALL.md) — live Linux/X11/Openbox/REAPER boot card.
- [`linux-ububtu-vm-workspace/BOOT-HANDOFF-CURRENT.md`](linux-ububtu-vm-workspace/BOOT-HANDOFF-CURRENT.md) — current detailed boot authority.
- [`linux-ububtu-vm-workspace/SNAPSHOT-INTEGRITY.md`](linux-ububtu-vm-workspace/SNAPSHOT-INTEGRITY.md) — admitted, historical, reconstructed, and rejected snapshot identities.
- [`audio/SETUP.md`](audio/SETUP.md) — audio workspace setup details.

## Included

- Workspace setup, package metadata, source/config recovery payloads, and SHA-256 provenance.
- X11/Openbox live-session recovery and REAPER 7.79 launcher behavior.
- Virtual Apollo / `apollo_spdif` ALSA continuity configuration.
- Exact Golden Master binary identities, storage locations, split-transport hashes, and verification tooling.
- `AI_Phase_align_drum_shells_to_overheads.lua` ReaScript.
- `AI_Drum_Shell_Phase_Align` JSFX processor.
- Agent collaboration protocol under `agentic-collaboration/`.
- CI regression checks for snapshot reconstruction, Golden Master identity, and canonical audio locks.

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

Golden Master ID (SHA-256 of golden-master/SHA256SUMS):
74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f

Rejected corrupt historical GitHub blob:
8276f6dda44535734ed0da4bf395df5bd32c16583246e02af63882a6e4db1f28
```

The current GitHub source/config recovery payload is stored as independently hashed UTF-8 base64 parts under `linux-ububtu-vm-workspace/source-snapshot.parts/` and rebuilt/validated by `restore.sh`.

The exact 888,467,386-byte Golden Master payload set is stored outside ordinary Git blobs in a private Google Drive snapshot and is admitted only by the hashes in `golden-master/`. The two >300 MB archives are losslessly split into ordered 64 MiB transport parts and must reassemble to the recorded final hashes.

## Regression gate

Run before promoting workspace changes:

```bash
bash linux-ububtu-vm-workspace/scripts/verify-regression.sh
```

For a downloaded Golden Master payload directory:

```bash
bash golden-master/verify-golden-master.sh /path/to/GM-2026-09-08
```

GitHub Actions runs the repository regression gate on both `main` and `linux-ububtu-vm-workspace` when the recovery surface changes.

## Binary distribution boundary

The binary assets are not ordinary Git blobs. Their exact recovery copies live in the private Golden Master storage tier and remain subject to their respective licenses and distribution terms. REAPER remains subject to Cockos' own license and distribution terms.
