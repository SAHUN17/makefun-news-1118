"""Layout audit: re-render with the text calls instrumented.

Every `ImageDraw.text` call is recorded with its measured box, so the page can
be checked for overlapping blocks, text outside the margins, or a band of the
page left empty, without looking at the pixels.
"""

from __future__ import annotations

import sys

from PIL import Image, ImageDraw

import content_1118
import render5 as render

MARGIN = render.MARGIN
SIDE = render.SIDE
boxes: list[tuple[float, float, float, float, str]] = []

_orig_text = ImageDraw.ImageDraw.text


def spy(self, xy, text, *a, **kw):
    if isinstance(text, str) and text.strip():
        f = kw.get("font")
        try:
            l, t, r, b = self.textbbox(xy, text, font=f)
            boxes.append((l, t, r, b, text))
        except Exception:
            pass
    return _orig_text(self, xy, text, *a, **kw)


ImageDraw.ImageDraw.text = spy
img = render.render(content_1118.PAGE)
img.save("../scratch/audit.png", optimize=True)
ImageDraw.ImageDraw.text = _orig_text

problems = 0
for l, t, r, b, text in boxes:
    if l < MARGIN - 2 or r > SIDE - MARGIN + 2 or b > SIDE or t < 0:
        print(f"OUTSIDE MARGIN: {text[:44]!r} box=({l:.0f},{t:.0f},{r:.0f},{b:.0f})")
        problems += 1

# overlap: two boxes that share more than a 2px sliver of area, and are not
# consecutive lines of the same block (same x, stacked)
for i in range(len(boxes)):
    l1, t1, r1, b1, s1 = boxes[i]
    for j in range(i + 1, len(boxes)):
        l2, t2, r2, b2, s2 = boxes[j]
        ox = min(r1, r2) - max(l1, l2)
        oy = min(b1, b2) - max(t1, t2)
        if ox > 2 and oy > 2:
            same_block = abs(l1 - l2) < 1.5 and (b1 <= t2 + 1 or b2 <= t1 + 1)
            if not same_block:
                print(f"OVERLAP: {s1[:30]!r} ({l1:.0f},{t1:.0f}) x {s2[:30]!r} ({l2:.0f},{t2:.0f}) ox={ox:.0f} oy={oy:.0f}")
                problems += 1

# empty bands: rows with no recorded text and no ink
px = img.convert("L").load()
blank_rows = []
for y in range(0, SIDE):
    ink = sum(1 for x in range(MARGIN, SIDE - MARGIN, 4) if px[x, y] < 235)
    if ink == 0:
        blank_rows.append(y)
runs, start = [], None
for y in blank_rows:
    if start is None:
        start = y
    elif y != start + len(runs[-1]) if runs else False:
        pass
# compress runs
comp = []
for y in blank_rows:
    if comp and y == comp[-1][1] + 1:
        comp[-1][1] = y
    else:
        comp.append([y, y])
for a, b in comp:
    if a < 16 or b > SIDE - 16:
        continue
    if b - a >= 20:
        print(f"BLANK BAND y={a}..{b} ({b - a + 1}px)")
        problems += 1

print(f"text blocks: {len(boxes)}, problems: {problems}")
sys.exit(1 if problems else 0)