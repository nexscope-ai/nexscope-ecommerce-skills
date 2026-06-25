# Buy Box Analysis — Product Validator v1.0

## Why Buy Box Matters

Even with a great product:
- If Amazon holds 90% of Buy Box → You won't get sales
- If one seller dominates → Price competition will hurt margins
- If no rotation → Market is locked

---

## Buy Box Data from Keepa

### Fields Used

| Field | Description |
|-------|-------------|
| `buyBoxSellerIdHistory` | Array of seller IDs who won Buy Box |
| `buyBoxPriceHistory` | Corresponding prices |
| `buyBoxIsFBA` | FBA vs FBM for each period |

### Extracting Shares

```python
def calculate_buybox_shares(seller_id_history, time_periods):
    """
    Calculate Buy Box share for each seller
    
    Args:
        seller_id_history: List of seller IDs (from Keepa)
        time_periods: Number of time slots to analyze
    
    Returns:
        Dict of seller_id -> share percentage
    """
    # Count occurrences
    seller_counts = {}
    for seller_id in seller_id_history[-time_periods:]:
        if seller_id:
            seller_counts[seller_id] = seller_counts.get(seller_id, 0) + 1
    
    # Calculate percentages
    total = sum(seller_counts.values())
    shares = {sid: count / total * 100 for sid, count in seller_counts.items()}
    
    return shares
```

---

## Risk Levels

### 🔴 Critical Risk (Score: 0)

| Condition | Why It's Bad |
|-----------|--------------|
| Single seller > 70% | Market locked, no room |
| Amazon > 50% | Amazon wins on price/Prime |
| No rotation (1 seller in 30d) | Monopoly |

### 🟡 Warning (Score: 4-7)

| Condition | Concern |
|-----------|---------|
| Top seller 50-70% | Dominant but not locked |
| Amazon 30-50% | Present but not controlling |
| 2-3 unique winners | Limited rotation |

### 🟢 Good (Score: 8-10)

| Condition | Why It's Good |
|-----------|---------------|
| Top seller < 40% | Healthy competition |
| No Amazon presence | Level playing field |
| 5+ unique winners | Active rotation |

---

## Amazon Seller ID Detection

Amazon's seller IDs:
```
ATVPDKIKX0DER (US)
A3P5ROKL5A1OLE (UK)
A1PA6795UKMFR9 (DE)
A13V1IB3VIYZZH (FR)
AN1VRQENFRJN5 (JP)
```

```python
AMAZON_SELLER_IDS = {
    'ATVPDKIKX0DER',  # US
    'A3P5ROKL5A1OLE',  # UK
    'A1PA6795UKMFR9',  # DE
    'A13V1IB3VIYZZH',  # FR
    'AN1VRQENFRJN5',   # JP
}

def is_amazon(seller_id):
    return seller_id in AMAZON_SELLER_IDS
```

---

## Scoring Implementation

```python
def score_buybox(buybox_data):
    """
    Score Buy Box accessibility (0-20)
    
    Components:
    - Dominance (0-10): How concentrated is Buy Box ownership
    - Amazon (0-5): Is Amazon competing
    - Rotation (0-5): How many sellers get Buy Box
    """
    top_share = buybox_data.get('top_seller_share', 50)
    amazon_share = buybox_data.get('amazon_share', 0)
    unique_winners = buybox_data.get('unique_winners', 3)
    
    flags = []
    
    # Dominance score
    if top_share < 40:
        dominance = 10
    elif top_share < 60:
        dominance = 7
    elif top_share < 70:
        dominance = 4
    else:
        dominance = 0
        flags.append({
            'flag': 'buybox_dominated',
            'severity': 'critical',
            'detail': f'Top seller holds {top_share:.0f}% of Buy Box'
        })
    
    # Amazon score
    if amazon_share == 0:
        amazon = 5
    elif amazon_share < 30:
        amazon = 3
    elif amazon_share < 50:
        amazon = 1
    else:
        amazon = 0
        flags.append({
            'flag': 'amazon_dominant',
            'severity': 'critical',
            'detail': f'Amazon holds {amazon_share:.0f}% of Buy Box'
        })
    
    # Rotation score
    if unique_winners >= 5:
        rotation = 5
    elif unique_winners >= 3:
        rotation = 3
    elif unique_winners >= 2:
        rotation = 1
    else:
        rotation = 0
    
    return dominance + amazon + rotation, flags
```

---

## Action Recommendations

| Scenario | Score | Action |
|----------|-------|--------|
| Open market | 15-20 | Proceed normally |
| Moderate concentration | 10-14 | Monitor competition |
| High concentration | 5-9 | Consider differentiation |
| Locked market | 0-4 | Avoid or find different ASIN |
