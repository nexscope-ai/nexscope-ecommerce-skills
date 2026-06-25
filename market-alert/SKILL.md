---
name: market-alert
version: 3.0.0
description: |
  Monitor recent market changes and anomalies: SOV shifts, sales movement, review velocity, competitor changes. Triggers: market alert, recent change, SOV change, sales shift. Use for alerts/changes, not full market snapshots; use market-overview for broad analysis.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Market Alert v3.0.0

## Core Question

What changed recently in this market, and does it require action?

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**Are there market changes?**

Monitor market changes using Jungle Scout data (International Standard).

## Clarify or Infer Before Querying

- Clarify keyword/category, marketplace, and what kind of recent change matters: SOV, sales, price, reviews, or competitors.
- Use market-overview when the user wants a full snapshot rather than recent anomalies.

## Differs From / Not Applicable

- Use market-overview for a full market snapshot.
- Use trend-discovery for finding rising categories before choosing a market.
- Use price-monitor or review-monitor for ASIN-specific price/review alerts.
- Use this skill for recent market-level anomalies and changes.

## Workflow

1. Confirm market keyword/category, marketplace, and change type.
2. Fetch recent market signals.
3. Identify anomalies in SOV, sales, reviews, price, or competitor behavior.
4. Return alert summary, severity, likely cause, and recommended action.

## Usage

```bash
# Basic keyword analysis
python3 scripts/market_alert.py '{"keyword": "bluetooth earbuds"}'

# Specific market
python3 scripts/market_alert.py '{"keyword": "yoga mat", "market": "uk"}'

# With charts
python3 scripts/market_alert.py '{"keyword": "bluetooth earbuds"}' --chart /tmp/charts
```

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Parameters

| Parameter | Type | Required | Default |
|-----------|------|----------|---------|
| `keyword` | string | Yes | - |
| `market` | string | No | |
| `new_threshold_days` | int | No | 90 |

## Output Structure

The output will be a structured markdown report, following this format:

**Market Monitoring Alert Report: [Keyword]**

---

**1. Executive Summary**
*   **Analyzed Keyword:** [keyword]
*   **Analysis Market:** [market]
*   **Data Source:** [data_source]
*   **Total Market Products:** [composition.total_products]
*   **Total Market Average Revenue:** [composition.revenue.total_avg]
*   **Total Market Average Reviews:** [composition.reviews.total_avg]

**2. SOV (Share of Voice) Analysis**
*   **Total Market Revenue:** [sov_analysis.total_market_revenue]
*   **Brand Revenue Ranking (Top 3):**

| Rank | Brand | Revenue SOV% |
| :--- | :--- | :--- |
| 1 | [sov_analysis.brand_ranking[0].brand] | [sov_analysis.brand_ranking[0].revenue_sov_pct]% |
| 2 | [sov_analysis.brand_ranking[1].brand] | [sov_analysis.brand_ranking[1].revenue_sov_pct]% |
| 3 | [sov_analysis.brand_ranking[2].brand] | [sov_analysis.brand_ranking[2].revenue_sov_pct]% |
*(Listing more brands if available)*

**3. Market Alerts**
*   **Identified Alerts:**

| Alert Type | Severity | Trigger Condition |
| :--- | :--- | :--- |
| [alert.type] | [alert.severity] | [alert.trigger] |
| ... | ... | ... |
*(Listing all identified alerts)*

**4. Attached Visualizations**
*   SOV (Share of Voice) (1_sov.png)
*   Price Tiers Distribution (2_price_tiers.png)
*   Product Composition (3_composition.png)
*   Alerts Breakdown (4_alerts.png)

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search (SerpApi) | `/api/v1/tools/linkfox/amazon/search` | Product list ranked by relevance, monthly sales |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Search volume, keyword trends |
| Keepa | `/api/v1/tools/linkfox/keepa/productRequest` | `availableDate` for new competitor detection |
| Jungle Scout (fallback) | `/api/v1/tools/jungle-scout/product-database/query` | Fallback if Amazon Search fails |

**Note:** v3.0 uses Amazon Search as primary product source (real search results) instead of
Jungle Scout product-database (which returns random keyword-matched products, not ranked results).
Keepa enriches with `availableDate` (batch, single API call for up to 50 ASINs) to enable new competitor detection.

## SOV Calculation

**v3.0 uses real revenue for SOV:**

```
Brand SOV = Brand's 30-day Revenue / Total Market Revenue × 100%
```

This is more accurate than exposure-based SOV because:
- Revenue = actual sales, not just visibility
- Based on Jungle Scout's verified data
- Internationally accepted methodology

## Alert Types

| Alert | Severity | Trigger |
|-------|----------|---------|
| ⚡ Fast Riser | HIGH | New product with $1k+/mo revenue |
| 🆕 New Competitors | HIGH | ≥20% new products |
| 📢 SOV Shift | HIGH | New brands ≥15% revenue share |
| 🎯 Tier Concentration | MEDIUM | ≥40% new in one tier |
| 👑 Market Concentration | INFO | Top 3 brands ≥70% |
| 💡 Price Vacuum | INFO | Empty price range |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| SOV | Revenue-based market share | `1_sov.png` |
| Price Tiers | Distribution by price | `2_price_tiers.png` |
| Composition | New vs Established | `3_composition.png` |
| Alerts | Severity breakdown | `4_alerts.png` |

## API Configuration

NexScope proxy API key is provided via environment variable `NEXSCOPE_API_KEY`.

Auth header format: `Authorization: Bearer {NEXSCOPE_API_KEY}`

## Why Jungle Scout?

| Benefit | Description |
|---------|-------------|
| **International Recognition** | Trusted by sellers worldwide |
| **Data Compliance** | Official Amazon data partner |
| **Real Sales Data** | 30-day actual revenue & units |
| **Brand Value** | Enhances skill credibility |

## Limitations

- API rate limits apply
- 30-day data only (no historical trends)
- Product database returns ~50 products per query
- Some products may have null revenue data


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- Jungle Scout API: {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout
