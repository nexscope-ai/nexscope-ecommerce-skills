# Red Flags — Keyword Opportunity Finder v1.0

## Auto-Avoid Keywords

These keywords have structural issues that make them poor opportunities regardless of volume.

---

## 1. Amazon Dominance

### Amazon Basics / Amazon Brands

| Signal | Detection |
|--------|-----------|
| "Amazon Basics" in top 5 | Hard to outrank |
| "Amazon Essentials" in top 5 | Amazon priority |
| "Amazon Commercial" in top 5 | B2B focus |

**Why Avoid:**
- Amazon prioritizes own brands in search
- Better placement, better pricing
- Nearly impossible to compete

```python
AMAZON_BRANDS = [
    'amazon basics', 'amazonbasics', 'amazon essentials',
    'amazon commercial', 'solimo', 'presto', 'mama bear',
    'happy belly', 'wickedly prime', 'goodthreads'
]

def check_amazon_dominance(search_results):
    top_5 = search_results[:5]
    for product in top_5:
        brand = product.get('brand', '').lower()
        if any(ab in brand for ab in AMAZON_BRANDS):
            return {'red_flag': True, 'reason': 'Amazon brand in top 5'}
    return {'red_flag': False}
```

---

## 2. Brand Walls

### All Known Brands

| Signal | Threshold |
|--------|-----------|
| Known brands | > 80% of top 10 |
| Same brand dominates | > 50% of top 10 |

**Why Avoid:**
- Consumers search for brands, not products
- Brand loyalty = high barrier
- Hard to break in without brand recognition

```python
def check_brand_wall(search_results, known_brands):
    top_10 = search_results[:10]
    known_count = sum(1 for p in top_10 if is_known_brand(p['brand'], known_brands))
    
    if known_count >= 8:  # > 80%
        return {'red_flag': True, 'reason': 'Brand wall (>80% known brands)'}
    
    # Check single brand dominance
    brand_counts = Counter(p['brand'] for p in top_10)
    top_brand_count = brand_counts.most_common(1)[0][1]
    if top_brand_count >= 5:  # 50%+
        return {'red_flag': True, 'reason': f'Single brand dominates ({top_brand_count}/10)'}
    
    return {'red_flag': False}
```

---

## 3. Review Fortress

### Extremely High Reviews

| Signal | Threshold |
|--------|-----------|
| Average reviews | > 2,000 |
| Minimum reviews | > 500 |

**Why Avoid:**
- Mature market with entrenched players
- Years to build competitive reviews
- Social proof disadvantage

```python
def check_review_fortress(search_results):
    top_10 = search_results[:10]
    reviews = [p.get('reviews', 0) for p in top_10]
    
    avg_reviews = sum(reviews) / len(reviews)
    min_reviews = min(reviews)
    
    if avg_reviews > 2000:
        return {'red_flag': True, 'reason': f'Review fortress (avg {avg_reviews:.0f})'}
    if min_reviews > 500:
        return {'red_flag': True, 'reason': f'No weak competitors (min {min_reviews})'}
    
    return {'red_flag': False}
```

---

## 4. Trademark Issues

### Brand Names in Keywords

| Signal | Examples |
|--------|----------|
| Trademark in keyword | "Nike running shoes" |
| Brand misspellings | "Yeeti tumbler" |
| Brand + generic | "Hydro Flask alternative" |

**Why Avoid:**
- Trademark infringement risk
- Amazon policy violation
- Listing removal possible

```python
TRADEMARKED_TERMS = [
    'nike', 'adidas', 'apple', 'samsung', 'yeti', 'hydroflask',
    'instant pot', 'kitchenaid', 'dyson', 'roomba', 'vitamix'
]

def check_trademark_risk(keyword):
    kw_lower = keyword.lower()
    for tm in TRADEMARKED_TERMS:
        if tm in kw_lower:
            return {'red_flag': True, 'reason': f'Trademark: {tm}'}
    return {'red_flag': False}
```

---

## 5. Dying Markets

### Declining Trends

| Signal | Threshold |
|--------|-----------|
| YoY decline | > 30% |
| Consistent decline | 6+ months |

