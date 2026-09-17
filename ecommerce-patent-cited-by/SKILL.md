---
name: ecommerce.patent-cited-by
description: Queries patent citation data from Zhihuiya (PatSnap), including citation counts and citing patent details. Trigger when the user mentions patent cited by, citation analysis, patent influence, citation frequency, patent family citations, forward citations, which patents cite a given patent, patent citations, citation count, patent influence, citation analysis, PatSnap. Also trigger when the user needs to query a patent's citation count or which patents cite it, even without explicitly mentioning Zhihuiya or PatSnap.
---

# Zhihuiya Patent Citations Explorer

This skill guides you on how to query patent citation data from Zhihuiya (PatSnap), helping users understand the citation landscape of specific patents.

## Core Concepts

Patent citation analysis reveals how influential a patent is within its technology domain. When Patent B references Patent A in its prior art section, Patent A is said to be "cited by" Patent B. A higher citation count generally indicates greater technological significance and broader industry influence.

**Key metrics**:
- **3-year citations** (`citedBy3y`): Number of times the patent was cited within 3 years of publication. Indicates early-stage impact.
- **5-year citations** (`citedBy5y`): Number of times the patent was cited within 5 years. Indicates medium-term influence.
- **Simple family citations** (`citedBySimpleFamily`): Count of simple patent family members that cite the patent.
- **INPADOC family citations** (`citedByInpadocFamily`): Count of INPADOC patent family members that cite the patent.
- **PatSnap family citations** (`citedByPatsnapFamily`): Count of PatSnap-defined patent family members that cite the patent.

## Parameter Guide

You must provide at least one of the following identifiers. If both are supplied, patent ID takes priority.

| Parameter | Description | Example |
|-----------|-------------|---------|
| patentId | Zhihuiya internal patent IDs; up to 100 comma-separated values. | abc123def456 |
| patentNumber | Publication / announcement number. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. | US10123456B2 |

**Important**: At least one of `patentId` or `patentNumber` is required. When the user provides a publication number (e.g., "US10123456B2"), use `patentNumber`. When they provide internal IDs, use `patentId`.

> **Batch limit**: `patentId` or `patentNumber` may contain up to 100 comma-separated values. Because the endpoint consumes significant credits, confirm the intended batch before submitting a multi-patent request.

## Usage Examples

**1. Single patent citation lookup by publication number**
Query: "How many citations does patent US10123456B2 have?"
```json
{
  "patentNumber": "US10123456B2"
}
```

**3. Lookup by patent ID**
Query: "Get citation data for patent ID abc123def456"
```json
{
  "patentId": "abc123def456"
}
```

## Display Rules

1. **Present data in tables**: Show citation results in clear, structured tables. Include the publication number, 3-year citations, 5-year citations, and family citation counts.
2. **Highlight key metrics**: For each returned patent, highlight citation counts across the 3-year, 5-year, and family metrics.
3. **Explain family types**: If the user is unfamiliar with patent families, briefly explain the difference between Simple, INPADOC, and PatSnap family definitions.
4. **Citing patent details**: If the response includes a `citedByPatents` array with details of citing patents, present them in a sub-table or expandable list.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest checking whether the patent number or ID is correct.
6. **No subjective advice**: Present factual citation data without making judgments about patent value or investment decisions.

## Calling the Tool

- **API Endpoint**: `/zhihuiya/patentCited` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_cited_by.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.patent-cited-by-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
- Response body <= 8 KB: write to disk then print full JSON to stdout
- Response body > 8 KB: write to disk then print only a summary to stdout (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Reading data**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file as needed, avoiding loading the entire JSON into context.
## Authentication & Credits

If you encounter authentication or credit issues:

### Error conditions
- **API Key not configured**: The `NEXSCOPE_API_KEY` environment variable is not set.
- **HTTP 401 or 402 status code**
- **Insufficient credits/balance**: Response message indicates credit balance exhausted, quota exceeded, subscription expired, or recharge required.

### Resolution steps
Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
For onboarding and setup guidance, refer to https://skill.nexscope.com/nexscopeskills/guide.htm
## User Expression & Scenario Quick Reference

**Applicable** -- Patent citation analysis scenarios:

| User Says | Scenario |
|-----------|----------|
| "How many times has this patent been cited" | Basic citation count |
| "Which patents cite this one" | Citing patent list |
| "Patent influence analysis" | Citation-based impact |
| "3-year / 5-year citation count" | Time-windowed citation metrics |
| "Patent family citation data" | Family-level citation analysis |
| "Forward citations for patent X" | Synonym for cited-by lookup |

**Not applicable** -- Needs beyond patent citation data:
- Patent full-text search or semantic search
- Patent legal status or prosecution history
- Patent valuation or licensing recommendations
- Backward citations (references *made by* a patent)
