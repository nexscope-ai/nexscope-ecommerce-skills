---
name: ecommerce.differentiation-advisor
version: 2.0.0
description: |
  Suggest product differentiation and USP using competitor/review evidence. Triggers: how to stand out, USP, competitive advantage, product improvement. Use for positioning and feature strategy, not raw competitor metrics or review monitoring.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
 requires:
 apis: ["nexscope"]
 auth:
 identity: seller
---

> 📖 **Analysis Philosophy:** 

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Differentiation Advisor v2.0.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


🆕 **v2.0.0**: Now analyzes REAL review content for pain points and competitor strengths!

## Core Question
**** — How should I differentiate my product?

## When to Use
- User asks "how do I differentiate"
- User asks about or 
- User asks "how to stand out" in a category
- User wants competitive advantage analysis
- User is entering a competitive market

## Differs From / Not Applicable

- Use competitor-analyzer for raw competitor metrics.
- Use review-checker for deep review pain-point mining.
- Use listing-keyword-optimizer for listing keyword placement.
- Use this skill when the user wants positioning, USP, product improvements, or how to stand out.

## What's New in v2.0.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Feature analysis | ✅ From titles | ✅ From titles |
| Pain point mining | ❌ API broken | ✅ Real review text |
| Competitor strengths | ❌ | ✅ From positive reviews |
| USP recommendations | Basic | Enhanced with evidence |
| Action plan | Generic | Specific with timeline |

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/search` | Find competitors |
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/reviews/list` | Review content (non-US) |
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/usReviewsList` | Reviews for US market |

## Supported Marketplaces

| Market | Domain | Status |
|--------|--------|--------|
| UK, CA, DE, FR, JP, AU | Direct | ✅ |
| **US** | — | ✅ Supported (via `/api/v1/tools/linkfox/amazon/usReviewsList`) |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic analysis
python3 scripts/differentiation_advisor.py '{"keyword": "yoga mat"}'

# Specific market
python3 scripts/differentiation_advisor.py '{"keyword": "bluetooth earbuds", "market": "UK"}'

# With charts
python3 scripts/differentiation_advisor.py '{"keyword": "yoga mat"}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `keyword` | string | Yes | - | Product category/keyword |
| `market` | string | No | | Marketplace (US, UK, DE, etc.) |
| `depth` | string | No | "standard" | Analysis depth: standard/deep |
| `feature_categories` | array | No | auto-detect | Feature categories to analyze (agent-specified) |

### Feature Categories (for `feature_categories` parameter)

When calling this skill, the agent should pick relevant feature categories based on the product type.
If omitted, the script auto-detects category (skincare/electronics/fitness/general) but coverage is limited.

**Available feature keys:**
- Skincare: `ingredients`, `skin_type`, `fragrance_free`, `gentle`, `clinical`, `cruelty_free`, `paraben_free`
- Electronics: `wireless`, `battery`, `noise_cancel`, `microphone`, `touch`
- Fitness: `material`, `thickness`, `grip`
- Universal: `eco`, `durability`, `comfort`, `size`, `waterproof`, `odor`, `warranty`, `certification`, `portability`

**Example** (dog water fountain):
```bash
python3 scripts/differentiation_advisor.py '{"keyword": "dog water fountain", "feature_categories": ["material", "size", "durability", "eco", "waterproof", "certification", "portability"]}'
```

## Output Structure

The output will be a structured markdown report, following this format:

**Product Differentiation Strategy Recommendation Report: [Keyword]**

---

**1. Executive Summary**
*   **Analysis Keyword:** [keyword]
*   **Analysis Market:** [market]
*   **Products Analyzed:** Total [market_data.total_found] found, [market_data.analyzed] analyzed
*   **Average Product Price:** [market_data.avg_price]
*   **Average Rating:** [market_data.avg_rating]
*   **Core Insight:** [insights.summary]

**2. Competitor Feature Analysis**
*   **Common Feature Status:**

| Feature Name | Market Adoption Rate | Status |
| :--- | :--- | :--- |
| [common_features[0].name] | [common_features[0].adoption] | [common_features[0].status] |
| ... | ... | ... |
*(Listing all common features)*

**3. Review Analysis**
*   **Total Reviews Analyzed:** [review_analysis.reviews_analyzed]
*   **Main Pain Points:**

| Category | Mentions | Severity | Common Phrases |
| :--- | :--- | :--- | :--- |
| [review_analysis.pain_points[0].category] | [review_analysis.pain_points[0].count] | [review_analysis.pain_points[0].severity] | [review_analysis.pain_points[0].common_phrases] |
| ... | ... | ... | ... |
*(Listing all main pain points, can limit quantity)*

*   **Competitor Strengths:**

| Category | Mentions |
| :--- | :--- |
| [review_analysis.competitor_strengths[0].category] | [review_analysis.competitor_strengths[0].count] |
| ... | ... |

**4. Differentiation Opportunities**
*   **Prioritized Recommendations:**

| Priority | Type | Opportunity | Insight | Action Recommendation | USP Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [differentiation_opportunities[0].priority] | [differentiation_opportunities[0].type] | [differentiation_opportunities[0].opportunity] | [differentiation_opportunities[0].insight] | [differentiation_opportunities[0].action] | [differentiation_opportunities[0].usp_title] |
| ... | ... | ... | ... | ... | ... |
*(Listing all differentiation opportunities, can limit quantity)*

**5. Differentiation Strategies**
*   **Recommended Strategies:**

| Strategy | Unique Selling Proposition | Target Customers | Price Positioning | Key Element | Title Element |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [strategies[0].strategy] | [strategies[0].usp] | [strategies[0].target_customers] | [strategies[0].price_position] | [strategies[0].key_element] | [strategies[0].title_element] |
| ... | ... | ... | ... | ... | ... |

**6. Action Plan**
*   **Specific Steps:**

| Phase | Action |
| :--- | :--- |
| [action_plan[0].step_phase] | [action_plan[0].action] |
| ... | ... |

**7. Attached Visualizations**
*   Feature Adoption Rate (1_feature_adoption.png)
*   Pain Point Analysis (2_pain_points.png)
*   Opportunity Priority (3_opportunities.png)
*   Competitor Strengths (4_competitor_strengths.png)

## Feature Status Levels

| Status | Adoption | Meaning |
|--------|----------|---------|
| **table_stakes** | 80%+ | Must have, everyone has it |
| **common** | 50-79% | Most competitors have it |
| **differentiator** | 20-49% | Could set you apart |
| **rare** | <20% | Potential first-mover advantage |

## Opportunity Priority Levels

| Priority | Trigger | Action |
|----------|---------|--------|
| 🔴 **CRITICAL** | HIGH severity pain point (10%+) | Solve immediately |
| 🟠 **HIGH** | Rare/differentiator feature gap | Add to product |
| 🔵 **MEDIUM** | Competitor strength to match | Don't fall behind |
| ⚪ **LOW** | Nice to have | Consider later |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Feature Adoption | What competitors have | `1_feature_adoption.png` |
| Pain Points | What customers hate | `2_pain_points.png` |
| Opportunities | Prioritized strategy | `3_opportunities.png` |
| Competitor Strengths | What they do well | `4_competitor_strengths.png` |

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INPUT: Keyword │
│ 2. SEARCH: Find competitors │
│ 3. FEATURES: Extract from titles │
│ 4. REVIEWS: Mine pain points + strengths (NEW!) │
│ 5. OPPORTUNITIES: Prioritize differentiation angles │
│ 6. USP: Generate positioning recommendations │
│ 7. ACTION: Step-by-step implementation plan │
└─────────────────────────────────────────────────────────────┘
```

## Integration with Other Skills

```
📊 Full Analysis Pipeline
├── review-checker → Get pain points + barrier
├── differentiation-advisor → Strategy recommendations ← YOU ARE HERE
├── competitor-analyzer → Deep competitor analysis
└── listing-keyword-optimizer → Implement in listing
```

## Example Analysis

**Keyword: "bluetooth earbuds"**

| Finding | Insight |
|---------|---------|
| Top Pain Point | Quality (28%) - "cheap", "defective" |
| Top Strength | Comfort (17%) - must match |
| Feature Gap | Noise Cancel (12% adoption) |
| **Strategy** | |

**Action Plan:**
1. ✅ MUST HAVE: Wireless, Battery (table stakes)
2. 🎯 DIFFERENTIATE: Premium build quality, rigorous QC
3. 📝 LISTING: Lead with in title
4. 💰 PRICE: Position as premium (+20%)

## Limitations

- US market supported via dedicated `/api/v1/tools/linkfox/amazon/usReviewsList` endpoint
- Feature extraction is keyword-based
- Review sample limited to top 5 competitors
- Trends may change quickly


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Output formatting
