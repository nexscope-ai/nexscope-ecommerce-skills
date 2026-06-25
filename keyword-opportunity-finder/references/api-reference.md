# API Reference — Keyword Opportunity Finder v1.2

## Data Sources Overview

| # | Source | Endpoint | Purpose | Priority |
|---|--------|----------|---------|----------|
| 1 | JS Keyword Research | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/keywords_by_keyword_query` | Related keywords, volume, PPC | Primary |
| 2 | JS Historical | `{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume` | Seasonality, 30-day surge | Primary |
| 3 | ABA | `/aba/intelligentQuery` | Search rank, click/conv share | Primary |
| 4 | Amazon Search | `/amazon/search` | Competition analysis | Primary |
| 5 | Web Search | Brave API | Social Signal detection | Primary |
| 6 | Google Trends | `/googleTrend/getTrendByKeys` | Trend validation | Backup |

---

## 1. Jungle Scout Keyword Research

**Primary source for keyword discovery.**

**Endpoint:** `POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/keywords_by_keyword_query`

**Headers:**
```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

**Request:**
```json
{
  "data": {
    "type": "keywords_by_keyword_query",
    "attributes": {
      "search_terms": "lunch box",
      "min_monthly_search_volume_exact": 1000
    }
  }
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `name` | Keyword text | Display |
| `monthly_search_volume_exact` | Exact match volume | Volume score |
| `monthly_trend` | Month-over-month change | Trend indicator |
| `relevancy_score` | Relevance to seed | Filtering |
| `organic_product_count` | Number of results | Competition |

---

## 2. Jungle Scout Historical Search Volume

**12-month search volume trend.**

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

**Key Calculations:**
```python
def analyze_historical(weekly_volumes):
    """
    Analyze 12-month historical data for Rising Trend detection
    """
    # 30-day surge (last 4 weeks vs previous 4 weeks)
    last_4 = sum(weekly_volumes[-4:]) / 4
    prev_4 = sum(weekly_volumes[-8:-4]) / 4
    surge_30d = (last_4 - prev_4) / prev_4 * 100 if prev_4 > 0 else 0
    
    # YoY change (last quarter vs first quarter)
    first_q = sum(weekly_volumes[:13]) / 13
    last_q = sum(weekly_volumes[-13:]) / 13
    yoy_change = (last_q - first_q) / first_q * 100 if first_q > 0 else 0
    
    # Seasonality index
    peak = max(weekly_volumes)
    trough = min([v for v in weekly_volumes if v > 0])
    seasonality = peak / trough if trough > 0 else 1
    
    return {
        'surge_30d': surge_30d,      # > 50% = Rising Trend
        'yoy_change': yoy_change,    # > 20% = Growing
        'seasonality': seasonality,   # > 3x = Seasonal
        'peak_volume': peak,
        'current_volume': last_4
    }
```

**Rising Trend Thresholds:**
| Metric | Threshold | Signal |
|--------|-----------|--------|
| surge_30d > 80% | 🔥🔥 Hot | Urgent opportunity |
| surge_30d > 50% | 🔥 Rising | Strong opportunity |
| yoy_change > 20% | 📈 Growing | Sustainable growth |
| seasonality > 3x | 🌊 Seasonal | Time-sensitive |

---

## 3. ABA (Amazon Brand Analytics)

**Search rank and click share data.**

**Endpoint:** `POST /aba/intelligentQuery`

**Request:**
```json
{
  "analysisDescription": "Get search frequency rank and top 3 clicked ASINs for [keyword] in US",
  "region": "US"
}
```

**Key Response Fields:**
| Field | Description | Use |
|-------|-------------|-----|
| `searchFrequencyRank` | Search popularity rank | Demand indicator |
| `clickShare` | % of clicks to top ASINs | Concentration |
| `conversionShare` | % of conversions | Purchase intent |

**Competition Signal:**
- High click concentration (> 50% to top 3) = Dominated market
- Low click concentration (< 30% to top 3) = Fragmented = Opportunity

---

## 4. Amazon Search

**Analyze top 10 results for competition.**

**Endpoint:** `POST /amazon/search`

**Request:**
```json
{
  "keyword": "stainless steel lunch box",
  "amazonDomain": "amazon.com",
  "page": 1
}
```

**Competition Metrics:**
```python
def analyze_serp(results):
    top_10 = results[:10]
    
    return {
        'avg_reviews': avg([p['reviews'] for p in top_10]),
        'min_reviews': min([p['reviews'] for p in top_10]),
        'avg_rating': avg([p['rating'] for p in top_10]),
        'known_brands': count_known_brands(top_10),
        'sponsored_count': count_sponsored(top_10),
        'weak_listings': find_weak_listings(top_10)
    }

def find_weak_listings(products):
    """Find products with weaknesses we can exploit"""
    weak = []
    for p in products:
        weaknesses = []
        if p['rating'] < 4.0:
            weaknesses.append('low_rating')
        if p['reviews'] < 100:
            weaknesses.append('few_reviews')
        if not is_known_brand(p['brand']):
            weaknesses.append('unknown_brand')
        if weaknesses:
            weak.append({'product': p, 'weaknesses': weaknesses})
    return weak
```

---

## 5. Google Trends

**Trend direction validation.**

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

**Trend Analysis:**
```python
def analyze_trend(values):
    non_zero = [int(v['value']) for v in values if v['value'] != '0']
    
    if len(non_zero) < 10:
        return {'direction': 'insufficient_data'}
    
    early = avg(non_zero[:len(non_zero)//3])
    recent = avg(non_zero[-len(non_zero)//3:])
    
    change = (recent - early) / early * 100 if early > 0 else 0
    
    return {
        'change_pct': change,
        'direction': 'rising' if change > 10 else 'declining' if change < -10 else 'stable'
    }
```

---

## API Call Sequence

```
1. JS Keyword Research (1 call)
   → Get 50+ related keywords with volume
   
2. Filter to candidates (no API)
   → Volume > 2,000, relevance > 0.5
   
3. Amazon Search for top 20 (20 calls or cached)
   → Competition analysis
   
4. JS Historical for top 10 (10 calls)
   → Seasonality check
   
5. Google Trends for top 5 (5 calls)
   → Trend validation

Total: ~35 API calls for full analysis
```

---

---

## 6. Web Search (Social Signal Detection)

**Detect TikTok/Reddit buzz for keywords not yet mainstream on Amazon.**

**Search Queries:**
```python
def detect_social_signal(keyword):
    queries = [
        f"{keyword} TikTok viral",
        f"{keyword} Reddit trending",
        f"{keyword} TikTok 2026"
    ]
    
    signals = {
        'has_tiktok': False,
        'has_reddit': False,
        'viral_indicators': []
    }
    
    for query in queries:
        results = web_search(query, count=5)
        
        for result in results:
            url = result.get('url', '')
            desc = result.get('description', '')
            
            # Check TikTok presence
            if 'tiktok.com' in url:
                signals['has_tiktok'] = True
                if '/discover/' in url:
                    signals['viral_indicators'].append('tiktok_discover_page')
            
            # Check Reddit presence
            if 'reddit.com' in url:
                signals['has_reddit'] = True
                if 'SkincareAddiction' in url or 'BuyItForLife' in url:
                    signals['viral_indicators'].append('reddit_popular_sub')
            
            # Check viral hashtags
            viral_tags = ['#tiktokmademebuyit', '#kbeauty', '#viral', '#trending']
            for tag in viral_tags:
                if tag in desc.lower():
                    signals['viral_indicators'].append(tag)
    
    return signals
```

**Social Signal Scoring:**
| Signal | Points | Why |
|--------|--------|-----|
| TikTok discover page exists | +3 | High visibility |
| Reddit popular sub discussion | +2 | Organic demand |
| Viral hashtag mentioned | +1 each | Social proof |
| ABA rank > 50,000 | Required | Amazon hasn't caught up |

**Example Detection:**
```
Keyword: "korean anti aging hand cream"
Web Search: "korean anti aging hand cream TikTok viral"

Results:
- tiktok.com/discover/korean-hand-cream-for-wrinkles ✅ TikTok discover
- "#kbeauty #koreanskincare #viralproducts" ✅ Viral hashtags

Signal: 📱 Social Signal DETECTED
```

---

## Rate Limits

| API | Limit | Strategy |
|-----|-------|----------|
| JS Keyword Research | 100/min | Single query returns many |
| JS Historical | 50/min | Batch by priority |
| Amazon Search | 30/min | Cache results |
| ABA | 20/min | Key keywords only |
| Web Search | 100/min | Social signal detection |
| Google Trends | 20/min | Backup only |
