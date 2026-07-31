---
name: ecommerce.tiktok-product-discovery
description: Search and filter TikTok global e-commerce products based on FastMoss data, supporting keyword search, multi-dimensional filtering (category, shop type, commission rate, sales, creator count, etc.) and sorting. Trigger when users mention TikTok product selection, TikTok product search, TikTok product data, TikTok creator sales, TikTok commission rate, TikTok bestseller tracking, TikTok GMV analysis, TikTok product search, TikTok product research, TikTok creator sales, TikTok commission rate, TikTok GMV analysis, FastMoss. Even if the user does not explicitly mention "FastMoss", trigger this skill whenever their need involves searching product data or analyzing product performance on TikTok.
---

# FastMoss - TikTok Product Search

This skill guides you on how to search and filter TikTok Shop product data using FastMoss, helping sellers and marketers discover product opportunities, evaluate sales performance, and identify influencer-driven products across 15 TikTok markets worldwide.

## Core Concepts

FastMoss is a well-known TikTok e-commerce data platform that tracks product performance across multiple TikTok marketplaces. This tool provides keyword-based product search with rich filtering capabilities, returning detailed product data including multi-period sales (7-day/28-day/90-day/total), GMV (revenue), pricing, ratings, review counts, commission rates, influencer promotion statistics, and shop information.

**Sales metrics**: Products include multi-period sales data -- 7-day, 28-day, 90-day, and total sales. The same granularity applies to GMV (Gross Merchandise Value) amounts.

**Commission rate**: Stored as a decimal (e.g., 0.10 means 10%). When displaying to the user, convert to percentage format.

**Shop types**: Products can be filtered by shop type -- local shops (1) or cross-border shops (2). The `isCrossBorder` field (1=cross-border, 0=local) and `isSShopText` field (TikTok fully-managed shop) provide additional shop classification.

## Parameter Guide

### Search & Filtering

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword (product title fuzzy match) |
| region | string | No | Market region code. Supported: US, GB, MX, ES, DE, IT, FR, ID, VN, MY, TH, PH, BR, JP, SG |
| category | string | No | Category name in English, matched to TikTok category ID. Non-English should be translated first |
| shopType | integer | No | Shop type: 1=local shop, 2=cross-border shop |

### Boolean Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| isTopSelling | boolean | No | Filter hot-selling products only |
| isNewListed | boolean | No | Filter new products only |
| isSshop | boolean | No | Filter TikTok fully-managed (S-shop) products only |
| isFreeShipping | boolean | No | Filter free-shipping products only |
| isLocalWarehouse | boolean | No | Filter local warehouse products only |

### Range Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| unitsSoldRange | object | No | Sales volume range filter: `{min, max}` |
| commissionRateRange | object | No | Commission rate range filter: `{min, max}` |
| creatorCountRange | object | No | Creator/influencer count range filter: `{min, max}` |

### Sorting & Pagination

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| orderField | string | No | Sort field: day7_units_sold, day7_gmv, commission_rate, total_units_sold, total_gmv, creator_count. Default: descending |
| page | integer | No | Page number, default 1 |
| pageSize | integer | No | Items per page, max 10, default 10 |

### Supported Markets (15)

US (United States), GB (United Kingdom), MX (Mexico), ES (Spain), DE (Germany), IT (Italy), FR (France), ID (Indonesia), VN (Vietnam), MY (Malaysia), TH (Thailand), PH (Philippines), BR (Brazil), JP (Japan), SG (Singapore)

## How to Call

- **API Endpoint**: `POST /fastmoss/productSearch` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/tiktok_product_discovery.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-fastmoss-product-search-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Data Fields

Key fields returned for each product:

