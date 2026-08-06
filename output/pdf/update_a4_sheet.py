<!-- ... existing code ... -->
OUTPUT = PDF_DIR / "new-labels-plus-tapered-cleaner-a4-one-each.pdf"

# Added a 6th value to each tuple to control rotation!
LABELS = [
    ("pantry-plain-flour-130x160mm.pdf", 130, 160, 5, 134, 0),
    ("pantry-rolled-oats-130x160mm.pdf", 130, 160, 5, 2, 90), # Rotated 90 degrees to fit!
    ("pantry-cornflour-icing-sugar-70x60mm.pdf", 70, 60, 138, 230, 0),
    ("ecover-all-purpose-cleaner-tapered-spray-bottle-44x70mm.pdf", 44, 70, 150, 145, 0),
    ("spice-jar-mild-caribbean-curry-powder-magical-50x40mm.pdf", 50, 40, 168, 80, 90), # Rotated 90 degrees to nest beside the oats!
    ("spice-jar-soft-brown-sugar-magical-38x30mm.pdf", 38, 30, 169, 45, 0),
    ("spice-jar-sesame-seeds-magical-38x30mm.pdf", 38, 30, 169, 10, 0),
]


def build():
    writer = PdfWriter()
    sheet = writer.add_blank_page(width=A4[0], height=A4[1])

    for filename, width_mm, height_mm, x_mm, y_mm, rotation_deg in LABELS:
        source = PdfReader(str(PDF_DIR / filename)).pages[0]
        
        # If the label is rotated 90 degrees, we adjust the pivot mathematically 
        # so it is placed cleanly from the bottom-left coordinate requested.
        if rotation_deg == 90:
            tx = (x_mm + height_mm) * mm
            ty = y_mm * mm
            transform = Transformation().rotate(90).translate(tx=tx, ty=ty)
        else:
            transform = Transformation().translate(tx=x_mm * mm, ty=y_mm * mm)

        sheet.merge_transformed_page(
            source,
            transform,
            over=True,
        )

    writer.add_metadata({
<!-- ... existing code ... -->