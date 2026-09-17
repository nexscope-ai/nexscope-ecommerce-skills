# Kalodata TikTok Livestream Search & Detail API Reference

## API Specification

- **Request URL (Livestream Rank)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/livestream/rank`
- **Request URL (Livestream Detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/livestream/detail`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read preferentially from environment variable `NEXSCOPE_API_KEY`, falling back to `NEXSCOPE_API_KEY` (if not configured, follow the **Resolving Authentication and Credit Issues** section in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s

## Request Parameters

### Livestream Rank: `POST /kalodata/livestream/rank`

POST Body (JSON), all parameters are optional:

| Parameter | Type | Required | Description |
|------|------|------|------|
| region | string | No | Region/market code, e.g., `US`. Max length 1000 |
| dateRange | string | No | Time range, e.g., `last7Day` (last 7 days), `last30Day` (last 30 days). Max length 1000 |
| pageNumber | integer | No | Page number, value range 1-5 (invalid values produce a platform error) |
| pageSize | integer | No | Items per page, value range 5-100 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US`. Max length 1000 |
| currency | string | No | Currency unit, e.g., `USD`. Max length 1000 |
| category_id | string | No | Category ID filter |
| shop_id | string | No | Shop ID filter |
| creator_id | string | No | Creator ID filter |
| product_id | string | No | Product ID filter |
| followers_range | string | No | Creator follower range filter |
| sortField | object | No | Sort criteria, structure defined by the gateway; pass an empty object `{}` for default rank order when not sorting |

> This endpoint is used to browse livestream rankings and does not support keyword search. `sortField` is declared as an object in `inputSchema` (with empty `properties`); the default sort is by `revenue` (GMV) descending; passing an empty object `{}` uses the default sort. Available sort fields are subject to what the gateway actually accepts; if an unsupported sort field is passed, the gateway will return a business error. In that case, fall back to default sort and do not attempt other bypass logic.

### Livestream Detail: `POST /kalodata/livestream/detail`

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| livestreamId | string | Yes | Target livestream unique ID (camelCase), e.g., `7661409374878878494`. Typically obtained from the `livestream_id` in the livestream rank endpoint. Max length 1000 |
| region | string | No | Region/market code, e.g., `US`. Max length 1000 |
| dateRange | string | No | Time range, e.g., `last7Day` (last 7 days), `last30Day` (last 30 days). Max length 1000 |
| language | string | No | Return language, e.g., `zh-CN`, `en-US`. Max length 1000 |
| currency | string | No | Currency unit, e.g., `USD`. Max length 1000 |

> `livestreamId` is required; other parameters are optional and the gateway uses defaults when omitted. This is a single-entity detail endpoint and does not support searching by keyword/title. It also has no pagination or sorting parameters like `pageNumber`/`pageSize`/`sortField`. You must first discover livestreams using the livestream rank endpoint and obtain `livestream_id`, then query details with `livestreamId`.

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
| data | array | Livestream rank list or livestream detail data |
| costToken | integer | Tokens consumed for this call, fixed at 14000 |

> The responses for both endpoints **do not include `total`**, nor do they have pagination metadata such as total page count. For the livestream rank, when paging is needed, keep requesting the next page until a page returns fewer items than `pageSize` or page 5 is reached. For livestream detail, `data` is always a 1-element array on success.

### Livestream Rank Fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| livestream_start_time | integer | Livestream start time (epoch milliseconds) |
| livestream_end_time | integer | Livestream end time (epoch milliseconds) |
| livestream_duration | integer | Livestream duration (seconds) |
| livestream_title | string | Livestream title |
| livestream_id | string | Livestream unique ID (string, to avoid large integer precision loss); can be used as `livestreamId` in the detail endpoint |
| creator_id | string | Creator unique ID (string, to avoid large integer precision loss) |
| creator_handle | string | Creator account handle |
| revenue | string | Total revenue / GMV (in the requested `currency`; **returned as string**, e.g., `"185590.52"`) |
| unit_price | string | Unit price (in the requested `currency`; **returned as string**, e.g., `"265.89"`) |
| views | integer | View count |
| record_type | string | Record type (e.g., `SHORT`) |

> **Currency fields are strings**: In the rank endpoint, `revenue` and `unit_price` are returned as strings (e.g., `"185590.52"`), not numbers. Convert to numeric type before use (`float()` / `Number()` / `ConvertFrom-Json`). Default sort is by `revenue` (GMV) descending.

### Livestream Detail Fields (`data` is always a 1-element array)

| Field | Type | Description |
|------|------|------|
| livestream_id | string | Livestream unique ID (matches the requested `livestreamId`) |
| livestream_title | string | Livestream title (e.g., `24 HOUR STREAM`) |
| creator_id | string | Creator unique ID (string, to avoid large integer precision loss) |
| creator_handle | string | Creator username/handle (e.g., `pokepiglt`) |
| livestream_start_time | integer | Livestream start time, epoch milliseconds (e.g., `1783810950000`) |
| livestream_end_time | integer | Livestream end time, epoch milliseconds (e.g., `1783898407000`) |
| livestream_duration | integer | Livestream duration, in **seconds** (e.g., `87457`) |
| record_type | string | Record type (e.g., `SHORT`) |
| viewers | integer | Viewer count (note: DETAIL uses `viewers`, RANK uses `views`) |
| revenue | number | Livestream revenue / GMV, **number** type, in the requested `currency` (e.g., `185590.52`) -- note: in the livestream RANK endpoint `revenue` is a string, but here it is a number |
| gpm | number | GMV per mille, number type -- unique to DETAIL, not present in the RANK endpoint |
| product_number | integer | Product count in the livestream |

> **Field name/type differences from RANK endpoint**: The livestream DETAIL endpoint uses `viewers` (RANK uses `views`); DETAIL's `revenue` is a **number** (RANK's `revenue` is a **string**); DETAIL has `gpm` (RANK does not), DETAIL does not have `unit_price` (RANK does). When extracting with `jq`/`ConvertFrom-Json`, make sure to use the correct field names for each endpoint.

## Real Response Examples

### Livestream Rank

`region=US, dateRange=last7Day, pageSize=5, pageNumber=1` (excerpt of first 2 records):

```json
{
  "data": [
    {
      "livestream_start_time": 1783810950000,
      "livestream_duration": 87457,
      "revenue": "185590.52",
      "livestream_title": "24 HOUR STREAM",
      "creator_id": "7446971784983921710",
      "livestream_id": "7661409374878878494",
      "creator_handle": "pokepiglt",
      "unit_price": "265.89",
      "livestream_end_time": 1783898407000,
      "views": 205348,
      "record_type": "SHORT"
    },
    {
      "livestream_start_time": 1783213207000,
      "livestream_duration": 4306,
      "revenue": "149304.17",
      "livestream_title": "DEALS FOR YOU - Live Now!",
      "creator_id": "7153432386608251946",
      "livestream_id": "7658842218676947743",
      "creator_handle": "based",
      "unit_price": "25.26",
      "livestream_end_time": 1783217513000,
      "views": 51765,
      "record_type": "SHORT"
    }
  ],
  "costToken": 14000
}
```

### Livestream Detail

`livestreamId=7661409374878878494`:

```json
{
  "data": [
    {
      "livestream_start_time": 1783810950000,
      "livestream_duration": 87457,
      "viewers": 205348,
      "revenue": 185590.52,
      "livestream_title": "24 HOUR STREAM",
      "gpm": 903.79,
      "creator_id": "7446971784983921710",
      "livestream_id": "7661409374878878494",
      "creator_handle": "pokepiglt",
      "livestream_end_time": 1783898407000,
      "record_type": "SHORT",
      "product_number": 68
    }
  ],
  "costToken": 14000
}
```

> The complete JSON saved by the script contains all fields. It is recommended to use `jq` or `ConvertFrom-Json` to extract as needed.

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error; follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| Insufficient credits | HTTP 402: follow the **Resolving Authentication and Credit Issues** section in SKILL.md |
| Upstream call failed / invalid parameters | Multiple forms: (1) `msg` like `Call to Kalodata API failed: Kalodata API HTTP 554: ` (transient Kalodata upstream error), retry 1-2 times with the same parameters without changing them; if it persists, contact the gateway side to confirm the Kalodata upstream configuration. (2) `msg` like `page_number range is 1-5, current: 999` (rank page number out of bounds), fix the parameter and retry. (3) Missing required `livestreamId` in the detail endpoint also returns 501, verify that the ID comes from the rank results |

## curl Example

### Livestream Rank

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/livestream/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 5,
    "pageNumber": 1
  }'
```

### Livestream Detail

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/kalodata/livestream/detail \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{
    "livestreamId": "7661409374878878494",
    "region": "US",
    "dateRange": "last7Day"
  }'
```

---
