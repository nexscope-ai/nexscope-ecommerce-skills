---
name: product-opportunity-finder
version: 2.2.0
description: |
  Find product ideas and blue-ocean product opportunities. Triggers: what should I sell, product ideas, product discovery, untapped products. Use for discovering opportunities, not validating a specific ASIN or broad market overview.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Product Opportunity Finder v2.2.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**What products should I sell?**

Find blue ocean products with multi-dimensional filtering and opportunity scoring.

## Core Question

> — What products should I sell?
> — What product opportunities are there?

## When to Use

- Looking for product ideas to sell
- Filtering through a large category for opportunities
- Finding gaps in the market
- Discovering underserved niches

## Differs From / Not Applicable

- Use product-validator when the user already has a specific ASIN/product.
- Use market-overview for broad market context.
- Use niche-evaluator for entry scoring.
- Use this skill for discovering product ideas and blue-ocean opportunities.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Products, sales, reviews |
| eBay | `/api/v1/tools/linkfox/ebay/search` | Cross-platform demand validation |
| Walmart | `/api/v1/tools/linkfox/walmart/search` | Multi-channel opportunity |
| Google Trends | `/api/v1/tools/linkfox/googleTrend/getTrendByKeys` | Trend validation |
| Keepa | `/api/v1/tools/linkfox/keepa/productRequest` | Product details, monthly sales |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR/price history |

## Opportunity Score (0-100)

Multi-dimensional score based on:

| Dimension | Weight | Metrics |
|-----------|--------|---------|
| 📈 **Demand** | 25% | Sales velocity, search volume |
| ⚔️ **Competition** | 25% | Review barriers, brand presence |
| 💰 **Profit** | 25% | Margins, price stability |
| 🎯 **Opportunity** | 25% | Gaps, differentiation |

## Opportunity Types

| Type | Description |
|------|-------------|
| 🏖️ **Low Competition** | High demand, few sellers |
| ⭐ **Quality Gap** | Low ratings, room for improvement |
| 💵 **Price Gap** | Underserved price segment |
| 📈 **Rising Star** | Growing demand trend |
| 🔄 **Channel Arbitrage** | Price difference across platforms |
| 📦 **Bundle Opportunity** | FBT (frequently bought together) |
| 🎯 **Niche Segment** | Underserved sub-category |

## Filter Presets

| Preset | Description |
|--------|-------------|
| **Conservative** | Low risk, proven demand |
| **Balanced** | Mix of risk/reward |
| **Aggressive** | Higher risk, higher potential |
| **Premium** | High-price products |
| **Budget** | Low-price, high-volume |
| **Trending** | Focus on rising trends |

## Red Lines (Auto-Exclude)

| Category | Reason |
|----------|--------|
| ⚠️ Hazmat | Shipping restrictions |
| ⚠️ Fragile | High damage rates |
| ⚠️ Patent/IP Risk | Legal issues |
| ⚠️ Oversized | FBA fee impact |
| ⚠️ Gated Category | Approval required |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Find opportunities in a category
python3 scripts/product_opportunity_finder.py '{"keyword": "yoga accessories"}'

# With specific preset
python3 scripts/product_opportunity_finder.py '{"keyword": "kitchen gadgets", "preset": "conservative"}'

# Custom filters
python3 scripts/product_opportunity_finder.py '{"keyword": "pet supplies", "min_price": 10, "max_reviews": 500}'

# Multi-platform analysis
python3 scripts/product_opportunity_finder.py '{"keyword": "phone cases", "platforms": ["amazon"]}'

# With chart output
python3 scripts/product_opportunity_finder.py '{"keyword": "yoga mat"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Category keyword |
| `market` | string | | Target marketplace |
| `preset` | string | "balanced" | Filter preset |
| `min_price` | float | - | Minimum price |
| `max_price` | float | - | Maximum price |
| `min_sales` | int | - | Minimum monthly sales |
| `max_reviews` | int | - | Maximum review count |
| `platforms` | array | ["amazon"] | Platforms to analyze |

## Output Structure

The output will be a structured markdown report, following this format:

**Product Opportunity Analysis Report: [Keyword, e.g., "Skincare"]**

---

