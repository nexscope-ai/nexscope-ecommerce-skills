# Category BSR Thresholds — New Product Tracker v1.0

## Why Category-Specific Thresholds?

BSR 50,000 means completely different things in different categories:
- **Beauty:** 50,000 = ~10-20 sales/day (competitive)
- **Industrial:** 50,000 = ~1-2 sales/day (low volume)

---

## BSR Threshold Table

| Category | Top | Great | Good | Notes |
|----------|-----|-------|------|-------|
| Beauty & Personal Care | 1,000 | 10,000 | 50,000 | High volume, competitive |
| Home & Kitchen | 2,000 | 20,000 | 100,000 | Very large category |
| Sports & Outdoors | 1,500 | 15,000 | 80,000 | Seasonal variation |
| Kitchen & Dining | 2,000 | 15,000 | 75,000 | Subset of Home |
| Office Products | 500 | 5,000 | 30,000 | Smaller category |
| Industrial & Scientific | 10,000 | 50,000 | 200,000 | Low volume per product |
| Pet Supplies | 1,000 | 10,000 | 50,000 | Growing category |
| Baby | 800 | 8,000 | 40,000 | Safety-conscious buyers |
| Toys & Games | 2,000 | 20,000 | 100,000 | Highly seasonal |
| Tools & Home Improvement | 1,500 | 15,000 | 75,000 | Steady demand |
| Automotive | 2,000 | 20,000 | 100,000 | Fragmented |
| Patio, Lawn & Garden | 1,000 | 10,000 | 50,000 | Seasonal |
| Health & Household | 1,500 | 15,000 | 75,000 | Essential items |
| Clothing | 3,000 | 30,000 | 150,000 | Size/style variations |
| Electronics | 2,000 | 20,000 | 100,000 | Fast-moving |
| Cell Phones & Accessories | 1,500 | 15,000 | 75,000 | High turnover |
| Grocery & Gourmet Food | 2,000 | 20,000 | 100,000 | Repurchase |
| Arts, Crafts & Sewing | 1,500 | 15,000 | 75,000 | Niche audiences |

---

## Threshold Definitions

| Level | Meaning | Opportunity Signal |
|-------|---------|-------------------|
| **Top** | Top performers in category | 🔴 Very competitive |
| **Great** | Strong sellers | 🟡 Competitive but achievable |
| **Good** | Solid performers | 🟢 Good opportunity zone |

---

## Implementation

