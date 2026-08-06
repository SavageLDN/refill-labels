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
OUTPUT_DIR = ROOT / "output" / "pdf"
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-spice-38x30.png"

PAGE_W = 38 * mm
PAGE_H = 30 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
RED = HexColor("#C94E52")
GREEN = HexColor("#76A779")
VIOLET = HexColor("#9B7ACB")


def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))


def draw_chilli(c):
    c.setStrokeColor(RED)
    c.setLineWidth(1.7)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(4.0 * mm, 9.0 * mm)
    p.curveTo(5.5 * mm, 5.0 * mm, 9.0 * mm, 4.0 * mm, 11.0 * mm, 6.5 * mm)
    c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(GREEN)
    c.setLineWidth(0.8)
    c.line(3.9 * mm, 9.0 * mm, 3.0 * mm, 11.0 * mm)


def draw_garam(c):
    c.setFillColor(GOLD)
    for x, y, r in [(5.0, 7.0, 1.0), (8.0, 6.0, .8), (10.5, 8.3, .9), (7.0, 10.0, .75), (10.0, 11.0, .55)]:
        c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(VIOLET)
    c.setLineWidth(0.5)
    c.arc(3.2 * mm, 4.3 * mm, 12.2 * mm, 10.0 * mm, 190, 160)


def draw_coriander(c):
    c.setStrokeColor(GREEN)
    c.setLineWidth(0.55)
    c.line(7.2 * mm, 4.2 * mm, 7.2 * mm, 12.2 * mm)
    c.setFillColor(GREEN)
    for x, y, rx, ry in [(4.8, 8.3, 2.0, 1.1), (9.4, 10.3, 2.1, 1.15), (5.2, 12.0, 1.7, 1.0)]:
        c.ellipse((x-rx)*mm, (y-ry)*mm, (x+rx)*mm, (y+ry)*mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    for x, y in [(4.0, 5.0), (9.8, 5.3), (11.2, 7.0)]:
        c.circle(x * mm, y * mm, .55 * mm, stroke=0, fill=1)


def draw_cumin(c):
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.setLineCap(1)
    for x, y, dx, dy in [(4.2, 6.0, 2.2, 3.5), (7.0, 8.0, 2.8, 2.0), (9.0, 5.0, 2.4, 3.2), (5.2, 11.0, 2.2, 1.4)]:
        c.line(x * mm, y * mm, (x + dx) * mm, (y + dy) * mm)


def draw_pepper(c):
    c.setFillColor(HexColor("#B9AEC9"))
    for x, y, r in [(4.7, 6.3, 1.1), (7.8, 5.3, .85), (10.4, 7.3, 1.0), (6.0, 9.6, .8), (9.0, 11.0, .95)]:
        c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.45)
    c.line(8.9 * mm, 12.0 * mm, 10.5 * mm, 14.0 * mm)


def draw_mustard(c):
    c.setFillColor(HexColor("#655B72"))
    for x, y, r in [(4.4, 6.0, 1.0), (7.3, 5.0, .85), (10.2, 6.6, .95), (5.4, 9.5, .8), (8.4, 10.5, 1.0), (11.0, 11.7, .7)]:
        c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)


def draw_sesame(c):
    c.setFillColor(HexColor("#E8D6A3"))
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.25)
    for x, y, rx, ry, angle in [
        (4.5, 6.0, 1.25, .55, 24),
        (7.7, 5.2, 1.15, .5, -18),
        (10.5, 7.0, 1.3, .55, 35),
        (5.8, 9.5, 1.1, .5, -32),
        (9.1, 10.7, 1.25, .55, 14),
        (11.1, 12.4, 1.05, .48, -20),
    ]:
        c.saveState()
        c.translate(x * mm, y * mm)
        c.rotate(angle)
        c.ellipse(-rx * mm, -ry * mm, rx * mm, ry * mm, stroke=1, fill=1)
        c.restoreState()


