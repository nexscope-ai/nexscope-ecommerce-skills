---
name: ecommerce.amazon-market-statistics
description: Use SellerSprite market statistics capability to output a market statistics dashboard by category node, including top listing average rating, average price, BSR, sales, seller count, and new product related metrics, suitable for quickly assessing the market quality and competitive landscape of a category. Trigger when the user mentions category market statistics, market selection dashboard, market fundamentals assessment, node market quality, top product statistics, SellerSprite market statistics, category statistics. Even if the user does not explicitly mention "SellerSprite", if the need is to view aggregated statistical results by category node, this skill should also be triggered.
---

# SellerSprite Market Statistics

This skill helps fetch node-level market statistics for Amazon categories via SellerSprite.

## Core Concepts

- **Node statistics**: Aggregated statistics for a specified category node, not returning complete product details.
- **TopN scope**: `topN` determines the sample size of top products for statistics (default 10).
- **New product definition**: `newProduct` specifies the number of recent months used to define "new product" (default 6).

## How to Invoke

- **API Endpoint**: `POST /sellersprite/market/statistics` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_market_statistics.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sellersprite-market-statistics-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Marketplace code, default `US` |
| nodeIdPath | string | Yes | Node ID path, e.g. `1064954:1069242:...` |
| month | string | No | `nearly` or `yyyyMM` |
| topN | integer | No | Top sample size, default 10 |
| newProduct | integer | No | New product definition (months), default 6 |

## Usage Example

```json
{
  "marketplace": "US",
  "nodeIdPath": "172282:281407",
  "month": "nearly",
  "topN": 10,
  "newProduct": 6
}
```

## Display Rules

1. Clearly display the statistical scope: `topN`, `newProduct`, time range.
2. Output key overview metrics first, then extended fields.
3. If the user does not provide `nodeIdPath`, guide them to provide a node path or do category location first.

## Important Limitations

- Required parameters: `marketplace`, `nodeIdPath`
- `nodeIdPath` must be a valid node path
- Month queries are limited by the third-party historical range

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://os.nexscope.com/ to top up credits.
