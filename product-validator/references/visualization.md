# Visualization — Product Validator v1.1

## Chart Overview

| Chart | Type | Purpose | When to Show |
|-------|------|---------|--------------|
| BSR & Price Dual-Axis | Line (dual Y) | Health status at a glance | Always |
| Seller & Stock Monitor | Area + Bar | Competition + supply chain | Always |
| Review Authenticity | Scatter | Detect manipulation | When review data available |

---

## Chart 1: BSR & Price Dual-Axis Trend

**Most Important Chart** — Shows product health instantly.

### Structure

```
┌─────────────────────────────────────────────────────┐
│  BSR & Price Trend (180 Days)                       │
│                                                     │
│  BSR ↓                                    Price ($) │
│  1,000 ┤                              ┌─────── 45   │
│  5,000 ┤        ╭──────╮             ╱        40   │
│ 10,000 ┤   ╭───╯      ╰────────────╯         35   │
│ 20,000 ┤──╯                                   30   │
│ 50,000 ┤  ══════════════════════════════     25   │
│        └───────────────────────────────────────    │
│        Jan  Feb  Mar  Apr  May  Jun  Jul           │
│                                                     │
│        ─── BSR (lower = better)  ═══ Price         │
└─────────────────────────────────────────────────────┘
```

### Key Design Points

1. **BSR Y-axis is INVERTED** — Lower BSR (better rank) appears at TOP
2. **Dual Y-axes** — Left for BSR, Right for Price
3. **Time range** — 90 or 180 days (configurable)

### Health Interpretation

| BSR Trend | Price Trend | Status | Emoji |
|-----------|-------------|--------|-------|
| ↓ Improving | → Stable | ✅ Healthy | 🟢 |
| ↓ Improving | ↑ Rising | ✅ Premium growth | 🟢 |
| → Stable | → Stable | ✅ Mature | 🟢 |
| ↓ Improving | ↓ Declining | ⚠️ Discount-driven | 🟡 |
| ↑ Worsening | ↓ Declining | 🔴 Clearance/Dying | 🔴 |
| Erratic | Any | 🔴 Manipulation | 🔴 |

### Implementation

```python
def generate_bsr_price_chart(bsr_history, price_history, dates):
    """
    Generate dual-axis BSR & Price chart
    
    Args:
        bsr_history: List of BSR values (daily)
        price_history: List of price values (daily)
        dates: List of date strings
    
    Returns:
        Chart specification dict
    """
    return {
        'type': 'dual_axis_line',
        'title': 'BSR & Price Trend',
        'x_axis': {
            'label': 'Date',
            'values': dates
        },
        'y_axis_left': {
            'label': 'BSR Rank',
            'values': bsr_history,
            'inverted': True,  # IMPORTANT: Lower = Top
            'color': '#2E86AB',
            'scale': 'log'  # Log scale for BSR
        },
        'y_axis_right': {
            'label': 'Price ($)',
            'values': price_history,
            'inverted': False,
            'color': '#A23B72',
            'scale': 'linear'
        },
        'annotations': detect_anomalies(bsr_history, price_history)
    }

def detect_anomalies(bsr, price):
    """Mark suspicious patterns on chart"""
    annotations = []
    
    # BSR spike detection
    for i in range(7, len(bsr)):
        week_change = (bsr[i-7] - bsr[i]) / bsr[i-7] * 100 if bsr[i-7] > 0 else 0
        if abs(week_change) > 50:
            annotations.append({
                'index': i,
                'type': 'bsr_spike',
                'label': f'BSR {week_change:+.0f}%'
            })
    
    # Price cliff detection
    for i in range(1, len(price)):
        if price[i-1] > 0:
            change = (price[i] - price[i-1]) / price[i-1] * 100
            if change < -20:
                annotations.append({
                    'index': i,
                    'type': 'price_drop',
                    'label': f'Price {change:.0f}%'
                })
    
    return annotations
```

---

## Chart 2: Seller & Stock Monitor

**Competition Dynamics + Supply Chain Health**

### Structure

```
┌─────────────────────────────────────────────────────┐
│  Competition & Stock Analysis (90 Days)             │
│                                                     │
│  Sellers                                            │
│  20 ┤                     ╭────────────────         │
│  15 ┤              ╭─────╯                          │
│  10 ┤        ╭────╯                                 │
│   5 ┤───────╯                                       │
│   0 ┼───────────────────────────────────────        │
│     │  ▓▓▓     ▓▓▓▓▓       ▓▓▓    ▓▓               │
│     └───────────────────────────────────────        │
│     Jan    Feb    Mar    Apr    May    Jun          │
│                                                     │
│     ─── Seller Count   ▓▓▓ Out of Stock Events     │
└─────────────────────────────────────────────────────┘
```

