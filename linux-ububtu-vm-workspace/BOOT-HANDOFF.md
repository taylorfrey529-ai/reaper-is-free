# HANDOFF — Boot `linux-ububtu-vm-workspace`

You are taking control of the previously built Linux/Ubuntu-style REAPER production workspace.

## Primary authority

Repository: `https://github.com/taylorfrey529-ai/reaper-is-free`

Branch: `linux-ububtu-vm-workspace`

Backup root: `linux-ububtu-vm-workspace/`

Canonical backup commit: `350f07895fbca399dfe0c50ca1e4c5723e9a9a58`

Do not rebuild the system from assumptions when the backup already defines the state. Treat the GitHub backup, README, restore script, manifests, checksums, REAPER project/configuration, graphics workspace, and Virtual Apollo implementation as continuity authority.

## Objective

Recover, boot, validate, and continue the existing `linux-ububtu-vm-workspace`.

Required end state:

- X11 virtual desktop
- Openbox session
- 1440x900 virtual display where supported
- REAPER 7.79 Linux x86_64
- existing `ASIO-Routing-Project`
- ALSA backend
- simulated `apollo_spdif` interface
- stereo S/PDIF, 2-in / 2-out
- 48 kHz
- 256-sample buffer x 3
- real-time audio backpressure
- rolling agent-ear PCM capture
- Vulkan/llvmpipe graphics path
- real `$screenshot-vm` validation with no Image Gen

## 1. Recover the GitHub state

```bash
git clone https://github.com/taylorfrey529-ai/reaper-is-free.git
cd reaper-is-free
git checkout linux-ububtu-vm-workspace
cd linux-ububtu-vm-workspace
```

Confirm the branch contains at least:

```text
README.md
BOOT-HANDOFF.md
restore.sh
SHA256SUMS
BINARY-MANIFEST.md
source-snapshot.tar.gz.b64
```

Read `README.md`, `SHA256SUMS`, and `BINARY-MANIFEST.md` before changing state.

## 2. Restore the source/config snapshot

```bash
chmod +x restore.sh
bash restore.sh /mnt/data/linux-ububtu-vm-workspace-restored
```

The restore flow must decode `source-snapshot.tar.gz.b64`, verify SHA-256, and stop on mismatch before extracting.

Expected source/config snapshot SHA-256:

```text
92327daed33fc5b352987c33a06700ac24ee09e8ef835c0ec57a535d4c1dba84
```

Full local compressed backup SHA-256:

```text
c67b69e513484e0a5870bd7f55a34a280b3b771b7a5b825cc9ef5bfb932bb31a
```

The uploaded full-backup archive from the handoff session was independently checked at 6,456,501 bytes and matched that full-backup SHA-256.

## 3. Reconstitute canonical workspace paths

Previous live locations:

```text
/mnt/data/ubuntu-desktop-workspace
/mnt/data/graphics-workspace
/mnt/data/virtual-apollo
```

Restore their equivalents from the verified source snapshot. If a live target already exists, compare it with the recovered state and preserve any newer approved state rather than overwriting blindly.

## 4. Recover runtime dependencies

Large third-party/runtime binaries are intentionally excluded from the GitHub source/config backup. Prefer exact local artifacts already staged in the ChatGPT workspace, including when present:

```text
/mnt/data/audio.zip
/mnt/data/graphics.zip
/mnt/data/packages.zip
/mnt/data/toolchains.zip
/mnt/data/operating-system.zip
```

Recover REAPER 7.79 Linux x86_64 from the local audio package when available. Do not silently substitute a different REAPER version.

## 5. Boot X11/Openbox

Preferred live display:

```text
DISPLAY=:88
```

Target geometry:

```text
1440x900
```

Verify before assuming the display exists:

```bash
xdpyinfo -display :88
```

If unavailable, use the recovered desktop startup script, typically:

```bash
cd /mnt/data/ubuntu-desktop-workspace
./start-desktop.sh
```

Then verify:

```bash
DISPLAY=:88 xdpyinfo
DISPLAY=:88 xwininfo -root -tree
```

The desktop must be genuinely rendered by X11. Never substitute generated imagery for failed desktop rendering.

## 6. Restore graphics

Recover `/mnt/data/graphics-workspace` and use its graphics environment/verification scripts. The validated graphics route is Vulkan on Mesa llvmpipe under X11/Xvfb. Software rendering is acceptable and must not be described as hardware acceleration.

Expected reusable scripts include:

```text
graphics-env.sh
run-x11-vulkan.sh
verify-graphics.sh
```

## 7. Boot Virtual Apollo S/PDIF

Recover `/mnt/data/virtual-apollo`.

This is an explicit userspace simulation of Apollo-style S/PDIF routing, not a real Universal Audio Thunderbolt/ASIO driver.

Canonical audio identity/state:

```text
Backend: ALSA
Interface: apollo_spdif
Inputs: 2
Outputs: 2
Sample rate: 48000 Hz
Buffer: 256 samples
Buffers: 3
Clocking: real-time wall-clock paced
```

The interface must expose stereo S/PDIF input/output, stable full-duplex operation, output capture/tap, agent-ear telemetry, and 48 kHz real-time backpressure.

Do not regress to the earlier unclocked sink behavior that drained REAPER output faster than real time.

## 8. Restore REAPER audio configuration

Canonical REAPER Linux settings:

