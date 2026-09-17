# Precision application patterns

Use these patterns for controls whose value changes continuously or whose hit target is small.

## Faders, knobs, sliders, and envelopes

1. Observe the control and any numeric readout.
2. Move the pointer to the visible control body or handle.
3. Click-hold only after target confirmation.
4. Apply a short drag vector.
5. Release and inspect the displayed value or visible result.
6. Repeat with smaller relative drags as the target value approaches.

Do not use one long drag when a small error would matter. Prefer two or three measured corrections over oscillating around the target.

## Menus and popup panels

Treat a newly opened menu as a new coordinate space. Re-observe after opening it. Do not reuse coordinates calculated before the menu existed.

## Timeline and item editing

For timeline placement, clip/item edges, automation points, and similar dense controls, verify zoom level and snapping state before fine pointer work. Recheck after scroll or zoom operations because both invalidate prior pixel-to-time assumptions.

## Native automation handoff

Native automation is appropriate when any of these dominates:

- exact numeric entry is required;
- many repetitive edits must be identical;
- mouse-only manipulation would accumulate drift;
- recovery from a malformed state is safer through the application's own API or project format;
- accessibility or rendering prevents trustworthy pointer targeting.

After native automation, return to the visible application and verify the change before continuing.

## Demonstrable control loop

For work the user expects to watch, keep the recording running across the entire observe-act-observe cycle. Make the pointer trajectory visible, pause briefly on small targets, perform one bounded adjustment, and capture the post-action state before any dependent edit. For REAPER faders and knobs, prefer a short `drag-human` movement followed by a visible value/state check. When testing rather than editing the user's project, use a disposable project copy and undo the demonstration change after verification.
