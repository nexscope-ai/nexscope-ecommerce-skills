---
name: ecommerce-amazon-product-discovery
description: "Amazon product discovery and potential bestseller mining via Jiimore data. Triggered when users mention product mining, potential bestsellers, high-conversion product selection, click growth analysis, market growth opportunities, keyword-based product selection, FBA profit screening, niche market product discovery, seller origin filtering, Jiimore data, FBA profitability screening, keyword-based product selection. Even if users do not explicitly mention \"Jiimore\", this skill should be triggered whenever the task involves keyword-driven Amazon product selection based on conversion rates, click volume, and profitability metrics."
---

# Jiimore Product Discovery

This skill guides you on how to discover and mine high-potential Amazon products using the Jiimore product discovery engine, helping Amazon sellers find potential bestsellers through keyword-based filtering with conversion, click growth, and profitability indicators.

## Core Concepts

Jiimore Product Discovery is a keyword-driven Amazon product mining tool. Given a search keyword, it returns a list of products matching specified performance criteria such as conversion rate, click growth rate, gross profit margin, pricing, reviews, and listing age. This makes it ideal for identifying emerging opportunities, validating product ideas, and competitive benchmarking.

**Keyword is required**: Every query must include a `keyword`. The keyword should be translated into the language of the target marketplace (e.g., Japanese for JP, German for DE).

**Rate values are decimals**: Conversion rates and growth rates are expressed as decimals between 0 and 1. For example, `0.1` means 10%, `0.25` means 25%. This is a common point of confusion when users specify percentages.

**Marketplace support**: Currently supports US (United States), JP (Japan), and DE (Germany). Default is **US**. Use US when the user does not specify a marketplace.

## Parameter Guide

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| keyword | Search keyword (must be translated to the target marketplace language) | wireless charger |

### Filtering Parameters

| Parameter | Description | Value Format |
|-----------|-------------|--------------|
| priceMin / priceMax | Product price range | Number (e.g., 10.0, 50.0) |
| totalReviewsMin / totalReviewsMax | Review count range | Integer (e.g., 0, 500) |
| customerRatingMin / customerRatingMax | Customer rating range | Number (e.g., 4.0, 5.0) |
| clickConversionRateMin / clickConversionRateMax | Click-to-purchase conversion rate | Decimal 0-1 (0.1 = 10%) |
| clickConversionRateCompositeMin / clickConversionRateCompositeMax | Composite conversion rate | Decimal 0-1 (0.1 = 10%) |
| clickCountT7Min / clickCountT7Max | Weekly click count range | Integer |
| clickCountT30Min / clickCountT30Max | Monthly click count range | Integer |
| clickCountGrowthT7Min / clickCountGrowthT7Max | Weekly click growth rate | Decimal 0-1 (0.1 = 10%) |
| clickCountGrowthT30Min / clickCountGrowthT30Max | Monthly click growth rate | Decimal 0-1 (0.1 = 10%) |
| salesVolumeT360Min / salesVolumeT360Max | Annual sales volume range | Integer |
| grossProfitMarginMin / grossProfitMarginMax | Gross profit margin range | Number |
| fbaFeeMin / fbaFeeMax | FBA fee range | Number |
| launchDateMin / launchDateMax | Listing date range | String: yyyyMMdd000000 |
| nicheCountMin / nicheCountMax | Niche market count range | Integer |
| sellerCountry | Seller origin country code(s), comma-separated | CN,US |
| countryCode | Target marketplace (US, JP, DE) | US |

### Sorting and Pagination

| Parameter | Description | Default |
|-----------|-------------|---------|
| sortField | Sort by field (see options below) | purchasedClicksT360 |
| sortType | Sort direction: `desc` or `asc` | desc |
| page | Page number | 1 |
| pageSize | Results per page (10-100) | 50 |

**Available sort fields**: totalReviews, price, launchDate, clickCountT7, clickCountT30, clickCountT90, clickConversionRate, clickConversionRateComposite, customerRating, purchasedClicksT360, clickCountGrowthT7, clickCountGrowthT30, currentPrice, fbaFee, shippingFee, gpm

## API Invocation