```ini
alsa_indev=apollo_spdif
alsa_outdev=apollo_spdif
alsa_rtprio=0
linux_audio_bits=32
linux_audio_bsize=256
linux_audio_bufs=3
linux_audio_mode=1
linux_audio_nch_in=2
linux_audio_nch_out=2
linux_audio_srate=48000
linux_audio_srateor=1
```

Critical continuity lock:

```text
linux_audio_mode=1 = ALSA
```

Do not set `linux_audio_mode=0`; that previously selected JACK and produced the audio-hardware/JACK-server error.

## 9. Open the canonical project

Canonical project path:

```text
/mnt/data/ubuntu-desktop-workspace/projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP
```

Preferred launch pattern:

```bash
DISPLAY=:88 \
HOME=/mnt/data/ubuntu-desktop-workspace/home \
XDG_CONFIG_HOME=/mnt/data/ubuntu-desktop-workspace/config \
/mnt/data/ubuntu-desktop-workspace/bin/launch-reaper.sh \
/mnt/data/ubuntu-desktop-workspace/projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP
```

Do not create a replacement project if the canonical RPP is recoverable.

## 10. Preserve drum-project continuity

The project includes/targets:

```text
Kick
Snare
Tom 1
Stereo Overheads
DRUMS BUS
8-Bar Drum Track - 120 BPM
```

Project timebase:

```text
Tempo: 120 BPM
Meter: 4/4
8 bars: 16.000 seconds
Audio: 48 kHz / 24-bit PCM source files
```

The final rendered mix was named:

```text
8_Bar_Drum_Track_120BPM.wav
```

Use `BINARY-MANIFEST.md` to validate known generated media hashes. If a generated WAV is unavailable, do not invent a replacement and call it byte-identical; clearly label any recreated file as reconstructed/derived.

## 11. Validate agent ears

Expected rolling capture path:

```text
/mnt/data/virtual-apollo/ears/latest.wav
```

When REAPER is stopped, digital silence is acceptable. During known non-silent playback, require measurable non-zero PCM before claiming the agent-ear path is operational.

A useful terminal check is:

```bash
sox /mnt/data/virtual-apollo/ears/latest.wav -n stat
```

The prior successful playback proof reached approximately -2.18 dBFS peak; that is historical evidence, not a required future target.

## 12. Test PLAY

Start REAPER playback with a real GUI control or trustworthy REAPER control mechanism. Verify all of:

1. the REAPER transport visibly reports playback;
2. project time advances in real time;
3. Virtual Apollo ear telemetry contains non-silent PCM.

If the 16-second project drains in a fraction of a second, repair the virtual-interface pacing before proceeding.

## 13. Screenshot verification

Use `$screenshot-vm` semantics. Do not use Image Gen.

Capture the live `:88` display, preferably at 1440x900, and validate the PNG before reporting success. For playback proof, capture REAPER while transport is genuinely running.

Suggested output:

```text
/mnt/data/linux-ububtu-vm-workspace-booted.png
```

## Final acceptance gate

Do not declare the workspace booted until all applicable checks pass:

```text
[ ] GitHub branch recovered
[ ] snapshot SHA-256 verified
[ ] desktop source restored
[ ] X11 display reachable
[ ] Openbox session running
[ ] graphics stack verified
[ ] REAPER 7.79 installed/recovered
[ ] ASIO-Routing-Project opened
[ ] linux_audio_mode=1
[ ] ALSA backend active
[ ] apollo_spdif input active
[ ] apollo_spdif output active
[ ] 48 kHz / 2-in / 2-out confirmed
[ ] real-time S/PDIF pacing confirmed
[ ] agent-ear tap operational
[ ] PLAY advances in real time
[ ] non-silent PCM reaches agent ears
[ ] real X11 screenshot captured and validated
```

## Continuity locks

Preserve unless explicitly changed by the user:

```text
Workspace: linux-ububtu-vm-workspace
Repository: taylorfrey529-ai/reaper-is-free
Backup branch: linux-ububtu-vm-workspace
Canonical backup commit: 350f07895fbca399dfe0c50ca1e4c5723e9a9a58
REAPER: 7.79 Linux x86_64
Audio backend: ALSA
Virtual interface: apollo_spdif
Digital format: stereo S/PDIF
Sample rate: 48000 Hz
REAPER buffer: 256 samples x 3
Desktop: X11 / Openbox
Preferred display: :88
Preferred geometry: 1440x900
Project: ASIO-Routing-Project
Tempo: 120 BPM
Meter: 4/4
```

## Reporting contract

At completion, report only verified state. Include the recovered GitHub commit, snapshot checksum result, display/session state, REAPER version, project path, active audio backend, Virtual Apollo status, S/PDIF sample rate/channel count, playback/ear telemetry result, screenshot link, and any missing third-party runtime or unrecoverable generated media.

Use these terms precisely:

- **Restored** — byte/config state recovered from backup.
- **Reconstructed** — recreated from source/config because an excluded runtime artifact was unavailable.
- **Verified live** — actually executed and observed in the current workspace.

Never describe reconstruction as byte-identical restoration without checksum evidence.

## Execute

Recover the GitHub backup and boot `linux-ububtu-vm-workspace` now. Proceed autonomously through recover -> restore -> runtime reconstruction -> desktop boot -> Virtual Apollo -> REAPER -> playback -> agent-ear validation -> `$screenshot-vm`.

Do not stop at configuration-file inspection. The required end state is a running, verified REAPER Linux workspace with real-time simulated Apollo S/PDIF audio flowing into the agent-ear capture path.
