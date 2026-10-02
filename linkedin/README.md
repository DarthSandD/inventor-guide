# LinkedIn Carousel — Autodesk Inventor Complete Guide

8-slide carousel promoting the guide. 1080×1080 PNGs, brand-matched to the site.

| File | Purpose |
|---|---|
| `slide-1.png` … `slide-8.png` | Upload in this order as a LinkedIn document post |
| `carousel.html` | Source. Edit, then re-render |
| `post-copy.md` | Main + short post text, posting notes, per-slide alt text |
| `shots/` | Real screenshots of the live site, embedded in slides 1, 3, 6 |
| `_one1.html` … `_one8.html` | Per-slide isolated copies used for rendering (generated) |

## Slides

1. Hook — "Inventor is huge. Finding the right tool shouldn't be." + real desktop screenshot
2. The problem — 30 seconds of intro to find 20 seconds you needed
3. The site — 225 topics / 18 categories / one page + real desktop screenshot
4. A real learning path — Basic 78 / Intermediate 58 / Advanced 89
5. Assembly focus — the 14 tool chips that make up the deepest section
6. Mobile — real phone-width screenshot
7. The honest bit — every video checked by hand, 224 of 225 matched
8. CTA + URL + closing question

## Why these are screenshots, not AI images

Slides 1, 3 and 6 embed **real screenshots of the live site**, which is more
credible than generated art. The rest are typographic slides rendered from HTML
with headless Chrome.

## Re-render

```bash
cd linkedin
CHROME="/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
BASE="file:///C:/Users/USER/hermes-work/inventor-guide/linkedin"
OUT="C:/Users/USER/hermes-work/inventor-guide/linkedin"
for i in 1 2 3 4 5 6 7 8; do
  python - "$i" <<'PY'
import sys
i=sys.argv[1]
src=open("carousel.html",encoding="utf-8").read()
inject=f"<style>body{{margin:0}}.slide{{display:none!important}}.slide#s{i}{{display:flex!important}}</style>"
open(f"_one{i}.html","w",encoding="utf-8").write(src.replace("</head>", inject+"</head>"))
PY
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --allow-file-access-from-files --force-device-scale-factor=1 \
    --window-size=1080,1080 --virtual-time-budget=9000 \
    --screenshot="$OUT/slide-$i.png" "$BASE/_one$i.html"
done
```

`#sN` alone does NOT isolate a slide (all slides share one document). Inject
`body{margin:0}.slide{display:none!important}.slide#sN{display:flex!important}`
before `</head>` and screenshot that.

## Refreshing the site screenshots

`_shot_desktop.html` and `_shot_mobile.html` load the live site inside a fixed
iframe (`shots/crop-desktop.png` 1180×640 for slides 1 & 3,
`shots/mobile-true.png` 390×600 for slide 6). Re-capture, then re-render the
slides that use them.

On Windows, headless Chrome clamps its window to roughly 494px minimum, so
requesting a narrow window renders at 494 and crops, which looks like broken
mobile layout. Render mobile inside a 390px-wide iframe in a wide window instead.
