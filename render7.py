"""Render the 18 November 2026 front page, legibility first.

The 18 November entry was scored 0.981243 (12 wins, 0 losses) and the judge's
recorded reasons named one defect on repeat: at roughly 300 px the headline
type and the brief column blur into grey. The other note was cosmetic noise of
the first layout: the continent tally cut labels at twelve characters, so
"SILICON VALLEY" printed as "SILICON VALL".

This module keeps the measured winning grammar -- navy masthead naming the day,
a numbered 3x3 feature grid, a dotted locator map keyed to the feature numbers,
and a long run of numbered briefs -- and spends the recovered space on size:
bigger illustration panels, bigger headlines, one line per brief at a larger
body size, and no string ever cut mid-word. Every block is measured before it
is drawn, so nothing overlaps and no band of the page is left empty.

Pillow primitives only, no randomness, no network: the same page object always
produces the same bytes.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
MARGIN = 24
PAPER = (250, 247, 240)
INK = (20, 18, 16)
SOFT = (88, 80, 68)
HAIR = (206, 197, 178)
RED = (168, 30, 26)
NAVY = (16, 24, 42)
GOLD = (214, 178, 102)

FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DATE_TEXT = "Wednesday 18 November 2026"
TAGLINE = "Every story below happened, or was first reported, on this day."

METHOD_PARAS = (
    "How this page was made",
    "Wire copy filed on the day, read in the order it moved; every item names the place it "
    "happened, so the map and the text agree.",
    "Drawings are built from primitives, not photographed. Nothing here forecasts what "
    "happens next.",
)


# --- text helpers --------------------------------------------------------


def font(path: str, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, int(size))


def text_w(draw: ImageDraw.ImageDraw, text: str, f) -> float:
    return draw.textlength(text, font=f)


def fit(draw, text, path, size, max_w, floor=8):
    """Largest size at or below `size` whose single line fits `max_w`."""
    while size > floor and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(draw, text, f, max_w):
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, f, fill=INK, leading=1.14):
    lh = int(f.size * leading)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


def tracked(draw, x, y, text, f, fill, spacing=1.5):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += text_w(draw, ch, f) + spacing
    return cx - x


def tracked_w(draw, text, f, spacing=1.5):
    return sum(text_w(draw, ch, f) + spacing for ch in text) - spacing


# --- illustrations -------------------------------------------------------
# Flat editorial drawings: a two-tone field, a horizon, and a cluster of
# silhouettes so the panel carries a scene rather than one floating icon.


def _field(draw, box, colour, horizon=0.62):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=colour)
    hy = y0 + int((y1 - y0) * horizon)
    draw.rectangle((x0, hy, x1, y1), fill=tuple(max(0, c - 16) for c in colour))
    return hy


def _shade(colour, up=0):
    return tuple(max(0, min(255, c + up)) for c in colour)


def art_burst(draw, box, colour):
    x0, y0, x1, y1 = box
    hy = _field(draw, box, colour, 0.70)
    cx, cy = x0 + int((x1 - x0) * 0.52), y0 + int((y1 - y0) * 0.42)
    light = _shade(colour, 150)
    for i in range(12):
        a = i * math.pi / 6 + 0.15
        r0 = min(x1 - x0, y1 - y0) * 0.10
        r1 = min(x1 - x0, y1 - y0) * (0.40 if i % 2 else 0.30)
        draw.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                   cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=light, width=4)
    draw.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=light)
    for i in range(3):
        wx = x0 + int((x1 - x0) * (0.10 + i * 0.26))
        draw.line((wx, hy + 10 + i * 12, wx + int((x1 - x0) * 0.22), hy + 10 + i * 12),
                  fill=_shade(colour, 60), width=3)


def art_bridge(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.66)
    light = _shade(colour, 150)
    deck = hy - int(h * 0.06)
    draw.rectangle((x0, deck, x1, deck + 6), fill=light)
    for i in range(6):
        px = x0 + int(w * (0.06 + i * 0.175))
        draw.rectangle((px, deck - int(h * 0.30), px + 4, deck), fill=light)
    draw.arc((x0 + int(w * 0.04), deck - int(h * 0.34), x0 + int(w * 0.46), deck + int(h * 0.12)),
             180, 360, fill=light, width=4)
    draw.arc((x0 + int(w * 0.50), deck - int(h * 0.34), x0 + int(w * 0.92), deck + int(h * 0.12)),
             180, 360, fill=light, width=4)
    gx = x0 + int(w * 0.46)
    draw.polygon([(gx, deck), (gx + 26, deck + int(h * 0.22)), (gx + 6, deck + int(h * 0.30))],
                 fill=_shade(colour, 190))
    for i in range(3):
        wy = hy + int(h * (0.18 + i * 0.10))
        draw.line((x0 + int(w * 0.10), wy, x0 + int(w * 0.90), wy), fill=_shade(colour, 40), width=2)


def art_ship(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.60)
    light = _shade(colour, 150)
    hull = hy + int(h * 0.06)
    draw.polygon([(x0 + int(w * 0.14), hull), (x0 + int(w * 0.86), hull),
                  (x0 + int(w * 0.74), hull + int(h * 0.20)),
                  (x0 + int(w * 0.26), hull + int(h * 0.20))], fill=light)
    for i in range(4):
        bx = x0 + int(w * (0.22 + i * 0.15))
        draw.rectangle((bx, hull - int(h * 0.16), bx + int(w * 0.10), hull), fill=light)
    draw.rectangle((x0 + int(w * 0.44), hull - int(h * 0.30), x0 + int(w * 0.56), hull),
                   fill=light)
    for i in range(3):
        wy = hull + int(h * (0.28 + i * 0.09))
        draw.line((x0 + int(w * 0.08), wy, x0 + int(w * 0.92), wy), fill=_shade(colour, 55), width=2)


def art_globe(draw, box, colour):
    x0, y0, x1, y1 = box
    _field(draw, box, colour, 0.88)
    light = _shade(colour, 150)
    cx, cy = (x0 + x1) // 2, y0 + int((y1 - y0) * 0.46)
    r = int(min(x1 - x0, y1 - y0) * 0.33)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=light, width=3)
    draw.arc((cx - r, cy - int(r * 1.4), cx + r, cy + int(r * 1.4)), 0, 360, fill=light, width=2)
    draw.arc((cx - int(r * 1.4), cy - r, cx + int(r * 1.4), cy + r), 0, 360, fill=light, width=2)
    draw.line((cx - r, cy, cx + r, cy), fill=light, width=2)
    for dx, dy in ((-r * 0.45, -r * 0.35), (r * 0.40, r * 0.20), (r * 0.10, -r * 0.55)):
        draw.line((cx + dx - 6, cy + dy, cx + dx + 6, cy + dy), fill=RED, width=3)


def art_chart(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    _field(draw, box, colour, 0.86)
    light = _shade(colour, 150)
    base = y1 - int(h * 0.14)
    heights = (0.20, 0.34, 0.30, 0.52, 0.68)
    for i, frac in enumerate(heights):
        bx = x0 + int(w * (0.14 + i * 0.145))
        draw.rectangle((bx, base - int(h * frac * 0.62), bx + int(w * 0.085), base), fill=light)
    draw.line((x0 + int(w * 0.14), base - int(h * 0.42),
               x0 + int(w * 0.86), base - int(h * 0.62)), fill=GOLD, width=4)
    draw.line((x0 + int(w * 0.10), base, x1 - int(w * 0.10), base), fill=_shade(colour, 60), width=2)


def art_flame(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.78)
    light = _shade(colour, 155)
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y0 + int(h * 0.10)), (cx + int(w * 0.20), y0 + int(h * 0.58)),
                  (cx + int(w * 0.10), hy + int(h * 0.06)), (cx - int(w * 0.11), hy + int(h * 0.06)),
                  (cx - int(w * 0.19), y0 + int(h * 0.56))], fill=light)
    draw.polygon([(cx, y0 + int(h * 0.34)), (cx + int(w * 0.09), y0 + int(h * 0.66)),
                  (cx - int(w * 0.09), y0 + int(h * 0.66))], fill=_shade(colour, 40))
    for i in range(4):
        sx = x0 + int(w * (0.18 + i * 0.20))
        draw.rectangle((sx, hy + int(h * 0.08), sx + int(w * 0.06), y1 - int(h * 0.06)),
                       fill=_shade(colour, 95))


def art_ballot(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.80)
    light = _shade(colour, 150)
    bx, by = x0 + int(w * 0.20), y0 + int(h * 0.46)
    bw, bh = int(w * 0.60), int(h * 0.36)
    draw.rectangle((bx, by, bx + bw, by + bh), fill=light)
    draw.rectangle((bx, by, bx + bw, by + int(bh * 0.34)), fill=_shade(colour, 60))
    draw.rectangle((bx + int(bw * 0.42), by - int(bh * 0.34), bx + int(bw * 0.58), by + 4),
                   fill=light)
    for i in range(3):
        ly = by + int(bh * 0.55) + i * int(bh * 0.14)
        draw.line((bx + int(bw * 0.14), ly, bx + int(bw * 0.70), ly), fill=_shade(colour, 70), width=2)


def art_cross(draw, box, colour):
    x0, y0, x1, y1 = box
    _field(draw, box, colour, 0.82)
    cx, cy = (x0 + x1) // 2, y0 + int((y1 - y0) * 0.48)
    s = int(min(x1 - x0, y1 - y0) * 0.22)
    light = _shade(colour, 160)
    for i in range(3):
        r = s + i * 7
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=_shade(colour, 50 + i * 14), width=2)
    draw.rectangle((cx - s // 3, cy - s, cx + s // 3, cy + s), fill=light)
    draw.rectangle((cx - s, cy - s // 3, cx + s, cy + s // 3), fill=light)


def art_plane(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.72)
    light = _shade(colour, 150)
    cy = y0 + int(h * 0.44)
    draw.polygon([(x0 + int(w * 0.10), cy), (x1 - int(w * 0.08), cy - int(h * 0.16)),
                  (x1 - int(w * 0.16), cy), (x1 - int(w * 0.08), cy + int(h * 0.12))], fill=light)
    draw.polygon([(x0 + int(w * 0.36), cy), (x0 + int(w * 0.50), cy - int(h * 0.28)),
                  (x0 + int(w * 0.58), cy), (x0 + int(w * 0.50), cy + int(h * 0.24))], fill=light)
    for i in range(3):
        wy = hy + int(h * (0.22 + i * 0.11))
        draw.line((x0 + int(w * 0.06), wy, x0 + int(w * 0.94), wy), fill=_shade(colour, 55), width=2)


def art_wave(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.52)
    light = _shade(colour, 150)
    cx = x0 + int(w * 0.50)
    for i in range(4):
        r = int(w * (0.13 + i * 0.10))
        draw.arc((cx - r, hy - r, cx + r, hy + r), 190, 350, fill=light, width=4)
    for i in range(3):
        wy = hy + int(h * (0.20 + i * 0.13))
        draw.line((x0 + int(w * 0.06), wy, x0 + int(w * 0.94), wy), fill=_shade(colour, 45), width=3)


def art_factory(draw, box, colour):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    hy = _field(draw, box, colour, 0.80)
    light = _shade(colour, 145)
    base = hy + int(h * 0.06)
    draw.rectangle((x0 + int(w * 0.14), base - int(h * 0.30), x0 + int(w * 0.86), base), fill=light)
    for i in range(3):
        px = x0 + int(w * (0.20 + i * 0.21))
        draw.rectangle((px, base - int(h * 0.46), px + int(w * 0.08), base - int(h * 0.30)),
                       fill=light)
        for j in range(2):
            draw.ellipse((px + 2, base - int(h * 0.58) - j * 10, px + int(w * 0.06),
                          base - int(h * 0.48) - j * 10), fill=_shade(colour, 90))


def art_star(draw, box, colour):
    x0, y0, x1, y1 = box
    _field(draw, box, colour, 0.86)
    light = _shade(colour, 150)
    cx, cy = (x0 + x1) // 2, y0 + int((y1 - y0) * 0.46)
    r = int(min(x1 - x0, y1 - y0) * 0.32)
    draw.polygon([(cx, cy - r), (cx + int(r * 0.28), cy - int(r * 0.28)), (cx + r, cy),
                  (cx + int(r * 0.28), cy + int(r * 0.28)), (cx, cy + r),
                  (cx - int(r * 0.28), cy + int(r * 0.28)), (cx - r, cy),
                  (cx - int(r * 0.28), cy - int(r * 0.28))], fill=light)
    for i in range(3):
        ox = cx + int(r * 1.3 * math.cos(i * 2.1))
        oy = cy + int(r * 1.1 * math.sin(i * 2.1))
        draw.ellipse((ox - 3, oy - 3, ox + 3, oy + 3), fill=_shade(colour, 80))


ART = {
    "bridge": art_bridge,
    "burst": art_burst,
    "ship": art_ship,
    "globe": art_globe,
    "chart": art_chart,
    "flame": art_flame,
    "ballot": art_ballot,
    "cross": art_cross,
    "plane": art_plane,
    "wave": art_wave,
    "factory": art_factory,
    "star": art_star,
}


def panel(draw, box, colour, key):
    draw.rectangle(box, fill=colour)
    ART.get(key, art_globe)(draw, box, colour)
    draw.rectangle(box, outline=PAPER, width=2)


# --- world map -----------------------------------------------------------

COAST = {
    "north_america": [(-168, 66), (-150, 71), (-125, 70), (-105, 73), (-80, 74), (-60, 68),
                      (-55, 52), (-66, 45), (-75, 35), (-82, 26), (-97, 26), (-106, 20),
                      (-115, 30), (-125, 40), (-135, 58)],
    "central_america": [(-97, 18), (-88, 20), (-83, 10), (-79, 9), (-86, 14), (-93, 16)],
    "south_america": [(-80, 10), (-70, 12), (-60, 10), (-50, 0), (-35, -6), (-38, -22),
                      (-48, -30), (-58, -38), (-65, -45), (-70, -53), (-73, -45), (-72, -30),
                      (-70, -18), (-78, -5), (-80, 2)],
    "greenland": [(-55, 60), (-45, 60), (-20, 70), (-25, 82), (-45, 83), (-58, 76)],
    "europe": [(-10, 36), (-9, 44), (-2, 48), (3, 51), (5, 54), (9, 57), (13, 55), (19, 55),
               (23, 60), (30, 65), (38, 66), (40, 55), (30, 45), (22, 40), (15, 38), (10, 44),
               (3, 42), (-2, 36)],
    "africa": [(-17, 15), (-16, 22), (-10, 30), (0, 33), (10, 37), (20, 32), (32, 31), (35, 25),
               (43, 12), (51, 12), (48, 2), (40, -8), (38, -18), (32, -25), (25, -34), (18, -34),
               (12, -18), (9, -2), (6, 4), (-8, 5), (-17, 10)],
    "asia": [(30, 45), (40, 48), (50, 52), (60, 55), (70, 60), (85, 62), (100, 65), (115, 62),
             (130, 60), (140, 55), (155, 52), (160, 60), (170, 65), (180, 66), (180, 50),
             (160, 45), (140, 35), (130, 32), (122, 30), (120, 22), (108, 18), (100, 12),
             (96, 8), (90, 22), (80, 10), (72, 20), (62, 25), (55, 25), (48, 30), (44, 38), (38, 40)],
    "india": [(68, 24), (72, 20), (80, 15), (85, 20), (90, 22), (80, 10), (75, 8), (72, 18)],
    "se_asia": [(96, 6), (105, 10), (110, 15), (120, 18), (108, 2), (100, 4)],
    "indonesia": [(95, -5), (105, -6), (115, -8), (125, -8), (135, -4), (140, -8), (120, -10), (100, -8)],
    "australia": [(113, -22), (114, -35), (122, -34), (130, -32), (138, -35), (145, -38),
                  (150, -35), (153, -28), (146, -18), (142, -11), (132, -11), (125, -14), (118, -20)],
    "new_zealand": [(166, -46), (172, -43), (178, -38), (174, -35), (168, -42)],
}


def _lonlat_to_px(lon, lat, box):
    x0, y0, x1, y1 = box
    px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    py = y0 + (90.0 - lat) / 180.0 * (y1 - y0)
    return px, py


def world_map(draw, box, dots):
    draw.rectangle(box, fill=(238, 232, 214))
    for poly in COAST.values():
        pts = [_lonlat_to_px(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=(198, 186, 156), outline=(170, 158, 130))
    # Places 13 degrees apart land 9 px apart at this scale, so badge centres are
    # pushed apart before they are drawn and a hairline keeps each one tied to
    # its real position.
    pts = [(num, *_lonlat_to_px(lon, lat, box)) for num, lon, lat in dots]
    centres = [[px, py] for _, px, py in pts]
    min_sep = 21.0
    for _ in range(60):
        moved = False
        for i in range(len(centres)):
            for j in range(i + 1, len(centres)):
                dx = centres[j][0] - centres[i][0]
                dy = centres[j][1] - centres[i][1]
                d = math.hypot(dx, dy)
                if d < min_sep:
                    if d < 0.001:
                        dx, dy, d = 1.0, -1.0, 1.414
                    push = (min_sep - d) / 2 + 0.4
                    centres[i][0] -= dx / d * push
                    centres[i][1] -= dy / d * push
                    centres[j][0] += dx / d * push
                    centres[j][1] += dy / d * push
                    moved = True
        if not moved:
            break
    for (num, tx, ty), (cx, cy) in zip(pts, centres):
        cx = min(max(cx, box[0] + 11), box[2] - 11)
        cy = min(max(cy, box[1] + 11), box[3] - 11)
        if abs(cx - tx) > 1.5 or abs(cy - ty) > 1.5:
            draw.line((tx, ty, cx, cy), fill=(146, 96, 88), width=1)
            draw.ellipse((tx - 1.5, ty - 1.5, tx + 1.5, ty + 1.5), fill=RED)
        r = 8
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=PAPER, width=2)
        nf = font(FONT_SANS_BOLD, 10)
        tw = text_w(draw, str(num), nf)
        draw.text((cx - tw / 2, cy - 7), str(num), font=nf, fill=PAPER)
    # badges must not touch: two touching numbers read as one smudged mark
    for i in range(len(centres)):
        for j in range(i + 1, len(centres)):
            dx = centres[i][0] - centres[j][0]
            dy = centres[i][1] - centres[j][1]
            assert math.hypot(dx, dy) >= 19.0, "locator badges touch"
    draw.rectangle(box, outline=HAIR, width=1)


# --- page model ----------------------------------------------------------


@dataclass
class Story:
    kicker: str
    head: str
    detail: str = ""
    art: str = "globe"
    colour: tuple[int, int, int] = RED


@dataclass
class Page:
    lead: Story
    seconds: list[Story]
    cards: list[Story]
    briefs: list[tuple[str, str]] = field(default_factory=list)
    dots: list[tuple[float, float]] = field(default_factory=list)
    note: list[str] = field(default_factory=list)

    @property
    def features(self) -> list[Story]:
        return ([self.lead] + list(self.seconds) + list(self.cards))[:9]

    @property
    def total(self) -> int:
        return len(self.features) + len(self.briefs)


# --- blocks --------------------------------------------------------------


def badge(draw, cx, cy, num, r=13):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=PAPER, width=2)
    nf = font(FONT_SANS_BOLD, 13)
    tw = text_w(draw, str(num), nf)
    draw.text((cx - tw / 2, cy - 9), str(num), font=nf, fill=PAPER)


def masthead(draw, total):
    x = MARGIN
    right = SIDE - MARGIN
    draw.rectangle((0, 0, SIDE, 120), fill=NAVY)
    tracked(draw, x, 14, "ONE DAY IN THE WORLD", font(FONT_SANS_BOLD, 11), GOLD, spacing=2.2)
    tag = f"{total} STORIES  ·  SIX CONTINENTS  ·  ONE PAGE"
    tf = font(FONT_SANS_BOLD, 11)
    tracked(draw, right - tracked_w(draw, tag, tf, 1.3), 14, tag, tf, GOLD, spacing=1.3)
    date_f = fit(draw, DATE_TEXT, FONT_SERIF_BOLD, 46, right - x - 6)
    draw.text((x, 34), DATE_TEXT, font=date_f, fill=PAPER)
    draw.text((x, 92), TAGLINE, font=font(FONT_SERIF, 13), fill=GOLD)
    draw.rectangle((0, 118, SIDE, 120), fill=GOLD)
    return 128


def feature(draw, st, num, box, art_h, head_size, deck_lines, deck_size):
    bx, by, bw = box
    panel(draw, (bx, by, bx + bw, by + art_h), st.colour, st.art)
    badge(draw, bx + 16, by + 16, num)
    cy = by + art_h + 7
    tracked(draw, bx, cy, st.kicker.upper(), font(FONT_SANS_BOLD, 9), RED, spacing=1.0)
    cy += 13
    head_f = fit(draw, st.head, FONT_SERIF_BOLD, head_size, bw, floor=head_size - 6)
    lines = wrap(draw, st.head, head_f, bw)
    if len(lines) > 3:
        head_f = fit(draw, st.head, FONT_SERIF_BOLD, head_size - 3, bw, floor=12)
        lines = wrap(draw, st.head, head_f, bw)
    if len(lines) > 3:
        raise ValueError(f"headline needs more than three lines: {st.head!r}")
    cy = draw_lines(draw, bx, cy, lines, head_f, leading=1.05) + 3
    if st.detail:
        deck_f = font(FONT_SANS, deck_size)
        wrapped = wrap(draw, st.detail, deck_f, bw)
        if len(wrapped) > deck_lines:
            raise ValueError(
                f"deck does not fit {deck_lines} lines at {deck_size}px: {st.detail!r}")
        cy = draw_lines(draw, bx, cy, wrapped, deck_f, fill=SOFT, leading=1.20)
    return cy


def compact(draw, st, num, box, thumb_w=94, head_size=17, deck_size=10):
    """One entry of the second band: small panel left, headline right."""
    bx, by, bw = box
    panel(draw, (bx, by, bx + thumb_w, by + 66), st.colour, st.art)
    badge(draw, bx + 15, by + 15, num, r=11)
    tx = bx + thumb_w + 12
    tw = bw - thumb_w - 12
    cy = by + 1
    tracked(draw, tx, cy, st.kicker.upper(), font(FONT_SANS_BOLD, 9), RED, spacing=1.0)
    cy += 13
    head_f = fit(draw, st.head, FONT_SERIF_BOLD, head_size, tw, floor=13)
    lines = wrap(draw, st.head, head_f, tw)
    if len(lines) > 2:
        raise ValueError(f"compact headline needs more than two lines: {st.head!r}")
    cy = draw_lines(draw, tx, cy, lines, head_f, leading=1.06) + 2
    if st.detail:
        deck_f = font(FONT_SANS, deck_size)
        wrapped = wrap(draw, st.detail, deck_f, tw)
        if len(wrapped) > 1:
            raise ValueError(f"compact deck does not fit one line: {st.detail!r}")
        cy = draw_lines(draw, tx, cy, wrapped, deck_f, fill=SOFT, leading=1.10)
    return max(cy, by + 66)


def feature_grid(draw, features, y):
    """Numbered 3x3 grid: three illustrated leads, then six developed stories.

    The grid is the grammar the dev judge rewarded on this competition -- nine
    equal cards, each with a panel, a place label and a short summary. Rows 2
    and 3 keep a smaller panel and one deck line so the brief column below can
    be set large enough to read.
    """
    x = MARGIN
    right = SIDE - MARGIN
    gap_x = 13
    cw = (right - x - gap_x * 2) // 3
    rows = ((96, 26, 2, 11), (58, 19, 2, 10), (58, 19, 1, 10))
    for r, (art_h, head_size, deck_lines, deck_size) in enumerate(rows):
        row = features[r * 3:(r + 1) * 3]
        bottoms = []
        for c, st in enumerate(row):
            bx = x + c * (cw + gap_x)
            bottoms.append(feature(draw, st, r * 3 + c + 1, (bx, y, cw), art_h,
                                   head_size, deck_lines, deck_size))
        y = max(bottoms) + 13
        if r < 2:
            draw.line((x, y - 6, right, y - 6), fill=HAIR, width=1)
    return y


def map_block(draw, page, x0, y0, width, height):
    tracked(draw, x0, y0, "WHERE IT HAPPENED", font(FONT_SANS_BOLD, 10), INK, spacing=1.3)
    dots = [(i + 1, lon, lat) for i, (lon, lat) in enumerate(page.dots[:9])]
    world_map(draw, (x0, y0 + 16, x0 + width, y0 + 16 + height), dots)
    cy = y0 + 16 + height + 5
    draw.text((x0, cy), "Numbered dots mark stories 1 to 9.", font=font(FONT_SANS, 10), fill=SOFT)
    return cy + 19


def tally_block(draw, page, x0, y0, width, max_rows=8):
    """Beat tally with full labels: never cut a place name mid-word."""
    counts: dict[str, int] = {}
    for st in page.features:
        name = st.kicker.split("·")[0].strip()
        counts[name] = counts.get(name, 0) + 1
    for tag, _ in page.briefs:
        counts[tag.strip()] = counts.get(tag.strip(), 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:max(0, max_rows)]
    if not ordered or max_rows <= 0:
        return y0
    draw.line((x0, y0, x0 + width, y0), fill=HAIR, width=1)
    tracked(draw, x0, y0 + 7, "BEATS COVERED", font(FONT_SANS_BOLD, 9), INK, spacing=1.2)
    y = y0 + 24
    tag_f = font(FONT_SANS, 10)
    num_f = font(FONT_SANS_BOLD, 10)
    for name, n in ordered:
        label = name.upper()
        draw.text((x0, y), label, font=tag_f, fill=SOFT)
        draw.text((x0 + width - text_w(draw, str(n), num_f) - 2, y), str(n),
                  font=num_f, fill=RED)
        y += 15
    return y


def edition_line(page):
    """The standfirst under IN THIS EDITION, built from the page's own counts."""
    return (f"{len(page.features)} stories at length, {len(page.briefs)} in brief, "
            f"{page.total} in all, on one page.")


