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

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

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
