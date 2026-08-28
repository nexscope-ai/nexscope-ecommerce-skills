# Jungle Scout Keyword Share of Voice API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/share-of-voice`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp` |
| keyword | string | Yes | Keyword to query |

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

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| costToken | integer | Tokens consumed |
| shareOfVoice | object | Share of Voice data body |

### shareOfVoice Object

| Field | Type | Description |
|------|------|------|
| id | string | Resource identifier |
| type | string | Fixed value `share_of_voice` |
| estimated30DaySearchVolume | integer | Exact match search volume over the past 30 days |
| exactSuggestedBidMedian | number | PPC bid median (USD) |
| productCount | integer | Total product count in the first 3 pages of search results |
| updatedAt | string | Data update time |
| topAsinsModelStartDate | string | TOP ASIN click/conversion data window start date |
| topAsinsModelEndDate | string | TOP ASIN click/conversion data window end date |
| brands | array | Brand SOV detail list |
| topAsins | array | TOP 3 ASIN click and conversion list |

### Each Object in brands Array

| Field | Type | Description |
|------|------|------|
| brand | string | Brand name |
| organicProducts | integer | Number of products in organic search results |
| sponsoredProducts | integer | Number of products in ad placements |
| combinedProducts | integer | Combined product count |
| organicBasicSov | number | Organic basic SOV (0-1) |
| organicWeightedSov | number | Organic weighted SOV (0-1) |
| sponsoredBasicSov | number | Sponsored basic SOV (0-1) |
| sponsoredWeightedSov | number | Sponsored weighted SOV (0-1) |
| combinedBasicSov | number | Combined basic SOV (0-1) |
| combinedWeightedSov | number | Combined weighted SOV (0-1) |
| organicAveragePosition | number | Average organic search rank position |
| sponsoredAveragePosition | number | Average sponsored search rank position |
| combinedAveragePosition | number | Combined average rank position |
| organicAveragePrice | number | Average organic search product price |
| sponsoredAveragePrice | number | Average sponsored search product price |
| combinedAveragePrice | number | Combined average product price |

### Each Object in topAsins Array

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN number |
| name | string | Product name |
| brand | string | Brand name |
| clicks | integer | Click volume (30-day window) |
| conversions | integer | Conversion volume (30-day window) |
| conversionRate | number | Conversion rate (0-1) |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `shareOfVoice` object normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits/balance | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/share-of-voice \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "keyword": "portable charger"}'
```

## Response Example

```json
{
  "costToken": 1,
  "shareOfVoice": {
    "id": "us_portable_charger",
    "type": "share_of_voice",
    "estimated30DaySearchVolume": 125000,
    "exactSuggestedBidMedian": 1.25,
    "productCount": 60,
    "updatedAt": "2026-04-10T00:00:00",
    "topAsinsModelStartDate": "2026-03-11",
    "topAsinsModelEndDate": "2026-04-10",
    "brands": [
      {
        "brand": "Anker",
        "organicProducts": 5,
        "sponsoredProducts": 3,
        "combinedProducts": 8,
        "organicBasicSov": 0.083,
        "organicWeightedSov": 0.112,
        "sponsoredBasicSov": 0.15,
        "sponsoredWeightedSov": 0.18,
        "combinedBasicSov": 0.133,
        "combinedWeightedSov": 0.152,
        "organicAveragePosition": 12.4,
        "sponsoredAveragePosition": 5.0,
        "combinedAveragePosition": 9.5,
        "organicAveragePrice": 29.99,
        "sponsoredAveragePrice": 25.99,
        "combinedAveragePrice": 28.49
      }
    ],
    "topAsins": [
      {
        "asin": "B09V3KXJPB",
        "name": "Anker Portable Charger 10000mAh",
        "brand": "Anker",
        "clicks": 15200,
        "conversions": 4560,
        "conversionRate": 0.30
      }
    ]
  }
}
```

---
