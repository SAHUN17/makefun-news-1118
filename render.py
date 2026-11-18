"""Render the world-news front page for Wednesday 18 November 2026.

One 1024x1024 broadsheet: a masthead that names the day, one dominant lead
package with a drawn illustration, two secondary illustrated stories, six
developed cards and a long run of one-line briefs. Pillow primitives only and
no randomness, so the same content always produces the same bytes.

Layout is computed from measured text, so a longer headline shrinks or wraps
rather than running into a neighbour's column.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
MARGIN = 34
PAPER = (247, 243, 233)
INK = (23, 21, 19)
SOFT = (99, 92, 80)
HAIR = (203, 195, 176)
RED = (163, 32, 27)
RULE_H = 3

FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# --- content -------------------------------------------------------------

DAY_LINE = "WEDNESDAY 18 NOVEMBER 2026"
EDITION = "EDITION 18.11"
STRAP = "ONE DAY IN THE WORLD"


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

    @property
    def total(self) -> int:
        return 1 + len(self.seconds) + len(self.cards) + len(self.briefs)


# --- text helpers --------------------------------------------------------


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_w(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=f)


def fit(draw, text, path, size, max_w, floor=9):
    """Largest size at or below `size` whose single line fits `max_w`."""
    while size > floor and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(draw, text, f, max_w):
    """Greedy wrap against the measured width; returns at most the lines that fit."""
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


def draw_lines(draw, x, y, lines, f, fill=INK, leading=1.18):
    lh = int(f.size * leading)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


def tracked(draw, x, y, text, f, fill, spacing=1.6):
    """Letter-spaced small-caps line; returns the width used."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += text_w(draw, ch, f) + spacing
    return cx - x


# --- illustrations -------------------------------------------------------


def _sky(draw, box, colour, height_ratio=0.55):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=colour)
    band = int((y1 - y0) * height_ratio)
    draw.rectangle((x0, y1 - band, x1, y1), fill=tuple(min(255, c + 26) for c in colour))


def art_bridge(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (34, 58, 96))
    w = x1 - x0
    deck = y1 - int((y1 - y0) * 0.34)
    draw.rectangle((x0, deck, x1, deck + 7), fill=ink)
    for i in range(6):
        px = x0 + int(w * (0.08 + i * 0.15))
        draw.rectangle((px, deck - 46 - (i % 2) * 8, px + 5, deck), fill=ink)
    draw.arc((x0 + int(w * 0.05), deck - 60, x0 + int(w * 0.46), deck + 34), 180, 360, fill=ink, width=4)
    draw.arc((x0 + int(w * 0.50), deck - 60, x0 + int(w * 0.92), deck + 34), 180, 360, fill=ink, width=4)
    # the broken span: a gap in the deck and a falling chunk
    gx = x0 + int(w * 0.46)
    draw.rectangle((gx, deck - 4, gx + int(w * 0.09), deck + 11), fill=(34, 58, 96))
    draw.polygon([(gx + 10, deck + 26), (gx + 46, deck + 44), (gx + 14, deck + 52)], fill=ink)
    for r in range(3):
        draw.line((gx + 4, deck + 70 + r * 9, gx + int(w * 0.2), deck + 70 + r * 9), fill=(150, 170, 200), width=2)


def art_burst(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (122, 46, 34))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    import math

    for i in range(12):
        a = i * math.pi / 6
        r0, r1 = 14, (x1 - x0) * 0.42
        draw.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                   cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=ink, width=4)
    draw.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=ink)


def art_ship(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (24, 74, 92))
    w, h = x1 - x0, y1 - y0
    hull_y = y0 + int(h * 0.62)
    draw.polygon([(x0 + int(w * 0.14), hull_y), (x0 + int(w * 0.86), hull_y),
                  (x0 + int(w * 0.74), hull_y + int(h * 0.16)), (x0 + int(w * 0.26), hull_y + int(h * 0.16))], fill=ink)
    draw.rectangle((x0 + int(w * 0.42), hull_y - int(h * 0.22), x0 + int(w * 0.58), hull_y), fill=ink)
    for i in range(4):
        wy = y0 + int(h * (0.84 + i * 0.04))
        draw.line((x0 + int(w * 0.08), wy, x0 + int(w * 0.92), wy), fill=(150, 190, 205), width=2)


