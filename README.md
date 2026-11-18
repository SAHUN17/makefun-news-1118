# 18 November 2026 — the world in one day

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/SAHUN17/makefun-news-1118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/SAHUN17/makefun-news-1118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

An entry for [make.fun's daily world-news image bounty](https://make.fun/bounty/news-image-20261118):
one image that sums up the world's news of **Wednesday 18 November 2026**.

`entry.png` is a 1024×1024 broadsheet page: the day's date across the masthead, a numbered band
of nine illustrated stories — three leads with large panels, six developed stories below — a
locator map keyed to those numbers, and twenty-four briefs set one line each. One page a reader
who missed the day can read front to back in a minute.

## How it is built

`main.py` publishes the committed `entry.png` to `/output/entry.png`: it re-checks the
bounty's limits (PNG, ≤ 1 MiB, ≤ 1024 px a side) and proves the bytes it wrote match the
asset it ships. `render7.py` is the drawing program behind the page — Pillow primitives, a
measured layout, and no randomness, so the same content always renders the same bytes.
`audit6.py` re-renders with every text call instrumented and fails if two blocks overlap, if
anything leaves the margins, if a band of the page is left empty, or if two locator badges
touch.

```sh
python3 main.py /tmp/out          # publish the page where the judge reads it
python3 render7.py out.png        # redraw the page from its content module
python3 audit6.py                 # layout check: overlaps, margins, empty bands
```

## The day, as the page sets it

See `content_1118.py` for the items on the page and the one-line context under each: the
lead story, two secondary packages, six developed stories and the briefs beneath them. Every
item is an event of Wednesday 18 November 2026 as reported that day.

## Licence

MIT — see [LICENSE](LICENSE).