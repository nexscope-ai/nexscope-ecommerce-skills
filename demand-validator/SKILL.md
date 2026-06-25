---
name: demand-validator
version: 1.0.0
description: |
  Validate whether demand is real by comparing search volume with sales and buying intent. Triggers: is demand real, fake demand, inflated volume, are people buying, conversion gap. Use for demand proof, not broad market overview or niche go/no-go scoring.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Demand Validator v1.0.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**Is this demand real or inflated?**

Validate whether market demand is genuine by comparing search volume to actual sales.

## Core Question

> — Is this demand real?
> Search volume ≠ Sales!

## When to Use

- Validating market opportunity before investment
- Detecting inflated/fake search volume
- Identifying markets with high buying intent
- Finding hidden gems with low search but high conversion

## Differs From / Not Applicable

- Use market-overview for a broad market picture.
- Use niche-evaluator for final go/no-go entry scoring.
- Use this skill when the question is whether search interest converts into actual buying demand.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/share-of-voice` | Monthly search volume (SOV) |
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Products with sales estimates |
| ABA (Amazon Brand Analytics) | `/api/v1/tools/linkfox/aba/intelligentQuery` | SFR 12-week trend + Top 3 Click Share (2 queries) |
| eBay | `/api/v1/tools/linkfox/ebay/search` (showOnly: Sold) | Cross-platform sold listings validation |
| TikTok Echotik | `/api/v1/tools/linkfox/echotik/listProduct` | Social commerce demand signals |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR history, seasonality, seller count trends |

## Core Metric: Search-to-Sale Ratio (SSR)

```
SSR = (Total Monthly Sales / Monthly Search Volume) × 100
```

### SSR Benchmarks

| SSR | Buying Intent | Meaning |
|-----|---------------|---------|
| > 5% | 🔥 HIGH | Strong conversion, real demand |
| 2-5% | 🟡 MODERATE | Normal market |
| 0.5-2% | 🟠 LOW | More browsing than buying |
| < 0.5% | 🔴 VERY LOW | Window shoppers, inflated search |

## Demand Patterns

| Pattern | Signal | Description | Risk |
|---------|--------|-------------|------|
| 🟢 **REAL_DEMAND** | High SSR + Stable | Verified buying intent | LOW |
| 🟠 **WINDOW_SHOPPERS** | High search, low sales | People look but don't buy | HIGH |
| 💎 **HIDDEN_GEM** | Low search, high conversion | Under-the-radar opportunity | LOW |
| 🎭 **HYPE_MARKET** | Massive search, tiny sales | Viral but no buyers | VERY HIGH |
| 👑 **MONOPOLIZED** | High sales concentration | Few sellers dominate | MEDIUM |

## Reality Score

Combined score (0-100) based on multiple factors:

| Component | Weight | Description |
|-----------|--------|-------------|
| SSR Score | 40% | Search-to-sale ratio |
| Sales Velocity | 30% | Total monthly sales volume |
| Market Distribution | 20% | How spread out are sales |
| Trend Stability | 10% | Consistent or volatile |

### Reality Score Classification

| Level | Score | Meaning |
|-------|-------|---------|
| 🟢 **VERIFIED** | 70-100 | Strong, real demand |
| 🟡 **MODERATE** | 50-70 | Real but verify further |
| 🟠 **QUESTIONABLE** | 30-50 | May be inflated |
| 🔴 **WEAK** | 0-30 | Likely not real demand |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Analyze keyword
python3 scripts/demand_validator.py '{"keyword": "yoga mat"}'

# Different market
python3 scripts/demand_validator.py '{"keyword": "face wash", "market": "UK"}'

# With chart output
python3 scripts/demand_validator.py '{"keyword": "kombucha"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Keyword to analyze |
| `market` | string | | Marketplace (US/UK/DE/FR/CA/JP) |

## Output Structure

The output will be a structured markdown report, following this format:

**Market Demand Validation Report: [Keyword]**

---

**1. Executive Summary**
*   **Keyword:** [keyword]
*   **Marketplace:** [marketplace]
*   **Products Analyzed:** [products_analyzed]
*   **Market Reality Assessment:** [reality_score.level] [reality_score.emoji]
*   **Demand Pattern:** [demand_pattern.pattern] [demand_pattern.emoji] - [demand_pattern.description]
*   **Core Insight:** [insights.summary]

**2. Demand & Sales Overview**
*   **Key Metrics:**

| Metric | Value | Unit/Description |
| :--- | :--- | :--- |
| Monthly Search Volume | [search_data.monthly_search_volume] | (Source: [search_data.source]) |
| Total Monthly Units Sold | [sales_data.total_monthly_units] | Units |
| Total Monthly Revenue | [sales_data.total_monthly_revenue] | |
| Avg Sales per Product | [sales_data.avg_sales_per_product] | Units/Product |
| Avg Revenue per Product | [sales_data.avg_revenue_per_product] | /Product |
| Search-to-Sale Ratio (SSR) | [demand_metrics.search_to_sale_ratio]% | |
| Revenue per Search | [demand_metrics.revenue_per_search] | |
| Buying Intent | [demand_metrics.buying_intent] | |

**3. Market Reality Assessment**
*   **Assessment Results:**

| Metric | Value | Description |
| :--- | :--- | :--- |
| Reality Score | [reality_score.score] | |
| Reality Level | [reality_score.level] | |
| Cross-Platform Confidence | [reality_score.cross_platform_confidence]% | |
| Demand Pattern | [demand_pattern.pattern] | [demand_pattern.description] (Risk: [demand_pattern.risk]) |

**4. Stability Analysis**
*   **Stability Indicators:**

| Indicator | Value |
| :--- | :--- |
| Sales Distribution | [stability_analysis.sales_distribution] |
| Top 10 Share | [stability_analysis.top_10_share]% |
| Variance Level | [stability_analysis.variance_level] |
| Stability Score | [stability_analysis.stability_score] |

**5. Cross-Platform Validation**
*   **Amazon Brand Analytics (ABA) Details:**

| ABA Metric | Value |
| :--- | :--- |
| Search Frequency Rank (SFR) | [cross_platform_validation.aba.search_frequency_rank] |
| SFR Trend | [cross_platform_validation.aba.sfr_direction] |
| Volume Tier | [cross_platform_validation.aba.volume_tier] |
| Market Concentration | [cross_platform_validation.aba.market_concentration] |

*   **ABA Top 3 Clicked ASINs:**

| ASIN | Product Name | Click Share |
| :--- | :--- | :--- |
| [cross_platform_validation.aba.top_asins[0].asin] | [cross_platform_validation.aba.top_asins[0].title] | [cross_platform_validation.aba.top_asins[0].share]% |
| [cross_platform_validation.aba.top_asins[1].asin] | [cross_platform_validation.aba.top_asins[1].title] | [cross_platform_validation.aba.top_asins[1].share]% |
| [cross_platform_validation.aba.top_asins[2].asin] | [cross_platform_validation.aba.top_asins[2].title] | [cross_platform_validation.aba.top_asins[2].share]% |

*   **Other Platform Validation:**

| Platform | Metric | Value | Validation Status |
| :--- | :--- | :--- | :--- |
| eBay | Units Sold | [cross_platform_validation.ebay.sold_count] | Demand Level: [cross_platform_validation.ebay.demand_level], Verified: [cross_platform_validation.ebay.demand_verified] |
| TikTok | Product Count | [cross_platform_validation.tiktok.product_count] | Opportunity: [cross_platform_validation.tiktok.opportunity], Signal: [cross_platform_validation.tiktok.signal] |
| Keepa | BSR Trend | [cross_platform_validation.keepa.bsr_trend] | Momentum: [cross_platform_validation.keepa.bsr_momentum], Seasonality: [cross_platform_validation.keepa.seasonality] |

**6. Actionable Recommendations**
*   [First recommendation from `insights.recommendations`]
*   [Second recommendation from `insights.recommendations`]
*   ... (Listing all key recommendations)

**7. Attached Visualizations**
*   Search vs Sales (1_search_vs_sales.png)
*   Sales Distribution Histogram (2_sales_distribution.png)
*   Reality Score Gauge (3_reality_score.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Search vs Sales | Bar comparison | `1_search_vs_sales.png` |
| Sales Distribution | Histogram curve | `2_sales_distribution.png` |
| Reality Score | Gauge visualization | `3_reality_score.png` |

## Insights Generated

| Insight | Trigger |
|---------|---------|
| Real Demand Verified | Reality score > 70 |
| Hidden Gem Found | HIDDEN_GEM pattern |
| Window Shoppers Warning | WINDOW_SHOPPERS pattern |
| Hype Market Alert | HYPE_MARKET pattern |
| Monopolized Market | Top 10 share > 80% |
| High Buying Intent | SSR > 5% |
| Low Conversion | SSR < 1% |
| ABA High Search Demand | SFR ≤ 1000 (VERY_HIGH tier) |
| ABA Fragmented Market | Top 3 click share < 40% total |

## ABA (Brand Analytics) Details

Two separate queries are made to the ABA intelligent query API:

1. **SFR Trend** — 12-week Search Frequency Rank history
   - Lower rank = more popular
   - Trend direction: RISING / STABLE / DECLINING
   - Volume tier: VERY_HIGH (≤1000), HIGH (≤5000), MEDIUM (≤20000), LOW (≤100000)

2. **Click Share** — Top 3 clicked ASINs and their click share %
   - Market concentration: MONOPOLY (top1 > 30%), CONCENTRATED (top3 > 40%), FRAGMENTED (else)
   - Used to assess whether new products can capture clicks

> ⚠️ Note: The `region` parameter must be uppercase (e.g., `US`, `UK`, `DE`). Lowercase will return empty data.

## Category Cleaner Integration

This skill uses the category cleaner to remove noise products:
- Accessories vs main products
- Different product types with same keyword
- Irrelevant items

Example: "yoga mat" removes mat bags, straps, towels.

## Workflow Integration

```
📊 Validation Phase
├── demand-validator → Validate demand is real ← YOU ARE HERE
└── price-history-analyzer → Check for price wars
└── product-validator → Validate product data
```

## Real-World Examples

| Keyword | Search | Sales | SSR | Pattern |
|---------|--------|-------|-----|---------|
| Face Wash | 899K | 1.25M | 138.6% | VERIFIED (repeat purchases) |
| Kombucha | 201K | 128K | 63.6% | REAL_DEMAND |
| Stainless Steel Lunch Box | 37K | 17.8K | 48.2% | HIDDEN_GEM |

## Limitations

- Sales estimates are approximations
- Search volume from Jungle Scout may lag
- Category cleaner may be aggressive
- High-repeat-purchase products show SSR > 100%
- ABA click share only returns Top 3 ASINs (API limitation)
- ABA requires uppercase region code (US/UK/DE/FR/CA/JP)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines
