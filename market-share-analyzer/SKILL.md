---
name: market-share-analyzer
version: 2.0.0
description: |
  Analyze brand dominance and market concentration. Triggers: market share, monopoly, top brand share, CR4, can new brands succeed. Use for concentration/SOV, not full market overview or niche entry score.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Market Share Analyzer v2.0.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**Is this market monopolized? Can new brands succeed?**

Analyze market concentration and brand dominance using three-source data fusion.

## Core Question

> — Is this market monopolized?
> — Can new brands succeed?

## When to Use

- Evaluating market entry feasibility
- Understanding brand concentration
- Finding markets open to new entrants
- Analyzing SOV vs actual revenue discrepancy

## Differs From / Not Applicable

- Use market-overview for broad market context.
- Use niche-evaluator for entry score and go/no-go recommendations.
- Use competitor-analyzer for product-level competitor metrics.
- Use this skill for brand dominance, SOV, CR4, and concentration.

## Data Sources (Three-Source Fusion)

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/share-of-voice` | Brand SOV %, organic/ads split |
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Product list, prices, reviews |
| Keepa | `/api/v1/tools/linkfox/keepa/productRequest` | Product details, monthly sales, seller info |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR history, price trends |

### Cross-Validation Architecture

```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Jungle Scout │ │ Amazon Search │ │ Keepa │
│ SOV API │ │ API │ │ Product Data │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ - Brand SOV % │ │ - Product list │ │ - Monthly sales │
│ - Organic/Ads │ │ - Prices │ │ - BSR history │
│ - Click/Conv │ │ - Reviews │ │ - Sales volume │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
 └──────────────┬──────┴─────────────────────┘
 ▼
 ┌─────────────────────┐
 │ Cross-Validation │
 │ Engine │
 └─────────────────────┘
