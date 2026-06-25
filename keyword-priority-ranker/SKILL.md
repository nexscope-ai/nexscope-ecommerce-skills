---
name: keyword-priority-ranker
version: 1.0.0
description: |
  Prioritize an existing keyword list by ROI/opportunity. Triggers: which keywords first, keyword priority, target order, rank my keyword list. Use when keywords already exist; use opportunity-finder to discover new gaps.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Keyword Priority Ranker v1.0.0

## Category / Market Understanding Step

Before running this skill, if the user provides a broad product category, niche, keyword, market idea, or trend topic, first identify:

- category or niche
- target marketplace, country, or platform
- user's analysis goal
- relevant seed keywords or subcategories
- whether the request is about demand, competition, trend, opportunity, or prioritization

Use this market understanding to choose keywords, filters, regions, comparison scope, and analysis dimensions before executing the script.

**Which keywords should I target first?**

Rank and prioritize keywords by actionable opportunity score.

## Core Question

> — Which keywords should I target first?

## When to Use

- After keyword research to decide targeting order
- Planning keyword strategy for new product launch
- Allocating PPC budget across keywords
- Building content/SEO roadmap

## Differs From / Not Applicable

- Use keyword-opportunity-finder to discover new keyword gaps.
- Use keyword-research to expand a seed keyword.
- Use keyword-rank-tracker to check current ASIN ranking positions.
- Use this skill when the user asks which known keywords to target first.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Keyword expansion, volume, difficulty |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-asin` | Current rankings (if ASIN provided) |

## Priority Score Formula

| Factor | Weight | Description |
|--------|--------|-------------|
| **Volume** | 25% | Search volume potential (normalized) |
| **Ease** | 25% | Ease of ranking (0-100 from API) |
| **Relevancy** | 15% | How relevant to your product |
| **Trend** | 15% | Growth momentum (centered at 50) |
| **PPC Value** | 10% | Higher PPC = more organic value |
| **Competition** | 10% | Fewer competitors = higher score |

```
Priority Score = Σ (Factor × Weight)
```

## Priority Tiers

| Tier | Score | Label | Action |
|------|-------|-------|--------|
| **P0** | 80-100 | 🥇 NOW | Attack immediately |
| **P1** | 60-79 | 🥈 SOON | Target within 2 weeks |
| **P2** | 40-59 | 🥉 LATER | Add to backlog |
| **P3** | 20-39 | ⏸️ HOLD | Monitor only |
| **SKIP** | <20 | ❌ SKIP | Don't waste resources |

## Strategy Types

| Strategy | Characteristics | When to Use |
|----------|-----------------|-------------|
| **QUICK_WIN** | High ease + Medium volume | Build momentum fast |
| **BIG_BET** | High volume + Moderate ease | Investment for traffic |
| **LONG_TAIL** | High relevancy + Low competition | Conversion focus |
| **DEFEND** | Already ranking well | Protect position |
| **BRAND_TERM** | Contains brand names | Strategic decision |
| **COMPETITIVE** | Low ease score | Requires resources |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# From seed keyword
python3 scripts/keyword_priority_ranker.py '{"keyword": "face wash"}'

# From ASIN (includes current rankings)
python3 scripts/keyword_priority_ranker.py '{"asin": "B07RL88DD2"}'

# Combined (seed + current rankings)
python3 scripts/keyword_priority_ranker.py '{"keyword": "face wash", "asin": "B07RL88DD2"}'

# With custom weights
python3 scripts/keyword_priority_ranker.py '{"keyword": "face wash", "volume_weight": 0.4}'

# With minimum volume
python3 scripts/keyword_priority_ranker.py '{"keyword": "face wash", "min_volume": 500}'

# With chart output
python3 scripts/keyword_priority_ranker.py '{"keyword": "face wash"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | - | Seed keyword for expansion |
| `asin` | string | - | ASIN for current rankings |
| `market` | string | | Marketplace |
| `min_volume` | int | 100 | Minimum search volume |
| `volume_weight` | float | 0.25 | Custom weight for volume |
| `ease_weight` | float | 0.25 | Custom weight for ease |
| `relevancy_weight` | float | 0.15 | Custom weight for relevancy |
| `trend_weight` | float | 0.15 | Custom weight for trend |
| `ppc_value_weight` | float | 0.10 | Custom weight for PPC value |
| `competition_weight` | float | 0.10 | Custom weight for competition |

## Output Structure

The output will be a structured markdown report, following this format:

**Keyword Priority Ranking Report**

---

**1. Executive Summary**
*   **Total Keywords Analyzed:** [total_keywords]
*   **Average Priority Score:** [avg_priority_score]
*   **P0 (Act Now) Keywords:** [tier_distribution.P0_now]
*   **Core Insight:** [insights.summary]

**2. Priority Tier Distribution**
*   **Keywords by Priority:**

| Priority | Label | Count |
| :--- | :--- | :--- |
| P0 (80-100) | 🥇 Act Now (NOW) | [tier_distribution.P0_now] |
| P1 (60-79) | 🥈 Soon (SOON) | [tier_distribution.P1_soon] |
| P2 (40-59) | 🥉 Later (LATER) | [tier_distribution.P2_later] |
| P3 (20-39) | ⏸️ Hold (HOLD) | [tier_distribution.P3_hold] |
| SKIP (<20) | ❌ Skip (SKIP) | [tier_distribution.skip] |

**3. Strategy Type Distribution**
*   **Keywords by Strategy Type:**

| Strategy Type | Count |
| :--- | :--- |
| Brand Term (BRAND_TERM) | [strategy_distribution.BRAND_TERM] |
| Quick Win (QUICK_WIN) | [strategy_distribution.QUICK_WIN] |
| (Other strategies, if any) | |

**4. Top Priority Keywords**
*   **P0 - Act Now Keywords (Showing all, or limited if too many):**

| Keyword | Priority Score | Priority | Strategy | Exact Search Volume |
| :--- | :--- | :--- | :--- | :--- |
| [p0_keywords[0].keyword] | [p0_keywords[0].priority_score] | [p0_keywords[0].tier_label] | [p0_keywords[0].strategy] | [p0_keywords[0].search_volume_exact] |
| ... | ... | ... | ... | ... |

*   **P1 - Act Soon Keywords (Showing Top 5):**

| Keyword | Priority Score | Priority | Strategy | Exact Search Volume |
| :--- | :--- | :--- | :--- | :--- |
| [p1_keywords[0].keyword] | [p1_keywords[0].priority_score] | [p1_keywords[0].tier_label] | [p1_keywords[0].strategy] | [p1_keywords[0].search_volume_exact] |
| ... | ... | ... | ... | ... |

**5. Action Plan & Recommendations**
*   **Action Plan:**
    *   [First recommendation from `insights.action_plan`]
    *   [Second recommendation from `insights.action_plan`]
    *   ...
*   **Recommended Optimization Sequence:**
    *   [insights.recommended_sequence[0]]
    *   [insights.recommended_sequence[1]]
    *   [insights.recommended_sequence[2]]
    *   [insights.recommended_sequence[3]]
*   **Warnings/Notes:**
    *   [Any warnings from `insights.warnings`]

**6. Attached Visualizations**
*   Tier Distribution Chart (1_tier_distribution.png)
*   Strategy Mix Chart (2_strategy_mix.png)
*   Top Priority Keywords Chart (3_top_priority.png)
*   Priority Matrix Chart (4_priority_matrix.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Tier Distribution | P0/P1/P2/P3/SKIP pie | `1_tier_distribution.png` |
| Strategy Mix | Quick Win/Big Bet/etc bar | `2_strategy_mix.png` |
| Top Priority | Ranked keywords bar | `3_top_priority.png` |
| Priority Matrix | Volume vs Score scatter | `4_priority_matrix.png` |

## Insights Generated

| Insight | Trigger |
|---------|---------|
| Excellent | >= 10 P0 keywords |
| Good Opportunity | >= 5 P0 keywords |
| Needs Research | 0 P0 keywords |
| Quick Wins Available | > 0 QUICK_WIN strategy |
| Big Bets Found | > 0 BIG_BET strategy |
| Long-tail Focus | > 0 LONG_TAIL strategy |
| Competitive Warning | > 30% competitive keywords |
| Low Quality Keywords | > 20% SKIP tier |

## Recommended Sequence

1. **Quick Wins** — Build momentum with easy rankings
2. **Defend** — Protect existing good rankings
3. **Big Bets** — Invest resources for high-volume keywords
4. **Long-tail** — Focus on conversion keywords

## Workflow Integration

```
1️⃣ keyword-reverse-lookup → What competitors rank for
2️⃣ keyword-research → Expand with related keywords
3️⃣ keyword-priority-ranker → Prioritize targeting order ← YOU ARE HERE
```

## Limitations

- Score is relative within the keyword set
- Weights can be customized but sum should equal 1.0
- Requires NexScope Proxy API access (Jungle Scout via proxy)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines
