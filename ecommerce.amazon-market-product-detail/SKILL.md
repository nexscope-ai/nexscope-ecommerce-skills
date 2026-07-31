---
name: ecommerce.amazon-market-product-detail
description: Query Amazon product detail and historical trends by ASIN using Sorftime data, covering 14 marketplaces. Trigger when the user mentions Sorftime product detail, ASIN detail query, sales trends, price curves, price history, BSR ranking history, BSR trends, profit analysis, FBA fee analysis, gross margin, product trend analysis, daily/monthly sales, revenue trends, Deal promotion history, product detail, sales trend, price history, BSR ranking, profit analysis, FBA fees. Even if the user does not explicitly mention "Sorftime", if their need involves querying Amazon product detail or historical trend data by ASIN, this skill should also be triggered.
---

# Sorftime Product Detail

This skill guides you on how to query Amazon product detail and historical trend data by ASIN via Sorftime, helping Amazon sellers analyze product performance, pricing strategy, and competitive positioning.

## Core Concepts

Sorftime Product Detail provides comprehensive product-level data by ASIN, with historical trend data going back to 2021. It covers sales volume & revenue trends, price & promotion tracking, multi-level BSR ranking history, and real-time profit analysis with FBA fee breakdown.

**Key differentiator**: This tool returns trend/time-series data for individual products. If you need to search/filter products across a category, brand, or seller, use the Sorftime Product Search skill instead.

## Data Fields

Response data covers the following categories (see `references/api.md` for complete field reference):

- **Basic info**: title, brand, ASIN, listing URL, images (main + A+), store name, bullet points, product badges, off-sale status, last update date, weight, size
- **Variations**: parent ASIN, variation count, child ASINs, variation attributes
- **Pricing & profit**: sale price, coupon, platform fee, FBA fees (with detail breakdown), FBM shipping cost, profit amount & rate
- **Sales**: official monthly sales (Amazon-published)
- **Rankings**: BSR rank, category tree, sub-category rankings, listing date, days online
- **Ratings**: rating score, rating count, star distribution (1-5 star percentages)
- **Seller**: Buybox seller name/ID/country, FBA status, seller count
- **Listing features**: A+ content, video, brand store, feature ratings, product info, properties
- **Promotions**: brand promotion, deal type, extra savings
- **Trends** (time-series): BSR rank, sub-BSR rank, daily/monthly sales volume, daily/monthly revenue, price, list price, deal status

## Supported Marketplaces

US (United States), GB (United Kingdom), DE (Germany), FR (France), IN (India), CA (Canada), JP (Japan), ES (Spain), IT (Italy), MX (Mexico), AE (United Arab Emirates), AU (Australia), BR (Brazil), SA (Saudi Arabia)

Default marketplace is **US**. Use `us` when the user doesn't specify a marketplace.

**Note**: Sorftime uses lowercase codes (e.g., `us`, `gb`, `de`), and UK is coded as `gb` (not `uk`).

## How to Invoke

- **API Endpoint**: `POST /sorftime/amazon/productDetail` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_market_product_detail.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sorftime-amazon-product-detail-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

The key parameters are `asin` and `marketplace` (both required), plus optional trend date range controls.

### Principles for Building Queries

1. **Always specify the marketplace**: Use lowercase site codes, e.g., `us`, `de`, `jp`
2. **Choose trend inclusion carefully**: Default includes trends (last 15 days). Set `includeTrend: 2` if only basic product info is needed - this saves cost and speeds up response
3. **Specify date range for historical analysis**: Use `queryTrendStartDate` and `queryTrendEndDate` (yyyy-MM-dd) when users need trends beyond the default 15 days. Be aware this costs double
4. **Batch ASINs when comparing**: Up to 10 ASINs can be queried at once, comma-separated - use this for competitive comparison rather than calling one at a time

### Query Examples for Common Scenarios

**1. Quick product check (default 15-day trend)**
```
asin: B00FLYWNYQ, marketplace: us
```

**2. Long-range trend analysis (specify dates)**
```
asin: B00FLYWNYQ, marketplace: us
queryTrendStartDate: 2025-01-01, queryTrendEndDate: 2025-03-31
```

**3. Batch ASIN comparison**
```
asin: B0088PUEPK,B00U26V4VQ,B0CVM8TXHP, marketplace: us
```

**4. Product info only, no trends**
```
asin: B0088PUEPK, marketplace: us, includeTrend: 2
```

**5. BSR ranking history (German market)**
```
asin: B00FLYWNYQ, marketplace: de
queryTrendStartDate: 2024-06-01, queryTrendEndDate: 2025-01-01
```

## Trend Data Interpretation

Trend arrays use an interleaved format: even indices are dates, odd indices are values.

```
[20250101, 150, 20250102, 180, 20250103, 165, ...]
 ^date     ^val ^date     ^val ^date     ^val
```

- **Sales volume/revenue trends**: value of `-1` means "cannot estimate" (e.g., category changed to Amazon Renewed)
- **Price trends**: units are in local currency smallest unit (cents for USD); `-1` means no available price that day
- **BSR rank trends**: for `bsrRankTrend`, format is `[{NodeId: xxx, Rank: [date, rank, ...]}]` per sub-category
- **Deal trend**: value `1` = has active Deal that day, `0` = no Deal

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Price unit awareness**: Trend data uses smallest currency unit (cents for USD). Convert to standard currency when displaying to users
4. **Sales estimation caveat**: Values of `-1` in sales/revenue fields mean "cannot estimate" - explain this to the user rather than showing -1 directly
5. **Trend visualization**: When showing trend data, present key data points in a readable table rather than dumping raw arrays
6. **Off-sale handling**: When `offSale` is true, clearly inform the user the product is currently unavailable/off-sale
7. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria

## Important Limitations

- **Max 10 ASINs** per query
- **Trend cost**: Default returns last 15 days; querying > 15 days costs double
- **Non-structured data**: Results do not support secondary analysis via `_dataQuery_executeDynamicQuery`
- **Sales estimation**: Products in non-standard categories (e.g., Amazon Renewed) may return -1 for sales fields

## User Expression & Scenario Quick Reference

**Applicable** -- Product detail and trend queries by ASIN:

| User Says | Scenario |
|-----------|----------|
| "Check the sales trend for this ASIN" | Sales trend |
| "How has this product's price changed recently" | Price history |
| "Help me see the profit margin for this product" | Profit analysis |
| "BSR ranking trend for this ASIN" | Ranking history |
| "Compare data across these ASINs" | Multi-ASIN comparison |
| "What's the FBA fee for this product" | FBA fee breakdown |
| "How long has this product been listed, what's the rating" | Basic product info |
| "Is this product still on sale" | Off-sale status check |
| "Does this product have Deal promotion history" | Deal history |
| "Show me the variant information for this product" | Variation details |

**Not applicable** -- Needs beyond single-product detail:
- Searching/filtering products across a category or brand (use Sorftime Product Search)
- ABA search term ranking data (use ABA Data Explorer)
- Advertising / PPC strategy
- Product reviews content analysis
- Patent or trademark checks

**Boundary judgment**: When users say "product analysis" or "competitor comparison", if it boils down to checking specific ASINs' detail data and trend curves, then this skill applies. If they're asking to discover or filter products across a market, it does not apply.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://os.nexscope.com/ to top up credits.
