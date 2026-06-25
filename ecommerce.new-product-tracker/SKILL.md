---
name: ecommerce.new-product-tracker
version: 1.1.0
description: |
  Find newly launched products with fast growth signals. Triggers: new products, recently launched, rising products, early winners. Use for new product discovery, not trend categories or existing product validation.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# New Product Tracker v1.1.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**What new products are rising fast?**

Track newly launched products showing rapid growth signals. Find rising stars before they become saturated.

## Core Question

> — What new products are rising?
> — Which new launches should I watch?

## When to Use

- Finding successful new product launches to learn from
- Identifying emerging competition in your niche
- Discovering product opportunities before saturation
- Validating that a market accepts new entrants

## Differs From / Not Applicable

- Use trend-discovery for rising categories and macro trend discovery.
- Use product-opportunity-finder for broader product idea generation.
- Use product-validator for validating a known ASIN/product.
- Use this skill for recently launched products and early winners.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Product list, sales estimates |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR history, listing age |
| Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/*` | Search trends |

## New Product Score (0-100)

```
Score = Freshness (25) + Growth (30) + Velocity (20) + Potential (15) + Stability (10)
```

| Dimension | Points | Metrics |
|-----------|--------|---------|
| 🆕 **Freshness** | 25 | Listing age (newer = higher) |
| 📈 **Growth** | 30 | BSR improvement rate |
| ⚡ **Velocity** | 20 | Review growth rate (validated) |
| 💰 **Potential** | 15 | Current sales + price point |
| 🔒 **Stability** | 10 | Price stability + stock status |

## Opportunity Patterns

| Pattern | Signal | Description |
|---------|--------|-------------|
| 🚀 **Fast Starter** | <90d old, top BSR | Quick success, validate market |
| 📈 **Rising Star** | 90d+ consistent growth | Sustainable momentum |
| 💎 **Hidden Gem** | Good BSR, few reviews | Under the radar |
| 🔥 **Viral Launch** | Sudden BSR spike | Watch for sustainability |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Track new products in a category
python3 scripts/new_product_tracker.py '{"keyword": "portable blender"}'

# Filter by age
python3 scripts/new_product_tracker.py '{"keyword": "yoga mat", "max_age_days": 90}'

# Minimum sales threshold
python3 scripts/new_product_tracker.py '{"keyword": "face wash", "min_sales": 100}'

# With chart output
python3 scripts/new_product_tracker.py '{"keyword": "kombucha"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Category keyword |
| `market` | string | | Target marketplace |
| `max_age_days` | int | 180 | Maximum listing age |
| `min_sales` | int | 50 | Minimum monthly sales |
| `limit` | int | 20 | Number of products to track |

## Output Structure

The output will be a structured markdown report, following this format:

**New Product Tracking Report: [Keyword]**

---

**1. Executive Summary**
*   **Analysis Keyword:** [keyword]
*   **Analysis Market:** [market]
*   **New Products Found:** [new_products_found]
*   **Core Insight:** [insights.summary] (if available)

**2. New Product Performance Overview**
*   **New Product Pattern Distribution:**

| Pattern Type | Count | Description |
| :--- | :--- | :--- |
| 🚀 Fast Starter | [patterns.fast_starters] | <90 days old, excellent BSR |
| 📈 Rising Star | [patterns.rising_stars] | Consistent growth for 90+ days |
| 💎 Hidden Gem | [patterns.hidden_gems] | Good BSR, few reviews |
| 🔥 Viral Launch | [patterns.viral_launches] | Sudden BSR spike |

**3. Top Performing New Products**
*   **Top New Products Ranked by Score (Showing Top 5):**

| Rank | ASIN | Title | Listing Age (Days) | Current BSR | BSR 30 Days Ago | BSR Improvement | Reviews | Review Growth | Score | Pattern |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [top_performers[0].asin] | [top_performers[0].title] | [top_performers[0].age_days] | [top_performers[0].current_bsr] | [top_performers[0].bsr_30d_ago] | [top_performers[0].bsr_improvement]% | [top_performers[0].reviews] | [top_performers[0].review_growth] | [top_performers[0].score] | [top_performers[0].pattern] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**4. Attached Visualizations**
*   BSR Trajectory (bsr_trajectory.png)
*   Age vs Performance (age_performance.png)
*   New Product Pattern Distribution (patterns.png)
*   Review Authenticity Validation (review_validation.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| BSR Trajectory | Top products over time | `bsr_trajectory.png` |
| Age vs Performance | Scatter plot | `age_performance.png` |
| Pattern Distribution | Pie chart | `patterns.png` |
| Review Authenticity | Validation chart | `review_validation.png` |

## Review Authenticity Check

| Signal | Risk |
|--------|------|
| Review spike (>50 in 1 week) | ⚠️ Potential fake reviews |
| Steady growth | ✅ Organic |
| Reviews > Sales ratio anomaly | ⚠️ Suspicious |

## Workflow Integration

```
🎯 Selection Phase
├── product-opportunity-finder → Find specific products
└── new-product-tracker → Track rising products ← YOU ARE HERE
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## Limitations

- Listing age detection depends on Keepa data
- BSR history limited to tracked ASINs
- Review velocity can be gamed (check authenticity)
- Category cleaner may filter some new products
- Viral products may crash after initial spike

## References

- `references/scoring-methodology.md` — Score calculation details
- `references/display-rules.md` — Chart styling guidelines

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/new_product_tracker.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/new_product_tracker.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/new_product_tracker.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