### Components

| Element | Visual | Data Source |
|---------|--------|-------------|
| Seller trend | Area chart (filled) | `sellerNum` history |
| OOS events | Red bars at bottom | `stockStatus` = -1 or 0 |

### Implementation

```python
def generate_seller_stock_chart(seller_history, stock_history, dates):
    """
    Generate seller count area chart with OOS bar overlay
    """
    # Identify OOS periods
    oos_events = []
    for i, stock in enumerate(stock_history):
        if stock <= 0:
            oos_events.append({
                'index': i,
                'date': dates[i]
            })
    
    return {
        'type': 'area_bar_combo',
        'title': 'Competition & Stock Analysis',
        'x_axis': {'values': dates},
        'area': {
            'label': 'Seller Count',
            'values': seller_history,
            'color': '#4ECDC4',
            'fill_opacity': 0.3
        },
        'bars': {
            'label': 'Out of Stock',
            'events': oos_events,
            'color': '#FF6B6B'
        },
        'metrics': {
            'seller_growth': calculate_growth(seller_history),
            'oos_rate': len(oos_events) / len(stock_history) * 100,
            'oos_streak': max_consecutive_oos(stock_history)
        }
    }

def max_consecutive_oos(stock_history):
    """Find longest OOS streak"""
    max_streak = current = 0
    for stock in stock_history:
        if stock <= 0:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return max_streak
```

### Interpretation

| Seller Trend | OOS Pattern | Meaning |
|--------------|-------------|---------|
| Flat/Slow growth | None | ✅ Stable market |
| Rapid growth | None | ⚠️ Competition incoming |
| Any | Frequent | ⚠️ Supply issues OR opportunity |
| Declining | Frequent | 🔴 Product may be dying |

---

## Chart 3: Review Authenticity Scatter

**Detect Fake Reviews & Listing Merges**

### Structure

```
┌─────────────────────────────────────────────────────┐
│  Review Authenticity Check                          │
│                                                     │
│  Monthly      Normal Zone (1-3% of sales)           │
│  Review    ┌─────────────────────────────┐          │
│  Growth    │    ·                        │          │
│            │  · · ·   ·                  │          │
│   50 ┤     │· · · · · · ·                │          │
│            │ · · · · · · · ·             │          │
│   25 ┤     │· · · · · · · · · ·          │          │
│            └─────────────────────────────┘          │
│    0 ┼─────────────────────────────────────         │
│           │                                         │
│        ⚠️ │  Suspicious: 85 reviews, 500 sales      │
│  -25 ┤    ↓  (17% rate, expected 1-3%)              │
│                                                     │
│      0    500   1000   1500   2000   2500           │
│              Monthly Estimated Sales                │
│                                                     │
│      · Data Point  ─── Expected Zone (1-3%)         │
└─────────────────────────────────────────────────────┘
```

### Logic

**Normal review rate:** 1-3% of monthly sales become reviews

| Review Rate | Classification | Risk |
|-------------|----------------|------|
| 1-3% | ✅ Normal | None |
| 3-5% | 🟡 High engagement | Low |
| 5-10% | 🟡 Suspicious | Medium |
| > 10% | 🔴 Likely manipulation | High |
| Step jump (vertical) | 🔴 Listing merge | Critical |

### Implementation

