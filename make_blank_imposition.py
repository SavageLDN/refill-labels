from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter, Transformation

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR = ROOT / "tmp" / "pdfs" / "assets"

TEMPLATES_DIR = ROOT / "output" / "pdf" / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

A4_W = 210 * mm
A4_H = 297 * mm

GOLD = HexColor("#D9B65D")
DARK_SCRIM = HexColor("#050814")

def draw_blank_backdrop(c, w, h):
    backdrop_path = ASSETS_DIR / "wanaka-night-sky-80x110.png"
    if backdrop_path.exists():
        try:
            img = Image.open(str(backdrop_path))
            iw, ih = img.size
            scale = max(float(w) / float(iw), float(h) / float(ih))
            draw_w, draw_h = iw * scale, ih * scale
            x_off = (float(w) - draw_w) / 2.0
            y_off = (float(h) - draw_h) / 2.0
            c.drawImage(ImageReader(str(backdrop_path)), x_off, y_off, width=draw_w, height=draw_h, mask="auto")
            c.setFillColor(DARK_SCRIM)
            c.setFillAlpha(0.25)
            c.rect(0, 0, w, h, stroke=0, fill=1)
            c.setFillAlpha(1.0)
        except Exception:
            pass

def generate_blank_label(filename, w, h, border_margin=3*mm, corner_radius=2*mm):
    out_path = TEMPLATES_DIR / filename
    c = canvas.Canvas(str(out_path), pagesize=(w, h))
    c.setTitle(f"Blank Template ({int(w/mm)}x{int(h/mm)}mm)")
    
    # Celestial Backdrop
    draw_blank_backdrop(c, w, h)
    
    # Outer Gold Label Border
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(border_margin, border_margin, w - 2*border_margin, h - 2*border_margin, corner_radius, stroke=1, fill=0)
    
    c.showPage()
    c.save()
    return out_path

def build_blank_master_a4(t1, t2, t3, t4, t5, t6, t7):
    out_path = TEMPLATES_DIR / "blank-templates-all-7-labels-a4-sheet.pdf"
    writer = PdfWriter()
    sheet = writer.add_blank_page(width=A4_W, height=A4_H)

    # Row 1 (Top): Two 80x60mm Blank Labels
    r1_y = A4_H - 12 * mm - 60 * mm
    t2_x = 18 * mm
    t3_x = 18 * mm + 80 * mm + 14 * mm
    sheet.merge_transformed_page(PdfReader(str(t2)).pages[0], Transformation().translate(tx=t2_x, ty=r1_y), over=True)
    sheet.merge_transformed_page(PdfReader(str(t3)).pages[0], Transformation().translate(tx=t3_x, ty=r1_y), over=True)

    # Row 2 (Middle): Two 60x80mm Vertical Labels + 1 Rotated 70x40mm Label
    r2_y = r1_y - 12 * mm - 80 * mm
    t4_x = 14 * mm
    t5_x = t4_x + 60 * mm + 10 * mm
    t1_rot_x = t5_x + 60 * mm + 12 * mm
    t1_rot_y = r2_y + 5 * mm

    sheet.merge_transformed_page(PdfReader(str(t4)).pages[0], Transformation().translate(tx=t4_x, ty=r2_y), over=True)
    sheet.merge_transformed_page(PdfReader(str(t5)).pages[0], Transformation().translate(tx=t5_x, ty=r2_y), over=True)

    p1 = PdfReader(str(t1)).pages[0]
    sheet.merge_transformed_page(p1, Transformation().rotate(90).translate(tx=t1_rot_x + 40 * mm, ty=t1_rot_y), over=True)

    # Row 3 (Bottom): One 80x110mm Label + One 100x70mm Label (both rotated for A4 fit)
    t7_rot_x = 12 * mm
    t7_rot_y = 12 * mm
    p7 = PdfReader(str(t7)).pages[0]
    sheet.merge_transformed_page(p7, Transformation().rotate(90).translate(tx=t7_rot_x + 110 * mm, ty=t7_rot_y), over=True)

    t6_rot_x = t7_rot_x + 110 * mm + 10 * mm
    t6_rot_y = 12 * mm
    p6 = PdfReader(str(t6)).pages[0]
    sheet.merge_transformed_page(p6, Transformation().rotate(90).translate(tx=t6_rot_x + 70 * mm, ty=t6_rot_y), over=True)

    with out_path.open("wb") as handle:
        writer.write(handle)
    print(f"Generated: {out_path}")

def run():
    t1 = generate_blank_label("blank-template-70x40mm.pdf", 70*mm, 40*mm, border_margin=2.5*mm, corner_radius=1.5*mm)
    t2 = generate_blank_label("blank-template-80x60mm-a.pdf", 80*mm, 60*mm)
    t3 = generate_blank_label("blank-template-80x60mm-b.pdf", 80*mm, 60*mm)
    t4 = generate_blank_label("blank-template-60x80mm-a.pdf", 60*mm, 80*mm)
    t5 = generate_blank_label("blank-template-60x80mm-b.pdf", 60*mm, 80*mm)
    t6 = generate_blank_label("blank-template-100x70mm.pdf", 100*mm, 70*mm)
    t7 = generate_blank_label("blank-template-80x110mm.pdf", 80*mm, 110*mm)
    
    build_blank_master_a4(t1, t2, t3, t4, t5, t6, t7)

if __name__ == "__main__":
    run()
