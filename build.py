"""Draws entry.png: the world's news of Wednesday 18 November 2026 on one page.

Run once with Pillow installed:  python build.py
main.py (standard library only) then copies the committed entry.png.

The page is drawn at 2x and reduced to 1024 x 1024 for clean edges.
Every shape comes from this file, the bundled OFL fonts (Merriweather, Archivo) and the Natural Earth
country outlines in data/ (public domain, prepared by prep_geo.py).
"""
import io
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

import stories as st

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
S = 2
W = H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
PAPER2 = (238, 232, 219)
INK = (26, 27, 36)
INK2 = (72, 72, 82)
GREY = (120, 118, 112)
RULE = (190, 184, 170)

# Illustration palette: navy, brick red, ochre, teal, cream. No pure black.
NAVY = (30, 44, 86)
NAVY_D = (20, 28, 54)
BRICK = (170, 58, 44)
OCHRE = (222, 160, 52)
TEAL = (30, 122, 126)
CREAM = (248, 240, 222)
OUT = (36, 38, 56)          # outline colour for key shapes

CAT = {
    "POWER": (36, 74, 150),
    "CONFLICT": (178, 34, 34),
    "ECONOMY": (24, 122, 78),
    "CLIMATE": (206, 116, 16),
    "SCIENCE": (98, 66, 168),
    "SOCIETY": (14, 132, 138),
}
CAT_LABEL = {
    "POWER": "POWER & DIPLOMACY", "CONFLICT": "WAR & SECURITY",
    "ECONOMY": "ECONOMY", "CLIMATE": "CLIMATE & DISASTERS",
    "SCIENCE": "SCIENCE & TECH", "SOCIETY": "SOCIETY & CULTURE",
}
CAT_SHORT = {
    "POWER": "POWER", "CONFLICT": "WAR", "ECONOMY": "ECONOMY",
    "CLIMATE": "CLIMATE", "SCIENCE": "SCIENCE", "SOCIETY": "SOCIETY",
}
ORDER = ["POWER", "CONFLICT", "ECONOMY", "CLIMATE", "SCIENCE", "SOCIETY"]

# ------------------------------------------------------------------ fonts
_cache = {}


def font(kind, size, wght=None, wdth=100):
    """serif / serif_i: Merriweather (wght, wdth, opsz). sans: Archivo (wght, wdth)."""
    key = (kind, size, wght, wdth)
    if key in _cache:
        return _cache[key]
    path = {"serif": "Merriweather-VF.ttf", "serif_i": "Merriweather-Italic-VF.ttf",
            "sans": "Archivo-VF.ttf"}[kind]
    f = ImageFont.truetype(os.path.join(FONTS, path), round(size * S))
    if kind == "sans":
        f.set_variation_by_axes([wght or 400, wdth])
    else:
        # optical size 18: the sturdiest cut, with the thickest thin strokes
        f.set_variation_by_axes([wght or 400, wdth, 18])
    _cache[key] = f
    return f


def serif(size, wght=900, wdth=87):
    return font("serif", size, wght, wdth)


def serif_i(size, wght=800, wdth=87):
    return font("serif_i", size, wght, wdth)


def sans(size, wght=400, wdth=100):
    return font("sans", size, wght, wdth)


def cond(size, wght=700):
    return font("sans", size, wght, 75)


# ---------------------------------------------------------------- drawing
img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)
OX = OY = 0                 # origin of the current drawing surface, in page pixels


def p(x, y):
    return (round((x - OX) * S), round((y - OY) * S))


def clipped(fn, x, y, w, h, *args):
    """Run an illustration on its own surface so nothing spills outside its box."""
    global d, OX, OY
    page_d, page_ox, page_oy = d, OX, OY
    sub = Image.new("RGB", (round(w * S), round(h * S)), PAPER)
    d, OX, OY = ImageDraw.Draw(sub), x, y
    try:
        fn(x, y, w, h, *args)
    finally:
        d, OX, OY = page_d, page_ox, page_oy
    img.paste(sub, p(x, y))


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1):
    q1 = p(x1, y1)
    d.rectangle([p(x0, y0), (q1[0] - 1, q1[1] - 1)],
                fill=fill, outline=outline, width=round(width * S))


def rrect(x0, y0, x1, y1, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([p(x0, y0), p(x1, y1)], radius=r * S, fill=fill,
                        outline=outline, width=round(width * S))


def line(pts, fill, width=1):
    d.line([p(*q) for q in pts], fill=fill, width=max(1, round(width * S)), joint="curve")


def poly(pts, fill, outline=None, width=2):
    d.polygon([p(*q) for q in pts], fill=fill, outline=outline,
              width=round(width * S) if outline else 1)


def ellipse(cx, cy, rx, ry, fill=None, outline=None, width=1):
    d.ellipse([p(cx - rx, cy - ry), p(cx + rx, cy + ry)], fill=fill,
              outline=outline, width=round(width * S))


def arc(cx, cy, r, a0, a1, fill, width=1):
    d.arc([p(cx - r, cy - r), p(cx + r, cy + r)], a0, a1, fill=fill, width=round(width * S))


def star(cx, cy, r, fill, n=5, inner=0.4, rot=-90):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(pts, fill)


def mix(a, b, t):
    return tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))


def dark(c, t=0.15):
    return mix(c, (0, 0, 0), t)


def tlen(s, f, tracking=0):
    return f.getlength(s) / S + tracking * max(0, len(s) - 1)


TEXT_SIZES = []
MIN_TEXT = 17


