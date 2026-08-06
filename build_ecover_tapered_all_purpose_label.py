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
OUTPUT = ROOT / "output" / "pdf" / "ecover-all-purpose-cleaner-tapered-spray-bottle-44x70mm.pdf"
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-44x70.png"
LOGO = ROOT / "tmp" / "pdfs" / "assets" / "ecover-official-logo.svg"

PAGE_W = 44 * mm
PAGE_H = 70 * mm
TOP_WIDTH = 28 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
GINGER = HexColor("#E8C568")
VIOLET = HexColor("#9B7ACB")
INK = HexColor("#573579")
CUTLINE = HexColor("#C9C9C9")


def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))


def label_shape(c):
    inset = (PAGE_W - TOP_WIDTH) / 2
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(PAGE_W, 0)
    p.lineTo(PAGE_W - inset, PAGE_H)
    p.lineTo(inset, PAGE_H)
    p.close()
    return p


def draw_white_ecover_logo(c):
    drawing = svg2rlg(str(LOGO))

    def make_white(node):
        if hasattr(node, "fillColor") and node.fillColor is not None:
            node.fillColor = CREAM
        if hasattr(node, "strokeColor") and node.strokeColor is not None:
            node.strokeColor = CREAM
        for child in getattr(node, "contents", []):
            make_white(child)

    make_white(drawing)
    target_w = 17 * mm
    scale = target_w / drawing.width
    drawing.scale(scale, scale)
    renderPDF.draw(drawing, c, (PAGE_W - target_w) / 2, 57.5 * mm)


def draw_ingredients(c):
    cx, cy = 12.5 * mm, 10.5 * mm
    c.setStrokeColor(VIOLET)
    c.setLineWidth(0.5)
    for dx, top in [(-3.3, 18.2), (-1.4, 19.6), (1.0, 19.0), (3.0, 17.8)]:
        c.line(cx + dx * mm, 5.8 * mm, cx + dx * 0.55 * mm, top * mm)

    c.setFillColor(GINGER)
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.65)
    p = c.beginPath()
    p.moveTo(cx - 5.0 * mm, cy - 0.7 * mm)
    p.curveTo(cx - 5.7 * mm, cy + 2.2 * mm, cx - 2.7 * mm, cy + 4.1 * mm, cx - 0.6 * mm, cy + 3.3 * mm)
    p.curveTo(cx + 0.6 * mm, cy + 5.5 * mm, cx + 4.0 * mm, cy + 4.3 * mm, cx + 4.0 * mm, cy + 1.9 * mm)
    p.curveTo(cx + 5.8 * mm, cy + 1.0 * mm, cx + 5.3 * mm, cy - 2.2 * mm, cx + 3.1 * mm, cy - 2.7 * mm)
    p.curveTo(cx + 2.2 * mm, cy - 4.6 * mm, cx - 1.0 * mm, cy - 4.5 * mm, cx - 2.4 * mm, cy - 2.8 * mm)
    p.curveTo(cx - 4.3 * mm, cy - 3.2 * mm, cx - 5.5 * mm, cy - 2.1 * mm, cx - 5.0 * mm, cy - 0.7 * mm)
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(GOLD)
    for dx, dy, radius in [(-2.3, 1.0, .5), (.1, 2.4, .45), (2.4, .2, .45), (.2, -1.8, .4)]:
        c.circle(cx + dx * mm, cy + dy * mm, radius * mm, stroke=0, fill=1)


def build():
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    staging = OUTPUT.with_suffix(".staging.pdf")

    c = canvas.Canvas(
        str(staging), pagesize=(PAGE_W, PAGE_H), pageCompression=1,
        initialFontName="LabelElegant", initialFontSize=10,
    )
    c.setTitle("Ecover All Purpose Cleaner - Tapered Spray Bottle Label")
    c.setAuthor("Custom refill label")

    shape = label_shape(c)
    c.saveState()
    c.clipPath(shape, stroke=0, fill=0)
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")
    c.restoreState()

    draw_white_ecover_logo(c)
    draw_shadowed_centred(
        c, PAGE_W / 2, 45.2 * mm, "Lemongrass & Ginger",
        "LabelElegant", 7.0, CREAM, offset_mm=0.35,
    )

    draw_shadowed_centred(
        c, PAGE_W / 2, 34.5 * mm, "All Purpose",
        "LabelMagic", 22.0, CREAM, offset_mm=0.5,
    )
    draw_shadowed_centred(
        c, PAGE_W / 2, 25.0 * mm, "Cleaner",
        "LabelMagic", 27.0, CREAM, offset_mm=0.5,
    )

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.setLineCap(1)
    c.line(14 * mm, 21.0 * mm, 30 * mm, 21.0 * mm)
    draw_ingredients(c)

    c.setFillColor(CREAM)
    c.roundRect(23 * mm, 4.0 * mm, 18 * mm, 7.5 * mm, 1.0 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("LabelElegant", 5.3)
    c.drawCentredString(32 * mm, 6.5 * mm, "Refill • Reuse")

    c.setStrokeColor(CUTLINE)
    c.setLineWidth(0.25)
    c.drawPath(label_shape(c), stroke=1, fill=0)
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
        "/Title": "Ecover All Purpose Cleaner - Tapered Spray Bottle Label - 44 x 70 mm",
        "/Author": "Custom refill label",
    })
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    staging.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
