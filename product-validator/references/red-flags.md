# Red Flags Detection — Product Validator v1.0

## Flag Severity Levels

| Level | Impact | Action |
|-------|--------|--------|
| 🔴 **Critical** | -10 points | Likely disqualifies the product |
| 🟡 **Warning** | -3 points | Needs manual verification |
| ℹ️ **Info** | 0 points | For awareness only |

---

## Critical Red Flags 🔴

### 1. BSR Manipulation

**Detection:**
```python
def detect_bsr_manipulation(bsr_history):
    """
    BSR manipulation is indicated by extremely high volatility
    that doesn't match seasonal patterns
    """
    if len(bsr_history) < 30:
        return None
    
    cv = stdev(bsr_history) / mean(bsr_history) * 100
    
    if cv > 80:
        return {
            'flag': 'bsr_manipulation',
            'severity': 'critical',
            'detail': f'BSR coefficient of variation: {cv:.0f}% (normal < 50%)',
            'risk': 'Product may use rank manipulation tactics, unreliable demand signal'
        }
    return None
```

**Why It's Critical:**
- Artificial rank boosting (giveaways, extreme discounts)
- Real demand is much lower than BSR suggests
- Pattern often precedes listing suspension

---

### 2. Review Step/Merge Detection

**Detection:**
```python
def detect_review_merge(review_history):
    """
    Sudden jumps in review count indicate listing merge
    or mass incentivized reviews
    """
    if len(review_history) < 10:
        return None
    
    max_5day_jump = 0
    for i in range(5, len(review_history)):
        jump = review_history[i] - review_history[i-5]
        max_5day_jump = max(max_5day_jump, jump)
    
    if max_5day_jump > 50:
        return {
            'flag': 'review_merge',
            'severity': 'critical',
            'detail': f'+{max_5day_jump} reviews in 5-day window',
            'risk': 'Likely listing merge or manipulation, high suspension risk'
        }
    return None
```

**Why It's Critical:**
- Merged listings often get demerged (reviews disappear)
- Indicates ToS violations
- Reviews may not reflect actual product quality

---

### 3. Buy Box Dominated by Single Seller

**Detection:**
```python
def detect_buybox_monopoly(buybox_shares):
    """
    If one seller controls >70% of Buy Box, 
    new sellers have almost no chance
    """
    top_share = max(buybox_shares.values()) if buybox_shares else 0
    
    if top_share > 70:
        return {
            'flag': 'buybox_dominated',
            'severity': 'critical',
            'detail': f'Top seller holds {top_share:.0f}% of Buy Box',
            'risk': 'Market effectively locked, entry extremely difficult'
        }
    return None
```

---

### 4. Amazon as Dominant Seller

**Detection:**
```python
AMAZON_IDS = {'ATVPDKIKX0DER', 'A3P5ROKL5A1OLE', ...}

def detect_amazon_dominance(buybox_shares):
    """
    Amazon competing = race to the bottom
    """
    amazon_share = sum(
        share for seller, share in buybox_shares.items()
        if seller in AMAZON_IDS
    )
    
    if amazon_share > 50:
        return {
            'flag': 'amazon_dominant',
            'severity': 'critical',
            'detail': f'Amazon holds {amazon_share:.0f}% of Buy Box',
            'risk': 'Cannot compete with Amazon on price or Prime delivery'
        }
    return None
```

---

### 5. Price War (Declining Price)

**Detection:**
```python
def detect_price_war(price_history):
    """
    Sustained price decline indicates race to bottom
    """
    if len(price_history) < 30:
        return None
    
    prices = [p for p in price_history if p > 0]
    if not prices:
        return None
    
    change = (prices[-1] - prices[0]) / prices[0] * 100
    
    if change < -30:
        return {
            'flag': 'price_war',
            'severity': 'critical',
            'detail': f'Price declined {abs(change):.0f}% over period',
            'risk': 'Active price war, margins will be squeezed'
        }
    return None
```

---

