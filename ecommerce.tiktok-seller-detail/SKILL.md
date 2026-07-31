---
name: ecommerce.tiktok-seller-detail
description: Query TikTok Shop store (seller) details, retrieving a complete store profile by sellerId with total sales, multi-period (1d/7d/30d/90d) sales and GMV, followers, rating, review count, positive feedback rate, delivery rate, response rate, in-store product count, promoting creator count, promotional video count, livestream count, price range, product categories, and estimated listing time. Trigger when users mention TikTok store detail, TikTok seller detail, TikTok store analysis, TikTok store data, TikTok store profile, TikTok Shop store detail, TikTok seller detail, EchoTik store profile. Even if the user does not explicitly mention "EchoTik" or "TikTok", trigger this skill whenever their need involves querying the full detail/profile of a specific TikTok Shop store (with a known sellerId).
---

# EchoTik TikTok Seller Detail

This skill fetches the full profile of a single TikTok Shop store (seller) by its `sellerId`, helping cross-border sellers and marketers deep-dive one store's performance -- sales, multi-period GMV, followers, ratings, fulfillment, and influencer/video/livestream reach.

## Core Concepts

EchoTik is a TikTok Shop analytics platform. This tool returns one store's complete detail object: total and incremental (1d/7d/30d/90d) sales volume and GMV, followers, rating, reviews, positive-feedback / response / delivery rates, product counts, price range, categories, and promoting-influencer / video / livestream counts.

**Where to get a `sellerId`**: This skill requires a store's `sellerId`. Obtain it from the EchoTik TikTok Seller Search results, which lists and filters TikTok Shop stores by region, category, GMV, trend, and store type.

**Listing date**: `firstCrawlDt` uses a compact integer format `YYYYMMDD` (e.g. `20240504` for May 4, 2024).

## Data Fields

The response is a flat store object (top level also carries `errcode`, `errmsg`, `costToken`, `columns`, `type`).

| Field | Description |
|-------|-------------|
| sellerId | Store ID |
| sellerName | Store name |
| sellerLink | Store link |
| coverUrl | Store cover image URL |
| region | Marketplace code |
| categoryId / categoryL2Id / categoryL3Id | Level-1 / 2 / 3 category ID |
| totalSaleCnt | Total sales volume |
| totalSale1dCnt / 7dCnt / 30dCnt / 90dCnt | Sales volume (1d/7d/30d/90d, incremental) |
| totalSaleGmvAmt | Total GMV (revenue) |
| totalSaleGmv1dAmt / 7dAmt / 30dAmt / 90dAmt | GMV (1d/7d/30d/90d, incremental) |
| followersCount | Follower count |
| rating | Store rating |
| reviewCount | Review count |
| positiveFeedbackRate | Positive feedback rate |
| responseRate | Response rate |
| deliveryRate | Delivery rate |
| totalProductCnt | Historical product count (incl. delisted) |
| totalCrawlProductCnt | Current in-store product count |
| spuAvgPrice | Avg SKU price in store |
| minPrice / maxPrice | Min / max price |
| totalIflCnt | Number of promoting influencers |
| totalVideoCnt | Number of promo videos |
| totalLiveCnt | Number of livestreams |
| salesFlagText | Main sales channel (video / live stream) |
| salesTrendFlagText | Sales trend (rising / declining / stable) |
| shopIdentityLabel | Store identity label (e.g. OFFICIAL SHOP) |
| shopTypeText | Brand store flag (yes / no) |
| fromFlagText | Local/cross-border flag (local / cross-border) |
| productCategoryList | Product categories (JSON string) |
| mostProductCategoryList | TOP1 product category (JSON string) |
| firstCrawlDt | Estimated listing time (YYYYMMDD) |
| userId | Influencer UID |
| sourceType | Source type (e.g. Tiktok) |
| sourceTool | Source tool |
| costToken | Tokens consumed |
| columns | Render column definitions (display metadata) |
| type | Render style (e.g. tableListWorkbenches) |

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| sellerId | string | Yes | - | TikTok Shop store ID. Obtain it from the Seller Search skill's results. Max length 1000 |

## How to Call

- **API Endpoint**: `POST /echotik/sellerDetail` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/tiktok_seller_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-seller-detail-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Fetch a store's full profile**
```json
{
  "sellerId": "7495514739648989419"
}
```

**2. Deep-dive a store found via Seller Search**
```
First use seller search to list top US stores by GMV, then view the full detail of medicube US Store (sellerId 7495514739648989419)
```

## Display Rules

1. **Present a clear store profile**: Show store name, region, seller link, cover image, and identity label (e.g. OFFICIAL SHOP)
2. **Sales & GMV granularity**: Show total sales and total GMV; surface the multi-period breakdown (1d/7d/30d/90d) for both volume and GMV so the user sees momentum
3. **Store health metrics**: Show followers, rating, review count, positive-feedback rate, response rate, and delivery rate together
4. **Store attributes**: Show `fromFlagText` (local/cross-border), `salesFlagText` (video/live driven), `salesTrendFlagText` (trend), and `shopTypeText` (brand store) for benchmarking
5. **Reach metrics**: Surface `totalIflCnt` (influencers), `totalVideoCnt` (videos), `totalLiveCnt` (livestreams), and product counts
6. **Store link**: When `sellerLink` is present, surface it so the user can open the store
7. **No secondary processing**: Results are live queries, not stored in a database; secondary SQL/data processing is not available

## Important Limitations

1. **sellerId required**: `sellerId` is mandatory; obtain it from seller search results or a known store link/ID
2. **Single store only**: This returns one store's detail; to list and filter stores, use the seller search skill
3. **Listing date format**: `firstCrawlDt` uses `YYYYMMDD` integers (e.g. `20240504`)
4. **Category IDs**: `categoryId` / `categoryL2Id` / `categoryL3Id` are internal IDs, not human-readable names
5. **Data real-time nature**: Results are live queries, not stored in a database; secondary SQL/data processing is not available

## User Expression & Scenario Quick Reference

**Applicable** -- Deep-dive one TikTok Shop store's full profile:

| User Says | Scenario |
|-----------|----------|
| "TikTok store detail" / "TikTok store detail" | Fetch one store's full profile by sellerId |
| "View this TikTok store's data" | Deep-dive a store found via search |
| "Analyze medicube's TikTok store" | Single-store performance analysis |
| "GMV and followers for this TikTok store" | Store-level sales/GMV/follower metrics |

**Not applicable** -- Needs beyond a single store detail:

- Listing or filtering TikTok Shop stores by region/GMV/trend (use seller search)
- TikTok product search or product rankings (use product search/rank skills)
- TikTok creator/influencer analytics (follower counts, engagement of creators)
- TikTok video performance analytics (views, likes on specific videos)
- Amazon, Shopee, or other non-TikTok platform data
- Store-level operations: order/logistics/ads management

**Boundary judgment**: When users say "analyze this store" or "view store detail" with a known store (sellerId or store link), this skill applies. If they want to discover or list stores by criteria, use the seller search skill instead.
