---
name: product-validator
version: 1.4.0
description: |
  Validate a specific product/ASIN for data reliability, demand signals, profitability, and sourcing risk. Triggers: validate product, trust this ASIN, verify sales, review authenticity. Use for known products, not product discovery.
allowed-tools:
  - Bash
  - Read
  - Write
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Product Validator v1.4.0

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Is this product data reliable? Should I trust these numbers?**

Validate product data reliability with 10-step analysis including profitability calculation.

## Core Question

> — Is this product data reliable?
> — Can I make money on this?

## When to Use

- Validating a product before sourcing
- Checking if BSR/sales estimates are realistic
- Calculating profitability and ROI
- Identifying fake reviews or manipulated data

## Differs From / Not Applicable

- Use product-opportunity-finder to discover products.
- Use competitor-analyzer to compare competing ASINs.
- Use price-history-analyzer for deep price history.
- Use this skill for validating a known product or ASIN before sourcing.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Keepa | `/api/v1/tools/linkfox/keepa/productRequest` | Product details, title, price, reviews, BSR |
| Keepa | `/api/v1/tools/linkfox/keepa/productSeries` | BSR history, price history (180-day) |
| Jungle Scout | `/api/v1/tools/jungle-scout/keywords/by-keyword` | Category benchmarks (avg search volume, difficulty) |

## 10-Step Validation Flow

| Step | Analysis | Output |
|------|----------|--------|
| 1️⃣ | Data Extraction | Raw product data |
| 2️⃣ | BSR History | Stability, seasonality |
| 3️⃣ | Price History | Volatility, trends |
| 4️⃣ | Buy Box Analysis | Stability, competition |
| 5️⃣ | Seller History | Seller count, types |
| 6️⃣ | Review Scoring | Authenticity check |
| 7️⃣ | Stock Status | Availability patterns |
| 8️⃣ | Seasonality | Peak/trough timing |
| 9️⃣ | Score Calculation | Composite score |
| 🔟 | Risk Assessment | Final recommendation |

## Validation Score (0-100)

| Score | Level | Action |
|-------|-------|--------|
| ≥80 | ✅ VALID | Proceed with confidence |
| 60-79 | ⚠️ CAUTION | Verify specific concerns |
| <60 | 🔴 AVOID | High risk, do not proceed |


## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Usage

```bash
# Validate a product
python3 scripts/product_validator.py '{"asin": "B07RL88DD2"}'

# With profitability calculation
python3 scripts/product_validator.py '{"asin": "B07RL88DD2", "cost_price": 19.99}'

# Batch validation
python3 scripts/product_validator.py '{"asins": ["B0XXX", "B0YYY"]}'

# With chart output
python3 scripts/product_validator.py '{"asin": "B07RL88DD2"}' --chart /tmp/output
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asin` | string | - | Single ASIN to validate |
| `asins` | array | - | Multiple ASINs to validate |
| `market` | string | | Target marketplace |
| `cost` | float | - | Product cost for profitability |
| `price` | float | - | Selling price (or use current) |
| `category` | string | - | Category for FBA fees |

## Output Structure

```json
{
  "asin": "B07RL88DD2",
  "market": "place": "US",
  "title": "Product Name",
  "validation_score": 85,
  "risk_level": "VALID",
  "recommendation": "Data trustworthy, proceed with standard due diligence",
  "scores": {
    "bsr":     {"score": 25, "max": 25},
    "price":   {"score": 18, "max": 20},
    "buybox":  {"score": 17, "max": 20},
    "sellers": {"score": 12, "max": 15},
    "reviews": {"score": 12, "max": 15},
    "stock":   {"score": 4,  "max": 5}
  },
  "red_flags": [
    {"type": "SEASONALITY", "severity": "low", "detail": "Q4 spike expected"}
  ],
  "seasonality": {
    "pattern": "MILD",
    "volatility": "LOW",
    "peak_months": [11, 12],
    "current_position": "OFF_PEAK",
    "bsr_trend": "STABLE",
    "modifier": 2,
    "interpretation": "Mild seasonal pattern"
  },
  "product_data": {
    "price": 19.99,
    "reviews": 1200,
    "rating": 4.5,
    "bsr": 5000,
    "sellers": 3,
    "monthly_sales": 250,
    "is_variant": false
  },
  "bsr_history": [4800, 5100, 4900, 5000],
  "price_history": [19.99],
  "series_data": {
    "available": true,
    "bsr_data_points": 180,
    "bsr_category": "Kitchen & Dining",
    "analysis": {"manipulation_flags": []}
  },
  "profitability": {
    "cost": 5.00,
    "price": 19.99,
    "fba_fee": 6.50,
    "referral_fee": 3.00,
    "profit": 5.49,
    "margin": 27.5,
    "roi": 109.8,
    "break_even_price": 14.50,
    "ad_buffer": 2.00
  },
  "category": "_benchmarks": {
    "avg_monthly_search_volume": 45000,
    "avg_difficulty": 55
  }
}
```

## Profitability Calculator

| Component | Description |
|-----------|-------------|
| **Referral Fee** | Category-based (typically 15%) |
| **FBA Fee** | Size/weight-based fulfillment |
| **Profit** | Price - Cost - Fees |
| **Margin** | Profit / Price × 100 |
| **ROI** | Profit / Cost × 100 |
| **Break-even** | Cost + Fees (minimum viable price) |
| **Ad Buffer** | Recommended PPC budget headroom |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| BSR Trend | Historical BSR line | `bsr_trend.png` |
| Price Trend | Historical price line | `price_trend.png` |
| Score Breakdown | Component bar | `score_breakdown.png` |
| Profitability | Waterfall chart | `profitability.png` |

## Risk Flags

| Flag | Trigger |
|------|---------|
| ⚠️ BSR Volatile | >50% variance in 90 days |
| ⚠️ Price War | >20% price drops |
| ⚠️ Review Spike | Unnatural review growth |
| ⚠️ Stock Issues | Frequent out-of-stock |
| ⚠️ Seasonal | >2x BSR variance by season |

## Modular Components

```
product_validator.py (main entry)
├── profitability_module.py (standalone FBA calculator)
└── seasonality_module.py (standalone seasonality detector)
```

## Workflow Integration

```
✅ Validation Phase
├── demand-validator → Validate demand is real
├── price-history-analyzer → Check for price wars
└── product-validator → Validate product data ← YOU ARE HERE
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## Limitations

- BSR history requires Keepa data
- FBA fee estimates are approximate
- Review authenticity is heuristic
- Seasonality detection needs 12+ months data
- Does not account for advertising costs in base profit

## References

- `references/fba-fee-guide.md` — Fee calculation details
- `references/display-rules.md` — Chart styling guidelines
