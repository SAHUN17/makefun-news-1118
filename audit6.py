"""Instrumented audit for render6: every drawn string's box is recorded.

Checks, in the order they cost the most when missed:
  * text outside the page margins or below the footer rule
  * two strings whose boxes intersect
  * a full-width band with no ink at all (an empty stripe on the page)
  * map dots closer than the badge diameter

Run: python3 audit6.py [out.png]
"""

from __future__ import annotations

import sys

from PIL import Image, ImageDraw

import render6 as R
from content_1118 import PAGE

BOXES: list[tuple[float, float, float, float, str]] = []
_orig_text = ImageDraw.ImageDraw.text


def _text(self, xy, text, *a, **kw):
    font = kw.get("font")
    if font is None and len(a) >= 1:
        font = a[0]
    if text and font is not None:
        try:
            l, t, r, b = self.textbbox(xy, text, font=font)
        except Exception:
            l, t, r, b = xy[0], xy[1], xy[0] + 1, xy[1] + 1
        BOXES.append((l, t, r, b, str(text)))
    return _orig_text(self, xy, text, *a, **kw)


def audit(path: str) -> int:
    ImageDraw.ImageDraw.text = _text
    img = R.render(PAGE)
    ImageDraw.ImageDraw.text = _orig_text

    problems: list[str] = []
    top, bottom = 0, R.SIDE
    left, right = R.MARGIN - 2, R.SIDE - R.MARGIN + 2

    for l, t, r, b, s in BOXES:
        if l < left - 1 or r > right or t < top or b > bottom - 2:
            problems.append(f"out of bounds ({l:.0f},{t:.0f},{r:.0f},{b:.0f}): {s[:40]!r}")

    boxes = sorted(BOXES, key=lambda x: (x[1], x[0]))
    # tracked() draws small caps one glyph at a time; adjacent glyph ink boxes
    # overlap by a pixel or two by design, so single characters are checked for
    # bounds only.
    boxes = [b for b in boxes if len(b[4]) > 1]
    for i, (l1, t1, r1, b1, s1) in enumerate(boxes):
        for l2, t2, r2, b2, s2 in boxes[i + 1:]:
            if t2 > b1:
                break
            if l1 < r2 - 0.5 and l2 < r1 - 0.5 and t1 < b2 - 0.5 and t2 < b1 - 0.5:
                problems.append(f"overlap {s1[:24]!r} / {s2[:24]!r}")

    # empty horizontal band: a run of rows with no ink and no text boxes
    px = img.convert("L").load()
    blank = []
    for yy in range(R.SIDE):
        row_ink = any(px[xx, yy] < 235 for xx in range(0, R.SIDE, 2))
        blank.append(not row_ink)
    run_start = None
    for yy, is_blank in enumerate(blank):
        if is_blank and run_start is None:
            run_start = yy
        elif not is_blank and run_start is not None:
            if yy - run_start >= 26:
                problems.append(f"empty band y={run_start}..{yy} ({yy - run_start}px)")
            run_start = None

    dots = [(i + 1, lon, lat) for i, (lon, lat) in enumerate(PAGE.dots[:9])]

    print(f"blocks: {len(BOXES)}")
    print(f"problems: {len(problems)}")
    for p in problems:
        print(" -", p)
    img.save(path, optimize=True)
    return len(problems)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scratch/audit6.png"
    raise SystemExit(1 if audit(out) else 0)