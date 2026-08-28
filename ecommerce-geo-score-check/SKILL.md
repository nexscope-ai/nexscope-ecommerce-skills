---
name: ecommerce-geo-score-check
description: "Score an ecommerce URL for SEO + GEO readiness and AI citation visibility. Triggers on \"geo score\", \"SEO + GEO score\", \"check ecommerce GEO\", \"Amazon/Shopify GEO\", \"GEO readiness audit\". Covers product pages, store pages, marketplace listings, category pages, and homepages, scored from crawlable evidence (not live AI polling)."
---

# Ecommerce GEO Score

## Overview

Use this skill to evaluate how ready an ecommerce URL is for SEO, GEO, AI visibility, citations, and product recommendation discovery.

The default output is a **Quick SEO + GEO Readiness Score** based on evidence that can be detected from the page, HTML, metadata, images, schema, robots, sitemap, llms files, and marketplace/listing content. It is not a live AI mention-rate report unless the user explicitly asks for live AI polling and the relevant polling workflow is available.

## Workflow

1. Confirm the target URL and target market.
   - Default market: United States.
   - **If the user gives no URL, you MUST ask for one before proceeding.** Do not guess, assume, or skip this step. Reply with a short prompt like: "Please share the URL you'd like me to check (e.g. your product page, store homepage, or marketplace listing link)."
   - If the user gives Amazon, TikTok Shop, Walmart, Shopify, or a DTC page, continue; do not assume only independent websites are valid.

2. Decide the evidence mode.
   - **DTC / Shopify / brand site mode:** inspect HTML, metadata, schema, images, robots.txt, sitemap.xml, llms.txt / llms-full.txt, and crawlable page copy.
   - **Marketplace listing mode:** inspect listing-visible evidence such as title, product name, category, bullets, images, A+ / rich content, reviews, ratings, Q&A, price, delivery/return proof, brand clarity, and buyer-intent coverage. Do not penalize the seller for platform-owned signals such as Amazon robots, sitemap, llms.txt, or Core Web Vitals.
   - **Blocked crawl mode:** if the page returns 403, bot protection, or no useful body, say what failed and request product facts or a screenshot/listing export. Do not invent page evidence.

3. Run the quick scorer when a local reproducible score is useful:

   ```bash
   node /Users/edy/.codex/skills/ecommerce-geo-score/scripts/quick_geo_score.mjs "https://example.com/product-url" --market US --json
   ```

   The script is a deterministic helper, not the only allowed path. If better browser/page evidence is available, use it and keep the same scoring contract.

4. Score the page with the eight-dimension model in `references/scoring-model.md`.

5. Produce a concise result:
   - Overall SEO + GEO readiness score.
   - Four summary scores: SEO Score, GEO / AI Visibility, Technical Health, Content Authority.
   - Eight detailed score cards.
   - Detected evidence.
   - Recommendations based only on detected gaps.
   - Evidence boundary: state whether this is quick readiness or live AI polling.

6. **Generate HTML report (MANDATORY - do NOT skip):**
   - You MUST first run: `Read /root/.claude/skills/ecommerce-geo-score-check/references/report-template.html`
   - You MUST read the ENTIRE template file BEFORE writing any HTML.
   - Copy the template's CSS and HTML structure exactly. Only replace data values.
   - If you did NOT read the template file, STOP and read it now. Do NOT generate HTML from memory or invent your own design.
   - Save the report to the workspace output directory.

7. **Write the HTML report using a Python script file (MANDATORY technique):**
   - Do NOT use Write tool, Bash heredoc, or single-line echo/printf to write the HTML. These WILL fail due to permission blocks or special characters.
   - Instead: write a Python script to a .py file first, then execute it. Example:
     ```
     Step A: Write /tmp/gen_report.py (a Python script that opens the output file and writes all HTML sections)
     Step B: Run `python3 /tmp/gen_report.py`
     ```
   - The Python script MUST write ALL sections in one execution. Do NOT split into multiple partial writes that can lose data.
   - If the script is too long for one Write call, split into 2-3 script files that each append to the same output file, but each script MUST be self-contained (no dependencies on previous writes succeeding).

8. **Verify report completeness BEFORE upload (MANDATORY - do NOT skip):**
   - After writing the HTML file, you MUST run: `wc -l <file>` and `wc -c <file>`
   - **Size check:** If the file is less than 15KB or less than 300 lines, it is INCOMPLETE. Do NOT upload. Regenerate the missing sections.
   - **Content check:** Run `grep -c "score-card-detail" <file>` — must return 8 (one per dimension). If less than 8, the report is missing dimension cards.
   - **Content check:** Run `grep -c "recommendation-item" <file>` — must return 5-8. If 0, recommendations are missing.
   - **Content check:** Run `grep -c "PASS\|FAIL\|WARN" <file>` — must return 20+. If less, evidence table is missing.
   - Only upload AFTER all checks pass. A 3KB file with only the header is NOT a report.

