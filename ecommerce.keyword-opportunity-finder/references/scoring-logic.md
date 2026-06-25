# Scoring Logic — Keyword Opportunity Finder v1.1

## Keyword Opportunity Score

```
Total Score = Volume (35) + Difficulty (30) + Efficiency (20) + Relevance (15)
Max Score = 100
```

| Dimension | Weight | Core Metrics |
|-----------|--------|--------------|
| 📈 Volume | 35 | 12-month avg search volume, recent growth trend |
| ⚔️ Difficulty | 30 | Exact match product count, Top 3 click share, avg reviews |
| 💰 Efficiency | 20 | Avg click-to-conversion rate, PPC bid estimate |
| 🎯 Relevance | 15 | Avg price point, repurchase potential |

---

## 1. Volume Score — 0-35

### Components

| Factor | Points | Data Source |
|--------|--------|-------------|
| 12-Month Avg Volume | 0-25 | JS Historical |
| Growth Trend | 0-10 | Google Trends |

### 12-Month Average Volume (0-25)

| Monthly Volume | Points | Classification |
|----------------|--------|----------------|
| > 50,000 | 25 | 🔥 Massive |
| 30,000 - 50,000 | 22 | High |
| 20,000 - 30,000 | 18 | Good |
| 10,000 - 20,000 | 14 | Moderate |
| 5,000 - 10,000 | 10 | Low-Moderate |
| 2,000 - 5,000 | 6 | Low |
| < 2,000 | 2 | Niche |

### Growth Trend (0-10)

| Trend (YoY Change) | Points | Signal |
|--------------------|--------|--------|
| > +30% | 10 | 🚀 Hot |
| +15% to +30% | 8 | 📈 Growing |
| +5% to +15% | 6 | ↗️ Rising |
| -5% to +5% | 4 | ➡️ Stable |
| -15% to -5% | 2 | ↘️ Slowing |
| < -15% | 0 | 📉 Declining |

### Implementation

```python
def score_volume(monthly_avg, trend_change):
    # 12-month average (0-25)
    if monthly_avg > 50000:
        vol_score = 25
    elif monthly_avg > 30000:
        vol_score = 22
    elif monthly_avg > 20000:
        vol_score = 18
    elif monthly_avg > 10000:
        vol_score = 14
    elif monthly_avg > 5000:
        vol_score = 10
    elif monthly_avg > 2000:
        vol_score = 6
    else:
        vol_score = 2
    
    # Growth trend (0-10)
    if trend_change > 30:
        trend_score = 10
    elif trend_change > 15:
        trend_score = 8
    elif trend_change > 5:
        trend_score = 6
    elif trend_change > -5:
        trend_score = 4
    elif trend_change > -15:
        trend_score = 2
    else:
        trend_score = 0
    
    return {
        'total': vol_score + trend_score,
        'volume_part': vol_score,
        'trend_part': trend_score
    }
```

---

## 2. Difficulty Score — 0-30

### Components

| Factor | Points | Data Source |
|--------|--------|-------------|
| Exact Match Products | 0-10 | Amazon Search |
| Top 3 Click Share | 0-10 | ABA |
| Average Reviews | 0-10 | Amazon Search |

### Exact Match Product Count (0-10)

Lower product count = Easier to rank

| Product Count | Points | Competition |
|---------------|--------|-------------|
| < 100 | 10 | 🟢 Low |
| 100 - 300 | 8 | Low-Medium |
| 300 - 500 | 6 | Medium |
| 500 - 1000 | 4 | Medium-High |
| 1000 - 3000 | 2 | High |
| > 3000 | 0 | 🔴 Very High |

### Top 3 Click Share Concentration (0-10)

Lower concentration = More fragmented = Easier entry

| Top 3 Click Share | Points | Market Structure |
|-------------------|--------|------------------|
| < 30% | 10 | 🟢 Fragmented |
| 30% - 45% | 8 | Somewhat fragmented |
| 45% - 60% | 5 | Moderate concentration |
| 60% - 75% | 3 | Concentrated |
| > 75% | 0 | 🔴 Dominated |

### Average Reviews in Top 10 (0-10)

Lower reviews = Easier to compete

| Avg Reviews | Points | Review Barrier |
|-------------|--------|----------------|
| < 100 | 10 | 🟢 Very Low |
| 100 - 300 | 8 | Low |
| 300 - 500 | 5 | Medium |
| 500 - 1000 | 3 | High |
| > 1000 | 0 | 🔴 Fortress |

### Implementation

