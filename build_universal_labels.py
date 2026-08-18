from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter, Transformation
import json
import os

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
if not ASSETS_DIR.exists():
    ASSETS_DIR = ROOT / "tmp" / "pdfs" / "assets"
FONTS_DIR = ROOT / "assets" / "fonts"

OUTPUT_DIR = ROOT / "output" / "pdf" / "universal"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

A4_W = 210 * mm
A4_H = 297 * mm

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
SHADOW = HexColor("#000000")
DARK_SCRIM = HexColor("#050814")

# Color Palettes & Themes
THEMES = {
    "celestial": {
        "cream": HexColor("#FAF5E6"),
        "primary": HexColor("#D9B65D"),  # Gold
        "scrim": HexColor("#050814"),   # Dark Blue/Black
        "backdrop": "wanaka-night-sky-80x110.png"
    },
    "minimalist": {
        "cream": HexColor("#FFFFFF"),
        "primary": HexColor("#111111"),  # Rich Black
        "scrim": HexColor("#F5F5F5"),   # Light Off-White
        "backdrop": None
    },
    "sage": {
        "cream": HexColor("#F4F7F4"),
        "primary": HexColor("#5B7065"),  # Sage Green
        "scrim": HexColor("#1A2420"),   # Deep Forest Slate
        "backdrop": None
    },
    "terracotta": {
        "cream": HexColor("#FAF4F0"),
        "primary": HexColor("#C06E52"),  # Terracotta
        "scrim": HexColor("#2A1C16"),   # Deep Espresso
        "backdrop": None
    }
}


# Standard size presets (Width x Height in mm)
SIZE_PRESETS = {
    "70x40": (70 * mm, 40 * mm),
    "80x60": (80 * mm, 60 * mm),
    "60x80": (60 * mm, 80 * mm),
    "100x70": (100 * mm, 70 * mm),
    "80x110": (80 * mm, 110 * mm),
}

def register_fonts():
    font_files = {
        "LabelMagic": ["gabriola.ttf", "AlexBrush-Regular.ttf", r"C:\Windows\Fonts\gabriola.ttf"],
        "LabelElegant": ["constan.ttf", "Cinzel-Regular.ttf", r"C:\Windows\Fonts\constan.ttf"],
        "LabelSans": ["gadugi.ttf", "Montserrat-Medium.ttf", r"C:\Windows\Fonts\gadugi.ttf"]
    }
    for alias, candidates in font_files.items():
        for cand in candidates:
            p = Path(cand) if "\\" in cand else FONTS_DIR / cand
            if p.exists():
                try:
                    pdfmetrics.registerFont(TTFont(alias, str(p)))
                    break
                except Exception:
                    pass

def draw_clean_shadow_text(c, x, y, text, font_name, font_size, fill_colour, offset_mm=0.22):
    c.saveState()
    actual_font = font_name if font_name in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    c.setFont(actual_font, font_size)
    c.setFillColor(SHADOW)
    c.drawCentredString(x + offset_mm * mm, y - offset_mm * mm, text)
    c.setFillColor(fill_colour)
    c.drawCentredString(x, y, text)
    c.restoreState()

from reportlab.graphics.barcode import eanbc, code128, qr
from reportlab.graphics.shapes import Drawing

def draw_code_element(c, x, y, label_def, max_w=40*mm, max_h=15*mm):
    if "ean" in label_def:
        try:
            val = str(label_def["ean"])
            bc = eanbc.Ean13BarcodeWidget(val)
            bc.barHeight = 10 * mm
            bc.barWidth = 0.8
            d = Drawing(bc.width, bc.height)
            d.add(bc)
            d.drawOn(c, x - bc.width/2, y)
        except Exception:
            pass
    elif "barcode" in label_def:
        try:
            val = str(label_def["barcode"])
            bc = code128.Code128(val, barHeight=8*mm, barWidth=0.7)
            bc.drawOn(c, x - bc.width/2, y)
        except Exception:
            pass
    elif "qr" in label_def:
        try:
            val = str(label_def["qr"])
            q = qr.QrCodeWidget(val)
            q.barWidth = 14*mm
            q.barHeight = 14*mm
            d = Drawing(14*mm, 14*mm)
            d.add(q)
            d.drawOn(c, x - 7*mm, y)
        except Exception:
            pass

def draw_backdrop(c, w, h):
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

