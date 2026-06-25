---
name: patent-report-generator
version: 1.0.0
description: |
  Generate a full patent/IP risk report combining product risk, claims, family, and legal status. Triggers: FTO report, clearance report, complete patent check, full IP picture. Use for comprehensive due diligence, not quick single checks.
allowed-tools:
  - Bash
  - Read
  - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Patent Report Generator v1.0.0

## Core Question

What is the complete patent/IP risk picture for this product or launch?

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.


**Generate a patent clearance report**

Generate comprehensive patent risk reports for products.

## Clarify or Infer Before Querying

- If product details, target countries, or relevant patent IDs are missing, ask for them or run the narrower patent skills first.
- Clarify whether the report is for launch clearance, supplier due diligence, or competitor risk.
- Do not treat this as a quick single-patent lookup.

## Differs From / Not Applicable

- Use patent-risk-checker for quick product-level screening.
- Use patent-claim-analyzer, patent-family-explorer, or patent-legal-status for a single narrow question.
- Use this skill when the user asks for full FTO/IP due diligence.

## Workflow

1. Understand product, target countries, and report purpose.
2. Run or incorporate risk, claims, family, and legal-status evidence.
3. Synthesize findings into a clearance/FTO report.
4. Return executive risk summary, evidence tables, caveats, and recommended next steps.

## Usage

```bash
# Basic report by image
python3 scripts/patent_report_generator.py '{"imageUrl": "https://example.com/product.jpg"}'

# Full report with product info
python3 scripts/patent_report_generator.py '{
  "imageUrl": "https://example.com/product.jpg",
  "productName": "Wireless Earbuds",
  "productDescription": "TWS earbuds with ANC, 30hr battery",
  "targetMarkets": "US,CN,EU"
}'

# With charts
python3 scripts/patent_report_generator.py '{"imageUrl": "..."}' --chart /tmp/charts
```

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `imageUrl` | string | Yes | - | Product image URL |
| `productName` | string | No | - | Product name |
| `productDescription` | string | No | - | Product description |
| `targetMarkets` | string | No | | Target markets |
| `lang` | string | No | "cn" | Report language |
| `topRisks` | int | No | 10 | Number of top risks to analyze |

## Report Sections

### 1. Executive Summary
- Overall risk score and level
- Key findings at a glance
- Go/No-Go recommendation

### 2. Design Patent Analysis
- Visual similarity search results
- Top matching design patents
- Design conflict assessment

### 3. Utility Patent Analysis
- Functional similarity search
- Key utility patents identified
- Technical overlap analysis

### 4. Geographic Risk Map
- Countries with protection
- Safe markets identified
- Family patent coverage

### 5. Top Risk Patents
For each high-risk patent:
- Patent number and title
- Current owner
- Legal status (Active/Expired)
- Expiration date
- Key claims (translated)
- Similarity score
- Risk assessment

### 6. Recommendations
- Specific action items
- Design modification suggestions
- Market entry strategy
- Legal consultation needs

## Risk Levels

| Score | Level | Meaning |
|-------|-------|---------|
| 0-25 | 🟢 LOW | Safe to proceed |
| 26-50 | 🟡 MEDIUM | Review recommended |
| 51-75 | 🟠 HIGH | Proceed with caution |
| 76-100 | 🔴 CRITICAL | Do not proceed |

## Output Files

| File | Format | Description |
|------|--------|-------------|
| `report.md` | Markdown | Human-readable report |
| `report.json` | JSON | Machine-readable data |
| `charts/` | PNG | Visualization charts |

## Charts Generated

| Chart | Description |
|-------|-------------|
| Risk Gauge | Overall risk visualization |
| Similarity Distribution | Patent similarity breakdown |
| Geographic Map | Countries with protection |
| Timeline | Patent expiration dates |
| Risk Matrix | Risk by category |

## Use Cases

### Pre-Sourcing Report
Before ordering samples, run a quick check on product viability.

### Product Launch Report
Comprehensive clearance before launching in target markets.

### Due Diligence Report
For investors or partners reviewing product portfolio.

### Periodic Monitoring
Regular checks as new patents are filed.

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (Design, model=1) | Design patent visual similarity |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentImageSearch` (Utility, model=4) | Utility patent image similarity |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/legalStatus` | Legal status and litigation events |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentFamily` | Family coverage across countries |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/claimDataTranslated` | Translated claims for top-risk patents |