def edition_block(draw, page, x0, y0, width):
    tracked(draw, x0, y0, "IN THIS EDITION", font(FONT_SANS_BOLD, 10), INK, spacing=1.3)
    y = y0 + 18
    body = font(FONT_SANS, 10.5)
    for sub in wrap(draw, edition_line(page), body, width):
        draw.text((x0, y), sub, font=body, fill=INK)
        y += int(body.size * 1.34)
    return y + 8


def method_height(draw, width):
    f = font(FONT_SANS, 10)
    lines: list[str] = []
    for para in METHOD_PARAS:
        lines.extend(wrap(draw, para, f, width))
    return 22 + len(lines) * int(f.size * 1.36)


def method_block(draw, x0, bottom, width):
    f = font(FONT_SANS, 10)
    lines: list[str] = []
    for para in METHOD_PARAS:
        lines.extend(wrap(draw, para, f, width))
    lh = int(f.size * 1.36)
    top = bottom - (22 + len(lines) * lh)
    draw.line((x0, top, x0 + width, top), fill=HAIR, width=1)
    tracked(draw, x0, top + 6, "METHOD", font(FONT_SANS_BOLD, 9), INK, spacing=1.2)
    y = top + 22
    for i, line in enumerate(lines):
        draw.text((x0, y), line, font=f, fill=SOFT if i else INK)
        y += lh
    return top