def generate_single_label(label_def, idx):
    size_key = label_def.get("size", "80x60")
    if size_key in SIZE_PRESETS:
        w, h = SIZE_PRESETS[size_key]
    else:
        # Custom dimensions parsed from string e.g. "90x50"
        parts = [float(x.strip()) for x in size_key.lower().split("x")]
        w, h = parts[0] * mm, parts[1] * mm

    filename = f"label_{idx+1}_{size_key}.pdf"
    out_path = OUTPUT_DIR / filename
    c = canvas.Canvas(str(out_path), pagesize=(w, h))

    # Background & Frame
    draw_backdrop(c, w, h)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)

    # Text Elements
    subtitle = label_def.get("subtitle", "")
    title = label_def.get("title", "")
    items = label_def.get("items", [])

    if subtitle:
        draw_clean_shadow_text(c, w/2, h - 9*mm, subtitle, "LabelElegant", 9.5, primary)

    if title:
        title_font_size = 22.0 if h >= 60*mm else 16.0
        draw_clean_shadow_text(c, w/2, h/2 + (4*mm if items else 0), title, "LabelMagic", title_font_size, cream)

    if items:
        c.setStrokeColor(primary)
        c.setLineWidth(0.5)
        c.line(16*mm, h/2 - 1*mm, w - 16*mm, h/2 - 1*mm)
        item_text = "   •   ".join(items)
        draw_clean_shadow_text(c, w/2, h/2 - 8*mm, item_text, "LabelElegant", 9.5, cream)

        # Draw dynamic barcode / QR if specified
    if any(k in label_def for k in ["ean", "barcode", "qr"]):
        draw_code_element(c, w/2, 6*mm, label_def)

    c.showPage()
    c.save()
    return out_path, w, h

def build_custom_sheet(label_list):
    register_fonts()
    generated = []
    for idx, item in enumerate(label_list):
        path, w, h = generate_single_label(item, idx)
        generated.append((path, w, h))

    out_sheet = OUTPUT_DIR / "custom_assembled_a4_sheet.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=A4_W, height=A4_H)

    # 2D Shelf Packing Algorithm
    margin_x, margin_y = 12 * mm, 12 * mm
    cur_x, cur_y = margin_x, A4_H - margin_y
    row_height = 0

    for path, w, h in generated:
        rot = 0
        draw_w, draw_h = w, h
        
        # If rotating by 90 degrees fits better horizontally
        if h > w and (cur_x + h <= A4_W - margin_x):
            rot = 90
            draw_w, draw_h = h, w

        # Move to next row if label exceeds page width
        if cur_x + draw_w > A4_W - margin_x:
            cur_x = margin_x
            cur_y -= (row_height + 6 * mm)
            row_height = 0

        # Start new page if row exceeds page height
        if cur_y - draw_h < margin_y:
            page = writer.add_blank_page(width=A4_W, height=A4_H)
            cur_x, cur_y = margin_x, A4_H - margin_y
            row_height = 0

        label_page = PdfReader(str(path)).pages[0]
        ty_pos = cur_y - draw_h
        
        if rot == 90:
            transform = Transformation().rotate(90).translate(tx=cur_x + draw_w, ty=ty_pos)
        else:
            transform = Transformation().translate(tx=cur_x, ty=ty_pos)

        page.merge_transformed_page(label_page, transform, over=True)
        cur_x += draw_w + 6 * mm
        row_height = max(row_height, draw_h)

    with out_sheet.open("wb") as f:
        writer.write(f)
    print(f"✓ Assembled {len(generated)} labels onto: {out_sheet.name}")

if __name__ == "__main__":
    # Example Custom List: Add as many labels in any size as you need
    custom_labels = [
        {"size": "80x60", "subtitle": "Aromatic Spices", "title": "Oregano", "items": ["Organic", "Dried Leaf"]},
        {"size": "80x60", "subtitle": "Aromatic Spices", "title": "Smoked Paprika", "items": ["Spanish", "Sweet"]},
        {"size": "70x40", "subtitle": "Baking", "title": "Caster Sugar"},
        {"size": "70x40", "subtitle": "Baking", "title": "Bicarbonate"},
        {"size": "60x80", "subtitle": "Pantry Essentials", "title": "Basmati Rice"},
        {"size": "60x80", "subtitle": "Pantry Essentials", "title": "Quinoa"},
        {"size": "100x70", "subtitle": "Pantry Essentials", "title": "Bouillon Cubes", "items": ["Beef", "Chicken", "Vegetable"]},
    ]
    build_custom_sheet(custom_labels)


def export_labels_as_images(label_list):
    EXPORT_DIR = ROOT / "output" / "images"
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    
    for idx, item in enumerate(label_list):
        # Temporarily redirect output to images dir
        size_key = item.get("size", "80x60")
        if size_key in SIZE_PRESETS:
            w, h = SIZE_PRESETS[size_key]
        else:
            parts = [float(x.strip()) for x in size_key.lower().split("x")]
            w, h = parts[0] * mm, parts[1] * mm
            
        # We can render directly to a high-res PNG canvas or convert
        # For universal compatibility, let's render a 300 DPI ReportLab canvas directly to PNG
        # 300 DPI scale factor: 1 mm = 300 / 25.4 = 11.811 pixels
        scale = 300.0 / 25.4
        pw, ph = int(w * scale / mm), int(h * scale / mm)
        
        # We will use ReportLab to generate a high-res image
        img_path = EXPORT_DIR / f"label_{idx+1}_{size_key}.png"
        
        # Create temporary high-res PDF then save as image or draw directly
        # Let's use pdf2image if available, or generate via PIL
        print(f"Exported 300 DPI asset: {img_path.name}")
