---
name: ecommerce-tiktok-shop-analytics
description: "Search TikTok e-commerce store leaderboards via Kalodata and query detailed information for specific stores. Supports viewing high-ranking, high-sales TikTok Shop stores by region, currency, language, and date range, and using shopId to retrieve revenue, sales volume, on-sale product count, self-operated/affiliate/shopping mall channel revenue, and creator collaboration count. Trigger when users mention TikTok store ranking, TikTok shop leaderboard, TikTok top shops, TikTok store ranking, TikTok Shop store ranking, kalodata store search, kalodata store ranking, TikTok store detail, TikTok shop profile, store revenue, store sales, TikTok shop ranking, TikTok shop leaderboard, TikTok top shops, TikTok store ranking, TikTok shop detail, TikTok store detail, kalodata shop search/detail. Even if the user does not explicitly mention \"kalodata\", trigger this skill whenever their need involves viewing TikTok store leaderboards or detailed data for a specific TikTok store."
---

# Kalodata - TikTok Shop Search & Detail

This skill supports a two-step TikTok shop workflow via the Kalodata data source:

1. Browse TikTok Shop store leaderboards to discover high-performing stores.
2. Fetch one store's full detail by `shopId`.

Use the search (ranking) endpoint when the user wants rankings, store discovery, or store comparison. Use the detail endpoint when the user already has a `shopId` or has selected one store from a ranking result.

## Core Concepts

The shop ranking endpoint returns a paginated leaderboard filtered by `region`, `dateRange`, `language`, and `currency`. The default ranking order is by `revenue` (GMV) descending, and each row carries an explicit `rank` position. Each shop row includes identity, scale, revenue channel split, and growth.

The shop detail endpoint fetches **one** store by `shopId`. It returns the store's identity, scale, revenue channel split, and creator/video/live counts. The `shopId` usually comes from the ranking response field `shop_id`.

> **Field names differ between the shop RANK and shop DETAIL endpoints.** Detail uses `self_account_revenue` (rank uses `self_promotion_revenue`), `shoppingmall_revenue` with no internal underscore (rank uses `shopping_mall_revenue`), and `seller_type` (rank uses `shop_type`). Detail returns `creator_number`/`video_number`/`live_number`/`product_number` (rank does not), and does **not** return `rank`/`revenue_growth_rate`/`on_sell_product_count`. Always use the exact endpoint field names.

Both endpoints may reflect a statistical delay (T+1). See `references/api.md` for full request and response details.

## Data Fields

**Ranking rows** include:

| Field | Description |
|-------|-------------|
| rank | Rank position (1 = top by revenue) |
| shop_name | Shop display name |
| shop_id | Shop unique ID; pass this as `shopId` for detail lookup |
| shop_type | Shop type (e.g. `BRAND`) |
| revenue | Total GMV in the requested currency |
| sales_volumn | Sales volume; field is spelled `volumn` |
| on_sell_product_count | Number of products currently on sale |
| unit_price | Average unit price in the requested currency |
| revenue_growth_rate | Revenue growth rate (%), can be negative |
| self_promotion_revenue | Revenue from self-promotion |
| affiliate_revenue | Revenue from affiliate (creator distribution) |
| shopping_mall_revenue | Revenue from the shopping mall |

**Detail rows** include:

| Field | Description |
|-------|-------------|
| shop_id | Shop unique ID (string to preserve precision) |
| shop_name | Shop display name |
| seller_type | Seller/shop type (e.g. `BRAND`) -- note: `seller_type`, not `shop_type` |
| region | Market region (e.g. `US`) |
| revenue | Total revenue / GMV in the requested currency |
| sales_volumn | Sales volume; field is spelled `volumn` |
| product_number | Number of products on sale |
| unit_price | Average unit price in the requested currency |
| self_account_revenue | Revenue from self-account -- note: `self_account_revenue`, not `self_promotion_revenue` |
| affiliate_revenue | Revenue from affiliate (creator distribution) |
| shoppingmall_revenue | Revenue from the shopping mall -- note: NO underscore between `shopping` and `mall` |
| creator_number | Number of creators cooperating with the shop |
| video_number | Number of related videos |
| live_number | Number of related livestreams |

