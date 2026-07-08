# Seasonality Analysis — Product Validator v1.2

## Why Seasonality Matters

BSR data without seasonal context can be misleading:
- A "declining" product might just be entering off-season
- A "rising" product might just be riding seasonal peak
- High BSR volatility could be normal seasonal behavior, not manipulation

---

## Category Seasonal Patterns

### High Seasonality Categories

| Category | Peak Season | Off-Season | Pattern |
|----------|-------------|------------|---------|
| Outdoor/Patio | May-Aug | Nov-Feb | Summer Peak |
| Pool/Water | Jun-Aug | Oct-Mar | Summer Peak |
| Holiday Gifts | Nov-Dec | Jan-Feb | Q4 Spike |
| Toys & Games | Nov-Dec | Jan-Mar | Q4 Spike |
| School Supplies | Jul-Sep | Nov-Jun | Back-to-School |
| Fitness | Jan-Mar | Jun-Aug | New Year |
| Tax/Office | Jan-Apr | May-Dec | Tax Season |
| Garden | Mar-Jun | Oct-Jan | Spring |
| Halloween | Sep-Oct | Nov-Aug | Event |
| Valentine | Jan-Feb | Mar-Dec | Event |

### Low Seasonality Categories

| Category | Notes |
|----------|-------|
| Pet Supplies | Year-round demand |
| Baby Products | Year-round demand |
| Electronics | Slight Q4 boost |
| Kitchen | Year-round, slight holiday boost |
| Health/Personal Care | Year-round |

---

## Seasonality Score Calculation

### Step 1: Detect Seasonal Category

```python
SEASONAL_CATEGORIES = {
    'outdoor': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'pool': {'peak_months': [6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'patio': {'peak_months': [4, 5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'garden': {'peak_months': [3, 4, 5, 6], 'pattern': 'spring', 'volatility': 'high'},
    'christmas': {'peak_months': [11, 12], 'pattern': 'holiday', 'volatility': 'extreme'},
    'halloween': {'peak_months': [9, 10], 'pattern': 'event', 'volatility': 'extreme'},
    'toys': {'peak_months': [11, 12], 'pattern': 'holiday', 'volatility': 'high'},
    'fitness': {'peak_months': [1, 2, 3], 'pattern': 'newyear', 'volatility': 'medium'},
    'school': {'peak_months': [7, 8, 9], 'pattern': 'backtoschool', 'volatility': 'high'},
    'tax': {'peak_months': [1, 2, 3, 4], 'pattern': 'taxseason', 'volatility': 'medium'},
    
    # Low seasonality
    'pet': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'baby': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'kitchen': {'peak_months': [11, 12], 'pattern': 'slight_holiday', 'volatility': 'low'},
    'electronics': {'peak_months': [11, 12], 'pattern': 'slight_holiday', 'volatility': 'low'},
}

def detect_category_seasonality(category_tree, title):
    """Detect seasonality based on category and title keywords"""
    text = (category_tree + ' ' + title).lower()
    
    for keyword, config in SEASONAL_CATEGORIES.items():
        if keyword in text:
            return config
    
    return {'peak_months': [], 'pattern': 'unknown', 'volatility': 'unknown'}
```

### Step 2: Determine Seasonal Position

```python
from datetime import datetime

def get_seasonal_position(peak_months, current_month=None):
    """
    Determine where we are in the seasonal cycle
    
    Returns:
        'peak': Currently in peak season
        'rising': 1-2 months before peak
        'falling': 1-2 months after peak
        'off': Deep off-season
        'stable': No clear seasonality
    """
    if current_month is None:
        current_month = datetime.now().month
    
    if not peak_months:
        return 'stable'
    
    if current_month in peak_months:
        return 'peak'
    
    # Check if approaching peak (within 2 months)
    for pm in peak_months:
        months_until = (pm - current_month) % 12
        if 1 <= months_until <= 2:
            return 'rising'
    
    # Check if just past peak (within 2 months)
    for pm in peak_months:
        months_since = (current_month - pm) % 12
        if 1 <= months_since <= 2:
            return 'falling'
    
    return 'off'
```

### Step 3: Calculate BSR Seasonality Coefficient

```python
def calculate_bsr_seasonality(bsr_history):
    """
    Analyze BSR history for seasonal patterns
    
    High CV (>60%) with regular pattern = seasonal
    High CV (>80%) with irregular pattern = manipulation suspect
    Low CV (<30%) = stable product
    """
    if not bsr_history or len(bsr_history) < 4:
        return {'coefficient': 0, 'pattern': 'insufficient_data'}
    
    # Calculate coefficient of variation
    avg = sum(bsr_history) / len(bsr_history)
    variance = sum((x - avg) ** 2 for x in bsr_history) / len(bsr_history)
    std_dev = variance ** 0.5
    cv = (std_dev / avg) * 100 if avg > 0 else 0
    
    # Detect pattern regularity (simplified)
    # A regular seasonal pattern has predictable ups and downs
    # Irregular = manipulation suspect
    
    if cv < 30:
        return {'coefficient': cv, 'pattern': 'stable'}
    elif cv < 60:
        return {'coefficient': cv, 'pattern': 'moderate_variation'}
    elif cv < 100:
        return {'coefficient': cv, 'pattern': 'high_variation'}
    else:
        return {'coefficient': cv, 'pattern': 'extreme_variation'}
```

---

## Scoring Impact

### Seasonality Modifier (±10 points)

| Scenario | Modifier | Reason |
|----------|----------|--------|
| Off-season + BSR improving | +10 | Strong organic demand |
| Off-season + BSR stable | +5 | Solid year-round product |
| Peak + BSR improving | 0 | Expected, no bonus |
| Peak + BSR declining | -5 | Losing even during peak |
| Falling season + BSR declining | 0 | Expected pattern |
| High seasonality + entering off | -5 | Risk warning |
| Extreme seasonality (event) | -5 | High risk, limited window |

```python
def calculate_seasonality_modifier(seasonal_config, position, bsr_trend):
    """
    Calculate score modifier based on seasonality context
    
    Args:
        seasonal_config: Category seasonality config
        position: Current seasonal position (peak/rising/falling/off/stable)
        bsr_trend: 'improving', 'stable', 'declining'
    
    Returns:
        Modifier value (-10 to +10)
    """
    volatility = seasonal_config.get('volatility', 'unknown')
    
    # Stable categories get no modifier
    if position == 'stable' or volatility == 'low':
        return 0
    
    # Off-season performance is the real test
    if position == 'off':
        if bsr_trend == 'improving':
            return 10  # Excellent - growing even in off-season
        elif bsr_trend == 'stable':
            return 5   # Good - maintaining in off-season
        else:
            return 0   # Expected decline in off-season
    
    # Peak season - don't reward inflated numbers
    if position == 'peak':
        if bsr_trend == 'declining':
            return -5  # Bad - declining during best time
        else:
            return 0   # No bonus for peak performance
    
    # Rising into peak - could be inflated
    if position == 'rising':
        if bsr_trend == 'improving':
            return -3  # Caution - might be seasonal
        else:
            return 0
    
    # Falling from peak - decline is expected
    if position == 'falling':
        if bsr_trend == 'declining':
            return 0   # Expected
        elif bsr_trend == 'stable':
            return 5   # Good - holding post-peak
        else:
            return 8   # Great - growing post-peak
    
    # Extreme seasonality warning
    if volatility == 'extreme':
        return -5
    
    return 0
```

---

## Red Flags

### Seasonal Red Flags

| Flag | Condition | Severity |
|------|-----------|----------|
| 🟡 Peak Season Risk | Currently in peak, data may be inflated | Warning |
| 🟡 Off-Season Entry | Entering off-season, expect BSR decline | Warning |
| 🟡 Extreme Seasonality | Halloween/Christmas category | Warning |
| 🔴 Peak Decline | BSR worsening during peak season | Critical |

```python
def detect_seasonal_flags(seasonal_config, position, bsr_trend):
    """Detect seasonality-related red flags"""
    flags = []
    volatility = seasonal_config.get('volatility', 'unknown')
    pattern = seasonal_config.get('pattern', 'unknown')
    
    # Peak season warning
    if position == 'peak':
        flags.append({
            'flag': 'peak_season',
            'severity': 'warning',
            'detail': f'Currently in peak season ({pattern}), BSR may be inflated'
        })
        
        if bsr_trend == 'declining':
            flags.append({
                'flag': 'peak_decline',
                'severity': 'critical',
                'detail': 'BSR declining during peak season - serious concern'
            })
    
    # Off-season entry warning
    if position == 'falling':
        flags.append({
            'flag': 'entering_offseason',
            'severity': 'warning',
            'detail': 'Entering off-season, expect BSR to worsen'
        })
    
    # Extreme seasonality categories
    if volatility == 'extreme':
        flags.append({
            'flag': 'extreme_seasonality',
            'severity': 'warning',
            'detail': f'Category has extreme seasonality ({pattern}), limited selling window'
        })
    
    return flags
```

---

## Output Format

```json
{
  "seasonality": {
    "category_pattern": "summer",
    "volatility": "high",
    "peak_months": [5, 6, 7, 8],
    "current_position": "off",
    "bsr_seasonality_cv": 45.2,
    "modifier": 10,
    "interpretation": "Strong performance - BSR improving during off-season indicates genuine demand"
  },
  "flags": [
    {
      "flag": "off_season_strength",
      "severity": "positive",
      "detail": "BSR improving in off-season (+10 modifier)"
    }
  ]
}
```

---

## Interpretation Guide

### For Sellers

| Situation | What It Means | Action |
|-----------|---------------|--------|
| Good BSR + Off-season | Genuinely strong product | Confident to proceed |
| Good BSR + Peak season | Might be inflated | Wait for post-peak data |
| Bad BSR + Off-season | Expected, not alarming | Check peak performance |
| Bad BSR + Peak season | Serious problem | Avoid |

### Seasonal Risk Assessment

```
Low Risk:    Stable category OR off-season strength
Medium Risk: Moderate seasonality with good post-peak data
High Risk:   Peak-only performance OR extreme seasonality
```
