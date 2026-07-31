---
name: ecommerce.amazon-niche-info
description: Query and analyze Jiimore data for Amazon niche market insights, including market metrics, buyer reviews, competitive landscape, price trends, and growth trends. Trigger when the user mentions niche market analysis, market insights, niche market data, market competition analysis, brand concentration, new product launch success rate, out-of-stock rate, price trends, review insights, market demand score, niche market insights, market metrics, competition analysis, price trends, growth trends, Jiimore data, market intelligence, out-of-stock rate. Even if the user does not explicitly mention "Jiimore" or "niche market", if their need involves querying market-level intelligence for a specific Amazon niche market by market ID, this skill should also be triggered.
---

# Jiimore Niche Market Info

This skill guides you on how to query and analyze Amazon niche market data via the Jiimore data service, helping Amazon sellers gain deep insights into specific niche markets including competition, pricing, reviews, and growth trends.

## How to Invoke

- **API Endpoint**: `POST /jiimore/getNicheInfo` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_niche_info.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-jiimore-get-niche-info-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Core Concepts

A **niche market** in Jiimore represents a fine-grained product segment on Amazon. Each niche is identified by a unique `nicheId`. This tool retrieves comprehensive market intelligence for a single niche at a time, covering:

- **Market overview**: niche title, demand score, product count, brand count, selling partner count
- **Pricing**: average price, minimum price, maximum price
- **Search & conversion**: weekly/quarterly search volume, search volume growth, search conversion rate, click-to-sale conversion rate, units sold
- **Competition concentration**: top 5 / top 20 product and brand click share (current, 90-day, 360-day snapshots)
- **Product launches**: new products launched, successful launches across 90-day / 180-day / 360-day windows
- **Inventory health**: average out-of-stock rate over time
- **Seller maturity**: average brand age, average selling partner age
- **Review insights**: average review rating, average review count, positive and negative customer review insights
- **Advertising**: ACOS (advertising cost of sales), sponsored products percentage
- **Profitability**: profit margin > 50% SKU ratio, break-even ratio, return rate

**Supported marketplaces**: US (United States), JP (Japan), DE (Germany). Default is **US**.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| nicheId | string | Yes | The niche market ID to query. Maximum 1000 characters. Only one ID per request. |
| countryCode | string | No | Marketplace code. Allowed values: `US`, `JP`, `DE`. Defaults to `US`. |

### How to Use Parameters

1. **nicheId is mandatory**: The user must provide or you must identify the niche market ID. This is a string identifier for a specific Amazon niche segment.
2. **countryCode defaults to US**: Only specify a different value when the user explicitly mentions Japan (`JP`) or Germany (`DE`).
3. **Single ID per call**: This tool only supports one niche ID per request. If the user wants to compare multiple niches, make separate calls.

## Usage Examples

**1. Basic niche market lookup (US)**
Query niche market data for a given niche ID in the US marketplace:
```
nicheId: "12345678"
countryCode: "US"
```

**2. Query a niche in the Japan marketplace**
```
nicheId: "87654321"
countryCode: "JP"
```

**3. Query a niche in the Germany marketplace**
```
nicheId: "11223344"
countryCode: "DE"
```

## Analysis Guidance

When presenting results, organize the rich data into logical sections for the user:

### Market Overview
- Niche title (English and Chinese translation if available)
- Demand score, product count, brand count, selling partner count
- Reference ASIN image (if available)

### Pricing & Profitability
- Average price, min price, max price
- Profit margin > 50% SKU ratio, break-even ratio, return rate
- ACOS

### Search & Demand Trends
- Weekly and quarterly search volume and growth rates
- Search conversion rate, click conversion rate
- Units sold (weekly/quarterly)

### Competition Landscape
- Top 5 and top 20 product/brand click share (current vs. 90-day vs. 360-day)
- Brand count trends, selling partner count trends
- Sponsored products percentage over time

### Product Launch Activity
- New products launched and successful launches across time windows
- Launch success rate (semiannual)

### Review & Customer Insights
- Average review rating and count trends
- Positive and negative customer review insights
- Product star rating impact

### Inventory & Operations
- Average out-of-stock rate trends

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables or grouped sections without subjective business advice unless specifically requested.
2. **Trend comparison**: When the response includes current, 90-day-ago, and 360-day-ago data points, present them side-by-side so users can easily spot trends.
3. **Percentage formatting**: Display share and rate values as percentages (e.g., 0.35 as 35.0%).
4. **Review insights**: If positive/negative customer review insights are present, list them as bullet points.
5. **Image display**: If `referenceAsinImageUrl` is present, display or link to the niche reference image.
6. **Error handling**: When a query fails, explain the reason based on the response and suggest checking the niche ID or country code.
## Important Limitations

- **Single ID only**: Only one niche ID can be queried per request. Batch queries are not supported.
- **Three marketplaces**: Only US, JP, and DE are supported.
- **Niche ID required**: The user must supply the niche ID; this tool cannot search for niches by keyword or category.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about a specific Amazon niche market:

| User Says | Scenario |
|-----------|----------|
| "Look up this niche market", "niche ID info" | Basic niche lookup |
| "How competitive is this niche", "brand concentration" | Competition analysis |
| "What's the average price in this niche" | Pricing intelligence |
| "Search volume for this niche", "demand trends" | Search & demand analysis |
| "How many new products launched", "launch success rate" | Product launch tracking |
| "Review rating in this niche", "buyer feedback insights" | Review analysis |
| "Out-of-stock rate", "inventory health" | Inventory analysis |
| "Is this niche worth entering", "niche opportunity" | Comprehensive niche evaluation |

**Not applicable** -- Needs beyond niche market lookup:

- Searching for niches by keyword or category (this tool requires a known niche ID)
- Individual ASIN-level product analysis
- ABA search term data (use the ABA Data Explorer instead)
- Advertising campaign management or PPC optimization
- Listing copywriting or review management

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
