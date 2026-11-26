#!/usr/bin/env python3
"""Wrap a raw Platane/snk SVG inside a Botanical Oat & Forest cut-paper card."""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

BOTANICAL_ROOT_VARS = (
    ":root{"
    "--cb:#1B2A2226;"
    "--cs:#E06D44;"
    "--ce:#ECE8DD;"
    "--c0:#ECE8DD;"
    "--c1:#D9F0E6;"
    "--c2:#74B89B;"
    "--c3:#1F6F54;"
    "--c4:#1B2A22"
    "}"
)

FONT_HEAD = "'Space Grotesk', 'Segoe UI', 'Ubuntu', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', 'Ubuntu', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
FONT_MONO = "'JetBrains Mono', 'DejaVu Sans Mono', Consolas, monospace"


def _spark_star(cx: float, cy: float, size: float = 16.0) -> str:
    r = size * 0.48
    ir = size * 0.16
    pts = [
        (cx, cy - r),
        (cx + ir, cy - ir),
        (cx + r, cy),
        (cx + ir, cy + ir),
        (cx, cy + r),
        (cx - ir, cy + ir),
        (cx - r, cy),
        (cx - ir, cy - ir),
    ]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return (
        f'<path d="{d}" fill="#C28A0C" stroke="#1B2A22" '
        f'stroke-width="1.4" stroke-linejoin="round"/>'
    )


def restyle_snake_svg(raw_svg: str) -> str:
    open_match = re.search(r"<svg\b([^>]*)>", raw_svg, flags=re.IGNORECASE | re.DOTALL)
    close_idx = raw_svg.rfind("</svg>")
    if not open_match or close_idx == -1:
        raise ValueError("Input file does not contain a valid root <svg>...</svg> element.")

    attrs = open_match.group(1)
    vb_match = re.search(r'viewBox\s*=\s*"([^"]+)"', attrs)
    view_box = vb_match.group(1) if vb_match else "-16 -32 880 192"

    inner = raw_svg[open_match.end() : close_idx]
    if re.search(r":root\s*\{[^}]*\}", inner):
        inner = re.sub(r":root\s*\{[^}]*\}", BOTANICAL_ROOT_VARS, inner, count=1)
    else:
        inner = re.sub(
            r"<style[^>]*>",
            f"<style>{BOTANICAL_ROOT_VARS}",
            inner,
            count=1,
            flags=re.IGNORECASE,
        )

    # Give snake segments a crisp Botanical charcoal ink outline.
    inner = inner.replace("</style>", ".s{stroke:#1B2A22;stroke-width:1.15px}</style>", 1)

    legend_dots = ["#ECE8DD", "#D9F0E6", "#74B89B", "#1F6F54", "#1B2A22"]
    legend_rects = "\n  ".join(
        f'<rect x="{952 + i * 18}" y="27" width="13" height="13" rx="3.5" '
        f'fill="{color}" stroke="#1B2A22" stroke-width="1.15"/>'
        for i, color in enumerate(legend_dots)
    )

    framed = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="336" viewBox="0 0 1200 336" role="img" aria-label="Abdelrahman Khaled — Contribution Activity Snake Animation">
  <title>Abdelrahman Khaled — Contribution Activity</title>
  <defs>
    <pattern id="snkOatDots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="4" cy="4" r="1.15" fill="#D6D0C1" fill-opacity="0.55"/>
    </pattern>
    <style>
      .snk-head {{ font-family: {FONT_HEAD}; }}
      .snk-body {{ font-family: {FONT_BODY}; }}
      .snk-mono {{ font-family: {FONT_MONO}; }}
    </style>
  </defs>

  <!-- Outer Botanical Oat Card -->
  <rect x="9" y="9" width="1186" height="324" rx="22" fill="#1B2A22"/>
  <rect x="4" y="4" width="1186" height="324" rx="22" fill="#F6F4EE" stroke="#1B2A22" stroke-width="1.8"/>
  <rect x="4" y="4" width="1186" height="324" rx="22" fill="url(#snkOatDots)" pointer-events="none"/>

  <!-- Section Title + Marker Highlight -->
  <rect x="30" y="34" width="244" height="14" rx="5" fill="#FEF3C7"/>
  <text x="34" y="44" class="snk-head" font-size="24" font-weight="700" fill="#1B2A22">Contribution Activity</text>
  {_spark_star(292, 35, 16)}

  <!-- Legend Strip -->
  <rect x="898" y="19" width="266" height="30" rx="15" fill="#FFFDF9" stroke="#1B2A22" stroke-width="1.4"/>
  <text x="914" y="38" class="snk-mono" font-size="11" font-weight="600" fill="#52635A">Less</text>
  {legend_rects}
  <text x="1048" y="38" class="snk-mono" font-size="11" font-weight="600" fill="#52635A">More</text>
  <rect x="1086" y="23" width="68" height="22" rx="11" fill="#FCE5DA" stroke="#1B2A22" stroke-width="1.2"/>
  <circle cx="1099" cy="34" r="4.5" fill="#E06D44" stroke="#1B2A22" stroke-width="1.1"/>
  <text x="1110" y="38" class="snk-body" font-size="11" font-weight="700" fill="#B0441F">Snake</text>

  <!-- Inner Crisp Paper Panel -->
  <rect x="34" y="76" width="1134" height="234" rx="18" fill="#1B2A22"/>
  <rect x="30" y="72" width="1134" height="234" rx="18" fill="#FFFDF9" stroke="#1B2A22" stroke-width="1.6"/>

  <!-- Nested Live Platane/snk SVG -->
  <svg xmlns="http://www.w3.org/2000/svg" x="48" y="84" width="1098" height="214" viewBox="{view_box}" preserveAspectRatio="xMidYMid meet">
    {inner}
  </svg>
</svg>
"""
    ET.fromstring(framed)
    return framed


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: wrap_snake_card.py <input_raw_snake.svg> <output_framed_snake.svg>")

    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, "r", encoding="utf-8") as fh:
        raw_svg = fh.read()

    framed_svg = restyle_snake_svg(raw_svg)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(framed_svg)
    print(f"Wrote & XML-validated {out_path} ({len(framed_svg)} bytes)")


if __name__ == "__main__":
    main()
