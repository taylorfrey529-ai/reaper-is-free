# Virtual Drums Production Rules

## Continuity priorities

1. Preserve the active REAPER project and its routing.
2. Preserve the overhead/room stereo image as acoustic truth.
3. Treat close shells and virtual outputs as reinforcement.
4. Make changes reversible and checkpoint the `.RPP` first.
5. Prove audio at Virtual Apollo before promotion.

## Current stereo convention

- OH and Room-style stereo ambience target: `LR_corr ~= +0.10`.
- Normal acceptance window: `0.08 .. 0.12` unless the user requests tighter tolerance.
- Do not force close-mic tracks or the complete drum bus to +0.10.
- Prefer a unity-magnitude all-pass network on one channel for decorrelation.
- Tune each source separately; do not reuse one OH setting blindly on a Room track.

## Current phase convention

- Do not move OH/Room waveforms to match close mics.
- Prefer all-pass phase rotation on kick/snare/tom reinforcement when phase alignment is needed.
- Preserve source item position at zero unless the user explicitly requests time alignment.
- Compare the processed shell against its corresponding overhead image, not only against another close mic.

## MTPDK multi-out convention

- Source: 16 channels, no direct master send.
- Out 1: Kick.
- Out 2: Snare/SideStick.
- Out 3: Tom Hi.
- Out 4: Tom Mid.
- Out 5: Tom Low.
- Out 6: Hi-Hats/Pedal.
- Out 7: Ride/Bell.
- Out 8: Crashes/China/Splash.
- Return tracks: no direct master send; route to DRUMS BUS.
- DRUMS BUS continues through the established MIX BUS/master path.

## MTPDK note encoding regression to prevent

The plugin's stored mapping uses `0 = off`, otherwise `stored = MIDI note + 1`.

Canonical main notes:

- Kick 36
- SideStick 37
- Snare 38
- Tom Low 41
- Closed Hat 42
- Half/Open Hat 44
- Tom Mid 45
- Open Hat 46
- Tom Hi 48
- Crash L 49
- Ride 51
- China 52
- Bell 53
- Splash 55
- Crash R 57
- Crash R choked 58
- HH Pedal 65

The previous wrong interpretation used the stored value directly, making intended Kick 36 events become note 37 and trigger SideStick. Always validate after mapping changes.

## Full performance convention

Default no-form 128-bar layout:

| Section | Bars |
|---|---:|
| Intro | 8 |
| Verse 1 | 16 |
| Pre-Chorus 1 | 8 |
| Chorus 1 | 16 |
| Verse 2 | 16 |
| Pre-Chorus 2 | 8 |
| Chorus 2 | 16 |
| Bridge | 16 |
| Final Chorus | 16 |
| Outro | 8 |

Preserve existing project tempo. Use deterministic humanization seed 529, note channel 1, CC channel 16.

## Evidence convention

A completion claim should include, when applicable:

- isolated Kick/SideStick return test;
- 48 kHz stereo Apollo capture;
- full-length master validation;
- map JSON/CSV;
- MIDI file;
- pre-change and final `.RPP`;
- final screenshot and full-turn recording;
- Google Drive copy when connected.