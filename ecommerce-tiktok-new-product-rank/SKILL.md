---
name: ecommerce-tiktok-new-product-rank
description: "Discover trending new products across 16 TikTok Shop regional markets via EchoTik new product ranking data. Trigger when users mention TikTok new product rankings, TikTok hot-selling products, TikTok Shop bestsellers, short-video e-commerce product selection, TikTok new product discovery, cross-border TikTok product selection, TikTok new product rankings, TikTok bestsellers, short-video product selection, TikTok viral products, new product ranking, TikTok product trends. Even if the user does not explicitly mention \"EchoTik\" or \"new product ranking\", trigger this skill whenever their need involves discovering hot-selling new products or emerging product trends on TikTok Shop."
---

# EchoTik - TikTok New Product Ranking

This skill guides you on how to query and analyze the TikTok Shop new product ranking data via the EchoTik data source, helping cross-border e-commerce sellers identify trending new products across TikTok's regional markets.

## Core Concepts

The TikTok New Product Ranking tracks recently listed products that are gaining traction on TikTok Shop. It reveals which new products are selling well, their pricing, sales volume, influencer coverage, and live-stream activity. This is an essential tool for product scouting, trend analysis, and competitive intelligence in the short-video e-commerce space.

**Data scope**: The ranking covers 16 TikTok Shop markets and provides daily snapshots of new products along with their performance metrics (sales volume, revenue, influencer count, video count, live-stream count, commission rate, ratings, and more).

**Pagination**: Results are paginated. Use `pageNum` (page number, starting from 1) and `pageSize` (items per page, default 50) to navigate through the result set.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| date | string | Yes | Query date in `YYYY-MM-DD` format |
| region | string | No | Market region code. Default: `US`. See Supported Markets below |
| pageNum | integer | No | Page number, starting from 1 (default: 1) |
| pageSize | integer | No | Number of products per page (default: 50) |

## Supported Markets

| Code | Market |
|------|--------|
| US | United States |
| GB | United Kingdom |
| ID | Indonesia |
| TH | Thailand |
| PH | Philippines |
| MY | Malaysia |
| VN | Vietnam |
| MX | Mexico |
| SG | Singapore |
| SA | Saudi Arabia |
| BR | Brazil |
| ES | Spain |
| JP | Japan |
| DE | Germany |
| IT | Italy |
| FR | France |

Default market is **US**. Use US when the user does not specify a market.

## How to Call

- **API Endpoint**: `POST /echotik/listNewProductRank` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/echotik_list_new_product_rank.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-list-new-product-rank-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Today's trending new products in the US**
Query the US market for the current date to see which new products are gaining traction.
```
date: "2025-06-15", region: "US"
```

**2. Discover hot new products in Southeast Asia**
Check the Indonesian or Thai market for new product opportunities.
```
date: "2025-06-15", region: "ID"
```

**3. Browse the UK market new product ranking**
Scout the UK TikTok Shop for trending new arrivals.
```
date: "2025-06-15", region: "GB"
```

**4. Paginate through a large result set**
Retrieve the second page of 20 results for the US market.
```
date: "2025-06-15", region: "US", pageNum: 2, pageSize: 20
```

## Data Fields (Response)

| Field | API Name | Description |
|-------|----------|-------------|
| Product Title | title | Name of the product |
| Product ID | asin | Unique product identifier |
| Region | region | Market region code |
| Price (Avg) | price | Average SPU price |
| Min Price | minPrice | Lowest price |
| Max Price | maxPrice | Highest price |
| Currency | currency | Currency code |
| Total Sales | totalSaleCnt | Total units sold |
| 30-Day Sales | totalSale30dCnt | Units sold in the last 30 days |
| Total Revenue | totalSaleGmvAmt | Total gross merchandise value |
| 30-Day Revenue | totalSaleGmv30dAmt | Revenue in the last 30 days |
| Sales Trend | salesTrendFlagText | Sales trend indicator (0 = stable, 1 = rising, 2 = declining) |
| Total Videos | totalVideoCnt | Number of associated videos |
| Total Live Streams | totalLiveCnt | Number of associated live streams |
| Total Influencers | totalIflCnt | Number of influencers promoting the product |
| Commission Rate | productCommissionRate | Product commission rate |
| Rating | productRating | Average product rating |
| Review Count | reviewCount | Number of product reviews |
| First Seen Date | availableDate | Date the product was first tracked |
| Category ID | categoryId | Product category identifier |
| Image URL | imageUrl | Product image URL |
| Image URLs | productImageUrls | List of product image URLs |

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Sales trend clarification**: When showing sales trend data, translate the numeric flag into human-readable labels: 0 = Stable, 1 = Rising, 2 = Declining
3. **Currency awareness**: Always display prices alongside their currency code since different markets use different currencies
4. **Volume notice**: When results are large, show a summary of the top products and remind users they can paginate for more results
5. **Image handling**: If product image URLs are available, mention them but do not attempt to render images inline unless the environment supports it
6. **Error handling**: When a query fails, explain the reason and suggest adjusting the date or region parameters

## Important Limitations

- **Date required**: The `date` parameter is mandatory; there is no default date
- **Daily granularity**: Data is a daily snapshot, not weekly or monthly
- **Pagination**: Use `pageNum` and `pageSize` to navigate large result sets; not all products are returned in a single call

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok Shop new product discovery and trend analysis:

| User Says | Scenario |
|-----------|----------|
| "What new products are trending on TikTok" | New product ranking lookup |
| "TikTok bestsellers today", "hot products on TikTok Shop" | Daily ranking query |
| "New product opportunities in Southeast Asia TikTok" | Regional market scouting |
| "Which new items are selling well on TikTok UK" | Region-specific ranking |
| "TikTok product scouting", "short-video e-commerce trends" | General product discovery |
| "Show me rising new products on TikTok" | Trend-filtered ranking |
| "TikTok influencer product picks", "what are TikTok creators promoting" | Influencer-driven product discovery |

**Not applicable** -- Needs beyond TikTok new product rankings:

- Amazon product research or ABA keyword data
- TikTok advertising / ad campaign management
- TikTok content creation or video editing
- Product reviews or listing copywriting
- Historical trend analysis spanning many months (this tool provides daily snapshots)
- Profit margin calculations or pricing strategy

**Boundary judgment**: When users say "product research" or "what's selling well", if the context clearly involves TikTok Shop or short-video e-commerce, this skill applies. If they are asking about Amazon, Shopify, or other platforms, it does not apply.
