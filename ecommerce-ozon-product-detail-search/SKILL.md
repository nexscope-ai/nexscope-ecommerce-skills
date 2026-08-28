---
name: ecommerce-ozon-product-detail-search
description: "Seerfar Ozon product detail query: fetches the complete detail of a single Ozon product by SKU, returning title, price (RUB), rating, review count, QA count, total and daily average sales within the stats window, revenue, stock, category ranking, daily sales trend, brand, seller, fulfillment method (FBO/FBS/OZON), weight, and listing time/days/months. Use for single product deep analysis, competitor product teardown, Ozon product selection assessment, listing diagnosis, sales trend and category ranking tracking. Trigger when the user mentions Ozon product detail, Ozon single product analysis, Ozon SKU query, competitor product data, Ozon sales trend, Ozon category ranking, Ozon stock, Ozon listing time, Seerfar Ozon product search, Ozon product detail, Ozon SKU lookup, single product analysis, competitor product teardown, Ozon sales trend, category rank. Also trigger when the intent is to view detailed data of an Ozon product, even without explicitly mentioning Seerfar."
---

# Seerfar Ozon Product Detail Search

This skill fetches the full detail of a single Ozon product by its SKU from the Seerfar analytics database — title, price (₽), rating, reviews, QA count, sales (total + daily average + daily trend), revenue, stock, category rank, brand, seller, fulfillment (FBO/FBS/OZON), weight and listing age. The starting point for single-product deep analysis, competitor product teardown, listing diagnostics and sales-trend tracking.

## Core Concepts

**Unit of data is a single product, looked up by `sku`**: pass one Ozon SKU, get that product's full detail. This is a *product-level* view (one SKU), not a shop catalog, keyword or category view.

**Where the SKU comes from**: `sku` is the Ozon product SKU — the same `sku` returned by other Seerfar Ozon tools (shop search, keyword back search, category search, market keyword search). If the user only has a product name, URL or shop, first obtain the `sku` from one of those listing-level sources, then call this skill for the deep dive.

**Sales window**: `dateRange` controls the sales/metrics window — `totalSales`, `dailySales`, `totalRevenue` and `salesTrendVOList` are computed over this range. Default `past_30_days`. Options: `past_7_days` / `past_30_days` / `past_60_days` / `past_90_days` / `past_180_days` / `past_365_days`.

**Sales & price currency**: `price` is in Russian rubles (₽), indicated by `currency`. `totalSales` is units over the window; `dailySales` is the average units/day; `totalRevenue` is revenue over the window.

**Listing age**: `upTime` is the listing timestamp (ms); `upDays` / `upMonths` are the derived age in days / months.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sku | string | yes | Ozon product SKU (e.g. `175924376`). The same `sku` from other Seerfar Ozon tools. |
| dateRange | string | no | Sales/metrics window. Default `past_30_days`. One of: `past_7_days`, `past_30_days`, `past_60_days`, `past_90_days`, `past_180_days`, `past_365_days`. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `sku` is required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/productDetailSearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_product_detail_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-ozon-product-detail-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. Default 30-day detail for a product**
```json
{"sku": "175924376"}
```

**2. Last 7 days (recent momentum)**
```json
{"sku": "175924376", "dateRange": "past_7_days"}
```

**3. Last 90 days (quarterly trend)**
```json
{"sku": "175924376", "dateRange": "past_90_days"}
```

**4. Full year (lifecycle view)**
```json
{"sku": "175924376", "dateRange": "past_365_days"}
```

## How to Build Queries

1. **Resolve the SKU first**: if the user gives a product name, URL or shop rather than a SKU, obtain the `sku` from a listing-level Seerfar Ozon source (shop search / keyword back search / category search / market keyword search) before calling this skill.
2. **Pick `dateRange` by intent**: short windows (`past_7_days` / `past_30_days`) for recent momentum and current stock; long windows (`past_90_days` / `past_180_days` / `past_365_days`) for lifecycle, seasonality and ranking stability.
3. **Read aggregates, then trend**: start with top-level `totalSales` / `dailySales` / `totalRevenue` / `stock` / `categoryRanks` for a snapshot, then drill into `salesTrendVOList` for the daily series.
4. **One SKU per call**: this endpoint takes a single `sku`; to compare products, call once per SKU.

