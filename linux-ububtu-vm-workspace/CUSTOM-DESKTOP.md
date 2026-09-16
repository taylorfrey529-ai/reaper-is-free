# Astra Workbench custom desktop

This feature branch is the visual layer for the authenticated Linux/Ubuntu workspace on X11 `:88`.

## Design

- dark navy/black studio glass
- crisp cyan and magenta signal edges with restrained amber/lime status accents
- sparse perspective rails that reinforce the existing 24-plane depth treatment
- minimal launch rail plus four large work surfaces instead of a crowded dashboard
- REAPER and Apollo routing presented as the primary production context

## Runtime contract

- Display: `:88`
- Canvas: `2560x1440x24`
- Depth: wallpaper layer 01 at alpha `198/255`, followed by 23 transparent RGBA planes at one-pixel steps
- Audio context: REAPER 7.79, ASIO-Routing-Project, 48 kHz, Apollo S/PDIF, 256x3 stereo
- Window title: `Astra Workbench Desktop`

## Restore behavior

`restore.sh` verifies the historical source snapshot and tar stream first. It then copies this overlay into the reconstructed workspace, including the shell, depth renderer, launcher/verifier, Openbox rule, and handoff text. The historical source and rejected-payload hashes are not rewritten.

## Verification

The live desktop was restarted on the authenticated `:88` session and verified at `2560x1440` with 24 root-window planes. The regression script compiles the shell/depth code, validates the overlay after restore, and checks the custom title/depth version markers.
