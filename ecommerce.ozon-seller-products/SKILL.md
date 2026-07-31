---
name: ecommerce.ozon-seller-products
description: MPSTATS Ozon Russia seller drill-down product list by seller ID. Returns all SKUs under a seller with complete metrics: sales, revenue, price, rating, stock, turnover, lost revenue, supporting multi-dimensional numeric filters, sorting, and currency conversion. Use for store structure analysis, seller bestseller analysis, competitor store benchmarking. Trigger when the user mentions Ozon seller products, Ozon store analysis, Ozon seller drill-down, Ozon seller SKUs, Ozon store bestsellers, Ozon competitor store, MPSTATS seller, Ozon seller drill-down, Ozon shop audit, Russian marketplace seller SKUs, Ozon store structure. Also trigger when the intent is to view all products and their sales performance under an Ozon seller ID, even without explicitly mentioning MPSTATS.
---

# MPSTATS Ozon Seller Products

This skill drills into all Ozon (Russia) products sold by a given seller, returning per-SKU sales, revenue, price, rating, stock, turnover, lost profit, and more. Designed for store-structure audits, bestseller dissection within a shop, and head-to-head competitor-store comparison.

## Core Concepts

**Seller ID, not name**: `sellerId` must be a **numeric string** — the `sellerId` field Ozon / MPSTATS uses to identify a shop. Do **not** pass a brand name, category path, or human-readable seller name. If you only have the seller name, resolve the ID via `ecommerce.ozon-product-search` (seller-filtered) and read `sellerId` from the result.

**Filters & ops**: Same AND-combined numeric filter model as `brand-products` and `category-products`. See Filter Reference.

**Currency**: Default `RUB`; override with `currency` / `currencyRate` for USD / EUR / CNY views.

**FBO / FBS**: `includeFbs: true` folds FBS into the numbers; `false` keeps FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | yes | Ozon seller ID as numeric string, e.g. `"3628678"` |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column (`sales`, `revenue`, ...) |
| sortDirection | string | no | `asc` / `desc` |
| currency | string | no | Currency code, default `RUB` |
| currencyRate | integer | no | Custom rate for non-default currency |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter list |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales`, `final_price`, `rating`, `comments`, `balance`, `revenue`, `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2`).

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/sellerProducts` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_seller_products.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-seller-products-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Seller's top-100 by sales**
```json
{
  "sellerId": "3628678",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 100
}
```

**2. Store's revenue top-20**
```json
{
  "sellerId": "3628678",
  "sortField": "revenue",
  "sortDirection": "desc",
  "pageSize": 20
}
```

**3. High-turnover star products**
```json
{
  "sellerId": "3628678",
  "filters": [
    {"field": "sales", "op": "GTE", "value": 30},
    {"field": "turnover_days", "op": "LTE", "value": 20}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**4. Stockout pain points for the store**
```json
{
  "sellerId": "3628678",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 100000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

**5. USD-converted store audit**
```json
{
  "sellerId": "3628678",
  "currency": "USD",
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact store table** — key columns: `productId`, `title`, `brand`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `balance`, `turnoverDays`, `lostProfit`, `position`.
2. **Revenue share = within this seller query** — 0-100%; clarify the base.
3. **Russian titles** — preserve; translate on user request.
4. **Currency labeling** — if converted, note `"converted to USD"`.
5. **Pagination** — for stores with thousands of SKUs, suggest tighter filters before paging deep.
6. **No buying advice** — the skill shows the store's book, not whether their SKUs are worth copying.

## Important Limitations

- **Numeric seller ID only** — passing a seller **name** will not resolve; go through `ecommerce.ozon-product-search` first.
- **Page cap** — max 100 rows per page.
- **T-1 data** — `endDate` cannot be today or a future date.
- **No business advice** — data-only.
- **Ozon-only** — Wildberries / other Russian marketplaces are separate.

## User Expression & Scenario Quick Reference

**Applicable** — Seller-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Show me everything seller 3628678 sells, by sales" | Store SKU map |
| "What are this Ozon store's top revenue products" | Store bestseller drill |
| "How many SKUs does the store have with turnover <20 days" | Operational health filter |
| "Where is this store losing money to stockouts" | Lost-profit scan |
| "Compare two Ozon stores' SKU counts and sales" | Store-vs-store benchmarking (call twice) |

**Not applicable** — Needs beyond seller drill-down:

- Only seller **name** known → use `ecommerce.ozon-product-search` to resolve the ID
- Brand-scoped drill → `ecommerce.ozon-brand-products`
- Category-scoped drill → `ecommerce.ozon-category-products`
- Single-SKU time-series → `ecommerce.ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the **dimension is a specific seller** and you want the per-SKU table under that shop. For "who are the top sellers in category X" you'd use category drill-down and group by seller client-side.
