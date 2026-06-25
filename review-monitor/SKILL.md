---
name: review-monitor
version: 1.0.0
description: |
  Monitor new/recent reviews and sentiment changes for an ASIN. Triggers: new reviews, negative review alert, sentiment tracking, review monitor. Use for recent changes/alerts, not deep review mining; use review-checker for pain points.
allowed-tools:
 - Bash
 - Read
 - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Review Monitor v1.0.0

## Core Question

What new or recent review changes should the seller react to?

**What do new reviews say?**

## Clarify or Infer Before Querying

- If ASIN is missing, ask for it or resolve it from product search.
- Clarify marketplace, monitoring window, and whether the user cares about negative reviews, sentiment, rating shifts, or topics.
- Do not substitute deep historical review mining unless the user asks for pain points.

## When to Use
- User wants to check recent reviews
- User asks "what are customers saying"
- User wants to monitor review sentiment
- User needs alerts on negative reviews
- User asks about review trends

## Differs From / Not Applicable

- Use review-checker for deep review mining and complaint themes.
- Use product-validator for review authenticity as part of full ASIN validation.
- Use this skill for recent review changes, alerts, and sentiment tracking.

## Difference from review-checker

| Feature | review-checker | review-monitor |
|---------|---------------|----------------|
| Focus | Pain point mining | Recent review monitoring |
| Purpose | Product research | Ongoing monitoring |
| Analysis | Deep pain point extraction | Sentiment + topic analysis |
| Use case | Before entering market | After product launch |

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/reviews/list` | Reviews for non-US markets |
| NexScope Proxy | `/api/v1/tools/linkfox/amazon/usReviewsList` | Reviews for US market |

## Supported Marketplaces

| Market | Domain | Status |
|--------|--------|--------|
| UK, CA, DE, FR, JP, AU, IN | Direct | Supported |
| **US** | - | Supported (via `/api/v1/tools/linkfox/amazon/usReviewsList`) |

## MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** - use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** - when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Basic monitoring
python3 scripts/review_monitor.py '{"asin": "B0BTYCRJSS"}'

# Specific market
python3 scripts/review_monitor.py '{"asin": "B0BTYCRJSS", "market": "UK"}'

# More reviews per star
python3 scripts/review_monitor.py '{"asin": "B0BTYCRJSS", "count_per_star": 30}'

# With charts
python3 scripts/review_monitor.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `asin` | string | Yes | - | ASIN to monitor |
| `market` | string | No | | Marketplace |
| `count_per_star` | int | No | 20 | Reviews per star rating (max 100) |

## Output Structure

The output will be a structured markdown report, following this format:

**Review Monitoring Report: [ASIN]**

---

**1. Executive Summary**
*   **Monitored ASIN:** [asin]
*   **Monitored Market:** [market]
*   **Total Reviews Analyzed:** [total_reviews]
*   **Current Product Rating:** [product_rating]
*   **Average Recent Review Rating:** [analysis.average_rating]
*   **Key Insight:** This report monitors recent reviews, analyzes sentiment, and highlights key trends and alerts.

**2. Review Analysis Overview**
*   **Total Reviews:** [analysis.total_analyzed]
*   **Average Rating:** [analysis.average_rating]
*   **Verified Review Percentage:** [analysis.verified_percentage]%
*   **Negative Review Percentage:** [analysis.negative_percentage]%
*   **Current Status:** [insights.status]

**3. Rating Distribution**
*   **Star Rating Distribution:**

| Star Rating | Review Count | Share (%) |
| :--- | :--- | :--- |
| 1 Star | [analysis.rating_distribution.1] | [calculated percentage]% |
| 2 Stars | [analysis.rating_distribution.2] | [calculated percentage]% |
| 3 Stars | [analysis.rating_distribution.3] | [calculated percentage]% |
| 4 Stars | [analysis.rating_distribution.4] | [calculated percentage]% |
| 5 Stars | [analysis.rating_distribution.5] | [calculated percentage]% |

**4. Sentiment Distribution**
*   **Review Sentiment Distribution:**

| Sentiment | Review Count | Share (%) |
| :--- | :--- | :--- |
| Positive | [analysis.sentiment_distribution.positive] | [calculated percentage]% |
| Negative | [analysis.sentiment_distribution.negative] | [calculated percentage]% |
| Mixed | [analysis.sentiment_distribution.mixed] | [calculated percentage]% |
| Neutral | [analysis.sentiment_distribution.neutral] | [calculated percentage]% |

**5. Top Topics**
*   **Most frequently mentioned topics in reviews:**

| Topic | Mention Count |
| :--- | :--- |
| [analysis.topic_frequency.topic1] | [analysis.topic_frequency.topic1_count] |
| [analysis.topic_frequency.topic2] | [analysis.topic_frequency.topic2_count] |
| [analysis.topic_frequency.topic3] | [analysis.topic_frequency.topic3_count] |
| ... | ... |

**6. Alerts Found**
*   **Alert List:**

| Type | Severity | Icon | Message |
| :--- | :--- | :--- | :--- |
| [alerts[0].type] | [alerts[0].severity] | [alerts[0].icon] | [alerts[0].message] |
| ... | ... | ... | ... |

**7. Key Findings & Recommendations**
*   **Key Findings:**
    *   [insights.key_findings[0]]
    *   [insights.key_findings[1]]
    *   ...
*   **Recommendations:** (derived from alerts and key findings)

**8. Sample Reviews**
*   **Top Positive Reviews:**
    *   [sample_reviews.top_positive[0]]
    *   ...
*   **Latest Negative Reviews:**
    *   [sample_reviews.recent_negative[0]]
    *   ...

**9. Attached Visualizations**
*   Rating Distribution (1_rating_distribution.png)
*   Sentiment Analysis (2_sentiment.png)
*   Common Topics (3_topics.png)
*   Alert Distribution (4_alerts.png)

## Sentiment Categories

| Sentiment | Meaning | Trigger |
|-----------|---------|---------|
| **positive** | Happy customer | Rating >=4 or positive keywords |
| **negative** | Unhappy customer | Rating <=2 or negative keywords |
| **mixed** | Mixed feelings | Rating 3 or conflicting signals |
| **neutral** | Factual review | No strong sentiment detected |

## Topics Tracked

| Topic | Example Keywords |
|-------|------------------|
| quality | quality, well made, cheap, flimsy |
| price_value | price, value, worth, expensive |
| shipping | shipping, delivery, package, damaged |
| functionality | works, function, performance |
| durability | lasted, durable, broke, stopped working |
| size_fit | size, fit, small, big, tight |
| appearance | looks, color, design, beautiful |
| ease_of_use | easy, simple, difficult, setup |
| customer_service | customer service, return, refund |

## Alert Types

| Alert | Severity | Trigger |
|-------|----------|---------|
| High Negative | HIGH | >=30% negative reviews |
| Moderate Negative | MEDIUM | 15-30% negative reviews |
| Low Rating | HIGH | Average rating < 3.5 |
| One-Star Reviews | HIGH | Any 1-star reviews found |
| Topic Issue | MEDIUM | 3+ complaints on same topic |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Rating Distribution | Bar chart by stars | `1_rating_distribution.png` |
| Sentiment Analysis | Positive/Negative/Mixed | `2_sentiment.png` |
| Common Topics | Horizontal bar chart | `3_topics.png` |
| Alerts | Alert severity breakdown | `4_alerts.png` |

## Workflow Integration

```text
Product Monitoring
|-- price-monitor -> Track prices
|-- review-monitor -> Monitor reviews -> YOU ARE HERE
|-- keyword-rank-tracker -> Track rankings
`-- competitor-analyzer -> Watch competitors
```

## Example Report

**ASIN: B0BTYCRJSS | 100 Reviews Analyzed**

| Metric | Value |
|--------|-------|
| Average Rating | 3.8 stars |
| Positive | 55% |
| Negative | 28% |
| Verified | 85% |

**Top Topics:**
1. Quality (35 mentions)
2. Price/Value (28 mentions)
3. Functionality (22 mentions)

**Alerts:**
- 28% negative reviews - monitor closely
- Quality complaints: 15 mentions

**Sample Negative Review:**
> 2/5 stars
>

## Use Cases

### 1. Daily Review Check
>

### 2. Negative Review Alert
>

### 3. Topic Analysis
>

### 4. Competitor Review Monitor
>

## Limitations

- US market supported via dedicated `/api/v1/tools/linkfox/amazon/usReviewsList` endpoint
- Max 100 reviews per star rating
- Sentiment analysis is keyword-based (not AI)
- Real-time monitoring not available (manual refresh needed)
- Historical comparison not included (use review-checker for trends)


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- `references/display-rules.md` - Output formatting
