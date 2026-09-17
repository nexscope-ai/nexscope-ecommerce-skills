---
name: ecommerce.patent-claims
description: Retrieves patent claims data from Zhihuiya (PatSnap). Trigger when the user mentions patent claims, claim text, independent claims, dependent claims, claim count, claims tree, claims analysis, claim scope, claim language, viewing the claims section of a specific patent, patent claims, independent claims, dependent claims, claims text, PatSnap. Also trigger when the user requests patent claims information by patent ID or publication number, even without explicitly mentioning Zhihuiya or PatSnap.
---

# Zhihuiya Patent Claims Data

This skill guides you on how to retrieve and present patent claims data from the Zhihuiya (PatSnap) patent database, helping IP professionals, patent analysts, and R&D teams quickly access the claims section of any patent.

## Calling the Tool

- **API Endpoint**: `/zhihuiya/claimData` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_claims.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.patent-claims-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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
1. Set the `NEXSCOPE_API_KEY` environment variable with a valid API key.
2. If credits are insufficient, visit https://www.nexscope.ai/pricing?co-from=skillNS to top up your balance.
3. For onboarding and setup guidance, refer to https://www.nexscope.ai/help/skills-external-access?co-from=skillNS
## Core Concepts

Patent claims define the legal scope of protection granted by a patent. They are the most critical part of a patent document for infringement analysis, freedom-to-operate assessments, and prior art comparisons. This tool retrieves the full set of claims for a single patent by its patent ID or publication number.

**Family substitution**: When a patent's claims are unavailable in the database, you can optionally request that claims from a related family member patent be returned instead. This is controlled by the `replaceByRelated` parameter.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Patent ID | patentId | Internal Zhihuiya patent identifier | 98a1b2c3-... |
| Publication Number | pn | Publication or grant number of the patent | CN115000000A |
| Related PN | pnRelated | Publication number of the family member used as substitute (only present when family substitution occurred) | US20230001234A1 |
| Claims | claims | Array of claim objects containing the claim text and metadata | [...] |
| Claim Count | claimCount | Total number of claims in the patent | 15 |

## Parameter Guide

### Required (at least one)

You must provide **at least one** of the following two parameters. If both are provided, `patentId` takes priority.

| Parameter | Description | Format |
|-----------|-------------|--------|
| patentId | Single patent ID only. Do NOT pass comma-separated multiple IDs | Single string |
| patentNumber | Single publication/announcement number only. Do NOT pass comma-separated multiple numbers | Single string |

### Optional

| Parameter | Description | Values |
|-----------|-------------|--------|
| replaceByRelated | Whether to substitute with a family member's claims when the target patent's claims are unavailable | `1` = yes, `0` = no (default) |

### How to Choose Between patentId and patentNumber

- Use **patentNumber** when the user provides a publication or grant number (e.g., `CN115000000A`, `US11234567B2`). This is the most common scenario.
- Use **patentId** when the user provides an internal Zhihuiya identifier, typically obtained from a previous Zhihuiya search result.
- When the user provides both, pass both and the API will prefer patentId.

> **Single-patent limit**: This endpoint consumes significant credits. To query multiple patents, obtain explicit user consent and make separate calls for each. Only 1 patent per call (`patentId` and `patentNumber` do not accept comma-separated multiple values).

## Usage Examples

**1. Single patent by publication number**
```json
{"patentNumber": "CN115000000A"}
```

**3. Single patent by patent ID**
```json
{"patentId": "98a1b2c3-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

**4. With family substitution enabled**
```json
{"patentNumber": "CN115000000A", "replaceByRelated": "1"}
```

## Display Rules

1. **Present claims clearly**: Display claims in a numbered list preserving the original claim numbering. Use indentation or formatting to distinguish independent claims from dependent claims where possible.
2. **Highlight claim count**: Always state the total number of claims returned for each patent.
3. **Family substitution notice**: If `pnRelated` is present in a result, explicitly inform the user that the claims shown are from a family member patent and provide the family member's publication number.
4. **Single patent results**: Results contain a single patent's data; present the output clearly with the publication number as the heading.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest the user verify the patent number format or try enabling family substitution.
6. **No subjective analysis**: Present the raw claim text without legal interpretation unless the user specifically requests analysis.
## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; omitting both will result in an error.
- **Single patent per request**: Only one patent ID or publication number may be passed per call (no comma-separated batches).
- **Claims availability**: Not all patents have claims data available. Use `replaceByRelated` = `1` to attempt family member substitution when claims are missing.
- **Claim object structure**: The individual claim objects within the `claims` array may vary in structure depending on the patent office and data source.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent claims retrieval and analysis:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims of patent XX" | Single patent claims lookup |
| "How many claims does patent XX have" | Claim count query |
| "What are the independent claims of XX" | Claims retrieval + display |
| "The claims are not available, try a family member" | Family substitution query |
| "Patent claim scope", "claim language" | Claims retrieval |

**Not applicable** -- Needs beyond patent claims data:
- Patent search or discovery (finding patents by keyword/topic)
- Patent legal status or prosecution history
- Patent citation or reference analysis
- Patent full-text beyond claims (abstract, description, drawings)
- Freedom-to-operate or infringement opinions (legal advice)
