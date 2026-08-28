---
name: ecommerce-patent-legal-status-data
description: "Query patent legal status information from the Zhihuiya (PatSnap) database. Triggered when users mention patent legal status, patent validity check, patent status query, patent event history, simple legal status, legal events such as transfer, license, pledge, opposition, litigation, re-examination, patent legal status, patent validity, patent events, transfer/license/pledge, PatSnap, or patent status lookup. Also triggered when users ask whether a patent is active, inactive, pending, expired, granted, withdrawn, or revoked, or want to look up legal status by patent ID or publication number."
---

# Zhihuiya Patent Legal Status

This skill guides you on how to query patent legal status information via the Zhihuiya (PatSnap) platform, helping users quickly determine the current legal standing and event history of a single patent.

## Invocation

- **API Endpoint**: `POST /zhihuiya/legalStatus` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_legal_status_data.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search. **Single Patent Limit**: This endpoint consumes many credits. Each call can only pass one patent; if you need to check multiple patents, you must obtain explicit user consent and make separate requests.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-legal-status-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Core Concepts

The Zhihuiya Patent Legal Status tool returns three layers of legal information for each patent:

1. **Simple Legal Status** -- A high-level summary of the patent's current standing (e.g., Active, Inactive, Pending, Undetermined, PCT designated period, PCT designated expiration).
2. **Legal Status** -- A detailed status describing the patent's lifecycle stage (e.g., Published, Examining, Granted, Abandoned, Withdrawn, Rejected, Expired, Revoked, Ceased, Restoration, etc.).
3. **Legal Events** -- Specific legal actions that have occurred on the patent (e.g., Transfer, License, Pledge, Opposition, Litigation, Re-examination, Customs, Preservation, Invalid-procedure, Oral-procedure, Declassification, Double application, Trust).

**Patent identification**: Patents can be looked up by either patent ID or publication (announcement) number. When both are provided, patent ID takes priority. Only one patent may be passed per request.

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| patentId | Conditionally | Patent ID. At least one of patentId or patentNumber must be provided. Single patent ID only. Do NOT pass comma-separated multiple IDs. |
| patentNumber | Conditionally | Publication (announcement) number. At least one of patentId or patentNumber must be provided. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. |

- If the user provides a publication number (e.g., CN115xxxxxxA, US11xxxxxxB2, EP3xxxxxxA1), use `patentNumber`.
- If the user provides an internal patent ID, use `patentId`.
- When both are supplied, `patentId` takes precedence.

> **Single Patent Limit**: This endpoint consumes many credits. If you need to check multiple patents, you must obtain explicit user consent and make separate requests. Each call can only pass one patent (`patentId` and `patentNumber` cannot be comma-separated into multiple values).

## Response Fields

| Field | Description |
|-------|-------------|
| patentId | The patent's internal ID |
| pn | Publication (announcement) number |
| simpleLegalStatus | High-level status: Active, Inactive, Pending, Undetermined, PCT designated period, PCT designated expiration |
| legalStatus | Detailed lifecycle status (Published, Examining, Granted, Abandoned, Withdrawn, Rejected, Expired, Revoked, Ceased, etc.) |
| eventStatus | Legal events (Transfer, License, Pledge, Opposition, Litigation, Re-examination, etc.) |
| legalDate | Date of the most recent legal status update |

## Usage Examples

**1. Check whether a single patent is still active**
```
Query the legal status for patent publication number CN115000000A.
```

**2. Identify legal events on a patent**
```
Has patent CN115000000A been involved in any litigation, transfer, or pledge events?
```

**3. Determine if a patent has expired or been revoked**
```
Check if patent US10000000B1 is expired, revoked, or still in force.
```

## Display Rules

1. **Present data clearly**: Show results in a structured table. Include the publication number, simple legal status, detailed legal status, and legal events for each patent.
2. **Translate status values**: When the user's language preference is clear, present status labels in that language while keeping the canonical English value in parentheses for precision.
3. **Highlight key findings**: If the user is checking validity, prominently state whether each patent is Active, Inactive, or Pending at the top of the response.
4. **Legal date context**: When `legalDate` is available, include it so users know how recent the status information is.
5. **Error handling**: If the query fails or returns no results, explain the possible reasons (invalid patent number format, patent not found in database) and suggest the user double-check the input.
6. **Single patent result**: Results contain a single patent's data.

## Important Limitations

- **Single patent per request**: Only one patent ID or publication number may be passed per call (no comma-separated batches).
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; the request will fail if both are empty.
- **Patent ID priority**: When both `patentId` and `patentNumber` are provided, the system uses `patentId` and ignores `patentNumber`.
- **Data coverage**: Results depend on the Zhihuiya (PatSnap) database coverage; some very recent filings may not yet be reflected.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about patent legal standing and events:

| User Says | Scenario |
|-----------|----------|
| "Is this patent still valid/active" | Simple legal status check |
| "What is the legal status of patent XX" | Detailed status lookup |
| "Has this patent been transferred or licensed" | Legal event query |
| "Any litigation on this patent" | Legal event filtering |
| "Patent legal status for CN115XXXXXXA" | Direct publication number lookup |

**Not applicable** -- Needs beyond patent legal status:

- Patent search by keyword, classification, or applicant name
- Patent full-text or claims retrieval
- Patent valuation or commercial analysis
- Freedom-to-operate (FTO) analysis
- Patent family or citation analysis
