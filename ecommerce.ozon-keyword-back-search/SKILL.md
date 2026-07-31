---
name: ecommerce.ozon-keyword-back-search
description: Seerfar Ozon keyword reverse lookup: reverse-looks up Ozon (and Wildberries) search keywords by a list of product SKUs (up to 20), returning which search terms those products appear under (organic/ad search terms), with multi-dimensional filtering by search volume, growth, product count, seller count, competitor count, natural rank, ad rank, exposure, conversion, cart-add conversion, etc. Each keyword carries monthly search volume, growth, market space, competitor/seller counts, average price, cart-add conversion, top products, and organic/ad channel, rank, exposure, and conversion (dimension) market profiles. Use for Ozon keyword reverse lookup, listing keyword optimization, competitor traffic word mining, and ad keyword analysis. Trigger when the user mentions Ozon keyword reverse lookup, Ozon reverse keyword search, Ozon SKU keyword reverse, Ozon product traffic keywords, Ozon competitor ranking keywords, Ozon organic/ad keyword reverse lookup, Seerfar Ozon, Ozon keyword back search, Ozon reverse keyword lookup, Ozon SKU keyword reverse. Also trigger when the intent is to reverse-lookup Ozon search keywords by product SKU and view market profiles, even without explicitly mentioning Seerfar.
---

# Seerfar Ozon Keyword Back-Search

