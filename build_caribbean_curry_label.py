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
OUTPUT = OUTPUT_DIR / "spice-jar-mild-caribbean-curry-powder-magical-50x40mm.pdf"
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-spice-38x30.png"

PAGE_W = 50 * mm
PAGE_H = 40 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
GREEN = HexColor("#76A779")
TURMERIC = HexColor("#E2A93B")
CHILLI = HexColor("#C94E52")
NIGHT = HexColor("#050712")

INGREDIENT_LINES = [
    "INGREDIENTS: Ground coriander, ground turmeric,",
    "ground fenugreek, ground chilli, ground black pepper,",
    "ground cumin, ground ginger, ground dill seed, potassium iodate.",
]


def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))


def draw_spice_bowl(c):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.65)
    c.setFillColor(TURMERIC)
    c.wedge(3.5 * mm, 17.0 * mm, 15.0 * mm, 27.0 * mm, 180, 180, stroke=1, fill=1)
    c.setFillColor(CHILLI)
    c.circle(6.0 * mm, 27.0 * mm, 0.7 * mm, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.ellipse(9.0 * mm, 25.8 * mm, 13.2 * mm, 27.6 * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.55)
    c.line(11.5 * mm, 26.5 * mm, 15.0 * mm, 30.2 * mm)
    c.restoreState()


def build():
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(
        str(OUTPUT),
        pagesize=(PAGE_W, PAGE_H),
        pageCompression=1,
        initialFontName="LabelElegant",
        initialFontSize=8,
    )
    c.setTitle("Mild Caribbean Style Curry Powder - Spice Jar Label")
    c.setAuthor("Custom refill label")
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")

    draw_spice_bowl(c)

    title_x = 31.0 * mm
    draw_shadowed_centred(
        c, title_x, 29.0 * mm, "Mild Caribbean",
        "LabelMagic", 17.0, CREAM, offset_mm=0.32,
    )
    draw_shadowed_centred(
        c, title_x, 22.7 * mm, "Style Curry",
        "LabelMagic", 17.0, CREAM, offset_mm=0.32,
    )
    draw_shadowed_centred(
        c, title_x, 16.4 * mm, "Powder",
        "LabelMagic", 18.0, CREAM, offset_mm=0.32,
    )

    c.saveState()
    c.setFillColor(NIGHT)
    c.setFillAlpha(0.78)
    c.roundRect(2.0 * mm, 2.0 * mm, 46.0 * mm, 10.8 * mm, 1.4 * mm, stroke=0, fill=1)
    c.restoreState()

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.55)
    c.line(4.0 * mm, 11.3 * mm, 46.0 * mm, 11.3 * mm)

    c.setFont("LabelElegant", 4.8)
    c.setFillColor(CREAM)
    for y_mm, text in zip((8.8, 6.2, 3.6), INGREDIENT_LINES):
        c.drawCentredString(25.0 * mm, y_mm * mm, text)

    c.showPage()
    c.save()

    reader = PdfReader(str(OUTPUT))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        "/Title": "Mild Caribbean Style Curry Powder - Spice Jar Label - 50 x 40 mm",
        "/Author": "Custom refill label",
    })
    cleaned = OUTPUT.with_suffix(".cleaned.pdf")
    with cleaned.open("wb") as handle:
        writer.write(handle)
    cleaned.replace(OUTPUT)


if __name__ == "__main__":
    build()
