# Jimore Amazon Product Discovery (ASIN) API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/pageAsinsByAsin`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| asin | string | Yes | Reference ASIN, used to query competitor listings that belong to the same niche as this ASIN, max length 1000 characters |

### Site and Pagination

  | Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| countryCode | string | No | US | Country code, options: `US` (United States), `JP` (Japan), `DE` (Germany) |
| page | integer | No | 1 | Page number (starting from 1) |
| pageSize | integer | No | 50 | Items returned per page (10-100) |
| sortField | string | No | purchasedClicksT360 | Sort field (see sort options below) |
| sortType | string | No | desc | Sort direction: `desc` (descending) or `asc` (ascending) |

### Filter Parameters (All Optional)

**Price and FBA**:

  | Parameter | Type | Description |
|------|------|------|
| priceMin | number | Minimum product price |
| priceMax | number | Maximum product price |
| fbaFeeMin | number | Minimum FBA fee |
| fbaFeeMax | number | Maximum FBA fee |
| grossProfitMarginMin | number | Minimum gross profit margin |
| grossProfitMarginMax | number | Maximum gross profit margin |

**Reviews and Rating**:

  | Parameter | Type | Description |
|------|------|------|
| totalReviewsMin | integer | Minimum review count |
| totalReviewsMax | integer | Maximum review count |
| customerRatingMin | number | Minimum rating, range 0.0-5.0 |
| customerRatingMax | number | Maximum rating, range 0.0-5.0 |

**Click Data (7 days)**:

  | Parameter | Type | Description |
|------|------|------|
| clickCountT7Min | integer | Minimum weekly click count |
| clickCountT7Max | integer | Maximum weekly click count |
| clickCountGrowthT7Min | number | Minimum weekly click growth rate, range 0-1, e.g., 0.1 means 10% |
| clickCountGrowthT7Max | number | Maximum weekly click growth rate, range 0-1, e.g., 0.1 means 10% |
| clickConversionRateMin | number | Minimum click conversion rate, range 0-1, e.g., 0.1 means 10% |
| clickConversionRateMax | number | Maximum click conversion rate, range 0-1, e.g., 0.1 means 10% |

**Click Data (30 days)**:

  | Parameter | Type | Description |
|------|------|------|
| clickCountT30Min | integer | Minimum monthly click count |
| clickCountT30Max | integer | Maximum monthly click count |
| clickCountGrowthT30Min | number | Minimum monthly click growth rate, range 0-1, e.g., 0.1 means 10% |
| clickCountGrowthT30Max | number | Maximum monthly click growth rate, range 0-1, e.g., 0.1 means 10% |

**Composite Conversion Rate**:

  | Parameter | Type | Description |
|------|------|------|
| clickConversionRateCompositeMin | number | Minimum composite click conversion rate, range 0-1, e.g., 0.1 means 10% |
| clickConversionRateCompositeMax | number | Maximum composite click conversion rate, range 0-1, e.g., 0.1 means 10% |

**Sales and Listing Time**:

  | Parameter | Type | Description |
|------|------|------|
| salesVolumeT360Min | integer | Minimum annual sales volume |
| salesVolumeT360Max | integer | Maximum annual sales volume |
| launchDateMin | string | Earliest listing time, format yyyyMMdd000000 |
| launchDateMax | string | Latest listing time, format yyyyMMdd000000 |

**Niche and Sellers**:

  | Parameter | Type | Description |
|------|------|------|
| nicheCountMin | integer | Minimum number of niche markets |
| nicheCountMax | integer | Maximum number of niche markets |
| sellerCountry | string | Seller country code, comma-separated for multiple countries, e.g.: CN,US |

### Sort Options

| Value | Description |
|------|------|
| purchasedClicksT360 | 360-day purchase clicks (default) |
| totalReviews | Review count |
| price | Price |
| launchDate | Listing time |
| clickCountT30 | 30-day click count |
| clickCountT90 | 90-day click count |
| clickCountT7 | 7-day click count |
| clickConversionRate | Click conversion rate (original 7-day click conversion rate) |
| clickConversionRateComposite | Composite click conversion rate |
| customerRating | Rating |
| clickCountGrowthT7 | Weekly click growth rate |
| clickCountGrowthT30 | Monthly click growth rate |
| currentPrice | Current price |
| fbaFee | FBA fee |
| shippingFee | FBA shipping fee |
| gpm | Gross profit margin |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total record count |
| pages | integer | Total page count |
| page | integer | Current page |
| pageSize | integer | Page size |
| data | array | ASIN product list (see product object fields below) |
| columns | array | Rendered columns |
| type | string | Render style |
| costToken | integer | Token consumption |

### Product Object Fields (in `data` array)

| Field | Type | Description |
|------|------|------|
| asin | string | Amazon product ASIN |
| parentAsin | string | Amazon product parent ASIN |
| title | string | Product title |
| brand | string | Brand |
| price | number | Price |
| currentPrice | number | Current price |
| currency | string | Currency |
| customerRating | number | Rating |
| totalReviews | integer | Review count |
| launchDate | string | Listing time |
| link | string | ASIN link |
| imagesUrl | string | Product main image |
| sellerName | string | Seller name |
| sellerId | string | Seller ID |
| fbaFee | number | FBA fee |
| shippingFee | number | FBA shipping fee |
| gpm | number | Gross profit margin |
| clickConversionRate | number | Click conversion rate (original 7-day click conversion rate) |
| clickConversionRateComposite | number | Composite click conversion rate |
| clickConversionRateType | string | Conversion rate calculation type |
| clickConversionRateCompositeType | string | Composite conversion rate calculation type |
| clickCountT7 | integer | 7-day click count |
| clickCountT30 | integer | 30-day click count |
| clickCountT90 | integer | 90-day click count |
| clickCountGrowthT7 | number | Weekly click growth rate |
| clickCountGrowthT30 | number | Monthly click growth rate |
| purchasedClicksT360 | integer | 360-day purchase clicks |
| salesVolumeT360 | integer | Annual sales volume |
| nicheCount | integer | Number of niche markets the product belongs to |
| sameNicheTitle | string | Same niche title |
| involvedNum | integer | Number of involved keywords |
| involvedFrequency | integer | Frequency of involved keywords |
| categoryNames | array | Category information |
| hasMetric | boolean | Whether the product has metrics |
| searchValueType | string | Search type: exact (exact match), sameNiche (same niche as reference ASIN), category (category) |
| niches | array | Top 3 niche markets, containing: nicheId, nicheTitle, demand (market score), image, marketplaceId |
| bestSellersRanking | array | Best seller rankings, containing: rank (ranking), category (category name) |
| trends | array | 90-day trend data, containing: day (date), clickCountT7 (weekly click count), reviewCount (review count), reviewRating (review rating), bestSellerRanking (BSR ranking), averagePriceT7 (weekly average price), totalOfferDepthT7 (7-day new offers) |
| lastUpdateTime | string | Last update time |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/pageAsinsByAsin \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0GC4RPX79",
    "countryCode": "US",
    "sortField": "purchasedClicksT360",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

### Query Example with Filter Conditions

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/pageAsinsByAsin \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0GC4RPX79",
    "countryCode": "US",
    "clickConversionRateCompositeMin": 0.15,
    "clickCountT30Min": 2000,
    "totalReviewsMax": 100,
    "sortField": "clickConversionRateComposite",
    "sortType": "desc",
    "page": 1,
    "pageSize": 50
  }'
```

---