## Evidence Boundary

Never present quick readiness as live AI visibility.

Allowed:
- "This page is ready for AI systems to understand and cite."
- "The page has strong/weak AI citation readiness signals."
- "The page still needs live AI polling to measure actual AI recommendation rate."

Not allowed unless live polling was actually run:
- AI recommendation rate.
- First recommendation rate.
- Average rank in ChatGPT / Gemini / Claude / Perplexity.
- Competitor mention share from AI answers.
- Source/citation URLs from AI responses.

Do not use or imply guaranteed profitable products, guaranteed sales growth, or guaranteed AI recommendations.

## Platform Rules

Read `references/platform-handling.md` before scoring Amazon, TikTok Shop, Walmart, or other marketplace URLs. Marketplace pages can be scored, but the dimensions must be interpreted as listing-readiness rather than site-infrastructure readiness.

## Report Contract

Use `references/report-contract.md` for the preferred JSON shape and user-facing report layout. If the user asks for a handoff to engineering, include persistence requirements:

- Store every report JSON in a database.
- Use stable `/geo-check/report/{checkId}` URLs.
- Do not rely on frontend memory, server runtime maps, or local files for report access.
- If email delivery is part of the flow, specify subject, body, CTA URLs, channel parameters, and backend archive requirements.


## Conversation Output Format (MANDATORY - follow exactly)

The conversation output MUST be detailed and comprehensive. Do NOT output a short summary. Follow this EXACT structure with FULL detail for every section:

---

### 1. Header Block

```
🎯 SEO + GEO Readiness Score Report
Target URL: https://example.com/product
Market: United States
Platform: DTC Brand Site
Category: Consumer Electronics
Assessment Type: Quick Readiness (not live AI polling)
```

### 2. Overall Score + Summary Table

State the overall score prominently, then show 4 summary dimensions:

```
Overall Score: 82/100 — Strong

| Summary Dimension | Score |
|---|---|
| SEO Score | **85**/100 |
| GEO / AI Visibility | **78**/100 |
| Technical Health | **80**/100 |
| Content Authority | **88**/100 |
```

### 3. Eight-Dimension Score Cards (MUST include all 8)

Each dimension MUST be a Signal | Evidence table. The Evidence column MUST start with a status emoji:
- ✅ = pass / good signal detected
- ❌ = fail / missing / not detected
- ⚠️ = warning / partial issue

Each dimension MUST have 4-8 rows covering both good and bad signals. Example:

```
#### 1. On-Page SEO — 86/100

| Signal | Evidence |
|---|---|
| Title tag | ✅ Present: "MacBook Air - Apple" (unique, descriptive) |
| Meta description | ✅ Contains product name + key feature |
| H1 heading | ✅ Clear, singular product heading detected |
| Image alt text | ✅ Present on hero product images |
| Price in meta | ❌ Not mentioned in metadata |
| Long-tail keywords | ⚠️ Missing secondary keyword variants |
```

All 8 dimensions MUST be output: On-Page SEO, Technical SEO, Schema/Structured Data, Content Depth, AI Crawlability, Citation Readiness, Competitive Positioning, User Intent Coverage.

### 4. Key Recommendations (MUST be detailed)

Priority headers use colored circle emoji. Individual items are plain numbered (NO emoji before the number):

```
🔴 **HIGH PRIORITY**

**1. Create llms.txt + llms-full.txt**

**Problem:** /llms.txt returns 404. AI search engines use this file to instantly understand site structure.

**Impact:** Without llms.txt, AI relies on slow crawls that miss JS content. Competitors with llms.txt get cited first.

**Action Steps:**
- Create /llms.txt with site overview, product lines, canonical URLs
- Create /llms-full.txt with full specs, pricing, audience segments
- Follow llms-txt.cloud spec: Markdown, text/plain, SSR
- Include competitive claims AI should cite
- Update with each product cycle

---

**2. Add Product Schema (JSON-LD)**

**Problem:** No Product JSON-LD detected...
**Impact:** 15-30% CTR loss...
**Action Steps:**
- ...

🟡 **MEDIUM PRIORITY**

**4. Server-Side Render Critical Content**
...

🟢 **LOW PRIORITY**

**7. Create Structured Comparison Content**
...
```

EVERY recommendation MUST include Problem + Impact + Action Steps (3-7 bullet points each). Do NOT just list one-line summaries.

### 5. Evidence Boundary

State: "This is a Quick SEO + GEO Readiness assessment based on crawlable signals. Not live AI polling."

### 6. HTML Report Link

Always end with a clickable link to the uploaded HTML report:
```
📎 **HTML online report:** `<generated report URL>`
```

