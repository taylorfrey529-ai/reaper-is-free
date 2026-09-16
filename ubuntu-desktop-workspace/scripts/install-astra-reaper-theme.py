#!/usr/bin/env python3
"""Build the Astra REAPER theme from the supplied Default 7 theme.

The REAPER binary remains an external runtime. This small deterministic
installer keeps the theme reproducible without committing that runtime or a
large generated theme archive to the workspace repository.
"""

from __future__ import annotations

import os
import re
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path("/mnt/data/ubuntu-desktop-workspace")
DEFAULT_THEME = ROOT / "apps" / "REAPER" / "InstallData" / "ColorThemes" / "Default_7.0.ReaperThemeZip"
OUTPUT_THEME = ROOT / "config" / "REAPER" / "ColorThemes" / "Astra_Workbench.ReaperThemeZip"
CONTROL_ATLAS = ROOT / "assets" / "astra-control-atlas.png"

COLOR_OVERRIDES = {
    "col_main_bg2": "1313543",
    "col_main_text2": "12559761",
    "col_main_textshadow": "853764",
    "col_main_3dhl": "5191206",
    "col_main_3dsh": "853764",
    "col_main_resize2": "16772978",
    "col_main_text": "16775154",
    "col_main_bg": "2693649",
    "col_main_editbk": "2167820",
    "col_transport_editbk": "2693649",
    "col_toolbar_text": "16775154",
    "col_toolbar_text_on": "16772978",
    "col_toolbar_frame": "5191206",
    "toolbararmed_color": "13331199",
    "col_tcp_text": "16775154",
    "col_tcp_textsel": "16772978",
    "col_seltrack": "6572328",
    "col_seltrack2": "6572328",
    "col_tracklistbg": "2167820",
    "col_mixerbg": "2693649",
    "col_arrangebg": "1313543",
    "arrange_vgrid": "3810327",
    "col_tl_fg": "16775154",
    "col_tl_fg2": "12559761",
    "col_tl_bg": "2693649",
    "col_tl_bgsel": "6572328",
    "col_tl_bgsel2": "5191206",
    "col_trans_bg": "1970701",
    "col_trans_fg": "16775154",
    "col_mi_label": "16775154",
    "col_mi_label_sel": "16775154",
    "col_mi_label_float": "16775154",
    "col_mi_label_float_sel": "16775154",
    "col_mi_bg": "3678740",
    "col_mi_bg2": "3810327",
    "col_tr1_itembgsel": "6572328",
    "col_tr2_itembgsel": "6572328",
    "col_tr1_peaks": "16772978",
    "col_tr2_peaks": "13331199",
    "col_peaksedge": "16772978",
    "col_peaksedge2": "13331199",
    "col_peaksedgesel": "16775154",
    "col_peaksedgesel2": "16775154",
    "col_tr1_bg": "2693649",
    "col_tr2_bg": "2167820",
    "selcol_tr1_bg": "6572328",
    "selcol_tr2_bg": "5191206",
    "col_tr1_divline": "5191206",
    "col_tr2_divline": "5191206",
    "col_cursor": "13331199",
    "col_cursor2": "16772978",
    "col_gridlines2": "5191206",
    "col_gridlines3": "5191206",
    "col_gridlines": "5191206",
    "col_vutop": "13331199",
    "col_vumid": "7058431",
    "col_vubot": "10158021",
    "col_vuintcol": "16772978",
    "col_vumidi": "13331199",
    "col_vuind1": "16772978",
    "col_vuind2": "13331199",
    "col_vuind3": "7058431",
    "col_vuind4": "16772978",
}


def _png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _scaled_point(value: float, scale: float) -> int:
    return max(1, int(round(value * scale)))


def _fader_grip(width: int, height: int) -> Image.Image:
    """A compact Astra glass fader grip with cyan edge and magenta index."""
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = width / 24.0
    inset = _scaled_point(1.2, scale)
    radius = _scaled_point(5.5, scale)
    draw.rounded_rectangle(
        [inset + 1, inset + 2, width - inset + 1, height - inset + 2],
        radius=radius,
        fill=(0, 0, 0, 110),
    )
    draw.rounded_rectangle(
        [inset, inset, width - inset - 1, height - inset - 1],
        radius=radius,
        fill=(13, 18, 30, 242),
        outline=(114, 239, 255, 235),
        width=max(1, _scaled_point(1.0, scale)),
    )
    hi = _scaled_point(2.5, scale)
    draw.line(
        [(inset + hi, inset + hi), (width - inset - hi, inset + hi)],
        fill=(242, 247, 255, 105),
        width=max(1, _scaled_point(0.7, scale)),
    )
    marker_y = int(height * 0.52)
    draw.rounded_rectangle(
        [inset + _scaled_point(3, scale), marker_y - _scaled_point(2, scale),
         width - inset - _scaled_point(3, scale), marker_y + _scaled_point(2, scale)],
        radius=_scaled_point(2, scale),
        fill=(255, 106, 203, 230),
    )
    draw.line(
        [(inset + _scaled_point(4, scale), marker_y),
         (width - inset - _scaled_point(4, scale), marker_y)],
        fill=(255, 230, 250, 230),
        width=max(1, _scaled_point(0.8, scale)),
    )
    return image


