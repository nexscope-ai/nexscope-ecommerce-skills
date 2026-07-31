---
name: ecommerce.tiktok-video-search
description: Search and analyze TikTok video data, filter videos by region, creator, product, category, views, duration, publish time, selling/ad/AI video flags, and return views, likes, comments, shares, favorites, video sales and GMV metrics across 16 TikTok Shop sites. Trigger when users mention TikTok video search, TikTok video list, TikTok promotional videos, TikTok video data, TikTok video views, TikTok video sales, TikTok video analytics, EchoTik video, TikTok video search, TikTok video list, TikTok video analytics, TikTok promotional videos, TikTok video views, TikTok video engagement. Even if the user does not explicitly mention "EchoTik" or "TikTok", trigger this skill whenever their need involves searching or analyzing TikTok video performance metrics by criteria.
---

# EchoTik TikTok Video Search

This skill searches and analyzes TikTok video data, helping cross-border sellers and marketers discover top-performing videos, benchmark content strategies, and evaluate video-level engagement and sales attribution across TikTok marketplaces.

## Core Concepts

EchoTik is a TikTok Shop analytics platform. This tool lists TikTok videos with rich filtering -- by region, creator, product, category, views, duration, publish time, and ad/AI/selling flags -- and returns engagement metrics (views, likes, comments, shares, favorites), estimated sales attribution (video sales count and GMV), and video metadata (duration, resolution, cover, publish date).

**Required input**: `region` is mandatory. Optional filters narrow by creator (`userId`), product (`productId`), category (`productCategoryId`), views range, duration range, publish-time range, and video type (ad / AI / selling).

**Sort fields**: videos can be sorted by likes (1), publish time (2), or views (3, default).

**Pagination**: `pageSize` must be a multiple of 10, max 100. The backend fetches in batches of 10 and merges results.

**Related skill**: This tool lists videos by region/filters (no product required). To get videos associated with one specific product, use the product video skill with a `productId` instead.

## Data Fields

| Field | Description |
|-------|-------------|
| videoId | Video ID |
| videoDesc | Video description / caption |
| officialUrl | TikTok official video URL |
| coverUrl | Video cover image URL |
| duration | Video duration (seconds) |
| width / height | Video dimensions in pixels (e.g. 576x1090) |
| ratio | Video resolution label (e.g. 540p/720p) |
| dataSize | Video file size |
| createDate | Publish date |
| userId / uniqueId / avatar | Creator ID / TikTok unique_id / creator avatar |
| totalViewsCnt | Total views (1d/7d/30d breakdown: totalViews1dCnt / 7dCnt / 30dCnt) |
| totalDiggCnt | Total likes (1d/7d/30d breakdown: totalDigg1dCnt / 7dCnt / 30dCnt) |
| totalCommentsCnt | Total comments |
| totalSharesCnt | Total shares |
| totalFavoritesCnt | Total favorites |
| totalVideoSaleCnt | Video sales (units) |
| totalVideoSaleGmvAmt | Video sales GMV (amount) |
| salesFlagText | Selling-video flag (Yes/No) |
| isAdText | Ad-video flag (Yes/No) |
| createdByAiText | AI-video flag (Yes/No/Unknown) |
| productCategoryList | Product categories |
| videoProducts | Related products |
| region | Marketplace code |
| sourceType / sourceTool | Source type / source tool |

## Parameter Guide

### Required & Region

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| region | string | Yes | - | Marketplace code. See supported list below |

### Creator / Product / Category

| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string | Filter by creator (influencer) ID |
| productId | string | Filter by related product ID |
| productCategoryId | string | Filter by related product category ID |

### Engagement / Duration / Time

| Parameter | Type | Description |
|-----------|------|-------------|
| minTotalViewsCnt / maxTotalViewsCnt | integer | Total-views range (min / max) |
| minDuration / maxDuration | integer | Duration range in seconds (min / max) |
| minCreateTime / maxCreateTime | integer | Publish-time range, Unix timestamp in seconds (min / max) |

### Video Type Flags

| Parameter | Type | Description |
|-----------|------|-------------|
| salesFlag | integer | Selling video: 0=non-selling, 1=selling (with cart) |
| isAd | integer | Ad video: 0=non-ad, 1=ad (paid promotion) |
| createdByAi | string | AI video: `"true"`=AI, `"false"`=non-AI (string, not boolean) |

