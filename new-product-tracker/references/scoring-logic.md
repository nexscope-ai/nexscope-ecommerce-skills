# Scoring Logic — New Product Tracker v1.0

## New Product Score (0-100)

```
Total = Freshness (25) + Growth (30) + Velocity (20) + Potential (15) + Stability (10)
```

---

## 1. Freshness Score (0-25)

Newer products score higher (more opportunity).

| Age (Days) | Points | Rationale |
|------------|--------|-----------|
| < 30 | 25 | Very fresh, early mover advantage |
| 30-60 | 22 | Still new |
| 60-90 | 18 | Recent launch |
| 90-120 | 14 | Established but young |
| 120-150 | 10 | Maturing |
| 150-180 | 6 | Near threshold |
| > 180 | 0 | Not a "new" product |

### Implementation

```python
def score_freshness(age_days):
    if age_days > 180:
        return 0
    
    brackets = [
        (30, 25),
        (60, 22),
        (90, 18),
        (120, 14),
        (150, 10),
        (180, 6)
    ]
    
    for max_age, points in brackets:
        if age_days <= max_age:
            return points
    
    return 0
```

---

## 2. Growth Score (0-30)

Based on BSR improvement over 30 days.

**Note:** Lower BSR = Better rank = More sales

| BSR 30d Improvement | Points | Signal |
|---------------------|--------|--------|
| > 70% | 30 | 🚀 Explosive growth |
| 50-70% | 25 | 📈 Strong growth |
| 30-50% | 20 | ✅ Good growth |
| 15-30% | 15 | ➡️ Moderate growth |
| 5-15% | 10 | Slow growth |
| 0-5% | 5 | Flat |
| Declining (negative) | 0 | ❌ Losing momentum |

### BSR Improvement Calculation

```python
def calculate_bsr_improvement(bsr_30d_ago, bsr_now):
    """
    Calculate BSR improvement percentage.
    Lower BSR is better, so improvement = (old - new) / old
    """
    if bsr_30d_ago <= 0:
        return 0
    
    # BSR decreased = improvement (more sales)
    improvement = (bsr_30d_ago - bsr_now) / bsr_30d_ago * 100
    return improvement

def score_growth(bsr_improvement):
    if bsr_improvement > 70:
        return 30
    elif bsr_improvement > 50:
        return 25
    elif bsr_improvement > 30:
        return 20
    elif bsr_improvement > 15:
        return 15
    elif bsr_improvement > 5:
        return 10
    elif bsr_improvement > 0:
        return 5
    else:
        return 0
```

---

## 3. Velocity Score (0-20)

Based on review growth rate (validated by authenticity check).

| Reviews/Month | Base Points | Authenticity Adjustment |
|---------------|-------------|------------------------|
| > 50 | 20 | -5 if Authenticity < 70 |
| 30-50 | 16 | -3 if Authenticity < 70 |
| 15-30 | 12 | None |
| 5-15 | 8 | None |
| < 5 | 4 | None |

### Implementation

```python
def score_velocity(reviews_per_month, authenticity_score):
    # Base score
    if reviews_per_month > 50:
        base = 20
        adjustment = -5 if authenticity_score < 70 else 0
    elif reviews_per_month > 30:
        base = 16
        adjustment = -3 if authenticity_score < 70 else 0
    elif reviews_per_month > 15:
        base = 12
        adjustment = 0
    elif reviews_per_month > 5:
        base = 8
        adjustment = 0
    else:
        base = 4
        adjustment = 0
    
    return max(0, base + adjustment)

def calculate_reviews_per_month(total_reviews, age_days):
    if age_days <= 0:
        return 0
    months = age_days / 30
    return total_reviews / months
```

---

## 4. Potential Score (0-15)

Based on estimated monthly revenue.

| Monthly Revenue | Points | Market Signal |
|-----------------|--------|---------------|
| > $50,000 | 15 | Hot market |
| $20,000-50,000 | 12 | Strong market |
| $10,000-20,000 | 9 | Good market |
| $5,000-10,000 | 6 | Moderate market |
| < $5,000 | 3 | Niche market |

### Revenue Estimation

