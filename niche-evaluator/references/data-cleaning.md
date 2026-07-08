# Data Cleaning Reference

## Overview

Jungle Scout search results often contain noise data (accessories, pet versions, unrelated products) that must be cleaned before scoring.

---

## ProductCleaner Class

```python
import re

class ProductCleaner:
    """General-purpose product data cleaner"""
    
    # ========== General Config ==========
    
    # Universal negative words (applies to all categories)
    UNIVERSAL_NEGATIVE = [
        'replacement', 'refill',           # Replacement parts
        'pet', 'dog', 'cat', 'puppy',      # Pet versions
        'golf cart',                        # Golf accessories
    ]
    
    # Accessory suffixes (auto-detected)
    ACCESSORY_SUFFIXES = [
        'bag', 'case', 'strap', 'holder', 'rack', 'stand',
        'cover', 'sleeve', 'carrier', 'organizer', 'storage'
    ]
    
    # ========== Category Config ==========
    
    # Synonym mapping
    SYNONYMS = {
        'sunscreen': ['sunblock', 'sun cream', 'spf lotion'],
        'yoga mat': ['exercise mat', 'fitness mat', 'workout mat'],
        'coffee cup': ['coffee mug', 'coffee tumbler', 'travel mug'],
        'phone holder': ['phone mount', 'phone stand', 'cell phone holder'],
        'laptop stand': ['notebook stand', 'computer stand'],
        'water bottle': ['drink bottle', 'sports bottle'],
    }
    
    # Category-specific negative words
    CATEGORY_CONFIG = {
        'sunscreen': {
            'negative': ['coating', 'film', 'shade', 'window', 'car'],
            'accessory_ok': False,
        },
        'yoga mat': {
            'negative': ['towel', 'block'],
            'accessory_ok': False,
        },
        'coffee cup': {
            'negative': ['warmer', 'maker', 'machine', 'press'],
            'accessory_ok': False,
        },
        'phone holder': {
            'negative': [],
            'accessory_ok': True,  # phone holder is itself an accessory
        },
        'laptop stand': {
            'negative': ['cooling pad', 'lap desk'],
            'accessory_ok': False,
        },
        'water bottle': {
            'negative': ['cap', 'lid', 'brush'],
            'accessory_ok': False,
        },
    }
    
    # ========== Methods ==========
    
    def __init__(self, keyword):
        self.keyword = keyword.lower()
        self.keywords = [self.keyword] + self.SYNONYMS.get(self.keyword, [])
        self.config = self.CATEGORY_CONFIG.get(
            self.keyword, 
            {'negative': [], 'accessory_ok': False}
        )
    
    def is_noise(self, product):
        """
        Determine if the product is noise data.
        Returns: (is_noise: bool, reasons: list)
        """
        title = (product.get('title') or '').lower()
        
        # 1. Must contain keyword or synonym
        if not any(kw in title for kw in self.keywords):
            return True, ['No keyword match']
        
        reasons = []
        
        # 2. Universal negative word check
        for neg in self.UNIVERSAL_NEGATIVE:
            if re.search(r'\b' + re.escape(neg) + r'\b', title):
                reasons.append(f'🚫{neg}')
        
        # 3. Category negative word check
        for neg in self.config.get('negative', []):
            if re.search(r'\b' + re.escape(neg) + r'\b', title):
                reasons.append(f'🚫{neg}')
        
        # 4. Accessory detection (if accessories not allowed)
        if not self.config.get('accessory_ok'):
            for suffix in self.ACCESSORY_SUFFIXES:
                if suffix in title and suffix not in self.keyword:
                    reasons.append(f'📦{suffix}')
                    break
        
        return len(reasons) > 0, reasons
    
    def clean(self, products):
        """
        Clean product list.
        Returns: (cleaned: list, removed: list)
        """
        cleaned, removed = [], []
        for p in products:
            is_noise, reasons = self.is_noise(p)
            if is_noise:
                removed.append({'product': p, 'reasons': reasons})
            else:
                cleaned.append(p)
        return cleaned, removed
```

---

## Usage

### Basic Usage

