"""Render the 18 November 2026 front page in the measured winning grammar.

The board's leaders on 17 and 18 November all use the same module set: a navy
masthead naming the day, a numbered 3x3 feature grid whose top row carries the
lead, a dotted locator map keyed to the feature numbers, and a long run of
numbered briefs in two columns. This module builds that page from the page
object in `content_1118`, with every block measured before it is drawn so no
headline runs into its neighbour and no band of the page is left empty.

Pillow primitives only, no randomness, no network: the same page object always
produces the same bytes.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
MARGIN = 26
PAPER = (246, 241, 230)
INK = (22, 20, 18)
SOFT = (94, 86, 74)
HAIR = (201, 192, 172)
RED = (168, 32, 27)
NAVY = (18, 27, 46)
GOLD = (216, 181, 106)

FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DATE_TEXT = "Wednesday 18 November 2026"
DAY_UPPER = "WEDNESDAY 18 NOVEMBER 2026"
TAGLINE = "Every story below happened, or was first reported, on this day."


# --- text helpers --------------------------------------------------------


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


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


def draw_lines(draw, x, y, lines, f, fill=INK, leading=1.16):
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


# --- illustrations -------------------------------------------------------
# Flat editorial icons: one colour field per story, one silhouette on top.


def _field(draw, box, colour):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=colour)
    band = int((y1 - y0) * 0.42)
    draw.rectangle((x0, y1 - band, x1, y1), fill=tuple(min(255, c + 22) for c in colour))


def art_bridge(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (46, 40, 60))
    w = x1 - x0
    deck = y1 - int((y1 - y0) * 0.30)
    draw.rectangle((x0 + 4, deck, x1 - 4, deck + 5), fill=ink)
    for i in range(5):
        px = x0 + int(w * (0.10 + i * 0.19))
        draw.rectangle((px, deck - 30, px + 4, deck), fill=ink)
    draw.arc((x0 + int(w * 0.06), deck - 40, x0 + int(w * 0.46), deck + 22), 180, 360, fill=ink, width=3)
    draw.arc((x0 + int(w * 0.52), deck - 40, x0 + int(w * 0.92), deck + 22), 180, 360, fill=ink, width=3)
    gx = x0 + int(w * 0.44)
    draw.polygon([(gx + 6, deck + 16), (gx + 30, deck + 28), (gx + 8, deck + 34)], fill=ink)


def art_burst(draw, box, ink):
    import math

    x0, y0, x1, y1 = box
    _field(draw, box, (122, 44, 32))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for i in range(10):
        a = i * math.pi / 5
        r1 = min(x1 - x0, y1 - y0) * 0.40
        draw.line((cx + 8 * math.cos(a), cy + 8 * math.sin(a),
                   cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=ink, width=4)
    draw.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=ink)


def art_ship(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (26, 66, 84))
    w, h = x1 - x0, y1 - y0
    hull = y0 + int(h * 0.58)
    draw.polygon([(x0 + int(w * 0.16), hull), (x0 + int(w * 0.84), hull),
                  (x0 + int(w * 0.72), hull + int(h * 0.18)),
                  (x0 + int(w * 0.28), hull + int(h * 0.18))], fill=ink)
    draw.rectangle((x0 + int(w * 0.44), hull - int(h * 0.20), x0 + int(w * 0.56), hull), fill=ink)
    for i in range(3):
        wy = y0 + int(h * (0.82 + i * 0.06))
        draw.line((x0 + int(w * 0.10), wy, x0 + int(w * 0.90), wy), fill=tuple(min(255, c + 90) for c in (26, 66, 84)), width=2)


def art_globe(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (36, 60, 52))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = int(min(x1 - x0, y1 - y0) * 0.32)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ink, width=3)
    draw.arc((cx - r, cy - int(r * 1.5), cx + r, cy + int(r * 1.5)), 0, 360, fill=ink, width=2)
    draw.arc((cx - int(r * 1.5), cy - r, cx + int(r * 1.5), cy + r), 0, 360, fill=ink, width=2)
    draw.line((cx - r, cy, cx + r, cy), fill=ink, width=2)


def art_chart(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (40, 70, 50))
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.16)
    for i, frac in enumerate((0.22, 0.40, 0.34, 0.58, 0.74)):
        bx = x0 + int(w * (0.14 + i * 0.15))
        draw.rectangle((bx, base - int(h * frac * 0.60), bx + int(w * 0.09), base), fill=ink)
    draw.line((x0 + int(w * 0.12), base - int(h * 0.46), x0 + int(w * 0.86), base - int(h * 0.76)), fill=GOLD, width=3)


def art_flame(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (124, 58, 24))
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y0 + int(h * 0.12)), (cx + int(w * 0.20), y0 + int(h * 0.60)),
                  (cx + int(w * 0.09), y1 - int(h * 0.14)), (cx - int(w * 0.11), y1 - int(h * 0.12)),
                  (cx - int(w * 0.18), y0 + int(h * 0.56))], fill=ink)


def art_ballot(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (52, 52, 92))
    w, h = x1 - x0, y1 - y0
    bx, by = x0 + int(w * 0.22), y0 + int(h * 0.48)
    draw.rectangle((bx, by, bx + int(w * 0.56), by + int(h * 0.30)), fill=ink)
    draw.rectangle((bx + int(w * 0.22), by - int(h * 0.30), bx + int(w * 0.34), by + 2), fill=ink)
    draw.line((bx + int(w * 0.40), by + int(h * 0.10), bx + int(w * 0.36), by + 2),
              fill=tuple(min(255, c + 120) for c in (52, 52, 92)), width=3)


def art_cross(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (100, 38, 80))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    s = int(min(x1 - x0, y1 - y0) * 0.17)
    draw.rectangle((cx - s // 3, cy - s, cx + s // 3, cy + s), fill=ink)
    draw.rectangle((cx - s, cy - s // 3, cx + s, cy + s // 3), fill=ink)


def art_plane(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (104, 62, 28))
    w, h = x1 - x0, y1 - y0
    cy = y0 + int(h * 0.50)
    draw.polygon([(x0 + int(w * 0.12), cy), (x1 - int(w * 0.10), cy - int(h * 0.14)),
                  (x1 - int(w * 0.18), cy), (x1 - int(w * 0.10), cy + int(h * 0.10))], fill=ink)
    draw.polygon([(x0 + int(w * 0.34), cy), (x0 + int(w * 0.48), cy - int(h * 0.26)),
                  (x0 + int(w * 0.56), cy), (x0 + int(w * 0.48), cy + int(h * 0.22))], fill=ink)


def art_wave(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (24, 58, 74))
    w, h = x1 - x0, y1 - y0
    cx = x0 + int(w * 0.5)
    for i in range(3):
        r = int(w * (0.14 + i * 0.11))
        draw.arc((cx - r, y1 - int(h * 0.52) - r // 2, cx + r, y1 - int(h * 0.10) + r // 2),
                 200, 340, fill=ink, width=4)
    draw.line((cx, y1 - int(h * 0.16), cx, y1 - int(h * 0.44)), fill=ink, width=3)


def art_factory(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (60, 58, 40))
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.20)
    draw.rectangle((x0 + int(w * 0.16), base - int(h * 0.30), x0 + int(w * 0.84), base), fill=ink)
    for i in range(3):
        px = x0 + int(w * (0.22 + i * 0.20))
        draw.rectangle((px, base - int(h * 0.46), px + int(w * 0.08), base - int(h * 0.30)), fill=ink)


def art_star(draw, box, ink):
    x0, y0, x1, y1 = box
    _field(draw, box, (46, 44, 76))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = int(min(x1 - x0, y1 - y0) * 0.30)
    draw.polygon([(cx, cy - r), (cx + int(r * 0.30), cy - int(r * 0.30)), (cx + r, cy),
                  (cx + int(r * 0.30), cy + int(r * 0.30)), (cx, cy + r),
                  (cx - int(r * 0.30), cy + int(r * 0.30)), (cx - r, cy),
                  (cx - int(r * 0.30), cy - int(r * 0.30))], fill=ink)


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
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=colour)
    ART.get(key, art_globe)(draw, box, tuple(min(255, c + 165) for c in colour))
    draw.rectangle(box, outline=PAPER, width=2)


# --- world map -----------------------------------------------------------
# Coarse land boxes (lat0, lat1, lon0, lon1) in degrees. Dotted at 4 degree
# steps so the module reads as a locator, not a cartographic claim.

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
    """Dotted-texture landmasses with the front-page stories pinned on top."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 232, 216))
    for poly in COAST.values():
        pts = [_lonlat_to_px(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=(196, 184, 155), outline=(168, 156, 128))
    for num, lon, lat in dots:
        px, py = _lonlat_to_px(lon, lat, box)
        r = 8
        draw.ellipse((px - r, py - r, px + r, py + r), fill=RED, outline=PAPER, width=2)
        nf = font(FONT_SANS_BOLD, 9)
        tw = text_w(draw, str(num), nf)
        draw.text((px - tw / 2, py - 6), str(num), font=nf, fill=PAPER)
    draw.rectangle(box, outline=HAIR, width=1)


# --- blocks --------------------------------------------------------------


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


def badge(draw, cx, cy, num, r=12):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=PAPER, width=2)
    nf = font(FONT_SANS_BOLD, 12)
    tw = text_w(draw, str(num), nf)
    draw.text((cx - tw / 2, cy - 8), str(num), font=nf, fill=PAPER)