**1. Executive Summary**
*   **Analysis Date:** [analysis_date]
*   **Total Products Analyzed:** [products_searched count]
*   **Total Opportunities Found:** [opportunities_found count]
*   **Overall Market Health:** [insights.market_health, e.g., Good, Highly Competitive]
*   **Key Insight:** [insights.summary]

**2. Market Overview**
*   **Average Product Price:** [market_stats.avg_price]
*   **Average Review Count:** [market_stats.avg_reviews]
*   **Average Rating:** [market_stats.avg_rating]
*   **Price Distribution:**
    *   Budget Products: [market_stats.price_distribution.budget]%
    *   Mid-Range Products: [market_stats.price_distribution.mid]%
    *   Premium Products: [market_stats.price_distribution.premium]%
*   **Cross-Platform Demand Validation:**
    *   eBay: [cross_platform.ebay.sold_count] sales, Demand Level: [cross_platform.ebay.demand_level]
    *   Walmart: Found [cross_platform.walmart.product_count] products
*   **Trend Validation (Google Trends):**
    *   Trend Direction: [trend_validation.google_trends.direction]
    *   Change Percentage: [trend_validation.google_trends.change_pct]%

**3. Top Product Opportunities**
*   **Recommended products ranked by Opportunity Score:**

| Rank | ASIN | Product Name | Brand | Price | Monthly Sales | Score | Grade | Opportunity Type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [opportunities[0].asin] | [opportunities[0].title] | [opportunities[0].brand] | [opportunities[0].price] | [opportunities[0].monthly_sales] | [opportunities[0].score] | [opportunities[0].grade] | [opportunities[0].opportunity_types] |
| 2 | ... | ... | ... | ... | ... | ... | ... | ... |

*(Showing top 5-10 opportunities)*

**4. Opportunity Type Distribution**
*   **Statistics for different opportunity types:**

| Opportunity Type | Count |
| :--- | :--- |
| Low Competition (LOW_COMPETITION) | [insights.opportunity_types.LOW_COMPETITION] |
| Quality Gap (QUALITY_GAP) | [insights.opportunity_types.QUALITY_GAP] |
| Price Gap (PRICE_GAP) | [insights.opportunity_types.PRICE_GAP] |
| Rising Star (RISING_STAR) | [insights.opportunity_types.RISING_STAR] |
| Channel Arbitrage (CHANNEL_ARBITRAGE) | [insights.opportunity_types.CHANNEL_ARBITRAGE] |
| Niche Segment (NICHE_SEGMENT) | [insights.opportunity_types.NICHE_SEGMENT] |
| (Other types, if any) | |

**5. Actionable Recommendations**
*   [insights.recommendations[0]]
*   [insights.recommendations[1]]
*   [insights.recommendations[2]]
*   (Listing all key recommendations)

**6. Attached Visualizations**
*   Seasonal Trend (seasonality.png)
*   Segment Opportunities (segments.png)
*   ROI Waterfall (roi_waterfall.png)
*   Radar Score (radar.png)
*   Product Comparison (comparison.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Seasonality Trend | Monthly pattern | `seasonality.png` |
| Segment Opportunities | By type bar | `segments.png` |
| ROI Waterfall | Margin breakdown | `roi_waterfall.png` |
| Radar Score | Multi-dimension | `radar.png` |
| Product Comparison | Top opportunities | `comparison.png` |

## Bundling Detection

| Signal | Description |
|--------|-------------|
| FBT Match | Products frequently bought together |
| Complementary | Same customer, different need |
| Accessory | Main product + add-ons |

## Workflow Integration

```
🎯 Selection Phase
├── product-opportunity-finder → Find specific products ← YOU ARE HERE
└── new-product-tracker → Track rising products
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- Sales estimates are approximations
- Red line detection is keyword-based
- Bundling requires FBT data availability
- Cross-platform arbitrage changes rapidly
- Category cleaner may filter opportunities

## References

- `references/opportunity-types.md` — Opportunity definitions
- `references/visualization.md` — Chart specifications
- `references/display-rules.md` — Chart styling guidelines

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/product_opportunity_finder.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/product_opportunity_finder.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/product_opportunity_finder.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
