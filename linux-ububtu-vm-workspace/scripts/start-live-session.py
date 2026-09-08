#!/usr/bin/env python3
"""Boot and verify the recovered linux-ububtu-vm-workspace live session.

This launcher intentionally preserves REAPER's real license/evaluation UI. It
never clicks, suppresses, patches, or bypasses an activation/evaluation prompt.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

CHECKOUT = pathlib.Path(__file__).resolve().parents[1]
WS = pathlib.Path(os.environ.get("REAPER_WORKSPACE_ROOT", "/mnt/data/ubuntu-desktop-workspace"))
APOLLO = pathlib.Path(os.environ.get("VIRTUAL_APOLLO_ROOT", "/mnt/data/virtual-apollo"))
PROJECT = pathlib.Path(
    os.environ.get(
        "REAPER_PROJECT",
        str(WS / "projects/ASIO-Routing-Project/ASIO-Routing-Project.RPP"),
    )
)
DISPLAY = os.environ.get("REAPER_DISPLAY", ":88")
LOG = WS / "logs/reaper-live-session.log"
PIDFILE = WS / "run/reaper.pid"


def run(cmd, *, env=None, check=True, capture=False):
    kwargs = {"text": True, "env": env}
    if capture:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = subprocess.run(cmd, **kwargs)
    if check and p.returncode != 0:
        if capture and p.stdout:
            sys.stderr.write(p.stdout)
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return p


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def require(path: pathlib.Path):
    if not path.exists():
        raise SystemExit(f"MISSING: {path}")


def reaper_config_guard() -> None:
    ini = WS / "config/REAPER/reaper.ini"
    require(ini)
    text = ini.read_text(errors="replace")
    locks = {
        "linux_audio_mode=1": "ALSA backend lock",
        "alsa_indev=apollo_spdif": "Virtual Apollo input lock",
        "alsa_outdev=apollo_spdif": "Virtual Apollo output lock",
        "linux_audio_srate=48000": "48 kHz sample-rate lock",
        "linux_audio_bsize=256": "256-sample buffer lock",
        "linux_audio_bufs=3": "3-buffer lock",
        "linux_audio_nch_in=2": "stereo input lock",
        "linux_audio_nch_out=2": "stereo output lock",
    }
    missing = [f"{value} ({label})" for value, label in locks.items() if value not in text]
    if missing:
        raise SystemExit("REAPER continuity lock failure:\n  " + "\n  ".join(missing))


for path in (
    WS / "start-desktop.sh",
    WS / "bin/launch-reaper.sh",
    WS / "apps/REAPER/reaper",
    APOLLO / "bin/start-apollo.sh",
    PROJECT,
):
    require(path)
reaper_config_guard()

run([str(WS / "start-desktop.sh")])
run([str(APOLLO / "bin/start-apollo.sh")])

env = os.environ.copy()
env.update(
    {
        "DISPLAY": DISPLAY,
        "HOME": str(WS / "home"),
        "XDG_CONFIG_HOME": str(WS / "config"),
    }
)
run(["xdpyinfo", "-display", DISPLAY], env=env, capture=True)

reaper_pid = None
if PIDFILE.exists():
    try:
        candidate = int(PIDFILE.read_text().strip())
        if pid_alive(candidate):
            reaper_pid = candidate
    except Exception:
        pass

if reaper_pid is None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    PIDFILE.parent.mkdir(parents=True, exist_ok=True)
    logf = open(LOG, "ab", buffering=0)
    proc = subprocess.Popen(
        [str(WS / "bin/launch-reaper.sh"), str(PROJECT)],
        env=env,
        stdout=logf,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    reaper_pid = proc.pid
    PIDFILE.write_text(f"{reaper_pid}\n")

# Keep scanning briefly after the first REAPER window appears. A prior launcher
# stopped immediately at that point and raced the evaluation/license UI, which
# produced a false activation_window_detected=false result.
window_tree = ""
seen_reaper = False
seen_activation = False
first_reaper_at = None
deadline = time.monotonic() + 12.0
post_reaper_scan = 4.0
while time.monotonic() < deadline:
    p = run(
        ["xwininfo", "-display", DISPLAY, "-root", "-tree"],
        env=env,
        check=False,
        capture=True,
    )
    window_tree = p.stdout or ""
    low = window_tree.lower()
    if "reaper" in low:
        seen_reaper = True
        if first_reaper_at is None:
            first_reaper_at = time.monotonic()
    if any(token in low for token in ("evaluation", "license", "purchase", "activation")):
        seen_activation = True
    if not pid_alive(reaper_pid):
        break
    if seen_reaper and seen_activation:
        break
    if first_reaper_at is not None and time.monotonic() - first_reaper_at >= post_reaper_scan:
        break
    time.sleep(0.1)

license_state = "evaluation" if seen_activation else "licensed-or-not-detected"
print(f"checkout={CHECKOUT}")
print(f"display={DISPLAY}")
print("desktop=live")
print("apollo=configured")
print(f"project={PROJECT}")
print(f"reaper_pid={reaper_pid}")
print(f"reaper_alive={str(pid_alive(reaper_pid)).lower()}")
print(f"reaper_window={str(seen_reaper).lower()}")
print(f"activation_window_detected={str(seen_activation).lower()}")
print(f"license_state={license_state}")
print(f"log={LOG}")

for line in window_tree.splitlines():
    low = line.lower()
    if any(
        key in low
        for key in (
            "reaper",
            "evaluation",
            "license",
            "purchase",
            "activation",
            "ubuntu workspace desktop",
        )
    ):
        print(f"window: {line.strip()}")

if not pid_alive(reaper_pid):
    if LOG.exists():
        sys.stderr.write(LOG.read_text(errors="replace")[-8000:])
    raise SystemExit(4)
if not seen_reaper:
    raise SystemExit(5)
