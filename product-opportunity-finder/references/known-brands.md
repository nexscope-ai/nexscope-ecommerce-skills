# Known Brands Database

## Purpose

Track well-known brands by category to calculate **Brand Dominance** score.

If known brands occupy most of the top 10 search results, new sellers face significant barriers.

---

## Brand Lists by Category

### Beverages

#### Kombucha
```python
KOMBUCHA_BRANDS = [
    'health-ade', 'health ade',
    'gt', "gt's",
    'synergy',
    'kevita',
    'brew dr',
    'humm',
    'remedy',
    'teazen',
    'wild tonic',
    'revive'
]
```

#### Lemon Juice
```python
LEMON_JUICE_BRANDS = [
    'realemon',
    'nellie & joe',
    'lakewood',
    'santa cruz',
    'italian volcano',
    'lucy\'s'
]
```

#### Coffee
```python
COFFEE_BRANDS = [
    'starbucks',
    'folgers',
    'dunkin',
    'peet\'s',
    'lavazza',
    'illy',
    'death wish',
    'kicking horse',
    'gevalia'
]
```

---

### Home & Kitchen

#### Coffee Mugs/Cups
```python
COFFEE_CUP_BRANDS = [
    'yeti',
    'hydroflask', 'hydro flask',
    'stanley',
    'contigo',
    'ember',
    'tervis',
    'zojirushi'
]
```

#### Kitchen Appliances
```python
KITCHEN_BRANDS = [
    'cuisinart',
    'kitchenaid',
    'ninja',
    'instant pot',
    'hamilton beach',
    'breville',
    'vitamix',
    'keurig'
]
```

---

### Electronics

#### Phone Accessories
```python
PHONE_ACCESSORY_BRANDS = [
    'anker',
    'otterbox',
    'spigen',
    'belkin',
    'zagg',
    'mophie',
    'ugreen'
]
```

#### Audio
```python
AUDIO_BRANDS = [
    'sony',
    'bose',
    'jbl',
    'beats',
    'sennheiser',
    'apple',
    'samsung',
    'jabra'
]
```

---

### Health & Personal Care

#### Supplements
```python
SUPPLEMENT_BRANDS = [
    'nature made',
    'garden of life',
    'now foods',
    'nature\'s bounty',
    'solgar',
    'pure encapsulations',
    'thorne',
    'life extension'
]
```

#### Skincare
```python
SKINCARE_BRANDS = [
    'cerave',
    'neutrogena',
    'la roche-posay',
    'the ordinary',
    'olay',
    'aveeno',
    'eucerin',
    'cetaphil'
]
```

---

### Sports & Outdoors

#### Fitness Equipment
```python
FITNESS_BRANDS = [
    'bowflex',
    'peloton',
    'rogue',
    'titan',
    'cap barbell',
    'nordic track',
    'sunny health'
]
```

#### Outdoor Gear
```python
OUTDOOR_BRANDS = [
    'coleman',
    'rei',
    'patagonia',
    'the north face',
    'osprey',
    'kelty',
    'big agnes'
]
```

---

## Usage

```python
def is_known_brand(brand_name, category_brands):
    """Check if a brand is in the known brands list"""
    if not brand_name:
        return False
    brand_lower = brand_name.lower()
    return any(kb in brand_lower for kb in category_brands)

def calculate_brand_dominance(top10_products, category_brands):
    """Calculate % of top 10 that are known brands"""
    brands = [p.get('brand', '') for p in top10_products]
    known_count = sum(1 for b in brands if is_known_brand(b, category_brands))
    return known_count / len(brands) * 100 if brands else 0
```

---

## Adding New Categories

When evaluating a new category:

1. Search Amazon for the main keyword
2. Note the top 20 sellers by brand
3. Research which are established national/international brands
4. Add to this file

**Criteria for "known brand":**
- National retail presence (Walmart, Target, etc.)
- Significant ad spend
- Brand search volume > 10K/month
- Multiple product lines
