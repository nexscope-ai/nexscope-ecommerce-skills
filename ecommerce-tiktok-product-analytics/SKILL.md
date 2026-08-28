---
name: ecommerce-tiktok-product-analytics
description: "Query TikTok e-commerce product leaderboards via Kalodata and query detailed data for specific products. Supports viewing high-ranking/hot-selling products by region, currency, language, and date range, and using productId to retrieve price range, sales, revenue, commission rate, listing/delisting time, and owning shop. Trigger when users mention TikTok product ranking, TikTok bestseller chart, TikTok top products, kalodata product rank, TikTok product detail, TikTok product profile, product price, product sales, TikTok product ranking, TikTok bestseller chart, TikTok top products, kalodata product rank, TikTok product detail, kalodata product detail, product analytics. Even if the user does not explicitly mention \"kalodata\", trigger this skill whenever their need involves viewing TikTok product leaderboards or detailed data for a specific TikTok product."
---

# Kalodata - TikTok Product Search & Detail

This skill supports a two-step TikTok Shop product workflow via the Kalodata data source:

1. Browse TikTok Shop product leaderboards to discover top-ranked and best-selling products.
2. Fetch one product's full detail by `productId`.

Use the ranking endpoint when the user wants best-seller rankings, hot products, or product discovery. Use the detail endpoint when the user already has a `productId` or has selected one product from a ranking result.

## Core Concepts

The product ranking endpoint returns a paginated leaderboard filtered by `region`, `dateRange`, `currency`, `language`, and optional `sortField`. Each product row includes identity, price, sales volume, revenue (split across video, live, and showcase channels), revenue growth rate, commission rate, and launch date. Results are paginated with `pageNumber` (1-5) and `pageSize` (5-100).

The product detail endpoint fetches **one** TikTok Shop product by `productId`. It returns the product's price range, sales, revenue (with channel split), commission rate, launch date, review count, category hierarchy, owning shop, and associated video/live/creator counts. The `productId` usually comes from the ranking response field `product_id`.

Both endpoints may reflect a statistical delay (T+1). See `references/api.md` for full request and response details.

## Data Fields

**Ranking rows** include:

| Field | Description |
|-------|-------------|
| product_id | Product unique ID; pass this as `productId` for detail lookup |
| product_name | Product title |
| unit_price | Price per unit (currency follows region, e.g. USD for US) |
| sales_volumn | Units sold (field is spelled `volumn`) |
| revenue | Total revenue / GMV; equals video + live + showcase revenue |
| video_revenue | Revenue from the video channel |
| live_revenue | Revenue from the live-stream channel |
| showcase_revenue | Revenue from the showcase channel |
| revenue_growth_rate | Revenue growth rate (%) |
| commission_rate | Commission rate as a direct percentage (25.0 = 25%) |
| launch_date | Product launch date (YYYY-MM-DD) |

**Detail rows** additionally include:

| Field | Description |
|-------|-------------|
| product_region | Product market region (e.g. `us`) |
| product_shop_id | ID of the shop this product belongs to |
| pri_cate_id / sec_cate_id / ter_cate_id | Primary / secondary / tertiary category IDs |
| min_price / max_price | Minimum / maximum price in the requested currency |
| product_review_count | Number of product reviews |
| delivery_type | Delivery type (e.g. `local`) |
| video_number / live_number / creator_number | Associated video / live / creator counts |
| shopping_mall_revenue | Revenue from the shopping mall channel |

> Detail revenue channel split: `revenue` = `video_revenue` + `live_revenue` + `shopping_mall_revenue`.

## Parameter Guide

**Product ranking (`/kalodata/product/rank`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | No | TikTok Shop market region code, e.g. `US`. Default `US` when unspecified |
| dateRange | string | No | Relative time window, e.g. `last7Day`, `last30Day` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| sortField | object | No | Sorting specification; omit for default ranking |
| pageNumber | integer | No | Page number, 1-5 |
| pageSize | integer | No | Page size, 5-100 |

**Product detail (`/kalodata/product/detail`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productId | string | Yes | TikTok product ID from ranking field `product_id` (string to preserve precision) |
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |

## How to Call

- **API Endpoints**: `POST /kalodata/product/rank` or `POST /kalodata/product/detail` (see `references/api.md` for full parameters/response/error codes)
- **Python Scripts**: `python scripts/product_detail.py '<JSON parameters>' [--inline]` or `python scripts/product_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-kalodata-tiktok-product-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Browse top TikTok products in the US (last 7 days)**
```json
{"region":"US","dateRange":"last7Day","pageSize":20,"pageNumber":1,"currency":"USD"}
```

**2. Fetch one product's detail**
```json
{"productId":"1729508370969629931","region":"US","dateRange":"last7Day","currency":"USD"}
```

**3. Discovery-to-detail workflow**
```text
Run product_detail.py first, choose a row's product_id, then pass that value as productId to product_detail.py.
```

## Display Rules

1. Present ranking results in a table with product name, product ID, price, sales volume, revenue (with channel split), growth rate, commission rate, and launch date.
2. Present detail results as one grouped profile: identity, price range, sales, revenue (channel split), commission, category hierarchy, owning shop, and associated video/live/creator counts.
3. Always label `dateRange`, `region`, and `currency` when showing monetary metrics.
4. Use the exact field name `sales_volumn`.
5. `commission_rate` is a direct percentage (25.0 = 25%), not basis points -- show with a % sign.
6. `revenue_growth_rate` is a percentage -- show with a % sign.
7. Revenue channel split: ranking `revenue` = `video_revenue` + `live_revenue` + `showcase_revenue`; detail `revenue` = `video_revenue` + `live_revenue` + `shopping_mall_revenue`. Present the split when useful.
8. Preserve ranking order unless the user explicitly requests a supported `sortField`.

## Important Limitations

- Ranking is not keyword search; it browses leaderboards by region and time window.
- Detail requires `productId`; it cannot find a product by name alone. Obtain `productId` from the ranking `product_id` first.
- The ranking response does not include `total` or page count; result count is `data.length`.
- `pageNumber` is limited to 1-5 and `pageSize` is limited to 5-100.
- A valid-but-empty request (e.g. an unsupported `region`) may return `errcode 200` with no `data` field and still be billed.
- Transient upstream errors may appear as `errcode 501` with a Kalodata HTTP 5xx message (e.g. 522/554). Retry the same parameters once or twice; do not change parameters automatically.
- Use the matching Kalodata video/creator/shop/livestream skills for non-product entities.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok product ranking or product detail lookup:

| User Says | Scenario |
|-----------|----------|
| "TikTok product ranking", "TikTok product leaderboard" | Product ranking lookup |
| "TikTok bestseller chart", "TikTok hot product ranking", "TikTok product selection ranking" | Best-seller / hot product ranking |
| "kalodata product ranking", "kalodata ranking" | Direct data source reference |
| "TikTok product detail", "TikTok product profile" | Single product detail lookup |
| "Product price", "product sales" | Product price / sales |
| "kalodata product rank/detail", "product analytics" | Direct product detail reference |

**Not applicable** -- Needs beyond TikTok products:

- TikTok video / creator / shop / livestream rankings or details
- Keyword-based product search
- Amazon / Shopify / 1688 product research (use the platform-specific skills)
- TikTok advertising / ad campaign management or content creation
