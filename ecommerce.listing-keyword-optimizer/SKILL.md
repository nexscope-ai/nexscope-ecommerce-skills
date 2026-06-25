---
name: ecommerce.listing-keyword-optimizer
version: 1.0.0
description: |
  Optimize Amazon listing keyword placement across title, bullets, description, and backend terms. Triggers: listing SEO, title keywords, bullet keywords, backend search terms. Use for placement/copy, not keyword discovery alone.
allowed-tools:
 - Bash
 - Read
 - Write
 - WebFetch
metadata:
  requires:
    apis: ["nexscope"]
  auth:
    scopes: ["keywords:read", "products:read"]
    identity: seller
---

> 📖 **Analysis Philosophy:** Think First, Then Fetch

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Listing Keyword Optimizer

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


## Core Question

— What keywords should I use in my listing, and where should they go?

## When to Use
- User asks "what keywords for my listing"
- User wants to optimize title/bullets/description
- User mentions "listing optimization" or "keyword": " placement"
- User has a product and needs keyword strategy
- User asks about "backend search terms"

## Differs From / Not Applicable

- Use keyword-research, keyword-opportunity-finder, or keyword-reverse-lookup to discover keywords first.
- Use this skill when the user wants keywords assigned to title, bullets, description, or backend terms.
- Do not use for market sizing, ranking tracking, or competitor business metrics.

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Keyword expansion, volume, difficulty |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-asin` | Competitor keyword reverse lookup |
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Product data, competitor listings |
| ABA (Amazon Brand Analytics) | `/api/v1/tools/linkfox/aba/intelligentQuery` | Search Frequency Rank validation |

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `keyword` | string | Yes* | - | Main product keyword |
| `asin` | string | Yes* | - | Target ASIN (yours or competitor) |
| `marketplace` | string | No | | Target marketplace |
| `category` | string | No | auto | Product category for context |
| `product_title` | string | No | auto from ASIN | Product title when the user provides listing/product context |
| `product_description` | string | No | - | Product description or short brief for relevance filtering |
| `features` / `product_features` | array | No | - | Key product attributes, materials, use cases, or design features |
| `target_audience` | string | No | - | Intended buyer or usage audience |
| `product_brand` | string | No | auto from ASIN | Own brand; excluded from competitor brand filtering |
| `max_title_chars` | int | No | 200 | Max title length |
| `bullet_count` | int | No | 5 | Number of bullet points |
| `brand_blocklist` | array | No | auto-detect | Competitor brand names to exclude from title |
| `bullet_features` | object | No | auto-detect | Custom bullet grouping {name: [signal_words]} |
| `min_relevance` | int | No | 25 | Minimum product relevance score for keyword inclusion |

*Either `keyword` or `asin` required

### Brand Blocklist (for `brand_blocklist` parameter)

Both `brand_blocklist` and `bullet_features` auto-detect from competitor data when not provided:
- **brand_blocklist**: Extracts brand names from competitor listings' brand field
- **bullet_features**: Detects product category (skincare/electronics/fitness/general) from keyword + titles, then uses category-specific bullet groupings

Agent can override either for fuller coverage.

**Example** (wireless earbuds with custom brands):
```bash
python3 scripts/listing_keyword_optimizer.py '{"keyword": "wireless earbuds", "brand_blocklist": ["apple", "airpods", "samsung", "sony", "bose", "jabra", "beats", "jbl", "anker", "tozo", "raycon"]}'
```

## Output Structure

The output will be a structured markdown report, following this format:

**Listing Keyword Optimization Report: [Keyword or ASIN]**

---

**1. Executive Summary**
*   **Main Keyword:** [main_keyword]
*   **Analyzed ASIN:** [asin] (if provided)
*   **Analysis Market:** [market]
*   **Analysis Date:** [analysis_date]
*   **Product Category:** [product_context.category]
*   **Core Insight:** [insights.summary]

**2. Title Keyword Recommendations**
*   **Suggested Title:** [title_keywords.suggested_title]
*   **Character Count:** [title_keywords.char_count] (Mobile Preview: [title_keywords.mobile_preview])
*   **Keyword Classification:**

| Priority | Keyword | Search Volume |
| :--- | :--- | :--- |
| Must Have | [title_keywords.must_have[0].keyword] | [title_keywords.must_have[0].volume] |
| Should Have | [title_keywords.should_have[0].keyword] | [title_keywords.should_have[0].volume] |
| Nice to Have | [title_keywords.nice_to_have[0].keyword] | [title_keywords.nice_to_have[0].volume] |

**3. Bullet Point Keyword Recommendations**
*   **Suggested Bullet Points and Keywords:**

| Bullet No. | Feature | Suggested Keywords (Top 3) | Search Volume (Example) |
| :--- | :--- | :--- | :--- |
| 1 | [bullet_keywords.bullet_1.feature] | [bullet_keywords.bullet_1.keywords[0].keyword], [bullet_keywords.bullet_1.keywords[1].keyword] | [bullet_keywords.bullet_1.keywords[0].volume] |
| 2 | [bullet_keywords.bullet_2.feature] | [bullet_keywords.bullet_2.keywords[0].keyword], [bullet_keywords.bullet_2.keywords[1].keyword] | [bullet_keywords.bullet_2.keywords[0].volume] |
| ... | ... | ... | ... |
*(Showing all bullet point recommendations, up to 3 keywords per bullet with example search volume)*

**4. Description Keyword Recommendations**
*   **Long-tail and Supplementary Keyword Examples:**

| Keyword Type | Example Keyword | Search Volume (Example) |
| :--- | :--- | :--- |
| Long-Tail | [description_keywords.long_tail[0].keyword] | [description_keywords.long_tail[0].volume] |
| Supplementary | [description_keywords.supplementary[0].keyword] | [description_keywords.supplementary[0].volume] |

**5. Backend Search Terms Recommendations**
*   **Backend Term Status:**

| Type | Keywords |
| :--- | :--- |
| Recommended | [backend_terms.recommended] |
| Misspellings | [backend_terms.misspellings] |
| To Avoid | [backend_terms.avoid] |

*   **Byte Usage:** [backend_terms.bytes_used] bytes used, [backend_terms.bytes_remaining] bytes remaining

**6. Keyword Coverage Analysis**
*   **Keyword Allocation and Coverage:**

| Section | Keywords Covered | Percentage of Total Keywords |
| :--- | :--- | :--- |
| Total Keywords | [keyword_map.total_keywords] | 100% |
| Title | [keyword_map.title_coverage] | [Calculated Percentage]% |
| Bullet Points | [keyword_map.bullet_coverage] | [Calculated Percentage]% |
| Description | [keyword_map.description_coverage] | [Calculated Percentage]% |
| Backend Search Terms | [keyword_map.backend_coverage] | [Calculated Percentage]% |

**7. Competitor Analysis Insights**
*   **Competitors Analyzed:** [competitor_analysis.titles_analyzed]
*   **Common Phrases in Competitors:** [competitor_analysis.common_phrases]
*   **Common Words in Competitors:** [competitor_analysis.common_words]

**8. Amazon Brand Analytics (ABA) Validation**
*   **Search Frequency Rank (SFR):** [aba_validation.search_frequency_rank]
*   **Search Volume Tier:** [aba_validation.search_volume_tier]

**9. Actionable Recommendations**
*   [First recommendation from `insights.recommendations`]
*   [Second recommendation from `insights.recommendations`]
*   ... (Listing all key recommendations)

**10. Attached Visualizations**
*   Keyword Priority Matrix
*   Placement Allocation
*   Coverage Analysis
*   Competitor Comparison

**Default Practical Output**

The script also returns a compact `listing_copy` object for direct use:

```json
{
  "listing_copy": {
    "title": "Readable Amazon-style title",
    "bullets": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4", "Bullet 5"],
    "backend_search_terms": "space separated backend terms"
  },
  "self_check": {
    "status": "PASS or REVIEW",
    "warnings": []
  }
}
```

## Keyword Placement Strategy

### Title (Most Important)
- **Characters:** 150-200 max (mobile truncates at ~80)
- **Priority:** Highest volume + most relevant
- **Rule:** Main keyword FIRST, then modifiers
- **Avoid:** Keyword stuffing, ALL CAPS, special characters

### Bullet Points (Feature-Focused)
- **Characters:** ~500 per bullet
- **Priority:** Feature + benefit keywords
- **Rule:** One main keyword per bullet, natural flow
- **Pattern:** FEATURE - Benefit - Keywords

### Description (Long-Tail)
- **Characters:** 2000 max
- **Priority:** Long-tail, semantic variations
- **Rule:** Natural sentences, storytelling
- **Avoid:** Duplicate title keywords

### Backend Search Terms
- **Characters:** 250 bytes
- **Priority:** Misspellings, synonyms, Spanish terms
- **Rule:** No repeats from title/bullets
- **Avoid:** Brand names, ASINs, subjective claims


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# By keyword
python3 scripts/listing_keyword_optimizer.py '{"keyword": "yoga mat"}'

# By ASIN (reverse engineer competitor)
python3 scripts/listing_keyword_optimizer.py '{"asin": "B07RL88DD2"}'

# With category context
python3 scripts/listing_keyword_optimizer.py '{"keyword": "yoga mat", "category": "Sports"}'

# With product understanding context
python3 scripts/listing_keyword_optimizer.py '{
  "keyword": "dive bag",
  "product_title": "Mesh scuba gear bag for fins and snorkel equipment",
  "features": ["mesh drainage", "large fin compartment", "shoulder strap"],
  "target_audience": "recreational scuba divers",
  "brand_blocklist": ["YETI", "TYR"]
}'

# Generate charts
python3 scripts/listing_keyword_optimizer.py '{"keyword": "yoga mat"}' --chart /tmp/charts
```

