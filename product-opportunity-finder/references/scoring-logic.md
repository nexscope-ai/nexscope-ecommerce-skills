# Scoring Logic — Product Opportunity Finder v1.0

## Opportunity Score Overview

```
Total Score = Demand (25) + Competition (30) + Profit (25) + Momentum (20)
Max Score = 100
```

**Score Interpretation:**
| Score | Rating | Action |
|-------|--------|--------|
| 80+ | 🟢 Excellent | Strong opportunity |
| 65-79 | 🟢 Good | Worth pursuing |
| 50-64 | 🟡 Moderate | Proceed with caution |
| 35-49 | 🟠 Weak | Consider alternatives |
| <35 | 🔴 Poor | Not recommended |

---

## 1. Demand Score (0-25 points)

**Based on monthly revenue.**

```python
def calculate_demand_score(revenue):
    if revenue >= 50000:
        return 25
    elif revenue >= 20000:
        return 20
    elif revenue >= 10000:
        return 15
    elif revenue >= 5000:
        return 10
    elif revenue >= 1000:
        return 5
    else:
        return 0
```

| Monthly Revenue | Points |
|-----------------|--------|
| $50K+ | 25 |
| $20K - $50K | 20 |
| $10K - $20K | 15 |
| $5K - $10K | 10 |
| $1K - $5K | 5 |
| < $1K | 0 |

---

## 2. Competition Score (0-30 points)

**Based on review count and other factors.**

### Base Competition (0-20)

```python
def calculate_competition_base(avg_reviews):
    if avg_reviews < 100:
        return 20
    elif avg_reviews < 300:
        return 16
    elif avg_reviews < 500:
        return 12
    elif avg_reviews < 1000:
        return 6
    else:
        return 0
```

| Avg Reviews | Points |
|-------------|--------|
| < 100 | 20 |
| 100 - 300 | 16 |
| 300 - 500 | 12 |
| 500 - 1000 | 6 |
| > 1000 | 0 |

### Competition Bonuses (0-10)

```python
def calculate_competition_bonus(product_data):
    bonus = 0
    
    # No known brands in top 10
    if product_data['known_brand_pct'] == 0:
        bonus += 4
    elif product_data['known_brand_pct'] < 30:
        bonus += 2
    
    # Few sellers per listing
    if product_data['avg_sellers'] < 3:
        bonus += 3
    elif product_data['avg_sellers'] < 5:
        bonus += 1
    
    # Quality gap opportunity
    if product_data['avg_rating'] < 4.0:
        bonus += 3
    elif product_data['avg_rating'] < 4.2:
        bonus += 1
    
    return min(bonus, 10)  # Cap at 10
```

| Bonus Condition | Points |
|-----------------|--------|
| No known brands in top 10 | +4 |
| < 30% known brands | +2 |
| < 3 sellers per listing | +3 |
| < 5 sellers per listing | +1 |
| Avg rating < 4.0 | +3 |
| Avg rating < 4.2 | +1 |

---

## 3. Profit Score (0-25 points)

**Based on estimated margin.**

```python
def calculate_profit_score(price, fees, estimated_cogs_pct=0.3):
    # Estimate COGS as 30% of price (can be adjusted)
    cogs = price * estimated_cogs_pct
    margin = (price - fees - cogs) / price * 100
    
    if margin > 40:
        return 25
    elif margin > 35:
        return 22
    elif margin > 30:
        return 18
    elif margin > 25:
        return 14
    elif margin > 20:
        return 10
    elif margin > 15:
        return 5
    else:
        return 0
```

| Est. Margin | Points |
|-------------|--------|
| > 40% | 25 |
| 35-40% | 22 |
| 30-35% | 18 |
| 25-30% | 14 |
| 20-25% | 10 |
| 15-20% | 5 |
| < 15% | 0 |

### Margin Estimation Formula

