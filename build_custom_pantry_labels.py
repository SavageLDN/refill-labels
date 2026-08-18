from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter, Transformation

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR = ROOT / "tmp" / "pdfs" / "assets"

OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

A4_W = 210 * mm
A4_H = 297 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
SHADOW = HexColor("#000000")
VIOLET = HexColor("#9B7ACB")
DARK_SCRIM = HexColor("#050814")
SAGE = HexColor("#11162E")

def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
        pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))
        pdfmetrics.registerFont(TTFont("LabelSans", r"C:\Windows\Fonts\gadugi.ttf"))
    except Exception:
        pass

def draw_clean_shadow_text(c, x, y, text, font_name, font_size, fill_colour, offset_mm=0.22):
    c.saveState()
    c.setFont(font_name, font_size)
    c.setFillColor(SHADOW)
    c.drawCentredString(x + offset_mm * mm, y - offset_mm * mm, text)
    c.setFillColor(fill_colour)
    c.drawCentredString(x, y, text)
    c.restoreState()

def select_best_backdrop_for_size(w, h):
    candidates = []
    for p in ASSETS_DIR.glob("*wanaka*.png"):
        try:
            with Image.open(p) as im:
                iw, ih = im.size
            aspect = float(iw) / float(ih)
            candidates.append((p, aspect, iw, ih))
        except Exception:
            continue
    if not candidates:
        return None
    target_aspect = float(w) / float(h)
    return min(candidates, key=lambda x: abs(x[1] - target_aspect))[0]

def draw_cover_backdrop(c, w, h, darken=False):
    chosen = select_best_backdrop_for_size(w, h)
    if chosen is None:
        chosen = ASSETS_DIR / "wanaka-night-sky-80x110.png"
    try:
        img = Image.open(str(chosen))
        iw, ih = img.size
        scale = max(float(w) / float(iw), float(h) / float(ih))
        draw_w, draw_h = iw * scale, ih * scale
        x_off = (float(w) - draw_w) / 2.0
        y_off = (float(h) - draw_h) / 2.0
        c.drawImage(ImageReader(str(chosen)), x_off, y_off, width=draw_w, height=draw_h, mask="auto")
        
        if darken:
            c.saveState()
            c.setFillColor(DARK_SCRIM)
            c.setFillAlpha(0.25)
            c.rect(0, 0, w, h, stroke=0, fill=1)
            c.restoreState()
    except Exception:
        pass

# --- Custom Vector Artworks ---

def draw_baking_art(c, x=7*mm, y=5*mm):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.setLineCap(1)
    c.line(0, 0, 3*mm, 8*mm)
    c.line(3*mm, 0, 3*mm, 9*mm)
    c.line(6*mm, 0, 3*mm, 8*mm)
    c.setFillColor(CREAM)
    for px, py in [(1.8, 5), (4.2, 5), (2.2, 7), (3.8, 7), (3, 9)]:
        c.circle(px*mm, py*mm, 0.45*mm, stroke=0, fill=1)
    c.restoreState()

def draw_flavour_pod_art(c, x=6*mm, y=5*mm):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(CREAM)
    c.setLineWidth(0.6)
    p = c.beginPath()
    p.moveTo(0, 2*mm)
    p.curveTo(3*mm, 6*mm, 6*mm, 8*mm, 9*mm, 9*mm)
    c.drawPath(p, stroke=1, fill=0)
    p2 = c.beginPath()
    p2.moveTo(2*mm, 0)
    p2.curveTo(5*mm, 3*mm, 7*mm, 6*mm, 11*mm, 7*mm)
    c.drawPath(p2, stroke=1, fill=0)
    c.setFillColor(GOLD)
    c.circle(2*mm, 6*mm, 0.5*mm, stroke=0, fill=1)
    c.restoreState()

def draw_spice_seeds_art(c, x=6*mm, y=5*mm):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.55)
    c.line(0, 2*mm, 8*mm, 7*mm)
    c.setFillColor(CREAM)
    for px, py in [(1.5, 4.5), (3.5, 3), (5, 6.5), (7, 5), (9, 7.5)]:
        c.circle(px*mm, py*mm, 0.65*mm, stroke=0, fill=1)
    c.restoreState()

def draw_oats_art(c, x=8*mm, y=7*mm):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(2*mm, 5*mm, 4*mm, 11*mm, 8*mm, 15*mm)
    c.drawPath(p, stroke=1, fill=0)
    c.setFillColor(CREAM)
    for gx, gy, rx, ry, ang in [(2.2, 6, 1.2, 0.6, 25), (3.8, 10, 1.2, 0.6, 35), (6.5, 13.5, 1.1, 0.55, 45), (8.2, 15.2, 1.0, 0.5, 50)]:
        c.saveState()
        c.translate(gx*mm, gy*mm)
        c.rotate(ang)
        c.ellipse(-rx*mm, -ry*mm, rx*mm, ry*mm, stroke=0, fill=1)
        c.restoreState()
    c.restoreState()

def draw_wheat_flour_art(c, x=8*mm, y=7*mm):
    c.saveState()
    c.translate(x, y)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.65)
    c.setLineCap(1)
    c.line(4*mm, 0, 4*mm, 15*mm)
    c.setFillColor(CREAM)
    for wy in [5, 7.5, 10, 12.5]:
        c.ellipse((4 - 1.8)*mm, (wy - 0.7)*mm, (4)*mm, (wy + 0.7)*mm, stroke=0, fill=1)
        c.ellipse((4)*mm, (wy - 0.7)*mm, (4 + 1.8)*mm, (wy + 0.7)*mm, stroke=0, fill=1)
    c.ellipse(3.2*mm, 14.2*mm, 4.8*mm, 16.2*mm, stroke=0, fill=1)
    c.restoreState()

