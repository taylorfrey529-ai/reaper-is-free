# Audio workspace setup

- REAPER 7.79 portable runtime: `/mnt/data/audio/runtime/reaper-7.79-portable`
- Launcher: `/mnt/data/audio/bin/reaper`
- Pristine source retained under `REAPER/7.79/linux-x86_64/pristine/`
- Upstream source retained under `REAPER/7.79/linux-x86_64/upstream/`
- Ubuntu 24.04 AMD64 audio packages retained under `linux-audio/ubuntu-24.04-amd/`
- The launcher uses a portable `reaper.ini`, so REAPER configuration stays with this workspace runtime.
- The current ChatGPT container has no `/dev/snd` device, so physical audio I/O cannot be validated here.
- Ubuntu-targeted `.deb` packages were not installed into the Debian host.

## Drum shell -> overhead phase alignment

A non-destructive REAPER alignment tool is staged in the portable runtime:

- ReaScript: `runtime/reaper-7.79-portable/Scripts/AI_Phase_align_drum_shells_to_overheads.lua`
- JSFX: `runtime/reaper-7.79-portable/Effects/utility/AI_Drum_Shell_Phase_Align`
- Last-run log (created when executed): `runtime/reaper-7.79-portable/phase-align-last-run.txt`

Behavior:
- Overhead/OH tracks are references only and are never moved.
- Close kick/snare/tom shell tracks are aligned from their own transients to the local corresponding arrival in the stereo overhead channels.
- Tom 1 is explicitly self-anchored: Tom 1 close-mic hits define the search windows, preventing it from being aligned to another drum's overhead transient.
- Alignment is applied as a dedicated sample-accurate delay/PDC stage, so it is non-destructive and repeatable.
- Existing alignment from this tool is neutralized before re-measuring, avoiding cumulative shifts on reruns.

Current blocker:
- No song `.RPP` project or multitrack drum media is present in the mounted workspace/Project files, so no real drum track has been changed yet.
