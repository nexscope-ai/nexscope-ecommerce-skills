---
name: keyword-reverse-lookup
version: 1.0.0
description: |
  Find keywords a competitor ASIN ranks for. Triggers: reverse ASIN, competitor keywords, what keywords drive their sales, spy on keywords. Use for ASIN-to-keywords, not seed keyword expansion or rank tracking for your ASIN.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Keyword Reverse Lookup v1.0.0

**What keywords drive sales for competitors?**

Reverse-engineer competitor traffic by finding what keywords they rank for.

## Core Question

> — What keywords are driving competitor sales?

## Clarify or Infer Before Querying

- If ASIN is missing, ask for the competitor ASIN before running.
- Clarify marketplace when not obvious.
- Do not invent ASINs from product names.

## When to Use

- Analyzing competitor keyword strategy
- Finding keywords you might be missing
- Understanding traffic sources for top sellers
- Identifying brand vs generic keyword dependency

## Differs From / Not Applicable

- Use keyword-research for seed keyword expansion.
- Use keyword-rank-tracker to check rank positions for specific keywords.
- Use listing-keyword-optimizer to place keywords into listing copy.
- Use this skill when the input is a competitor ASIN.

## Data Source

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-asin` | Keywords, rankings, volume, trends |

## Analysis Dimensions

| Dimension | Description |
|-----------|-------------|
| **Traffic Keywords** | All keywords the ASIN ranks for |
| **Organic vs Sponsored** | Natural ranking vs paid positioning |
| **Search Volume** | Monthly exact/broad match volume |
| **Ranking Position** | Where competitor ranks (top 10, 50, etc.) |
| **PPC Opportunity** | Keywords with good volume but low competition |
| **Keyword Types** | Brand/Generic/Long-tail classification |

## Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| Keywords Found | Total traffic keywords | > 50 |
| High Volume Keywords | Search > 1,000/mo | > 10 |
| Top 10 Rankings | Organic rank ≤ 10 | > 5 |
| PPC Overlap | Also running ads | % indicates strategy |
| Ease of Ranking | JS score 0-100 | > 70 is easy |

## Keyword Type Classification

| Type | Description | Example |
|------|-------------|---------|
| **BRAND** | Contains brand name | "cerave face wash" |
| **GENERIC** | Category terms (1-3 words) | |
| **LONG_TAIL** | Specific modifiers (4+ words) | |

## Traffic Distribution Analysis

| Pattern | Signal | Implication |
|---------|--------|-------------|
| High Brand % | Brand loyalty | Hard to steal traffic |
| High Generic % | Market reach | Broader opportunity |
| High Long-tail % | Niche targeting | Conversion focused |
| High Sponsored % | PPC dependent | Vulnerable to budget cuts |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Single ASIN lookup
python3 scripts/keyword_reverse_lookup.py '{"asin": "B07RL88DD2"}'

# Multiple ASINs (competitor comparison)
python3 scripts/keyword_reverse_lookup.py '{"asins": ["B07RL88DD2", "B08EXAMPLE"]}'

# With minimum volume filter
python3 scripts/keyword_reverse_lookup.py '{"asin": "B07RL88DD2", "min_volume": 500}'

# With chart output
python3 scripts/keyword_reverse_lookup.py '{"asin": "B07RL88DD2"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asin` | string | required | Single ASIN to analyze |
| `asins` | array | - | Multiple ASINs to compare |
| `market` | string | | Marketplace (US/UK/DE/FR/CA/JP) |
| `min_volume` | int | 100 | Minimum search volume filter |

## Output Structure

The output will be a structured markdown report, following this format:

**Keyword Reverse Lookup Report: [ASIN(s)]**

---

**1. Executive Summary**
*   **Analyzed ASIN(s):** [asin or asins]
*   **Analysis Market:** [market]
*   **Analysis Date:** [analysis_date]
*   **Total Keywords Found:** [total_keywords_found]
*   **Primary Insight:** [summary.insights]

