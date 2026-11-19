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
MIN_TEXT = 12


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
    for (cx, cy), name, off, fs in [(bh, "BAHRAIN", (-26, 6), MIN_TEXT)]:
        ellipse(cx, cy, 5, 5, outline=OCHRE, width=1.6)
        ellipse(cx, cy, 2, 2, fill=OCHRE)
        tf = cond(fs, 900)
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
    cx, cy, r = nx0 + 26, mid, 19
    ellipse(cx, cy, r, r, fill=(0, 51, 153), outline=OUT, width=1.5)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        star(cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a), 3.2, (255, 204, 0))
    # embossed value (left edge kept clear of the disc)
    f = cond(27, 900)
    tx = max((cx + r + nx1) / 2 + 2, cx + r + 6 + tlen("\u20ac45bn", f) / 2)
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
    text(dx0 + dw * 0.20 - 4, dy0 + dh - 21, "COP31", cond(10, 900), BRICK, anchor="ma", tracking=0.5)
    text(dx0 + dw * 0.80 + 6, dy0 + dh - 27, "SPLIT", cond(10, 900), BRICK, anchor="ma", tracking=0.5)


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


def art_gaza(x, y, w, h):
    vgrad(x, y, x + w, y + h, (236, 214, 176), (210, 176, 132))
    rect(x, y + h - 18, x + w, y + h, fill=(186, 150, 108))
    for i in range(6):
        tx = x + 6 + i * 22
        poly([(tx, y + h - 18), (tx + 9, y + h - 34), (tx + 18, y + h - 18)], (248, 244, 232), outline=OUT, width=1)
    lx = x + w * 0.66
    for k in range(6):
        line([(lx, y + 6 + k * (h - 12) / 6), (lx, y + 6 + k * (h - 12) / 6 + (h - 12) / 12)], (214, 168, 20), 2.4)
    text(x + 6, y + h - 11, "CEASEFIRE LINE", cond(10.5, 900), (120, 80, 10), anchor="la", tracking=0.4)
    # key info, 3 words
    kf = cond(12, 900)
    lab = "TANKS IN GAZA"
    tw = tlen(lab, kf, 0.6) + 12
    rect(x + 6, y + 5, x + 6 + tw, y + 23, fill=(26, 27, 36))
    text(x + 12, y + 6.5, lab, kf, (255, 255, 255), tracking=0.6)
    cx, cy = x + w * 0.80, y + h - 22
    rrect(cx - 26, cy - 6, cx + 26, cy + 8, 6, fill=(86, 92, 76), outline=OUT, width=1.4)
    for k in range(5):
        ellipse(cx - 20 + k * 10, cy + 8, 4.2, 4.2, fill=(52, 54, 46))
    rrect(cx - 12, cy - 16, cx + 10, cy - 5, 4, fill=(104, 110, 92), outline=OUT, width=1.4)
    line([(cx - 12, cy - 11), (cx - 30, cy - 13)], OUT, 2.6)


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


# ------------------------------------------------------- v5 card artwork
REG = {
    "ASIA": (122, 62, 168), "MIDDLE EAST": (198, 96, 20), "EUROPE": (36, 84, 166),
    "AFRICA": (28, 126, 70), "AMERICAS": (188, 40, 40), "OCEANIA": (14, 130, 136),
    "GLOBAL": (80, 88, 100), "SPACE": (44, 40, 120),
}


def mini_map(x, y, w, h, lon0, lon1, lat0, lat1, land, sea, outline=(255, 255, 255)):
    """Equirectangular crop of the Natural Earth world, filled into the box."""
    rect(x, y, x + w, y + h, fill=sea)

    def P(lo, la):
        return (x + (lo - lon0) / (lon1 - lon0) * w, y + (lat1 - la) / (lat1 - lat0) * h)

    for ring in WORLD:
        if any(lon0 - 20 <= lo <= lon1 + 20 and lat0 - 20 <= la <= lat1 + 20 for lo, la in ring):
            poly([P(lo, la) for lo, la in ring], land, outline=outline, width=0.6)
    return P


def drone(cx, cy, s, fill, ang=math.pi):
    def R(a, r):
        return (cx + r * math.cos(ang + a), cy + r * math.sin(ang + a))
    poly([R(0, s), R(2.5, s), R(math.pi, s * 0.35), R(-2.5, s)], fill, outline=OUT, width=1)


