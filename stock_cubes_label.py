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
OUTPUT = OUTPUT_DIR / "pantry-stock-cubes-magical-70x100mm.pdf"

# Reusing a larger background asset which will be scaled to fit
BACKGROUND = ROOT / "tmp" / "pdfs" / "assets" / "wanaka-night-sky-80x110.png"

# 7 cm x 10 cm
PAGE_W = 70 * mm
PAGE_H = 100 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")

def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))

def build():
    register_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(
        str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1,
        initialFontName="LabelElegant", initialFontSize=10,
    )
    c.setTitle("Stock Cubes - Pantry Label")
    c.setAuthor("Custom refill label")

    # Draw scaled background
    c.drawImage(ImageReader(str(BACKGROUND)), 0, 0, width=PAGE_W, height=PAGE_H, mask="auto")

    # Draw magical border frame
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.roundRect(4 * mm, 4 * mm, PAGE_W - 8 * mm, PAGE_H - 8 * mm, 3 * mm, stroke=1, fill=0)

    # Draw much larger text for cupboard visibility
    centre_x = PAGE_W / 2
    draw_shadowed_centred(
        c, centre_x, 56.0 * mm, "Stock",
        "LabelMagic", 55.0, CREAM, offset_mm=0.6,
    )
    draw_shadowed_centred(
        c, centre_x, 37.0 * mm, "Cubes",
        "LabelMagic", 55.0, CREAM, offset_mm=0.6,
    )

    # Draw decorative dividing line
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.setLineCap(1)
    c.line(20 * mm, 22.0 * mm, PAGE_W - 20 * mm, 22.0 * mm)

    c.showPage()
    c.save()

    # Preserve only necessary metadata and clean up
    reader = PdfReader(str(OUTPUT))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        "/Title": "Stock Cubes - Pantry Label - 70 x 100 mm",
        "/Author": "Custom refill label",
    })
    cleaned = OUTPUT.with_suffix(".cleaned.pdf")
    with cleaned.open("wb") as handle:
        writer.write(handle)
    cleaned.replace(OUTPUT)

if __name__ == "__main__":
    build()