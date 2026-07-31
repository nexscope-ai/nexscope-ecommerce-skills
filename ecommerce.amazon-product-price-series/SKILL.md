---
name: ecommerce.amazon-product-price-series
description: Query Amazon product historical time-series data, including price trends, BSR (Best Sellers Rank) trends, rating changes, seller counts, and monthly sales, supporting any ASIN across multiple Amazon marketplaces. Triggered when users mention price history, price tracking, BSR history, BSR trends, historical pricing, price fluctuations, Keepa data, rank history, price drop alerts, lightning deal historical prices, Buy Box price trends, coupon prices, FBA/FBM price comparison, seller count changes, rating trends, sales history. Even if users do not explicitly mention "Keepa" or "time-series data", this skill should be triggered whenever the task involves analyzing Amazon product-level historical data (such as price, rank, or sales trends over time).
---

# Keepa Product Time-Series Data Explorer

This skill guides you on how to query and analyze Amazon product historical time-series data, helping Amazon sellers track price movements, BSR trends, rating changes, and other key product metrics over time.

## Core Concepts

This tool provides historical time-series data for individual Amazon products (ASINs) powered by Keepa. It returns timestamped data points for various metrics, allowing trend analysis over a configurable time window (up to 365 days). Each query targets a single ASIN in a specific Amazon marketplace.

**Time-series format**: All data series are returned as arrays of `{time, value}` objects, where `time` is a timestamp and `value` is the metric at that point. BSR data includes a `categoryName` field along with a `points` array.

**BSR logic**: A smaller BSR value means a better sales rank. Rank 1 is the top-selling product in its category. When a user says "BSR improved", it means the numeric value decreased; "BSR dropped" means the value increased.

## Available Data Series

| Series | Parameter | Description |
|--------|-----------|-------------|
| Buy Box Price | *(always returned)* | Buy Box price over time |
| Lowest New Price | showPrice=1 | Lowest marketplace new item price |
| List Price | showPriceList=1 | Strikethrough / list price |
| Deal Price | showPriceDeal=1 | Lightning deal price |
| Prime Exclusive Price | showPricePrime=1 | Prime-exclusive new item price |
| FBA Price | showPriceFba=1 | Third-party FBA new item price |
| FBM Price | showPriceFbm=1 | Third-party FBM new item price |
| Coupon Price | showPriceCoupon=1 | Post-coupon Buy Box price |
| Main Category BSR | showBsrMain=1 | Best Sellers Rank in the main (root) category |
| Seller Count | showSellerCount=1 | Number of active sellers |
| Rating | *(always returned)* | Product star rating over time |
| Rating Count | *(always returned)* | Number of ratings over time |
| Monthly Sales | *(always returned)* | Monthly unit sales volume |
| Sub-category BSR | *(always returned)* | Best Sellers Rank in sub-categories |

## Supported Marketplaces

| Domain ID | Marketplace |
|-----------|-------------|
| 1 | Amazon.com (US) |
| 2 | Amazon.co.uk (UK) |
| 3 | Amazon.de (Germany) |
| 4 | Amazon.fr (France) |
| 5 | Amazon.co.jp (Japan) |
| 6 | Amazon.ca (Canada) |
| 8 | Amazon.it (Italy) |
| 9 | Amazon.es (Spain) |
| 10 | Amazon.in (India) |
| 11 | Amazon.com.mx (Mexico) |
| 12 | Amazon.com.br (Brazil) |

Default marketplace is **1** (US). Use domain=1 when the user does not specify a marketplace.

## API Invocation

- **API Endpoint**: `POST /keepa/productSeries` (see `references/api.md` for full parameters/responses/error codes)
- **Python Script**: `python scripts/amazon_product_price_series.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination in the same session is only called once by default, with 24h local caching in the script. Failed or empty results should not trigger automatic retries with different keywords, pagination, or postal codes. Inform the user before making additional queries that will incur extra costs.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-keepa-product-series-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body less than or equal to 8 KB: print the full JSON to stdout after saving to disk
- Response body greater than 8 KB: after saving, stdout prints only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data Reading Tips**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## Parameter Guide

### Required Parameters

- **asin**: The Amazon Standard Identification Number to query. Only a single ASIN per request is supported.
- **domain**: The Amazon marketplace domain ID (see table above). Always map the user's marketplace mention to the correct numeric ID.

### Optional Parameters

- **days**: Number of historical days to retrieve (1-365, default 90). Use 30 for short-term, 90 for medium-term, 365 for long-term analysis.
- **show\* flags**: Set any `show*` parameter to `1` to include that data series. By default, only the core series (Buy Box price, rating, rating count, monthly sales, sub-category BSR) are returned.

### How to Choose Parameters

1. **Price analysis**: Enable `showPrice`, `showPriceList`, `showPriceDeal`, `showPriceCoupon` as needed for the specific price comparison the user wants.
2. **FBA vs FBM comparison**: Enable both `showPriceFba` and `showPriceFbm`.
3. **BSR deep-dive**: Enable `showBsrMain` to get the root category BSR alongside the always-returned sub-category BSR.
4. **Competitive landscape**: Enable `showSellerCount` to see how many sellers are competing.
5. **Full product overview**: Enable all show flags for a comprehensive historical snapshot.

## Usage Examples

**1. Basic price history for a US product**
```
asin: B0XXXXXXXX, domain: 1, days: 90
```

**2. Long-term BSR trend (1 year) on the German marketplace**
```
asin: B0XXXXXXXX, domain: 3, days: 365, showBsrMain: 1
```

**3. Price comparison across fulfillment channels**
```
asin: B0XXXXXXXX, domain: 1, days: 30, showPriceFba: 1, showPriceFbm: 1, showPrice: 1
```

**4. Deal and coupon price tracking**
```
asin: B0XXXXXXXX, domain: 1, days: 90, showPriceDeal: 1, showPriceCoupon: 1
```

**5. Full product health check**
```
asin: B0XXXXXXXX, domain: 1, days: 90, showPrice: 1, showPriceList: 1, showPriceDeal: 1, showPricePrime: 1, showPriceFba: 1, showPriceFbm: 1, showPriceCoupon: 1, showBsrMain: 1, showSellerCount: 1
```

## Display Rules

1. **Present data clearly**: Show time-series data in tables or describe trends; avoid subjective business advice unless the user explicitly asks for it.
2. **BSR clarification**: When showing BSR data, remind users that lower values mean better (higher) sales ranks.
3. **Price formatting**: Display prices with proper currency symbols matching the marketplace ($ for US, EUR for DE/FR/ES/IT, GBP for UK, JPY for JP, etc.).
4. **Time formatting**: Present timestamps in a human-readable date format.
5. **Trend summarization**: When data series are long, summarize the overall trend (e.g., "price decreased from $29.99 to $24.99 over 90 days") and highlight significant changes such as price drops, BSR spikes, or rating shifts.
6. **Error handling**: When a query fails, explain the reason and suggest corrections (e.g., verify the ASIN is valid, check the marketplace domain ID).
7. **Single ASIN limitation**: If the user asks about multiple ASINs, inform them that queries must be made one ASIN at a time, and run multiple sequential calls.
## Important Limitations

- **Single ASIN per query**: Only one ASIN can be queried at a time. For multi-ASIN comparisons, make separate requests.
- **Maximum 365 days**: Historical data is limited to at most 365 days back.
- **Data granularity**: Data points are at irregular intervals depending on when Keepa captured changes, not at fixed daily intervals.

## User Expression and Scenario Quick Reference

**Applicable** -- Historical product-level data queries on Amazon:

| User Says | Scenario |
|-----------|----------|
| "What is the price history for this ASIN" | Price trend analysis |
| "Show me the BSR trend", "how is it ranking" | BSR tracking |
| "Has the price dropped recently", "any deals" | Price drop / deal detection |
| "How many sellers are on this listing" | Seller count trend |
| "What is the rating trend", "review count over time" | Rating / review tracking |
| "FBA vs FBM price", "who has the Buy Box" | Fulfillment price comparison |
| "Monthly sales for this product" | Sales volume trend |
| "Was there a price war on this ASIN" | Competitive pricing analysis |
| "Show me the Keepa chart", "Keepa data" | Explicit Keepa data requests |

**Not applicable** -- Needs beyond product-level historical data:

- Search term / keyword analysis (use ABA data instead)
- Advertising / PPC campaign data
- Listing copywriting or content optimization
- Category-wide or market-level aggregate trends (this tool is per-ASIN only)
- Real-time inventory or stock level checks
- Product reviews text or sentiment analysis

**Boundary judgment**: When users say "product research" or "competitor analysis", if it boils down to examining a specific ASIN's historical price, BSR, or sales data, this skill applies. If they need keyword data, market-wide trends, or advertising metrics, it does not apply.
