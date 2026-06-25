---
name: design-patent-analyzer
version: 1.0.0
description: |
  Check visual/design patent similarity from product images. Triggers: design infringement, look-alike patent, visual similarity, design clearance. Use for appearance/design risk, not utility claims or legal-status checks.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Design Patent Analyzer v1.0.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Does this design have conflicts?**

Design patent similarity analysis using dual-model image search against 170M+ patents.

## Core Question

> — Does this design have patent conflicts?
> — Is my product design safe to launch?

## When to Use

- Before finalizing product design — check for conflicts early
- Before mold production — expensive to change later
- When copying competitor designs — know the risks
- For design registration — ensure novelty

## Differs From / Not Applicable

- Use patent-risk-checker for broader product-level IP/FTO risk screening.
- Use patent-claim-analyzer for interpreting a known patent claim.
- Use patent-legal-status for validity/expiration questions.
- Use this skill when visual/design similarity is the main concern.

## Workflow

1. Understand product appearance and target countries.
2. Run design/appearance patent similarity search from the image.
3. Rank similar designs by visual similarity and legal relevance.
4. Return risk level, closest matches, and next legal-review steps.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (model=1) | Smart association — similar designs by appearance |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (model=2) | Exact match — shape and pattern-based matches |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/legalStatus` | Legal status and litigation events |

**Coverage**: 170M+ patents from 150+ countries. Full Locarno classification (LOC) support.


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic search
python3 scripts/design_patent_analyzer.py '{"imageUrl": "https://example.com/product.jpg"}'

# With region filter
python3 scripts/design_patent_analyzer.py '{"imageUrl": "https://example.com/product.jpg", "countries": "US,CN,EU"}'

# Generate charts
python3 scripts/design_patent_analyzer.py '{"imageUrl": "..."}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `imageUrl` | string | Yes | - | Product image URL |
| `countries` | string | No | all | Country filter (e.g., "US,CN,EU") |
| `limit` | int | No | 30 | Max patents per model |
| `activeOnly` | bool | No | true | Only active patents |

## Output Structure

The output will be a structured markdown report, following this format:

**Product Design Patent Analysis Report**

---

**1. Executive Summary**
*   **Analysis Date:** [analysis_date]
*   **Data Source:** [data_source]
*   **Input Image:** [input.image_url] (Analyzed Countries: [input.countries], Active Patents Only: [input.active_only])
*   **Conflict Level:** [conflict_summary.emoji] [conflict_summary.level] (Highest Similarity: [conflict_summary.max_similarity_pct])
*   **Core Recommendation:** [conflict_summary.recommendation]
*   **Total Patents Found:** [conflict_summary.total_patents_found]

**2. Similarity Model Comparison**
*   **Similar Patents Found by Different Models:**

| Model | Count Found | Total in Database | Highest Similarity |
| :--- | :--- | :--- | :--- |
| Smart Association | [model_comparison.smart_association.count] | [model_comparison.smart_association.total_in_db] | [model_comparison.smart_association.max_similarity] |
| Exact Match | [model_comparison.exact_match.count] | [model_comparison.exact_match.total_in_db] | [model_comparison.exact_match.max_similarity] |

**3. Conflict Summary**
*   **Conflict Level Distribution:**

| Level | Count |
| :--- | :--- |
| Likely Conflict | [conflict_summary.conflict_counts.likely] |
| High Similarity | [conflict_summary.conflict_counts.high] |
| Potential Conflict | [conflict_summary.conflict_counts.potential] |
| None | [conflict_summary.conflict_counts.none] |

**4. Top Similar Patents Found**
*   **List of Patents Ranked by Similarity (Showing Top 5):**

| Patent Number | Similarity | Title | Assignee | Filing Date | Status | Patent Image |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [top_conflicts[0].patent_number] | [top_conflicts[0].similarity] | [top_conflicts[0].title] | [top_conflicts[0].assignee] | [top_conflicts[0].filing_date] | [top_conflicts[0].status] | [top_conflicts[0].image_url] |
| ... | ... | ... | ... | ... | ... | ... |

**5. Locarno Classification Analysis**
*   **Predicted Product Classification:** [loc_analysis.predicted_product_loc]
*   **Total LOC Matches:** [loc_analysis.total_loc_matches]
*   **Unique Classifications:** [loc_analysis.unique_classifications]
*   **Top Classifications:**
    *   [loc_analysis.top_classifications[0].loc] (Count: [loc_analysis.top_classifications[0].count])
    *   ...

**6. Assignee Analysis**
*   **Unique Assignees:** [assignee_analysis.unique_assignees]
*   **Top Assignees (Showing Top 3):**

| Assignee Name | Patent Count | Highest Similarity |
| :--- | :--- | :--- |
| [assignee_analysis.top_assignees[0].name] | [assignee_analysis.top_assignees[0].patent_count] | [assignee_analysis.top_assignees[0].max_similarity] |
| ... | ... | ... |

**7. Attached Visualizations**
*   Similarity Gauge (1_conflict_gauge.png)
*   Model Comparison (2_model_comparison.png)
*   Top Conflicts Distribution (3_top_conflicts.png)
*   Assignee Map (4_assignees.png)
*   Conflict Level Distribution (5_distribution.png)

## Conflict Levels

| Level | Similarity | Action |
|-------|-----------|--------|
| 🟢 NO_CONFLICT | < 50% | Design appears novel — safe to proceed |
| 🟡 POTENTIAL | 50–70% | Review specific features, consider modifications |
| 🟠 HIGH_SIMILARITY | 70–85% | Significant redesign recommended |
| 🔴 LIKELY_CONFLICT | ≥ 85% | Abandon this design direction |

## LOC Classification

Locarno Classification (LOC) categorizes industrial designs:

| Class | Category |
|-------|----------|
| 01 | Foodstuffs |
| 02 | Clothing |
| 06 | Furnishing |
| 07 | Household goods |
| 09 | Packaging |
| 14 | Recording equipment |
| 21 | Games & toys |
| 26 | Lighting |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Similarity Gauge | Overall conflict level | `1_conflict_gauge.png` |
| Model Comparison | Smart vs Exact results | `2_model_comparison.png` |
| Top Conflicts | Similarity distribution | `3_top_conflicts.png` |
| Assignee Map | Top patent holders | `4_assignees.png` |
| Conflict Distribution | Level breakdown pie | `5_distribution.png` |

## Limitations

- Image quality affects search accuracy
- Some newer patents may not be indexed
- Results are advisory, not legal opinions
- Best for product appearance, not functional features


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- Locarno Classification: https://www.wipo.int/classifications/locarno/