```python
from data_cleaning import ProductCleaner

# Create cleaner
cleaner = ProductCleaner('sunscreen')

# Clean product list
cleaned, removed = cleaner.clean(products)

print(f"Kept: {len(cleaned)} products")
print(f"Filtered: {len(removed)} noise items")
```

### Check Single Product

```python
cleaner = ProductCleaner('yoga mat')

product = {'title': 'Yoga Mat Bag Carrier with Strap'}
is_noise, reasons = cleaner.is_noise(product)

if is_noise:
    print(f"Noise: {reasons}")  # ['📦bag']
```

---

## Filter Rules

### 1. Keyword Matching

Must contain the main keyword or a synonym:

| Search Term | Synonyms |
|-------------|----------|
| sunscreen | sunblock, sun cream, spf lotion |
| yoga mat | exercise mat, fitness mat |
| coffee cup | coffee mug, coffee tumbler |

### 2. Universal Negative Words

Applied to all categories, auto-filtered:

| Negative Word | Reason |
|---------------|--------|
| pet, dog, cat | Pet version products |
| replacement, refill | Spare parts / consumables |
| golf cart | Golf accessories |

### 3. Category Negative Words

Configured per category:

| Category | Negative Words | Reason |
|----------|----------------|--------|
| sunscreen | coating, film, window | Auto/building film |
| yoga mat | towel, block | Yoga accessories |
| coffee cup | warmer, maker | Coffee machines/heaters |

### 4. Accessory Detection

Auto-detects `{keyword} + accessory word` pattern:

```
yoga mat bag → Filtered (bag is an accessory)
yoga mat strap → Filtered (strap is an accessory)
premium yoga mat → Kept ✅
```

**Exception**: `phone holder` is itself an accessory, set `accessory_ok: True`

---

## Extending Configuration

### Add New Category

```python
# Add to CATEGORY_CONFIG
CATEGORY_CONFIG['air fryer'] = {
    'negative': ['liner', 'rack', 'accessories'],
    'accessory_ok': False,
}

# Add to SYNONYMS
SYNONYMS['air fryer'] = ['air cooker', 'airfryer']
```

### Add Universal Negative Words

```python
UNIVERSAL_NEGATIVE.append('refurbished')  # Refurbished items
UNIVERSAL_NEGATIVE.append('used')         # Used items
```

### Add Accessory Suffixes

```python
ACCESSORY_SUFFIXES.append('mat')      # Mat-type accessories
ACCESSORY_SUFFIXES.append('tray')     # Tray-type accessories
```

---

## Cleaning Example Results

### Sunscreen

| Product | Result | Reason |
|---------|--------|--------|
| Neutrogena SPF 50 Sunscreen | ✅ Kept | - |
| Golf Cart Sunscreen Coating | ❌ Filtered | 🚫golf cart, 🚫coating |
| Pet Dog Sunscreen Spray | ❌ Filtered | 🚫pet, 🚫dog |
| Car Window Sunscreen Film | ❌ Filtered | 🚫window, 🚫film |

### Yoga Mat

| Product | Result | Reason |
|---------|--------|--------|
| Premium Yoga Mat 6mm | ✅ Kept | - |
| Yoga Mat Bag Carrier | ❌ Filtered | 📦bag |
| Yoga Mat Strap | ❌ Filtered | 📦strap |
| Exercise Mat for Home | ✅ Kept | Synonym match |

---

## Output Format

After cleaning:

```markdown
✅ Data Cleaning: 50 → 47 products

Filtered:
  🚫 golf cart | $50K | 10L0L Golf Cart Sunscreen Coating...
  🚫 pet | $9K | Pet Dog Sunscreen Spray...
  📦 bag | $12K | Yoga Mat Bag with Strap...
```

---

## Notes

1. **Word boundary matching**: Uses `\b` to ensure full-word matching
   - "retention" won't match "tent" ✅
   - "car" won't match "skincare" ✅

2. **Synonym maintenance**: Update synonym lists regularly to cover more variants

3. **False positive check**: Review the removed list after cleaning to confirm no false positives

4. **Category expansion**: Test new categories before adding configuration
