# Authenticity Check — New Product Tracker v1.0

## Why Check Authenticity?

New products with rapid growth may have:
- **Fake reviews** (paid, incentivized)
- **Merged variations** (inherited reviews from different product)
- **Review manipulation** (vote brigading, etc.)

Trusting manipulated data leads to bad decisions.

---

## Authenticity Score (0-100)

Higher score = More trustworthy data

| Score | Grade | Interpretation | Action |
|-------|-------|----------------|--------|
| 80-100 | ✅ Authentic | Trust the data | Proceed with analysis |
| 60-79 | ⚠️ Suspicious | Verify manually | Check reviews, be cautious |
| < 60 | ❌ Likely Fake | Data unreliable | Exclude or heavily discount |

---

## Detection Signals

### 1. Velocity Anomaly

**Problem:** Reviews growing faster than sales should allow.

| Metric | Normal | Suspicious | Red Flag |
|--------|--------|------------|----------|
| Reviews/Day (sustained) | < 2 | 2-5 | > 5 |
| Reviews/Sales Ratio | 1-3% | 4-6% | > 7% |

```python
def check_velocity_anomaly(reviews, age_days, estimated_sales):
    """
    Check if review velocity is anomalously high
    """
    reviews_per_day = reviews / age_days if age_days > 0 else 0
    review_rate = reviews / estimated_sales if estimated_sales > 0 else 0
    
    penalty = 0
    flags = []
    
    # Reviews per day check
    if reviews_per_day > 5:
        penalty += 30
        flags.append(f"Extreme velocity: {reviews_per_day:.1f} reviews/day")
    elif reviews_per_day > 2:
        penalty += 15
        flags.append(f"High velocity: {reviews_per_day:.1f} reviews/day")
    
    # Review rate check (normal is 1-3%)
    if review_rate > 0.07:
        penalty += 20
        flags.append(f"Abnormal review rate: {review_rate*100:.1f}%")
    elif review_rate > 0.05:
        penalty += 10
        flags.append(f"High review rate: {review_rate*100:.1f}%")
    
    return {'penalty': penalty, 'flags': flags}
```

---

### 2. BSR-Review Mismatch

**Problem:** Reviews don't match what BSR suggests about sales.

```python
def estimate_expected_reviews(bsr, age_days):
    """
    Estimate expected reviews based on BSR and age
    """
    # Approximate daily sales from BSR
    if bsr < 500:
        daily_sales = 80
    elif bsr < 1000:
        daily_sales = 50
    elif bsr < 5000:
        daily_sales = 20
    elif bsr < 10000:
        daily_sales = 10
    elif bsr < 50000:
        daily_sales = 3
    elif bsr < 100000:
        daily_sales = 1
    else:
        daily_sales = 0.5
    
    total_sales = daily_sales * age_days
    # Review rate ~1.5%
    expected_reviews = total_sales * 0.015
    
    return max(1, int(expected_reviews))

def check_bsr_review_mismatch(reviews, bsr, age_days):
    """
    Check if reviews significantly exceed expected for BSR
    """
    expected = estimate_expected_reviews(bsr, age_days)
    ratio = reviews / expected if expected > 0 else 1
    
    penalty = 0
    flags = []
    
    if ratio > 3:
        penalty += 30
        flags.append(f"Reviews {ratio:.1f}x higher than expected for BSR")
    elif ratio > 2:
        penalty += 15
        flags.append(f"Reviews {ratio:.1f}x expected")
    
    return {'penalty': penalty, 'flags': flags, 'expected': expected}
```

---

### 3. Rating Distribution

**Problem:** Authentic products rarely have > 85% 5-star reviews.

| Distribution | Normal | Suspicious | Red Flag |
|--------------|--------|------------|----------|
| 5-star % | 50-70% | 75-85% | > 85% |
| 1-star % | 3-10% | < 3% | < 1% |

```python
def check_rating_distribution(rating_breakdown):
    """
    Check if rating distribution looks authentic
    
    rating_breakdown: {'5': 100, '4': 30, '3': 10, '2': 5, '1': 5}
    """
    total = sum(rating_breakdown.values())
    if total == 0:
        return {'penalty': 0, 'flags': []}
    
    five_star_pct = rating_breakdown.get('5', 0) / total * 100
    one_star_pct = rating_breakdown.get('1', 0) / total * 100
    
    penalty = 0
    flags = []
    
    # Check 5-star percentage
    if five_star_pct > 90:
        penalty += 25
        flags.append(f"Suspiciously high 5-star: {five_star_pct:.0f}%")
    elif five_star_pct > 85:
        penalty += 15
        flags.append(f"High 5-star: {five_star_pct:.0f}%")
    
    # Check 1-star percentage (authentic products have some)
    if one_star_pct < 1 and total > 50:
        penalty += 10
        flags.append(f"Almost no 1-star reviews: {one_star_pct:.1f}%")
    
    return {'penalty': penalty, 'flags': flags}
```