def draw_brown_sugar(c):
    c.setFillColor(HexColor("#B97845"))
    c.setStrokeColor(HexColor("#E2B376"))
    c.setLineWidth(0.25)
    for x, y, size, angle in [
        (4.7, 6.0, 1.5, 12),
        (7.8, 5.2, 1.35, -18),
        (10.5, 6.8, 1.45, 24),
        (5.8, 9.4, 1.25, -28),
        (8.9, 10.5, 1.55, 8),
        (11.2, 12.2, 1.1, -12),
    ]:
        c.saveState()
        c.translate(x * mm, y * mm)
        c.rotate(angle)
        c.rect(-size * .5 * mm, -size * .5 * mm, size * mm, size * mm, stroke=1, fill=1)
        c.restoreState()


def draw_yellow_chilli(c):
    c.setStrokeColor(HexColor("#E7C84B"))
    c.setLineWidth(1.7)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(4.0 * mm, 9.2 * mm)
    p.curveTo(5.4 * mm, 5.2 * mm, 9.1 * mm, 4.0 * mm, 11.2 * mm, 6.4 * mm)
    c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(GREEN)
    c.setLineWidth(0.8)
    c.line(3.9 * mm, 9.2 * mm, 3.0 * mm, 11.2 * mm)


def build_one(filename, lines, sizes, icon):
    output = OUTPUT_DIR / filename
    c = canvas.Canvas(
        str(output), pagesize=(PAGE_W, PAGE_H), pageCompression=1,
        initialFontName="LabelElegant", initialFontSize=10,
    )
    c.setTitle(" - ".join(lines) + " - Spice Jar Label")
    c.setAuthor("Custom refill label")
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")

    icon(c)
    centre_x = 24.5 * mm
    if len(lines) == 1:
        draw_shadowed_centred(
            c, centre_x, 10.8 * mm, lines[0],
            "LabelMagic", sizes[0], CREAM, offset_mm=0.32,
        )
    else:
        draw_shadowed_centred(
            c, centre_x, 14.0 * mm, lines[0],
            "LabelMagic", sizes[0], CREAM, offset_mm=0.3,
        )
        draw_shadowed_centred(
            c, centre_x, 7.7 * mm, lines[1],
            "LabelMagic", sizes[1], CREAM, offset_mm=0.3,
        )

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.75)
    c.setLineCap(1)
    c.line(15.5 * mm, 5.0 * mm, 33.5 * mm, 5.0 * mm)
    c.showPage()
    c.save()

    reader = PdfReader(str(output))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({"/Title": " - ".join(lines) + " - Spice Jar Label - 38 x 30 mm"})
    cleaned = output.with_suffix(".cleaned.pdf")
    with cleaned.open("wb") as handle:
        writer.write(handle)
    cleaned.replace(output)


def build():
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_one("spice-jar-hot-chilli-magical-38x30mm.pdf", ["Hot Chilli"], [17.5], draw_chilli)
    build_one("spice-jar-garam-masala-magical-38x30mm.pdf", ["Garam Masala"], [15.5], draw_garam)
    build_one("spice-jar-ground-coriander-magical-38x30mm.pdf", ["Ground", "Coriander"], [15.0, 15.0], draw_coriander)
    build_one("spice-jar-cumin-seeds-magical-38x30mm.pdf", ["Cumin Seeds"], [16.5], draw_cumin)
    build_one("spice-jar-ground-black-pepper-magical-38x30mm.pdf", ["Ground Black", "Pepper"], [13.5, 16.0], draw_pepper)
    build_one("spice-jar-black-mustard-seeds-magical-38x30mm.pdf", ["Black Mustard", "Seeds"], [13.5, 16.0], draw_mustard)
    build_one("spice-jar-sesame-seeds-magical-38x30mm.pdf", ["Sesame Seeds"], [16.0], draw_sesame)
    build_one("spice-jar-soft-brown-sugar-magical-38x30mm.pdf", ["Soft Brown", "Sugar"], [14.5, 17.0], draw_brown_sugar)
    build_one("spice-jar-amazon-yellow-chillies-magical-38x30mm.pdf", ["Amazon Yellow", "Chillies"], [13.5, 16.0], draw_yellow_chilli)


if __name__ == "__main__":
    build()
