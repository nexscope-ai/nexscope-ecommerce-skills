---
name: ecommerce.tiktok-video-analytics
description: Search TikTok e-commerce trending promotional video leaderboards via Kalodata and query detailed data for specific videos. Supports viewing high-ranking/high-view/hot-selling promotional videos by region, currency, language, and date range, and using videoId to retrieve views, likes, comments, shares, revenue, GPM, and advertising metrics. Trigger when users mention TikTok video search, TikTok video ranking, TikTok viral video chart, TikTok video detail, video analytics, kalodata video search/detail. Even if the user does not explicitly mention "kalodata", trigger this skill whenever their need involves viewing TikTok trending promotional video leaderboards or detailed sales and engagement data for a specific TikTok video.
---

# Kalodata - TikTok Video Search & Detail

This skill supports a two-step TikTok video workflow via the Kalodata data source:

1. Browse TikTok Shop video leaderboards to discover high-performing shoppable videos.
2. Fetch one video's full performance detail by `videoId`.

Use the search endpoint when the user wants rankings, hot videos, viral videos, or video discovery. Use the detail endpoint when the user already has a `videoId` or has selected one video from a ranking result.

## Core Concepts

The video ranking endpoint returns a paginated leaderboard filtered by `region`, `dateRange`, `language`, `currency`, and optional `sortField`. Each video row includes identity, engagement, revenue, ad-performance, and creator fields. Results are paginated with `pageNumber` (1-5) and `pageSize` (5-100).

The video detail endpoint fetches **one** shoppable TikTok video by `videoId`. It returns the video's engagement metrics, monetization metrics, advertising metrics, creator identity, region, duration, and linked product count. The `videoId` usually comes from the ranking response field `video_id`.

Both endpoints may reflect a statistical delay (T+1). See `references/api.md` for full request and response details.

## Data Fields

**Ranking rows** include:

| Field | Description |
|-------|-------------|
| video_id | Video unique ID; pass this as `videoId` for detail lookup |
| video_title | Video title / caption |
| views | Video view count |
| digg_count / comment_count / share_count | Likes, comments, and shares |
| revenue | Total GMV in the requested currency |
| revenue_growth_rate | Revenue growth rate (%) |
| ad / ad_view_ratio / ad_revenue_ratio / ads_roas | Ad and advertising performance fields |
| belonged_creator_id / belonged_creator_handle | Creator identity |
| creator_debut | Creator debut date |

**Detail rows** additionally include:

| Field | Description |
|-------|-------------|
| video_region | Video region; may be empty |
| sales_volumn | Sales volume; field is spelled `volumn` |
| video_gpm | GMV per mille (revenue per 1000 views) |
| ads_views / ad_cpa / ads_period | Ad views, CPA, and ad running period |
| duration | Video duration in seconds |
| product_number | Number of products linked in the video |

## Parameter Guide

**Video ranking (`/kalodata/video/rank`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, 1-5 |
| pageSize | integer | No | Page size, 5-100 |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |
| sortField | object | No | Sorting specification; omit for default ranking |

**Video detail (`/kalodata/video/detail`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| videoId | string | Yes | TikTok video ID from ranking field `video_id` or a TikTok video URL |
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |

## How to Call

- **API Endpoints**: `POST /kalodata/video/rank` or `POST /kalodata/video/detail` (see `references/api.md` for full parameters/response/error codes)
- **Python Scripts**: `python scripts/video_detail.py '<JSON parameters>' [--inline]` or `python scripts/video_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-kalodata-tiktok-video-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## Usage Examples

**1. Browse top TikTok videos in the US**
```json
{"region":"US","dateRange":"last7Day","pageSize":10,"pageNumber":1,"currency":"USD"}
```

**2. Fetch one video's detail**
```json
{"videoId":"7659161409279806734","region":"US","dateRange":"last7Day","currency":"USD"}
```

**3. Discovery-to-detail workflow**
```text
Run video_detail.py first, choose a row's video_id, then pass that value as videoId to video_detail.py.
```

## Display Rules

1. Present ranking results in a table with title, video ID, views, engagement, revenue, ad indicators, and creator handle.
2. Present detail results as one grouped profile: identity, engagement, monetization, ads, creator, duration, and linked products.
3. Always label `dateRange`, `region`, and `currency` when showing metrics.
4. Use the exact field name `sales_volumn`.
5. `video_gpm` is GMV per mille; do not display it as a percentage.
6. Preserve ranking order unless the user explicitly requests a supported `sortField`.

## Important Limitations

- Ranking is not keyword search; it browses leaderboards by region and time window.
- Detail requires `videoId`; it cannot find a video by title alone.
- The ranking response does not include total/page count; result count is `data.length`.
- `pageNumber` is limited to 1-5 and `pageSize` is limited to 5-100.
- Transient upstream errors may appear as `errcode 501` with a Kalodata HTTP 554 message. Retry the same parameters once or twice; do not change parameters automatically.
- Use the matching Kalodata product/creator/shop/livestream skills for non-video entities.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok video ranking or video detail lookup:

| User Says | Scenario |
|-----------|----------|
| "TikTok video ranking", "TikTok video leaderboard" | Video ranking lookup |
| "TikTok trending videos", "TikTok viral videos" | Top or viral video ranking |
| "TikTok promotional video ranking", "top TikTok videos" | Region-specific shoppable video leaderboard |
| "TikTok video detail", "TikTok promotional video data" | Single video detail lookup |
| "Video views", "video engagement data", "video GPM" | Video engagement or monetization metrics |
| "kalodata video search/detail" | Direct data source reference |

**Not applicable** -- Needs beyond TikTok videos:

- TikTok product / creator / shop / livestream rankings or details
- Keyword-based video or product search
- TikTok advertising / ad campaign management
- Video editing, video download, or content creation