### Sorting & Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| videoSortField | integer | 3 | Sort field: 1=likes (total_digg_cnt), 2=publish time (create_time), 3=views (total_views_cnt) |
| sortType | integer | 1 | Sort order: 0=ascending, 1=descending |
| pageNum | integer | 1 | Page number (starts at 1) |
| pageSize | integer | 50 | Page size -- must be a multiple of 10, max 100 |

### Supported Marketplaces

US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France)

When the user doesn't specify a marketplace, ask or default to **US**.

## How to Call

- **API Endpoint**: `POST /echotik/listVideo` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/tiktok_video_search.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-echotik-list-video-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## Usage Examples

**1. Top US videos by views**
```json
{
  "region": "US",
  "videoSortField": 3,
  "sortType": 1,
  "pageSize": 20,
  "pageNum": 1
}
```

**2. Highest-converting selling videos (by video sales)**
```json
{
  "region": "US",
  "salesFlag": 1,
  "videoSortField": 3,
  "sortType": 1,
  "pageSize": 20
}
```

**3. Videos by a specific creator**
```json
{
  "region": "US",
  "userId": "7234567890123456789",
  "videoSortField": 1,
  "sortType": 1
}
```

**4. High-view videos in a time range (sorted by likes)**
```json
{
  "region": "GB",
  "minTotalViewsCnt": 100000,
  "minCreateTime": 1717200000,
  "maxCreateTime": 1719792000,
  "videoSortField": 1,
  "sortType": 1
}
```

**5. Recent AI videos sorted by publish date**
```json
{
  "region": "US",
  "createdByAi": "true",
  "videoSortField": 2,
  "sortType": 1,
  "pageSize": 50
}
```

## Display Rules

1. **Present data in tables**: Show video description (truncated if long), views, likes, comments, shares, video sales, video GMV, publish date, and creator ID
2. **Link to original**: When `officialUrl` is available, provide it so users can view the video on TikTok
3. **Cover image**: If `coverUrl` is present, mention it so the user knows video thumbnails are available
4. **Duration formatting**: Convert `duration` (seconds) to a readable format (e.g., "1:30" for 90 seconds)
5. **Estimation notice**: Video sales and GMV are estimated values, remind users these are approximations
6. **Multi-period metrics**: When relevant, mention 1d/7d/30d views/likes breakdowns are available in the saved JSON
7. **Result count**: Always inform the user of `total` records and the current page; suggest pagination or tighter filters when the result set is large

## Important Limitations

1. **Region required**: `region` is mandatory; no default is applied by the API.
2. **pageSize rule**: Must be a multiple of 10 (max 100). Other values may be rejected or adjusted.
3. **createdByAi is a string**: Pass `"true"` / `"false"` (not boolean) -- the value is validated against `^(true|false)$`.
4. **Timestamps**: `minCreateTime` / `maxCreateTime` are Unix timestamps in seconds.
5. **Category/product IDs**: `productId` / `productCategoryId` / `userId` are internal IDs -- obtain them from prior results.
6. **No secondary processing**: Results are live queries, not stored in a database; secondary SQL/data processing is not available.
7. **Product-specific videos**: To list videos for one specific product (by `productId`), prefer the product video skill; here `productId` is only a filter within a region-scoped video listing.

## User Expression & Scenario Quick Reference

**Applicable** -- TikTok video discovery and performance analysis:

| User Says | Scenario |
|-----------|----------|
| "TikTok trending videos" / "TikTok top videos" | List videos sorted by views (field 3) |
| "TikTok promotional video ranking" | Filter salesFlag=1, sort by views/sales |
| "A creator's TikTok videos" | Filter by userId |
| "TikTok paid promotion videos" / "TikTok ad videos" | Filter isAd=1 |
| "TikTok AI videos" | Filter createdByAi="true" |
| "Recent high-view TikTok videos" | Views range + time range |
| "Which TikTok video has the highest GMV" | Sort by views, inspect GMV column |

**Not applicable** -- Needs beyond region-scoped video listing:

- Videos for one specific product by `productId` (use the product video skill)
- TikTok product search or rankings (use product search/rank skills)
- TikTok creator/influencer profile analytics (followers, bio)
- TikTok live-stream data
- Video download URL resolution (use the video download URL skill)
- Non-TikTok platform video data

**Boundary judgment**: When users ask about "TikTok videos", determine whether they want a region-scoped video listing with filters (this skill) or videos tied to one known product (the product video skill). If they mention a region or filters like "trending/promotional/paid videos" without a specific product, this skill applies.
