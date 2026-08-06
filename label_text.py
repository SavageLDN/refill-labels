from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm


SHADOW = HexColor("#050712")


def draw_shadowed_centred(c, x, y, text, font, size, foreground, offset_mm=0.45):
    """Draw crisp pale lettering with a restrained lower-right night-sky shadow."""
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(SHADOW)
    c.drawCentredString(x + offset_mm * mm, y - offset_mm * mm, text)
    c.setFillColor(foreground)
    c.drawCentredString(x, y, text)
    c.restoreState()