## Display Rules

1. **Present data only**: show the product metrics in a clear layout without subjective advice.
2. **Lead with identity + snapshot**: `title`, `sku`, `price` (₽), `reviewRating` (`reviewCount` reviews, `questionsAndAnswers` Q&A), then the sales snapshot (`totalSales`, `dailySales`, `totalRevenue`, `stock`) and the window (`startDate`–`endDate`).
3. **Category ranks**: `categoryRanks` is a monthly rank history (`{date, rank, count}`) — it has no category name, so show the category path from `categoryInfo` (`titlePath` / `cnTitlePath`) alongside the rank history.
4. **Sales trend**: `salesTrendVOList` is a daily series (`{date, sales, revenue, price, stock, reviewCount, reviewRating}`) — summarize (peak day, trend direction) rather than dumping every row; offer the persisted file for the full series. Some days may have `sales: 0` — treat as no-sales, not missing data.
5. **Seller & brand**: show `sellerName` (`sellerId` — negative means an Ozon platform seller) and `brandName` (`brandId`) so the user can trace the seller/brand.
6. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`, or `["OZON"]` for platform-sold items); join multiple values with `/`.
7. **Listing age**: render `upTime` as a date (ms timestamp) alongside `upDays` / `upMonths`.
8. **Conditional fields**: `weight` (physical goods only) and `grossMargin` are schema-defined but absent for some products (e.g. digital goods / Ozon platform sellers) — show `-` when missing rather than failing. `monthlySalesUnits` / `monthlySalesRevenue` mirror the window's `totalSales` / `totalRevenue` and are safe to read directly.
9. **Empty result**: a non-existent `sku` returns success with `total:0` and empty `products` — tell the user the SKU may be wrong rather than reporting a system error.
10. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain from `msg` / `errmsg` and suggest fixes (check SKU, retry on rate-limit).

## Important Limitations

- **`sku` is required**; omitting it returns a parameter error.
- **Single-SKU endpoint**: returns one product's detail; no batch/list mode. Compare products by calling once per SKU.
- **`dateRange` only affects sales aggregates + trend**: product metadata (title, price, rating, brand, seller, weight, fulfillment) is a point-in-time snapshot, not windowed.
- **Conditional fields**: `weight` (physical goods only) and `grossMargin` are schema-defined but not always returned — absent for digital goods / Ozon platform sellers. `monthlySalesUnits` / `monthlySalesRevenue` are returned and mirror the window's `totalSales` / `totalRevenue`.
- **Sales/revenue are Seerfar model estimates** over the chosen window, not Ozon-official figures.
- **`total` reflects returned record count** (1 when the SKU is found), not a catalog total.

## User Expression & Scenario Quick Reference

**Applicable** — deep-dive on one Ozon product:

| User Says | Scenario |
|-----------|----------|
| "View this Ozon product's detail" / "Data for this SKU" | Single product detail |
| "How many units did this competitor sell in the last 30 days" / "Average daily sales" | Sales snapshot (`totalSales` / `dailySales`) |
| "Revenue for this product" | Revenue (`totalRevenue`) |
| "Stock/inventory level for this product" | Stock check (`stock`) |
| "Category ranking for this product" | Category rank (`categoryRanks`) |
| "Recent sales trend for this product" / "Which day had the best sales" | Daily sales trend (`salesTrendVOList`) |
| "Who sells this / what brand" | Seller + brand (`sellerName` / `brandName`) |
| "How long has this product been listed" | Listing age (`upDays` / `upMonths`) |

**Not applicable** — needs beyond one product's detail:
- A shop's full product catalog → use the Seerfar Ozon shop search skill.
- Discovering Ozon keywords → use market keyword search / keyword mining / keyword back search.
- Browsing the category tree → use category search.
- Multiple products' summary at once → call this skill per SKU, or use a listing-level source.

**Boundary judgment**: if the user already has a specific Ozon SKU (or obtained one from a listing-level source) and wants that product's full metrics — sales, revenue, stock, category rank, trend, brand, seller — start here. If they want to discover products, keywords or shops, route to the corresponding Seerfar Ozon skill first.
