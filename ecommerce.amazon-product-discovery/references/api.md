# Jimore Amazon Product Discovery API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/productDiscovery`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Keyword (required; translate the keyword to the language of the selected country) |

### Filter Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| countryCode | string | No | Country, use country abbreviation. Default `US`. Options: `US`, `JP`, `DE` |
| priceMin | number | No | Minimum product price |
| priceMax | number | No | Maximum product price |
| totalReviewsMin | integer | No | Minimum number of reviews |
| totalReviewsMax | integer | No | Maximum number of reviews |
| customerRatingMin | number | No | Minimum rating |
| customerRatingMax | number | No | Maximum rating |
| clickConversionRateMin | number | No | Minimum click-to-purchase conversion rate, value range 0-1, 0.1 means 10% |
| clickConversionRateMax | number | No | Maximum click-to-purchase conversion rate, value range 0-1, 0.1 means 10% |
| clickConversionRateCompositeMin | number | No | Minimum composite conversion rate, value range 0-1, 0.1 means 10% |
| clickConversionRateCompositeMax | number | No | Maximum composite conversion rate, value range 0-1, 0.1 means 10% |
| clickCountT7Min | integer | No | Minimum weekly click count |
| clickCountT7Max | integer | No | Maximum weekly click count |
| clickCountT30Min | integer | No | Minimum monthly click count |
| clickCountT30Max | integer | No | Maximum monthly click count |
| clickCountGrowthT7Min | number | No | Minimum weekly click growth rate, value range 0-1, 0.1 means 10% |
| clickCountGrowthT7Max | number | No | Maximum weekly click growth rate, value range 0-1, 0.1 means 10% |
| clickCountGrowthT30Min | number | No | Minimum monthly click growth rate, value range 0-1, 0.1 means 10% |
| clickCountGrowthT30Max | number | No | Maximum monthly click growth rate, value range 0-1, 0.1 means 10% |
| salesVolumeT360Min | integer | No | Minimum annual sales volume |
| salesVolumeT360Max | integer | No | Maximum annual sales volume |
| grossProfitMarginMin | number | No | Minimum gross profit margin |
| grossProfitMarginMax | number | No | Maximum gross profit margin |
| fbaFeeMin | number | No | Minimum FBA fee |
| fbaFeeMax | number | No | Maximum FBA fee |
| launchDateMin | string | No | Earliest listing time, format: `yyyyMMdd000000` |
| launchDateMax | string | No | Latest listing time, format: `yyyyMMdd000000` |
| nicheCountMin | integer | No | Minimum niche market count |
| nicheCountMax | integer | No | Maximum niche market count |
| sellerCountry | string | No | Seller country/region code, comma-separated for multiple selections, e.g.: `CN,US` |

### Sorting and Pagination

| Parameter | Type | Required | Description |
|------|------|------|------|
| sortField | string | No | Sort field. Default `purchasedClicksT360`. Options: `totalReviews` (total reviews), `price` (price), `launchDate` (listing time), `clickCountT7` (7-day click count), `clickCountT30` (30-day click count), `clickCountT90` (90-day click count), `clickConversionRate` (click-to-purchase conversion rate), `clickConversionRateComposite` (composite click-to-purchase conversion rate), `customerRating` (rating), `purchasedClicksT360` (360-day purchase clicks), `clickCountGrowthT7` (weekly click growth rate), `clickCountGrowthT30` (monthly click growth rate), `currentPrice` (current price), `fbaFee` (FBA fee), `shippingFee` (FBA shipping), `gpm` (gross profit margin) |
| sortType | string | No | Sort direction. Default `desc`. Options: `desc` (descending), `asc` (ascending) |
| page | integer | No | Page number. Default `1` |
| pageSize | integer | No | Items per page (10-100). Default `50` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total count |
| sourceTool | string | Tool type: `jiimore` |
| sourceType | string | Source type: `amazon` |
| type | string | Render style |
| title | string | Title |
| costToken | integer | Token consumption |
| columns | array | Rendered columns |
| products | array | Product list (see below) |

### Product Object Fields

| Field | Type | Description |
|------|------|------|
| asin | string | Amazon product ASIN |
| parentAsin | string | Amazon product parent ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| imageUrl | string | Product main image |
| productImageUrls | array | Product image URL list |
| asinUrl | string | ASIN link |
| ratings | integer | Number of reviews |
| availableDate | string | Listing time (timestamp) |
| availableDateString | string | Listing date (string) |
| categoryNames | array | Category information |
| marketplaceId | string | Site ID |
| clickCountT7 | integer | Weekly click count |
| clickCountT30 | integer | Monthly click count |
| clickCountT90 | integer | Quarterly click count |
| clickConversionRate | number | Click-to-purchase conversion rate |
| clickConversionRateComposite | number | Composite conversion rate |
| grossProfitMargin | number | Gross profit margin |
| fbaFee | number | Amazon fee |
| shippingFee | number | FBA shipping fee |
| sourceTool | string | Tool type: `jiimore` |
| sourceType | string | Source type: `amazon` |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient balance | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/productDiscovery \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "wireless charger",
    "countryCode": "US",
    "clickConversionRateMin": 0.1,
    "priceMin": 10,
    "priceMax": 50,
    "sortField": "clickConversionRate",
    "sortType": "desc",
    "page": 1,
    "pageSize": 20
  }'
```

---