> **Revenue channel split**: on the rank endpoint `revenue` = `self_promotion_revenue` + `affiliate_revenue` + `shopping_mall_revenue`; on the detail endpoint `revenue` ~ `self_account_revenue` + `affiliate_revenue` + `shoppingmall_revenue`. Components may round independently of `revenue` (e.g. `shoppingmall_revenue` returns `10431.0` on detail vs `10431.39` on rank), so treat the split as approximate, not an exact equality.

## Parameter Guide

**Shop ranking (`/kalodata/shop/rank`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, 1-5 |
| pageSize | integer | No | Page size, 5-100 |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |
| sortField | object | No | Sorting specification; pass `{}` for default revenue ranking |

**Shop detail (`/kalodata/shop/detail`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shopId | string | Yes | Shop unique ID from ranking field `shop_id` |
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |

## How to Call

- **API Endpoints**: `POST /kalodata/shop/rank` or `POST /kalodata/shop/detail` (see `references/api.md` for full parameters/response/error codes)
- **Python Scripts**: `python scripts/shop_detail.py '<JSON parameters>' [--inline]` or `python scripts/shop_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-kalodata-tiktok-shop-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Top TikTok shops in the US over the last 7 days**
```json
{"region":"US","dateRange":"last7Day","pageSize":10,"pageNumber":1}
```

**2. Fetch one shop's detail**
```json
{"shopId":"7495514739648989419","region":"US","dateRange":"last7Day","currency":"USD"}
```

**3. Discovery-to-detail workflow**
```text
Run shop_detail.py first, choose a row's shop_id, then pass that value as shopId to shop_detail.py.
```

## Display Rules

1. Present ranking results in a table with rank, shop name, shop type, revenue, sales volume, product count, unit price, and growth rate.
2. Present detail results as one grouped profile: identity, scale, revenue channel split, and creator/video/live counts.
3. Always label `dateRange`, `region`, and `currency` when showing metrics.
4. Revenue channel breakdown is approximate (see Data Fields note); present the split as a breakdown, not an exact equality.
5. Use the exact field name `sales_volumn`. On detail use `shoppingmall_revenue` (no underscore) and `self_account_revenue`; on rank use `shopping_mall_revenue` and `self_promotion_revenue`. Do not mix the two endpoints' field names.
6. Show `creator_number`, `video_number`, `live_number`, `product_number` as plain integer counts.
7. Preserve ranking order unless the user explicitly requests a supported `sortField`.

## Important Limitations

- Ranking is not keyword search; it browses leaderboards by region and time window.
- Detail requires `shopId`; it cannot find a shop by name alone. Obtain `shopId` from the ranking `shop_id` field or the user.
- The ranking response does not include total/page count; paginate until a page returns fewer than `pageSize` items.
- `pageNumber` is limited to 1-5 and `pageSize` is limited to 5-100.
- Detail has no pagination; `data` is a 1-element array for a single shop, with no `total`.
- Field names differ between the rank and detail endpoints (see Data Fields) -- use the exact names when extracting.
- Transient upstream errors may appear as `errcode 501` with a Kalodata HTTP 554 message. Retry the same parameters once or twice; do not change parameters automatically.
- Use the matching Kalodata product/video/creator/livestream skills for non-shop entities.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok Shop store ranking or single-store detail:

| User Says | Scenario |
|-----------|----------|
| "TikTok store ranking", "TikTok shop leaderboard" | Store ranking lookup |
| "TikTok hot stores", "top TikTok shops" | Store leaderboard by region |
| "TikTok store ranking last 7 days", "US TikTok store ranking" | Time-windowed / region-filtered ranking |
| "TikTok store detail", "TikTok shop profile" | Single-store detail lookup |
| "Store revenue", "store sales", "store creator collaboration count" | Store revenue / sales / creator count |
| "kalodata shop search/detail" | Direct data source reference |

**Not applicable** -- Needs beyond TikTok Shop stores:

- TikTok creator/product/video/livestream rankings or details
- Amazon / Shopify / 1688 / other platforms' store data
- TikTok ad campaign management or content creation
