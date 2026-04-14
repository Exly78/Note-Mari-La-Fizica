"""
Procedurally generate item "cards" for the case simulator so no
copyrighted game art needs to be bundled or downloaded.

Each card = rounded rectangle with the rarity gradient, a stylised
weapon silhouette drawn with PIL primitives, and the item name.

Returns a PIL ImageTk.PhotoImage ready to drop into a tk.Label.
"""
from PIL import Image, ImageDraw, ImageFont, ImageTk

from .theme import COLORS


_FONT_CACHE = {}


def _font(size, bold=False):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    candidates = [
        "seguisb.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    font = None
    for name in candidates:
        try:
            font = ImageFont.truetype(name, size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _rarity_gradient(rarity, size):
    w, h = size
    base = _hex(COLORS[rarity])
    top = tuple(min(255, int(c * 0.55)) for c in base)
    bottom = tuple(max(0, int(c * 0.18)) for c in base)
    img = Image.new("RGB", size, COLORS["panel2"])
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def _draw_silhouette(draw, weapon, box):
    """Cheap abstract weapon silhouettes with PIL primitives."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    w = x1 - x0
    h = y1 - y0
    col = (230, 230, 235)
    shadow = (0, 0, 0, 90)
    weapon_l = weapon.lower()

    if "knife" in weapon_l:
        # curved blade (kukri-ish): polygon
        pts = [
            (cx - w * 0.34, cy + h * 0.08),
            (cx - w * 0.10, cy - h * 0.22),
            (cx + w * 0.22, cy - h * 0.12),
            (cx + w * 0.34, cy + h * 0.02),
            (cx + w * 0.14, cy + h * 0.06),
            (cx - w * 0.02, cy + h * 0.18),
        ]
        draw.polygon(pts, fill=col)
        # handle
        draw.rectangle([cx - w * 0.42, cy + h * 0.05,
                        cx - w * 0.30, cy + h * 0.18],
                       fill=(120, 85, 55))
    elif "awp" in weapon_l:
        # long rifle
        draw.rectangle([cx - w * 0.42, cy - h * 0.04,
                        cx + w * 0.42, cy + h * 0.08], fill=col)
        draw.rectangle([cx - w * 0.38, cy + h * 0.08,
                        cx - w * 0.20, cy + h * 0.22], fill=col)  # stock
        draw.ellipse([cx - w * 0.06, cy - h * 0.18,
                      cx + w * 0.10, cy - h * 0.02], outline=col, width=3)  # scope
    elif "ak" in weapon_l:
        draw.rectangle([cx - w * 0.40, cy - h * 0.02,
                        cx + w * 0.38, cy + h * 0.08], fill=col)
        draw.rectangle([cx - w * 0.40, cy + h * 0.08,
                        cx - w * 0.22, cy + h * 0.22], fill=col)
        draw.polygon([(cx + w * 0.10, cy + h * 0.08),
                      (cx + w * 0.22, cy + h * 0.08),
                      (cx + w * 0.16, cy + h * 0.22)], fill=col)  # magazine
    elif "m4" in weapon_l:
        draw.rectangle([cx - w * 0.38, cy - h * 0.02,
                        cx + w * 0.36, cy + h * 0.06], fill=col)
        draw.rectangle([cx - w * 0.10, cy + h * 0.06,
                        cx + w * 0.02, cy + h * 0.22], fill=col)
    elif "awp" in weapon_l or "sg" in weapon_l or "aug" in weapon_l:
        draw.rectangle([cx - w * 0.36, cy - h * 0.02,
                        cx + w * 0.38, cy + h * 0.08], fill=col)
    elif "glock" in weapon_l or "usp" in weapon_l or "tec" in weapon_l or "beretta" in weapon_l or "deagle" in weapon_l or "eagle" in weapon_l:
        # pistol
        draw.rectangle([cx - w * 0.22, cy - h * 0.02,
                        cx + w * 0.22, cy + h * 0.08], fill=col)
        draw.polygon([(cx - w * 0.02, cy + h * 0.08),
                      (cx + w * 0.12, cy + h * 0.08),
                      (cx + w * 0.04, cy + h * 0.24)], fill=col)
    elif "zeus" in weapon_l:
        draw.rectangle([cx - w * 0.18, cy - h * 0.05,
                        cx + w * 0.18, cy + h * 0.08], fill=col)
        # prongs
        draw.line([cx + w * 0.18, cy - h * 0.02,
                   cx + w * 0.32, cy - h * 0.12], fill=col, width=3)
        draw.line([cx + w * 0.18, cy + h * 0.04,
                   cx + w * 0.32, cy + h * 0.14], fill=col, width=3)
    elif "nova" in weapon_l or "mag" in weapon_l or "sawed" in weapon_l or "xm" in weapon_l:
        # shotgun
        draw.rectangle([cx - w * 0.40, cy - h * 0.02,
                        cx + w * 0.40, cy + h * 0.08], fill=col)
        draw.rectangle([cx - w * 0.40, cy + h * 0.08,
                        cx - w * 0.22, cy + h * 0.22], fill=col)
    else:
        # generic SMG / fallback
        draw.rectangle([cx - w * 0.34, cy - h * 0.02,
                        cx + w * 0.34, cy + h * 0.08], fill=col)
        draw.rectangle([cx - w * 0.20, cy + h * 0.08,
                        cx - w * 0.06, cy + h * 0.22], fill=col)


def render_item_card(weapon, skin, rarity, size=(220, 150)):
    w, h = size
    img = _rarity_gradient(rarity, size)
    draw = ImageDraw.Draw(img, "RGBA")

    # border
    border_col = _hex(COLORS[rarity])
    draw.rectangle([0, 0, w - 1, h - 1], outline=border_col, width=3)

    # silhouette
    _draw_silhouette(draw, weapon, (10, 18, w - 10, h - 46))

    # bottom label strip
    draw.rectangle([0, h - 40, w, h], fill=(0, 0, 0, 140))
    draw.line([(0, h - 40), (w, h - 40)], fill=border_col, width=2)

    name_font = _font(12, bold=True)
    sub_font = _font(10, bold=False)
    draw.text((10, h - 36), skin, fill=(245, 245, 250), font=name_font)
    draw.text((10, h - 20), weapon, fill=(190, 195, 205), font=sub_font)

    return img


def to_photo(pil_img):
    return ImageTk.PhotoImage(pil_img)
