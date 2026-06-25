---
name: niche-evaluator
version: 3.1.0
description: |
  Score whether a niche is worth entering. Triggers: should I enter, go/no-go, niche score, entry barrier, saturated market. Use for entry decisions, not broad overview, market share, or raw demand validation alone.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Niche Evaluator v3.1.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**Is this niche worth entering?**

Quantitatively evaluate whether a niche is worth entering using multi-platform data.

## Core Question

> — Is this niche worth entering?

## When to Use

- Evaluating a potential product category
- Comparing multiple niche opportunities
- Getting a quantitative score for go/no-go decisions
- Understanding the risk/reward profile of a market

## Differs From / Not Applicable

- Use market-overview for broad background research.
- Use demand-validator to test whether demand is real.
- Use market-share-analyzer to inspect brand concentration.
- Use this skill for an entry decision or quantitative niche score.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Products, prices, reviews, BSR |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Search volume, competition metrics |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | Historical BSR, price trends |
| Google Trends | `/api/v1/tools/linkfox/googleTrend/getTrendByKeys` | Trend momentum validation |
| ABA (Amazon Brand Analytics) | `/api/v1/tools/linkfox/aba/intelligentQuery` | Search Frequency Rank |
| eBay | `/api/v1/tools/linkfox/ebay/search` | Cross-platform demand validation |
| TikTok Echotik | `/api/v1/tools/linkfox/echotik/listProduct` | Social commerce trend signals |

## Scoring System

### Grade Scale

| Score | Grade | Action |
|-------|-------|--------|
| 75+ | A 🔥 | Highly Recommended |
| 65-74 | B ✅ | Recommended |
| 55-64 | C+ ⚠️ | Consider with differentiation |
| 45-54 | C 🟡 | Proceed with caution |
| <45 | D ❌ | Not recommended |

### Score Formula

```
Final Score = Base Score (0-100) + Modifiers (±32)
```

### Base Score Components

| Component | Points | Metrics |
|-----------|--------|---------|
| 📈 **Demand** | 25 | Search volume, trend direction |
| ⚔️ **Competition** | 25 | Review barriers, brand concentration |
| 💰 **Profit** | 25 | Price points, margins |
| 🎯 **Opportunity** | 25 | Gaps, differentiation potential |

### Modifier Factors (12 total)

| Factor | Range | Source | Auto |
|--------|-------|--------|------|
| Rating Quality | -2 ~ +4 | JS | ✅ |
| Amazon Seller | -6 ~ 0 | JS | ✅ |
| Brand Moat | -4 ~ 0 | JS | ✅ |
| New Entrants | 0 ~ +4 | JS | ✅ |
| Price Stability | -2 ~ +2 | Keepa | ✅ |
| Seasonality | -4 ~ +2 | JS | ✅ |
| Trend Momentum | -4 ~ +4 | Google | ✅ |
| Review Velocity | -2 ~ +2 | Keepa | ✅ |
| Listing Quality | -2 ~ +2 | Scrape | ✅ |
| Return Rate | -4 ~ 0 | JS | ✅ |
| Complexity Tag | -4 ~ 0 | Manual | ❌ |
| Moat Tag | 0 ~ +4 | Manual | ❌ |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Evaluate a niche
python3 scripts/niche_evaluator.py '{"keyword": "yoga mat"}'

# With specific tags
python3 scripts/niche_evaluator.py '{"keyword": "yoga mat", "tags": ["complexity:high"]}'

# Compare multiple niches
python3 scripts/niche_evaluator.py '{"keywords": ["yoga mat", "pilates mat"]}'

# With chart output
python3 scripts/niche_evaluator.py '{"keyword": "kombucha"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Niche keyword to evaluate |
| `keywords` | array | - | Multiple niches to compare |
| `market` | string | | Target marketplace |
| `tags` | array | - | Manual modifier tags |

## Output Structure

The output will be a structured markdown report, following this format:

**Niche Market Evaluation Report: [Keyword]**

---

**1. Executive Summary**
*   **Evaluated Keyword:** [keyword]
*   **Analysis Market:** [market]
*   **Analysis Date:** [analysis_date]
*   **Final Score:** [score.total]
*   **Evaluation Grade:** [score.grade]
*   **Recommendation:** [recommendation]
*   **Core Insight:** [insights.summary] (if available)

**2. Evaluation Score Details**
*   **Overall Score:** [score.total]
*   **Grade:** [score.grade]
*   **Base Score:** [score.base]
*   **Modifier Adjustment:** [score.modifiers]
*   **Score Components:**

| Component | Score |
| :--- | :--- |
| 📈 Demand | [score.components.demand] |
| ⚔️ Competition | [score.components.competition] |
| 💰 Profit | [score.components.profit] |
| 🎯 Opportunity | [score.components.opportunity] |

**3. Modifier Factors Analysis**
*   **Applied Modifier Factors:**

| Factor Name | Value/Description | Reason/Insight |
| :--- | :--- | :--- |
| [modifiers_applied[0].name] | [modifiers_applied[0].value] | [modifiers_applied[0].reason] |
| ... | ... | ... |
*(Listing all applied modifier factors)*

**4. Overall Recommendations**
*   [insights.summary]
*   [recommendation]
*   (If `insights` includes a `recommendations` list, list them here)

**5. Attached Visualizations**
*   4-Dimension Radar Chart (radar_chart.png)
*   Modifier Waterfall Chart (waterfall_chart.png)
*   Price Segment Chart (price_segment.png)
*   Comparison Matrix Chart (comparison.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| 4-Dimension Radar | Demand/Competition/Profit/Opportunity | `radar_chart.png` |
| Modifier Waterfall | Score buildup visualization | `waterfall_chart.png` |
| Price Segment | Price distribution | `price_segment.png` |
| Comparison Matrix | Multi-niche comparison | `comparison.png` |

## Workflow Integration

```
📈 Discovery Phase
├── trend-discovery → Find trending categories
├── market-overview → Understand the market
└── niche-evaluator → Evaluate niche potential ← YOU ARE HERE
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- Manual tags require human judgment
- Some modifiers need Keepa data (may not be available)
- Score is relative, not absolute
- Does not account for seller-specific capabilities
- Historical data limited to API availability

## References

- `references/scoring-methodology.md` — Detailed scoring logic
- `references/display-rules.md` — Chart styling guidelines
