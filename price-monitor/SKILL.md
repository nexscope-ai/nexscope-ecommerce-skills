---
name: price-monitor
version: 1.0.0
description: |
  Monitor recent competitor price, BSR, and seller-count changes. Triggers: price alert, competitor changed price, current price monitoring. Use for recent/current changes, not long-term Keepa history; use price-history-analyzer for history.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope", "keepa"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Price Monitor v1.0.0

## Core Question

Have competitor prices, BSR, sellers, or availability changed recently?

**Did competitors change their prices?**

Monitor competitor price changes, BSR trends, and seller count.

## Clarify or Infer Before Querying

- If ASINs or competitors are missing, ask for them or find candidates with competitor/product search first.
- Clarify marketplace, alert metric, and comparison window.
- Use recent/current monitoring assumptions rather than long-term history unless requested.

## When to Use
- User wants to track competitor prices
- User asks "what's the price history"
- User wants to know about price changes
- User needs BSR trend analysis
- User wants to monitor seller count
- User asks "did they lower their price"

## Differs From / Not Applicable

- Use price-history-analyzer for long-term Keepa history and price-war analysis.
- Use competitor-analyzer for broader product competition.
- Use this skill for recent/current changes and monitoring.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | Price history, BSR, seller count |

## Supported Marketplaces

| Market | Domain | Currency |
|--------|--------|----------|
| 🇺🇸 US | 1 | $ |
| 🇬🇧 UK | 2 | £ |
| 🇩🇪 DE | 3 | € |
| 🇫🇷 FR | 4 | € |
| 🇯🇵 JP | 5 | ¥ |
| 🇨🇦 CA | 6 | C$ |
| 🇮🇹 IT | 8 | € |
| 🇪🇸 ES | 9 | € |
| 🇮🇳 IN | 10 | ₹ |
| 🇲🇽 MX | 11 | MX$ |
| 🇧🇷 BR | 12 | R$ |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Single ASIN
python3 scripts/price_monitor.py '{"asin": "B0BTYCRJSS"}'

# Multiple ASINs
python3 scripts/price_monitor.py '{"asins": ["B0BTYCRJSS", "B08EXAMPLE"]}'

# Custom period
python3 scripts/price_monitor.py '{"asin": "B0BTYCRJSS", "days": 30}'

# Different market
python3 scripts/price_monitor.py '{"asin": "B0BTYCRJSS", "market": "UK"}'

# With charts
python3 scripts/price_monitor.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `asin` | string | Yes* | - | Single ASIN to monitor |
| `asins` | array | Yes* | - | Multiple ASINs (max 5) |
| `market` | string | No | | Marketplace |
| `days` | int | No | 90 | History period (max 365) |

*One of `asin` or `asins` required

## Output Structure

The output will be a structured markdown report, following this format:

**Price Monitoring Report: [ASIN(s)]**

---

**1. Executive Summary**
*   **Monitored Market:** [market]
*   **Currency:** [currency]
*   **Monitoring Days:** [days]
*   **Products Monitored:** [summary.products_monitored]
*   **Total Alerts:** [summary.total_alerts]
*   **High-Priority Alerts:** [summary.high_priority]
*   **Status:** [summary.status]
*   **Key Insight:** This report summarizes price, BSR, and seller-count changes for key products during the monitoring period.

**2. Product Details & Changes**
*(Provide detailed analysis for each monitored ASIN)*

**Target ASIN: [products[i].asin]**

*   **Price Analysis (Buy Box):**

| Metric | Value |
| :--- | :--- |
| Current Price | [products[i].price_analysis.buybox.current] |
| Initial Price | [products[i].price_analysis.buybox.oldest] |
| Lowest Price | [products[i].price_analysis.buybox.min] |
| Highest Price | [products[i].price_analysis.buybox.max] |
| Change Amount | [products[i].price_analysis.buybox.change] |
| Change Percentage | [products[i].price_analysis.buybox.change_pct]% |
| Trend | [products[i].price_analysis.buybox.trend] |

*   **BSR Analysis:**

