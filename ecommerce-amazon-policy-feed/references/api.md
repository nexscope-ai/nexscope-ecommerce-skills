# Amazon Latest Policy & News API Reference

This skill encapsulates two chained APIs: **Policy/News List** (`amazon/policyFeed`) and **News Detail** (`amazon/policyFeedDetail`). Use the list API to obtain the news `id`, then use the detail API to retrieve the full body.

## API Specification

- **HTTP Method**: POST, Content-Type: application/json
- **Gateway Base URL**: Environment variable `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/policyFeed` (script uses a built-in default address if not configured)
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)
- **Business Success Determination**: HTTP status code 200; business success is determined by the `errcode` field in the response body (`errcode = 200` indicates success; other values indicate business errors, with `errmsg` providing the reason)

---

## I. Policy/News List

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}Feed`
- **Script**: `scripts/amazon_policy_feed.py`

### Request Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| site | string | No | Amazon site code (uppercase), default `US`. Site filtering only applies to certain news types; some news items are always returned regardless of site. Options: US/JP/UK/AU/BE/BR/CA/EG/FR/DE/IN/IT/MX/NL/PL/SA/SG/ES/SE/TR/AE/ZA/IE |
| publishedAtGte | string | No | Publication/change time lower bound (inclusive), format `yyyy-MM-dd HH:mm:ss`. Defaults to the last 7 days if not provided |
| publishedAtLte | string | No | Publication/change time upper bound (inclusive), format `yyyy-MM-dd HH:mm:ss`. Defaults to current time if not provided |
| page | integer | No | Page number, starting from 1, default `1` |
| pageSize | integer | No | Items per page, default `20`, range 1-100 |

### Response Structure

| Field | Type | Description |
|------|------|------|
| errcode | integer | Gateway response code (200 = success) |
| errmsg | string | Message |
| code | string | Business response code ("200" = success) |
| msg | string | Business message |
| total | integer | Number of items returned this time |
| type | string | Render style, fixed `tableListWorkbenches` |
| data | array | News list, sorted by publication/change time descending (see table below) |
| costTime | integer | Total processing time (milliseconds) |
| costToken | integer | Token consumption |
| columns | array | Frontend column definitions |

#### News Object Fields in data

| Field | Type | Description |
|------|------|------|
| id | string | Record ID (32-character string), used as input for `amazon/policyFeedDetail` |
| title | string | News title |
| summaryZh | string | Summary in Chinese, AI-generated 1-3 sentence overview |
| originalUrl | string | Link to original article |
| publishedAt | string | Publication/change time, format `yyyy-MM-dd HH:mm:ss` |

### curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}Feed \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"site": "US", "pageSize": 20}'
```

---

## II. News Detail

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}FeedDetail`
- **Script**: `scripts/amazon_policy_feed_detail.py`

### Request Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| id | string | Yes | News record ID (32-character string), from `data[].id` in the list API response |

### Response Structure

| Field | Type | Description |
|------|------|------|
| errcode | integer | Gateway response code (200 = success) |
| errmsg | string | Message / error information |
| type | string | Response type, fixed `stdoutWorkbenches` (frontend renders stdout as Markdown) |
| stdout | string | Full news body (Markdown format) |
| title | string | News title |
| summaryZh | string | Summary in Chinese (AI-generated 1-3 sentence overview) |
| costTime | integer | Total processing time (milliseconds) |
| costToken | integer | Token consumption |

### curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}FeedDetail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}'
```

---

## Error Codes

| code | Meaning | Action |
|------|------|----------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example (detail API with invalid id):

```json
{
    "errcode": 400,
    "errmsg": "News record not found."
}
```

---
