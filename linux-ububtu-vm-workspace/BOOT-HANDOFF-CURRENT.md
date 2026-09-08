# Current boot handoff — linux-ububtu-vm-workspace

This is the current operational handoff. The older `BOOT-HANDOFF.md` is retained as historical detail; where snapshot transport instructions conflict, this file and `SNAPSHOT-INTEGRITY.md` take precedence.

## Identity and locks

```text
Repository: taylorfrey529-ai/reaper-is-free
Branch: linux-ububtu-vm-workspace
Historical backup commit: 350f07895fbca399dfe0c50ca1e4c5723e9a9a58
Full backup SHA-256: c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a
Current GitHub source snapshot SHA-256: be32a0d06c9836b8bdbba56d01e98fd8fe0c1adb705bb54b473780f24805beac
Desktop: X11 / Openbox
Display: :88
Geometry: 1440x900 where supported
REAPER: 7.79 Linux x86_64
Project: ASIO-Routing-Project
Backend: ALSA / linux_audio_mode=1
Interface: apollo_spdif
S/PDIF: stereo 2-in / 2-out
Sample rate: 48000 Hz
Buffer: 256 samples x 3
Tempo: 120 BPM, 4/4
```

## Fresh recovery

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
git checkout linux-ububtu-vm-workspace
cd linux-ububtu-vm-workspace
bash scripts/verify-regression.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
bash verify-runtime-bundles.sh /mnt/data
```

Use the restored source/config state to populate/reconcile:

```text
/mnt/data/ubuntu-desktop-workspace
/mnt/data/graphics-workspace
/mnt/data/virtual-apollo
```

Do not overwrite a newer approved live state blindly. Runtime binaries are external; restore only exact hash-matching bundles from `RUNTIME-BUNDLES.md`. Do not substitute another REAPER version.

## Boot

After canonical live roots and runtime binaries are present:

```bash
python3 scripts/start-live-session.py
```

The launcher must preserve the legitimate REAPER license/evaluation UI. It may detect/report the prompt but must not dismiss, suppress, patch, or bypass it.

## Acceptance gate

Do not claim the workspace is booted until applicable live checks pass:

```text
[ ] regression source snapshot gate passes
[ ] runtime bundle hashes pass
[ ] X11 :88 reachable
[ ] Openbox/session live
[ ] REAPER 7.79 process/window live
[ ] ASIO-Routing-Project opened
[ ] linux_audio_mode=1
[ ] apollo_spdif 2-in/2-out at 48 kHz
[ ] 256 samples x 3
[ ] Virtual Apollo real-time pacing works
[ ] playback advances in real time
[ ] agent-ear capture receives non-silent PCM during known playback
[ ] real X11 screenshot captured/validated when requested
```

The canonical project path remains:

`/mnt/data/ubuntu-desktop-workspace/projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP`

The canonical ear path remains:

`/mnt/data/virtual-apollo/ears/latest.wav`

Use `SNAPSHOT-INTEGRITY.md` for restore provenance and rejected identities. Use `RUNTIME-BUNDLES.md` for external binary identities.
