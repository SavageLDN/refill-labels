from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from label_text import draw_shadowed_centred


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "plant-mister-water-only-magical-55x70mm.pdf"
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-55x70.png"

PAGE_W = 55 * mm
PAGE_H = 70 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
VIOLET = HexColor("#9B7ACB")
INK = HexColor("#573579")


def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))


def draw_leaf(c, cx, cy, flip=1):
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.55)
    p = c.beginPath()
    p.moveTo(cx, cy)
    p.curveTo(
        cx + flip * 1.0 * mm, cy + 4.0 * mm,
        cx + flip * 6.0 * mm, cy + 5.0 * mm,
        cx + flip * 7.5 * mm, cy + 2.0 * mm,
    )
    p.curveTo(
        cx + flip * 5.0 * mm, cy - 0.2 * mm,
        cx + flip * 1.8 * mm, cy + 0.2 * mm,
        cx, cy,
    )
    c.drawPath(p, stroke=1, fill=0)
    c.line(cx, cy, cx + flip * 6.2 * mm, cy + 2.2 * mm)


def draw_botanical_mark(c):
    cx = 15 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.setLineCap(1)
    c.line(cx, 7 * mm, cx, 21 * mm)
    draw_leaf(c, cx, 12.0 * mm, flip=-1)
    draw_leaf(c, cx, 16.5 * mm, flip=1)

    c.setStrokeColor(VIOLET)
    c.setFillColor(VIOLET)
    for x, y, radius in [(8.2, 22.0, 1.0), (12.1, 25.0, .75), (20.0, 22.5, .85)]:
        p = c.beginPath()
        p.moveTo(x * mm, (y + radius * 1.7) * mm)
        p.curveTo(
            (x - radius) * mm, y * mm,
            (x - radius) * mm, (y - radius) * mm,
            x * mm, (y - radius) * mm,
        )
        p.curveTo(
            (x + radius) * mm, (y - radius) * mm,
            (x + radius) * mm, y * mm,
            x * mm, (y + radius * 1.7) * mm,
        )
        c.drawPath(p, stroke=0, fill=1)


def build():
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(
        str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1,
        initialFontName="LabelElegant", initialFontSize=10,
    )
    c.setTitle("Plant Mister - Water Only - Front Label")
    c.setAuthor("Custom refill label")
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")

    draw_shadowed_centred(
        c, PAGE_W / 2, 34.5 * mm, "Plant Mister",
        "LabelMagic", 31.0, CREAM, offset_mm=0.6,
    )

    draw_shadowed_centred(
        c, PAGE_W / 2, 27.0 * mm, "Water Only",
        "LabelElegant", 8.4, CREAM,
    )
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.setLineCap(1)
    c.line(19 * mm, 23.0 * mm, 36 * mm, 23.0 * mm)

    draw_botanical_mark(c)

    c.setFillColor(CREAM)
    c.roundRect(25 * mm, 5.0 * mm, 26 * mm, 8.5 * mm, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("LabelElegant", 5.8)
    c.drawCentredString(38 * mm, 8.0 * mm, "Fine Mist • Happy Plants")
    c.showPage()
    c.save()

    reader = PdfReader(str(OUTPUT))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        "/Title": "Plant Mister - Water Only - Front Label - 55 x 70 mm",
        "/Author": "Custom refill label",
    })
    cleaned = OUTPUT.with_suffix(".cleaned.pdf")
    with cleaned.open("wb") as handle:
        writer.write(handle)
    cleaned.replace(OUTPUT)


if __name__ == "__main__":
    build()
