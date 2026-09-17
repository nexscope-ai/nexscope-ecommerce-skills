# EchoTik TikTok Video List API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideo`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

POST Body (JSON):

  | Parameter | Type | Required | Default | Description |  
|------|------|------|--------|------|
| region | string | Yes | - | Region code. Options: US (United States), ID (Indonesia), TH (Thailand), PH (Philippines), MY (Malaysia), VN (Vietnam), GB (United Kingdom), MX (Mexico), SG (Singapore), SA (Saudi Arabia), BR (Brazil), ES (Spain), JP (Japan), DE (Germany), IT (Italy), FR (France) |
| userId | string | No | - | Creator ID filter. Max length 1000 |
| productId | string | No | - | Associated product ID. Max length 1000 |
| productCategoryId | string | No | - | Associated product category ID. Max length 1000 |
| minTotalViewsCnt | integer | No | - | Video view count filter (minimum) |
| maxTotalViewsCnt | integer | No | - | Video view count filter (maximum) |
| minDuration | integer | No | - | Video duration range filter (seconds) - minimum |
| maxDuration | integer | No | - | Video duration range filter (seconds) - maximum |
| minCreateTime | integer | No | - | Publish time range filter (seconds-level timestamp) - minimum |
| maxCreateTime | integer | No | - | Publish time range filter (seconds-level timestamp) - maximum |
| salesFlag | integer | No | - | Whether a promotional video: 0=non-promotional video, 1=promotional video |
| isAd | integer | No | - | Whether an ad video: 0=non-ad video, 1=ad video |
| createdByAi | string | No | - | Whether AI video, string `"true"`=AI video, `"false"`=non-AI video (regex `^(true|false)$`, not boolean) |
| videoSortField | integer | No | 3 | Sort field: 1=total_digg_cnt (likes), 2=create_time (publish time), 3=total_views_cnt (views) |
| sortType | integer | No | 1 | Sort direction: 0=ascending, 1=descending |
| pageNum | integer | No | 1 | Page number, starting from 1 |
| pageSize | integer | No | 50 | Items per page. **Must be a multiple of 10, max 100**; the third-party API limit is 10 per page, internally the gateway fetches 10 per page in multiple rounds and merges |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| data | array | Video list (see video fields below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Video Object Fields

| Field | Type | Description |
|------|------|------|
| videoId | string | Video ID |
| videoDesc | string | Video description |
| officialUrl | string | TikTok official video URL |
| coverUrl | string | Video cover URL |
| duration | integer | Video duration (seconds) |
| width | string | Video width |
| height | string | Video height |
| ratio | string | Video resolution (e.g., 540p/720p) |
| dataSize | string | Video file size |
| createDate | string | Video publish date |
| userId | string | Creator ID |
| uniqueId | string | TikTok account ID (unique_id) |
| avatar | string | Creator avatar |
| totalViewsCnt | integer | Total view count |
| totalViews1dCnt | integer | Views in last 1 day |
| totalViews7dCnt | integer | Views in last 7 days |
| totalViews30dCnt | integer | Views in last 30 days |
| totalDiggCnt | integer | Total like count |
| totalDigg1dCnt | integer | Likes in last 1 day |
| totalDigg7dCnt | integer | Likes in last 7 days |
| totalDigg30dCnt | integer | Likes in last 30 days |
| totalCommentsCnt | integer | Total comment count |
| totalSharesCnt | integer | Total share count |
| totalFavoritesCnt | integer | Total favorite count |
| totalVideoSaleCnt | integer | Video sales (units) |
| totalVideoSaleGmvAmt | integer | Video sales GMV (amount) |
| salesFlagText | string | Whether promotional video |
| isAdText | string | Whether ad video |
| createdByAiText | string | Whether AI video (Yes/No/Unknown) |
| productCategoryList | string | Product categories |
| videoProducts | string | Video associated products |
| region | string | Region code |
| sourceType | string | Product source |
| sourceTool | string | Source tool |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter validation error | Parameter value is invalid (e.g., `region` not in the supported list, `createdByAi` not `true`/`false`, `pageSize` not a multiple of 10). Refer to `msg` for the specific field and valid value set |
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

### Basic video list (sorted by views descending)

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideo \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "region": "US",
    "videoSortField": 3,
    "sortType": 1,
    "pageSize": 20,
    "pageNum": 1
  }'
```

### Filter promotional videos + view count range

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideo \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "region": "US",
    "salesFlag": 1,
    "minTotalViewsCnt": 100000,
    "videoSortField": 3,
    "sortType": 1,
    "pageSize": 20
  }'
```

### Filter by creator + sort by likes descending

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideo \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "region": "US",
    "userId": "7234567890123456789",
    "videoSortField": 1,
    "sortType": 1
  }'
```

---
