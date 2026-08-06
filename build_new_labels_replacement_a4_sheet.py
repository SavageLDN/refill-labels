from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "output" / "pdf"
OUTPUT = PDF_DIR / "new-labels-plus-tapered-cleaner-a4-one-each.pdf"

LABELS = [
    ("ecover-all-purpose-cleaner-tapered-spray-bottle-44x70mm.pdf", 44, 70, 18, 205),
    ("spice-jar-mild-caribbean-curry-powder-magical-50x40mm.pdf", 50, 40, 76, 235),
    ("spice-jar-sesame-seeds-magical-38x30mm.pdf", 38, 30, 140, 245),
    ("spice-jar-soft-brown-sugar-magical-38x30mm.pdf", 38, 30, 140, 205),
]


def build():
    writer = PdfWriter()
    sheet = writer.add_blank_page(width=A4[0], height=A4[1])

    for filename, width_mm, height_mm, x_mm, y_mm in LABELS:
        source = PdfReader(str(PDF_DIR / filename)).pages[0]
        sheet.merge_transformed_page(
            source,
            Transformation().translate(tx=x_mm * mm, ty=y_mm * mm),
            over=True,
        )

    writer.add_metadata({
        "/Title": "New Labels Plus Tapered Cleaner - One of Each - A4",
        "/Author": "Custom refill labels",
    })
    with OUTPUT.open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    build()