```python
def generate_review_authenticity_chart(review_history, sales_history, dates):
    """
    Generate scatter plot comparing review growth vs sales
    
    X-axis: Monthly estimated sales
    Y-axis: Monthly review growth
    """
    # Calculate monthly deltas
    monthly_data = []
    for i in range(30, len(review_history), 30):
        review_growth = review_history[i] - review_history[i-30]
        sales_sum = sum(sales_history[i-30:i])
        
        expected_min = sales_sum * 0.01
        expected_max = sales_sum * 0.03
        
        status = 'normal'
        if review_growth > expected_max * 3:
            status = 'suspicious'
        if review_growth > expected_max * 5:
            status = 'manipulation'
        
        monthly_data.append({
            'date': dates[i],
            'sales': sales_sum,
            'reviews': review_growth,
            'expected_min': expected_min,
            'expected_max': expected_max,
            'status': status
        })
    
    # Detect step jumps (vertical clusters)
    step_jumps = detect_step_jumps(review_history)
    
    return {
        'type': 'scatter',
        'title': 'Review Authenticity Check',
        'x_axis': {
            'label': 'Monthly Estimated Sales',
            'scale': 'linear'
        },
        'y_axis': {
            'label': 'Monthly Review Growth',
            'scale': 'linear'
        },
        'data_points': monthly_data,
        'reference_lines': [
            {'slope': 0.01, 'label': '1% (min normal)', 'style': 'dashed'},
            {'slope': 0.03, 'label': '3% (max normal)', 'style': 'dashed'}
        ],
        'step_jumps': step_jumps,
        'verdict': calculate_authenticity_verdict(monthly_data, step_jumps)
    }

def detect_step_jumps(review_history):
    """
    Detect sudden vertical jumps in review count
    (indicates listing merge or mass fake reviews)
    """
    jumps = []
    window = 5  # 5-day window
    
    for i in range(window, len(review_history)):
        jump = review_history[i] - review_history[i-window]
        if jump > 50:  # More than 50 reviews in 5 days
            jumps.append({
                'index': i,
                'magnitude': jump,
                'severity': 'critical' if jump > 100 else 'warning'
            })
    
    return jumps

def calculate_authenticity_verdict(monthly_data, step_jumps):
    """Final authenticity verdict"""
    if step_jumps:
        return {
            'status': 'SUSPICIOUS',
            'reason': f'{len(step_jumps)} step jump(s) detected',
            'flag': 'review_merge'
        }
    
    suspicious_months = sum(1 for m in monthly_data if m['status'] in ['suspicious', 'manipulation'])
    
    if suspicious_months >= len(monthly_data) * 0.3:
        return {
            'status': 'SUSPICIOUS',
            'reason': f'{suspicious_months}/{len(monthly_data)} months show abnormal review velocity',
            'flag': 'review_velocity_mismatch'
        }
    
    return {
        'status': 'NORMAL',
        'reason': 'Review growth matches sales pattern'
    }
```

---

## Chart Selection Logic

```python
def select_charts(product_data, validation_result):
    """
    Determine which charts to generate based on data availability
    and detected issues
    """
    charts = []
    
    # Chart 1: Always show BSR & Price
    if product_data.get('bsr_history') and product_data.get('price_history'):
        charts.append({
            'chart': 'bsr_price_dual',
            'priority': 1,
            'reason': 'Core health indicator'
        })
    
    # Chart 2: Always show if seller/stock data available
    if product_data.get('seller_history') or product_data.get('stock_history'):
        charts.append({
            'chart': 'seller_stock_monitor',
            'priority': 2,
            'reason': 'Competition dynamics'
        })
    
    # Chart 3: Show if review data available or suspicious flags
    review_flags = [f for f in validation_result.get('red_flags', []) 
                   if f['flag'] in ['review_merge', 'suspicious_reviews']]
    
    if product_data.get('review_history') or review_flags:
        charts.append({
            'chart': 'review_authenticity',
            'priority': 3,
            'reason': 'Review verification' + (' (⚠️ flags detected)' if review_flags else '')
        })
    
    return sorted(charts, key=lambda x: x['priority'])
```

---

## Report Integration

### ASCII Fallback (Terminal/Discord)

```
═══════════════════════════════════════════
📈 BSR & PRICE TREND (90 Days)
═══════════════════════════════════════════
BSR:   45K ▃▃▄▅▆▇█████████▇▇▆▆▅▅▄▄▃▃▂▂ 8K ↓ Good
Price: $28 ════════════════════════════ $32 → Stable
Status: 🟢 HEALTHY (improving BSR, stable price)

═══════════════════════════════════════════
👥 COMPETITION & STOCK (90 Days)
═══════════════════════════════════════════
Sellers: 5 ▂▂▃▃▃▄▄▄▅▅▅▅▆▆▆▇▇▇████████ 12 (+140%)
OOS Events: ▓▓▓░░░░░▓▓░░░░░░░░░░░░▓▓░░░░ (8%)
Status: 🟡 CAUTION (sellers increasing)

═══════════════════════════════════════════
⭐ REVIEW AUTHENTICITY
═══════════════════════════════════════════
Reviews/Sales Ratio: 2.1% ✅ Normal (expected: 1-3%)
Step Jumps: None detected ✅
Status: 🟢 AUTHENTIC
```

---

## Output Example

```json
{
  "charts": [
    {
      "chart_type": "bsr_price_dual",
      "title": "BSR & Price Trend (180 Days)",
      "status": "healthy",
      "interpretation": "Improving BSR with stable price indicates organic growth"
    },
    {
      "chart_type": "seller_stock_monitor",
      "title": "Competition & Stock Analysis",
      "status": "caution",
      "interpretation": "Seller count +140% in 90 days, monitor competition"
    },
    {
      "chart_type": "review_authenticity",
      "title": "Review Authenticity Check",
      "status": "normal",
      "interpretation": "Review velocity (2.1%) within normal range"
    }
  ]
}
```
