---
name: ecommerce.amazon-competitor-lookup
description: Use SellerSprite data to find and analyze competitors on Amazon, covering 12 marketplaces, with product metrics including sales, BSR, pricing, ratings, and growth trends. Trigger when the user mentions competitor lookup, competitor analysis, ASIN reverse lookup, competitive product research, finding similar products, market competitor discovery, product benchmarking, competitor sales estimation, analyzing competitor listings, competitor analysis, ASIN reverse lookup, competitor sales, competitor research, SellerSprite, market competitor discovery, competitor trends. Even if the user does not explicitly mention "SellerSprite" or "competitor lookup", if their need involves discovering and analyzing Amazon competitors by ASIN, keyword, seller name, brand, or category, this skill should also be triggered.
---

# SellerSprite Competitor Lookup

This skill guides you on how to query and analyze Amazon competitor product data, helping Amazon sellers discover competing products, benchmark performance, and extract actionable competitive intelligence.

## Core Concepts

The SellerSprite Competitor Lookup tool provides comprehensive Amazon product data across 12 marketplaces. It allows querying products by ASIN, keyword, seller name, brand, or category, and returns detailed metrics including monthly sales volume, revenue, BSR ranking, pricing, ratings, and growth trends.

**Data snapshots**: The tool supports both real-time data (last 30 days) and historical monthly snapshots. Use `nearly` (default) for current data or a `yyyyMM` format (e.g., `202501`) for historical snapshots. Historical snapshots capture all active listings for that month, enabling year-over-year and seasonal comparisons.

**Category hierarchy**: Amazon category names support multi-level paths separated by colons (`:`). For example, `Electronics:Computers & Accessories:Monitors`. Convert user-provided category descriptions into the proper colon-separated format.

## Supported Marketplaces

US (United States), UK (United Kingdom), DE (Germany), FR (France), JP (Japan), CA (Canada), IT (Italy), ES (Spain), MX (Mexico), AU (Australia), TR (Turkey), IN (India)

Default marketplace is **US**. Use US when the user does not specify a marketplace.

## Parameter Guide

### Search Filters

| Parameter | Description | Example |
|-----------|-------------|---------|
| marketplace | Amazon marketplace code | `US`, `UK`, `DE`, `JP` |
| keyword | Search keyword (translate to the marketplace language) | `wireless earbuds` |
| asinList | One or more ASINs, comma-separated (max 40) | `B072MQ5BRX,B08N5WRWNW` |
| sellerName | Seller name to filter by | `Anker Direct` |
| brand | Brand name to filter by | `Anker` |
| nodeLabel | Amazon category name (colon-separated levels) | `Electronics:Headphones` |
| nodeIdPath | Amazon category ID path | `172282` |
| matchType | Keyword match mode: 1 = phrase, 2 = fuzzy, 3 = exact (default 1) | `1` |
| showVariation | Show product variations: `Y` or `N` (default `N`) | `N` |
| dataSnapshotMonth | Data snapshot month (`nearly` for real-time, or `yyyyMM`) | `nearly` |

### Pagination & Sorting

| Parameter | Description | Example |
|-----------|-------------|---------|
| page | Page number, starting from 1 | `1` |
| size | Results per page, 10-100 (default 50) | `50` |
| order.field | Sort field (see sort options below) | `total_units` |
| order.desc | Sort direction: `true` = descending, `false` = ascending | `true` |

### Sort Field Options

| Field | Description |
|-------|-------------|
| total_units | Monthly sales units |
| total_amount | Monthly sales revenue |
| bsr_rank | BSR ranking |
| price | Price |
| rating | Rating score |
| reviews | Number of reviews |
| profit | Gross margin |
| reviews_rate | Review rate |
| available_date | Listing date |
| questions | Q&A count |
| total_units_growth | Monthly sales unit growth rate |
| total_amount_growth | Monthly revenue growth rate |
| reviews_increasement | Monthly new reviews |
| bsr_rank_cv | 7-day BSR growth count |
| bsr_rank_cr | 7-day BSR growth rate |
| amz_unit | Variant sales units |

### Key Response Fields

| Field | Description |
|-------|-------------|
| asin | Product ASIN |
| title | Product title |
| price | Current price |
| monthlySalesUnits | Monthly sales volume |
| monthlySalesRevenue | Monthly sales revenue |
| bsr | BSR ranking |
| bsrGrowthRate | BSR growth rate |
| bsrGrowthCount | BSR growth count |
| rating | Rating score |
| ratings | Number of ratings |
| ratingsGrowth | Monthly new ratings |
| ratingsRate | Review rate |
| brand | Brand name |
| sellerName | BuyBox seller |
| sellerNation | BuyBox seller nationality |
| fulfillment | Fulfillment type (AMZ/FBA/FBM) |
| availableDateString | Listing date |
| profit | Gross margin |
| nodeLabelPath | Category path |
| imageUrl | Product image URL |
| monthlySalesUnitsGrowthRate | Monthly sales growth rate |
| listingQualityScore | Listing quality score |
| variationNum | Number of variations |
| parent | Parent ASIN |
| badgeBestSeller | Best Seller badge (Y/N) |
| badgeAmazonChoice | Amazon's Choice badge (Y/N) |
| badgeEbc | A+ Content (Y/N) |
| badgeVideo | Video present (Y/N) |