def art_globe(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (38, 66, 58))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = int(min(x1 - x0, y1 - y0) * 0.34)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ink, width=4)
    draw.arc((cx - r, cy - int(r * 1.6), cx + r, cy + int(r * 1.6)), 0, 360, fill=ink, width=3)
    draw.arc((cx - int(r * 1.6), cy - r, cx + int(r * 1.6), cy + r), 0, 360, fill=ink, width=3)
    draw.line((cx - r, cy, cx + r, cy), fill=ink, width=3)
    draw.line((cx, cy - r, cx, cy + r), fill=ink, width=3)


def art_chart(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (44, 78, 52))
    w, h = x1 - x0, y1 - y0
    base = y1 - int(h * 0.14)
    for i, frac in enumerate((0.28, 0.44, 0.40, 0.62, 0.78)):
        bx = x0 + int(w * (0.14 + i * 0.15))
        draw.rectangle((bx, base - int(h * frac * 0.62), bx + int(w * 0.09), base), fill=ink)
    draw.line((x0 + int(w * 0.12), base - int(h * 0.5), x0 + int(w * 0.88), base - int(h * 0.78)), fill=(240, 226, 150), width=4)


def art_flame(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (128, 62, 26))
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y0 + int(h * 0.1)), (cx + int(w * 0.22), y0 + int(h * 0.62)),
                  (cx + int(w * 0.1), y1 - int(h * 0.12)), (cx - int(w * 0.12), y1 - int(h * 0.1)),
                  (cx - int(w * 0.2), y0 + int(h * 0.58))], fill=ink)


def art_ballot(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (54, 54, 96))
    w, h = x1 - x0, y1 - y0
    bx, by = x0 + int(w * 0.2), y0 + int(h * 0.5)
    draw.rectangle((bx, by, bx + int(w * 0.6), by + int(h * 0.32)), fill=ink)
    draw.rectangle((bx + int(w * 0.24), by - int(h * 0.34), bx + int(w * 0.36), by + 2), fill=ink)
    draw.line((bx + int(w * 0.42), by + int(h * 0.12), bx + int(w * 0.42) - 4, by + 2), fill=(230, 220, 200), width=4)


