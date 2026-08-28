---
name: ecommerce-walmart-search
description: "Search and browse Walmart product listings by keyword, category, price range, and other conditions. Trigger when users mention Walmart product search, Walmart product listing, Walmart price comparison, Walmart competitor analysis, Walmart product research, Walmart market data, find products on Walmart, Walmart search, Walmart products, Walmart product selection, Walmart pricing, Walmart competitors, Walmart market. Even if the user does not explicitly mention \"Walmart search\", trigger this skill whenever their need involves searching for products on Walmart, checking product availability, comparing Walmart prices, or analyzing Walmart product listings."
---

# Walmart Product Search

This skill enables you to search and retrieve Walmart product listing data, helping e-commerce sellers and researchers extract actionable insights from Walmart's marketplace.

## Core Concepts

Walmart Product Search retrieves real-time product listing data from Walmart's marketplace. It supports keyword-based search, category browsing, price filtering, sorting options, and device-specific results. This is a direct search tool that returns current product listings as they appear on Walmart.com.

**Search modes**: You can search by keyword, by category ID, or by combining both. At least one of `keyword` or `categoryId` must be provided.

**Sorting options**: Results can be sorted by `best_seller`, `best_match`, `price_low` (price ascending), or `price_high` (price descending). When no sort is specified, the default relevance-based ranking applies.

**Pagination**: Results are paginated with a default of page 1. The maximum page number is 100.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No* | Search keyword (max 1024 chars). *At least one of keyword or categoryId must be provided |
| categoryId | string | No* | Category ID for browsing. *At least one of keyword or categoryId must be provided. Use `0` for all departments |
| sort | string | No | Sort order: `best_seller`, `best_match`, `price_low`, `price_high` |
| page | integer | No | Page number (1-100, default 1) |
| minPrice | number | No | Minimum price filter |
| maxPrice | number | No | Maximum price filter |
| spelling | boolean | No | Enable spelling correction (default true) |
| softSort | boolean | No | Sort by relevance (default true). Set to false to disable |
| storeId | string | No | Store ID for store-specific results |
| device | string | No | Device type: `desktop` (default), `tablet`, `mobile` |
| facet | string | No | Filter facets in `key:value` format, separated by `||` |
| nextDayEnabled | boolean | No | Show only NextDay delivery results (default false) |
| jsonRestrictor | string | No | JSON field restrictor to limit returned fields |

## Product Data Fields

| Field | Description |
|-------|-------------|
| productId | Walmart product ID |
| usItemId | US item ID |
| title | Product title |
| description | Product description |
| price | Current price |
| wasPrice | Original price before discount |
| currency | Currency code |
| minPrice | Minimum price (for multi-option products) |
| pricePerUnitAmount | Per-unit price amount |
| pricePerUnit | Per-unit price label |
| rating | Average rating score |
| reviews | Total number of reviews |
| sellerName | Seller name |
| sellerId | Seller ID |
| imageUrl | Product thumbnail URL |
| productPageUrl | Product detail page URL |
| sponsored | Whether the listing is a sponsored ad |
| outOfStock | Whether the product is out of stock |
| freeShipping | Whether free shipping is available |
| twoDayShipping | Whether two-day shipping is available |
| freeShippingWithWalmartPlus | Free shipping with Walmart Plus membership |
| shippingPrice | Shipping cost |
| multipleOptionsAvailable | Whether the product has multiple variants |
| variantSwatches | List of variant options with names and images |

## Usage Examples

**1. Basic keyword search**
Search for products matching a keyword:
```json
{"keyword": "wireless earbuds"}
```

**2. Price-filtered search**
Find products within a specific price range:
```json
{"keyword": "laptop stand", "minPrice": 10, "maxPrice": 50}
```

**3. Best sellers in a category**
Browse top-selling products sorted by popularity:
```json
{"keyword": "coffee maker", "sort": "best_seller"}
```

**4. Budget shopping -- lowest price first**
Find the cheapest options for a product:
```json
{"keyword": "phone case", "sort": "price_low"}
```

**5. Category browsing with pagination**
Browse a specific category across multiple pages:
```json
{"categoryId": "976759_976787", "page": 2}
```

**6. Store-specific inventory check**
Search products available at a specific Walmart store:
```json
{"keyword": "tent", "storeId": "1862"}
```

**7. Mobile results simulation**
See results as they appear on mobile devices:
```json
{"keyword": "water bottle", "device": "mobile"}
```

**8. Combined filters**
Apply multiple filters for precise results:
```json
{"keyword": "running shoes", "minPrice": 30, "maxPrice": 80, "sort": "best_match"}
```

## Display Rules

1. **Present data clearly**: Show search results in well-structured tables with key fields (title, price, rating, reviews, seller). Do not add subjective buying recommendations unless the user asks for analysis.
2. **Price formatting**: Always display prices with the currency symbol. When `wasPrice` is present, show both current and original prices to highlight discounts.
3. **Rating context**: Display ratings alongside review counts so users can judge credibility (e.g., "4.5 stars from 1,230 reviews").
4. **Stock status**: Clearly flag out-of-stock items so users do not overlook availability issues.
5. **Sponsored labeling**: Mark sponsored products so users can distinguish organic from paid placements.
6. **Pagination guidance**: When results have a large total count, inform the user of the total and suggest paginating with the `page` parameter to see more.
7. **Error handling**: When a query fails, explain the error clearly and suggest adjusting parameters (e.g., broadening the keyword, changing filters).
8. **Product links**: When showing results, include `productPageUrl` so users can navigate directly to the Walmart product page.

## User Expression & Scenario Quick Reference

**Applicable** -- Walmart product listing queries:

| User Says | Scenario |
|-----------|----------|
| "Search Walmart for XX" | Keyword search |
| "Find cheap XX on Walmart" | Price-filtered search |
| "What's the best-selling XX on Walmart" | Best-seller sort |
| "Compare prices for XX on Walmart" | Price comparison |
| "Is XX in stock at Walmart" | Availability check |
| "Show me Walmart products under $50" | Price-range browse |
| "What are the top-rated XX on Walmart" | Rating-based filtering |
| "Walmart competitor products for XX" | Competitive research |

**Not applicable** -- Needs beyond Walmart product listings:
- Walmart seller account management or advertising
- Walmart order tracking or purchase history
- Product reviews text analysis (only rating/count is available)
- Historical price tracking or price trend analysis
- Walmart affiliate or API key management

**Boundary judgment**: When users say "product research" or "competitor analysis" in the context of Walmart, if their need involves searching for current product listings, prices, ratings, or seller information, then this skill applies. If they are asking about advertising strategy, account metrics, or historical sales data, it does not apply.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
