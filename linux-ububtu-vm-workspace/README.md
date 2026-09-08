# linux-ububtu-vm-workspace

GitHub backup snapshot of the ChatGPT Linux/Ubuntu-style REAPER workspace as of 2026-09-08.

## Backed up here

The committed source/config snapshot contains the reproducible workspace state:

- X11/Openbox desktop shell, startup/stop/verification scripts, and launcher configuration.
- REAPER 7.79 user configuration needed for the current workspace.
- ASIO-Routing-Project RPP and Lua import/routing scripts.
- Virtual Apollo x4-style S/PDIF userspace interface source, ALSA configuration, telemetry state, and control scripts.
- Vulkan/X11 bootstrap and verification source.
- SHA-256 inventory for the larger local snapshot.

## Restore

Run:

```bash
bash restore.sh [output-directory]
```

The restore script decodes `source-snapshot.tar.gz.b64`, verifies its SHA-256, and extracts the source/config snapshot.

## Audio state

- REAPER backend: ALSA (`linux_audio_mode=1`)
- Interface name: `apollo_spdif`
- Stereo S/PDIF: 2 input / 2 output
- Sample rate: 48 kHz
- Buffer: 256 samples x 3
- REAPER project tempo: 120 BPM
- Generated drum arrangement: 8 bars / 16 seconds

## Snapshot integrity

Source/config snapshot SHA-256:

`92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84`

Full local compressed snapshot SHA-256:

`c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a`

## Large/runtime data policy

The GitHub backup intentionally excludes third-party REAPER application binaries, Vulkan SDK/Mesa/LLVM payloads, Chromium caches, runtime PIDs/FIFOs/logs, rolling agent-ear buffers, and generated WAV binaries. Important local binary/audio/evidence hashes are recorded in `BINARY-MANIFEST.md`. The full local compressed archive remains available separately from the workspace session.
