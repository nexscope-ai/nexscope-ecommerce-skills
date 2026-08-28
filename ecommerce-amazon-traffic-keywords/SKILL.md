---
name: ecommerce-amazon-traffic-keywords
description: "Query traffic keyword lists for an Amazon ASIN via SellerSprite, including traffic source type, conversion type, organic rank, and ad rank with historical month and multi-dimensional sorting. Trigger when user mentions ASIN reverse traffic keywords, traffic keyword list, keyword traffic structure, organic/ad keyword analysis, keyword conversion type, SellerSprite traffic keyword, Amazon traffic keywords, reverse ASIN keywords — even if \"SellerSprite\" is not explicitly mentioned, as long as the need involves viewing keyword traffic sources and keyword lists for a specific ASIN."
---

# SellerSprite Traffic Keyword

This skill helps query and analyze traffic keyword lists for an Amazon ASIN via SellerSprite.

## Core Concepts

- **ASIN Reverse Keyword Lookup**: Input an ASIN to view the keyword list that drives traffic to that product.
- **Traffic Share Types** (`trafficKeywordTypes`): Primary traffic keywords, precise traffic keywords, and `preciseLongTail` (labeled as "conversion loss keywords" in the tool UI) as defined in the schema.
- **Conversion Types** (`conversionKeywordTypes`): Conversion-strong keywords, stable keywords, loss keywords, etc.
- **Keyword Badges** (`badges`): Organic search keywords, Amazon Choice recommended keywords, etc.

## API Invocation

- **API Endpoint**: `POST /sellersprite/traffic/keyword` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_traffic_keywords.py ''<JSON params>'' [--inline]`
- **Cost**: This tool consumes credits. The same parameter combination is only called once per session by default; the script has a 24h local cache. Do not automatically retry with different keywords, pages, or zip codes on failure/empty results. If further retrieval is needed, explain the additional cost to the user first.

**Output Strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-sellersprite-traffic-keyword-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` comes from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: after writing to disk, stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tips**: Check the summary first to see if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Key Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | Marketplace site, default `US` |
| asin | string | Yes | ASIN to look up |
| month | string | No | Historical month, format `yyyyMM`; default is last 30 days |
| page | integer | No | Page number, default 1 |
| size | integer | No | Items per page, default 50, maximum 100 |
| keyword | string | No | Keyword filter |
| badges | string | No | Keyword badges, multiple values comma-separated |
| trafficKeywordTypes | string | No | Traffic share types, multiple values comma-separated |
| conversionKeywordTypes | string | No | Conversion types, multiple values comma-separated |
| orderField | string | No | Sort field, default `rankPosition` |
| orderDesc | boolean | No | Descending order, default `false` |

## Usage Examples

```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "size": 50,
  "orderField": "rankPosition",
  "orderDesc": false
}
```

```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "month": "202507",
  "trafficKeywordTypes": "primary,precise",
  "conversionKeywordTypes": "excellent,stable",
  "page": 1,
  "size": 100
}
```

## Display Rules

1. Prioritize displaying: keyword, organic rank, ad rank, traffic share type, conversion type.
2. Clearly indicate the query period (last 30 days or historical month).
3. When paginated, show total count and current page.
4. Do not output subjective business advice unrelated to the API unless explicitly requested by the user.

## Important Limitations

- Required parameters: `marketplace`, `asin`
- Maximum 100 items per page per call
- Historical queries require the `yyyyMM` format

## Credit Consumption

Consumes 15 credits.

> Users pay for credit consumption. When high-frequency calls to this skill are needed, or when the user may underestimate the credit cost, be sure to remind them and let them decide whether to continue.