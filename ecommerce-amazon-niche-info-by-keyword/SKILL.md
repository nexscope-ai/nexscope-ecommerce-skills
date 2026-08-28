---
name: ecommerce-amazon-niche-info-by-keyword
description: "Deep analysis of Amazon niche markets by keyword, covering monopoly level, brand concentration, new product success rate, and market opportunity score. Trigger when the user mentions niche market analysis, keyword market research, monopoly assessment, brand concentration analysis, new product success rate, market demand score, competitive landscape, Amazon sub-market exploration, niche market analysis, keyword market, monopoly level, brand concentration, new product success rate, market opportunity score, competitive landscape, Jiimore data. Even if the user does not explicitly mention \"niche market\", if their need involves evaluating the competitive landscape, brand density, or opportunity potential of the Amazon market at the keyword dimension level, this skill should also be triggered."
---

# Jiimore Niche Info by Keyword

This skill guides you on how to query and analyze Amazon niche market data by keyword, helping Amazon sellers evaluate market segments for competitive intensity, brand maturity, pricing structure, and entry opportunity.

## How to Invoke

- **API Endpoint**: `POST /jiimore/getNicheInfoByKeyword` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_niche_info_by_keyword.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-jiimore-get-niche-info-by-keyword-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Core Concepts

A **niche** (sub-market segment) is a grouping of products that share a common keyword theme on Amazon. This tool returns rich analytical dimensions for each niche, including search volume, sales volume, click-through rates, brand count, top-brand concentration, new product launch success rates, CPC estimates, and a composite demand score. Data is available for **US**, **JP**, and **DE** marketplaces.

**Keyword is required**: Every query must include a `keyword`. The keyword should be provided in the language of the target marketplace (e.g., English for US, Japanese for JP, German for DE). When the user provides a keyword in a different language, translate it to the marketplace language before calling the API.

**Percentage fields**: Several parameters and response fields use a 0-1 decimal range representing 0%-100%. When displaying these values to users, convert them to percentages (e.g., 0.35 -> 35%).

**Demand score**: The `demand` field is a composite opportunity score assigned to each niche. A higher value indicates greater market demand potential.

## Parameter Guide

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| keyword | string | Search keyword (max 1000 chars). Translate to the target marketplace language. |

### Marketplace & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, DE |
| page | integer | 1 | Page number (starts from 1) |
| pageSize | integer | 50 | Results per page (10-100) |
| sortField | string | unitsSoldT7 | Field to sort by (see Sorting Options below) |
| sortType | string | desc | Sort direction: `desc` or `asc` |

### Filter Parameters (all optional, min/max ranges)

**Product & Pricing**:
| Parameter | Type | Description |
|-----------|------|-------------|
| productCountMin / productCountMax | integer | Product count range |
| avgPriceMin / avgPriceMax | number | Average price range |

**Search & Sales (7-day)**:
| Parameter | Type | Description |
|-----------|------|-------------|
| searchVolumeT7Min / searchVolumeT7Max | integer | Weekly search volume range |
| unitsSoldT7Min / unitsSoldT7Max | integer | Weekly units sold range |
| clickCountT7Min / clickCountT7Max | integer | Weekly click count range |
| clickConversionRateT7Min / clickConversionRateT7Max | number | Weekly click conversion rate (0-1) |

**Brand Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| brandCountMin / brandCountMax | integer | Number of brands in niche |
| top5BrandsClickShareMin / top5BrandsClickShareMax | number | Top 5 brands click share (0-1) |
| avgBrandAgeMin / avgBrandAgeMax | number | Average brand age (current) |
| avgBrandAgeQoqMin / avgBrandAgeQoqMax | number | Average brand age (90-day) |
| avgBrandAgeYoyMin / avgBrandAgeYoyMax | number | Average brand age (360-day) |

**Seller Metrics**:
| Parameter | Type | Description |
|-----------|------|-------------|
| avgSellingPartnerAgeMin / avgSellingPartnerAgeMax | number | Average seller age (current) |
| avgSellingPartnerAgeQoqMin / avgSellingPartnerAgeQoqMax | number | Average seller age (90-day) |
| avgSellingPartnerAgeYoyMin / avgSellingPartnerAgeYoyMax | number | Average seller age (360-day) |

**Competition & Advertising**:
| Parameter | Type | Description |
|-----------|------|-------------|
| top5ProductsClickShareMin / top5ProductsClickShareMax | number | Top 5 products click share (0-1) |
| sponsoredProductsPercentageMin / sponsoredProductsPercentageMax | number | SP ad percentage (0-1) |
| cpcMediumMin / cpcMediumMax | number | CPC median value range |

**New Product & Returns**:
| Parameter | Type | Description |
|-----------|------|-------------|
| launchRateT180Min / launchRateT180Max | number | 180-day new product success rate (0-1) |
| newProductRateT180 | number | 180-day new product ratio minimum (0-1) |
| returnRateT360Min / returnRateT360Max | number | 360-day return rate (0-1) |

### Sorting Options

