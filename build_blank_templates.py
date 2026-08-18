from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "output" / "pdf" / "templates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CREAM = HexColor("#FAF5E6")
GOLD = HexColor("#D9B65D")
DARK_SCRIM = HexColor("#050814")

LABEL_SIZES = [
    {"name": "template-70x40mm-small-horizontal.pdf", "w": 70 * mm, "h": 40 * mm, "title": "70x40mm Horizontal"},
    {"name": "template-80x60mm-medium-horizontal.pdf", "w": 80 * mm, "h": 60 * mm, "title": "80x60mm Horizontal"},
    {"name": "template-60x80mm-medium-vertical.pdf",   "w": 60 * mm, "h": 80 * mm, "title": "60x80mm Vertical"},
    {"name": "template-100x70mm-large-horizontal.pdf", "w": 100 * mm, "h": 70 * mm, "title": "100x70mm Horizontal"},
    {"name": "template-80x110mm-large-vertical.pdf",   "w": 80 * mm, "h": 110 * mm, "title": "80x110mm Vertical"},
]

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

def generate_templates():
    for item in LABEL_SIZES:
        out_path = OUTPUT_DIR / item["name"]
        w, h = item["w"], item["h"]
        c = canvas.Canvas(str(out_path), pagesize=(w, h))
        c.setTitle(f"Blank Template - {item['title']}")
        
        # Background
        draw_backdrop(c, w, h)
        
        # Outer Gold Frame
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.6)
        c.roundRect(3*mm, 3*mm, w - 6*mm, h - 6*mm, 2*mm, stroke=1, fill=0)
        
        c.showPage()
        c.save()
        print(f"Generated template: {out_path.name}")

if __name__ == "__main__":
    generate_templates()
