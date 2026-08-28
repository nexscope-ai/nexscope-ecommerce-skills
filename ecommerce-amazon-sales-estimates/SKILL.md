---
name: ecommerce-amazon-sales-estimates
description: "Jungle Scout ASIN sales estimates query, returning daily estimated sales and latest known price for a specified ASIN over a given time period, covering 10 marketplaces including US, UK, Germany, and Japan. Triggered when users mention ASIN sales estimates, ASIN daily sales, sales estimation, competitor sales monitoring, average daily sales, sales trends, product sales tracking, Jungle Scout sales data, sales estimates, daily sales, estimated units sold, ASIN sales tracking, competitor sales monitoring, product sales trend, daily unit sales. Even if users do not explicitly mention \"Jungle Scout\", this skill should be triggered whenever the task involves viewing daily estimated sales data for an Amazon ASIN over a time period."
---

# Jungle Scout -- ASIN Sales Estimates

This skill queries daily sales estimates and last known price for a given Amazon ASIN via the Jungle Scout data source, returning day-level data points over a specified date range across 10 Amazon marketplaces.

## Core Concepts

The Jungle Scout ASIN Sales Estimates tool provides **daily estimated unit sales** and **latest known price** for a single ASIN across Amazon marketplaces. Sellers can query sales changes within a specified date range to:

- **Monitor competitor sales**: Understand competitor daily order volumes and assess their market share
- **Validate product opportunities**: Use actual sales data to verify if product demand is sufficient
- **Track seasonal patterns**: Observe sales fluctuations across months to identify peak and off-peak seasons
- **Assess pricing impact**: Analyze the relationship between price and sales changes to inform pricing decisions
- **Track new product performance**: Follow the sales ramp-up curve after a new listing launches

**Data granularity**: Each record represents **1 day**, containing estimated units sold and latest known price (USD).

## Data Fields

### Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ASIN | asin | Queried ASIN | B0CXXX1234 |
| Data ID | id | Data point identifier | sales_estimate_B0CXXX1234_20260301 |
| Resource Type | type | Fixed value | sales_estimate_result |
| Parent ASIN | parentAsin | Parent ASIN (for variants) | B0CXXX0000 |
| Is Parent | isParent | Whether this is a parent product | true / false |
| Is Variant | isVariant | Whether this is a variant product | true / false |
| Is Standalone | isStandalone | Whether this is a standalone product (non-variant) | true / false |
| Variant List | variants | Array of variant ASINs under this parent | ["B0CX1", "B0CX2"] |
| Daily Estimates | dailyEstimates | Array of daily data points | See below |
| Cost Token | costToken | Tokens consumed by this call | 1 |

### Each Object in dailyEstimates Array

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Date | date | Data date (YYYY-MM-DD) | 2026-03-15 |
| Estimated Daily Sales | estimatedUnitsSold | Estimated units sold that day | 42 |
| Latest Known Price | lastKnownPrice | Latest known price (USD) | 29.99 |

## Supported Marketplaces

10 Amazon marketplaces: `us` (United States), `uk` (United Kingdom), `de` (Germany), `in` (India), `ca` (Canada), `fr` (France), `it` (Italy), `es` (Spain), `mx` (Mexico), `jp` (Japan). Default marketplace is **us**. Use us when the user does not specify a marketplace.

## API Invocation

- **API Endpoint**: `POST /tool-jungle-scout/sales-estimates/query` (see `references/api.md` for full parameters/responses/error codes)
- **Python Script**: `python scripts/amazon_sales_estimates.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination in the same session is only called once by default, with 24h local caching in the script. Failed or empty results should not trigger automatic retries with different keywords, pagination, or postal codes. Inform the user before making additional queries that will incur extra costs.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-junglescout-sales-estimates-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body less than or equal to 8 KB: print the full JSON to stdout after saving to disk
- Response body greater than 8 KB: after saving, stdout prints only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data Reading Tips**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## How to Build Queries

All four parameters are **required**: `marketplace`, `asin`, `startDate`, `endDate`.

### Principles for Building API Calls

1. **Marketplace mapping**: "US marketplace" -> `us`, "Japan marketplace" -> `jp`, "Germany marketplace" -> `de`; default to `us` when not specified
2. **Date format**: Must be `YYYY-MM-DD`, e.g., `2026-03-01`
3. **endDate restriction**: `endDate` must be before the current date (cannot include today or future dates)
4. **ASIN format**: Standard Amazon ASIN, typically starting with B0, 10 characters total
5. **Common time ranges**:
   - "Past 30 days" -> endDate is yesterday, startDate is 30 days before
   - "Last month" -> 1st to last day of the previous month
   - "Q3 vs Q4" -> two separate calls for Jul-Sep and Oct-Dec

### Common Query Scenarios

**1. Monitor competitor sales over the past 30 days**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX1234",
  "startDate": "2026-03-18",
  "endDate": "2026-04-16"
}
```

**2. Compare Q3 vs Q4 sales performance**

Two separate calls:
- Q3: `startDate=2025-07-01`, `endDate=2025-09-30`
- Q4: `startDate=2025-10-01`, `endDate=2025-12-31`

**3. Validate product opportunity -- view full-year sales**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX5678",
  "startDate": "2025-04-01",
  "endDate": "2026-03-31"
}
```

**4. Track new product launch performance**
```json
{
  "marketplace": "de",
  "asin": "B0DYYY9999",
  "startDate": "2026-01-15",
  "endDate": "2026-04-15"
}
```

**5. Monitor sales during major promotion events (e.g., Prime Day)**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX1234",
  "startDate": "2025-07-01",
  "endDate": "2025-07-21"
}
```

## Display Rules

1. **Line chart preferred**: Use a line chart to display daily sales changes, with date on the X-axis and estimated daily sales on the Y-axis; if price data is available, overlay a second Y-axis to show price trends
2. **Table as supplement**: Also provide a data table for precise lookup, with columns: Date, Estimated Sales, Latest Known Price
3. **Summary statistics**: After the data, summarize key metrics -- total sales, average daily sales, estimated total revenue (total sales x average price)
4. **Trend summary**: Briefly summarize the trend direction (rising/falling/stable/seasonal fluctuations), and highlight peak and trough dates
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters (e.g., endDate must not include today or future dates)

## Important Limitations

- **endDate cannot include today**: `endDate` must be before the current date; cannot query today's or future sales
- **Single ASIN per call**: Each call queries only one ASIN; comparing multiple ASINs requires multiple calls
- **All parameters required**: `marketplace`, `asin`, `startDate`, `endDate` are all mandatory
- **Price is in USD**: `lastKnownPrice` is denominated in USD, not local currency

## User Expression and Scenario Quick Reference

**Applicable** -- ASIN sales estimates and sales trend analysis:

| User Says | Scenario |
|-----------|----------|
| "How many units does this ASIN sell per day" | Query recent daily sales estimates |
| "How is my competitor selling lately" | Monitor competitor sales over the past 30 days |
| "Does this product have seasonality" | Full-year sales data to assess seasonal patterns |
| "Show me the sales trend for this product" | Sales trend over a specified time range |
| "How are Q4 peak season sales" | Specific quarter sales query |
| "Is this product worth pursuing" | Validate product opportunity via historical sales |
| "How many units sold during the promotion event" | Sales monitoring during promotional periods |

**Not applicable** -- Beyond ASIN sales estimate scope:

- Keyword search volume (requires keyword historical search volume tool)
- BSR rank history (requires BSR tracking tool)
- Category-wide sales / market size
- Non-Amazon platform sales data
- Real-time/current moment sales (data has a lag and does not include today)

**Boundary judgment**: When users say "sales", "daily sales", or "how many sold", if they want to see a specific ASIN's daily estimated sales over a time range, this skill applies. If they want keyword search volume, category rankings, or real-time live sales, it does not apply.
