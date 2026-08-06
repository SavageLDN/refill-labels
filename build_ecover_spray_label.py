from pathlib import Path
import re

from pypdf import PdfReader, PdfWriter
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

from label_text import draw_shadowed_centred


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "ecover-all-purpose-cleaner-lemongrass-ginger-magical-60x85mm.pdf"
LOGO = ROOT / "tmp" / "pdfs" / "assets" / "ecover-official-logo.svg"
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-60x85.png"

PAGE_W = 60 * mm
PAGE_H = 85 * mm
DESIGN_W = 80 * mm
DESIGN_H = 110 * mm
DESIGN_SCALE = 0.75
DESIGN_X_OFFSET = (PAGE_W - DESIGN_W * DESIGN_SCALE) / 2
DESIGN_Y_OFFSET = (PAGE_H - DESIGN_H * DESIGN_SCALE) / 2

SCENT_TEXT = "Lemongrass & Ginger"
PRODUCT_LINE_1 = "All Purpose"
PRODUCT_LINE_2 = "Cleaner"
DESCRIPTOR_TEXT = "Refill • Reuse"

AQUA = HexColor("#101C3A")
AQUA_DARK = HexColor("#392557")
AQUA_DEEP = HexColor("#5B3E86")
AQUA_LIGHT = HexColor("#665086")
CREAM = HexColor("#FAF5E6")
CORAL = HexColor("#D9B65D")
GINGER = HexColor("#E8C568")
LEAF = HexColor("#9B7ACB")


def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelSans", r"C:\Windows\Fonts\gadugi.ttf"))
    pdfmetrics.registerFont(TTFont("LabelSansBold", r"C:\Windows\Fonts\gadugib.ttf"))
    pdfmetrics.registerFont(TTFont("LabelSerifBold", r"C:\Windows\Fonts\georgiab.ttf"))
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))


def line(c, x1, y1, x2, y2, colour=CREAM, width=0.65):
    c.setStrokeColor(colour)
    c.setLineWidth(width)
    c.setLineCap(1)
    c.line(x1, y1, x2, y2)


def draw_pattern(c):
    c.saveState()
    c.setStrokeColor(AQUA_DEEP)
    c.setLineWidth(0.42)
    for dx, dy, scale in [(8, 69, 1.0), (44, 80, 0.82), (43, 34, 1.02), (15, 12, 0.7)]:
        p = c.beginPath()
        p.moveTo((dx + 1) * mm, dy * mm)
        p.curveTo((dx + 10 * scale) * mm, (dy + 13 * scale) * mm,
                  (dx + 25 * scale) * mm, (dy + 12 * scale) * mm,
                  (dx + 30 * scale) * mm, (dy + 1 * scale) * mm)
        p.curveTo((dx + 21 * scale) * mm, (dy - 7 * scale) * mm,
                  (dx + 8 * scale) * mm, (dy - 5 * scale) * mm,
                  (dx + 1) * mm, dy * mm)
        c.drawPath(p, stroke=1, fill=0)
        line(c, (dx + 4) * mm, dy * mm,
             (dx + 26 * scale) * mm, (dy + 2 * scale) * mm,
             AQUA_DEEP, 0.36)
    c.setStrokeColor(AQUA_LIGHT)
    c.setLineWidth(0.55)
    c.circle(65 * mm, 18 * mm, 16 * mm, stroke=1, fill=0)
    c.circle(69 * mm, 92 * mm, 12 * mm, stroke=1, fill=0)
    c.restoreState()


def draw_magic_motif(c):
    """An elegant gold moon and a star field kept outside the wording zones."""
    c.saveState()
    c.setStrokeColor(CORAL)
    c.setLineWidth(0.65)
    c.roundRect(4 * mm, 4 * mm, 72 * mm, 102 * mm, 2 * mm, stroke=1, fill=0)

    c.setFillColor(CORAL)
    c.circle(66 * mm, 96 * mm, 6.2 * mm, stroke=0, fill=1)
    c.setFillColor(AQUA)
    c.circle(69.0 * mm, 98.2 * mm, 6.2 * mm, stroke=0, fill=1)
    c.setFillColor(AQUA_LIGHT)
    c.setStrokeColor(CORAL)
    c.setLineWidth(0.45)
    cloud = c.beginPath()
    cloud.moveTo(56 * mm, 91 * mm)
    cloud.curveTo(57.5 * mm, 94.2 * mm, 60.5 * mm, 95.0 * mm, 62.5 * mm, 93.2 * mm)
    cloud.curveTo(63.8 * mm, 97.0 * mm, 68.2 * mm, 97.2 * mm, 69.5 * mm, 93.4 * mm)
    cloud.curveTo(72.5 * mm, 95.0 * mm, 75.0 * mm, 93.1 * mm, 75.0 * mm, 90.7 * mm)
    cloud.curveTo(70.8 * mm, 89.0 * mm, 60.0 * mm, 89.0 * mm, 56 * mm, 91 * mm)
    c.drawPath(cloud, stroke=1, fill=1)
    for cx, cy, radius in [(12, 87, 1.25), (71, 73, 1.0), (9, 54, 1.1), (70, 41, 1.15), (20, 101, 0.8)]:
        line(c, (cx - radius) * mm, cy * mm, (cx + radius) * mm, cy * mm, CORAL, 0.52)
        line(c, cx * mm, (cy - radius) * mm, cx * mm, (cy + radius) * mm, CORAL, 0.52)
    for cx, cy, radius in [
        (9, 99, .36), (15, 94, .24), (28, 102, .22), (51, 101, .28),
        (72, 84, .30), (8, 78, .22), (73, 65, .28), (8, 63, .22),
        (72, 51, .23), (10, 46, .30), (72, 34, .26), (9, 30, .22),
        (73, 24, .30), (13, 16, .24), (35, 7, .22), (52, 29, .20),
    ]:
        c.setFillColor(CORAL)
        c.circle(cx * mm, cy * mm, radius * mm, stroke=0, fill=1)
    c.restoreState()


