#!/usr/bin/env python
"""Resolve a curated YouTube tutorial clip for every Inventor command.

For each command we search YouTube (via yt-dlp, flat-playlist for speed),
score the candidates on title relevance, channel reputation, duration and
popularity, then keep the single best match. Results are written to
video_db.json (incremental: already-resolved keys are skipped).
"""
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from commands import COMMANDS  # noqa: E402

OUT = os.path.join(HERE, "video_db.json")
CAND_N = 8

# Targeted query overrides where the default search phrasing pulled a weak match.
QUERY_OVERRIDES = {
    "PLACE": "Autodesk Inventor place component into assembly tutorial",
    "CREATECOMPONENT": "Autodesk Inventor create component tool assembly tutorial",
    "FREEMOVE": "Autodesk Inventor move component in assembly tutorial",
    "COPY_COMP": "Autodesk Inventor copy component in assembly tutorial",
    "INTERFERENCE": "Autodesk Inventor interference check assembly tutorial",
    "SELECTOTHER": "Autodesk Inventor select other tool tutorial",
    "SM_FACE": "Autodesk Inventor sheet metal face tool tutorial",
    "SM_UNFOLD": "Autodesk Inventor create flat pattern sheet metal tutorial",
    "SM_FLANGE": "Autodesk Inventor sheet metal flange tool tutorial",
    "REST": "Autodesk Inventor boss rest feature tutorial",
    "RECTANGLE": "Autodesk Inventor sketch rectangle tool tutorial",
    "DIMENSION": "Autodesk Inventor sketch general dimension tool tutorial",
    "CONSTRAINTS": "Autodesk Inventor show constraints in sketch tutorial",
    "CHAMFER2D": "Autodesk Inventor sketch chamfer tool tutorial",
    "THREAD": "Autodesk Inventor thread tool tutorial",
    "FACEOFFSET": "Autodesk Inventor move face offset tutorial",
    "COIL": "Autodesk Inventor coil tool tutorial",
    "BOUNDARYPATCH": "Autodesk Inventor boundary patch tutorial",
    "ADAPTIVE": "Autodesk Inventor adaptive part tutorial",
    "PARAMETRIC_ASSY": "Autodesk Inventor assembly parameters tutorial",
    "WELDMENT": "Autodesk Inventor weldment tutorial",
    "FILLET": "Autodesk Inventor fillet tool tutorial",
    "HOLE": "Autodesk Inventor hole tool tutorial",
    "EXTRUDE": "Autodesk Inventor extrude tool tutorial",
    "3DSKETCH": "Autodesk Inventor 3D sketch tool tutorial",
}

# Channels known for solid, tool-focused Autodesk Inventor tutorials.
GOOD_CHANNELS = {
    "autodesk inventor": 6,
    "autodesk": 5,
    "engineering applied": 5,
    "cad by nana": 4,
    "tech3d": 4,
    "tfi": 4,
    "cory allen": 4,
    "3d parametric solid model drawing": 4,
    "inventor tutorials": 3,
    "jw cad": 3,
    "the inventor guy": 3,
    "cad cam tutorial": 3,
    "solid solutions": 3,
    "rand 3d": 3,
    "ketiv": 2,
    "cadline": 2,
    "graitec": 2,
    "microcad": 2,
    "cadmicro": 2,
    "pro cad": 2,
    "tedcf": 2,
    "manufacturing": 1,
}

STOP = {
    "autodesk", "inventor", "tutorial", "tutorials", "the", "a", "an", "and",
    "or", "of", "for", "to", "in", "on", "with", "how", "use", "using", "by",
    "part", "create", "creating", "make", "making", "your",
}


