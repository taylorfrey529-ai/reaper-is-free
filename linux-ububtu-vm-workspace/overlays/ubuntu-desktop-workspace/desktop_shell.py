#!/usr/bin/env python3
"""Astra Workbench desktop shell for the authenticated :88 workspace.

The shell is intentionally ordinary Tk/Openbox UI: it keeps the desktop
reconstructable on Xvfb while giving the live workspace a deliberate studio
identity. Launchers remain local and offline; the wallpaper/depth builder is
the only generated visual asset.
"""

from __future__ import annotations

import os
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageFont, ImageTk

from desktop_depth import build_depth_scene


ROOT = Path("/mnt/data/ubuntu-desktop-workspace")
HOME = ROOT / "home"
DISPLAY = os.environ.get("DISPLAY", ":88")
W = int(os.environ.get("WORKSPACE_WIDTH", "2560"))
H = int(os.environ.get("WORKSPACE_HEIGHT", "1440"))
DEPTH = int(os.environ.get("WORKSPACE_DEPTH", "24"))
DEPTH_LAYERS = int(os.environ.get("DESKTOP_DEPTH_LAYERS", "24"))
DEPTH_STEP_PIXELS = int(os.environ.get("DESKTOP_DEPTH_STEP_PIXELS", "1"))

TOP = 40
DOCK_W = 96

# Astra palette: dark studio glass, with restrained cyan/magenta signal edges.
BG = "#070b14"
PANEL = "#0d121e"
DOCK = "#09101a"
GLASS = "#111a29"
GLASS_ALT = "#142238"
LINE = "#26364f"
CYAN = "#72efff"
PINK = "#ff6acb"
LIME = "#c5ff9a"
AMBER = "#ffb36b"
TEXT = "#f2f7ff"
MUTED = "#91a5bf"
DIM = "#61738e"

os.environ["HOME"] = str(HOME)
HOME.mkdir(parents=True, exist_ok=True)


def find_font(size: int, bold: bool = False, mono: bool = False):
    if mono:
        choices = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    else:
        choices = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    for candidate in choices:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def make_wallpaper(path: Path) -> None:
    """Render the custom Astra base plane at the active desktop size."""

    image = Image.new("RGB", (W, H), BG)
    pixels = image.load()
    for y in range(H):
        v = y / max(1, H - 1)
        for x in range(W):
            u = x / max(1, W - 1)

            # Near-black navy foundation with a subtle right-side lift.
            red = 6 + int(10 * u + 5 * (1.0 - v))
            green = 10 + int(13 * u + 6 * (1.0 - v))
            blue = 19 + int(27 * u + 12 * (1.0 - v))

            # Magenta signal bloom, upper-right.
            dx = (x - W * 0.82) / (W * 0.52)
            dy = (y - H * 0.22) / (H * 0.50)
            magenta = max(0.0, 1.0 - (dx * dx + dy * dy))
            red += int(78 * magenta)
            green += int(5 * magenta)
            blue += int(52 * magenta)

            # Cyan counter-bloom, lower-left, kept dim so text remains clear.
            dx = (x - W * 0.18) / (W * 0.62)
            dy = (y - H * 0.82) / (H * 0.58)
            cyan = max(0.0, 1.0 - (dx * dx + dy * dy))
            red += int(4 * cyan)
            green += int(24 * cyan)
            blue += int(38 * cyan)

            pixels[x, y] = (
                min(255, red),
                min(255, green),
                min(255, blue),
            )

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)

    # Sparse perspective grid: a stage, not a wallpaper pattern.
    for y in range(int(H * 0.62), H, 72):
        alpha = 18 if y < H * 0.82 else 12
        draw.line([(DOCK_W + 20, y), (W - 70, y - 12)], fill=(93, 172, 220, alpha), width=1)
    for x in range(DOCK_W + 40, W, 180):
        draw.line([(x, H), (W * 0.62 + (x - W * 0.62) * 0.12, H * 0.60)], fill=(74, 135, 190, 12), width=1)

    # Two long neon diagonals establish the desktop's depth direction.
    draw.line(
        [(DOCK_W + 108, H - 150), (W - 180, TOP + 142)],
        fill=(255, 78, 196, 34),
        width=2,
    )
    draw.line(
        [(DOCK_W + 180, TOP + 152), (W - 290, H - 190)],
        fill=(89, 239, 255, 24),
        width=2,
    )

    # Thin framing arcs/rails behind the glass cards.
    for inset, alpha in ((0, 28), (18, 17), (36, 10)):
        draw.rounded_rectangle(
            [DOCK_W + 112 + inset, TOP + 82 + inset, W - 116 - inset, H - 88 - inset],
            radius=24,
            outline=(149, 92, 206, alpha),
            width=1,
        )

    image = Image.alpha_composite(image.convert("RGBA"), glow)
    d = ImageDraw.Draw(image)
    title_font = find_font(42, True)
    sub_font = find_font(17, False)
    mono_font = find_font(13, True, mono=True)
    d.text((DOCK_W + 116, H - 148), "ASTRA WORKBENCH", font=title_font, fill=(242, 247, 255, 228))
    d.text((DOCK_W + 120, H - 96), "LOCAL PRODUCTION DESKTOP  /  SIGNAL OVER NOISE", font=sub_font, fill=(145, 165, 191, 220))
    d.text((W - 438, H - 84), "DISPLAY :88   CANVAS 2560×1440×24", font=mono_font, fill=(197, 255, 154, 166))
    image.convert("RGB").save(path, format="PNG", optimize=True)


