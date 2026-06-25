---
name: ecommerce.image-similarity-finder
version: 1.0.0
description: |
  Find visually similar Amazon products from an image. Triggers: reverse image search, find lookalikes, who else sells this, source by image. Use for marketplace lookalikes, not patent similarity or design infringement checks.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Image Similarity Finder v1.0.0

## Core Question

Which Amazon products look visually similar to this image or product?

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Are there similar products?**

Find similar products on Amazon using image-based visual search.

## When to Use
- User has a product image and wants to find similar items
- User asks 
- User wants to discover competitors based on appearance
- User asks for "reverse image search on Amazon"
- User wants to compare prices of similar-looking products
- User asks or

## Differs From / Not Applicable

- Use design-patent-analyzer for design-patent infringement or visual patent risk.
- Use patent-risk-checker for IP/FTO screening.
- Use this skill for finding visually similar marketplace products or sellers.

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| Amazon | `/api/v1/tools/linkfox/amazon/searchByImage` | Visual product search |
| Keepa (optional) | via `aggregateByKeepaData: true` in searchByImage | Sales rank, monthly sales enrichment |

## Supported Marketplaces

| Market | Domain | Currency |
|--------|--------|----------|
| 🇺🇸 US | amazon.com | $ |
| 🇬🇧 UK | amazon.co.uk | £ |
| 🇩🇪 DE | amazon.de | € |
| 🇫🇷 FR | amazon.fr | € |
| 🇮🇹 IT | amazon.it | € |
| 🇪🇸 ES | amazon.es | € |
| 🇯🇵 JP | amazon.co.jp | ¥ |
| 🇮🇳 IN | amazon.in | ₹ |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic image search
python3 scripts/image_similarity_finder.py '{"image_url": "https://example.com/product.jpg"}'

# Specific market
python3 scripts/image_similarity_finder.py '{"image_url": "https://example.com/product.jpg", "market": "DE"}'

# With Keepa sales data
python3 scripts/image_similarity_finder.py '{"image_url": "https://example.com/product.jpg", "with_keepa": true}'

# Cross-market comparison
python3 scripts/image_similarity_finder.py '{"image_url": "https://example.com/product.jpg", "cross_market": true}'

# With charts
python3 scripts/image_similarity_finder.py '{"image_url": "https://example.com/product.jpg"}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_url` | string | Yes | - | Publicly accessible image URL |
| `market` | string | No | | Target marketplace |
| `sort` | string | No | "default" | Sort order (see below) |
| `with_keepa` | bool | No | false | Include sales data |
| `cross_market` | bool | No | false | Search multiple markets |

### Sort Options

| Value | Description |
|-------|-------------|
| `default` | Relevance |
| `price-asc-rank` | Price: low to high |
| `price-desc-rank` | Price: high to low |
| `rating-asc-rank` | Rating: low to high |
| `rating-desc-rank` | Rating: high to low |
| `ratings-asc-rank` | Reviews: low to high |
| `ratings-desc-rank` | Reviews: high to low |

## Output Structure

The output will be a structured markdown report, following this format:

**Product Image Similarity Analysis Report**

---

**1. Executive Summary**
*   **Input Image:** [image_url]
*   **Analysis Market:** [market]
*   **Total Similar Products Found:** [total_found]
*   **Opportunity Assessment:** [opportunity_assessment.level] (Score: [opportunity_assessment.score]/100)
*   **Core Insight:** [insights.summary]

**2. Similar Products Market Analysis**
*   **Price Analysis:**
    *   Minimum Price: [market_analysis.price_analysis.min]
    *   Maximum Price: [market_analysis.price_analysis.max]
    *   Median Price: [market_analysis.price_analysis.median]
    *   Currency: [market_analysis.price_analysis.currency]
*   **Rating Analysis:**
    *   Minimum Rating: [market_analysis.rating_analysis.min]
    *   Maximum Rating: [market_analysis.rating_analysis.max]
    *   Average Rating: [market_analysis.rating_analysis.avg]
*   **Brand Distribution (Top 3):**

| Brand | Similar Product Count |
| :--- | :--- |
| [market_analysis.brand_distribution.brand1] | [market_analysis.brand_distribution.count1] |
| [market_analysis.brand_distribution.brand2] | [market_analysis.brand_distribution.count2] |
| [market_analysis.brand_distribution.brand3] | [market_analysis.brand_distribution.count3] |

*   **Price Segment Distribution:**

| Price Segment | Product Count |
| :--- | :--- |
| Budget | [market_analysis.price_tiers.budget] |
| Mid-Range | [market_analysis.price_tiers.mid] |
| Premium | [market_analysis.price_tiers.premium] |

**3. Opportunity Assessment**
*   **Score:** [opportunity_assessment.score] / 100
*   **Level:** [opportunity_assessment.level]
*   **Recommendation:** [opportunity_assessment.recommendation]
*   **Price Gap Opportunities:**

| Lower Price | Upper Price | Gap Percentage | Suggested Opportunity Price |
| :--- | :--- | :--- | :--- |
| [price_gaps[0].lower_price] | [price_gaps[0].upper_price] | [price_gaps[0].gap_percentage]% | [price_gaps[0].opportunity_price] |

**4. Discovered Similar Products**
*   **List of Similar Products by Rank (Showing Top 5):**

| Rank | ASIN | Product Name | Brand | Price | Rating | Reviews | Monthly Sales |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [similar_products[0].rank] | [similar_products[0].asin] | [similar_products[0].title] | [similar_products[0].brand] | [similar_products[0].price] | [similar_products[0].rating] | [similar_products[0].reviews] | [similar_products[0].monthly_sales] |
| ... | ... | ... | ... | ... | ... | ... | ... |

**5. Actionable Recommendations**
*   [First recommendation from `insights.recommendations`]
*   [Second recommendation from `insights.recommendations`]
*   ... (Listing all key recommendations)

**6. Attached Visualizations**
*   Price Comparison (1_price_comparison.png)
*   Rating vs Reviews (2_rating_reviews.png)
*   Brand Distribution (3_brand_distribution.png)
*   Opportunity Score (4_opportunity_score.png)

## Opportunity Score (0-100)

| Level | Score | Meaning |
|-------|-------|---------|
| 🟢 HIGH | 70-100 | Few competitors, quality gaps exist |
| 🟡 MODERATE | 50-70 | Viable with differentiation |
| 🟠 LOW | 30-50 | Challenging, strong differentiation needed |
| 🔴 VERY LOW | 0-30 | Difficult market |

### Score Factors

| Factor | Impact | Trigger |
|--------|--------|---------|
| Low competition | +20 | < 10 similar products |
| Quality gap | +15 | Avg rating < 4.0★ |
| Fragmented market | +10 | No dominant brand |
| High competition | -15 | > 50 similar products |
| Brand dominated | -10 | One brand > 50% share |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Price Comparison | Bar chart of similar product prices | `1_price_comparison.png` |
| Rating vs Reviews | Scatter plot of quality vs popularity | `2_rating_reviews.png` |
| Brand Distribution | Horizontal bar of brand shares | `3_brand_distribution.png` |
| Opportunity Score | Gauge visualization | `4_opportunity_score.png` |

## Workflow Integration

```
🔍 Product Discovery
├── image-similarity-finder → Find similar products ← YOU ARE HERE
├── review-checker → Analyze reviews
├── differentiation-advisor → Strategy
└── listing-keyword-optimizer → Optimize listing
```

## Example Use Cases

### 1. Competitor Discovery
> 

### 2. Sourcing Alternative
> 

### 3. Cross-Border Opportunity
> 

### 4. Counterfeit Detection
> 

### 5. Market Entry
> 

## Limitations

- Requires publicly accessible image URL (no local files)
- Visual similarity is algorithm-based (not perfect)
- Some marketplaces may have limited results
- Keepa data costs additional tokens
- Cross-market search is slower (multiple API calls)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/api.md` — NexScope Proxy API documentation