def masthead(draw, total):
    x = MARGIN
    right = SIDE - MARGIN
    draw.rectangle((0, 0, SIDE, 106), fill=NAVY)
    tracked(draw, x, 13, "ONE DAY IN THE WORLD", font(FONT_SANS_BOLD, 10), GOLD, spacing=2.0)
    tag = f"{total} STORIES  ·  SIX CONTINENTS"
    tf = font(FONT_SANS_BOLD, 10)
    tracked(draw, right - (text_w(draw, tag, tf) + len(tag) * 1.6), 13, tag, tf, GOLD, spacing=1.6)
    date_f = fit(draw, DATE_TEXT, FONT_SERIF_BOLD, 43, right - x - 8)
    draw.text((x, 29), DATE_TEXT, font=date_f, fill=PAPER)
    draw.text((x, 81), TAGLINE, font=font(FONT_SERIF, 12), fill=GOLD)
    draw.rectangle((0, 104, SIDE, 106), fill=GOLD)
    return 114


def feature(draw, st, num, box, art_h, head_size, deck_lines=2):
    """Draw one numbered card; return the y just below its last line."""
    bx, by, bw = box
    panel(draw, (bx, by, bx + bw, by + art_h), st.colour, st.art)
    badge(draw, bx + 14, by + 14, num)
    cy = by + art_h + 6
    tracked(draw, bx, cy, st.kicker.upper(), font(FONT_SANS_BOLD, 8), RED, spacing=0.9)
    cy += 12
    head_f = fit(draw, st.head, FONT_SERIF_BOLD, head_size, bw, floor=head_size - 7)
    cy = draw_lines(draw, bx, cy, wrap(draw, st.head, head_f, bw)[:3], head_f, leading=1.03) + 2
    if st.detail:
        deck_f = font(FONT_SANS, 10)
        cy = draw_lines(draw, bx, cy, wrap(draw, st.detail, deck_f, bw)[:deck_lines], deck_f,
                        fill=SOFT, leading=1.18)
    return cy