WALLPAPER = ROOT / "assets" / "wallpaper.png"
make_wallpaper(WALLPAPER)
DESKTOP_SCENE = build_depth_scene(
    WALLPAPER,
    ROOT / "assets",
    W,
    H,
    depth_layers=DEPTH_LAYERS,
    step_pixels=DEPTH_STEP_PIXELS,
)

root = tk.Tk()
root.title("Astra Workbench Desktop")
root.geometry(f"{W}x{H}+0+0")
root.overrideredirect(True)
root.configure(bg=BG)
root.lower()

wall_img = ImageTk.PhotoImage(Image.open(DESKTOP_SCENE).convert("RGBA"))
background = tk.Label(root, image=wall_img, bd=0, highlightthickness=0)
background.place(x=0, y=0, width=W, height=H)


def launch(command, **kwargs):
    environment = os.environ.copy()
    environment["DISPLAY"] = DISPLAY
    environment["HOME"] = str(HOME)
    try:
        subprocess.Popen(command, env=environment, start_new_session=True, **kwargs)
    except Exception as error:
        messagebox.showerror("Launch failed", str(error))


def terminal():
    launch(
        [
            "xterm",
            "-title",
            "Astra Terminal",
            "-geometry",
            "104x30+220+150",
            "-fa",
            "DejaVu Sans Mono",
            "-fs",
            "11",
            "-bg",
            "#080d17",
            "-fg",
            "#eaf6ff",
            "-e",
            "bash",
            "-lc",
            "printf '\\033[1;38;5;81mASTRA WORKBENCH\\033[0m\\n'; printf 'Authenticated local session • DISPLAY=%s\\n\\n' \"$DISPLAY\"; cd /mnt/data; exec bash",
        ]
    )


def browser():
    local = ROOT / "home.html"
    launch(
        [
            "chromium",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            f"--user-data-dir={ROOT / 'profile'}",
            "--new-window",
            local.as_uri(),
        ]
    )


def graphics():
    command = (
        "source /mnt/data/graphics-workspace/graphics-env.sh; "
        "export DISPLAY='%s'; "
        "echo 'Starting Vulkan graphics test on Astra display...'; vkcube" % DISPLAY
    )
    launch(
        [
            "xterm",
            "-title",
            "Astra Graphics",
            "-geometry",
            "88x18+340+220",
            "-bg",
            "#080d17",
            "-fg",
            "#eaf6ff",
            "-e",
            "bash",
            "-lc",
            command,
        ]
    )


def reaper():
    launch([str(ROOT / "bin" / "launch-reaper.sh")])


