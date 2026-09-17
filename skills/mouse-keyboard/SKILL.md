---
name: mouse-keyboard
description: Operate a live graphical desktop through deliberate human-style mouse and keyboard input, including pointer movement, clicking, dragging, scrolling, typing, hotkeys, fine adjustments, window targeting, and evidence-backed verification. Use when ChatGPT needs to control GUI applications, REAPER, games such as World of Warcraft, virtual machines, desktop settings, or other workflows that should look and behave like a living operator using the computer. Favor visible pointer movement and mouse clicks for REAPER and gameplay; use application-native automation only when precision, repeatability, recovery, or safety makes it more appropriate. Record substantial operations and finish with a genuine screenshot of the resulting desktop state.
---

# Mouse & Keyboard

## Fresh-session bootstrap

Start a fresh or restored workspace by using only this skill folder. Do not depend on a previous development directory.

1. Run `scripts/preflight.sh :88`. Treat missing OS libraries/tools as runtime dependencies, not missing skill files. Read `references/dependencies.md` when preflight fails.
2. Run `scripts/self_test.sh :88 /mnt/data/mouse-keyboard-selftest` before substantial work. Require both the generated screenshot and short MP4 to validate.
3. Use the bundled input/capture/record/window scripts directly. They recover the matching local X server's existing authorization path automatically, so callers do not need to manually export `XAUTHORITY`.
4. If the session is absent rather than merely unauthorized, recover the workspace/display first; do not create a replacement desktop unless the user's workspace policy permits it.

Operate the computer as an embodied desktop user: observe the rendered state, move the pointer visibly, act, observe the result, and continue. Treat the live desktop as the authority. Never replace missing GUI evidence with generated or reconstructed imagery.

## Execution loop

1. Resolve the active desktop, display, authorization, resolution, and target window from the current workspace. Prefer an existing session; in the REAPER workspace, use canonical display `:88` unless the project explicitly establishes another display. Use `scripts/desktop_context.sh` when authorization or display geometry is not already verified; it may recover the server's existing `-auth` file path without printing cookie material.
2. Start a real screen recording before the first user-visible action when the task is substantial, system-changing, REAPER-related, gameplay-related, or otherwise requires evidence.
3. Capture or inspect the current desktop before acting when target position, focus, or window state is uncertain.
4. Identify the intended control from visible evidence or trustworthy window geometry. Do not click guessed coordinates blindly.
5. Move the pointer visibly to the target. Pause briefly when visual confirmation is useful.
6. Click, drag, scroll, type, or press the requested key sequence.
7. Observe the result. Verify the intended visible state before continuing to dependent actions.
8. Use native application automation only when it is safer or materially more precise than simulated input. Still verify the resulting GUI state.
9. Stop recording only after verification. Capture and validate a final genuine screenshot.
10. Return a concise action summary, verification status, recording path when required, and final screenshot path.

## Human-style pointer behavior

- Make pointer travel visible. Default to `move-human` or `click-at`; their path is a deterministic sine wave around the direct target vector instead of a teleport or generic arc.
- Scale movement duration, sine amplitude, and cycle count to distance. Keep the wave subtle for nearby controls and more visible for long travel; use slower movement when locating a small control or demonstrating an action.
- When already near a control, use short relative movement rather than jumping away and back.
- Hover briefly before clicks when the UI exposes tooltips, hover states, or small hit targets.
- Click only after the target is plausibly under the pointer. Re-observe if a window moved, resized, opened a menu, or changed layout.
- Use double-click, right-click, hold, drag, and wheel events only when the visible UI calls for them.
- For fine adjustments, prefer small relative drags with verification between passes. Do not overshoot repeatedly by using one large blind drag.

## Keyboard behavior

- Establish focus before typing. Prefer a visible click into the intended control, editor, console, or field.
- Type ordinary text with a small per-character interval so the application receives events reliably and the recording remains legible.
- Use hotkeys for normal human shortcuts such as save, undo, copy, paste, navigation, and transport when appropriate.
- For destructive shortcuts, confirm the focused application and visible target state first.
- Do not expose passwords, authentication cookies, API keys, or other secrets in typed commands, logs, screenshots, or recordings.

## REAPER policy

Favor mouse movement, clicking, wheel input, and deliberate drags for REAPER controls so edits remain visible and auditable.