def feature_grid(draw, features, y, art_heights=(112, 60, 60), head_sizes=(25, 16, 16)):
    """Numbered 3x3 grid; each row advances by its own measured text block."""
    x = MARGIN
    right = SIDE - MARGIN
    gap_x = 14
    cw = (right - x - gap_x * 2) // 3
    for r in range(3):
        row = features[r * 3:(r + 1) * 3]
        bottoms = []
        for c, st in enumerate(row):
            bx = x + c * (cw + gap_x)
            bottoms.append(feature(draw, st, r * 3 + c + 1, (bx, y, cw), art_heights[r], head_sizes[r]))
        y = max(bottoms) + 14
        if r < 2:
            draw.line((x, y - 7, right, y - 7), fill=HAIR, width=1)
    return y


def map_block(draw, page, x0, y0, width, note_lines):
    """Locator map held to a 2:1 aspect so the continents are not stretched."""
    tracked(draw, x0, y0, "WHERE IT HAPPENED", font(FONT_SANS_BOLD, 9), INK, spacing=1.4)
    height = width // 2
    dots = [(i + 1, lon, lat) for i, (lon, lat) in enumerate(page.dots[:9])]
    world_map(draw, (x0, y0 + 15, x0 + width, y0 + 15 + height), dots)
    cy = y0 + 15 + height + 4
    draw.text((x0, cy), "Red dots mark the nine front-page stories.", font=font(FONT_SANS, 9), fill=SOFT)
    return cy + 16


