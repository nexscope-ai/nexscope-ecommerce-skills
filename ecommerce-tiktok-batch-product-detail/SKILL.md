---
name: ecommerce-tiktok-batch-product-detail
description: "Batch query TikTok product detail data, including multi-period sales and GMV (1d/7d/15d/30d/60d/90d/cumulative), live sales and live GMV, promoting video and creator data, views, price, rating, review count, commission rate, and delisted/fully-managed status. Supports batch retrieval by product ID or TikTok Shop product URL. Trigger when users mention TikTok product detail, batch query TikTok products, TikTok product sales analysis, TikTok product GMV, TikTok live sales, TikTok influencer sales data, TikTok product price rating, batch get TikTok product info, EchoTik product detail, TikTok product detail, batch product lookup, TikTok sales analysis, TikTok GMV, TikTok live sales, TikTok influencer data. Even if the user does not explicitly mention \"EchoTik\", trigger this skill whenever their need involves batch retrieval of detailed TikTok product sales and marketing data by product ID or product URL."
---

# EchoTik TikTok Batch Product Detail

This skill guides you on how to fetch detailed performance metrics for a batch of TikTok Shop products, helping sellers and operators compare candidate products side-by-side using sales, GMV, live-stream, video, and influencer data.

## Core Concepts

This tool retrieves full detail metrics for up to **1000** TikTok Shop products in a single call. You identify products by ID and/or by TikTok Shop product URL; the backend extracts the `productId` from each URL and merges it with any IDs you supplied, then returns per-product analytics.

**Input options** (at least one is needed; both can be combined):
- `productIds` -- array of TikTok product IDs
- `productUrls` -- array of TikTok Shop product URLs (e.g. `https://shop.tiktok.com/us/pdp/<slug>/<productId>?...`); the trailing `productId` is extracted from each URL

**Multi-period metrics**: Sales, GMV, live count, video count, influencer count, and views are each reported across `1d / 7d / 15d / 30d / 60d / 90d` windows plus a cumulative total, so you can read both recent momentum and long-run totals.

**Prices are in USD**: `minPrice`, `maxPrice`, and `spuAvgPrice` are USD values.

**Status flags** (integers): `salesTrendFlag` -- `0`=stable, `1`=rising, `2`=falling; `isSShop` -- fully-managed shop; `offMark` -- delisted; `freeShipping` -- free shipping.

**vs. search**: This is detail **lookup for known products** (you already have IDs/URLs). To *discover* products by keyword, use the product search skill; for new-product rankings use the new product rank skill.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| productIds | array<string> | No* | TikTok product IDs (up to 1000 items) | - |
| productUrls | array<string> | No* | TikTok Shop product URLs; the `productId` is extracted from each and merged with `productIds` (up to 1000 items) | - |

\* At least one of `productIds` / `productUrls` must be provided; both can be passed together.

## How to Call

- **API Endpoint**: `POST /echotik/batchProductDetail` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/echotik_batch_product_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-batch-product-detail-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Batch lookup by product IDs**
```json
{
  "productIds": ["1729382310407603945", "1729382310407603946"]
}
```

**2. Batch lookup by product URLs**
```json
{
  "productUrls": [
    "https://shop.tiktok.com/us/pdp/phone-case/1729382310407603945",
    "https://shop.tiktok.com/us/pdp/case-for-phone/1729382310407603946"
  ]
}
```

**3. Mixed IDs and URLs (merged server-side)**
```json
{
  "productIds": ["1729382310407603945"],
  "productUrls": ["https://shop.tiktok.com/us/pdp/phone-case/1729382310407603946"]
}
```

## Display Rules

1. **Present a comparison table**: Show one row per product with key columns -- name, price (USD), total sales, 30-day sales, total GMV, rating, review count, commission rate, and number of promoting influencers
2. **Multi-period context**: When comparing momentum, surface the relevant window (e.g. 7d/30d) alongside the cumulative total rather than only the total
3. **Currency**: Prices are in USD; label them as USD
4. **Commission formatting**: Display `productCommissionRate` as a percentage (e.g. `0.05` -> "5%")
5. **Trend flag**: Render `salesTrendFlag` as stable/rising/falling for quick scanning
6. **Status badges**: Mark `isSShop` (fully-managed), `offMark` (delisted), and `freeShipping` where relevant so users don't compare a delisted product unknowingly
7. **Image reference**: If `imageUrl` / `productImageUrls` is present, mention that images are available
8. **Long descriptions**: `descDetail` can be long HTML/text -- summarize or note its availability instead of dumping it
9. **Missing product handling**: If a requested product returns no record, list which IDs/URLs had no data so the user can verify them
10. **Error handling**: When a query fails, explain the reason from the `errmsg`/`error` field and suggest checking the IDs/URLs

## Important Limitations

- **Batch cap**: Up to 1000 products per request
- **Pricing currency**: All price fields are in USD
- **Estimated data**: Sales, GMV, and attribution figures are analytics estimates, not exact platform figures
- **Lookup only**: This tool does not search by keyword or category -- it resolves specific IDs/URLs you already have

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Look up the details for these TikTok products" | Batch detail by product IDs |
| "Pull sales data for these TikTok links" | Batch detail by product URLs |
| "Compare the GMV of these TikTok products" | Batch lookup, surface GMV columns |
| "Which of these TikTok products are trending up" | Batch lookup, read `salesTrendFlag` |
| "Are any of these TikTok products delisted / fully-managed" | Batch lookup, read `offMark` / `isSShop` |
| "Get live-stream sales for these TikTok products" | Batch lookup, surface live sales/GMV |

### Not Applicable Scenarios

- Discovering products by keyword (use the product search skill)
- New / trending product rankings (use the new product rank skill)
- Promotional videos linked to a product (use the product video skill)
- Resolving a TikTok video download link (use the video download URL skill)
- TikTok creator/influencer profile analytics
- Non-TikTok platform product data

### Boundary Judgment

When users say "analyze these TikTok products", check whether they already have specific product IDs or TikTok Shop URLs (this skill) or want to *find* products by keyword/category (the search skill). If they paste a list of IDs/URLs and want sales/GMV/livestream details, this skill applies. If they ask "what should I sell on TikTok" or "find trending products", it does not.
