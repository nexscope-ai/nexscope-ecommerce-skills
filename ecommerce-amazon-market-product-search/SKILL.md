---
name: ecommerce.amazon-market-product-search
description: Multi-dimensional Amazon product search and filtering based on Sorftime data, covering 14 marketplaces, with support for historical monthly snapshot lookback. Trigger when the user mentions Sorftime product search, Amazon product filtering, competitor research, category analysis, brand bestsellers, seller analysis, seasonal products, historical snapshot review, product search, monthly sales/revenue, ABA keyword product discovery, price range filtering, new product discovery, multi-condition combined filtering, product search, competitor research, category analysis, brand bestsellers, seller analysis, seasonal products, historical snapshot. Even if the user does not explicitly mention "Sorftime", if their need involves Amazon product search, filtering, comparison, or product exploration by category/brand/seller dimensions, this skill should also be triggered.
---

# Sorftime Product Search

This skill guides you on how to search and filter Amazon products via Sorftime across multiple dimensions, helping Amazon sellers discover products, analyze competitors, and explore market opportunities.

## Core Concepts

Sorftime Product Search supports multi-dimensional product retrieval with 16 query types, single or multi-condition AND combinations, and historical monthly snapshot lookback from January 2024. Data covers pricing, BSR rankings, monthly sales, FBA fees, and profit analysis.

**Key differentiator**: This tool is for searching and filtering across products. If you need detailed trend data (sales/price/BSR history) for a specific ASIN, use the Sorftime Product Detail skill instead.

## Data Fields

Response data covers the following categories (see `references/api.md` for complete field reference):

- **Basic info**: ASIN, title, brand, listing URL, images (main + list), parent ASIN, variation count, weight, size
- **Pricing & profit**: current price, sale price (after coupon), strikethrough price, coupon, FBA fees (with detail breakdown), platform fee, profit amount & rate
- **Sales**: monthly sales units, monthly revenue, daily sales, daily revenue (values of -1 = cannot estimate)
- **Rankings**: BSR rank, category, sub-category rankings
- **Ratings**: rating score, rating count
- **Listing info**: listing date, days online
- **Seller**: Buybox seller name/ID/country, FBA status, seller count
- **Listing features**: A+ content, video, brand store

## Supported Marketplaces

US (United States), GB (United Kingdom), DE (Germany), FR (France), IN (India), CA (Canada), JP (Japan), ES (Spain), IT (Italy), MX (Mexico), AE (United Arab Emirates), AU (Australia), BR (Brazil), SA (Saudi Arabia)

Default marketplace is **US**. Use `us` when the user doesn't specify a marketplace.

**Note**: Sorftime uses lowercase codes (e.g., `us`, `gb`, `de`), and UK is coded as `gb` (not `uk`).

## How to Invoke

- **API Endpoint**: `POST /sorftime/amazon/productQuery` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_market_product_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sorftime-amazon-product-query-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

The key parameters are `marketplace` (required), `queryMode`, `queryType`, and `queryValue`. The query system has two modes and 16 filter types that can be combined flexibly.

### Principles for Building Queries

1. **Always specify the marketplace**: Use lowercase site codes, e.g., `us`, `de`, `jp`
2. **Choose the right query mode**: Use `queryMode=1` for a single filter; use `queryMode=2` to combine multiple filters with AND logic
3. **Match queryType with queryValue format**: Each queryType expects a specific format - see the table below. Mismatched formats will cause errors
4. **Mind price units**: Price filters (queryType=8) use smallest currency unit (cents for USD), so $19.99 = `1999`
5. **Use open ranges when appropriate**: Omit one end for open range - `,1000` means "up to 1000"; `100,` means "100 or more"
6. **Use queryMonth for historical comparison**: Format `yyyy-MM`; compare with a second call without queryMonth to see changes over time

### Query Types (queryType, for queryMode=1)

| queryType | Name | queryValue Format | Example |
|-----------|------|-------------------|---------|
| 1 | ASIN Similar | ASIN | `B0CVM8TXHP` |
| 2 | Category | NodeId | `3743561` |
| 3 | Brand | Brand name | `Anker` |
| 4 | Seller Name | Store name | `AnkerDirect` |
| 5 | Seller ID | SellerId | `A294P4X9EWVXLJ` |
| 6 | ABA Keyword | Keyword | `Power Bank` |
| 7 | Title/Attribute Match | Keywords | `10,000mAh 30W` |
| 8 | Price Range | `min,max` (in cents) | `1,1000` (=$0.01~$10) |
| 9 | Monthly Sales Range | `min,max` | `100,1000` |
| 10 | Seasonal Products | Month list | `1,2,3` (peak in Jan-Mar) |
| 11 | Listing Date Range | `start,end` (yyyy-MM-dd) | `2024-06-01,2024-12-01` |
| 12 | Rating Range | `min,max` | `3,5` |
| 13 | Review Count Range | `min,max` | `10,500` |
| 14 | Rank Range | `bsr_min,bsr_max;sub_min,sub_max` | `500,5000;1,100` |
| 15 | Fulfillment | `FBA` / `FBM` | `FBA,FBM` |
| 16 | Variation Count | `min,max` | `1,50` |