## How to Invoke

- **API Endpoint**: `POST /sellersprite/competitor-lookup` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_competitor_lookup.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sellersprite-competitor-lookup-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Usage Examples

**1. Look up competitors by ASIN**
```json
{
  "marketplace": "US",
  "asinList": "B072MQ5BRX,B08N5WRWNW"
}
```
Use case: Analyze specific competing products by their ASINs.

**2. Search competitors by keyword**
```json
{
  "marketplace": "US",
  "keyword": "wireless earbuds",
  "matchType": 1,
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
Use case: Discover top-selling products for a keyword, sorted by monthly sales.

**3. Filter by brand and category**
```json
{
  "marketplace": "US",
  "brand": "Anker",
  "nodeLabel": "Electronics:Headphones",
  "order": {"field": "total_amount", "desc": "true"}
}
```
Use case: Analyze a specific brand's product lineup within a category.

**4. Find products by seller name**
```json
{
  "marketplace": "DE",
  "sellerName": "Anker Direct",
  "order": {"field": "bsr_rank", "desc": "false"}
}
```
Use case: View all products from a particular seller sorted by BSR.

**5. Historical snapshot comparison**
```json
{
  "marketplace": "US",
  "keyword": "space heater",
  "dataSnapshotMonth": "202412",
  "order": {"field": "total_units", "desc": "true"},
  "size": 20
}
```
Use case: Analyze seasonal product performance using historical data snapshots.

**6. Show product variations**
```json
{
  "marketplace": "JP",
  "asinList": "B0XXXXXXXXX",
  "showVariation": "Y"
}
```
Use case: Examine all variation-level data for a product family.

## Display Rules

1. **Present data clearly**: Show query results in well-formatted tables. Include key metrics such as ASIN, title, price, monthly sales, BSR, rating, and brand. Do not provide subjective business advice unless the user asks for it.
2. **Keyword language**: When searching by keyword, always translate the keyword to the target marketplace language (e.g., English for US/UK, German for DE, Japanese for JP). Remind the user of this if they provide keywords in the wrong language.
3. **BSR clarification**: When displaying BSR data, remind users that a lower BSR value indicates stronger sales performance.
4. **Growth metrics**: When showing growth rates, clarify whether positive values mean improvement or decline (positive BSR growth count means BSR increased, which means worsened ranking).
5. **Pagination notice**: When the total result count exceeds the returned page size, inform the user of the total count and offer to fetch additional pages.
6. **Badge highlights**: When products carry badges (Best Seller, Amazon's Choice, A+ Content, Video), highlight these in the results as they are important competitive signals.
7. **Error handling**: When a query fails, explain the reason based on the `message` field and suggest adjusting query parameters.
8. **Snapshot guidance**: When users want to do seasonal or trend analysis, proactively suggest using historical snapshots (e.g., last year's same month) for comparison.
## Important Limitations

- **Result cap**: Each page returns 10-100 records (controlled by `size`). Use pagination for larger result sets.
- **ASIN limit**: A maximum of 40 ASINs can be queried at once via `asinList`.
- **Historical snapshots**: Only existing monthly snapshots can be queried; future dates are not supported.
- **Keyword language**: Keywords should match the marketplace language for best results.

## User Expression & Scenario Quick Reference

**Applicable** -- Amazon competitor product data queries:

| User Says | Scenario |
|-----------|----------|
| "Find competitors for this ASIN" | ASIN-based competitor lookup |
| "Top sellers for wireless earbuds" | Keyword-based product discovery |
| "What is this seller selling" | Seller product portfolio analysis |
| "Show me products in Electronics category" | Category-based browsing |
| "Monthly sales for these ASINs" | Sales estimation for specific products |
| "New products gaining traction" | Growth trend detection |
| "Compare products across brands" | Brand benchmarking |
| "How was this niche last December" | Historical snapshot analysis |
| "Best sellers with high ratings" | Multi-metric filtering |
| "FBA vs FBM in this category" | Fulfillment type analysis |

**Not applicable** -- Needs beyond competitor product data:

- ABA search term data or keyword ranking (use ABA Data Explorer instead)
- Advertising / PPC campaign management
- Product reviews content or sentiment analysis
- Listing copywriting or optimization suggestions
- Supplier sourcing or manufacturing costs
- Account health or policy compliance

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://os.nexscope.com/ to top up credits.
