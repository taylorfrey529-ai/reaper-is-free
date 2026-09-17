#!/usr/bin/env python3
import argparse
import ctypes
import ctypes.util
import json
import math
import os
from pathlib import Path
import sys
import time

X11_NAME = ctypes.util.find_library('X11') or 'libX11.so.6'
XTST_NAME = ctypes.util.find_library('Xtst') or 'libXtst.so.6'
X11 = ctypes.CDLL(X11_NAME)
XTST = ctypes.CDLL(XTST_NAME)

Display_p = ctypes.c_void_p
Window = ctypes.c_ulong
Bool = ctypes.c_int
KeySym = ctypes.c_ulong
KeyCode = ctypes.c_ubyte

X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XOpenDisplay.restype = Display_p
X11.XCloseDisplay.argtypes = [Display_p]
X11.XCloseDisplay.restype = ctypes.c_int
X11.XDefaultRootWindow.argtypes = [Display_p]
X11.XDefaultRootWindow.restype = Window
X11.XFlush.argtypes = [Display_p]
X11.XFlush.restype = ctypes.c_int
X11.XStringToKeysym.argtypes = [ctypes.c_char_p]
X11.XStringToKeysym.restype = KeySym
X11.XKeysymToKeycode.argtypes = [Display_p, KeySym]
X11.XKeysymToKeycode.restype = KeyCode
X11.XQueryPointer.argtypes = [Display_p, Window, ctypes.POINTER(Window), ctypes.POINTER(Window), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint)]
X11.XQueryPointer.restype = Bool
XTST.XTestFakeMotionEvent.argtypes = [Display_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeMotionEvent.restype = ctypes.c_int
XTST.XTestFakeButtonEvent.argtypes = [Display_p, ctypes.c_uint, Bool, ctypes.c_ulong]
XTST.XTestFakeButtonEvent.restype = ctypes.c_int
XTST.XTestFakeKeyEvent.argtypes = [Display_p, ctypes.c_uint, Bool, ctypes.c_ulong]
XTST.XTestFakeKeyEvent.restype = ctypes.c_int

def recover_xauthority(display_name):
    """Recover the existing local X server -auth path without reading cookie bytes."""
    if not display_name:
        return None
    display = str(display_name)
    target = display.rsplit(':', 1)[-1].split('.', 1)[0]
    if not target.isdigit():
        return None
    server_names = {'Xvfb', 'Xorg', 'X', 'Xephyr'}
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            raw = (proc / 'cmdline').read_bytes()
        except OSError:
            continue
        argv = [x.decode(errors='surrogateescape') for x in raw.split(b'\0') if x]
        if not argv or os.path.basename(argv[0]) not in server_names:
            continue
        if f':{target}' not in argv:
            continue
        for i, value in enumerate(argv[:-1]):
            if value == '-auth':
                candidate = argv[i + 1]
                if os.path.isfile(candidate) and os.access(candidate, os.R_OK):
                    os.environ['XAUTHORITY'] = candidate
                    return candidate
    return None

BUTTONS = {'left': 1, 'middle': 2, 'right': 3}
MODIFIERS = {
    'CTRL': 'Control_L', 'CONTROL': 'Control_L', 'SHIFT': 'Shift_L',
    'ALT': 'Alt_L', 'OPTION': 'Alt_L', 'SUPER': 'Super_L', 'WIN': 'Super_L',
    'META': 'Meta_L'
}
SPECIAL_KEYS = {
    'ENTER': 'Return', 'RETURN': 'Return', 'ESC': 'Escape', 'ESCAPE': 'Escape',
    'TAB': 'Tab', 'SPACE': 'space', 'BACKSPACE': 'BackSpace', 'DELETE': 'Delete',
    'UP': 'Up', 'DOWN': 'Down', 'LEFT': 'Left', 'RIGHT': 'Right',
    'HOME': 'Home', 'END': 'End', 'PAGEUP': 'Page_Up', 'PAGEDOWN': 'Page_Down',
    'INSERT': 'Insert'
}
PLAIN_PUNCT = {
    '-': 'minus', '=': 'equal', '[': 'bracketleft', ']': 'bracketright', '\\': 'backslash',
    ';': 'semicolon', "'": 'apostrophe', ',': 'comma', '.': 'period', '/': 'slash', '`': 'grave'
}
SHIFTED = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8',
    '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']', '|': '\\', ':': ';',
    '"': "'", '<': ',', '>': '.', '?': '/'
}