**Important**: queryType=1 (ASIN Similar) finds products similar to the given ASIN, not the ASIN itself. To query a single product's detail, use the Sorftime Product Detail skill.

### Historical Snapshots (queryMonth)

Set `queryMonth` (format `yyyy-MM`) to query a past month's product data snapshot. This lets users compare historical prices, rankings, and sales with current data.

- Supported range: January 2024 to present (~2 years)
- US, GB, DE support full "unlimited" lookback mode
- Other sites support Top 100 products only in lookback
- AU, BR, IN do **not** support lookback

### Query Examples for Common Scenarios

**1. Competitors of a given ASIN**
```
queryMode: 1, queryType: 1, queryValue: B0CVM8TXHP, marketplace: us
```

**2. Browse a category's top products**
```
queryMode: 1, queryType: 2, queryValue: 3743561, marketplace: us
```

**3. Analyze a brand's product portfolio**
```
queryMode: 1, queryType: 3, queryValue: Anker, marketplace: us
```

**4. Search by ABA keyword**
```
queryMode: 1, queryType: 6, queryValue: Power Bank, marketplace: us
```

**5. Discover seasonal products (Q4 peak)**
```
queryMode: 1, queryType: 10, queryValue: 10,11,12, marketplace: us
```

**6. Compare historical vs current data**
```
queryMonth: 2024-11, queryMode: 1, queryType: 2, queryValue: 3743561, marketplace: us
-> Compare with current data (no queryMonth) to see price/sales changes
```

**7. Multi-condition: new FBA products with good sales**
```
queryMode: 2
queryValue: [{"QueryType":11,"Content":"2024-06-01,"},{"QueryType":9,"Content":"300,"},{"QueryType":15,"Content":"FBA"}]
marketplace: us
```

**8. Find low-price high-sales products**
```
queryMode: 2
queryValue: [{"QueryType":8,"Content":",2000"},{"QueryType":9,"Content":"500,"}]
marketplace: us
```

**9. Check a seller's product portfolio**
```
queryMode: 1, queryType: 4, queryValue: AnkerDirect, marketplace: us
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Pagination notice**: Search results return max 100 products per page, up to 200 pages. If results are large, show highlights and remind users to paginate
4. **Sales estimation caveat**: Values of `-1` in sales/revenue fields mean "cannot estimate" - explain this to the user rather than showing -1 directly
5. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria

## Important Limitations

- **Pagination**: Max 100 products per page, max 200 pages
- **Historical snapshots**: AU, BR, IN do not support historical lookback
- **Non-structured data**: Results do not support secondary analysis via `_dataQuery_executeDynamicQuery`
- **Sales estimation**: Products in non-standard categories may return -1 for sales fields
- **ABA keyword search** (queryType=6): Currently only supports ABA keywords, not arbitrary search terms

## User Expression & Scenario Quick Reference

**Applicable** -- Product search and filtering on Amazon:

| User Says | Scenario |
|-----------|----------|
| "Find the top-selling products in this category" | Category exploration |
| "What are Anker's hot-selling products" | Brand analysis |
| "What are the competitors for this ASIN" | Competitor discovery |
| "Help me find some seasonal products" | Seasonal product discovery |
| "Which new products have monthly sales above 500" | Filtered product discovery |
| "Price snapshot for this category during last year's peak season" | Historical snapshot comparison |
| "What else does this seller sell" | Seller portfolio |
| "Help me filter FBA products with profit margin above 30%" | Profit-focused filtering |
| "Products with 1000+ monthly sales and 4+ star rating" | Multi-condition filtering |
| "Products with wireless charger in the title" | Title keyword search |

**Not applicable** -- Needs beyond product search:
- Detailed trend/history data for a specific ASIN (use Sorftime Product Detail)
- ABA search term ranking data (use ABA Data Explorer)
- Advertising / PPC strategy
- Product reviews content analysis
- Patent or trademark checks

**Boundary judgment**: When users say "competitor analysis" or "market research", if they need to discover and compare products across dimensions (category, brand, price range, etc.), this skill applies. If they need historical trend curves for a specific ASIN, use the Product Detail skill. If they need keyword search volume data, use ABA Data Explorer.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
