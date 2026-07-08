# HHI Calculation — Market Share Analyzer

## Herfindahl-Hirschman Index (HHI)

### Formula

```
HHI = Σ (Si)²

Where:
- Si = Market share of firm i (as percentage, 0-100)
- Sum over all firms in the market
```

### Example Calculation

**Market with 5 brands:**
- Brand A: 40% share
- Brand B: 25% share
- Brand C: 15% share
- Brand D: 12% share
- Brand E: 8% share

```
HHI = 40² + 25² + 15² + 12² + 8²
    = 1600 + 625 + 225 + 144 + 64
    = 2,658
```

**Result:** HHI = 2,658 → Highly Concentrated Market

---

## Interpretation Thresholds

| HHI Range | Classification | Market Structure |
|-----------|----------------|------------------|
| 0 - 1,000 | Highly Competitive | Many small players |
| 1,000 - 1,500 | Unconcentrated | Healthy competition |
| 1,500 - 2,500 | Moderately Concentrated | Some dominant players |
| 2,500 - 5,000 | Highly Concentrated | Few major players |
| 5,000 - 10,000 | Near Monopoly | 1-2 dominant players |
| 10,000 | Perfect Monopoly | Single player = 100% |

---

## Special Cases

### Perfect Competition
```
100 brands × 1% each = 100 × 1² = 100 HHI
```

### Duopoly (50/50)
```
2 brands × 50% each = 2 × 50² = 5,000 HHI
```

### Monopoly
```
1 brand × 100% = 100² = 10,000 HHI
```

---

## Equivalent Number of Firms

The "equivalent number" represents how many equal-sized firms would produce the same HHI:

```
N_equivalent = 10,000 / HHI
```

| HHI | Equivalent Firms |
|-----|------------------|
| 10,000 | 1 |
| 5,000 | 2 |
| 2,500 | 4 |
| 2,000 | 5 |
| 1,000 | 10 |
| 500 | 20 |

---

## Python Implementation

```python
def calculate_hhi(market_shares: list[float]) -> int:
    """
    Calculate Herfindahl-Hirschman Index
    
    Args:
        market_shares: List of market shares as percentages (0-100)
                       Must sum to ~100
    
    Returns:
        HHI value (0-10000)
    """
    # Validate input
    total = sum(market_shares)
    if abs(total - 100) > 1:
        # Normalize if not summing to 100
        market_shares = [s * 100 / total for s in market_shares]
    
    hhi = sum(share ** 2 for share in market_shares)
    return round(hhi)


def classify_hhi(hhi: int) -> dict:
    """
    Classify market based on HHI
    """
    if hhi < 1000:
        return {
            'level': 'HIGHLY_COMPETITIVE',
            'emoji': '🟢',
            'description': 'Many small players, easy entry'
        }
    elif hhi < 1500:
        return {
            'level': 'UNCONCENTRATED',
            'emoji': '🟢',
            'description': 'Healthy competition'
        }
    elif hhi < 2500:
        return {
            'level': 'MODERATE',
            'emoji': '🟡',
            'description': 'Some dominant players, differentiation needed'
        }
    elif hhi < 5000:
        return {
            'level': 'CONCENTRATED',
            'emoji': '🔴',
            'description': 'Few major players dominate'
        }
    else:
        return {
            'level': 'NEAR_MONOPOLY',
            'emoji': '⛔',
            'description': 'Market dominated by 1-2 players'
        }
```

---

## Revenue-Based vs Unit-Based HHI

### Revenue-Based (Recommended)
```python
brand_revenue = brand_sales * brand_avg_price
total_revenue = sum(all_brand_revenues)
brand_share = brand_revenue / total_revenue * 100
```

**Why:** Captures economic importance, accounts for premium vs budget positioning.

### Unit-Based
```python
brand_units = brand_sales
total_units = sum(all_brand_units)
brand_share = brand_units / total_units * 100
```

**When to use:** Commodity markets where price is uniform.

---

## Delta HHI (Merger Analysis)

When analyzing impact of brand consolidation:

```
ΔHHI = 2 × S1 × S2

Where S1, S2 are the shares of merging entities
```

| ΔHHI | Regulatory Concern |
|------|-------------------|
| < 100 | Unlikely concern |
| 100-200 | Moderate scrutiny |
| > 200 | Likely anticompetitive |

---

## Amazon-Specific Adjustments

### Include Amazon Retail
If Amazon sells directly (not marketplace), count as separate brand:
```python
if 'Amazon' in sellers or 'Amazon.com' in sellers:
    amazon_share = calculate_amazon_share(products)
    brands['Amazon Retail'] = amazon_share
```

### Handle Private Label
Group small private labels vs count separately:
```python
# Option 1: Group all private label
private_label_total = sum(shares for b in brands if is_private_label(b))

# Option 2: Count top private labels individually
# More accurate for markets with strong Amazon Basics etc.
```