def system_info():
    window = tk.Toplevel(root)
    window.title("Astra Workbench — Session")
    window.geometry("760x560+390+170")
    window.configure(bg=BG)
    window.resizable(False, False)

    tk.Label(
        window,
        text="ASTRA WORKBENCH",
        font=("DejaVu Sans", 24, "bold"),
        bg=BG,
        fg=TEXT,
        anchor="w",
    ).pack(fill="x", padx=34, pady=(28, 4))
    tk.Label(
        window,
        text="Session contract / authenticated local desktop",
        font=("DejaVu Sans", 11),
        bg=BG,
        fg=MUTED,
        anchor="w",
    ).pack(fill="x", padx=36, pady=(0, 22))

    box = tk.Frame(window, bg=GLASS, highlightbackground=LINE, highlightthickness=1)
    box.pack(fill="x", padx=30)
    rows = [
        ("Display", f"{DISPLAY}  /  {W}×{H}×{DEPTH}"),
        ("Depth stack", f"{DEPTH_LAYERS} transparent RGBA planes  /  {DEPTH_STEP_PIXELS}px steps"),
        ("Window manager", "Openbox"),
        ("REAPER", "7.79 native Linux x86_64"),
        ("Project", "ASIO-Routing-Project"),
        ("Audio", "48 kHz  /  Apollo S/PDIF  /  256×3 stereo"),
        ("Graphics", "Vulkan llvmpipe / Mesa workspace"),
        ("Network", "Offline in current container"),
    ]
    for index, (key, value) in enumerate(rows):
        row = tk.Frame(box, bg=GLASS)
        row.pack(fill="x", padx=18, pady=(14 if index == 0 else 7, 7))
        tk.Label(row, text=key.upper(), width=17, anchor="w", bg=GLASS, fg=CYAN, font=("DejaVu Sans", 9, "bold")).pack(side="left")
        tk.Label(row, text=value, anchor="w", bg=GLASS, fg=TEXT, font=("DejaVu Sans", 10)).pack(side="left", fill="x", expand=True)

    tk.Button(
        window,
        text="CLOSE",
        command=window.destroy,
        bg=GLASS_ALT,
        fg=TEXT,
        activebackground=CYAN,
        activeforeground=BG,
        relief="flat",
        bd=0,
        padx=22,
        pady=8,
        font=("DejaVu Sans", 10, "bold"),
    ).pack(anchor="e", padx=30, pady=24)


