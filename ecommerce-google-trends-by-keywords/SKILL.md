---
name: ecommerce-google-trends-by-keywords
description: "Google Trends keyword search popularity comparison and trend analysis, supporting global regions and custom time ranges. Triggered by: Google Trends, keyword popularity over time, search interest comparison, keyword trend analysis, seasonal trend detection, regional search popularity, keyword heatmap, multi-keyword comparison on Google, keyword research, market trend analysis, search trends, seasonal analysis, regional popularity."
---

# Google Trends Keyword Trend Analysis

This skill guides you on how to query and analyze Google Trends keyword search interest data, helping users understand how keyword popularity changes over time across different regions.

## Core Concepts

Google Trends provides normalized search interest data (0-100 scale) reflecting how popular a given search term is relative to its peak popularity in the selected region and time range. A value of 100 represents peak popularity, 50 means the term is half as popular as its peak, and 0 means insufficient data.

**Important language rule**: Keywords must be in the language of the target country. For example, use English keywords for the US, German keywords for Germany, Japanese keywords for Japan. If the user provides keywords in the wrong language, translate them before querying.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | The search keyword to analyze (max 100 characters). Must be in the target country's language. |
| region | string | No | Country/region code. Defaults to `US`. |
| dayRangeStart | string | No | Start date for the time range (format: YYYY-MM-DD, from 2004 onward). |
| dayRangeEnd | string | No | End date for the time range (format: YYYY-MM-DD, from 2004 onward). |

When both `dayRangeStart` and `dayRangeEnd` are provided, the custom time range takes priority.

## Supported Regions

US (United States), GB (United Kingdom), JP (Japan), CA (Canada), MX (Mexico), DE (Germany), FR (France), IT (Italy), ES (Spain), NL (Netherlands), AU (Australia), SG (Singapore), AE (United Arab Emirates), BR (Brazil), IN (India), TR (Turkey), PL (Poland), SE (Sweden)

Default region is **US**. Use US when the user doesn't specify a region.

## API Invocation

- **API Endpoint**: `POST /googleTrend/getTrendByKeys` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/google_trends_by_keywords.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same session + parameter combination is called only once by default; the script includes a 24-hour local cache. Do not automatically retry failed or empty results by changing keywords, paginating, or switching region codes. If further retrieval is needed, inform the user of the additional cost first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-google-trend-get-trend-by-keys-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouping by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body <= 8 KB: after saving to disk, print the full JSON to stdout
- Response body > 8 KB: after saving to disk, stdout prints a summary only (top-level fields, common counts like `total`/`costToken`, the length of the largest list field plus the first 3 sample items)
- Use `--inline` to force full output to stdout (also saves to disk)

**Data Reading Tips**: First check the summary to determine if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract on demand from the saved JSON file, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## How to Build Queries

### Principles for Effective Queries

1. **Use the correct language**: Always ensure keywords match the target region's language. Translate first if needed.
2. **Specify a region**: Default is US, but always confirm the user's intended market.
3. **Use date ranges for focused analysis**: For seasonal trends or specific event analysis, provide `dayRangeStart` and `dayRangeEnd`.
4. **Keep keywords concise**: Google Trends works best with short, focused search terms.

### Usage Examples

**1. Basic Keyword Trend (Default Region & Time)**
```json
{"keyword": "wireless charger"}
```
Query the overall search interest trend for "wireless charger" in the US.

**2. Keyword Trend in a Specific Region**
```json
{"keyword": "Ladekabel", "region": "DE"}
```
Query the search interest for "Ladekabel" (charging cable) in Germany.

**3. Custom Date Range Analysis**
```json
{"keyword": "christmas gifts", "region": "US", "dayRangeStart": "2024-09-01", "dayRangeEnd": "2025-01-31"}
```
Analyze the seasonal trend of "christmas gifts" in the US from September 2024 through January 2025.

**4. Year-over-Year Comparison**
```json
{"keyword": "sunscreen", "region": "AU", "dayRangeStart": "2023-01-01", "dayRangeEnd": "2025-12-31"}
```
Compare multi-year seasonality of "sunscreen" in Australia.

**5. Regional Market Research**
```json
{"keyword": "yoga mat", "region": "GB"}
```
Check the popularity trend of "yoga mat" in the United Kingdom.

**6. Emerging Trend Detection**
```json
{"keyword": "AI glasses", "region": "US", "dayRangeStart": "2024-01-01", "dayRangeEnd": "2025-12-31"}
```
Track the rise of "AI glasses" search interest over the past two years in the US.

## Display Rules

1. **Present data clearly**: Show trend data in well-formatted tables or describe the trend curve. Include key data points such as peak values, troughs, and notable changes.
2. **Explain the scale**: Remind users that Google Trends values are on a 0-100 normalized scale, where 100 = peak popularity in the selected scope.
3. **Highlight patterns**: Point out seasonal patterns, sudden spikes, or sustained growth/decline when visible in the data.
4. **Chart data availability**: When the response includes `chartOption`, mention that visualization data is available and describe the trend shape.
5. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., check keyword spelling, try a different date range, ensure the keyword is in the correct language).

## Important Limitations

- **No secondary SQL processing**: Results from this tool are unstructured and cannot be fed into dynamic query tools for secondary analysis.
- **Normalized values**: Trend values are relative (0-100), not absolute search volumes.
- **Data availability**: Data is available from 2004 onward, but very niche terms may have sparse data.
- **Single keyword per call**: Each API call handles one keyword. For multi-keyword comparisons, make separate calls and compare results.
- **Language requirement**: Keywords must match the target region's language for accurate results.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about keyword search popularity trends:

| User Says | Scenario |
|-----------|----------|
| "How popular is XX keyword on Google" | Basic trend lookup |
| "Is XX trending up or down" | Trend direction analysis |
| "When does XX peak in searches" | Seasonal peak detection |
| "Compare popularity of XX across months" | Seasonal pattern analysis |
| "Is XX gaining traction in Germany" | Regional trend check |
| "What's the search trend for XX over the past year" | Historical trend analysis |
| "Holiday search trends for XX" | Seasonal / event-driven analysis |

**Not applicable** -- Needs beyond Google Trends search interest data:

- Google Ads keyword planner or bid/CPC data
- Absolute search volume numbers (Google Trends provides relative, not absolute data)
- Social media trending topics (Twitter/X, TikTok, etc.)
- Amazon-specific search term data (use ABA Data Explorer instead)
- Website traffic analytics (Google Analytics, SimilarWeb, etc.)
- Keyword ranking on search engine result pages (SEO rank tracking)

**Boundary judgment**: When users say "keyword research" or "market trend analysis", if it specifically relates to search interest popularity over time from Google's perspective, this skill applies. If they want absolute traffic numbers, advertising metrics, or e-commerce-platform-specific data, it does not apply.
