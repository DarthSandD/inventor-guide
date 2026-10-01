#!/usr/bin/env python
"""Build the single-file Autodesk Inventor Guide (index.html).

Reads data/commands.py + data/video_db.json, reuses the CSS from the AutoCAD
guide for visual parity, and emits a self-contained index.html.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
sys_path = HERE
import sys
sys.path.insert(0, os.path.join(HERE, "data"))
from commands import COMMANDS, CATEGORIES  # noqa: E402

AUTOCAD = os.path.join(os.path.dirname(HERE), "autocad-guide", "index.html")
OUT = os.path.join(HERE, "index.html")


def get_css():
    with open(AUTOCAD, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    css = m.group(1)
    # Recolour to the Inventor teal identity.
    css = css.replace("#00e5ff", "#19d3c5")
    css = css.replace("#00b8cc", "#12b3a8")
    css = css.replace("rgba(0, 229, 255, 0.15)", "rgba(25, 211, 197, 0.15)")
    css = css.replace("rgba(0, 229, 255, 0.1)", "rgba(25, 211, 197, 0.1)")
    css = css.replace("--orange: #ff9f1c", "--orange: #ff8a3d")
    return css


EXTRA_CSS = """
/* ── Inventor additions ─────────────────────────────────────── */
.header-brand .accent { color: var(--accent); }
.hero {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  background: radial-gradient(1200px 300px at 20% -40%, var(--accent-glow), transparent 70%);
}
.hero h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: .4rem; }
.hero h1 .accent { color: var(--accent); }
.hero p { color: var(--text-secondary); max-width: 760px; font-size: .95rem; }
.hero-stats { display: flex; gap: 1.75rem; margin-top: 1.1rem; flex-wrap: wrap; }
.hero-stat { display: flex; flex-direction: column; }
.hero-stat b { font-size: 1.35rem; font-weight: 700; color: var(--text); font-family: var(--font-mono); }
.hero-stat span { font-size: .72rem; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); }

