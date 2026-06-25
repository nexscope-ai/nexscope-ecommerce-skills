---
name: keyword-rank-tracker
version: 2.0.0
description: |
  Track Amazon keyword ranking positions for a specific ASIN and keyword set. Triggers: keyword rank, ASIN position, ranking changes, where does my product rank. Use for current/ranking changes, not keyword discovery or reverse ASIN lookup.
allowed-tools:
 - Bash
 - Read
 - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Keyword Rank Tracker v2.0.0

## Core Question

Where does this ASIN rank for the target keywords, and how are rankings changing?

**How are my keyword rankings?**

## Clarify or Infer Before Querying

- If ASIN is missing, ask for it or use a relevant product search skill first.
- If keywords are missing, ask for the target keyword list or use keyword-reverse-lookup/keyword-research to generate candidates.
- Clarify marketplace and whether the user wants current rank or rank-change tracking.

## When to Use
- User wants to check keyword rankings
- User asks "what keywords am I ranking for"
- User wants to analyze traffic sources
- User asks about keyword performance
- User wants to find ranking opportunities

## Differs From / Not Applicable

- Use keyword-reverse-lookup to discover which keywords an ASIN ranks for.
- Use keyword-priority-ranker to prioritize a keyword list by opportunity.
- Use this skill only when an ASIN and target keywords/ranking question are known.

## Workflow

