---
name: ecommerce.patent-legal-status
version: 1.0.0
description: |
  Check patent legal status, validity, expiration, and status events. Triggers: expired patent, still in force, enforceable, maintenance fees, when does it expire. Use for status/validity, not claim scope or image-based risk.
allowed-tools:
 - Bash
 - Read
 - Write
metadata:
  requires:
    apis: ["nexscope"]
---

> **IMPORTANT — Working Directory**: All scripts in this skill MUST be executed with the working directory set to the **absolute path** of the directory containing this SKILL.md file (the skill root directory). Always `cd` into this directory before running any command. Do NOT use relative paths or shell shortcuts like `~` in paths, as they may not be resolved by the execution environment.

# Patent Legal Status v1.0.0

## Core Question

Is this patent still active, enforceable, expired, or affected by legal events?

**Is this patent still valid?**

Query patent legal status (valid/invalid/expired).

## Clarify or Infer Before Querying

- If patent ID/publication number is missing, ask for it first.
- Clarify target country/authority if the patent has family members.
- Do not assume a patent is enforceable just because a related family member exists.

## Differs From / Not Applicable

- Use patent-claim-analyzer for what the patent covers.
- Use patent-family-explorer for country/family coverage.
- Use patent-risk-checker for product-level risk screening.
- Use this skill for expiration, enforceability, maintenance, and legal events.

## Workflow

1. Confirm patent/publication ID and authority/region.
2. Fetch current legal status and event history.
3. Identify active, expired, abandoned, pending, or uncertain status.
4. Return enforceability caveats and next verification steps.

## Usage

```bash
# Single patent
python3 scripts/patent_legal_status.py '{"patentNumber": "US11234567B2"}'

# Multiple patents
python3 scripts/patent_legal_status.py '{"patentNumber": "US11234567B2,CN115000000A,EP4000000A1"}'

# By patent ID
python3 scripts/patent_legal_status.py '{"patentId": "abc123,def456"}'
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

## Legal Status Types

### Simple Status (simpleLegalStatus)

| Status | Meaning | Icon |
|--------|---------|------|
| **Active** | Patent is valid and enforceable | ✅ |
| **Inactive** | Patent is no longer valid | ❌ |
| **Pending** | Application under examination | ⏳ |
| **Undetermined** | Status not confirmed | ❓ |
| **PCT designated period** | PCT application in designated period | 🌐 |
| **PCT designated expiration** | PCT designated period expired | 🌐 |

### Detailed Status (legalStatus)

| Status | Description |
|--------|-------------|
| Published | Application published |
| Examining | Under substantive examination |
| Granted | Patent rights granted |
| Expired | Term expired |
| Abandoned | Voluntarily or deemed abandoned |
| Withdrawn | Application withdrawn |
| Rejected | Application rejected |
| Revoked | Patent revoked |
| Non-Payment | Lapsed due to non-payment |
| Ceased | Rights terminated |

### Legal Events (eventStatus)

| Event | Risk Level | Description |
|-------|------------|-------------|
| **Litigation** | 🔴 HIGH | Patent involved in lawsuit |
| **Transfer** | 🟡 MEDIUM | Ownership changed |
| **License** | 🟡 MEDIUM | Licensed to third party |
| **Pledge** | 🟡 MEDIUM | Used as collateral |
| Opposition | 🟠 | Third party opposition filed |
| Re-examination | 🟠 | Under re-examination |
| Invalid-procedure | 🟠 | Invalidation proceeding |

## Output Structure

The output will be a structured markdown report, following this format:

**Patent Legal Status Report: [Patent Number(s) or ID(s)]**

---

**1. Executive Summary**
*   **Query Date:** [query_date]
*   **Total Patents Queried:** [total_queried]
*   **Active Patents:** [summary.active]
*   **Inactive Patents:** [summary.inactive]
*   **Pending Patents:** [summary.pending]
*   **Patents with Litigation Risk:** [summary.with_litigation]
*   **Core Insight:** This report provides a quick overview of the legal validity and potential risks of the queried patents.

**2. Detailed Patent Status (Per Patent)**
*(For each queried patent, its detailed status is displayed)*

**Patent Number: [patent_number]**

*   **Simple Status:** [simple_status] [status_icon]
*   **Is Valid:** [is_valid]
*   **Detailed Status Events:**
    *   [detailed_status[0]]
    *   ... (List all detailed status events)
*   **Legal Events:**
    *   [legal_events[0].event] (Risk Level: [legal_events[0].risk_level], Description: [legal_events[0].description])
    *   ... (List all legal events)
*   **Has Risk Events:** [has_risk_events]
*   **Status Date:** [status_date]

**3. Summary of Queried Patents**
*   **Status Distribution:**

| Status | Count |
| :--- | :--- |
| Active | [summary.active] |
| Inactive | [summary.inactive] |
| Pending | [summary.pending] |
| With Litigation | [summary.with_litigation] |

**4. Attached Visualizations**
*   Status Distribution (1_status_distribution.png)
*   Risk Events (2_risk_events.png)

## Quick Reference

| Question | Check |
|----------|-------|
| Can I sell this product? | `simple_status` = Active → ⚠️ Risk |
| Is the patent expired? | `simple_status` = Inactive |
| Is it being enforced? | `legal_events` contains |
| Who owns it now? | Use Bibliography API |

## Common Use Cases

### 1. Before Sourcing
Check if competitor patents are still valid before copying designs.

### 2. Due Diligence
Verify patent status before business deals or investments.

### 3. FTO Analysis
Determine freedom to operate in a market.

### 4. Monitoring
Track status changes of patents you're watching.

## Batch Query Example

```bash
# Check multiple competitor patents
python3 scripts/patent_legal_status.py '{"patentNumber": "USD900000S,USD901000S,USD902000S,USD903000S"}'
```

## Charts Generated

| Chart | Description | File |
|-------|-------------|------|
| Status Distribution | Patent status breakdown | `1_status_distribution.png` |
| Risk Events | Upcoming expiry / lapse events | `2_risk_events.png` |

## Limitations

- Maximum 100 patents per query
- Some recent status changes may not be reflected immediately
- PCT applications show special status codes
- Status interpretation varies by jurisdiction

## Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/legalStatus` | Simple status, detailed status, legal events |
| Zhihuiya | `/api/v1/tools/linkfox/zhihuiya/simpleBibliography` | Patent title, type, country |

**Coverage**: 170M+ patents from 150+ countries. Comprehensive litigation, transfer, license, and pledge event records included.


## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |

## References

- USPTO Status Codes: https://www.uspto.gov
- EPO Legal Status: https://www.epo.org