This skill reverse-looks-up Ozon search keywords **by a list of product SKU IDs** in the Seerfar analytics database: pass up to 20 SKUs (your own listing or a competitor's) and it returns the search terms those products appear under — organic and/or ad — each enriched with a full market profile (search volume, 30-day growth, product/seller/competitor counts, average price, conversion concentration, top products, plus per-term organic/ad channel, natural rank, exposure, and conversion in the `dimension` object). It is the starting point for Ozon keyword reverse lookup, listing-title optimization, and competitor traffic-word discovery.

## Core Concepts

**SKU-driven, not keyword-driven**: unlike keyword mining (expand *from* a seed term) or market keyword search (browse the whole market), this endpoint takes `skuIds` and returns the search terms *those specific products* rank for. The direction is product → keywords (reverse).

**`hasVariant` is required**: every request must declare whether to exclude variants — `0` keep variants, `1` exclude variants. Pick `1` when you want de-duplicated keyword coverage for a parent listing.

**Natural vs ad terms**: `type` filters the search-term channel — `["0"]` organic (organic search terms) only, `["1"]` ad (ad search terms) only; omit to get both. Combine with the `naturalRank` / `adRank` range filters to qualify positioning.

**Back-search metrics live in `dimension`**: each returned term carries a `dimension` object with the reverse-lookup-specific metrics — `type` (`0` organic / `1` ad), `naturalRank` (the SKU's natural rank for that term), `exposure` (exposure share, 0–1), `conversion` (conversion rate, 0–1), and `x` (opaque position indicator). The input filters `type` / `naturalRank` / `adRank` / `exposure` / `conversion` filter on these same per-term values. Note: `relevancy` is defined in the schema but is **not** returned by this endpoint.

**Platform coverage**: each keyword record carries a `platform` field (`0` = Ozon, `1` = Wildberries). The dataset is Ozon-centric; Wildberries rows appear where available. There is no input to restrict the platform — filter client-side if needed.

**Match mode**: `matchType` controls how `includeKeywords` / `excludeKeywords` are matched — `0` exact, `1` fuzzy.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| skuIds | array<integer> | yes | Reverse-lookup SKU list, max 20. |
| hasVariant | integer | yes | Variant exclusion: `0` keep variants, `1` exclude variants. |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| matchType | integer | no | Keyword match mode: `0` exact, `1` fuzzy. |
| type | array<string> | no | Search-term channel filter: `0` organic, `1` ad; omit for both. |
| historyDate | string | no | Historical month `yyyy-MM` (e.g. `2026-02`); omit for current period. |
| includeKeywords | array<string> | no | Terms that must appear (max 1000). |
| excludeKeywords | array<string> | no | Terms to exclude (max 1000). |
| searchVolume | {min,max} | no | Monthly search volume range. |
| searchChange30 | {min,max} | no | 30-day search change range. |
| wordCount | {min,max} | no | Keyword word/char count range. |
| productViews | {min,max} | no | Product view range. |
| products | {min,max} | no | Product count range. |
| sellers | {min,max} | no | Seller count range. |
| marketSpace | {min,max} | no | Market space range. |
| conversionSharing | {min,max} | no | Conversion concentration range. |
| uniqQueriesWCa | {min,max} | no | Cart-add count range. |
| ca | {min,max} | no | Cart-add conversion rate range. |
| conversion | {min,max} | no | Conversion rate range. |
| titleDensity | {min,max} | no | Title density range. |
| adRivalCount | {min,max} | no | Ad competitor count range. |
| adRank | {min,max} | no | Ad rank range. |
| naturalRank | {min,max} | no | Natural rank range. |
| exposure | {min,max} | no | Exposure range. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. `skuIds`, `hasVariant`, and `page` are all required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/keywordBackSearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_keyword_back_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-keyword-back-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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
2. If credits are insufficient, visit https://os.nexscope.com/ to top up your balance.
3. For onboarding and setup guidance, refer to https://skill.nexscope.com/nexscopeskills/guide.htm
## Usage Examples

**1. Reverse-lookup a single SKU's traffic keywords (sort by search volume)**
```json
{"skuIds": [4380710124], "hasVariant": 0, "page": {"page": 1, "pageSize": 10, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**2. Organic terms where the SKU ranks near the top**
```json
{"skuIds": [4380710124], "hasVariant": 1, "type": ["0"], "naturalRank": {"max": 10}, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**3. Ad search words only, with an ad-rank floor**
```json
{"skuIds": [4380710124], "hasVariant": 0, "type": ["1"], "adRank": {"max": 50}, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**4. Narrow with include / exclude lists**
```json
{"skuIds": [4380710124], "hasVariant": 0, "page": {"page": 1, "pageSize": 20}, "includeKeywords": ["платье"], "excludeKeywords": ["ремень"], "matchType": 1}
```

## How to Build Queries

1. **Always lead with `skuIds` + `hasVariant`**: both are required and define the reverse-lookup target. Use real Ozon SKU IDs (the same IDs returned by Seerfar Ozon product / shop / category skills).
2. **Lead with `page.orders`**: sort by the metric you care about (`searchVolume` DESC for traffic weight, `sellers` ASC for low competition, `count30GrowthRate` DESC for rising terms).
3. **Split organic vs ad with `type`**: pass `["0"]` or `["1"]` to focus a listing-optimization pass (organic) or an ads pass (ad), then bound `naturalRank` / `adRank` to qualify positioning — these filter on the values surfaced in each row's `dimension`.
4. **Use `includeKeywords` / `excludeKeywords` to steer**: force in must-have modifiers and strip noise without running a second query.

## Display Rules

1. **Present data only**: show reverse-looked-up keyword metrics in a clear table without subjective advice.
2. **Lead with keyword columns**: `query` / `queryCn` (Chinese translation), then `searchVolume`, `count30GrowthRate`, `productCount`, `sellers`, `avgPrice`; show `dimension.naturalRank` and `dimension.type` (organic/ad) to convey how the SKU ranks for each term.
3. **Russian keywords**: preserve the original `query`; the `queryCn` field provides a Chinese translation when available.
4. **Channel tag**: when `type` is omitted and both organic and ad rows are present, show `dimension.type` (`0` organic / `1` ad) and `dimension.naturalRank` so the user can distinguish them.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting the SKU list or filters.

## Important Limitations

- **`skuIds` + `hasVariant` + `page` required**: a payload missing any of these is rejected.
- **`skuIds` capped at 20**: pass more than 20 and the request is rejected or truncated.
- **No keyword seed**: this endpoint has no `keyword` parameter — it is reverse (SKU → keywords), not expansion (keyword → keywords). Use the keyword mining skill to expand from a seed.
- **No `searchDate` / `categories` input**: only `historyDate` (historical month) is accepted; there is no category filter. Use the market keyword search skill for month- or category-scoped browsing.
- **Nested fields**: `products[*]` (Top Products) and `dimension` (per-term back-search metrics: `type`, `naturalRank`, `exposure`, `conversion`, `x`) are structured and decision-useful — see `references/api.md` for sub-fields. `categoryInfos` is defined in the schema/columns but is **not** returned in `data[*]` on this endpoint (same as the keyword-mining sibling; the market-keyword-search sibling does return it — don't assume parity). `relevancy` is likewise defined in the schema but **not** returned.

## User Expression & Scenario Quick Reference

**Applicable** — SKU-driven Ozon keyword reverse lookup:

| User Says | Scenario |
|-----------|----------|
| "Reverse-lookup keywords for this Ozon product / SKU" | Reverse keyword lookup for a SKU |
| "Which search terms drive traffic to this Ozon listing" | Traffic-word discovery for a listing |
| "Ozon competitor SKU ranking/traffic keywords" | Competitor traffic-word mining |
| "Ozon product organic vs ad keywords" | Organic vs ad term breakdown |
| "Ozon keyword reverse lookup by SKU" | Generic reverse keyword lookup |

**Not applicable** — Needs beyond SKU-driven reverse lookup:
- Browse/rank the whole market's hot keywords (no SKU) → use the Seerfar Ozon market keyword search skill.
- Expand outward from a seed keyword → use the Seerfar Ozon keyword mining skill.
- A specific SKU's price/sales/stock → use a product-level Seerfar Ozon data source.
- A specific seller's catalog → use the Seerfar Ozon shop search skill.
- Category-tree browsing → use the Seerfar Ozon category search skill.

**Boundary judgment**: if the user has a **product/SKU** (own or competitor) and wants the **search terms it ranks for**, start here. If they want to **browse the market** (no SKU) or **expand from a seed keyword**, route to the market keyword search or keyword mining skill respectively.
