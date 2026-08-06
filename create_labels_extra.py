from PIL import Image, ImageDraw, ImageFont
import os

DPI = 300

def cm_to_px(cm):
    return int(round(cm/2.54 * DPI))

def mm_to_px(mm):
    return int(round(mm/25.4 * DPI))

cwd = r"C:\Users\moonl\OneDrive\Documents\10 - Refill Labels"
assets_bg = os.path.join(cwd, r"tmp\pdfs\rendered\wanaka-miniml-laundry.png")
logo_path = os.path.join(cwd, r"tmp\pdfs\assets\miniml-official-logo.png")
output_dir = os.path.join(cwd, r"output\pdf")
os.makedirs(output_dir, exist_ok=True)

sizes_cm = [(15,15),(15,15),(13,15)]
texts = [
    "Miniml Eco\nWhite Vinegar Cleaning\nSorrento Lemon Scented",
    "Miniml Natural Fabric Softener & Conditioner 5L Refill\nPink Dragonfruit & Orchid Scented\nAll Natural Fabric Softener for Sensitive Skin",
    "Miniml Eco Toilet Cleaner\nSpearmint & Peppermint"
]

# load background
if os.path.exists(assets_bg):
    bg_template = Image.open(assets_bg).convert("RGBA")
else:
    bg_template = Image.new("RGBA", (cm_to_px(15), cm_to_px(15)), (15,18,40,255))
# logo
logo = None
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except:
        logo = None

font_name = r"C:\Windows\Fonts\segoeuib.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else None

label_images = []
for (w_cm,h_cm), text in zip(sizes_cm, texts):
    w_px = cm_to_px(w_cm)
    h_px = cm_to_px(h_cm)
    label = bg_template.copy().resize((w_px, h_px), Image.LANCZOS)
    draw = ImageDraw.Draw(label)

    if logo is not None:
        max_logo_w = int(w_px * 0.35)
        logo_ratio = logo.width / logo.height
        logo_h = int(max_logo_w / logo_ratio)
        logo_resized = logo.resize((max_logo_w, logo_h), Image.LANCZOS)
        logo_x = (w_px - logo_resized.width)//2
        logo_y = int(h_px * 0.06)
        label.paste(logo_resized, (logo_x, logo_y), logo_resized)
        text_y_offset = logo_y + logo_resized.height + int(h_px*0.03)
    else:
        text_y_offset = int(h_px*0.08)

    # font sizing
    base_size = max(18, int(w_px/14))
    lines = text.split('\n')
    longest = max(lines, key=lambda s: len(s))
    fs = int(base_size)
    while fs > 8:
        try:
            ftmp = ImageFont.truetype(font_name, fs) if font_name else ImageFont.load_default()
            bbox = draw.textbbox((0,0), longest, font=ftmp)
            tw = bbox[2]-bbox[0]
            if tw <= w_px * 0.9:
                break
            fs -= 2
        except:
            break
    try:
        font = ImageFont.truetype(font_name, fs) if font_name else ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        line_heights.append(bbox[3]-bbox[1])
    total_text_h = sum(line_heights) + (len(lines)-1)*int(fs*0.3)
    cur_y = text_y_offset + (h_px - text_y_offset - total_text_h)//2

    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0,0), line, font=font)
        tw = bbox[2]-bbox[0]
        x = (w_px - tw)//2
        draw.text((x+2, cur_y+2), line, font=font, fill=(0,0,0,160))
        stroke_w = max(1, int(fs*0.08))
        draw.text((x, cur_y), line, font=font, fill=(255,255,255,255), stroke_width=stroke_w, stroke_fill=(10,10,10,200))
        cur_y += lh + int(fs*0.3)

    pill_w = int(w_px*0.28)
    pill_h = int(h_px*0.10)
    pill_x = w_px - pill_w - int(w_px*0.04)
    pill_y = h_px - pill_h - int(h_px*0.05)
    pill = Image.new('RGBA', (pill_w, pill_h), (255,255,255,220))
    pd = ImageDraw.Draw(pill)
    try:
        pill_font = ImageFont.truetype(font_name, max(10, int(pill_h*0.45))) if font_name else ImageFont.load_default()
    except:
        pill_font = ImageFont.load_default()
    bbox = pd.textbbox((0,0), 'Refill • Reuse', font=pill_font)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    pd.text(((pill_w-tw)//2, (pill_h-th)//2), 'Refill • Reuse', font=pill_font, fill=(20,20,20,255))
    label.paste(pill, (pill_x, pill_y), pill)

    label_images.append(label)

# rotate images
rotated = [img.rotate(-90, expand=True, resample=Image.BICUBIC) for img in label_images]

# 1) Safe margins A4: scale to fit within 10mm margins
A4_w = int(round(210/25.4 * DPI))
A4_h = int(round(297/25.4 * DPI))
margin_px = mm_to_px(10)
avail_w = A4_w - 2*margin_px
avail_h = A4_h - 2*margin_px

spacing = mm_to_px(5)
max_w = max(r.width for r in rotated)
total_h = sum(r.height for r in rotated) + spacing*(len(rotated)-1)

scale = min(1.0, avail_w / max_w, avail_h / total_h)

# create canvas and paste scaled images centered horizontally
canvas = Image.new('RGB', (A4_w, A4_h), (255,255,255))
x = margin_px + (avail_w - int(max_w*scale))//2
y = margin_px
for r in rotated:
    new_w = int(r.width * scale)
    new_h = int(r.height * scale)
    r_s = r.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(r_s.convert('RGB'), (x, y))
    y += new_h + spacing

safe_out = os.path.join(output_dir, 'new-rotated-labels-a4-safemargins.pdf')
canvas.save(safe_out, 'PDF', resolution=DPI)
print('Saved safe margins A4:', safe_out)

# 2) Separate PDFs per label — save at physical size (using DPI metadata)
for idx, img in enumerate(rotated, start=1):
    # determine physical size from original sizes_cm but rotated swaps dimensions
    w_cm, h_cm = sizes_cm[idx-1]
    # when rotated 90°, width/height swap
    page_w_px = cm_to_px(h_cm)
    page_h_px = cm_to_px(w_cm)
    # create page sized canvas and paste image centered (if sizes differ a bit)
    page = Image.new('RGB', (page_w_px, page_h_px), (255,255,255))
    # scale image to fit page if needed
    scale2 = min(1.0, page_w_px / img.width, page_h_px / img.height)
    nw = int(img.width * scale2)
    nh = int(img.height * scale2)
    img_s = img.resize((nw, nh), Image.LANCZOS)
    px = (page_w_px - nw)//2
    py = (page_h_px - nh)//2
    page.paste(img_s.convert('RGB'), (px, py))
    outp = os.path.join(output_dir, f'label-{idx}-rotated.pdf')
    page.save(outp, 'PDF', resolution=DPI)
    print('Saved individual:', outp)

