---
name: keyword-opportunity-finder
version: 1.4.0
description: |
  Find high-volume low-competition keyword gaps. Triggers: blue ocean keywords, low competition, opportunity keywords. Use for keyword gaps, not broad expansion; use keyword-research for expansion and reverse-lookup for ASIN keywords.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Keyword Opportunity Finder v1.4.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**What keywords have high volume but low competition?**

Find blue ocean keywords with high search volume and low competition.

## Core Question

> — Which keywords have high volume but low competition?

## When to Use

- Building keyword strategy for a new product
- Finding gaps in competitor keyword coverage
- Identifying long-tail opportunities
- Discovering trending keywords early

## Differs From / Not Applicable

- Use keyword-research to expand from a seed keyword.
- Use keyword-reverse-lookup to discover keywords from a competitor ASIN.
- Use keyword-priority-ranker when the user already has a keyword list.
- Use this skill for high-volume, low-competition keyword gaps.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Related keywords, volume, difficulty |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/historical-search-volume` (POST) | 30/90/180-day trend data |
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Competition density, product count |

## Scoring Dimensions

| Dimension | Weight | Metrics |
|-----------|--------|---------|
| 📈 **Volume** | 35% | 12-month avg + growth trend |
| ⚔️ **Difficulty** | 30% | Product count + Top 3 click share + reviews |
| 💰 **Efficiency** | 20% | Conversion rate + PPC cost |
| 🎯 **Relevance** | 15% | Avg price + repurchase potential |

## Opportunity Patterns

| Pattern | Detection | Action |
|---------|-----------|--------|
| 🔥 **Rising Trend** | 30-day surge >50% | Capture early |
| 💎 **High-Conv Longtail** | Conv share >60% | Priority target |
| 🛡️ **Under-optimized** | 30%+ weak listings | Easy wins |
| 📱 **Social Signal** | TikTok/Reddit viral | Time-sensitive |

## Red Flags

| Flag | Description |
|------|-------------|
| ⚠️ Amazon Dominance | Amazon brand owns top spots |
| ⚠️ Brand Wall | >80% known brands |
| ⚠️ Review Fortress | >2000 avg reviews |
| ⚠️ Trademark Risk | Brand name in keyword |
| ⚠️ Dying Market | Declining trend |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Find keyword opportunities
python3 scripts/keyword_opportunity_finder.py '{"keyword": "yoga mat"}'

# With minimum volume
python3 scripts/keyword_opportunity_finder.py '{"keyword": "face wash", "min_volume": 1000}'

# Focus on long-tail
python3 scripts/keyword_opportunity_finder.py '{"keyword": "yoga mat", "max_competition": 500}'

# With chart output
python3 scripts/keyword_opportunity_finder.py '{"keyword": "kombucha"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Starting keyword |
| `marketplace` | string | `us` | Target marketplace (us, uk, de, etc.) |
| `min_volume` | int | 500 | Minimum monthly volume |
| `max_competition` | int | - | Maximum product count |
| `include_trends` | bool | true | Include trend analysis |

## Output Structure

The output will be a structured markdown report, following this format:

**Keyword Opportunity Discovery Report: [Seed Keyword]**

---

**1. Executive Summary**
*   **Seed Keyword:** [seed_keyword]
*   **Analysis Marketplace:** [marketplace]
*   **Total Keywords Found:** [summary.total_keywords]
*   **Number of Blue Ocean Keywords:** [summary.blue_ocean_keywords]
*   **Core Insight:** [insights.summary]

**2. Keyword Opportunity Overview**
*   **Keyword Discovery Statistics:**
    *   High Volume Keywords: [insights.high_volume_count]
    *   Low Difficulty Keywords: [insights.low_difficulty_count]
    *   Trending Keywords: [insights.trending_count]
*   **Identified Patterns:**

| Pattern | Count |
| :--- | :--- |
| Rising Trend (RISING_TREND) | [insights.patterns_found.RISING_TREND] |
| High Conversion Long-tail (HIGH_CONV_LONGTAIL) | [insights.patterns_found.HIGH_CONV_LONGTAIL] |
| Under-optimized (UNDER_OPTIMIZED) | [insights.patterns_found.UNDER_OPTIMIZED] |
| (Other patterns, if any) | |

**3. Top Keyword Opportunities**
*   **Keywords ranked by total score (Showing Top 10 Blue Ocean or Highest Scoring Keywords):**

| Rank | Keyword | Exact Volume | Broad Volume | Difficulty | PPC Bid (Exact) | Monthly Trend | Trend Direction | Total Score | Blue Ocean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [keywords[0].keyword] | [keywords[0].exact_volume] | [keywords[0].broad_volume] | [keywords[0].keyword_difficulty] | [keywords[0].ppc_bid_exact] | [keywords[0].monthly_trend]% | [keywords[0].trend_direction] | [keywords[0].score.total_score] | [keywords[0].is_blue_ocean] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**4. Actionable Recommendations**
*   [First recommendation from `insights.recommendations`]
*   [Second recommendation from `insights.recommendations`]
*   ... (Listing all key recommendations)

**5. Attached Visualizations**
*   Keyword Radar Chart (keyword_radar.png)
*   Keyword Scores Chart (keyword_scores.png)
*   Volume vs Difficulty Scatter Plot (volume_difficulty.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Keyword Radar | Multi-dimension keyword score visualization | `keyword_radar.png` |
| Keyword Scores | Top keywords ranked by score | `keyword_scores.png` |
| Volume vs Difficulty | Search volume vs competition scatter | `volume_difficulty.png` |

## Workflow Integration

```
🔑 Keyword Phase
├── keyword-reverse-lookup → What competitors rank for
├── keyword-research → Expand keyword list
├── keyword-opportunity-finder → Find low-competition keywords ← YOU ARE HERE
└── keyword-priority-ranker → Prioritize targeting order
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## Limitations

- Requires live keyword API data; if the API is unavailable or returns no keyword records, the script fails instead of generating mock opportunities.
- Volume data has 1-2 week lag
- Competition density is point-in-time
- Trend detection requires sufficient history
- Social signals require manual verification
- Red flags are heuristic-based

## References

- `references/visualization.md` — Chart specifications
- `references/display-rules.md` — Chart styling guidelines
