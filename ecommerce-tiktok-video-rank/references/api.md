## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# EchoTik-TikTok Video Ranking API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: Bearer <api_key>`, Read api_key from the `NEXSCOPE_API_KEY` environment variable, falling back to `NEXSCOPE_API_KEY` (if unset, follow **## Resolve authentication and credit issues** in SKILL.md)
- **User-Agent**：`Nexscope-Skill/2.0`
- **Timeout**: 150s

## Request parameters

POST body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| date | string | Yes | - | Ranking query date in `YYYY-MM-DD` format |
| rankType | integer | Yes | - | Ranking period: `1` = daily, `2` = weekly, `3` = monthly |
| region | string | Yes | - | Region code. Options: US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France) |
| videoRankField | integer | Yes | - | Video ranking metric: `1` = views, `2` = video sales |
| productCategoryId | string | No | - | First-level product category ID for filtering products in shoppable video rankings |
| createdByAi | string | No | - | Whether the video is AI-generated; accepts the strings `true` / `false` |
| pageNum | integer | No | 1 | Page number, starting at 1 |
| pageSize | integer | No | 50 | Records per page. **Must be a multiple of 10, maximum 100**; the official API caps each page at 10, so the service fetches multiple pages of 10 and merges them |

### rankType enum

| Value | Meaning |
|----|------|
| 1 | Daily ranking (day) |
| 2 | Weekly ranking (week) |
| 3 | Monthly ranking (month) |

### videoRankField enum

| Value | Meaning | Observed result |
|----|------|------|
| 1 | Rank by views (`totalViewsCnt`) | ✓ 200, returns videos with high view counts |
| 2 | Rank by video sales (`totalVideoSaleCnt`) | ✓ 200, returns videos with high sales |

> **Sparse metrics**: When sorting by a `videoRankField`, counts for other metrics may be 0 (views/likes/comments may be 0 when ranking by sales; sales/GMV may be 0 when ranking by views).

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| data | array | Video list, sorted by `videoRankField`; see video fields below |
| columns | array | Rendering columns (frontend rendering metadata; may contain more items than `data`; use `data` for records) |
| type | string | Rendering style |
| costToken | integer | Tokens consumed |

### Video object fields

> The following 25 fields are returned in `data[*]` and correspond to the `columns` definitions. Although metric names start with `total`, they represent cumulative values **within the selected ranking period** (`columns` titles begin with "周期…", meaning "period...").

| Field | Type | Description |
|------|------|------|
| videoId | string | Video ID |
| officialUrl | string | Official TikTok video URL |
| userId | string | Creator ID |
| uniqueId | string | TikTok account ID |
| nickName | string | Creator nickname |
| avatar | string | Creator avatar |
| category | string | Creator category |
| videoDesc | string | Video description |
| createDate | string | Video publication date |
| coverUrl | string | Video cover URL |
| region | string | Region code |
| duration | integer | Video duration (seconds) |
| createdByAiText | string | Whether the video is AI-generated (`是` / `否`, meaning yes / no) |
| salesFlagText | string | Whether the video is shoppable (`是` / `否`, meaning yes / no) |
| productCategoryList | string | Categories of promoted products |
| videoProducts | string | Products promoted in the video |
| totalCommentsCnt | integer | Comments during the period |
| totalDiggCnt | integer | Likes during the period |
| totalFavoritesCnt | integer | Favorites during the period |
| totalSharesCnt | integer | Shares during the period |
| totalViewsCnt | integer | Views during the period |
| totalVideoSaleCnt | integer | Video sales during the period (estimated) |
| totalVideoSaleGmvAmt | number | Video sales GMV during the period (estimated) |
| sourceTool | string | Source tool |
| sourceType | string | Product source |

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter validation error | Missing required parameters (`date`, `rankType`, `region`, and `videoRankField`) or invalid values. See `msg` for the specific field and allowed values |
| Authentication failed | HTTP 401 or `authorized error`: follow **## Resolve authentication and credit issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolve authentication and credit issues** in SKILL.md. |

## curl examples

### US video view ranking for a specified date

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "date": "2026-08-10",
    "rankType": 1,
    "region": "US",
    "videoRankField": 1,
    "pageNum": 1,
    "pageSize": 20
  }'
```

### UK video ranking

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "date": "2026-08-10",
    "rankType": 2,
    "region": "GB",
    "videoRankField": 1
  }'
```

### US monthly AI shoppable video sales ranking

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "date": "2026-08-01",
    "rankType": 3,
    "region": "US",
    "videoRankField": 2,
    "createdByAi": "true",
    "productCategoryId": "601450",
    "pageNum": 1,
    "pageSize": 10
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-echotik-list-video-rank",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`nexscope-echotik-list-video-rank`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