| Field | Description |
|-------|-------------|
| title | Product name |
| productId | Unique product identifier |
| region | Market region code |
| price, minPrice, maxPrice | Product price and price range |
| currency | Currency code |
| totalSaleCnt | Total cumulative sales |
| totalSale1dCnt, totalSale7dCnt, totalSale28dCnt, totalSale90dCnt | Sales by period |
| totalSaleGmvAmt, totalSaleGmv7dAmt, totalSaleGmv28dAmt | GMV by period |
| totalVideoCnt, totalLiveCnt, totalIflCnt | Video count, live count, influencer count |
| productCommissionRate | Commission rate (decimal, 0.10 = 10%) |
| productRating, reviewCount | Rating and review count |
| skuCount | Number of SKUs |
| shopName, shopSellerId, shopTotalUnitsSold | Shop information |
| isCrossBorder | 1=cross-border, 0=local |
| isSShopText, freeShippingText | Fully-managed shop flag, free shipping flag |
| salesTrendFlagText | Sales trend label |
| categoryName | Product category |
| tiktokUrl, fastmossUrl, imageUrl | Links and image |

## Usage Examples

**1. Basic Keyword Search -- Find top-selling products**
```json
{
  "keyword": "phone case",
  "region": "US",
  "orderField": "total_units_sold",
  "pageSize": 10
}
```

**2. High-Commission Product Discovery -- Products with commission >= 10%**
```json
{
  "keyword": "beauty",
  "region": "US",
  "commissionRateRange": {"min": 0.10},
  "orderField": "commission_rate"
}
```

**3. Cross-Border Shop Products -- Filter by shop type**
```json
{
  "keyword": "gadget",
  "region": "US",
  "shopType": 2,
  "orderField": "day7_units_sold"
}
```

**4. Influencer-Hot Products -- Products promoted by many creators**
```json
{
  "keyword": "skincare",
  "region": "US",
  "creatorCountRange": {"min": 50},
  "orderField": "creator_count"
}
```

**5. Hot-Selling New Products on TikTok**
```json
{
  "keyword": "fashion",
  "region": "GB",
  "isTopSelling": true,
  "isNewListed": true,
  "orderField": "day7_gmv"
}
```

## Display Rules

1. **Present data only**: Show query results in organized tables with key columns -- product name, price, total sales, 7-day sales, GMV, rating, commission rate, and number of promoting influencers. Do not make subjective business advice
2. **Commission formatting**: Commission rate is a decimal (0.10 = 10%) -- always display as percentage for readability
3. **Cross-border awareness**: `isCrossBorder`: 1 = cross-border shop, 0 = local shop. Display clearly
4. **Currency awareness**: Include the currency field from the response when displaying prices and GMV
5. **Trend labels**: Display `salesTrendFlagText` directly as the trend indicator
6. **Shop flags**: Display `freeShippingText` and `isSShopText` directly (values are readable text)
7. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting parameters

## Important Limitations

- No required parameters (all optional), but at minimum provide keyword or category for meaningful results
- Max 10 items per page

## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Find trending products on TikTok" | Keyword search sorted by sales |
| "TikTok products with high commission" | Filter by commission rate range |
| "What's selling well on TikTok Shop US" | Regional product search by sales |
| "Search TikTok cross-border shop products" | Filter by shopType=2 |
| "Which products have many influencers promoting them" | Filter by creator count range |
| "TikTok fully-managed shop products" | Filter with isSshop=true |
| "TikTok product research for Southeast Asia" | Search specific SE Asian regions |
| "New hot-selling products on TikTok" | Use isTopSelling + isNewListed flags |
| "FastMoss product data" | Direct platform reference |

## Not Applicable Scenarios

- TikTok influencer/creator analytics (follower counts, engagement rates of creators)
- TikTok video performance analytics (views, likes, shares on specific videos)
- TikTok advertising / ad campaign management
- Amazon, Shopee, or other non-TikTok platform product data
- TikTok Shop store-level analytics
- Product listing creation or optimization advice
- Logistics, fulfillment, or shipping analysis

**Boundary judgment**: When users say "product research" or "what should I sell on TikTok", if it involves searching and filtering products by sales data, pricing, or commission rates on TikTok Shop, then this skill applies. If they're asking about content strategy, video creation, or influencer outreach, it does not apply.
