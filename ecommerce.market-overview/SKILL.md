---
name: ecommerce.market-overview
version: 2.3.0
description: |
  Produce a broad market snapshot across demand, competition, price, and platforms. Triggers: market overview, what is this market like, full market picture. Use for broad context, not go/no-go scoring, share concentration, or recent alerts.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Market Overview v2.3.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**What's the market like? Complete market intelligence.**

Comprehensive market analysis covering industry overview, competitive landscape, consumer demand, and multi-platform comparison.

## Core Question

> — What's this market like?
> — Give me the market overview.

## When to Use

- Starting research on a new product category
- Getting a complete picture before deep-diving
- Comparing market conditions across platforms
- Understanding the full competitive landscape

## Differs From / Not Applicable

- Use niche-evaluator for go/no-go entry scoring.
- Use market-share-analyzer for concentration and brand dominance.
- Use market-alert for recent changes and anomalies.
- Use this skill for broad first-pass market understanding.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Products, prices, reviews, BSR |
| eBay Search | `/api/v1/tools/linkfox/ebay/search` | Cross-platform pricing |
| Walmart Search | `/api/v1/tools/linkfox/walmart/search` | Multi-channel comparison |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/share-of-voice` | Search volume, brand SOV |
| ABA (Amazon Brand Analytics) | `/api/v1/tools/linkfox/aba/intelligentQuery` | Search Frequency Rank |
| TikTok Echotik | `/api/v1/tools/linkfox/echotik/listProduct` | Social commerce signals |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | Historical BSR, price trends |

## Analysis Dimensions

| Dimension | Description |
|-----------|-------------|
| **Industry Overview** | Market size, growth trends |
| **Competitive Landscape** | Brand concentration, top players |
| **Consumer Demand** | Search patterns, buying behavior |
| **Price Analysis** | Distribution, sweet spots |
| **Multi-Platform** | Amazon vs eBay vs Walmart |
| **Compliance** | Category restrictions, requirements |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Full market overview
python3 scripts/market_overview.py '{"keyword": "yoga mat"}'

# Specific platform focus
python3 scripts/market_overview.py '{"keyword": "face wash", "platforms": ["amazon"]}'

# Different market
python3 scripts/market_overview.py '{"keyword": "kombucha", "market": "UK"}'

# With chart output
python3 scripts/market_overview.py '{"keyword": "yoga mat"}' --chart /tmp/output

# With market sizing
python3 scripts/market_overview.py '{"keyword": "yoga mat"}' --market-size

# Export to CSV
python3 scripts/market_overview.py '{"keyword": "yoga mat"}' --csv /tmp/market.csv
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Market keyword |
| `market` | string | | Target marketplace |
| `platforms` | array | ["amazon"] | Platforms to analyze |
| `limit` | int | 50 | Products per platform |

## Output Structure

The output will be a structured markdown report, following this format:

**Market Overview Analysis Report: [Keyword]**

---

**1. Executive Summary**
*   **Analysis Keyword:** [keyword]
*   **Market Overview:** [insights.summary]
*   **Market Health:** [insights.market_health]
*   **Competition Level:** [summary.competition_level]
*   **Estimated Market Size:** [summary.estimated_market_size]
*   **Core Recommendation:** [insights.recommendations[0]]

**2. Platform Data Comparison**
*   **Key Metrics Across Platforms:**

| Platform | Product Count | Average Price | Average Reviews | Average Rating | Monthly Revenue (Est.) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Amazon | [platforms.amazon.total_products] | [platforms.amazon.avg_price] | [platforms.amazon.avg_reviews] | [platforms.amazon.avg_rating] | [platforms.amazon.total_monthly_revenue] |
| eBay | [platforms.ebay.total_products] | [platforms.ebay.avg_price] | - | - | - |
| Walmart | [platforms.walmart.total_products] | [platforms.walmart.avg_price] | - | - | - |

*   **Amazon Platform Price Range:** Min [platforms.amazon.price_range.min], Max [platforms.amazon.price_range.max], Avg [platforms.amazon.price_range.avg]

**3. Brand & Competitive Landscape**
*   **Top 3 Amazon Brands:**

| Rank | Brand | Product Count |
| :--- | :--- | :--- |
| 1 | [platforms.amazon.top_brands[0][0]] | [platforms.amazon.top_brands[0][1]] |
| 2 | [platforms.amazon.top_brands[1][0]] | [platforms.amazon.top_brands[1][1]] |
| 3 | [platforms.amazon.top_brands[2][0]] | [platforms.amazon.top_brands[2][1]] |

*   **Market Concentration (ABA):** [enhanced_data.aba.market_concentration]
*   **Top Clicked ASINs (ABA):** [enhanced_data.aba.top_asins]

**4. Consumer Demand Analysis**
*   **Amazon Brand Analytics (ABA) Overview:**

| Metric | Value |
| :--- | :--- |
| Search Frequency Rank (SFR) | [enhanced_data.aba.search_frequency_rank] |
| Volume Tier | [enhanced_data.aba.volume_tier] |

*   **Cross-Platform Sales & Demand:**

| Platform | Units Sold / Product Count | Demand Level | Price Comparison (vs Amazon) | Opportunity Assessment |
| :--- | :--- | :--- | :--- | :--- |
| eBay | [enhanced_data.ebay_sold.sold_count] | [enhanced_data.ebay_sold.demand_level] | eBay Avg: [enhanced_data.ebay_sold.price_comparison.ebay_avg] | - |
| TikTok | [enhanced_data.tiktok.product_count] | - | - | [enhanced_data.tiktok.opportunity] (GMV: [enhanced_data.tiktok.estimated_gmv]) |

**5. Market Sizing Estimation (If available)**
*(Displayed only if `market_sizing` data is present)*

| Type | Total Amount | E-commerce Portion (if applicable) |
| :--- | :--- | :--- |
| TAM (Total Addressable Market) | [market_sizing.tam.total_retail] | [market_sizing.tam.ecommerce] |
| SAM (Serviceable Addressable Market) | [market_sizing.sam.amazon] (Amazon) | - |
| SOM (Serviceable Obtainable Market - Estimate) | [market_sizing.som.conservative_1pct] (Conservative 1% Share) | [market_sizing.som.aggressive_3pct] (Aggressive 3% Share) |

**6. Overall Insights & Recommendations**
*   **Key Metrics Summary:**

| Metric | Value |
| :--- | :--- |
| Average Reviews | [insights.key_metrics.avg_reviews] |
| Average Rating | [insights.key_metrics.avg_rating] |
| Average Price | [insights.key_metrics.avg_price] |
| Monthly Revenue | [insights.key_metrics.monthly_revenue] |

*   **All Recommendations:**
    *   [First recommendation from `insights.recommendations`]
    *   [Second recommendation from `insights.recommendations`]
    *   ...

**7. Attached Visualizations**
*   Cross-Platform Comparison (cross_platform.png)
*   Price Distribution (price_distribution.png)
*   Market Share (market_share.png)
*   Demand Trend (demand_trend.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Cross-Platform Comparison | Price/volume by platform | `cross_platform.png` |
| Price Distribution | Price segment bar | `price_distribution.png` |
| Market Share | Top brands pie | `market_share.png` |
| Demand Trend | Search volume over time | `demand_trend.png` |

## Market Health Indicators

| Indicator | Healthy | Warning |
|-----------|---------|---------|
| Growth Trend | Rising/Stable | Declining |
| Concentration | <60% CR4 | >80% CR4 |
| Price Stability | <10% variance | >25% variance |
| New Entrant Success | >20% new in top 50 | <5% new |

## Workflow Integration

```
📈 Discovery Phase
├── trend-discovery → Find trending categories
├── market-overview → Understand the market ← YOU ARE HERE
└── niche-evaluator → Evaluate niche potential
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- Multi-platform comparison requires all API access
- Revenue estimates are approximations
- Cross-platform data may have timing differences
- Compliance info is general guidance only
- Category cleaner affects sample size

## References

- `references/display-rules.md` — Chart styling guidelines
