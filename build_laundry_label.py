from pathlib import Path
from io import BytesIO
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image

# Assets stored in project assets folder
ASSETS_DIR = Path(r"C:\Users\moonl\OneDrive\Documents\10 - Refill Labels\assets")
OUTPUT_DIR = Path(r"C:\Users\moonl\OneDrive\Documents\10 - Refill Labels\output\pdf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Label and page sizes
LABEL_W = 80 * mm
LABEL_H = 110 * mm
A4_W = 210 * mm
A4_H = 297 * mm

# Backdrop (prefer correctly sized 80x110 if available; will be used without stretching)
BACKDROP = ASSETS_DIR / "wanaka-night-sky-80x110.png"

# Colours
CREAM = HexColor("#FAF5E6")
SAGE = HexColor("#11162E")
HUSK = HexColor("#D9B65D")

# Register fonts (Windows defaults). Adjust paths if fonts are missing.
def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont("LabelSans", r"C:\\Windows\\Fonts\\gadugi.ttf"))
        pdfmetrics.registerFont(TTFont("LabelMagic", r"C:\\Windows\\Fonts\\gabriola.ttf"))
        pdfmetrics.registerFont(TTFont("LabelElegant", r"C:\\Windows\\Fonts\\constan.ttf"))
    except Exception:
        # fall back to built-in fonts if those aren't available
        pass


def draw_flavour_artwork(c, flavour_key, x, y, scale=1.0):
    """Clearer, higher-contrast clipart that reads at small sizes.
    Drawn as simple linework supporting the magical theme but recognisable.
    """
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    c.setLineWidth(0.9)

    if flavour_key == "lemon":
        # clean lemon outline with a leaf
        c.setStrokeColor(CREAM)
        c.setFillColor(HUSK)
        # lemon body
        c.ellipse(0 * mm, 4 * mm, 18 * mm, 12 * mm, stroke=1, fill=1)
        # pips/detail
        c.setFillColor(CREAM)
        c.circle(5 * mm, 10 * mm, 0.9 * mm, stroke=0, fill=1)
        c.circle(9 * mm, 8 * mm, 0.8 * mm, stroke=0, fill=1)
        # leaf
        c.setStrokeColor(CREAM)
        p = c.beginPath()
        p.moveTo(18 * mm, 12 * mm)
        p.curveTo(23 * mm, 16 * mm, 26 * mm, 12 * mm, 22 * mm, 9 * mm)
        c.drawPath(p, stroke=1, fill=0)
    elif flavour_key == "dragonfruit":
        # round fruit with stylized scales
        c.setStrokeColor(CREAM)
        c.setFillColor(HUSK)
        c.circle(8 * mm, 8 * mm, 8 * mm, stroke=1, fill=1)
        c.setStrokeColor(CREAM)
        for a in range(6):
            c.arc(2 * mm + a * 1.6 * mm, 4 * mm, 14 * mm, 12 * mm, 0, 180)
    elif flavour_key == "mint":
        c.setStrokeColor(CREAM)
        c.setFillColor(SAGE)
        # two clear leaves
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
        # sparkle fallback
        c.setFillColor(HUSK)
        c.circle(6 * mm, 10 * mm, 2.2 * mm, stroke=0, fill=1)
        c.setStrokeColor(CREAM)
        c.line(6 * mm, 13 * mm, 6 * mm, 7 * mm)
        c.line(3 * mm, 10 * mm, 9 * mm, 10 * mm)

    c.restoreState()


def draw_company_wordmark(c, cx, cy):
    # Larger white wordmark at the top; size scales with page width for visibility
    c.setFillColor(CREAM)
    try:
        page_w = float(getattr(c, '_pagesize', (LABEL_W, LABEL_H))[0])
        # sensible scaling: ~0.25pt per mm gives ~20pt on 80mm label
        fs = max(16, int((page_w / mm) * 0.25))
        c.setFont("LabelSans", fs)
    except Exception:
        c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(cx, cy, "miniml")


def wrap_and_draw_centred(c, cx, y, text, fontname, fontsize, max_width):
    """Simple word-wrap centred block. Returns the final top y position used.
    Special handling: force '&' to its own line and draw it slightly smaller.
    Reduced leading by 10% for tighter spacing as requested.
    """
    from reportlab.pdfbase import pdfmetrics
    tokens = text.replace('\r', '').split()
    lines = []
    cur = ""
    for w in tokens:
        # Force ampersand onto its own line
        if w == "&":
            if cur:
                lines.append(cur)
            lines.append("&")
            cur = ""
            continue
        test = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(test, fontname, fontsize) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # draw lines centred, starting at y and moving down by leading
    leading = fontsize * 0.95  # reduced by 10% from previous 1.05 multiplier
    for i, line in enumerate(lines):
        if line == "&":
            # smaller ampersand
            try:
                amp_font = fontname
                amp_size = fontsize * 0.85
                c.setFont(amp_font, amp_size)
            except Exception:
                c.setFont("Times-Italic", fontsize * 0.85)
            c.drawCentredString(cx, y - i * leading, line)
            # restore font
            c.setFont(fontname, fontsize)
        else:
            c.drawCentredString(cx, y - i * leading, line)
    return y - (len(lines) - 1) * leading


def select_best_backdrop_for_size(w, h):
    """Pick the asset image with the closest aspect ratio to target (w,h). Returns Path or None."""
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
    best = min(candidates, key=lambda x: abs(x[1] - target_aspect))
    return best[0]


