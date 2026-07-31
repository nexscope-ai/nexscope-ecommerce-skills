---
name: ecommerce.amazon-product-database
description: Jungle Scout Product Database multi-condition filtering. Filter Amazon products by category, price, sales volume, revenue, reviews, rating, weight, BSR rank, LQS, seller type, and more across 10 marketplaces. Trigger when users mention Amazon product selection, product database filtering, BSR rank filtering, category-based product discovery, high-rating low-competition products, FBA product search, Amazon product discovery, or similar terms. Even if the user does not explicitly mention "Jungle Scout" or "product database," trigger this skill whenever the request involves filtering Amazon products by multiple criteria or discovering potential products.
---

# Jungle Scout -- Product Database Query

This skill queries the Jungle Scout Product Database via the NexScope tool gateway, enabling multi-condition filtering of Amazon products across 10 marketplaces. Sellers can discover products by category, price range, sales volume, revenue, reviews, rating, BSR rank, Listing Quality Score (LQS), seller type, and more.

## Core Concepts

The Jungle Scout Product Database is a multi-dimensional filtering tool at the Amazon product level, helping sellers quickly identify target products from a vast catalog:

- **Category-Based Discovery**: Filter products by Amazon main categories
- **Sales/Revenue Filtering**: Narrow down products by monthly sales volume and revenue ranges
- **Competition Assessment**: Evaluate competition intensity through review counts, ratings, and seller counts
- **Listing Quality Assessment**: LQS (Listing Quality Score, 1-10) helps spot products with optimization potential
- **Product Type Filtering**: Distinguish FBA/FBM/AMZ seller types, standard/oversize product tiers
- **New Product Discovery**: Filter by listing date to find recently launched products

**Internal paging**: The API handles pagination automatically; you specify `needCount` to control how many results you want, and the backend fetches them across pages internally.

## Data Fields

### Key Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Title | title | Product title | Yoga Mat Non Slip... |
| Brand | brand | Brand name | Liforme |
| Main Category | category | Amazon main category | Sports & Outdoors |
| Category Path | breadcrumbPath | Full category hierarchy | Sports & Outdoors > Exercise & Fitness |
| Price | price | Current price (USD) | 29.99 |
| Monthly Sales | approximate30DayUnitsSold | Estimated 30-day units sold | 1200 |
| Monthly Revenue | approximate30DayRevenue | Estimated 30-day revenue (USD) | 35988.00 |
| BSR Rank | productRank | Best Sellers Rank | 3456 |
| Reviews | reviews | Total review count | 850 |
| Rating | rating | Average rating (1.0-5.0) | 4.5 |
| LQS | listingQualityScore | Listing Quality Score (1-10) | 8 |
| Number of Sellers | numberOfSellers | Active seller count | 3 |
| Seller Type | sellerType | Seller type (amz/fba/fbm) | fba |
| First Listed Date | dateFirstAvailable | Product first available date | 2024-06-15 |
| Weight | weightValue / weightUnit | Product weight | 2.5 lbs |
| Dimensions | lengthValue / widthValue / heightValue / dimensionsUnit | Product dimensions | 24x8x8 inches |
| Parent ASIN | parentAsin | Parent ASIN | B0XXXXXXXX |
| Buy Box Owner | buyBoxOwner | Current Buy Box holder | BrandName |
| Fee Breakdown | feeBreakdown | FBA fees, referral fees, total fees, etc. | {fbaFee: 5.40, ...} |
| Subcategory Ranks | subcategoryRanks | Subcategory BSR rank list | [{subcategory: "Yoga Mats", rank: 12}] |
| Cost Token | costToken | Token consumption for this call | 5 |

## Supported Marketplaces

us (United States), uk (United Kingdom), de (Germany), in (India), ca (Canada), fr (France), it (Italy), es (Spain), mx (Mexico), jp (Japan)

Default marketplace is **us**. Use us when the user does not specify a marketplace.

## API Invocation

- **API Endpoint**: `POST /tool-jungle-scout/product-database/query` (full parameters/responses/error codes see `references/api.md`)
- **Python Script**: `python scripts/amazon_product_database.py '<JSON params>' [--inline]`
- **Cost Constraint**: This tool consumes credits; the same parameter combination is called only once per session by default, with a 24h local cache in the script. Do not automatically retry with different keywords, pagination, or zip codes after failures/empty results; inform the user about additional cost before continuing.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-junglescout-product-database-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do NOT write to /tmp** -- error out if the current directory is not writable)
- Response body <= 8 KB: after writing to disk, print the full JSON to stdout
- Response body > 8 KB: after writing to disk, stdout outputs only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (while still writing to disk)

**Data Reading Tips**: First check the summary to see if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## How to Build Queries

Only `marketplace` is **required**. All other parameters are optional filters -- combine them to narrow results.