def file_browser(path: Path = Path("/mnt/data")):
    window = tk.Toplevel(root)
    window.title("Astra Workbench — Files")
    window.geometry("880x620+290+130")
    window.configure(bg=BG)

    current = tk.StringVar(value=str(path))
    top = tk.Frame(window, bg=GLASS, highlightbackground=LINE, highlightthickness=1)
    top.pack(fill="x", padx=18, pady=18)
    tk.Label(top, text="FILES", bg=GLASS, fg=CYAN, font=("DejaVu Sans", 10, "bold"), padx=14, pady=8).pack(side="left")
    tk.Label(top, textvariable=current, bg=GLASS, fg=TEXT, font=("DejaVu Sans Mono", 10), anchor="w", padx=10).pack(side="left", fill="x", expand=True)

    body = tk.Frame(window, bg=GLASS, highlightbackground=LINE, highlightthickness=1)
    body.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    listbox = tk.Listbox(
        body,
        font=("DejaVu Sans Mono", 11),
        bg="#0c1421",
        fg=TEXT,
        bd=0,
        highlightthickness=0,
        selectbackground="#284964",
        selectforeground=CYAN,
        activestyle="none",
    )
    listbox.pack(side="left", fill="both", expand=True, padx=14, pady=14)
    scrollbar = tk.Scrollbar(body, command=listbox.yview, troughcolor=GLASS, bg=LINE, activebackground=CYAN)
    scrollbar.pack(side="right", fill="y", pady=14)
    listbox.config(yscrollcommand=scrollbar.set)
    entries = []

    def load(folder):
        nonlocal entries
        folder = Path(folder)
        if not folder.exists() or not folder.is_dir():
            return
        current.set(str(folder))
        listbox.delete(0, "end")
        entries = []
        if folder != Path("/"):
            entries.append(("..", folder.parent, True))
            listbox.insert("end", "[DIR]  ..")
        try:
            children = sorted(folder.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        except OSError:
            children = []
        for child in children:
            try:
                is_directory = child.is_dir()
            except OSError:
                is_directory = False
            entries.append((child.name, child, is_directory))
            listbox.insert("end", ("[DIR]  " if is_directory else "        ") + child.name)

    def open_selected(_event=None):
        selection = listbox.curselection()
        if not selection:
            return
        _, selected_path, is_directory = entries[selection[0]]
        if is_directory:
            load(selected_path)
        elif selected_path.suffix.lower() in (".html", ".htm", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".txt", ".md"):
            browser_path = selected_path.as_uri()
            launch(["chromium", "--no-sandbox", "--disable-gpu", "--new-window", browser_path])
        else:
            launch(
                [
                    "xterm",
                    "-title",
                    selected_path.name,
                    "-e",
                    "bash",
                    "-lc",
                    f"cd {str(selected_path.parent)!r}; ls -lh {selected_path.name!r}; echo; file {selected_path.name!r}; exec bash",
                ]
            )

    listbox.bind("<Double-Button-1>", open_selected)
    load(path)


def shutdown():
    if messagebox.askyesno("End session", "End the Astra Workbench desktop session?"):
        root.destroy()


def make_button(parent, label, command, accent=CYAN, width=18):
    button = tk.Button(
        parent,
        text=label,
        command=command,
        width=width,
        bg=GLASS_ALT,
        fg=TEXT,
        activebackground=accent,
        activeforeground=BG,
        relief="flat",
        bd=0,
        highlightbackground=LINE,
        highlightcolor=accent,
        highlightthickness=1,
        padx=12,
        pady=9,
        font=("DejaVu Sans", 10, "bold"),
        cursor="hand2",
    )
    button.bind("<Enter>", lambda _event: button.configure(bg="#1d3852", fg=accent))
    button.bind("<Leave>", lambda _event: button.configure(bg=GLASS_ALT, fg=TEXT))
    return button


def dock_button(parent, label, glyph, command, accent=CYAN):
    button = tk.Button(
        parent,
        text=f"{glyph}\n{label}",
        command=command,
        bg=DOCK,
        fg=TEXT,
        activebackground=GLASS_ALT,
        activeforeground=accent,
        relief="flat",
        bd=0,
        highlightthickness=0,
        font=("DejaVu Sans", 8, "bold"),
        height=3,
        width=9,
        cursor="hand2",
    )
    button.pack(pady=4, padx=6)
    button.bind("<Enter>", lambda _event: button.configure(bg=GLASS_ALT, fg=accent))
    button.bind("<Leave>", lambda _event: button.configure(bg=DOCK, fg=TEXT))
    return button


def card(parent, x, y, width, height, title, accent=CYAN):
    frame = tk.Frame(parent, bg=GLASS, highlightbackground=LINE, highlightthickness=1)
    frame.place(x=x, y=y, width=width, height=height)
    tk.Frame(frame, bg=accent, height=2).pack(fill="x", side="top")
    tk.Label(frame, text=title, bg=GLASS, fg=accent, anchor="w", font=("DejaVu Sans", 10, "bold")).pack(fill="x", padx=24, pady=(18, 2))
    return frame


# Main hero card.
content_x = DOCK_W + 86
right_x = W - 558
hero = card(root, content_x, TOP + 86, 880, 374, "EVERMORE  /  ASTRA WORKBENCH", PINK)
tk.Label(hero, text="MAKE SPACE FOR\nTHE SIGNAL", bg=GLASS, fg=TEXT, justify="left", anchor="w", font=("DejaVu Sans", 38, "bold")).pack(fill="x", padx=24, pady=(20, 3))
tk.Label(hero, text="A precision desktop for sound, graphics, and local tools.", bg=GLASS, fg=MUTED, anchor="w", font=("DejaVu Sans", 13)).pack(fill="x", padx=26, pady=(0, 22))
quick = tk.Frame(hero, bg=GLASS)
quick.pack(fill="x", padx=22)
make_button(quick, "OPEN REAPER", reaper, CYAN, 16).pack(side="left", padx=4)
make_button(quick, "OPEN TERMINAL", terminal, PINK, 16).pack(side="left", padx=4)
make_button(quick, "BROWSE FILES", lambda: file_browser(Path("/mnt/data")), AMBER, 16).pack(side="left", padx=4)
tk.Label(hero, text="LOCAL / OFFLINE / RECONSTRUCTABLE", bg=GLASS, fg=DIM, anchor="w", font=("DejaVu Sans Mono", 9, "bold")).pack(fill="x", padx=26, pady=(28, 0))

# Live session telemetry.
telemetry = card(root, right_x, TOP + 86, 458, 374, "SESSION TELEMETRY", CYAN)
tk.Label(telemetry, text="READY  /  DISPLAY AUTHENTICATED", bg=GLASS, fg=LIME, anchor="w", font=("DejaVu Sans Mono", 10, "bold")).pack(fill="x", padx=24, pady=(16, 18))


def telemetry_row(parent, key, value, color=TEXT):
    row = tk.Frame(parent, bg=GLASS)
    row.pack(fill="x", padx=24, pady=6)
    tk.Label(row, text=key, bg=GLASS, fg=DIM, anchor="w", font=("DejaVu Sans Mono", 9, "bold")).pack(side="left")
    tk.Label(row, text=value, bg=GLASS, fg=color, anchor="e", font=("DejaVu Sans Mono", 10, "bold")).pack(side="right")


telemetry_row(telemetry, "X11 DISPLAY", ":88", CYAN)
telemetry_row(telemetry, "CANVAS", f"{W}×{H}×{DEPTH}", TEXT)
telemetry_row(telemetry, "DEPTH PLANES", f"{DEPTH_LAYERS}  /  {DEPTH_STEP_PIXELS}px", PINK)
telemetry_row(telemetry, "AUDIO CLOCK", "48 kHz", LIME)
telemetry_row(telemetry, "ROUTE", "APOLLO S/PDIF", AMBER)
make_button(telemetry, "SESSION DETAILS", system_info, CYAN, 20).pack(anchor="w", padx=24, pady=(22, 0))

# Production card.
production = card(root, content_x, TOP + 496, 880, 286, "REAPER PRODUCTION DESK", AMBER)
tk.Label(production, text="ASIO-ROUTING-PROJECT", bg=GLASS, fg=TEXT, anchor="w", font=("DejaVu Sans", 20, "bold")).pack(fill="x", padx=24, pady=(18, 2))
tk.Label(production, text="REAPER 7.79  /  native Linux x86_64  /  256×3 stereo", bg=GLASS, fg=MUTED, anchor="w", font=("DejaVu Sans Mono", 10)).pack(fill="x", padx=26, pady=(0, 22))
production_actions = tk.Frame(production, bg=GLASS)
production_actions.pack(fill="x", padx=22)
make_button(production_actions, "OPEN PROJECT", reaper, AMBER, 17).pack(side="left", padx=4)
make_button(production_actions, "AUDIO TERMINAL", terminal, CYAN, 17).pack(side="left", padx=4)
tk.Label(production, text="SIGNAL PATH  /  INPUT → MIX → APOLLO S/PDIF", bg=GLASS, fg=DIM, anchor="w", font=("DejaVu Sans Mono", 9, "bold")).pack(fill="x", padx=26, pady=(26, 0))

# Workspace modules card.
modules = card(root, right_x, TOP + 496, 458, 286, "WORKSPACE MODULES", PINK)
module_rows = [
    ("FILES", "workspace browser", lambda: file_browser(Path("/mnt/data")), CYAN),
    ("WEB", "local start page", browser, PINK),
    ("VULKAN", "graphics test", graphics, AMBER),
    ("SETTINGS", "session contract", system_info, LIME),
]
for label, description, command, accent in module_rows:
    row = tk.Frame(modules, bg=GLASS)
    row.pack(fill="x", padx=22, pady=4)
    make_button(row, label, command, accent, 10).pack(side="left")
    tk.Label(row, text=description, bg=GLASS, fg=MUTED, anchor="w", font=("DejaVu Sans", 10)).pack(side="left", padx=14)

tk.Label(root, text="ASTRA / LOCAL WORKSPACE", bg=BG, fg=DIM, font=("DejaVu Sans Mono", 9, "bold")).place(x=content_x, y=H - 54)

# Top panel.
panel = tk.Toplevel(root)
panel.overrideredirect(True)
panel.geometry(f"{W}x{TOP}+0+0")
panel.configure(bg=PANEL)
panel.attributes("-topmost", True)
tk.Frame(panel, bg=CYAN, width=3).pack(side="left", fill="y")
tk.Label(panel, text="A", bg=PANEL, fg=CYAN, font=("DejaVu Sans", 15, "bold"), padx=12).pack(side="left", fill="y")
tk.Label(panel, text="ASTRA WORKBENCH", bg=PANEL, fg=TEXT, font=("DejaVu Sans", 10, "bold")).pack(side="left", padx=(0, 22))
tk.Label(panel, text="LOCAL PRODUCTION DESKTOP", bg=PANEL, fg=MUTED, font=("DejaVu Sans", 9)).pack(side="left")
clock = tk.Label(panel, text="", bg=PANEL, fg=TEXT, font=("DejaVu Sans Mono", 9, "bold"))
clock.pack(side="right", padx=20)
tk.Label(panel, text="●  LIVE :88", bg=PANEL, fg=LIME, font=("DejaVu Sans Mono", 9, "bold")).pack(side="right", padx=8)
tk.Label(panel, text="2560×1440×24", bg=PANEL, fg=CYAN, font=("DejaVu Sans Mono", 9, "bold")).pack(side="right", padx=8)


def tick():
    clock.config(text=time.strftime("%a %b %d   %H:%M"))
    root.after(1000, tick)


tick()

# Left dock.
dock = tk.Toplevel(root)
dock.overrideredirect(True)
dock.geometry(f"{DOCK_W}x{H - TOP}+0+{TOP}")
dock.configure(bg=DOCK)
dock.attributes("-topmost", True)
tk.Frame(dock, bg=PINK, width=2).place(x=DOCK_W - 2, y=0, relheight=1)
logo = tk.Frame(dock, bg=DOCK)
logo.pack(fill="x", pady=(18, 8))
tk.Label(logo, text="A", bg=DOCK, fg=PINK, font=("DejaVu Sans", 26, "bold")).pack()
tk.Label(logo, text="CORE", bg=DOCK, fg=DIM, font=("DejaVu Sans Mono", 7, "bold")).pack()
dock_button(dock, "Files", "[]", lambda: file_browser(Path("/mnt/data")), CYAN)
dock_button(dock, "REAPER", "R", reaper, AMBER)
dock_button(dock, "Terminal", ">_", terminal, CYAN)
dock_button(dock, "Web", "◎", browser, PINK)
dock_button(dock, "Vulkan", "◇", graphics, AMBER)
dock_button(dock, "Settings", "?", system_info, LIME)
tk.Frame(dock, bg=DOCK).pack(fill="both", expand=True)
dock_button(dock, "Power", "x", shutdown, PINK)

# Local start page for the browser launcher.
home_html = ROOT / "home.html"
home_html.write_text(
    """<!doctype html>
<meta charset="utf-8">
<title>Astra Workbench</title>
<style>
  :root{color-scheme:dark;font-family:Inter,Ubuntu,Arial,sans-serif}
  body{margin:0;background:radial-gradient(circle at 82% 18%,#3b1644 0,#111727 40%,#070b14 100%);color:#f2f7ff;min-height:100vh}
  main{max-width:980px;margin:0 auto;padding:15vh 48px}
  .eyebrow{color:#72efff;letter-spacing:.18em;font:700 13px monospace}
  h1{font-size:64px;line-height:1.02;margin:20px 0 14px;letter-spacing:-.04em}
  h1 span{color:#ff6acb}
  p{color:#91a5bf;font-size:18px}
  .card{margin-top:48px;padding:30px;border:1px solid #26364f;background:#111a29cc;box-shadow:0 20px 60px #0008}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:28px}
  .item{padding:18px;background:#142238;color:#dbeaff;border-left:2px solid #72efff}
  code{color:#c5ff9a}
</style>
<main>
  <div class="eyebrow">EVERMORE / ASTRA WORKBENCH</div>
  <h1>Make space for<br><span>the signal.</span></h1>
  <p>Local production desktop · authenticated X11 :88 · 2560×1440×24</p>
  <div class="card">
    <strong>Workspace online.</strong>
    <div class="grid">
      <div class="item">REAPER 7.79<br><small>ASIO-Routing-Project</small></div>
      <div class="item">AUDIO CLOCK<br><small>48 kHz / Apollo S/PDIF</small></div>
      <div class="item">DEPTH STACK<br><small>24 transparent RGBA planes</small></div>
      <div class="item">ROOT<br><small><code>/mnt/data</code></small></div>
    </div>
  </div>
</main>
""",
    encoding="utf-8",
)


def apply_hints():
    try:
        subprocess.run(
            ["wmctrl", "-r", "Astra Workbench Desktop", "-b", "add,below,sticky"],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


root.after(900, apply_hints)
root.mainloop()
