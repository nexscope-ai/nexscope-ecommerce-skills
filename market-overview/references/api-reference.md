# API Reference — Market Overview v1.0

## Data Sources Overview

| # | Source | Provider | Endpoint | Purpose |
|---|--------|----------|----------|---------|
| 1 | Segments | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/segments` | Market totals |
| 2 | Sales Estimates | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/sales_estimates_query` | Growth calculation |
| 3 | Product DB | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query` | Product-level data |
| 4 | Share of Voice | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/share-of-voice` | Brand keyword share |
| 5 | ABA | Data Provider | `/aba/intelligentQuery` | Search trends, click share |
| 6 | Keepa History | Data Provider | `/keepa/productSeries` | Price/BSR/seller trends |
| 7 | Keepa Detail | Data Provider | `/keepa/productRequest` | Listing date, 12-month sales |

---

## 1. Jungle Scout Segments

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/segments
```

### Headers
```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_revenue` | number | Total monthly revenue |
| `total_revenue_trend` | number | Revenue trend % |
| `total_unit_sales` | number | Total monthly units |
| `total_unit_sales_trend` | number | Units trend % |
| `total_asins` | number | Active product count |
| `total_brands` | number | Brand count |
| `average_price` | number | Avg selling price |
| `average_price_trend` | number | Price trend % |
| `average_reviews` | number | Avg review count |

### Use Case
- Market size (total_revenue)
- Market growth trend (total_revenue_trend)
- Market scale (total_asins, total_brands)

---

## 2. Jungle Scout Sales Estimates

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/sales_estimates_query
```

### Request
```json
{
  "asin": "B0XXXXXXXX",
  "marketplace": "us",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asin` | string | Yes | Product ASIN |
| `marketplace` | string | Yes | `us`, `uk`, etc. |
| `start_date` | string | Yes | YYYY-MM-DD |
| `end_date` | string | Yes | YYYY-MM-DD |

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Product ASIN |
| `date` | string | Data date |
| `estimated_units_sold` | number | Daily unit sales |
| `last_known_price` | number | Price on that date |
| `is_parent` | boolean | Is parent ASIN |
| `is_variant` | boolean | Is variant |

### Use Case
- Calculate MoM/YoY growth for top ASINs
- Track daily sales trends
- Price trend analysis

### Example Request
```bash
curl -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/sales_estimates_query" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"asin":"B0XXXXXXXX","marketplace":"us","start_date":"2025-04-01","end_date":"2026-04-01"}'
```

---

## 3. Jungle Scout Product Database

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query
```

### Request Body
```json
{
  "data": {
    "type": "product_database_query",
    "attributes": {
      "include_keywords": ["KEYWORD"],
      "min_price": 10,
      "max_price": 100,
      "min_revenue": 300
    }
  }
}
```

### Key Response Fields

| Field | Description |
|-------|-------------|
| `price` | Product price |
| `approximate_30_day_revenue` | Monthly revenue |
| `approximate_30_day_units` | Monthly units |
| `reviews` | Review count |
| `rating` | Average rating |
| `brand` | Brand name |
| `seller_type` | AMZ/FBA/FBM |

### Use Case
- Price segment analysis
- Brand revenue calculation
- Competition assessment

---

## 4. Jungle Scout Share of Voice

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/share-of-voice
```

### Request
```json
{
  "keyword": "KEYWORD",
  "marketplace": "us"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keyword` | string | Yes | Search keyword |
| `marketplace` | string | Yes | `us`, `uk`, etc. |

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `estimated_30_day_search_volume` | number | Monthly searches |
| `brands` | array | Brand share data |
| `brands[].name` | string | Brand name |
| `brands[].share` | number | Organic share % |
| `brands[].sponsored_share` | number | Sponsored share % |
| `top_asins` | array | Top performing ASINs |

### Use Case
- Brand market share
- Keyword competition analysis
- Organic vs sponsored split

---

## 5. ABA (Amazon Brand Analytics)

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/aba/intelligentQuery
```

### Headers
```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

### Request Body
```json
{
  "analysisDescription": "Filter US marketplace, keyword [KEYWORD] search popularity ranking over the past 12 weeks, and Top 3 ASIN click share and conversion share",
  "region": "US",
  "createDownloadUrl": false
}
```

### Key Response Fields

| Field | Description |
|-------|-------------|
| `searchTerm` | Search keyword |
| `searchFrequencyRank` | Popularity rank (lower = better) |
| `clickedAsin` | ASIN that received clicks |
| `clickShare` | Click share (0-1) |
| `conversionShare` | Conversion share (0-1) |
| `reportStartDate` | Week start date |

### Use Case
- Search trend analysis (3 years weekly)
- Market share (click/conversion)
- Competitive landscape (top ASINs)

### Example Queries

**Market Trend:**
```json
{
  "analysisDescription": "Filter US marketplace, keyword 'yoga mat' search popularity ranking trend over the past 52 weeks",
  "region": "US"
}
```

