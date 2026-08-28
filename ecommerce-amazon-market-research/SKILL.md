---
name: ecommerce-amazon-market-research
description: "Use SellerSprite market list capability to filter Amazon niche markets by category dimensions, supporting market size, competition, top concentration, seller structure, new product share, price/rating/margin ranges, and many other criteria for discovering viable markets and evaluating product selection directions. Trigger when the user mentions Amazon market research, niche category research, market opportunity screening, market concentration analysis, new product opportunities, market selection, SellerSprite market research, category market research. Even if the user does not explicitly mention \"SellerSprite\", if the need is to screen and evaluate Amazon markets by category dimensions, this skill should also be triggered."
---

# SellerSprite Market Research

This skill helps screen and rank Amazon category markets using SellerSprite market-research data.

## Core Concepts

- **Category market-level analysis**: Not a product-level list, but market profiles aggregated by category/node.
- **Market size**: Monthly average sales volume, monthly average revenue, product count, etc.
- **Competition structure**: Seller/brand concentration, top concentration, Amazon self-operated share, FBA/FBM share.
- **Input scale**: Filter parameters **GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion** (`min*`/`max*`) must be **0~1 decimal values**, see the parameter table below and `references/api.md`.
- **New product opportunities**: New product count, new product share, new product average price/rating/sales, etc.

## How to Invoke

- **API Endpoint**: `POST /sellersprite/market/research` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_market_research.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sellersprite-market-research-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Key Parameters

> The endpoint filter options are consistent with the `_sellersprite_market_research` tool (70+); below is a commonly used subset. **For complete parameters and output fields, see `references/api.md`**.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Marketplace code, default `US` |
| month | string | No | `nearly` or `yyyyMM` |
| nodeIdPath | string | No | Category node path |
| departmentKeyword | string | No | Category keyword path |
| page / size | integer | No | Pagination, default 1/50, `size` max 200 |
| orderField / orderDesc | string/boolean | No | Sort field and direction; `orderDesc` defaults to `true` (descending) |
| minAvgRevenue / maxAvgRevenue | number | No | Monthly average revenue range |
| minAvgUnits / maxAvgUnits | integer | No | Monthly average sales range |
| minGoodsCount / maxGoodsCount | integer | No | Product count range |
| minGoodsCrn / maxGoodsCrn | number | No | Product concentration (**decimal 0~1**, e.g. `0.4` means 40%, do not use integer `40`) |
| minSellerCrn / maxSellerCrn | number | No | Seller concentration (**decimal 0~1**) |
| minBrandCrn / maxBrandCrn | number | No | Brand concentration (**decimal 0~1**) |
| minAmazonSelfProportion / maxAmazonSelfProportion | number | No | Amazon self-operated share (**decimal 0~1**) |
| minFbaProportion / maxFbaProportion | number | No | FBA share (**decimal 0~1**) |
| minFbmProportion / maxFbmProportion | number | No | FBM share (**decimal 0~1**) |
| minEbcProportion / maxEbcProportion | number | No | A+ content share (**decimal 0~1**) |
| minNewProportion / maxNewProportion | number | No | New product share (scale may differ from above; check `references/api.md` / schema) |
| minAvgPrice / maxAvgPrice | number | No | Average price range |
| minAvgRating / maxAvgRating | number | No | Average rating range |
| minAvgProfit / maxAvgProfit | number | No | Average gross margin (%) |

## Usage Example

```json
{
  "marketplace": "US",
  "month": "nearly",
  "minAvgRevenue": 10000,
  "maxGoodsCrn": 0.4,
  "minNewProportion": 10,
  "maxSellerCrn": 0.5,
  "orderField": "total_amount",
  "orderDesc": true,
  "page": 1,
  "size": 50
}
```

## Display Rules

1. First present the top N market candidates, then show core metrics (market size, concentration, new product share).
2. **Input parameter echo**: `GoodsCrn` / `BrandCrn` / `SellerCrn` / `EbcProportion` / `FbaProportion` / `FbmProportion` / `AmazonSelfProportion` filters use **0~1 decimal values**; when presenting to users, convert to percentage (e.g., passing `0.4` can be expressed as "product concentration cap of 40%"). If fields in the response `data[]` still carry "(%)" fields, their scale may differ from input scale, and the response values take precedence.
3. Other ratios, gross margins, and similar field units should reference `references/api.md`.
4. Display filter criteria echo so users can reproduce results.
5. If results are too few or too many, suggest users adjust key thresholds (e.g., concentration, scale thresholds).

## Important Limitations

- Required parameter: `marketplace`
- Maximum 200 records per page
- Historical month range is limited by the third party (typically last 24 months)

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