class XInput:
    def __init__(self, display_name):
        if display_name:
            os.environ['DISPLAY'] = display_name
        if not os.environ.get('XAUTHORITY'):
            recover_xauthority(display_name or os.environ.get('DISPLAY'))
        name = display_name.encode() if display_name else None
        self.dpy = X11.XOpenDisplay(name)
        if not self.dpy:
            recover_xauthority(display_name or os.environ.get('DISPLAY'))
            self.dpy = X11.XOpenDisplay(name)
        if not self.dpy:
            raise RuntimeError(f'cannot open X11 display {display_name or os.environ.get("DISPLAY")!r}')
        self.root = X11.XDefaultRootWindow(self.dpy)

    def close(self):
        if self.dpy:
            X11.XCloseDisplay(self.dpy)
            self.dpy = None

    def flush(self):
        X11.XFlush(self.dpy)

    def position(self):
        root_ret = Window()
        child_ret = Window()
        root_x = ctypes.c_int()
        root_y = ctypes.c_int()
        win_x = ctypes.c_int()
        win_y = ctypes.c_int()
        mask = ctypes.c_uint()
        ok = X11.XQueryPointer(self.dpy, self.root, ctypes.byref(root_ret), ctypes.byref(child_ret), ctypes.byref(root_x), ctypes.byref(root_y), ctypes.byref(win_x), ctypes.byref(win_y), ctypes.byref(mask))
        if not ok:
            raise RuntimeError('XQueryPointer failed')
        return root_x.value, root_y.value

    def move(self, x, y, duration=0.25):
        sx, sy = self.position()
        duration = max(0.0, float(duration))
        if duration == 0:
            XTST.XTestFakeMotionEvent(self.dpy, -1, int(x), int(y), 0)
            self.flush()
            return
        steps = max(2, min(120, int(duration * 60)))
        for i in range(1, steps + 1):
            t = i / steps
            s = t * t * (3.0 - 2.0 * t)
            px = round(sx + (x - sx) * s)
            py = round(sy + (y - sy) * s)
            XTST.XTestFakeMotionEvent(self.dpy, -1, px, py, 0)
            self.flush()
            time.sleep(duration / steps)

    def move_human(self, x, y, duration=None, curve=None, waves=None):
        sx, sy = self.position()
        tx, ty = int(x), int(y)
        dx = tx - sx
        dy = ty - sy
        distance = math.hypot(dx, dy)
        if duration is None:
            duration = min(1.10, max(0.22, 0.18 + distance / 1800.0))
        duration = max(0.0, float(duration))
        if distance < 1 or duration == 0:
            return self.move(tx, ty, 0)

        amplitude = curve
        if amplitude is None:
            amplitude = min(36.0, max(6.0, distance * 0.035))
        amplitude = max(0.0, float(amplitude))
        if waves is None:
            waves = min(3.25, max(1.0, distance / 520.0))
        waves = max(0.25, float(waves))

        nx, ny = -dy / distance, dx / distance
        steps = max(18, min(220, int(duration * 120)))
        for i in range(1, steps + 1):
            t = i / steps
            u = t * t * (3.0 - 2.0 * t)
            envelope = math.sin(math.pi * u)
            lateral = amplitude * envelope * math.sin(2.0 * math.pi * waves * u)
            px = round(sx + dx * u + nx * lateral)
            py = round(sy + dy * u + ny * lateral)
            XTST.XTestFakeMotionEvent(self.dpy, -1, px, py, 0)
            self.flush()
            time.sleep(duration / steps)

        XTST.XTestFakeMotionEvent(self.dpy, -1, tx, ty, 0)
        self.flush()

    def click_at(self, x, y, button='left', duration=None, hover=0.12, curve=None, waves=None):
        self.move_human(x, y, duration, curve, waves)
        time.sleep(max(0.0, float(hover)))
        self.click(button, 1, 0.0)

    def drag_human_to(self, x, y, duration=None, button='left', curve=None, waves=None):
        self.button(button, True)
        time.sleep(0.07)
        self.move_human(x, y, duration, curve, waves)
        time.sleep(0.06)
        self.button(button, False)

    def button(self, button, down):
        code = BUTTONS.get(str(button).lower())
        if not code:
            raise ValueError(f'unsupported button: {button}')
        XTST.XTestFakeButtonEvent(self.dpy, code, 1 if down else 0, 0)
        self.flush()

    def click(self, button='left', count=1, interval=0.10):
        for i in range(count):
            self.button(button, True)
            time.sleep(0.035)
            self.button(button, False)
            if i + 1 < count:
                time.sleep(max(0.0, interval))

    def drag_to(self, x, y, duration=0.35, button='left'):
        self.button(button, True)
        time.sleep(0.06)
        self.move(x, y, duration)
        time.sleep(0.05)
        self.button(button, False)

    def scroll(self, steps):
        if steps == 0:
            return
        code = 4 if steps > 0 else 5
        for _ in range(abs(steps)):
            XTST.XTestFakeButtonEvent(self.dpy, code, 1, 0)
            XTST.XTestFakeButtonEvent(self.dpy, code, 0, 0)
            self.flush()
            time.sleep(0.045)

    def keycode(self, keysym_name):
        sym = X11.XStringToKeysym(keysym_name.encode())
        if sym == 0:
            raise ValueError(f'unknown keysym: {keysym_name}')
        code = int(X11.XKeysymToKeycode(self.dpy, sym))
        if code == 0:
            raise ValueError(f'no keycode for keysym: {keysym_name}')
        return code

    def key_event(self, keysym_name, down):
        code = self.keycode(keysym_name)
        XTST.XTestFakeKeyEvent(self.dpy, code, 1 if down else 0, 0)
        self.flush()

    def chord(self, chord):
        parts = [p.strip() for p in chord.split('+') if p.strip()]
        if not parts:
            raise ValueError('empty key chord')
        modifiers = []
        key_name = None
        for part in parts:
            upper = part.upper()
            if upper in MODIFIERS:
                modifiers.append(MODIFIERS[upper])
            else:
                if key_name is not None:
                    raise ValueError(f'multiple non-modifier keys in chord: {chord}')
                key_name = SPECIAL_KEYS.get(upper, part)
        if key_name is None:
            raise ValueError(f'chord has no non-modifier key: {chord}')
        for mod in modifiers:
            self.key_event(mod, True)
        self.key_event(key_name, True)
        time.sleep(0.035)
        self.key_event(key_name, False)
        for mod in reversed(modifiers):
            self.key_event(mod, False)

    def type_char(self, ch):
        shift = False
        if ch == '\n':
            name = 'Return'
        elif ch == '\t':
            name = 'Tab'
        elif ch == ' ':
            name = 'space'
        elif ch.isalpha() and ch.upper() == ch and ch.lower() != ch:
            shift = True
            name = ch.lower()
        elif ch in SHIFTED:
            shift = True
            name = SHIFTED[ch]
        else:
            name = PLAIN_PUNCT.get(ch, ch)
        name = PLAIN_PUNCT.get(name, name)
        if shift:
            self.key_event('Shift_L', True)
        self.key_event(name, True)
        self.key_event(name, False)
        if shift:
            self.key_event('Shift_L', False)

    def type_text(self, text, interval=0.025):
        for ch in text:
            self.type_char(ch)
            time.sleep(max(0.0, interval))


