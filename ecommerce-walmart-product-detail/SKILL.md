---
name: ecommerce-walmart-product-detail
description: "Query Walmart product details via WallySmarter, including pricing history and sales trends. Trigger when users mention Walmart product detail, Walmart product data, WallySmarter, Walmart price trends, Walmart sales trends, Walmart product detail, Walmart price history, Walmart sales trend, WallySmarter product. Even if the user does not explicitly mention \"WallySmarter\", trigger this skill whenever their need involves viewing detailed information, historical price changes, or sales trends for a single Walmart product."
---

# WallySmarter Product Detail

This skill retrieves detailed product information from Walmart via WallySmarter, including pricing history and sales volume trends.

## Core Concepts

WallySmarter Product Detail looks up a single Walmart product by its ItemId and returns comprehensive product attributes along with historical pricing and sales data. This is a product-level deep-dive tool, complementing the broader Walmart search skill that operates at the search/listing level.

**Data scope**: Returns current product attributes (title, price, brand, ratings, fulfillment type, etc.) plus historical stats when `includeStats` is enabled (default).

**Non-structured output**: The tool returns mixed structured and non-structured data. It does NOT support secondary analysis via data query.

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| productId | integer | Yes | -- | Walmart Item ID. Found in product URLs: `https://www.walmart.com/ip/<productId>` |
| includeStats | boolean | No | true | Whether to include historical price and sales data |

## Product Data Fields

| Field | Description |
|-------|-------------|
| title | Product title |
| description | Product description |
| price | Current selling price (USD) |
| wasPrice | Strikethrough price (USD) |
| minPrice | Lowest price (USD) |
| brand | Brand name |
| rating | Average rating (0.0--5.0) |
| reviews | Total review count |
| salesEstimate | Estimated sales volume (units) |
| revenue | Estimated revenue (USD) |
| sellerName | Seller name |
| fulfillmentType | Fulfillment: MARKETPLACE or WFS |
| productPageUrl | Product page URL |
| imageUrl | Product image URL |
| departmentName | Department category name |
| departmentId | Department ID |
| listingScore | Listing quality score |
| contentScore | Content quality score |
| outOfStock | Stock status: 0=in stock, 1=out of stock |
| sponsored | Ad flag: 0=organic, 1=sponsored |
| isBranded | Brand flag: 0=no, 1=yes |
| multipleOptionsAvailable | Variant flag: 0=no, 1=yes |
| usItemId | Internal US Item ID |
| createdAt | Product creation timestamp |
| updatedAt | Last update timestamp |
| stats | Historical price and sales trend data object |

## Usage Examples

**1. Basic product lookup (with history)**
Get full details for a Walmart product including price and sales trends:
```json
{"productId": 5177343351}
```

**2. Product detail only (no history)**
Get product attributes without historical data for faster response:
```json
{"productId": 5169493923, "includeStats": false}
```

## Display Rules

1. **Present data clearly**: Show product details in a structured format. Do not add subjective business recommendations unless asked.
2. **Price formatting**: Display current price alongside wasPrice when available to highlight discounts. Always show USD symbol.
3. **Trend summary**: When stats data is available, summarize price and sales trends (e.g., "Price dropped 15% over the last 30 days").
4. **Score context**: Explain listingScore and contentScore in context (higher = better quality listing).
5. **Stock and fulfillment**: Clearly flag out-of-stock items and fulfillment type (WFS vs Marketplace).
6. **Single product**: This tool queries one product at a time. If the user needs multiple products, call the tool separately for each ItemId.

## Important Limitations

- Only supports lookup by Walmart ItemId (the numeric ID in the product URL)
- Returns non-structured data -- NOT compatible with secondary data analysis tools
- Single ItemId per call; batch queries require multiple invocations
- Historical data availability depends on WallySmarter's tracking coverage

## User Expression & Scenario Quick Reference

**Applicable** -- Walmart single-product deep-dive:

| User Says | Scenario |
|-----------|----------|
| "Look up this Walmart product detail" | Basic product lookup |
| "What's the recent price trend for this Walmart product" | Price trend analysis |
| "WallySmarter look up Walmart product 5177343351" | Direct ID lookup |
| "How are sales for this Walmart product" | Sales estimate check |
| "Walmart product detail for item XX" | English variant |
| "Has this Walmart product dropped in price recently" | Price change detection |

**Not applicable** -- Needs beyond single product detail:

- Walmart product search by keyword (use the Walmart search skill)
- Bulk product comparison across multiple items simultaneously
- Walmart seller account or advertising metrics
- Real-time inventory or delivery estimates
- Category-level market analysis

**Boundary judgment**: If the user has a specific Walmart product ID or URL and wants detailed attributes, pricing history, or sales trends, this skill applies. If they want to search/browse products by keyword or category, use the Walmart search skill instead.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
