# EchoTik TikTok Video Download URL API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/getVideoDownloadUrl`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| url | string | Yes | TikTok video URL, supports two formats: `https://vt.tiktok.com/xxx` short link or `https://www.tiktok.com/@user/video/xxx` full link. Max length 1000 |

## Response Structure

On success, the HTTP status code is 200. The response body carries both the business code `errcode=200`, `errmsg="ok"`, and the following data fields at the top level.

  | Field | Type | Always Returned | Description |  
|------|------|----------|------|
| noWatermarkDownloadUrl | string | Conditional | Video download URL (no watermark). **Not all videos return this**: some videos omit this field, in which case no-watermark download is unavailable |
| downloadUrl | string | Conditional | Video download URL (with watermark). **Not all videos return this**: omitted or present together with the no-watermark URL |
| playUrl | string | Always | Video play URL. When download URLs are absent, this serves as a fallback for playback/preview |
| coverUrl | string | Always | Video cover image URL (static) |
| dynamicCoverUrl | string | Always | Video dynamic cover URL |
| videoId | string | Always | Video ID |
| columns | array | Always | Render column definitions (field metadata: field/title/cellType/filterable/sortable, for frontend table rendering) |
| type | string | Always | Render style (e.g., `tableListWorkbenches`) |
| costToken | integer | Always | Token cost |
| errcode | integer | Always | Business code, 200 indicates success |
| errmsg | string | Always | Business message, `ok` on success |

> **Download URL absence note**: Based on actual testing, some videos (subject to region, privacy, or source restrictions) will not return `noWatermarkDownloadUrl` / `downloadUrl`, and only return `playUrl` and cover. In such cases, inform the user that no direct download URL is currently available for this video, and suggest using `playUrl` for playback/preview.

Success response example (real call, long URLs truncated):

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "videoId": "7096674515245206810",
  "noWatermarkDownloadUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "downloadUrl": "https://v45.tiktokcdn-eu.com/626c5d3d5a7d...",
  "playUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "coverUrl": "https://agent-files.nexscope.com/tiktok/20260629/7096674515245206810.jpg",
  "dynamicCoverUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-useast2a-p-0037...",
  "type": "tableListWorkbenches",
  "costToken": 12000,
  "columns": [/* render column definitions */]
}
```

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errcode` field in the response body (`errcode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errcode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 400 | Parameter error | `errmsg` will indicate the missing item, e.g., `url is a required parameter`; check whether `url` is provided and non-empty |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 10000 | Unable to get video download URL | URL is not a TikTok video link, the video is inaccessible, or it has been deleted; prompt the user to check whether the link is a valid TikTok video URL |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response examples:

```json
// Missing parameter
{
    "errcode": 400,
    "errmsg": "url is a required parameter",
    "url": ""
}

// Not a valid TikTok video link
{
    "errcode": 10000,
    "errmsg": "Unable to get video download URL"
}

// Unauthorized
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/getVideoDownloadUrl \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.tiktok.com/@user/video/1234567890"
  }'
```

---
