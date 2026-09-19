---
name: virtual-drums
description: Build, repair, map, humanize, route, mix, render, and validate virtual drum workflows in REAPER, especially MT Power Drum Kit (MTPDK) multi-output kits with MIDI note/CC mapping, full-length performances, overhead/room stereo correlation targets, all-pass phase alignment, Virtual Apollo validation, and evidence handoff. Use when a user asks for virtual drums, MTPDK setup or repair, a drum MIDI map, all MIDI CC assignments, multi-output drum routing, overhead/room phase or LR correlation work, drum humanization, a new/full-length MIDI drum performance, drum rendering, or verification of REAPER drum signal flow.
---

# Virtual Drums

Treat the live REAPER project and verified audio boundary as authority. Preserve approved routing, MIDI, phase, and mix continuity instead of rebuilding from generic assumptions.

## Compose with installed workspace skills

When available, invoke these helpers for their narrow jobs:

- `reaper-v7-79` for runtime probing, project/routing rules, and Virtual Apollo validation.
- `mouse-keyboard` for visible REAPER interaction and full-turn recording.
- `screenshot-vm` for genuine final desktop evidence.
- `mit-magic-cookie-1` when X11 authorization or display recovery is required.

Use terminal/ReaScript for exact repetitive edits, but verify the result visibly inside REAPER.

## Operating sequence

1. Probe the live runtime and identify the active `.RPP`, display, REAPER version, audio backend, sample rate, and Virtual Apollo state.
2. Back up the current `.RPP` before any destructive or structural change.
3. Determine whether the request is mapping, routing, performance, phase/stereo work, rendering, repair, or a combination.
4. Apply the smallest deterministic change that preserves the known-good project.
5. Verify inside REAPER.
6. Verify important audio changes through the actual 48 kHz stereo Virtual Apollo boundary.
7. Save the project, capture a real final screenshot, finish the screen recording, and upload the final evidence bundle to Google Drive when connected.

Never claim a route, plugin, render, or MIDI fix works from project text or GUI meters alone when an audio-boundary test is possible.

## MTPDK mapping contract

Load `references/mtpdk-midi-map.json` for the canonical machine-readable map. Use `references/mtpdk-note-map.csv` and `references/mtpdk-cc-map.csv` when a compact table is enough.

Preserve these channel roles:

- MIDI channel 1: drum notes.
- MIDI channel 16: controller automation.
- CC `n` maps to exposed MTPDK parameter index `n` for CC 0 through 127 unless live parameter enumeration proves the plugin version differs.

Before creating a new map, enumerate the live plugin parameters. Do not bind controllers to unnamed placeholder parameters merely because the plugin exposes thousands of automation slots.

### Critical MTPDK note encoding rule

MTPDK's stored Map values reserve `0 = off`. For a nonzero Map value:

`canonical MIDI note = stored value - 1`

Do not use the stored value directly as the MIDI note. This exact off-by-one error turns Kick 36 into SideStick 37.

Require at minimum:

- Kick main = 36
- SideStick main = 37
- Snare main = 38

Run `scripts/validate_mtpdk_map.py` after map creation or repair. For a generated Standard MIDI File, run `scripts/validate_midi_performance.py` and inspect the articulation counts.

## MTPDK output topology

Use one 16-channel `MTPDK SOURCE` track feeding eight stereo returns:

1. Out 1 -> Kick
2. Out 2 -> Snare + SideStick
3. Out 3 -> Tom Hi
4. Out 4 -> Tom Mid
5. Out 5 -> Tom Low
6. Out 6 -> Open/Closed/half-open Hi-Hat + pedal chick
7. Out 7 -> Ride + Bell
8. Out 8 -> Crash L/R + choked Crash + China + Splash

Disable direct master send on the MTPDK source and its eight returns. Send the returns into the existing `DRUMS BUS`, then preserve the established downstream mix-bus/master path.

After any map or routing repair, perform an isolated identity test:

- MIDI 36 must produce signal on the Kick return and effectively no Snare/SideStick return signal.
- MIDI 37 must produce signal on the Snare/SideStick return and effectively no Kick return signal.

Treat this as stronger evidence than labels or parameter text.

## MTPDK session gate

The free MTPDK build can reopen muted. Inspect the plugin UI when playback produces MIDI activity but no audio. Click its `START` control once per REAPER session when the UI reports that sound is muted.

Also verify the FX bypass state. A green/loaded FX chain is not sufficient evidence that the instrument is producing audio.

## Acoustic drum hierarchy

Use the stereo overhead/room image as the acoustic reference when those tracks exist.