def art_voyager_lead(x, y, w, h):
    vgrad(x, y, x + w, y + h, (40, 30, 96), (12, 12, 40))
    rng = random.Random(18112026)
    for _ in range(90):
        ellipse(x + rng.random() * w, y + rng.random() * h, 0.6, 0.6,
                fill=mix((120, 120, 180), (255, 255, 255), rng.random()))
    ex, ey = x + 34, y + h * 0.46
    vx, vy = x + w - 62, y + h * 0.40
    poly([(vx - 18, vy - 12), (vx - 18, vy + 12), (ex, ey + 1.6), (ex, ey - 1.6)], (60, 52, 130))
    poly([(vx - 18, vy - 4), (vx - 18, vy + 4), (ex, ey + 0.6), (ex, ey - 0.6)], (110, 100, 190))
    glow(ex, ey, 14, (120, 180, 255), (24, 20, 66), 6)
    ellipse(ex, ey, 6, 6, fill=(70, 140, 236))
    poly([(ex - 3, ey - 3), (ex + 2, ey - 4), (ex + 3, ey), (ex - 1, ey + 2)], (90, 180, 110))
    line([(vx + 4, vy + 6), (vx + 40, vy + 26)], (200, 200, 210), 1.8)
    line([(vx - 3, vy + 8), (vx - 16, vy + 32)], (200, 200, 210), 1.8)
    rect(vx - 7, vy + 6, vx + 9, vy + 18, fill=OCHRE, outline=OUT, width=1.4)
    ellipse(vx, vy, 24, 24, fill=(236, 236, 240), outline=OUT, width=2)
    d.pieslice([p(vx - 24, vy - 24), p(vx + 24, vy + 24)], -30, 150, fill=dark((236, 236, 240)))
    ellipse(vx - 2, vy - 2, 19.5, 19.5, fill=(236, 236, 240))
    ellipse(vx, vy, 24, 24, outline=OUT, width=2)
    ellipse(vx, vy, 3.4, 3.4, fill=(170, 170, 182))
    tf = cond(12.5, 800)
    text(x + 8, y + 4, "EARTH", tf, (170, 190, 240), anchor="la", tracking=0.8)
    text(vx - 28, y + 4, "VOYAGER 1", tf, (220, 220, 236), anchor="ra", tracking=0.8)
    ry = y + h - 16
    line([(ex, ry), (vx, ry)], (210, 214, 236), 1)
    for xx in (ex, vx):
        line([(xx, ry - 4), (xx, ry + 4)], (210, 214, 236), 1)



