# Amazon Latest Policy & News API Reference

This skill encapsulates two chained APIs: **Policy/News List** (`amazon/policyFeed`) and **News Detail** (`amazon/policyFeedDetail`). Use the list API to obtain the news `id`, then use the detail API to retrieve the full body.

## API Specification

- **HTTP Method**: POST, Content-Type: application/json
- **Gateway Base URL**: Environment variable `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/policyFeed` (script uses a built-in default address if not configured)
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)
- **Business Success Determination**: Only the numeric outer platform `code: 0` succeeds. Read outer `msg` for failures, independently of HTTP status and nested business fields.

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

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

### Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Provider business value retained inside `data`; not the outer platform status |
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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Meaning | Action |
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
