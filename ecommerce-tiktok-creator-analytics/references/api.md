# Kalodata TikTok Creator Search & Detail API Reference

## API Specification

- **Request URL (Creator Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/creator/rank`
- **Request URL (Creator Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/creator/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

### Creator Rank: `POST /kalodata/creator/rank`

POST Body (JSON), all parameters are optional:

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | No | Region/market code, e.g., `US` |
| dateRange | string | No | Time range, e.g., `last7Day`, `last30Day` |
| pageNumber | integer | No | Page number, value range 1-5 |
| pageSize | integer | No | Items per page, value range 5-100 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| currency | string | No | Currency unit, e.g., `USD` |
| category_ids | array<integer> | No | Category ID list filter |
| shop_id | string | No | Shop ID filter |
| revenue_range | string | No | Revenue / GMV range filter |
| creator_type | string | No | Creator type filter |
| followers_range | string | No | Follower range filter |
| engagement_rate | string | No | Engagement-rate filter |
| sortField | object | No | Sort criteria; pass an empty object `{}` for default rank order when not sorting |

> Default sort is by `revenue` (GMV) descending. Available sort fields are subject to what the gateway actually accepts; if an unsupported sort field is passed, fall back to default sort and do not attempt other bypass logic.

### Creator Detail: `POST /kalodata/creator/detail`

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| creatorId | string | Yes | Creator unique ID, e.g., `7153432386608251946`, obtainable from the `creator_id` in the creator rank response |
| shop_id | string | No | Shop ID filter |
| category_ids | array<integer> | No | Category ID list filter |
| region | string | No | Region/market code, e.g., `US` |
| dateRange | string | No | Time range, e.g., `last7Day`, `last30Day` |
| language | string | No | Return language, e.g., `zh-CN`, `en-US` |
| currency | string | No | Currency unit, e.g., `USD` |

> `creatorId` is required. This endpoint does not support searching creators by keyword/nickname; you must first discover creators using the creator rank endpoint and obtain `creator_id`, then query details with `creatorId`.

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

### Creator Rank Fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| creator_nickname | string | Creator nickname |
| creator_handle | string | TikTok profile name, e.g., `@based` |
| creator_id | string | Creator unique ID, string format to avoid large integer precision loss |
| creator_followers | string | Follower count, returned as string |
| content_views | string | Total content views, returned as string |
| sales_volumn | integer | Sales volume, field spelled as `volumn` |
| revenue | number | Total revenue / GMV, returned in the requested `currency` |
| video_revenue | number | Short video sales revenue |
| live_revenue | number | Livestream sales revenue |
| revenue_growth_rate | number | Revenue growth rate (%), can be positive or negative |

> `outputSchema` may declare a `total` field, but the actual response does not include `total`, nor does it have pagination metadata such as total page count. When paging is needed, keep requesting the next page until a page returns fewer items than `pageSize`.

### Creator Detail Fields (`data` is always a 1-element array)

| Field | Type | Description |
|------|------|------|
| creator_id | string | Creator unique ID |
| creator_nickname | string | Creator nickname |
| creator_handle | string | Creator handle |
| creator_region | string | Creator region |
| creator_status | string | Creator status |
| creator_bio | string | Creator bio |
| creator_belonged_shop_id | string | Belonged shop ID |
| creator_followers | string | Total follower count, returned as string |
| new_followers | integer | New followers within the `dateRange` window |
| revenue | number | Total revenue / GMV |
| video_revenue | number | Video revenue |
| live_revenue | number | Livestream revenue |
| sales_volumn | integer | Sales volume, field spelled as `volumn` |
| unit_price | number | Unit price |
| video_number | integer | Video count within the window |
| video_views | integer | Total video views |
| video_gpm | number | Video GPM |
| live_number | integer | Livestream count within the window |
| live_views | integer | Total livestream views |
| live_gpm | number | Livestream GPM |
| product_number | integer | Associated product count |
| shop_number | integer | Associated shop count |
| creator_contact_email | string | Contact email |
| creator_contact_ins | string | Instagram contact |
| creator_contact_whatsapp | string | WhatsApp contact |
| creator_contact_facebook | string | Facebook contact |
| creator_contact_tiktok | string | TikTok contact |
| creator_contact_zalo | string | Zalo contact |
| creator_contact_line | string | Line contact |

> `data` is typically a 1-element array for valid `creatorId`. The detail response does not include a `total` field.

## Real Response Examples

### Creator Rank

```json
{
  "data": [
    {
      "revenue_growth_rate": 1.36,
      "revenue": 389817.79,
      "video_revenue": 238900.7,
      "sales_volumn": 14781,
      "content_views": "79192665",
      "creator_followers": "3700000",
      "creator_id": "7153432386608251946",
      "creator_handle": "@based",
      "creator_nickname": "BASED",
      "live_revenue": 150857.09
    }
  ],
  "costToken": 14000
}
```

### Creator Detail

```json
{
  "data": [
    {
      "creator_contact_line": "",
      "video_revenue": 238900.7,
      "sales_volumn": 14781,
      "video_number": 222,
      "creator_contact_email": "",
      "product_number": 51,
      "creator_bio": "based.com/tt",
      "revenue": 389817.79,
      "live_gpm": 29.32,
      "video_views": 74047861,
      "video_gpm": 3.23,
      "creator_handle": "@based",
      "creator_nickname": "BASED",
      "live_views": 5144804,
      "creator_followers": "3700000",
      "creator_region": "us",
      "unit_price": 26.37,
      "new_followers": 100000,
      "creator_belonged_shop_id": "7495079418085345590",
      "creator_status": "BELONGED_TO_SELLER",
      "creator_contact_tiktok": "based",
      "creator_id": "7153432386608251946",
      "shop_number": 1,
      "live_number": 2,
      "live_revenue": 150857.09
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
| Upstream call failed / invalid parameters | If `msg` contains Kalodata HTTP 554, retry 1-2 times with the same parameters; if due to missing or invalid `creatorId`, verify that the ID comes from the rank results |

## curl Example

### Creator Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/creator/detail \
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

### Creator Detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/creator/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "creatorId": "7153432386608251946",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```
