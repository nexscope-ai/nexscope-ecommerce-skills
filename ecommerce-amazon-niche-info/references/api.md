# Jimore - Amazon - Niche Market Insights API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfo`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| nicheId | string | Yes | Niche market ID, max length 1000 characters, only supports single ID query |
| countryCode | string | No | Country code, only supports `US`, `JP`, `DE`, default `US` |


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
| total | integer | Record count |
| data | array | Niche market information list, each element is an object containing the fields below |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |

### `data` Element Key Fields

#### Market Overview

| Field | Type | Description |
|------|------|------|
| nicheId | string | Niche market ID |
| nicheTitle | string | Niche market title |
| translationZh | string | Niche market title (Chinese) |
| referenceAsinImageUrl | string | Niche market reference image URL |
| marketplaceId | string | Market ID |
| demand | integer | Niche market score |
| categorieList | array | Product category list |

#### Product and Brand Counts

| Field | Type | Description |
|------|------|------|
| productCount | integer | Product count |
| productCountNow | integer | Product count (current) |
| productCountT90Before | integer | Product count (90 days ago) |
| productCountT360Before | integer | Product count (360 days ago) |
| brandCount | integer | Brand count |
| brandCountNow | integer | Brand count (current) |
| brandCountT90Before | integer | Brand count (90 days ago) |
| brandCountT360Before | integer | Brand count (360 days ago) |
| brandCountT360Now | integer | Brand count (360-day stats) (current) |
| brandCountT360T90Before | integer | Brand count (360-day stats) (90 days ago) |
| brandCountT360T360Before | integer | Brand count (360-day stats) (360 days ago) |
| sellingPartnerCountNow | integer | Selling partner count (current) |
| sellingPartnerCountT90Before | integer | Selling partner count (90 days ago) |
| sellingPartnerCountT360Before | integer | Selling partner count (360 days ago) |
| sellingPartnerCountT360Now | integer | Selling partner count (360-day stats) (current) |
| sellingPartnerCountT360T90Before | integer | Selling partner count (360-day stats) (90 days ago) |
| sellingPartnerCountT360T360Before | integer | Selling partner count (360-day stats) (360 days ago) |

#### Price

| Field | Type | Description |
|------|------|------|
| avgPrice | number | Average product price |
| avgProductPriceNow | number | Average product price (current) |
| avgProductPriceT90Before | number | Average product price (90 days ago) |
| avgProductPriceT360Before | number | Average product price (360 days ago) |
| minimumPrice | number | Lowest product price |
| maximumPrice | number | Highest product price |

#### Search and Conversion

| Field | Type | Description |
|------|------|------|
| searchVolumeWeekly | integer | Search volume (weekly data) |
| searchVolumeQuarterly | integer | Search volume (quarterly data) |
| searchVolumeGrowthWeekly | number | Search volume growth rate (weekly data) |
| searchVolumeGrowthQuarterly | number | Search volume growth rate (quarterly data) |
| searchConversionRateWeekly | number | Search conversion rate (weekly data) |
| searchConversionRateQuarterly | number | Search conversion rate (quarterly data) |
| clickCountWeekly | integer | Click volume (weekly data) |
| clickCountQuarterly | integer | Click volume (quarterly data) |
| clickConversionRateQuarterly | number | Click conversion rate (quarterly data) |
| clickToSaleConversionWeekly | number | Click conversion rate (weekly data) |
| unitsSoldWeekly | integer | Sales volume (weekly data) |
| unitsSoldQuarterly | integer | Sales volume (quarterly data) |

#### Competition - Product Click Share

