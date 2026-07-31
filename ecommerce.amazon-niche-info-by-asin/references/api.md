# Jimore - Amazon - Niche Info by ASIN API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByAsin`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | Product ASIN (required). The tool will find market segments that share the same niche as this ASIN |

### Site and Quantity

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| countryCode | string | No | US | Country code, options: `US` (United States), `JP` (Japan), `DE` (Germany) |
| count | integer | No | 10 | Number of niche markets returned |

### Filter Parameters (All Optional)

**Product and Price**:

| Parameter | Type | Description |
|------|------|------|
| productCountMin | integer | Minimum product count (current) |
| productCountMax | integer | Maximum product count (current) |
| avgPriceMin | number | Minimum average price (current) |
| avgPriceMax | number | Maximum average price (current) |

**Search and Sales (7-Day Stats)**:

| Parameter | Type | Description |
|------|------|------|
| searchVolumeT7Min | integer | Minimum search volume (7-day stats) |
| searchVolumeT7Max | integer | Maximum search volume (7-day stats) |
| unitsSoldT7Min | integer | Minimum sales volume (7-day stats) |
| unitsSoldT7Max | integer | Maximum sales volume (7-day stats) |
| clickCountT7Min | integer | Minimum click volume (7-day stats) |
| clickCountT7Max | integer | Maximum click volume (7-day stats) |
| clickConversionRateT7Min | number | Minimum click conversion rate (7-day stats), range 0-1, 0.1 means 10% conversion rate |
| clickConversionRateT7Max | number | Maximum click conversion rate (7-day stats), range 0-1, 0.1 means 10% conversion rate |

**Brand Metrics**:

| Parameter | Type | Description |
|------|------|------|
| brandCountMin | integer | Minimum brand count |
| brandCountMax | integer | Maximum brand count |
| top5BrandsClickShareMin | number | Minimum top 5 brands' click share in the niche market, range 0-1, 0.1 means 10% click share |
| top5BrandsClickShareMax | number | Maximum top 5 brands' click share in the niche market, range 0-1, 0.1 means 10% click share |
| avgBrandAgeMin | number | Minimum average brand age (current) |
| avgBrandAgeMax | number | Maximum average brand age (current) |
| avgBrandAgeQoqMin | number | Minimum average brand age (90-day stats) |
| avgBrandAgeQoqMax | number | Maximum average brand age (90-day stats) |
| avgBrandAgeYoyMin | number | Minimum average brand age (360-day stats) |
| avgBrandAgeYoyMax | number | Maximum average brand age (360-day stats) |

**Seller Metrics**:

| Parameter | Type | Description |
|------|------|------|
| avgSellingPartnerAgeMin | number | Minimum average selling partner age |
| avgSellingPartnerAgeMax | number | Maximum average selling partner age |
| avgSellingPartnerAgeQoqMin | number | Minimum average selling partner age (90-day stats) |
| avgSellingPartnerAgeQoqMax | number | Maximum average selling partner age (90-day stats) |
| avgSellingPartnerAgeYoyMin | number | Minimum average selling partner age (360-day stats) |
| avgSellingPartnerAgeYoyMax | number | Maximum average selling partner age (360-day stats) |

**Competition and Advertising**:

| Parameter | Type | Description |
|------|------|------|
| top5ProductsClickShareMin | number | Minimum top 5 products click share (current), range 0-1, 0.1 means 10% click share |
| top5ProductsClickShareMax | number | Maximum top 5 products click share (current), range 0-1, 0.1 means 10% click share |
| sponsoredProductsPercentageMin | number | Minimum SP ad share, range 0-1, 0.1 means 10% |
| sponsoredProductsPercentageMax | number | Maximum SP ad share, range 0-1, 0.1 means 10% |
| cpcMediumMin | number | Minimum CPC (current) |
| cpcMediumMax | number | Maximum CPC (current) |

**New Products and Returns**:

| Parameter | Type | Description |
|------|------|------|
| launchRateT180Min | number | Minimum product launch success rate (180-day stats), range 0-1, 0.1 means 10% success rate |
| launchRateT180Max | number | Maximum product launch success rate (180-day stats), range 0-1, 0.1 means 10% success rate |
| returnRateT360Min | number | Minimum return rate (360-day stats), range 0-1, 0.1 means 10% return rate |
| returnRateT360Max | number | Maximum return rate (360-day stats), range 0-1, 0.1 means 10% return rate |

## Response Structure

| Field | Type | Description |
|------|------|------|
| errcode | integer | Business status code, 200 indicates success |
| costToken | integer | Tokens consumed |
| nicheInfoVoList | array | Niche market information list (see niche market object fields below) |

> Note: Business status is determined by the `errcode` field in the response body (`errcode = 200` indicates success). When the result is empty, the API will return a business error (no niche market information matching the criteria).

### Niche Market Object Fields (within `nicheInfoVoList` Array)

| Field | Type | Description |
|------|------|------|
| nicheId | string | Niche market ID |
| nicheTitle | string | Niche market title |
| translationZh | string | Niche market title (Chinese) |
| demand | integer | Niche market score |
| productCount | integer | Product count |
| avgPrice | number | Average product price |
| minimumPrice | number | Lowest product price |
| maximumPrice | number | Highest product price |
| searchVolumeWeekly | integer | Search volume (weekly data) |
| searchVolumeQuarterly | integer | Search volume (quarterly data) |
| searchVolumeGrowthWeekly | number | Search volume growth rate (weekly data) |
| searchVolumeGrowthQuarterly | number | Search volume growth rate (quarterly data) |
| unitsSoldWeekly | integer | Sales volume (weekly data) |
| unitsSoldQuarterly | integer | Sales volume (quarterly data) |
| clickCountWeekly | integer | Click volume (weekly data) |
| clickCountQuarterly | integer | Click volume (quarterly data) |
| clickToSaleConversionWeekly | number | Click conversion rate (weekly data) |
| clickConversionRateQuarterly | number | Click conversion rate (quarterly data) |
| searchConversionRateWeekly | number | Search conversion rate (weekly data) |
| searchConversionRateQuarterly | number | Search conversion rate (quarterly data) |
| brandCount | integer | Brand count |
| top5BrandsClickShare | number | Top 5 brands' click share in the niche market |
| top5ProductsClickShare | number | Top 5 products click share |
| avgBrandAgeNow | number | Average brand age (current) |
| avgBrandAgeQuarterly | number | Average brand age (quarterly data) |
| newProductsLaunchedSemiannual | integer | Number of new products launched (semi-annual data) |
| successfulLaunchedSemiannual | integer | Number of successfully launched products (semi-annual data) |
| launchRateSemiannual | number | Product launch success rate (semi-annual data) |
| returnRateAnnual | number | Return rate (annual data) |
| acos | number | (ACOS) Advertising Cost of Sale |
| profitMarginGt50PctSkuRatio | number | Proportion of products with profit margin > 50% |
| breakEvenRatio | number | Break-even natural share |
| cpc | object | CPC data: `{ high (maximum bid), medium (median bid), low (minimum bid) }` |
| categorieList | array | Product category list |
| referenceAsinImageUrl | string | Niche market reference image URL |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 10000 | No niche market information matching the criteria | Relax filter conditions or try a different ASIN |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByAsin \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0D9NWVC6Z",
    "countryCode": "US",
    "count": 10
  }'
```

### Query Example with Filters

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByAsin \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0D9NWVC6Z",
    "countryCode": "US",
    "count": 20,
    "top5BrandsClickShareMax": 0.5,
    "brandCountMin": 20,
    "searchVolumeT7Min": 5000
  }'
```

---
