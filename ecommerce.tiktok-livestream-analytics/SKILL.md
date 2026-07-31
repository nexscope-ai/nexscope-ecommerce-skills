---
name: ecommerce.tiktok-livestream-analytics
description: Search TikTok e-commerce livestream leaderboards via Kalodata and query detailed data for specific livestreams. Supports viewing high-ranking, high-sales TikTok shopping livestreams by region, currency, language, and date range, and using livestreamId to retrieve revenue, viewers, duration, GPM, and number of products sold. Trigger when users mention TikTok livestream ranking, TikTok live ranking, TikTok top livestreams, TikTok live shopping ranking, TikTok livestream detail, TikTok live data, live viewers, kalodata livestream search, kalodata livestream ranking, TikTok livestream ranking, TikTok live ranking, TikTok top livestreams, TikTok live shopping ranking, TikTok livestream detail, kalodata livestream search/detail, live analytics. Even if the user does not explicitly mention "kalodata", trigger this skill whenever their need involves viewing TikTok livestream leaderboards or detailed data for a specific TikTok livestream.
---

# Kalodata - TikTok Livestream Search & Detail

This skill supports a two-step TikTok livestream workflow via the Kalodata data source:

1. Browse TikTok Shop livestream leaderboards to discover top-performing shoppable livestreams.
2. Fetch one livestream's full performance detail by `livestreamId`.

Use the search (rank) endpoint when the user wants rankings, hot livestreams, or livestream discovery. Use the detail endpoint when the user already has a `livestreamId` or has selected one livestream from a ranking result.

## Core Concepts

The livestream ranking endpoint returns a paginated leaderboard filtered by `region`, `dateRange`, `language`, `currency`, and optional `sortField`. The default ranking order is by `revenue` (GMV) descending. Each livestream row includes identity, timing, scale, and creator fields. Results are paginated with `pageNumber` (1-5) and `pageSize` (5-100). The response does **not** include a total count -- paginate until a page returns fewer than `pageSize` items. Money fields (`revenue`, `unit_price`) are returned as **strings** on the ranking endpoint.

The livestream detail endpoint fetches **one** shoppable TikTok livestream by `livestreamId`. It returns a **1-element array** with the single livestream's full detail (12 fields), including `viewers`, numeric `revenue`, `gpm`, and `product_number`. There is no pagination and no `total`. The `livestreamId` usually comes from the ranking response field `livestream_id`.

> **Field names/types differ between the two endpoints**: DETAIL uses `viewers` (RANK uses `views`); DETAIL `revenue` is a **number** (RANK `revenue` is a **string**); DETAIL has `gpm` and lacks `unit_price` (RANK has `unit_price` and lacks `gpm`). Do not assume field names/types carry over between the two endpoints.

Both endpoints may reflect a statistical delay (T+1). See `references/api.md` for full request and response details.

## Data Fields

**Ranking rows** (each item in `data` from `/kalodata/livestream/rank`):

| Field | Type | Description |
|-------|------|-------------|
| livestream_id | string | Livestream unique ID; pass this as `livestreamId` for detail lookup |
| livestream_title | string | Livestream title |
| creator_id | string | Creator unique ID (string to preserve precision) |
| creator_handle | string | Creator handle / username |
| livestream_start_time | integer | Start time, epoch milliseconds |
| livestream_end_time | integer | End time, epoch milliseconds |
| livestream_duration | integer | Duration in seconds |
| revenue | string | Total revenue / GMV in the requested `currency` -- **returned as a string**, e.g. `"185590.52"` |
| unit_price | string | Average unit price in the requested `currency` -- **returned as a string**, e.g. `"265.89"` |
| views | integer | Total views (note: RANK uses `views`) |
| record_type | string | Record type (e.g. `SHORT`) |

**Detail rows** (the single item in `data` from `/kalodata/livestream/detail`):

| Field | Type | Description |
|-------|------|-------------|
| livestream_id | string | Livestream unique ID (matches the requested `livestreamId`) |
| livestream_title | string | Livestream title (e.g. `24 HOUR STREAM`) |
| creator_id | string | Creator unique ID (string to preserve precision) |
| creator_handle | string | Creator handle / username (e.g. `pokepiglt`) |
| livestream_start_time | integer | Start time, epoch milliseconds |
| livestream_end_time | integer | End time, epoch milliseconds |
| livestream_duration | integer | Duration in seconds |
| record_type | string | Record type (e.g. `SHORT`) |
| viewers | integer | Total viewers (note: DETAIL uses `viewers`, NOT `views`) |
| revenue | number | Livestream revenue / GMV as a **number** in the requested `currency` (e.g. `185590.52`) -- a number here, a string on the RANK endpoint |
| gpm | number | GMV per mille (revenue per 1,000 impressions) -- DETAIL-only, absent from RANK |
| product_number | integer | Number of products sold/promoted during the livestream |

> **Money fields are strings on RANK, numbers on DETAIL.** Parse RANK `revenue`/`unit_price` (`float()`, `Number()`, or `ConvertFrom-Json`) before numeric comparison or formatting. Use the exact field name for the endpoint you are reading (`views` on RANK, `viewers` on DETAIL).

## Parameter Guide

**Livestream ranking (`/kalodata/livestream/rank`)** -- all parameters optional:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, 1-5 |
| pageSize | integer | No | Page size, 5-100 |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |
| sortField | object | No | Sorting specification; pass `{}` for the default ranking order |

