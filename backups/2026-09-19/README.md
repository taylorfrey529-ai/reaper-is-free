# REAPER / Virtual Drums Backup - 2026-09-19

Repository: `taylorfrey529-ai/reaper-is-free`
Backup branch: `backup/2026-09-19-virtual-drums`
Base branch: `linux-ububtu-vm-workspace`
Base head at backup start: `bb972fbd0f9101827cc2f68dbfe008bc1ab84579`

This snapshot preserves the reproducible REAPER 7.79 / Virtual Drums state produced in the live Linux workspace. It intentionally excludes bearer credentials, transient PID files, and large media/toolchain payloads that are better retained in Drive/persistent project storage than ordinary Git history.

## Included directly in GitHub

- Current `ASIO-Routing-Project.RPP` with the corrected MTPDK note mapping and full 128-bar humanized performance embedded in the project.
- Complete Virtual Drums skill source: `SKILL.md`, agent metadata, production rules, canonical note/CC/MIDI references, and all validator scripts.
- MTPDK note map, CC map, MIDI map, REAPER note names, routing proof, validation reports, and production reports.
- Current workspace README snapshot.
- SHA-256 integrity manifest for large source archives, packaged skill, standalone MIDI, and master audio.
- `DRIVE-EVIDENCE.txt` indexing the Google Drive evidence locations.

## Retained outside ordinary Git history

The packaged `skill.zip`, standalone `.mid`, 48 kHz/24-bit master WAV, full-turn MP4 recordings, screenshots, MTPDK installer ZIP, and large workspace/toolchain archives remain in Google Drive and/or persistent project sources. Their integrity hashes are recorded in `SHA256SUMS.txt`.

## Critical continuity rules

- MTPDK stored map values encode `MIDI note + 1`; zero means off.
- Correct primary notes: Kick 36, SideStick 37, Snare 38.
- Drum notes use MIDI channel 1; CC control uses channel 16.
- All 128 MIDI CCs are assigned to the useful exposed MTPDK parameter surface.
- Omega drum law: OVERHEADS = KIT; close shells are reinforcement.
- Stereo OH/Room ambience target: `LR_corr ~= +0.10` using all-pass decorrelation, not waveform time-shifting.
- Virtual Apollo boundary: 48 kHz stereo.

## Restore

1. Restore the canonical Linux workspace from the repository's existing restore system and persistent archives.
2. Replace the active REAPER project with `backups/2026-09-19/projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP`.
3. Restore the Virtual Drums skill from `backups/2026-09-19/virtual-drums/`, then package it with the normal skill packaging workflow if a `skill.zip` is required.
4. Use `DRIVE-EVIDENCE.txt` to retrieve the standalone MIDI/master/evidence when needed and verify them against `SHA256SUMS.txt`.
5. Restore MTPDK 2.1.5.1 and verify Kick 36 / SideStick 37 / Snare 38 before playback.
6. Validate the 48 kHz stereo Virtual Apollo boundary before claiming the session is recovered.
