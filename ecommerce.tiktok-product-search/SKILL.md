---
name: ecommerce.tiktok-product-search
description: Search and analyze TikTok product data including sales, influencer sales data, pricing, and commission rates across 16 TikTok Shop sites. Trigger when users mention TikTok product search, TikTok Shop product analysis, TikTok sales data, influencer sales, TikTok product selection, TikTok commission rate, TikTok product ranking, EchoTik data query, TikTok product search, TikTok sales, influencer sales, TikTok commission, TikTok product selection, short-video e-commerce, TikTok data. Even if the user does not explicitly mention "EchoTik" or "TikTok", trigger this skill whenever their need involves searching products on TikTok Shop or analyzing TikTok product performance metrics.
---

# EchoTik TikTok Product Search

This skill guides you on how to search and analyze TikTok Shop product data, helping sellers and marketers discover product opportunities, evaluate sales performance, and identify influencer-driven products on TikTok.

## Core Concepts

EchoTik is a TikTok Shop analytics platform that tracks product performance across multiple TikTok marketplaces. This tool provides keyword-based product search with rich filtering capabilities, returning detailed product data including sales volumes (1d/7d/15d/30d/60d/90d/total), GMV (revenue), pricing, ratings, review counts, commission rates, and influencer promotion statistics.

**Sales metrics**: Products include multi-period sales data -- 1-day, 7-day, 15-day, 30-day, 60-day, 90-day, and total sales. The same granularity applies to GMV (Gross Merchandise Value) amounts.

**Commission rate**: Stored as a decimal (e.g., 0.05 means 5%). When a user specifies a percentage, convert it to decimal before passing to the API.

**Listing date**: The `firstCrawlDt` field uses a compact integer format `YYYYMMDD` (e.g., `20240101` for January 1, 2024).

## Parameter Guide

### Search & Filtering

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| keyword | string | Product keyword (translate to the local language of the target marketplace) | - |
| region | string | Marketplace code | US |
| categoryKeywordCN | string | Product category (must be in Chinese) | - |

### Sales Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minTotalSaleCnt / maxTotalSaleCnt | integer | Total sales volume range |
| minTotalSale30dCnt / maxTotalSale30dCnt | integer | 30-day sales volume range |
| minTotalSaleGmvAmt / maxTotalSaleGmvAmt | string | Total GMV range |
| minTotalSaleGmv30dAmt / maxTotalSaleGmv30dAmt | string | 30-day GMV range |

### Product Attribute Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minSpuAvgPrice / maxSpuAvgPrice | number | SPU average price range |
| minProductRating / maxProductRating | number | Product rating range |
| minReviewCount / maxReviewCount | integer | Review count range |
| minProductCommissionRate / maxProductCommissionRate | number | Commission rate range (decimal, e.g., 0.05 = 5%) |

### Influencer & Video Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| minTotalIflCnt / maxTotalIflCnt | integer | Number of influencers promoting the product |
| minTotalVideoCnt / maxTotalVideoCnt | integer | Number of promotion videos |
| minTotalViewsCnt / maxTotalViewsCnt | integer | Total views on promotion videos |

### Listing Date & Duration

| Parameter | Type | Description |
|-----------|------|-------------|
| minFirstCrawlDt / maxFirstCrawlDt | integer | Listing date range (YYYYMMDD format, e.g., 20240101) |
| saleDays | integer | Days since listing |

### Sorting & Pagination

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| productSortField | integer | Sort field: 1=total sales, 2=total GMV, 3=avg price, 4=7d sales, 5=30d sales, 6=7d GMV, 7=30d GMV | 1 |
| sortType | integer | Sort order: 0=ascending, 1=descending | 1 |
| pageNum | integer | Page number | 1 |
| pageSize | integer | Results per page | 50 |

### Supported Marketplaces

US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France)

Default marketplace is **US**. Use US when the user doesn't specify a marketplace.

## How to Call

- **API Endpoint**: `POST /echotik/listProduct` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/echotik_list_product.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-list-product-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## Usage Examples

**1. Basic Keyword Search -- Find top-selling products for a keyword**
```json
{
  "keyword": "phone case",
  "region": "US",
  "productSortField": 1,
  "sortType": 1,
  "pageSize": 20
}
```

**2. High-Commission Product Discovery -- Products with commission >= 10%**
```json
{
  "keyword": "beauty",
  "region": "US",
  "minProductCommissionRate": 0.10,
  "productSortField": 5,
  "sortType": 1
}
```

**3. New & Trending Products -- Recently listed with strong 30-day sales**
```json
{
  "keyword": "gadget",
  "region": "US",
  "minFirstCrawlDt": 20250101,
  "minTotalSale30dCnt": 1000,
  "productSortField": 5,
  "sortType": 1
}
```

**4. Influencer-Hot Products -- Products promoted by many influencers**
```json
{
  "keyword": "skincare",
  "region": "US",
  "minTotalIflCnt": 50,
  "minTotalViewsCnt": 1000000,
  "productSortField": 1,
  "sortType": 1
}
```

**5. Budget-Friendly High-Sellers -- Low price + high volume**
```json
{
  "keyword": "accessories",
  "region": "US",
  "maxSpuAvgPrice": 10,
  "minTotalSaleCnt": 5000,
  "productSortField": 2,
  "sortType": 1
}
```

**6. Southeast Asia Market Exploration**
```json
{
  "keyword": "fashion",
  "region": "TH",
  "minTotalSale30dCnt": 500,
  "productSortField": 7,
  "sortType": 1
}
```

## Display Rules

1. **Present data clearly**: Show query results in organized tables with key columns -- product name, price, total sales, 30-day sales, GMV, rating, commission rate, and number of promoting influencers
2. **Currency awareness**: Include the currency field from the response when displaying prices and GMV
3. **Commission formatting**: Display commission rates as percentages for readability (e.g., show 0.05 as "5%")
4. **Volume notice**: When results have a large `total` count, show the current page data and inform the user of total available records; suggest adjusting filters or pagination to explore more
5. **Image reference**: If `imageUrl` or `coverUrl` is present, mention it so the user knows product images are available
6. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting parameters
7. **Keyword translation reminder**: When the user targets a non-English marketplace, remind them that the keyword should be in the local language of that marketplace for best results

## Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Find trending products on TikTok" | Keyword search sorted by sales |
| "TikTok products with high commission" | Filter by commission rate |
| "What's selling well on TikTok Shop US" | Regional product search by sales |
| "New products blowing up on TikTok" | Filter by listing date + sales |
| "Which products have many influencers promoting them" | Filter by influencer count |
| "Cheap but high-volume TikTok products" | Filter by price + sales |
| "TikTok product research for Southeast Asia" | Search specific SE Asian regions |
| "Products with good reviews on TikTok" | Filter by rating + review count |

## Not Applicable Scenarios

- TikTok influencer/creator analytics (follower counts, engagement rates of creators)
- TikTok video performance analytics (views, likes, shares on specific videos)
- TikTok advertising / ad campaign management
- Amazon, Shopee, or other non-TikTok platform product data
- TikTok Shop store-level analytics
- Product listing creation or optimization advice
- Logistics, fulfillment, or shipping analysis

**Boundary judgment**: When users say "product research" or "what should I sell on TikTok", if it involves searching and filtering products by sales data, pricing, or commission rates on TikTok Shop, then this skill applies. If they're asking about content strategy, video creation, or influencer outreach, it does not apply.
