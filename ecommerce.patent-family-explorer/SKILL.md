---
name: ecommerce.patent-family-explorer
version: 1.0.0
description: |
  Explore patent family members and country coverage for a known patent/publication. Triggers: patent family, international coverage, where valid, applies in US/EU/UK, PCT. Use for family/territory mapping, not claims or legal status.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Patent Family Explorer v1.0.0

## Core Question

Where does this patent family exist, and what countries or related filings matter?

**Are there family patents in other countries?**

Explore patent families across multiple countries.

## Clarify or Infer Before Querying

- If patent ID/publication number is missing, ask for it first.
- Clarify target countries/regions when the user asks where it applies.
- Do not answer legal-status or claim-scope questions unless also using the relevant skill.

## Differs From / Not Applicable

- Use patent-claim-analyzer for claim scope.
- Use patent-legal-status for current validity and legal events.
- Use patent-report-generator for full clearance reporting.
- Use this skill for family members, PCT/INPADOC coverage, and territory mapping.

## Workflow

1. Confirm patent/publication ID and target regions.
2. Fetch family members and country coverage.
3. Group by simple family/INPADOC/authority where available.
4. Return territory coverage, priority links, and follow-up status checks.

## Usage

```bash
# Basic family search
python3 scripts/patent_family_explorer.py '{"patentNumber": "US10000001B2"}'

# Multiple patents
python3 scripts/patent_family_explorer.py '{"patentNumber": "US10000001B2,EP3000001A1"}'

# With charts
python3 scripts/patent_family_explorer.py '{"patentNumber": "..."}' --chart /tmp/charts
```

## ⚠️ MANDATORY: Charts & Display Rules

1. **Generate charts by default for full analytical reports** — use `--chart` with an output directory unless the user asks for a quick text-only result or chart data is unavailable.
2. **Send generated charts to the user** — when charts are created, share all chart PNGs immediately.
3. **All chart styling** is driven by `ecommerce_chart_helpers.py` which reads from `chart_style.json` (derived from `references/display-rules.md`). Do NOT hardcode colors in scripts.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `patentNumber` | string | Yes* | Publication number(s), comma-separated |
| `patentId` | string | Yes* | Patent ID(s), comma-separated |

*One of `patentNumber` or `patentId` is required.

## Family Types

### Simple Family
Patents sharing the **exact same priority** claims.
- Most restrictive definition
- Direct equivalents across countries

### INPADOC Family
Patents sharing **at least one priority** claim.
- Broader than Simple Family
- Includes related applications

### PatSnap Family
Patents with **related technical content** (AI-determined).
- Broadest definition
- Includes continuations, divisionals, etc.

## Output Structure

The output will be a structured markdown report, following this format:

**Patent Family Exploration Report: [Patent Number]**

---

**1. Executive Summary**
*   **Analyzed Patent Number:** [patent_number]
*   **Data Source:** Zhihuiya - International Patent Database
*   **Countries Covered by Patent Family:** [family_overview.countries_covered]
*   **Geographic Risk Assessment:** [geographic_risk.coverage_level]
*   **Core Insight:** Understanding the geographic scope of patent protection helps assess market entry risks and intellectual property strategies.

**2. Patent Family Size Comparison**
*   **Patent Family Size Under Different Definitions:**

| Family Type | Size |
| :--- | :--- |
| Simple Family | [family_overview.simple_family_size] |
| INPADOC Family | [family_overview.inpadoc_family_size] |
| PatSnap Family | [family_overview.patsnap_family_size] |

**3. Geographic Coverage & Risk Assessment**
*   **Covered Countries:** [family_overview.countries_covered]
*   **Number of Protected Regions:** [geographic_risk.protected_regions]
*   **Major Markets Covered:** [geographic_risk.major_markets_covered]
*   **Potentially Safe Markets:** [geographic_risk.safe_markets]
*   **Geographic Risk Level:** [geographic_risk.coverage_level]
*   **Risk Interpretation:** [geographic_risk.meaning]

**4. Patent Family Members Details**
*   **List of Patent Family Members (Showing Top 10):**

| Patent Number | Country | Family Type (Simple/INPADOC/PatSnap) |
| :--- | :--- | :--- |
| [family_members[0].patent_number] | [family_members[0].country] | [family_members[0].family_type] |
| ... | ... | ... |
*(Listing more family members if available)*

**5. Attached Visualizations**
*   World Map (Countries with protection) (1_world_map.png)
*   Family Comparison (Simple vs INPADOC vs PatSnap) (2_family_types.png)
*   Cross-Country Filing Timeline (3_timeline.png)

## Geographic Risk Assessment

| Coverage | Risk Level | Meaning |
|----------|------------|---------|
| 🔴 US + CN + EU | HIGH | Major markets protected |
| 🟠 US + CN or US + EU | MEDIUM | Key markets protected |
| 🟡 US only | LOW | Limited protection |
| 🟢 No major markets | MINIMAL | May be safe to sell |

## Major Markets

| Region | Code | Importance |
|--------|------|------------|
| 🇺🇸 United States | US | #1 e-commerce market |
| 🇨🇳 China | CN | #1 manufacturing |
| 🇪🇺 European Union | EP/DE/FR/GB | Major consumer market |
| 🇯🇵 Japan | JP | High-value market |
| 🇰🇷 Korea | KR | Tech-savvy market |
| 🇬🇧 United Kingdom | GB | Post-Brexit separate |

## Use Cases

### 1. Before Sourcing
Check if a competitor's US patent has a CN equivalent that could
block your manufacturing in China.

### 2. Market Entry
Before entering a new market, check if patents protecting 
competitor products exist in that country.

### 3. Licensing Decisions
Understand the full geographic scope of a patent you want to license.

### 4. Invalidation Strategy
Find family members that might be easier to invalidate than the
original patent.

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| World Map | Countries with protection | `1_world_map.png` |
| Family Comparison | Simple vs INPADOC vs PatSnap | `2_family_types.png` |
| Timeline | Filing dates across countries | `3_timeline.png` |

## Limitations

- Only shows patents in the Zhihuiya database
- Some recent filings may not be linked yet
- PCT applications may show as separate entries
- Family definitions vary by source

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/patentFamily` | Patent family members (Simple, INPADOC, PatSnap) |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/legalStatus` | Legal status of each family member |

**Coverage**: 170M+ patents from 150+ countries. Regular sync with patent offices.


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- WIPO Patent Families: https://www.wipo.int
