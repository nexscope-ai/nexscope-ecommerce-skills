---
name: ecommerce.amazon-broad-product-search
description: Use SellerSprite data to search and filter Amazon products, supporting multi-dimensional criteria including price, monthly sales, BSR ranking, gross margin, ratings, fulfillment method, badges, seller origin, and more across multiple Amazon marketplaces. Trigger when the user mentions Amazon product selection research, product filtering, sales filtering, product discovery, BSR analysis, niche product discovery, competitor analysis, market opportunity assessment, product-level market size estimation, gross margin screening, SellerSprite product selection, Amazon product selection, sales filtering, BSR analysis, profit screening, market analysis, product selection tool. Even if the user does not explicitly mention "SellerSprite", if their need involves filtering and analyzing Amazon product-level data for product selection, this skill should also be triggered.
---

# SellerSprite Product Search

This skill guides you on how to search, filter, and analyze Amazon product data via the SellerSprite product database, helping Amazon sellers make data-driven product selection decisions.

## Core Concepts

SellerSprite Product Search provides access to a comprehensive Amazon product database with rich filtering dimensions. It supports real-time data (last 30 days) as well as monthly historical snapshots for year-over-year and month-over-month comparisons. Supported `marketplace` codes are **only**: US, UK, DE, FR, JP, CA, IT, ES, MX, and IN (same as the gateway schema).

**BSR (Best Sellers Rank)**: A lower BSR value means better sales performance in its category. A BSR of 1 means the top-selling product in that category. When a user says "BSR improved", it means the numeric value decreased; "BSR dropped" means the value increased.

**Data snapshot**: The `dataSnapshotMonth` parameter controls which time period to query. Use `nearly` (the default) for real-time last-30-day data, or a `yyyyMM` string (e.g., `202412`) to query a historical monthly snapshot. This is useful for seasonal analysis and year-over-year comparison.

**Match types for keywords**: When searching by keyword, three matching strategies are available:
- **Phrase match** (default): Product titles must contain the keyword phrase
- **Fuzzy match**: Broader matching with related terms
- **Exact match**: Strict exact-string matching

## Parameter Guide

### Search & Filtering

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| keyword | string | Search keyword; translate to the target marketplace language (e.g., English for US, German for DE) | - |
| matchType | integer | 1 = Phrase match, 2 = Fuzzy match, 3 = Exact match | 1 |
| excludeKeywords | string | Keywords to exclude from results | - |
| marketplace | string | Marketplace code (allowed set only): US, UK, DE, FR, JP, CA, IT, ES, MX, IN | US |
| nodeLabel | string | Amazon category name | - |
| nodeIdPath | string | Amazon category node ID | - |
| filterSubNode | boolean | Whether to filter by subcategory node (only effective when nodeLabel or nodeIdPath is set) | - |
| dataSnapshotMonth | string | Data snapshot month in `yyyyMM` format, or `nearly` for real-time last 30 days | nearly |

### Price & Financials

| Parameter | Type | Description |
|-----------|------|-------------|
| minPrice / maxPrice | number | Price range filter |
| minProfit / maxProfit | number | Gross margin range (1-100, unit: %) |
| minRevenue / maxRevenue | number | Monthly revenue range |
| minFba / maxFba | number | FBA fee range |

### Sales & Ranking

| Parameter | Type | Description |
|-----------|------|-------------|
| minUnits / maxUnits | integer | Monthly sales volume range |
| minAmzUnit / maxAmzUnit | integer | Child-ASIN last-30-day sales range (**only** when querying last-30-day style data, e.g. `dataSnapshotMonth: "nearly"`) |
| minUnitsGrowthRate / maxUnitsGrowthRate | number | Monthly sales growth rate (%) |
| minBsr / maxBsr | integer | Main-category BSR rank range |
| minBsrGrowthRate / maxBsrGrowthRate | number | BSR growth rate (%) |
| minBsrGrowthCount / maxBsrGrowthCount | integer | BSR growth count |
| minSubNodeBsrRank / maxSubNodeBsrRank | integer | Subcategory BSR rank (requires filterSubNode = true) |

### Reviews & Ratings

