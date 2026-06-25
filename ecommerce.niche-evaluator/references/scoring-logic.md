# Scoring Logic v3.0

## Overview

```
Final Score = Base Score (0-100) + Modifiers (-32 to +30)
```

| Component | Range | Source |
|-----------|-------|--------|
| Base Score | 0-100 | 4 dimensions × 25 pts |
| Modifiers | -32 to +30 | 12 factors |

---

## Part 1: Base Score (4 Dimensions)

### 1.1 Demand Score (0-25)

#### Market Size (0-10)

| Total Revenue | Points |
|---------------|--------|
| > $200K | 10 |
| > $100K | 8 |
| > $50K | 6 |
| > $20K | 4 |
| ≤ $20K | 2 |

#### Average Revenue per Product (0-8)

| Avg Revenue | Points |
|-------------|--------|
| > $10K | 8 |
| > $5K | 6 |
| > $3K | 4 |
| > $1K | 2 |
| ≤ $1K | 0 |

#### Trend Direction (0-5)

*Source: Google Trends 30-day data*

| Trend Change | Points |
|--------------|--------|
| > +20% | 5 |
| > +10% | 3 |
| -10% to +10% | 2 |
| < -10% | 0 |
| < -20% | -2 |

#### Seasonality Timing (0-2)

*Source: JS Historical Search Volume*

| Current vs Peak | Points |
|-----------------|--------|
| > 80% of peak | 2 |
| > 50% of peak | 1 |
| < 30% of peak | 0 |

---

### 1.2 Competition Score (0-25)

#### Low-Review Ratio (0-10)

*Products with < 100 reviews = easier to compete*

| Low-Review % | Points |
|--------------|--------|
| > 50% | 10 |
| > 35% | 7 |
| > 20% | 4 |
| ≤ 20% | 2 |

#### Average Reviews (0-8)

| Avg Reviews | Points |
|-------------|--------|
| < 300 | 8 |
| < 700 | 6 |
| < 1500 | 4 |
| ≥ 1500 | 2 |

#### High-Review Dominance (0-4)

*Products with ≥ 1000 reviews = review barrier*

| High-Review % | Points |
|---------------|--------|
| < 15% | 4 |
| < 30% | 2 |
| ≥ 30% | 0 |

#### Brand Dominance (-6 to +3)

*Source: Amazon Search top 10 results*

| Known Brand % | Points | Signal |
|---------------|--------|--------|
| 100% | **-6** | 💀 Brand monopoly |
| ≥ 80% | -4 | 🔴 Heavy brand presence |
| ≥ 60% | -2 | 🟡 Moderate brand presence |
| ≥ 40% | 0 | Balanced |
| < 20% | +2 | 🟢 Low brand presence |

---

### 1.3 Profitability Score (0-25)

#### Profit Margin (0-12)

```python
margin = (price - total_fees - price * 0.3) / price * 100
```

| Margin | Points |
|--------|--------|
| > 35% | 12 |
| > 25% | 9 |
| > 15% | 6 |
| ≤ 15% | 3 |

#### Average Price (0-8)

| Avg Price | Points |
|-----------|--------|
| > $35 | 8 |
| > $20 | 6 |
| > $12 | 4 |
| ≤ $12 | 2 |

#### Price Stability (0-5)

| Price Std Dev | Points |
|---------------|--------|
| < 20% of mean | 5 |
| < 40% of mean | 3 |
| ≥ 40% of mean | 1 |

---

### 1.4 Opportunity Score (0-25)

#### Low-Review Success Rate (0-10)

*Products with < 100 reviews AND > $2K revenue*

| Success Rate | Points |
|--------------|--------|
| > 25% | 10 |
| > 15% | 7 |
| > 8% | 4 |
| ≤ 8% | 2 |

#### Seasonality Index (0-5)

*Lower = more stable year-round demand*

| Seasonality Index | Points |
|-------------------|--------|
| < 1.5 | 5 |
| < 2.5 | 3 |
| < 4.0 | 1 |
| ≥ 4.0 | 0 |

#### TikTok Signal (0-6)

| TikTok 30d Sales | Points |
|------------------|--------|
| > 10K | 4 |
| > 1K | 2 |
| 0 | 0 |
| + Low Amazon competition | +2 |

#### Sponsored % (0-4)

*Source: Amazon Search*

| Sponsored % | Points |
|-------------|--------|
| < 10% | 4 |
| < 20% | 2 |
| < 40% | 0 |
| ≥ 40% | -2 |

---

## Part 2: Modifier Factors (12 Total)

### Original Modifiers (1-8)

#### 1. Rating Quality (-2 to +4)

*Source: JS avg rating*

| Avg Rating | Modifier | Signal |
|------------|----------|--------|
| < 4.0 | **+4** | ✅ Room for improvement |
| 4.0 - 4.2 | +2 | ✅ Some room |
| 4.3 - 4.5 | 0 | ➡️ Normal |
| 4.5 - 4.7 | -1 | 🟡 High bar |
| > 4.7 | **-2** | 🔴 Very hard to beat |

#### 2. Amazon Seller Presence (-6 to 0)

*Source: JS seller_type field*

