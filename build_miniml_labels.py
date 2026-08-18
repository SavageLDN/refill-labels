from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR = ROOT / "tmp" / "pdfs" / "assets"

OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LABEL_W = 80 * mm
LABEL_H = 110 * mm
A4_W = 210 * mm
A4_H = 297 * mm

CREAM = HexColor("#FAF5E6")
SAGE = HexColor("#11162E")
HUSK = HexColor("#D9B65D")

def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont("LabelSans", r"C:\Windows\Fonts\gadugi.ttf"))
        pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\Windows\Fonts\gabriola.ttf"))
        pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\Windows\Fonts\constan.ttf"))
    except Exception:
        pass

def draw_flavour_artwork(c, flavour_key, x, y, scale=1.0):
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    c.setLineWidth(0.9)

    if flavour_key == "lemon":
        c.setStrokeColor(CREAM)
        c.setFillColor(HUSK)
        c.ellipse(0 * mm, 4 * mm, 18 * mm, 12 * mm, stroke=1, fill=1)
        c.setFillColor(CREAM)
        c.circle(5 * mm, 10 * mm, 0.9 * mm, stroke=0, fill=1)
        c.circle(9 * mm, 8 * mm, 0.8 * mm, stroke=0, fill=1)
        c.setStrokeColor(CREAM)
        p = c.beginPath()
        p.moveTo(18 * mm, 12 * mm)
        p.curveTo(23 * mm, 16 * mm, 26 * mm, 12 * mm, 22 * mm, 9 * mm)
        c.drawPath(p, stroke=1, fill=0)
    elif flavour_key == "dragonfruit":
        c.setStrokeColor(CREAM)
        c.setFillColor(HUSK)
        c.circle(8 * mm, 8 * mm, 8 * mm, stroke=1, fill=1)
        c.setStrokeColor(CREAM)
        for a in range(6):
            c.arc(2 * mm + a * 1.6 * mm, 4 * mm, 14 * mm, 12 * mm, 0, 180)
    elif flavour_key == "mint":
        c.setStrokeColor(CREAM)
        c.setFillColor(SAGE)
        p = c.beginPath()
        p.moveTo(0 * mm, 6 * mm)
        p.curveTo(6 * mm, 14 * mm, 14 * mm, 14 * mm, 18 * mm, 6 * mm)
        p.curveTo(14 * mm, 3 * mm, 6 * mm, 3 * mm, 0 * mm, 6 * mm)
        c.drawPath(p, stroke=1, fill=1)
        p2 = c.beginPath()
        p2.moveTo(-2 * mm, 2 * mm)
        p2.curveTo(4 * mm, 10 * mm, 12 * mm, 10 * mm, 16 * mm, 2 * mm)
        p2.curveTo(12 * mm, -1 * mm, 4 * mm, -1 * mm, -2 * mm, 2 * mm)
        c.setStrokeColor(CREAM)
        c.drawPath(p2, stroke=1, fill=0)
    else:
        c.setFillColor(HUSK)
        c.circle(6 * mm, 10 * mm, 2.2 * mm, stroke=0, fill=1)
        c.setStrokeColor(CREAM)
        c.line(6 * mm, 13 * mm, 6 * mm, 7 * mm)
        c.line(3 * mm, 10 * mm, 9 * mm, 10 * mm)

    c.restoreState()

def draw_company_wordmark(c, cx, cy):
    c.setFillColor(CREAM)
    try:
        page_w = float(getattr(c, '_pagesize', (LABEL_W, LABEL_H))[0])
        fs = max(16, int((page_w / mm) * 0.25))
        c.setFont("LabelSans", fs)
    except Exception:
        c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(cx, cy, "miniml")

def wrap_and_draw_centred(c, cx, y, text, fontname, fontsize, max_width):
    tokens = text.replace('\r', '').split()
    lines, cur = [], ""
    for w in tokens:
        if w == "&":
            if cur: lines.append(cur)
            lines.append("&")
            cur = ""
            continue
        test = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(test, fontname, fontsize) <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    leading = fontsize * 0.95
    for i, line in enumerate(lines):
        if line == "&":
            c.setFont(fontname, fontsize * 0.85)
            c.drawCentredString(cx, y - i * leading, line)
            c.setFont(fontname, fontsize)
        else:
            c.drawCentredString(cx, y - i * leading, line)
    return y - (len(lines) - 1) * leading

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

