---
name: ecommerce.amazon-product-database-search
description: Advanced Amazon product search and filtering powered by Keepa data, supporting multi-dimensional criteria including category, price, monthly sales, keywords, BSR rank, review count, rating, package dimensions, weight, fulfillment type, and more. Trigger when users mention Keepa product selection, Amazon product search, advanced product selection, BSR filtering, sales rank filtering, keyword-based product discovery, category search, competitor screening, niche product discovery, historical rank filtering, or similar terms. Even if the user does not explicitly mention "Keepa," trigger this skill whenever the request involves multi-criteria Amazon product search, sales-metric-based filtering, or advanced product selection beyond simple keyword search.
---

# Keepa Product Search

This skill guides you on how to search and filter Amazon products using Keepa is extensive product database, helping Amazon sellers find products that match specific criteria across multiple dimensions.

## Core Concepts

This tool provides advanced Amazon product search powered by Keepa data. Unlike a simple Amazon storefront search, it supports multi-criteria filtering: category, price range, monthly sales volume, BSR (Best Sellers Rank), keyword matching (positive and negative), review counts, ratings, package dimensions, weight, fulfillment type, historical sales rank, and more. It returns detailed product data including pricing, titles, images, listing dates, materials, weights, monthly sales for the past 12 months, and more.

**BSR (Best Sellers Rank)**: A lower `salesRank` value means better sales performance. Rank 1 is the best-selling product in its category. When a user says "top-selling products", they want low BSR values.

**Price unit**: Prices are expressed in the smallest currency unit (e.g., cents for USD). So `$25.99` = `2599`. Always convert when building queries and when displaying results.

**Category names**: The `categoriesIncludeNames` parameter supports multi-level category paths separated by a colon `:` or the `>` character. Automatically convert user input into the correct format.

## Parameters

### Marketplace (Required)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| domain | string | Yes | Amazon marketplace ID | - |

**Domain ID mapping:**

| ID | Marketplace |
|----|-------------|
| 1 | Amazon.com (United States) |
| 2 | Amazon.co.uk (United Kingdom) |
| 3 | Amazon.de (Germany) |
| 4 | Amazon.fr (France) |
| 5 | Amazon.co.jp (Japan) |
| 6 | Amazon.ca (Canada) |
| 8 | Amazon.it (Italy) |
| 9 | Amazon.es (Spain) |
| 10 | Amazon.in (India) |
| 11 | Amazon.com.mx (Mexico) |

Default marketplace is **1** (US). Use domain `1` when the user does not specify a marketplace.

### Keyword Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | Title keyword filter (case-insensitive; space = AND; wrap phrases in double quotes; prefix with `-` to exclude; `&` is replaced by space; max 50 keywords, max 1000 chars) |

### Category Filtering

| Parameter | Type | Description |
|-----------|------|-------------|
| rootCategory | array[int] | Root category IDs (max 50) |
| rootCategoryNames | array[string] | Root category names (max 50); used when rootCategory is empty; system auto-resolves IDs |
| categoriesInclude | array[int] | Sub-category IDs to include (max 50) |
| categoriesIncludeNames | array[string] | Sub-category names to include (max 50); supports full category paths with `:` or `>` separators |
| categoriesExclude | array[int] | Sub-category IDs to exclude (max 50) |
| categoriesExcludeNames | array[string] | Sub-category names to exclude (max 50); supports full category paths |

### Sales & Ranking Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentSalesGte | integer | Current BSR -- minimum (higher number = worse rank) |
| currentSalesLte | integer | Current BSR -- maximum (lower number = better rank) |
| avg90SalesGte | integer | 90-day average BSR -- minimum |
| avg90SalesLte | integer | 90-day average BSR -- maximum |
| deltaPercent90SalesGte | integer | 90-day BSR change percentage -- minimum |
| deltaPercent90SalesLte | integer | 90-day BSR change percentage -- maximum |
| monthlySoldGte | integer | Monthly sales units -- minimum |
| monthlySoldLte | integer | Monthly sales units -- maximum |
| srAvgGte | integer | Historical average BSR -- minimum (for a specific month) |
| srAvgLte | integer | Historical average BSR -- maximum (for a specific month) |
| srAvgMonth | string | Historical BSR month selection (format: YYYYMM, within last 36 months) |

