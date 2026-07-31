---
name: ecommerce.ozon-category-search
description: Seerfar Ozon category product search: fetches the product list for a given Ozon category ID, returning category-level aggregates (total sales, total revenue, average price, average rating, seasonality) and per-product sales, price, rating, review count, brand, seller, and fulfillment method. Use for category selection analysis, category bestseller mining, category capacity and price band analysis, seasonality assessment. Trigger when the user mentions Ozon category products, Ozon category analysis, Ozon category selection, Ozon category bestsellers, Ozon category total sales, Ozon category average price, Ozon category search, Ozon category products, category best-sellers, category analysis. Also trigger when the intent is to view products and category-level summary data within an Ozon category, even without explicitly mentioning Seerfar.
---

# Seerfar Ozon Category Search

This skill lists the products of a specific Ozon category from the Seerfar analytics database. Given a `categoryId`, it returns category-level aggregates (total sales, total revenue, average price, average rating, seasonality) plus each product's sales, price, rating, review count, brand and seller — the starting point for category selection analysis, best-seller mining within a category, and category capacity / price-band analysis.

## Core Concepts

**Unit of data is the product, scoped to one category**: pass a single `categoryId` and receive that category's product list with performance metrics, alongside category-level aggregates. This is a *category-level* view, not a shop or keyword view.

**Where the `categoryId` comes from**: `categoryId` is the Ozon category identifier — a hierarchical path joined by `_` (e.g. `15621032_15621049_115951147`), obtained from the Ozon category document or from other Seerfar Ozon tools. If the user only has a category name, first resolve it to a `categoryId` from an upstream Seerfar Ozon source before calling this skill.

**Category aggregates vs product rows**: the response carries both category-level totals (`totalSales`, `totalRevenue`, `avgPrice`, `rating`, `seasonalityAmplitude`, `seasonalityCoef`, `startDate`/`endDate`) and a paginated product list (`data` / `products`). Use the aggregates for category sizing and the rows for individual product analysis.

**Sales & price currency**: `sales` / `monthlySalesUnits` are units; `price` / `revenue` are in Russian rubles (₽), indicated by `currency`.

**Time window**: by default the data covers the last 30 days (`startDate` / `endDate` show the actual range). Pass `date` as `yyyy-MM` (e.g. `2026-02`) to query a historical month snapshot.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| categoryId | string | yes | Ozon category ID, e.g. `15621032_15621049_115951147` (levels joined by `_`). |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. |
| page.page | integer | no | Page number, from 1 (default 1). |
| page.pageSize | integer | no | Page size, default 20. **Max 20** — larger values are rejected (`errcode 1002`). |
| page.orders | array | no | Sort rules, elements `{field, direction}` (both required); `direction` `DESC`/`ASC`. Common fields: `sales`, `price`, `revenue`, `reviewRating`. |
| date | string | no | Historical month `yyyy-MM` (e.g. `2026-02`); omit for last 30 days. |
| fulfillment | string | no | Fulfillment filter, one of `FBO` / `FBS` / `RFBS` / `FBP` / `OZON`; omit to query all. **Single string, not an array.** |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `categoryId` and `page` are required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/categorySearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_category_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-category-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Category best-sellers (sort by 30-day sales)**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**2. Category top-revenue products**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "revenue", "direction": "DESC"}]}}
```

**3. Category premium price band (highest-priced)**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "price", "direction": "DESC"}]}}
```

