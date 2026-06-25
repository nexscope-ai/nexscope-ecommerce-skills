---
name: ecommerce.tiktok-top-selling
description: |
  Query TikTok hot-selling product rankings by market, category, and time period. Triggers: TikTok best sellers, top selling, hot products, leaderboard, sales ranking. Use for leaderboards, not flexible product filters or video analysis.
---

TikTok Top Selling Rankings

## Core Question

What products are currently top-selling on TikTok Shop for a given market, category, and time period?

## When to Use

- User asks for TikTok best sellers, hot products, top-selling rankings, or sales leaderboards.
- User wants a market/category ranking by day, week, or month.
- User wants to discover what is already selling well before deeper product research.
- User asks for sales or GMV rankings rather than a flexible product search.

## Clarify or Infer Before Querying

If the user request is broad or ambiguous, identify:

- target region or TikTok Shop market
- date period and granularity: day, week, or month
- category if the user wants a focused ranking
- ranking metric: units sold, GMV, total sales, total GMV, or growth rate
- desired number of products

Use sensible defaults when the user's intent is clear: US, latest weekly ranking, units sold descending, 10 products.

## Differs From / Not Applicable

- Use `ecommerce.tiktok-product-research` for flexible product search with filters like price, commission, creator count, shop type, or new listing status.
- Use `ecommerce.tiktok-product-video` when the user already has a TikTok `productId` and wants video/influencer performance for that product.
- Use this skill for ranking/leaderboard questions, not broad filtered discovery or single-product video analysis.
- Do not use for Temu, Amazon, listing optimization, or patent/IP risk.

## Workflow

1. Normalize market, time period, category, ranking metric, and page size.
2. Query FastMoss top-selling rankings.
3. Return a compact ranking table with sales, GMV, price, category, shop, commission, and growth.
4. Highlight top products, fast growers, and products worth deeper research.
5. Recommend follow-up with product research or product video analysis when useful.

## Output Structure

Default output should include:

- Query assumptions: region, dateInfo, category, orderby, pageSize
- Ranking table: rank, title/product ID, category, shop, price, units sold, GMV, growth rate, commission, image/link if available
- Short interpretation: what categories/products dominate, outliers, growth signals
- Suggested next step: run `tiktok-product-research` for filters or `tiktok-product-video` for a selected product

Endpoint: {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/fastmoss/productRankTopSelling
Auth: Bearer {NEXSCOPE_API_KEY}
Method: POST JSON

Required Parameters:
- region: US/GB/MX/ES/ID/VN/MY/TH/PH
- dateInfo: {type: day/week/month, value: YYYY-MM-DD / YYYY-WW / YYYY-MM}

Optional Parameters:
- category (string): English category name
- orderby: {field: units_sold/gmv/total_units_sold/total_gmv/growth_rate, order: desc/asc}
- page (int): default 1
- pageSize (int): max 10, default 10

Response fields per product: title, productId, region, price/minPrice/maxPrice/currency, totalSaleCnt, totalSale1dCnt/7dCnt/30dCnt (varies by dateInfo.type), totalSaleGmvAmt/1dAmt/7dAmt/30dAmt, growthRate, shopName/shopSellerId/shopTotalUnitsSold, categoryName, productCommissionRate (basis points 1000=10%), imageUrl, offShelvesText

Display: commission convert basis points to percentage, currency with prices, growth rate as percentage

See references/api.md for full documentation.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