| Parameter | Type | Description |
|-----------|------|-------------|
| minRating / maxRating | number | Rating score range (0-5); 3.8-4.3 indicates product improvement opportunity |
| minRatings / maxRatings | integer | Number of ratings range (0-10000) |
| minRatingsGrowthCount / maxRatingsGrowthCount | integer | Monthly new ratings count |
| minListingQualityScore / maxListingQualityScore | number | Listing quality score range |

### Product Attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| minVariations / maxVariations | integer | Variation count range |
| minWeights / maxWeights | number | Weight range |
| weightUnit | string | Weight unit: g, kg, oz, lb (required if weight filters are used) |
| dimensionType | string | Package dimension type (marketplace-specific codes) |
| minSellers / maxSellers | integer | Number of sellers range |

### Badges & Fulfillment

| Parameter | Type | Description |
|-----------|------|-------------|
| badgeBestSeller | string | Best Seller badge: Y / N / empty (all) |
| badgeAmazonsChoice | string | Amazon's Choice badge: Y / N / empty (all) |
| badgeNewRelease | string | New Release badge: Y / N / empty (all) |
| fulfillment | string | Fulfillment type: AMZ, FBA, FBM (comma-separated for multiple) |
| showVariation | string | Show variations: Y / N (default N) |

### Seller & Brand

| Parameter | Type | Description |
|-----------|------|-------------|
| sellerNation | string | Seller country code (e.g., US, CN, HK); comma-separated for multiple |
| includeSellers / excludeSellers | string | Include / exclude specific sellers |
| includeBrands / excludeBrands | string | Include / exclude specific brands |

### Listing & Pagination

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| hideUnlistedProduct | boolean | Hide delisted products | true |
| listedWithinLastMonths | integer | Listed within last N months (1, 3, 6, 12, or 24) | - |
| page | integer | Page number, starting from 1 | 1 |
| size | integer | Results per page (10-100) | 20 |

### Sorting

Use the `order` object with two fields:

| Field | Type | Description |
|-------|------|-------------|
| field | string | Sort field: total_units, total_amount, bsr_rank, price, rating, reviews, profit, reviews_rate, available_date, questions, total_units_growth, total_amount_growth, reviews_increasement, bsr_rank_cv, bsr_rank_cr, amz_unit; use `""` when you intentionally omit a business sort key (per gateway schema) |
| desc | string | `"true"` for descending, `"false"` for ascending |

Default sort: `total_units` descending.

### Optional gateway / session fields

If the hosting environment supplies them, you may pass `chatId`, `uid`, `requestId`, and `teamId` as strings (see `references/api.md`). They are not required for ad-hoc script calls.

## How to Invoke

- **API Endpoint**: `POST /sellersprite/productSearch` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_broad_product_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sellersprite-product-search-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Usage Examples

**1. Find high-sales products in a niche**
Search for products with keyword "yoga mat" in the US marketplace with monthly sales above 500 units, sorted by monthly sales descending.
```json
{
  "keyword": "yoga mat",
  "marketplace": "US",
  "minUnits": 500,
  "order": {"field": "total_units", "desc": "true"}
}
```

**2. Discover new product opportunities with low competition**
Find recently listed products (within 6 months) in the US with fewer than 50 ratings and monthly revenue above $5,000.
```json
{
  "keyword": "desk organizer",
  "marketplace": "US",
  "listedWithinLastMonths": 6,
  "maxRatings": 50,
  "minRevenue": 5000,
  "order": {"field": "total_units", "desc": "true"}
}
```

**3. Product improvement opportunity mining**
Find products with ratings between 3.8 and 4.3 (improvement sweet spot), monthly sales above 300, in a specific category.
```json
{
  "keyword": "phone case",
  "marketplace": "US",
  "minRating": 3.8,
  "maxRating": 4.3,
  "minUnits": 300,
  "order": {"field": "total_units", "desc": "true"}
}
```

**4. High-margin product screening**
Find products with gross margin above 40%, price between $15 and $50, at least 100 monthly sales.
```json
{
  "marketplace": "US",
  "minProfit": 40,
  "minPrice": 15,
  "maxPrice": 50,
  "minUnits": 100,
  "order": {"field": "profit", "desc": "true"}
}
```

