---
name: ecommerce.shopee-product-search
description: YouYing Shopee product selection tool supporting product query and filtering across all Shopee marketplaces, covering Malaysia, Taiwan (China), Indonesia, Thailand, Philippines, Singapore, Vietnam, Brazil, Mexico, Chile, and Colombia. Triggered when users mention Shopee product selection, Shopee product search, Shopee bestsellers, Shopee market analysis, Shopee category selection, Shopee keyword selection, Shopee sales filtering, Shopee price filtering, Southeast Asia e-commerce product selection, Shopee product search, Shopee product selection, Shopee bestsellers, or Shopee market analysis. Even if the user does not explicitly mention "YouYing" or "Shopee," this skill should be triggered whenever their need involves searching for products or filtering Shopee product data on the Shopee platform.
---

# YouYing - Shopee Product Selection

This skill guides you on how to query and filter Shopee product data across 11 marketplaces, helping cross-border sellers discover trending products and market opportunities on Shopee.

## Core Concepts

The YouYing Shopee Product Selection tool provides structured query capabilities for products across all Shopee marketplaces. Sellers can flexibly combine multi-dimensional filtering criteria such as keywords, price ranges, sales volume, listing date, and store attributes to discover trending products and market opportunities.

**Core Data Dimensions**:
- **Sales Data**: Sold units in the last 30 days (sold), estimated sold units in the last 30 days (estimateSold), total historical sold units (historicalSold), sales revenue in the last 30 days (payment)
- **Price Data**: Default price (price), minimum price (minPrice), maximum price (maxPrice)
- **Store Data**: Store name, official store status, Shopee Verified, local/overseas, cross-border/local
- **Product Attributes**: Rating, rating count, favorites, views, SKU count, listing date, category structure

## Data Fields

### Product Fields (Output)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Product ID | pid | Unique product identifier | 12345678 |
| Product Title | title | Product name | Storage Box Organizer |
| Product Description | description | Detailed product description | ... |
| Product Main Image | imageUrl | Main product image URL | https://... |
| Product Link | productUrl | Shopee product page link | https://... |
| Default Price | price | Default product price (local currency) | 29.90 |
| Minimum Price | minPrice | Lowest SKU price | 19.90 |
| Maximum Price | maxPrice | Highest SKU price | 39.90 |
| Sold (30 days) | sold | Actual sales in last 30 days | 1500 |
| Estimated Sold (30 days) | estimateSold | Estimated sales in last 30 days | 1200 |
| Total Sold | historicalSold | Cumulative total sales | 50000 |
| Revenue (30 days) | payment | Sales revenue in last 30 days (local currency) | 45000 |
| Rating | rating | 0-5 rating | 4.8 |
| Rating Count | ratings | Total number of ratings received | 320 |
| Favorites | favorite | Number of times favorited | 2800 |
| Views | viewCount | Number of views | 15000 |
| Stock | stock | Current inventory quantity | 500 |
| SKU Count | skuNumber | Number of SKU variants | 8 |
| Listing Date | genTime | Date first listed | 2025-06-01 |
| Category Structure | categoryStructure | Category path hierarchy | Home & Living > Storage |
| Store Name | shopName | Store name | BestHome Official |
| Store Link | shopUrl | Store page link | https://... |
| Official Store | isOfficialShop | 1=Yes, 0=No | 1 |
| Shopee Verified | isShopeeVerified | 1=Verified, 0=Not Verified | 1 |
| Fulfillment Type | cbOption | 1=Cross-border, 0=Local | 0 |
| Store Location Type | shippingIconType | 0=Local, 1=Overseas | 0 |
| Product Status | status | 1=Active, 0=Delisted | 1 |

## Supported Marketplaces

| Marketplace | station Value | Code |
|-------------|---------------|------|
| Malaysia | malaysia | MY |
| Taiwan (China) | taiwan_china | Taiwan_CHN |
| Indonesia | indonesia | ID |
| Thailand | thailand | TH |
| Philippines | philippines | PH |
| Singapore | singapore | SG |
| Vietnam | vietnam | VN |
| Brazil | brazil | BR |
| Mexico | mexico | MX |
| Chile | chile | CL |
| Colombia | columbia | CO |

`station` is a **required** parameter. Pass the marketplace name (e.g., `malaysia`) or code (e.g., `MY`). When the user does not specify a marketplace, **ask the user** which marketplace they want to query.

## Invocation

- **API Endpoint**: `POST /youying/shopee/getProductInfos` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/shopee_product_search.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-youying-shopee-get-product-infos-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## How to Build Queries

Convert natural language requirements into API parameter combinations. The core principle is **precisely mapping user filtering criteria to the corresponding parameters**.

### Principles for Building API Calls