.level-badge {
  display: inline-block; font-size: .62rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .05em; padding: .12rem .45rem; border-radius: 4px; margin-left: .5rem;
  vertical-align: middle; font-family: var(--font-mono);
}
.level-Basic { background: rgba(25,211,197,.13); color: #19d3c5; }
.level-Intermediate { background: rgba(255,138,61,.14); color: #ff8a3d; }
.level-Advanced { background: rgba(255,71,110,.14); color: #ff476e; }

.card-key { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .5rem; }
.card-path { font-size: .68rem; color: var(--text-muted); font-family: var(--font-mono); margin-top: .35rem; }

.level-filter { display: flex; gap: .35rem; padding: 0 1.25rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.level-btn {
  font-size: .72rem; font-weight: 600; padding: .28rem .6rem; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--text-secondary);
  cursor: pointer; font-family: var(--font-sans);
}
.level-btn:hover { color: var(--text); border-color: var(--text-muted); }
.level-btn.active { background: var(--accent-glow); border-color: var(--accent); color: var(--accent); }

.legend { display:flex; gap:1rem; align-items:center; padding: 0 2.5rem 1.25rem; flex-wrap: wrap; font-size:.75rem; color: var(--text-muted);}
.legend .sw { width:10px; height:10px; border-radius:2px; display:inline-block; margin-right:.35rem; vertical-align:middle;}
.legend .b{background:#19d3c5;} .legend .i{background:#ff8a3d;} .legend .a{background:#ff476e;}
"""


def js_data():
    db = {}
    path = os.path.join(HERE, "data", "video_db.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            db = json.load(f)

    cmds = []
    for c in COMMANDS:
        v = db.get(c["key"])
        entry = {
            "key": c["key"],
            "name": c["name"],
            "cat": c["cat"],
            "keys": c["keys"],
            "level": c["level"],
            "desc": c["desc"],
        }
        if v and v.get("videoId"):
            entry["v"] = {
                "id": v["videoId"],
                "title": v.get("title", c["name"]),
                "channel": v.get("channel", ""),
                "dur": v.get("duration", 0) or 0,
            }
        cmds.append(entry)

    cats = [{"id": c["id"], "name": c["name"], "icon": c["icon"]} for c in CATEGORIES]
    return cmds, cats


def build():
    cmds, cats = js_data()
    with_video = sum(1 for c in cmds if c.get("v"))
    n_basic = sum(1 for c in cmds if c["level"] == "Basic")
    n_inter = sum(1 for c in cmds if c["level"] == "Intermediate")
    n_adv = sum(1 for c in cmds if c["level"] == "Advanced")

    html = HTML_TEMPLATE
    html = html.replace("/*__CSS__*/", get_css() + EXTRA_CSS)
    html = html.replace("/*__COMMANDS__*/", json.dumps(cmds, ensure_ascii=False, indent=1))
    html = html.replace("/*__CATEGORIES__*/", json.dumps(cats, ensure_ascii=False, indent=1))
    html = html.replace("__TOTAL__", str(len(cmds)))
    html = html.replace("__WITHVID__", str(with_video))
    html = html.replace("__NBASIC__", str(n_basic))
    html = html.replace("__NINTER__", str(n_inter))
    html = html.replace("__NADV__", str(n_adv))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {OUT}  ({len(html)} bytes)")
    print(f"  commands: {len(cmds)}  with clip: {with_video}  "
          f"basic/inter/adv: {n_basic}/{n_inter}/{n_adv}")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Autodesk Inventor Guide — Complete Tutorial &amp; Command Reference</title>
<meta name="description" content="A complete Autodesk Inventor guide: sketching, part modelling, advanced features, assembly, sheet metal, drawings, surfaces, iLogic and more — every topic with its own curated tutorial video.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/*__CSS__*/
</style>
</head>
<body>

<div class="progress-bar" id="progressBar"></div>

<header class="header">
  <a class="header-brand" href="#">
    <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M16 3 29 10v12L16 29 3 22V10z"/>
      <path d="M16 3v13l13 6M16 16 3 22"/>
      <circle cx="16" cy="16" r="3.2"/>
    </svg>
    <span>Inventor <span class="accent">Guide</span></span>
  </a>
  <div class="header-search">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="text" id="searchInput" placeholder="Search tools, shortcuts, or topics (e.g. loft, constrain, flange)...">
  </div>
</header>

<section class="hero">
  <h1>Autodesk Inventor <span class="accent">Complete Guide</span></h1>
  <p>From your very first sketch to advanced assembly modelling, sheet metal, surfaces, iLogic and stress analysis — every topic explained, with its own curated tutorial clip. Pick a category, search a tool, or follow the Basic &rarr; Advanced path.</p>
  <div class="hero-stats">
    <div class="hero-stat"><b>__TOTAL__</b><span>Topics</span></div>
    <div class="hero-stat"><b>__WITHVID__</b><span>With video</span></div>
    <div class="hero-stat"><b>__NBASIC__</b><span>Basic</span></div>
    <div class="hero-stat"><b>__NINTER__</b><span>Intermediate</span></div>
    <div class="hero-stat"><b>__NADV__</b><span>Advanced</span></div>
  </div>
</section>

<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-title">Level</div>
      <div class="level-filter" id="levelFilter"></div>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-title">Categories</div>
      <ul class="sidebar-list" id="categoryList"></ul>
    </div>
  </nav>

  <main class="main">
    <div class="section-header">
      <h1 class="section-title" id="sectionTitle">All Topics</h1>
      <p class="section-subtitle" id="sectionSubtitle"></p>
    </div>
    <div class="command-grid" id="commandGrid"></div>
    <div class="empty-state" id="emptyState" style="display:none">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <p>No topics found matching your search.</p>
    </div>
  </main>
</div>

<div class="legend">
  <span><span class="sw b"></span>Basic — start here</span>
  <span><span class="sw i"></span>Intermediate</span>
  <span><span class="sw a"></span>Advanced</span>
  <span style="margin-left:auto">Click any card's thumbnail to play its tutorial</span>
</div>

<!-- Video Modal -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <div class="modal-video" id="modalVideo"></div>
    <div class="modal-info">
      <div class="modal-info-text">
        <div class="modal-info-cmd" id="modalCmd"></div>
        <div class="modal-info-name" id="modalName"></div>
        <div class="modal-info-time" id="modalTime"></div>
      </div>
      <button class="modal-close" id="modalClose" aria-label="Close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ─── Command / topic database ───────────────────────────────────
const COMMANDS = /*__COMMANDS__*/;

const CATEGORIES = /*__CATEGORIES__*/;

const LEVELS = [
  { id:'all', name:'All levels' },
  { id:'Basic', name:'Basic' },
  { id:'Intermediate', name:'Intermediate' },
  { id:'Advanced', name:'Advanced' }
];

// ─── State ───────────────────────────────────────────────────────
let currentCategory = 'all';
let currentLevel = 'all';
let currentSearch = '';

// ─── DOM refs ────────────────────────────────────────────────────
const $grid = document.getElementById('commandGrid');
const $empty = document.getElementById('emptyState');
const $search = document.getElementById('searchInput');
const $catList = document.getElementById('categoryList');
const $levelFilter = document.getElementById('levelFilter');
const $modalOverlay = document.getElementById('modalOverlay');
const $modalVideo = document.getElementById('modalVideo');
const $modalCmd = document.getElementById('modalCmd');
const $modalName = document.getElementById('modalName');
const $modalTime = document.getElementById('modalTime');
const $modalClose = document.getElementById('modalClose');
const $progressBar = document.getElementById('progressBar');
const $toast = document.getElementById('toast');
const $sectionTitle = document.getElementById('sectionTitle');
const $sectionSubtitle = document.getElementById('sectionSubtitle');

// ─── Helpers ────────────────────────────────────────────────────
function fmtTime(s) {
  s = Math.max(0, Math.round(s || 0));
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m + ':' + String(sec).padStart(2, '0');
}

function thumbUrl(videoId) {
  return 'https://img.youtube.com/vi/' + videoId + '/mqdefault.jpg';
}

function toast(msg) {
  $toast.innerHTML = msg;
  $toast.classList.add('show');
  setTimeout(() => $toast.classList.remove('show'), 2000);
}

function copyText(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(() => {});
  } else {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ─── Render ─────────────────────────────────────────────────────
function renderLevelFilter() {
  $levelFilter.innerHTML = '';
  LEVELS.forEach(lv => {
    const b = document.createElement('button');
    b.className = 'level-btn' + (currentLevel === lv.id ? ' active' : '');
    b.textContent = lv.name;
    b.onclick = () => { currentLevel = lv.id; render(); };
    $levelFilter.appendChild(b);
  });
}

function renderSidebar() {
  $catList.innerHTML = '';
  CATEGORIES.forEach(cat => {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.className = 'sidebar-link' + (currentCategory === cat.id ? ' active' : '');
    const count = cat.id === 'all' ? COMMANDS.length : COMMANDS.filter(c => c.cat === cat.id).length;
    btn.innerHTML = `<span>${cat.icon}</span> ${escapeHtml(cat.name)}<span class="count">${count}</span>`;
    btn.onclick = () => { currentCategory = cat.id; render(); };
    li.appendChild(btn);
    $catList.appendChild(li);
  });
}

function matches(c) {
  if (currentCategory !== 'all' && c.cat !== currentCategory) return false;
  if (currentLevel !== 'all' && c.level !== currentLevel) return false;
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    return (c.key || '').toLowerCase().includes(q) ||
           (c.name || '').toLowerCase().includes(q) ||
           (c.keys || '').toLowerCase().includes(q) ||
           (c.desc || '').toLowerCase().includes(q) ||
           (c.cat || '').toLowerCase().includes(q) ||
           (c.level || '').toLowerCase().includes(q);
  }
  return true;
}

function renderGrid() {
  const items = COMMANDS.filter(matches);

  const catName = currentCategory === 'all' ? 'All Topics'
    : (CATEGORIES.find(c => c.id === currentCategory) || {}).name || '';
  $sectionTitle.textContent = catName + (currentLevel !== 'all' ? ' · ' + currentLevel : '');
  const vid = items.filter(i => i.v).length;
  $sectionSubtitle.textContent = items.length + ' topic' + (items.length !== 1 ? 's' : '') +
    (currentSearch ? ' matching search' : '') + ' · ' + vid + ' with video';

  if (items.length === 0) {
    $grid.style.display = 'none';
    $empty.style.display = 'block';
    return;
  }
  $grid.style.display = 'grid';
  $empty.style.display = 'none';
  $grid.innerHTML = '';

  items.forEach((cmd, i) => {
    const v = cmd.v;
    const card = document.createElement('div');
    card.className = 'card';
    card.style.animationDelay = (Math.min(i, 30) * 0.02) + 's';

    const thumb = v
      ? `<div class="card-thumb" data-video="${v.id}" data-end="${v.dur}" data-cmd="${escapeHtml(cmd.key)}" data-title="${escapeHtml(v.title)}">
          <img src="${thumbUrl(v.id)}" alt="" loading="lazy" onerror="this.style.display='none'">
          <div class="play-overlay"><svg viewBox="0 0 24 24" fill="currentColor"><polygon points="6,4 20,12 6,20"/></svg></div>
          <div class="clip-time">${fmtTime(v.dur)}</div>
        </div>`
      : `<div class="card-thumb no-video" data-cmd="${escapeHtml(cmd.key)}" data-title="${escapeHtml(cmd.name)}" title="No clip yet — click to search YouTube">
          <div class="no-clip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5h.01M14.5 9.5h.01M9 15c1-1 2-1.5 3-1.5s2 .5 3 1.5"/></svg>
            <span>No clip</span>
          </div>
        </div>`;

    card.innerHTML = `
      ${thumb}
      <div class="card-body">
        <div class="card-cmd">${escapeHtml(cmd.key)}<span class="level-badge level-${cmd.level}">${cmd.level}</span></div>
        <div class="card-name">${escapeHtml(cmd.name)}</div>
        <div class="card-desc">${escapeHtml(cmd.desc)}</div>
        <div class="card-path">${escapeHtml(cmd.keys)}</div>
        <div class="card-key"><span class="key-badge">${escapeHtml(cmd.cat)}</span></div>
      </div>
      <button class="card-copy" data-cmd="${escapeHtml(cmd.key)}" title="Copy tool name">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      </button>
    `;
    $grid.appendChild(card);
  });

  $grid.querySelectorAll('.card-thumb[data-video]').forEach(el => {
    el.addEventListener('click', () => {
      openModal({
        videoId: el.dataset.video,
        end: parseInt(el.dataset.end) || 0,
        title: el.dataset.title,
        cmdKey: el.dataset.cmd
      });
    });
  });

  $grid.querySelectorAll('.card-thumb.no-video').forEach(el => {
    el.addEventListener('click', () => {
      const q = encodeURIComponent(el.dataset.cmd + ' Autodesk Inventor tutorial');
      window.open('https://www.youtube.com/results?search_query=' + q, '_blank', 'noopener');
    });
  });

  $grid.querySelectorAll('.card-copy').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      const cmdKey = el.dataset.cmd;
      copyText(cmdKey);
      el.classList.add('copied');
      toast(`Copied <span class="toast-accent">${escapeHtml(cmdKey)}</span> to clipboard`);
      setTimeout(() => el.classList.remove('copied'), 1500);
    });
  });
}

function render() {
  renderLevelFilter();
  renderSidebar();
  renderGrid();
  updateProgress();
}

// ─── Modal / YouTube Player ─────────────────────────────────────
function openModal(video) {
  $modalCmd.textContent = (video.cmdKey || '') + ' — tutorial';
  $modalName.textContent = video.title || 'Tutorial';
  $modalTime.textContent = video.end ? 'Length ' + fmtTime(video.end) : '';
  $modalOverlay.classList.add('open');
  document.body.style.overflow = 'hidden';

  let vidUrl = 'https://www.youtube.com/embed/' + video.videoId +
    '?autoplay=1&rel=0&modestbranding=1&enablejsapi=1';
  if (video.end) vidUrl += '&end=' + video.end;
  $modalVideo.innerHTML = '<iframe src="' + vidUrl + '" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
}

function closeModal() {
  $modalOverlay.classList.remove('open');
  document.body.style.overflow = '';
  $modalVideo.innerHTML = '';
}

$modalClose.addEventListener('click', closeModal);
$modalOverlay.addEventListener('click', (e) => { if (e.target === $modalOverlay) closeModal(); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && $modalOverlay.classList.contains('open')) closeModal();
});

// ─── Progress bar ───────────────────────────────────────────────
function updateProgress() {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
  const progress = maxScroll > 0 ? (window.scrollY / maxScroll) * 100 : 0;
  $progressBar.style.width = progress + '%';
}

// ─── Search ─────────────────────────────────────────────────────
let searchTimeout;
$search.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentSearch = $search.value.trim();
    render();
  }, 150);
});

window.addEventListener('scroll', updateProgress, { passive: true });

// ─── Init ───────────────────────────────────────────────────────
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
