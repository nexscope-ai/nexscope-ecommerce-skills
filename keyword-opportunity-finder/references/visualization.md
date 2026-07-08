# Visualization — Keyword Opportunity Finder v1.4

## Chart Types

| # | Chart | Purpose | When to Use |
|---|-------|---------|-------------|
| 1 | Trend Line | 12-month volume + 30-day surge | Rising Trend detected |
| 2 | Radar | Compare keywords across 4 dimensions | 3+ blue ocean keywords |
| 3 | Competition | Rating/brand distribution | Quality Gap detected |

---

## 1. Trend Line Chart

**Purpose:** Visualize 12-month search volume trend with 30-day surge highlight

### When to Generate
- Rising Trend pattern detected (30-day surge > 50%)
- Strong seasonality detected (index > 3x)

### Data Requirements
- JS Historical weekly data (52 weeks)
- Calculate: surge_30d, avg_volume, seasonality

### Code Template

```python
import matplotlib.pyplot as plt
import numpy as np

def generate_trend_chart(keyword, weekly_volumes, output_path):
    """
    Generate 12-month trend line chart
    
    Args:
        keyword: Search term
        weekly_volumes: List of 52 weekly search volumes
        output_path: Where to save the chart
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    
    weeks = list(range(1, len(weekly_volumes) + 1))
    
    # Main line
    ax.plot(weeks, weekly_volumes, color='#2196F3', linewidth=2, label='Weekly Volume')
    ax.fill_between(weeks, weekly_volumes, alpha=0.2, color='#2196F3')
    
    # Highlight last 4 weeks (30-day surge)
    ax.fill_between(weeks[-4:], weekly_volumes[-4:], alpha=0.4, color='#4CAF50', 
                    label='30-Day Surge')
    
    # Calculate and show surge
    last_4 = np.mean(weekly_volumes[-4:])
    prev_4 = np.mean(weekly_volumes[-8:-4])
    surge = (last_4 - prev_4) / prev_4 * 100 if prev_4 > 0 else 0
    
    ax.annotate(f'+{surge:.0f}% SURGE', xy=(len(weeks)-2, max(weekly_volumes[-4:])), 
                fontsize=12, fontweight='bold', color='#4CAF50')
    
    # Average line
    avg = np.mean(weekly_volumes)
    ax.axhline(y=avg, color='#9E9E9E', linestyle='--', linewidth=1, 
               label=f'Avg: {avg:.0f}/week')
    
    # Labels
    ax.set_xlabel('Week')
    ax.set_ylabel('Weekly Search Volume')
    ax.set_title(f'12-Month Search Trend: "{keyword}"', fontweight='bold')
    ax.legend(loc='upper left')
    
    # Seasonality note
    peak = max(weekly_volumes)
    trough = min([v for v in weekly_volumes if v > 0])
    seasonality = peak / trough if trough > 0 else 1
    
    ax.text(0.98, 0.02, f'Seasonality: {seasonality:.1f}x', 
            transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='#FFF9C4', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path
```

### Color Scheme
| Element | Color | Hex |
|---------|-------|-----|
| Main line | Blue | #2196F3 |
| Surge highlight | Green | #4CAF50 |
| Average line | Gray | #9E9E9E |
| Seasonality box | Yellow | #FFF9C4 |

---

## 2. Keyword Comparison Radar

**Purpose:** Compare multiple keywords across 4 scoring dimensions

### When to Generate
- 3+ blue ocean keywords identified
- User needs to choose between opportunities

### Data Requirements
- Normalized scores (0-100) for each keyword:
  - Volume score
  - Difficulty score (inverted: high = low competition)
  - Efficiency score
  - Relevance score

### Code Template

```python
import matplotlib.pyplot as plt
import numpy as np

def generate_radar_chart(keywords_data, output_path):
    """
    Generate keyword comparison radar chart
    
    Args:
        keywords_data: Dict of {keyword: [volume, difficulty, efficiency, relevance]}
        output_path: Where to save the chart
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150, subplot_kw=dict(polar=True))
    
    categories = ['Volume', 'Low Competition', 'Efficiency', 'Value']
    N = len(categories)
    
    # Colors for up to 5 keywords
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63']
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    for i, (keyword, scores) in enumerate(keywords_data.items()):
        values = scores + scores[:1]  # Complete the loop
        ax.plot(angles, values, 'o-', linewidth=2, label=keyword, color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.15, color=colors[i % len(colors)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    
    ax.set_title('Keyword Comparison Radar\n(Higher = Better)', fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.0), fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path
```

### Score Normalization

```python
def normalize_scores(keyword_data):
    """
    Normalize raw data to 0-100 scores for radar chart
    """
    # Volume: 0-50K mapped to 0-100
    volume_score = min(100, keyword_data['volume'] / 500)
    
    # Difficulty: Inverted (low competition = high score)
    # Based on avg_reviews, known_brand_pct, product_count
    difficulty_score = 100 - min(100, keyword_data['avg_reviews'] / 20)
    
    # Efficiency: Based on conversion rate and CPC
    efficiency_score = min(100, keyword_data['conversion_rate'] * 5)
    
    # Relevance: Based on price and repurchase potential
    relevance_score = min(100, keyword_data['avg_price'] * 2)
    
    return [volume_score, difficulty_score, efficiency_score, relevance_score]
```

---

## 3. Competition Distribution Chart

**Purpose:** Show rating and brand distribution for competition analysis

