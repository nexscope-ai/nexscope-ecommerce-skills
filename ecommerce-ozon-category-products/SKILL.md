---
name: ecommerce.ozon-category-products
description: MPSTATS Ozon Russia category drill-down product list by Russian category path. Returns all products in a category with complete metrics: sales, revenue, price, rating, stock, turnover, lost revenue, supporting multi-dimensional numeric filters, sorting, and currency conversion. Use for category bestseller mining, blue-ocean insight discovery, category ranking analysis, brand landscape observation. Trigger when the user mentions Ozon category drill-down, Ozon category products, Ozon blue-ocean mining, Ozon category bestsellers, Ozon category ranking, Ozon subcategory structure, Ozon niche SKUs, MPSTATS category, Ozon category drill-down, Russian marketplace niche, Ozon niche mining, Ozon subcategory bestseller. Also trigger when the intent is to view all products and their sales/price/ranking performance under an Ozon category path, even without explicitly mentioning MPSTATS.
---

# MPSTATS Ozon Category Products

This skill drills into all Ozon (Russia) products under a given Russian category path, returning each SKU's sales, revenue, price, rating, stock, turnover, lost profit, and more. Designed for category bestseller mining, blue-ocean niche discovery, and brand-landscape scanning within a specific category.

## Core Concepts

**Russian full-path requirement**: `categoryPath` must be the **full Russian category path** as used on the Ozon platform, with levels separated by `/` — for example, `Одежда/Женская одежда/Футболки и топы женские`. A partial path, English translation, or root-only value will generally return empty results.

**Where to find the path**: Typical workflows resolve the path via an upstream Ozon category-search step (if available in your toolchain) or by pulling a known SKU's `category` field from `ecommerce.ozon-product-detail` / `ecommerce.ozon-product-search`.

**Filters are AND-combined**: `filters` carries multi-field numeric conditions, each `{field, op, value, value2?}`. See the Filter Reference.

**Currency**: Default `RUB`. Override with `currency` (USD, EUR, CNY, ...) and optionally `currencyRate`.

**FBO / FBS**: `includeFbs: true` folds FBS into stock / sales numbers; `false` keeps FBO-only.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| categoryPath | string | yes | Full Russian category path separated by `/` |
| startDate | string | no | Stats window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Stats window end, `YYYY-MM-DD`; latest = yesterday |
| page | integer | no | Page number, starts at 1 |
| pageSize | integer | no | Rows per page, 1-100, default 100 |
| sortField | string | no | snake_case column: `sales`, `revenue`, `final_price`, `balance`, `rating`, ... |
| sortDirection | string | no | `asc` / `desc` |
| currency | string | no | Currency code, default `RUB` |
| currencyRate | integer | no | Custom rate when non-default currency is used |
| includeFbs | boolean | no | Include FBS data |
| filters | array | no | Numeric filter list (see below) |

## Filter Reference

Each `filters` entry: `{"field": "<snake_case>", "op": "<OP>", "value": <num>, "value2": <num?>}`.

**Common fields**: `sales` (monthly units), `final_price` (price RUB), `rating` (0-5), `comments` (reviews), `balance` (stock), `revenue` (amount RUB), `days_in_stock`, `turnover_days`, `lost_profit`, `category_position`.

**Operators**: `GTE`, `LTE`, `GT`, `LT`, `EQ`, `NOT_EQ`, `BETWEEN` (requires `value2`).

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/categoryProducts` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_category_products.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-category-products-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Women's T-shirts — top by sales**
```json
{
  "categoryPath": "Одежда/Женская одежда/Футболки и топы женские",
  "sortField": "sales",
  "sortDirection": "desc",
  "pageSize": 100
}
```

**2. Blue-ocean hunt (sales ≥ 50, rating ≥ 4.5)**
```json
{
  "categoryPath": "Одежда/Женская одежда/Футболки и топы женские",
  "filters": [
    {"field": "sales", "op": "GTE", "value": 50},
    {"field": "rating", "op": "GTE", "value": 4.5}
  ],
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**3. Mid-price + strong turnover**
```json
{
  "categoryPath": "Электроника/Наушники",
  "filters": [
    {"field": "final_price", "op": "BETWEEN", "value": 1500, "value2": 5000},
    {"field": "turnover_days", "op": "LTE", "value": 30}
  ]
}
```

**4. USD-converted ranking for cross-market comparison**
```json
{
  "categoryPath": "Электроника/Смартфоны",
  "currency": "USD",
  "sortField": "revenue",
  "sortDirection": "desc"
}
```

**5. High lost-profit category scan**
```json
{
  "categoryPath": "Одежда/Мужская одежда/Куртки мужские",
  "filters": [{"field": "lost_profit", "op": "GTE", "value": 500000}],
  "sortField": "lost_profit",
  "sortDirection": "desc"
}
```

## Display Rules

1. **Compact category table** — key columns: `productId`, `title`, `brand`, `sellerName`, `price`, `monthlySalesUnits`, `monthlySalesRevenue`, `rating`, `balance`, `position`, `revenueSharePercent`.
2. **Revenue share = within this category query** — 0-100%; clarify the basis when presenting.
3. **Russian titles / brands** — preserve original; translate on demand.
4. **Currency labeling** — state the currency; if converted, note `"converted to USD"`.
5. **Pagination** — report `total`; for large categories (tens of thousands of SKUs) suggest tightening filters rather than naively paging through.
6. **Category position** — lower is better; mention this when showing `categoryPosition`.

## Important Limitations

- **Russian full path only** — partial or translated paths return empty.
- **Path discovery is upstream** — this endpoint does not browse the category tree; resolve the path via product detail / search first.
- **Page cap** — max 100 rows per page.
- **T-1 data** — `endDate` cannot be today or a future date.
- **No business advice** — data-only view.

## User Expression & Scenario Quick Reference

**Applicable** — Category-scoped Ozon product metrics:

| User Says | Scenario |
|-----------|----------|
| "Bestsellers in category X on Ozon" | Category bestseller mining |
| "Find blue-ocean SKUs in niche Y" | Blue-ocean niche scan |
| "Show mid-price, fast-turnover items in this category" | Multi-criteria niche filter |
| "Which brands dominate this Ozon category" | Brand-landscape pre-cut (then group by brand client-side) |
| "Huge lost-profit opportunities in category X" | Out-of-stock pain hunting |

**Not applicable** — Needs beyond category drill-down:

- Unknown category path → use `ecommerce.ozon-product-search` or product detail to discover the exact Russian path
- Brand-scoped drill → `ecommerce.ozon-brand-products`
- Seller-scoped drill → `ecommerce.ozon-seller-products`
- Single-SKU time-series → `ecommerce.ozon-product-trend`
- Wildberries / other Russian marketplaces → not covered

**Boundary judgment**: Use this skill when the **dimension is a category path** and you want the per-SKU roll-up under it. For cross-category comparisons you must run multiple calls and fuse results at the Agent layer.
