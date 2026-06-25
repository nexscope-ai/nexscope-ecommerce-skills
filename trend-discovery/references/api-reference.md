# API Reference — Trend Discovery v2.0

## Data Sources

| Source | Purpose | Endpoint |
|--------|---------|----------|
| Google Trends | Search interest over time | `/googleTrend/getTrendByKeys` |
| TikTok Echotik | Social commerce sales | `/echotik/listProduct` |
| Amazon Search | E-commerce competition | `/amazon/search` |
| Jungle Scout | Sales estimates | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/*` |

---

## 1. Google Trends

**Endpoint:** `POST /googleTrend/getTrendByKeys`

**Request:**
```json
{
  "keyword": "keyword1,keyword2",
  "region": "US",
  "startDate": "2026-03-01",
  "endDate": "2026-04-01"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"date": "2026-03-01", "value": 45},
    {"date": "2026-03-08", "value": 52}
  ]
}
```

**Use Cases:**
- Compare multiple keywords
- Detect trend direction
- Seasonal pattern analysis

---

## 2. TikTok Echotik

**Endpoint:** `POST /echotik/listProduct`

**Request:**
```json
{
  "keyword": "search term",
  "region": "US",
  "minTotalSale30dCnt": 1000,
  "productSortField": 5,
  "pageSize": 50
}
```

**Sort Fields:**
| Value | Sort By |
|-------|---------|
| 5 | Total sales (30d) |
| 6 | Sales growth |
| 7 | Revenue |

**Key Response Fields:**
- `totalSale30dCnt` — 30-day unit sales
- `totalSaleAmt` — Total revenue
- `productTitle` — Product name
- `shopName` — Seller name
- `avgScore` — Rating

---

## 3. Amazon Search

**Endpoint:** `POST /amazon/search`

**Request:**
```json
{
  "keyword": "search term",
  "amazonDomain": "amazon.com",
  "page": 1
}
```

**Key Response Fields:**
- `products[].title`
- `products[].price`
- `products[].rating`
- `products[].reviews`
- `products[].sponsored` — Ad indicator

---

## 4. Jungle Scout Keywords

**Endpoint:** `POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/keywords_by_keyword_query`

**Request:**
```json
{
  "data": {
    "type": "keywords_by_keyword_query",
    "attributes": {
      "search_terms": "keyword",
      "marketplace": "us"
    }
  }
}
```

**Key Response Fields:**
- `monthly_search_volume_exact`
- `monthly_trend`
- `dominant_category`