- **API Endpoint**: `POST /jiimore/productDiscovery` (see `references/api.md` for full parameters/responses/error codes)
- **Python Script**: `python scripts/amazon_product_discovery.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination in the same session is only called once by default, with 24h local caching in the script. Failed or empty results should not trigger automatic retries with different keywords, pagination, or postal codes. Inform the user before making additional queries that will incur extra costs.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-jiimore-product-discovery-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body less than or equal to 8 KB: print the full JSON to stdout after saving to disk
- Response body greater than 8 KB: after saving, stdout prints only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data Reading Tips**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Usage Examples

**1. Find high-conversion wireless chargers in the US market**
```json
{
  "keyword": "wireless charger",
  "countryCode": "US",
  "clickConversionRateMin": 0.1,
  "sortField": "clickConversionRate",
  "sortType": "desc"
}
```

**2. Discover fast-growing new products (listed within the last 6 months, weekly click growth greater than 20%)**
```json
{
  "keyword": "desk lamp",
  "countryCode": "US",
  "launchDateMin": "20250901000000",
  "clickCountGrowthT7Min": 0.2,
  "sortField": "clickCountGrowthT7",
  "sortType": "desc"
}
```

**3. Find underpriced high-margin products with low competition (few reviews)**
```json
{
  "keyword": "phone stand",
  "countryCode": "US",
  "priceMin": 10,
  "priceMax": 30,
  "totalReviewsMax": 100,
  "grossProfitMarginMin": 0.3,
  "sortField": "gpm",
  "sortType": "desc"
}
```

**4. Mine products from Chinese sellers with strong monthly click growth in the German market**
```json
{
  "keyword": "Handyhuelle",
  "countryCode": "DE",
  "sellerCountry": "CN",
  "clickCountGrowthT30Min": 0.15,
  "sortField": "clickCountGrowthT30",
  "sortType": "desc"
}
```

**5. Find high-rated products with strong annual sales in the Japanese market**
```json
{
  "keyword": "ワイヤレスイヤホン",
  "countryCode": "JP",
  "customerRatingMin": 4.0,
  "salesVolumeT360Min": 1000,
  "sortField": "purchasedClicksT360",
  "sortType": "desc"
}
```

**6. Identify niche opportunities with high composite conversion and multiple niche markets**
```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "clickConversionRateCompositeMin": 0.15,
  "nicheCountMin": 3,
  "sortField": "clickConversionRateComposite",
  "sortType": "desc"
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables, including product title, ASIN, price, ratings, conversion rates, click counts, and growth rates
2. **Rate formatting**: Always display rate values as percentages for readability (e.g., show 0.12 as 12%). Remind users that the API accepts decimals (0-1)
3. **Image display**: When product image URLs are available, display the main product image alongside the data
4. **Pagination awareness**: When results span multiple pages, inform the user of the total count and current page, and offer to fetch additional pages
5. **Keyword translation reminder**: Remind users that keywords must be in the target marketplace language (English for US, Japanese for JP, German for DE)
6. **Error handling**: When a query fails, explain the reason based on the response and suggest adjusting query criteria
7. **No subjective advice**: Present factual product data without making subjective business recommendations
## Important Limitations

- **Keyword is mandatory**: Every query requires a keyword; browsing without a keyword is not supported
- **Three marketplaces only**: Currently limited to US, JP, and DE
- **Page size cap**: Maximum 100 results per page
- **Rate values**: All rate/percentage parameters must be passed as decimals (0-1), not percentages
- **Launch date format**: Must follow the `yyyyMMdd000000` format exactly (e.g., `20250101000000`)

## User Expression and Scenario Quick Reference

**Applicable** -- Product discovery and mining tasks:

| User Says | Scenario |
|-----------|----------|
| "Find hot products for keyword X" | Keyword-based product discovery |
| "High conversion products", "best sellers" | High-conversion product screening |
| "Fast growing products", "trending items" | Click growth-based discovery |
| "New products with high potential" | New listing + growth filtering |
| "Products with good margins", "profitable items" | Gross profit margin screening |
| "Low competition products", "few reviews" | Low-review opportunity mining |
| "Products from Chinese sellers" | Seller origin filtering |
| "Niche market opportunities" | Niche count-based discovery |

**Not applicable** -- Needs beyond product discovery:

- ABA search term data and keyword analysis (use ABA Data Explorer)
- Advertising / PPC campaign management
- Product reviews and listing optimization
- Inventory management and supply chain
- Comprehensive market reports with profit/pricing strategy