def build_parser():
    p = argparse.ArgumentParser(description='Deterministic X11 mouse and keyboard driver using XTEST')
    p.add_argument('--display', default=os.environ.get('DISPLAY'), help='X11 display, e.g. :88')
    sub = p.add_subparsers(dest='command', required=True)

    sub.add_parser('position')

    m = sub.add_parser('move')
    m.add_argument('--x', type=int, required=True)
    m.add_argument('--y', type=int, required=True)
    m.add_argument('--duration', type=float, default=0.25)

    mr = sub.add_parser('move-relative')
    mr.add_argument('--dx', type=int, required=True)
    mr.add_argument('--dy', type=int, required=True)
    mr.add_argument('--duration', type=float, default=0.20)

    mh = sub.add_parser('move-human')
    mh.add_argument('--x', type=int, required=True)
    mh.add_argument('--y', type=int, required=True)
    mh.add_argument('--duration', type=float)
    mh.add_argument('--curve', '--amplitude', dest='curve', type=float, help='sine-wave amplitude in pixels')
    mh.add_argument('--waves', type=float, help='number of sine cycles across the move')

    ca = sub.add_parser('click-at')
    ca.add_argument('--x', type=int, required=True)
    ca.add_argument('--y', type=int, required=True)
    ca.add_argument('--button', choices=BUTTONS, default='left')
    ca.add_argument('--duration', type=float)
    ca.add_argument('--hover', type=float, default=0.12)
    ca.add_argument('--curve', '--amplitude', dest='curve', type=float, help='sine-wave amplitude in pixels')
    ca.add_argument('--waves', type=float, help='number of sine cycles across the move')

    c = sub.add_parser('click')
    c.add_argument('--button', choices=BUTTONS, default='left')
    c.add_argument('--count', type=int, default=1)
    c.add_argument('--interval', type=float, default=0.10)

    d = sub.add_parser('drag')
    d.add_argument('--x', type=int, required=True)
    d.add_argument('--y', type=int, required=True)
    d.add_argument('--duration', type=float, default=0.35)
    d.add_argument('--button', choices=BUTTONS, default='left')

    dr = sub.add_parser('drag-relative')
    dr.add_argument('--dx', type=int, required=True)
    dr.add_argument('--dy', type=int, required=True)
    dr.add_argument('--duration', type=float, default=0.25)
    dr.add_argument('--button', choices=BUTTONS, default='left')

    dh = sub.add_parser('drag-human')
    dh.add_argument('--x', type=int, required=True)
    dh.add_argument('--y', type=int, required=True)
    dh.add_argument('--duration', type=float)
    dh.add_argument('--button', choices=BUTTONS, default='left')
    dh.add_argument('--curve', '--amplitude', dest='curve', type=float, help='sine-wave amplitude in pixels')
    dh.add_argument('--waves', type=float, help='number of sine cycles across the move')

    s = sub.add_parser('scroll')
    s.add_argument('--steps', type=int, required=True, help='positive=up, negative=down')

    t = sub.add_parser('type')
    t.add_argument('--text', required=True)
    t.add_argument('--interval', type=float, default=0.025)

    k = sub.add_parser('key')
    k.add_argument('--keys', required=True, help='Chord such as CTRL+S or ALT+F4')

    return p


