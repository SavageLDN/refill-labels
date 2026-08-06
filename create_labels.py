from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

DPI = 300

def cm_to_px(cm):
    return int(round(cm/2.54 * DPI))

cwd = r"C:\Users\moonl\OneDrive\Documents\10 - Refill Labels"
assets_bg = os.path.join(cwd, r"tmp\pdfs\rendered\wanaka-miniml-laundry.png")
logo_path = os.path.join(cwd, r"tmp\pdfs\assets\miniml-official-logo.png")
output_dir = os.path.join(cwd, r"output\pdf")
os.makedirs(output_dir, exist_ok=True)

# target sizes in cm
sizes_cm = [(15,15),(15,15),(13,15)]
texts = [
    "Miniml Eco\nWhite Vinegar Cleaning\nSorrento Lemon Scented",
    "Miniml Natural Fabric Softener & Conditioner 5L Refill\nPink Dragonfruit & Orchid Scented\nAll Natural Fabric Softener for Sensitive Skin",
    "Miniml Eco Toilet Cleaner\nSpearmint & Peppermint"
]

# load background if available, otherwise create plain dark background
if os.path.exists(assets_bg):
    bg_template = Image.open(assets_bg).convert("RGBA")
else:
    bg_template = Image.new("RGBA", (cm_to_px(15), cm_to_px(15)), (15,18,40,255))

# load logo if available
logo = None
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception:
        logo = None

# fonts
font_name = r"C:\Windows\Fonts\segoeuib.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else None

label_images = []
for (w_cm,h_cm), text in zip(sizes_cm, texts):
    w_px = cm_to_px(w_cm)
    h_px = cm_to_px(h_cm)
    # start from template and resize/crop to fit
    label = bg_template.copy()
    label = label.resize((w_px, h_px), resample=Image.LANCZOS)
    draw = ImageDraw.Draw(label)

    # paste logo near top center if available
    if logo is not None:
        # scale logo to max 30% width
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

    # prepare text - centered
    # choose font size relative to label
    try:
        # dynamic font sizing
        base_size = max(18, int(w_px/14))
    except Exception:
        base_size = 40

    # Draw multiline text with larger, bold and stroke
    lines = text.split('\n')
    # adjust font size to fit box width
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
        except Exception:
            break
    try:
        font = ImageFont.truetype(font_name, fs) if font_name else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # calculate total text height
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
        # draw shadow
        draw.text((x+2, cur_y+2), line, font=font, fill=(0,0,0,160))
        # main text with white and black stroke for contrast
        stroke_w = max(1, int(fs*0.08))
        draw.text((x, cur_y), line, font=font, fill=(255,255,255,255), stroke_width=stroke_w, stroke_fill=(10,10,10,200))
        cur_y += lh + int(fs*0.3)

    # add small 'Refill' pill bottom-right
    pill_w = int(w_px*0.28)
    pill_h = int(h_px*0.10)
    pill_x = w_px - pill_w - int(w_px*0.04)
    pill_y = h_px - pill_h - int(h_px*0.05)
    pill = Image.new('RGBA', (pill_w, pill_h), (255,255,255,220))
    pd = ImageDraw.Draw(pill)
    try:
        pill_font = ImageFont.truetype(font_name, max(10, int(pill_h*0.45))) if font_name else ImageFont.load_default()
    except Exception:
        pill_font = ImageFont.load_default()
    bbox = pd.textbbox((0,0), 'Refill • Reuse', font=pill_font)
    tw = bbox[2]-bbox[0]
    th = bbox[3]-bbox[1]
    pd.text(((pill_w-tw)//2, (pill_h-th)//2), 'Refill • Reuse', font=pill_font, fill=(20,20,20,255))
    label.paste(pill, (pill_x, pill_y), pill)

    label_images.append(label)

# rotate each as requested (90 degrees clockwise)
rotated = [img.rotate(-90, expand=True, resample=Image.BICUBIC) for img in label_images]

# create A4 canvas (portrait) at 300 DPI
A4_w = int(round(210/25.4 * DPI))
A4_h = int(round(297/25.4 * DPI))
canvas = Image.new('RGB', (A4_w, A4_h), (255,255,255))

# paste them tightly in a single column, starting near top-left — this may crop as requested
x = int( (A4_w - rotated[0].width)//2 ) if rotated[0].width < A4_w else 10
y = 20
for rimg in rotated:
    canvas.paste(rimg.convert('RGB'), (x, y))
    y += rimg.height + 10

out_pdf = os.path.join(output_dir, 'new-rotated-labels-a4.pdf')
canvas.save(out_pdf, 'PDF', resolution=DPI)
print('Saved:', out_pdf)