**Why Avoid:**
- Shrinking demand
- Harder to grow
- Potential obsolescence

```python
def check_dying_market(trend_data):
    change = trend_data['change_pct']
    
    if change < -30:
        return {'red_flag': True, 'reason': f'Dying market ({change:.0f}% decline)'}
    
    # Check for consistent decline
    monthly_changes = trend_data.get('monthly_changes', [])
    if len(monthly_changes) >= 6:
        decline_months = sum(1 for c in monthly_changes[-6:] if c < 0)
        if decline_months >= 5:
            return {'red_flag': True, 'reason': 'Consistent decline (5+ months)'}
    
    return {'red_flag': False}
```

---

## 6. Regulatory/Compliance Issues

### Restricted Categories

| Category | Issue |
|----------|-------|
| Supplements | FDA regulations |
| Electronics | FCC certification |
| Children's products | CPSIA testing |
| Food items | FDA approval |

```python
RESTRICTED_KEYWORDS = [
    # Supplements
    'supplement', 'vitamin', 'protein powder', 'probiotic',
    # Medical
    'medical', 'therapeutic', 'treatment', 'cure',
    # Weapons
    'knife', 'weapon', 'self defense',
    # Hazmat
    'battery', 'lithium', 'flammable'
]

def check_restricted_category(keyword):
    kw_lower = keyword.lower()
    for restricted in RESTRICTED_KEYWORDS:
        if restricted in kw_lower:
            return {'red_flag': True, 'reason': f'Restricted: {restricted}'}
    return {'red_flag': False}
```

---

## 7. Low Intent Keywords

### Informational Only

| Signal | Examples |
|--------|----------|
| "How to" questions | "how to pack a lunch box" |
| "What is" questions | "what is bento" |
| DIY keywords | "DIY lunch bag" |

**Why Avoid:**
- Low purchase intent
- Users want information, not products
- Low conversion rate

```python
LOW_INTENT_SIGNALS = [
    'how to', 'what is', 'why do', 'diy', 'homemade',
    'free', 'download', 'template', 'ideas', 'inspiration'
]

def check_low_intent(keyword):
    kw_lower = keyword.lower()
    for signal in LOW_INTENT_SIGNALS:
        if signal in kw_lower:
            return {'red_flag': True, 'reason': f'Low intent: {signal}'}
    return {'red_flag': False}
```

---

## Combined Red Flag Check

```python
def check_all_red_flags(keyword, search_results, trend_data, known_brands):
    """
    Run all red flag checks on a keyword
    Returns list of triggered flags
    """
    flags = []
    
    # Check each red flag
    checks = [
        check_amazon_dominance(search_results),
        check_brand_wall(search_results, known_brands),
        check_review_fortress(search_results),
        check_trademark_risk(keyword),
        check_dying_market(trend_data),
        check_restricted_category(keyword),
        check_low_intent(keyword)
    ]
    
    for check in checks:
        if check['red_flag']:
            flags.append(check['reason'])
    
    return {
        'has_red_flags': len(flags) > 0,
        'flags': flags,
        'flag_count': len(flags)
    }
```

---

## Red Flag Summary Table

| Red Flag | Detection | Severity |
|----------|-----------|----------|
| Amazon brand in top 5 | Brand check | 🔴 Critical |
| Brand wall (>80%) | Brand % | 🔴 Critical |
| Review fortress (>2000 avg) | Review analysis | 🔴 Critical |
| Trademark in keyword | Term matching | 🔴 Critical |
| Dying market (>30% decline) | Trend analysis | 🟠 High |
| Restricted category | Category check | 🟠 High |
| Low intent keyword | Signal matching | 🟡 Medium |
| Single brand dominates (>50%) | Brand count | 🟡 Medium |

---

## Output Format

```markdown
### ⚠️ Red Flags Detected

| Keyword | Flag | Severity |
|---------|------|----------|
| [keyword] | Amazon Basics in top 3 | 🔴 Critical |
| [keyword] | Brand wall (85% known) | 🔴 Critical |
| [keyword] | Dying market (-45%) | 🟠 High |

**Recommendation:** Avoid these keywords or find long-tail alternatives.
```
