#!/usr/bin/env python3
"""
generate_icons.py — Convert Numa SVG icons to PNG for Home Assistant add-on.

Usage:
    python3 scripts/generate_icons.py

Output:
    numa/icon.png   — 128x128 px  (required by HA Supervisor)
    numa/logo.png   — 250x100 px  (required by HA Supervisor)

Dependencies (install one of):
    pip install cairosvg            # preferred — best SVG fidelity
    pip install Pillow cairosvg     # if you also want Pillow post-processing

If cairosvg is not available the script falls back to Inkscape or rsvg-convert
if either is found on PATH.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NUMA_DIR = REPO_ROOT / "numa"

ICONS = [
    {
        "svg": NUMA_DIR / "icon.svg",
        "png": NUMA_DIR / "icon.png",
        "width": 128,
        "height": 128,
    },
    {
        "svg": NUMA_DIR / "logo.svg",
        "png": NUMA_DIR / "logo.png",
        "width": 250,
        "height": 100,
    },
]


# ---------------------------------------------------------------------------
# Conversion back-ends
# ---------------------------------------------------------------------------


def convert_cairosvg(svg_path: Path, png_path: Path, width: int, height: int) -> bool:
    """Convert using the cairosvg Python library."""
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return False

    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=width,
        output_height=height,
    )
    return True


def convert_inkscape(svg_path: Path, png_path: Path, width: int, height: int) -> bool:
    """Convert using the Inkscape CLI (v1.x syntax)."""
    if not shutil.which("inkscape"):
        return False

    cmd = [
        "inkscape",
        str(svg_path),
        f"--export-filename={png_path}",
        f"--export-width={width}",
        f"--export-height={height}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def convert_rsvg(svg_path: Path, png_path: Path, width: int, height: int) -> bool:
    """Convert using rsvg-convert (part of librsvg)."""
    if not shutil.which("rsvg-convert"):
        return False

    cmd = [
        "rsvg-convert",
        "-w",
        str(width),
        "-h",
        str(height),
        "-o",
        str(png_path),
        str(svg_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def convert_imagemagick(
    svg_path: Path, png_path: Path, width: int, height: int
) -> bool:
    """Convert using ImageMagick's convert / magick command."""
    cmd_name = "magick" if shutil.which("magick") else "convert"
    if not shutil.which(cmd_name):
        return False

    cmd = [
        cmd_name,
        "-background",
        "none",
        "-resize",
        f"{width}x{height}",
        str(svg_path),
        str(png_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


BACKENDS = [
    ("cairosvg (Python library)", convert_cairosvg),
    ("Inkscape", convert_inkscape),
    ("rsvg-convert", convert_rsvg),
    ("ImageMagick", convert_imagemagick),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def convert_icon(entry: dict) -> bool:
    svg: Path = entry["svg"]
    png: Path = entry["png"]
    width: int = entry["width"]
    height: int = entry["height"]

    if not svg.exists():
        print(f"  [ERROR] SVG not found: {svg}", file=sys.stderr)
        return False

    for name, fn in BACKENDS:
        try:
            ok = fn(svg, png, width, height)
        except Exception as exc:
            print(f"  [{name}] failed with exception: {exc}")
            ok = False

        if ok and png.exists():
            size = png.stat().st_size
            print(
                f"  OK  {png.relative_to(REPO_ROOT)}  ({width}x{height}, {size:,} bytes)  [{name}]"
            )
            return True
        elif ok:
            print(f"  [{name}] reported success but output file not found.")

    return False


def main() -> int:
    print("Numa icon generator")
    print("=" * 50)

    any_failed = False
    for entry in ICONS:
        svg_rel = entry["svg"].relative_to(REPO_ROOT)
        png_rel = entry["png"].relative_to(REPO_ROOT)
        print(f"\n{svg_rel}  ->  {png_rel}  ({entry['width']}x{entry['height']})")

        if not convert_icon(entry):
            print(
                f"  [FAIL] Could not convert {svg_rel}.\n"
                f"         Install one of: cairosvg, inkscape, rsvg-convert, imagemagick",
                file=sys.stderr,
            )
            any_failed = True

    print()
    if any_failed:
        print("Some icons could not be generated. See errors above.")
        print()
        print("Quick fix:")
        print("  pip install cairosvg")
        print("  python3 scripts/generate_icons.py")
        return 1

    print("All icons generated successfully.")
    print()
    print("Next steps:")
    print("  git add numa/icon.png numa/logo.png")
    print("  git commit -m 'feat: add add-on icon and logo'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
