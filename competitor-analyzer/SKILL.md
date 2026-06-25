---
name: competitor-analyzer
version: 1.0.0
description: |
  Compare Amazon competitor business metrics: price, reviews, BSR, sales, seller count, traffic. Triggers: competitor metrics, who performs best, price/BSR/review comparison. Use for business performance, not listing copy; use competitor-listing-analyzer for content structure.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Competitor Analyzer v1.0.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Who are the competitors? How do they compare?**

Analyze competitive landscape for Amazon products. Compare competitors on price, reviews, BSR stability, sales momentum, seller count, and API-reported traffic distribution.

## Core Question

> — Who are the competitors and how do they perform?

## When to Use

- Entering a new market and need to understand competition
- Analyzing why certain products outperform others
- Finding gaps in competitor offerings
- Understanding API-reported traffic distribution (organic vs sponsored)
- Comparing competitor price, review, BSR, sales, and seller-count signals

## Differs From / Not Applicable

- Use competitor-listing-analyzer for title, bullets, images, A+ content, and listing quality.
- Use this skill for business performance metrics such as price, reviews, BSR, sales, traffic, and seller count.
- Do not use for keyword placement, review mining, or product validation.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon Search | `/api/v1/tools/linkfox/amazon/search` | Product list, prices, reviews, BSR |
| Keepa | `/api/v1/tools/linkfox/keepa/productRequest` | Product details, monthly sales, seller count |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR history, price history (180-day) |

## Analysis Dimensions

| Dimension | Description |
|-----------|-------------|
| **Market Overview** | Price range, sweet spot, review barrier |
| **Competitive Matrix** | Side-by-side comparison of all competitors |
| **Traffic Distribution** | Organic vs Sponsored positioning when reported by API data |
| **Sales & Stability** | Monthly sales, seller count, BSR trend, price history |
| **Gap Analysis** | Price gaps, feature gaps |
| **Entry Matrix** | Quadrant: Traffic × Competitive strength |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Analyze competitors for a specific ASIN
python3 scripts/competitor_analyzer.py '{"asin": "B0XXXXXXXXX"}'

# Analyze top sellers for a keyword
python3 scripts/competitor_analyzer.py '{"keyword": "dog water fountain"}'

# Compare specific ASINs directly
python3 scripts/competitor_analyzer.py '{"asins": ["B0XXX", "B0YYY"]}'

