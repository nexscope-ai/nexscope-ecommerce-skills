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
| costToken | integer | Tokens consumed |
| nicheInfoVoList | array | Niche market information list (see niche market object fields below) |

> Note: Read only the numeric outer platform code. When the result is empty, the API will return a business error (no niche market information matching the criteria).

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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| No niche market information matching the criteria | Relax filter conditions or try a different ASIN |

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