### Principles for Building API Calls

1. **Marketplace mapping**: "US site" -> `us`, "Japan site" -> `jp`, "Germany site" -> `de`; default to `us` when not specified
2. **Keywords**: `includeKeywords` supports comma-separated multiple terms (searches title or ASIN), e.g. `yoga mat,fitness`; `excludeKeywords` excludes products containing specific terms
3. **Category matching**: `categories` must use the corresponding marketplace is standard English category names, e.g. US site `Sports & Outdoors`, `Home & Kitchen`, etc.; multiple categories comma-separated
4. **Numeric ranges**: min/max used in pairs, either end can be omitted; e.g. only `minSales=300` means monthly sales >= 300
5. **Sorting**: prefix `sort` field name with `-` for descending, e.g. `-sales` for sales high-to-low; defaults to `name` ascending
6. **Result count**: `needCount` controls total results returned; defaults to a standard amount if not set

### Common Query Scenarios

**1. Keyword search + sales volume filter**
```json
{
  "marketplace": "us",
  "includeKeywords": "yoga mat",
  "minSales": 300,
  "maxSales": 5000,
  "sort": "-sales",
  "needCount": 50
}
```

**2. Category + price range filter**
```json
{
  "marketplace": "us",
  "categories": "Home & Kitchen",
  "minPrice": 15,
  "maxPrice": 50,
  "minSales": 100,
  "sort": "-revenue",
  "needCount": 50
}
```

**3. High rating, low competition (few reviews, high rating)**
```json
{
  "marketplace": "us",
  "categories": "Beauty & Personal Care",
  "minRating": 4.0,
  "maxReviews": 200,
  "minSales": 100,
  "sort": "-sales",
  "needCount": 50
}
```

**4. FBA-only product filter**
```json
{
  "marketplace": "us",
  "includeKeywords": "phone stand",
  "sellerTypes": "fba",
  "productTiers": "standard",
  "minSales": 200,
  "sort": "-sales",
  "needCount": 50
}
```

**5. Exclude top brands + discover blue ocean opportunities**
```json
{
  "marketplace": "us",
  "categories": "Sports & Outdoors",
  "excludeTopBrands": true,
  "minSales": 300,
  "maxReviews": 500,
  "minRating": 4.0,
  "sort": "-sales",
  "needCount": 50
}
```

**6. Discover new products by listing date**
```json
{
  "marketplace": "us",
  "categories": "Electronics",
  "minUpdatedAt": "2026-01-01",
  "minSales": 50,
  "sort": "-sales",
  "needCount": 50
}
```

## Display Rules

1. **Table format**: Present results in a structured table with key columns: title, brand, price, monthly sales, monthly revenue, BSR rank, reviews, rating, LQS
2. **Sorting note**: Remind the user what sorting was applied and how many results were returned
3. **Highlight insights**: Mark products with notably low reviews but high sales (potential opportunity), or high LQS scores
4. **Fee breakdown**: When users ask about profitability, include feeBreakdown details (FBA fee, referral fee, total fees)
5. **Image links**: Include `imageUrl` when displaying individual product details
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **marketplace is required**: Every query must specify a marketplace
- **Category names must match**: `categories` values must exactly match the standard main category names for that marketplace
- **Keyword limits**: `includeKeywords` / `excludeKeywords` max 100 items each, max 50 characters per item
- **Data freshness**: Data is sourced from Jungle Scout periodic updates, not real-time data
- **Rating range**: `minRating` / `maxRating` values are 1.0-5.0
- **Weight unit**: `minWeight` / `maxWeight` are in pounds

## User Expression & Scenario Quick Reference

**Applicable** - Amazon product multi-condition filtering and discovery:

| User Says | Scenario |
|-----------|----------|
| "Find yoga mats with monthly sales over 500" | Keyword + sales filter |
| "What are good products under $30 in the US Kitchen category?" | Category + price filter |
| "Blue ocean products with few reviews but high ratings" | High rating, low competition |
| "Find FBA standard-size phone stands" | Seller type + product tier filter |
| "Sports category opportunities excluding major brands" | Exclude top brands |
| "Which recently listed electronics are selling well?" | New product discovery |
| "Home products with BSR rank under 10,000" | BSR rank filter |
| "High-sales products with LQS below 5" | Listing optimization opportunities |

**Not applicable** - Beyond product database filtering:
- Keyword search volume/trend analysis (use keyword history tools)
- ABA search term ranking (use ABA tools)
- Product detail page/listing content analysis
- Advertising/PPC strategy
- Non-Amazon platform product data

**Boundary judgment**: When users say "product selection", "find products", or "market research", if their need is to filter products by specific criteria (price, sales, category, reviews, etc.) from Amazon is product catalog, this skill applies. If they need keyword-level search volume data, advertising insights, or non-Amazon platform data, it does not apply.