| Metric | Value |
| :--- | :--- |
| Category | [products[i].bsr_analysis.category] |
| Current BSR | [products[i].bsr_analysis.current] |
| Initial BSR | [products[i].bsr_analysis.oldest] |
| Change Percentage | [products[i].bsr_analysis.change_pct]% |
| Improved | [products[i].bsr_analysis.improved] |
| Trend | [products[i].bsr_analysis.trend] |

*   **Seller Analysis:**

| Metric | Value |
| :--- | :--- |
| Current Seller Count | [products[i].seller_analysis.current] |
| Initial Seller Count | [products[i].seller_analysis.oldest] |
| Change Amount | [products[i].seller_analysis.change] |
| Trend | [products[i].seller_analysis.trend] |

*   **Alerts Found:**

| Alert Type | Severity | Icon | Message |
| :--- | :--- | :--- | :--- |
| [products[i].alerts[0].type] | [products[i].alerts[0].severity] | [products[i].alerts[0].icon] | [products[i].alerts[0].message] |
| ... | ... | ... | ... |
*(List all alerts for this product)*

*   **Key Findings:**
    *   [products[i].insights.key_findings[0]]
    *   [products[i].insights.key_findings[1]]
    *   ...

**3. All Alerts Summary**
*   **All Product Alerts:**

| ASIN | Alert Type | Severity | Message |
| :--- | :--- | :--- | :--- |
| [all_alerts[0].asin] | [all_alerts[0].type] | [all_alerts[0].severity] | [all_alerts[0].message] |
| ... | ... | ... | ... |

**4. Attached Visualizations**
*   Price Summary (1_price_summary.png)
*   Price Change (2_price_change.png)
*   BSR Range (3_bsr_range.png)
*   Alert Distribution (4_alerts.png)

## Price Types Tracked

| Type | Description |
|------|-------------|
| **Buybox** | Current buy box price |
| **FBA** | Third-party FBA seller price |
| **FBM** | Third-party FBM seller price |
| **List** | Crossed-out list price |
| **Deal** | Lightning deal / flash sale price |

## Alert Types

| Alert | Severity | Trigger |
|-------|----------|---------|
| 🔴 Price Drop | HIGH | ≥15% decrease |
| 🟡 Price Decrease | MEDIUM | 5-15% decrease |
| 📈 Price Increase | INFO | ≥15% increase |
| ⚡ Flash Sale | HIGH | ≥20% single-day drop |
| 🚀 BSR Surge | HIGH | ≥30% improvement |
| 📉 BSR Decline | MEDIUM | ≥50% decline |
| 👥 New Sellers | MEDIUM | 3+ new sellers |
| 📤 Sellers Left | INFO | 2+ sellers left |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Price Summary | Min/Current/Max by type | `1_price_summary.png` |
| Price Change | % change by type | `2_price_change.png` |
| BSR Range | BSR over period | `3_bsr_range.png` |
| Alerts | Alert severity breakdown | `4_alerts.png` |

## Workflow Integration

```
📊 Competitive Intelligence
├── competitor-analyzer → Find competitors
├── price-monitor → Track prices ← YOU ARE HERE
├── keyword-rank-tracker → Track rankings
└── review-checker → Monitor reviews
```

## Example Report

**ASIN: B0BTYCRJSS | 90-Day Monitor**

| Metric | Start | Current | Change |
|--------|-------|---------|--------|
| Buybox | $24.99 | $19.99 | -20% 🔴 |
| FBA | $19.99 | $19.99 | 0% |
| BSR | #85 | #37 | -56% 🚀 |
| Sellers | 1 | 3 | +2 👥 |

**Alerts:**
- 🔴 HIGH: Buybox price dropped 20%
- 🚀 HIGH: BSR improved significantly
- 👥 MEDIUM: 2 new sellers entered

## Use Cases

### 1. Competitor Price Watch
> 

### 2. Price Drop Detection
> 

### 3. Market Entry Timing
> 

### 4. BSR Correlation
> 

## Limitations

- Keepa data may have gaps (especially for low-volume products)
- Price values of `-1` indicate out-of-stock periods
- Maximum 365 days of history
- Max 5 ASINs per request (to manage API costs)
- Real-time data not available (historical snapshots)

## API Cost

~360 tokens per ASIN (varies with data density)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Output formatting

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/price_monitor.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/price_monitor.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/price_monitor.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
