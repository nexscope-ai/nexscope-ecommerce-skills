---
name: ecommerce.ozon-product-detail
description: MPSTATS Ozon Russia SKU full detail batch query. Pass up to 100 Ozon product IDs at once, returning each SKU's price, discount, Ozon Card price, rating, review count, stock, sales, revenue, revenue potential/lost revenue, listing date, images, and complete product card. Trigger when the user mentions Ozon product detail, Ozon SKU detail, Ozon price/rating/sales/stock check, batch Ozon SKU query, competitor Ozon basic data pull, Ozon competitor card, MPSTATS Ozon detail, Ozon SKU detail, Ozon product card, Ozon batch lookup, Russian marketplace product detail. Also trigger when the intent is to pull full product card data by Ozon SKU, even without explicitly mentioning MPSTATS.
---

# MPSTATS Ozon Product Detail (Batch)

This skill batch-fetches the full product card for one or more Ozon (Russia) SKUs via MPSTATS. Returned fields include price, Ozon Card price, discount, rating, reviews, stock, monthly sales units, monthly sales revenue, lost profit, potential revenue, first listing date, image, and more.

## Core Concepts

**Batch semantics**: Pass up to **100** `productIds` in a single call. The server fans out concurrently and automatically retries each failed SKU once; partial success is allowed, so a mixed list is normal.

**Fulfillment model per SKU**: Each product card carries `deliveryScheme`:
- `FBO` — Fulfillment by Ozon (stock in Ozon warehouses)
- `FBS` — Fulfillment by Seller (seller-shipped)

Pass `includeFbs: true` to allow FBS SKUs and FBS-scoped metrics into the response; `false` (or omitted) keeps the result FBO-centric. This switch applies to the whole batch.

**Previous-period comparison**: The card includes `previousSalesUnits` / `previousRevenue` — sales and revenue from the equal-length period immediately before `[startDate, endDate]` — ready for MoM / period-over-period diffs without extra calls.

**Revenue potential**: `revenuePotential` projects what the SKU could have earned if it had been in stock every day of the window; compare with `monthlySalesRevenue` to quantify stock-out drag, together with `lostProfit` / `lostProfitPercent`.

**Date window**: `startDate` / `endDate` define the period for all period-aggregated metrics. Latest selectable date is **yesterday** (T-1); today and future dates are rejected.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productIds | array<integer\|string> | yes | Ozon SKU list, up to **100** per call |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| includeFbs | boolean | no | `true` to include FBS data; `false` = FBO-only |

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/productDetail` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_product_detail.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-product-detail-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Single-SKU detail**
```json
{"productIds": [1786874757]}
```

**2. Batch lookup with period**
```json
{
  "productIds": [1786874757, 151623766, 142257239],
  "startDate": "2025-03-01",
  "endDate": "2025-03-31",
  "includeFbs": true
}
```

**3. FBO-only snapshot**
```json
{"productIds": [1786874757, 151623766], "includeFbs": false}
```

**4. SKUs discovered upstream — full card**
```json
{"productIds": [<list from ecommerce.ozon-product-search>]}
```

## How to Chain with Other Ozon Skills

1. **Search → detail**: Use `ecommerce.ozon-product-search` to resolve a keyword / brand / seller into `productId`s, then pass them here for full metrics.
2. **Detail vs trend**: This endpoint is a **period aggregate** per SKU; for day-by-day time-series on a single SKU, use `ecommerce.ozon-product-trend`.
3. **Detail vs drill-downs**: When the input dimension is a brand / category / seller (not a SKU list), prefer `brand-products` / `category-products` / `seller-products` — they already return aggregated metrics per SKU under that dimension.

## Display Rules

1. **Compact table** — lead with `productId`, `title`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `reviewCount`, `balance`, `deliveryScheme`, `firstDate`. Pull `revenuePotential` / `lostProfit` / `lostProfitPercent` in when the user asks about stock-out impact.
2. **Currency** — Ozon native currency is **RUB**; the `currency` field carries the symbol. Do not silently relabel.
3. **Partial success** — the response carries `successCount` / `failedCount` / `failures`; when `failedCount > 0`, list the failed `productId`s from `failures` to the user rather than silently dropping them.
4. **Period-over-period** — when both current and `previous*` fields are present, render them side-by-side or as diff; don't report a single-period number as "trend".
5. **With-stock vs all-days** — `salesPerDayWithStock` / `dailySalesRevenueWithStock` only count days that had inventory; distinguish from the plain `salesPerDay` / `dailySalesRevenue`.
6. **Delivery model** — prefer the per-SKU `deliveryScheme` value over assuming FBO; remind users when a batch mixes FBO and FBS.
7. **No business advice** — present data; do not extrapolate "this SKU is worth selling" without a wider analysis.

## Important Limitations

- **100-SKU batch cap** — split larger input lists and call multiple times; the Agent must paginate.
- **Ozon-only** — this tool does not cover Wildberries or other Russian marketplaces.
- **T-1 data** — `endDate` must not be today or future.
- **FBS coverage** — some categories have partial FBS coverage; if the input set is FBS-heavy, expect sparser cards.
- **Field set differs from brand/seller** — this endpoint does **not** return `brandId`, `country`, `category`, `minPrice` / `maxPrice` / `averagePrice`, `balanceFbs`, `frozenStocks`, `warehousesCount`, `daysInSite` / `daysInStock` / `turnoverDays`, `position` / `categoryPosition` / `revenueSharePercent`, `isFbs`. Use `brand-products` / `category-products` / `seller-products` if those are needed.
- **No translation** — titles are returned in Russian; translate on demand when presenting to Chinese / English users.

## User Expression & Scenario Quick Reference

**Applicable** — Per-SKU Ozon card lookup:

| User Says | Scenario |
|-----------|----------|
| "Pull Ozon details for these SKUs" | Batch card fetch |
| "What's the price / rating / stock of Ozon SKU 1786874757" | Single-SKU card |
| "Competitor's Ozon listings, give me sales & rating" | Competitor card audit |
| "Compare FBO vs FBO+FBS metrics for this SKU set" | Fulfillment-model comparison |

**Not applicable** — Needs beyond per-SKU card:

- Keyword-based discovery → use `ecommerce.ozon-product-search`
- Day-by-day time-series for one SKU → use `ecommerce.ozon-product-trend`
- Listing copy / reviews / images analysis beyond URL → out of scope
- Brand / category / seller drill-down with filters → use the matching drill-down skill

**Boundary judgment**: If the user already has a **SKU list** and wants per-SKU sales / price / stock / rating, this is the skill. If they don't yet have SKUs, route through the search or drill-down skills first.
