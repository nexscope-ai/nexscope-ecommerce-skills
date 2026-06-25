---
name: keyword-research
version: 1.0.0
description: |
  Expand a seed keyword into related terms, long-tail variations, and trends. Triggers: keyword ideas, related keywords, long-tail, expand keywords. Use for broad expansion, not opportunity scoring, priority ranking, or ASIN reverse lookup.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Keyword Research v1.0.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**What other keywords can I target?**

Discover and expand keyword opportunities from a seed keyword.

## Core Question

> — What other keywords should I target?

## When to Use

- Expanding keyword list from initial seed
- Finding related keyword opportunities
- Discovering trending keywords
- Identifying hidden gem keywords with low competition

## Differs From / Not Applicable

- Use keyword-opportunity-finder to score low-competition/high-volume gaps.
- Use keyword-reverse-lookup for competitor ASIN keywords.
- Use keyword-priority-ranker to rank an existing keyword list.
- Use this skill for broad expansion and long-tail discovery.

## Data Source

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Related keywords, volume, trends, difficulty |

## Analysis Dimensions

| Dimension | Description |
|-----------|-------------|
| **Related Keywords** | Semantically related search terms |
| **Search Volume** | Monthly exact/broad match volume |
| **Trend Direction** | Growing or declining keywords |
| **Competition Level** | Ease of ranking + product count |
| **PPC Cost** | Advertising cost indicators |
| **Opportunity Score** | Volume × Ease / Competition |

## Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| Search Volume | Monthly exact searches | > 1,000 |
| Ease of Ranking | JS score 0-100 | > 70 |
| Monthly Trend | % change month-over-month | > 0% |
| Relevancy Score | How related to seed | > 70 |
| Organic Products | Competition count | < 500 |

## Keyword Categories

| Category | Characteristics | Strategy |
|----------|-----------------|----------|
| 🔥 **HOT_OPPORTUNITY** | High volume + Easy + Trending up | Priority target |
| 💎 **HIDDEN_GEM** | Medium volume + Very easy + Low competition | Quick wins |
| 📈 **RISING_STAR** | Strong positive trend (>15%) | Future investment |
| ⚠️ **COMPETITIVE** | High volume + Hard to rank | Requires resources |
| 📉 **DECLINING** | Negative trend (<-15%) | Avoid or monitor |
| 📊 **STANDARD** | Normal opportunity | Evaluate case by case |

## Opportunity Score Formula

```
Score = (Volume × Ease × Trend_Boost) / Competition_Factor

Where:
- Trend_Boost = 1 + max(0, trend% / 100)
- Competition_Factor = max(1, organic_products / 100)
```


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic keyword expansion
python3 scripts/keyword_research.py '{"keyword": "face wash"}'

# With minimum volume filter
python3 scripts/keyword_research.py '{"keyword": "yoga mat", "min_volume": 1000}'

# Different market
python3 scripts/keyword_research.py '{"keyword": "face wash", "market": "UK"}'

# With chart output
python3 scripts/keyword_research.py '{"keyword": "face wash"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | required | Seed keyword to expand |
| `market` | string | | Marketplace (US/UK/DE/FR/CA/JP) |
| `min_volume` | int | 100 | Minimum search volume filter |

## Output Structure

The output will be a structured markdown report, following this format:

**Keyword Research Report: [Seed Keyword]**

---

**1. Executive Summary**
*   **Seed Keyword:** [seed_keyword]
*   **Analysis Market:** [market]
*   **Analysis Date:** [analysis_date]
*   **Data Source:** [data_source]
*   **Total Keywords Found:** [analysis.total]
*   **Core Insight:** [insights.summary]

**2. Keyword Analysis Overview**
*   **Keyword Relationship Distribution:**

| Relationship Type | Count |
| :--- | :--- |
| SEED | [analysis.by_relationship.SEED] |
| EXPANSION | [analysis.by_relationship.EXPANSION] |
| RELATED | [analysis.by_relationship.RELATED] |
| ADJACENT | [analysis.by_relationship.ADJACENT] |

*   **Keyword Category Distribution:**

| Category | Count |
| :--- | :--- |
| 💎 Hidden Gem | [analysis.by_category.💎 Hidden Gem] |
| 📊 Standard | [analysis.by_category.📊 Standard] |
| 📈 Rising Star | [analysis.by_category.📈 Rising Star] |
| ⚠️ Competitive | [analysis.by_category.⚠️ Competitive] |

*   **Trend Distribution:**

| Trend | Count |
| :--- | :--- |
| Growing (GROWING) | [analysis.by_trend.GROWING] |
| Flat (FLAT) | [analysis.by_trend.FLAT] |
| Declining (DECLINING) | [analysis.by_trend.DECLINING] |

*   **Search Volume Statistics:**
    *   Total Monthly Search Volume: [analysis.volume_stats.total]
    *   Average Monthly Search Volume: [analysis.volume_stats.avg]
    *   Maximum Monthly Search Volume: [analysis.volume_stats.max]

**3. Top Keyword Opportunities**
*   **Keywords Ranked by Opportunity Score (Showing Top 10):**

| Keyword | Monthly Volume | Trend | Relationship | Category | Opportunity Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [analysis.top_keywords[0].keyword] | [analysis.top_keywords[0].monthly_volume] | [analysis.top_keywords[0].trend] | [analysis.top_keywords[0].relationship] | [analysis.top_keywords[0].category] | [analysis.top_keywords[0].opportunity_score] |
| ... | ... | ... | ... | ... | ... |

**4. Actionable Recommendations**
*   [First recommendation from `insights.insights`]
*   [Second recommendation from `insights.insights`]
*   ... (Listing all key recommendations)

**5. Attached Visualizations**
*   Opportunity Matrix Chart (1_opportunity_matrix.png)
*   Category Distribution Chart (2_category_distribution.png)
*   Volume Distribution Chart (3_volume_distribution.png)
*   Top Opportunities Chart (4_top_opportunities.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Opportunity Matrix | Volume vs Ease scatter | `1_opportunity_matrix.png` |
| Category Distribution | Keyword categories bar | `2_category_distribution.png` |
| Volume Distribution | High/Medium/Low bar | `3_volume_distribution.png` |
| Top Opportunities | Ranked by score | `4_top_opportunities.png` |

## Insights Generated

| Insight | Trigger |
|---------|---------|
| Excellent Market | >= 5 hot opportunities |
| Good Potential | >= 5 hidden gems |
| Growing Market | >= 5 rising stars |
| Easy Market | Avg ease score >= 80 |
| Competitive Market | Avg ease score < 50 |
| Top Opportunity | Highest scoring keyword |
| Fastest Growing | Highest trend % keyword |
| Declining Warning | > 3 declining keywords |

## Recommendations

| Situation | Recommendation |
|-----------|----------------|
| Hot opportunities exist | Target immediately |
| Many hidden gems | Capture for easy rankings |
| Rising stars found | Invest early |
| High PPC market | Focus on organic ranking |
| Many declining | Consider different niche |

## Workflow Integration

```
1️⃣ keyword-reverse-lookup → What competitors rank for
2️⃣ keyword-research → Expand with related keywords ← YOU ARE HERE
3️⃣ keyword-priority-ranker → Prioritize targeting order
```

## Limitations

- API returns max ~50 keywords per query
- Requires NexScope Proxy API access (Jungle Scout via proxy)
- Trend data may have 1-2 week lag


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/keyword_research.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/keyword_research.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/keyword_research.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
