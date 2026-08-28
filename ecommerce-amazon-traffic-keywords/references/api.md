# SellerSprite Traffic Keyword Reverse Lookup API Reference

This document aligns with the `inputSchema` / `outputSchema` of the tool `_sellersprite_traffic_keyword` (see `temp/tools20260430.txt`).

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/traffic/keyword`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

  | Parameter | Type | Required | Constraints | Description |
|------|------|------|------|------|
| marketplace | string | Yes | See table below | Marketplace site, default `US` |
| asin | string | Yes | maxLength 1000 | Product ASIN to reverse lookup |
| month | string | No | Regex `^(19|20)\d{2}(0[1-9]|1[0-2])$` | Historical month in `yyyyMM` format; defaults to the last 30 days if not provided |
| page | integer | No | Default 1 | Current page |
| size | integer | No | Default 50, min 1, max 100; up to 2000 records can be queried | Items per page |
| keyword | string | No | maxLength 1000 | Keyword filter |
| badges | string | No | maxLength 1000, comma-separated for multiple values | Traffic keyword type (impression position), see [Badges Enum](#badges-enum) |
| trafficKeywordTypes | string | No | maxLength 1000, comma-separated for multiple values | Traffic share type, see [trafficKeywordTypes Enum](#traffickeywordtypes-enum) |
| conversionKeywordTypes | string | No | maxLength 1000, comma-separated for multiple values | Traffic conversion type, see [conversionKeywordTypes Enum](#conversionkeywordtypes-enum) |
| orderField | string | No | maxLength 1000, default `rankPosition` | Sort field, see [orderField Options](#orderfield-options) |
| orderDesc | boolean | No | Default `false` | Whether to sort in descending order |

### marketplace Options

| Value | Meaning |
|------|------|
| US | United States USD($) |
| JP | Japan JPY(\) |
| UK | United Kingdom GBP(PS) |
| DE | Germany EUR(EUR) |
| FR | France EUR(EUR) |
| IT | Italy EUR(EUR) |
| ES | Spain EUR(EUR) |
| CA | Canada C$($) |
| IN | India INR(Rs) |

### Badges Enum

Multiple values separated by English commas.

| Value | Meaning |
|------|------|
| naturalSearching | Natural search keyword |
| amazonChoice | AC recommended keyword |
| editorialRecommendations | ER recommended keyword |
| fourStar | Four-star recommended keyword |
| highlyRated | HR recommended keyword |
| sponsorBrand | Brand recommended keyword |
| sponsorVideo | Video recommended keyword |
| ads | SP ad keyword |

### trafficKeywordTypes Enum

Multiple values separated by English commas (consistent with tool schema text).

| Value | Meaning |
|------|------|
| primary | Primary traffic keyword |
| precise | Precise traffic keyword |
| preciseLongTail | Conversion churn keyword |

### conversionKeywordTypes Enum

Multiple values separated by English commas.

| Value | Meaning |
|------|------|
| excellent | High-conversion keyword |
| stable | Stable-conversion keyword |
| lost | Conversion churn keyword |
| invalid | Invalid impression keyword |

### orderField Options

| Value | Meaning |
|------|------|
| rankPosition | Organic ranking (default) |
| adPosition | Ad ranking |
| createdTime | Creation time |
| searchesRank | Search volume weekly ranking |
| searches | Monthly search volume |
| purchases | Monthly purchase volume |
| purchaseRate | Purchase rate |
| products | Product count |
| supplyDemandRatio | Supply-demand ratio |
| latest1daysAds | Ad competitor count |
| bid | PPC bid |
| trafficPercentage | Traffic share |

## Response Structure

### Top-level Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Total count |
| marketplace | string | Marketplace code |
| asin | string | Queried ASIN |
| data | array | Traffic keyword list (corresponds to third-party `data.items`) |
| summaryList | array | High-frequency keyword summary list |
| columns | array | Column definitions |
| costToken | integer | Token consumption |
| type | string | Render style |

### summaryList Elements

| Field | Type | Description |
|------|------|------|
| total | integer | Total count |
| keywords | string | Keywords |

### data[] Elements (Individual Traffic Keyword)

| Field | Type | Description |
|------|------|------|
| keyword | string | Keyword |
| keywordCn | string | Keyword Chinese translation |
| trafficKeywordType | string | Traffic share type |
| conversionKeywordType | string | Traffic conversion type |
| badges | array | Impression position (traffic keyword type) |
| rankPosition | object | Organic ranking position info, see [Ranking Object](#ranking-object-rankposition--adposition) |
| adPosition | object | Ad ranking position info, same structure as [Ranking Object](#ranking-object-rankposition--adposition) |
| searches | integer | Monthly search volume |
| searchesRank | integer | Weekly search volume ranking |
| searchesRankTimeFrom | integer | Weekly search volume ranking time range start |
| searchesRankTimeTo | integer | Weekly search volume ranking time range end |
| purchases | integer | Monthly purchase volume |
| purchaseRate | number | Purchase rate |
| products | integer | Product count |
| supplyDemandRatio | number | Supply-demand ratio |
| trafficPercentage | number | Traffic share |
| naturalRatio | number | Traffic distribution - organic share |
| adRatio | number | Traffic distribution - ad share |
| calculatedWeeklySearches | number | Estimated weekly impressions |
| impressions | integer | Impressions |
| clicks | integer | Clicks |
| bid | number | PPC bid |
| bidMin | number | PPC bid lower limit |
| bidMax | number | PPC bid upper limit |
| latest1daysAds | integer | Ad competitors in the last 1 day |
| latest7daysAds | integer | Ad competitors in the last 7 days |
| latest30daysAds | integer | Ad competitors in the last 30 days |
| sprt | number | SP-related ratio |
| monopolyClickRate | number | Monopoly click rate |
| top3ClickingRate | number | Top 3 click rate |
| top3ConversionRate | number | Top 3 conversion rate |
| titleDensity | number | Title density |
| stats | array | High-frequency words, elements see table below |
| updatedTime | integer | Update time |

### stats[] Elements (High-frequency Word Sub-item)

| Field | Type | Description |
|------|------|------|
| keywords | string | Word |
| total | integer | Total count |
| rankPosition | object | Organic ranking position, structure see below |
| adPosition | object | Ad ranking position, structure see below |

### Ranking Object (rankPosition / adPosition)

| Field | Type | Description |
|------|------|------|
| updatedTime | integer | Ranking time |
| pageSize | integer | Items per page |
| index | integer | Position on current page |
| page | integer | Page number |
| position | integer | Position in total results |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/traffic/keyword   -H "Authorization: Bearer ${NEXSCOPE_API_KEY}"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "asin": "B0XXXXXXXXX",
    "page": 1,
    "size": 50
  }'
```

---