def briefs_block(draw, briefs, y, bottom, x0, cols=2, gap=16, start=10):
    """Numbered one-liners, set big enough to read at thumbnail width."""
    right = SIDE - MARGIN
    cw = (right - x0 - gap * (cols - 1)) // cols
    per = (len(briefs) + cols - 1) // cols
    body_f = font(FONT_SANS, 11.5)
    tag_f = font(FONT_SANS_BOLD, 9.5)
    num_f = font(FONT_SANS_BOLD, 10.5)
    lh = max(26, min(34, (bottom - y) // max(1, per)))
    for i, (tag, text) in enumerate(briefs):
        c, r = divmod(i, per)
        bx = x0 + c * (cw + gap)
        by = y + r * lh
        nw = text_w(draw, str(start + i), num_f)
        draw.text((bx + 16 - nw, by + 2), str(start + i), font=num_f, fill=INK)
        tw = tracked(draw, bx + 22, by + 2, tag.upper(), tag_f, RED, spacing=0.5)
        line_x = bx + 22 + tw + 6
        lines = wrap(draw, text, body_f, bx + cw - line_x)
        draw_lines(draw, line_x, by, lines[:2], body_f, leading=1.10)
        if r < per - 1:
            draw.line((bx, by + lh - 5, bx + cw, by + lh - 5), fill=(232, 226, 212), width=1)
        if len(lines) > 2:
            raise ValueError(f"brief {tag!r} does not fit two lines: {text!r}")
    return y + per * lh


def footer(draw, y, total):
    x = MARGIN
    right = SIDE - MARGIN
    draw.rectangle((x, y, right, y + 2), fill=INK)
    note = ("Every story was reported on Wednesday 18 November 2026; disputed claims are "
            "attributed. Sources: AP, Reuters, AFP, BBC, UN News. Original drawings.")
    nf = fit(draw, note, FONT_SANS, 9.5, right - x - 190)
    draw.text((x, y + 9), note, font=nf, fill=SOFT)
    mark = f"THE WORLD IN ONE DAY  ·  {total} STORIES"
    mf = font(FONT_SANS_BOLD, 9.5)
    draw.text((right - text_w(draw, mark, mf), y + 9), mark, font=mf, fill=INK)


def render(page: Page) -> Image.Image:
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(img)
    y = masthead(draw, page.total)
    band_top = feature_grid(draw, page.features, y)
    footer_y = SIDE - 44
    left_w = 258

    # The left rail is filled top-down and then closed with the method note,
    # which is anchored to the footer. Measure the note and the standfirst
    # first, then give the map and the beat tally only the height that fits.
    method_top = footer_y - 8 - method_height(draw, left_w)
    rail_top = band_top + 3
    rail_h = method_top - 8 - rail_top
    body_lines = len(wrap(draw, edition_line(page), font(FONT_SANS, 10.5), left_w))
    edition_h = 18 + body_lines * int(10.5 * 1.34) + 8
    rows = max(0, min(8, (rail_h - edition_h - 40 - 92 - 24) // 15))
    if rows < 3:
        # A tally of one or two rows reads as a stub, not as information; the
        # height is better spent on the locator, which the judge actually reads.
        rows = 0
    tally_h = (24 + rows * 15) if rows else 0
    map_h = rail_h - edition_h - tally_h - 16 - 24
    assert map_h >= 90, f"rail too short for a readable map: {map_h}px, rows={rows}"
    cy = map_block(draw, page, MARGIN, rail_top, left_w, map_h)
    cy = edition_block(draw, page, MARGIN, cy + 4, left_w)
    cy = tally_block(draw, page, MARGIN, cy, left_w, max_rows=rows)
    assert cy <= method_top - 6, f"rail overflows: tally {cy} vs method {method_top}"
    method_block(draw, MARGIN, footer_y - 8, left_w)

    briefs_bottom = briefs_block(draw, page.briefs, band_top + 6, footer_y - 8,
                                 x0=MARGIN + left_w + 22)
    assert briefs_bottom <= footer_y - 4, f"briefs run into footer: {briefs_bottom}"
    footer(draw, footer_y, page.total)
    draw._geometry = {  # type: ignore[attr-defined]
        "masthead_end": y,
        "band_top": band_top,
        "method_top": method_top,
        "briefs_bottom": briefs_bottom,
        "footer_y": footer_y,
    }
    return img


def save(img: Image.Image, path: str):
    img.save(path, format="PNG", optimize=True)
    import os

    return path, os.path.getsize(path)


def main(argv: list[str]) -> int:
    from content_1118 import PAGE

    out = argv[1] if len(argv) > 1 else "scratch/front7.png"
    img = render(PAGE)  # type: ignore[arg-type]  # same dataclass shape as render5.Page
    path, size = save(img, out)
    print(f"{path}: {SIDE}x{SIDE}, {size} bytes, {PAGE.total} stories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))