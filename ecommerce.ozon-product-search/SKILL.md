---
name: ecommerce.ozon-product-search
description: MPSTATS Ozon Russia product search and reverse lookup. Searches Ozon products in the MPSTATS database by Russian keyword or SKU, returning product ID, title, brand, and seller information. The entry point for Ozon product discovery and competitor analysis chains. Trigger when the user mentions Ozon product selection, Ozon product search, Russian e-commerce product selection, Ozon keyword search, Ozon SKU query, MPSTATS Ozon, Ozon product search, MPSTATS Ozon, Russian marketplace, Ozon SKU lookup, Ozon keyword search. Also trigger when the intent is to discover or reverse-lookup products on Ozon Russia by keyword or SKU, even without explicitly mentioning MPSTATS.
---

# MPSTATS Ozon Product Search

This skill searches Ozon (Russia) products in the MPSTATS analytics database by Russian keyword or SKU list. It is the **entry point** for Ozon product discovery and competitor lookup — downstream drill-downs (brand/category/seller/detail/trend) typically start from the IDs returned here.

## Core Concepts

**MPSTATS Ozon coverage**: Ozon is Russia's largest general-category marketplace. MPSTATS indexes Ozon product listings and sales history. This endpoint returns the **basic identity card only** — 10 fields: `productId` / `title` / `productPageUrl` / `imageUrl` / `brand` / `brandId` / `sellerName` / `sellerId` plus `sourceType` / `sourceTool`. Per-SKU price / sales / rating / stock / turnover / ranking are **not** returned here — the backend `OzonProductSearchItem` DTO is intentionally narrow. For those metrics, chain into `ecommerce.ozon-product-detail` (batch full card, 36 fields) or the `brand/category/seller-products` drill-downs (39 fields).

**Language requirement**: Keywords must be in **Russian** (Cyrillic) — or the Latin-script form actually used on the Ozon storefront. If the user supplies an English or Chinese keyword, translate it to Russian first and note the translation.

**At-least-one input rule**: The input schema marks both filters as optional, but the tool's business rule requires at least one of `keyword` / `productIds` to be supplied. The two can be combined to narrow results. For brand- or seller-scoped discovery, use `ecommerce.ozon-brand-products` / `ecommerce.ozon-seller-products` instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | conditional | Russian search keyword, e.g., `кроссовки` (sneakers) |
| productIds | array<integer\|string> | conditional | Ozon SKU list |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; defaults to one year ago |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; defaults to yesterday, **cannot** be today or future |

At least one of `keyword` / `productIds` must be supplied. The endpoint returns at most ~36 records in a single call (an upstream-acknowledged cap), and there are no pagination / sort / filter inputs — narrow via keyword/SKU and date window instead.

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/productSearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_product_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-product-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Keyword search — sneakers in Russian**
```json
{"keyword": "кроссовки"}
```

**2. SKU batch reverse lookup**
```json
{"productIds": [1786874757, 151623766, 142257239]}
```

**3. Dated window for period-specific search**
```json
{"keyword": "футболка", "startDate": "2025-02-01", "endDate": "2025-02-28"}
```

## How to Chain with Other Ozon Skills

1. **Keyword → drill-down**: Search → pick `productId` → call `ecommerce.ozon-product-detail` (batch metrics) or `ecommerce.ozon-product-trend` (single-SKU time-series).
2. **Brand drill-down**: For brand-scoped product listings with full metrics, call `ecommerce.ozon-brand-products` directly with the brand display name.
3. **Seller drill-down**: For seller-scoped product listings with full metrics, call `ecommerce.ozon-seller-products` directly with the seller ID.

## Display Rules

1. **Lead with identity columns** — this endpoint returns only 10 identity fields. Headline the table with `productId`, `title`, `brand`, `sellerName`; include `productPageUrl` / `imageUrl` as secondary columns. Do **not** add price / sales / rating / stock columns — they are not in the response.
2. **Russian titles** — preserve the original Russian title; optionally offer an English or Chinese translation on user request.
3. **Result count** — the endpoint returns at most ~36 records and has no pagination. If `total` exceeds what was returned, suggest narrowing the keyword/SKU set or date window rather than asking for more pages.
4. **Route to drill-downs for any business metric** — business metrics are never in this response. If the user asks for sales / price / rating / stock / turnover / ranking, **always** route to `ecommerce.ozon-product-detail` (single or batch) or the `*-products` drill-downs. Do not fabricate or estimate from identity fields.
5. **Error handling** — when `code` / `errcode` is non-200, explain the reason from `msg` / `errmsg` and suggest adjusting inputs (supply at least one of `keyword` / `productIds`, use Russian, narrow date range).

## Important Limitations

- **At least one of `keyword` / `productIds` required** — empty payloads are rejected by the tool's business rule even though `required` is empty in inputSchema.
- **Russian / Latin only** — non-Russian keywords generally return empty results.
- **Date range** — `endDate` cannot be today or a future date; data is T-1.
- **Hard result cap** — upstream returns at most ~36 records per call and exposes no pagination/sort/filter. Cannot be bypassed; narrow the query instead.
- **No business metrics** — price / sales / rating / stock / turnover / ranking are **not** in this endpoint's response at all. The backend `OzonProductSearchItem` DTO declares exactly 10 identity fields. This is a hard contract, not a sparse payload — do not assume missing metric fields could be filled in by re-calling with different dates.

## User Expression & Scenario Quick Reference

**Applicable** — Ozon product discovery / identity resolution:

| User Says | Scenario |
|-----------|----------|
| "Search Ozon for sneakers / headphones / ..." | Keyword discovery |
| "I have a list of Ozon SKUs, pull their names" | Batch SKU reverse lookup |
| "Translate this keyword to Russian and search Ozon" | Cross-language discovery |

**Not applicable** — Needs beyond discovery:

- Reliable per-SKU sales / revenue / stock / rating metrics → use `ecommerce.ozon-product-detail` (batch card) or the `*-products` drill-down skills.
- Brand-scoped product listing → use `ecommerce.ozon-brand-products` directly.
- Seller-scoped product listing → use `ecommerce.ozon-seller-products` directly.
- Time-series trend for a single SKU → use `ecommerce.ozon-product-trend`.
- Wildberries or other non-Ozon Russian marketplaces → not covered here.
- Category-tree navigation / Russian category path lookup → use `ecommerce.ozon-category-products` with a known path.

**Boundary judgment**: If the user wants to **find or identify** Ozon products, start here. If they already have an ID or a dimension (brand / category / seller) and want **metrics** under it, go to the corresponding drill-down skill directly.