**4. Historical month snapshot**
```json
{"categoryId": "15621032_15621049_115951147", "date": "2026-02", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**5. Filter to FBO-fulfilled products only**
```json
{"categoryId": "15621032_15621049_115951147", "fulfillment": "FBO", "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**6. Page deeper into the category**
```json
{"categoryId": "15621032_15621049_115951147", "page": {"page": 2, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

## How to Build Queries

1. **Always pass `page.orders`**: categories can contain many products — sort by the metric you care about (`sales` DESC for best-sellers, `revenue` DESC for top revenue, `price` DESC for the premium band, `reviewRating` DESC for best-reviewed).
2. **Keep `pageSize` ≤ 20**: the gateway caps page size at 20. Use `page.page` to paginate; check `hasNextPage` to know whether more pages exist.
3. **Resolve the `categoryId` first**: if the user gives a category name rather than an id, obtain the `categoryId` from an upstream Seerfar Ozon source before calling this skill.
4. **Use category aggregates for sizing**: `totalSales`, `totalRevenue`, `avgPrice` and `rating` describe the whole category at a glance — use them for capacity and price-band assessment before drilling into rows.
5. **Use `date` for historical comparison**: pass `date` as `yyyy-MM` to compare a past month against the current 30-day window.
6. **`fulfillment` is a single string**: pass one of `FBO` / `FBS` / `RFBS` / `FBP` / `OZON`, not an array.

## Display Rules

1. **Present data only**: show the category aggregates and product metrics in a clear table without subjective advice.
2. **Lead with category context, then product columns**: state the category name (from `categoryInfo.cnTitlePath` / `enTitlePath` — confirms the right category), then `totalSales`, `totalRevenue`, `avgPrice`, `rating`, seasonality (`seasonalityAmplitude` / `seasonalityCoef`) and date range, plus the fulfillment distribution (`sellerType` map) as a one-line FBO/FBS/RFBS/... split; then a table of `sku`, `title`, `price`, `sales`, `revenue`, `reviewRating`, `reviewCount`, `brandName`, `sellerName`.
3. **Currency**: `price` / `revenue` are in rubles (₽); render with the `currency` symbol.
4. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`); join multiple values with `/`.
5. **Unified vs original fields**: `productId`/`rating`/`brand`/`monthlySalesUnits`/`monthlySalesRevenue`/`productPageUrl` mirror `sku`/`reviewRating`/`brandName`/`sales`/`revenue`/`productUrl` — show one set, prefer the originals.
6. **Pagination guidance**: when `hasNextPage` is true, tell the user more pages are available via `page.page`; remind them `pageSize` is capped at 20.
7. **Empty category**: a non-existent `categoryId` returns success with `total=0` and no data — tell the user the id may be wrong rather than reporting a system error.
8. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest fixes (add `page`, lower `pageSize`, retry on rate-limit).

## Important Limitations

- **`categoryId` and `page` are both required**; omitting either returns `errcode 400`.
- **`pageSize` max 20**: exceeding it returns `errcode 1002`.
- **No text/keyword filter within a category**: this endpoint filters by category (plus optional `fulfillment` and `date`) only; to find products by keyword, use the Seerfar Ozon market keyword search skill.
- **`total` is the page row count**, not the category's total product count — use `hasNextPage` to decide whether to fetch more pages.
- **`sellerType` is a fulfillment distribution, not seller type**: despite the name, the top-level `sellerType` is a map of fulfillment model → product count (`{FBO, RFBS, FBP, FBS, OZON}`); it does not carry local/cross-border (local/cross-border) info. `categoryInfo` carries the category name path (CN/EN/RU) and `crossBorderSellable`.

## User Expression & Scenario Quick Reference

**Applicable** — analyzing one Ozon category's products and aggregates:

| User Says | Scenario |
|-----------|----------|
| "Analyze products in this Ozon category" / "How big is this category" | Category sizing (totalSales / totalRevenue / avgPrice) |
| "What are the best-selling products in this category" | Best-seller mining (sort by sales) |
| "Top-revenue products in this category" | Top-revenue products (sort by revenue) |
| "Price band / average order value in this category" | Price-band analysis (sort by price) |
| "Best-reviewed products in this category" | Best-reviewed (sort by reviewRating) |
| "Last month's data for this category" | Historical month snapshot (date) |
| "FBO products in this category" | Fulfillment filter |

**Not applicable** — Needs beyond one category's product list:
- One shop/seller's catalog → use the Seerfar Ozon shop search skill.
- Market-level keyword discovery → use the Seerfar Ozon market keyword search skill.
- Keyword mining → use the Seerfar Ozon keyword mining skill.
- A single product's full detail → use a product-level Seerfar Ozon source (this skill returns category-level fields only).

**Boundary judgment**: if the user already has a `categoryId` (or one resolved from an upstream source) and wants to enumerate, rank, or size that category's products by sales/price/rating, start here. If they want a shop's catalog, keyword discovery, or a single product's deep detail, route to the corresponding Seerfar Ozon skill.
