---
name: ecommerce-amazon-niche-reviews-by-keyword
description: "Amazon niche market review analysis and consumer sentiment insights. Trigger when the user mentions niche market review analysis, consumer sentiment, user pain points, customer feedback insights, review topic analysis, positive/negative review breakdown, niche market opinion mining, product review sentiment analysis, niche market reviews, consumer sentiment, customer pain points, review topic analysis, positive/negative reviews, opinion mining, Jiimore data. Even if the user does not explicitly mention \"niche market reviews\", if their need involves analyzing consumer reviews within Amazon niche markets or understanding customer sentiment at the niche market level, this skill should also be triggered."
---

# Jiimore Niche Review from Keyword

This skill guides you on how to query and analyze Amazon niche market review data powered by Jiimore, helping Amazon sellers uncover consumer sentiment, pain points, and real demand signals from product reviews within niche markets.

## Core Concepts

Niche Review Analysis aggregates and categorizes customer reviews across products in an Amazon niche market. Given a keyword, the system identifies the relevant niche markets, extracts review topics, classifies them as positive or negative, and shows how frequently each topic is mentioned. This enables sellers to understand what customers love, what frustrates them, and where product improvement opportunities exist.

**Review types**: Each review entry is classified as either "positive" or "negative", reflecting the overall sentiment of that review topic.

**Mention percentage**: The `percentOfMentions` value (0-1 scale, representing 0%-100%) indicates how frequently a particular topic appears across all reviews in the niche. A higher percentage means more customers are talking about that topic.

## Supported Marketplaces

US (United States), JP (Japan), DE (Germany)

Default marketplace is **US**. Use US when the user does not specify a marketplace.

## How to Invoke

- **API Endpoint**: `POST /jiimore/getNicheReviewFromKeyword` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_niche_reviews_by_keyword.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-jiimore-get-niche-review-from-keyword-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Parameter Guide

### Required Parameter

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | The search keyword (max 1000 chars). Must be in the language of the target marketplace (English for US, German for DE, Japanese for JP) |

### Marketplace & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, or DE |
| page | integer | 1 | Page number (starting from 1) |
| pageSize | integer | 50 | Results per page (10-100) |

### Sorting

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| sortField | string | unitsSoldT7 | Field to sort by (see Sortable Fields below) |
| sortType | string | desc | Sort direction: `desc` (descending) or `asc` (ascending) |

**Sortable Fields**:

| Field | Description |
|-------|-------------|
| unitsSoldT7 | Units sold (7-day) |
| searchVolumeT7 | Search volume (7-day) |
| searchVolumeGrowthT7 | Search volume growth (7-day) |
| clickConversionRateT7 | Click conversion rate (7-day) |
| searchConversionRateT7 | Search conversion rate (7-day) |
| clickCountT7 | Click count (7-day) |
| demand | Demand score |
| avgPrice | Average price |
| maximumPrice | Maximum price |
| minimumPrice | Minimum price |
| productCount | Product count |
| brandCount | Brand count |
| top5BrandsClickShare | Top 5 brands click share |
| top5ProductsClickShare | Top 5 products click share |
| clickCountT90 | Click count (90-day) |
| clickConversionRateT90 | Click conversion rate (90-day) |
| searchConversionRateT90 | Search conversion rate (90-day) |
| searchVolumeT90 | Search volume (90-day) |
| unitsSoldT90 | Units sold (90-day) |
| unitsSoldGrowthT90 | Units sold growth (90-day) |
| searchVolumeGrowthT90 | Search volume growth (90-day) |
| returnRateT360 | Return rate (360-day) |
| newProductsLaunchedT180 | New products launched (180-day) |
| successfulLaunchesT180 | Successful launches (180-day) |
| launchRateT180 | Launch success rate (180-day) |
| acos | ACOS |
| profitRate50 | Profit rate at 50% organic orders |

### Niche Filtering Parameters

All filter parameters follow a min/max range pattern. Values for percentage-based fields use a 0-1 scale (e.g., 0.05 = 5%).

**Product & Brand Metrics**:

| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| brandCountMin / brandCountMax | integer | Brand count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Sales & Search Volume**:

| Parameter | Type | Description |
|-----------|------|-------------|
| unitsSoldT7Min / unitsSoldT7Max | integer | Units sold (7-day) range |
| searchVolumeT7Min / searchVolumeT7Max | integer | Search volume (7-day) range |
| clickCountT7Min / clickCountT7Max | integer | Click count (7-day) range |

