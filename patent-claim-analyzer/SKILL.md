---
name: patent-claim-analyzer
version: 1.0.0
description: |
  Analyze patent claims and protection scope for a known patent/publication. Triggers: what does patent cover, claim scope, independent claims, design around. Use for claim interpretation, not product-level FTO screening or legal status.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Patent Claim Analyzer v1.0.0

## Core Question

What does this patent claim cover, and what design-around constraints matter?

**What is the scope of patent protection?**

Analyze patent claims to understand protection scope.

## Clarify or Infer Before Querying

- If patent ID/publication number is missing, ask for it or use a patent search/risk skill first.
- Clarify desired language and whether the user wants scope interpretation or design-around notes.
- Do not infer claim scope from product images alone.

## Differs From / Not Applicable

- Use patent-risk-checker for product/image-based infringement screening.
- Use patent-family-explorer for related family members and country coverage.
- Use patent-legal-status for validity or expiration.
- Use this skill to interpret claim scope for a known patent/publication.

## Workflow

1. Confirm patent/publication ID and language needs.
2. Fetch independent and dependent claim data.
3. Summarize protection scope and key claim limitations.
4. Highlight design-around considerations and uncertainties.

## Usage

```bash
# Basic claim analysis
python3 scripts/patent_claim_analyzer.py '{"patentNumber": "US11234567B2"}'

# With translation to Chinese
python3 scripts/patent_claim_analyzer.py '{"patentNumber": "US11234567B2", "lang": "cn"}'

# Multiple patents
python3 scripts/patent_claim_analyzer.py '{"patentNumber": "US11234567B2,CN115000000A"}'
```

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `patentNumber` | string | Yes* | - | Publication number(s) |
| `patentId` | string | Yes* | - | Patent ID(s) |
| `lang` | string | No | "cn" | Translation: en, cn, jp |
| `replaceByRelated` | int | No | 1 | Use family patent if claims unavailable |

*One of `patentNumber` or `patentId` is required.

## Claim Types

### Independent Claims
The broadest claims that stand alone:
- **Claim 1** usually covers the main invention
- Must include ALL elements to infringe
- Fewer elements = broader scope

### Dependent Claims
Claims that reference other claims:
- 
- Adds limitations → narrower scope
- Infringement of dependent = also infringes independent

## Output Structure

The output will be a structured markdown report, following this format:

**Patent Claim Analysis Report: [Patent Number(s)]**

---

**1. Executive Summary**
*   **Analyzed Patent Number:** [patent_number]
*   **Total Claims:** [claim_count]
*   **Independent Claims:** [analysis.independent_claims.length]
*   **Dependent Claims:** [analysis.dependent_claims.length]
*   **Core Insight:** Independent claims define the broadest scope of protection. This report helps understand patent protection for product design and infringement avoidance.

**2. Claim Overview**
*   **Patent Number:** [patent_number]
*   **Total Claims:** [claim_count]
*   **Claim Type Distribution:**

| Type | Count | Example Claim No. |
| :--- | :--- | :--- |
| Independent Claims | [analysis.independent_claims.length] | [analysis.independent_claims[0]] (if available) |
| Dependent Claims | [analysis.dependent_claims.length] | [analysis.dependent_claims[0]] (if available) |

**3. Independent Claims Analysis**
*(This section will highlight the first independent claim, and if structured elements are provided in JSON, they will be listed. Otherwise, the raw text will be displayed.)*

*   **Claim 1 (Example):**
    *   **Type:** Independent
    *   **Key Elements:** [analysis.claim_structure.claim_1.elements] (if `claim_structure.claim_1` exists and contains `elements`)
    *   **Full Text:**
        ```
        [claims_original[0]]
        ```
*(Note: This will display the full text of Claim 1.)*

**4. Principles of Infringement**
*   **Infringement Rule:** A product must contain all elements of an independent claim to infringe.
*   **Key Points:**
    *   ✅ Contains A, B, C → Infringes
    *   ❌ Contains A, B only → Does NOT infringe
    *   ❌ Contains A, B, C, D → Still infringes (extra features do not prevent infringement)

**5. Full Claims Text**
*(If a translation language is provided, the translated text will be displayed. For brevity, display length may be limited or user prompted to view attachment/full report.)*
```
[claims_original]
```

**6. Attached Visualizations**
*   Claim Structure (1_claim_structure.png)
*   Claims Comparison (2_claims_comparison.png)

## How to Read Claims

### Claim Structure
```
Claim 1: A [CATEGORY] comprising:
 [ELEMENT A];
 [ELEMENT B]; and
 [ELEMENT C].
```

### Infringement Test
To infringe, a product must have **ALL** elements:
- ✅ Has A, B, C → Infringes
- ❌ Has A, B only → Does NOT infringe
- ❌ Has A, B, C, D → Still infringes (extra features don't help)

## Use Cases

### 1. Product Design
Check if your product has all elements of Claim 1.
If missing even one element, no infringement.

### 2. Design-Around
Identify which element to remove or change
to avoid infringement.

### 3. Competitor Analysis
Understand what competitors actually protect,
not what they claim in marketing.

### 4. Licensing Negotiation
Know exactly what you're licensing.

## Translation Languages

| Code | Language | Use Case |
|------|----------|----------|
| `en` | English | International communication |
| `cn` | Chinese | Chinese suppliers/teams |
| `jp` | Japanese | Japanese market/patents |

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Claim Structure | Independent vs dependent claims | `1_claim_structure.png` |
| Claims Comparison | Claim count across patents | `2_claims_comparison.png` |

## Limitations

- Some older patents may not have structured claims
- Machine translation may have errors for technical terms
- Design patents have different claim structure
- Claim interpretation requires legal expertise

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/claimData` | Original claim text |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/claimDataTranslated` | Translated claims (cn/en/jp) |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/simpleBibliography` | Patent title, type, country context |

**Coverage**: 170M+ patents from 150+ countries. Uses family fallback (`replaceByRelated`) when claims unavailable.


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- USPTO Claim Guidelines: https://www.uspto.gov