| Amazon Seller % | Modifier | Signal |
|-----------------|----------|--------|
| 0% | 0 | ✅ No Amazon |
| < 10% | -2 | ⚠️ Amazon present |
| 10-30% | -4 | 🔴 Amazon competing |
| > 30% | **-6** | 💀 **RED LINE** |

#### 3. Market Maturity (-2 to +3)

*Source: Keepa listedSince or JS date_first_available*

| New Product % (< 1 year) | Modifier | Signal |
|--------------------------|----------|--------|
| > 50% | **+3** | 🆕 Emerging market |
| > 30% | +1 | 📈 Growing market |
| Normal | 0 | ➡️ Mature market |
| > 50% products > 5 years | -2 | 🔴 Established market |

#### 4. Logistics Difficulty (-3 to +2)

*Source: Keepa packageWeight/dimensions or category tag*

| Weight/Size | Modifier | Signal |
|-------------|----------|--------|
| Light & small (< 1 lb) | +2 | 🟢 Easy logistics |
| Standard | 0 | ➡️ Normal |
| Heavy (> 5 lb) | -2 | 📦 Heavy item |
| Liquid/Fragile | **-3** | 🔴 Special handling |

#### 5. Price War Risk (-3 to +1)

*Source: JS price distribution*

| Low Price % (< $20) | Modifier | Signal |
|---------------------|----------|--------|
| > 60% | -3 | 🔴 Price war zone |
| > 40% | -2 | ⚠️ Price pressure |
| 20-40% | 0 | ➡️ Normal |
| < 20% | +1 | 🟢 Premium market |

#### 6. Units Analysis (0 to +2)

*Source: JS approximate_30_day_units*

High units + low price = bundle/multi-pack opportunity

| Avg Units | Avg Price | Modifier |
|-----------|-----------|----------|
| > 200 | < $15 | +2 |
| > 100 | < $20 | +1 |
| Otherwise | | 0 |

#### 7. Repurchase Potential (0 to +4) — Manual Tag

| Category Type | Modifier | Examples |
|---------------|----------|----------|
| High-frequency consumable | **+4** | Food, beverages, supplements |
| Regular consumable | +2 | Skincare, pet supplies |
| Occasional repurchase | +1 | Stationery, cleaning |
| One-time purchase | 0 | Furniture, electronics |

#### 8. Compliance Requirements (-4 to +2) — Manual Tag

| Compliance Level | Modifier | Examples |
|------------------|----------|----------|
| No special requirements | +2 | Generic home goods |
| Standard (FCC, etc.) | 0 | Electronics |
| FDA/USDA | -2 | Food, supplements |
| High barrier (UL, CE) | **-4** | Safety equipment |

---

### New v3.0 Modifiers (9-12)

#### 9. BSR Trend (-3 to +4)

*Source: Keepa productSeries bsrMain*

**Logic:** BSR decrease = better rank = sales growing

```python
def bsr_trend_modifier(keepa_history, days=90):
    points = keepa_history.get('bsrMain', [{}])[0].get('points', [])
    early = avg(points[:days//3])
    recent = avg(points[-days//3:])
    change_pct = (early - recent) / early * 100  # Note: decrease = positive
    
    if change_pct > 30: return +4, "🚀 Rapid market growth"
    if change_pct > 15: return +2, "📈 Market growing"
    if change_pct > -15: return 0, "➡️ Stable market"
    if change_pct > -30: return -2, "📉 Market declining"
    return -3, "💀 Market shrinking"
```

| BSR Change | Modifier | Signal |
|------------|----------|--------|
| ↓ > 30% | **+4** | 🚀 Rapid growth |
| ↓ 15-30% | +2 | 📈 Growing |
| ± 15% | 0 | ➡️ Stable |
| ↑ 15-30% | -2 | 📉 Declining |
| ↑ > 30% | **-3** | 💀 Shrinking |

#### 10. Price Trend (-4 to +2)

*Source: Keepa productSeries price*

**Logic:** Price decrease = price war = margin compression

```python
def price_trend_modifier(keepa_history, days=90):
    points = keepa_history.get('price', [])
    early = avg(points[:days//3])
    recent = avg(points[-days//3:])
    change_pct = (recent - early) / early * 100
    
    if change_pct < -20: return -4, "🔴 Intense price war"
    if change_pct < -10: return -2, "⚠️ Price declining"
    if change_pct > 10: return +2, "📈 Price increasing"
    return 0, "➡️ Price stable"
```

| Price Change | Modifier | Signal |
|--------------|----------|--------|
| ↓ > 20% | **-4** | 🔴 Price war |
| ↓ 10-20% | -2 | ⚠️ Price pressure |
| ± 10% | 0 | ➡️ Stable |
| ↑ > 10% | +2 | 📈 Price power |

#### 11. Seller Trend (-3 to +2)

*Source: Keepa productSeries sellerCount*

**Logic:** More sellers = more competition

