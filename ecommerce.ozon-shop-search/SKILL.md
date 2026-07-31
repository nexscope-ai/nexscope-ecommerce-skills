---
name: ecommerce.ozon-shop-search
description: Seerfar Ozon shop product search: fetches the product list of an Ozon shop (seller) by shop ID, returning each product's 30-day sales, price, rating, weight, fulfillment method (FBO/FBS), seller type (local/cross-border), return/cancellation rate, and the shop's total 30-day sales. Use for competitor shop product analysis, shop bestseller mining, seller product structure analysis. Trigger when the user mentions Ozon shop products, Ozon seller product list, competitor shop analysis, Ozon shop bestsellers, Ozon seller analysis, Seerfar Ozon shop search, Ozon shop search, Ozon seller products, competitor shop analysis, Ozon store products. Also trigger when the intent is to view an Ozon shop/seller's products and sales data, even without explicitly mentioning Seerfar.
---

# Seerfar Ozon Shop Search

This skill lists the products of a specific Ozon shop (seller) from the Seerfar analytics database. Given a shop `id`, it returns each product's 30-day sales, price, rating, weight, fulfillment model (FBO/FBS), seller type (local / cross-border) and return/cancellation rate, plus the shop's total 30-day sales — the starting point for competitor-shop product analysis, best-seller mining, and seller catalog teardown.

## Core Concepts

**Unit of data is the product, scoped to one shop**: pass a single shop `id` and receive that shop's product catalog with performance metrics. This is a *shop-level* view, not a keyword or category view.

**Where the shop `id` comes from**: `id` is the Seerfar seller/shop identifier — the same `sellerId` returned by other Seerfar Ozon tools (e.g. product report / product detail search). Negative ids (e.g. `-2` Ozon Express, `-4` Ozon Fresh) are Ozon's own platform sellers; positive ids are third-party sellers. If the user only has a shop name or product, first obtain the `sellerId` from a product-level Seerfar Ozon source, then call this skill.

**Seller type**: each product carries `sellerType` — `0` local (local), `1` cross-border (cross-border). A shop is typically all one type; use it to judge whether a competitor is a domestic or cross-border seller.

**Sales & price currency**: `sales` / `monthlySalesUnits` are 30-day units; `price` is in Russian rubles (₽), indicated by `currency`.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | yes | Shop (seller) ID — the `sellerId` from other Seerfar Ozon tools. Negative = Ozon platform seller. |
| page | object | yes | Pagination `{page, pageSize, orders[]}`. |
| page.page | integer | no | Page number, from 1 (default 1). |
| page.pageSize | integer | no | Page size, default 20. **Max 20** — larger values are rejected (`errcode 1002`). |
| page.orders | array | no | Sort rules, elements `{field, direction}`; `direction` `DESC`/`ASC`. Common fields: `sales`, `price`, `reviewRating`, `upTime`. |
| uId | string | no | User ID. |
| memberId | string | no | Member ID (data attribution). |

Only `id` and `page` are required.

## Calling the Tool

- **API Endpoint**: `/seerfar/ozon/shopSearch` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_shop_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-shop-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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

**1. A shop's best-sellers (sort by 30-day sales)**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

**2. A shop's newest listings (sort by upload time)**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "upTime", "direction": "DESC"}]}}
```

**3. A shop's highest-priced products**
```json
{"id": 1362816, "page": {"page": 1, "pageSize": 20, "orders": [{"field": "price", "direction": "DESC"}]}}
```

**4. Page deeper into a shop's catalog**
```json
{"id": 1362816, "page": {"page": 2, "pageSize": 20, "orders": [{"field": "sales", "direction": "DESC"}]}}
```

## How to Build Queries

1. **Always pass `page.orders`**: the catalog can be large — sort by the metric you care about (`sales` DESC for best-sellers, `upTime` DESC for new arrivals, `price` DESC for premium SKUs).
2. **Keep `pageSize` ≤ 20**: the gateway caps page size at 20. Use `page.page` to paginate; check `hasNextPage` to know whether more pages exist.
3. **Resolve the shop `id` first**: if the user gives a shop/product name rather than an id, obtain the `sellerId` from a product-level Seerfar Ozon source before calling this skill.
4. **Use `totalSales` for shop-level context**: the response's `totalSales` is the shop's total 30-day sales — a quick health indicator for the whole shop, independent of the current page.

## Display Rules

1. **Present data only**: show the shop's product metrics in a clear table without subjective advice.
2. **Lead with shop context, then product columns**: state `totalSales` (shop 30-day total) first, then a table of `sku`, `price`, `sales`, `reviewRating`, `weight`, `sellerType`, `fulfillment`, `returnCancellationRate`.
3. **Seller type label**: render `sellerType` as local/cross-border (0/1) so the user reads it at a glance.
4. **Fulfillment**: `fulfillment` is an array (e.g. `["FBO"]`); join multiple values with `/`.
5. **Missing `returnCancellationRate`**: for Ozon platform sellers (negative `id`) this field is often absent — show `-` rather than failing.
6. **Pagination guidance**: when `hasNextPage` is true, tell the user more pages are available via `page.page`; remind them `pageSize` is capped at 20.
7. **Empty shop**: a non-existent `id` returns success with `total=0` and no data — tell the user the id may be wrong rather than reporting a system error.
8. **Error handling**: when `code` is not `"200"` (or `errcode` is not `200`), explain the reason from `msg` / `errmsg` and suggest fixes (add `page`, lower `pageSize`, retry on rate-limit).

## Important Limitations

- **`id` and `page` are both required**; omitting either returns `errcode 400`.
- **`pageSize` max 20**: exceeding it returns `errcode 1002`.
- **`total` is the page row count**, not the shop's full catalog size — use `hasNextPage` to decide whether to fetch more pages.
- **No text/keyword filter**: this endpoint filters by shop only; to find a shop by name, use another Seerfar Ozon source first.
- **Field variance by seller type**: `returnCancellationRate` is populated for third-party sellers but frequently absent for Ozon platform sellers (negative `id`). Schema-defined `productPageUrl`, `monthlySalesRevenue`, `brand` are not returned (upstream has no source, omitted rather than null).

## User Expression & Scenario Quick Reference

**Applicable** — analyzing one Ozon shop/seller's catalog:

| User Says | Scenario |
|-----------|----------|
| "Analyze this Ozon shop's products" / "What is this seller selling" | Shop product catalog |
| "What are the best-selling products in this shop" | Best-seller mining (sort by sales) |
| "What new products has this shop listed recently" | New arrivals (sort by upTime) |
| "Price band / average order value for this competitor shop" | Price-band analysis (sort by price) |
| "Is this shop a local or cross-border seller" | Seller type check (sellerType) |
| "Total sales for this shop" | Shop health (totalSales) |

**Not applicable** — Needs beyond one shop's catalog:
- Discovering Ozon keywords by market metrics → use the Seerfar Ozon market keyword search skill.
- A single product's full detail → use a product-level Seerfar Ozon source (this skill returns catalog-level fields only).
- Browsing the category tree → use a category-level Seerfar Ozon source.
- Finding which shop sells a given product → use a product-level Seerfar Ozon source to get the `sellerId` first.

**Boundary judgment**: if the user already has a shop/seller ID (or a `sellerId` obtained from a product lookup) and wants to enumerate or rank that shop's products by sales/price/rating, start here. If they want market-level keyword discovery or a single product's deep detail, route to the corresponding Seerfar Ozon skill.