---

### 4. Review Burst Detection

**Problem:** Large portion of reviews came in a short window.

```python
def check_review_burst(review_history):
    """
    Check if reviews came in suspicious bursts
    
    review_history: List of weekly review counts
    """
    if not review_history or len(review_history) < 4:
        return {'penalty': 0, 'flags': []}
    
    total_reviews = sum(review_history)
    if total_reviews == 0:
        return {'penalty': 0, 'flags': []}
    
    max_week = max(review_history)
    max_week_pct = max_week / total_reviews * 100
    
    # Check for single-week burst
    penalty = 0
    flags = []
    
    if max_week_pct > 60:
        penalty += 25
        flags.append(f"{max_week_pct:.0f}% of reviews in single week")
    elif max_week_pct > 40:
        penalty += 15
        flags.append(f"{max_week_pct:.0f}% of reviews in single week")
    
    # Check for 2-week burst
    sorted_weeks = sorted(review_history, reverse=True)
    top_2_weeks = sum(sorted_weeks[:2])
    top_2_pct = top_2_weeks / total_reviews * 100
    
    if top_2_pct > 80 and total_reviews > 30:
        penalty += 15
        flags.append(f"{top_2_pct:.0f}% of reviews in just 2 weeks")
    
    return {'penalty': penalty, 'flags': flags}
```

---

### 5. Verified Purchase Ratio

**Problem:** Fake reviews often aren't verified purchases.

| Verified % | Normal | Suspicious | Red Flag |
|------------|--------|------------|----------|
| Range | > 85% | 70-85% | < 70% |

```python
def check_verified_ratio(verified_count, total_reviews):
    """
    Check verified purchase ratio
    """
    if total_reviews == 0:
        return {'penalty': 0, 'flags': []}
    
    verified_pct = verified_count / total_reviews * 100
    
    penalty = 0
    flags = []
    
    if verified_pct < 50:
        penalty += 30
        flags.append(f"Very low verified: {verified_pct:.0f}%")
    elif verified_pct < 70:
        penalty += 15
        flags.append(f"Low verified: {verified_pct:.0f}%")
    
    return {'penalty': penalty, 'flags': flags}
```

---

## Combined Authenticity Check

```python
def calculate_authenticity_score(product):
    """
    Calculate overall authenticity score (0-100)
    """
    base_score = 100
    all_flags = []
    
    # Estimate sales for comparison
    estimated_sales = estimate_sales_from_bsr(product['bsr'], product['age_days'])
    
    # Check 1: Velocity anomaly
    velocity = check_velocity_anomaly(
        product['reviews'], 
        product['age_days'],
        estimated_sales
    )
    base_score -= velocity['penalty']
    all_flags.extend(velocity['flags'])
    
    # Check 2: BSR-review mismatch
    mismatch = check_bsr_review_mismatch(
        product['reviews'],
        product['bsr'],
        product['age_days']
    )
    base_score -= mismatch['penalty']
    all_flags.extend(mismatch['flags'])
    
    # Check 3: Rating distribution
    if product.get('rating_breakdown'):
        rating = check_rating_distribution(product['rating_breakdown'])
        base_score -= rating['penalty']
        all_flags.extend(rating['flags'])
    
    # Check 4: Review burst
    if product.get('review_history'):
        burst = check_review_burst(product['review_history'])
        base_score -= burst['penalty']
        all_flags.extend(burst['flags'])
    
    # Check 5: Verified ratio
    if product.get('verified_count') is not None:
        verified = check_verified_ratio(
            product['verified_count'],
            product['reviews']
        )
        base_score -= verified['penalty']
        all_flags.extend(verified['flags'])
    
    final_score = max(0, base_score)
    
    return {
        'score': final_score,
        'grade': get_authenticity_grade(final_score),
        'flags': all_flags,
        'flag_count': len(all_flags)
    }

def get_authenticity_grade(score):
    if score >= 80:
        return '✅ Authentic'
    elif score >= 60:
        return '⚠️ Suspicious'
    else:
        return '❌ Likely Fake'
```

---

## Output Format

```markdown
### Authenticity Check: [Product]

**Score:** 72/100 ⚠️ Suspicious

**Flags Detected:**
- ⚠️ High 5-star: 88%
- ⚠️ Reviews 2.3x expected for BSR

**Recommendation:** Verify reviews manually before trusting data.
```

---

## Integration with Scoring

```python
def adjust_score_for_authenticity(product_score, authenticity_score):
    """
    Adjust product score based on authenticity
    """
    if authenticity_score >= 80:
        # Authentic: no adjustment
        return product_score
    elif authenticity_score >= 60:
        # Suspicious: reduce confidence
        return product_score * 0.85
    else:
        # Likely fake: significant penalty
        return product_score * 0.5
```