### Price Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentNewGte | integer | Current new price -- minimum (smallest currency unit) |
| currentNewLte | integer | Current new price -- maximum (smallest currency unit) |
| currentBuyBoxShippingGte | integer | Current Buy Box price including shipping -- minimum (smallest currency unit) |
| currentBuyBoxShippingLte | integer | Current Buy Box price including shipping -- maximum (smallest currency unit) |

### Review & Rating Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| currentCountReviewsGte | integer | Review count -- minimum |
| currentCountReviewsLte | integer | Review count -- maximum |
| currentRatingGte | number | Rating -- minimum (0.0-5.0) |
| currentRatingLte | number | Rating -- maximum (0.0-5.0) |

### Package & Dimensions Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| packageLengthGte / packageLengthLte | integer | Package length range (mm) |
| packageWidthGte / packageWidthLte | integer | Package width range (mm) |
| packageHeightGte / packageHeightLte | integer | Package height range (mm) |
| packageWeightGte / packageWeightLte | integer | Package weight range (grams) |

### Other Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| brand | array[string] | Brand names (OR match) |
| color | array[string] | Colors (OR match) |
| size | array[string] | Sizes (OR match) |
| availableDateGte / availableDateLte | string | Listing date range (yyyy-MM-dd) |
| buyBoxIsAmazon | boolean | Buy Box seller is Amazon |
| buyBoxIsFBA | boolean | Buy Box is FBA fulfilled |
| isHazMat | boolean | Hazardous material flag |
| variationCountGte / variationCountLte | integer | Variation count range |
| currentCountNewGte / currentCountNewLte | integer | Number of new offers range |
| outOfStockPercentage90Gte / outOfStockPercentage90Lte | integer | 90-day out-of-stock percentage range |
| singleVariation | boolean | Return only one variation per parent ASIN |
| productType | array[int] | Product types: 0=standard, 1=downloadable, 2=ebook, 5=variation parent |

### Data Options

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| history | integer | Include historical data (price history, sales rank, monthly sales per month) | 0 (no) |
| rating | integer | Include rating info | 1 (yes) |

### Pagination & Sorting

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| page | integer | Page number (starting from 1) | 1 |
| perPage | integer | Results per page (min 50, max 100) | 50 |
| sort | array[object] | Sort rules (max 3); each object: `{"fieldName": "...", "sortDirection": "asc|desc"}` | - |

**Sortable fields**: `availableDate`, `currentSales`, `monthlySold`, `currentRating`, `currentCountReviews`, `currentBuyBoxShipping`, `currentNew`

## API Invocation

- **API Endpoint**: `POST /keepa/productSearch` (full parameters/responses/error codes see `references/api.md`)
- **Python Script**: `python scripts/amazon_product_database_search.py '<JSON params>' [--inline]`
- **Cost Constraint**: This tool consumes credits; the same parameter combination is called only once per session by default, with a 24h local cache in the script. Do not automatically retry with different keywords, pagination, or zip codes after failures/empty results; inform the user about additional cost before continuing.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-keepa-product-search-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do NOT write to /tmp** -- error out if the current directory is not writable)
- Response body <= 8 KB: after writing to disk, print the full JSON to stdout
- Response body > 8 KB: after writing to disk, stdout outputs only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (while still writing to disk)

**Data Reading Tips**: First check the summary to see if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## How to Build Queries

Construct the request parameters based on the user is intent:

1. **Determine the marketplace**: Map the user is target country to the correct `domain` ID value
2. **Set keyword filters**: Use `keyword` for title-based filtering with positive and negative terms
3. **Set category scope**: Use `categoriesIncludeNames` or `rootCategoryNames` to scope by category; convert user input into proper category path format
4. **Apply numeric filters**: Map sales volume, price, BSR, review, and rating requirements to the appropriate Gte/Lte parameters
5. **Set sort order**: If the user wants results sorted by sales, price, or rating, configure the `sort` array
6. **Enable historical data**: Set `history` to `1` if the user needs monthly sales trends or price history

### Usage Examples

**1. Search for electronics with monthly sales over 1000 on US marketplace**
```json
{"domain": "1", "rootCategoryNames": ["Electronics"], "monthlySoldGte": 1000}
```

