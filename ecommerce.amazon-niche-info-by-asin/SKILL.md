---
name: ecommerce.amazon-niche-info-by-asin
description: Deep analysis of Amazon niche markets by product ASIN, covering monopoly level, brand concentration, new product success rate, and market opportunity score. Trigger when the user mentions niche market analysis by ASIN, ASIN market research, ASIN niche lookup, monopoly assessment, brand concentration analysis, new product success rate, market demand score, competitive landscape, Amazon sub-market exploration, ASIN niche analysis, niche by ASIN, monopoly level, brand concentration, new product success rate, market opportunity score, competitive landscape, Jiimore data. Even if the user does not explicitly mention "niche market" or "ASIN", if their need involves evaluating the competitive landscape, brand density, or opportunity potential of the niche segment a specific product ASIN belongs to, this skill should also be triggered.
---

# Jiimore Niche Info by ASIN

This skill guides you on how to query and analyze Amazon niche market data by a reference ASIN, helping Amazon sellers evaluate market segments for competitive intensity, brand maturity, pricing structure, and entry opportunity.

## How to Invoke

- **API Endpoint**: `POST /jiimore/getNicheInfoByAsin` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_niche_info_by_asin.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different ASINs, marketplaces, or relaxed filters; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-jiimore-get-niche-info-by-asin-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Core Concepts

A **niche** (sub-market segment) is a grouping of products that share a common keyword theme on Amazon. Given a reference ASIN, this tool finds the niche segments that ASIN belongs to and returns rich analytical dimensions for each, including search volume, sales volume, click-through rates, brand count, top-brand concentration, new product launch success rates, CPC estimates, and a composite demand score. Data is available for **US**, **JP**, and **DE** marketplaces.

**ASIN is required**: Every query must include an `asin`. The tool locates the niche segments associated with that ASIN and returns them with detailed metrics. Use this when the user already has a specific product (ASIN) in hand and wants to understand the market segments it competes in -- as opposed to keyword-driven niche discovery.

**Percentage fields**: Several parameters and response fields use a 0-1 decimal range representing 0%-100%. When displaying these values to users, convert them to percentages (e.g., 0.35 -> 35%).

**Demand score**: The `demand` field is a composite opportunity score assigned to each niche. A higher value indicates greater market demand potential.

## Parameter Guide

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| asin | string | Reference product ASIN. The tool finds niche segments associated with this ASIN. |

### Marketplace & Count

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| countryCode | string | US | Country code: US, JP, DE |
| count | integer | 10 | Number of niche segments to return |

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
| returnRateT360Min / returnRateT360Max | number | 360-day return rate (0-1) |

## Usage Examples

**1. Basic niche exploration by ASIN**
Find the niche segments associated with ASIN `B0D9NWVC6Z` in the US market:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "count": 10
}
```

**2. Low-competition niche filtering by ASIN**
Find niches for an ASIN where the top 5 brands hold less than 50% click share and brand count exceeds 20:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "count": 20,
  "top5BrandsClickShareMax": 0.5,
  "brandCountMin": 20
}
```

**3. High-demand, high-conversion niches by ASIN**
Find niches for an ASIN with weekly search volume above 10000 and click conversion rate above 10%:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "searchVolumeT7Min": 10000,
  "clickConversionRateT7Min": 0.1
}
```

**4. New product opportunity analysis by ASIN**
Find niches for an ASIN with high new product success rate (above 20%) and low return rate (below 5%):
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "launchRateT180Min": 0.2,
  "returnRateT360Max": 0.05
}
```

**5. Japanese market niche research by ASIN**
Explore niches associated with an ASIN in the Japan market:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "JP",
  "count": 10
}
```

**6. Price-range-specific niche analysis by ASIN**
Find niches for an ASIN with average price between $20 and $50 and low advertising saturation:
```json
{
  "asin": "B0D9NWVC6Z",
  "countryCode": "US",
  "avgPriceMin": 20,
  "avgPriceMax": 50,
  "sponsoredProductsPercentageMax": 0.3
}
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables. Convert decimal ratios to percentages for readability (e.g., 0.25 -> 25%).
2. **Highlight key metrics**: Always surface the niche title, demand score, weekly search volume, weekly sales, brand count, and top 5 brands click share as primary columns.
3. **Translate niche titles**: When the `translationZh` field is present and the user prefers Chinese, show it alongside the original `nicheTitle`.
4. **Empty result handling**: When the response indicates no matching niche info (errcode 10000), explain that no niches matched the filters and suggest broadening ranges or verifying the ASIN.
5. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting filter criteria (e.g., broadening ranges or checking the ASIN/country).
6. **CPC display**: When CPC data is present, show all three tiers (low, medium, high) to give a complete advertising cost picture.
7. **No subjective advice**: Present data objectively without adding unsolicited business recommendations. Only provide interpretation when explicitly requested by the user.

## Important Limitations

- **Supported marketplaces**: Only US, JP, and DE are available. Other marketplace codes will be rejected.
- **ASIN required**: Every query must include an ASIN. The API will not return results without one.
- **No pagination/sorting**: This endpoint returns a fixed number of niches via `count` (default 10); it does not expose page/pageSize/sort parameters. Use the keyword-based niche skill when sorting or deeper pagination is needed.
- **Percentage values**: All rate/share parameters use 0-1 range, not 0-100. Ensure correct values when constructing filters.

## User Expression & Scenario Quick Reference

**Applicable** -- Niche-level market segment analysis driven by a reference ASIN:

| User Says | Scenario |
|-----------|----------|
| "Which niches does this ASIN belong to" | ASIN-to-niche mapping |
| "Analyze the market for ASIN XXXXX" | ASIN-driven niche assessment |
| "How competitive is the niche this product is in" | Monopoly / brand concentration by ASIN |
| "Find low-competition niches for this ASIN" | Blue ocean segment filtering |
| "What's the new product success rate for this ASIN's niches" | New entrant viability |
| "Show me niche data for this product" | General niche exploration by ASIN |
| "What's the CPC / ad cost for this ASIN's niches" | Advertising cost analysis |
| "Brand concentration in this ASIN's market" | Brand dominance assessment |

**Not applicable** -- Needs beyond ASIN-driven niche segment data:
- Keyword-driven niche discovery (use the keyword-based niche skill instead)
- Individual ASIN performance or sales estimation
- Search term ranking trends (use ABA data tools instead)
- Advertising campaign management or bid optimization
- Product review analysis or listing optimization

**Boundary judgment**: When users say "market research" or "product opportunity" while holding a specific ASIN, if their intent focuses on evaluating the competitive landscape and demand potential of the niche segments that ASIN competes in, this skill applies. If they need keyword-driven discovery, ASIN-level sales estimates, or comprehensive business strategy, direct them to the appropriate tool.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
