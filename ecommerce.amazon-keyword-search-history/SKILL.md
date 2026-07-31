---
name: ecommerce.amazon-keyword-search-history
description: Jungle Scout keyword historical search volume query, returning Amazon keyword exact search volume trends in 7-day periods, covering 10 marketplaces including US, UK, DE, JP, etc. Trigger when the user mentions keyword search volume trends, historical search volume, search popularity changes, keyword seasonality, search volume fluctuations, Jungle Scout search volume, keyword search volume history, keyword trend, search volume over time, seasonal search volume, keyword popularity trend. Even if the user does not explicitly mention "Jungle Scout", if their need involves viewing the search volume trend of an Amazon keyword over time, this skill should also be triggered.
---

# Jungle Scout -- Keyword Historical Search Volume

This skill queries the historical exact search volume for Amazon keywords via the Jungle Scout data source, returning weekly search volume data points over a specified date range across 10 Amazon marketplaces.

## Core Concepts

The Jungle Scout Keyword Historical Search Volume tool provides **weekly granularity exact match search volume** historical data for Amazon marketplace keywords. Sellers can query search volume changes within a specified time range to determine:

- **Seasonal patterns**: Which months are peak/off-season for a keyword
- **Trend direction**: Whether search volume is consistently rising, falling, or stable
- **Volatility**: Assess the stability of market demand
- **Holiday effects**: Search volume spikes around major promotions and holidays

**Data granularity**: Each record represents a **7-day period**, including the exact match search volume estimate for that week.

## Data Fields

### Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Period ID | id | Data period identifier (marketplace/keyword/date range) | us_sushi_20250105_20250111 |
| Period Start Date | estimateStartDate | Start of the 7-day statistical period | 2025-01-05 |
| Period End Date | estimateEndDate | End of the 7-day statistical period | 2025-01-11 |
| Exact Search Volume | estimatedExactSearchVolume | Exact match search volume for the period (searches/week) | 12500 |
| Resource Type | type | Fixed value | historical_keyword_search_volume |
| Cost Token | costToken | Tokens consumed by this call | 1 |

## Supported Marketplaces

| Marketplace | marketplace value | Description |
|-------------|-------------------|-------------|
| United States | us | Amazon.com |
| United Kingdom | uk | Amazon.co.uk |
| Germany | de | Amazon.de |
| India | in | Amazon.in |
| Canada | ca | Amazon.ca |
| France | fr | Amazon.fr |
| Italy | it | Amazon.it |
| Spain | es | Amazon.es |
| Mexico | mx | Amazon.com.mx |
| Japan | jp | Amazon.co.jp |

Default marketplace is **us**. When the user does not specify a marketplace, use us.

## How to Invoke

- **API Endpoint**: `POST /tool-jungle-scout/keywords/historical-search-volume` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_keyword_search_history.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-junglescout-keyword-history-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

All four parameters are **required**: `marketplace`, `keyword`, `startDate`, `endDate`.

### Principles for Building API Calls

1. **Marketplace mapping**: "US marketplace" -> `us`, "Japan marketplace" -> `jp`, "Germany marketplace" -> `de`; default to `us` when unspecified
2. **Date format**: Must be `YYYY-MM-DD`, e.g. `2025-01-05`
3. **Time span**: `startDate` to `endDate` maximum **366 days**; split into multiple requests if exceeding this
4. **Keyword**: Pass the user-provided keyword as-is (lowercase English preferred)
5. **Common time calculations**:
   - "Past 3 months" -> endDate = today, startDate = ~90 days ago
   - "Full last year" -> `2025-01-01` to `2025-12-31`
   - "Peak season" -> determine by category, e.g. Q4 = `10-01` to `12-31`

### Common Query Scenarios

**1. View keyword search trend for the past half year**
```json
{
  "marketplace": "us",
  "keyword": "yoga mat",
  "startDate": "2025-10-01",
  "endDate": "2026-03-31"
}
```

**2. Determine keyword seasonality (full year data)**
```json
{
  "marketplace": "us",
  "keyword": "christmas decorations",
  "startDate": "2025-01-01",
  "endDate": "2025-12-31"
}
```

**3. Compare peak-season vs off-season search volume**

Make two separate calls:
- Off-season: `startDate=2025-02-01`, `endDate=2025-04-30`
- Peak season: `startDate=2025-10-01`, `endDate=2025-12-31`

**4. Multi-marketplace comparison**

Query the same keyword across different marketplaces (e.g., `us`, `de`, `jp`) and compare search volume scale across markets.

**5. Verify whether market demand is growing**
```json
{
  "marketplace": "de",
  "keyword": "luftreiniger",
  "startDate": "2025-04-01",
  "endDate": "2026-03-31"
}
```

## Display Rules

1. **Trend visualization priority**: Recommend displaying search volume changes as a timeline/line chart, with date periods on the X-axis and search volume on the Y-axis
2. **Table support**: Also provide a data table for precise reference, columns including: Period Start Date, Period End Date, Search Volume
3. **Trend summary**: Briefly summarize the trend direction after the data (rising/falling/stable/cyclical), highlighting peak and trough periods
4. **Peak annotation**: Highlight the periods with the highest and lowest search volume for quick peak/off-season identification
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters (e.g., date range exceeds 366 days)

## Important Limitations

- **Time span cap**: Single query `startDate` to `endDate` maximum 366 days; split into multiple queries if exceeding
- **Data granularity**: Weekly (7 days per data point), not daily
- **Search volume type**: Exact match search volume, not broad match
- **All parameters required**: `marketplace`, `keyword`, `startDate`, `endDate` -- all are mandatory

## User Expression & Scenario Quick Reference

**Applicable** -- Keyword search volume historical trend analysis:

| User Says | Scenario |
|-----------|----------|
| "How has this keyword's search volume changed" | Search volume trend query |
| "Does this category have seasonality" | Full year data for seasonal pattern analysis |
| "Is search volume rising or falling recently" | Recent trend assessment |
| "When is the peak season" | Peak period identification |
| "What was the search volume in Q4 last year" | Specified time period search volume query |
| "How popular is this keyword on the Germany marketplace" | Non-US marketplace search volume query |
| "Compare search volume between two time periods" | Peak/off-season or year-over-year comparison |

**Not applicable** -- Beyond keyword historical search volume scope:
- Keyword suggestions/expansion (requires keyword mining tools)
- Real-time/current search volume ranking (requires ABA or SIF tools)
- Keyword competition, CPC bids
- Product sales, listing analysis
- Non-Amazon platform search volume

**Boundary judgment**: When users say "search volume", "keyword popularity", or "market demand trends", if they specifically want to see how a keyword's search volume changes over a period of time (historical trend), this skill applies. If they want the current ranking or a list of trending keywords, it does not apply.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
