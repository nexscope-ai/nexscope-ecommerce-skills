---
name: ecommerce.ozon-market-keyword-search
description: Seerfar Ozon market hot keyword search: filters Ozon (and Wildberries) market keywords by multi-dimensional metrics including search volume, growth, product count, seller count, competitor count, price, sales, conversion concentration, etc. Each keyword carries monthly search volume, growth, market space, competitor/seller counts, average price, cart-add conversion, top products, and market profile. Use for Ozon keyword selection, blue-ocean keyword mining, and market opportunity analysis. Trigger when the user mentions Ozon hot keywords, Ozon keyword market analysis, Ozon keyword selection, Ozon blue-ocean keywords, Ozon search volume, Wildberries keywords, Seerfar Ozon, Ozon market keyword search, Ozon keyword research, blue ocean keywords Ozon. Also trigger when the intent is to filter Ozon market keywords by metrics and view market profiles, even without explicitly mentioning Seerfar.
---

# Seerfar Ozon Market Keyword Search

This skill searches Ozon marketplace keywords in the Seerfar analytics database and filters them by rich performance metrics — search volume, 30-day growth, product/seller/competitor counts, average price, monthly sales/revenue, conversion & view concentration, ratings/reviews, and more. Each returned keyword carries a full market profile (market space, return/cancellation rate, top products, Chinese translation), making it the starting point for Ozon keyword selection, blue-ocean term mining, and market-opportunity analysis.

## Core Concepts

**Unit of data is the keyword, not the SKU**: unlike a product search, this endpoint returns marketplace search terms ("hot keywords"), each enriched with market metrics. You discover *which search terms* are worth targeting on Ozon.

**Platform coverage**: each keyword record carries a `platform` field (`0` = Ozon, `1` = Wildberries). The dataset is Ozon-centric; Wildberries rows appear where available. There is no input to restrict the platform — filter client-side if needed.

**Date semantics**: `searchDate` selects the data month. Pass `2026-04-01` to get March 2026 data; omit it for the last 30 days. Metrics such as `searchVolume` (monthly search volume) and `count30GrowthRate` (monthly search growth) are relative to the selected period.

