# Ruiguan Text Trademark Detection API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/textTrademarkDetection`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| productTitle | string | Yes | Product title, used for trademark detection (max 1000 characters) |
| regions | string | No | Country/region codes, multiple separated by commas. Supported values: US, EM, GB, DE, FR, IT, ES, AU, CA, MX, JP, CN, WO, TR, BX |
| limit | integer | Yes | Limit on the number of returned results (default 100, max 500) |
| productText | string | No | Other product text information, such as bullet points or product description (max 1000 characters) |


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
| total | integer | Number of matched trademark records |
| data | array | Trademark list (flattened), each element contains the following fields |
| detectId | string | API call ID |
| columns | array | Rendered column definitions |
| blacklistTrademarks | array | Blacklisted trademarks detected in the text |
| whitelistTrademarks | array | Whitelisted (safe) trademarks detected in the text |
| textTrademarkRadar | string | Product risk level: "0" = low risk, "1" = pending manual review, "2" = high risk |
| costToken | integer | Token cost |
| type | string | Render style |

### data[] Element Fields

| Field | Type | Description |
|------|------|------|
| trademarkName | string | Trademark word |
| region | string | Country/region code |
| score | integer | Risk score |
| highestModeScore | integer | Highest risk score (range 0-5) |
| trademarksStatus | string | Status of the highest-score trademark word |
| regionStatus | string | Trademark status in the matched region |
| holder | string | Rights holder |
| applicationNumber | string | Application number |
| registrationNumber | string | Registration number |
| isFamous | boolean | Whether it is a famous trademark |
| isAmazonBrand | boolean | Whether it is an Amazon hot search brand |
| isActiveHolder | boolean | Whether the holder is an active enforcer |
| isCompatibility | boolean | Whether it is compatibility |
| isCommonSense | boolean | Whether it is a common word |
| niceClass | array | Nice classification |
| originalTextMatches | array | Original matched trigger words |

### blacklistTrademarks[] and whitelistTrademarks[] Element Fields

| Field | Type | Description |
|------|------|------|
| trademark | string | Trademark name |
| region | string | Country/region code |
| note | string | Remarks |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/textTrademarkDetection \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "productTitle": "Wireless Bluetooth Headphones Noise Cancelling Over Ear",
    "regions": "US",
    "limit": 100
  }'
```

### Example with Product Text

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/textTrademarkDetection \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "productTitle": "Portable USB-C Charger Fast Charging Power Bank",
    "productText": "Compatible with iPhone, Samsung Galaxy, supports QC 3.0",
    "regions": "US,EM,GB",
    "limit": 200
  }'
```

---