# Generate visual report
python3 scripts/competitor_analyzer.py '{"keyword": "dog water fountain"}' --report
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asin` | string | - | Target ASIN to find competitors for |
| `keyword` | string | - | Search keyword to analyze market |
| `asins` | array | - | List of ASINs to compare directly |
| `marketplace` | string | | Amazon marketplace |
| `limit` | int | 10 | Number of competitors to analyze |

## Flags

| Flag | Description |
|------|-------------|
| `--report` | Generate visual charts |
| `--chart <dir>` | Generate chart PNG files in the specified directory |

## Output Structure

The output will be a structured markdown report, following this format:

**[Product/Keyword] Competitor Analysis Report**

---

**1. Executive Summary**
*   **Analysis Object:** [keyword or target_asin]
*   **Analysis Market:** [market]
*   **Analysis Date:** [analyzed_at]
*   **Core Insight:** [Summary extracted from gap_analysis and entry_matrix.recommendation]

**2. Market Overview**
*   **Price Analysis:**
    *   Minimum Price: [price_analysis.min]
    *   Maximum Price: [price_analysis.max]
    *   Average Price: [price_analysis.avg]
    *   Median Price: [price_analysis.median]
    *   Price Sweet Spot: [price_analysis.sweet_spot]
*   **Review Analysis:**
    *   Top 3 Average Reviews: [review_analysis.top3_avg]
    *   Top 10 Average Reviews: [review_analysis.top10_avg]
    *   Minimum Reviews: [review_analysis.min]
    *   Maximum Reviews: [review_analysis.max]
    *   Review Barrier Level: [review_analysis.barrier_level]
    *   Review Barrier Assessment: [review_analysis.assessment]
*   **Traffic Distribution:**
    *   Organic Traffic Products: [traffic_analysis.organic_count]
    *   Sponsored Traffic Products: [traffic_analysis.sponsored_count]
    *   Organic Traffic Percentage: [traffic_analysis.organic_pct]%
    *   Sponsored Traffic Percentage: [traffic_analysis.sponsored_pct]%
    *   Traffic Type: [traffic_analysis.traffic_type]

**3. Competitor Details**
*   **Overview of Major Competitors:**

| ASIN | Product Name | Price | Reviews | Rating | BSR | Monthly Sales | Trend | Sponsored |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [competitors[i].asin] | [competitors[i].title] | [competitors[i].price] | [competitors[i].reviews] | [competitors[i].rating] | [competitors[i].bsr] | [competitors[i].monthly_sales] | [competitors[i].trend[0]] ([competitors[i].trend[1]]%) | [competitors[i].sponsored] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
*(Showing all or top N competitors)*

**4. Market Gaps Analysis (Gap Analysis)**
*   **Identified Market Gaps:**
    *   [gap_analysis[0].type]: [gap_analysis[0].detail]
    *   (Listing all identified gaps)

**5. Market Entry Matrix**
*   **Quadrant:** [entry_matrix.quadrant]
*   **Traffic Score:** [entry_matrix.traffic_score]
*   **Competitive Strength Score:** [entry_matrix.competitive_strength_score]
*   **Entry Recommendation:** [entry_matrix.recommendation]

**6. Attached Visualizations**
*   Competitive Positioning (competitive_positioning.png)
*   Price Distribution (price_distribution.png)
*   Market Entry Matrix (entry_matrix.png)

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Competitive Positioning | Price vs Reviews scatter | `competitive_positioning.png` |
| Price Distribution | Price bracket bar chart | `price_distribution.png` |
| Market Entry Matrix | Traffic × Competitive strength quadrant | `entry_matrix.png` |

## Traffic Distribution Types

| Type | Signal | Entry Strategy |
|------|--------|----------------|
| **ORGANIC_DRIVEN** | >70% organic | SEO-focused entry possible |
| **BALANCED** | 40-70% organic | Mix of SEO + PPC |
| **AD_HEAVY** | <40% organic | Requires significant ad budget |

## Competitive Strength Scoring

| Signal | Meaning |
|--------|---------|
| Review barrier | Higher top-competitor review counts increase entry difficulty |
| Monthly sales | Higher average competitor sales indicate stronger incumbents |
| Seller count | More sellers can indicate heavier price pressure |

## Workflow Integration

```
📊 Competition Phase
├── market-share-analyzer → Analyze brand concentration
├── competitor-analyzer → Analyze competitors ← YOU ARE HERE
└── review-checker → Check review barriers
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |

## Limitations

- Listing quality audit is limited to API-available fields
- BSR history limited to Keepa data availability
- Sponsored detection may miss some edge cases
- Category cleaner applied (may affect results)

## References

- `references/display-rules.md` — Chart styling guidelines
- `shared/category_cleaner.py` — Product filtering module

## Multi-Batch Usage

When analyzing more items than you want to run in a single invocation, keep charts and reports aligned by saving each batch as raw JSON and then generating one merged result.

Step 1: run each batch with `--output` to save intermediate JSON.

```bash
python3 scripts/competitor_analyzer.py '{"keyword": "example"}' --output /tmp/batch1.json
python3 scripts/competitor_analyzer.py '{"keyword": "example 2"}' --output /tmp/batch2.json
```

Step 2: merge every batch JSON and generate the final unified chart.

```bash
python3 scripts/competitor_analyzer.py --merge /tmp/batch1.json /tmp/batch2.json --sort score --chart /tmp/final-charts
```

Use the merged JSON output and `/tmp/final-charts/merged_ranking.png` for the final report. Do not present per-batch charts as final charts when the text report has been globally re-ranked.