def draw_detailed_stock_trio(c, x=24*mm, y=4*mm):
    """Accurate vector illustrations of an actual Chicken, Cow, and Carrot."""
    c.saveState()
    c.translate(x, y)

    # --- 1. DETAILED CHICKEN (Gold & Cream) ---
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setFillColor(CREAM)
    c.setLineWidth(0.55)
    c.setLineJoin(1)
    
    # Body & Tail Path
    p_chk = c.beginPath()
    p_chk.moveTo(0, 6.5*mm) # Tail tip
    p_chk.curveTo(2*mm, 8.5*mm, 4*mm, 7.5*mm, 5.5*mm, 5.5*mm) # Back
    p_chk.curveTo(6*mm, 8*mm, 7*mm, 10*mm, 8*mm, 10*mm) # Neck up to head
    p_chk.lineTo(9.5*mm, 9.5*mm) # Beak tip
    p_chk.lineTo(8.2*mm, 8.5*mm) # Chin
    p_chk.curveTo(9.5*mm, 6.5*mm, 9*mm, 3.5*mm, 6.5*mm, 2.5*mm) # Plump Breast
    p_chk.curveTo(4*mm, 2*mm, 2*mm, 3.5*mm, 0.5*mm, 5.5*mm) # Underbelly
    p_chk.close()
    c.drawPath(p_chk, stroke=1, fill=1)
    
    # Comb & Wattle (Gold)
    c.setFillColor(GOLD)
    c.circle(7.8*mm, 10.5*mm, 0.65*mm, stroke=0, fill=1)
    c.circle(8.5*mm, 10.3*mm, 0.55*mm, stroke=0, fill=1)
    c.circle(8.0*mm, 8.2*mm, 0.45*mm, stroke=0, fill=1)
    
    # Eye
    c.setFillColor(SHADOW)
    c.circle(7.8*mm, 9.2*mm, 0.3*mm, stroke=0, fill=1)
    
    # Wing detail
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    p_w = c.beginPath()
    p_w.moveTo(4.5*mm, 5.5*mm)
    p_w.curveTo(3*mm, 5.5*mm, 2*mm, 4.5*mm, 3.5*mm, 3.5*mm)
    c.drawPath(p_w, stroke=1, fill=0)
    
    # Legs & Feet
    c.line(4.5*mm, 2.5*mm, 4.2*mm, 0)
    c.line(4.2*mm, 0, 5.5*mm, 0)
    c.line(6.0*mm, 2.5*mm, 5.8*mm, 0)
    c.line(5.8*mm, 0, 7.0*mm, 0)
    c.restoreState()

    # --- 2. DETAILED COW (Cream & Gold) ---
    c.saveState()
    c.translate(16*mm, 0)
    c.setStrokeColor(GOLD)
    c.setFillColor(CREAM)
    c.setLineWidth(0.55)
    c.setLineJoin(1)
    
    # Full Cow Body Profile
    p_cow = c.beginPath()
    p_cow.moveTo(0, 8.5*mm) # Rump/Tailhead
    p_cow.curveTo(4*mm, 9.0*mm, 10*mm, 8.8*mm, 13*mm, 9.5*mm) # Backline & Withers
    p_cow.lineTo(14.5*mm, 11*mm) # Neck up to Poll
    p_cow.lineTo(17.5*mm, 9.5*mm) # Face to Muzzle
    p_cow.lineTo(16.5*mm, 8.0*mm) # Chin
    p_cow.curveTo(15*mm, 7.5*mm, 14*mm, 6.0*mm, 13*mm, 5.0*mm) # Dewlap & Chest
    # Front Leg
    p_cow.lineTo(12.5*mm, 0)
    p_cow.lineTo(11.0*mm, 0)
    p_cow.lineTo(11.5*mm, 4.5*mm)
    # Underbelly & Udder
    p_cow.curveTo(9*mm, 4.2*mm, 6*mm, 4.0*mm, 4*mm, 3.8*mm)
    # Back Leg
    p_cow.lineTo(3.5*mm, 0)
    p_cow.lineTo(2.0*mm, 0)
    p_cow.lineTo(1.8*mm, 5.5*mm)
    p_cow.curveTo(0.5*mm, 6.5*mm, 0, 7.5*mm, 0, 8.5*mm) # Flank
    p_cow.close()
    c.drawPath(p_cow, stroke=1, fill=1)
    
    # Horns & Ears
    c.setFillColor(GOLD)
    p_horn = c.beginPath()
    p_horn.moveTo(14.5*mm, 11*mm)
    p_horn.curveTo(14.8*mm, 12.5*mm, 16.0*mm, 12.2*mm, 15.5*mm, 10.8*mm)
    c.drawPath(p_horn, stroke=0, fill=1)
    c.circle(13.8*mm, 9.8*mm, 0.65*mm, stroke=0, fill=1) # Ear
    
    # Eye & Muzzle
    c.setFillColor(SHADOW)
    c.circle(15.8*mm, 9.2*mm, 0.3*mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.circle(17.0*mm, 8.8*mm, 0.35*mm, stroke=0, fill=1) # Nose
    
    # Arched Tail
    c.setStrokeColor(GOLD)
    p_tail = c.beginPath()
    p_tail.moveTo(0, 8.5*mm)
    p_tail.curveTo(-1.5*mm, 6.5*mm, -1.0*mm, 3.5*mm, -0.5*mm, 2.0*mm)
    c.drawPath(p_tail, stroke=1, fill=0)
    # Tail Tuft
    c.setFillColor(GOLD)
    c.circle(-0.5*mm, 1.8*mm, 0.5*mm, stroke=0, fill=1)
    c.restoreState()

    # --- 3. DETAILED CARROT (Gold & Cream) ---
    c.saveState()
    c.translate(39*mm, 0)
    c.setStrokeColor(GOLD)
    c.setFillColor(CREAM)
    c.setLineWidth(0.55)
    c.setLineJoin(1)
    
    # Tapered Carrot Root Path
    p_crt = c.beginPath()
    p_crt.moveTo(1*mm, 7.5*mm) # Left shoulder
    p_crt.curveTo(3*mm, 8.0*mm, 5*mm, 8.0*mm, 7*mm, 7.5*mm) # Rounded crown
    p_crt.curveTo(6*mm, 4.5*mm, 4.5*mm, 1.5*mm, 4*mm, 0) # Taper to tip
    p_crt.curveTo(3.5*mm, 1.5*mm, 2*mm, 4.5*mm, 1*mm, 7.5*mm)
    p_crt.close()
    c.drawPath(p_crt, stroke=1, fill=1)
    
    # Horizontal Texture Ridges
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.45)
    c.line(2.2*mm, 6.0*mm, 5.8*mm, 6.0*mm)
    c.line(2.8*mm, 4.2*mm, 5.2*mm, 4.2*mm)
    c.line(3.3*mm, 2.5*mm, 4.7*mm, 2.5*mm)
    
    # Feathery Carrot Greens (Top)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    # Central stem
    c.line(4*mm, 7.8*mm, 4*mm, 12.0*mm)
    c.line(4*mm, 9.5*mm, 2.5*mm, 11.0*mm)
    c.line(4*mm, 10.5*mm, 5.5*mm, 11.5*mm)
    # Left stem
    p_l = c.beginPath()
    p_l.moveTo(3*mm, 7.8*mm)
    p_l.curveTo(2*mm, 9.5*mm, 1.5*mm, 10.5*mm, 1*mm, 11.5*mm)
    c.drawPath(p_l, stroke=1, fill=0)
    c.line(2*mm, 9.5*mm, 0.5*mm, 9.8*mm)
    # Right stem
    p_r = c.beginPath()
    p_r.moveTo(5*mm, 7.8*mm)
    p_r.curveTo(6*mm, 9.5*mm, 6.5*mm, 10.5*mm, 7*mm, 11.5*mm)
    c.drawPath(p_r, stroke=1, fill=0)
    c.line(6*mm, 9.5*mm, 7.5*mm, 9.8*mm)
    
    c.restoreState()

    c.restoreState()

def draw_toilet_and_mint_art(c, x=8*mm, y=10*mm):
    c.saveState()
    c.translate(x, y)
    
    c.setStrokeColor(GOLD)
    c.setFillColor(CREAM)
    c.setLineWidth(0.65)
    
    c.roundRect(0, 7.5*mm, 7*mm, 8.5*mm, 1.0*mm, stroke=1, fill=1)
    c.roundRect(-0.5*mm, 15.5*mm, 8*mm, 1.5*mm, 0.5*mm, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.circle(3.5*mm, 16.2*mm, 0.45*mm, stroke=0, fill=1)
    
    c.setFillColor(CREAM)
    p_bowl = c.beginPath()
    p_bowl.moveTo(6.5*mm, 10.0*mm)
    p_bowl.lineTo(13.5*mm, 10.0*mm)
    p_bowl.curveTo(13.5*mm, 4.5*mm, 10.0*mm, 3.0*mm, 7.5*mm, 3.0*mm)
    p_bowl.lineTo(7.5*mm, 0)
    p_bowl.lineTo(2.0*mm, 0)
    p_bowl.lineTo(2.0*mm, 3.0*mm)
    p_bowl.lineTo(6.5*mm, 3.0*mm)
    p_bowl.close()
    c.drawPath(p_bowl, stroke=1, fill=1)
    
    c.setStrokeColor(GOLD)
    c.line(6.0*mm, 10.5*mm, 14.0*mm, 10.5*mm)
    
    c.translate(12.5*mm, 2.0*mm)
    c.setStrokeColor(GOLD)
    c.setFillColor(CREAM)
    c.setLineWidth(0.6)
    
    p_m1 = c.beginPath()
    p_m1.moveTo(0, 3*mm)
    p_m1.curveTo(4*mm, 9*mm, 10*mm, 10*mm, 12*mm, 5*mm)
    p_m1.curveTo(9*mm, 1*mm, 4*mm, 0.5*mm, 0, 3*mm)
    c.drawPath(p_m1, stroke=1, fill=1)
    c.line(0, 3*mm, 10*mm, 6*mm)
    
    p_m2 = c.beginPath()
    p_m2.moveTo(1*mm, 1.5*mm)
    p_m2.curveTo(5*mm, 3.5*mm, 8*mm, 0, 9*mm, -3*mm)
    p_m2.curveTo(5*mm, -4*mm, 2*mm, -2*mm, 1*mm, 1.5*mm)
    c.drawPath(p_m2, stroke=1, fill=1)
    c.line(1*mm, 1.5*mm, 7.5*mm, -1.5*mm)
    
    c.restoreState()

# --- Label Builders ---

def build_label_1():
    w, h = 70 * mm, 40 * mm
    out_file = OUTPUT_DIR / "custom-pantry-cornflour-icing-sugar-70x40mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Cornflour & Icing Sugar Pantry Label")
    
    draw_cover_backdrop(c, w, h, darken=True)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(2.5*mm, 2.5*mm, w - 5*mm, h - 5*mm, 1.5*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 8.5*mm, "Baking Essentials", "LabelElegant", 9.5, GOLD, offset_mm=0.25)
    draw_clean_shadow_text(c, w/2 + 2*mm, 21.5*mm, "Cornflour", "LabelMagic", 18.0, CREAM, offset_mm=0.30)
    draw_clean_shadow_text(c, w/2 + 2*mm, 16.0*mm, "&", "LabelMagic", 13.0, GOLD, offset_mm=0.22)
    draw_clean_shadow_text(c, w/2 + 2*mm, 8.5*mm, "Icing Sugar", "LabelMagic", 18.0, CREAM, offset_mm=0.30)
    
    draw_baking_art(c, x=5.5*mm, y=4.0*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

def build_label_2():
    w, h = 80 * mm, 60 * mm
    out_file = OUTPUT_DIR / "custom-pantry-baking-essentials-80x60mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Baking Essentials & Extracts Pantry Label")
    
    draw_cover_backdrop(c, w, h, darken=True)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 9.0*mm, "Baking & Pantry Essentials", "LabelMagic", 18.5, GOLD, offset_mm=0.30)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(16*mm, h - 12.0*mm, w - 16*mm, h - 12.0*mm)
    
    c.setLineWidth(0.55)
    c.line(w/2, h - 15.5*mm, w/2, 8.0*mm)
    
    col1_x = 24.0 * mm
    col2_x = 56.0 * mm
    
    draw_clean_shadow_text(c, col1_x, 36.0*mm, "Baking Powder", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col2_x, 36.0*mm, "Baking Soda", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col1_x, 23.5*mm, "Vanilla Essence", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col2_x, 25.5*mm, "Chocolate", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col2_x, 19.5*mm, "Powder", "LabelElegant", 10.5, CREAM)
    draw_clean_shadow_text(c, col1_x, 11.0*mm, "Honey", "LabelElegant", 11.0, CREAM)
    
    draw_flavour_pod_art(c, x=5.0*mm, y=5.0*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

def build_label_3():
    w, h = 80 * mm, 60 * mm
    out_file = OUTPUT_DIR / "custom-pantry-spice-selection-80x60mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Whole & Ground Spice Selection Label")
    
    draw_cover_backdrop(c, w, h, darken=True)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 9.0*mm, "Aromatic Spice Selection", "LabelMagic", 18.5, GOLD, offset_mm=0.30)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(16*mm, h - 12.0*mm, w - 16*mm, h - 12.0*mm)
    
    c.setLineWidth(0.55)
    c.line(w/2, h - 15.5*mm, w/2, 17.5*mm)
    
    col1_x = 24.0 * mm
    col2_x = 56.0 * mm
    
    draw_clean_shadow_text(c, col1_x, 36.0*mm, "Coriander Seeds", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col2_x, 36.0*mm, "Cumin Seeds", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col1_x, 23.5*mm, "Chinese 5 Spice", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, col2_x, 23.5*mm, "Ground Ginger", "LabelElegant", 11.0, CREAM)
    draw_clean_shadow_text(c, w/2 + 2*mm, 9.5*mm, "Lemongrass & Lime Leaves", "LabelElegant", 11.0, CREAM)
    
    draw_spice_seeds_art(c, x=5.0*mm, y=4.5*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

def build_label_4():
    w, h = 60 * mm, 80 * mm
    out_file = OUTPUT_DIR / "custom-pantry-rolled-oats-60x80mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Rolled Oats Pantry Label")
    
    draw_cover_backdrop(c, w, h, darken=False)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 11.5*mm, "Pantry Essentials", "LabelElegant", 10.5, GOLD, offset_mm=0.30)
    draw_clean_shadow_text(c, w/2, 48.0*mm, "Rolled", "LabelMagic", 26.0, CREAM, offset_mm=0.45)
    draw_clean_shadow_text(c, w/2, 35.0*mm, "Oats", "LabelMagic", 30.0, CREAM, offset_mm=0.50)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(16*mm, 28.5*mm, w - 16*mm, 28.5*mm)
    
    draw_oats_art(c, x=8*mm, y=6.5*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

def build_label_5():
    w, h = 60 * mm, 80 * mm
    out_file = OUTPUT_DIR / "custom-pantry-plain-flour-60x80mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Plain Flour Pantry Label")
    
    draw_cover_backdrop(c, w, h, darken=False)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 11.5*mm, "Baking Essentials", "LabelElegant", 10.5, GOLD, offset_mm=0.30)
    draw_clean_shadow_text(c, w/2, 48.0*mm, "Plain", "LabelMagic", 26.0, CREAM, offset_mm=0.45)
    draw_clean_shadow_text(c, w/2, 35.0*mm, "Flour", "LabelMagic", 30.0, CREAM, offset_mm=0.50)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(16*mm, 28.5*mm, w - 16*mm, 28.5*mm)
    
    draw_wheat_flour_art(c, x=8*mm, y=6.5*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

# --- Label 6: Stock Cubes (100 x 70 mm) [ACCURATE CHICKEN, COW & CARROT ARTWORK] ---
def build_label_6():
    w, h = 100 * mm, 70 * mm
    out_file = OUTPUT_DIR / "custom-pantry-stock-cubes-100x70mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Stock Cubes Pantry Label")
    
    draw_cover_backdrop(c, w, h, darken=True)
    
    # Outer Gold Frame
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    # Header Subtitle & Title
    draw_clean_shadow_text(c, w/2, h - 9.0*mm, "Pantry Essentials", "LabelElegant", 9.5, GOLD, offset_mm=0.25)
    draw_clean_shadow_text(c, w/2, h - 19.5*mm, "Stock Cubes", "LabelMagic", 25.0, CREAM, offset_mm=0.45)
    
    # Top Divider Line
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(22*mm, h - 23.5*mm, w - 22*mm, h - 23.5*mm)
    
    # 3-Item Product List
    items_y = h - 33.5*mm
    draw_clean_shadow_text(c, 24*mm, items_y, "Chicken", "LabelElegant", 13.0, CREAM, offset_mm=0.35)
    draw_clean_shadow_text(c, 50*mm, items_y, "Beef", "LabelElegant", 13.0, CREAM, offset_mm=0.35)
    draw_clean_shadow_text(c, 77*mm, items_y, "Vegetable", "LabelElegant", 13.0, CREAM, offset_mm=0.35)
    
    # Lower Divider Line
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.55)
    c.line(16*mm, 20.0*mm, w - 16*mm, 20.0*mm)
    
    # Actual Chicken, Cow, and Carrot Vector Artwork
    draw_detailed_stock_trio(c, x=26.5*mm, y=5.0*mm)
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