def draw_logo(c):
    """Place the product logo in white as the sole wordmark."""
    centre = 40 * mm
    drawing = svg2rlg(str(LOGO))
    def make_white(node):
        if hasattr(node, "fillColor") and node.fillColor is not None:
            node.fillColor = CREAM
        if hasattr(node, "strokeColor") and node.strokeColor is not None:
            node.strokeColor = CREAM
        for child in getattr(node, "contents", []):
            make_white(child)
    make_white(drawing)
    target_w = 18 * mm
    scale = target_w / drawing.width
    drawing.scale(scale, scale)
    renderPDF.draw(drawing, c, centre - target_w / 2, 91.0 * mm)


def draw_spark(c, cx, cy, r=2.8):
    import math
    for angle in (0, 45, 90, 135):
        a = math.radians(angle)
        dx, dy = math.cos(a) * r * mm, math.sin(a) * r * mm
        line(c, cx - dx, cy - dy, cx + dx, cy + dy, CREAM, 0.55)


def draw_spray(c, cx, cy):
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.55)
    c.roundRect(cx - 2.7 * mm, cy - 3.4 * mm, 5.4 * mm, 6.0 * mm, 0.8 * mm, stroke=1, fill=0)
    line(c, cx - 1.5 * mm, cy + 2.6 * mm, cx + 1.6 * mm, cy + 2.6 * mm, CREAM, 0.55)
    line(c, cx + 1.6 * mm, cy + 2.6 * mm, cx + 3.1 * mm, cy + 1.7 * mm, CREAM, 0.55)
    for dx, dy in [(4.2, 2.3), (5.0, 1.2), (5.1, 3.5)]:
        c.setFillColor(CREAM)
        c.circle(cx + dx * mm, cy + dy * mm, 0.25 * mm, stroke=0, fill=1)


def draw_leaf(c, cx, cy):
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.55)
    p = c.beginPath()
    p.moveTo(cx - 3.0 * mm, cy - 1.0 * mm)
    p.curveTo(cx - 1.6 * mm, cy + 3.2 * mm, cx + 2.6 * mm, cy + 2.8 * mm, cx + 3.1 * mm, cy + 0.4 * mm)
    p.curveTo(cx + 1.0 * mm, cy - 2.1 * mm, cx - 1.7 * mm, cy - 2.1 * mm, cx - 3.0 * mm, cy - 1.0 * mm)
    c.drawPath(p, stroke=1, fill=0)
    line(c, cx - 2.3 * mm, cy - 0.7 * mm, cx + 2.0 * mm, cy + 1.0 * mm, CREAM, 0.5)


def draw_refill(c, cx, cy):
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.55)
    c.arc(cx - 3.5 * mm, cy - 3.5 * mm, cx + 3.5 * mm, cy + 3.5 * mm, 35, 115)
    c.arc(cx - 3.5 * mm, cy - 3.5 * mm, cx + 3.5 * mm, cy + 3.5 * mm, 215, 115)
    line(c, cx + 1.9 * mm, cy + 2.7 * mm, cx + 3.6 * mm, cy + 2.7 * mm, CREAM, 0.5)
    line(c, cx + 3.6 * mm, cy + 2.7 * mm, cx + 3.1 * mm, cy + 1.0 * mm, CREAM, 0.5)
    line(c, cx - 1.9 * mm, cy - 2.7 * mm, cx - 3.6 * mm, cy - 2.7 * mm, CREAM, 0.5)
    line(c, cx - 3.6 * mm, cy - 2.7 * mm, cx - 3.1 * mm, cy - 1.0 * mm, CREAM, 0.5)


def draw_icon_rail(c):
    c.setFillColor(AQUA_DARK)
    c.roundRect(7 * mm, 8 * mm, 11 * mm, 94 * mm, 1.2 * mm, stroke=0, fill=1)
    x = 12.5 * mm
    draw_spark(c, x, 87 * mm)
    draw_spray(c, x, 66 * mm)
    draw_leaf(c, x, 45 * mm)
    draw_refill(c, x, 23 * mm)