**Match mode**: `matchType` controls how the `keywords` array is matched — `0` exact, `1` fuzzy. Choose the mode that fits your discovery intent when filtering by keyword text.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | object | yes | Pagination `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| keywords | array<string> | no | Keyword list to filter (max 1000); combined with `matchType`. |
| matchType | integer | no | Keyword match mode: `0` exact, `1` fuzzy. |
| searchDate | string | no | Data date `yyyy-MM-dd`; default last 30 days. `2026-04-01` → March 2026 data. |
| categories | array<string> | no | Category ID list (max 1000). |
| searchVolume | {min,max} | no | Monthly search volume range. |
| searchChange30 | {min,max} | no | 30-day search change range. |
| monthlySales | {min,max} | no | Monthly sales range. |
| monthlyRevenue | {min,max} | no | Monthly revenue range. |
| price | {min,max} | no | Average price range. |
| productViews | {min,max} | no | Product view range. |
| products | {min,max} | no | Product count range. |
| volume | {min,max} | no | Volume range. |
| marketSpace | {min,max} | no | Market space range. |
| conversionSharing | {min,max} | no | Conversion concentration range. |
| reviews | {min,max} | no | Review count range. |
| ratings | {min,max} | no | Rating range. |
| sellers | {min,max} | no | Seller count range. |
| weight | {min,max} | no | Weight range. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. Only `page` is required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/marketKeywordSearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_market_keyword_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-market-keyword-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
- Response body <= 8 KB: write to disk then print full JSON to stdout
- Response body > 8 KB: write to disk then print only a summary to stdout (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Reading data**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file as needed, avoiding loading the entire JSON into context.
## Authentication & Credits

If you encounter authentication or credit issues:

### Error conditions
- **API Key not configured**: The `NEXSCOPE_API_KEY` environment variable is not set.
- **HTTP 401 or 402 status code**
- **Insufficient credits/balance**: Response message indicates credit balance exhausted, quota exceeded, subscription expired, or recharge required.

### Resolution steps
1. Set the `NEXSCOPE_API_KEY` environment variable with a valid API key.
2. If credits are insufficient, visit https://www.nexscope.ai/pricing?co-from=skillNS to top up your balance.
3. For onboarding and setup guidance, refer to https://www.nexscope.ai/help/skills-external-access?co-from=skillNS
## Usage Examples

**1. Hottest keywords right now (sort by search volume)**
```json
{"page": {"page": 1, "pageSize": 10, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**2. Blue-ocean terms — high volume, few sellers**
```json
{"page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}, "searchVolume": {"min": 10000}, "sellers": {"max": 50}}
```

**3. Filter by keyword text (fuzzy, Russian)**
```json
{"page": {"page": 1, "pageSize": 20}, "keywords": ["телефон"], "matchType": 1}
```

**4. A specific data month with a sales floor**
```json
{"page": {"page": 1, "pageSize": 20}, "searchDate": "2026-04-01", "monthlySales": {"min": 1000}}
```

## How to Build Queries

1. **Lead with `page.orders`**: the dataset is large — always sort by the metric you care about (`searchVolume` DESC for popularity, `count30GrowthRate` DESC for rising terms, `sellers` ASC for low competition).
2. **Stack range filters to find opportunities**: combine a high `searchVolume` floor with a low `sellers` ceiling to surface blue-ocean keywords; add `conversionSharing` / `marketSpace` bounds to qualify demand.
3. **Use `keywords` + `matchType` to scope a niche**: pass seed terms in Russian with `matchType: 1` (fuzzy) to enumerate related long-tail terms.
4. **Pick the right `searchDate`**: omit it for current trends (last 30 days); pass an explicit date for month-over-month comparison.

## Display Rules

1. **Present data only**: show keyword metrics in a clear table without subjective advice.
2. **Lead with keyword columns**: `query` / `queryCn` (Chinese translation), then `searchVolume`, `count30GrowthRate`, `productCount`, `sellers`, `avgPrice`.
3. **Russian keywords**: preserve the original `query`; the `queryCn` field provides a Chinese translation when available.
4. **Platform tag**: when both Ozon and Wildberries rows are present, show `platform` (0/1) so the user can distinguish them.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting filters.

## Important Limitations

- **`page` is required**: a payload without `page` is rejected.
- **No platform selector**: the Ozon/Wildberries mix is controlled server-side; filter client-side via the `platform` field.
- **Category IDs are opaque**: `categories` requires Seerfar category IDs, not human-readable names.
- **Pagination caps**: use `pageSize` and `page` to page; very large `pageSize` values may be capped server-side.
- **Nested fields**: `products[*]` (Top Products) and `categoryInfos[*]` (category path and cross-border availability flag) are structured and decision-useful — see `references/api.md` for sub-fields. `dimension` / `columns` are opaque or partially populated; `relevancy` / `titleDensity` / `wordCount` are usually absent.

## User Expression & Scenario Quick Reference

**Applicable** — Ozon keyword market research:

| User Says | Scenario |
|-----------|----------|
| "What are the Ozon hot / trending keywords" | Hottest keywords by search volume |
| "Ozon blue-ocean terms: low competition, high search volume" | Blue-ocean term mining (high volume, few sellers) |
| "Ozon rising keywords / fast-growing terms" | Rising keywords (growth sort) |
| "Long-tail keywords around a Russian seed term" | Fuzzy keyword expansion |
| "Market space / competitor count / seller count for an Ozon keyword" | Keyword market profile |

**Not applicable** — Needs beyond keyword market data:
- A specific SKU's price/sales/stock → use a product-level Seerfar Ozon data source, not this keyword endpoint.
- A specific seller's catalog → use a seller/shop-level Seerfar Ozon data source.
- Category-tree browsing → use a category-level Seerfar Ozon data source.
- Non-Ozon/Wildberries marketplaces → not covered here.

**Boundary judgment**: if the user wants to **discover and rank search terms** on Ozon by market metrics, start here. If they already have a SKU / seller / category and want entities under it, route to the corresponding Seerfar Ozon data source.