def art_drones_ua(x, y, w, h):
    vgrad(x, y, x + w, y + h, (52, 70, 120), (156, 120, 130))
    rect(x, y + h - 14, x + w, y + h, fill=(40, 46, 64))
    rng = random.Random(141)
    for i in range(14):
        cx = x + 14 + (i % 7) * (w - 28) / 6 + rng.uniform(-6, 6)
        cy = y + 9 + (i // 7) * 11 + rng.uniform(-2, 2)
        if i in (3, 9):
            glow(cx, cy, 8, (255, 230, 160), (90, 90, 130), 4)
            star(cx, cy, 6, (255, 240, 200), n=8, inner=0.45)
        else:
            drone(cx, cy, 5, (226, 228, 236))
    f = cond(13, 900)
    s = "141 FIRED \u00b7 126 DOWNED"
    tw = tlen(s, f, 0.4) + 10
    rect(x + 6, y + h - 22, x + 6 + tw, y + h - 5, fill=(255, 255, 255))
    text(x + 11, y + h - 21, s, f, INK, tracking=0.4)


def art_alaska(x, y, w, h):
    P = mini_map(x, y, w, h, -176, -104, 50, 73, (60, 96, 176), (214, 226, 236))
    rect(x + w * 0.50, y, x + w, y + h, fill=(246, 240, 228))
    bx0, bx1 = x + w * 0.54, x + w - 8
    f = cond(20, 900)
    text(bx0, y + 5, "56", f, (36, 74, 150))
    text(bx1, y + 5, "44", f, (178, 34, 34), anchor="ra")
    text((bx0 + bx1) / 2, y + 8, "D \u00b7 R", cond(11, 800), INK2, anchor="ma")
    cols, rows = 20, 5
    cw = (bx1 - bx0) / cols
    for k in range(100):
        c, r = divmod(k, rows)
        col = (36, 74, 150) if k < 56 else (178, 34, 34)
        cx = bx0 + c * cw + cw / 2
        cy = y + 28 + r * ((h - 48) / rows) + 3
        ellipse(cx, cy, 1.7, 1.7, fill=col)
    text(bx0 + (bx1 - bx0) / 2, y + h - 13, "SENATE SEATS", cond(11, 800), INK2, anchor="ma", tracking=0.8)


def art_inflation(x, y, w, h):
    vgrad(x, y, x + w, y + h, (240, 232, 214), (226, 214, 190))
    base = y + h - 16
    bars = [("UK", 3.5, 3.6, (36, 74, 150)), ("EURO AREA", 3.8, 4.0, (0, 51, 153))]
    bw = 26
    for i, (lab, prev, now, col) in enumerate(bars):
        cx = x + w * (0.27 + i * 0.46)
        sc = (h - 40) / 4.2
        rect(cx - bw - 2, base - prev * sc, cx - 2, base, fill=(176, 170, 160))
        rect(cx + 2, base - now * sc, cx + bw + 2, base, fill=col, outline=OUT, width=1)
        text(cx + bw / 2 + 2, base - now * sc - 16, "%.1f%%" % now, cond(14, 900), col, anchor="ma")
        text(cx, base + 2, lab, cond(12, 800), INK2, anchor="ma", tracking=0.6)
    line([(x + 6, base), (x + w - 6, base)], INK2, 1)


def art_cyclone(x, y, w, h):
    P = mini_map(x, y, w, h, 74, 96, 8, 24, (196, 186, 160), (120, 170, 208))
    cx, cy = P(88.6, 18.8)
    for i, r in enumerate((14, 10, 6)):
        arc(cx, cy, r, 30 + i * 110, 290 + i * 110, (255, 255, 255), 3.2)
    ellipse(cx, cy, 3.4, 3.4, fill=(255, 255, 255))
    tx, ty = P(81.6, 16.6)
    dash = 8
    for i in range(0, dash, 2):
        t0, t1 = i / dash, (i + 1) / dash
        line([(cx + (tx - cx) * t0, cy + (ty - cy) * t0), (cx + (tx - cx) * t1, cy + (ty - cy) * t1)], (255, 236, 160), 2)
    ellipse(tx, ty, 4, 4, fill=(178, 34, 34), outline=(255, 255, 255), width=1.2)
    text(x + 6, y + 5, "INDIA", cond(13, 900), INK, tracking=0.6)


def art_sudan(x, y, w, h):
    vgrad(x, y, x + w, y + h, (246, 214, 160), (222, 168, 110))
    rng = random.Random(37)
    bx = x
    while bx < x + w:
        bw = rng.choice([14, 18, 22])
        bh = rng.choice([14, 18, 24])
        rect(bx, y + h - bh, bx + bw - 2, y + h, fill=(176, 120, 86))
        rect(bx + 4, y + h - bh + 4, bx + 8, y + h - bh + 8, fill=(120, 76, 56))
        bx += bw
    drone(x + w * 0.62, y + 20, 10, (70, 70, 84), ang=math.pi * 0.85)
    cx, cy = x + w * 0.30, y + h - 26
    arc(cx, cy, 9, 0, 360, (178, 34, 34), 2)
    line([(cx - 13, cy), (cx + 13, cy)], (178, 34, 34), 1.6)
    line([(cx, cy - 13), (cx, cy + 13)], (178, 34, 34), 1.6)
    f = cond(14, 900)
    text(x + 6, y + 5, "EL OBEID", f, INK, tracking=0.8)
    # key info, 2 words
    kf = cond(15, 900)
    lab = "37 KILLED"
    tw = tlen(lab, kf, 0.6) + 12
    rect(x + w - 6 - tw, y + 5, x + w - 6, y + 24, fill=(178, 34, 34))
    text(x + w - 12, y + 6.5, lab, kf, (255, 255, 255), anchor="ra", tracking=0.6)


def art_gold(x, y, w, h):
    vgrad(x, y, x + w, y + h, (240, 234, 220), (222, 212, 192))
    gold, goldd = (230, 180, 60), (196, 146, 40)
    for i, (gx, gy) in enumerate([(0.10, 0.62), (0.30, 0.62), (0.20, 0.36)]):
        x0, y0 = x + w * gx, y + h * gy
        poly([(x0, y0 + 18), (x0 + 6, y0), (x0 + 34, y0), (x0 + 40, y0 + 18)], gold, outline=OUT, width=1.2)
        poly([(x0 + 28, y0), (x0 + 34, y0), (x0 + 40, y0 + 18), (x0 + 32, y0 + 18)], goldd)
    ax, ay = x + w * 0.38, y + 8
    line([(ax, ay), (ax + 14, ay + 34)], (178, 34, 34), 4)
    poly([(ax + 6, ay + 36), (ax + 22, ay + 30), (ax + 18, ay + 46)], (178, 34, 34))
    text(x + w - 8, y + 8, "$3,800", cond(20, 900), (178, 34, 34), anchor="ra")
    text(x + w - 8, y + 28, "14-MONTH LOW", cond(12, 800), INK2, anchor="ra", tracking=0.5)


def art_gta(x, y, w, h):
    vgrad(x, y, x + w, y + h, (88, 40, 120), (238, 110, 120))
    ellipse(x + w * 0.74, y + h * 0.62, 20, 20, fill=(255, 196, 120))
    rect(x, y + h - 14, x + w, y + h, fill=(40, 22, 60))
    for px_ in (x + w * 0.10, x + w * 0.88):
        line([(px_, y + h - 14), (px_ + 4, y + 22)], (40, 22, 60), 3)
        for a in (-150, -120, -60, -30, -90):
            r = math.radians(a)
            line([(px_ + 4, y + 22), (px_ + 4 + 16 * math.cos(r), y + 22 - 10 * math.sin(-r) + 8)], (40, 22, 60), 2.4)
    cx, cy = x + w * 0.42, y + h * 0.60
    rrect(cx - 26, cy - 13, cx + 26, cy + 14, 13, fill=(250, 250, 250), outline=OUT, width=1.6)
    rect(cx - 18, cy - 2, cx - 8, cy + 3, fill=OUT)
    rect(cx - 15, cy - 5, cx - 11, cy + 6, fill=OUT)
    for bx, by in ((cx + 10, cy + 2), (cx + 16, cy - 3)):
        ellipse(bx, by, 2.6, 2.6, fill=(178, 34, 34))
    text(x + 6, y + 3, "MIDNIGHT IN NZ", cond(10.5, 900), (255, 236, 220), tracking=0.6)
    # key info, 2 words, on a red banner (was white-on-sun, unreadable)
    kf = cond(18, 900)
    lab = "GTA VI"
    tw = tlen(lab, kf, 0.6) + 12
    rect(x + w - 8 - tw, y + 4, x + w - 8, y + 24, fill=(178, 34, 34))
    text(x + w - 14, y + 5.5, lab, kf, (255, 255, 255), anchor="ra", tracking=0.6)


def art_anthropic(x, y, w, h):
    vgrad(x, y, x + w, y + h, (26, 34, 72), (12, 18, 46))
    for gx in range(1, 5):
        line([(x + gx * w / 5, y + 6), (x + gx * w / 5, y + h - 6)], (48, 58, 96), 0.8)
    pts = [(x + 8, y + h - 12), (x + w * 0.28, y + h - 24), (x + w * 0.48, y + h - 16),
           (x + w * 0.68, y + h - 30), (x + w - 10, y + 10)]
    for i in range(len(pts) - 1):
        line([pts[i], pts[i + 1]], (64, 224, 160), 2.4)
    for px_, py_ in pts:
        ellipse(px_, py_, 2.6, 2.6, fill=(255, 255, 255))
    text(x + 8, y + 5, "ANT", cond(15, 900), (255, 255, 255), tracking=0.8)
    text(x + w - 8, y + h - 19, "$83", cond(15, 900), (255, 196, 88), anchor="ra")


def art_border(x, y, w, h):
    P = mini_map(x, y, w, h, 32, 46, 8.5, 18.5, (214, 196, 160), (150, 190, 214))
    bx = x + w * 0.52
    for k in range(7):
        line([(bx, y + 6 + k * (h - 12) / 7), (bx, y + 6 + k * (h - 12) / 7 + (h - 12) / 14)], INK, 2)
    cy = y + h * 0.56
    poly([(bx - 6, cy), (bx - 26, cy - 11), (bx - 26, cy - 4), (bx - 48, cy - 4), (bx - 48, cy + 4),
          (bx - 26, cy + 4), (bx - 26, cy + 11)], (28, 126, 70), outline=OUT, width=1)
    poly([(bx + 6, cy), (bx + 26, cy - 11), (bx + 26, cy - 4), (bx + 48, cy - 4), (bx + 48, cy + 4),
          (bx + 26, cy + 4), (bx + 26, cy + 11)], (150, 90, 40), outline=OUT, width=1)
    f = cond(12.5, 900)
    text(bx - 8, y + 5, "ETHIOPIA", f, INK, anchor="ra", tracking=0.5)
    text(bx + 8, y + 5, "ERITREA", f, INK, tracking=0.5)


ART = {"shenzhen": art_shenzhen, "gulf": art_gulf, "voyager": art_voyager_lead,
       "eu": art_eu, "drones_ua": art_drones_ua, "alaska": art_alaska, "cop": art_cop,
       "inflation": art_inflation, "cyclone": art_cyclone, "sudan": art_sudan,
       "gold": art_gold, "gta": art_gta, "border": art_border, "gaza": art_gaza,
       "anthropic": art_anthropic}


# ------------------------------------------------------------------ page
M = 22
R = W - M


def pin(cx, cy, num, col, r=7.5):
    ellipse(cx, cy, r + 1.3, r + 1.3, fill=(255, 255, 255))
    ellipse(cx, cy, r, r, fill=col)
    s = str(num)
    text(cx, cy + 0.4, s, cond(r * (1.5 if len(s) == 1 else 1.25), 900), (255, 255, 255), anchor="mm")


def header():
    # vertical budget: top bar 0-6, kicker 15-27, title 31-101,
    # subtitle 106-121, region bar 130-150
    rect(0, 0, W, 6, fill=INK)
    # kicker + story count on one baseline (y=15, 12px)
    f = cond(12, 800)
    text(M, 15, "THE DAY IN WORLD NEWS", f, CAT["CONFLICT"], tracking=1.6)
    text(R, 15, "%d STORIES \u00b7 8 REGIONS \u00b7 ONE DAY" % st.count(), f, INK2, anchor="ra", tracking=1.6)
    # title: ink spans exactly M..R (22..1002); letter-spacing -0.01em
    title = "Wednesday 18 November 2026"
    best = None
    for sz in range(90, 50, -1):
        tf = serif(sz, 900, 100)
        w = tlen(title, tf, -0.01 * sz)
        if w <= R - M:
            best = (sz, tf, w)
            break
    sz, tf, w = best
    text(M, 25, title, tf, INK, tracking=-0.01 * sz)
    text(M, 106, st.JUDGE_NOTE, serif_i(15, 600), INK2)
    # region bar: y 130..150, height 20, equal-width segments, 2px gaps, 11px bold
    y = 130
    counts = {}
    for _, s in st.all_stories():
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    regs = [r for r in st.REGIONS if counts.get(r)]
    bw = (R - M) / len(regs)
    bf = cond(11, 900)
    x = M
    for r in regs:
        rect(x, y, x + bw - 2, y + 20, fill=REG[r])
        text(x + bw / 2 - 1, y + 3.5, "%s %d" % (r, counts[r]), bf, (255, 255, 255), anchor="ma", tracking=0.8)
        x += bw
    return y + 20  # 150


def card(x, y, w, art_h, s, num, hsize, dsize, lead):
    col = REG[s["region"]]
    rect(x, y, x + w, y + 3, fill=col)
    clipped(ART[s["art"]], x, y + 3, w, art_h)

    # label row (regular cards use a tighter gap/row so a row is exactly 155px)
    agap = 7 if lead else 5
    yy = y + 3 + art_h + agap
    if lead:
        # number circle 16px, 11px caps kicker, source right-aligned 10px
        pin(x + 8, yy + 7, num, col, r=8)
        kf = cond(11, 800)
        text(x + 21, yy, s["region"] + " \u00b7 " + s["beat"], kf, col, tracking=0.6)
        text(x + w, yy, s["src"], cond(10, 700), GREY, anchor="ra", tracking=0.5)
        if s.get("tag"):
            text(x + w, yy, s["tag"], cond(10, 700), GREY, anchor="ra", tracking=0.5)
    else:
        # level 2: 14px pin, 6px gap, 9.5px region+topic (0.04em tracking),
        # 9px source right-aligned on the same baseline.
        # Row never exceeds the card width: drop the topic word first,
        # keep only the region. The source is never dropped or shortened.
        pin(x + 7, yy + 7, num, col, r=7)
        tf = cond(9.5, 800)
        sf = cond(9, 700)
        lab = s["topic"]
        lw = tlen(lab, tf, 0.38)
        sw = tlen(s["src"], sf)
        if 14 + 6 + lw + sw > w:
            lab = lab.split(" \u00b7 ")[0]
        text(x + 20, yy, lab, tf, col, tracking=0.38)
        text(x + w, yy, s["src"], sf, GREY, anchor="ra")
    yy += 18 if lead else 16
    # headline: exactly 2 lines (lead 26/28, level2 17/21)
    hf = serif(hsize, 900)
    hlead = 28 if lead else 21
    lines = wrap(s["hed"], hf, w)[:2]
    for ln in lines:
        text(x, yy, ln, hf, INK)
        yy += hlead
    yy += 3
    # dek: exactly 2 lines (lead 13.5/16, level2 12.5/15)
    df = sans(dsize, 500, 87.5)
    dlead = 16 if lead else 15
    for ln in wrap(s["dek"], df, w)[:2]:
        text(x, yy, ln, df, INK2)
        yy += dlead
    return yy


def map_block(x0, y0, w):
    # map image only (header drawn by build at y=755); height 84, 1px warm-grey frame
    my = y0
    lat0, lat1 = 64.0, -38.0
    h = round(w * (lat0 - lat1) / 360)  # 84 at w=296
    rect(x0, my, x0 + w, my + h, outline=(200, 190, 175), width=1)
    sea, landc = (214, 224, 230), (204, 196, 182)

    def P(lo, la):
        return (x0 + (lo + 180) / 360 * w, my + (lat0 - la) / (lat0 - lat1) * h)

    def land(ax, ay, aw, ah):
        rect(ax, ay, ax + aw, ay + ah, fill=sea)
        for ring in WORLD:
            poly([P(lo, la) for lo, la in ring], landc, outline=(255, 255, 255), width=0.5)

    clipped(land, x0, my, w, h)
    stories = st.all_stories()
    nlead = len(st.LEAD) + len(st.CARDS)
    pins = [(n, s) + P(*s["at"]) for n, s in stories[:nlead] if s.get("at")]
    pos = [[q[2], q[3]] for q in pins]
    for _ in range(300):
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
                dist = math.hypot(dx, dy) or 0.01
                if dist < 15:
                    push = (15 - dist) / 2
                    ux, uy = dx / dist, dy / dist
                    pos[i][0] -= ux * push; pos[i][1] -= uy * push
                    pos[j][0] += ux * push; pos[j][1] += uy * push
        for q in pos:
            q[0] = min(x0 + w - 8, max(x0 + 8, q[0]))
            q[1] = min(my + h - 8, max(my + 8, q[1]))
    # brief dots: every brief gets a dot. If its true spot sits under a
    # numbered pin (final or true position) or on another dot, nudge it to
    # the nearest free spot on a small ring so it stays visible.
    drawn_dots = []
    for n, s in stories[nlead:]:
        px_, py_ = P(*s["at"])
        cands = [(px_, py_)]
        for rad in (14, 20, 26):
            for ang in range(8):
                a = math.radians(ang * 45)
                cands.append((px_ + rad * math.cos(a), py_ + rad * math.sin(a)))
        spot = None
        for cx, cy in cands:
            if not (x0 + 4 <= cx <= x0 + w - 4 and my + 4 <= cy <= my + h - 4):
                continue
            if any(math.hypot(cx - qx, cy - qy) < 12 for qx, qy in pos):
                continue
            if any(math.hypot(cx - q[2], cy - q[3]) < 12 for q in pins):
                continue
            if any(math.hypot(cx - dx, cy - dy) < 5 for dx, dy in drawn_dots):
                continue
            spot = (cx, cy)
            break
        if not spot:
            continue
        drawn_dots.append(spot)
        ellipse(spot[0], spot[1], 2.4, 2.4, fill=(255, 255, 255))
        ellipse(spot[0], spot[1], 1.8, 1.8, fill=REG[s["region"]])
    for (n, s, tx, ty), (cx, cy) in zip(pins, pos):
        if math.hypot(cx - tx, cy - ty) > 3:
            line([(tx, ty), (cx, cy)], INK2, 0.7)
            ellipse(tx, ty, 1.4, 1.4, fill=INK)
    for (n, s, tx, ty), (cx, cy) in zip(pins, pos):
        pin(cx, cy, n, REG[s["region"]], r=6.6)
    # Voyager is off the map
    lab = "3 \u2192 VOYAGER 1, OFF THE MAP"
    lf = cond(11, 900)
    tw = tlen(lab, lf, 0.4) + 10
    vx, vy = x0 + 4 + tw, my + h - 12
    rect(vx - tw, vy - 8, vx, vy + 8, fill=REG["SPACE"])
    text(vx - tw + 5, vy - 6.5, lab, lf, OCHRE, tracking=0.4)
    return my + h


def utc_strip(y):
    # horizontal 24-hour UTC strip: 8 time points, chips 18px, 11px font,
    # 14px clock icon, evenly spread between M..R (22..1002)
    f_time = cond(11, 900)
    f_lab = sans(11, 600, 80)
    units = []
    total = 0
    for tm, what, reg in st.TIMELINE:
        tw = tlen(tm, f_time) + 10
        lw = tlen(what, f_lab)
        units.append((tm, what, REG[reg], tw, lw))
        total += tw + 4 + lw
    gap = (R - M - 20 - total) / max(len(units) - 1, 1)
    gap = max(gap, 6)
    x = M
    # clock icon (14px) at the start of the strip
    ellipse(x + 7, y + 9, 7, 7, outline=INK, width=1.6)
    line([(x + 7, y + 9), (x + 7, y + 5)], INK, 1.6)
    line([(x + 7, y + 9), (x + 11, y + 9)], INK, 1.6)
    x += 20
    for tm, what, col, tw, lw in units:
        rect(x, y + 1, x + tw, y + 19, fill=col)
        text(x + tw / 2, y + 2.5, tm, f_time, (255, 255, 255), anchor="ma")
        text(x + tw + 4, y + 2.5, what, f_lab, INK)
        x += tw + 4 + lw + gap
    return y + 20


def warn_icon(x, y, s):
    """Warning triangle with an exclamation mark."""
    poly([(x + s / 2, y), (x + s, y + s * 0.9), (x, y + s * 0.9)], (232, 176, 32), outline=INK, width=1.2)
    rect(x + s / 2 - 1, y + s * 0.28, x + s / 2 + 1, y + s * 0.62, fill=INK)
    ellipse(x + s / 2, y + s * 0.72, 1.4, 1.4, fill=INK)


def datecheck_block(x0, y0, w):
    # DATE CHECK box: height 116, 1px warm-grey frame, padding 8,
    # title bold with 12px warning icon, body 10.5px/13
    rect(x0, y0, x0 + w, y0 + 116, outline=(200, 190, 175), width=1)
    px = x0 + 8
    pw = w - 16
    tf = cond(12, 900)
    bf = sans(10.5, 800, 80)
    rf = sans(10.5, 600, 80)
    warn_icon(px, y0 + 8, 12)
    text(px + 18, y0 + 8, st.DATE_CHECK[0][0], tf, INK, tracking=0.8)
    y = y0 + 8 + 19
    line([(px, y), (px + pw, y)], INK, 1.0)
    y += 6
    w = pw
    x0 = px
    for label, body in st.DATE_CHECK[1:]:
        # bold label + regular body, wrapped together
        words = (label + " " + body).split(" ")
        # build lines: label words bold, body words regular
        nlab = len(label.split(" "))
        lines = []
        cur = []
        curw = 0
        for i, wd in enumerate(words):
            f = bf if i < nlab else rf
            ww = tlen(wd + " ", f)
            if cur and curw + ww > w:
                lines.append(cur)
                cur = [(wd, f)]
                curw = ww
            else:
                cur.append((wd, f))
                curw += ww
        if cur:
            lines.append(cur)
        for ln in lines:
            xx = x0
            for wd, f in ln:
                text(xx, y, wd + " ", f, INK)
                xx += tlen(wd + " ", f)
            y += 13
        y += 1
    return y


def timeline_block(x0, y0, w, y_end):
    text(x0, y0, "THE DAY BY THE CLOCK \u00b7 UTC", cond(13, 900), INK, tracking=1.2)
    y = y0 + 19
    line([(x0, y), (x0 + w, y)], INK, 1.2)
    rows = st.TIMELINE
    step = (y_end - y - 4) / len(rows)
    for k, (tm, what, reg) in enumerate(rows):
        yy = y + 4 + k * step
        col = REG[reg]
        rect(x0, yy + 1, x0 + 46, yy + 17, fill=col)
        text(x0 + 23, yy + 2, tm, cond(13, 900), (255, 255, 255), anchor="ma")
        text(x0 + 54, yy + 1.5, what, sans(13, 600, 80), INK)


def also_block(x0, y0, x1, y_end):
    # list only (header drawn by build at y=755); 2 cols x 323, gap 16,
    # 12px font, 15px pitch, badge 18x12 with 8.5px number, 6px badge gap
    stories = st.all_stories()[len(st.LEAD) + len(st.CARDS):]
    half = (len(stories) + 1) // 2
    gap = 16
    cw = (x1 - x0 - gap) / 2
    lead_ = (y_end - y0) / half
    for i, (n, s) in enumerate(stories):
        c, r = divmod(i, half)
        cx = x0 + c * (cw + gap)
        cy = y0 + r * lead_
        col = REG[s["region"]]
        rect(cx, cy + 1, cx + 18, cy + 13, fill=col)
        text(cx + 9, cy + 1.5, str(n), cond(8.5, 900), (255, 255, 255), anchor="ma")
        pf = font("sans", 12, 800, 80)
        pw = tlen(s["place"] + ": ", pf)
        text(cx + 24, cy + 1, s["place"] + ":", pf, INK)
        rest = s["hed"]
        maxw = cw - 24 - pw
        for wd in (80, 75, 70, 66, 62):
            rf = font("sans", 12, 500, wd)
            if tlen(rest, rf) <= maxw:
                break
        text(cx + 24 + pw, cy + 1, rest, rf, INK2)


def footer():
    line([(M, 994), (R, 994)], INK, 1)
    f = sans(10, 500, 80)
    text(M, 999, st.FOOT_NOTE, f, GREY)
    text(R, 999, st.SOURCES, f, GREY, anchor="ra")


def build():
    # vertical budget (exact): header 0-150, UTC strip 156-176,
    # level 1 188-380, divider 392, level 2 rows 405-560 / 574-729,
    # dark divider 741-743, bottom header 755-769, bottom body 776-986,
    # footer line 994, text 999-1009
    y = header()  # -> 150
    y = utc_strip(156)  # -> 176
    # level 1: 3 cols 317/318/317, gap 14; art 72, hed 26/28, dek 13.5/16
    l1w = [317, 318, 317]
    l1x = [M]
    for wd in l1w[:-1]:
        l1x.append(l1x[-1] + wd + 14)
    ends = []
    for i, s in enumerate(st.LEAD):
        ends.append(card(l1x[i], 188, l1w[i], 72, s, i + 1, 26, 13.5, True))
    l1_end = max(ends)
    line([(M, 392), (R, 392)], RULE, 1)
    # level 2: 5 cols 185/185/184/185/185, gap 14; art 56, hed 17/21, dek 12.5/15
    l2w = [185, 185, 184, 185, 185]
    l2x = [M]
    for wd in l2w[:-1]:
        l2x.append(l2x[-1] + wd + 14)
    n = len(st.LEAD) + 1
    row_y = [405, 574]
    for row in range(2):
        ends = []
        for c in range(5):
            s = st.CARDS[row * 5 + c]
            ends.append(card(l2x[c], row_y[row], l2w[c], 56, s, n, 17, 12.5, False))
            n += 1
        l2_end = max(ends)
    line([(M, 741), (R, 741)], INK, 1.4)
    line([(M, 742), (R, 742)], INK, 1.4)
    # bottom header (755-769): map title left, list title right
    ellipse(M + 7, 762, 6, 6, fill=REG["GLOBAL"])
    ellipse(M + 7, 762, 2.4, 2.4, fill=(255, 255, 255))
    text(M + 18, 755, "WHERE IT HAPPENED", cond(13, 900), INK, tracking=1.2)
    lx = M + 296 + 22
    for k in range(3):
        line([(lx + 2, 758 + k * 5), (lx + 14, 758 + k * 5)], INK, 1.6)
    text(lx + 18, 755, "ALSO ON WEDNESDAY 18 NOVEMBER", cond(13, 900), INK, tracking=1.2)
    # bottom body (776-986): map 84 + gap 10 + datecheck 116; list 2 cols
    mw = 296
    map_end = map_block(M, 776, mw)  # -> 860
    dc_end = datecheck_block(M, 870, mw)  # -> 986
    also_block(lx, 776, R, 986)
    footer()

    out = img.resize((W, H), Image.LANCZOS).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=95, optimize=True)
    data = buf.getvalue()
    if len(data) > 1048576:
        buf = io.BytesIO()
        out.save(buf, "JPEG", quality=85, optimize=True)
        data = buf.getvalue()
    with open(os.path.join(HERE, "entry.png"), "wb") as fh:
        fh.write(data)
    print("entry.png", len(data), "bytes; level1 end", round(l1_end), "level2 end", round(l2_end),
          "map end", round(map_end), "datecheck end", round(dc_end),
          "smallest text", round(min(sz for sz, _ in TEXT_SIZES), 1))


if __name__ == "__main__":
    build()