def draw_ingredient_mark(c):
    # A clearly recognisable ginger root with long lemongrass blades behind it.
    cx, cy = 25 * mm, 23 * mm
    for x1, y1, x2, y2 in [(-7, -9, -4, 13), (-3, -10, -1, 15), (2, -10, 2, 14), (6, -9, 5, 12)]:
        line(c, cx + x1 * mm, cy + y1 * mm, cx + x2 * mm, cy + y2 * mm, LEAF, 0.75)

    c.setFillColor(GINGER)
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(cx - 8.5 * mm, cy - 2.0 * mm)
    p.curveTo(cx - 10.0 * mm, cy + 3.5 * mm, cx - 5.5 * mm, cy + 7.3 * mm, cx - 1.4 * mm, cy + 6.0 * mm)
    p.curveTo(cx + 1.2 * mm, cy + 10.0 * mm, cx + 7.0 * mm, cy + 8.0 * mm, cx + 7.2 * mm, cy + 4.0 * mm)
    p.curveTo(cx + 11.0 * mm, cy + 2.5 * mm, cx + 10.0 * mm, cy - 2.8 * mm, cx + 6.0 * mm, cy - 4.0 * mm)
    p.curveTo(cx + 4.8 * mm, cy - 8.0 * mm, cx - 0.3 * mm, cy - 9.0 * mm, cx - 3.2 * mm, cy - 6.0 * mm)
    p.curveTo(cx - 7.0 * mm, cy - 7.0 * mm, cx - 10.0 * mm, cy - 5.0 * mm, cx - 8.5 * mm, cy - 2.0 * mm)
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(CORAL)
    for dx, dy, radius in [(-4.5, 1.8, 1.0), (0.6, 4.7, 0.85), (4.3, 0.1, 0.9), (0.0, -3.5, 0.7)]:
        c.circle(cx + dx * mm, cy + dy * mm, radius * mm, stroke=0, fill=1)


def build():
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    staging = OUTPUT.with_suffix(".staging.pdf")

    c = canvas.Canvas(
        str(staging), pagesize=(PAGE_W, PAGE_H), pageCompression=1,
        initialFontName="LabelSans", initialFontSize=10,
    )
    c.setTitle(f"Witches and Wizards Pantry {PRODUCT_LINE_1} {PRODUCT_LINE_2} - {SCENT_TEXT} - Front Label")
    c.setAuthor("Custom refill label")

    c.setFillColor(AQUA)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    c.saveState()
    c.translate(DESIGN_X_OFFSET, DESIGN_Y_OFFSET)
    c.scale(DESIGN_SCALE, DESIGN_SCALE)
    draw_logo(c)

    text_centre = 40 * mm
    draw_shadowed_centred(
        c, text_centre, 66.3 * mm, SCENT_TEXT,
        "LabelElegant", 9.2, CREAM,
    )

    draw_shadowed_centred(
        c, text_centre, 54.5 * mm, PRODUCT_LINE_1,
        "LabelMagic", 25.0, CREAM, offset_mm=0.6,
    )
    draw_shadowed_centred(
        c, text_centre, 43.3 * mm, PRODUCT_LINE_2,
        "LabelMagic", 31.0, CREAM, offset_mm=0.6,
    )
    line(c, 28 * mm, 38.5 * mm, 52 * mm, 38.5 * mm, CORAL, 1.35)

    draw_ingredient_mark(c)

    pill_x, pill_y, pill_w, pill_h = 42 * mm, 12 * mm, 30 * mm, 9 * mm
    c.setFillColor(CREAM)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 1.4 * mm, stroke=0, fill=1)
    c.setFillColor(AQUA_DEEP)
    c.setFont("LabelElegant", 7.7)
    c.drawCentredString(pill_x + pill_w / 2, pill_y + 3.05 * mm, DESCRIPTOR_TEXT)
    c.restoreState()

    c.showPage()
    c.save()

    reader = PdfReader(str(staging))
    page = reader.pages[0]
    content = page.get_contents()
    cleaned_data = re.sub(rb"BT /F\d+ 10 Tf 12 TL ET\s*", b"", content.get_data())
    content.set_data(cleaned_data)
    page.replace_contents(content)
    fonts = page["/Resources"]["/Font"]
    for font_key in list(fonts.keys()):
        if font_key.encode("ascii") not in cleaned_data:
            del fonts[font_key]
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        "/Title": f"Witches and Wizards Pantry {PRODUCT_LINE_1} {PRODUCT_LINE_2} - {SCENT_TEXT} - Front Label",
        "/Author": "Custom refill label",
    })
    cleaned = OUTPUT.with_suffix(".cleaned.pdf")
    with cleaned.open("wb") as handle:
        writer.write(handle)
    cleaned.replace(OUTPUT)
    staging.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
