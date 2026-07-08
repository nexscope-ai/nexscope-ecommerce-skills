# API Reference — Product Opportunity Finder v1.3

## Data Sources Overview

| # | Source | Provider | Endpoint | Purpose |
|---|--------|----------|----------|---------|
| 1 | Jungle Scout Product DB | JS | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query` | Product discovery |
| 2 | Jungle Scout Historical | JS | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume` | Seasonality |
| 3 | Keepa Detail | Data Provider | `/keepa/productRequest` | Listing age, sellers |
| 4 | Keepa History | Data Provider | `/keepa/productSeries` | BSR/price trends |
| 5 | Amazon Search | Data Provider | `/amazon/search` | Brand dominance |
| 6 | **eBay Search** | Data Provider | `/ebay/search` | Cross-platform pricing |
| 7 | **Walmart Search** | Data Provider | `/walmart/search` | Cross-platform validation |
| 8 | ABA | Data Provider | `/aba/intelligentQuery` | Search trends |
| 9 | Google Trends | Data Provider | `/googleTrend/getTrendByKeys` | Trend direction |

## Data Collection Flow

```
Phase 1: Multi-Platform Discovery
┌─────────────────────────────────────────────────────────────┐
│  Amazon Search    ──→  Products, brands, prices             │
│  eBay Search      ──→  Sold items, market pricing           │
│  Walmart Search   ──→  Cross-platform validation            │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase 2: Deep Analysis (Top Candidates)
┌─────────────────────────────────────────────────────────────┐
│  Jungle Scout     ──→  Revenue, reviews, fees               │
│  Keepa Detail     ──→  Listing age, weight, sellers         │
│  Keepa History    ──→  BSR/price/seller trends              │
└─────────────────────────────────────────────────────────────┘
                              ↓
Phase 3: Trend Validation
┌─────────────────────────────────────────────────────────────┐
│  JS Historical    ──→  12-month seasonality                 │
│  ABA              ──→  Search rank trends                   │
│  Google Trends    ──→  Interest over time                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Jungle Scout Product Database

**Primary data source for product discovery.**

**Endpoint:** `POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/product_database_query`

**Request:**
```json
{
  "data": {
    "type": "product_database_query",
    "attributes": {
      "include_keywords": ["keyword"],
      "exclude_keywords": ["case", "accessory", "replacement"],
      "min_revenue": 5000,
      "max_revenue": 100000,
      "min_price": 15,
      "max_price": 50,
      "min_reviews": 0,
      "max_reviews": 500,
      "min_rating": 3.5,
      "seller_type": "FBA"
    }
  }
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `asin` | Product identifier | Lookup key |
| `title` | Product title | Display |
| `brand` | Brand name | Brand analysis |
| `price` | Current price | Margin calculation |
| `approximate_30_day_revenue` | Monthly revenue | Demand score |
| `approximate_30_day_units` | Monthly units | Volume |
| `reviews` | Review count | Competition score |
| `rating` | Average rating | Quality gap analysis |
| `seller_type` | AMZ/FBA/FBM | Exclude Amazon |
| `fees` | FBA fees | Margin calculation |

---

## 2. Keepa Product Detail (Batch)

**Get detailed info for multiple products at once.**

**Endpoint:** `POST /keepa/productRequest`

**Request:**
```json
{
  "asin": "B0XXX,B0YYY,B0ZZZ",
  "domain": "1",
  "history": 1
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `listedSince` | First available date | Market maturity |
| `packageWeight` | Shipping weight | Logistics score |
| `monthlySalesHistory` | 12-month sales | Seasonality |
| `numberOfSellers` | Current seller count | Competition |
| `buyBoxSellerIdHistory` | Buy box history | Seller stability |

---

## 3. Keepa Product History

**Get trend data for individual products.**

**Endpoint:** `POST /keepa/productSeries`

**Request:**
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

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `bsrMain` | BSR history | Trend direction |
| `sellerCount` | Seller count over time | Competition trend |
| `price` | Price history | Price stability |

**Trend Calculation:**
```python
def calculate_trend(history_array, days=90):
    if len(history_array) < 10:
        return 'unknown'
    
    recent = history_array[-30:]  # Last 30 days
    earlier = history_array[-90:-60]  # 60-90 days ago
    
    recent_avg = sum(recent) / len(recent)
    earlier_avg = sum(earlier) / len(earlier)
    
    change = (recent_avg - earlier_avg) / earlier_avg * 100
    
    if change < -20:  # BSR decreasing = sales increasing
        return 'improving'
    elif change > 20:
        return 'declining'
    else:
        return 'stable'
```

---

## 4. Amazon Search

**Check brand dominance and ad presence.**

**Endpoint:** `POST /amazon/search`

**Request:**
```json
{
  "keyword": "search term",
  "amazonDomain": "amazon.com",
  "page": 1
}
```

**Analysis:**
```python
def analyze_search_results(products):
    known_brands = load_known_brands()
    
    brand_count = sum(1 for p in products[:10] 
                      if is_known_brand(p['brand'], known_brands))
    
    ad_count = sum(1 for p in products[:10] if p.get('sponsored'))
    
    return {
        'known_brand_pct': brand_count / 10 * 100,
        'ad_saturation': ad_count / 10 * 100
    }
```

---

## 5. ABA Search Trends

**Analyze search rank trends.**

**Endpoint:** `POST /aba/intelligentQuery`

**Request:**
```json
{
  "analysisDescription": "Get search frequency rank trend for [keyword] over past 12 weeks",
  "region": "US"
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `searchFrequencyRank` | Search popularity rank | Demand trend |
| `clickShare` | Click distribution | Market concentration |
| `conversionShare` | Conversion by ASIN | Top performers |

---

## API Call Sequence

### For 50 Product Candidates

```
1. Jungle Scout Query (1 call)
   → Returns 50 products with basic metrics
   
2. Keepa Batch Detail (1 call, 50 ASINs)
   → Add listing age, weight, seller count
   
3. Filter to Top 20 candidates

4. Keepa History (20 calls or batch)
   → Add trend data for top candidates
   
5. Amazon Search (1 call)
   → Brand dominance check
   
6. ABA Query (1 call)
   → Search trend confirmation
```

**Total API calls:** ~25 for a full analysis

---

## 6. eBay Search (Sold Items)

**Cross-platform pricing and demand validation.**

**Endpoint:** `POST /ebay/search`

**Request:**
```json
{
  "keyword": "stainless steel lunch box",
  "ebayDomain": "ebay.com",
  "pageSize": 50,
  "showOnly": "Sold"
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `products[].title` | Product title | Data cleaning |
| `products[].price` | Sold price | Market pricing |
| `products[].soldDate` | When sold | Demand validation |
| `products[].condition` | New/Used | Filter to new |

**Analysis:**
```python
def analyze_ebay_sold(products):
    prices = [p['price'] for p in products if p.get('condition') == 'New']
    return {
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'price_range': (min(prices), max(prices)) if prices else (0, 0),
        'sold_count': len(products)
    }
```

---

## 7. Walmart Search

**Cross-platform validation and competition check.**

**Endpoint:** `POST /walmart/search`

**Request:**
```json
{
  "keyword": "stainless steel lunch box",
  "sort": "best_seller"
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `products[].title` | Product title | Data cleaning |
| `products[].price` | Current price | Cross-platform comparison |
| `products[].rating` | Average rating | Quality benchmark |
| `products[].reviews` | Review count | Competition level |
| `products[].seller` | Seller name | Brand analysis |

**Analysis:**
```python
def analyze_walmart(products):
    prices = [p['price'] for p in products if p.get('price')]
    return {
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'product_count': len(products),
        'vs_amazon': 'cheaper' if avg < amazon_avg else 'pricier'
    }
```

---

## 8. Jungle Scout Historical Search Volume

**12-month seasonality analysis.**

**Endpoint:** `POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume`

**Request:**
```json
{
  "marketplace": "us",
  "keyword": "KEYWORD",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

**Response Example:**
```json
{
  "data": [
    {
      "attributes": {
        "estimate_start_date": "2025-04-06",
        "estimate_end_date": "2025-04-12",
        "estimated_exact_search_volume": 6561
      }
    }
  ]
}
```

**Seasonality Calculation:**
```python
def calculate_seasonality(weekly_data):
    # Group by month
    monthly = {}
    for week in weekly_data:
        month = week['start_date'][:7]
        if month not in monthly:
            monthly[month] = []
        monthly[month].append(week['volume'])
    
    monthly_avg = {m: sum(v)/len(v) for m, v in monthly.items()}
    
    peak = max(monthly_avg.values())
    trough = min(monthly_avg.values())
    
    return {
        'seasonality_index': peak / trough if trough > 0 else 1,
        'peak_months': [m for m, v in monthly_avg.items() if v > peak * 0.8],
        'pattern': classify_pattern(monthly_avg)
    }

def classify_pattern(monthly):
    summer = avg([monthly.get(f'2025-0{m}', 0) for m in [6,7,8]])
    winter = avg([monthly.get(f'2025-{m}', 0) for m in ['11','12','01']])
    overall = avg(monthly.values())
    
    if summer > overall * 1.3 and winter > overall * 1.3:
        return "Double Peak"
    elif summer > overall * 1.3:
        return "Summer Peak"
    elif winter > overall * 1.3:
        return "Winter Peak"
    else:
        return "Year-round"
```

---

## 9. Google Trends

**Trend direction confirmation.**

**Endpoint:** `POST /googleTrend/getTrendByKeys`

**Request:**
```json
{
  "keyword": "stainless steel lunch box",
  "startDate": "2025-04-01",
  "endDate": "2026-04-01",
  "region": "US"
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `trendValues[].value` | Interest (0-100) | Trend direction |
| `trendValues[].timeRange` | Date | Time series |

**Trend Analysis:**
```python
def analyze_google_trends(values):
    early = avg([int(v['value']) for v in values[:10] if v['value'] != '0'])
    recent = avg([int(v['value']) for v in values[-10:] if v['value'] != '0'])
    
    change = (recent - early) / early * 100 if early > 0 else 0
    
    return {
        'trend_change': change,
        'direction': 'rising' if change > 10 else 'declining' if change < -10 else 'stable',
        'avg_interest': avg([int(v['value']) for v in values if v['value'] != '0'])
    }
```

---

## Cross-Platform Comparison

**Compare pricing and competition across platforms.**

```python
def cross_platform_analysis(amazon, ebay, walmart):
    return {
        'platforms': {
            'Amazon': {
                'products': len(amazon),
                'avg_price': avg_price(amazon),
                'known_brands': known_brand_pct(amazon)
            },
            'eBay': {
                'products': len(ebay),
                'avg_price': avg_price(ebay),
                'note': 'Sold items = proven demand'
            },
            'Walmart': {
                'products': len(walmart),
                'avg_price': avg_price(walmart),
                'known_brands': known_brand_pct(walmart)
            }
        },
        'insights': {
            'price_leader': min_by_price([amazon, ebay, walmart]),
            'most_products': max_by_count([amazon, ebay, walmart]),
            'arbitrage': find_arbitrage_opportunities(amazon, ebay, walmart)
        }
    }
```

---

## API Call Sequence (Full Analysis)

```
Phase 1: Multi-Platform Discovery (~3 calls)
├── Amazon Search      → 60 products
├── eBay Search        → 60 sold items
└── Walmart Search     → 40 products

Phase 2: Deep Analysis (~5 calls)
├── Jungle Scout       → Revenue/reviews for filtered products
├── Keepa Detail       → Batch 50 ASINs
└── Keepa History      → Top 10 candidates

Phase 3: Trend Validation (~3 calls)
├── JS Historical      → 12-month seasonality
├── ABA               → Search rank trend
└── Google Trends     → Interest validation

Total: ~11 API calls for full analysis
```

---

## Rate Limits

| API | Limit | Strategy |
|-----|-------|----------|
| Jungle Scout | 100/min | Batch queries |
| Keepa | 50/min | Use batch endpoint |
| Amazon Search | 30/min | Cache results |
| eBay Search | 30/min | Single query |
| Walmart Search | 30/min | Single query |
| ABA | 20/min | Single query |
| Google Trends | 20/min | Single query |