### When to Generate
- Quality Gap pattern detected (30%+ low-rated products)
- Under-optimized Main pattern detected
- Brand analysis shows 60%+ unknown brands

### Data Requirements
- Amazon Search results (top 20 products)
- Rating for each product
- Brand for each product
- Known brands list

### Code Template

```python
import matplotlib.pyplot as plt

def generate_competition_chart(keyword, products, known_brands, output_path):
    """
    Generate competition distribution chart (rating + brand)
    
    Args:
        keyword: Search term
        products: List of product dicts with 'rating' and 'brand'
        known_brands: List of known brand names
        output_path: Where to save the chart
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=150)
    
    # Left: Rating Distribution
    rating_buckets = {'< 3.5\n(Poor)': 0, '3.5-4.0\n(Below Avg)': 0, 
                      '4.0-4.5\n(Good)': 0, '4.5+\n(Excellent)': 0}
    
    for p in products:
        rating = p.get('rating', 0)
        if rating < 3.5:
            rating_buckets['< 3.5\n(Poor)'] += 1
        elif rating < 4.0:
            rating_buckets['3.5-4.0\n(Below Avg)'] += 1
        elif rating < 4.5:
            rating_buckets['4.0-4.5\n(Good)'] += 1
        else:
            rating_buckets['4.5+\n(Excellent)'] += 1
    
    colors = ['#EF5350', '#FFC107', '#8BC34A', '#4CAF50']
    bars = ax1.bar(rating_buckets.keys(), rating_buckets.values(), color=colors)
    
    ax1.set_ylabel('Number of Products')
    ax1.set_title(f'Rating Distribution (Top {len(products)})\n"{keyword}"', fontweight='bold')
    
    # Add value labels
    for bar, count in zip(bars, rating_buckets.values()):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                 str(count), ha='center', va='bottom', fontweight='bold')
    
    # Quality gap annotation
    low_pct = (rating_buckets['< 3.5\n(Poor)'] + rating_buckets['3.5-4.0\n(Below Avg)']) / len(products) * 100
    if low_pct > 30:
        ax1.annotate(f'QUALITY GAP!\n{low_pct:.0f}% below 4.0', 
                     xy=(0.5, max(rating_buckets.values()) + 1), fontsize=10, 
                     ha='center', color='#E53935', fontweight='bold',
                     bbox=dict(boxstyle='round', facecolor='#FFEBEE', alpha=0.8))
    
    # Right: Brand Distribution
    unknown_count = sum(1 for p in products 
                        if not any(kb in p.get('brand', '').lower() for kb in known_brands))
    known_count = len(products) - unknown_count
    
    unknown_pct = unknown_count / len(products) * 100
    known_pct = known_count / len(products) * 100
    
    ax2.pie([unknown_pct, known_pct], 
            labels=['Unknown\nBrands', 'Known\nBrands'],
            autopct='%1.0f%%',
            colors=['#4CAF50', '#9E9E9E'],
            explode=(0.05, 0),
            textprops={'fontsize': 11},
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    
    ax2.set_title(f'Brand Distribution\n"{keyword}"', fontweight='bold')
    
    # Opportunity annotation
    if unknown_pct > 60:
        ax2.text(0.5, -0.15, f'OPPORTUNITY: {unknown_pct:.0f}% unknown brands = Low barrier', 
                 transform=ax2.transAxes, fontsize=10, ha='center',
                 bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path
```

---

## Chart Decision Logic

```python
def should_generate_charts(analysis_results):
    """
    Determine which charts to generate based on analysis results
    """
    charts = []
    
    # Trend chart: Rising Trend or strong seasonality
    if analysis_results.get('surge_30d', 0) > 50:
        charts.append('trend')
    elif analysis_results.get('seasonality', 1) > 3:
        charts.append('trend')
    
    # Radar chart: 3+ blue ocean keywords
    blue_ocean_count = len([kw for kw in analysis_results.get('keywords', []) 
                           if kw.get('score', 0) >= 65])
    if blue_ocean_count >= 3:
        charts.append('radar')
    
    # Competition chart: Quality gap or brand opportunity
    if analysis_results.get('low_rating_pct', 0) > 30:
        charts.append('competition')
    elif analysis_results.get('unknown_brand_pct', 0) > 60:
        charts.append('competition')
    
    return charts
```

---

## Output Guidelines

### Chart Quantity by Analysis Depth

| Depth | Charts | Which Ones |
|-------|--------|------------|
| Quick scan | 0 | Tables only |
| Standard | 1-2 | Trend + Radar |
| Deep dive | 2-3 | All applicable |

### When NOT to Generate Charts

| Scenario | Reason |
|----------|--------|
| No Rising Trend | Trend chart adds no value |
| < 3 blue ocean keywords | Radar not useful |
| Competition evenly distributed | Competition chart not informative |
| Quick scan request | Keep response light |

### File Naming Convention

```
kw_{keyword_slug}_{chart_type}.png

Examples:
kw_hand_spf_trend.png
kw_lunch_box_radar.png
kw_heated_bento_box_competition.png
```

---

## Color Reference

| Purpose | Color | Hex |
|---------|-------|-----|
| Positive/Good | Green | #4CAF50 |
| Neutral | Blue | #2196F3 |
| Warning | Yellow/Orange | #FFC107 / #FF9800 |
| Negative/Poor | Red | #EF5350 |
| Muted/Secondary | Gray | #9E9E9E |
| Highlight box | Light Yellow | #FFF9C4 |
| Success box | Light Green | #E8F5E9 |
| Error box | Light Red | #FFEBEE |
