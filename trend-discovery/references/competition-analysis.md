# Competition Analysis — Trend Discovery v2.0

## Competition Scoring

### Amazon Competition

Based on average review count of top 10 results:

```python
def amazon_competition(avg_reviews):
    if avg_reviews > 20000:
        return '🔴 High'
    elif avg_reviews > 5000:
        return '🟡 Medium'
    else:
        return '🟢 Low'
```

### TikTok Competition

Based on sales volume and review count:

```python
def tiktok_competition(avg_reviews, total_sales):
    if avg_reviews > 20000 or total_sales > 500000:
        return '🔴 High'
    elif avg_reviews > 5000 or total_sales > 100000:
        return '🟡 Medium'
    else:
        return '🟢 Low'
```

## Arbitrage Detection

Compare competition levels across platforms:

| TikTok | Amazon | Opportunity |
|--------|--------|-------------|
| 🔴 High | 🟢 Low | TikTok → Amazon |
| 🟢 Low | 🔴 High | Amazon → TikTok |
| 🟢 Low | 🟢 Low | 🔥 Blue ocean |
| 🔴 High | 🔴 High | ⚠️ Saturated |