def text(x, y, s, f, fill, anchor="la", tracking=0):
    TEXT_SIZES.append((f.size / S, s))
    if tracking == 0:
        d.text(p(x, y), s, font=f, fill=fill, anchor=anchor)
        return tlen(s, f)
    total = tlen(s, f, tracking)
    if anchor[0] == "r":
        x -= total
    elif anchor[0] == "m":
        x -= total / 2
    for ch in s:
        d.text(p(x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(ch) / S + tracking
    return total


def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tlen(t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, f, fill, maxw, lead):
    for ln in wrap(s, f, maxw):
        text(x, y, ln, f, fill)
        y += lead
    return y


def vgrad(x0, y0, x1, y1, top, bottom):
    h = round((y1 - y0) * S)
    a, b = p(x0, y0), p(x1, y1)
    for i in range(h):
        c = mix(top, bottom, i / max(1, h - 1))
        d.line([(a[0], a[1] + i), (b[0] - 1, a[1] + i)], fill=c)


def glow(cx, cy, r, core, bg, steps=8):
    """Soft glow: concentric discs fading from core colour into the background."""
    for i in range(steps, 0, -1):
        t = i / steps
        ellipse(cx, cy, r * t, r * t, fill=mix(bg, core, (1 - t) ** 1.4 * 0.9 + 0.1))


def badge(x, y, num, cat, r=None, fg=(255, 255, 255)):
    """Numbered circle with a 17 px number; (x, y) is the centre. Returns the radius."""
    s = str(num)
    f = cond(MIN_TEXT, 900)
    r = max(r or 0, tlen(s, f) / 2 + 4, 10.5)
    ellipse(x, y, r, r, fill=CAT[cat])
    text(x, y + 0.5, s, f, fg, anchor="mm")
    return r


def kicker(x, y, s, cat, num=None, color=None, maxw=None):
    """17 px caps line. With a number, a badge leads it. y is the top of the line."""
    c = color or CAT[cat]
    if num is not None:
        r = badge(x + 11, y + 10, num, cat)
        x += 2 * r + 5
        if maxw:
            maxw -= 2 * r + 5
    else:
        rect(x, y + 4, x + 8, y + 16, fill=c)
        x += 13
        if maxw:
            maxw -= 13
    for wd, tr in ((75, 0.8), (75, 0.3), (68, 0.3), (62, 0.2)):
        f = font("sans", MIN_TEXT, 800, wd)
        if not maxw or tlen(s, f, tr) <= maxw:
            break
    text(x, y + 1, s, f, c, tracking=tr)


# --------------------------------------------------------------- geo data
WORLD = json.load(open(os.path.join(HERE, "data", "world.json")))
GULF = json.load(open(os.path.join(HERE, "data", "gulf.json")))


# ------------------------------------------------------------ illustrations
def art_shenzhen(x, y, w, h):
    """Evening arrival at Shenzhen: skyline, airliner, red carpet and the three leaders' flags."""
    hz = y + h * 0.58
    vgrad(x, y, x + w, hz, (255, 204, 132), (236, 112, 86))
    glow(x + w * 0.30, hz - 4, 50, (255, 238, 190), (246, 160, 108), 10)
    ellipse(x + w * 0.30, hz - 4, 16, 16, fill=(255, 242, 206))
    # skyline in two depths, with a tall tapering tower
    rng = random.Random(1118)
    for depth, col in ((0, (214, 120, 118)), (1, (168, 82, 104))):
        bx = x - 4
        while bx < x + w:
            bw = rng.choice([9, 11, 13, 16])
            bh = rng.choice([8, 12, 18, 24, 30]) * (0.7 if depth else 1.0)
            rect(bx, hz - bh, bx + bw, hz, fill=col)
            if depth and rng.random() < 0.6:
                for k in range(int(bh // 6)):
                    if rng.random() < 0.5:
                        rect(bx + 3, hz - bh + 3 + k * 6, bx + 5, hz - bh + 5 + k * 6, fill=(255, 210, 120))
            bx += bw + rng.choice([2, 3, 5])
    tx = x + w * 0.56
    poly([(tx - 7, hz), (tx - 5, hz - 52), (tx, hz - 64), (tx + 5, hz - 52), (tx + 7, hz)], (150, 72, 98))
    # tarmac
    vgrad(x, hz, x + w, y + h, (104, 100, 122), (66, 64, 84))
    for i in range(9):
        xx = x + 8 + i * w / 8
        rect(xx, hz + 9, xx + 16, hz + 11.5, fill=(236, 226, 208))
    # airliner, nose to the right: outline pass first, then fills inset by 1.6 px
    fx0, fx1 = x + w * 0.36, x + w - 8
    fh = 24
    fy = hz - fh - 4
    body = (252, 250, 246)
    o = 1.6
    tail = [(fx0, fy + 3), (fx0 + 34, fy), (fx0 + 34, fy + fh), (fx0 + 14, fy + fh * 0.62)]
    fin = [(fx0 + 6, fy + 3), (fx0 - 8, fy - 30), (fx0 + 10, fy - 30), (fx0 + 46, fy + 1)]
    stab = [(fx0 + 6, fy + 9), (fx0 - 10, fy + 15), (fx0 - 4, fy + 17), (fx0 + 24, fy + 13)]
    for shape in (fin, stab):
        poly(shape, OUT)
    poly(tail, OUT)
    rect(fx0 + 30, fy, fx1 - 16, fy + fh, fill=OUT)
    ellipse(fx1 - 18, fy + fh / 2, 18, fh / 2, fill=OUT)
    poly([(fx0 + 7, fy + 4), (fx0 - 5, fy - 28), (fx0 + 9, fy - 28), (fx0 + 42, fy + 2)], NAVY)
    poly([(fx0 + 6, fy + 10.5), (fx0 - 7, fy + 15), (fx0 - 3, fy + 15.6), (fx0 + 22, fy + 12.5)], dark(NAVY, 0.2))
    poly([(fx0 + o * 1.5, fy + 3 + o), (fx0 + 34, fy + o), (fx0 + 34, fy + fh - o), (fx0 + 14.5, fy + fh * 0.62 - o * 0.6)], body)
    rect(fx0 + 30, fy + o, fx1 - 16, fy + fh - o, fill=body)
    ellipse(fx1 - 18, fy + fh / 2, 18 - o, fh / 2 - o, fill=body)
    rect(fx0 + 24, fy + fh * 0.64, fx1 - 18, fy + fh - o, fill=dark(body, 0.12))
    d.chord([p(fx1 - 36 + o, fy + o), p(fx1 - o, fy + fh - o)], 20, 160, fill=dark(body, 0.12))
    rect(fx0 + 22, fy + fh * 0.50, fx1 - 20, fy + fh * 0.60, fill=NAVY)
    for k in range(15):
        wx = fx0 + 40 + k * (fx1 - fx0 - 92) / 14
        rrect(wx - 2, fy + 5, wx + 2, fy + 10, 2, fill=(255, 196, 88))
    poly([(fx1 - 14, fy + 5), (fx1 - 4, fy + 7), (fx1 - 3, fy + 10), (fx1 - 15, fy + 10)], NAVY_D)
    # landing gear
    for gx, r in ((fx1 - 30, 3.2), (fx0 + (fx1 - fx0) * 0.46, 3.8), (fx0 + (fx1 - fx0) * 0.46 + 9, 3.8)):
        line([(gx, fy + fh - 2), (gx, fy + fh + 3)], OUT, 1.6)
        ellipse(gx, fy + fh + 4, r, r, fill=(48, 48, 60))
    # swept wing with an engine
    wr = fx0 + (fx1 - fx0) * 0.58
    wing = [(wr, fy + fh * 0.66), (wr - 40, fy + fh * 0.66), (wr - 66, fy + fh + 9), (wr - 52, fy + fh + 9)]
    poly(wing, (214, 214, 220), outline=OUT, width=1.6)
    poly([(wr - 40, fy + fh * 0.66), (wr - 30, fy + fh * 0.66), (wr - 52, fy + fh + 9), (wr - 62, fy + fh + 9)], dark((214, 214, 220), 0.15))
    ellipse(wr - 18, fy + fh + 3, 14, 5.6, fill=(196, 198, 208), outline=OUT, width=1.5)
    ellipse(wr - 6, fy + fh + 3, 2.6, 4.2, fill=(60, 62, 76))
    # door, stairs and the red carpet running left to the flags
    door = fx1 - 44
    rect(door - 4, fy + 3, door + 4, fy + 17, fill=(255, 196, 88), outline=OUT, width=1)
    poly([(door - 4, fy + 17), (door + 4, fy + 17), (door - 10, hz + 16), (door - 24, hz + 16)], (232, 228, 222), outline=OUT, width=1.2)
    cy0, cy1 = hz + 16, hz + 26
    poly([(door - 24, cy0), (door - 10, cy0), (door - 6, cy1), (x, cy1 + 10), (x, cy0 + 4)], BRICK)
    poly([(door - 8, cy0 + 4), (door - 6, cy1), (x, cy1 + 10), (x, cy1 + 4)], dark(BRICK, 0.2))
    # three flags in front of the carpet, with name tags
    flags = [("XI", "cn"), ("TRUMP", "us"), ("PUTIN", "ru")]
    for i, (name, kind) in enumerate(flags):
        px_ = x + 14 + i * w * 0.095
        top = y + 12
        line([(px_, top), (px_, y + h - 25)], (60, 56, 64), 1.8)
        fw, fh2 = w * 0.082, w * 0.054
        fx_, fy_ = px_ + 1, top + 1
        if kind == "cn":
            rect(fx_, fy_, fx_ + fw, fy_ + fh2, fill=(222, 41, 16))
            star(fx_ + fw * 0.25, fy_ + fh2 * 0.32, fh2 * 0.20, (255, 222, 0))
        elif kind == "us":
            for k in range(7):
                rect(fx_, fy_ + k * fh2 / 7, fx_ + fw, fy_ + (k + 0.5) * fh2 / 7 + 0.4, fill=(178, 34, 52))
                rect(fx_, fy_ + (k + 0.5) * fh2 / 7, fx_ + fw, fy_ + (k + 1) * fh2 / 7, fill=(255, 255, 255))
            rect(fx_, fy_, fx_ + fw * 0.42, fy_ + fh2 * 0.54, fill=(60, 59, 110))
        else:
            rect(fx_, fy_, fx_ + fw, fy_ + fh2 / 3, fill=(255, 255, 255))
            rect(fx_, fy_ + fh2 / 3, fx_ + fw, fy_ + 2 * fh2 / 3, fill=(0, 57, 166))
            rect(fx_, fy_ + 2 * fh2 / 3, fx_ + fw, fy_ + fh2, fill=(213, 43, 30))
        rect(fx_, fy_, fx_ + fw, fy_ + fh2, outline=OUT, width=1)
    tf = cond(MIN_TEXT, 900)
    xx = x + 6
    for n, _ in flags:
        tw = tlen(n, tf, 0.6) + 10
        rect(xx, y + h - 24, xx + tw, y + h - 3, fill=(255, 255, 255))
        text(xx + 5, y + h - 22.5, n, tf, INK, tracking=0.6)
        xx += tw + 4


def art_gulf(x, y, w, h):
    lon0, lon1, lat0, lat1 = 41.5, 57.5, 24.0, 31.6
    sea = (14, 22, 44)
    rect(x, y, x + w, y + h, fill=sea)

    def P(lo, la):
        return (x + (lo - lon0) / (lon1 - lon0) * w, y + (lat1 - la) / (lat1 - lat0) * h)

    land = (58, 72, 112)
    for item in GULF:
        pts = [P(lo, la) for lo, la in item["ring"]]
        if item["name"] in ("Kuwait", "Bahrain"):
            poly(pts, (74, 90, 132), outline=(150, 166, 206), width=1)
        else:
            poly(pts, land, outline=(86, 100, 140), width=0.6)
    lab = cond(MIN_TEXT, 800)
    for name, lo, la in [("IRAN", 54.0, 30.4), ("IRAQ", 44.0, 31.0), ("SAUDI ARABIA", 45.2, 25.0)]:
        text(*P(lo, la), name, lab, (146, 160, 200), anchor="mm", tracking=1.2)
    text(*P(54.6, 25.4), "THE GULF", cond(MIN_TEXT, 700), (96, 114, 158), anchor="mm", tracking=1.6)
    kw = P(47.52, 29.35)
    bh = P(50.55, 26.05)
    # drone tracks from Iran
    for (slo, sla), tgt, k in [((51.0, 30.7), kw, 0.70), ((52.4, 29.4), kw, 0.66), ((52.9, 27.9), bh, 0.62)]:
        s0 = P(slo, sla)
        steps = 14
        for i in range(steps):
            t0, t1 = i / steps * k, (i + 1) / steps * k
            c = mix(sea, OCHRE, 0.25 + 0.75 * (i / steps))
            line([(s0[0] + (tgt[0] - s0[0]) * t0, s0[1] + (tgt[1] - s0[1]) * t0),
                  (s0[0] + (tgt[0] - s0[0]) * t1, s0[1] + (tgt[1] - s0[1]) * t1)], c, 1.6)
        hx, hy = s0[0] + (tgt[0] - s0[0]) * k, s0[1] + (tgt[1] - s0[1]) * k
        ang = math.atan2(tgt[1] - s0[1], tgt[0] - s0[0])
        sz = 7

        def R(a, r):
            return (hx + r * math.cos(ang + a), hy + r * math.sin(ang + a))

        poly([R(0, sz), R(2.5, sz), R(math.pi, sz * 0.4), R(-2.5, sz)], CREAM, outline=OUT, width=1)
        # interceptor arc from the target and a small burst where they meet
        mx, my = (hx + tgt[0]) / 2, (hy + tgt[1]) / 2 - 10
        pts = []
        for i in range(11):
            t = i / 10
            pts.append(((1 - t) ** 2 * tgt[0] + 2 * (1 - t) * t * mx + t * t * (hx + (tgt[0] - hx) * 0.25),
                        (1 - t) ** 2 * tgt[1] + 2 * (1 - t) * t * my + t * t * (hy + (tgt[1] - hy) * 0.25)))
        line(pts, (150, 210, 214), 1.1)
        bx, by = pts[-1]
        glow(bx, by, 7, (255, 236, 170), sea, 5)
        star(bx, by, 4.5, (255, 246, 214), n=8, inner=0.45)
    for (cx, cy), name, off in [(kw, "KUWAIT", (-14, 8)), (bh, "BAHRAIN", (-26, 6))]:
        ellipse(cx, cy, 5, 5, outline=OCHRE, width=1.6)
        ellipse(cx, cy, 2, 2, fill=OCHRE)
        tf = cond(MIN_TEXT, 900)
        text(cx + off[0], cy + off[1], name, tf, (255, 236, 190), anchor="ma", tracking=1)


def art_eu(x, y, w, h):
    vgrad(x, y, x + w, y + h, (46, 86, 170), (24, 46, 108))
    nx0, ny0, nx1, ny1 = x + 12, y + 8, x + w - 12, y + h - 8
    rrect(nx0 + 3, ny0 + 3, nx1 + 3, ny1 + 3, 5, fill=(16, 30, 74))
    mid = (ny0 + ny1) / 2
    d.rounded_rectangle([p(nx0, ny0), p(nx1, ny1)], radius=5 * S, fill=(0, 87, 183))
    rect(nx0 + 2, mid, nx1 - 2, ny1 - 3, fill=(255, 213, 0))
    rect(nx0 + 2, ny1 - 6, nx1 - 2, ny1 - 2, fill=dark((255, 213, 0)))
    rrect(nx0, ny0, nx1, ny1, 5, outline=OUT, width=2)
    rrect(nx0 + 5, ny0 + 5, nx1 - 5, ny1 - 5, 3, outline=(236, 228, 200), width=0.8)
    # EU star circle disc on the left
    cx, cy, r = nx0 + 30, mid, 22
    ellipse(cx, cy, r, r, fill=(0, 51, 153), outline=OUT, width=1.5)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        star(cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a), 3.2, (255, 204, 0))
    # embossed value
    f = cond(30, 900)
    tx = (cx + r + nx1) / 2 + 2
    text(tx - 1, mid - 18, "\u20ac45bn", f, (236, 236, 236), anchor="ma")
    text(tx + 1.2, mid - 15.8, "\u20ac45bn", f, NAVY_D, anchor="ma")
    text(tx, mid - 17, "\u20ac45bn", f, (255, 255, 255), anchor="ma")


def art_cop(x, y, w, h):
    vgrad(x, y, x + w, y + h, (255, 222, 160), (240, 156, 84))
    cx, cy, r = x + w * 0.22, y + h * 0.52, h * 0.38
    ellipse(cx, cy, r, r, fill=(52, 120, 196))
    d.pieslice([p(cx - r, cy - r), p(cx + r, cy + r)], -60, 120, fill=dark((52, 120, 196)))
    ellipse(cx - r * 0.12, cy - r * 0.05, r * 0.86, r * 0.9, fill=(52, 120, 196))
    poly([(cx - r * .6, cy - r * .5), (cx - r * .1, cy - r * .7), (cx + r * .1, cy - r * .2), (cx - r * .3, cy + r * .1),
          (cx - r * .7, cy - r * .1)], (92, 170, 96))
    poly([(cx + r * .2, cy + r * .1), (cx + r * .7, cy - r * .1), (cx + r * .6, cy + r * .5), (cx + r * .2, cy + r * .7)],
         (92, 170, 96))
    ellipse(cx, cy, r, r, outline=OUT, width=2)
    # thermometer
    tx, ty0, ty1 = cx + r + 14, y + 10, y + h - 18
    rrect(tx - 5, ty0, tx + 5, ty1, 5, fill=CREAM, outline=OUT, width=2)
    rect(tx - 2, ty0 + (ty1 - ty0) * 0.22, tx + 2, ty1, fill=BRICK)
    ellipse(tx, ty1 + 3, 8, 8, fill=BRICK, outline=OUT, width=2)
    # draft torn in two
    dx0, dy0, dw, dh = x + w * 0.56, y + 9, w * 0.36, h - 18
    tear = [(0.50, 0.0), (0.44, 0.15), (0.54, 0.30), (0.45, 0.47), (0.55, 0.62), (0.46, 0.80), (0.52, 1.0)]
    left = [(dx0 - 4, dy0 + 3)] + [(dx0 + dw * a - 4, dy0 + 3 + dh * b) for a, b in tear][::-1][::-1]
    left = [(dx0 - 4, dy0 + 3)] + [(dx0 + dw * a - 4, dy0 + 3 + dh * b) for a, b in tear] + [(dx0 - 4, dy0 + dh + 3)]
    right = [(dx0 + dw * a + 6, dy0 - 3 + dh * b) for a, b in tear] + [(dx0 + dw + 6, dy0 + dh - 3), (dx0 + dw + 6, dy0 - 3)]
    poly(left, (255, 255, 255), outline=OUT, width=1.6)
    poly(right, dark((255, 255, 255), 0.08), outline=OUT, width=1.6)
    for k in range(2):
        yy = dy0 + 10 + k * 7
        line([(dx0 + 2, yy + 3), (dx0 + dw * 0.38 - 4, yy + 3)], (172, 178, 190), 1.3)
        line([(dx0 + dw * 0.62 + 6, yy - 3), (dx0 + dw - 2, yy - 3)], (172, 178, 190), 1.3)
    text(dx0 + dw * 0.22 - 4, dy0 + dh - 22, "DRA", cond(MIN_TEXT, 900), BRICK, anchor="ma", tracking=0.5)
    text(dx0 + dw * 0.80 + 6, dy0 + dh - 28, "FT", cond(MIN_TEXT, 900), BRICK, anchor="ma", tracking=0.5)


def art_voyager(x, y, w, h):
    bg = (26, 20, 66)
    vgrad(x, y, x + w, y + h, (52, 34, 110), (14, 14, 44))
    rng = random.Random(18112026)
    for _ in range(55):
        ellipse(x + rng.random() * w, y + rng.random() * h, 0.6, 0.6, fill=mix((110, 120, 170), (255, 255, 255), rng.random()))
    ex, ey = x + 70, y + 14
    vx, vy = x + w - 34, y + 20
    # faint beam back to Earth
    poly([(vx - 14, vy - 10), (vx - 14, vy + 10), (ex, ey + 1.5), (ex, ey - 1.5)], (62, 50, 130))
    poly([(vx - 14, vy - 4), (vx - 14, vy + 4), (ex, ey + 0.6), (ex, ey - 0.6)], (92, 80, 170))
    glow(ex, ey, 7, (120, 180, 255), bg, 4)
    ellipse(ex, ey, 3.2, 3.2, fill=(80, 150, 240))
    # probe: big dish, bus, booms
    line([(vx + 3, vy + 4), (vx + 26, vy + 18)], (200, 200, 210), 1.4)
    line([(vx - 2, vy + 6), (vx - 10, vy + 22)], (200, 200, 210), 1.4)
    rect(vx - 5, vy + 4, vx + 6, vy + 12, fill=OCHRE, outline=OUT, width=1.2)
    ellipse(vx, vy, 15, 15, fill=(236, 236, 240), outline=OUT, width=2)
    d.pieslice([p(vx - 15, vy - 15), p(vx + 15, vy + 15)], -30, 150, fill=dark((236, 236, 240)))
    ellipse(vx - 1.5, vy - 1.5, 12, 12, fill=(236, 236, 240))
    ellipse(vx, vy, 15, 15, outline=OUT, width=2)
    ellipse(vx, vy, 2.4, 2.4, fill=(170, 170, 182))
    # ruler under the beam
    ry = y + h - 13
    line([(x + 8, ry), (x + w - 8, ry)], (210, 214, 236), 1)
    for xx in (x + 8, x + w - 8):
        line([(xx, ry - 4), (xx, ry + 4)], (210, 214, 236), 1)
    lab = "1 LIGHT-DAY = 25.9bn km"
    tf = cond(MIN_TEXT, 800)
    tw = tlen(lab, tf, 0.3) + 10
    mx = x + w / 2
    rect(mx - tw / 2, ry - 11, mx + tw / 2, ry + 10, fill=(20, 16, 54))
    text(mx, ry - 10, lab, tf, OCHRE, anchor="ma", tracking=0.3)
    text(x + 8, y + 4, "EARTH", cond(MIN_TEXT, 800), (160, 180, 236), tracking=0.6)


def art_markets(x, y, w, h):
    bg = (16, 48, 52)
    vgrad(x, y, x + w, y + h, (20, 58, 62), (12, 36, 40))
    cx, cy, cs = x + w * 0.62, y + h * 0.52, 12
    glow(cx, cy, 44, (90, 200, 120), bg, 9)
    # candles rising out of the chip, up and to the right
    vals = [(0.70, 0.30, 0.52), (0.76, 0.40, 0.62), (0.82, 0.46, 0.70), (0.88, 0.44, 0.80), (0.94, 0.62, 0.94)]
    for i, (fx, lo, hi) in enumerate(vals):
        xx = x + w * fx
        y_lo, y_hi = y + h * (1 - lo) - 6, y + h * (1 - hi)
        c = (70, 200, 120) if i != 3 else (214, 90, 70)
        line([(xx + 4, y_hi - 4), (xx + 4, y_lo + 4)], c, 1)
        rect(xx, y_hi, xx + 8, y_lo, fill=c, outline=dark(c, 0.3), width=1)
    for k in range(4):
        o = -cs + (k + 0.5) * cs * 2 / 4
        line([(cx - cs - 5, cy + o), (cx + cs + 5, cy + o)], (150, 170, 160), 1.4)
        line([(cx + o, cy - cs - 5), (cx + o, cy + cs + 5)], (150, 170, 160), 1.4)
    rrect(cx - cs, cy - cs, cx + cs, cy + cs, 4, fill=(40, 46, 50), outline=OUT, width=2)
    rrect(cx - cs * 0.62, cy - cs * 0.62, cx + cs * 0.62, cy + cs * 0.62, 2, fill=(118, 196, 40))
    for i, (lab, val) in enumerate([("KOSPI", "+2.73%"), ("NIKKEI", "+1.19%")]):
        tf = cond(MIN_TEXT, 900)
        s = lab + " " + val
        tw = tlen(s, tf) + 12
        tx, ty = x + 6, y + 5 + i * 25
        rrect(tx, ty, tx + tw, ty + 21, 10, fill=CREAM)
        text(tx + 6, ty + 1.5, lab, tf, INK)
        text(tx + 6 + tlen(lab + " ", tf), ty + 1.5, val, tf, CAT["ECONOMY"])


ART = {"eu": art_eu, "cop": art_cop, "voyager": art_voyager, "markets": art_markets}


# ---------------------------------------------------------------- icons
def icon(kind, x, y, s, cat):
    c = CAT[cat]
    rrect(x, y, x + s, y + s, 6, fill=c)
    wcol = (255, 255, 255)
    cx, cy = x + s / 2, y + s / 2
    u = s / 40
    if kind == "burst":
        star(cx, cy, 15 * u, wcol, n=10, inner=0.5)
        star(cx, cy, 6 * u, c, n=8, inner=0.5)
    elif kind == "cyclone":
        for i, r in enumerate((14, 10, 6)):
            arc(cx, cy, r * u, 40 + i * 120, 300 + i * 120, wcol, 2.6 * u)
        ellipse(cx, cy, 2.4 * u, 2.4 * u, fill=wcol)
    elif kind == "border":
        for k in range(5):
            line([(cx, y + 6 * u + k * 6.4 * u), (cx, y + 9.5 * u + k * 6.4 * u)], wcol, 2 * u)
        poly([(cx - 4 * u, cy), (cx - 13 * u, cy - 7 * u), (cx - 13 * u, cy + 7 * u)], wcol)
        poly([(cx + 4 * u, cy), (cx + 13 * u, cy - 7 * u), (cx + 13 * u, cy + 7 * u)], wcol)
    elif kind == "target":
        for r in (13, 7):
            arc(cx, cy, r * u, 0, 360, wcol, 2.4 * u)
        line([(cx, cy - 17 * u), (cx, cy + 17 * u)], wcol, 2 * u)
        line([(cx - 17 * u, cy), (cx + 17 * u, cy)], wcol, 2 * u)
    elif kind == "shield":
        poly([(cx, cy - 15 * u), (cx + 12 * u, cy - 10 * u), (cx + 11 * u, cy + 4 * u), (cx, cy + 15 * u),
              (cx - 11 * u, cy + 4 * u), (cx - 12 * u, cy - 10 * u)], wcol)
        poly([(cx, cy - 10 * u), (cx + 7 * u, cy - 7 * u), (cx + 6 * u, cy + 3 * u), (cx, cy + 9 * u)], c)
    elif kind == "ipo":
        poly([(cx, y + 3 * u), (cx + 7 * u, y + 11 * u), (cx - 7 * u, y + 11 * u)], wcol)
        text(cx, y + s - 3, "IPO", cond(MIN_TEXT, 900), wcol, anchor="mb")
    elif kind == "gamepad":
        rrect(cx - 15 * u, cy - 8 * u, cx + 15 * u, cy + 9 * u, 8 * u, fill=wcol)
        rect(cx - 10 * u, cy - 1.5 * u, cx - 3 * u, cy + 1.5 * u, fill=c)
        rect(cx - 8 * u, cy - 3.5 * u, cx - 5 * u, cy + 3.5 * u, fill=c)
        ellipse(cx + 6 * u, cy + 1 * u, 1.8 * u, 1.8 * u, fill=c)
        ellipse(cx + 10 * u, cy - 2 * u, 1.8 * u, 1.8 * u, fill=c)
    elif kind == "advance":
        poly([(x + 7 * u, cy - 5 * u), (x + 22 * u, cy - 5 * u), (x + 22 * u, cy - 12 * u), (x + 34 * u, cy),
              (x + 22 * u, cy + 12 * u), (x + 22 * u, cy + 5 * u), (x + 7 * u, cy + 5 * u)], wcol)
    elif kind == "fence":
        for k in (-10, 10):
            rect(cx + k * u - 2 * u, cy - 12 * u, cx + k * u + 2 * u, cy + 13 * u, fill=wcol)
        rect(cx - 16 * u, cy - 8 * u, cx + 16 * u, cy - 1 * u, fill=wcol)
        rect(cx - 16 * u, cy + 3 * u, cx + 16 * u, cy + 10 * u, fill=wcol)
        for k in range(4):
            xx = cx - 14 * u + k * 9 * u
            poly([(xx, cy - 8 * u), (xx + 4 * u, cy - 8 * u), (xx + 1 * u, cy - 1 * u), (xx - 3 * u, cy - 1 * u)], c)


# ------------------------------------------------------------------ page
# Every piece of text on the page is MIN_TEXT (17 px) or larger, so it stays
# readable when the page is shown 300 px across. build() checks this.
M = 22
R = W - M
LINE = 20                  # line height for 17 px text

SZ_X0, SZ_X1 = M, 600
GF_X0, GF_X1 = 614, R
LEAD_TOP, LEAD_BOT = 111, 368
T2_TOP, T2_BOT = 377, 525
T3_TOP, T3_BOT = 535, 688
BOT_TOP, BOT_BOT = 698, 994


def body(size=MIN_TEXT, wght=600, wdth=75):
    return font("sans", size, wght, wdth)


def fit_line(s, maxw, wght=600, size=MIN_TEXT):
    """The widest Archivo width (75 down to 62) at which s fits on one line."""
    for wd in (75, 70, 66, 62):
        f = font("sans", size, wght, wd)
        if tlen(s, f) <= maxw:
            return f
    raise ValueError("does not fit at %s px: %r" % (size, s))


def header():
    rect(0, 0, W, 6, fill=INK)
    text(M - 1, 12, "THE WORLD IN A DAY", serif(34, 900, 100), INK)
    f = cond(26, 900)
    wtxt, dtxt = "WEDNESDAY ", "18 NOVEMBER 2026"
    dw = tlen(dtxt, f, 0.4)
    text(R, 16, dtxt, f, INK, anchor="ra", tracking=0.4)
    text(R - dw - 10, 16, wtxt.strip(), f, CAT["CONFLICT"], anchor="ra", tracking=0.4)
    text(M, 53, st.JUDGE_NOTE, body(MIN_TEXT, 600, 80), INK2)
    line([(M, 77), (R, 77)], INK, 2)
    line([(M, 80), (R, 80)], INK, 0.7)
    x = M
    f = font("sans", MIN_TEXT, 800, 75)
    for k in ORDER:
        rect(x, 88, x + 10, 98, fill=CAT[k])
        x += 14 + text(x + 14, 83.5, CAT_SHORT[k], f, INK2, tracking=0.4) + 16
    text(R, 83.5, "%d STORIES \u00b7 6 CONTINENTS + SPACE" % st.count(), f, INK2, anchor="ra", tracking=0.4)
    line([(M, 105), (R, 105)], RULE, 1)


def lead_size():
    for s in range(36, 25, -1):
        f = serif(s, 900)
        if (len(wrap(st.SHENZHEN["hed"], f, SZ_X1 - SZ_X0)) <= 2
                and len(wrap(st.GULF["hed"], f, GF_X1 - GF_X0 - 24)) <= 2):
            return s
    return 26


def shenzhen_block(hs):
    L = st.SHENZHEN
    x0, x1, top = SZ_X0, SZ_X1, LEAD_TOP
    w = x1 - x0
    kicker(x0, top, L["kicker"], L["cat"], num=L["num"])
    hf = serif(hs, 900)
    y = top + 25
    for ln in wrap(L["hed"], hf, w):
        text(x0 - 1, y, ln, hf, INK)
        y += hs * 1.05
    y += 3
    text(x0, y, L["dek"], fit_line(L["dek"], w), INK2)
    y += LINE + 6
    aw = 292
    clipped(art_shenzhen, x0, y, aw, LEAD_BOT - y)
    bx = x0 + aw + 10
    rect(bx, y, x1, LEAD_BOT, fill=PAPER2)
    text(bx + 9, y + 3, "ALSO AT APEC", font("sans", MIN_TEXT, 800, 75), CAT["POWER"], tracking=1)
    yy = y + 4 + LINE + 1
    lf_b = font("sans", MIN_TEXT, 800, 75)
    for label, rest in st.ALSO_AT_APEC:
        lw = tlen(label + " ", lf_b)
        text(bx + 9, yy, label, lf_b, INK)
        text(bx + 9 + lw, yy, rest, fit_line(rest, x1 - bx - 18 - lw, 600), INK2)
        yy += LINE + 1
    rect(x0, LEAD_BOT + 3, x1, LEAD_BOT + 6, fill=CAT["POWER"])


def gulf_block(hs):
    L = st.GULF
    x0, x1, top = GF_X0, GF_X1, LEAD_TOP
    w = x1 - x0
    rect(x0, top, x1, LEAD_BOT, fill=(24, 28, 44))
    clipped(art_gulf, x0, top, w, 108)
    y = top + 114
    kicker(x0 + 12, y, L["kicker"], L["cat"], num=L["num"], color=(244, 128, 118), maxw=w - 24)
    y += 26
    hf = serif(hs, 900)
    for ln in wrap(L["hed"], hf, w - 24):
        text(x0 + 12, y, ln, hf, (255, 255, 255))
        y += hs * 1.05
    y += 3
    for ln in wrap(L["dek"], body(MIN_TEXT, 600, 75), w - 24):
        text(x0 + 12, y, ln, body(MIN_TEXT, 600, 75), (226, 228, 238))
        y += LINE
    rect(x0, LEAD_BOT + 3, x1, LEAD_BOT + 6, fill=CAT["CONFLICT"])


def major_row():
    top = T2_TOP
    gap = 14
    cw = (R - M - gap * 3) / 4
    for i, m in enumerate(st.MAJOR):
        x0 = M + i * (cw + gap)
        rect(x0, top, x0 + cw, top + 3, fill=CAT[m["cat"]])
        clipped(ART[m["art"]], x0, top + 3, cw, 54)
        y = top + 62
        kicker(x0, y, m["kicker"], m["cat"], num=m["num"], maxw=cw)
        y += 25
        hf = serif(19, 900)
        for ln in wrap(m["hed"], hf, cw):
            text(x0, y, ln, hf, INK)
            y += 20.5
        y += 2
        text(x0, y, m["fact"], fit_line(m["fact"], cw), INK2)
        if i:
            line([(x0 - gap / 2, top), (x0 - gap / 2, T2_BOT)], RULE, 1)


def key_grid():
    """Twelve stories, each in its own box with its number badge inside."""
    cols, rows = 4, 3
    gap = 10
    cw = (R - M - gap * (cols - 1)) / cols
    rh = (T3_BOT - T3_TOP) / rows
    pad = 4
    for i, k in enumerate(st.KEY):
        r, c = divmod(i, cols)
        x0 = M + c * (cw + gap)
        y0 = T3_TOP + r * rh
        bh = rh - 3
        rrect(x0, y0, x0 + cw, y0 + bh, 4, fill=PAPER2, outline=RULE, width=0.8)
        rect(x0, y0 + 3, x0 + 3, y0 + bh - 3, fill=CAT[k["cat"]])
        ix = x0 + pad + 4
        if "big" in k:
            f = cond(27, 900)
            iw = tlen(k["big"], f)
            text(ix, y0 + 7, k["big"], f, CAT[k["cat"]])
        else:
            iw = 36
            icon(k["icon"], ix, y0 + (bh - 36) / 2, 36, k["cat"])
        tx = ix + iw + 7
        tw = x0 + cw - pad - tx
        kicker(tx, y0 + 3, k["kicker"], k["cat"], num=k["num"], maxw=tw)
        text(tx, y0 + 26, k["hed"], fit_line(k["hed"], tw, 700), INK)


# ------------------------------------------------------------- world map
MAP_LAT0, MAP_LAT1 = 75.0, -48.0


def spread(xs, gap, lo, hi):
    """Push positions apart to at least `gap`, keeping them inside [lo, hi]."""
    xs = list(xs)
    for _ in range(400):
        moved = False
        for i in range(len(xs) - 1):
            ov = gap - (xs[i + 1] - xs[i])
            if ov > 0.01:
                xs[i] -= ov / 2
                xs[i + 1] += ov / 2
                moved = True
        xs = [min(hi, max(lo, v)) for v in xs]
        if not moved:
            break
    return xs


def world_map(x0, top, w):
    h = round(w * (MAP_LAT0 - MAP_LAT1) / 360)
    strip = 26
    y0 = top + strip
    sea = (214, 224, 230)
    landc = (204, 196, 182)

    def P(lo, la):
        return (x0 + (lo + 180) / 360 * w, y0 + (MAP_LAT0 - la) / (MAP_LAT0 - MAP_LAT1) * h)

    def land(ax, ay, aw, ah):
        rect(ax, ay, ax + aw, ay + ah, fill=sea)
        for ring in WORLD:
            poly([P(lo, la) for lo, la in ring], landc, outline=(255, 255, 255), width=0.5)

    clipped(land, x0, y0, w, h)
    rect(x0, y0, x0 + w, y0 + h, outline=RULE, width=1)

    # briefs: small dots
    for cat, (lo, la), _ in st.briefs_flat():
        px_, py_ = P(lo, la)
        ellipse(px_, py_, 2.6, 2.6, fill=(255, 255, 255))
        ellipse(px_, py_, 2.0, 2.0, fill=CAT[cat])

    # numbered stories: dot at the place, number badge on the map's top or bottom edge
    dot_r = {1: 5.0, 2: 4.0, 3: 3.2}
    placed = [(t, s) + P(*s["at"]) for t, s in st.numbered() if s.get("at")]
    north = sorted([q for q in placed if q[1]["at"][1] >= 28], key=lambda q: q[2])
    south = sorted([q for q in placed if q[1]["at"][1] < 28], key=lambda q: q[2])
    for group, by, ly in ((north, top + strip / 2, y0), (south, y0 + h + strip / 2, y0 + h)):
        xs = spread([q[2] for q in group], 25, x0 + 12, x0 + w - 12)
        for (tier, s, px_, py_), bx in zip(group, xs):
            line([(bx, by), (bx, ly), (px_, py_)], INK2, 0.8)
        for (tier, s, px_, py_), bx in zip(group, xs):
            r = dot_r[tier]
            ellipse(px_, py_, r + 1.2, r + 1.2, fill=(255, 255, 255))
            ellipse(px_, py_, r, r, fill=CAT[s["cat"]])
            badge(bx, by, s["num"], s["cat"])

    tf = font("sans", MIN_TEXT, 900, 75)
    title = "WHERE IT HAPPENED"
    tw = tlen(title, tf, 0.8) + 12
    rect(x0, y0, x0 + tw, y0 + 22, fill=INK)
    text(x0 + 6, y0 + 1, title, tf, (255, 255, 255), tracking=0.8)

    # legend: categories, then dot size and Voyager
    ly = y0 + h + strip + 4
    lf = font("sans", MIN_TEXT, 800, 66)
    xx = x0
    for k in ORDER:
        ellipse(xx + 5, ly + 10, 5, 5, fill=CAT[k])
        xx += 12 + text(xx + 12, ly, CAT_SHORT[k], lf, INK2, tracking=0.2) + 9
    ly += LINE + 4
    xx = x0
    for r in (5.0, 4.0, 3.2, 2.0):
        ellipse(xx + r, ly + 10, r, r, fill=(120, 120, 128))
        xx += 2 * r + 3
    text(xx + 3, ly, "Dot size = importance", font("sans", MIN_TEXT, 700, 66), INK2)
    s5 = st.MAJOR[2]
    lab = "VOYAGER 1 \u2192 25.9bn km, OFF MAP"
    vf = font("sans", MIN_TEXT, 900, 66)
    vw = tlen(lab, vf, 0.2) + 34
    bx1 = x0 + w
    rect(bx1 - vw, ly - 1, bx1, ly + 22, fill=(26, 20, 66))
    badge(bx1 - vw + 12, ly + 10.5, s5["num"], s5["cat"])
    text(bx1 - vw + 27, ly + 0.5, lab, vf, OCHRE, tracking=0.2)
    return ly + 22


def briefs(x0, x1, top):
    cols = [[0, 2, 3], [1, 4]]       # Asia + Europe + Africa | Oceania + Americas
    gap = 12
    cw = (x1 - x0 - gap) / 2
    bottom = top
    for ci, idxs in enumerate(cols):
        cx = x0 + ci * (cw + gap)
        y = top
        for bi in idxs:
            region, items = st.BRIEFS[bi]
            hdr = 23
            box_h = hdr + 4 + LINE * len(items) + 4
            rect(cx, y, cx + cw, y + box_h, fill=PAPER2)
            rect(cx, y, cx + cw, y + hdr, fill=INK)
            text(cx + 7, y + 1.5, region, font("sans", MIN_TEXT, 900, 75), (255, 255, 255), tracking=1)
            yy = y + hdr + 4
            for cat, _, s_ in items:
                rect(cx + 6, yy + 6, cx + 13, yy + 13, fill=CAT[cat])
                text(cx + 18, yy, s_, fit_line(s_, cw - 24, 600), INK)
                yy += LINE
            y += box_h + 8
        bottom = max(bottom, y - 8)
    return bottom


def footer():
    line([(M, 998), (R, 998)], INK, 1)
    f = font("sans", MIN_TEXT, 600, 66)
    text(M, 1001, st.SOURCES, f, GREY)
    text(R, 1001, "Illustrations drawn in code", f, GREY, anchor="ra")


def build():
    header()
    hs = lead_size()
    shenzhen_block(hs)
    gulf_block(hs)
    major_row()
    line([(M, 530), (R, 530)], INK, 1.4)
    key_grid()
    line([(M, 692), (R, 692)], INK, 1.4)
    mw = 446
    map_bottom = world_map(M, BOT_TOP, mw)
    brief_bottom = briefs(M + mw + 14, R, BOT_TOP)
    footer()

    small = sorted(set((round(sz, 2), s) for sz, s in TEXT_SIZES if sz < MIN_TEXT - 0.01))
    assert not small, "text below %d px: %r" % (MIN_TEXT, small[:5])
    assert map_bottom <= 994 and brief_bottom <= 994, (map_bottom, brief_bottom)

    out = img.resize((W, H), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "PNG", optimize=True)
    data = buf.getvalue()
    if len(data) > 1048576:
        buf = io.BytesIO()
        out.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(buf, "PNG", optimize=True)
        data = buf.getvalue()
    with open(os.path.join(HERE, "entry.png"), "wb") as fh:
        fh.write(data)
    print("entry.png", len(data), "bytes; lead", hs, "px; smallest text",
          round(min(sz for sz, _ in TEXT_SIZES), 2), "px; map/briefs end", round(map_bottom), round(brief_bottom))


if __name__ == "__main__":
    build()
