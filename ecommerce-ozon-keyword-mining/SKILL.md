---
name: ecommerce-ozon-keyword-mining
description: "Seerfar Ozon keyword mining: mines Ozon (and Wildberries) related keywords around a seed keyword with multi-dimensional filtering by search volume, growth, product count, seller count, competitor count, price, relevancy, title density, cart-add conversion, etc. Each mined keyword carries a full market profile (monthly search volume, growth, market space, competitor/seller counts, average price, cart-add conversion, top products). Use for Ozon keyword expansion, long-tail keyword mining, and seed keyword opportunity analysis. Trigger when the user mentions Ozon keyword mining, Ozon keyword expansion, Ozon long-tail keyword mining, find related keywords around a term, Ozon blue-ocean keyword mining, Seerfar Ozon, Ozon keyword mining, Ozon keyword expansion, Ozon related keywords, mine Ozon keywords. Also trigger when the intent is to mine Ozon related keywords around a seed term and view market profiles, even without explicitly mentioning Seerfar."
---

# Seerfar Ozon Keyword Mining

This skill mines Ozon marketplace keywords **around a seed keyword** in the Seerfar analytics database and filters the discovered terms by rich performance metrics — search volume, 30-day growth, product/seller/competitor counts, average price, relevancy, title density, cart-add conversion, and more. Each mined keyword carries a full market profile (market space, return/cancellation rate, top products, Chinese translation), making it the starting point for Ozon keyword expansion, long-tail discovery, and seed-term opportunity analysis.

## Core Concepts

**Seed-driven, not market-browse**: unlike a market keyword search, this endpoint requires a `keyword` (the seed) and returns terms *related to* that seed, each enriched with market metrics. You expand *outward from a term you already have in mind*.

**Relevancy is the mining signal**: `relevancy` scores how closely a mined term relates to the seed (the seed term itself returns at `relevancy: 100`, related terms rank lower); `titleDensity` reflects how densely the term appears in product titles. Both are populated on every row — sort by `relevancy` DESC to keep expansions on-topic.

**Platform coverage**: each keyword record carries a `platform` field (`0` = Ozon, `1` = Wildberries). The dataset is Ozon-centric; Wildberries rows appear where available. There is no input to restrict the platform — filter client-side if needed.

**Match mode**: `matchType` controls how the seed `keyword` (and `includeKeywords`) are matched — `0` exact, `1` fuzzy. Choose fuzzy to broaden the expansion, exact to stay tight.

**No date or category selectors**: this endpoint does not accept `searchDate` or `categories`. If you need month-over-month or category-scoped browsing, use the market keyword search skill instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | yes | Seed keyword; mining expands around it (maxLength 1000). |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. `page` from 1 (default 1), `pageSize` default 20. `orders[]` = `{field, direction}` with `direction` `DESC`/`ASC`. |
| matchType | integer | no | Keyword match mode: `0` exact, `1` fuzzy. |
| includeKeywords | array<string> | no | Terms that must appear (max 1000); narrows the expansion. |
| excludeKeywords | array<string> | no | Terms to exclude (max 1000); removes irrelevant expansions. |
| wordCount | {min,max} | no | Keyword word/char count range. |
| searchVolume | {min,max} | no | Monthly search volume range. |
| searchChange30 | {min,max} | no | 30-day search change range. |
| productViews | {min,max} | no | Product view range. |
| products | {min,max} | no | Product count range. |
| sellers | {min,max} | no | Seller count range. |
| price | {min,max} | no | Average price range. |
| marketSpace | {min,max} | no | Market space range. |
| conversionSharing | {min,max} | no | Conversion concentration range. |
| relevancy | {min,max} | no | Relevancy-to-seed range. |
| uniqQueriesWCa | {min,max} | no | Cart-add count range. |
| ca | {min,max} | no | Cart-add conversion rate range. |
| titleDensity | {min,max} | no | Title density range. |
| adRivalCount | {min,max} | no | Ad competitor count range. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

