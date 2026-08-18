from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

def draw_shadowed_centred(c, x, y, text, font_name, font_size, text_colour, shadow_colour=HexColor("#0B0813"), offset_mm=0.35):
    c.saveState()
    c.setFont(font_name, font_size)
    
    # Drop Shadow
    c.setFillColor(shadow_colour)
    c.drawCentredString(x + offset_mm * mm, y - offset_mm * mm, text)
    
    # Main Text
    c.setFillColor(text_colour)
    c.drawCentredString(x, y, text)
    c.restoreState()
