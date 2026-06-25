# Keyword Patterns — Keyword Opportunity Finder v1.0

## Long-Tail Keyword Patterns

Long-tail keywords (3+ words) typically have lower competition and higher conversion rates.

---

## High-Value Patterns

### 1. Product + Audience

```
{product} for {audience}
```

| Example | Why It Works |
|---------|--------------|
| "lunch box for toddlers" | Specific age group |
| "yoga mat for beginners" | Skill level |
| "laptop bag for women" | Gender-specific |
| "running shoes for flat feet" | Physical attribute |

**Detection:**
```python
AUDIENCE_KEYWORDS = [
    'for kids', 'for adults', 'for women', 'for men',
    'for toddlers', 'for babies', 'for seniors',
    'for beginners', 'for professionals',
    'for students', 'for teachers'
]
```

---

### 2. Material + Product

```
{material} {product}
```

| Example | Why It Works |
|---------|--------------|
| "stainless steel lunch box" | Material preference |
| "bamboo cutting board" | Eco-conscious |
| "silicone baking mat" | Specific material |
| "leather laptop sleeve" | Premium material |

**Detection:**
```python
MATERIAL_KEYWORDS = [
    'stainless steel', 'bamboo', 'silicone', 'leather',
    'glass', 'ceramic', 'wood', 'metal', 'plastic',
    'cotton', 'wool', 'nylon', 'polyester'
]
```

---

### 3. Attribute + Product

```
{attribute} {product}
```

| Example | Why It Works |
|---------|--------------|
| "insulated lunch box" | Function-specific |
| "waterproof phone case" | Feature need |
| "portable blender" | Use case |
| "foldable laptop stand" | Space constraint |

**Detection:**
```python
ATTRIBUTE_KEYWORDS = [
    'insulated', 'waterproof', 'portable', 'foldable',
    'wireless', 'rechargeable', 'adjustable', 'compact',
    'large', 'small', 'mini', 'extra large',
    'lightweight', 'heavy duty', 'professional'
]
```

---

### 4. Product + Feature

```
{product} with {feature}
```

| Example | Why It Works |
|---------|--------------|
| "lunch box with compartments" | Specific feature |
| "backpack with laptop sleeve" | Integrated feature |
| "water bottle with straw" | Convenience feature |
| "phone case with card holder" | Multi-function |

**Detection:**
```python
FEATURE_INDICATORS = ['with', 'including', 'and', 'plus']
```

---

### 5. Problem-Based Keywords

```
{solution} {product}
```

| Example | Pain Point |
|---------|------------|
| "leak proof lunch container" | Spilling |
| "non-slip yoga mat" | Slipping |
| "quiet keyboard" | Noise |
| "tangle-free earbuds" | Tangling |

**Detection:**
```python
PROBLEM_SOLUTIONS = [
    'leak proof', 'spill proof', 'non-slip', 'anti-slip',
    'quiet', 'silent', 'noise cancelling',
    'tangle-free', 'no tangle', 'wireless',
    'odor-free', 'stain-resistant', 'scratch-proof'
]
```

---

### 6. Use Case Keywords

```
{product} for {use_case}
```

| Example | Use Case |
|---------|----------|
| "lunch box for meal prep" | Activity |
| "bag for gym" | Location |
| "shoes for hiking" | Activity |
| "laptop for video editing" | Task |

**Detection:**
```python
USE_CASES = [
    'for work', 'for school', 'for travel', 'for gym',
    'for meal prep', 'for camping', 'for hiking',
    'for home', 'for office', 'for outdoor'
]
```

---

### 7. Comparison Keywords

```
{product A} vs {product B}
best {product} {year}
```

| Example | Intent |
|---------|--------|
| "yeti vs hydroflask" | Brand comparison |
| "airpods vs galaxy buds" | Product comparison |
| "best laptop 2026" | Best-in-class |

**Detection:**
```python
COMPARISON_SIGNALS = [
    ' vs ', ' versus ', ' or ', ' compared to ',
    'best', 'top 10', 'top 5', 'review'
]
```

---

## Pattern Combination Matrix

High-value keywords often combine multiple patterns:

| Combination | Example | Value |
|-------------|---------|-------|
| Material + Audience | "stainless steel lunch box for kids" | ⭐⭐⭐ |
| Problem + Audience | "leak proof lunch box for toddlers" | ⭐⭐⭐ |
| Attribute + Material | "insulated stainless steel bottle" | ⭐⭐⭐ |
| Feature + Use Case | "lunch box with compartments for work" | ⭐⭐⭐ |

---

## Pattern Detection Code

```python
def extract_keyword_patterns(keyword):
    kw_lower = keyword.lower()
    patterns = []
    
    # Check audience
    for audience in AUDIENCE_KEYWORDS:
        if audience in kw_lower:
            patterns.append(('audience', audience))
    
    # Check material
    for material in MATERIAL_KEYWORDS:
        if material in kw_lower:
            patterns.append(('material', material))
    
    # Check attribute
    for attr in ATTRIBUTE_KEYWORDS:
        if attr in kw_lower:
            patterns.append(('attribute', attr))
    
    # Check problem/solution
    for solution in PROBLEM_SOLUTIONS:
        if solution in kw_lower:
            patterns.append(('problem', solution))
    
    # Check use case
    for use_case in USE_CASES:
        if use_case in kw_lower:
            patterns.append(('use_case', use_case))
    
    # Check comparison
    for signal in COMPARISON_SIGNALS:
        if signal in kw_lower:
            patterns.append(('comparison', signal))
    
    return {
        'patterns': patterns,
        'pattern_count': len(patterns),
        'is_long_tail': len(keyword.split()) >= 3,
        'specificity_score': len(patterns) * 10  # More patterns = more specific
    }
```

---

## Pattern-Based Opportunity Finding

```python
def find_pattern_gaps(keywords, seed_product):
    """
    Find underserved pattern combinations
    """
    # Count existing patterns
    pattern_counts = defaultdict(int)
    for kw in keywords:
        patterns = extract_keyword_patterns(kw)
        for pattern_type, _ in patterns['patterns']:
            pattern_counts[pattern_type] += 1
    
    # Identify gaps
    all_patterns = ['audience', 'material', 'attribute', 'problem', 'use_case']
    gaps = []
    
    for pattern in all_patterns:
        if pattern_counts[pattern] < 3:  # Under-represented
            # Suggest combinations
            if pattern == 'audience':
                for aud in AUDIENCE_KEYWORDS[:5]:
                    gaps.append(f"{seed_product} {aud}")
            elif pattern == 'problem':
                for prob in PROBLEM_SOLUTIONS[:5]:
                    gaps.append(f"{prob} {seed_product}")
    
    return gaps
```

---

## Seasonal Pattern Keywords

| Pattern | Peak | Examples |
|---------|------|----------|
| "back to school {product}" | Jul-Aug | lunch box, backpack |
| "christmas {product}" | Nov-Dec | gift set, decoration |
| "summer {product}" | May-Jul | cooler, outdoor |
| "winter {product}" | Nov-Feb | gloves, heater |
| "spring {product}" | Mar-May | garden, cleaning |