```python
def score_difficulty(product_count, top3_click_share, avg_reviews):
    # Product count (0-10)
    if product_count < 100:
        prod_score = 10
    elif product_count < 300:
        prod_score = 8
    elif product_count < 500:
        prod_score = 6
    elif product_count < 1000:
        prod_score = 4
    elif product_count < 3000:
        prod_score = 2
    else:
        prod_score = 0
    
    # Top 3 click share concentration (0-10)
    if top3_click_share < 30:
        click_score = 10
    elif top3_click_share < 45:
        click_score = 8
    elif top3_click_share < 60:
        click_score = 5
    elif top3_click_share < 75:
        click_score = 3
    else:
        click_score = 0
    
    # Average reviews (0-10)
    if avg_reviews < 100:
        review_score = 10
    elif avg_reviews < 300:
        review_score = 8
    elif avg_reviews < 500:
        review_score = 5
    elif avg_reviews < 1000:
        review_score = 3
    else:
        review_score = 0
    
    return {
        'total': prod_score + click_score + review_score,
        'product_count_part': prod_score,
        'click_share_part': click_score,
        'review_part': review_score
    }
```

---

## 3. Efficiency Score — 0-20

### Components

| Factor | Points | Data Source |
|--------|--------|-------------|
| Click-to-Conversion Rate | 0-12 | ABA |
| PPC Cost Estimate | 0-8 | Estimated |

### Click-to-Conversion Rate (0-12)

Higher conversion = Better buying intent

| Avg Conversion Rate | Points | Intent Quality |
|---------------------|--------|----------------|
| > 15% | 12 | 🟢 Excellent |
| 10% - 15% | 10 | Good |
| 7% - 10% | 7 | Moderate |
| 5% - 7% | 5 | Below Average |
| 3% - 5% | 3 | Low |
| < 3% | 0 | 🔴 Very Low |

### PPC Cost Efficiency (0-8)

Lower cost per click = Better ROI potential

| Estimated CPC | Points | Cost Level |
|---------------|--------|------------|
| < $0.50 | 8 | 🟢 Cheap |
| $0.50 - $1.00 | 6 | Affordable |
| $1.00 - $2.00 | 4 | Moderate |
| $2.00 - $3.00 | 2 | Expensive |
| > $3.00 | 0 | 🔴 Very Expensive |

**CPC Estimation Logic:**
```python
def estimate_cpc(avg_price, competition_level):
    """
    Estimate CPC based on price and competition
    Higher price products = higher CPC
    Higher competition = higher CPC
    """
    base_cpc = avg_price * 0.03  # ~3% of product price
    
    # Competition multiplier
    if competition_level == 'low':
        multiplier = 0.7
    elif competition_level == 'medium':
        multiplier = 1.0
    elif competition_level == 'high':
        multiplier = 1.5
    else:
        multiplier = 2.0
    
    return base_cpc * multiplier
```

### Implementation

```python
def score_efficiency(conversion_rate, estimated_cpc):
    # Conversion rate (0-12)
    if conversion_rate > 15:
        conv_score = 12
    elif conversion_rate > 10:
        conv_score = 10
    elif conversion_rate > 7:
        conv_score = 7
    elif conversion_rate > 5:
        conv_score = 5
    elif conversion_rate > 3:
        conv_score = 3
    else:
        conv_score = 0
    
    # PPC cost (0-8)
    if estimated_cpc < 0.5:
        cpc_score = 8
    elif estimated_cpc < 1.0:
        cpc_score = 6
    elif estimated_cpc < 2.0:
        cpc_score = 4
    elif estimated_cpc < 3.0:
        cpc_score = 2
    else:
        cpc_score = 0
    
    return {
        'total': conv_score + cpc_score,
        'conversion_part': conv_score,
        'cpc_part': cpc_score
    }
```

---

## 4. Relevance Score — 0-15

### Components

| Factor | Points | Data Source |
|--------|--------|-------------|
| Average Price Point | 0-10 | Amazon Search |
| Repurchase Potential | 0-5 | Category Tag |

### Average Price Point (0-10)

Higher price = Better margin potential

| Avg Price | Points | Margin Potential |
|-----------|--------|------------------|
| > $50 | 10 | 🟢 High Margin |
| $35 - $50 | 8 | Good Margin |
| $25 - $35 | 6 | Moderate Margin |
| $15 - $25 | 4 | Low-Moderate |
| $10 - $15 | 2 | Low Margin |
| < $10 | 0 | 🔴 Very Low |

### Repurchase Potential (0-5)

Consumable/repurchasable products have higher LTV