def art_cross(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (104, 40, 84))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    s = int(min(x1 - x0, y1 - y0) * 0.18)
    draw.rectangle((cx - s // 3, cy - s, cx + s // 3, cy + s), fill=ink)
    draw.rectangle((cx - s, cy - s // 3, cx + s, cy + s // 3), fill=ink)


def art_plane(draw, box, ink):
    x0, y0, x1, y1 = box
    _sky(draw, box, (108, 66, 30))
    w, h = x1 - x0, y1 - y0
    cy = y0 + int(h * 0.5)
    draw.polygon([(x0 + int(w * 0.1), cy), (x1 - int(w * 0.08), cy - int(h * 0.16)),
                  (x1 - int(w * 0.16), cy), (x1 - int(w * 0.08), cy + int(h * 0.12))], fill=ink)
    draw.polygon([(x0 + int(w * 0.36), cy), (x0 + int(w * 0.5), cy - int(h * 0.3)),
                  (x0 + int(w * 0.58), cy), (x0 + int(w * 0.5), cy + int(h * 0.26))], fill=ink)


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
}


def panel(draw, box, colour, key):
    draw.rectangle(box, fill=colour, outline=None)
    fn = ART.get(key, art_globe)
    fn(draw, box, tuple(min(255, c + 150) for c in colour))
    draw.rectangle(box, outline=PAPER, width=2)


# --- page ----------------------------------------------------------------


def masthead(draw, total):
    x = MARGIN
    right = SIDE - MARGIN
    draw.text((x, 22), "THE WORLD", font=font(FONT_SERIF_BOLD, 46), fill=INK)
    w = text_w(draw, "THE WORLD", font(FONT_SERIF_BOLD, 46))
    draw.text((x + w + 16, 30), STRAP, font=font(FONT_SANS_BOLD, 11), fill=RED)

    date_f = font(FONT_SERIF_BOLD, 27)
    dw = text_w(draw, "18 NOVEMBER 2026", date_f)
    draw.text((right - dw, 20), "18 NOVEMBER 2026", font=date_f, fill=INK)
    wk = font(FONT_SANS_BOLD, 12)
    draw.text((right - text_w(draw, "WEDNESDAY", wk), 52), "WEDNESDAY", font=wk, fill=SOFT)

    draw.rectangle((x, 78, right, 78 + RULE_H), fill=INK)
    strap = f"{total} STORIES  ·  SIX CONTINENTS  ·  ALL OF IT ON ONE DAY"
    tracked(draw, x, 90, strap, font(FONT_SANS_BOLD, 11), SOFT)
    ed = EDITION
    draw.text((right - text_w(draw, ed, font(FONT_SANS_BOLD, 11)), 90), ed, font=font(FONT_SANS_BOLD, 11), fill=SOFT)
    draw.line((x, 112, right, 112), fill=HAIR, width=1)
    return 122


def lead_package(draw, story: Story, y, height=238):
    x = MARGIN
    right = SIDE - MARGIN
    box_w = 596
    panel(draw, (x, y, x + box_w, y + height), story.colour, story.art)

    tx = x + box_w + 20
    tw = right - tx
    cy = y
    cy = int(tracked(draw, tx, cy, story.kicker, font(FONT_SANS_BOLD, 11), story.colour) and cy + 22)
    head_f = fit(draw, story.head, FONT_SERIF_BOLD, 34, tw, floor=20)
    lines = wrap(draw, story.head, head_f, tw)[:4]
    cy = draw_lines(draw, tx, cy, lines, head_f, leading=1.06) + 8
    draw.line((tx, cy, right, cy), fill=HAIR, width=1)
    cy += 8
    det_f = font(FONT_SANS, 13)
    cy = draw_lines(draw, tx, cy, wrap(draw, story.detail, det_f, tw)[:5], det_f, fill=SOFT, leading=1.32)
    return y + height + 14


def second_row(draw, stories, y, height=150):
    x = MARGIN
    gap = 18
    col = (SIDE - 2 * MARGIN - gap) // 2
    for i, st in enumerate(stories[:2]):
        bx = x + i * (col + gap)
        panel(draw, (bx, y, bx + 132, y + height), st.colour, st.art)
        tx = bx + 146
        tw = col - 146
        cy = int(tracked(draw, tx, y + 2, st.kicker, font(FONT_SANS_BOLD, 10), st.colour) and y + 22)
        head_f = fit(draw, st.head, FONT_SERIF_BOLD, 21, tw, floor=15)
        cy = draw_lines(draw, tx, cy, wrap(draw, st.head, head_f, tw)[:4], head_f, leading=1.08) + 4
        det_f = font(FONT_SANS, 11)
        draw_lines(draw, tx, cy, wrap(draw, st.detail, det_f, tw)[:4], det_f, fill=SOFT, leading=1.28)
    return y + height + 16


def card_grid(draw, cards, y, bottom, cols=3, gap_x=16, gap_y=18):
    """Lay the cards out in 3 columns, sizing each row to its own content."""
    x = MARGIN
    right = SIDE - MARGIN
    cw = (right - x - gap_x * (cols - 1)) // cols
    items = cards[:6]
    rows = [items[i:i + cols] for i in range(0, len(items), cols)]
    tall = []
    for row in rows:
        tallest = 0
        for st in row:
            cy = 18
            head_f = fit(draw, st.head, FONT_SERIF_BOLD, 17, cw, floor=13)
            cy += len(wrap(draw, st.head, head_f, cw)[:3]) * int(head_f.size * 1.08) + 2
            det_f = font(FONT_SANS, 10)
            cy += len(wrap(draw, st.detail, det_f, cw)[:2]) * int(det_f.size * 1.25)
            tallest = max(tallest, cy)
        tall.append(tallest)
    total = sum(tall) + gap_y * (len(rows) - 1)
    # spread any slack between rows so the band does not end in white space
    extra = max(0, (bottom - y - total)) // max(1, len(rows) - 1) if len(rows) > 1 else 0
    extra = min(extra, 26)
    cy0 = y
    for r, row in enumerate(rows):
        for c, st in enumerate(row):
            bx = x + c * (cw + gap_x)
            by = cy0
            cy = int(tracked(draw, bx, by, st.kicker, font(FONT_SANS_BOLD, 9), st.colour) and by + 15)
            head_f = fit(draw, st.head, FONT_SERIF_BOLD, 17, cw, floor=13)
            cy = draw_lines(draw, bx, cy, wrap(draw, st.head, head_f, cw)[:3], head_f, leading=1.08) + 2
            det_f = font(FONT_SANS, 10)
            draw_lines(draw, bx, cy, wrap(draw, st.detail, det_f, cw)[:2], det_f, fill=SOFT, leading=1.25)
        if r < len(rows) - 1:
            sy = cy0 + tall[r] + 8
            draw.line((x, sy, right, sy), fill=HAIR, width=1)
            tracked(draw, x, sy + 4, "MORE OF THE DAY", font(FONT_SANS_BOLD, 9), SOFT, spacing=1.4)
        cy0 += tall[r] + gap_y + extra
    return cy0 - gap_y - extra


def brief_list(draw, briefs, y, bottom, cols=2, gap=26):
    """One-line briefs, two columns, spaced to fill the band down to `bottom`."""
    x = MARGIN
    right = SIDE - MARGIN
    cw = (right - x - gap) // cols
    per = (len(briefs) + cols - 1) // cols
    body_f = font(FONT_SANS, 13)
    tag_f = font(FONT_SANS_BOLD, 11)
    lh = max(18, min(26, (bottom - y) // max(1, per)))
    for i, (tag, text) in enumerate(briefs):
        c, r = divmod(i, per)
        bx = x + c * (cw + gap)
        by = y + r * lh
        tw = tracked(draw, bx, by + 1, tag, tag_f, RED, spacing=0.6) + 6
        line = text
        while text_w(draw, line, body_f) > cw - tw and " " in line:
            line = line[:-1]
        draw.text((bx + tw, by - 1), line, font=body_f, fill=INK)
        if r < per - 1:
            draw.line((bx, by + lh - 6, bx + cw, by + lh - 6), fill=(232, 226, 212), width=1)
    return y + per * lh


def footer(draw, y):
    x = MARGIN
    right = SIDE - MARGIN
    draw.line((x, y, right, y), fill=INK, width=RULE_H)
    note = "Compiled from the day's reporting; all events of Wednesday 18 November 2026."
    draw.text((x, y + 8), note, font=font(FONT_SANS, 10), fill=SOFT)
    mark = "THE WORLD IN ONE DAY"
    draw.text((right - text_w(draw, mark, font(FONT_SANS_BOLD, 10)), y + 8), mark,
              font=font(FONT_SANS_BOLD, 10), fill=INK)


def render(page: Page) -> Image.Image:
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(img)
    footer_y = SIDE - 46
    y = masthead(draw, page.total)
    y = lead_package(draw, page.lead, y)
    y = second_row(draw, page.seconds, y)
    y = card_grid(draw, page.cards, y, y + 190)
    y = brief_list(draw, page.briefs, y + 10, footer_y - 12)
    footer(draw, footer_y)
    return img


def save(img: Image.Image, path: str) -> tuple[str, int]:
    img.save(path, format="PNG", optimize=True)
    import os

    return path, os.path.getsize(path)


def main(argv: list[str]) -> int:
    from content_1118 import PAGE

    out = argv[1] if len(argv) > 1 else "scratch/draft.png"
    img = render(PAGE)
    path, size = save(img, out)
    print(f"{path}: {SIDE}x{SIDE}, {size} bytes, {PAGE.total} stories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))