def yt_search(query, n=CAND_N):
    cmd = [
        "yt-dlp", f"ytsearch{n}:{query}",
        "--dump-json", "--flat-playlist", "--no-warnings",
        "--no-check-certificates",
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return []
    out = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        out.append({
            "id": d.get("id"),
            "title": d.get("title") or "",
            "channel": (d.get("channel") or d.get("uploader") or ""),
            "duration": d.get("duration") or 0,
            "views": d.get("view_count") or 0,
        })
    return out


def head_noun(name):
    """The last significant word of a command name is its head noun."""
    words = [w for w in re.findall(r"[a-z0-9]+", name.lower()) if w not in STOP]
    return words[-1] if words else name.lower()


def name_tokens(name):
    return [w for w in re.findall(r"[a-z0-9]+", name.lower()) if w not in STOP and len(w) > 2]


def tok_in(tok, title):
    """Loose presence test: first 4 chars of the token appear in the title."""
    return tok[:4] in title


def score(cand, cmd):
    title = cand["title"].lower()
    chan = cand["channel"].lower()
    dur = cand["duration"] or 0
    must = head_noun(cmd["name"])
    toks = name_tokens(cmd["name"])
    q = cmd["q"]

    # MANDATORY: the command's head noun must appear as a whole word.
    if not re.search(r"\b" + re.escape(must) + r"\b", title):
        return -999

    s = 0.0

    # every significant token of the command name should be present
    if toks:
        present = sum(1 for w in toks if tok_in(w, title))
        s += (present / len(toks)) * 10
        missing = len(toks) - present
        s -= missing * 6
        if present == len(toks):
            s += 5                       # whole command name covered
        if tok_in(toks[0], title):
            s += 4                       # first word (the action) present

    # extra query keywords present
    qwords = [w for w in re.findall(r"[a-z0-9]+", q.lower()) if w not in STOP and len(w) > 2]
    if qwords:
        s += (sum(1 for w in qwords if tok_in(w, title)) / len(qwords)) * 4

    # channel reputation
    for name, pts in GOOD_CHANNELS.items():
        if name in chan:
            s += pts
            break

    # duration window: tutorials are usually 1.5-45 min
    if dur == 0:
        s -= 2
    elif 90 <= dur <= 1800:
        s += 4
    elif dur < 90:
        s -= 6
    elif dur > 3600:
        s -= 2

    views = cand["views"] or 0
    if views > 100000:
        s += 2
    elif views > 20000:
        s += 1

    for bad in ("shorts", "live", "stream", "reaction", "shortsfeed", "full course", "what's new"):
        if bad in title:
            s -= 4
    return s


def resolve(cmd):
    q = QUERY_OVERRIDES.get(cmd["key"], cmd["q"])
    cands = yt_search(q)
    if not cands:
        return None
    scored = [(score(c, cmd), c) for c in cands]
    scored = [(s, c) for s, c in scored if s > -900]
    if not scored:
        return None
    best_score, best = max(scored, key=lambda t: t[0])
    if best_score < 4:
        return None
    return {
        "videoId": best["id"],
        "title": best["title"],
        "channel": best["channel"],
        "duration": best["duration"],
    }


def load():
    if os.path.exists(OUT):
        with open(OUT, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save(db):
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=1, ensure_ascii=False)
    os.replace(tmp, OUT)


def main():
    db = load()
    todo = [c for c in COMMANDS if c["key"] not in db]
    limit = int(os.environ.get("LIMIT", "0"))
    if limit:
        todo = todo[:limit]
    print(f"resolving {len(todo)} commands ({len(db)} already done)", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(resolve, c): c for c in todo}
        for fut in as_completed(futs):
            c = futs[fut]
            try:
                res = fut.result()
            except Exception as e:      # noqa: BLE001
                res = None
                print(f"  ! {c['key']}: {e}", flush=True)
            if res:
                db[c["key"]] = res
            else:
                db[c["key"]] = None
            done += 1
            if done % 10 == 0:
                save(db)
                print(f"  ...{done}/{len(todo)}", flush=True)
    save(db)
    found = sum(1 for v in db.values() if v)
    print(f"DONE: {found}/{len(db)} commands have a clip", flush=True)


if __name__ == "__main__":
    main()