**2. Core ASIN Keyword Overview (If Single ASIN)**
*   **Primary ASIN:** [summary.primary_asin]
*   **Total Keywords:** [summary.total_keywords]
*   **Estimated Monthly Traffic:** [summary.estimated_traffic]
*   **Top 10 Ranked Keywords:** [summary.top_10_rankings]
*   **Organic Traffic Percentage:** [summary.organic_pct]%
*   **Top Keyword Examples:** [summary.top_keywords]

**3. Detailed ASIN Analysis**
*(Detailed analysis for each analyzed ASIN)*

**Target ASIN: [current_asin]**

*   **Total Keywords:** [asin_analyses[current_asin].total_keywords]
*   **Total Search Volume:** [asin_analyses[current_asin].total_search_volume]
*   **Estimated Monthly Traffic:** [asin_analyses[current_asin].estimated_monthly_traffic]
*   **Ranking Distribution:**
    *   Top 10 Keywords: [asin_analyses[current_asin].ranking_distribution.top_10]
    *   Top 20 Keywords: [asin_analyses[current_asin].ranking_distribution.top_20]
    *   Top 50 Keywords: [asin_analyses[current_asin].ranking_distribution.top_50]
    *   Below 50 Keywords: [asin_analyses[current_asin].ranking_distribution.below_50]
*   **Traffic Sources:**
    *   Organic Only Keywords: [asin_analyses[current_asin].traffic_sources.organic_only]
    *   Sponsored Only Keywords: [asin_analyses[current_asin].traffic_sources.sponsored_only]
    *   Both Organic and Sponsored: [asin_analyses[current_asin].traffic_sources.both]
    *   Organic Traffic Percentage: [asin_analyses[current_asin].traffic_sources.organic_pct]%
*   **Keyword Type Distribution:**
    *   Brand Keywords (BRAND): [asin_analyses[current_asin].keyword_types.BRAND]
    *   Generic Keywords (GENERIC): [asin_analyses[current_asin].keyword_types.GENERIC]
    *   Long-Tail Keywords (LONG_TAIL): [asin_analyses[current_asin].keyword_types.LONG_TAIL]
*   **Key Insights:** [asin_analyses[current_asin].insights.summary]
*   **Traffic Level:** [asin_analyses[current_asin].insights.traffic_level]
*   **Assessments:** [asin_analyses[current_asin].insights.assessments]
*   **Recommendations:** [asin_analyses[current_asin].insights.recommendations]

**4. Attached Visualizations**
*   Keyword Type Distribution (1_keyword_types.png)
*   Ranking Distribution (2_ranking_distribution.png)
*   Traffic Sources (3_traffic_sources.png)
*   Top Keywords (4_top_keywords.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Keyword Types | Brand/Generic/Long-tail pie | `1_keyword_types.png` |
| Ranking Distribution | Top 10/20/50/Below bar | `2_ranking_distribution.png` |
| Traffic Sources | Organic/Sponsored pie | `3_traffic_sources.png` |
| Top Keywords | Volume horizontal bar | `4_top_keywords.png` |

## Insights Generated

| Insight | Trigger |
|---------|---------|
| Traffic Level | HIGH/MEDIUM/LOW based on estimate |
| Strong Rankings | > 10 keywords in top 10 |
| Weak Rankings | < 3 keywords in top 10 |
| Brand Dependent | > 30% brand keywords |
| Good Generic Reach | > 40% generic keywords |
| Heavy PPC | > 20% keywords with both organic + ads |
| Opportunity | Target easy-ranking high-volume keywords |

## Workflow Integration

```
1️⃣ keyword-reverse-lookup → What competitors rank for
2️⃣ keyword-research → Expand with related keywords
3️⃣ keyword-priority-ranker → Prioritize targeting order
```

## Limitations

- API returns max 50-100 keywords per ASIN
- Requires NexScope Proxy API access (Jungle Scout via proxy)
- Historical ranking data not available


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines
