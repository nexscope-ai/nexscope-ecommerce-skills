---
name: ecommerce.review-checker
version: 3.0.0
description: |
  Deep-analyze review content for pain points, complaints, and product opportunities. Triggers: customer complaints, what customers hate, review pain points. Use for historical/deep review mining, not recent review alerts; use review-monitor for monitoring.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Review Checker v3.0.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Analyze actual review content to find pain points and opportunities.**

🆕 **v3.0.0**: Now fetches REAL review text for pain point mining!

## Core Questions

> — What are customers complaining about?
> — How high is the review barrier?
> — Where are competitors failing?

## When to Use

- Mining customer pain points from real reviews
- Finding product improvement opportunities
- Evaluating market entry difficulty
- Understanding what competitors do well/poorly
- Identifying differentiation angles

## Differs From / Not Applicable

- Use review-monitor for recent review alerts and sentiment changes.
- Use differentiation-advisor when the user wants USP/product-improvement strategy from evidence.
- Use this skill for deep historical review mining and pain-point discovery.

## What's New in v3.0.0

| Feature | v2.0 | v3.0 |
|---------|------|------|
| Review barrier analysis | ✅ | ✅ |
| Pain point mining | ❌ API broken | ✅ Real review text |
| Sentiment analysis | ❌ | ✅ |
| Positive aspects | ❌ | ✅ |
| Review examples | ❌ | ✅ Actual quotes |
| Opportunity generation | Basic | Enhanced with examples |

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Amazon | `/api/v1/tools/linkfox/amazon/search` | Products with review counts |
| Amazon | `/api/v1/tools/linkfox/amazon/usReviewsList` | **US market review content** |
| Amazon | `/api/v1/tools/linkfox/amazon/reviews/list` | **Non-US review content** (with `domainCode`) |

## Supported Marketplaces

| Market | Domain Code | Status |
|--------|-------------|--------|
| UK | co.uk | ✅ Primary |
| Canada | ca | ✅ |
| Germany | de | ✅ |
| France | fr | ✅ |
| Japan | co.jp | ✅ |
| Australia | com.au | ✅ |
| **US** | — | ✅ Supported (via `/api/v1/tools/linkfox/amazon/usReviewsList`) |

**Note:** US market uses a dedicated API endpoint `/api/v1/tools/linkfox/amazon/usReviewsList`. Non-US markets use `/api/v1/tools/linkfox/amazon/reviews/list` with the appropriate `domainCode`.


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Analyze by keyword (full analysis)
python3 scripts/review_checker.py '{"keyword": "yoga mat"}'

# Specific market
python3 scripts/review_checker.py '{"keyword": "yoga mat", "market": "UK"}'

# Analyze specific ASIN
python3 scripts/review_checker.py '{"asin": "B01LP0U5X0", "market": "UK"}'

# With charts
python3 scripts/review_checker.py '{"keyword": "yoga mat"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | string | - | Keyword to analyze |
| `asin` | string | - | Specific ASIN (alternative to keyword) |
| `market` | string | | Marketplace code |
| `mode` | string | | , "barrier", or "painpoints" |
| `limit` | int | 60 | Products for barrier analysis |

## Output Structure

```json
{
 "keyword": "yoga mat",
 "market": "US",
 "domain_codeco.uk",
 "api_versionv3.0.0",
 
 "barrier_analysis": {
 "barrier_score": 45,
 "barrier_levelHIGH",
 "distributionmediantop_10_avg": 15000},
 "tier_breakdown": {...}
 },
 
 "pain_point_analysis": {
 "reviews_analyzed": 180,
 "negative_count": 72,
 "negative_percentage": 40.0,
 "rating_distribution1_star2_star": 20, ...},
 
 "pain_points": [
 {
 "category": "Smell",
 "category": "_keysmell",
 : 25,
 "percentage": 34.7,
 "severityMEDIUM",
 "common_phraseschemical smell", "strong odor"],
 : [
 {
 "rating": 1,
 "title": "Terrible chemical smell",
 "snippetHad to air it out for a week...",
 "verified": true
 }
 ]
 }
 ],
 
 "positive_aspects": [
 {
 "category": "Value",
 : 45,
 "percentage": 41.7,
 : [...]
 }
 ],
 
 "verified_review_percentage": 85.2,
 "vine_review_percentage": 3.1
 },
 
 "opportunities": {
 "product_improvements": [
 
 ],
 "listing_improvements": [
 
 ],
 "differentiation_angles": [
 
 ],
 "competitor_strengths_to_match": [
 
 ]
 },
 
 "insights": {
 "summaryBarrier: HIGH (45/100) | Top Pain: Smell",
 "barrier_assessmentHigh barrier (score 45). Median 982 reviews...",
 "pain_point_summaryTop complaints: **Smell** (35%), **Durability** (22%)",
 "positive_summaryCustomers love: Value (42%), Ease Of Use (28%)",
 "recommendations": [
 "🎯 Top opportunity: Address 'Smell' issues",
 "💡 Differentiation: 100% Odor-Free Guarantee"
 ]
 }
}
```

## Pain Point Categories

| Category | Severity | Keywords Detected |
|----------|----------|-------------------|
| Quality | 🔴 HIGH | cheap, flimsy, defective |
| Durability | 🔴 HIGH | broke, fell apart, peeling |
| Functionality | 🔴 HIGH | doesn't work, malfunction |
| Misleading | 🔴 HIGH | not as described, fake |
| Size/Fit | 🟡 MEDIUM | too small, wrong size |
| Value | 🟡 MEDIUM | overpriced, not worth it |
| Smell | 🟡 MEDIUM | chemical smell, odor |
| Customer Service | 🟡 MEDIUM | no response, refund |
| Shipping | 🟢 LOW | arrived damaged |
| Instructions | 🟢 LOW | confusing, hard to assemble |

## Positive Aspect Categories

| Category | Keywords Detected |
|----------|-------------------|
| Quality | high quality, well made, sturdy |
| Value | great value, worth every penny |
| Ease of Use | easy to use, simple, intuitive |
| Durability | durable, long lasting |
| Appearance | looks great, beautiful |
| Comfort | comfortable, soft |
| Fast Shipping | fast shipping, arrived early |
| Recommend | highly recommend, love it |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Tier Distribution | Review barrier tiers | `1_tier_distribution.png` |
| Pain Points | Horizontal bar with severity | `2_pain_points.png` |
| Rating Distribution | 1-5 star breakdown | `3_rating_distribution.png` |
| Positive Aspects | What customers love | `4_positive_aspects.png` |
| Barrier Score | Gauge visualization | `5_barrier_score.png` |

## Review Tiers (Barrier Analysis)

| Tier | Range | Difficulty |
|------|-------|------------|
| Zero | 0 | 🟢 New product |
| Starter | 1-49 | 🟢 Entry-friendly |
| Established | 50-199 | 🟡 Getting traction |
| Competitive | 200-999 | 🟡 Solid presence |
| Dominant | 1K-5K | 🔴 Hard to challenge |
| Fortress | 5K+ | ⛔ Market leader |

## Barrier Score (0-100)

| Level | Score | Entry Strategy |
|-------|-------|----------------|
| 🟢 LOW | 70-100 | Launch confidently |
| 🟡 MODERATE | 50-70 | Strong launch needed |
| 🔴 HIGH | 30-50 | Differentiate heavily |
| ⛔ FORTRESS | 0-30 | Find sub-niche |

## Workflow Integration

```
📊 Competition Phase
├── market-share-analyzer → Brand concentration
├── competitor-analyzer → Competitor landscape
└── review-checker → Pain points + barrier ← YOU ARE HERE

🎯 Differentiation
├── review-checker → Find competitor weaknesses
└── differentiation-advisor → Build positioning
```

## Example Analysis

**Keyword: "yoga mat" (UK market)**

| Metric | Value |
|--------|-------|
| Reviews Analyzed | 180 |
| Negative Rate | 40% |
| Top Pain Point | Smell (35%) |
| Top Positive | Value (42%) |
| Barrier Score | 45 (HIGH) |

**Top Recommendations:**
1. 🎯 Address 'Smell' - biggest customer complaint
2. 💡 Differentiate with 
3. ⚠️ High barrier - consider niche variant

## Limitations

- US market supported via dedicated `/api/v1/tools/linkfox/amazon/usReviewsList` endpoint
- Max 100 reviews per star rating per ASIN
- Reviews fetched in real-time (no historical archive)
- Pain point detection is keyword-based (not AI sentiment)
- Category cleaner may filter some products


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` — Chart styling guidelines
