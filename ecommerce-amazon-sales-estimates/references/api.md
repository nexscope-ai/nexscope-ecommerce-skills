# Jungle Scout ASIN Sales Estimates API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/sales-estimates/query`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| asin | string | Yes | Amazon ASIN to query |
| startDate | string | Yes | Start date (format: YYYY-MM-DD) |
| endDate | string | Yes | End date (format: YYYY-MM-DD); must be earlier than the current date |

### Site Mapping

| Site | marketplace value |
|------|---------------|
| United States | us |
| United Kingdom | uk |
| Germany | de |
| India | in |
| Canada | ca |
| France | fr |
| Italy | it |
| Spain | es |
| Mexico | mx |
| Japan | jp |

## Response Structure

| Field | Type | Description |
|------|------|------|
| costToken | integer | Token consumption |
| salesEstimateList | array | Sales estimate result list |

### Each Object in salesEstimateList Array

| Field | Type | Description |
|------|------|------|
| asin | string | Queried ASIN |
| id | string | Data point identifier |
| type | string | Resource type, fixed value `sales_estimate_result` |
| parentAsin | string | Parent ASIN (returned for variant scenarios) |
| isParent | boolean | Whether it is a parent listing |
| isVariant | boolean | Whether it is a variant listing |
| isStandalone | boolean | Whether it is a standalone listing (non-variant) |
| variants | array | Array of variant ASINs under this parent |
| dailyEstimates | array | Array of daily estimate data |

### Each Object in dailyEstimates Array

| Field | Type | Description |
|------|------|------|
| date | string | Data date (YYYY-MM-DD) |
| estimatedUnitsSold | integer | Estimated units sold on that day |
| lastKnownPrice | number | Last known price (USD) |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `salesEstimateList` normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/sales-estimates/query \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "asin": "B0F15TM77B", "startDate": "2026-03-01", "endDate": "2026-03-31"}'
```

## Response Example

```json
{
  "costToken": 1,
  "salesEstimateList": [
    {
      "asin": "B0CXXX1234",
      "id": "sales_estimate_B0CXXX1234_20260301",
      "type": "sales_estimate_result",
      "parentAsin": "B0CXXX0000",
      "isParent": false,
      "isVariant": true,
      "isStandalone": false,
      "variants": [],
      "dailyEstimates": [
        {
          "date": "2026-03-01",
          "estimatedUnitsSold": 35,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-02",
          "estimatedUnitsSold": 42,
          "lastKnownPrice": 29.99
        },
        {
          "date": "2026-03-03",
          "estimatedUnitsSold": 38,
          "lastKnownPrice": 27.99
        }
      ]
    }
  ]
}
```

---
