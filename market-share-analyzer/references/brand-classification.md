# Brand Classification — Market Share Analyzer

## Brand Types

| Type | Code | Description | Example |
|------|------|-------------|---------|
| Major Brand | `MAJOR` | Established, recognized nationally/globally | Apple, Nike, Sony |
| Emerging Brand | `EMERGING` | Growing brand, <5 years, gaining share | Anker (early days) |
| Private Label | `PRIVATE` | Store brand or seller-owned | Amazon Basics, Walmart's |
| White Label | `WHITE` | Generic/unbranded or obscure brand | "Brand: Generic" |
| Amazon | `AMAZON` | Amazon's own brands | Amazon Basics, Solimo |

---

## Major Brands by Category

### Electronics & Tech

```python
ELECTRONICS_BRANDS = [
    # Audio
    'bose', 'sony', 'jbl', 'sennheiser', 'beats', 'apple', 'samsung',
    'skullcandy', 'harman kardon', 'bang & olufsen',
    
    # Mobile/Accessories
    'anker', 'belkin', 'mophie', 'otterbox', 'spigen', 'case-mate',
    
    # Computing
    'logitech', 'microsoft', 'razer', 'corsair', 'steelseries',
    'hp', 'dell', 'lenovo', 'asus', 'acer',
    
    # Smart Home
    'ring', 'nest', 'arlo', 'wyze', 'eufy', 'ecobee', 'philips hue',
    
    # TV/Display
    'lg', 'samsung', 'sony', 'vizio', 'tcl', 'hisense',
]
```

### Home & Kitchen

```python
HOME_KITCHEN_BRANDS = [
    # Appliances
    'cuisinart', 'kitchenaid', 'ninja', 'instant pot', 'vitamix',
    'breville', 'hamilton beach', 'black+decker', 'keurig', 'nespresso',
    
    # Cookware
    'all-clad', 'le creuset', 'lodge', 'calphalon', 't-fal', 'rachael ray',
    
    # Organization
    'oxo', 'rubbermaid', 'tupperware', 'pyrex', 'anchor hocking',
    
    # Bedding
    'tempur-pedic', 'casper', 'purple', 'tuft & needle', 'linenspa',
    
    # Cleaning
    'dyson', 'shark', 'bissell', 'irobot', 'hoover', 'eureka',
]
```

### Beauty & Personal Care

```python
BEAUTY_BRANDS = [
    # Skincare
    'cerave', 'neutrogena', 'la roche-posay', 'olay', 'cetaphil',
    'the ordinary', 'drunk elephant', 'tatcha', 'sk-ii',
    
    # Makeup
    'maybelline', 'loreal', 'nyx', 'revlon', 'covergirl', 'elf',
    'mac', 'nars', 'urban decay', 'too faced', 'benefit',
    
    # Hair
    'pantene', 'tresemme', 'dove', 'garnier', 'olaplex', 'moroccanoil',
    'redken', 'paul mitchell', 'chi', 'kenra',
    
    # Fragrance
    'versace', 'dior', 'chanel', 'gucci', 'calvin klein', 'armani',
]
```

### Pet Supplies

```python
PET_BRANDS = [
    # Dog/Cat Food
    'purina', 'blue buffalo', 'hills science diet', 'royal canin',
    'iams', 'pedigree', 'wellness', 'merrick', 'nutro', 'taste of the wild',
    
    # Pet Accessories
    'kong', 'nylabone', 'petsafe', 'furminator', 'frisco',
    'outward hound', 'chuckit', 'starmark',
    
    # Aquarium
    'tetra', 'api', 'fluval', 'marineland', 'penn plax',
]
```

### Sports & Outdoors

```python
SPORTS_BRANDS = [
    # Athletic Wear
    'nike', 'adidas', 'under armour', 'puma', 'reebok', 'new balance',
    'asics', 'brooks', 'saucony', 'lululemon',
    
    # Outdoor Gear
    'coleman', 'the north face', 'patagonia', 'columbia', 'rei',
    'yeti', 'stanley', 'hydro flask', 'nalgene',
    
    # Fitness Equipment
    'bowflex', 'peloton', 'nordictrack', 'sole', 'concept2',
    'theragun', 'trigger point', 'foam roller',
]
```

### Baby & Kids

```python
BABY_BRANDS = [
    # Diapers/Care
    'pampers', 'huggies', 'luvs', 'honest company', 'seventh generation',
    
    # Feeding
    'dr. browns', 'philips avent', 'tommee tippee', 'munchkin', 'nuk',
    
    # Gear
    'graco', 'chicco', 'baby jogger', 'uppababy', 'britax', 'evenflo',
    
    # Toys
    'fisher-price', 'little tikes', 'melissa & doug', 'vtech', 'leapfrog',
]
```

---

## Amazon Private Labels

```python
AMAZON_BRANDS = [
    # Core
    'amazon basics', 'amazon essentials', 'amazon commercial',
    
    # Fashion
    'goodthreads', 'daily ritual', 'lark & ro', 'core 10', 'find.',
    
    # Home
    'solimo', 'presto!', 'mama bear', 'happy belly',
    'rivet', 'stone & beam', 'pinzon',
    
    # Electronics
    'amazon devices', 'fire tv', 'echo', 'kindle', 'eero', 'blink',
    
    # Other
    'wag', 'denali', 'nod by tuft & needle',
]
```

---

## Private Label Detection Logic

```python
def is_private_label(brand: str, seller: str, product_count: int) -> bool:
    """
    Detect if a brand is likely private label / white label
    """
    brand_lower = brand.lower().strip()
    seller_lower = seller.lower().strip()
    
    # Explicit private label indicators
    PRIVATE_INDICATORS = [
        'generic', 'unbranded', 'no brand', 'n/a', 'unknown',
        'oem', 'custom', 'house brand', 'store brand',
    ]
    
    if any(ind in brand_lower for ind in PRIVATE_INDICATORS):
        return True
    
    # Brand name matches seller name (seller's own brand)
    if brand_lower == seller_lower:
        return True
    
    # Brand contains seller name
    if seller_lower in brand_lower or brand_lower in seller_lower:
        return True
    
    # Single-product brand (likely white label)
    if product_count == 1:
        return True  # Or mark as 'LIKELY_PRIVATE'
    
    return False


def classify_brand(brand: str, category: str) -> str:
    """
    Classify brand type
    
    Returns: 'MAJOR', 'AMAZON', 'PRIVATE', 'EMERGING', 'WHITE'
    """
    brand_lower = brand.lower().strip()
    
    # Check Amazon brands
    if brand_lower in [b.lower() for b in AMAZON_BRANDS]:
        return 'AMAZON'
    
    # Check major brands by category
    category_brands = get_category_brands(category)
    if brand_lower in [b.lower() for b in category_brands]:
        return 'MAJOR'
    
    # Check for private label signals
    if is_private_label(brand, '', 0):
        return 'WHITE'
    
    # Default: Emerging or unknown
    return 'EMERGING'
```

---

## Brand Age Detection

```python
from datetime import datetime, timedelta

def get_brand_age(products: list) -> dict:
    """
    Estimate brand age from product listing dates
    
    Returns: {'years': float, 'first_product': 'YYYY-MM-DD', 'is_new_entrant': bool}
    """
    if not products:
        return {'years': None, 'first_product': None, 'is_new_entrant': False}
    
    # Find earliest product launch date
    dates = []
    for p in products:
        available_since = p.get('available_date') or p.get('availableSince')
        if available_since:
            dates.append(available_since)
    
    if not dates:
        return {'years': None, 'first_product': None, 'is_new_entrant': False}
    
    first_date = min(dates)
    years = (datetime.now() - first_date).days / 365.25
    
    return {
        'years': round(years, 1),
        'first_product': first_date.strftime('%Y-%m-%d'),
        'is_new_entrant': years < 2  # Less than 2 years = new entrant
    }
```

---

## Category Detection from Search Results

```python
CATEGORY_KEYWORDS = {
    'electronics': ['wireless', 'bluetooth', 'usb', 'charger', 'cable', 'speaker', 'headphone'],
    'home_kitchen': ['kitchen', 'cookware', 'appliance', 'storage', 'organizer', 'bedding'],
    'beauty': ['skincare', 'makeup', 'cosmetic', 'serum', 'cream', 'shampoo', 'beauty'],
    'pet': ['dog', 'cat', 'pet', 'puppy', 'kitten', 'aquarium', 'fish'],
    'sports': ['fitness', 'workout', 'gym', 'yoga', 'running', 'outdoor', 'camping'],
    'baby': ['baby', 'infant', 'toddler', 'nursery', 'diaper', 'stroller'],
    'toys': ['toy', 'game', 'puzzle', 'lego', 'doll', 'action figure'],
    'health': ['vitamin', 'supplement', 'health', 'medical', 'first aid'],
}

def detect_category(keyword: str, products: list) -> str:
    """
    Detect most likely category from keyword and product data
    """
    keyword_lower = keyword.lower()
    
    # Check keyword against category keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in keyword_lower for kw in keywords):
            return category
    
    # Check product categories/BSR categories
    category_counts = {}
    for p in products:
        cat = p.get('bsr_category', '').lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in cat for kw in keywords):
                category_counts[category] = category_counts.get(category, 0) + 1
    
    if category_counts:
        return max(category_counts, key=category_counts.get)
    
    return 'general'
```