| Category Type | Points | Repurchase |
|---------------|--------|------------|
| Consumable (supplements, food) | 5 | 🟢 High |
| Semi-consumable (skincare, pet supplies) | 4 | Good |
| Accessory (cases, covers) | 3 | Moderate |
| Durable (furniture, tools) | 1 | Low |
| One-time purchase | 0 | None |

**Repurchase Category Detection:**
```python
HIGH_REPURCHASE_KEYWORDS = [
    'supplement', 'vitamin', 'protein', 'snack', 'coffee', 'tea',
    'skincare', 'lotion', 'shampoo', 'soap', 'toothpaste',
    'pet food', 'dog treat', 'cat litter',
    'cleaning', 'wipes', 'paper towel', 'trash bag'
]

MEDIUM_REPURCHASE_KEYWORDS = [
    'filter', 'cartridge', 'refill', 'replacement',
    'case', 'cover', 'screen protector',
    'battery', 'charger'
]

def detect_repurchase_potential(keyword, category):
    kw_lower = keyword.lower()
    
    if any(kw in kw_lower for kw in HIGH_REPURCHASE_KEYWORDS):
        return 5
    elif any(kw in kw_lower for kw in MEDIUM_REPURCHASE_KEYWORDS):
        return 3
    else:
        return 1  # Default for durable goods
```

### Implementation

```python
def score_relevance(avg_price, repurchase_score):
    # Price point (0-10)
    if avg_price > 50:
        price_score = 10
    elif avg_price > 35:
        price_score = 8
    elif avg_price > 25:
        price_score = 6
    elif avg_price > 15:
        price_score = 4
    elif avg_price > 10:
        price_score = 2
    else:
        price_score = 0
    
    return {
        'total': price_score + repurchase_score,
        'price_part': price_score,
        'repurchase_part': repurchase_score
    }
```

---

## Final Score Calculation

```python
def calculate_keyword_score(
    monthly_avg, trend_change,           # Volume inputs
    product_count, top3_click_share, avg_reviews,  # Difficulty inputs
    conversion_rate, estimated_cpc,      # Efficiency inputs
    avg_price, repurchase_score          # Relevance inputs
):
    # Calculate each dimension
    volume = score_volume(monthly_avg, trend_change)
    difficulty = score_difficulty(product_count, top3_click_share, avg_reviews)
    efficiency = score_efficiency(conversion_rate, estimated_cpc)
    relevance = score_relevance(avg_price, repurchase_score)
    
    # Total score
    total = volume['total'] + difficulty['total'] + efficiency['total'] + relevance['total']
    
    return {
        'total': total,
        'grade': get_grade(total),
        'breakdown': {
            'volume': {'score': volume['total'], 'max': 35, 'details': volume},
            'difficulty': {'score': difficulty['total'], 'max': 30, 'details': difficulty},
            'efficiency': {'score': efficiency['total'], 'max': 20, 'details': efficiency},
            'relevance': {'score': relevance['total'], 'max': 15, 'details': relevance}
        }
    }

def get_grade(score):
    if score >= 80:
        return 'A 🔥'
    elif score >= 70:
        return 'B ✅'
    elif score >= 60:
        return 'C+ ⚠️'
    elif score >= 50:
        return 'C 🟡'
    else:
        return 'D ❌'
```

---

## Score Output Format

```markdown
### 🔑 Keyword Score: [KEYWORD]

**Total: XX/100 (Grade X)**

| Dimension | Score | Max | Key Data |
|-----------|-------|-----|----------|
| 📈 Volume | XX | 35 | XX,XXX/mo, +XX% trend |
| ⚔️ Difficulty | XX | 30 | XXX products, XX% top3, XXX reviews |
| 💰 Efficiency | XX | 20 | XX% conv, $X.XX CPC |
| 🎯 Relevance | XX | 15 | $XX avg price, [repurchase level] |

**Score Breakdown:**
- Volume: XX (avg) + X (trend) = XX
- Difficulty: X (products) + X (click share) + X (reviews) = XX
- Efficiency: X (conversion) + X (CPC) = XX
- Relevance: X (price) + X (repurchase) = XX
```

---

## Grade Interpretation

| Score | Grade | Meaning | Action |
|-------|-------|---------|--------|
| 80-100 | A 🔥 | Blue ocean keyword | 🟢 Prioritize |
| 70-79 | B ✅ | Strong opportunity | 🟢 Pursue |
| 60-69 | C+ ⚠️ | Moderate opportunity | 🟡 Consider |
| 50-59 | C 🟡 | Competitive keyword | 🟡 Caution |
| 0-49 | D ❌ | Poor opportunity | 🔴 Avoid |