```python
def seller_trend_modifier(keepa_history, days=90):
    points = keepa_history.get('sellerCount', [])
    early = avg(points[:days//3])
    recent = avg(points[-days//3:])
    change_pct = (recent - early) / early * 100
    
    if change_pct > 50: return -3, "🔴 Seller influx"
    if change_pct > 20: return -1, "⚠️ Sellers increasing"
    if change_pct < -20: return +2, "🟢 Sellers decreasing"
    return 0, "➡️ Sellers stable"
```

| Seller Change | Modifier | Signal |
|---------------|----------|--------|
| ↑ > 50% | **-3** | 🔴 Seller influx |
| ↑ 20-50% | -1 | ⚠️ Competition increasing |
| ± 20% | 0 | ➡️ Stable |
| ↓ > 20% | +2 | 🟢 Competition easing |

#### 12. Pain Point Signal (-2 to +4)

*Source: Amazon Product Detail ratingsDistribution + topReviews*

**Logic:** High negative review % = product problems = improvement opportunity

```python
def pain_point_modifier(amz_detail):
    dist = amz_detail.get('ratingsDistribution', {})
    total = sum(dist.values())
    low_rating_pct = (dist.get('1', 0) + dist.get('2', 0)) / total * 100
    
    if low_rating_pct > 20: return +4, "🎯 Clear pain points"
    if low_rating_pct > 10: return +2, "✅ Room for improvement"
    if low_rating_pct < 5: return -2, "🔴 Mature product"
    return 0, "➡️ Normal"
```

| Low Rating % | Modifier | Signal |
|--------------|----------|--------|
| > 20% | **+4** | 🎯 Clear pain points |
| 10-20% | +2 | ✅ Improvement room |
| 5-10% | 0 | ➡️ Normal |
| < 5% | -2 | 🔴 Hard to beat |

---

## Part 3: Modifier Summary Table

| # | Factor | Range | Source | Auto |
|---|--------|-------|--------|------|
| 1 | ⭐ Rating Quality | -2 ~ +4 | JS | ✅ |
| 2 | 🛒 Amazon Seller | -6 ~ 0 | JS | ✅ |
| 3 | 📅 Market Maturity | -2 ~ +3 | Keepa | ✅ |
| 4 | 📐 Logistics | -3 ~ +2 | Keepa | ✅ |
| 5 | 💰 Price War (static) | -3 ~ +1 | JS | ✅ |
| 6 | 📦 Units Analysis | 0 ~ +2 | JS | ✅ |
| 7 | 🔄 Repurchase | 0 ~ +4 | Tag | ❌ |
| 8 | 📋 Compliance | -4 ~ +2 | Tag | ❌ |
| 9 | 📈 BSR Trend | -3 ~ +4 | Keepa | ✅ |
| 10 | 💰 Price Trend | -4 ~ +2 | Keepa | ✅ |
| 11 | 👥 Seller Trend | -3 ~ +2 | Keepa | ✅ |
| 12 | 🎯 Pain Point | -2 ~ +4 | Amazon | ✅ |
| | **Total Range** | **-32 ~ +30** | | **10/12 Auto** |

---

## Part 4: Grade Scale

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 75+ | A 🔥 | Highly recommended — Strong opportunity |
| 65-74 | B ✅ | Recommended — Good opportunity |
| 55-64 | C+ ⚠️ | Consider — Needs differentiation |
| 45-54 | C 🟡 | Caution — Significant risks |
| < 45 | D ❌ | Not recommended — Avoid |

---

## Part 5: Red Lines (Auto-Reject)

| Condition | Signal | Action |
|-----------|--------|--------|
| Amazon Seller % > 30% | 💀 | Do not recommend |
| Known Brand % = 100% | 💀 | Do not recommend |

---

## Part 6: Category Tags Reference

### Repurchase Potential Tags

| Tag | Modifier | Categories |
|-----|----------|------------|
| `high_consumable` | +4 | Food, beverages, supplements, pet food |
| `regular_consumable` | +2 | Skincare, cleaning, stationery |
| `occasional` | +1 | Seasonal items, hobby supplies |
| `one_time` | 0 | Furniture, appliances, tools |

### Compliance Tags

| Tag | Modifier | Categories |
|-----|----------|------------|
| `none` | +2 | Generic home goods, accessories |
| `standard` | 0 | Electronics (FCC) |
| `fda` | -2 | Food, supplements, cosmetics |
| `high_barrier` | -4 | Safety equipment, medical devices |

### Logistics Tags

| Tag | Modifier | Categories |
|-----|----------|------------|
| `light_small` | +2 | Jewelry, phone accessories |
| `standard` | 0 | Most products |
| `heavy` | -2 | Fitness equipment, appliances |
| `liquid` | -3 | Beverages, cleaning products |
| `fragile` | -3 | Glassware, ceramics |

---

## Version History

| Version | Changes |
|---------|---------|
| v1.0 | Basic 4-dimension scoring |
| v2.0 | Added trends, seasonality, TikTok, ads |
| v2.4 | Adjusted thresholds for 60 = passing |
| v2.5 | Added brand dominance |
| v2.6 | Added 5 modifier factors |
| v2.7 | Added Amazon seller, market maturity, units analysis |
| **v3.0** | **Added Keepa trends (BSR/price/seller) + pain point analysis, 12 total modifiers** |
