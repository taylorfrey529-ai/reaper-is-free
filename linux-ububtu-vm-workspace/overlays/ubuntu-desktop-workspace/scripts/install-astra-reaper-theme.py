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
from pathlib import Path


ROOT = Path("/mnt/data/ubuntu-desktop-workspace")
DEFAULT_THEME = ROOT / "apps" / "REAPER" / "InstallData" / "ColorThemes" / "Default_7.0.ReaperThemeZip"
OUTPUT_THEME = ROOT / "config" / "REAPER" / "ColorThemes" / "Astra_Workbench.ReaperThemeZip"

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
                    target.writestr(info, payload)
            os.replace(temporary_name, OUTPUT_THEME)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


if __name__ == "__main__":
    main()
