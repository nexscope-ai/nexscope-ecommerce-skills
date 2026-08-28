---
name: ecommerce-ozon-brand-products
description: "MPSTATS Ozon Russia brand drill-down product list. Returns all products under an Ozon brand display name (Russian/Latin) with complete metrics: sales, revenue, price, rating, stock, turnover, lost revenue, supporting multi-dimensional numeric filters, sorting, and currency conversion. Use for brand benchmarking, competitor analysis, brand product structure research, SKU-level bestseller analysis. Trigger when the user mentions Ozon brand drill-down, Ozon brand products, Ozon competitor brand analysis, brand structure, brand SKUs, brand bestsellers, Ozon brand sales, MPSTATS brand, Ozon brand products, brand drill-down, brand competitor analysis, Russian marketplace brand SKUs, brand revenue share. Also trigger when the intent is to view all products and their sales/price/rating performance under an Ozon brand, even without explicitly mentioning MPSTATS."
---

# MPSTATS Ozon Brand Products

This skill drills into all Ozon (Russia) products sold under a given brand display name, returning each SKU's sales, revenue, price, rating, stock, turnover, lost profit, and more. Built for brand competitor audits, brand SKU structure analysis, and bestseller dissection.

## Core Concepts

**Brand display name**: `brandName` must match what's shown on the Ozon storefront — typically Russian (Cyrillic) or Latin (`adidas`, `Xiaomi`). Do **not** pass a category path, a seller ID, or an internal brand code here. If unsure of the exact spelling, resolve via `ecommerce-ozon-product-search` first.

**Filters are AND-combined**: The `filters` array supports multiple numeric conditions ANDed together. Each filter is `{field, op, value, value2?}`. Common fields and operators are in the Filter Reference below.

**Currency & rate**: Default currency is **RUB**. Set `currency: "USD"` (or another code) to have monetary fields converted server-side; `currencyRate` lets you override the default rate if desired.

**FBO / FBS mix**: `includeFbs: true` folds FBS (seller-shipped) stock + sales into the numbers; `false` keeps them FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| brandName | string | yes | Ozon brand display name (Russian or Latin) |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column: `sales`, `revenue`, `final_price`, `balance`, `rating`, ... |
| sortDirection | string | no | `asc` or `desc` |
| currency | string | no | Currency code, default `RUB`; e.g. `USD`, `EUR`, `CNY` |
| currencyRate | integer | no | Custom rate when non-default currency is used |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter conditions (see below) |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales` (monthly units), `final_price` (selling price RUB), `rating` (0-5), `comments` (review count), `balance` (stock), `revenue` (sales amount RUB), `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2` as the upper bound).

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/brandProducts` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_brand_products.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-ozon-brand-products-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Top-50 by sales for brand `adidas`**
```json
{
  "brandName": "adidas",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 50
}
```

**2. High-rating, mid-price filter**
```json
{
  "brandName": "Xiaomi",
  "filters": [
    {"field": "rating", "op": "GTE", "value": 4.5},
    {"field": "final_price", "op": "BETWEEN", "value": 1000, "value2": 5000}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**3. USD-converted output**
```json
{
  "brandName": "Nike",
  "currency": "USD",
  "sortField": "revenue"
}
```

**4. Include FBS + only in-stock items**
```json
{
  "brandName": "adidas",
  "includeFbs": true,
  "filters": [{"field": "balance", "op": "GT", "value": 0}]
}
```

**5. Lost-profit hunters (out-of-stock pain)**
```json
{
  "brandName": "Nike",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 100000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact brand table** — key columns: `productId`, `title`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `reviewCount`, `balance`, `turnoverDays`, `lostProfit`.
2. **Revenue share context** — `revenueSharePercent` is the SKU's share **within this brand result set**, 0-100; clarify the base when presenting.
3. **Currency labeling** — always state the currency in the table header; if `currency` was overridden, note "converted to USD".
4. **Russian titles** — preserve original; translate on user request.
5. **Pagination** — report total and guide the user to next page or narrower filters when total exceeds the returned page.
6. **No business advice** — present the data; don't project future sales from a snapshot.

## Important Limitations

- **Exact brand-name match** — no fuzzy search; typos return empty results. Verify via `ecommerce-ozon-product-search` if unsure.
- **Page cap** — max 100 rows per page; paginate for larger brands.
- **Date window** — `endDate` cannot be today or a future date (T-1 data).
- **Currency conversion** — server-side; historical rates may differ slightly from the user's reference rate.
- **Russian-only titles** — translate only when asked.

## User Expression & Scenario Quick Reference

**Applicable** — Brand-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Show me adidas's top-selling Ozon SKUs" | Brand bestseller drill |
| "What does Xiaomi sell on Ozon, sorted by revenue" | Brand revenue structure |
| "Which brand-X SKUs have rating ≥4.5 and stock >0" | Brand quality filter |
| "Are brand-X's stockouts causing big lost profit" | Lost-profit hunter |
| "Convert brand-X's Ozon sales to USD" | Currency-normalized audit |

**Not applicable** — Needs beyond brand drill-down:

- Unknown exact brand name → first use `ecommerce-ozon-product-search`
- Category-level comparison across brands → use `ecommerce-ozon-category-products`
- Seller-scoped analysis → use `ecommerce-ozon-seller-products`
- Single-SKU time-series → use `ecommerce-ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the question centers on **one brand** and you want the per-SKU rollup under it. For "which brand dominates category X" use category drill-down and compare brand rows server-side.