1. Confirm ASIN, keywords, and marketplace.
2. Query rank positions for the target ASIN and keyword set.
3. Compare positions across keywords or time if data is available.
4. Return ranking table, weak keywords, and action recommendations.

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/by-asin` | keyword rankings, search volume, monthly trend for tracked ASINs |

## Supported Marketplaces

US, CA, MX, UK, DE, FR, IT, ES, JP, IN, AU, BR, NL, SE, PL, TR, AE, SA, SG


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic rank tracking
python3 scripts/keyword_rank_tracker.py '{"asin": "B0BTYCRJSS"}'

# Specific market
python3 scripts/keyword_rank_tracker.py '{"asin": "B0BTYCRJSS", "market": "DE"}'

# With filter conditions
python3 scripts/keyword_rank_tracker.py '{"asin": "B0BTYCRJSS", "conditions": {"isPurchaseKw": true}}'

# With charts
python3 scripts/keyword_rank_tracker.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `asin` | string | Yes | - | Amazon ASIN to track |
| `market` | string | No | | Marketplace code |
| `conditions` | string | No | - | Filter conditions (comma-separated) |
| `limit` | int | No | 100 | Max keywords to fetch |

### Filter Conditions

| Condition | Description |
|-----------|-------------|
| `nfPosition` | Natural traffic keywords |
| `isSpAd` | SP ad keywords |
| `isBrandAd` | Brand ad keywords |
| `isAC` | Amazon's Choice keywords |
| `isMainKw` | Main traffic keywords |
| `isPurchaseKw` | Keywords generating orders |
| `isQualityKw` | High conversion keywords |
| `isLossKw` | Conversion loss keywords |

## Output Structure

The output will be a structured markdown report, following this format:

**Keyword Ranking Tracking Report: [ASIN]**

---

**1. Executive Summary**
*   **Analyzed ASIN:** [asin]
*   **Analysis Market:** [market]
*   **Total Keywords Tracked:** [total_keywords]
*   **Page 1 (Top 10) Keywords:** [analysis.rank_distribution.page1]
*   **Core Insight:** [insights.summary]

**2. Keyword Ranking Overview**
*   **Ranking Distribution:**

| Rank Range | Count | Percentage |
| :--- | :--- | :--- |
| Top 3 | [analysis.rank_distribution.top3] | [analysis.rank_distribution.top3_percentage]% |
| Page 1 (4-10) | [analysis.rank_distribution.page1] | [analysis.rank_distribution.page1_percentage]% |
| Page 2 (11-20) | [analysis.rank_distribution.page2] | [analysis.rank_distribution.page2_percentage]% |
| Page 3-5 (21-50) | [analysis.rank_distribution.page3_5] | [analysis.rank_distribution.page3_5_percentage]% |
| Beyond Page 5 | [analysis.rank_distribution.beyond] | [analysis.rank_distribution.beyond_percentage]% |
| Unranked | [analysis.rank_distribution.unranked] | [analysis.rank_distribution.unranked_percentage]% |

*   **Keyword Type Distribution:**

| Type | Count |
| :--- | :--- |
| HEAD (Short-tail) | [analysis.keyword_types.HEAD] |
| BODY (Mid-tail) | [analysis.keyword_types.BODY] |
| LONG_TAIL (Long-tail) | [analysis.keyword_types.LONG_TAIL] |

*   **Traffic Type:**
    *   Organic Traffic Keywords: [analysis.position_types.organic]
    *   Sponsored Traffic Keywords: [analysis.position_types.sponsored]
    *   Keywords with Both Organic and Sponsored Ranks: [analysis.position_types.both]

*   **Search Volume Statistics:**
    *   Total Monthly Search Volume: [analysis.search_volume_stats.total_monthly]
    *   Average Monthly Search Volume: [analysis.search_volume_stats.avg_monthly]
    *   Maximum Monthly Search Volume: [analysis.search_volume_stats.max_monthly]
    *   Estimated Total Traffic: [analysis.estimated_total_traffic]

**3. Top Traffic Keywords**
*   **Keywords Ranked by Estimated Traffic (Showing Top 5):**

| Keyword | Estimated Traffic | Organic Rank | Monthly Search Volume |
| :--- | :--- | :--- | :--- |
| [analysis.top_traffic_keywords[0].keyword] | [analysis.top_traffic_keywords[0].estimated_traffic] | [analysis.top_traffic_keywords[0].organic_rank] | [analysis.top_traffic_keywords[0].monthly_search] |
| ... | ... | ... | ... |

**4. Opportunities & Recommendations**
*   **High Potential Keywords:**

| Keyword | Monthly Search Volume | Current Rank | Potential |
| :--- | :--- | :--- | :--- |
| [opportunities.high_potential[0].keyword] | [opportunities.high_potential[0].monthly_search] | [opportunities.high_potential[0].current_rank] | [opportunities.high_potential[0].potential] |
| ... | ... | ... | ... |

*   **Quick Wins:** [Keywords from opportunities.quick_wins]
*   **Keywords to Defend:** [Keywords from opportunities.defend]
*   **Trending Keywords:** [Keywords from opportunities.trending]
*   **Action Recommendations:**
    *   [First recommendation from `insights.recommendations`]
    *   [Second recommendation from `insights.recommendations`]
    *   ...

**5. Attached Visualizations**
*   Rank Distribution (1_rank_distribution.png)
*   Top Traffic Keywords (2_top_traffic.png)
*   Position Types (3_position_types.png)
*   Keyword Types (4_keyword_types.png)

## Rank Tiers

| Tier | Rank Range | Icon |
|------|------------|------|
| Top 3 | 1-3 | 🥇 |
| Page 1 | 4-10 | 🟢 |
| Page 2 | 11-20 | 🟡 |
| Page 3-5 | 21-50 | 🟠 |
| Beyond P5 | 51+ | 🔴 |
| Unranked | No rank | ⚪ |

## Position Types

| Type | Description | Icon |
|------|-------------|------|
| natural | Organic search result | 🔵 |
| sp | Sponsored Products ad | 🟢 |
| ac | Amazons Choice | 3 keywords |

**Top Keywords:**
| Keyword | Rank | Search/Week | Traffic |
|---------|------|-------------|---------|
| wireless earbuds | #2 | 114,175 | 16.1% |
| earbuds | #1 | 139,290 | 9.7% |
| bluetooth headphones | #12 | 138,309 | 4.7% |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Rank Distribution | Keyword rank position histogram | `1_rank_distribution.png` |
| Top Traffic Keywords | Estimated traffic by keyword | `2_top_traffic.png` |
| Position Types | Organic vs sponsored breakdown | `3_position_types.png` |
| Keyword Types | Keyword category distribution | `4_keyword_types.png` |

## Limitations

- Data reflects current snapshot (not historical trends)
- Weekly search volume is estimated
- Traffic share is approximate
- Some keywords may not have rank data
- API costs ~1000 tokens per 100 keywords


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
python3 scripts/keyword_rank_tracker.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/keyword_rank_tracker.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/keyword_rank_tracker.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
