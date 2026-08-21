from pathlib import Path
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "output" / "pdf" / "universal"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

A4_W, A4_H = 210 * mm, 297 * mm

CREAM, GOLD, RED, GREEN, VIOLET, TURMERIC = HexColor("#FAF5E6"), HexColor("#D9B65D"), HexColor("#C94E52"), HexColor("#76A779"), HexColor("#9B7ACB"), HexColor("#E2A93B")
BROWN, L_BROWN, PEPPER, NIGHT = HexColor("#B97845"), HexColor("#E2B376"), HexColor("#B9AEC9"), HexColor("#02040a")

def register_fonts():
    pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
    pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))
    pdfmetrics.registerFont(TTFont("LabelSans", r"C:\Windows\Fonts\gadugi.ttf"))

def draw_shadowed_centred(c, x, y, text, font_name, font_size, fill_colour, offset=0.3):
    c.saveState()
    c.setFont(font_name, font_size)
    c.setFillColor(HexColor("#000000"))
    c.drawCentredString(x + offset * mm, y - offset * mm, text)
    c.setFillColor(fill_colour)
    c.drawCentredString(x, y, text)
    c.restoreState()

def draw_dynamic_shadowed(c, x, y, text, font_name, max_size, max_w, fill_colour):
    size = max_size
    while size > 5.0 and c.stringWidth(text, font_name, size) > max_w:
        size -= 0.5
    draw_shadowed_centred(c, x, y, text, font_name, size, fill_colour)

