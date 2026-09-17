# Runtime dependencies

The skill intentionally does not bundle operating-system binaries. A working X11 session must provide these runtime pieces:

- `python3`
- X11 client library (`libX11.so.6`)
- XTEST library (`libXtst.so.6`)
- `xdpyinfo` and `xwininfo`
- `ffmpeg` and `ffprobe` for evidence capture

Run `scripts/preflight.sh :88` before a fresh or recovered session. It reports missing binaries/libraries and whether the target display is reachable.

Do not treat a missing runtime dependency as a missing skill file. The skill package contains the control logic; the workspace or OS layer supplies X11 and multimedia binaries.

For authenticated displays, `scripts/desktop_context.sh` first tries the inherited environment and then inspects the matching local X server process for its existing `-auth` file. It never prints cookie bytes. `--shell` emits only `DISPLAY` and `XAUTHORITY` exports so bundled tools can inherit the verified session automatically.
