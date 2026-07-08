# Metrics Logic — Market Overview v1.0

## Overview

Market Overview calculates 6 key metric categories:

| Category | Primary Metrics |
|----------|-----------------|
| 1. Market Size | Revenue, Units, Products, Brands |
| 2. Growth Rate | MoM%, YoY%, CMGR |
| 3. Price Segments | Revenue by tier, Share, Competition |
| 4. Market Share | CR5, HHI, Top player dominance |
| 5. Seasonality | Index, Peak month, Current position |
| 6. Competition | Seller trends, Entry barriers |

---

## 1. Market Size Calculation

### Total Market Revenue

**Source:** JS Product DB (sum) or JS Segments (direct)

```python
def calculate_market_size(products):
    """Calculate total market metrics from product data"""
    
    # Revenue
    total_revenue = sum(p.get('approximate_30_day_revenue', 0) for p in products)
    
    # Units
    total_units = sum(p.get('approximate_30_day_units', 0) for p in products)
    
    # Product count
    product_count = len(products)
    
    # Brand count
    brands = set(p.get('brand', 'Unknown') for p in products)
    brand_count = len(brands)
    
    # Average metrics
    avg_price = total_revenue / total_units if total_units > 0 else 0
    avg_reviews = mean(p.get('reviews', 0) for p in products)
    
    return {
        'total_revenue': total_revenue,
        'total_units': total_units,
        'product_count': product_count,
        'brand_count': brand_count,
        'avg_price': avg_price,
        'avg_reviews': avg_reviews
    }
```

### Market Size Classification

| Monthly Revenue | Classification | Description |
|-----------------|----------------|-------------|
| > $10M | 🔥 Massive | Major category |
| $5M - $10M | 📈 Large | Significant market |
| $1M - $5M | 📊 Medium | Solid opportunity |
| $500K - $1M | 📉 Small | Niche market |
| < $500K | ⚠️ Micro | Very small |

---

## 2. Growth Rate Calculation

### Month-over-Month (MoM) Growth

**Source:** JS Sales Estimates (daily → monthly aggregation)

```python
def calculate_mom_growth(daily_sales):
    """Calculate MoM growth from daily sales data"""
    
    # Aggregate to monthly
    monthly = {}
    for record in daily_sales:
        month = record['date'][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + record['estimated_units_sold']
    
    # Sort months
    sorted_months = sorted(monthly.keys())
    
    if len(sorted_months) < 2:
        return None
    
    current = monthly[sorted_months[-1]]
    previous = monthly[sorted_months[-2]]
    
    if previous == 0:
        return None
    
    mom_growth = (current - previous) / previous * 100
    return round(mom_growth, 1)
```

### Year-over-Year (YoY) Growth

```python
def calculate_yoy_growth(daily_sales):
    """Calculate YoY growth comparing same month last year"""
    
    monthly = aggregate_to_monthly(daily_sales)
    sorted_months = sorted(monthly.keys())
    
    if len(sorted_months) < 12:
        return None
    
    current_month = sorted_months[-1]
    same_month_last_year = current_month[:4] + str(int(current_month[:4]) - 1) + current_month[4:]
    
    if same_month_last_year not in monthly:
        return None
    
    current = monthly[current_month]
    last_year = monthly[same_month_last_year]
    
    if last_year == 0:
        return None
    
    yoy_growth = (current - last_year) / last_year * 100
    return round(yoy_growth, 1)
```

### Compound Monthly Growth Rate (CMGR)

```python
def calculate_cmgr(monthly_data, months=12):
    """Calculate compound monthly growth rate"""
    
    sorted_months = sorted(monthly_data.keys())
    
    if len(sorted_months) < months:
        return None
    
    start_value = monthly_data[sorted_months[-months]]
    end_value = monthly_data[sorted_months[-1]]
    
    if start_value <= 0:
        return None
    
    cmgr = ((end_value / start_value) ** (1 / months) - 1) * 100
    return round(cmgr, 2)
```

### Growth Classification

| YoY Growth | Classification | Signal |
|------------|----------------|--------|
| > 50% | 🚀 Hypergrowth | Emerging market |
| 20% - 50% | 📈 Fast growth | Growing opportunity |
| 5% - 20% | 📊 Moderate | Healthy market |
| -5% - 5% | ➡️ Stable | Mature market |
| -20% - -5% | 📉 Declining | Caution needed |
| < -20% | 💀 Collapsing | Avoid |

