---
name: tiktok-product-video
version: 1.0.0
category: product-sourcing
description: |
  Analyze TikTok promotional videos for a known productId. Triggers: product videos, influencer performance, video sales, video GMV, views/likes/shares. Use after a product is known, not for product discovery or market rankings.
---

# TikTok Product Video Analysis

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.

## Core Question

Which promotional videos and influencers are driving views, engagement, sales, or GMV for a specific TikTok Shop product?

## When to Use

- User provides a TikTok `productId` and asks for product videos, influencer performance, video sales, video GMV, views, likes, comments, shares, or publish timing.
- User wants to understand why a specific TikTok product is selling through videos.
- User wants to find top-performing creatives or creators for one TikTok Shop product.
- User wants video-level evidence after selecting a product from TikTok rankings or product search.

## Clarify or Infer Before Querying

If the user request is broad or ambiguous, identify:

- TikTok `productId`; if missing, first use product search or top-selling ranking to find one
- sort metric: views, likes, shares, video sales, video GMV, or publish date
- time range if the user asks for recent videos
- whether to filter by a specific influencer/userId
- desired number of videos

Use sensible defaults when the user's intent is clear: sort by views descending, pageSize 50, no creator filter.

## Differs From / Not Applicable

- Use `ecommerce.tiktok-product-research` when the user needs to search for TikTok products or find a `productId`.
- Use `ecommerce.tiktok-top-selling` when the user asks for market/category best-seller rankings.
- Use this skill only after a specific TikTok product is known.
- Do not use for video creation advice, ad campaign management, live-stream data, Temu/Amazon products, or general influencer profile analytics.

## Workflow

1. Confirm or obtain the TikTok `productId`.
2. Choose sort field, time range, creator filter, page, and page size.
3. Query FastMoss product video data.
4. Return a compact video table with engagement, video-attributed sales/GMV, creator ID, publish time, and links.
5. Interpret creative/influencer patterns and recommend follow-up actions.

## Output Structure

Default output should include:

- Query assumptions: productId, sort field, sort order, time range, pageSize
- Video table: description, creator/userId, publish date, views, likes, comments, shares, video sales, video GMV, duration, official URL
- Key observations: top sales-driving videos, high-engagement videos, creator concentration, recent momentum, content themes/hashtags
- Caveats: video sales and GMV are estimates; playback URLs may expire
- Suggested next step: shortlist creators, inspect top videos manually, or compare with similar products


This skill queries promotional videos associated with a TikTok Shop product, helping sellers analyze video marketing performance and identify effective influencer content strategies.

## Core Concepts

This tool retrieves the list of promotional videos linked to a specific TikTok product. Each video record includes engagement metrics (views, likes, comments, shares, favorites), estimated sales attribution (video sales count and GMV), video metadata (duration, resolution, publish date), and the creator (influencer) ID. This enables sellers to understand which videos drive the most sales for a product and what content patterns work best.

**Required input**: A `productId` is mandatory. You can obtain product IDs from other TikTok product search or ranking tools.

**Sort fields**: Videos can be sorted by views (1), likes (2), shares (3), video sales (4), video GMV (5), or publish date (6).

**Pagination**: `pageSize` must be a multiple of 10, max 100. The backend fetches in batches of 10 and merges results.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| productId | string | Yes | TikTok product ID | - |
| userId | string | No | Filter by influencer ID | - |
| productVideoSortField | integer | No | Sort field: 1=views, 2=likes, 3=shares, 4=video sales, 5=video GMV, 6=publish date | 1 |
| sortType | integer | No | Sort order: 0=ascending, 1=descending | 1 |
| minCreateTime | integer | No | Video publish start time (Unix timestamp in seconds) | - |
| maxCreateTime | integer | No | Video publish end time (Unix timestamp in seconds) | - |
| pageNum | integer | No | Page number | 1 |
| pageSize | integer | No | Results per page (multiple of 10, max 100) | 50 |

## API Usage

This tool calls the NexScope proxy API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/tiktok_product_video.py` directly to run queries.

## Usage Examples

**1. Top videos by views for a product**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 1,
  "sortType": 1,
  "pageSize": 20
}
```

**2. Find highest-converting videos (by video sales)**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 4,
  "sortType": 1,
  "pageSize": 20
}
```

**3. Videos by a specific influencer for a product**
```json
{
  "productId": "1729382310407603945",
  "userId": "7234567890123456789",
  "productVideoSortField": 1,
  "sortType": 1
}
```

**4. Recent videos in a time range (sorted by GMV)**
```json
{
  "productId": "1729382310407603945",
  "minCreateTime": 1717200000,
  "maxCreateTime": 1719792000,
  "productVideoSortField": 5,
  "sortType": 1
}
```

**5. Videos sorted by publish date (newest first)**
```json
{
  "productId": "1729382310407603945",
  "productVideoSortField": 6,
  "sortType": 1,
  "pageSize": 50
}
```

## Display Rules

1. **Present data in tables**: Show video description (truncated if long), views, likes, comments, shares, video sales, video GMV, publish date, and influencer ID
2. **Link to original**: When `officialUrl` is available, provide it so users can view the video on TikTok
3. **Estimation notice**: Video sales and GMV are estimated values, remind users these are approximations
4. **Cover image**: If `coverUrl` is present, mention it so the user knows video thumbnails are available
5. **Duration formatting**: Convert `duration` (seconds) to a readable format (e.g., "1:30" for 90 seconds)
6. **Hashtag display**: Show `hashTag` when present to help users understand content themes
7. **Playback URL caveat**: The `playAddr` field may expire quickly; prefer `officialUrl` for sharing

## User Expression & Scenario Quick Reference

### Applicable Scenarios

| User Says | Scenario |
|-----------|----------|
| "Show me the promotional videos for this TikTok product" | Query videos by product ID |
| "Which videos are driving the most sales for this product" | Sort by video sales (field 4) |
| "What influencer videos are promoting this product" | General video list query |
| "Show me videos by a specific creator for this product" | Filter by userId |
| "Recent promotional videos for this product" | Filter by time range or sort by date |
| "Which TikTok videos have the highest GMV for this product" | Sort by video GMV (field 5) |
| "Analyze the video marketing performance of this product" | Comprehensive video list query |

### Not Applicable Scenarios

- Searching for products (use product search tools instead)
- TikTok new product rankings (use new product ranking tools instead)
- Influencer profile analytics (follower count, bio, overall performance)
- TikTok live-stream data
- Video content creation or editing advice
- TikTok advertising / ad campaign management
- Non-TikTok platform video data

### Boundary Judgment

When users ask about "TikTok videos", determine whether they want videos associated with a specific product (this skill) or general TikTok video analytics (not this skill). If they mention a product ID or ask "what videos are promoting product X", this skill applies. If they ask about trending videos in general without a product context, this skill does not apply.

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/tiktok_product_video.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data -- do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** -- apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