```python
def estimate_monthly_revenue(bsr, category, price):
    """
    Estimate monthly revenue from BSR.
    Use Jungle Scout API for accurate data, or estimate.
    """
    # Simplified estimation (use JS API for accuracy)
    # Different categories have different BSR-to-sales ratios
    
    category_multipliers = {
        'beauty': 0.8,
        'home_kitchen': 1.0,
        'sports': 0.9,
        'baby': 0.7,
        'toys': 1.2,
        'default': 1.0
    }
    
    mult = category_multipliers.get(category, 1.0)
    
    # Rough estimation formula
    if bsr < 1000:
        daily_sales = 50 * mult
    elif bsr < 5000:
        daily_sales = 20 * mult
    elif bsr < 10000:
        daily_sales = 10 * mult
    elif bsr < 50000:
        daily_sales = 3 * mult
    else:
        daily_sales = 1 * mult
    
    monthly_revenue = daily_sales * 30 * price
    return monthly_revenue

def score_potential(monthly_revenue):
    if monthly_revenue > 50000:
        return 15
    elif monthly_revenue > 20000:
        return 12
    elif monthly_revenue > 10000:
        return 9
    elif monthly_revenue > 5000:
        return 6
    else:
        return 3
```

---

## 5. Stability Score (0-10)

Measures sustainability of the opportunity.

| Factor | Points | Criteria |
|--------|--------|----------|
| Price Stability | 0-3 | < 10% volatility = 3, < 20% = 2, else = 0 |
| Stock Stability | 0-3 | > 90% in stock = 3, > 70% = 2, else = 0 |
| Seller Stability | 0-2 | Stable = 2, Increasing slowly = 1, else = 0 |
| No Manipulation | 0-2 | Authenticity > 80 = 2, > 60 = 1, else = 0 |

### Implementation

```python
def score_stability(product_data):
    score = 0
    
    # Price stability
    price_volatility = product_data.get('price_volatility', 0)
    if price_volatility < 10:
        score += 3
    elif price_volatility < 20:
        score += 2
    
    # Stock stability
    in_stock_pct = product_data.get('in_stock_pct', 100)
    if in_stock_pct > 90:
        score += 3
    elif in_stock_pct > 70:
        score += 2
    
    # Seller stability
    seller_trend = product_data.get('seller_count_trend', 0)
    if -0.1 <= seller_trend <= 0.2:  # Stable to slightly growing
        score += 2
    elif seller_trend < 0.5:  # Growing moderately
        score += 1
    
    # Authenticity bonus
    authenticity = product_data.get('authenticity_score', 100)
    if authenticity > 80:
        score += 2
    elif authenticity > 60:
        score += 1
    
    return min(10, score)
```

---

## Final Score Calculation

```python
def calculate_new_product_score(product):
    """
    Calculate total New Product Score (0-100)
    """
    # Get individual scores
    freshness = score_freshness(product['age_days'])
    
    bsr_improvement = calculate_bsr_improvement(
        product['bsr_30d_ago'], 
        product['bsr_now']
    )
    growth = score_growth(bsr_improvement)
    
    reviews_per_month = calculate_reviews_per_month(
        product['reviews'],
        product['age_days']
    )
    authenticity = product.get('authenticity_score', 100)
    velocity = score_velocity(reviews_per_month, authenticity)
    
    monthly_revenue = product.get('monthly_revenue') or estimate_monthly_revenue(
        product['bsr_now'],
        product.get('category'),
        product['price']
    )
    potential = score_potential(monthly_revenue)
    
    stability = score_stability(product)
    
    total = freshness + growth + velocity + potential + stability
    
    return {
        'total': total,
        'grade': get_grade(total),
        'breakdown': {
            'freshness': {'score': freshness, 'max': 25},
            'growth': {'score': growth, 'max': 30},
            'velocity': {'score': velocity, 'max': 20},
            'potential': {'score': potential, 'max': 15},
            'stability': {'score': stability, 'max': 10}
        }
    }

def get_grade(score):
    if score >= 85:
        return 'A+ 🚀'
    elif score >= 75:
        return 'A 🔥'
    elif score >= 65:
        return 'B ✅'
    elif score >= 55:
        return 'C ⚠️'
    else:
        return 'D ❌'
```

---

## Score Interpretation

| Score | Grade | Meaning | Action |
|-------|-------|---------|--------|
| 85-100 | A+ 🚀 | Exceptional new product | Study immediately |
| 75-84 | A 🔥 | Strong opportunity | Prioritize |
| 65-74 | B ✅ | Good opportunity | Consider |
| 55-64 | C ⚠️ | Moderate opportunity | Low priority |
| < 55 | D ❌ | Weak opportunity | Skip |
