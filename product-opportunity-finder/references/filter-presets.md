# Filter Presets — Product Opportunity Finder v1.0

## Preset Overview

| Preset | Risk Level | Best For |
|--------|------------|----------|
| Conservative | Low | Beginners, risk-averse |
| Balanced | Medium | Most sellers |
| Aggressive | High | Experienced sellers |
| Premium | Medium | High-margin focus |
| Budget | Medium | Volume focus |
| Trending | High | Trend chasers |

---

## 1. Conservative (Low Risk)

**Best for:** New sellers, risk-averse, proven markets

```json
{
  "filters": {
    "min_revenue": 15000,
    "max_revenue": 100000,
    "min_reviews": 10,
    "max_reviews": 200,
    "min_rating": 4.0,
    "min_price": 20,
    "max_price": 60,
    "max_seasonality": 2.0,
    "exclude_known_brands": true,
    "exclude_amazon_seller": true,
    "min_listing_age_days": 180
  },
  "description": "Proven products with low competition and good ratings"
}
```

**Rationale:**
- Higher revenue floor ensures proven demand
- Low review ceiling finds weak competitors
- Good rating floor avoids quality issues
- Excludes brands and Amazon for cleaner entry
- Older listings = proven market

---

## 2. Balanced (Medium Risk)

**Best for:** Most sellers, general product research

```json
{
  "filters": {
    "min_revenue": 10000,
    "max_revenue": 150000,
    "min_reviews": 0,
    "max_reviews": 400,
    "min_rating": 3.8,
    "min_price": 15,
    "max_price": 75,
    "max_seasonality": 2.5,
    "exclude_known_brands": true,
    "exclude_amazon_seller": true
  },
  "description": "Balanced approach with reasonable risk/reward"
}
```

**Rationale:**
- Includes newer products (min_reviews: 0)
- Wider revenue range captures more opportunities
- Slightly lower rating threshold finds quality gaps
- Standard brand/Amazon exclusions

---

## 3. Aggressive (High Risk)

**Best for:** Experienced sellers, emerging markets

```json
{
  "filters": {
    "min_revenue": 5000,
    "max_revenue": 200000,
    "min_reviews": 0,
    "max_reviews": 600,
    "min_rating": 3.5,
    "min_price": 12,
    "max_price": 100,
    "max_seasonality": 3.0,
    "exclude_known_brands": false,
    "exclude_amazon_seller": true
  },
  "description": "Cast wide net, includes riskier but potentially high-reward opportunities"
}
```

**Rationale:**
- Lower revenue floor catches emerging products
- Higher review ceiling still avoids saturated
- Lower rating finds quality gaps to exploit
- Allows competition with brands (if you can differentiate)

---

## 4. Premium Focus

**Best for:** High-margin strategy, premium products

```json
{
  "filters": {
    "min_revenue": 20000,
    "max_revenue": 200000,
    "min_reviews": 0,
    "max_reviews": 250,
    "min_rating": 4.0,
    "min_price": 40,
    "max_price": 150,
    "max_seasonality": 2.0,
    "exclude_known_brands": true,
    "exclude_amazon_seller": true
  },
  "description": "Focus on premium products with high margins"
}
```

**Rationale:**
- Higher price floor = better margins
- Very low review ceiling = true blue ocean
- Good rating floor = quality market
- Smaller but more profitable opportunities

---

## 5. Budget Focus

**Best for:** Volume strategy, competitive pricing

```json
{
  "filters": {
    "min_revenue": 25000,
    "max_revenue": 500000,
    "min_reviews": 0,
    "max_reviews": 500,
    "min_rating": 3.8,
    "min_price": 10,
    "max_price": 30,
    "max_seasonality": 2.5,
    "exclude_known_brands": true,
    "exclude_amazon_seller": true
  },
  "description": "High-volume, lower-price products"
}
```

**Rationale:**
- Higher revenue floor ensures volume
- Lower price = more buyers, more volume
- Must have strong supply chain for margins
- Compete on efficiency

---

## 6. Trending (High Risk)

**Best for:** Catching emerging trends, first-mover advantage

```json
{
  "filters": {
    "min_revenue": 3000,
    "max_revenue": 100000,
    "min_reviews": 0,
    "max_reviews": 100,
    "min_rating": 0,
    "min_price": 15,
    "max_price": 80,
    "max_listing_age_days": 365,
    "bsr_trend": "improving",
    "search_trend": "rising",
    "exclude_known_brands": true,
    "exclude_amazon_seller": true
  },
  "description": "New and rising products, first-mover opportunities"
}
```

**Rationale:**
- Very low review ceiling = new market
- No rating floor = allows brand new products
- Max listing age = recent products only
- Requires trend data confirmation
- High risk, high reward

---

## Category-Specific Adjustments

### Electronics
```json
{
  "adjustments": {
    "max_reviews": "-30%",
    "min_price": "+50%",
    "exclude_known_brands": true
  },
  "notes": "Electronics have higher reviews, higher prices"
}
```

### Beauty & Personal Care
```json
{
  "adjustments": {
    "min_revenue": "-20%",
    "max_reviews": "+20%",
    "min_rating": "4.0"
  },
  "notes": "Beauty has lower revenue threshold but needs good ratings"
}
```

### Home & Kitchen
```json
{
  "adjustments": {
    "max_reviews": "+30%",
    "max_seasonality": "3.0"
  },
  "notes": "Home products often have more reviews, more seasonal"
}
```

### Sports & Outdoors
```json
{
  "adjustments": {
    "max_seasonality": "3.5",
    "min_price": "-20%"
  },
  "notes": "Accept higher seasonality, lower prices"
}
```

---

## Custom Filter Builder

Use this template to create custom filters:

```json
{
  "name": "My Custom Filter",
  "filters": {
    "min_revenue": [YOUR_VALUE],
    "max_revenue": [YOUR_VALUE],
    "min_reviews": [YOUR_VALUE],
    "max_reviews": [YOUR_VALUE],
    "min_rating": [YOUR_VALUE],
    "min_price": [YOUR_VALUE],
    "max_price": [YOUR_VALUE],
    "max_seasonality": [YOUR_VALUE],
    "exclude_known_brands": [true/false],
    "exclude_amazon_seller": [true/false],
    "max_listing_age_days": [YOUR_VALUE],
    "bsr_trend": ["improving"/"stable"/"any"],
    "search_trend": ["rising"/"stable"/"any"]
  }
}
```

---

## Filter Selection Guide

| Your Situation | Recommended Preset |
|----------------|-------------------|
| First product, low budget | Conservative |
| Have some experience | Balanced |
| Want high margins | Premium |
| Can compete on volume | Budget |
| Experienced, risk tolerant | Aggressive |
| Want emerging products | Trending |