**5. Seasonal year-over-year comparison**
Query last year's December snapshot data to compare with current data for seasonal product planning.
```json
{
  "keyword": "christmas lights",
  "marketplace": "US",
  "dataSnapshotMonth": "202412",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**6. Chinese seller competitive landscape**
Find FBA-fulfilled products from Chinese sellers in a category with high monthly sales.
```json
{
  "keyword": "bluetooth speaker",
  "marketplace": "US",
  "sellerNation": "CN",
  "fulfillment": "FBA",
  "minUnits": 200,
  "order": {"field": "total_units", "desc": "true"}
}
```

**7. Best Seller & Amazon's Choice badge holders**
Find products carrying the Best Seller badge with strong sales performance.
```json
{
  "keyword": "water bottle",
  "marketplace": "US",
  "badgeBestSeller": "Y",
  "order": {"field": "total_units", "desc": "true"}
}
```

**8. Fast-growing products by sales growth rate**
Find products with monthly sales growth rate above 50%.
```json
{
  "keyword": "standing desk",
  "marketplace": "US",
  "minUnitsGrowthRate": 50,
  "order": {"field": "total_units_growth", "desc": "true"}
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Key columns to prioritize: ASIN, title, price, monthly sales, monthly revenue, BSR rank, rating, ratings count, gross margin, fulfillment type
2. **BSR clarification**: When showing BSR data, remind users that lower values mean better rankings
3. **Gross margin note**: Gross margin values are percentages. Remind users this is an estimate based on price minus FBA fees and estimated costs
4. **Pagination awareness**: When the total count exceeds the returned page size, inform the user of the total result count and suggest adjusting page or size parameters to see more results
5. **Snapshot labeling**: When displaying historical snapshot data, clearly label the data period (e.g., "Data from December 2024 snapshot") to avoid confusion with real-time data
6. **Error handling**: When a query fails, explain the reason based on the `message` field and suggest adjusting query criteria
7. **Weight unit reminder**: When the user provides weight filters without specifying a unit, ask them to confirm the weight unit (g, kg, oz, or lb) before proceeding
8. **Keyword translation**: When the user provides keywords in a language different from the target marketplace, translate the keyword to the appropriate language and note the translation
## Important Limitations

- **Result cap**: Each page returns a maximum of 100 records (size parameter max is 100)
- **Historical snapshots**: Only past monthly snapshots are available; future dates are not supported
- **Weight unit required**: If any weight filter is used, the `weightUnit` must also be provided
- **Subcategory BSR**: The subcategory BSR rank filters only work when `filterSubNode` is set to `true`
- **Listed time enum only**: The `listedWithinLastMonths` parameter only accepts specific values: 1, 3, 6, 12, or 24
- **Child ASIN 30-day sales filters**: `minAmzUnit` / `maxAmzUnit` apply only to last-30-day style queries (typically `dataSnapshotMonth: "nearly"`); do not rely on them for historical `yyyyMM` snapshots

## User Expression & Scenario Quick Reference

**Applicable** -- Product-level data queries on Amazon:

| User Says | Scenario |
|-----------|----------|
| "Find products with high sales in XX category" | Niche product search |
| "Show me low-competition products", "new product opportunities" | Blue ocean product discovery |
| "Which products have high margins" | Profitability screening |
| "Products with rising sales", "trending products" | Growth trend detection |
| "What are Chinese sellers selling well" | Competitive landscape analysis |
| "Recently launched products doing well" | New product tracking |
| "Products with bad reviews but good sales" | Product improvement opportunities |
| "Compare this category with last year" | Seasonal / YoY analysis |
| "FBA products under $30 with 1000+ sales" | Multi-criteria product filtering |
| "Best sellers in XX category" | Badge-based product discovery |

**Not applicable** -- Needs beyond product-level search data:
- ABA search term / keyword analysis (use ABA Data Explorer instead)
- Advertising / PPC campaign data
- Product review text analysis
- Listing copywriting or optimization
- Supplier sourcing or manufacturing costs
- Logistics and inventory planning

**Boundary judgment**: When users say "product research" or "market analysis", if it boils down to filtering Amazon products by sales, price, BSR, ratings, and other product attributes, then this skill applies. If they are asking about keyword search volume, search term rankings, or click/conversion share data, the ABA Data Explorer skill is more appropriate.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