def build_label_7():
    w, h = 80 * mm, 110 * mm
    out_file = OUTPUT_DIR / "miniml-eco-toilet-cleaner-spearmint-peppermint-80x110mm.pdf"
    c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
    c.setTitle("Miniml Eco Toilet Cleaner - Spearmint & Peppermint")
    
    draw_cover_backdrop(c, w, h, darken=True)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
    
    draw_clean_shadow_text(c, w/2, h - 17.0*mm, "miniml", "LabelSans", 28.0, CREAM, offset_mm=0.35)
    
    draw_clean_shadow_text(c, w/2, 73.0*mm, "Spearmint", "LabelMagic", 25.0, CREAM, offset_mm=0.45)
    draw_clean_shadow_text(c, w/2, 65.5*mm, "&", "LabelMagic", 17.0, GOLD, offset_mm=0.35)
    draw_clean_shadow_text(c, w/2, 57.0*mm, "Peppermint", "LabelMagic", 25.0, CREAM, offset_mm=0.45)
    
    draw_clean_shadow_text(c, w/2, 44.0*mm, "Eco Toilet Cleaner", "LabelElegant", 14.5, CREAM, offset_mm=0.35)
    
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(16 * mm, 37.0 * mm, w - 16 * mm, 37.0 * mm)
    
    draw_toilet_and_mint_art(c, x=9 * mm, y=10.5 * mm)
    
    c.setFillColor(CREAM)
    c.roundRect(w - 38 * mm, 12 * mm, 30 * mm, 9 * mm, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(SAGE)
    c.setFont("LabelElegant", 7.5)
    c.drawCentredString(w - 38 * mm + 15 * mm, 15.0 * mm, "Refill")
    
    c.showPage()
    c.save()
    print(f"Generated: {out_file}")
    return out_file

# --- Clean Master A4 Imposition Sheet ---

def build_master_a4_sheet(l1_path, l2_path, l3_path, l4_path, l5_path, l6_path, l7_path):
    out_path = OUTPUT_DIR / "complete-custom-pantry-all-7-labels-a4-sheet.pdf"

    writer = PdfWriter()
    sheet = writer.add_blank_page(width=A4_W, height=A4_H)

    # Row 1 (Top): Label 2 & Label 3 (80x60mm each)
    r1_y = A4_H - 12 * mm - 60 * mm
    l2_x = 18 * mm
    l3_x = 18 * mm + 80 * mm + 14 * mm
    sheet.merge_transformed_page(PdfReader(str(l2_path)).pages[0], Transformation().translate(tx=l2_x, ty=r1_y), over=True)
    sheet.merge_transformed_page(PdfReader(str(l3_path)).pages[0], Transformation().translate(tx=l3_x, ty=r1_y), over=True)

    # Row 2 (Middle):
    r2_y = r1_y - 12 * mm - 80 * mm
    l4_x = 14 * mm
    l5_x = l4_x + 60 * mm + 10 * mm
    l1_rot_x = l5_x + 60 * mm + 12 * mm
    l1_rot_y = r2_y + 5 * mm

    sheet.merge_transformed_page(PdfReader(str(l4_path)).pages[0], Transformation().translate(tx=l4_x, ty=r2_y), over=True)
    sheet.merge_transformed_page(PdfReader(str(l5_path)).pages[0], Transformation().translate(tx=l5_x, ty=r2_y), over=True)

    # Rotated Cornflour Label
    p1 = PdfReader(str(l1_path)).pages[0]
    t1 = Transformation().rotate(90).translate(tx=l1_rot_x + 40 * mm, ty=l1_rot_y)
    sheet.merge_transformed_page(p1, t1, over=True)

    # Row 3 (Bottom):
    l7_rot_x = 12 * mm
    l7_rot_y = 12 * mm
    p7 = PdfReader(str(l7_path)).pages[0]
    t7 = Transformation().rotate(90).translate(tx=l7_rot_x + 110 * mm, ty=l7_rot_y)
    sheet.merge_transformed_page(p7, t7, over=True)

    l6_rot_x = l7_rot_x + 110 * mm + 10 * mm
    l6_rot_y = 12 * mm
    p6 = PdfReader(str(l6_path)).pages[0]
    t6 = Transformation().rotate(90).translate(tx=l6_rot_x + 70 * mm, ty=l6_rot_y)
    sheet.merge_transformed_page(p6, t6, over=True)

    with out_path.open("wb") as handle:
        writer.write(handle)
    print(f"Generated Clean 7-Label Master Sheet: {out_path}")

def build():
    register_fonts()
    l1 = build_label_1()
    l2 = build_label_2()
    l3 = build_label_3()
    l4 = build_label_4()
    l5 = build_label_5()
    l6 = build_label_6()
    l7 = build_label_7()
    build_master_a4_sheet(l1, l2, l3, l4, l5, l6, l7)

if __name__ == "__main__":
    build()