```python
estimated_margin = (price - fba_fees - estimated_cogs) / price

# Where:
# - fba_fees: From Jungle Scout data
# - estimated_cogs: 25-35% of price (varies by category)
```

---

## 4. Momentum Score (0-20 points)

**Based on trends and market timing.**

```python
def calculate_momentum_score(product_data):
    score = 0
    
    # BSR improving (lower BSR = better)
    if product_data['bsr_trend'] == 'improving':
        score += 8
    elif product_data['bsr_trend'] == 'stable':
        score += 4
    
    # Search trend rising
    if product_data['search_trend'] == 'rising':
        score += 6
    elif product_data['search_trend'] == 'stable':
        score += 3
    
    # New market (recent listings gaining share)
    if product_data['market_age'] == 'new':
        score += 6
    elif product_data['market_age'] == 'growing':
        score += 3
    
    return min(score, 20)
```

| Momentum Factor | Points |
|-----------------|--------|
| BSR improving (>20% better) | +8 |
| BSR stable | +4 |
| Search trend rising | +6 |
| Search trend stable | +3 |
| New market (avg listing < 2 years) | +6 |
| Growing market (avg listing < 3 years) | +3 |

---

## Red Flags (Disqualifiers)

These conditions automatically reduce or eliminate opportunities:

```python
def apply_red_flags(product, score):
    # Amazon dominates - reduce by 50%
    if product['amazon_seller_pct'] > 30:
        score *= 0.5
        flags.append('⚠️ Amazon seller > 30%')
    
    # All known brands - reduce by 40%
    if product['known_brand_pct'] == 100:
        score *= 0.6
        flags.append('⚠️ Brand monopoly')
    
    # Extreme seasonality - reduce by 30%
    if product['seasonality_index'] > 4:
        score *= 0.7
        flags.append('⚠️ Extreme seasonality')
    
    # Saturated market - reduce by 40%
    if product['avg_reviews'] > 5000:
        score *= 0.6
        flags.append('⚠️ Saturated market')
    
    # Low margin potential - reduce by 30%
    if product['price'] < 10:
        score *= 0.7
        flags.append('⚠️ Low margin potential')
    
    return score, flags
```

| Red Flag | Score Reduction |
|----------|-----------------|
| Amazon seller > 30% | -50% |
| 100% known brands | -40% |
| Seasonality > 4x | -30% |
| Avg reviews > 5000 | -40% |
| Price < $10 | -30% |

---

## Opportunity Type Classification

```python
def classify_opportunity(product):
    types = []
    
    # Type 1: Low Competition + High Demand
    if product['revenue'] > 20000 and product['avg_reviews'] < 300:
        types.append('🔵 Classic Blue Ocean')
    
    # Type 2: Quality Gap
    if product['avg_rating'] < 4.0 and product['revenue'] > 10000:
        types.append('⭐ Quality Opportunity')
    
    # Type 3: Rising Star
    if product['bsr_trend'] == 'improving' and product['listing_age'] < 365:
        types.append('📈 Rising Star')
    
    # Type 4: Price Gap
    if product['price_gap_detected']:
        types.append('💰 Price Gap')
    
    # Type 5: Channel Arbitrage
    if product['tiktok_sales'] > 5000 and product['avg_reviews'] < 500:
        types.append('📱 Channel Arbitrage')
    
    return types
```

---

## Example Calculation

**Product: Bamboo Cutting Board**

| Dimension | Metric | Points |
|-----------|--------|--------|
| **Demand** | $35K/mo revenue | 20 |
| **Competition** | 180 avg reviews | 16 |
| - Bonus: No known brands | | +4 |
| - Bonus: 3 sellers avg | | +1 |
| **Profit** | 32% est. margin | 18 |
| **Momentum** | BSR improving | +8 |
| - Search stable | | +3 |
| | | |
| **Total** | | **70/100** 🟢 |

**Classification:** 🔵 Classic Blue Ocean, ⭐ Quality Opportunity