---

## 3. Price Segment Analysis

### Segment Definition

```python
DEFAULT_SEGMENTS = {
    'Budget': (0, 15),
    'Value': (15, 25),
    'Mid': (25, 40),
    'Premium': (40, 60),
    'Luxury': (60, float('inf'))
}

def analyze_price_segments(products, segments=DEFAULT_SEGMENTS):
    """Analyze market by price segment"""
    
    results = {}
    total_revenue = sum(p.get('approximate_30_day_revenue', 0) for p in products)
    
    for name, (low, high) in segments.items():
        segment_products = [
            p for p in products 
            if low <= p.get('price', 0) < high
        ]
        
        if not segment_products:
            continue
        
        segment_revenue = sum(p.get('approximate_30_day_revenue', 0) for p in segment_products)
        segment_reviews = mean(p.get('reviews', 0) for p in segment_products)
        
        results[name] = {
            'range': f"${low}-{high}" if high < float('inf') else f"${low}+",
            'product_count': len(segment_products),
            'revenue': segment_revenue,
            'share': segment_revenue / total_revenue * 100 if total_revenue > 0 else 0,
            'avg_price': mean(p.get('price', 0) for p in segment_products),
            'avg_reviews': segment_reviews,
            'competition': classify_competition(segment_reviews)
        }
    
    return results

def classify_competition(avg_reviews):
    if avg_reviews > 500:
        return '🔴 High'
    elif avg_reviews > 100:
        return '🟡 Medium'
    else:
        return '🟢 Low'
```

### Price Trend Analysis

**Source:** Keepa price history

```python
def analyze_price_trend(keepa_price_history, days=90):
    """Analyze price trends from Keepa data"""
    
    if not keepa_price_history or len(keepa_price_history) < 10:
        return None
    
    early = [p['value'] for p in keepa_price_history[:len(keepa_price_history)//3] if p['value'] > 0]
    recent = [p['value'] for p in keepa_price_history[-len(keepa_price_history)//3:] if p['value'] > 0]
    
    if not early or not recent:
        return None
    
    early_avg = mean(early)
    recent_avg = mean(recent)
    
    change_pct = (recent_avg - early_avg) / early_avg * 100
    
    return {
        'early_avg': early_avg,
        'recent_avg': recent_avg,
        'change_pct': round(change_pct, 1),
        'trend': classify_price_trend(change_pct)
    }

def classify_price_trend(change_pct):
    if change_pct < -15:
        return '📉 Price war'
    elif change_pct < -5:
        return '⬇️ Declining'
    elif change_pct > 15:
        return '📈 Rising'
    elif change_pct > 5:
        return '⬆️ Increasing'
    else:
        return '➡️ Stable'
```

---

## 4. Market Share Analysis

### CR5 (Concentration Ratio)

```python
def calculate_cr5(products):
    """Calculate top 5 brands' market share"""
    
    # Aggregate revenue by brand
    brand_revenue = {}
    for p in products:
        brand = p.get('brand', 'Unknown')
        revenue = p.get('approximate_30_day_revenue', 0)
        brand_revenue[brand] = brand_revenue.get(brand, 0) + revenue
    
    # Sort and get top 5
    sorted_brands = sorted(brand_revenue.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_brands[:5]
    
    total_revenue = sum(brand_revenue.values())
    top_5_revenue = sum(r for _, r in top_5)
    
    cr5 = top_5_revenue / total_revenue * 100 if total_revenue > 0 else 0
    
    return {
        'cr5': round(cr5, 1),
        'top_5_brands': [(b, round(r/total_revenue*100, 1)) for b, r in top_5],
        'interpretation': classify_cr5(cr5)
    }

def classify_cr5(cr5):
    if cr5 > 80:
        return '🔴 Highly concentrated (oligopoly)'
    elif cr5 > 60:
        return '🟡 Moderately concentrated'
    elif cr5 > 40:
        return '🟢 Competitive'
    else:
        return '🟢 Highly competitive (fragmented)'
```

### HHI (Herfindahl-Hirschman Index)