def draw_single_label(c, x0, y0, flavour, product_line, w=LABEL_W, h=LABEL_H):
    c.saveState()
    c.translate(x0, y0)

    chosen = select_best_backdrop_for_size(w, h)
    if chosen is None:
        chosen = ASSETS_DIR / "wanaka-night-sky-80x110.png"

    try:
        img = Image.open(str(chosen))
        iw, ih = img.size
        scale = max(float(w) / float(iw), float(h) / float(ih))
        draw_w, draw_h = iw * scale, ih * scale
        x_off, y_off = (float(w) - draw_w) / 2.0, (float(h) - draw_h) / 2.0
        c.drawImage(ImageReader(str(chosen)), x_off, y_off, width=draw_w, height=draw_h, mask="auto")
    except Exception:
        pass

    draw_company_wordmark(c, w / 2, h - 16 * mm)
    key = flavour_key_from_flavour(flavour)
    
    fontname = "LabelMagic"
    base_fs = max(12, int(min(48, (w / mm) * 0.28 * 10)))
    fontsize = int(base_fs * (0.50 if key in ['dragonfruit', 'mint'] else 0.9))
    c.setFont(fontname, fontsize)
    c.setFillColor(CREAM)

    flavour_top_y = h - (h * (0.42 if key == 'lemon' else 0.32)) - (6 * mm if key == 'lemon' else 4 * mm)
    flavour_top_y = min(max(flavour_top_y, h * 0.52), h - 26 * mm)
    flavour_bottom = wrap_and_draw_centred(c, w / 2, flavour_top_y, flavour, fontname, fontsize, float(w - 20 * mm))

    c.setFont("LabelElegant", max(10, int((w / mm) * 0.18)))
    c.setFillColor(CREAM)
    prod_y = flavour_bottom - (14 * mm if key == 'lemon' else 16 * mm if key == 'mint' else 6 * mm)
    c.drawCentredString(w / 2, prod_y, product_line)

    c.setStrokeColor(HUSK)
    c.setLineWidth(1.0)
    sep_y = prod_y - 6 * mm
    c.line(14 * mm, sep_y, w - 14 * mm, sep_y)

    art_y = min(max(18 * mm, sep_y - 22 * mm), h * 0.30)
    art_scale = 0.9 if key == 'lemon' else 0.8 if key == 'dragonfruit' else 0.85
    draw_flavour_artwork(c, key, 8 * mm, art_y, scale=art_scale)

    c.setFillColor(CREAM)
    c.roundRect(w - 42 * mm, 10 * mm, 34 * mm, 9 * mm, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(SAGE)
    c.setFont("LabelElegant", 7.2)
    c.drawCentredString(w - 42 * mm + 17 * mm, 13 * mm, "Refill")
    c.restoreState()

def draw_cut_marks(c, x, y, w, h, mark_len=5*mm):
    c.saveState()
    c.setStrokeColor(HUSK)
    c.setLineWidth(0.5)
    c.line(x, y + h + (mark_len/2), x + mark_len, y + h + (mark_len/2))
    c.line(x - (mark_len/2), y + h, x - (mark_len/2), y + h - mark_len)
    c.line(x + w - mark_len, y + h + (mark_len/2), x + w, y + h + (mark_len/2))
    c.line(x + w + (mark_len/2), y + h, x + w + (mark_len/2), y + h - mark_len)
    c.line(x, y - (mark_len/2), x + mark_len, y - (mark_len/2))
    c.line(x - (mark_len/2), y, x - (mark_len/2), y + mark_len)
    c.line(x + w - mark_len, y - (mark_len/2), x + w, y - (mark_len/2))
    c.line(x + w + (mark_len/2), y, x + w + (mark_len/2), y + mark_len)
    c.restoreState()

def flavour_key_from_flavour(flavour_text: str) -> str:
    text = flavour_text.lower()
    if "lemon" in text or "sorrento" in text: return "lemon"
    if "dragonfruit" in text or "orchid" in text: return "dragonfruit"
    if "spearmint" in text or "peppermint" in text or "mint" in text: return "mint"
    return "spark"

def build():
    register_fonts()
    out_path = OUTPUT_DIR / "three_labels_a4_cutting_guides.pdf"
    c = canvas.Canvas(str(out_path), pagesize=(A4_W, A4_H), pageCompression=1)
    
    # 1. Sorrento Lemon Vinegar (scaled to 115x155 to fit cleanly on A4)
    wv, hv = 115 * mm, 155 * mm
    x_left, y_top = 7 * mm, A4_H - 8 * mm - hv
    draw_single_label(c, x_left, y_top, "Sorrento Lemon Scented", "Eco White Vinegar Cleaning", w=wv, h=hv)
    draw_cut_marks(c, x_left, y_top, wv, hv)

    # 2. Pink Dragonfruit & Orchid Conditioner (80x100mm sits within the right border)
    wr, hr = 80 * mm, 100 * mm
    x_right = x_left + wv + 3 * mm
    y_cond = A4_H - 8 * mm - hr
    draw_single_label(c, x_right, y_cond, "Pink Dragonfruit & Orchid", "Fabric Softener & Conditioner", w=wr, h=hr)
    draw_cut_marks(c, x_right, y_cond, wr, hr)

    # 3. Spearmint & Peppermint Toilet Cleaner (Rotated across bottom)
    w_orig, h_orig = 80 * mm, 120 * mm
    rot_w, rot_h = h_orig, w_orig
    x_toilet = (A4_W - rot_w) / 2
    y_toilet = 10 * mm
    c.saveState()
    c.translate(float(x_toilet), float(y_toilet))
    c.rotate(90)
    draw_single_label(c, 0, -float(w_orig), "Spearmint & Peppermint", "Eco Toilet Cleaner", w=w_orig, h=h_orig)
    c.restoreState()
    draw_cut_marks(c, x_toilet, y_toilet, rot_w, rot_h)

    c.showPage()
    c.save()
    print(f"Generated clean A4 sheet: {out_path}")

if __name__ == "__main__":
    build()
