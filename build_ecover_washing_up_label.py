from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

import build_ecover_spray_label as label


ROOT = Path(__file__).resolve().parent

# Reuse the established Ecover/Miniml-style system at a larger handwash-bottle size.
label.OUTPUT = ROOT / "output" / "pdf" / "ecover-washing-up-liquid-lemongrass-ginger-magical-55x70mm.pdf"
label.BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-55x70.png"
label.PAGE_W = 55 * mm
label.PAGE_H = 70 * mm
label.DESIGN_SCALE = min(label.PAGE_W / label.DESIGN_W, label.PAGE_H / label.DESIGN_H)
label.DESIGN_X_OFFSET = (label.PAGE_W - label.DESIGN_W * label.DESIGN_SCALE) / 2
label.DESIGN_Y_OFFSET = (label.PAGE_H - label.DESIGN_H * label.DESIGN_SCALE) / 2

label.SCENT_TEXT = "Lemongrass & Ginger"
label.PRODUCT_LINE_1 = "Washing Up"
label.PRODUCT_LINE_2 = "Liquid"
label.DESCRIPTOR_TEXT = "Refill • Reuse"

# A warmer, kitchen-friendly colourway so it is distinct from the aqua cleaner.
label.AQUA = HexColor("#241431")
label.AQUA_DARK = HexColor("#151B38")
label.AQUA_DEEP = HexColor("#5A3A78")
label.AQUA_LIGHT = HexColor("#624980")
label.CREAM = HexColor("#FAF5E6")
label.CORAL = HexColor("#D9B65D")
label.GINGER = HexColor("#E8C568")
label.LEAF = HexColor("#9B7ACB")


def draw_washing_ingredients(c):
    """Lemongrass blades and a bright ginger slice for the scent ingredients."""
    cx, cy = 25 * mm, 23 * mm

    for x1, y1, x2, y2 in [(-7, -9, -4, 13), (-3, -10, -1, 15), (2, -10, 2, 14), (6, -9, 5, 12)]:
        label.line(c, cx + x1 * mm, cy + y1 * mm,
                   cx + x2 * mm, cy + y2 * mm,
                   label.LEAF, 0.75)

    c.setFillColor(label.CREAM)
    c.setStrokeColor(label.CREAM)
    c.setLineWidth(0.8)
    c.circle(cx, cy, 10.8 * mm, stroke=1, fill=1)
    c.setFillColor(label.GINGER)
    c.setStrokeColor(label.CORAL)
    c.setLineWidth(0.7)
    c.circle(cx, cy, 7.1 * mm, stroke=1, fill=1)
    c.setFillColor(label.CORAL)
    for dx, dy, radius in [(-3.8, 2.6, 0.8), (0.0, 4.3, 0.9), (3.7, 2.1, 0.75), (2.0, -2.8, 0.7), (-2.8, -2.2, 0.65)]:
        c.circle(cx + dx * mm, cy + dy * mm, radius * mm, stroke=0, fill=1)


label.draw_ingredient_mark = draw_washing_ingredients


if __name__ == "__main__":
    label.build()
