# Kalodata TikTok Video Search & Detail API Reference

## API Specification

- **Request URL (Video Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/rank`
- **Request URL (Video Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

### Video Rank: `POST /kalodata/video/rank`

POST Body (JSON), all parameters are optional:

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | No | Region/market code, e.g., `US` |
| dateRange | string | No | Time range, e.g., `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, value range 1-5 |
| pageSize | integer | No | Items per page, value range 5-100 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| currency | string | No | Currency unit, e.g., `USD` |
| category_id | string | No | Category ID filter |
| shop_id | string | No | Shop ID filter |
| creator_id | string | No | Creator ID filter |
| product_id | string | No | Product ID filter |
| revenue_range | string | No | GMV range; `revenue` in the response is GMV, e.g. `1-100`, `>1000`, `<100` |
| followers_range | string | No | Creator follower range filter |
| ads_roas | number | No | Advertising ROAS filter |
| sortField | object | No | GMV sort criteria, e.g. `{"field":"revenue","type":"DESC"}` |

> This endpoint is used to browse video rankings and does not support keyword search. The backend supports GMV filtering through `revenue_range`. Available sort fields are subject to what the gateway actually accepts; if an unsupported sort field is passed, handle according to the outer platform `msg` and do not attempt other bypass logic.

### Video Detail: `POST /kalodata/video/detail`

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| videoId | string | Yes | TikTok video ID, e.g., `7659161409279806734`, obtainable from the `video_id` in the video rank response |
| region | string | No | Region/market code, e.g., `US` |
| dateRange | string | No | Time range, e.g., `last7Day`, `last30Day` |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| currency | string | No | Currency unit, e.g., `USD` |

> `videoId` is required. This endpoint does not support searching videos by keyword/title; you must first discover videos using the video rank endpoint and obtain `video_id`, then query details with `videoId`.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

### Common Top-Level Fields

| Field | Type | Description |
|------|------|------|
| data | array | Rank or detail data |
| costToken | integer | Tokens consumed for this call, typically 14000 |

### Video Rank Fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| video_id | string | Video ID, string format to avoid large integer precision loss |
| video_title | string | Video title / caption |
| views | integer | View count |
| digg_count | integer | Like count |
| comment_count | integer | Comment count |
| share_count | integer | Share count |
| revenue | number | Total revenue / GMV, returned in the requested `currency` |
| revenue_growth_rate | number | Revenue growth rate (%), can be positive or negative |
| ad | integer | Whether ad/promotional video flag (1=yes) |
| ad_view_ratio | number | Ad view share (%) |
| ad_revenue_ratio | number | Ad revenue share (%) |
| ads_roas | number | Ad ROAS |
| belonged_creator_id | string | Belonged creator ID |
| belonged_creator_handle | string | Belonged creator username |
| creator_debut | string | Creator debut date (`YYYY-MM-DD`) |

> The actual response does not include `total`, nor does it have pagination metadata such as total page count. When paging is needed, keep requesting the next page until a page returns fewer items than `pageSize` or page 5 is reached.

### Video Detail Fields (`data` is always a 1-element array)

| Field | Type | Description |
|------|------|------|
| video_id | string | Video ID, string format to avoid large integer precision loss |
| video_title | string | Video title / caption |
| video_region | string | Video region, may be empty string |
| belonged_creator_id | string | Belonged creator ID |
| belonged_creator_handle | string | Belonged creator username |
| views | integer | View count |
| digg_count | integer | Like count |
| comment_count | integer | Comment count |
| share_count | integer | Share count |
| revenue | number | Total revenue / GMV |
| sales_volumn | integer | Sales volume, field spelled as `volumn` |
| video_gpm | number | Video GPM (GMV per thousand views) |
| ad | integer | Whether ad is running (1=with ad, 0=without ad) |
| ads_views | integer | Ad view count |
| ads_roas | number | Ad ROAS |
| ad_cpa | number | Ad CPA |
| ad_view_ratio | number | Ad view share (%) |
| ads_period | integer | Ad running period (days) |
| duration | number | Video duration (seconds) |
| product_number | integer | Associated product count in the video |

> `data` is typically a 1-element array for valid `videoId`. The detail response does not include a `total` field.

## Real Response Examples

### Video Rank

```json
{
  "data": [
    {
      "video_id": "7659161409279806734",
      "video_title": "Ashley always getting me into trouble...",
      "views": 8935253,
      "digg_count": 183512,
      "comment_count": 2668,
      "share_count": 29847,
      "revenue": 180245.0,
      "revenue_growth_rate": 0,
      "ad": 1,
      "ad_view_ratio": 6.494768530896663,
      "ad_revenue_ratio": 0,
      "ads_roas": 4.24,
      "belonged_creator_id": "7565796510165943309",
      "belonged_creator_handle": "kimkrecs"
    }
  ],
  "costToken": 14000
}
```

### Video Detail

```json
{
  "data": [
    {
      "comment_count": 2668,
      "video_region": "",
      "ads_views": 7901839,
      "ad": 1,
      "sales_volumn": 3835,
      "ad_cpa": 6.518341651222737,
      "ad_view_ratio": 6.494768530896663,
      "product_number": 1,
      "belonged_creator_id": "7565796510165943309",
      "ads_roas": 4.24,
      "share_count": 29847,
      "duration": 105.1,
      "belonged_creator_handle": "kimkrecs",
      "revenue": 180245.0,
      "video_title": "Ashley always getting me into trouble ...",
      "digg_count": 183512,
      "video_gpm": 20.17,
      "ads_period": 3,
      "views": 8935253,
      "video_id": "7659161409279806734"
    }
  ],
  "costToken": 14000
}
```

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error; follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| Insufficient credits | Follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| Upstream call failed / invalid parameters | If `msg` contains Kalodata HTTP 554, retry 1-2 times with the same parameters; if due to missing or invalid `videoId`, verify that the ID comes from the rank results |

## curl Example

### Video Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 10,
    "pageNumber": 1,
    "currency": "USD"
  }'
```

### Video Detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "videoId": "7659161409279806734",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```
