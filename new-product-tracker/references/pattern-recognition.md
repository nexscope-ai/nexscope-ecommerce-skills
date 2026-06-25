# Pattern Recognition — New Product Tracker v1.0

## 4 Opportunity Patterns

Each pattern represents a different type of rising product opportunity.

---

## 🚀 Fast Starter

**Definition:** Very new product that's already crushing it.

### Detection Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| Age | < 90 days | Required |
| BSR | < Category "Great" | Required |
| Reviews | 20-200 | Required |
| Authenticity | > 70 | Required |
| Review Velocity | > 15/month | Bonus |

### Implementation

```python
def detect_fast_starter(product, category_thresholds):
    """
    Detect Fast Starter pattern
    """
    # All required criteria must be met
    required = [
        product['age_days'] < 90,
        product['bsr'] < category_thresholds['great'],
        20 <= product['reviews'] <= 200,
        product['authenticity_score'] > 70
    ]
    
    if not all(required):
        return None
    
    # Calculate confidence
    confidence = 'high'
    if product['review_velocity'] > 15:
        confidence = 'very_high'
    
    return {
        'pattern': 'fast_starter',
        'emoji': '🚀',
        'label': 'Fast Starter',
        'confidence': confidence,
        'signals': [
            f"Only {product['age_days']} days old",
            f"Already BSR #{product['bsr']:,}",
            f"{product['reviews']} authentic reviews"
        ],
        'action': 'Study this product immediately - exceptional product-market fit',
        'opportunity': 'Learn from success factors, consider similar product'
    }
```

### Signal Strength

| Factor | Very High | High | Medium |
|--------|-----------|------|--------|
| Age | < 45 days | < 60 days | < 90 days |
| BSR | < "Top" | < "Great" | < "Good" |
| Velocity | > 30/mo | > 20/mo | > 15/mo |

---

## 📈 Rising Star

**Definition:** Established new product with consistent upward trajectory.

### Detection Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| Age | 90-180 days | Required |
| BSR 30d Change | Improved > 40% | Required |
| BSR 90d Trend | Consistently improving | Required |
| Review Velocity | > 15/month | Required |
| Authenticity | > 60 | Required |

### Implementation

```python
def detect_rising_star(product):
    """
    Detect Rising Star pattern
    """
    # Check age range
    if not (90 <= product['age_days'] <= 180):
        return None
    
    # Check BSR improvement
    bsr_30d_improvement = calculate_bsr_improvement(
        product['bsr_30d_ago'],
        product['bsr']
    )
    if bsr_30d_improvement < 40:
        return None
    
    # Check 90d trend consistency
    if not is_trend_consistent(product['bsr_history_90d']):
        return None
    
    # Check velocity
    if product['review_velocity'] < 15:
        return None
    
    # Check authenticity
    if product['authenticity_score'] < 60:
        return None
    
    return {
        'pattern': 'rising_star',
        'emoji': '📈',
        'label': 'Rising Star',
        'confidence': 'high' if bsr_30d_improvement > 60 else 'medium',
        'signals': [
            f"BSR improved {bsr_30d_improvement:.0f}% in 30 days",
            f"Consistent upward trend over 90 days",
            f"{product['review_velocity']:.0f} reviews/month"
        ],
        'action': 'Prime competitor target - validated demand, sustainable growth',
        'opportunity': 'Enter market with differentiated product'
    }

def is_trend_consistent(bsr_history):
    """
    Check if BSR trend is consistently improving (downward)
    """
    if len(bsr_history) < 3:
        return False
    
    # Split into thirds
    third = len(bsr_history) // 3
    early = sum(bsr_history[:third]) / third
    middle = sum(bsr_history[third:2*third]) / third
    recent = sum(bsr_history[2*third:]) / third
    
    # Each period should be better (lower) than previous
    return early > middle > recent
```

---

## 💎 Hidden Gem

**Definition:** Good BSR but surprisingly few reviews - undermarketed.

### Detection Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| BSR | < Category "Good" | Required |
| Reviews | < Expected * 0.5 | Required |
| Rating | > 4.2 | Required |
| Age | > 60 days | Required |
| Authenticity | > 70 | Required |

### Expected Reviews Calculation

```python
def estimate_expected_reviews(bsr, age_days, category):
    """
    Estimate expected review count based on BSR and age
    """
    # Approximate daily sales from BSR
    if bsr < 1000:
        daily_sales = 50
    elif bsr < 5000:
        daily_sales = 20
    elif bsr < 10000:
        daily_sales = 10
    elif bsr < 50000:
        daily_sales = 3
    else:
        daily_sales = 1
    
    # Total estimated sales
    total_sales = daily_sales * age_days
    
    # Review rate (~1-3% of buyers leave reviews)
    review_rate = 0.015
    
    return int(total_sales * review_rate)
```

