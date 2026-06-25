# API Reference v3.0

## Data Sources Overview

| # | Source | Provider | Endpoint | Purpose |
|---|--------|----------|----------|---------|
| 1 | Product DB | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query` | Sales, reviews, fees |
| 2 | Historical | Jungle Scout | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume` | Seasonality |
| 3 | Google Trends | Data Provider | `/googleTrend/getTrendByKeys` | Trend direction |
| 4 | Amazon Search | Data Provider | `/amazon/search` | Ads, brand dominance |
| 5 | TikTok | Data Provider | `/echotik/listProduct` | Social commerce |
| 6 | Keepa History | Data Provider | `/keepa/productSeries` | BSR/price/seller trends |
| 7 | Keepa Detail | Data Provider | `/keepa/productRequest` | Batch product details |
| 8 | Amazon Detail | Data Provider | `/amazon/product/detail` | Product info + top reviews |

---

## 1. Jungle Scout Product Database

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query
```

### Headers
```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

### Request
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

| Field | Purpose |
|-------|---------|
| `price` | Product price |
| `approximate_30_day_revenue` | Monthly revenue |
| `approximate_30_day_units` | Monthly units sold |
| `reviews` | Review count |
| `rating` | Average rating |
| `fee_breakdown.total_fees` | FBA fees |
| `seller_type` | AMZ = Amazon seller |
| `brand` | Brand name |
| `date_first_available` | Listing date |

---

