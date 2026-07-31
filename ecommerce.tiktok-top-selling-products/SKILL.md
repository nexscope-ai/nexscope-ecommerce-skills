---
name: ecommerce.tiktok-top-selling-products
description: Query TikTok global e-commerce market top-selling product rankings via FastMoss data, supporting daily/weekly/monthly dimensions and category-level analysis. Trigger when users mention TikTok bestseller chart, TikTok hot product ranking, TikTok sales ranking, TikTok GMV ranking, TikTok category bestsellers, TikTok weekly product report, TikTok top-selling rankings, TikTok bestseller charts, TikTok GMV ranking, TikTok category hot sellers, TikTok weekly product report, FastMoss. Even if the user does not explicitly mention "FastMoss", trigger this skill whenever their need involves viewing TikTok platform bestseller rankings or sales rankings by time dimension.
---

# FastMoss - TikTok Top Selling Rankings

This skill guides you on how to query and analyze the TikTok top selling product rankings via the FastMoss data source, helping cross-border e-commerce sellers identify hot-selling products across TikTok's global markets by day, week, or month.

## Core Concepts

The TikTok Top Selling Ranking tracks the best-performing products on TikTok Shop across 9 global markets. It reveals which products are leading in sales volume, GMV, and growth rate over configurable time windows (daily, weekly, monthly). This is an essential tool for product scouting, trend analysis, and competitive intelligence in TikTok e-commerce.

**Data scope**: The ranking covers 9 TikTok Shop markets and supports three time granularities -- day, week, and month -- via the `dateInfo` parameter. Each product entry includes sales volume, GMV, growth rate, commission rate, shop information, category, and more.

**dateInfo format is important**:
- type: `"day"` -> value: `"2025-02-01"` (YYYY-MM-DD)
- type: `"week"` -> value: `"2025-18"` (year-weekNumber)
- type: `"month"` -> value: `"2025-02"` (year-month)

**Pagination**: Results are paginated. Use `page` (page number, starting from 1) and `pageSize` (items per page, max 10, default 10) to navigate through the result set. 

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Market region code (US, GB, MX, ES, ID, VN, MY, TH, PH) |
| dateInfo | object | Yes | Date specification with `type` (day/week/month) and `value` (see format above) |
| category | string | No | Category name in English, matched to TikTok category ID. Non-English input should be translated first |
| orderby | object | No | Sorting: `field` (units_sold/gmv/total_units_sold/total_gmv/growth_rate) + `order` (desc/asc). Default: desc |
| page | integer | No | Page number, default 1 |
| pageSize | integer | No | Items per page, max 10, default 10 |

## Supported Markets

| Code | Market |
|------|--------|
| US | United States |
| GB | United Kingdom |
| MX | Mexico |
| ES | Spain |
| ID | Indonesia |
| VN | Vietnam |
| MY | Malaysia |
| TH | Thailand |
| PH | Philippines |

Default market is **US**. Use US when the user does not specify a market.

## How to Call

- **API Endpoint**: `POST /fastmoss/productRankTopSelling` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/tiktok_top_selling_products.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-fastmoss-product-rank-top-selling-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## Usage Examples

**1. Today's top selling products in the US (daily)**
Query the US market for a specific day to see which products lead in sales.
```
region: "US", dateInfo: {"type": "day", "value": "2026-04-15"}
```

**2. Weekly top sellers in the UK**
Check the UK market for weekly best-performing products.
```
region: "GB", dateInfo: {"type": "week", "value": "2026-15"}
```

**3. Monthly GMV leaders in Southeast Asia**
Scout the Indonesian market for monthly top sellers sorted by GMV.
```
region: "ID", dateInfo: {"type": "month", "value": "2026-03"}, orderby: {"field": "gmv", "order": "desc"}
```

**4. Category-specific ranking**
Find top selling products in a specific category.
```
region: "US", dateInfo: {"type": "day", "value": "2026-04-15"}, category: "Beauty"
```

## Data Fields (Response)

| Field | API Name | Description |
|-------|----------|-------------|
| Product Title | title | Name of the product |
| Product ID | productId | Unique product identifier |
| Region | region | Market region code |
| Price | price | Product price |
| Min Price | minPrice | Lowest price |
| Max Price | maxPrice | Highest price |
| Currency | currency | Currency code |
| Total Sales | totalSaleCnt | Total units sold |
| 1-Day Sales | totalSale1dCnt | Units sold in the last 1 day (when dateType=day) |
| 7-Day Sales | totalSale7dCnt | Units sold in the last 7 days (when dateType=week) |
| 30-Day Sales | totalSale30dCnt | Units sold in the last 30 days (when dateType=month) |
| Total GMV | totalSaleGmvAmt | Total gross merchandise value |
| 1-Day GMV | totalSaleGmv1dAmt | GMV in the last 1 day (when dateType=day) |
| 7-Day GMV | totalSaleGmv7dAmt | GMV in the last 7 days (when dateType=week) |
| 30-Day GMV | totalSaleGmv30dAmt | GMV in the last 30 days (when dateType=month) |
| Growth Rate | growthRate | Sales growth rate (percentage) |
| Shop Name | shopName | Name of the seller's shop |
| Shop Total Units Sold | shopTotalUnitsSold | Total units sold by the shop |
| Shop Seller ID | shopSellerId | Unique shop seller identifier |
| Category Name | categoryName | Product category |
| Commission Rate | productCommissionRate | Commission rate in basis points (1000 = 10%) |
| Image URL | imageUrl | Product image URL |
| Delisted Status | offShelvesText | Delisted indicator ("Yes" = delisted, "No" = active) |

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Growth rate**: Growth rate is in percentage -- show with % sign
3. **Commission rate**: Commission rate is in basis points (1000 = 10%) -- convert to percentage for display
4. **Currency awareness**: Always display currency alongside prices since different markets use different currencies
5. **dateInfo format**: Validate and remind users of the correct format for the selected time granularity
6. **Delisted status**: `offShelvesText` value "Yes" means delisted, "No" means active -- clarify this for users

## Important Limitations

- **dateInfo is mandatory**: Both `type` and `value` must be provided with specific format requirements
- **No keyword search**: This tool does NOT support keyword search (use the product discovery skill for that)
- **Max 10 items per page**: The `pageSize` parameter cannot exceed 10
- **Data delay**: Data has T+1 statistical delay

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok top selling product rankings and trend analysis:

| User Says | Scenario |
|-----------|----------|
| "What are the top selling products on TikTok" | Top selling ranking lookup |
| "TikTok bestsellers this week", "hot products on TikTok Shop" | Weekly/daily ranking query |
| "TikTok GMV ranking", "highest revenue products on TikTok" | GMV-based ranking |
| "TikTok category hot sellers", "top selling beauty products on TikTok" | Category-specific ranking |
| "TikTok weekly product report", "monthly top sellers" | Time-dimension analysis |
| "FastMoss top selling", "FastMoss ranking data" | Direct data source reference |
| "Which products are growing fastest on TikTok" | Growth rate sorted ranking |

**Not applicable** -- Needs beyond TikTok top selling rankings:

- Amazon product research or ABA keyword data
- TikTok advertising / ad campaign management
- TikTok content creation or video editing
- Product reviews or listing copywriting
- TikTok product keyword search (use the product discovery skill instead)
- Profit margin calculations or pricing strategy

**Boundary judgment**: When users say "product research" or "what's selling well", if the context clearly involves TikTok Shop or TikTok e-commerce rankings, this skill applies. If they are asking about Amazon, Shopify, or other platforms, it does not apply. If they want to search products by keyword rather than browse rankings, use the product discovery skill instead.
