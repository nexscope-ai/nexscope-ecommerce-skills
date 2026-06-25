# Data Cleaning — Market Overview v1.1

## Problem Statement

Amazon search results for a keyword often include **unrelated products**:

```
Search: "kombucha"

Returns:
├── ✅ Kombucha drinks (intended)
├── ❌ Kombucha gummies (supplement)
├── ❌ Kombucha skincare (beauty)
├── ❌ Brewing kits (tools)
└── ❌ Kombucha powder (different format)
```

**Without cleaning:** Analysis reflects Amazon search competition, NOT the actual product market.

---

## Intent Recognition

### Step 1: Identify Product Intent

When user asks about a market, determine the **core product type**:

| User Query | Intent | Product Type |
|------------|--------|--------------|
| "kombucha market" | Beverage | Liquid drink |
| "yoga mat market" | Fitness equipment | Mat |
| "coffee mug market" | Drinkware | Ceramic/metal cup |
| "vitamin C market" | Supplement | Capsule/tablet |

### Step 2: Define Inclusion/Exclusion Rules

```python
PRODUCT_INTENT_RULES = {
    'kombucha': {
        'type': 'beverage',
        'include_keywords': ['drink', 'bottle', 'oz', 'fl oz', 'pack', 'organic'],
        'exclude_keywords': ['gummy', 'gummies', 'capsule', 'powder', 'cream', 'serum', 
                            'cleanser', 'face', 'skin', 'kit', 'brewing', 'scoby',
                            'starter', 'hydrometer', 'jar'],
        'include_categories': ['Grocery', 'Beverages'],
        'exclude_categories': ['Beauty', 'Health & Household', 'Home & Kitchen']
    },
    'coffee mug': {
        'type': 'drinkware',
        'include_keywords': ['mug', 'cup', 'oz', 'ceramic', 'porcelain'],
        'exclude_keywords': ['warmer', 'coaster', 'holder', 'rack', 'tree'],
        'include_categories': ['Kitchen & Dining'],
        'exclude_categories': ['Electronics']
    },
    # Add more as needed
}
```

---

## Data Cleaning Pipeline

### Pipeline Overview

```
Raw Data (JS/Amazon)
    │
    ▼
┌─────────────────────┐
│ 1. Keyword Match    │ → Title must contain core keyword
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 2. Exclusion Filter │ → Remove by exclude_keywords
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 3. Inclusion Filter │ → Prefer products with include_keywords
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 4. Category Filter  │ → Filter by Amazon category
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 5. Brand Validation │ → Identify known vs unknown brands
└─────────────────────┘
    │
    ▼
Cleaned Data
```

### Implementation

```python
class MarketDataCleaner:
    def __init__(self, keyword, intent_rules=None):
        self.keyword = keyword.lower()
        self.rules = intent_rules or self._detect_intent()
        
    def _detect_intent(self):
        """Auto-detect product intent from keyword"""
        # Check if we have predefined rules
        for key, rules in PRODUCT_INTENT_RULES.items():
            if key in self.keyword:
                return rules
        
        # Default rules
        return {
            'type': 'generic',
            'include_keywords': [],
            'exclude_keywords': [],
            'include_categories': [],
            'exclude_categories': []
        }
    
    def clean(self, products):
        """Main cleaning pipeline"""
        original_count = len(products)
        
        # Step 1: Keyword in title
        products = self._filter_keyword_match(products)
        
        # Step 2: Exclusion filter
        products = self._filter_exclusions(products)
        
        # Step 3: Inclusion boost (don't filter, just flag)
        products = self._flag_inclusions(products)
        
        # Step 4: Category filter
        products = self._filter_categories(products)
        
        # Step 5: Brand validation
        products = self._validate_brands(products)
        
        cleaned_count = len(products)
        
        return products, {
            'original': original_count,
            'cleaned': cleaned_count,
            'removed': original_count - cleaned_count,
            'removal_rate': (original_count - cleaned_count) / original_count * 100
        }
    
    def _filter_keyword_match(self, products):
        """Filter products where title contains the keyword"""
        return [
            p for p in products
            if self.keyword in (p.get('title') or '').lower()
        ]
    
    def _filter_exclusions(self, products):
        """Remove products with exclusion keywords in title"""
        exclude = self.rules.get('exclude_keywords', [])
        if not exclude:
            return products
        
        def should_exclude(title):
            title_lower = title.lower()
            return any(ex in title_lower for ex in exclude)
        
        return [
            p for p in products
            if not should_exclude(p.get('title') or '')
        ]
    
    def _flag_inclusions(self, products):
        """Flag products that strongly match intent"""
        include = self.rules.get('include_keywords', [])
        if not include:
            return products
        
        for p in products:
            title_lower = (p.get('title') or '').lower()
            p['_intent_score'] = sum(1 for inc in include if inc in title_lower)
        
        return products
    
    def _filter_categories(self, products):
        """Filter by Amazon category"""
        include_cats = self.rules.get('include_categories', [])
        exclude_cats = self.rules.get('exclude_categories', [])
        
        if not include_cats and not exclude_cats:
            return products
        
        def category_ok(p):
            cat = p.get('category') or p.get('categories') or ''
            if isinstance(cat, list):
                cat = ' '.join(cat)
            cat_lower = cat.lower()
            
            # Check exclusions first
            if exclude_cats:
                if any(ex.lower() in cat_lower for ex in exclude_cats):
                    return False
            
            # Check inclusions
            if include_cats:
                return any(inc.lower() in cat_lower for inc in include_cats)
            
            return True
        
        return [p for p in products if category_ok(p)]
    
    def _validate_brands(self, products):
        """Add brand validation flags"""
        for p in products:
            brand = p.get('brand') or ''
            p['_brand_type'] = self._classify_brand(brand)
        
        return products
    
    def _classify_brand(self, brand):
        """Classify brand as known, private label, or unknown"""
        if not brand:
            return 'unknown'
        
        brand_lower = brand.lower()
        
        # Check against known brands database
        # (This would be loaded from known-brands.md)
        known_brands = self._get_known_brands()
        
        if any(kb in brand_lower for kb in known_brands):
            return 'known'
        
        # Detect likely private label patterns
        private_label_patterns = [
            'generic', 'basic', 'essentials', 'choice',
            'select', 'value', 'premium'
        ]
        if any(pl in brand_lower for pl in private_label_patterns):
            return 'private_label'
        
        return 'independent'
    
    def _get_known_brands(self):
        """Get known brands for this product type"""
        # Would load from references/known-brands.md
        return []
```

