---
name: ecommerce.competitor-listing-analyzer
version: 1.0.0
description: |
  Analyze Amazon listing content and structure: title, bullets, images, A+ content, and listing quality. Triggers: listing breakdown, reverse-engineer listings, title/bullet/image analysis. Use for content audits, not business metrics; use competitor-analyzer for price/BSR/sales.
allowed-tools:
 - Bash
 - Read
 - Write
 - WebFetch
metadata:
 requires:
 apis: ["nexscope"]
 auth:
 scopes: ["products:read"]
 identity: seller
---

> 📖 **Analysis Philosophy:** 

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Competitor Listing Analyzer

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


## Core Question
**** — How do competitors write their listings?

## When to Use
- User asks "how does competitor write their listing"
- User wants to analyze a specific ASIN's listing
- User asks for "listing structure breakdown"
- User wants to reverse-engineer successful listings
- User asks "what can I learn from this listing"

## Differs From / Not Applicable

- Use competitor-analyzer for price, reviews, BSR, traffic, sales, and business-performance comparisons.
- Use this skill for listing structure and creative/content audits.
- Do not use for market-level analysis, product validation, or review sentiment monitoring.

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| Amazon | `/api/v1/tools/linkfox/amazon/product/detail` | Full listing content extraction |
| Amazon | `/api/v1/tools/linkfox/amazon/search` | Find top competitors by keyword |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `asin` | string | Yes* | - | Target ASIN to analyze |
| `asins` | list | Yes* | - | Multiple ASINs to compare |
| `keyword` | string | Yes* | - | Find top competitors for keyword |
| `marketplace` | string | No | | Target marketplace |
| `depth` | string | No | "standard" | Analysis depth: quick/standard/deep |

*One of `asin`, `asins`, or `keyword` required

## Output Structure

The output will be a structured markdown report, following this format:

**[Product/Keyword] Competitor Listing Analysis Report**

---

**1. Executive Summary**
*   **Analysis Object:** [Display asin, asins, or keyword based on input parameters]
*   **Analysis Depth:** [depth]
*   **Core Insight:** [Summary extracted from `overall_score`, `strengths`, `weaknesses`, and `recommendations` fields]

**2. Overall Analysis & Comparison**
*   **Listing Score Comparison (for each analyzed ASIN):**

| ASIN | Overall Score | Title Score | Bullet Score | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [analyzed_listings[i].asin] | [analyzed_listings[i].overall_score] | [analyzed_listings[i].title_analysis.title_score] | [analyzed_listings[i].bullet_analysis.bullet_score] | [analyzed_listings[i].strengths] | [analyzed_listings[i].weaknesses] |
| ... | ... | ... | ... | ... | ... |
*(If multiple ASINs are analyzed, comparison data for all ASINs will be listed here.)*

*   **General Recommendations:**
    *   [First recommendation from `recommendations`]
    *   [Second recommendation from `recommendations`]
    *   ...

**3. Detailed Listing Structure Analysis**
*(Detailed analysis for each analyzed ASIN)*

**Target ASIN: [analyzed_listings[i].asin]**

*   **3.1 Title Analysis**
    *   Title: [analyzed_listings[i].title_analysis.title]
    *   Character Count: [analyzed_listings[i].title_analysis.char_count]
    *   Structure Pattern: [analyzed_listings[i].title_analysis.structure]
    *   Detected Keywords: [analyzed_listings[i].title_analysis.keywords_detected]
    *   Title Score: [analyzed_listings[i].title_analysis.title_score]

*   **3.2 Bullet Points Analysis**
    *   Bullet Count: [analyzed_listings[i].bullet_analysis.bullet_count]
    *   Bullet Pattern: [analyzed_listings[i].bullet_analysis.pattern]
    *   Bullet Score: [analyzed_listings[i].bullet_analysis.bullet_score]
    *   Bullet Details (Example, showing up to 3 bullets):
        *   - [analyzed_listings[i].bullet_analysis.bullets[0].text] (Keywords: [analyzed_listings[i].bullet_analysis.bullets[0].keywords])
        *   - [analyzed_listings[i].bullet_analysis.bullets[1].text] (Keywords: [analyzed_listings[i].bullet_analysis.bullets[1].keywords])
        *   - [analyzed_listings[i].bullet_analysis.bullets[2].text] (Keywords: [analyzed_listings[i].bullet_analysis.bullets[2].keywords])

*   **3.3 Description Analysis**
    *   Has Description: [analyzed_listings[i].description_analysis.has_description]
    *   Has A+ Content: [analyzed_listings[i].description_analysis.has_aplus]
    *   Word Count: [analyzed_listings[i].description_analysis.word_count]
    *   Structure Pattern: [analyzed_listings[i].description_analysis.structure]

*   **3.4 Image Analysis**
    *   Main Image Count: [analyzed_listings[i].image_analysis.main_image_count]
    *   Has Video: [analyzed_listings[i].image_analysis.has_video]
    *   Infographic Count: [analyzed_listings[i].image_analysis.infographic_count]
    *   Lifestyle Image Count: [analyzed_listings[i].image_analysis.lifestyle_count]

**4. Attached Visualizations**
*   Listing Score Comparison
*   Title Structure Breakdown
*   Bullet Pattern Analysis
*   Image Strategy Matrix

## Analysis Dimensions

### Title Analysis
- Character count & mobile truncation check
- Structure pattern detection
- Keyword extraction
- Brand positioning

### Bullet Points Analysis
- Count and length
- Feature-Benefit pattern detection
- Keyword density
- Emoji/formatting usage
- Unique selling points

### Description Analysis
- Plain text vs A+ Content
- Structure breakdown
- Keyword usage
- Call-to-action presence

### Image Analysis
- Image count
- Video presence
- Infographic detection
- Lifestyle vs product shots


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Single ASIN analysis
python3 scripts/competitor_listing_analyzer.py '{"asin": "B07RL88DD2"}'

# Compare multiple ASINs
python3 scripts/competitor_listing_analyzer.py '{"asins": ["B07RL88DD2", "B08EXAMPLE"]}'

# Find and analyze top competitors for keyword
python3 scripts/competitor_listing_analyzer.py '{"keyword": "yoga mat", "depth": "deep"}'

# Generate comparison charts
python3 scripts/competitor_listing_analyzer.py '{"keyword": "yoga mat"}' --chart /tmp/charts
```

## Charts Generated

1. **Listing Score Comparison** — Overall scores across competitors
2. **Title Structure Breakdown** — How competitors structure titles
3. **Bullet Pattern Analysis** — Feature types and patterns
4. **Image Strategy Matrix** — Image types used

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INPUT: ASIN(s) or keyword │
│ 2. EXTRACT: Fetch full listing content from Amazon │
│ 3. PARSE: Break down title, bullets, description │
│ 4. ANALYZE: Score each component, detect patterns │
│ 5. COMPARE: Cross-competitor analysis │
│ 6. RECOMMEND: Actionable improvements │
└─────────────────────────────────────────────────────────────┘
```

## Insights Generated

- 🎯 Title structure patterns
- 📝 Bullet writing formulas
- 🖼️ Image strategy insights
- ⭐ What top sellers do differently
- 🚫 Common mistakes to avoid

## Limitations

- A+ Content extraction may be limited
- Some enhanced content may be unavailable through API data
- Brand Registry features not always visible
- Video content analysis is basic
- Non-US marketplaces may have different patterns


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/listing-best-practices.md` — Amazon listing guidelines
- `references/display-rules.md` — Output formatting rules
