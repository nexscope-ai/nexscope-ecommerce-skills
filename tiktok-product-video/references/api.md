# TikTok Product Video API Reference

## Calling Convention

- **Request URL**: `{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/echotik/listProductVideo`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: Bearer <api_key>`, where api_key is read from environment variable `NEXSCOPE_API_KEY`

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productId | string | Yes | Product ID. Max length 1000 |
| userId | string | No | Influencer ID, used to filter videos by a specific creator. Max length 1000 |
| productVideoSortField | integer | No | Sort field: 1=views, 2=likes, 3=shares, 4=video sales, 5=video GMV, 6=publish date. Default `1` |
| sortType | integer | No | Sort order: 0=ascending, 1=descending. Default `1` |
| minCreateTime | integer | No | Video publish time range start (Unix timestamp in seconds) |
| maxCreateTime | integer | No | Video publish time range end (Unix timestamp in seconds) |
| pageNum | integer | No | Page number. Default `1` |
| pageSize | integer | No | Results per page (must be a multiple of 10, max 100; the upstream API has a limit of 10 per page, internally fetches multiple pages and merges). Default `50` |

## Response Structure

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total record count |
| data | array | Video list (see Video Object below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token cost |

### Video Object

| Field | Type | Description |
|-------|------|-------------|
| videoId | string | Video ID |
| productId | string | Product ID |
| userId | string | Influencer ID |
| videoDesc | string | Video description |
| officialUrl | string | TikTok official video URL |
| covet | integer | Share count |
| totalFavoritesCnt | integer | Favorites count |
| totalVideoSaleCnt | integer | Video sales (estimated) |
| totalVideoSaleGmvAmt | integer | Video GMV (estimated) |
| hashTag | string | Hashtags |
| createDate | string (date) | Video publish date |
| region | string | Region code |
| sourceTool | string | Source tool |
| sourceType | string | Product source |

## Error Codes

Under normal circumstances, the HTTP status code is always 200. Business success/failure is indicated by the `errorCode` field in the response body (errorCode = 200 means success, other values indicate business errors). For unauthorized requests, HTTP status code is 401 with corresponding errorCode of 401.

| errcode | Meaning | Suggested Action |
|---------|---------|-----------------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | Check that the `Authorization` header correctly carries the Bearer token with API Key |
| Other non-200 values | Business error | Refer to `errmsg` field for specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/echotik/listProductVideo \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "productId": "1729382310407603945",
    "productVideoSortField": 1,
    "sortType": 1,
    "pageSize": 20
  }'
```