---

## Kombucha-Specific Cleaning

### Problem Analysis

| Search Result | Actual Product | Action |
|---------------|----------------|--------|
| "Kombucha Organic Tea" | ✅ Drink | Keep |
| "Kombucha Gummies 60ct" | ❌ Supplement | Remove |
| "Kombucha Face Cleanser" | ❌ Skincare | Remove |
| "Kombucha Brewing Kit" | ❌ Equipment | Remove |
| "Kombucha SCOBY Starter" | ❌ Ingredient | Remove |
| "Kombucha Powder Sticks" | ⚠️ Different format | Flag/Separate |

### Cleaning Rules

```python
KOMBUCHA_RULES = {
    'type': 'beverage',
    'include_keywords': [
        'drink', 'bottle', 'fl oz', 'oz', 'pack', 'organic',
        'raw', 'probiotic', 'fermented', 'tea', 'cans'
    ],
    'exclude_keywords': [
        # Supplements
        'gummy', 'gummies', 'capsule', 'tablet', 'supplement',
        # Skincare
        'cream', 'serum', 'cleanser', 'face', 'skin', 'lotion', 'moisturizer',
        # Equipment
        'kit', 'brewing', 'scoby', 'starter', 'jar', 'vessel',
        'hydrometer', 'thermometer', 'ph strip',
        # Different formats
        'powder', 'stick', 'instant', 'mix'
    ],
    'include_categories': [
        'Grocery & Gourmet Food',
        'Beverages'
    ],
    'exclude_categories': [
        'Beauty & Personal Care',
        'Health & Household',
        'Home & Kitchen',
        'Sports & Outdoors'
    ],
    'known_brands': [
        'gt', "gt's", 'synergy',
        'health-ade', 'health ade',
        'kevita',
        'humm',
        'brew dr',
        'remedy',
        'wild tonic',
        'revive',
        'buchi'
    ]
}
```

### Before vs After

```python
# Before cleaning
products = 50
brands = ['BoochBod', 'Botanic Tree', 'Brewer's Elite', ...]

# After cleaning
cleaner = MarketDataCleaner('kombucha', KOMBUCHA_RULES)
cleaned, stats = cleaner.clean(products)

# Result
products = 23  # Only actual drinks
brands = ['GT's', 'Health-Ade', 'Kevita', ...]  # Real beverage brands
removal_rate = 54%  # Removed 54% noise
```

---

## Output Transparency

### Always Report Cleaning Stats

```markdown
## 📊 Data Quality

| Metric | Value |
|--------|-------|
| Raw products | 50 |
| After cleaning | 23 |
| Removed | 27 (54%) |

**Removed categories:**
- 12 supplements (gummies/capsules)
- 8 skincare products
- 5 brewing equipment
- 2 other

**Note:** This analysis covers **Amazon kombucha drinks only**, 
not the full retail market (GT's, Health-Ade dominate offline).
```

---

## Category-Specific Rules Database

### How to Add New Categories

```python
# 1. Identify the product type
# 2. Search Amazon, note what irrelevant products appear
# 3. Create include/exclude rules
# 4. Add known brands

NEW_CATEGORY_TEMPLATE = {
    'type': 'product_type',
    'include_keywords': [
        # Words that indicate THIS is the product
    ],
    'exclude_keywords': [
        # Words that indicate WRONG product
    ],
    'include_categories': [
        # Amazon categories to include
    ],
    'exclude_categories': [
        # Amazon categories to exclude
    ],
    'known_brands': [
        # Real market leaders
    ]
}
```

### Common Patterns

| Product Type | Common Noise |
|--------------|--------------|
| Beverage | Gummies, powder, supplements |
| Electronics | Cases, accessories, cables |
| Skincare | Tools, supplements, devices |
| Kitchenware | Accessories, refills, parts |
| Fitness equipment | Accessories, supplements |

---

## Integration with Market Overview

### Updated Flow

```
User: "kombucha market overview"
    │
    ▼
┌─────────────────────┐
│ Intent Recognition  │ → "kombucha" = beverage
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Data Collection     │ → JS, ABA, Keepa...
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ DATA CLEANING       │ → Apply KOMBUCHA_RULES
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Analysis            │ → Size, share, segments...
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Output with caveat  │ → "Amazon drinks only"
└─────────────────────┘
```

### Caveat in Output

Every Market Overview should include:

```markdown
⚠️ **Scope:** This analysis covers **Amazon [product type] sales only**.
Offline retail channels (supermarkets, specialty stores) are not included.
Market leaders like [known brands] may have larger overall market share
than shown here due to their retail presence.
```