def _pan_thumb(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = width / 15.0
    cx, cy = width // 2, height // 2
    radius = max(2, _scaled_point(4.8, scale))
    draw.ellipse([cx - radius + 1, cy - radius + 2, cx + radius + 1, cy + radius + 2], fill=(0, 0, 0, 105))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(13, 18, 30, 245), outline=(114, 239, 255, 235), width=max(1, _scaled_point(1, scale)))
    draw.line([(cx, cy - radius + 2), (cx, cy + radius - 2)], fill=(255, 106, 203, 230), width=max(1, _scaled_point(1, scale)))
    draw.line([(cx - _scaled_point(2.5, scale), cy), (cx + _scaled_point(2.5, scale), cy)], fill=(242, 247, 255, 220), width=max(1, _scaled_point(0.7, scale)))
    return image


def _pan_bg(width: int, height: int) -> Image.Image:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = max(2, height // 2)
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=radius, fill=(7, 13, 24, 232), outline=(38, 54, 79, 255), width=max(1, height // 8))
    cy = height // 2
    draw.line([(max(1, height // 2), cy), (width - max(1, height // 2), cy)], fill=(114, 239, 255, 190), width=max(1, height // 5))
    draw.line([(width // 2, max(1, height // 4)), (width // 2, height - max(1, height // 4))], fill=(255, 106, 203, 230), width=max(1, height // 7))
    return image


def _knob_stack(frame_width: int, frames: int = 25, accent: str = "cyan") -> Image.Image:
    """Render a REAPER knob stack: 25 frame states, Astra glass hardware."""
    image = Image.new("RGBA", (frame_width, frame_width * frames), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = frame_width / 23.0
    ring = (114, 239, 255, 245) if accent == "cyan" else (255, 106, 203, 245)
    secondary = (255, 106, 203, 230) if accent == "cyan" else (114, 239, 255, 230)
    for index in range(frames):
        top = index * frame_width
        cx = frame_width // 2
        cy = top + frame_width // 2
        radius = max(3, _scaled_point(8.8, scale))
        draw.ellipse([cx - radius + 1, cy - radius + 2, cx + radius + 1, cy + radius + 2], fill=(0, 0, 0, 105))
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(13, 18, 30, 248), outline=(38, 54, 79, 255), width=max(1, _scaled_point(1, scale)))
        progress = index / max(1, frames - 1)
        draw.arc([cx - radius + 1, cy - radius + 1, cx + radius - 1, cy + radius - 1], 220, int(220 + 280 * progress), fill=ring, width=max(1, _scaled_point(1.2, scale)))
        draw.arc([cx - radius + 3, cy - radius + 3, cx + radius - 3, cy + radius - 3], 40, 130, fill=secondary, width=max(1, _scaled_point(0.8, scale)))
        # Pointer sweeps from lower-left to upper-right across the 25 states.
        import math
        angle = math.radians(225 - 270 * progress)
        px = int(cx + math.cos(angle) * radius * 0.66)
        py = int(cy + math.sin(angle) * radius * 0.66)
        draw.line([(cx, cy), (px, py)], fill=(242, 247, 255, 240), width=max(1, _scaled_point(1.2, scale)))
        dot = max(1, _scaled_point(1.3, scale))
        draw.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=secondary)
    return image


def _single_knob(width: int, height: int, accent: str) -> Image.Image:
    """Render a one-frame knob while preserving REAPER's exact asset box."""
    source_size = max(width, height)
    image = _knob_stack(source_size, 1, accent)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _control_assets(theme_root: str) -> dict[str, bytes]:
    """Return same-size Astra control art for all REAPER density buckets."""
    assets: dict[str, bytes] = {}
    scales = {
        "": 1.0,
        "150": 1.5,
        "200": 2.0,
    }
    for scale_name, scale in scales.items():
        def add(name: str, image: Image.Image) -> None:
            prefix = f"{theme_root}/" + (f"{scale_name}/" if scale_name else "")
            assets[prefix + name] = _png_bytes(image)

        add("mcp_volthumb.png", _fader_grip(round(24 * scale), round(53 * scale)))
        add("mcp_panthumb.png", _pan_thumb(round(15 * scale), round(19 * scale)))
        add("mcp_panbg.png", _pan_bg(round(58 * scale), round(12 * scale)))
        add("mcp_volbg.png", _pan_bg(round(26 * scale), round(22 * scale)))
        add("tcp_volthumb.png", _fader_grip(round(29 * scale), round(29 * scale)))
        add("tcp_panthumb.png", _pan_thumb(round(15 * scale), round(19 * scale)))
        add("tcp_panbg.png", _pan_bg(round(58 * scale), round(12 * scale)))
        add("gen_volthumb_vert.png", _fader_grip(round(19 * scale), round(25 * scale)))
        add("gen_volbg_vert.png", _pan_bg(round(22 * scale), round(24 * scale)))
        add("gen_panthumb_horz.png", _pan_thumb(round(25 * scale), round(25 * scale)))
        add("gen_panbg_horz.png", _pan_bg(round(24 * scale), round(22 * scale)))
        gen_width = round(18 * scale)
        gen_height = round(20 * scale)
        add("gen_knob_bg_small.png", _single_knob(gen_width, gen_height, "cyan"))
        transport_size = round(38 * scale)
        add("transport_knob_bg_small.png", _single_knob(transport_size, transport_size, "magenta"))

        stacks = {
            "mcp_fxparm_knob_stack.png": (23, "cyan"),
            "mcp_send_knob_stack.png": (18, "magenta"),
            "tcp_fxparm_knob_stack.png": (23, "cyan"),
            "tcp_vol_knob_stack.png": (20, "cyan"),
            "tcp_pan_knob_stack.png": (20, "magenta"),
            "tcp_wid_knob_stack.png": (20, "magenta"),
        }
        for name, (base_width, accent) in stacks.items():
            add(name, _knob_stack(round(base_width * scale), 25, accent))

    return assets


def _write_control_atlas() -> None:
    """Create a small human-readable preview of the custom control language."""
    atlas = Image.new("RGBA", (860, 290), (7, 11, 20, 255))
    draw = ImageDraw.Draw(atlas)
    draw.rounded_rectangle([12, 12, 848, 278], radius=18, fill=(13, 18, 30, 255), outline=(38, 54, 79, 255), width=2)
    draw.text((34, 28), "ASTRA CONTROL SURFACE", fill=(114, 239, 255, 255))
    draw.text((34, 52), "REAPER native theme components / 25-frame knobs / glass fader grips", fill=(145, 165, 191, 255))
    samples = [
        ("KNOB", _knob_stack(62, 1, "cyan").crop((0, 0, 62, 62)), 60),
        ("PAN", _pan_thumb(48, 54), 230),
        ("FADER", _fader_grip(44, 96), 400),
        ("METER GRIP", _fader_grip(32, 74), 590),
    ]
    for label, sample, x in samples:
        atlas.alpha_composite(sample, (x, 104))
        draw.text((x, 220), label, fill=(242, 247, 255, 230))
    draw.line([(34, 250), (826, 250)], fill=(255, 106, 203, 170), width=2)
    draw.text((34, 255), "CYAN = signal / MAGENTA = gesture / NAVY = surface", fill=(197, 255, 154, 220))
    CONTROL_ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.convert("RGB").save(CONTROL_ATLAS, format="PNG", optimize=True)


def rewrite_theme_text(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        key, separator, _value = line.partition("=")
        if separator and key in COLOR_OVERRIDES:
            newline = "\n" if line.endswith("\n") else ""
            line = f"{key}={COLOR_OVERRIDES[key]}{newline}"
        lines.append(line)
    return "".join(lines)


def rewrite_rtconfig(text: str) -> str:
    replacements = {
        "tcpBgColR": "13",
        "tcpBgColG": "18",
        "tcpBgColB": "30",
    }
    lines = []
    for line in text.splitlines(keepends=True):
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        for key, value in replacements.items():
            match = re.match(rf"^(define_parameter\s+{key}\s+'.*?'\s+)\d+(\s+0\s+255.*)$", body)
            if match:
                body = f"{match.group(1)}{value}{match.group(2)}"
                line = body + newline
                break
        lines.append(line)
    return "".join(lines)


def main() -> None:
    if not DEFAULT_THEME.is_file():
        raise SystemExit(f"REAPER default theme not found: {DEFAULT_THEME}")
    OUTPUT_THEME.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(DEFAULT_THEME) as source:
        names = source.namelist()
        theme_name = next(name for name in names if name.endswith("_unpacked.ReaperTheme"))
        rtconfig_name = next(name for name in names if name.endswith("/rtconfig.txt"))
        # The .ReaperTheme descriptor is a root-level file; image assets live
        # beside rtconfig.txt in the unpacked directory.
        theme_root = rtconfig_name.rsplit("/", 1)[0]
        custom_assets = _control_assets(theme_root)
        fd, temporary_name = tempfile.mkstemp(prefix="Astra_Workbench.", suffix=".ReaperThemeZip", dir=OUTPUT_THEME.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(temporary_name, "w") as target:
                for info in source.infolist():
                    payload = source.read(info.filename)
                    if info.filename == theme_name:
                        payload = rewrite_theme_text(payload.decode("utf-8")).encode("utf-8")
                    elif info.filename == rtconfig_name:
                        payload = rewrite_rtconfig(payload.decode("utf-8")).encode("utf-8")
                    elif info.filename in custom_assets:
                        payload = custom_assets.pop(info.filename)
                    target.writestr(info, payload)
                for filename, payload in custom_assets.items():
                    target.writestr(filename, payload, compress_type=zipfile.ZIP_DEFLATED)
            os.replace(temporary_name, OUTPUT_THEME)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


    _write_control_atlas()


if __name__ == "__main__":
    main()
