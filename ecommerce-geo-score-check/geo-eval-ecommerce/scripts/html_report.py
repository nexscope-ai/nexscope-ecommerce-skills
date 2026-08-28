"""Generate HTML report matching Nexscope GEO Visibility Report design."""
import json
import csv
import re
from pathlib import Path
from datetime import datetime, date
from collections import Counter, defaultdict
from urllib.parse import urlparse
import html as html_mod


def _pct(val):
    return f"{val*100:.1f}%"


def _domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url[:40]


def _esc(text):
    return html_mod.escape(str(text)) if text else ""


def _load_all_data(run_dir):
    run_dir = Path(run_dir)
    normalized_dir = run_dir / "normalized"
    eval_dir = run_dir / "eval"
    records = {}
    for f in sorted(normalized_dir.glob("*.json")):
        try:
            norm = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            continue
        stem = f.stem
        eval_path = eval_dir / f.name
        ev = None
        if eval_path.exists():
            try:
                ev = json.loads(eval_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        records[stem] = {"normalized": norm, "eval": ev}
    return records


CATEGORY_LABELS = {
    "discovery": "Discovery",
    "comparison": "Comparison",
    "purchase_advice": "Purchase Advice",
    "alternatives": "Alternatives",
    "trust_validation": "Trust Validation",
    "scenario": "Scenario",
    "problem_solving": "Problem Solving",
    "gift": "Gift",
    "feature": "Feature Search",
    "social_proof": "Social Proof",
}

CATEGORY_ORDER = ["discovery", "comparison", "purchase_advice", "alternatives", "trust_validation", "scenario", "problem_solving", "gift", "feature", "social_proof"]


CSS = """:root {
  --page:#f8fbff;
  --card:#fff;
  --ink:#0f172a;
  --text:#475569;
  --muted:#64748b;
  --border:#dbe6f3;
  --brand:#2563eb;
  --violet:#7c3aed;
  --ok:#059669;
  --warn:#d97706;
  --risk:#e11d48;
  --sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --serif:Georgia,"Times New Roman",serif;
}
* { box-sizing:border-box; }
html { scroll-behavior:smooth; scroll-padding-top:84px; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--sans); line-height:1.55; }
a { color:var(--brand); }
.topbar { position:sticky; top:0; z-index:20; border-bottom:1px solid var(--border); background:rgba(255,255,255,.92); backdrop-filter:blur(16px); }
.topbar-inner { max-width:1180px; margin:0 auto; padding:14px 28px; display:flex; justify-content:space-between; align-items:center; gap:16px; }
.brandmark { display:flex; align-items:baseline; gap:10px; text-decoration:none; color:var(--ink); }
.brandmark b { color:var(--brand); font-size:13px; font-weight:800; letter-spacing:.02em; }
.brandmark span { color:var(--muted); font-size:13px; }
.top-links { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.top-links a { border:1px solid var(--border); border-radius:999px; padding:7px 10px; background:white; color:var(--text); font-size:12px; font-weight:800; text-decoration:none; }
main { max-width:1180px; margin:0 auto; padding:38px 28px 72px; }
.cover { position:relative; overflow:hidden; padding:34px 0 40px; border-bottom:1px solid var(--border); }
.cover:before { content:""; position:absolute; inset:-120px -80px auto auto; width:520px; height:360px; background:radial-gradient(circle,rgba(124,58,237,.16),transparent 62%); pointer-events:none; }
.eyebrow { display:inline-flex; align-items:center; gap:8px; border:1px solid #bfdbfe; border-radius:999px; background:#eff6ff; color:var(--brand); padding:7px 12px; font-size:12px; font-weight:800; letter-spacing:.02em; }
h1,h2,h3 { font-family:var(--serif); letter-spacing:0; line-height:1.12; }
h1 { max-width:980px; margin:14px 0 18px; font-size:clamp(46px,7.4vw,82px); }
h2 { margin:0 0 12px; font-size:30px; }
h3 { margin:0 0 10px; font-size:21px; }
.lead { max-width:880px; color:var(--text); font-size:18px; }
.lead strong { color:var(--ink); }
.highlight { color:var(--brand); background:linear-gradient(180deg,transparent 58%,#dbeafe 0); padding:0 3px; }
.target-line { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
.tag { display:inline-flex; align-items:center; border-radius:999px; background:#eef5ff; color:#1d4ed8; padding:6px 10px; font-size:12px; font-weight:700; white-space:nowrap; }
.tag.primary { background:#ecfdf5; color:var(--ok); }
.tag.alt { background:#eff6ff; color:var(--brand); }
.tag.miss { background:#fff1f2; color:var(--risk); }
.tag.mentioned { background:#fff7ed; color:var(--warn); }
.tag.warn { background:#f5f3ff; color:var(--violet); }
.tag.muted { color:var(--muted); background:#f1f5f9; }
.metric-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin:24px 0; }
.metric-card { min-width:0; min-height:176px; padding:24px 28px; border:1px solid var(--border); border-radius:14px; background:rgba(255,255,255,.9); box-shadow:0 16px 40px rgba(15,23,42,.06); }
.metric-card span { display:inline; white-space:nowrap; color:var(--ink); font-size:18px; font-weight:600; line-height:1.18; background:linear-gradient(180deg,transparent 72%,#dbeafe 0); box-decoration-break:clone; -webkit-box-decoration-break:clone; padding:0 2px 1px; }
.metric-card.good span { background:linear-gradient(180deg,transparent 72%,#bbf7d0 0); }
.metric-card.mid span { background:linear-gradient(180deg,transparent 72%,#bfdbfe 0); }
.metric-card.risk span { background:linear-gradient(180deg,transparent 72%,#fed7aa 0); }
.metric-card strong { display:block; margin-top:8px; color:var(--ink); font-size:34px; line-height:1; }
.metric-card p { margin:9px 0 0; color:var(--text); font-size:13px; }
section { padding:32px 0; border-bottom:1px solid var(--border); }
.panel,.query-card { min-width:0; padding:20px; border:1px solid var(--border); border-radius:14px; background:var(--card); box-shadow:0 10px 30px rgba(15,23,42,.04); }
.verdict { position:relative; overflow:hidden; padding:0; border:0; border-radius:0; background:transparent; box-shadow:none; }
.verdict h2 { font-size:34px; }
.verdict-line { margin:0 0 14px; color:var(--text); font-size:17px; }
.verdict-line strong { color:var(--ink); }
.next-actions { display:grid; gap:8px; margin:14px 0 0; padding:0 0 0 20px; color:var(--text); }
.action-pill { display:list-item; padding-left:2px; color:var(--text); font-size:15px; }
.action-pill b { color:var(--brand); font-weight:800; }
.inline-risk { margin:18px 0 0; padding:16px 18px; border-left:4px solid #f97316; background:#fff7ed; border-radius:0 12px 12px 0; }
.inline-risk h3 { margin:0 0 6px; color:#9a3412; font-family:var(--sans); font-size:15px; font-weight:900; }
.risk-score { display:block; margin:0 0 6px; color:#c2410c; font-size:32px; line-height:1; font-weight:900; }
ul.clean { padding-left:18px; margin:10px 0 0; color:var(--text); list-style:disc outside; }
ul.clean li { margin:7px 0; }
table { width:100%; border-collapse:collapse; margin-top:12px; overflow:hidden; border-radius:8px; background:var(--card); }
th,td { padding:11px 10px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; font-size:13px; }
th { color:var(--brand); font-size:12px; font-weight:800; background:#eff6ff; }
tr:last-child td { border-bottom:0; }
.table-wrap { width:100%; overflow-x:auto; }
.summary-grid { display:grid; gap:14px; }
.single-card-section { display:grid; gap:14px; }
.query-list { display:grid; gap:14px; }
.query-head { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:16px; align-items:start; }
.query-status { border-radius:14px; background:#f8fafc; border:1px solid var(--border); padding:10px 12px; color:var(--text); font-size:13px; font-weight:800; text-align:right; }
.micro-label { display:block; color:var(--muted); font-size:11px; font-weight:800; line-height:1.45; }
.rank-table td:first-child { width:170px; }
.rank-table td:nth-child(2) { min-width:320px; color:var(--ink); }
.rank-table td:nth-child(3) { min-width:240px; }
.rank-list { display:grid; gap:6px; margin:0; padding:0; list-style:none; }
.rank-list li { display:grid; grid-template-columns:54px 1fr; gap:8px; align-items:start; padding:7px 8px; border:1px solid #e6edf7; border-radius:10px; background:#fbfdff; }
.rank-list li.target { border-color:#bfdbfe; background:#eff6ff; box-shadow:inset 3px 0 0 var(--brand); }
.rank-pos { display:inline-flex; align-items:center; justify-content:center; min-height:24px; border-radius:999px; background:#eef5ff; color:var(--brand); font-size:11px; font-weight:900; }
.rank-list li.target .rank-pos { background:#2563eb; color:white; }
.rank-freeform { padding:8px 10px; border:1px solid #e6edf7; border-radius:10px; background:#fbfdff; }
.sources { display:grid; gap:6px; }
.sources a,.sources span { display:block; border-radius:10px; background:#f8fafc; border:1px solid var(--border); padding:6px 8px; color:var(--text); font-size:11px; line-height:1.35; text-decoration:none; }
.muted { color:var(--muted); }
.service-cta { display:flex; align-items:center; justify-content:space-between; gap:22px; margin:24px 0; padding:22px; border:1px solid #bfdbfe; border-radius:18px; background:linear-gradient(135deg,#eff6ff,#f5f3ff); box-shadow:0 18px 50px rgba(37,99,235,.08); }
.service-cta p { max-width:720px; margin:0; color:var(--text); }
.service-eyebrow { color:var(--brand)!important; font-size:12px; font-weight:800; letter-spacing:.02em; }
.btn { display:inline-flex; align-items:center; justify-content:center; min-height:48px; padding:0 22px; border-radius:12px; font-size:14px; font-weight:800; text-decoration:none; }
.btn.primary { color:white; background:linear-gradient(135deg,var(--brand),var(--violet)); box-shadow:0 12px 28px rgba(124,58,237,.18); }
.footer-note { margin-top:24px; color:var(--muted); font-size:12px; }
.next-steps-section { margin-bottom:32px; }
.steps-table { width:100%; border-collapse:separate; border-spacing:0; }
.steps-table th { background:var(--card); padding:12px 16px; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); border-bottom:2px solid var(--border); text-align:left; }
.steps-table td { padding:16px; border-bottom:1px solid var(--border); vertical-align:top; font-size:14px; line-height:1.6; }
.steps-table tr:last-child td { border-bottom:none; }
.steps-table td strong { color:var(--ink); font-size:14px; }
.step-detail { color:var(--text); font-size:13px; }
.step-detail b { color:var(--ink); }
.rec-quote { margin-top:4px; font-size:12px; color:var(--muted); font-style:italic; line-height:1.4; }
.legend { font-size:12px; color:var(--muted); margin-bottom:16px; }
.legend .tag { font-size:11px; vertical-align:middle; }
.step-badge { display:flex; align-items:center; justify-content:center; width:44px; height:28px; border-radius:8px; font-size:12px; font-weight:900; letter-spacing:.02em; }
.step-p0 { background:#fee2e2; color:#dc2626; }
.step-p1 { background:#fff7ed; color:#ea580c; }
.step-p2 { background:#eff6ff; color:#2563eb; }
@media (max-width:760px) {
  main { padding:26px 16px 60px; }
  .topbar-inner { padding:12px 16px; align-items:flex-start; flex-direction:column; }
  h1 { font-size:36px; }
  .metric-grid { grid-template-columns:1fr; max-width:none; }
  .service-cta { align-items:flex-start; flex-direction:column; }
  .query-head { grid-template-columns:1fr; }
  .query-status { text-align:left; }
  th,td { min-width:150px; }
}"""


def _get_metric_class(mention_rate):
    if mention_rate >= 0.8:
        return "good"
    elif mention_rate >= 0.5:
        return "mid"
    return "risk"


def _get_pos_class(avg_pos):
    if avg_pos and avg_pos <= 2.0:
        return "good"
    elif avg_pos and avg_pos <= 3.0:
        return "mid"
    return "risk"


def _get_primary_class(primary_rate):
    if primary_rate >= 0.5:
        return "good"
    elif primary_rate >= 0.25:
        return "mid"
    return "risk"


_COMMON_WORDS = {
    "wireless", "bluetooth", "headphones", "earbuds", "earphones", "speaker", "portable",
    "monitor", "laptop", "tablet", "phone", "smartphone", "computer", "desktop",
    "keyboard", "mouse", "charger", "adapter", "cable", "dock", "hub",
    "case", "cover", "sleeve", "stand", "mount", "holder", "bracket",
    "camera", "printer", "router", "modem", "watch", "band", "strap",
    "with", "for", "and", "the", "in", "on", "by", "to", "of", "from",
    "inch", "mm", "cm", "new", "best", "top", "latest", "newest", "original",
    "edition", "version", "series", "model", "generation", "type", "style",
    "premium", "professional", "gaming", "office", "home", "outdoor", "travel",
    "compact", "lightweight", "heavy", "duty",
}

_VARIANT_WORDS = {
    "1tb", "2tb", "4tb", "8tb", "16tb",
    "8gb", "16gb", "32gb", "64gb", "128gb", "256gb", "512gb", "1024gb",
    "black", "white", "silver", "gold", "blue", "red", "green", "pink",
    "purple", "gray", "grey", "orange", "yellow", "brown", "beige", "cream",
    "navy", "teal", "coral", "rose", "ivory", "bronze", "copper",
    "titanium", "graphite", "midnight", "starlight", "natural", "desert",
    "space", "jet", "pacific", "alpine", "sierra", "phantom", "mystic",
    "matte", "glossy", "frosted", "transparent", "clear",
    "wifi", "wi-fi", "cellular", "lte", "5g", "gps",
    "small", "medium", "large", "xs", "xl", "xxl",
    "leather", "silicone", "fabric", "nylon", "stainless", "steel",
    "aluminum", "aluminium", "ceramic", "plastic", "rubber", "canvas",
    "mesh", "carbon", "fiber", "wood", "bamboo", "glass",
    "us", "uk", "eu", "global", "international",
    "bundle", "combo", "kit", "set", "pack", "pair",
}

_IGNORE_WORDS = _COMMON_WORDS | _VARIANT_WORDS


def _force_target_highlight(prods, product_name):
    """Match target product in recommendation list.
    Model/generation (M4, M5, Gen2) must match exactly.
    Variant attributes (color, storage, material) are ignored."""
    if not product_name:
        return
    name_lower = product_name.lower()
    name_words = set(name_lower.split())
    name_significant = name_words - _IGNORE_WORDS

    for i, p in enumerate(prods):
        pname = (p.get("product_name") or "").lower()
        if not pname:
            continue
        if name_lower in pname or pname in name_lower:
            p["is_target_product"] = True
            return

    best_idx = -1
    best_score = 0
    for i, p in enumerate(prods):
        pname = (p.get("product_name") or "").lower()
        if not pname:
            continue
        pname_words = set(pname.split())
        pname_significant = pname_words - _IGNORE_WORDS
        missing = name_significant - pname_significant
        if missing:
            continue
        score = len(name_significant & pname_significant)
        if score > best_score:
            best_score = score
            best_idx = i

    if best_score >= 2 and best_idx >= 0:
        prods[best_idx]["is_target_product"] = True


def _status_tag(ev):
    mentioned = ev.get("mentioned", False)
    rec_strength = ev.get("recommendation_strength", "not_mentioned")
    position = ev.get("position")
    mention_form = ev.get("mention_form", "not_mentioned")

    if not mentioned:
        return '<span class="tag miss">Not Mentioned</span>', '<span class="tag muted">' + _esc(mention_form.replace("_", " ").title()) + '</span>'

    if rec_strength == "primary":
        tag = '<span class="tag primary">Primary #' + str(position or "?") + '</span>'
    elif rec_strength == "alternative":
        tag = '<span class="tag alt">Alt #' + str(position or "?") + '</span>'
    else:
        tag = '<span class="tag mentioned">Mentioned #' + str(position or "?") + '</span>'

    form_tag = '<span class="tag muted">' + _esc(mention_form.replace("_", " ").title()) + '</span>'
    return tag, form_tag


def _query_outcome_summary(engines_data):
    counts = Counter()
    misses = 0
    for engine, data in engines_data.items():
        ev = data.get("eval") or {}
        if not ev.get("mentioned"):
            misses += 1
        else:
            rs = ev.get("recommendation_strength", "mention_only")
            if rs == "primary":
                counts["Primary"] += 1
            elif rs == "alternative":
                counts["Alternative"] += 1
            else:
                counts["Mentioned"] += 1
    parts = []
    for label in ["Primary", "Alternative", "Mentioned"]:
        if counts[label] > 0:
            parts.append(str(counts[label]) + " " + label)
    if misses > 0:
        parts.append(str(misses) + " Missed")
    return ", ".join(parts) if parts else "No Data"


def _primary_wins(engines_data):
    wins = sum(1 for d in engines_data.values() if (d.get("eval") or {}).get("recommendation_strength") == "primary")
    return str(wins) + "/" + str(len(engines_data))


def _misses_count(engines_data):
    return sum(1 for d in engines_data.values() if not (d.get("eval") or {}).get("mentioned"))


def _build_lead_text(mention_rate, primary_rate, avg_pos, product_name):
    name = _esc(product_name) or "Target product"
    if mention_rate >= 0.8 and primary_rate < 0.4:
        return '<strong>High AI visibility, weak first-choice ownership.</strong> LLMs mention this product often, but the <span class="highlight">' + _pct(primary_rate) + ' primary recommendation rate</span> shows the main growth gap.'
    elif mention_rate >= 0.8 and primary_rate >= 0.4:
        return '<strong>Strong AI visibility and recommendation.</strong> ' + name + ' is both frequently mentioned (' + _pct(mention_rate) + ') and often the <span class="highlight">primary recommendation (' + _pct(primary_rate) + ')</span>.'
    elif mention_rate >= 0.5:
        return '<strong>Moderate visibility with room to grow.</strong> ' + name + ' appears in ' + _pct(mention_rate) + ' of AI responses. <span class="highlight">Primary recommendation rate is ' + _pct(primary_rate) + '</span>.'
    else:
        return '<strong>Low AI visibility — urgent action needed.</strong> ' + name + ' only appears in <span class="highlight">' + _pct(mention_rate) + '</span> of AI responses.'


def _build_verdict(mention_rate, primary_rate, avg_pos, product_name, top_competitors, by_category, by_query):
    name = _esc(product_name) or "Target product"
    top_comp = top_competitors[0]["name"] if top_competitors else "competitors"

    weak_cats = []
    for cat in CATEGORY_ORDER:
        qids = by_category.get(cat, [])
        misses = 0
        for qid in qids:
            engines_data = by_query.get(qid, {})
            misses += sum(1 for d in engines_data.values() if not (d.get("eval") or {}).get("mentioned"))
        if misses > 0:
            weak_cats.append((cat, misses))
    weak_cats.sort(key=lambda x: -x[1])

    parts = []
    if mention_rate >= 0.8 and primary_rate < 0.4:
        parts.append('<p class="verdict-line"><strong>' + name + ' is visible, but not yet the default answer.</strong> It appears in most AI responses, while ' + _esc(top_comp) + ' still wins many first-choice recommendations in broad discovery and purchase-advice questions.</p>')
    elif mention_rate >= 0.8 and primary_rate >= 0.4:
        parts.append('<p class="verdict-line"><strong>' + name + ' has strong overall AI presence.</strong> Focus on maintaining first-choice position and closing remaining gaps in specific query categories.</p>')
    else:
        parts.append('<p class="verdict-line"><strong>' + name + ' needs visibility improvements across multiple categories.</strong> AI engines are not consistently recommending this product.</p>')

    parts.append('<ul class="next-actions">')
    if weak_cats:
        weak_label = CATEGORY_LABELS.get(weak_cats[0][0], weak_cats[0][0])
        parts.append('<li class="action-pill"><b>Fix First:</b> ' + weak_label + ' queries where AI misses ' + name + ' or generic answers favor competitors.</li>')
    parts.append('<li class="action-pill"><b>Positioning:</b> Make ' + name + " key features and USPs easier for LLMs to quote as primary recommendation.</li>")
    parts.append('<li class="action-pill"><b>Source Gap:</b> Strengthen third-party comparison and review pages where ' + _esc(top_comp) + ' currently defines the category narrative.</li>')
    parts.append('</ul>')

    parts.append('<div class="inline-risk">')
    parts.append('<h3>Main Risk</h3>')
    if mention_rate < 0.4:
        parts.append('<span class="risk-score">' + _pct(mention_rate) + '</span>')
        parts.append('<p class="verdict-line">AI engines are not mentioning this product in most shopping queries.</p>')
        parts.append('<p class="verdict-line"><strong>Priority:</strong> increase presence across all LLMs before optimizing ranking position.</p>')
    elif primary_rate < 0.3:
        parts.append('<span class="risk-score">' + _pct(primary_rate) + '</span>')
        parts.append('<p class="verdict-line">Primary recommendation rate is critically low. AI mentions the product but almost never as first choice.</p>')
        parts.append('<p class="verdict-line"><strong>Priority:</strong> strengthen USP positioning so LLMs recommend as top pick, not just an option.</p>')
    elif primary_rate < 0.5:
        parts.append('<span class="risk-score">' + _pct(primary_rate) + '</span>')
        parts.append('<p class="verdict-line">Primary recommendation rate is too low for a product that already has strong mention coverage.</p>')
        parts.append('<p class="verdict-line"><strong>Priority:</strong> convert mentions into first choice.</p>')
    else:
        parts.append('<span class="risk-score">' + _pct(mention_rate) + '</span>')
        parts.append('<p class="verdict-line">Strong first-choice position. Main risk is coverage gaps in specific query categories.</p>')
        parts.append('<p class="verdict-line"><strong>Priority:</strong> expand into weak query categories and defend against rising competitors.</p>')
    parts.append('</div>')

    return "\n        ".join(parts)


def _build_next_steps(mention_rate, primary_rate, top_competitors, product_name, by_category, by_query, engine_stats):
    from scripts._next_steps import build_next_steps
    return build_next_steps(mention_rate, primary_rate, top_competitors, product_name,
                            by_category, by_query, engine_stats, CATEGORY_LABELS, CATEGORY_ORDER, _pct)

def generate_report(run_dir, base_dir, profile):
    run_dir = Path(run_dir)
    preag_path = run_dir / "preaggregate.json"

    if not preag_path.exists():
        return None, "preaggregate.json not found"

    preag = json.loads(preag_path.read_text(encoding="utf-8"))
    records = _load_all_data(run_dir)

    product_path = Path(base_dir) / "profiles" / profile / "product.md"
    product_name = ""
    if product_path.exists():
        for line in product_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if "Name:" in s or "Product:" in s:
                product_name = s.split(":", 1)[-1].strip()
                break

    queries_path = Path(base_dir) / "profiles" / profile / "queries.csv"
    query_meta = {}
    if queries_path.exists():
        with open(queries_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                query_meta[row["id"]] = row

    summary = preag.get("summary", {})
    engine_stats = preag.get("engine_stats", {})
    top_competitors = preag.get("top_competitors", [])
    signals = preag.get("shopping_signals", {})
    rec_strengths = preag.get("recommendation_strengths", {})

    mention_rate = summary.get("mention_rate", 0)
    avg_pos = summary.get("avg_position")
    total_evals = summary.get("total_evaluations", 0)
    primary_rate = rec_strengths.get("primary", 0) / max(total_evals, 1)

    by_query = defaultdict(dict)
    for stem, data in records.items():
        qid = data["normalized"].get("query_id", "")
        engine = data["normalized"].get("engine", "")
        by_query[qid][engine] = data

    by_category = defaultdict(list)
    for qid in sorted(by_query.keys()):
        cat = query_meta.get(qid, {}).get("category", "other")
        by_category[cat].append(qid)

    all_citations = []
    for stem, data in records.items():
        for c in data["normalized"].get("citations", []):
            c_copy = dict(c)
            c_copy["engine"] = data["normalized"].get("engine", "")
            c_copy["query_id"] = data["normalized"].get("query_id", "")
            all_citations.append(c_copy)

    domain_counts = Counter(_domain(c.get("url", "")) for c in all_citations if c.get("url"))

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_year = str(date.today().year)

    # BUILD HTML
    h = []
    h.append('<!doctype html>\n<html lang="en">\n<head>')
    h.append('  <meta charset="utf-8">')
    h.append('  <meta name="viewport" content="width=device-width, initial-scale=1">')
    h.append('  <title>' + _esc(product_name or profile) + ' GEO Visibility Report | Nexscope</title>')
    h.append('  <style>\n' + CSS + '\n  </style>')
    h.append('</head>\n<body>')

    # Topbar
    h.append('  <header class="topbar">')
    h.append('    <div class="topbar-inner">')
    h.append('      <a class="brandmark" href="https://www.nexscope.ai/"><b>Nexscope</b><span>Ecommerce AI Visibility Report</span></a>')
    h.append('      <nav class="top-links">')
    h.append('        <a href="#overview">Overview</a>')
    h.append('        <a href="#query-summary">Queries</a>')
    h.append('        <a href="#rankings">Rankings</a>')
    h.append('        <a href="#next-steps">Next Steps</a>')
    h.append('      </nav>')
    h.append('    </div>')
    h.append('  </header>')
    h.append('')
    h.append('  <main>')

    # Cover
    lead_text = _build_lead_text(mention_rate, primary_rate, avg_pos, product_name)
    h.append('    <header class="cover" id="overview">')
    h.append('      <div class="eyebrow">Ecommerce GEO Visibility</div>')
    h.append('      <h1>' + _esc(product_name or profile) + '</h1>')
    h.append('      <p class="lead">' + lead_text + '</p>')
    h.append('      <div class="target-line">')
    h.append('        <span class="tag">United States</span>')
    h.append('        <span class="tag">Ecommerce Product</span>')
    h.append('        <span class="tag warn">LLM Ranking + Shopping Signals</span>')
    h.append('        <span class="tag muted">' + now_str + '</span>')
    h.append('        <span class="tag muted">' + str(total_evals) + ' evaluations</span>')
    h.append('      </div>')

    mr_class = "good"
    pos_class = "mid"
    pr_class = "risk" 
    avg_pos_str = ("%.1f" % avg_pos) if avg_pos else "N/A"

    h.append('      <div class="metric-grid">')
    h.append('        <article class="metric-card ' + mr_class + '">')
    h.append('          <span>Mention Rate</span>')
    h.append('          <strong>' + _pct(mention_rate) + '</strong>')
    h.append('          <p>' + _esc(product_name or "Target product") + ' appears in AI answers.</p>')
    h.append('        </article>')
    h.append('        <article class="metric-card ' + pos_class + '">')
    h.append('          <span>Average Position</span>')
    h.append('          <strong>' + avg_pos_str + '</strong>')
    h.append('          <p>Average visible rank when listed.</p>')
    h.append('        </article>')
    h.append('        <article class="metric-card ' + pr_class + '">')
    h.append('          <span>Primary Recommendation Rate</span>')
    h.append('          <strong>' + _pct(primary_rate) + '</strong>')
    h.append('          <p>How often AI makes it the first choice.</p>')
    h.append('        </article>')
    h.append('      </div>')
    h.append('    </header>')

    # Verdict
    verdict_text = _build_verdict(mention_rate, primary_rate, avg_pos, product_name, top_competitors, by_category, by_query)
    h.append('')
    h.append('    <section class="summary-grid">')
    h.append('      <div class="panel verdict">')
    h.append('        <h2>Read This First</h2>')
    h.append('        ' + verdict_text)
    h.append('      </div>')
    h.append('    </section>')

    # Top Competitors (placed after overview for immediate competitive context)
    if top_competitors:
        h.append('')
        h.append('    <section class="single-card-section">')
        h.append('      <h2>Top Competitors</h2>')
        h.append('      <article class="panel">')
        h.append('        <div class="table-wrap"><table><thead><tr><th>Competitor</th><th>Mentions</th><th>Rate</th><th>Avg Pos</th><th>Primary Rate</th></tr></thead><tbody>')
        for comp in top_competitors[:8]:
            ap = comp.get("avg_position")
            ap_str = ("%.1f" % ap) if ap else "-"
            h.append('<tr><td>' + _esc(comp["name"]) + '</td><td>' + str(comp["mention_count"]) + '</td><td>' + _pct(comp["mention_rate"]) + '</td><td>' + ap_str + '</td><td>' + _pct(comp["primary_rate"]) + '</td></tr>')
        h.append('</tbody></table></div>')
        h.append('      </article>')
        h.append('    </section>')

    # Question Summary
    h.append('')
    h.append('    <section id="query-summary">')
    h.append('      <h2>Question Summary</h2>')
    h.append('      <p class="lead">Every tested question is listed here first. The full LLM-by-LLM rankings are in the next section.</p>')
    h.append('      <div class="table-wrap">')
    h.append('        <table>')
    h.append('          <thead>')
    h.append('            <tr><th>ID</th><th>Intent</th><th>Question</th><th>Outcome</th><th>Primary Wins</th><th>Misses</th></tr>')
    h.append('          </thead>')
    h.append('          <tbody>')

    for cat in CATEGORY_ORDER:
        qids = by_category.get(cat, [])
        cat_label = CATEGORY_LABELS.get(cat, cat)
        cat_count = len(qids)
        for qid in qids:
            engines_data = by_query[qid]
            qm = query_meta.get(qid, {})
            query_text = qm.get("query", "").replace("{{year}}", current_year)
            outcome = _query_outcome_summary(engines_data)
            pw = _primary_wins(engines_data)
            mc = _misses_count(engines_data)
            h.append('          <tr>')
            h.append('            <td>' + _esc(qid) + '</td>')
            h.append('            <td>' + _esc(cat_label) + ' (' + str(cat_count) + ' queries)</td>')
            h.append('            <td>' + _esc(query_text) + '</td>')
            h.append('            <td>' + _esc(outcome) + '</td>')
            h.append('            <td>' + pw + '</td>')
            h.append('            <td>' + str(mc) + '</td>')
            h.append('          </tr>')

    h.append('          </tbody>')
    h.append('        </table>')
    h.append('      </div>')
    h.append('    </section>')

    # Rankings
    h.append('')
    h.append('    <section id="rankings">')
    h.append('      <h2>Ranking Details By Question</h2>')
    h.append('      <p class="lead">Each card shows the buyer question, then the ranking returned by each LLM.</p>')
    h.append('      <p class="legend"><span class="tag primary">Primary</span> = explicitly named as the best choice. <span class="tag alt">Alt</span> = recommended as one of several options. <span class="tag mentioned">Mentioned</span> = referenced without endorsement. Position shows list order.</p>')
    h.append('      <div class="query-list">')

    for cat in CATEGORY_ORDER:
        qids = by_category.get(cat, [])
        for qid in qids:
            engines_data = by_query[qid]
            qm = query_meta.get(qid, {})
            query_text = qm.get("query", "").replace("{{year}}", current_year)
            cat_label = CATEGORY_LABELS.get(cat, cat)
            persona = qm.get("user_persona", "")
            notes = qm.get("notes", "")
            outcome = _query_outcome_summary(engines_data)

            h.append('        <article class="query-card">')
            h.append('          <div class="query-head">')
            h.append('            <div>')
            h.append('              <span class="micro-label">' + _esc(qid) + ' | ' + _esc(cat_label) + ' | ' + _esc(persona) + ' | ' + _esc(notes) + '</span>')
            h.append('              <h3>' + _esc(query_text) + '</h3>')
            h.append('            </div>')
            h.append('            <div class="query-status">' + _esc(outcome) + '</div>')
            h.append('          </div>')
            h.append('          <div class="table-wrap">')
            h.append('            <table class="rank-table">')
            h.append('              <thead>')
            h.append('                <tr><th>LLM</th><th>Ranking Returned</th><th>Citation Links</th></tr>')
            h.append('              </thead>')
            h.append('              <tbody>')

            for engine in sorted(engines_data.keys()):
                data = engines_data[engine]
                ev = data.get("eval") or {}
                norm = data["normalized"]
                status_tag, form_tag = _status_tag(ev)
                prods = ev.get("product_recommendations", [])
                if ev.get("mentioned") and prods and not any(p.get("is_target_product") for p in prods):
                    _force_target_highlight(prods, product_name)
                cites = norm.get("citations", [])

                rec_quote = ev.get("recommendation_quote", "")
                h.append('            <tr>')
                quote_html = '<div class="rec-quote">&ldquo;' + _esc(rec_quote) + '&rdquo;</div>' if rec_quote else ''
                h.append('              <td><strong>' + _esc(engine.title()) + '</strong><br>' + status_tag + ' ' + form_tag + quote_html + '</td>')

                if prods:
                    h.append('              <td><ol class="rank-list">')
                    for p in prods[:6]:
                        is_target = p.get("is_target_product", False)
                        pos = p.get("position", "?")
                        pname = p.get("product_name", "Unknown")
                        price = p.get("price_mentioned", "")
                        price_str = " (" + _esc(price) + ")" if price else ""
                        li_class = ' class="target"' if is_target else ' class=""'
                        pos_label = "#" + str(pos) if isinstance(pos, int) else "Mentioned"
                        h.append('<li' + li_class + '><span class="rank-pos">' + pos_label + '</span><span>' + _esc(pname) + price_str + '</span></li>')
                    h.append('</ol></td>')
                else:
                    response = norm.get("response_content", "")
                    snippet = response[:150].replace("\n", " ").strip()
                    if len(response) > 150:
                        snippet += "..."
                    h.append('              <td><div class="rank-freeform">' + _esc(snippet) + '</div></td>')

                h.append('              <td><div class="sources">')
                if cites:
                    for c in cites[:4]:
                        title = c.get("title", "") or _domain(c.get("url", ""))
                        url = c.get("url", "")
                        h.append('<a href="' + _esc(url) + '" target="_blank" rel="noopener">' + _esc(title) + '</a> ')
                else:
                    h.append('<span class="muted">No sources captured</span>')
                h.append('</div></td>')
                h.append('            </tr>')

            h.append('              </tbody>')
            h.append('            </table>')
            h.append('          </div>')
            h.append('        </article>')

    h.append('      </div>')
    h.append('    </section>')

    # LLM Comparison
    h.append('')
    h.append('    <section class="single-card-section">')
    h.append('      <h2>LLM Comparison</h2>')
    h.append('      <article class="panel">')
    h.append('        <div class="table-wrap"><table><thead><tr><th>LLM</th><th>Queries</th><th>Mention</th><th>Avg Pos</th><th>Primary</th><th>Alternative</th></tr></thead><tbody>')
    for engine in sorted(engine_stats.keys()):
        stats = engine_stats[engine]
        mr = stats.get("mention_rate", 0)
        ap = stats.get("avg_position")
        ap_str = ("%.1f" % ap) if ap else "-"
        rs = stats.get("rec_strengths", {})
        h.append('<tr><td>' + _esc(engine.title()) + '</td><td>' + str(stats.get("total", 0)) + '</td><td>' + _pct(mr) + '</td><td>' + ap_str + '</td><td>' + str(rs.get("primary", 0)) + '</td><td>' + str(rs.get("alternative", 0)) + '</td></tr>')
    h.append('</tbody></table></div>')
    h.append('      </article>')
    h.append('    </section>')

    # Shopping Signals
    h.append('')
    h.append('    <section id="sources" class="single-card-section">')
    h.append('      <h2>Shopping Signals</h2>')
    h.append('      <article class="panel">')
    sr = signals.get("signal_rates", {})
    h.append('        <div class="table-wrap"><table><thead><tr><th>Signal</th><th>Rate</th><th>Meaning</th></tr></thead><tbody>')
    signal_info = [
        ("has_price_info", "Contains Price Info", "AI response includes specific prices"),
        ("has_purchase_links", "Contains Purchase Links", "AI gives URLs or store names to buy"),
        ("has_comparison_table", "Has Comparison Table", "AI formats a side-by-side comparison"),
        ("has_pros_cons", "Lists Pros and Cons", "AI lists advantages/disadvantages"),
    ]
    for key, label, desc in signal_info:
        val = sr.get(key, 0)
        h.append('<tr><td>' + label + '</td><td>' + _pct(val) + '</td><td>' + desc + '</td></tr>')
    h.append('</tbody></table></div>')
    h.append('      </article>')
    h.append('    </section>')

    # Top Cited Domains
    h.append('')
    h.append('    <section class="single-card-section">')
    h.append('      <h2>Top Cited Domains</h2>')
    h.append('      <article class="panel">')
    h.append('        <div class="table-wrap"><table><thead><tr><th>Domain</th><th>Times Cited</th></tr></thead><tbody>')
    for domain, count in domain_counts.most_common(10):
        h.append('<tr><td>' + _esc(domain) + '</td><td>' + str(count) + '</td></tr>')
    h.append('</tbody></table></div>')
    h.append('      </article>')
    h.append('    </section>')



    # Next Steps (table at bottom)
    steps = _build_next_steps(mention_rate, primary_rate, top_competitors, product_name, by_category, by_query, engine_stats)
    h.append('')
    h.append('    <section id="next-steps" class="next-steps-section">')
    h.append('      <h2>Next Steps</h2>')
    h.append('      <p class="lead">Prioritized actions to improve AI visibility and recommendation strength.</p>')
    h.append('      <div class="table-wrap">')
    h.append('        <table class="steps-table">')
    h.append('          <thead><tr><th style="width:60px">Priority</th><th style="width:280px">Action</th><th>Details</th></tr></thead>')
    h.append('          <tbody>')
    for priority, title, detail in steps:
        if priority == "P0":
            badge_class = "step-p0"
        elif priority == "P1":
            badge_class = "step-p1"
        else:
            badge_class = "step-p2"
        h.append('            <tr>')
        h.append('              <td><span class="step-badge ' + badge_class + '">' + priority + '</span></td>')
        h.append('              <td><strong>' + title + '</strong></td>')
        h.append('              <td class="step-detail">' + detail + '</td>')
        h.append('            </tr>')
    h.append('          </tbody>')
    h.append('        </table>')
    h.append('      </div>')
    h.append('    </section>')

    # CTA
    h.append('')
    h.append('    <section>')
    h.append('      <div class="service-cta">')
    h.append('        <div>')
    h.append('          <p class="service-eyebrow">Nexscope Services</p>')
    h.append('          <h2>Need Help Turning This Into A Fix Plan?</h2>')
    h.append('          <p>Nexscope Ecommerce Growth Services can prioritize AI visibility gaps, product content, review-source outreach, schema, and marketplace-ready optimization.</p>')
    h.append('        </div>')
    h.append('        <a class="btn primary" href="https://www.nexscope.ai/ecommerce-growth-services?co-from=Pgeo">Talk To A GEO Expert</a>')
    h.append('      </div>')
    h.append('      <p class="footer-note">Generated by Nexscope GEO Eval for Ecommerce. Data from ' + str(total_evals) + ' AI engine evaluations across ' + str(len(by_query)) + ' buyer questions.</p>')
    h.append('    </section>')

    h.append('  </main>')
    h.append('</body>')
    h.append('</html>')

    html_content = "\n".join(h)
    report_path = run_dir / "report.html"
    report_path.write_text(html_content, encoding="utf-8")
    return report_path, None