```python
def calculate_hhi(products):
    """Calculate HHI for market concentration"""
    
    # Aggregate revenue by brand
    brand_revenue = {}
    for p in products:
        brand = p.get('brand', 'Unknown')
        revenue = p.get('approximate_30_day_revenue', 0)
        brand_revenue[brand] = brand_revenue.get(brand, 0) + revenue
    
    total_revenue = sum(brand_revenue.values())
    
    if total_revenue == 0:
        return None
    
    # Calculate HHI
    hhi = sum((r / total_revenue * 100) ** 2 for r in brand_revenue.values())
    
    return {
        'hhi': round(hhi, 0),
        'market_type': classify_hhi(hhi),
        'brand_count': len(brand_revenue)
    }

def classify_hhi(hhi):
    if hhi < 1500:
        return '🟢 Competitive market'
    elif hhi < 2500:
        return '🟡 Moderate concentration'
    else:
        return '🔴 Highly concentrated'
```

### Click/Conversion Share Analysis

**Source:** ABA data

```python
def analyze_market_share_aba(aba_data):
    """Analyze market share from ABA click/conversion data"""
    
    # Get latest week's data
    latest_data = get_latest_week(aba_data)
    
    # Aggregate by ASIN
    asin_share = {}
    for record in latest_data:
        asin = record.get('clickedAsin')
        click_share = record.get('clickShare', 0)
        conv_share = record.get('conversionShare', 0)
        
        if asin not in asin_share:
            asin_share[asin] = {'click': 0, 'conversion': 0}
        
        asin_share[asin]['click'] = max(asin_share[asin]['click'], click_share)
        asin_share[asin]['conversion'] = max(asin_share[asin]['conversion'], conv_share)
    
    # Sort by click share
    sorted_asins = sorted(asin_share.items(), key=lambda x: x[1]['click'], reverse=True)
    
    return {
        'top_10': sorted_asins[:10],
        'top1_click_share': sorted_asins[0][1]['click'] * 100 if sorted_asins else 0,
        'monopoly_risk': 'High' if sorted_asins and sorted_asins[0][1]['click'] > 0.3 else 'Low'
    }
```

---

## 5. Seasonality Analysis

### Seasonality Index

**Source:** Keepa 12-month sales or JS Historical search volume

```python
def calculate_seasonality(monthly_data):
    """Calculate seasonality index from monthly data"""
    
    if not monthly_data or len(monthly_data) < 6:
        return None
    
    # Handle both list and dict inputs
    if isinstance(monthly_data, dict):
        values = list(monthly_data.values())
    else:
        values = monthly_data
    
    # Filter out zeros
    valid_values = [v for v in values if v > 0]
    
    if len(valid_values) < 6:
        return None
    
    peak = max(valid_values)
    trough = min(valid_values)
    
    if trough == 0:
        return None
    
    seasonality_index = peak / trough
    peak_month = values.index(peak) + 1 if isinstance(monthly_data, list) else list(monthly_data.keys())[list(monthly_data.values()).index(peak)]
    
    current_month = datetime.now().month
    current_value = values[current_month - 1] if isinstance(monthly_data, list) else monthly_data.get(current_month, peak)
    current_pct = current_value / peak * 100
    
    return {
        'index': round(seasonality_index, 2),
        'peak_month': peak_month,
        'current_pct_of_peak': round(current_pct, 1),
        'classification': classify_seasonality(seasonality_index)
    }

def classify_seasonality(index):
    if index < 1.5:
        return '🟢 Year-round demand'
    elif index < 3.0:
        return '🟡 Moderate seasonality'
    else:
        return '🔴 Highly seasonal'
```

### Trend Detection from ABA

**Source:** ABA search frequency rank

```python
def detect_trend_aba(aba_weekly_data, weeks=12):
    """Detect market trend from ABA search rank data"""
    
    # Lower rank = more popular
    sorted_data = sorted(aba_weekly_data, key=lambda x: x['reportStartDate'])
    
    if len(sorted_data) < weeks:
        return None
    
    early_ranks = [d['searchFrequencyRank'] for d in sorted_data[:weeks//2]]
    recent_ranks = [d['searchFrequencyRank'] for d in sorted_data[-weeks//2:]]
    
    early_avg = mean(early_ranks)
    recent_avg = mean(recent_ranks)
    
    # Improvement = rank decreased (got better)
    improvement_pct = (early_avg - recent_avg) / early_avg * 100
    
    return {
        'early_avg_rank': round(early_avg, 0),
        'recent_avg_rank': round(recent_avg, 0),
        'improvement_pct': round(improvement_pct, 1),
        'trend': classify_trend(improvement_pct)
    }

def classify_trend(improvement_pct):
    if improvement_pct > 20:
        return '🚀 Rising fast'
    elif improvement_pct > 5:
        return '📈 Growing'
    elif improvement_pct > -5:
        return '➡️ Stable'
    elif improvement_pct > -20:
        return '📉 Declining'
    else:
        return '💀 Falling fast'
```