| Value | Meaning |
|-------|---------|
| unitsSoldT7 | Weekly units sold |
| searchVolumeT7 | Weekly search volume |
| demand | Demand score |
| avgPrice | Average price |
| maximumPrice | Maximum price |
| minimumPrice | Minimum price |
| productCount | Product count |
| searchConversionRateT7 | Weekly search conversion rate |
| clickConversionRateT7 | Weekly click conversion rate |
| searchVolumeGrowthT7 | Search volume growth rate |
| clickCountT7 | Weekly click count |
| clickCountT90 | 90-day click count |
| brandCount | Brand count |
| top5BrandsClickShare | Top 5 brands click share |
| top5ProductsClickShare | Top 5 products click share |
| newProductsLaunchedT180 | 180-day new products launched |
| successfulLaunchesT180 | 180-day successful launches |
| launchRateT180 | 180-day launch success rate |
| returnRateT360 | Annual return rate |
| clickConversionRateT90 | 90-day click conversion rate |
| searchConversionRateT90 | 90-day search conversion rate |
| searchVolumeT90 | 90-day search volume |
| unitsSoldT90 | 90-day units sold |
| unitsSoldGrowthT90 | 90-day sales growth rate |
| searchVolumeGrowthT90 | 90-day search volume growth rate |
| acos | Advertising cost of sales |
| profitRate50 | Profit margin at 50% organic sales |

## Usage Examples

**1. Basic niche exploration by keyword**
Query niches related to "wireless earbuds" in the US market, sorted by weekly sales volume:
```json
{
  "keyword": "wireless earbuds",
  "countryCode": "US",
  "sortField": "unitsSoldT7",
  "sortType": "desc"
}
```

**2. Low-competition niche discovery**
Find niches for "yoga mat" where the top 5 brands hold less than 50% click share and brand count exceeds 20:
```json
{
  "keyword": "yoga mat",
  "countryCode": "US",
  "top5BrandsClickShareMax": 0.5,
  "brandCountMin": 20,
  "sortField": "demand",
  "sortType": "desc"
}
```

**3. High-demand, high-conversion niches**
Find niches for "phone case" with weekly search volume above 10000 and click conversion rate above 10%:
```json
{
  "keyword": "phone case",
  "countryCode": "US",
  "searchVolumeT7Min": 10000,
  "clickConversionRateT7Min": 0.1,
  "sortField": "searchVolumeT7",
  "sortType": "desc"
}
```

**4. New product opportunity analysis**
Find niches for "LED light" with high new product success rate (above 20%) and low return rate (below 5%):
```json
{
  "keyword": "LED light",
  "countryCode": "US",
  "launchRateT180Min": 0.2,
  "returnRateT360Max": 0.05,
  "sortField": "launchRateT180",
  "sortType": "desc"
}
```

**5. Japanese market niche research**
Explore niches related to headphones in Japan, sorted by demand score:
```json
{
  "keyword": "headphone",
  "countryCode": "JP",
  "sortField": "demand",
  "sortType": "desc"
}
```

**6. Price-range-specific niche analysis**
Find niches for "backpack" with average price between $20 and $50 and low advertising saturation:
```json
{
  "keyword": "backpack",
  "countryCode": "US",
  "avgPriceMin": 20,
  "avgPriceMax": 50,
  "sponsoredProductsPercentageMax": 0.3,
  "sortField": "unitsSoldT7",
  "sortType": "desc"
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Convert decimal ratios to percentages for readability (e.g., 0.25 -> 25%).
2. **Highlight key metrics**: Always surface the niche title, demand score, weekly search volume, weekly sales, brand count, and top 5 brands click share as primary columns.
3. **Translate niche titles**: When the `translationZh` field is present and the user prefers Chinese, show it alongside the original `nicheTitle`.
4. **Pagination guidance**: When `total` exceeds the current page size, inform the user of the total count and suggest fetching additional pages if needed.
5. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting filter criteria (e.g., broadening ranges or checking the keyword).
6. **CPC display**: When CPC data is present, show all three tiers (low, medium, high) to give a complete advertising cost picture.
7. **No subjective advice**: Present data objectively without adding unsolicited business recommendations. Only provide interpretation when explicitly requested by the user.
## Important Limitations

- **Supported marketplaces**: Only US, JP, and DE are available. Other marketplace codes will be rejected.
- **Keyword required**: Every query must include a keyword. The API will not return results without one.
- **Result cap**: Maximum 100 results per page.
- **Percentage values**: All rate/share parameters use 0-1 range, not 0-100. Ensure correct values when constructing filters.

## User Expression & Scenario Quick Reference

**Applicable** -- Niche-level market segment analysis by keyword:

| User Says | Scenario |
|-----------|----------|
| "Is there opportunity in the XX market" | Niche opportunity assessment |
| "How competitive is XX keyword" | Monopoly / brand concentration |
| "Find low-competition niches for XX" | Blue ocean niche discovery |
| "What's the new product success rate for XX" | New entrant viability |
| "Show me niche data for XX" | General niche exploration |
| "Which XX niches have high demand" | Demand-driven niche ranking |
| "What's the CPC / ad cost for XX niches" | Advertising cost analysis |
| "Find niches with high conversion for XX" | Conversion-optimized segments |
| "Brand concentration in XX market" | Brand dominance assessment |

**Not applicable** -- Needs beyond niche-level segment data:
- Individual ASIN performance or sales estimation
- Search term ranking trends (use ABA data tools instead)
- Advertising campaign management or bid optimization
- Product review analysis or listing optimization
- Supplier sourcing or logistics planning

**Boundary judgment**: When users say "market research" or "product opportunity", if their intent focuses on evaluating the competitive landscape and demand potential of keyword-level market segments, this skill applies. If they need ASIN-level data, search term ranking trends, or comprehensive business strategy, direct them to the appropriate tool.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