| Field | Type | Description |
|------|------|------|
| top5ProductsClickShare | number | Top 5 products click share |
| top5ProductsClickShareNow | number | Top 5 products' click share in the niche market (current) |
| top5ProductsClickShareT90Before | number | Top 5 products' click share in the niche market (90 days ago) |
| top5ProductsClickShareT360Before | number | Top 5 products' click share in the niche market (360 days ago) |
| top5ProductsClickShareT360Now | number | Top 5 products click share (360-day stats) (current) |
| top5ProductsClickShareT360T90Before | number | Top 5 products click share (360-day stats) (90 days ago) |
| top5ProductsClickShareT360T360Before | number | Top 5 products click share (360-day stats) (360 days ago) |
| top20ProductsClickShareNow | number | Top 20 products' click share in the niche market (current) |
| top20ProductsClickShareT90Before | number | Top 20 products' click share in the niche market (90 days ago) |
| top20ProductsClickShareT360Before | number | Top 20 products' click share in the niche market (360 days ago) |
| top20ProductsClickShareT360Now | number | Top 20 products click share (360-day stats) (current) |
| top20ProductsClickShareT360T90Before | number | Top 20 products click share (360-day stats) (90 days ago) |
| top20ProductsClickShareT360T360Before | number | Top 20 products click share (360-day stats) (360 days ago) |

#### Competition - Brand Click Share

| Field | Type | Description |
|------|------|------|
| top5BrandsClickShare | number | Top 5 brands' click share in the niche market |
| top5BrandsClickShareNow | number | Top 5 brands' click share in the niche market (current) |
| top5BrandsClickShareT90Before | number | Top 5 brands' click share in the niche market (90 days ago) |
| top5BrandsClickShareT360Before | number | Top 5 brands' click share in the niche market (360 days ago) |
| top5BrandsClickShareT360Now | number | Top 5 brands' click share in the niche market (360-day stats) (current) |
| top5BrandsClickShareT360T90Before | number | Top 5 brands' click share in the niche market (360-day stats) (90 days ago) |
| top5BrandsClickShareT360T360Before | number | Top 5 brands' click share in the niche market (360-day stats) (360 days ago) |
| top20BrandsClickShareNow | number | Top 20 brands' click share in the niche market (current) |
| top20BrandsClickShareT90Before | number | Top 20 brands' click share in the niche market (90 days ago) |
| top20BrandsClickShareT360Before | number | Top 20 brands' click share in the niche market (360 days ago) |
| top20BrandsClickShareT360Now | number | Top 20 brands' click share in the niche market (360-day stats) (current) |
| top20BrandsClickShareT360T90Before | number | Top 20 brands' click share in the niche market (360-day stats) (90 days ago) |
| top20BrandsClickShareT360T360Before | number | Top 20 brands' click share in the niche market (360-day stats) (360 days ago) |

#### Product Launches

| Field | Type | Description |
|------|------|------|
| newProductsLaunchedSemiannual | integer | Number of new products launched (semi-annual data) |
| newProductsLaunchedT180Now | integer | Number of new products launched (180-day stats) (current) |
| newProductsLaunchedT180T90Before | integer | Number of new products launched (180-day stats) (90 days ago) |
| newProductsLaunchedT180T360Before | integer | Number of new products launched (180-day stats) (360 days ago) |
| newProductsLaunchedT360Now | integer | Number of newly listed products (360-day stats) (current) |
| newProductsLaunchedT360T90Before | integer | Number of newly listed products (360-day stats) (90 days ago) |
| newProductsLaunchedT360T360Before | integer | Number of newly listed products (360-day stats) (360 days ago) |
| successfulLaunchedSemiannual | integer | Number of successfully launched products (semi-annual data) |
| launchRateSemiannual | number | Product launch success rate (semi-annual data) |
| successfulLaunchesT90Now | integer | Successfully launched count (90-day stats) (current) |
| successfulLaunchesT90T90Before | integer | Successfully launched count (90-day stats) (90 days ago) |
| successfulLaunchesT90T360Before | integer | Successfully launched count (90-day stats) (360 days ago) |
| successfulLaunchesT180Now | integer | Number of successfully launched products (180-day stats) (current) |
| successfulLaunchesT180T90Before | integer | Number of successfully launched products (180-day stats) (90 days ago) |
| successfulLaunchesT180T360Before | integer | Number of successfully launched products (180-day stats) (360 days ago) |
| successfulLaunchesT360Now | integer | Number of successfully launched products (360-day stats) (current) |
| successfulLaunchesT360T90Before | integer | Number of successfully launched products (360-day stats) (90 days ago) |
| successfulLaunchesT360T360Before | integer | Number of successfully launched products (360-day stats) (360 days ago) |

#### Inventory and Operations