1. **Required marketplace**: Every call must specify `station`. User says "Malaysia" -> `malaysia`; "Taiwan" -> `taiwan_china`; "Indonesia" -> `indonesia`, etc.
2. **Keyword search**: `keyword` for title keywords, paired with `keywordType` to control matching mode (1=exact phrase match, 2=multi-word AND, 3=multi-word OR)
3. **Numeric ranges**: Most filtering criteria use Start/End or Min/Max paired parameters, set one or both sides as needed
4. **Sorting**: `orderBy` specifies the sort field, `orderByType` specifies ascending/descending (default DESC)
5. **Pagination**: `page` starts from 1, `pageSize` range 1-1000, default 1000
6. **Exclusion logic**: `notExistKeyword` excludes products containing specific words, `notExistShopIdList` excludes specific stores

### Common Query Scenarios

**1. Keyword product selection -- filter hot-selling products by sales volume**
```
station: malaysia
keyword: Storage Box
keywordType: 2
soldMin: 100
orderBy: sold
orderByType: DESC
pageSize: 100
```

**2. New product discovery -- recently listed products with some sales**
```
station: thailand
keyword: Phone Case
listingDateFrom: 2025-06-01
soldMin: 50
orderBy: gen_time
orderByType: DESC
```

**3. High-potential products -- low price, high sales**
```
station: indonesia
keyword: LED Light
priceMax: 50000
soldMin: 500
orderBy: payment
orderByType: DESC
```

**4. Cross-border seller product filtering**
```
station: malaysia
keyword: Wireless Earbuds
cbOption: 1
soldMin: 200
orderBy: sold
orderByType: DESC
```

**5. Category selection -- filter by category + revenue**
```
station: vietnam
pL1Id: 11036379
paymentStart: 10000000
orderBy: payment
orderByType: DESC
pageSize: 200
```

**6. Competitor store analysis -- view products from a specific store**
```
station: malaysia
shopIdList: 123456789
orderBy: sold
orderByType: DESC
```

**7. Verified product filtering -- Shopee Verified + high rating**
```
station: philippines
keyword: Beauty
isShopeeVerified: 1
ratingMin: 4.5
soldMin: 100
orderBy: rating
orderByType: DESC
```

**8. Top-seller exclusion -- discover small/medium seller opportunities**
```
station: taiwan_china
keyword: Storage Box
notExistShopIdList: 111111,222222,333333
soldMin: 50
soldMax: 500
orderBy: sold
orderByType: DESC
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Currency notice**: Different marketplaces use different currencies (MYR, TWD, IDR, THB, PHP, SGD, VND, BRL, MXN, CLP, COP). Always remind users of the currency context when showing price/payment data
3. **Volume notice**: When results are large, show core data (title, price, sold, payment, rating) and remind users they can view more via pagination
4. **Key metrics highlight**: Prioritize showing `sold` (30-day sales), `payment` (30-day revenue), `price`, `rating` as these are the most decision-relevant metrics
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting query criteria
6. **Image display**: When `imageUrl` is available, include product images to help users make visual assessments

## Important Limitations

- **Result cap**: `pageSize` maximum is 1000 records per request
- **Required field**: `station` is always required -- if missing, ask the user which marketplace to query
- **Price currency**: Prices are in local currency of the selected marketplace, not USD
- **Data freshness**: Data depends on YouYing's crawling schedule, see `lastModiTime` for last update time

## User Expression & Scenario Quick Reference

**Applicable** - Shopee product search and filtering:

| User Says | Scenario |
|-----------|----------|
| "What sells well on Shopee" / "Shopee bestsellers" | Hot-selling product discovery |
| "Search for XX product on Shopee" | Keyword product search |
| "Newly listed products on Malaysia site" | New product discovery by listing date |
| "Products with over 1000 sales" | Volume-based product filtering |
| "Which categories have opportunities in SE Asia" | Category-level opportunity scan |
| "Show me products from this store" | Competitor shop analysis |
| "Compare cross-border vs local products" | Cross-border vs local comparison |
| "Shopee Verified product filtering" | Shopee Verified product filtering |
| "Low price, high sales products" | Price-volume opportunity mining |

**Not applicable** - Needs beyond Shopee product search:
- Product search on other platforms such as Amazon, TikTok, eBay, 1688
- Shopee advertising strategy
- Shopee store operations advice
- Shopee logistics/warehousing solutions
- Processing of local Shopee data files that already exist

**Boundary judgment**: When users say "SE Asia product selection," "Shopee market analysis," or "cross-border e-commerce product selection," if it boils down to searching and filtering products on Shopee by various criteria, this skill applies. If they're asking about logistics planning, advertising strategy, or store operations, it does not apply.
