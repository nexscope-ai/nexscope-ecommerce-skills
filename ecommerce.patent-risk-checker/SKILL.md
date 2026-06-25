---
name: ecommerce.patent-risk-checker
version: 1.1.0
description: |
  Screen product patent/IP infringement risk by image/product context. Triggers: safe to sell, will I get sued, IP risk, FTO, patent clearance. Use for product-level risk screening, not single-patent claim/legal-status queries.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Patent Risk Checker v1.1.0

## Core Question

Does this product have patent/IP infringement risk in the target market?

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Does this product have patent risks?**

Patent infringement risk assessment via image search.

## Clarify or Infer Before Querying

- If product image or product context is missing, ask for image URL, listing, or product details.
- Clarify target countries/regions before risk screening.
- Use patent-report-generator when the user asks for a complete clearance report.

## Differs From / Not Applicable

- Use design-patent-analyzer for visual design-patent similarity only.
- Use patent-claim-analyzer for a known patent claim.
- Use patent-legal-status for expiration/validity.
- Use patent-report-generator for complete clearance reports.

## Workflow

1. Understand product image/context and target regions.
2. Search for similar design/utility patent risks.
3. Assess similarity, active status, and litigation/legal relevance.
4. Return risk level, closest patents, and whether deeper claim/legal review is needed.

## Usage

```bash
# Basic risk check by image
python3 scripts/patent_risk_checker.py '{"imageUrl": "https://example.com/product.jpg", "regions": "US,EU"}'

# With product info for utility patent check
python3 scripts/patent_risk_checker.py '{
  "imageUrl": "https://example.com/product.jpg",
  "productTitle": "Wireless Earbuds with Active Noise Cancellation",
  "productDescription": "TWS earbuds with ANC, 30hr battery...",
  "regions": "US"
}'

# Generate charts
python3 scripts/patent_risk_checker.py '{"imageUrl": "..."}' --chart /tmp/charts
```

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `imageUrl` | string | **Yes** | - | Product image URL (required) |
| `countries` | string | No | | Target countries (comma-separated, e.g. "US,EU,CN") |
| `limit` | int | No | 50 | Max patents to return per type |

## Supported Regions

| Region | Code | Patent Office |
|--------|------|---------------|
| 🇺🇸 United States | US | USPTO |
| 🇪🇺 European Union | EU | EPO |
| 🇨🇳 China | CN | CNIPA |
| 🇯🇵 Japan | JP | JPO |
| 🇰🇷 Korea | KR | KIPO |
| 🇩🇪 Germany | DE | DPMA |
| 🇬🇧 United Kingdom | GB | UKIPO |
| 🇫🇷 France | FR | INPI |
| 🇮🇹 Italy | IT | UIBM |
| 🇦🇺 Australia | AU | IP Australia |
| 🇨🇦 Canada | CA | CIPO |
| 🇧🇷 Brazil | BR | INPI |
| 🇲🇽 Mexico | MX | IMPI |
| 🇮🇳 India | IN | IPO India |

## Risk Levels

| Score | Level | Meaning | Recommendation |
|-------|-------|---------|----------------|
| 0-25 | 🟢 LOW | Minimal risk | Proceed with confidence |
| 26-50 | 🟡 MEDIUM | Some concerns | Review flagged patents |
| 51-75 | 🟠 HIGH | Significant risk | Legal consultation advised |
| 76-100 | 🔴 CRITICAL | Major infringement risk | Do not proceed |

## Risk Scoring Algorithm

```
Risk Score = (
 Similarity × 50% +
 Legal_Status × 30% +
 Litigation × 20%
)
```

### Component Breakdown

| Factor | Weight | Logic |
|--------|--------|-------|
| **Similarity** | 50% | Highest similarity × 100 |
| **Legal Status** | 30% | % of active patents |
| **Litigation** | 20% | 100 if litigation history, else 0 |

## Output Structure

The output will be a structured markdown report, following this format:

**Product Patent Risk Check Report: [Product Image URL]**

---