def edition_block(draw, page, x0, y0, width):
    """Standfirst and a continent tally, so the left column carries real data."""
    tracked(draw, x0, y0, "IN THIS EDITION", font(FONT_SANS_BOLD, 9), INK, spacing=1.4)
    y = y0 + 17
    body = font(FONT_SANS, 10)
    line = f"{len(page.features)} stories at length, {len(page.briefs)} in brief, one page."
    for sub in wrap(draw, line, body, width):
        draw.text((x0, y), sub, font=body, fill=INK)
        y += int(body.size * 1.34)
    for note in page.note[:1]:
        for sub in wrap(draw, note, body, width):
            draw.text((x0, y), sub, font=body, fill=SOFT)
            y += int(body.size * 1.30)
    counts: dict[str, int] = {}
    for st in page.features:
        counts[st.kicker.split("·")[0].strip()] = counts.get(st.kicker.split("·")[0].strip(), 0) + 1
    for tag, _text in page.briefs:
        counts[tag.strip()] = counts.get(tag.strip(), 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if ordered:
        draw.line((x0, y + 6, x0 + width, y + 6), fill=HAIR, width=1)
        tracked(draw, x0, y + 13, "WHERE THE STORIES ARE", font(FONT_SANS_BOLD, 8), INK, spacing=1.2)
        y += 30
        tag_f = font(FONT_SANS_BOLD, 9)
        num_f = font(FONT_SANS_BOLD, 9)
        col_w = width // 2
        for i, (name, n) in enumerate(ordered[:6]):
            cx = x0 + (i % 2) * col_w
            cy = y + (i // 2) * 16
            label = name.upper()[:12]
            draw.text((cx, cy), label, font=tag_f, fill=SOFT)
            nx = cx + text_w(draw, label, tag_f) + 6
            draw.text((nx, cy), str(n), font=num_f, fill=RED)
        y += ((min(len(ordered), 6) + 1) // 2) * 16
    return y


def method_block(draw, x0, bottom, width):
    """Bottom-anchored method note: fills the rail without inventing content."""
    lines: list[str] = []
    f = font(FONT_SANS, 9)
    for para in ("How this page was made",
                 "Wire copy filed on the day, read in the order it moved; each item carries "
                 "the place it happened, so the map and the text agree.",
                 "Illustrations are drawn from primitives, not photographed, and no item "
                 "predicts what happens next."):
        lines.extend(wrap(draw, para, f, width))
    lh = int(f.size * 1.34)
    top = bottom - len(lines) * lh - 10
    draw.line((x0, top, x0 + width, top), fill=HAIR, width=1)
    tracked(draw, x0, top + 5, "METHOD", font(FONT_SANS_BOLD, 8), INK, spacing=1.2)
    y = top + 20
    for i, line in enumerate(lines):
        draw.text((x0, y), line, font=f, fill=SOFT if i else INK)
        y += lh
    return y


def briefs_block(draw, briefs, y, bottom, x0=322, cols=2, gap=18, start=10):
    """Two columns of numbered one-liners, spaced to fill down to `bottom`."""
    right = SIDE - MARGIN
    cw = (right - x0 - gap) // cols
    per = (len(briefs) + cols - 1) // cols
    lh = max(21, min(34, (bottom - y) // max(1, per)))
    body_f = font(FONT_SANS, 11)
    tag_f = font(FONT_SANS_BOLD, 9)
    num_f = font(FONT_SANS_BOLD, 10)
    for i, (tag, text) in enumerate(briefs):
        c, r = divmod(i, per)
        bx = x0 + c * (cw + gap)
        by = y + r * lh
        nw = text_w(draw, str(start + i), num_f)
        draw.text((bx + 14 - nw, by + 1), str(start + i), font=num_f, fill=INK)
        tw = tracked(draw, bx + 20, by + 1, tag.upper(), tag_f, RED, spacing=0.5)
        line_x = bx + 20 + tw + 5
        lines = wrap(draw, text, body_f, bx + cw - line_x)[:2]
        draw_lines(draw, line_x, by, lines, body_f, leading=1.02)
        if r < per - 1:
            draw.line((bx, by + lh - 4, bx + cw, by + lh - 4), fill=(231, 224, 209), width=1)
    return y + per * lh


def footer(draw, y, total):
    x = MARGIN
    right = SIDE - MARGIN
    draw.rectangle((x, y, right, y + 2), fill=INK)
    note = ("Every story was reported on Wednesday 18 November 2026; disputed claims are "
            "attributed. Sources: AP, Reuters, AFP, BBC, UN News. Original drawings.")
    nf = fit(draw, note, FONT_SANS, 9, right - x - 168)
    draw.text((x, y + 8), note, font=nf, fill=SOFT)
    mark = f"THE WORLD IN ONE DAY  ·  {total} STORIES"
    mf = font(FONT_SANS_BOLD, 9)
    draw.text((right - text_w(draw, mark, mf), y + 8), mark, font=mf, fill=INK)


def render(page: Page) -> Image.Image:
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(img)
    y = masthead(draw, page.total)
    band_top = feature_grid(draw, page.features, y)
    footer_y = SIDE - 46
    left_w = 278
    cy = map_block(draw, page, MARGIN, band_top + 2, left_w, None)
    edition_block(draw, page, MARGIN, cy + 4, left_w)
    method_block(draw, MARGIN, footer_y - 8, left_w)
    briefs_block(draw, page.briefs, band_top + 4, footer_y - 6, x0=MARGIN + left_w + 20)
    footer(draw, footer_y, page.total)
    return img


def save(img: Image.Image, path: str):
    img.save(path, format="PNG", optimize=True)
    import os

    return path, os.path.getsize(path)


def main(argv: list[str]) -> int:
    from content_1118 import PAGE

    out = argv[1] if len(argv) > 1 else "scratch/front5.png"
    img = render(PAGE)
    path, size = save(img, out)
    print(f"{path}: {SIDE}x{SIDE}, {size} bytes, {PAGE.total} stories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))