**Livestream detail (`/kalodata/livestream/detail`)**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| livestreamId | string | Yes | Target livestream's unique ID (camelCase), e.g. `7661409374878878494`. Typically obtained from the ranking field `livestream_id` |
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |

## How to Call

- **API Endpoints**: `POST /kalodata/livestream/rank` (leaderboard) or `POST /kalodata/livestream/detail` (detail) (see `references/api.md` for full parameters/response/error codes)
- **Python Scripts**: `python scripts/livestream_detail.py '<JSON parameters>' [--inline]` (leaderboard) or `python scripts/livestream_detail.py '<JSON parameters>' [--inline]` (detail)
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-kalodata-tiktok-livestream-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Browse top TikTok livestreams in the US**
```json
{"region":"US","dateRange":"last7Day","pageSize":10,"pageNumber":1}
```

**2. Fetch one livestream's detail**
```json
{"livestreamId":"7661409374878878494","region":"US","dateRange":"last7Day"}
```

**3. Discovery-to-detail workflow**
```text
Run livestream_detail.py first, choose a row's livestream_id, then pass that value as livestreamId to livestream_detail.py.
```

## Display Rules

1. **Present data only**: Show the ranking in a clear table (livestream title, creator handle, revenue, views, duration, unit price, start/end times) and the detail as one grouped profile, without subjective business advice.
2. **Ranking order**: The default order is `revenue` (GMV) descending; there is no explicit `rank` field -- position is implied by order. Preserve it unless the user explicitly requests a supported `sortField`.
3. **Currency awareness**: Display the requested `currency` alongside `revenue`/`unit_price` (rank) or `revenue`/`gpm` (detail).
4. **Money as strings on RANK**: RANK `revenue` and `unit_price` are returned as **strings** (e.g. `"185590.52"`) -- parse them before numeric comparison or formatting. DETAIL `revenue` is a number. Use the exact field name when extracting with `jq` / `ConvertFrom-Json`.
5. **Viewers vs views**: Use `views` for ranking rows and `viewers` for detail rows -- do not mix them.
6. **GPM**: `gpm` is GMV per mille (detail-only) -- present with appropriate precision (e.g. `903.79`), not as a percentage.
7. **Time fields**: `livestream_start_time`/`livestream_end_time` are epoch **milliseconds**; `livestream_duration` is **seconds**. Format human-readable local times when displaying.
8. **Time window**: Always label which `dateRange` the data covers (e.g. "last 7 days").
9. **Pagination hint**: The ranking response has no total/page count; if a full page is returned, suggest the user can request the next page (up to `pageNumber` 5).
10. **Single entity**: The detail is one livestream -- do not present it as a ranking or leaderboard.

## Important Limitations

- **Ranking is not keyword search**: It browses a livestream leaderboard filtered by region/time; it does not search livestreams by keyword.
- **Detail requires `livestreamId`**: It cannot find a livestream by title alone. Obtain `livestreamId` from the ranking field `livestream_id`.
- **Max 5 pages, page size 5-100**: `pageNumber` is limited to 1-5; out of range returns `errcode 501, errmsg "page_number range is 1-5, current: <n>"`. `pageSize` must be between 5 and 100.
- **No total/page count**: Neither response includes `total` or page-count fields; paginate the ranking until a page returns fewer than `pageSize` items.
- **Field names/types differ between endpoints**: DETAIL uses `viewers` (RANK uses `views`); DETAIL `revenue` is a **number** (RANK `revenue` is a **string**); DETAIL has `gpm` and lacks `unit_price` (RANK has `unit_price` and lacks `gpm`). Do not assume field names/types carry over.
- **Data delay**: Both endpoints may have a statistical delay (T+1).
- **Transient upstream errors**: The gateway may occasionally return `errcode 501, errmsg "Kalodata API call failed: Kalodata API HTTP 554: "` (a transient upstream Kalodata error). Retry the same parameters once or twice; do not change parameters.
- **Unsupported sort/filter**: If a requested `sortField` is not accepted by the gateway, do NOT attempt workarounds -- inform the user and fall back to the default ranking order.
- **Use the matching Kalodata skills for non-livestream entities**: creator/product/video/shop rankings or details.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok livestream ranking or livestream detail lookup:

| User Says | Scenario |
|-----------|----------|
| "TikTok live leaderboard", "TikTok live ranking" | Livestream ranking lookup |
| "TikTok hot livestreams", "top TikTok livestreams" | Livestream leaderboard by region |
| "TikTok live ranking last 7 days", "US TikTok live ranking" | Time-windowed / region-filtered ranking |
| "Kalodata live leaderboard" | Direct data source reference |
| "TikTok livestream detail", "TikTok live data" | Single livestream detail lookup |
| "Viewers for this livestream", "How much did this livestream sell" | Viewers / revenue / GPM for a specific livestream |
| "TikTok livestream detail", "kalodata livestream search/detail" | Direct detail/rank fetch |

**Not applicable** -- Needs beyond TikTok livestreams:

- TikTok creator/product/video/shop rankings or details (use the corresponding Kalodata skills)
- A livestream's detail without a known `livestreamId` (first obtain the ID via the ranking endpoint)
- Amazon / Shopify / 1688 / other platforms' livestream data
- TikTok ad campaign management or content creation

**Boundary judgment**: When users say "live leaderboard" or "live ranking" in a TikTok Shop / TikTok e-commerce context, use the ranking endpoint. When they ask about a *specific* livestream's detailed metrics (revenue, viewers, duration, GPM) and a `livestreamId` is available (or can be obtained from the ranking), use the detail endpoint.
