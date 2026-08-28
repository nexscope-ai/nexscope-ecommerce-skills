# Jimore - Amazon - Niche Market Info by Keyword API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByKeyword`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Keyword (required, translate the keyword to the corresponding country's language based on the selected country), max length 1000 characters |

### Site and Pagination

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| countryCode | string | No | US | Country code, options: `US` (United States), `JP` (Japan), `DE` (Germany) |
| page | integer | No | 1 | Page number (starting from 1) |
| pageSize | integer | No | 50 | Results per page (10-100) |
| sortField | string | No | unitsSoldT7 | Sort field (see sort options below) |
| sortType | string | No | desc | Sort direction: `desc` (descending) or `asc` (ascending) |

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
| clickConversionRateT7Min | number | Minimum click conversion rate (7-day stats), range 0-1, representing 0%-100% |
| clickConversionRateT7Max | number | Maximum click conversion rate (7-day stats), range 0-1, representing 0%-100% |

**Brand Metrics**:

| Parameter | Type | Description |
|------|------|------|
| brandCountMin | integer | Minimum brand count |
| brandCountMax | integer | Maximum brand count |
| top5BrandsClickShareMin | number | Minimum top 5 brands' click share in the niche market, range 0-1, representing 0%-100% |
| top5BrandsClickShareMax | number | Maximum top 5 brands' click share in the niche market, range 0-1, representing 0%-100% |
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
| top5ProductsClickShareMin | number | Minimum top 5 products click share (current), range 0-1, representing 0%-100% |
| top5ProductsClickShareMax | number | Maximum top 5 products click share (current), range 0-1, representing 0%-100% |
| sponsoredProductsPercentageMin | number | Minimum SP ad share, range 0-1, representing 0%-100% |
| sponsoredProductsPercentageMax | number | Maximum SP ad share, range 0-1, representing 0%-100% |
| cpcMediumMin | number | Minimum CPC (current) |
| cpcMediumMax | number | Maximum CPC (current) |

**New Products and Returns**:

| Parameter | Type | Description |
|------|------|------|
| launchRateT180Min | number | Minimum product launch success rate (180-day stats), range 0-1, representing 0%-100% |
| launchRateT180Max | number | Maximum product launch success rate (180-day stats), range 0-1, representing 0%-100% |
| newProductRateT180 | number | Minimum new product share (180-day stats), range 0-1, representing 0%-100% |
| returnRateT360Min | number | Minimum return rate (360-day stats), range 0-1, representing 0%-100% |
| returnRateT360Max | number | Maximum return rate (360-day stats), range 0-1, representing 0%-100% |

### Sort Options

| Value | Description |
|------|------|
| unitsSoldT7 | 7-day sales volume |
| searchVolumeT7 | 7-day search volume |
| demand | Demand score |
| avgPrice | Average product price |
| maximumPrice | Highest product price |
| minimumPrice | Lowest product price |
| productCount | Product count |
| searchConversionRateT7 | 7-day search conversion rate |
| clickConversionRateT7 | 7-day click conversion rate |
| searchVolumeGrowthT7 | Search growth rate |
| clickCountT7 | Weekly click volume |
| clickCountT90 | 90-day click volume |
| brandCount | Brand count |
| top5BrandsClickShare | TOP5 brand share |
| top5ProductsClickShare | Top 5 product click share |
| newProductsLaunchedT180 | 180-day new product success rate - launch count |
| successfulLaunchesT180 | 180-day new product success rate - new product count |
| launchRateT180 | 180-day new product success rate - launch rate |
| returnRateT360 | Return rate |
| clickConversionRateT90 | 90-day click conversion rate |
| searchConversionRateT90 | 90-day search conversion rate |
| searchVolumeT90 | 90-day search volume |
| unitsSoldT90 | 90-day sales volume |
| unitsSoldGrowthT90 | 90-day sales growth rate |
| searchVolumeGrowthT90 | 90-day search growth rate |
| acos | Advertising cost of sale |
| profitRate50 | Profit rate for 50% natural orders |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total count |
| data | array | Niche market information list (see niche market object fields below) |
| columns | array | Render columns |
| title | string | Title |
| type | string | Render style |
| costToken | integer | Tokens consumed |

### Niche Market Object Fields (within `data` Array)

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
| breakEvenRatio | number | Break-even ratio |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByKeyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "wireless earbuds",
    "countryCode": "US",
    "sortField": "demand",
    "sortType": "desc",
    "page": 1,
    "pageSize": 20
  }'
```

### Query Example with Filters

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfoByKeyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "yoga mat",
    "countryCode": "US",
    "top5BrandsClickShareMax": 0.5,
    "brandCountMin": 20,
    "searchVolumeT7Min": 5000,
    "sortField": "unitsSoldT7",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

---