**Market Share:**
```json
{
  "analysisDescription": "Filter US marketplace, keyword 'yoga mat' Top 10 ASIN click share and conversion share over the last 4 weeks",
  "region": "US"
}
```

**Seasonality:**
```json
{
  "analysisDescription": "Filter US marketplace, keyword 'yoga mat' monthly average search ranking over the past 2 years, for seasonality analysis",
  "region": "US"
}
```

---

## 6. Keepa Product History

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productSeries
```

### Request Body
```json
{
  "asin": "B0XXXXXXXX",
  "domain": "1",
  "days": 365,
  "showBsrMain": 1,
  "showSellerCount": 1,
  "showPrice": 1
}
```

### Domain Mapping

| ID | Marketplace |
|----|-------------|
| 1 | amazon.com (US) |
| 2 | amazon.co.uk |
| 3 | amazon.de |

### Key Response Fields

| Field | Description |
|-------|-------------|
| `bsrMain[].points` | BSR time series |
| `price[]` | Price time series |
| `sellerCount[]` | Seller count time series |
| `monthlySold[]` | Monthly sales |

### Use Case
- Price trend analysis
- Sales trend (via BSR)
- Competition dynamics (seller count)

---

## 7. Keepa Product Detail

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productRequest
```

### Request Body
```json
{
  "asin": "B0XXX,B0YYY,B0ZZZ",
  "domain": "1",
  "history": 1
}
```

### Key Response Fields

| Field | Description |
|-------|-------------|
| `listedSince` | Listing date (Unix timestamp) |
| `monthlySales` | Current monthly sales |
| `monthlySalesHistory` | 12-month sales array |
| `packageWeight` | Weight (grams) |

### Use Case
- Seasonality (12-month sales)
- Market maturity (listing dates)

---

## Complete Data Collection Script

```bash
#!/bin/bash
KEYWORD="$1"
API_KEY="$NEXSCOPE_API_KEY"
# (use NEXSCOPE_API_KEY instead)
# (use NEXSCOPE_API_KEY instead)

echo "=== Market Overview Data Collection: $KEYWORD ==="

# 1. JS Product DB (get products + top ASINs)
echo "1/7 JS Product DB..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"data\":{\"type\":\"product_database_query\",\"attributes\":{\"include_keywords\":[\"$KEYWORD\"],\"min_price\":10,\"max_price\":100,\"min_revenue\":300}}}" \
  > /tmp/mo_products.json

# Extract top ASINs
TOP_ASINS=$(cat /tmp/mo_products.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
asins = [p['attributes'].get('asin','') for p in d.get('data',[])[:10] if p['attributes'].get('asin')]
print(','.join(asins))
")
TOP_ASIN=$(echo $TOP_ASINS | cut -d',' -f1)
echo "Top ASINs: $TOP_ASINS"

# 2. JS Sales Estimates (1 year for top ASIN)
echo "2/7 JS Sales Estimates..."
START_DATE=$(date -d '1 year ago' +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/sales_estimates_query" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"asin\":\"$TOP_ASIN\",\"marketplace\":\"us\",\"start_date\":\"$START_DATE\",\"end_date\":\"$END_DATE\"}" \
  > /tmp/mo_sales.json

# 3. JS Share of Voice
echo "3/7 JS Share of Voice..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/share-of-voice" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"keyword\":\"$KEYWORD\",\"marketplace\":\"us\"}" \
  > /tmp/mo_sov.json

# 4. ABA Search Trends
echo "4/7 ABA Search Trends..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/aba/intelligentQuery" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"analysisDescription\":\"Filter US marketplace, keyword '$KEYWORD' search popularity ranking over the past 52 weeks, and weekly Top 3 ASIN click share\",\"region\":\"US\"}" \
  > /tmp/mo_aba.json

# 5. Keepa History (top ASIN)
echo "5/7 Keepa History..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productSeries" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"asin\":\"$TOP_ASIN\",\"domain\":\"1\",\"days\":365,\"showBsrMain\":1,\"showSellerCount\":1,\"showPrice\":1}" \
  > /tmp/mo_keepa_hist.json

# 6. Keepa Detail (batch)
echo "6/7 Keepa Detail..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productRequest" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"asin\":\"$TOP_ASINS\",\"domain\":\"1\",\"history\":1}" \
  > /tmp/mo_keepa_detail.json

# 7. JS Historical (seasonality)
echo "7/7 JS Historical..."
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"marketplace\":\"us\",\"keyword\":\"$KEYWORD\",\"start_date\":\"$START_DATE\",\"end_date\":\"$END_DATE\"}" \
  > /tmp/mo_hist.json

echo "=== Data collection complete ==="
```

---

## Rate Limits

| API | Limit |
|-----|-------|
| Jungle Scout | 100 req/min |
| Data Provider | Check headers |
| ABA | May be slower (complex queries) |

## Error Handling

| Status | Action |
|--------|--------|
| 200 | Success |
| 401 | Check API key |
| 429 | Rate limited, wait and retry |
| Empty data | Try broader keyword |