def draw_single_label(c, x0, y0, flavour, product_line, w=LABEL_W, h=LABEL_H):
    c.saveState()
    c.translate(x0, y0)

    # (removed opaque base fill so backdrop is visible)
    # Choose best backdrop for this size to avoid stretching
    chosen = select_best_backdrop_for_size(w, h)
    if chosen is None:
        chosen = ASSETS_DIR / "wanaka-night-sky-original.png"

    # Draw backdrop proportionally without stretching; prefer center-crop
    try:
        img = Image.open(str(chosen))
        iw, ih = img.size
        tgt_ratio = float(w) / float(h)
        img_ratio = float(iw) / float(ih)
        if abs(img_ratio - tgt_ratio) < 0.01:
            c.drawImage(ImageReader(str(chosen)), 0, 0, width=w, height=h, mask="auto")
        else:
            # Scale to cover the label (cover) then center-crop visually
            # compute scale to cover
            scale_w = float(w) / float(iw)
            scale_h = float(h) / float(ih)
            scale = max(scale_w, scale_h)  # cover
            draw_w = iw * scale
            draw_h = ih * scale
            x_off = (float(w) - draw_w) / 2.0
            y_off = (float(h) - draw_h) / 2.0
            c.drawImage(ImageReader(str(chosen)), x_off, y_off, width=draw_w, height=draw_h, mask="auto")
    except Exception:
        # fallback to default
        try:
            c.drawImage(ImageReader(str(ASSETS_DIR / "wanaka-night-sky-80x110.png")), 0, 0, width=w, height=h, mask="auto")
        except Exception:
            pass

    # Wordmark (logo) - kept white and slightly larger relative to width
    logo_y = h - (12 * mm) - (4 * mm)  # increase top margin by 4mm
    draw_company_wordmark(c, w / 2, logo_y)

    # Flavour (calligraphy-style), wrap and ensure padding from edges
    key = flavour_key_from_flavour(flavour)
    try:
        fontname = "LabelMagic"
        # baseline font size scales with width; adjust per flavour
        base_fs = max(12, int(min(48, (w / mm) * 0.28 * 10)))
        # apply per-flavour scaling: conditioner & toilet need smaller flavour text
        if key == 'dragonfruit':
            fontsize = int(base_fs * 0.50)  # set conditioner flavour to 50% of base
        elif key == 'mint':
            fontsize = int(base_fs * 0.5)
        else:
            fontsize = int(base_fs * 0.9)
        c.setFont(fontname, fontsize)
    except Exception:
        fontname = "Times-BoldItalic"
        base_fs = max(12, int((w / mm) * 0.25 * 9))
        if key == 'dragonfruit':
            fontsize = int(base_fs * 0.45)
        elif key == 'mint':
            fontsize = int(base_fs * 0.5)
        else:
            fontsize = int(base_fs * 0.9)
        c.setFont(fontname, fontsize)
    c.setFillColor(CREAM)
    max_w = float(w - 20 * mm)
    # default placement (keep within readable upper 60-85% of label)
    flavour_top_y = h - (h * 0.32) - (4 * mm)
    # vinegar: move the flavour further down to sit below moon/clouds but clamp
    if key == 'lemon':
        flavour_top_y = h - (h * 0.42) - (6 * mm)
    # clamp to sensible band so text doesn't fall to bottom
    min_top = h * 0.52
    max_top = h - 26 * mm
    flavour_top_y = min(max(flavour_top_y, min_top), max_top)

    # wrap and draw and capture bottom y of flavour block
    flavour_bottom = wrap_and_draw_centred(c, w / 2, flavour_top_y, flavour, fontname, fontsize, max_w)

    # Product line (main text) placed beneath the flavour block, in white only
    try:
        c.setFont("LabelElegant", max(10, int((w / mm) * 0.18)))
    except Exception:
        c.setFont("Helvetica", max(10, int((w / mm) * 0.16)))
    c.setFillColor(CREAM)
    # position the product line a fixed gap below the flavour bottom; larger gap for lemon and mint
    if key == 'lemon':
        prod_y = flavour_bottom - (8 * mm)
    elif key == 'mint':
        prod_y = flavour_bottom - (10 * mm)
    else:
        prod_y = flavour_bottom - (6 * mm)

    # Apply small manual nudges requested: vinegar down 6mm, spearmint down 6mm
    if key == 'lemon':
        prod_y = prod_y - (6 * mm)  # move vinegar product line further down
    if key == 'mint':
        prod_y = prod_y - (6 * mm)  # move spearmint product-type further down

    c.drawCentredString(w / 2, prod_y, product_line)

    # Separator moved beneath the product line with consistent gap
    c.setStrokeColor(HUSK)
    c.setLineWidth(1.0)
    sep_y = prod_y - (6 * mm)
    c.line(14 * mm, sep_y, w - 14 * mm, sep_y)

    # Flavour artwork moved upward slightly to give more breathing room from bottom and separator
    art_x = 8 * mm
    # ensure artwork sits above page bottom and below separator by a safe margin
    art_y_candidate = sep_y - 22 * mm
    art_y = min(max(18 * mm, art_y_candidate), h * 0.30)
    # scale artwork slightly smaller for large shapes to avoid covering text
    key_for_art = flavour_key_from_flavour(flavour)
    art_scale = 0.9 if key_for_art == 'lemon' else 0.8 if key_for_art == 'dragonfruit' else 0.85
    draw_flavour_artwork(c, key_for_art, art_x, art_y, scale=art_scale)

    # Small pill descriptor bottom-right
    c.setFillColor(CREAM)
    c.roundRect(w - 42 * mm, 10 * mm, 34 * mm, 9 * mm, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(SAGE)
    try:
        c.setFont("LabelElegant", 7.2)
    except Exception:
        c.setFont("Helvetica", 7.0)
    c.drawCentredString(w - 42 * mm + 17 * mm, 13 * mm, "Refill")

    c.restoreState()


def build_combined_a4_for_cutting():
    """Place the three custom-size labels onto one A4 sheet with cutting guides for easy cutting."""
    # target label sizes
    size_vin = (120 * mm, 160 * mm, "miniml-eco-white-vinegar-sorrento-lemon-120x160mm.pdf", "Sorrento Lemon Scented", "Eco White Vinegar Cleaning")
    size_cond = (80 * mm, 100 * mm, "miniml-natural-fabric-softener-pink-dragonfruit-orchid-80x100mm.pdf", "Pink Dragonfruit & Orchid", "Fabric Softener & Conditioner")
    size_toilet = (80 * mm, 120 * mm, "miniml-eco-toilet-cleaner-spearmint-peppermint-80x120mm.pdf", "Spearmint & Peppermint", "Eco Toilet Cleaner")

    # create A4 canvas
    out_path = OUTPUT_DIR / "three_labels_a4_cutting_guides.pdf"
    c = canvas.Canvas(str(out_path), pagesize=(A4_W, A4_H), pageCompression=1)
    c.setTitle("Miniml - 3 labels A4 for cutting")

    left_margin = 12 * mm
    gap = 8 * mm

    # Place vinegar label on left column, top aligned
    wv, hv = size_vin[0], size_vin[1]
    x_left = left_margin
    y_top = A4_H - left_margin - hv
    draw_single_label(c, x_left, y_top, size_vin[3], size_vin[4], w=wv, h=hv)
    draw_cut_marks(c, x_left, y_top, wv, hv)

    # Place conditioner at top-right
    wr, hr = size_cond[0], size_cond[1]
    x_right = x_left + wv + gap
    y_cond = A4_H - left_margin - hr
    draw_single_label(c, x_right, y_cond, size_cond[3], size_cond[4], w=wr, h=hr)
    draw_cut_marks(c, x_right, y_cond, wr, hr)

    # Place toilet cleaner rotated 90 degrees at bottom center
    wr2, hr2 = size_toilet[0], size_toilet[1]
    # original toilet width (w_orig) and height (h_orig)
    w_orig = wr2
    h_orig = hr2
    # rotated footprint
    rot_w = h_orig
    rot_h = w_orig
    # place centered at bottom with margin
    bottom_margin = left_margin
    x_toilet = (A4_W - rot_w) / 2
    y_toilet = bottom_margin
    # draw rotated: translate to (x_toilet, y_toilet), rotate and draw original-size label
    c.saveState()
    c.translate(float(x_toilet), float(y_toilet))
    c.rotate(90)
    # after rotation, draw_single_label at (0, -w_orig) so it occupies the rotated rect
    draw_single_label(c, 0, -float(w_orig), size_toilet[3], size_toilet[4], w=w_orig, h=h_orig)
    c.restoreState()
    # draw cut marks around the rotated footprint
    draw_cut_marks(c, x_toilet, y_toilet, rot_w, rot_h)

    # optional: draw faint registration and crop marks at page edges
    draw_page_crop_marks(c, 6 * mm)

    c.showPage()
    c.save()
    print(f"Saved combined A4 with cutting guides to: {out_path}")


def draw_cut_marks(c, x, y, w, h, mark_len=6*mm):
    """Draw small crop marks around rectangle at (x,y) size w,h"""
    c.saveState()
    c.setStrokeColor(HUSK)
    c.setLineWidth(0.6)
    # top-left
    c.line(x, y + h + (mark_len/2), x + mark_len, y + h + (mark_len/2))
    c.line(x - (mark_len/2), y + h, x - (mark_len/2), y + h - mark_len)
    # top-right
    c.line(x + w - mark_len, y + h + (mark_len/2), x + w, y + h + (mark_len/2))
    c.line(x + w + (mark_len/2), y + h, x + w + (mark_len/2), y + h - mark_len)
    # bottom-left
    c.line(x, y - (mark_len/2), x + mark_len, y - (mark_len/2))
    c.line(x - (mark_len/2), y, x - (mark_len/2), y + mark_len)
    # bottom-right
    c.line(x + w - mark_len, y - (mark_len/2), x + w, y - (mark_len/2))
    c.line(x + w + (mark_len/2), y, x + w + (mark_len/2), y + mark_len)
    c.restoreState()


def draw_page_crop_marks(c, inset=6*mm):
    c.saveState()
    c.setStrokeColor(HUSK)
    c.setLineWidth(0.4)
    # simple cross marks at mid-edges
    c.line(inset, A4_H/2 - 4*mm, inset + 4*mm, A4_H/2 - 4*mm)
    c.line(A4_W - inset, A4_H/2 - 4*mm, A4_W - inset - 4*mm, A4_H/2 - 4*mm)
    c.line(A4_W/2 - 4*mm, inset, A4_W/2 - 4*mm, inset + 4*mm)
    c.line(A4_W/2 - 4*mm, A4_H - inset, A4_W/2 - 4*mm, A4_H - inset - 4*mm)
    c.restoreState()


def flavour_key_from_flavour(flavour_text: str) -> str:
    text = flavour_text.lower()
    if "lemon" in text or "sorrento" in text:
        return "lemon"
    if "dragonfruit" in text or "orchid" in text:
        return "dragonfruit"
    if "spearmint" in text or "peppermint" in text or "mint" in text:
        return "mint"
    return "spark"


# Define the three labels and filenames (auto-named)
LABEL_DEFINITIONS = [
    {
        "filename": "miniml-eco-white-vinegar-sorrento-lemon-80x110.pdf",
        "flavour": "Sorrento Lemon Scented",
        "product_line": "Eco White Vinegar Cleaning",
    },
    {
        "filename": "miniml-natural-fabric-softener-pink-dragonfruit-orchid-80x110.pdf",
        "flavour": "Pink Dragonfruit & Orchid",
        "product_line": "Fabric Softener & Conditioner",
    },
    {
        "filename": "miniml-eco-toilet-cleaner-spearmint-peppermint-80x110.pdf",
        "flavour": "Spearmint & Peppermint",
        "product_line": "Eco Toilet Cleaner",
    },
]


def save_individual_labels():
    register_fonts()
    for item in LABEL_DEFINITIONS:
        out_file = OUTPUT_DIR / item["filename"]
        c = canvas.Canvas(str(out_file), pagesize=(LABEL_W, LABEL_H), pageCompression=1)
        draw_single_label(c, 0, 0, item["flavour"], item["product_line"])
        c.showPage()
        c.save()
        print(f"Saved individual label: {out_file}")


def build_three_up_a4():
    register_fonts()
    out_path = OUTPUT_DIR / "three_labels_a4.pdf"
    temp_path = OUTPUT_DIR / "three_labels_a4.tmp.pdf"
    c = canvas.Canvas(str(temp_path), pagesize=(A4_W, A4_H), pageCompression=1)
    c.setTitle("Miniml - 3-up A4 labels")

    # Layout plan:
    margin_left = 15 * mm
    margin_top = 15 * mm

    top_y = A4_H - margin_top - LABEL_H
    left_x = margin_left
    right_x = margin_left + LABEL_W + 10 * mm

    # Top-left
    draw_single_label(c, left_x, top_y, LABEL_DEFINITIONS[0]["flavour"], LABEL_DEFINITIONS[0]["product_line"])

    # Top-right
    draw_single_label(c, right_x, top_y, LABEL_DEFINITIONS[1]["flavour"], LABEL_DEFINITIONS[1]["product_line"])

    # Bottom-center: rotated to fit nicely
    bottom_y = top_y - LABEL_H - 10 * mm
    center_x = (A4_W - LABEL_H) / 2
    c.saveState()
    c.translate(center_x, bottom_y)
    c.rotate(90)
    draw_single_label(c, 0, -LABEL_W, LABEL_DEFINITIONS[2]["flavour"], LABEL_DEFINITIONS[2]["product_line"])
    c.restoreState()

    c.showPage()
    c.save()

    try:
        temp_path.replace(out_path)
        print(f"Saved A4 3-up PDF to: {out_path}")
    except PermissionError:
        print(f"Warning: could not replace {out_path} (file may be open). Temporary file left at: {temp_path}")


def generate_custom_size_pdfs():
    sizes = [
        (120 * mm, 160 * mm, "miniml-eco-white-vinegar-sorrento-lemon-120x160mm.pdf", "Sorrento Lemon Scented", "Eco White Vinegar Cleaning"),
        (80 * mm, 100 * mm, "miniml-natural-fabric-softener-pink-dragonfruit-orchid-80x100mm.pdf", "Pink Dragonfruit & Orchid", "Fabric Softener & Conditioner"),
        (80 * mm, 120 * mm, "miniml-eco-toilet-cleaner-spearmint-peppermint-80x120mm.pdf", "Spearmint & Peppermint", "Eco Toilet Cleaner"),
    ]
    register_fonts()
    for w, h, fname, flavour, product_line in sizes:
        out_file = OUTPUT_DIR / fname
        c = canvas.Canvas(str(out_file), pagesize=(w, h), pageCompression=1)
        draw_single_label(c, 0, 0, flavour, product_line, w=w, h=h)
        c.showPage()
        c.save()
        print(f"Saved custom size label: {out_file}")


if __name__ == "__main__":
    # Save the standard individual labels and combined sheets, plus custom sizes
    save_individual_labels()
    build_three_up_a4()
    generate_custom_size_pdfs()
    build_combined_a4_for_cutting()
