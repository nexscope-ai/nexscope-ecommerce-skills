---
name: ecommerce.google-trends-by-time
description: Query and analyze Google Trends real-time hot topics and trending searches for a specified time range and country/region. Triggered by: Google Trends, hot topics, real-time trending, popular trends, current hot searches, recent trending, viral topics, trending searches, trend discovery, market trends, what's popular, trending now, breakout topics.
---

# Google Trends Time-Range Analysis

This skill guides you on how to query and analyze Google Trends data for trending topics within a configurable time window, helping users discover real-time popular searches and emerging trends across 18 supported regions.

## Core Concepts

Google Trends reflects real user search interest on Google. This tool retrieves **trending topics** (recently popular queries) for a chosen country/region over a specified number of recent days. It is ideal for spotting what is currently gaining traction in a market.

**Key data points per trending query**:
- **query** -- the trending search term
- **searchVolume** -- relative search volume value
- **increasePercentage** -- percentage change in search interest (-100 to 100, unit: %)
- **startTime / endTime** -- timestamps bounding the trend observation window

A positive `increasePercentage` means rising interest; a negative value means declining interest. A value near 100 signals an explosive spike.

## Parameter Guide

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | integer | No | 7 | Time range in days. Common values: 1 (last 24 hours), 2, 7 (past week) |
| region | string | No | US | Country/region code. See Supported Regions below |

### Supported Regions

US (United States), GB (United Kingdom), JP (Japan), CA (Canada), MX (Mexico), DE (Germany), FR (France), IT (Italy), ES (Spain), NL (Netherlands), AU (Australia), SG (Singapore), AE (United Arab Emirates), BR (Brazil), IN (India), TR (Turkey), PL (Poland), SE (Sweden)

Default region is **US**. Use US when the user does not specify a region.

## API Invocation

- **API Endpoint**: `POST /googleTrend/getTrendByTime` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/google_trends_by_time.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same session + parameter combination is called only once by default; the script includes a 24-hour local cache. Do not automatically retry failed or empty results by changing keywords, paginating, or switching region codes. If further retrieval is needed, inform the user of the additional cost first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-google-trend-get-trend-by-time-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouping by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body <= 8 KB: after saving to disk, print the full JSON to stdout
- Response body > 8 KB: after saving to disk, stdout prints a summary only (top-level fields, common counts like `total`/`costToken`, the length of the largest list field plus the first 3 sample items)
- Use `--inline` to force full output to stdout (also saves to disk)

**Data Reading Tips**: First check the summary to determine if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract on demand from the saved JSON file, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## Usage Examples

**1. What's trending in the US over the past week?**
```json
{"days": 7, "region": "US"}
```

**2. Hot topics in Japan in the last 24 hours**
```json
{"days": 1, "region": "JP"}
```

**3. Trending searches in Germany over the past 2 days**
```json
{"days": 2, "region": "DE"}
```

**4. Recent buzz in Brazil this week**
```json
{"days": 7, "region": "BR"}
```

**5. What's gaining popularity in the UK right now?**
```json
{"days": 1, "region": "GB"}
```

## Display Rules

1. **Present data clearly**: Show trending queries in a well-formatted table with columns for query, search volume, and increase percentage. Sort by search volume or increase percentage as appropriate.
2. **Highlight spikes**: When `increasePercentage` is notably high (e.g., above 50%), call attention to these breakout topics.
3. **Time context**: Always state the time range and region in your summary so the user knows exactly what window the data covers.
4. **Chart data**: If the response includes `chartOption`, describe the chart structure (title, axes, data points) so the user understands the visual trend.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters (e.g., try a different region code or time range).

## Important Limitations

- **Unstructured data**: Results from this tool are unstructured and cannot be fed into secondary SQL-based query tools for further processing.
- **Relative volumes**: Search volume values are relative, not absolute counts.
- **Short time windows**: The `days` parameter controls recency; this tool is designed for recent/real-time trends, not long historical analysis.
- **Region coverage**: Only the 18 listed regions are supported. Unsupported region codes will produce errors.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about trending/popular topics on Google:

| User Says | Scenario |
|-----------|----------|
| "What's trending right now" | Real-time trending topics |
| "Hot searches in [country]" | Regional trend discovery |
| "What topics are popular this week" | Weekly popularity overview |
| "Any viral topics in [market]" | Breakout / spike detection |
| "Show me Google Trends for [region]" | Region-specific trend query |
| "What's buzzing in the last 24 hours" | Short-window trend scan |
| "Trending searches in [country] recently" | Recent trend analysis |
| "What are people searching for in [region]" | General search interest exploration |

**Not applicable** -- Needs beyond trending topic discovery:

- Historical keyword search volume over months/years (use a dedicated Google Trends historical tool)
- Amazon-specific keyword or ASIN analysis (use ABA tools)
- Advertising / PPC campaign management
- Social media trend analysis (Twitter/X, TikTok, etc.)
- SEO ranking or backlink analysis
- Competitor website traffic estimation

**Boundary judgment**: When users say "market trends" or "what's popular", if it boils down to discovering what people are currently searching for on Google in a specific region, this skill applies. If they are asking about stock market trends, social media virality, or long-term historical search patterns, it does not apply.