```python
BSR_THRESHOLDS = {
    'beauty': {'top': 1000, 'great': 10000, 'good': 50000},
    'home_kitchen': {'top': 2000, 'great': 20000, 'good': 100000},
    'sports': {'top': 1500, 'great': 15000, 'good': 80000},
    'kitchen': {'top': 2000, 'great': 15000, 'good': 75000},
    'office': {'top': 500, 'great': 5000, 'good': 30000},
    'industrial': {'top': 10000, 'great': 50000, 'good': 200000},
    'pet': {'top': 1000, 'great': 10000, 'good': 50000},
    'baby': {'top': 800, 'great': 8000, 'good': 40000},
    'toys': {'top': 2000, 'great': 20000, 'good': 100000},
    'tools': {'top': 1500, 'great': 15000, 'good': 75000},
    'automotive': {'top': 2000, 'great': 20000, 'good': 100000},
    'garden': {'top': 1000, 'great': 10000, 'good': 50000},
    'health': {'top': 1500, 'great': 15000, 'good': 75000},
    'clothing': {'top': 3000, 'great': 30000, 'good': 150000},
    'electronics': {'top': 2000, 'great': 20000, 'good': 100000},
    'phones': {'top': 1500, 'great': 15000, 'good': 75000},
    'grocery': {'top': 2000, 'great': 20000, 'good': 100000},
    'crafts': {'top': 1500, 'great': 15000, 'good': 75000},
}

# Category name mapping (Amazon category to our key)
CATEGORY_MAP = {
    'beauty & personal care': 'beauty',
    'home & kitchen': 'home_kitchen',
    'sports & outdoors': 'sports',
    'kitchen & dining': 'kitchen',
    'office products': 'office',
    'industrial & scientific': 'industrial',
    'pet supplies': 'pet',
    'baby': 'baby',
    'toys & games': 'toys',
    'tools & home improvement': 'tools',
    'automotive': 'automotive',
    'patio, lawn & garden': 'garden',
    'health & household': 'health',
    'clothing, shoes & jewelry': 'clothing',
    'electronics': 'electronics',
    'cell phones & accessories': 'phones',
    'grocery & gourmet food': 'grocery',
    'arts, crafts & sewing': 'crafts',
}

def get_category_thresholds(category_name):
    """
    Get BSR thresholds for a category
    """
    # Normalize category name
    cat_lower = category_name.lower().strip()
    
    # Try direct mapping
    if cat_lower in CATEGORY_MAP:
        key = CATEGORY_MAP[cat_lower]
        return BSR_THRESHOLDS[key]
    
    # Try partial match
    for name, key in CATEGORY_MAP.items():
        if name in cat_lower or cat_lower in name:
            return BSR_THRESHOLDS[key]
    
    # Default thresholds if category not found
    return {'top': 2000, 'great': 20000, 'good': 100000}

def normalize_bsr_score(bsr, category):
    """
    Normalize BSR to 0-100 score based on category
    """
    thresholds = get_category_thresholds(category)
    
    if bsr <= thresholds['top']:
        # Top performer: 90-100
        return 90 + 10 * (thresholds['top'] - bsr) / thresholds['top']
    elif bsr <= thresholds['great']:
        # Great: 70-90
        range_size = thresholds['great'] - thresholds['top']
        position = bsr - thresholds['top']
        return 90 - 20 * (position / range_size)
    elif bsr <= thresholds['good']:
        # Good: 40-70
        range_size = thresholds['good'] - thresholds['great']
        position = bsr - thresholds['great']
        return 70 - 30 * (position / range_size)
    else:
        # Below good: 0-40
        overage = bsr - thresholds['good']
        return max(0, 40 - 40 * (overage / thresholds['good']))

def classify_bsr_level(bsr, category):
    """
    Classify BSR into level
    """
    thresholds = get_category_thresholds(category)
    
    if bsr <= thresholds['top']:
        return 'top'
    elif bsr <= thresholds['great']:
        return 'great'
    elif bsr <= thresholds['good']:
        return 'good'
    else:
        return 'below_threshold'
```

---

## Dynamic Threshold Estimation

When category is unknown or not in the table, estimate from market data:

```python
def estimate_category_thresholds(products_sample):
    """
    Estimate category thresholds from a sample of products
    """
    if not products_sample:
        return {'top': 2000, 'great': 20000, 'good': 100000}
    
    bsr_values = sorted([p['bsr'] for p in products_sample if p.get('bsr')])
    
    if len(bsr_values) < 10:
        return {'top': 2000, 'great': 20000, 'good': 100000}
    
    # Use percentiles
    import numpy as np
    
    return {
        'top': int(np.percentile(bsr_values, 5)),
        'great': int(np.percentile(bsr_values, 20)),
        'good': int(np.percentile(bsr_values, 50))
    }
```

---

## Seasonal Adjustments

Some categories have significant seasonal variation:

| Category | Peak Season | Off-Season Adjustment |
|----------|-------------|----------------------|
| Toys | Q4 (Nov-Dec) | Thresholds * 2 in off-season |
| Garden | Spring (Mar-May) | Thresholds * 1.5 in winter |
| Sports | Summer | Thresholds * 1.3 in winter |
| Baby | Consistent | No adjustment |
| Office | Back-to-school (Aug) | Thresholds * 1.2 off-peak |

```python
def get_seasonal_adjustment(category, month):
    """
    Get seasonal multiplier for BSR thresholds
    """
    seasonal_patterns = {
        'toys': {11: 0.7, 12: 0.6, 1: 1.5, 2: 1.5},  # Q4 peak
        'garden': {3: 0.8, 4: 0.7, 5: 0.8, 11: 1.5, 12: 1.5, 1: 1.5, 2: 1.5},
        'sports': {6: 0.8, 7: 0.8, 8: 0.8, 12: 1.3, 1: 1.3, 2: 1.3},
    }
    
    if category in seasonal_patterns:
        return seasonal_patterns[category].get(month, 1.0)
    return 1.0
```
