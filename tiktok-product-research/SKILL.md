---
name: tiktok-product-research
description: |
  Search and filter TikTok Shop products via FastMoss. Triggers: TikTok product search, product discovery, sales/commission/category/shop filters. Use for flexible product search, not fixed best-seller rankings or product-video analysis.
---

TikTok Product Research

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.

## Core Question

Which TikTok Shop products match the user's discovery, sourcing, category, sales, commission, creator, or shop filters?

## When to Use

- User asks to search or filter TikTok Shop products.
- User wants product discovery by keyword, category, region, price, sales, GMV, commission rate, creator count, shop type, or new listing status.
- User gives a product idea and wants similar TikTok products or market examples.
- User wants a filtered product list rather than a fixed top-selling leaderboard.

## Clarify or Infer Before Querying

If the user request is broad or ambiguous, identify:

- target region or TikTok Shop market
- product keyword or category
- sales/GMV, price, commission, creator-count, rating, or shop-type filters
- whether the user wants new listings, top-selling products, local shops, cross-border shops, or S Shop products
- sort metric and desired result count

Use sensible defaults when the user's intent is clear: US, pageSize 10, sort by 7-day units sold or 7-day GMV depending on whether the user asks about sales or revenue.

## Differs From / Not Applicable

- Use `ecommerce.tiktok-top-selling` for official best-seller rankings by market/category/time period.
- Use `ecommerce.tiktok-product-video` when the user provides a TikTok `productId` and wants promotional video or influencer performance.
- Use this skill for flexible product search/filtering, not fixed leaderboards or video-level analysis.
- Do not use for Temu, Amazon, patent checks, or listing keyword placement.

## Workflow

1. Understand the product/category intent and normalize filters.
2. Choose region, keyword/category, shop filters, ranges, and sort order.
3. Query FastMoss product search.
4. Return a compact product table with sales, GMV, price, commission, creator count, rating, shop, and category.
5. Add sourcing observations and identify products worth checking with video analysis.

## Output Structure

Default output should include:

- Query assumptions and filters used
- Product table: title/product ID, region, category, shop, price, 7/28/90-day sales or GMV, commission, creator/video/live counts, rating, reviews, links
- Key observations: high sales, high commission, creator traction, new listing momentum, cross-border/local-shop signal
- Suggested next step: inspect selected product videos, compare with TikTok rankings, or validate demand on Amazon/Temu

Endpoint: {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/fastmoss/productSearch
Auth: Bearer {NEXSCOPE_API_KEY}
Method: POST JSON

Parameters: keyword, region (US/GB/MX/ES/DE/IT/FR/ID/VN/MY/TH/PH/BR/JP/SG), category, shopType (1=local/2=cross-border), isTopSelling, isNewListed, isSshop, isFreeShipping, isLocalWarehouse, unitsSoldRange, commissionRateRange, creatorCountRange, orderField (day7_units_sold/day7_gmv/commission_rate/total_units_sold/total_gmv/creator_count), page, pageSize (max 10)

Response fields per product: title, productId, region, price/minPrice/maxPrice/currency, totalSaleCnt/totalSale7dCnt/totalSale28dCnt/totalSale90dCnt, totalSaleGmvAmt/totalSaleGmv7dAmt/totalSaleGmv28dAmt, totalVideoCnt/totalLiveCnt/totalIflCnt, productCommissionRate, productRating/reviewCount, shopName/isCrossBorder/isSShopText, categoryName, salesTrendFlagText, tiktokUrl/fastmossUrl/imageUrl

Display: commission as percentage, currency with prices, trend labels directly

See references/api.md for full documentation.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
