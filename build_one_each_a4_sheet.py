from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "output" / "pdf"
OUTPUT = PDF_DIR / "complete-refill-label-set-a4-one-of-each-updated.pdf"

LABELS = [
    ("spice-jar-hot-chilli-magical-38x30mm.pdf", 38, 30, 17, 263),
    ("spice-jar-garam-masala-magical-38x30mm.pdf", 38, 30, 64, 263),
    ("spice-jar-ground-coriander-magical-38x30mm.pdf", 38, 30, 111, 263),
    ("spice-jar-amazon-yellow-chillies-magical-38x30mm.pdf", 38, 30, 158, 263),
    ("spice-jar-cumin-seeds-magical-38x30mm.pdf", 38, 30, 17, 229),
    ("spice-jar-ground-black-pepper-magical-38x30mm.pdf", 38, 30, 64, 229),
    ("spice-jar-black-mustard-seeds-magical-38x30mm.pdf", 38, 30, 111, 229),
    ("spice-jar-sesame-seeds-magical-38x30mm.pdf", 38, 30, 158, 229),
    ("miniml-laundry-liquid-tropical-coconut-magical-80x110mm.pdf", 80, 110, 7, 111),
    ("ecover-all-purpose-cleaner-lemongrass-ginger-magical-60x85mm.pdf", 60, 85, 93, 136),
    ("ecover-all-purpose-cleaner-tapered-spray-bottle-44x70mm.pdf", 44, 70, 159, 151),
    ("ecover-washing-up-liquid-lemongrass-ginger-magical-55x70mm.pdf", 55, 70, 46, 33),
    ("plant-mister-water-only-magical-55x70mm.pdf", 55, 70, 109, 33),
    ("spice-jar-mild-caribbean-curry-powder-magical-50x40mm.pdf", 50, 40, 157, 107),
    ("spice-jar-soft-brown-sugar-magical-38x30mm.pdf", 38, 30, 168, 70),
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
        "/Title": "Complete Refill Label Set - One of Each - A4",
        "/Author": "Custom refill labels",
    })
    with OUTPUT.open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    build()
