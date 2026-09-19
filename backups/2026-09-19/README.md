# REAPER / Virtual Drums Backup - 2026-09-19

Repository: `taylorfrey529-ai/reaper-is-free`
Backup branch: `backup/2026-09-19-virtual-drums`
Base branch: `linux-ububtu-vm-workspace`
Base head at backup start: `bb972fbd0f9101827cc2f68dbfe008bc1ab84579`

This snapshot preserves the reproducible REAPER 7.79 / Virtual Drums state produced in the live Linux workspace. It intentionally excludes bearer credentials, transient PID files, and giant media/toolchain payloads that cannot be written through the GitHub connector or exceed ordinary GitHub file-size limits.

## Included directly in GitHub

- Current `ASIO-Routing-Project.RPP` with corrected MTPDK note mapping and full 128-bar humanized performance.
- Virtual Drums skill source, references, scripts, and metadata.
- Packaged Virtual Drums `skill.zip`, encoded as base64 text for lossless reconstruction.
- MTPDK note map, CC map, MIDI map, REAPER note names, corrected full-length MIDI, validation and production reports.
- Reproducible desktop source/config files required to reconstruct the Astra-style workspace shell.
- SHA-256 manifest for large source archives and master audio retained outside ordinary Git storage.

## Critical continuity rules

- MTPDK stored map values encode `MIDI note + 1`; zero means off.
- Correct primary notes: Kick 36, SideStick 37, Snare 38.
- Drum notes use MIDI channel 1; CC control uses channel 16.
- All 128 MIDI CCs are assigned to the useful exposed MTPDK parameter surface.
- Omega drum law: OVERHEADS = KIT; close shells are reinforcement.
- Stereo OH/Room ambience target: `LR_corr ~= +0.10` using all-pass decorrelation, not waveform time-shifting.
- Virtual Apollo boundary: 48 kHz stereo.

## Large binary policy

Large WAV/MP4 evidence and large workspace/toolchain archives remain in the project's Google Drive evidence hierarchy and/or persistent project sources. Their exact hashes are recorded in `SHA256SUMS.txt`. Do not replace a binary unless its hash is intentionally changed and documented.

## Restore

1. Restore the canonical Linux workspace from the repository's existing restore system and persistent archives.
2. Replace the active REAPER project with `projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP` from this backup folder.
3. Install the `virtual-drums` skill source from this backup, or decode `skill.zip.b64` to recover the packaged skill.
4. Restore MTPDK 2.1.5.1 and verify the corrected Kick/SideStick/Snare map before playback.
5. Validate the 48 kHz stereo Virtual Apollo boundary before claiming the session is recovered.