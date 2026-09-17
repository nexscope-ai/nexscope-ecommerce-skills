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

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

On platform success (`code: 0`), the following business fields are inside the outer `data` object.

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

> **Download URL absence note**: Based on actual testing, some videos (subject to region, privacy, or source restrictions) will not return `noWatermarkDownloadUrl` / `downloadUrl`, and only return `playUrl` and cover. In such cases, inform the user that no direct download URL is currently available for this video, and suggest using `playUrl` for playback/preview.

Success response example (real call, long URLs truncated):

```json
{
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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter error | `msg` will indicate the missing item, e.g., `url is a required parameter`; check whether `url` is provided and non-empty |
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Unable to get video download URL | URL is not a TikTok video link, the video is inaccessible, or it has been deleted; prompt the user to check whether the link is a valid TikTok video URL |

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
