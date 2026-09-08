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

Read `BOOT-HANDOFF-CURRENT.md` and `SNAPSHOT-INTEGRITY.md` first. The legacy `BOOT-HANDOFF.md` is historical detail only where its snapshot-transport wording conflicts.

## Fresh start

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
git checkout linux-ububtu-vm-workspace
cd linux-ububtu-vm-workspace
bash scripts/verify-regression.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
bash verify-runtime-bundles.sh /mnt/data
```

Reconcile restored source/config into:

```text
/mnt/data/ubuntu-desktop-workspace
/mnt/data/graphics-workspace
/mnt/data/virtual-apollo
```

Then boot:

```bash
python3 scripts/start-live-session.py
```

## Continuity locks

```text
X11/Openbox :88, 1440x900 where supported
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

## Vocabulary

- Restored = checksum-admitted backup/snapshot state recovered.
- Reconstructed = recreated from an admitted authority.
- Verified live = actually executed and observed in the current runtime.