## 2. Jungle Scout Historical Search Volume

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume
```

### Request
```json
{
  "marketplace": "us",
  "keyword": "KEYWORD",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `estimated_30_day_search_volume` | Monthly search volume |
| `attributes.data[].estimate` | Monthly data points |

### Seasonality Calculation
```python
peak = max(monthly_volumes)
trough = min(monthly_volumes)
seasonality_index = peak / trough
```

---

## 3. Google Trends

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/googleTrend/getTrendByKeys
```

### Headers
```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

### Request
```json
{
  "keyword": "KEYWORD",
  "startDate": "2026-03-01",
  "endDate": "2026-04-01",
  "region": "US"
}
```

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `timeline_data[].value` | Interest value (0-100) |

### Trend Calculation
```python
early = avg(values[:10])
recent = avg(values[-10:])
trend_change = (recent - early) / early * 100
```

---

## 4. Amazon Search

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/search
```

### Request
```json
{
  "keyword": "KEYWORD",
  "amazonDomain": "amazon.com",
  "page": 1
}
```

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `products[].asin` | Product ASIN |
| `products[].title` | Product title |
| `products[].brand` | Brand name |
| `products[].isSponsored` | Is sponsored ad |
| `products[].position` | Search position |

### Derived Metrics
```python
sponsored_pct = count(isSponsored=True) / total * 100
known_brand_pct = count(brand in KNOWN_BRANDS) / total * 100
```

---

## 5. TikTok Echotik

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/echotik/listProduct
```

### Request
```json
{
  "keyword": "KEYWORD",
  "region": "US",
  "minTotalSale30dCnt": 50,
  "productSortField": 5,
  "pageSize": 30
}
```

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `products[].title` | Product title |
| `products[].totalSale30dCnt` | 30-day sales count |
| `products[].price` | Price |

---

## 6. Keepa Product History (v3.0)

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productSeries
```

### Request
```json
{
  "asin": "B0XXXXXXXX",
  "domain": "1",
  "days": 90,
  "showBsrMain": 1,
  "showSellerCount": 1,
  "showPrice": 1
}
```

### Domain Mapping

| ID | Marketplace |
|----|-------------|
| 1 | amazon.com (US) |
| 2 | amazon.co.uk (UK) |
| 3 | amazon.de (Germany) |
| 4 | amazon.fr (France) |
| 5 | amazon.co.jp (Japan) |
| 6 | amazon.ca (Canada) |

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `bsrMain[].points` | BSR time series |
| `price[]` | Price time series |
| `sellerCount[]` | Seller count time series |
| `rating[]` | Rating time series |
| `monthlySold[]` | Monthly sales |

### Trend Analysis
```python
def analyze_trend(data_points, days=90):
    early = avg(points[:days//3])
    recent = avg(points[-days//3:])
    change_pct = (recent - early) / early * 100
    return change_pct
```

---

## 7. Keepa Product Detail (v3.0)

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productRequest
```

### Request
```json
{
  "asin": "B0XXX,B0YYY,B0ZZZ",
  "domain": "1",
  "history": 1
}
```

**Note:** Supports batch query up to 100 ASINs (comma-separated)

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `products[].title` | Product title |
| `products[].listedSince` | Listing date (Unix timestamp) |
| `products[].packageWeight` | Weight in grams |
| `products[].packageLength` | Length in mm |
| `products[].packageWidth` | Width in mm |
| `products[].packageHeight` | Height in mm |
| `products[].monthlySales` | Current monthly sales |
| `products[].monthlySalesHistory` | 12-month sales history |
| `products[].fbaFees` | FBA fees |

### Market Maturity Calculation
```python
def market_maturity(products):
    now = datetime.now()
    ages = []
    for p in products:
        if p.get('listedSince'):
            age_days = (now - datetime.fromtimestamp(p['listedSince'])).days
            ages.append(age_days)
    
    new_pct = sum(1 for a in ages if a < 365) / len(ages) * 100
    return new_pct
```

---

## 8. Amazon Product Detail (v3.0)

### Endpoint
```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/product/detail
```

### Request
```json
{
  "asins": "B0XXXXXXXX",
  "amazonDomain": "amazon.com",
  "returnAuthorsReviews": true
}
```

### Key Response Fields

| Field | Purpose |
|-------|---------|
| `products[].title` | Product title |
| `products[].bulletPoints` | Bullet points |
| `products[].aPlusContent` | A+ content |
| `products[].ratingsDistribution` | Rating breakdown (1-5 stars) |
| `products[].topReviews` | Top reviews |
| `products[].variantCount` | Number of variants |

### Pain Point Detection
```python
def detect_pain_points(detail):
    dist = detail.get('ratingsDistribution', {})
    total = sum(dist.values())
    low_rating_pct = (dist.get('1', 0) + dist.get('2', 0)) / total * 100
    
    if low_rating_pct > 20:
        return +4, "High pain point signal"
    elif low_rating_pct > 10:
        return +2, "Some improvement room"
    elif low_rating_pct < 5:
        return -2, "Mature product, hard to beat"
    return 0, "Normal"
```

---

## Complete Collection Script

```bash
#!/bin/bash
KEYWORD="$1"
API_KEY="$NEXSCOPE_API_KEY"
# (use NEXSCOPE_API_KEY instead)
# (use NEXSCOPE_API_KEY instead)

# 1. Jungle Scout Product DB
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"data\":{\"type\":\"product_database_query\",\"attributes\":{\"include_keywords\":[\"$KEYWORD\"],\"min_price\":10,\"max_price\":100,\"min_revenue\":300}}}" \
  > /tmp/js_products.json

# 2. Google Trends
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/googleTrend/getTrendByKeys" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"keyword\":\"$KEYWORD\",\"startDate\":\"$(date -d '30 days ago' +%Y-%m-%d)\",\"endDate\":\"$(date +%Y-%m-%d)\",\"region\":\"US\"}" \
  > /tmp/trends.json

# 3. Amazon Search
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/search" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"keyword\":\"$KEYWORD\",\"amazonDomain\":\"amazon.com\",\"page\":1}" \
  > /tmp/amz_search.json

# 4. TikTok
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/echotik/listProduct" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"keyword\":\"$KEYWORD\",\"region\":\"US\",\"minTotalSale30dCnt\":50,\"pageSize\":30}" \
  > /tmp/tiktok.json

# 5. JS Historical (Seasonality)
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"marketplace\":\"us\",\"keyword\":\"$KEYWORD\",\"start_date\":\"$(date -d '1 year ago' +%Y-%m-%d)\",\"end_date\":\"$(date +%Y-%m-%d)\"}" \
  > /tmp/js_hist.json

# Get top ASIN from Amazon Search
TOP_ASIN=$(cat /tmp/amz_search.json | python3 -c "import sys,json; print(json.load(sys.stdin).get('products',[{}])[0].get('asin',''))")
TOP_5_ASINS=$(cat /tmp/amz_search.json | python3 -c "import sys,json; print(','.join([p.get('asin','') for p in json.load(sys.stdin).get('products',[])[:5] if p.get('asin')]))")

# 6. Keepa History (top ASIN)
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productSeries" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"asin\":\"$TOP_ASIN\",\"domain\":\"1\",\"days\":90,\"showBsrMain\":1,\"showSellerCount\":1,\"showPrice\":1}" \
  > /tmp/keepa_hist.json

# 7. Keepa Detail (batch)
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productRequest" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"asin\":\"$TOP_5_ASINS\",\"domain\":\"1\",\"history\":1}" \
  > /tmp/keepa_detail.json

# 8. Amazon Detail (top ASIN with reviews)
curl -s -X POST "{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/product/detail" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" -H "Content-Type: application/json" \
  -d "{\"asins\":\"$TOP_ASIN\",\"amazonDomain\":\"amazon.com\",\"returnAuthorsReviews\":true}" \
  > /tmp/amz_detail.json

echo "Data collection complete"
```

---

## Rate Limits

| API | Limit |
|-----|-------|
| Jungle Scout | 100 req/min |
| Data Provider | Check response headers |

## Error Handling

| Status | Action |
|--------|--------|
| 200 | Success |
| 401 | Check API key |
| 429 | Rate limited, wait and retry |
| Empty data | Try broader keyword |
