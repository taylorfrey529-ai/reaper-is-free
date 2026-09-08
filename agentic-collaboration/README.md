# Waveform / Pause / Waveform Agentic Collaboration

This backup captures an audio-native collaboration primitive for Agent Musicians working in a DAW.

## Core idea

A musical agent does not need to "talk" only with text. Its performance can itself be the utterance:

```text
WAVEFORM(Agent A) -> PAUSE / LISTEN / HANDOFF -> WAVEFORM(Agent B)
```

The waveform is an authored musical statement. The pause is an intentional turn boundary: time for another agent to listen, inspect shared song state, accept or reject the implied musical idea, and prepare a response. The next waveform is the response.

This makes agentic collaboration native to a DAW timeline. It can represent call-and-response, groove negotiation, fills answered by bass or guitar, producer interventions, engineer listening windows, and human participation.

## Invariants

1. A dialogue begins with a waveform.
2. Two waveform turns may not overlap inside one dialogue lane.
3. A handoff pause separates adjacent turns.
4. The pause has an explicit duration rather than being discarded as "nothing."
5. A response records both the responding agent and the agent whose waveform it follows.
6. Musical audio/MIDI remains the authoritative performance; text metadata only describes ownership and intent.
7. Every accepted response can become a new REAPER take/revision instead of destructively replacing the previous performance.

## Example

```text
0.000 - 2.400  WAVE   Drummer     groove statement
2.400 - 2.750  PAUSE  handoff     listening window
2.750 - 4.700  WAVE   Bassist     rhythmic answer
4.700 - 5.050  PAUSE  handoff     listening window
5.050 - 7.300  WAVE   Guitarist   harmonic answer
```

The corresponding code lives in `WaveformDialogue.lua`.

## REAPER mapping

`WaveformDialogue.lua` can materialize a dialogue as REAPER timeline regions/markers when run inside ReaScript:

- waveform turn -> region named `[AGENT:<name>] WAVE`
- pause boundary -> marker named `[HANDOFF] <from> -> <to>`

The eventual production system can bind each waveform turn to concrete REAPER media items, MIDI items, takes, automation, or rendered agent buses while preserving the same protocol.

## Why the pause matters

The pause is not empty data. It is synchronization. It is where ownership changes, a collaborator listens, shared state is reconciled, and the next agent earns the turn. In musical terms it is breath, space, anticipation, and permission to answer.
