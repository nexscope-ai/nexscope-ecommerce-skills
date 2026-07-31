# Kalodata TikTok Video Search & Detail API Reference

## API Specification

- **Request URL (Video Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail`
- **Request URL (Video Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `NexScope-Skill/2.0`
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
| sortField | object | No | Sort criteria; omitted to use default rank order |

> This endpoint is used to browse video rankings and does not support keyword search. Available sort fields are subject to what the gateway actually accepts; if an unsupported sort field is passed, handle according to the server `errmsg` and do not attempt other bypass logic.

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

## Response Structure

### Common Top-Level Fields

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code, 200 indicates success |
| data | array | Rank or detail data |
| costToken | integer | Tokens consumed for this call, typically 14000 |
| errmsg | string | Status message, `ok` on success |

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
  "errcode": 200,
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
  "costToken": 14000,
  "errmsg": "ok"
}
```

### Video Detail

```json
{
  "errcode": 200,
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
  "costToken": 14000,
  "errmsg": "ok"
}
```

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by the `errcode` field in the response body. Unauthorized cases may return HTTP 401, with the corresponding `errcode` also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error; follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 402 | Insufficient credits | Follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| 501 | Upstream call failed / invalid parameters | If `errmsg` contains Kalodata HTTP 554, retry 1-2 times with the same parameters; if due to missing or invalid `videoId`, verify that the ID comes from the rank results |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

## curl Example

### Video Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/video/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
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
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "videoId": "7659161409279806734",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```