### Implementation

```python
def detect_hidden_gem(product, category_thresholds):
    """
    Detect Hidden Gem pattern - good sales, few reviews
    """
    # Check basic criteria
    if product['age_days'] < 60:
        return None
    if product['rating'] < 4.2:
        return None
    if product['bsr'] > category_thresholds['good']:
        return None
    if product['authenticity_score'] < 70:
        return None
    
    # Calculate expected reviews
    expected = estimate_expected_reviews(
        product['bsr'],
        product['age_days'],
        product.get('category')
    )
    
    # Check if reviews are significantly below expected
    if product['reviews'] >= expected * 0.5:
        return None
    
    return {
        'pattern': 'hidden_gem',
        'emoji': '💎',
        'label': 'Hidden Gem',
        'confidence': 'high' if product['reviews'] < expected * 0.3 else 'medium',
        'signals': [
            f"BSR #{product['bsr']:,} suggests strong sales",
            f"Only {product['reviews']} reviews (expected ~{expected})",
            f"Rating {product['rating']}★ indicates quality"
        ],
        'action': 'Good product with poor marketing - opportunity to do better',
        'opportunity': 'Enter with superior listing, better keywords, more reviews'
    }
```

---

## 🔥 Viral Launch

**Definition:** Sudden BSR spike, possibly from social media viral moment.

### Detection Criteria

| Metric | Threshold | Weight |
|--------|-----------|--------|
| BSR 7d Change | Improved > 70% | Required |
| BSR Spike | Sudden drop in last 14 days | Required |
| Stock Status | Tight or Shortage | Bonus |

### Implementation

```python
def detect_viral_launch(product):
    """
    Detect Viral Launch pattern - sudden BSR spike
    """
    # Check 7-day BSR change
    bsr_7d_improvement = calculate_bsr_improvement(
        product['bsr_7d_ago'],
        product['bsr']
    )
    
    if bsr_7d_improvement < 70:
        return None
    
    # Check for spike pattern (sudden drop)
    if not detect_bsr_spike(product['bsr_history_14d']):
        return None
    
    # Determine urgency based on stock
    stock_status = product.get('stock_status', 'stable')
    if stock_status in ['tight', 'shortage']:
        urgency = 'critical'
    else:
        urgency = 'high'
    
    return {
        'pattern': 'viral_launch',
        'emoji': '🔥',
        'label': 'Viral Launch',
        'confidence': 'high',
        'urgency': urgency,
        'signals': [
            f"BSR improved {bsr_7d_improvement:.0f}% in just 7 days",
            f"Spike detected in last 14 days",
            f"Stock status: {stock_status}"
        ],
        'action': 'Likely social media / influencer driven - act fast',
        'opportunity': 'Fast window, consider similar product immediately',
        'risk': 'Trend may be short-lived'
    }

def detect_bsr_spike(bsr_history_14d):
    """
    Detect if there's a sudden BSR drop (spike in sales)
    """
    if len(bsr_history_14d) < 7:
        return False
    
    # Compare first half to second half
    first_week_avg = sum(bsr_history_14d[:7]) / 7
    second_week_avg = sum(bsr_history_14d[7:]) / len(bsr_history_14d[7:])
    
    # If second week BSR is significantly lower (better)
    improvement = (first_week_avg - second_week_avg) / first_week_avg * 100
    
    return improvement > 50
```

---

## Pattern Priority

When multiple patterns match, prioritize:

| Priority | Pattern | Reason |
|----------|---------|--------|
| 1 | 🔥 Viral Launch | Time-sensitive |
| 2 | 🚀 Fast Starter | Exceptional opportunity |
| 3 | 📈 Rising Star | Validated, sustainable |
| 4 | 💎 Hidden Gem | Requires execution |

---

## Combined Detection

```python
def detect_all_patterns(product, category_thresholds):
    """
    Run all pattern detections and return matches
    """
    patterns = []
    
    # Check each pattern
    fast_starter = detect_fast_starter(product, category_thresholds)
    if fast_starter:
        patterns.append(fast_starter)
    
    rising_star = detect_rising_star(product)
    if rising_star:
        patterns.append(rising_star)
    
    hidden_gem = detect_hidden_gem(product, category_thresholds)
    if hidden_gem:
        patterns.append(hidden_gem)
    
    viral = detect_viral_launch(product)
    if viral:
        patterns.append(viral)
    
    # Sort by priority
    priority_order = ['viral_launch', 'fast_starter', 'rising_star', 'hidden_gem']
    patterns.sort(key=lambda p: priority_order.index(p['pattern']))
    
    return {
        'patterns': patterns,
        'primary_pattern': patterns[0] if patterns else None,
        'pattern_count': len(patterns)
    }
```