## Charts Generated

1. **Keyword Priority Matrix** — Volume vs Difficulty scatter
2. **Placement Allocation** — Where each keyword goes
3. **Coverage Analysis** — Keyword distribution across sections
4. **Competitor Comparison** — Your coverage vs top competitors

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INPUT: keyword, ASIN, or product context │
│ 1.5 UNDERSTAND: Fetch ASIN detail or use provided title/features/audience │
│ 2. EXPAND: Get related keywords from Jungle Scout │
│ 3. VALIDATE: Check competitor listings and detect competitor brands │
│ 4. FILTER: Remove off-product and competitor-brand keywords │
│ 5. CATEGORIZE: Title / Bullet / Description / Backend │
│ 6. GENERATE: Readable title, bullet copy, backend terms │
│ 7. REVIEW: Check readability, brand conflicts, and relevance drift │
│ 8. OUTPUT: Compact listing copy + detailed keyword analysis │
└─────────────────────────────────────────────────────────────┘
```

If the review step flags brand conflicts or low-relevance visible keywords, revise filters and rerun before giving final listing copy.

## Insights Generated

- 🎯 Must-have keywords (high volume, high relevance)
- 💎 Hidden gems (medium volume, low competition)
- ⚠️ Over-competitive keywords to de-prioritize
- 📈 Trending keywords to include
- 🚫 Keywords to avoid (irrelevant, trademarked)

## Limitations

- Amazon title limits vary by category (check Seller Central)
- Backend terms have strict byte limits
- Some keywords may be restricted in certain categories
- A+ Content keywords not indexed (description replacement)
- Keyword indexing can take 24-48 hours


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/amazon-listing-guidelines.md` — Official Amazon rules
- `references/keyword-placement-best-practices.md` — Placement strategies
- `references/display-rules.md` — Output formatting rules