**OVERHEADS = KIT.**

- Keep OH/Room placement and stereo image authoritative.
- Treat kick, snare, and tom close tracks as reinforcement.
- Align a close shell toward its image in the overheads; do not make overheads chase the close mic.
- Prefer phase rotation/all-pass filtering over waveform time nudging unless the user explicitly requests time movement.
- Preserve polarity unless measurement supports inversion.

For this workflow, target true stereo OH/Room ambience at approximately `LR_corr = +0.10`, normally with tolerance `+/- 0.02`.

Do not apply the +0.10 target to close shells or to the full drum mix. Tune each stereo ambience source independently using unity-magnitude, channel-specific all-pass decorrelation. Measure the actual processed source, not a guessed width control.

Run `scripts/analyze_stereo_corr.py` on a captured OH/Room WAV to verify the target.

## Full-length performance defaults

Preserve the project's existing tempo and time signature. If the user asks for a new full-length performance without a form, use a 128-bar form as the default and adapt it to the current tempo:

- Intro: 8 bars
- Verse 1: 16
- Pre-Chorus 1: 8
- Chorus 1: 16
- Verse 2: 16
- Pre-Chorus 2: 8
- Chorus 2: 16
- Bridge: 16
- Final Chorus: 16
- Outro: 8

Use mapped articulations rather than hard-coded guesses. Build musical variation across sections with hats, ride, crashes, fills, tom movement, and dynamics. Keep SideStick intentional rather than substituting it for Kick or Snare.

Use CC53 for broad MTPDK global-volume section dynamics when appropriate. Keep structural CC events sparse and deliberate.

## Humanization

Humanize only drum-note events on MIDI channel 1 unless the user requests controller humanization.

Use deterministic seed `529` by default for reproducibility. Keep the established natural range approximately:

- average timing movement around 2 ms;
- maximum timing movement around 5 ms;
- average velocity movement around 3 to 4 MIDI velocity units;
- maximum velocity movement around 9 units.

Preserve intentional flams/fills and do not re-quantize after humanization unless explicitly requested. Keep channel-16 CC events sample/PPQ exact.

## Render and capture rules

Prefer a normal REAPER render when the instrument supports it, but validate the resulting WAV before promotion.

MTPDK's free-session gate can mute offline rendering. If an offline render is correctly formatted but silent:

1. Reject it as a master.
2. Re-enable MTPDK in the live session.
3. Confirm live audio through Virtual Apollo before starting a long pass.
4. Capture the full performance in real time through the verified Apollo PCM path.
5. Trim only proven capture lead-in/tail silence.
6. Convert to the requested delivery depth while preserving 48 kHz stereo unless the user requests another format.

Never preserve a silent render as the accepted master.

## Validation standard

Require the relevant boundary for the claim:

- Note map -> map validator plus isolated return identity test.
- CC map -> 128 links read back or otherwise verified.
- Routing -> reopened project plus audible Apollo capture.
- OH/Room correlation -> source-only capture measured near +0.10.
- Full performance -> complete MIDI length/event check plus real audio playback.
- Master -> duration, sample rate, channels, bit depth, peaks/RMS, and non-silence validation.

Keep full-mix L/R correlation separate from the OH/Room target. A full drum mix around +0.7 does not violate a +0.10 overhead rule.

## Evidence and handoff

For substantial REAPER work, preserve:

- pre-change `.RPP` checkpoint;
- final `.RPP`;
- MIDI map files;
- final `.mid` when performance work occurred;
- validated WAV/capture when audio changed;
- concise validation report;
- full-turn desktop recording;
- final genuine desktop screenshot.

When Google Drive is connected, upload the completed bundle before ending the turn. Keep rejected/silent artifacts clearly labeled or omit them from the primary handoff.

## Bundled resources

- `references/mtpdk-midi-map.json` - canonical corrected MTPDK note and CC map.
- `references/mtpdk-note-map.csv` - compact note/articulation table.
- `references/mtpdk-cc-map.csv` - CC 0-127 to MTPDK exposed parameters.
- `references/reaper-note-names.txt` - REAPER note-name mapping.
- `references/production-rules.md` - routing, stereo, phase, performance, and evidence conventions.
- `scripts/validate_mtpdk_map.py` - reject the historical +1 note-decoding regression and malformed CC maps.
- `scripts/validate_midi_performance.py` - inspect a Standard MIDI File against the bundled MTPDK map.
- `scripts/analyze_stereo_corr.py` - measure PCM WAV L/R correlation and optionally enforce the +0.10 target.