**Conversion & Click Rates** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| clickConversionRateT7Min / clickConversionRateT7Max | number | Click conversion rate (7-day) range |

**Market Concentration** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share range |
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share range |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage range |

**Brand & Seller Age**:

| Parameter | Type | Description |
|-----------|------|-------------|
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**New Product & Return Metrics** (0-1 scale):

| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | Launch success rate (180-day) range |
| newProductRateT180 | number | New product percentage (180-day) min |
| returnRateT360Min / returnRateT360Max | number | Return rate (360-day) range |

**Advertising**:

| Parameter | Type | Description |
|-----------|------|-------------|
| cpcMediumMin / cpcMediumMax | number | CPC (current) range |

## Usage Examples

**1. Basic niche review lookup for a keyword**
```
Analyze customer reviews in niche markets related to "yoga mat" on the US marketplace.
```
Parameters: `{"keyword": "yoga mat", "countryCode": "US"}`

**2. Find niche reviews with high search volume**
```
Show me niche market reviews for "wireless earbuds" where 7-day search volume is above 10000.
```
Parameters: `{"keyword": "wireless earbuds", "countryCode": "US", "searchVolumeT7Min": 10000}`

**3. Low competition niches with review insights**
```
Find review insights for "pet bed" niches where top 5 brands hold less than 30% click share.
```
Parameters: `{"keyword": "pet bed", "countryCode": "US", "top5BrandsClickShareMax": 0.3}`

**4. Japanese market niche reviews**
```
Analyze niche reviews for wireless earbuds on the Japan marketplace.
```
Parameters: `{"keyword": "wireless earbuds", "countryCode": "JP"}`

**5. Sorted by demand score**
```
Show niche reviews for "kitchen organizer" sorted by demand score in descending order.
```
Parameters: `{"keyword": "kitchen organizer", "sortField": "demand", "sortType": "desc"}`

**6. Filter by new product success rate**
```
Find niches for "phone case" where the 180-day new product launch success rate is above 20%.
```
Parameters: `{"keyword": "phone case", "launchRateT180Min": 0.2}`

**7. Low return rate niches**
```
Show review topics for "water bottle" niches with return rates below 5%.
```
Parameters: `{"keyword": "water bottle", "returnRateT360Max": 0.05}`

## Display Rules

1. **Present data clearly**: Show review topics in a well-organized table. Include the niche name, review type (positive/negative), topic, mention percentage, and a review example
2. **Percentage formatting**: Convert 0-1 scale values to percentages for display (e.g., 0.15 -> 15%)
3. **Sentiment separation**: When presenting results, group or clearly label positive vs. negative reviews so users can quickly identify opportunities and pain points
4. **Actionable insight framing**: While showing data objectively, highlight high-mention-percentage negative reviews as potential product improvement opportunities, and high-mention-percentage positive reviews as features to emphasize in listings
5. **Volume notice**: When results are large, show the most relevant data first and remind users about pagination options
6. **Error handling**: When a query fails, explain the reason and suggest adjusting the keyword or filter criteria
7. **Language reminder**: If a user provides a keyword in the wrong language for the target marketplace, remind them to use the marketplace's native language (English for US, German for DE, Japanese for JP)
## User Expression & Scenario Quick Reference

**Applicable** -- Consumer review and sentiment analysis within Amazon niche markets:

| User Says | Scenario |
|-----------|----------|
| "What do customers say about XX" | Niche review topic lookup |
| "Customer pain points for XX" | Negative review analysis |
| "What features do buyers love in XX" | Positive review analysis |
| "Review sentiment for XX niche" | Full sentiment breakdown |
| "Consumer demand insights for XX" | Demand signal extraction from reviews |
| "Common complaints about XX products" | Negative topic mining |
| "What makes XX products popular" | Positive topic mining |
| "Niche market review analysis" | General niche review exploration |

**Not applicable** -- Needs beyond niche review analysis:
- Individual ASIN review analysis (this tool works at the niche/market level)
- Keyword search volume trends without review context (use ABA data tools instead)
- Product listing optimization or copywriting
- Advertising strategy and PPC management
- Sales estimation or revenue forecasting

**Boundary judgment**: When users say "market research" or "product opportunity", if their intent focuses on understanding consumer sentiment, review topics, and pain points within a niche market, this skill applies. If they are asking about search volume trends, pricing strategy, or sales data without review context, it does not apply.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