---

**OUTPUT LENGTH:** The full conversation output should be 800-1500 lines of Markdown. If your output is shorter than 400 lines, you are missing detail. Go back and add more evidence rows and more action steps to recommendations.

## HTML Report Template (MANDATORY - ABSOLUTE PATH)

⚠️ **STOP: Before writing ANY HTML, you MUST read the template file first. If you have not yet called `Read` on the path below, do it NOW. Do NOT proceed without reading it. Do NOT generate HTML from your own knowledge.**

When generating an HTML report, you MUST:

1. **FIRST ACTION:** Read the template file at this ABSOLUTE path: `/root/.claude/skills/ecommerce-geo-score-check/references/report-template.html` — You MUST call the Read tool on this file. This is not optional. If you skip this step, the report will be wrong.
2. Use that file as the EXACT base template. Copy its CSS and HTML structure verbatim.
3. Replace ALL data placeholders with actual analysis results. Every section must be fully populated.
4. Do NOT invent your own CSS, color scheme, layout, or HTML structure. The template is authoritative.
5. The HTML report MUST contain the SAME detailed recommendations as the conversation output (Problem + Impact + Action Steps for each).

### ⚠️ COMPLETENESS CHECK — the HTML report MUST include ALL of these sections with REAL data (not empty, not placeholder):

| Section | Required Content | If Missing = FAIL |
|---|---|---|
| Cover + metric-grid | 5 score cards (Overall, SEO, GEO/AI, Technical, Content) with real numbers | ❌ |
| Evidence boundary | Two-col: left = assessment type explanation, right = target URL + market + platform + category | ❌ |
| Evidence table | Full `<table>` with 20-40 rows: Signal / Status (PASS/FAIL/WARN) / Evidence detail | ❌ |
| Score detail grid | ALL 8 dimension cards, each with: score-pill, progress bar, 2-4 "What Looks Good" + 2-4 "What Needs Work" findings | ❌ |
| Recommendations | 5-8 numbered items, each with h3 title + pri-badge + 4-8 bullet action steps | ❌ |
| Footer | Evidence boundary disclaimer + generation date | ❌ |

**If your HTML report is missing ANY of the above sections, it is INCOMPLETE. Go back and add the missing sections before uploading.**

A report with only the cover/header and no body content is NOT acceptable. The full report should be 400-800 lines of HTML.

### Critical CSS Variables (copy exactly):
```css
:root {
  --page:#f7f9fc;--card:#ffffff;--soft:#eef5ff;--brand:#2563eb;--violet:#7c3aed;
  --ink:#0f172a;--muted:#64748b;--text:#334155;--border:#dbe4f0;
  --ok:#059669;--warn:#d97706;--risk:#ea580c;
  --serif:Charter,Georgia,"Times New Roman",serif;
  --sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
```

### Required HTML Structure (in order):
1. **Cover section** with `.eyebrow` tag + `h1` title + `.target-line` tags + `.metric-grid` (5 `.metric-card` boxes showing Overall, SEO, GEO, Technical, Content scores)
2. **Evidence boundary** section with `.two-col` layout: left `.panel.boundary` (assessment type note) + right `.panel` (target profile info)
3. **Evidence table** section: HTML `<table>` with columns: Signal | Status | Evidence. Status uses colored text: `color:var(--ok)` for PASS, `color:var(--risk)` for FAIL, `color:var(--warn)` for WARN.
4. **Score detail grid** section: `.score-detail-grid` with 8 `.score-card-detail` cards. Each card has:
   - `.score-detail-head` with `h3` dimension name + `.score-pill` (class `good`/`mid`/`low` based on score)
   - `.bar` with `<i>` fill element (width = score%, class `good`/`mid`/`low`)
   - `.finding-pair` with two `<div>`: "What Looks Good" items + "What Needs Work" items
5. **Recommendations** section: `<ol class="recommendation-list">` with `<li class="recommendation-item">` items. Each has:
   - `<span>` with number
   - `<div>` with `<h3>` title + `<span class="pri-badge pri-high/pri-med/pri-low">` priority + `<ul>` action steps
6. **Footer** with evidence boundary disclaimer

### NEVER DO:
- Dark theme / dark background
- Gradient header backgrounds
- Colored score circles (use white cards with colored text)
- Minimal/short reports without detailed recommendations
- Skip reading the template file

If the template file cannot be read at the absolute path above, replicate EXACTLY the structure described here. The design is: white cards on light gray (#f7f9fc) background, serif headings (Charter/Georgia), Inter sans body text.

## Related Workflows

- For a live AI polling report, use the GEOEval / BrowserAct GEO evaluation workflow if explicitly requested and available.
- For a Nexscope landing page, use the Nexscope landing page SOP skill instead.
- For schema-only fixes, use the schema markup generator skill.