def main():
    args = build_parser().parse_args()
    if not args.display:
        raise SystemExit('DISPLAY is not set; pass --display')
    xi = XInput(args.display)
    try:
        if args.command == 'position':
            x, y = xi.position()
            print(json.dumps({'x': x, 'y': y, 'display': args.display}, separators=(',', ':')))
        elif args.command == 'move':
            xi.move(args.x, args.y, args.duration)
        elif args.command == 'move-relative':
            x, y = xi.position()
            xi.move(x + args.dx, y + args.dy, args.duration)
        elif args.command == 'move-human':
            xi.move_human(args.x, args.y, args.duration, args.curve, args.waves)
        elif args.command == 'click-at':
            xi.click_at(args.x, args.y, args.button, args.duration, args.hover, args.curve, args.waves)
        elif args.command == 'click':
            xi.click(args.button, max(1, args.count), args.interval)
        elif args.command == 'drag':
            xi.drag_to(args.x, args.y, args.duration, args.button)
        elif args.command == 'drag-relative':
            x, y = xi.position()
            xi.drag_to(x + args.dx, y + args.dy, args.duration, args.button)
        elif args.command == 'drag-human':
            xi.drag_human_to(args.x, args.y, args.duration, args.button, args.curve, args.waves)
        elif args.command == 'scroll':
            xi.scroll(args.steps)
        elif args.command == 'type':
            xi.type_text(args.text, args.interval)
        elif args.command == 'key':
            xi.chord(args.keys)
    finally:
        xi.close()

if __name__ == '__main__':
    main()
