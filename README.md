# Autodesk Inventor Complete Guide

Live site: https://darthsandd.github.io/inventor-guide/ (GitHub Pages, serves `index.html`).

A single-file, zero-dependency reference and learning path for Autodesk Inventor —
from your very first sketch through advanced assembly modelling, sheet metal,
surfaces, drawings, iLogic automation and stress analysis. Every topic card carries
its own curated tutorial clip.

## What's inside

- **225 topics across 18 categories**, each tagged **Basic / Intermediate / Advanced** (78 / 58 / 89).
- Category browser + level filter + full-text search (tool name, shortcut, path, description).
- One curated YouTube tutorial per topic — click a card's thumbnail to play it in a modal.
- Copy-to-clipboard per topic, sidebar navigation, scroll progress bar, toast notifications.
- Responsive and keyboard-navigable (Esc closes the player).

## Coverage

Categories: Sketching, Sketch Constraints, Part Features, Advanced Part, Assembly,
Advanced Assembly, Sheet Metal, Drawing, Presentation & Studio, Surfaces, Analysis,
Automation, Content Center, Work Features, Navigation & View, File & Project, Specialized.

Shortcuts reflect Inventor's predefined one-key shortcuts and multi-character command
aliases (e.g. `E` Extrude, `R` Revolve, `C` Constraint, `H` Hole, `P` Place, `L` Line,
`F2/F3/F4` Pan/Zoom/Rotate). Sources: Autodesk Inventor Help — *Predefined Command Alias
and Shortcut Reference* and the *Inventor Keyboard Shortcuts Guide*.

## Video accuracy

- Each clip is discovered by searching YouTube and scored on title relevance to the
  exact tool, channel reputation, duration and popularity — a clip is never borrowed
  from a differently-named tool.
- A topic without a confident match shows an honest **No clip** state that opens a
  YouTube search for that exact tool instead of playing a mismatched video.

## Notes

- Fully self-contained: one `index.html`, no build step, no backend, no dependencies.
- Video is embedded from YouTube. No local video files.

## LinkedIn assets

`linkedin/` holds an 8-slide carousel (1080×1080 PNGs) and the post copy — see
`linkedin/README.md`.

## Rebuild

```
python data/resolve_videos.py   # (re)discover clips  -> data/video_db.json
python build.py                 # -> index.html
```

## Deploy

Local `main` pushes to remote `main`. Pages rebuilds in ~1–2 min.

```
git add -A && git commit -m "..." && git push origin main
```