```

## Key Metrics

| Metric | Description | Thresholds |
|--------|-------------|------------|
| **HHI** | Herfindahl-Hirschman Index | <1500 Open, 1500-2500 Moderate, >2500 Concentrated |
| **CR1** | Top 1 brand share | >40% = Dominant leader |
| **CR4** | Top 4 brands share | >70% = Oligopoly |
| **CR10** | Top 10 brands share | >90% = Closed market |
| **Entry Score** | 0-100 feasibility | >70 Good, 50-70 Moderate, <50 Difficult |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Analyze market share
python3 scripts/market_share_analyzer.py '{"keyword": "yoga mat"}'

# Different market
python3 scripts/market_share_analyzer.py '{"keyword": "face wash", "market": "UK"}'

# With chart output
python3 scripts/market_share_analyzer.py '{"keyword": "kombucha"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Market keyword |
| `market` | string | | Target marketplace |
| `limit` | int | 50 | Products to analyze |

## Output Structure

The output will be a structured markdown report, following this format:

**Market Share Analysis Report: [Keyword]**

---

**1. Executive Summary**
*   **Analysis Keyword:** [keyword]
*   **Analysis Market:** [market]
*   **Data Source:** [data_source]
*   **Market Structure:** [market_structure]
*   **New Brand Entry Feasibility:** [metrics.hhi_classification]
*   **Core Insight:** [insights.market_openness]
*   **Recommended Strategy:** [insights.recommended_strategy[0].strategy] - [insights.recommended_strategy[0].detail]

**2. Market Concentration Metrics**
*   **Key Market Indicators:**

| Indicator | Value | Classification | Description |
| :--- | :--- | :--- | :--- |
| HHI (Herfindahl-Hirschman Index) | [metrics.hhi] | [metrics.hhi_classification] | <1500 Open, 1500-2500 Moderate, >2500 Concentrated |
| CR1 (Top 1 Brand Share) | [metrics.cr1]% | | >40% = Dominant Leader |
| CR4 (Top 4 Brand Share) | [metrics.cr4]% | | >70% = Oligopoly |
| CR10 (Top 10 Brand Share) | [metrics.cr10]% | | >90% = Closed Market |
| Equivalent Number of Firms | [metrics.equivalent_firms] | | Measure of market competition |

**3. Brand Distribution & Composition**
*   **Brand Type Counts:**

| Brand Type | Count | Estimated Market Share |
| :--- | :--- | :--- |
| Major Brands | [brand_breakdown.major_brands] | [brand_breakdown.major_brand_share]% |
| Amazon Brands | [brand_breakdown.amazon_brands] | [brand_breakdown.amazon_share]% |
| Private Label | [brand_breakdown.private_label] | [brand_breakdown.private_label_share]% |
| Emerging Brands | [brand_breakdown.emerging] | - |

*   **Top Brands List (Showing Top 5):**

| Rank | Brand Name | Market Share (SOV%) | Revenue Share (%) |
| :--- | :--- | :--- | :--- |
| 1 | [top_brands[0].brand_name] | [top_brands[0].sov_pct]% | [top_brands[0].revenue_share_pct]% |
| ... | ... | ... | ... |

**4. Traffic & Sales Analysis**
*   **Traffic Distribution:**
    *   Organic Traffic Percentage: [traffic_analysis.organic_pct]%
    *   Sponsored Traffic Percentage: [traffic_analysis.sponsored_pct]%
    *   Traffic Type: [traffic_analysis.traffic_type]
    *   Assessment: [traffic_analysis.assessment]
*   **Estimated Total Market Revenue:** [total_revenue_estimated]
*   **Top Converting ASINs (Showing Top 5):**

| ASIN | Brand | Monthly Sales (Est.) | Conversion Rate (Est.) |
| :--- | :--- | :--- | :--- |
| [top_converting_asins[0].asin] | [top_converting_asins[0].brand] | [top_converting_asins[0].monthly_sales] | [top_converting_asins[0].conversion_rate]% |
| ... | ... | ... | ... |

**5. Market Gaps Analysis**
*   **Identified Market Gaps:**

| Brand | SOV% | Revenue Share% | Gap Type | Insight |
| :--- | :--- | :--- | :--- | :--- |
| [gap_analysis[0].brand] | [gap_analysis[0].sov]% | [gap_analysis[0].revenue_share]% | [gap_analysis[0].gap_type] | [gap_analysis[0].insight] |
| ... | ... | ... | ... | ... |

**6. Overall Recommendations**
*   **All Recommended Strategies:**
    *   Priority: [insights.recommended_strategy[0].priority], Strategy: [insights.recommended_strategy[0].strategy], Detail: [insights.recommended_strategy[0].detail]
    *   ... (Listing all key recommendations)

**7. Attached Visualizations**
*   Market Share Pie Chart (market_share.png)
*   Concentration Metrics Bar Chart (concentration.png)
*   Brand Type Distribution (brand_types.png)
*   Opportunity Bubble Chart (opportunity.png)
*   Price Segment Revenue Chart (price_segments.png)

## Gap Analysis Types

| Gap Type | Signal | Opportunity |
|----------|--------|-------------|
| HIGH_SOV_LOW_CONVERSION | High visibility, low sales | Pricing/review problem |
| LOW_SOV_HIGH_CONVERSION | Low visibility, high sales | Strong product, weak marketing |

## Brand Classification

| Type | Description |
|------|-------------|
| **Major Brand** | >5% market share, established |
| **Amazon Brand** | Amazon Basics, private labels |
| **Private Label** | FBA sellers, white label |
| **Emerging** | <2% share, new entrants |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Market Share Pie | By brand type | `market_share.png` |
| Concentration Bar | HHI/CR metrics | `concentration.png` |
| Brand Breakdown | Type distribution | `brand_types.png` |
| Opportunity Bubble | SOV vs Revenue | `opportunity.png` |
| Price Segments | Revenue by price tier | `price_segments.png` |

## Workflow Integration

```
📊 Competition Phase
├── market-share-analyzer → Analyze brand concentration ← YOU ARE HERE
├── competitor-analyzer → Analyze competitors
└── review-checker → Check review barriers
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- SOV data requires Jungle Scout access
- Revenue estimates are approximations
- Brand classification is heuristic-based
- Cross-validation may show discrepancies
- Category cleaner affects sample size

## References

- `references/display-rules.md` — Chart styling guidelines

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/market_share_analyzer.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/market_share_analyzer.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/market_share_analyzer.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
