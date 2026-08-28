# Jungle Scout Keyword Expansion by Keyword API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/by-keyword`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| marketplace | string | Yes | Target marketplace code. Options: `us`, `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp`. Default `us` |
| searchTerms | string | Yes | Seed keyword (single keyword string) |

### Optional Parameters -- Result Control

| Parameter | Type | Required | Description |
|------|------|------|------|
| needCount | int | No | Total number of results returned |
| sort | string | No | Sort field, default `-monthly_search_volume_exact` (exact search volume descending) |

### Optional Parameters -- Search Volume Filter

| Parameter | Type | Required | Description |
|------|------|------|------|
| minMonthlySearchVolumeExact | int | No | Minimum exact search volume |
| maxMonthlySearchVolumeExact | int | No | Maximum exact search volume |
| minMonthlySearchVolumeBroad | int | No | Minimum broad search volume |
| maxMonthlySearchVolumeBroad | int | No | Maximum broad search volume |

### Optional Parameters -- Other Filters

| Parameter | Type | Required | Description |
|------|------|------|------|
| minWordCount | int | No | Minimum word count for keywords (for filtering long-tail keywords) |
| maxWordCount | int | No | Maximum word count for keywords |
| minOrganicProductCount | int | No | Minimum organic product count |
| maxOrganicProductCount | int | No | Maximum organic product count |

### sort Options

| Value | Description |
|----|------|
| name / -name | Keyword name ascending/descending |
| dominant_category / -dominant_category | Dominant category ascending/descending |
| monthly_trend / -monthly_trend | Monthly trend ascending/descending |
| quarterly_trend / -quarterly_trend | Quarterly trend ascending/descending |
| monthly_search_volume_exact / -monthly_search_volume_exact | Exact search volume ascending/descending (default descending) |
| monthly_search_volume_broad / -monthly_search_volume_broad | Broad search volume ascending/descending |
| recommended_promotions / -recommended_promotions | Recommended promotions ascending/descending |
| sp_brand_ad_bid / -sp_brand_ad_bid | Brand ad bid ascending/descending |
| ppc_bid_broad / -ppc_bid_broad | PPC broad bid ascending/descending |
| ppc_bid_exact / -ppc_bid_exact | PPC exact bid ascending/descending |
| ease_of_ranking_score / -ease_of_ranking_score | Ease of ranking score ascending/descending |
| relevancy_score / -relevancy_score | Relevancy score ascending/descending |
| organic_product_count / -organic_product_count | Organic product count ascending/descending |

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
| costToken | integer | Tokens consumed |
| keywordInfoList | array | Keyword information list |

### Each Object in keywordInfoList

| Field | Type | Description |
|------|------|------|
| name | string | Keyword name |
| country | string | Marketplace code |
| monthlySearchVolumeExact | integer | Monthly average exact match search volume |
| monthlySearchVolumeBroad | integer | Monthly average broad match search volume |
| monthlyTrend | number | Monthly search volume change percentage |
| quarterlyTrend | number | Quarterly search volume change percentage |
| dominantCategory | string | Category with the highest share in search results |
| relevancyScore | integer | Relevance score to the seed keyword |
| easeOfRankingScore | integer | Ease of ranking score (higher means easier to rank) |
| organicProductCount | integer | Number of organic ranking products |
| sponsoredProductCount | integer | Number of sponsored products |
| ppcBidExact | number | Exact match PPC suggested bid (USD) |
| ppcBidBroad | number | Broad match PPC suggested bid (USD) |
| spBrandAdBid | number | Sponsored Brand ad suggested bid (USD) |
| recommendedPromotions | integer | Number of recommended promotion giveaways |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errorCode` field in the response body (errorCode = 200 indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `keywordInfoList` normally |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tool-jungle-scout/keywords/by-keyword \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"marketplace": "us", "searchTerms": "yoga mat", "needCount": 20}'
```

## Response Example

```json
{
  "costToken": 1,
  "keywordInfoList": [
    {
      "name": "yoga mat thick",
      "country": "us",
      "monthlySearchVolumeExact": 45000,
      "monthlySearchVolumeBroad": 120000,
      "monthlyTrend": 15.3,
      "quarterlyTrend": -5.2,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 856,
      "easeOfRankingScore": 3,
      "organicProductCount": 342,
      "sponsoredProductCount": 28,
      "ppcBidExact": 1.25,
      "ppcBidBroad": 0.89,
      "spBrandAdBid": 2.50,
      "recommendedPromotions": 150
    },
    {
      "name": "yoga mat non slip",
      "country": "us",
      "monthlySearchVolumeExact": 38000,
      "monthlySearchVolumeBroad": 95000,
      "monthlyTrend": 8.1,
      "quarterlyTrend": 12.4,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 920,
      "easeOfRankingScore": 2,
      "organicProductCount": 510,
      "sponsoredProductCount": 35,
      "ppcBidExact": 1.58,
      "ppcBidBroad": 1.12,
      "spBrandAdBid": 3.10,
      "recommendedPromotions": 200
    }
  ]
}
```

---