- Use the mouse first for track selection, faders, pans, sends, plugin controls, timeline placement, item manipulation, routing dialogs, and other ordinary GUI work.
- For knobs and faders, use small drag passes for fine adjustment and inspect the displayed value or resulting meters after each meaningful change.
- Avoid hard-coded modifier assumptions for precision controls. Respect the actual REAPER version, current preferences, and established workspace behavior.
- Use ReaScript, REAPER actions, project-text edits, or other native automation when exact numeric values, repetitive batch work, routing structure, recovery, or deterministic edits make mouse-only control inferior.
- After native automation, verify inside the visible REAPER GUI before claiming success.
- Preserve the active project, established track organization, routing, and known-good checkpoints unless the request explicitly changes them.

For additional precision patterns, read `references/precision-apps.md`.

## Gameplay policy

Treat games as interactive visual systems rather than static forms.

- Prefer direct mouse and keyboard control for movement, camera, targeting, menus, inventory, and ordinary gameplay interaction.
- Keep control loops bounded: observe, act briefly, observe again. Do not run unattended infinite input loops.
- Reacquire window focus and geometry after resolution, fullscreen, UI-scale, zoning, loading-screen, or window-mode changes.
- For tiny UI targets, zoom or inspect the rendered frame when possible rather than guessing.
- Respect the application's rules and the user's authorization. This skill controls the local input surface; it does not bypass anti-cheat, access controls, or platform restrictions.

## Coordinate and window rules

- Prefer coordinates derived from the current rendered frame or current window geometry.
- Treat saved pixel coordinates as temporary hints, never permanent truth across resolution or UI-layout changes.
- Use root-desktop coordinates only after confirming the current resolution.
- When a trustworthy window ID exists, obtain its current geometry rather than assuming an old position.
- After any action that can move, resize, open, close, scroll, zoom, or relayout the interface, invalidate stale target coordinates.

## Bundled tools

Use `scripts/input_driver.py` for deterministic X11 input when no higher-level desktop-control tool is available. Prefer its human-motion commands for user-visible work: `move-human` uses a deterministic sine-wave path with distance-scaled timing, amplitude, and cycle count; `click-at` combines that movement with a short hover and click; `drag-human` applies the same sine path while holding the selected button. A tapering envelope forces zero lateral offset at the start and target so the pointer lands exactly on small controls. These avoid random drift while keeping the action legible in a recording.

Examples:

```bash
python3 scripts/input_driver.py --display :88 position
python3 scripts/input_driver.py --display :88 move-human --x 640 --y 420
python3 scripts/input_driver.py --display :88 move-human --x 1500 --y 760 --duration 1.2 --amplitude 42 --waves 2.5
python3 scripts/input_driver.py --display :88 click-at --x 640 --y 420 --hover 0.15
python3 scripts/input_driver.py --display :88 drag-human --x 640 --y 400 --duration 0.30 --button left
python3 scripts/input_driver.py --display :88 drag-relative --dx 0 --dy -8 --duration 0.25 --button left
python3 scripts/input_driver.py --display :88 type --text 'hello world' --interval 0.025
python3 scripts/input_driver.py --display :88 key --keys 'CTRL+S'
```

The script relies on the local X11 and XTEST libraries and honors `XAUTHORITY` from the environment.

Use `scripts/desktop_context.sh` when `DISPLAY` or X11 authorization is uncertain. The bundled tools call it automatically; `input_driver.py` also retries by recovering the matching server process's existing `-auth` path. Treat the reported authority path as sensitive operational metadata and never print cookie bytes.

Use `scripts/capture_x11.sh` for a real X11 screenshot when the dedicated screenshot capability is unavailable. Prefer an installed screenshot skill when present because it adds stronger validation.

Use `scripts/record_x11.sh` to start or stop an evidence recording when no workspace-specific recorder already exists.

Use `scripts/window_probe.sh` to inspect current X11 window IDs, names, and geometry before coordinate-sensitive actions.

Use `scripts/preflight.sh` and `scripts/self_test.sh` for clean-extraction validation. Read `references/dependencies.md` for the runtime/skill boundary.

## Recovery and safety

- Never use broad `pkill`, `killall`, or process termination against the desktop, REAPER, X11, games, or unrelated processes.
- Do not repair X11 authorization with `xhost +`, `-ac`, or world-readable authority files.
- If the requested control surface is not reachable, report the blocked state instead of fabricating mouse movement or screenshots.
- Stop only recorder or helper processes created by the current workflow, using stored PIDs when available.
- If an input action worsens state, return to the last known-good checkpoint when one exists before continuing.

## Evidence contract

For substantial operations, return:

- what mouse and keyboard actions materially changed;
- what visible state was verified;
- the real screen recording covering the operation;
- the final genuine desktop screenshot;
- any limitation that prevented full verification.

Do not claim completion from configuration text alone when the task depends on the rendered GUI.
