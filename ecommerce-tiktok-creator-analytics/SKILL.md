---
name: ecommerce-tiktok-creator-analytics
description: "Search TikTok e-commerce creator leaderboards via Kalodata and query detailed profiles for specific creators. Supports viewing top-performing influencer-sellers by region, currency, language, and date range, and using creatorId to retrieve follower count, video/live revenue and GPM, contact information, and associated shops. Trigger when users mention TikTok creator search, TikTok creator ranking, TikTok influencer leaderboard, TikTok creator detail, TikTok creator profile, creator homepage data, creator contact info, TikTok creator search, TikTok creator ranking, TikTok influencer leaderboard, TikTok creator detail, creator analytics, kalodata creator search/detail. Even if the user does not explicitly mention \"kalodata\", trigger this skill whenever their need involves viewing TikTok creator leaderboards or detailed sales performance data for a specific TikTok creator."
---

# Kalodata - TikTok Creator Search & Detail

This skill supports a two-step TikTok creator workflow via the Kalodata data source:

1. Browse creator leaderboards to discover high-performing TikTok Shop creators.
2. Fetch one creator's full profile and performance detail by `creatorId`.

Use the search endpoint when the user wants rankings, influencer discovery, or creator comparison. Use the detail endpoint when the user already has a `creatorId` or has selected one creator from a ranking result.

## Core Concepts

The creator ranking endpoint returns a paginated leaderboard filtered by `region`, `dateRange`, `language`, and `currency`. The default ranking order is by `revenue` (GMV) descending. Each creator row includes identity, audience, content views, sales volume, video/live revenue, and revenue growth rate.

The creator detail endpoint fetches **one** creator by `creatorId`. It returns the creator's identity, audience, revenue split, video/live metrics, product/shop counts, and contact channels. The `creatorId` usually comes from the ranking response field `creator_id`.

Both endpoints may reflect a statistical delay (T+1). See `references/api.md` for full request and response details.

## Data Fields

**Ranking rows** include:

| Field | Description |
|-------|-------------|
| creator_nickname | Creator display name |
| creator_handle | TikTok handle |
| creator_id | Creator unique ID; pass this as `creatorId` for detail lookup |
| creator_followers | Follower count, returned as a string |
| content_views | Total content views, returned as a string |
| sales_volumn | Sales volume; field is spelled `volumn` |
| revenue | Total GMV in the requested currency |
| video_revenue | Revenue from videos |
| live_revenue | Revenue from livestreams |
| revenue_growth_rate | Revenue growth rate (%) |

**Detail rows** additionally include:

| Field | Description |
|-------|-------------|
| creator_region / creator_status / creator_bio | Creator profile metadata |
| new_followers | New followers in the requested date window |
| unit_price | Average unit price in the requested currency |
| video_number / video_views / video_gpm | Video count, views, and GPM |
| live_number / live_views / live_gpm | Livestream count, views, and GPM |
| product_number / shop_number | Associated product and shop counts |
| creator_contact_* | Email and social contact fields; often empty |

## Parameter Guide

**Creator ranking (`/kalodata/creator/rank`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, 1-5 |
| pageSize | integer | No | Page size, 5-100 |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |
| sortField | object | No | Sorting specification; pass `{}` for default revenue ranking |

**Creator detail (`/kalodata/creator/detail`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| creatorId | string | Yes | Creator unique ID from ranking field `creator_id` |
| region | string | No | Market region code, e.g. `US` |
| dateRange | string | No | Time window, e.g. `last7Day`, `last30Day` |
| language | string | No | Response language, e.g. `zh-CN`, `en-US` |
| currency | string | No | Currency for monetary metrics, e.g. `USD` |

## How to Call

- **API Endpoints**: `POST /kalodata/creator/rank` or `POST /kalodata/creator/detail` (see `references/api.md` for full parameters/response/error codes)
- **Python Scripts**: `python scripts/creator_detail.py '<JSON parameters>' [--inline]` or `python scripts/creator_detail.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-kalodata-tiktok-creator-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Browse top TikTok creators in the US**
```json
{"region":"US","dateRange":"last7Day","pageSize":10,"pageNumber":1,"currency":"USD"}
```

**2. Fetch one creator's detail**
```json
{"creatorId":"7153432386608251946","region":"US","dateRange":"last7Day","currency":"USD"}
```

**3. Discovery-to-detail workflow**
```text
Run creator_detail.py first, choose a row's creator_id, then pass that value as creatorId to creator_detail.py.
```

## Display Rules

1. Present ranking results in a table with nickname, handle, followers, content views, sales volume, revenue, video/live revenue, and growth rate.
2. Present detail results as one grouped profile: identity, audience, revenue, video, live, products/shops, and contact.
3. Always label `dateRange`, `region`, and `currency` when showing metrics.
4. Treat `creator_followers` and `content_views` as string-typed counts; parse before numeric comparison.
5. Use the exact field name `sales_volumn`.
6. Show contact fields only when populated; otherwise say no contact was provided.
7. Preserve ranking order unless the user explicitly requests a supported `sortField`.

## Important Limitations

- Ranking is not keyword search; it browses leaderboards by region and time window.
- Detail requires `creatorId`; it cannot find a creator by nickname or handle alone.
- The ranking response does not include total/page count; paginate until a page returns fewer than `pageSize` items.
- `pageNumber` is limited to 1-5 and `pageSize` is limited to 5-100.
- Transient upstream errors may appear as `errcode 501` with a Kalodata HTTP 554 message. Retry the same parameters once or twice; do not change parameters automatically.
- Use the matching Kalodata product/video/shop/livestream skills for non-creator entities.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok creator ranking or creator profile lookup:

| User Says | Scenario |
|-----------|----------|
| "TikTok creator leaderboard", "top TikTok creators" | Creator ranking lookup |
| "TikTok influencer-seller leaderboard", "top TikTok creators" | Creator leaderboard by region |
| "TikTok creator leaderboard last 7 days" | Time-windowed ranking |
| "TikTok creator detail", "creator homepage data" | Creator detail lookup |
| "Creator contact info", "creator contact" | Contact channels |
| "kalodata creator search/detail" | Direct data source reference |

**Not applicable** -- Needs beyond TikTok creators:

- TikTok product/video/shop/livestream rankings or details
- Amazon / Shopify / 1688 / other platforms' creator or product data
- TikTok ad campaign management or content creation