**Coverage**: 170M+ patents from 150+ countries.
- Legal status database
- Patent family data
- Claims and translations

## Limitations

- Report is advisory, not legal advice
- Best used as starting point for legal review
- Some very recent patents may not be indexed
- Machine translation may have errors


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

This skill integrates:
- `ecommerce.patent-risk-checker`
- `ecommerce.design-patent-analyzer`
- `ecommerce.patent-legal-status`
- `ecommerce.patent-family-explorer`
- `ecommerce.patent-claim-analyzer`

## Output Structure

The output will be a structured markdown report, following this format:

**Product Patent Risk Comprehensive Report: [Product Name]**

---

**1. Executive Summary**
*   **Product Name:** [productName]
*   **Product Description:** [productDescription]
*   **Target Markets:** [targetMarkets]
*   **Overall Risk Score:** [overall_risk.score]
*   **Overall Risk Level:** [overall_risk.level] ([overall_risk.emoji])
*   **Core Recommendation:** [overall_risk.recommendation]

**2. Design Patent Analysis**
*   **Similar Design Patents Found:** [design_patent_analysis.count]
*   **Highest Similarity:** [design_patent_analysis.max_similarity_pct]
*   **Design Conflict Assessment:** [design_patent_analysis.conflict_level]
*   **Recommendation:** [design_patent_analysis.recommendation]
*   **Top 3 Similar Design Patents:**

| Patent Number | Title | Assignee | Similarity | Status |
| :--- | :--- | :--- | :--- | :--- |
| [design_patent_analysis.top_matches[0].patent_number] | [design_patent_analysis.top_matches[0].title] | [design_patent_analysis.top_matches[0].assignee] | [design_patent_analysis.top_matches[0].similarity_pct]% | [design_patent_analysis.top_matches[0].status] |
| ... | ... | ... | ... | ... |

**3. Utility Patent Analysis**
*   **Similar Utility Patents Found:** [utility_patent_analysis.count]
*   **Highest Similarity:** [utility_patent_analysis.max_similarity_pct]
*   **Technical Overlap Analysis:** [utility_patent_analysis.overlap_assessment]
*   **Recommendation:** [utility_patent_analysis.recommendation]
*   **Top 3 Similar Utility Patents:**

| Patent Number | Title | Assignee | Similarity | Status |
| :--- | :--- | :--- | :--- | :--- |
| [utility_patent_analysis.top_matches[0].patent_number] | [utility_patent_analysis.top_matches[0].title] | [utility_patent_analysis.top_matches[0].assignee] | [utility_patent_analysis.top_matches[0].similarity_pct]% | [utility_patent_analysis.top_matches[0].status] |
| ... | ... | ... | ... | ... |

**4. Geographic Risk Map**
*   **Target Market Coverage:**
    *   Number of Protected Regions: [geographic_risk_map.protected_regions]
    *   Major Markets Covered: [geographic_risk_map.major_markets_covered]
    *   Potentially Safe Markets: [geographic_risk_map.safe_markets]
    *   Geographic Risk Level: [geographic_risk_map.level]
    *   Recommendation: [geographic_risk_map.recommendation]

**5. Top Risk Patents**
*   **Identified High-Risk Patents (Showing Top 5):**

| Patent Number | Title | Current Owner | Legal Status | Expiration Date | Similarity% | Risk Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [top_risk_patents[0].patent_number] | [top_risk_patents[0].title] | [top_risk_patents[0].owner] | [top_risk_patents[0].legal_status] | [top_risk_patents[0].expiration_date] | [top_risk_patents[0].similarity_pct]% | [top_risk_patents[0].risk_assessment] |
| ... | ... | ... | ... | ... | ... | ... |

*   **Key Claims Summary (Example for the first high-risk patent):**
    ```
    [top_risk_patents[0].key_claims_summary]
    ```

**6. Comprehensive Recommendations**
*   [recommendations[0].action]
*   [recommendations[1].action]
*   ... (Listing all key recommendations)

**7. Attached Visualizations**
*   Overall Risk Gauge
*   Similarity Distribution
*   Geographic Protection Map
*   Patent Expiration Timeline
*   Risk Matrix
