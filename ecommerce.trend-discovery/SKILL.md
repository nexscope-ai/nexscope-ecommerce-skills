---
name: ecommerce.trend-discovery
version: 2.0.0
description: |
  Discover rising ecommerce categories and emerging niches across platforms. Triggers: what is trending, trending products, rising categories, next big thing. Use for trend discovery, not validating a specific niche or finding new Amazon launches.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Trend Discovery v2.0.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**What categories are trending? What niches are rising?**

Discover rising e-commerce categories using cross-platform data analysis.

## Core Question

> — What categories are trending?
> — What's hot on TikTok?

## When to Use

- Starting product research and need direction
- Finding rising niches before they become competitive
- Validating category momentum across platforms
- Comparing trend strength between keywords
- Identifying seasonal vs sustained trends

## Differs From / Not Applicable

- Use market-overview after selecting a market/category to understand it deeply.
- Use new-product-tracker for newly launched Amazon products.
- Use niche-evaluator for go/no-go entry scoring.
- Use this skill for early trend/category discovery.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| TikTok Echotik | `/api/v1/tools/linkfox/echotik/listProduct` | Hot products, sales velocity |
| Google Trends | `/api/v1/tools/linkfox/googleTrend/getTrendByKeys` | Search interest over time |
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Product listings, competition |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/historical-search-volume` (POST) | 30/90/180-day search volume trends |

## Analysis Modes

| Mode | Use Case |
|------|----------|
| `+cross-platform` | Full discovery (TikTok → Google → Amazon) |
| `+tiktok-hot` | TikTok trending products only |
| `+compare` | Compare specific keywords head-to-head |
| `+timeline` | Single keyword historical trend |

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately
3. **All chart styling** is driven by `scripts/chart_style.json` (derived from `references/display-rules.md`). If you need to change colors/fonts/styles, edit `chart_style.json` — do NOT hardcode styles in the script.
4. **To update chart_style.json**: read `references/display-rules.md`, extract the relevant values, write to `scripts/chart_style.json`.

## Usage

**Always include `--chart /tmp/<descriptive-name>` in every run:**

```bash
# Full cross-platform discovery (ALWAYS with --chart)
python3 scripts/trend_discovery.py '{"keywords": ["yoga mat", "pilates mat"]}' --chart /tmp/trend-charts

# Single keyword
python3 scripts/trend_discovery.py '{"keywords": ["kombucha"]}' --chart /tmp/trend-charts
```

After the script finishes, **send all generated chart PNGs to the user**.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | "cross-platform" | Analysis mode |
| `region` | string | | Target region |
| `keywords` | array | - | Keywords to compare |
| `keyword` | string | - | Single keyword for timeline |
| `min_sales` | int | 5000 | Minimum 30d sales for TikTok |
| `days` | int | 90 | Historical days for trends |

## Output Structure

The output will be a structured markdown report, following this format:

**Trend Discovery Report: [Keywords]**

---

**1. Executive Summary**
*   **Analyzed Keywords:** [analyzed_keywords]
*   **Analysis Mode:** [mode] (for example: cross-platform, TikTok hot, comparison, timeline)
*   **Confidence Level:** [insights.confidence_level]
*   **Key Insight:** [insights.summary]

**2. Trend Overview**
*   **Trend Distribution:**

| Trend Category | Keyword Count |
| :--- | :--- |
| 🔥 Hot | [insights.trend_distribution.hot] |
| 📈 Rising | [insights.trend_distribution.rising] |
| ➡️ Stable | [insights.trend_distribution.stable] |
| 📉 Declining | [insights.trend_distribution.declining] |

*   **Platform Signals:**

| Platform | Count (Keywords with Signals) |
| :--- | :--- |
| TikTok Hot | [insights.platform_signals.tiktok_hot] |
| Google Rising Trend | [insights.platform_signals.google_rising] |
| Amazon New Product Success | [insights.platform_signals.amazon_new_success] |

**3. Discovered Trends**
*   **Keywords sorted by trend score (show top 5):**

| Rank | Keyword | Trend Score | Trend Verdict | Signal Sources | Google Trend Direction | Google Trend Change % | TikTok Sales (Estimated) | Amazon New Product Success |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [trends[0].keyword] | [trends[0].trend_score.score] | [trends[0].trend_score.verdict] | [trends[0].trend_score.signals] | [trends[0].google_trends.direction] | [trends[0].google_trends.change_pct]% | [trends[0].tiktok.total_sales] | [trends[0].amazon.new_entrant_success] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**4. Overall Recommendations**
*   **All Recommendations:**
    *   [insights.recommendations[0]]
    *   [insights.recommendations[1]]
    *   ...

**5. Attached Visualizations**
*   Trend Score Comparison (trend_comparison.png)
*   Google Trends (google_trends.png)
*   Market Maturity (market_maturity.png)
*   Score Breakdown (score_breakdown.png)

## Trend Classification

| Signal | Criteria | Action |
|--------|----------|--------|
| 🔥 **HOT** | TikTok viral + Google rising + Amazon growing | Enter quickly |
| 📈 **RISING** | Consistent upward trend across 2+ platforms | Good opportunity |
| ➡️ **STABLE** | Flat trend, established market | Evaluate competition |
| 📉 **DECLINING** | Downward trend | Avoid or exit |
| 🎭 **HYPE** | TikTok hot but no Amazon demand | Risky, may not convert |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Trend Score Comparison | Horizontal bar chart of keyword scores | `trend_comparison.png` |
| Google Trends | Multi-keyword search interest over time | `google_trends.png` |
| Market Maturity | Pie chart of emerging/growing/mature split | `market_maturity.png` |
| Score Breakdown | Top keyword score composition | `score_breakdown.png` |

## Cross-Platform Validation

| Platform | Signal Weight | Why |
|----------|---------------|-----|
| TikTok | 35% | Early trend indicator, viral potential |
| Google Trends | 30% | Consumer interest validation |
| Amazon | 35% | Actual purchase intent |

## Workflow Integration

```text
Discovery Phase
|-- trend-discovery -> Find trending categories -> YOU ARE HERE
|-- market-overview -> Understand the market
`-- niche-evaluator -> Evaluate niche potential
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- TikTok data limited to supported regions
- Google Trends has 1-2 day lag
- Cross-platform correlation is approximate
- Some trends are regional only
- Viral products may not have long-term demand

## References

- `references/api-reference.md` - API endpoint documentation
- `references/display-rules.md` - Chart styling guidelines (source of truth)
- `scripts/chart_style.json` - Machine-readable chart style config (derived from display-rules.md, loaded by script at runtime)

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/trend_discovery.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/trend_discovery.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/trend_discovery.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