---

## 6. Competitive Landscape

### Seller Trend Analysis

**Source:** Keepa seller count

```python
def analyze_seller_trend(keepa_seller_data, days=90):
    """Analyze seller count trends"""
    
    if not keepa_seller_data or len(keepa_seller_data) < 10:
        return None
    
    third = len(keepa_seller_data) // 3
    early = [p['value'] for p in keepa_seller_data[:third] if p['value'] > 0]
    recent = [p['value'] for p in keepa_seller_data[-third:] if p['value'] > 0]
    
    if not early or not recent:
        return None
    
    early_avg = mean(early)
    recent_avg = mean(recent)
    
    change_pct = (recent_avg - early_avg) / early_avg * 100
    
    return {
        'early_sellers': round(early_avg, 0),
        'recent_sellers': round(recent_avg, 0),
        'change_pct': round(change_pct, 1),
        'dynamics': classify_seller_dynamics(change_pct)
    }

def classify_seller_dynamics(change_pct):
    if change_pct > 30:
        return '🔴 Sellers flooding in'
    elif change_pct > 10:
        return '🟡 Competition increasing'
    elif change_pct < -10:
        return '🟢 Competition easing'
    else:
        return '➡️ Stable'
```

### Entry Barrier Assessment

```python
def assess_entry_barriers(market_data):
    """Assess barriers to market entry"""
    
    barriers = []
    
    # Review barrier
    avg_reviews = market_data.get('avg_reviews', 0)
    if avg_reviews > 1000:
        barriers.append('🔴 High review count (>1000 avg)')
    elif avg_reviews > 500:
        barriers.append('🟡 Moderate review count (500-1000)')
    
    # Brand concentration
    cr5 = market_data.get('cr5', 0)
    if cr5 > 70:
        barriers.append('🔴 Brand dominance (CR5 > 70%)')
    elif cr5 > 50:
        barriers.append('🟡 Some brand concentration')
    
    # Price competition
    price_trend = market_data.get('price_trend_pct', 0)
    if price_trend < -10:
        barriers.append('🔴 Price war in progress')
    
    # Amazon presence
    amz_pct = market_data.get('amazon_seller_pct', 0)
    if amz_pct > 20:
        barriers.append('🔴 Amazon directly competing')
    
    # Seller growth
    seller_change = market_data.get('seller_change_pct', 0)
    if seller_change > 30:
        barriers.append('🟡 Many new entrants')
    
    return {
        'barriers': barriers,
        'overall': 'High' if len([b for b in barriers if '🔴' in b]) >= 2 else 'Medium' if barriers else 'Low'
    }
```

---

## Summary Metrics Card

```python
def generate_summary_card(all_metrics):
    """Generate executive summary card"""
    
    return {
        'market_size': {
            'value': format_currency(all_metrics['total_revenue']),
            'class': classify_market_size(all_metrics['total_revenue'])
        },
        'yoy_growth': {
            'value': f"{all_metrics['yoy_growth']:+.1f}%",
            'class': classify_growth(all_metrics['yoy_growth'])
        },
        'cr5': {
            'value': f"{all_metrics['cr5']:.1f}%",
            'class': classify_cr5(all_metrics['cr5'])
        },
        'hhi': {
            'value': f"{all_metrics['hhi']:.0f}",
            'class': classify_hhi(all_metrics['hhi'])
        },
        'seasonality': {
            'value': f"{all_metrics['seasonality_index']:.1f}x",
            'class': classify_seasonality(all_metrics['seasonality_index'])
        },
        'market_type': determine_market_type(all_metrics)
    }

def determine_market_type(metrics):
    """Determine overall market type"""
    
    growth = metrics.get('yoy_growth', 0)
    cr5 = metrics.get('cr5', 50)
    
    if growth > 30 and cr5 < 50:
        return '🚀 Emerging'
    elif growth > 10:
        return '📈 Growing'
    elif growth > -5 and cr5 > 60:
        return '📊 Mature'
    elif growth < -10:
        return '📉 Declining'
    else:
        return '➡️ Stable'
```
