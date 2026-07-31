# Jimore - Amazon - Niche Market Reviews API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheReviewFromKeyword`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Keyword (required, use the language of the corresponding site, e.g. English for the US site, German for the Germany site), max length 1000 characters |

### Site and Pagination

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| countryCode | string | No | US | Country code, options: `US` (United States), `JP` (Japan), `DE` (Germany) |
| page | integer | No | 1 | Page number (starting from 1) |
| pageSize | integer | No | 50 | Results per page (10-100) |

### Sort

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| sortField | string | No | unitsSoldT7 | Sort field, options: `clickConversionRateT7` (7-day click conversion rate), `demand` (demand score), `avgPrice` (average product price), `maximumPrice` (highest product price), `minimumPrice` (lowest product price), `productCount` (product count), `searchConversionRateT7` (7-day search conversion rate), `searchVolumeT7` (7-day search volume), `unitsSoldT7` (7-day sales volume), `searchVolumeGrowthT7` (search growth rate), `clickCountT90` (90-day click volume), `clickCountT7` (weekly click volume), `brandCount` (brand count), `top5BrandsClickShare` (TOP5 brand share), `newProductsLaunchedT180` (180-day new product success rate - launch count), `successfulLaunchesT180` (180-day new product success rate - new product count), `launchRateT180` (180-day new product success rate - launch rate), `top5ProductsClickShare` (top 5 product click share), `returnRateT360` (return rate), `clickConversionRateT90` (90-day click conversion rate), `searchConversionRateT90` (90-day search conversion rate), `searchVolumeT90` (90-day search volume), `unitsSoldT90` (90-day sales volume), `unitsSoldGrowthT90` (90-day sales growth rate), `searchVolumeGrowthT90` (90-day search growth rate), `acos`, `profitRate50` (profit rate for 50% natural orders) |
| sortType | string | No | desc | Sort direction, options: `desc` (descending), `asc` (ascending) |

### Niche Market Filters (All Optional)

**Product and Brand Metrics**:

| Parameter | Type | Description |
|------|------|------|
| productCountMin | integer | Minimum product count (current) |
| productCountMax | integer | Maximum product count (current) |
| brandCountMin | integer | Minimum brand count |
| brandCountMax | integer | Maximum brand count |
| avgPriceMin | number | Minimum average price (current) |
| avgPriceMax | number | Maximum average price (current) |

**Sales and Search Volume**:

| Parameter | Type | Description |
|------|------|------|
| unitsSoldT7Min | integer | Minimum sales volume (7-day stats) |
| unitsSoldT7Max | integer | Maximum sales volume (7-day stats) |
| searchVolumeT7Min | integer | Minimum search volume (7-day stats) |
| searchVolumeT7Max | integer | Maximum search volume (7-day stats) |
| clickCountT7Min | integer | Minimum click volume (7-day stats) |
| clickCountT7Max | integer | Maximum click volume (7-day stats) |

**Conversion Rate** (range 0-1, representing 0%-100%):

| Parameter | Type | Description |
|------|------|------|
| clickConversionRateT7Min | number | Minimum click conversion rate (7-day stats) |
| clickConversionRateT7Max | number | Maximum click conversion rate (7-day stats) |

**Market Concentration** (range 0-1, representing 0%-100%):

| Parameter | Type | Description |
|------|------|------|
| top5BrandsClickShareMin | number | Minimum top 5 brands' click share in the niche market |
| top5BrandsClickShareMax | number | Maximum top 5 brands' click share in the niche market |
| top5ProductsClickShareMin | number | Minimum top 5 products click share (current) |
| top5ProductsClickShareMax | number | Maximum top 5 products click share (current) |
| sponsoredProductsPercentageMin | number | Minimum SP ad share |
| sponsoredProductsPercentageMax | number | Maximum SP ad share |

**Brand Age**:

| Parameter | Type | Description |
|------|------|------|
| avgBrandAgeMin | number | Minimum average brand age (current) |
| avgBrandAgeMax | number | Maximum average brand age (current) |
| avgBrandAgeQoqMin | number | Minimum average brand age (90-day stats) |
| avgBrandAgeQoqMax | number | Maximum average brand age (90-day stats) |
| avgBrandAgeYoyMin | number | Minimum average brand age (360-day stats) |
| avgBrandAgeYoyMax | number | Maximum average brand age (360-day stats) |

**Selling Partner Age**:

| Parameter | Type | Description |
|------|------|------|
| avgSellingPartnerAgeMin | number | Minimum average selling partner age |
| avgSellingPartnerAgeMax | number | Maximum average selling partner age |
| avgSellingPartnerAgeQoqMin | number | Minimum average selling partner age (90-day stats) |
| avgSellingPartnerAgeQoqMax | number | Maximum average selling partner age (90-day stats) |
| avgSellingPartnerAgeYoyMin | number | Minimum average selling partner age (360-day stats) |
| avgSellingPartnerAgeYoyMax | number | Maximum average selling partner age (360-day stats) |

**New Products and Returns** (range 0-1, representing 0%-100%):

| Parameter | Type | Description |
|------|------|------|
| launchRateT180Min | number | Minimum product launch success rate (180-day stats) |
| launchRateT180Max | number | Maximum product launch success rate (180-day stats) |
| newProductRateT180 | number | Minimum new product share (180-day stats) |
| returnRateT360Min | number | Minimum return rate (360-day stats) |
| returnRateT360Max | number | Maximum return rate (360-day stats) |

**Advertising**:

| Parameter | Type | Description |
|------|------|------|
| cpcMediumMin | number | Minimum CPC (current) |
| cpcMediumMax | number | Maximum CPC (current) |

**System Fields** (can be ignored, automatically handled by the system):


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total count |
| data | array | Niche market review list (see data item fields below for details) |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |
| title | string | Title |

### Data Item Fields

| Field | Type | Description |
|------|------|------|
| nicheId | string | Niche market ID |
| nicheName | string | Niche market name |
| keyword | string | Keyword |
| reviewType | string | Review type (values: [Positive Reviews], [Negative Reviews]) |
| topic | string | Review topic |
| percentOfMentions | number | Share (range 0-1, representing 0%-100%) |
| reviewExample | string | Review example |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheReviewFromKeyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "yoga mat",
    "countryCode": "US",
    "pageSize": 20,
    "sortField": "unitsSoldT7",
    "sortType": "desc"
  }'
```

### Example with Filters

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheReviewFromKeyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "wireless earbuds",
    "countryCode": "US",
    "searchVolumeT7Min": 5000,
    "top5BrandsClickShareMax": 0.5,
    "sortField": "demand",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

---
