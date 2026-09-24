#!/usr/bin/env python3
"""Build the transparent 24-plane depth treatment for the workspace desktop.

The stack is deliberately rendered as ordinary RGBA assets rather than relying
on a compositor. That keeps the effect deterministic on Xvfb while retaining
the layer data for a future composited VM desktop.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BG = (44, 0, 30)
TOP = 32
DOCK_W = 74
WALLPAPER_ALPHA = 198
STACK_VERSION = 1


def _font(size: int, bold: bool = False):
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


def _layer_name(index: int) -> str:
    if index == 1:
        return "layer-01-wallpaper.png"
    return f"layer-{index:02d}-desktop-depth.png"


def _manifest_matches(manifest_path: Path, width: int, height: int,
                       depth_layers: int, step_pixels: int,
                       stack_dir: Path, composite_path: Path) -> bool:
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError):
        return False
    if manifest.get("version") != STACK_VERSION:
        return False
    if manifest.get("canvas") != [width, height]:
        return False
    if manifest.get("depth_layers") != depth_layers:
        return False
    if manifest.get("step_pixels") != step_pixels:
        return False
    if not composite_path.exists():
        return False
    layers = manifest.get("layers")
    if not isinstance(layers, list) or len(layers) != depth_layers:
        return False
    return all((stack_dir / item.get("file", "")).exists() for item in layers)


def _save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    image.save(temporary, format="PNG", optimize=True)
    temporary.replace(path)


def _draw_depth_layer(width: int, height: int, z: int,
                      step_pixels: int) -> Image.Image:
    """Render one transparent plane. z is 2..depth_layers."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    offset = (z - 1) * step_pixels
    shadow_alpha = min(64, 6 + z * 2)
    edge_alpha = min(72, 10 + z * 2)

    # A one-pixel extrusion under the top panel and left dock establishes the
    # desktop's physical frame without changing the existing controls.
    draw.rectangle(
        [offset, TOP + offset, width - 1, TOP + offset + 1],
        fill=(11, 2, 12, shadow_alpha),
    )
    draw.line(
        [(DOCK_W + offset, TOP + offset),
         (DOCK_W + offset, height - 1)],
        fill=(245, 91, 171, edge_alpha),
        width=1,
    )

    # The icon well receives a stepped translucent extrusion behind it.
    ix0, iy0 = DOCK_W + 38 + offset, TOP + 38 + offset
    ix1, iy1 = ix0 + 150, iy0 + 240
    draw.rounded_rectangle(
        [ix0, iy0, ix1, iy1],
        radius=6,
        fill=(64, 5, 52, shadow_alpha),
        outline=(225, 68, 151, edge_alpha),
        width=1,
    )

    # Every fourth plane is a faint perspective guide. These remain sparse so
    # the wallpaper stays readable while the 24-pixel depth is visible.
    if z % 4 == 0:
        margin = 86 + offset
        draw.rounded_rectangle(
            [margin, TOP + 86 + offset, width - margin, height - 88 - offset],
            radius=18,
            outline=(217, 76, 155, min(26, 6 + z // 2)),
            width=1,
        )
    if z in (6, 12, 18, 24):
        guide_alpha = min(24, 8 + z // 3)
        draw.line(
            [(DOCK_W + 118 + offset, TOP + 52 + offset),
             (width - 150 + offset, height - 156 + offset)],
            fill=(246, 108, 176, guide_alpha),
            width=1,
        )
        draw.line(
            [(DOCK_W + 118 + offset, height - 156 + offset),
             (width - 150 + offset, TOP + 52 + offset)],
            fill=(130, 58, 143, guide_alpha),
            width=1,
        )

    if z == 24:
        label = "DESKTOP DEPTH 24 / 1PX PLANES"
        draw.text(
            (width - 340, height - 48),
            label,
            font=_font(14, True),
            fill=(255, 189, 219, 132),
        )

    return layer


def build_depth_scene(wallpaper_path: Path, assets_root: Path, width: int,
                      height: int, depth_layers: int = 24,
                      step_pixels: int = 1) -> Path:
    """Create or reuse the 24-plane RGBA stack and its deterministic composite."""
    if depth_layers < 2:
        raise ValueError("depth_layers must be at least 2")
    if step_pixels < 1:
        raise ValueError("step_pixels must be at least 1")

    stack_dir = assets_root / "depth"
    manifest_path = stack_dir / "manifest.json"
    composite_path = assets_root / "desktop-3d-composite.png"
    if _manifest_matches(manifest_path, width, height, depth_layers,
                         step_pixels, stack_dir, composite_path):
        return composite_path

    with Image.open(wallpaper_path) as source:
        wallpaper = source.convert("RGBA")
    if wallpaper.size != (width, height):
        resampling = getattr(Image, "Resampling", Image).LANCZOS
        wallpaper = wallpaper.resize((width, height), resampling)
    wallpaper.putalpha(WALLPAPER_ALPHA)

    stack_dir.mkdir(parents=True, exist_ok=True)
    layer_records = []
    scene = Image.new("RGBA", (width, height), (*BG, 255))

    wallpaper_layer_path = stack_dir / _layer_name(1)
    _save_png(wallpaper, wallpaper_layer_path)
    scene.alpha_composite(wallpaper)
    layer_records.append({
        "index": 1,
        "z": 0,
        "file": wallpaper_layer_path.name,
        "role": "wallpaper base plane",
        "rgba": True,
        "alpha": WALLPAPER_ALPHA,
        "transparent": True,
    })

    for z in range(2, depth_layers + 1):
        layer = _draw_depth_layer(width, height, z, step_pixels)
        layer_path = stack_dir / _layer_name(z)
        _save_png(layer, layer_path)
        scene.alpha_composite(layer)
        layer_records.append({
            "index": z,
            "z": z - 1,
            "file": layer_path.name,
            "role": "transparent desktop extrusion and perspective guide",
            "rgba": True,
            "alpha": "sparse",
            "transparent": True,
        })

    _save_png(scene, composite_path)
    manifest = {
        "version": STACK_VERSION,
        "canvas": [width, height],
        "display_depth": 24,
        "depth_layers": depth_layers,
        "step_pixels": step_pixels,
        "construction": "wallpaper layer 01, then transparent 1px planes outward",
        "layers": layer_records,
        "composite": composite_path.name,
    }
    temporary_manifest = manifest_path.with_name(manifest_path.name + ".tmp")
    temporary_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    temporary_manifest.replace(manifest_path)
    return composite_path