**2. Find products in a price range with good ratings**
```json
{"domain": "1", "currentBuyBoxShippingGte": 1500, "currentBuyBoxShippingLte": 5000, "currentRatingGte": 4.0, "keyword": "wireless charger"}
```

**3. New products listed in the last 6 months with low review counts**
```json
{"domain": "1", "availableDateGte": "2025-10-01", "currentCountReviewsLte": 50, "monthlySoldGte": 500}
```

**4. BSR rank filtering for competitive analysis**
```json
{"domain": "1", "categoriesIncludeNames": ["Home & Kitchen"], "currentSalesLte": 5000, "sort": [{"fieldName": "monthlySold", "sortDirection": "desc"}]}
```

**5. Find non-Amazon FBA products with good sales**
```json
{"domain": "1", "buyBoxIsAmazon": false, "buyBoxIsFBA": true, "monthlySoldGte": 300, "currentRatingGte": 4.0}
```

**6. Lightweight small products for easy shipping**
```json
{"domain": "1", "packageWeightLte": 500, "packageLengthLte": 200, "packageWidthLte": 150, "packageHeightLte": 100, "monthlySoldGte": 200}
```

**7. Search on Japan marketplace with historical data**
```json
{"domain": "5", "keyword": "USB charger", "history": 1, "monthlySoldGte": 100}
```

**8. Brand-specific search excluding hazardous materials**
```json
{"domain": "1", "brand": ["Anker", "UGREEN"], "isHazMat": false, "sort": [{"fieldName": "monthlySold", "sortDirection": "desc"}]}
```

## Display Rules

1. **Present data clearly**: Show search results in well-structured tables with key fields: ASIN, title, price, BSR, monthly sales, rating, review count, brand
2. **Price conversion**: Convert prices from smallest currency unit to standard format (e.g., 2599 -> $25.99)
3. **BSR clarification**: When showing BSR data, remind users that lower values mean better sales ranking
4. **Monthly sales history**: When historical data is included, present the 12-month sales trend clearly
5. **Pagination notice**: Inform users of the total result count and suggest fetching additional pages if needed
6. **Image links**: If image URLs are available, mention them but do not attempt to render them inline unless the user requests it
7. **Error handling**: When a query fails, explain the reason and suggest adjusting filter criteria

## Important Limitations

- **Result cap**: Maximum 100 results per page, minimum 50
- **Sort limit**: Maximum 3 sort rules per query
- **Category limit**: Maximum 50 category IDs or names per filter
- **Keyword limit**: Maximum 50 keywords in keyword parameter
- **Historical data cost**: Setting `history=1` increases response size and token cost significantly
- **Price unit**: All price values are in the smallest currency unit (cents, pence, etc.)

## User Expression & Scenario Quick Reference

**Applicable** -- Multi-criteria Amazon product search and filtering:

| User Says | Scenario |
|-----------|----------|
| "Find products with monthly sales over X" | Sales volume filtering |
| "Search for products in XX category" | Category-based product discovery |
| "Products with BSR under X" | Sales rank filtering |
| "New products listed in the last N months" | New product discovery |
| "Products priced between $X and $Y" | Price range filtering |
| "FBA products with good ratings" | Fulfillment + rating filter |
| "Lightweight products under X grams" | Package dimension filtering |
| "Products from brand XX" | Brand-specific search |
| "Show me historical sales data for XX" | Historical sales analysis |
| "Advanced product selection", "product screening" | Multi-criteria product research |
| "Niche product hunting", "find low-competition products" | Competitive gap analysis |
| "BSR trends", "sales rank history" | Historical rank filtering |

**Not applicable** -- Needs beyond product search:
- Real-time Amazon search result page simulation (use Amazon Search)
- Historical search term volume or ranking trends (use ABA data)
- Product review content or sentiment analysis
- Advertising campaign management or bid optimization
- Listing optimization or copywriting suggestions
- Inventory or supply chain data

**Boundary judgment**: When users say "product research" or "find products", if it involves filtering by sales metrics, BSR, price, category, and other structured criteria, this skill applies. If they want to see what appears on the actual Amazon search page for a keyword, use Amazon Search instead. If they want search term analytics, use ABA data.