---
name: ecommerce-patent-references
description: "Query patent forward citation details from the Zhihuiya patent database. Triggered when users ask about patent citations, cited patents, cited references, patent references, forward citations, prior art citations, or want to see which patents and non-patent literature specific patents cited during the application process, patent cited references, forward citations, patent references, citation analysis, or PatSnap. When users provide a patent ID or publication number and need citation information, even if they do not explicitly say \"forward citation,\" any request about which references a patent cited applies."
---

# Zhihuiya Patent Forward Citation

This skill guides you on how to query patent forward citation data from the Zhihuiya patent database, helping users discover the patents and non-patent literature cited by specific patents during their application process.

## Core Concepts

**Forward citation** refers to the patents and non-patent literature that a given patent has cited in its application documents. This is a fundamental aspect of patent analysis -- understanding what prior art a patent references helps assess its novelty, scope, and technological lineage.

- **Patent citations** (`citedPatents`): Other patents referenced by the queried patent.
- **Non-patent literature citations** (`citedOthers`): Academic papers, technical reports, and other non-patent documents referenced by the queried patent.

## Parameter Guide

You must provide at least one of the following two parameters. If both are provided, `patentId` takes priority.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Up to 100 comma-separated patent IDs. |
| patentNumber | string | Conditionally | Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. |

**Rules**:
1. At least one of `patentId` or `patentNumber` must be provided.
2. If both are present, `patentId` is used preferentially.
3. A request may contain up to 100 comma-separated patents. Confirm the intended batch before a multi-patent call.

> **Batch limit**: `patentId` or `patentNumber` may contain up to 100 comma-separated values. Because the endpoint consumes significant credits, confirm the intended batch before submitting a multi-patent request.

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Total number of records returned |
| data | array | List of patent citation results |
| data[].patentId | string | Patent ID of the queried patent |
| data[].pn | string | Publication/announcement number |
| data[].citedPatents | array | List of cited patent documents |
| data[].citedOthers | array | List of cited non-patent literature |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by the query |
| type | string | Rendering style hint |

## Invocation

- **API Endpoint**: `POST /zhihuiya/patentForwardCitation` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_references.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry after failure or empty results. Batch requests may contain up to 100 comma-separated patents; confirm the intended batch first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-patent-forward-citation-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.

## Usage Examples

**1. Query forward citations by publication number**
```
Look up the forward citations for patent US10000000B2.
```
Parameters: `{"patentNumber": "US10000000B2"}`

**2. Query forward citations by patent ID**
```
Retrieve the cited references for patent ID 12345678.
```
Parameters: `{"patentId": "12345678"}`

**3. Query forward citations using both identifiers**
```
Look up citations for patent ID 12345678 (publication number US10000000B2).
```
Parameters: `{"patentId": "12345678", "patentNumber": "US10000000B2"}` (patentId takes priority)

## Display Rules

1. **Present data clearly**: Show citation results in well-structured tables, separating patent citations from non-patent literature citations.
2. **Summarize counts**: Always state the total number of cited patents and cited non-patent literature items.
3. **No fabrication**: Only display data returned by the API. Do not infer or fabricate citation details.
4. **Error handling**: When a query fails, explain the reason based on the error response and suggest the user verify their patent ID or publication number.
5. **Per-patent results**: Present each returned patent's citation data separately.
6. **Empty results**: If a patent has no citations, explicitly inform the user rather than showing an empty table.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent citation queries:

| User Says | Scenario |
|-----------|----------|
| "What patents does XX cite" | Forward citation lookup |
| "Show me the references for patent XX" | Citation detail retrieval |
| "What prior art is cited by XX" | Prior art reference query |
| "List the cited literature for XX" | Non-patent literature lookup |
| "Citation analysis for patent XX" | Combined patent + literature citation |
| "What documents does patent XX reference" | General citation query |

**Not applicable** -- Needs beyond forward citation data:
- Backward/reverse citations (who cites this patent)
- Patent validity or legal status
- Patent family analysis
- Patent full-text search
- Patent classification or landscape analysis