## Warning Red Flags 🟡

### 6. Seller Surge

**Detection:**
```python
def detect_seller_surge(seller_history, current):
    """
    Rapid increase in sellers = incoming competition
    """
    if len(seller_history) < 30:
        return None
    
    sellers_30d_ago = seller_history[-30]
    if sellers_30d_ago <= 0:
        return None
    
    growth = (current - sellers_30d_ago) / sellers_30d_ago * 100
    
    if growth > 50:
        return {
            'flag': 'seller_surge',
            'severity': 'warning',
            'detail': f'+{growth:.0f}% sellers in 30 days',
            'risk': 'Competition increasing rapidly, may drive down margins'
        }
    return None
```

---

### 7. Frequent Out of Stock

**Detection:**
```python
def detect_frequent_oos(stock_history):
    """
    Frequent OOS may indicate supply chain issues
    or demand exceeding supply
    """
    if len(stock_history) < 30:
        return None
    
    recent = stock_history[-90:] if len(stock_history) >= 90 else stock_history
    oos_days = sum(1 for s in recent if s <= 0)
    oos_rate = oos_days / len(recent) * 100
    
    if oos_rate > 20:
        return {
            'flag': 'frequent_oos',
            'severity': 'warning',
            'detail': f'{oos_rate:.0f}% out of stock in last 90 days',
            'risk': 'Supply chain may be unreliable'
        }
    return None
```

---

### 8. Zombie Variant

**Detection:**
```python
def detect_zombie_variant(is_variant, variant_reviews, parent_reviews):
    """
    Variant with very low share of parent reviews
    """
    if not is_variant:
        return None
    
    share = variant_reviews / parent_reviews * 100 if parent_reviews > 0 else 100
    
    if share < 5:
        return {
            'flag': 'zombie_variant',
            'severity': 'warning',
            'detail': f'Only {share:.1f}% of parent reviews',
            'risk': 'BSR is misleading, this specific variant has low demand'
        }
    return None
```

---

### 9. High Competition

**Detection:**
```python
def detect_high_competition(seller_count):
    """
    Many sellers = price pressure
    """
    if seller_count > 20:
        return {
            'flag': 'high_competition',
            'severity': 'warning',
            'detail': f'{seller_count} active sellers',
            'risk': 'Saturated market, differentiation difficult'
        }
    return None
```

---

### 10. Review Velocity Mismatch

**Detection:**
```python
def detect_review_velocity_mismatch(monthly_reviews, monthly_sales):
    """
    Reviews growing faster than sales would suggest
    """
    expected = monthly_sales * 0.02  # ~2% review rate
    
    if expected > 5 and monthly_reviews > expected * 3:
        return {
            'flag': 'suspicious_reviews',
            'severity': 'warning',
            'detail': f'{monthly_reviews} reviews/mo vs {expected:.0f} expected',
            'risk': 'Review velocity unusually high, may indicate manipulation'
        }
    return None
```

---

## Flag Aggregation

```python
def aggregate_flags(all_flags):
    """
    Calculate total penalty and summarize
    """
    critical_count = sum(1 for f in all_flags if f['severity'] == 'critical')
    warning_count = sum(1 for f in all_flags if f['severity'] == 'warning')
    
    penalty = (critical_count * 10) + (warning_count * 3)
    
    return {
        'critical_flags': critical_count,
        'warning_flags': warning_count,
        'total_penalty': penalty,
        'flags': all_flags
    }
```

---

## Output Format

```json
{
  "red_flags": [
    {
      "flag": "buybox_dominated",
      "severity": "critical",
      "detail": "Top seller holds 75% of Buy Box",
      "risk": "Market effectively locked"
    },
    {
      "flag": "seller_surge",
      "severity": "warning", 
      "detail": "+65% sellers in 30 days",
      "risk": "Competition increasing rapidly"
    }
  ],
  "summary": {
    "critical_count": 1,
    "warning_count": 1,
    "total_penalty": 13
  }
}
```