All range filters are `{min, max}` objects; supply either or both bounds. `keyword` and `page` are both required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/keywordMining` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_keyword_mining.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-ozon-keyword-mining-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Expand around a seed term (sort by search volume)**
```json
{"keyword": "платье", "page": {"page": 1, "pageSize": 10, "orders": [{"field": "searchVolume", "direction": "DESC"}]}}
```

**2. Blue-ocean expansions — high volume, few sellers**
```json
{"keyword": "телефон", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "searchVolume", "direction": "DESC"}]}, "searchVolume": {"min": 10000}, "sellers": {"max": 50}}
```

**3. Keep expansions on-topic with relevancy + title density**
```json
{"keyword": "наушники", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "relevancy", "direction": "DESC"}]}, "relevancy": {"min": 50}}
```

**4. Narrow with include / exclude lists**
```json
{"keyword": "часы", "page": {"page": 1, "pageSize": 20}, "includeKeywords": ["женские"], "excludeKeywords": ["ремень"], "matchType": 1}
```

## How to Build Queries

1. **Always lead with the seed `keyword`**: it is required and defines the expansion center. Pass it in Russian for Ozon.
2. **Lead with `page.orders`**: sort by the metric you care about (`searchVolume` DESC for popularity, `relevancy` DESC for on-topic, `sellers` ASC for low competition).
3. **Stack range filters to find opportunities**: combine a high `searchVolume` floor with a low `sellers` ceiling to surface blue-ocean expansions; add `relevancy` / `titleDensity` bounds to keep them relevant to the seed.
4. **Use `includeKeywords` / `excludeKeywords` to steer the expansion**: force in must-have modifiers and strip noise without running a second query.

## Display Rules

1. **Present data only**: show mined-keyword metrics in a clear table without subjective advice.
2. **Lead with keyword columns**: `query` / `queryCn` (Chinese translation), then `searchVolume`, `count30GrowthRate`, `productCount`, `sellers`, `avgPrice`; show `relevancy` to convey closeness to the seed (the seed term itself is `100`).
3. **Russian keywords**: preserve the original `query`; the `queryCn` field provides a Chinese translation when available.
4. **Platform tag**: when both Ozon and Wildberries rows are present, show `platform` (0/1) so the user can distinguish them.
5. **Large result sets**: when `total` is large, show the top rows and remind the user they can persist the full response via the large-response pattern below, or page further with `page.page`.
6. **Error handling**: when `code` is not `200` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest adjusting the seed keyword or filters.

## Important Limitations

- **`keyword` + `page` required**: a payload missing either is rejected.
- **No date selector**: there is no `searchDate`; you cannot pick a data month here. Use the market keyword search skill for month-scoped data.
- **No category selector**: `categories` is not accepted as input; each returned keyword carries a `categories` ID array you can group or filter client-side.
- **`dimension` / `categoryInfos` not returned**: both are defined in the schema and appear as `columns`, but real `data[*]` rows do not populate them on this endpoint. (`categoryInfos` IS populated on the sibling market-keyword-search endpoint — don't assume parity.)
- **Nested fields**: `products[*]` (Top Products) is structured and decision-useful — see `references/api.md` for sub-fields. (`categoryInfos[*]` is documented there for schema completeness but is not returned on this endpoint; `dimension` / `columns` are opaque or partially populated.)

## User Expression & Scenario Quick Reference

**Applicable** — seed-driven Ozon keyword expansion:

| User Says | Scenario |
|-----------|----------|
| "Mine Ozon related keywords around term XX" | Seed-keyword expansion |
| "Ozon long-tail keyword mining / expansion around a term" | Long-tail mining around a seed |
| "Ozon blue-ocean expansion for a term: low competition, high search" | Blue-ocean expansion (high volume, few sellers) |
| "Ozon keywords related to XX, sorted by relevancy" | Relevancy-ranked expansion |
| "Ozon keyword expansion with include/exclude filters" | Include/exclude steered expansion |

**Not applicable** — Needs beyond seed-driven keyword mining:
- Browse/rank the whole market's hot keywords without a seed → use the Seerfar Ozon market keyword search skill.
- A specific SKU's price/sales/stock → use a product-level Seerfar Ozon data source.
- A specific seller's catalog → use a seller/shop-level Seerfar Ozon data source.
- Month-over-month or category-scoped keyword browsing → use the market keyword search skill (supports `searchDate` / `categories`).

**Boundary judgment**: if the user wants to **expand outward from a seed term** and rank the related terms by market metrics, start here. If they want to **browse the whole market** of keywords (no seed) or scope by month/category, route to the market keyword search skill.