| Field | Type | Description |
|------|------|------|
| avgOOSRateNow | number | Average out-of-stock rate (current) |
| avgOOSRateT90Before | number | Average out-of-stock rate (90 days ago) |
| avgOOSRateT360Before | number | Average out-of-stock rate (360 days ago) |
| avgOOSRateT360Now | number | Average out-of-stock rate (360-day stats) (current) |
| avgOOSRateT360T90Before | number | Average out-of-stock rate (360-day stats) (90 days ago) |
| avgOOSRateT360T360Before | number | Average out-of-stock rate (360-day stats) (360 days ago) |
| primeProductsPercentageNow | number | Prime product percentage (current) |
| primeProductsPercentageT90Before | number | Prime product percentage (90 days ago) |
| primeProductsPercentageT360Before | number | Prime product percentage (360 days ago) |
| primeProductsPercentageT360Now | number | Prime product percentage (360-day stats) (current) |
| primeProductsPercentageT360T90Before | number | Prime product percentage (360-day stats) (90 days ago) |
| primeProductsPercentageT360T360Before | number | Prime product percentage (360-day stats) (360 days ago) |

#### Reviews and Ratings

| Field | Type | Description |
|------|------|------|
| avgReviewRatingNow | number | Average review rating (current) |
| avgReviewRatingT90Before | number | Average review rating (90 days ago) |
| avgReviewRatingT360Before | number | Average review rating (360 days ago) |
| avgReviewCountNow | number | Average review count (current) |
| avgReviewCountT90Before | number | Average review count (90 days ago) |
| avgReviewCountT360Before | number | Average review count (360 days ago) |
| positiveCustomerReviewInsights | array | Positive customer review insights |
| negativeCustomerReviewInsights | array | Negative customer review insights |
| productStarRatingImpact | array | Product star rating impact information |

#### Seller Maturity

| Field | Type | Description |
|------|------|------|
| avgBrandAgeNow | number | Average brand age (current) |
| avgBrandAgeT90Before | number | Average brand age (90 days ago) |
| avgBrandAgeT360Before | number | Average brand age (360 days ago) |
| avgBrandAgeQuarterly | number | Average brand age (quarterly data) |
| avgBrandAgeT360Now | number | Average brand age (360-day stats) (current) |
| avgBrandAgeT360T90Before | number | Average brand age (360-day stats) (90 days ago) |
| avgBrandAgeT360T360Before | number | Average brand age (360-day stats) (360 days ago) |
| avgSellingPartnerAgeNow | number | Average selling partner age (current) |
| avgSellingPartnerAgeT90Before | number | Average selling partner age (90 days ago) |
| avgSellingPartnerAgeT360Before | number | Average selling partner age (360 days ago) |
| avgBestSellerRankNow | number | Average Best Seller rank (current) |
| avgBestSellerRankT90Before | number | Average Best Seller rank (90 days ago) |
| avgBestSellerRankT360Before | number | Average Best Seller rank (360 days ago) |

#### Advertising and Profitability

| Field | Type | Description |
|------|------|------|
| acos | number | (ACOS) Advertising Cost of Sale |
| sponsoredProductsPercentageNow | number | Percentage of products with Sponsored Products ads (current) |
| sponsoredProductsPercentageT90Before | number | Percentage of products with Sponsored Products ads (90 days ago) |
| sponsoredProductsPercentageT360Before | number | Percentage of products with Sponsored Products ads (360 days ago) |
| sponsoredProductsPercentageT360Now | number | Percentage of products with Sponsored Products ads (360-day stats) (current) |
| sponsoredProductsPercentageT360T90Before | number | Percentage of products with Sponsored Products ads (360-day stats) (90 days ago) |
| sponsoredProductsPercentageT360T360Before | number | Percentage of products with Sponsored Products ads (360-day stats) (360 days ago) |
| profitMarginGt50PctSkuRatio | number | Proportion of products with profit margin > 50% |
| breakEvenRatio | number | Break-even ratio |
| returnRateAnnual | number | Return rate (annual data) |
| cpc | object | CPC (Cost Per Click) data |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/jiimore/getNicheInfo \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"nicheId": "12345678", "countryCode": "US"}'
```

---