**1. Executive Summary**
*   **Input Image:** [imageUrl]
*   **Target Countries:** [countries] (if provided)
*   **Overall Risk Score:** [risk_summary.overall_score]
*   **Risk Level:** [risk_summary.level] ([risk_summary.emoji])
*   **Recommendation:** [Recommendation from Risk Levels table for corresponding level]
*   **Core Insight:** This report assesses potential patent infringement risks related to the product image, covering both design and utility patents.

**2. Risk Overview**
*   **Design Patent Risk Score:** [risk_summary.design_patent_risk]
*   **Utility Patent Risk Score:** [risk_summary.utility_patent_risk]

**3. Alerts & Risk Events**
*   **Identified Alerts:**

| Alert Type | Severity | Trigger Condition (Detailed Description) |
| :--- | :--- | :--- |
| [alerts[0].type] | [alerts[0].severity] | [alerts[0].description] |
| ... | ... | ... |
*(Listing all identified alerts)*

**4. Design Patent Analysis**
*   **Matching Patent Count:** [design_patents.count]
*   **Highest Similarity:** [design_patents.highest_similarity]
*   **TRO Flagged Count:** [design_patents.tro_flagged] (if `tro_flagged` exists)
*   **Top 3 Matching Design Patents:**

| Patent Number | Title | Similarity% | Status |
| :--- | :--- | :--- | :--- |
| [design_patents.top_matches[0].patent_number] | [design_patents.top_matches[0].title] | [design_patents.top_matches[0].similarity_pct]% | [design_patents.top_matches[0].status] |
| ... | ... | ... | ... |

**5. Utility Patent Analysis**
*   **Matching Patent Count:** [utility_patents.count]
*   **Highest Similarity:** [utility_patents.highest_similarity]
*   **TRO Flagged Count:** [utility_patents.tro_flagged] (if `tro_flagged` exists)
*   **Top 3 Matching Utility Patents:**

| Patent Number | Title | Similarity% | Status |
| :--- | :--- | :--- | :--- |
| [utility_patents.top_matches[0].patent_number] | [utility_patents.top_matches[0].title] | [utility_patents.top_matches[0].similarity_pct]% | [utility_patents.top_matches[0].status] |
| ... | ... | ... | ... |

**6. Actionable Recommendations**
*   **Based on Overall Risk Level:** [Recommendation from Risk Levels table for corresponding level]
*   **Specific Recommendations:** (if `insights` includes a `recommendations` list)

**7. Attached Visualizations**
*   Risk Gauge (1_risk_gauge.png)
*   Similarity Distribution (2_similarity.png)
*   Region Coverage (3_regions.png)
*   Patent Expiration Timeline (4_timeline.png)

## Alert Types

| Alert | Severity | Trigger |
|-------|----------|---------|
| 🚨 LITIGATION_HISTORY | CRITICAL | Patent has litigation event history |
| ⚠️ HIGH_SIMILARITY | HIGH | Design ≥80% or Utility ≥70% |
| ⚠️ MODERATE_SIMILARITY | MEDIUM | Design 60-80% similarity |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Risk Gauge | Overall risk visualization | `1_risk_gauge.png` |
| Similarity Distribution | Patent similarity breakdown | `2_similarity.png` |
| Region Coverage | Risk by target market | `3_regions.png` |
| Timeline | Patent expiration timeline | `4_timeline.png` |

## Best Practices

### When to Check
1. **Before sourcing** — Check supplier samples
2. **Before listing** — Verify main product images
3. **Before PPC** — Don't advertise risky products
4. **Periodically** — New patents file constantly

### What to Do with Results

| Risk Level | Action |
|------------|--------|
| 🟢 LOW | Document check, proceed |
| 🟡 MEDIUM | Review specific patents, modify if needed |
| 🟠 HIGH | Get legal opinion before proceeding |
| 🔴 CRITICAL | Do not sell this product |

## Limitations

- Visual search works best with clear product images
- Utility search requires accurate product descriptions
- Results are advisory, not legal advice
- Some newer patents may not be indexed yet

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (Design, model=1) | Design patent visual similarity |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (Utility, model=4) | Utility patent image similarity |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/legalStatus` | Legal status and litigation event history |

**Coverage**: 170M+ patents from 150+ countries. Litigation, Transfer, License, Pledge event records included.


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- USPTO: https://www.uspto.gov
- EPO: https://www.epo.org