# --- YOUR BESPOKE VECTOR ARTWORK ---
def draw_spice_bowl(c):
    c.saveState()
    c.setStrokeColor(GOLD); c.setLineWidth(0.65); c.setFillColor(TURMERIC)
    c.wedge(3.5 * mm, 17.0 * mm, 15.0 * mm, 27.0 * mm, 180, 180, stroke=1, fill=1)
    c.setFillColor(RED); c.circle(6.0 * mm, 27.0 * mm, 0.7 * mm, stroke=0, fill=1)
    c.setFillColor(GREEN); c.ellipse(9.0 * mm, 25.8 * mm, 13.2 * mm, 27.6 * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(0.55); c.line(11.5 * mm, 26.5 * mm, 15.0 * mm, 30.2 * mm)
    c.restoreState()

def draw_leaf(c, cx, cy, flip=1):
    c.setStrokeColor(CREAM); c.setLineWidth(0.55); p = c.beginPath(); p.moveTo(cx, cy)
    p.curveTo(cx + flip * 1.0 * mm, cy + 4.0 * mm, cx + flip * 6.0 * mm, cy + 5.0 * mm, cx + flip * 7.5 * mm, cy + 2.0 * mm)
    p.curveTo(cx + flip * 5.0 * mm, cy - 0.2 * mm, cx + flip * 1.8 * mm, cy + 0.2 * mm, cx, cy)
    c.drawPath(p, stroke=1, fill=0); c.line(cx, cy, cx + flip * 6.2 * mm, cy + 2.2 * mm)

def draw_botanical_mark(c):
    cx = 15 * mm
    c.setStrokeColor(GOLD); c.setLineWidth(0.7); c.setLineCap(1); c.line(cx, 7 * mm, cx, 21 * mm)
    draw_leaf(c, cx, 12.0 * mm, flip=-1); draw_leaf(c, cx, 16.5 * mm, flip=1)
    c.setStrokeColor(VIOLET); c.setFillColor(VIOLET)
    for x, y, radius in [(8.2, 22.0, 1.0), (12.1, 25.0, .75), (20.0, 22.5, .85)]:
        p = c.beginPath(); p.moveTo(x * mm, (y + radius * 1.7) * mm)
        p.curveTo((x - radius) * mm, y * mm, (x - radius) * mm, (y - radius) * mm, x * mm, (y - radius) * mm)
        p.curveTo((x + radius) * mm, (y - radius) * mm, (x + radius) * mm, y * mm, x * mm, (y + radius * 1.7) * mm)
        c.drawPath(p, stroke=0, fill=1)

def draw_chilli(c):
    c.setStrokeColor(RED); c.setLineWidth(1.7); c.setLineCap(1); p = c.beginPath(); p.moveTo(4.0 * mm, 9.0 * mm)
    p.curveTo(5.5 * mm, 5.0 * mm, 9.0 * mm, 4.0 * mm, 11.0 * mm, 6.5 * mm); c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.line(3.9 * mm, 9.0 * mm, 3.0 * mm, 11.0 * mm)

def draw_garam(c):
    c.setFillColor(GOLD)
    for x, y, r in [(5.0, 7.0, 1.0), (8.0, 6.0, .8), (10.5, 8.3, .9), (7.0, 10.0, .75), (10.0, 11.0, .55)]:
        c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(VIOLET); c.setLineWidth(0.5); c.arc(3.2 * mm, 4.3 * mm, 12.2 * mm, 10.0 * mm, 190, 160)

def draw_coriander(c):
    c.setStrokeColor(GREEN); c.setLineWidth(0.55); c.line(7.2 * mm, 4.2 * mm, 7.2 * mm, 12.2 * mm)
    c.setFillColor(GREEN)
    for x, y, rx, ry in [(4.8, 8.3, 2.0, 1.1), (9.4, 10.3, 2.1, 1.15), (5.2, 12.0, 1.7, 1.0)]:
        c.ellipse((x-rx)*mm, (y-ry)*mm, (x+rx)*mm, (y+ry)*mm, stroke=0, fill=1)
    c.setFillColor(GOLD)
    for x, y in [(4.0, 5.0), (9.8, 5.3), (11.2, 7.0)]: c.circle(x * mm, y * mm, .55 * mm, stroke=0, fill=1)

def draw_pepper(c):
    c.setFillColor(PEPPER)
    for x, y, r in [(4.7, 6.3, 1.1), (7.8, 5.3, .85), (10.4, 7.3, 1.0), (6.0, 9.6, .8), (9.0, 11.0, .95)]:
        c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(GOLD); c.setLineWidth(0.45); c.line(8.9 * mm, 12.0 * mm, 10.5 * mm, 14.0 * mm)

def draw_brown_sugar(c):
    c.setFillColor(BROWN); c.setStrokeColor(L_BROWN); c.setLineWidth(0.25)
    for x, y, size, angle in [(4.7, 6.0, 1.5, 12), (7.8, 5.2, 1.35, -18), (10.5, 6.8, 1.45, 24), (5.8, 9.4, 1.25, -28), (8.9, 10.5, 1.55, 8)]:
        c.saveState(); c.translate(x * mm, y * mm); c.rotate(angle)
        c.rect(-size * .5 * mm, -size * .5 * mm, size * mm, size * mm, stroke=1, fill=1); c.restoreState()

def draw_sesame(c):
    c.setFillColor(L_BROWN); c.setStrokeColor(GOLD); c.setLineWidth(0.25)
    for x, y, rx, ry, angle in [(4.5, 6.0, 1.25, .55, 24), (7.7, 5.2, 1.15, .5, -18), (10.5, 7.0, 1.3, .55, 35), (5.8, 9.5, 1.1, .5, -32), (9.1, 10.7, 1.25, .55, 14)]:
        c.saveState(); c.translate(x * mm, y * mm); c.rotate(angle)
        c.ellipse(-rx * mm, -ry * mm, rx * mm, ry * mm, stroke=1, fill=1); c.restoreState()


# --- GENERATOR LOGIC ---
def generate_single_label(label_def, idx):
    size_str = label_def.get("size", "100x40")
    w, h = [int(x) * mm for x in size_str.split("x")]
    
    out_path = OUTPUT_DIR / f"label_{idx+1}_{size_str}.pdf"
    c = canvas.Canvas(str(out_path), pagesize=(w, h))

    bg = ASSETS_DIR / "wanaka-night-sky-original.png"
    if not bg.exists(): bg = ASSETS_DIR / "wanaka-night-sky-80x110.png"
    
    c.saveState()
    p = c.beginPath(); p.rect(0, 0, w, h); c.clipPath(p, stroke=0, fill=0)
    if bg.exists():
        try:
            img = ImageReader(str(bg))
            iw, ih = img.getSize()
            scale = max(w / iw, h / ih)
            draw_w, draw_h = iw * scale, ih * scale
            
            draw_x = (w - draw_w) / 2
            
            # FIX: If it's a wide tub, align to the TOP of the image so the moon is beautifully framed!
            if w > h:
                draw_y = (h - draw_h) * 0.95 
            else:
                draw_y = (h - draw_h) / 2
                
            c.drawImage(img, draw_x, draw_y, width=draw_w, height=draw_h, mask="auto")
        except: pass
    c.restoreState()

    # FIX: Lighten the overlay so clouds and stars are actually visible again
    c.setFillColor(NIGHT); c.setFillAlpha(0.40)
    c.rect(0, 0, w, h, fill=1, stroke=0); c.setFillAlpha(1.0)

    # Gold Border
    c.setStrokeColor(GOLD); c.setLineWidth(0.75); c.setLineCap(1)
    c.roundRect(3*mm, 3*mm, w-6*mm, h-6*mm, 2*mm, stroke=1, fill=0)

    title = label_def.get("title", "")
    subtitle = label_def.get("subtitle", "")
    items = label_def.get("items", [])
    t_lower = title.lower()

    if h == 40 * mm: # 100x40 Tubs
        c.saveState()
        if "specialty" in t_lower:
            c.translate(7*mm, -3*mm)
            draw_spice_bowl(c)
        else:
            c.translate(7*mm, 12*mm); c.scale(1.4, 1.4)
            if "herb" in t_lower: draw_coriander(c)
            elif "heat" in t_lower: draw_chilli(c)
            elif "warm" in t_lower: draw_garam(c)
            elif "condiment" in t_lower: draw_pepper(c)
            elif "oat" in t_lower: draw_brown_sugar(c)
            elif "snack" in t_lower: draw_sesame(c)
            else: draw_coriander(c)
        c.restoreState()
        
        tx = 60 * mm
        max_w = 70 * mm
        draw_dynamic_shadowed(c, tx, 26.5*mm, subtitle, "LabelElegant", 9, max_w, GOLD)
        draw_dynamic_shadowed(c, tx, 17.5*mm, title, "LabelMagic", 20, max_w, CREAM)
        
        c.setStrokeColor(GOLD); c.setLineWidth(0.4)
        c.line(26*mm, 12*mm, w-6*mm, 12*mm)
        
        item_str = " • ".join(items)
        c.saveState()
        size = 8.0
        while size > 4.5 and c.stringWidth(item_str, "LabelSans", size) > (w - 32*mm):
            size -= 0.5
        c.setFont("LabelSans", size); c.setFillColor(HexColor("#000000"))
        c.drawCentredString(tx + 0.3*mm, 7.5*mm - 0.3*mm, item_str)
        c.setFillColor(CREAM); c.drawCentredString(tx, 7.5*mm, item_str)
        c.restoreState()

    else: # 80x80 & 60x90 Oils
        c.saveState()
        c.translate(w/2 - 15*mm, h - 30*mm)
        draw_botanical_mark(c)
        c.restoreState()
        
        tx = w / 2
        draw_dynamic_shadowed(c, tx, h - 45*mm, subtitle, "LabelElegant", 9, w-10*mm, GOLD)
        draw_dynamic_shadowed(c, tx, h - 55*mm, title, "LabelMagic", 22, w-10*mm, CREAM)
        
        c.setStrokeColor(GOLD); c.setLineWidth(0.6)
        c.line(12*mm, h - 65*mm, w-12*mm, h - 65*mm)
        
        item_str = " • ".join(items)
        c.saveState()
        size = 8.5
        while size > 5.0 and c.stringWidth(item_str, "LabelSans", size) > (w - 20*mm):
            size -= 0.5
        c.setFont("LabelSans", size); c.setFillColor(HexColor("#000000"))
        c.drawCentredString(tx + 0.3*mm, h - 72*mm - 0.3*mm, item_str)
        c.setFillColor(CREAM); c.drawCentredString(tx, h - 72*mm, item_str)
        c.restoreState()

    c.showPage(); c.save()
    return out_path, w, h

def build_custom_sheet(label_list):
    register_fonts()
    generated = [generate_single_label(i, idx) for idx, i in enumerate(label_list)]
    out_sheet = OUTPUT_DIR / "custom_assembled_a4_sheet.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=A4_W, height=A4_H)

    margin = 5 * mm
    cur_x, cur_y = margin, A4_H - margin
    row_height = 0

    generated.sort(key=lambda x: max(x[1], x[2]), reverse=True)

    for path, w, h in generated:
        rot, draw_w, draw_h = 0, w, h
        if w > h: rot, draw_w, draw_h = 90, h, w

        if cur_x + draw_w > A4_W - margin:
            cur_x, cur_y = margin, cur_y - (row_height + 4 * mm)
            row_height = 0

        label_page = PdfReader(str(path)).pages[0]
        ty_pos = cur_y - draw_h
        transform = Transformation().rotate(90).translate(tx=cur_x + draw_w, ty=ty_pos) if rot == 90 else Transformation().translate(tx=cur_x, ty=ty_pos)
        page.merge_transformed_page(label_page, transform, over=True)
        
        cur_x += draw_w + 4 * mm
        row_height = max(row_height, draw_h)

    with out_sheet.open("wb") as f: writer.write(f)
    print(f"✓ Backdrop framing fixed: {out_sheet.name}")

import json
with open("my_labels.json", "r", encoding="utf-8") as f:
    labels = json.load(f)
build_custom_sheet(labels)
