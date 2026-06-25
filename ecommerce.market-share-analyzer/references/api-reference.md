# API Reference — Market Share Analyzer v1.2

## Primary: Jungle Scout Share of Voice

### Endpoint

```
POST {NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/share-of-voice
```

### Headers

```
Authorization: Bearer {NEXSCOPE_API_KEY}
Content-Type: application/json
```

### Request

```json
{
  "keyword": "yoga mat",
  "marketplace": "us"
}
```

### Parameters

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `keyword` | string | Yes | Search keyword |
| `marketplace` | string | Yes | `us`, `uk`, `de`, `fr`, `it`, `es`, `ca`, `mx`, `jp` |

### Response Structure

```json
{
  "data": {
    "id": "us/yoga mat",
    "type": "share_of_voice",
    "attributes": {
      "estimated_30_day_search_volume": 1151842,
      "exact_suggested_bid_median": 0.0,
      "product_count": 154,
      "updated_at": "2026-04-07T11:04:15Z",
      "brands": [...],
      "top_asins": [...]
    }
  }
}
```

### Brand Object

```json
{
  "brand": "Amazon Basics",
  "combined_products": 1,
  "combined_weighted_sov": 0.2454,
  "combined_basic_sov": 0.0065,
  "combined_average_position": 1,
  "combined_average_price": 21.58,
  "organic_products": 1,
  "organic_weighted_sov": 0.2454,
  "organic_basic_sov": 0.0069,
  "organic_average_position": 1,
  "organic_average_price": 21.58,
  "sponsored_products": 0,
  "sponsored_weighted_sov": 0,
  "sponsored_basic_sov": 0,
  "sponsored_average_position": null,
  "sponsored_average_price": null
}
```

| Field | Description |
|-------|-------------|
| `combined_weighted_sov` | Total weighted share of voice (0-1) |
| `organic_weighted_sov` | Organic (non-ad) share |
| `sponsored_weighted_sov` | Sponsored (ad) share |
| `combined_average_position` | Average search result position |
| `combined_average_price` | Average product price |
| `organic_products` | Number of organic listings |
| `sponsored_products` | Number of sponsored listings |

### Top ASIN Object

```json
{
  "asin": "B01LP0U5X0",
  "name": "Amazon Basics 1/2 Inch Extra Thick Exercise Yoga Mat...",
  "brand": "Amazon Basics",
  "clicks": 12395,
  "conversions": 282,
  "conversion_rate": 0.02
}
```

### Cost

~1 token per call

---

## Amazon Search (via NexScope Proxy)

### Endpoint

```
POST {API_BASE}/amazon/search
```

### Request

```json
{
  "keyword": "yoga mat",
  "marketplace": "US",
  "limit": 50
}
```

### Response

```json
{
  "products": [
    {
      "asin": "B01LP0U5X0",
      "title": "Amazon Basics Yoga Mat...",
      "brand": "Amazon Basics",
      "price": 21.58,
      "reviews": 12500,
      "rating": 4.5
    }
  ]
}
```

---

## Fallback: Keepa Product Request

### Endpoint

```
POST {API_BASE}/keepa/productRequest
```

### Request

```json
{
  "asin": "B01LP0U5X0",
  "domain": 1
}
```

### Response

```json
{
  "asin": "B01LP0U5X0",
  "brand": "Amazon Basics",
  "monthlySold": 5000,
  "reviewCount": 12500,
  "buyBoxPrice": 2158,
  "availableSince": "2020-01-15"
}
```

### Domain Codes

| Market | Domain |
|--------|--------|
| US | 1 |
| UK | 2 |
| DE | 3 |
| FR | 4 |
| JP | 5 |
| CA | 6 |
| IT | 8 |
| ES | 9 |
| MX | 11 |

---

## Environment Variables

```bash
# Jungle Scout (Primary)
export NEXSCOPE_API_KEY="nk-xxx"

# NexScope Proxy (required — must be set before running)
# export NEXSCOPE_PROXY_BASE="<provided by ops>"
export NEXSCOPE_API_KEY="nk-xxx"
```

---

## Error Handling

### JS SOV API Errors

| Code | Meaning | Action |
|------|---------|--------|
| 403 | Invalid API key | Check NEXSCOPE_API_KEY is set correctly |
| 404 | Keyword not found | Use NexScope Proxy |
| 429 | Rate limited | Wait and retry |

### Fallback Trigger

Script automatically uses NexScope Proxy + Keepa when:
- JS SOV API returns error
- JS SOV response has no brands
- Network timeout

```python
sov_data = get_share_of_voice(keyword, market)

if sov_data and sov_data.get('brands'):
    return analyze_with_sov(keyword, market, sov_data)
else:
    return analyze_with_search(keyword, market, limit)
```
