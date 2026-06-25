---
name: price-history-analyzer
version: 1.1.0
description: |
  Analyze historical pricing, price wars, volatility, and Buy Box stability. Triggers: Keepa chart, price history, price trend, historical pricing. Use for long-term history, not current alerts; use price-monitor for recent changes.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Price History Analyzer v1.1.0

**Is there a price war? Are prices stable?**

Analyze price wars, volatility, and Buy Box stability using Keepa historical data.

## Core Questions

> — Is there a price war?
> — Are prices stable?
> — Can I win the Buy Box?

## Clarify or Infer Before Querying

- If ASIN is missing, ask for the ASIN or use product search to find candidate ASINs.
- Clarify marketplace and desired history window when relevant.
- Do not use only a product keyword for historical price analysis unless an ASIN can be resolved.

## When to Use

- Evaluating market pricing stability before entry
- Assessing price war risk
- Understanding Buy Box competition
- Analyzing historical pricing trends

## Differs From / Not Applicable

- Use price-monitor for recent/current price alerts and competitor changes.
- Use competitor-analyzer for broader competitor metrics.
- Use this skill for historical price trend, volatility, price wars, and Buy Box stability.

## Data Source

| Source | Endpoint | Data |
|--------|----------|------|
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | Buy Box history, BSR, ratings, monthly sold |
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/search` | Current product list |

### Keepa Data Fields

| Field | Description |
|-------|-------------|
| `buyboxPrice` | Historical Buy Box prices with timestamps |
| `bsrSub` | BSR ranking history by category |
| `ratingCount` | Review count history |
| `monthlySold` | Monthly sales history |

## Key Metrics

| Metric | Description | Thresholds |
|--------|-------------|------------|
| **Price War Score** | Overall price war intensity (0-100) | < 25 LOW, 25-50 MODERATE, 50-75 HIGH, > 75 SEVERE |
| **PVI (Price Volatility Index)** | Standard deviation / mean × 100 | < 5% LOW, 5-10% MEDIUM, 10-20% HIGH, > 20% EXTREME |
| **Buy Box Stability** | Changes per day | < 0.5 VERY_STABLE, 0.5-1 STABLE, 1-2 MODERATE, 2-5 UNSTABLE, > 5 CHAOTIC |
| **Price Trend** | Direction over time | RISING, STABLE, DECLINING, CRASHED |

## Price War Score Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Volatility | 35% | PVI contribution (max 35 points) |
| Trend | 25% | Declining trend adds points |
| Price Drops | 25% | Frequency of significant drops |
| Buy Box Instability | 15% | Changes per day factor |

## Price War Levels

| Level | Score | Signal | Action |
|-------|-------|--------|--------|
| 🟢 **LOW** | 0-25 | Healthy pricing | Safe to enter |
| 🟡 **MODERATE** | 25-50 | Some competition | Monitor weekly |
| 🟠 **HIGH** | 50-75 | Active price war | Caution required |
| 🔴 **SEVERE** | 75-100 | Intense price war | Avoid market |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Analyze by keyword
python3 scripts/price_history_analyzer.py '{"keyword": "face wash"}'

# Analyze specific ASIN
python3 scripts/price_history_analyzer.py '{"asin": "B07RL88DD2"}'

# Different market
python3 scripts/price_history_analyzer.py '{"keyword": "yoga mat", "market": "UK"}'

# With chart output
python3 scripts/price_history_analyzer.py '{"keyword": "face wash"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | - | Search keyword |
| `asin` | string | - | Specific ASIN to analyze |
| `market` | string | | Marketplace (US/UK/DE/FR/CA/JP) |

## Output Structure

```json
{
 "keyword": "face wash",
 "market": "US",
 "analysis_date2026-04-09",
 "products_analyzed": 5,
 "price_analysis": {
 "data_points": 265,
 "period_days": 90,
 "current_price": 7.49,
 "min_price": 5.36,
 "max_price": 7.49,
 "avg_price": 6.82,
 "std_dev": 0.42,
 "pvi": 6.1,
 "volatility_levelLOW",
 "price_changes_count": 15,
 "price_drops": 3,
 "price_increases": 5,
 "trend_pct": 2.1,
 "trend_directionSTABLE"
 },
 "buybox_analysis": {
 "stabilityMODERATE",
 "stability_score": 50,
 "total_changes": 54,
 "changes_per_day": 1.8,
 "outages": 2,
 "outage_pct": 3.7
 },
 "price_war_score": {
 "score": 9,
 "levelLOW",
 : "🟢",
 : {
 "volatility": 9,
 "trend": 0,
 "price_drops": 0,
 "buybox_instability": 0
 }
 },
 "insights": {
 "summary🟢 Healthy pricing. Score 9, volatility 6.1%. Safe market.",
 "assessments": [...],
 "recommendations": [...]
 }
}
```

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Price History | Line chart with trend | `1_price_history.png` |
| Price War Score | Gauge visualization | `2_price_war_score.png` |
| Volatility & Buy Box | Side-by-side summary | `3_volatility_buybox.png` |

## Insights Generated

| Insight | Trigger |
|---------|---------|
| Healthy Pricing | Score < 25 |
| Moderate Competition | Score 25-50 |
| Active Price War | Score 50-75 |
| Severe Price War | Score > 75 |
| High Volatility | PVI > 15% |
| Low Volatility | PVI < 5% |
| Downward Trend | Declining direction |
| Upward Trend | Rising direction |
| Buy Box Chaotic | Stability = CHAOTIC |
| Buy Box Stable | Stability = VERY_STABLE |

## Recommendations

| Situation | Recommendation |
|-----------|----------------|
| Score < 25 | Normal competitive strategy viable |
| Score 25-50 | Monitor prices weekly, build margin buffer |
| Score > 50 | Avoid price competition, differentiate on value |
| Declining trend | Factor declining prices into margin calculations |
| Organic > 90% | Competitor relies on organic — vulnerable to PPC attack |
| Organic < 50% | Competitor heavily PPC-dependent — may have weak organic |

## Workflow Integration

```
📊 Validation Phase
├── demand-validator → Validate demand is real
├── price-history-analyzer → Check for price wars ← YOU ARE HERE
└── product-validator → Validate product data
```

## Limitations

- Keepa data availability varies by ASIN
- Historical data typically 90 days
- API calls consume Keepa tokens
- Category cleaner applied (may reduce sample size)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines
