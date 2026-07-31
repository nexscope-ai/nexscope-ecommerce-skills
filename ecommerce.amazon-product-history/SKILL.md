---
name: ecommerce.amazon-product-history
description: Retrieve Amazon product details by ASIN, including price, title, main image, listing date, material, weight, variant monthly sales, and up to 12 months of monthly sales history. Triggered when users query Amazon product details, ASIN lookup, product pricing, sales rank history, monthly sales trends, product dimensions, FBA fees, product specifications, batch ASIN query, Keepa product details, ASIN detail lookup, monthly sales data, pricing info, product specifications, FBA fees, batch ASIN query. Even if users do not explicitly mention "Keepa", this skill should be triggered whenever the task involves obtaining structured product data for one or more Amazon ASINs.
---

# Keepa Product Data Request

This skill guides you on how to retrieve Amazon product details via the Keepa product request API, helping Amazon sellers and analysts obtain structured product data for one or more ASINs across multiple Amazon marketplaces.

## Core Concepts

The Keepa Product Request API returns detailed product listing data from Amazon, sourced through Keepa. Given one or more ASINs and a marketplace, it returns comprehensive product information: pricing, title, main image, listing date, material, weight, dimensions, sales rank, monthly sales units (current and up to 12 months of history), FBA fees, ratings, review counts, category tree, and more.

**Key points**:
- You can query up to **5 ASINs** in a single request by separating them with commas.
- The `domain` parameter is a numeric marketplace ID (e.g., `1` = Amazon.com US), not a country code.
- Setting `history` to `1` includes historical sales data (monthly sales for up to 12 prior months, average sales rank over 30/90/180 days). Setting it to `0` returns only current product information.
- The response does **not** include product descriptions or reviews content.

## Parameter Guide

### domain (Required)

Numeric Amazon marketplace ID. The mapping is:

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

Default to **1** (US) when the user does not specify a marketplace.

### asin (Required)

One or more Amazon Standard Identification Numbers. For multiple ASINs, separate with commas. Maximum 5 ASINs per request, with a total string length limit of 300 characters.

### history (Optional)

Whether to include historical data such as monthly sales for the past 12 months and average sales rank over 30/90/180 days. Set to `1` to include history, `0` (default) for basic info only.

## Usage Examples

**1. Single ASIN lookup (US marketplace, basic info)**
```json
{"asin": "B0088PUEPK", "domain": "1"}
```

**2. Single ASIN with historical sales data**
```json
{"asin": "B0088PUEPK", "domain": "1", "history": 1}
```

**3. Batch lookup of multiple ASINs (Germany)**
```json
{"asin": "B0088PUEPK,B00U26V4VQ,B07M68S376", "domain": "3", "history": 1}
```

**4. Product lookup on Amazon Japan**
```json
{"asin": "B09V3KXJPB", "domain": "5", "history": 0}
```

**5. Competitor comparison across multiple ASINs (US, with sales history)**
```json
{"asin": "B0CXYZ1234,B0CXYZ5678,B0CXYZ9012,B0CXYZABCD", "domain": "1", "history": 1}
```

## API Invocation

- **API Endpoint**: `POST /keepa/productRequest` (see `references/api.md` for full parameters/responses/error codes)
- **Python Script**: `python scripts/amazon_product_history.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination in the same session is only called once by default, with 24h local caching in the script. Failed or empty results should not trigger automatic retries with different keywords, pagination, or postal codes. Inform the user before making additional queries that will incur extra costs.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-keepa-product-request-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body less than or equal to 8 KB: print the full JSON to stdout after saving to disk
- Response body greater than 8 KB: after saving, stdout prints only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data Reading Tips**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Display Rules

1. **Present data clearly**: Show product details in well-structured tables. Group related fields (e.g., dimensions together, sales data together) for readability.
2. **Price and currency**: Always display the price alongside its currency (e.g., "$29.99 USD"). The `currency` field in the response indicates the local currency.
3. **Sales trend**: When historical data is included, present the 12-month sales trend in a table or describe the trajectory (growing, declining, stable) to help users quickly assess momentum.
4. **Dimensions and weight**: Convert millimeter values to more intuitive units when appropriate (e.g., show both mm and inches, or mm and cm). Note that weight is in grams.
5. **Unavailable data**: Fields with value `0` or `-1` indicate data is unavailable. Do not display these as actual measurements; instead note "N/A" or omit them.
6. **Image display**: If `imageUrl` is present, display the product image to help users visually identify the product.
7. **Error handling**: When a query fails, explain the issue based on the response and suggest corrections (e.g., invalid ASIN format, unsupported marketplace).
8. **Large batch results**: For batch queries with many ASINs, present a summary table first and offer to show individual product details on request.
## Important Limitations

- **No product descriptions or reviews**: The API does not return product description text or review content.
- **Maximum 5 ASINs per request**: Batch queries are capped at 5 ASINs.
- **ASIN string length limit**: The `asin` parameter has a maximum length of 300 characters.
- **Historical data is optional**: Monthly sales history is only returned when `history` is set to `1`.
- **Data freshness**: The `lastUpdate` field indicates when the product data was last refreshed.

## User Expression and Scenario Quick Reference

**Applicable** -- Product data retrieval by ASIN:

| User Says | Scenario |
|-----------|----------|
| "Look up this ASIN", "Get product details for B0XXXXXXXX" | Single ASIN lookup |
| "What is the price of this product on Amazon" | Price query |
| "How many units does this product sell per month" | Monthly sales check |
| "Compare these ASINs", "batch lookup these products" | Multi-ASIN comparison |
| "Show me the sales trend for this ASIN" | Historical sales analysis |
| "What category is this product in" | Category / classification lookup |
| "Product dimensions", "how much does it weigh" | Physical specs query |
| "FBA fees for this product" | Fee estimation |
| "When was this product listed", "listing date" | Listing age / launch date |
| "Is this product FBA or FBM" | Fulfillment method check |

**Not applicable** -- Needs beyond ASIN-level product data:

- Search term / keyword analysis (use ABA data tools instead)
- Product reviews or listing copywriting content
- Advertising / PPC campaign data
- Seller account or store-level analytics
- Product research without specific ASINs (e.g., "find trending products in kitchen category")
- Price history charts or Buy Box history over time (only current and average rank data are available)

**Boundary judgment**: When users say "product research" or "competitor analysis", if they have specific ASINs and want structured product data (price, sales, dimensions, category), this skill applies. If they want keyword-level analysis, market-wide trends without specific ASINs, or advertising metrics, this skill does not apply.
