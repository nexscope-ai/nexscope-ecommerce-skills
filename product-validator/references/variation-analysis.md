# Variation Analysis — Product Validator v1.0

## The Zombie Variant Problem

Many ASINs are part of a parent listing with multiple variations (colors, sizes, etc.). The BSR shown is shared across ALL variations, but:

- 80% of sales may come from ONE color
- The target ASIN might be a "zombie" with almost no sales
- Review counts are often aggregated, hiding the true picture

---

## Detecting Zombie Variants

### Step 1: Check if ASIN is a Variant

```python
def is_variant(keepa_product):
    """Check if ASIN is a variation"""
    return (
        keepa_product.get('isVariant', False) or
        bool(keepa_product.get('parentAsin')) or
        bool(keepa_product.get('variations'))
    )
```

### Step 2: Get Parent Data

```python
def get_parent_data(keepa_product):
    """Extract parent listing data"""
    return {
        'parent_asin': keepa_product.get('parentAsin'),
        'total_variations': len(keepa_product.get('variations', [])),
        'parent_reviews': keepa_product.get('parentReviewCount', 0),
        'variation_attributes': keepa_product.get('variationAttributes', [])
    }
```

### Step 3: Calculate Variation Share

```python
def calculate_variation_share(variant_reviews, parent_reviews):
    """
    Calculate this variant's share of parent reviews
    
    A low share indicates the variant may be a "zombie"
    """
    if parent_reviews == 0:
        return 100  # Solo listing
    
    share = variant_reviews / parent_reviews * 100
    return share
```

---

## Risk Classification

| Share | Classification | Risk |
|-------|----------------|------|
| > 30% | **Dominant Variant** | Low - This is THE seller |
| 15-30% | **Strong Variant** | Low - Significant share |
| 5-15% | **Minor Variant** | Medium - Exists but not popular |
| < 5% | **Zombie Variant** | High - Almost no real demand |

---

## Scoring Implementation

```python
def score_variation(is_variant, variant_reviews, parent_reviews):
    """
    Score variation health (0-5)
    
    Part of the Reviews dimension score
    """
    flags = []
    
    if not is_variant:
        # Standalone product - full score
        return 5, flags
    
    share = calculate_variation_share(variant_reviews, parent_reviews)
    
    if share > 20:
        score = 5  # Strong variant
    elif share > 10:
        score = 3  # Moderate variant
    elif share > 5:
        score = 1  # Weak variant
    else:
        score = 0  # Zombie
        flags.append({
            'flag': 'zombie_variant',
            'severity': 'warning',
            'detail': f'Only {share:.1f}% of parent reviews ({variant_reviews}/{parent_reviews})'
        })
    
    return score, flags
```

---

## Advanced: Variation Attribute Analysis

Some variations have inherent advantages:

### Color Analysis

```python
# Common "winner" colors by category
WINNER_COLORS = {
    'kitchen': ['black', 'stainless', 'white', 'gray'],
    'electronics': ['black', 'white', 'silver'],
    'apparel': ['black', 'navy', 'white'],
    'pet': ['blue', 'gray', 'black'],
}

def analyze_color_potential(color, category):
    """Check if this color is typically popular"""
    winners = WINNER_COLORS.get(category, [])
    color_lower = color.lower()
    
    for winner in winners:
        if winner in color_lower:
            return 'high_potential'
    
    return 'uncertain'
```

### Size Analysis

```python
def analyze_size_potential(size):
    """
    Middle sizes typically sell best
    Extremes (XS, XXL, tiny, huge) often have lower demand
    """
    size_lower = size.lower()
    
    # Low-demand indicators
    low_demand = ['xs', 'xxs', 'xxxl', 'xxl', 'jumbo', 'tiny', 'mini']
    for indicator in low_demand:
        if indicator in size_lower:
            return 'low_potential'
    
    # High-demand indicators  
    high_demand = ['medium', 'regular', 'standard', 'large', 'm', 'l']
    for indicator in high_demand:
        if size_lower == indicator or size_lower.startswith(indicator):
            return 'high_potential'
    
    return 'uncertain'
```

---

## Recommendations by Variant Status

### If Zombie Variant Detected

1. **Don't trust the BSR** - It's shared with better-selling variants
2. **Check the dominant variant** - That's the real opportunity
3. **Consider if your variant is viable** - Maybe this color/size just doesn't sell
4. **Look at review content** - Are buyers asking for this variant?

### If Strong Variant

1. **BSR is meaningful** - This variant contributes significantly
2. **Standard validation applies** - Proceed with other checks
3. **Monitor variant competition** - Other sellers may target same variant

---

## Output Example

```json
{
  "is_variant": true,
  "parent_asin": "B0PARENT123",
  "variant_analysis": {
    "variant_reviews": 45,
    "parent_reviews": 892,
    "share_percentage": 5.04,
    "classification": "zombie_variant",
    "attributes": {
      "color": "Pink",
      "size": "Small"
    },
    "color_potential": "low_potential",
    "size_potential": "low_potential"
  },
  "recommendation": "This variant has only 5% of parent reviews. The BSR is misleading - actual demand for this specific variant is low. Consider the dominant variant instead."
}
```
