---
name: ecommerce.patent-description-data
description: Retrieve patent description (specification) data from the Zhihuiya patent database by patent ID or publication number. Triggered when users mention patent specification, patent full text, patent technical description, patent embodiment details, Zhihuiya specification data, patent specification, patent full text, technical description, embodiment details, PatSnap, or patent detailed description. Even if the user does not explicitly say "Zhihuiya," this skill should be triggered whenever they need to view the complete specification/description content of one or more patents.
---

# Zhihuiya Patent Description Data

This skill guides you on how to query patent description (specification) data from the Zhihuiya patent database, helping users retrieve the full-text description content of specific patents.

## Core Concepts

A patent description (also called the specification) is the detailed technical document that accompanies a patent filing. It discloses how the invention works, preferred embodiments, and other technical details required by patent law. This tool queries the Zhihuiya database to return description data for a single patent per request, identified by its internal patent ID or public publication number.

**Identifier priority**: When both a patent ID and a publication number are provided for the same query, the patent ID takes precedence.

**Family substitution**: If the description for a given patent is unavailable, the tool can optionally return the description from a related family member patent instead.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Internal patent ID. At least one of patentId or patentNumber must be provided. Single patent ID only. Do NOT pass comma-separated multiple IDs. |
| patentNumber | string | Conditionally | Publication / announcement number. At least one of patentId or patentNumber must be provided. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. |
| replaceByRelated | string | No | Whether to substitute a family patent's description when the target patent's description is unavailable. `1` = yes, `0` = no. |

> **Single Patent Limit**: This endpoint consumes many credits. If you need to check multiple patents, you must obtain explicit user consent and make separate requests. Each call can only pass one patent (`patentId` and `patentNumber` cannot be comma-separated into multiple values).

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of patent records returned |
| data | array | List of patent description objects |
| data[].patentId | string | Patent ID |
| data[].pn | string | Publication number |
| data[].pnRelated | string | Publication number of the substitute family patent (only present when family substitution is used) |
| data[].description | array | Description / specification content sections |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by the query |
| type | string | Rendering style hint |

## Invocation

- **API Endpoint**: `POST /zhihuiya/descriptionData` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_description_data.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search. **Single Patent Limit**: This endpoint consumes many credits. Each call can only pass one patent; if you need to check multiple patents, you must obtain explicit user consent and make separate requests.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-description-data-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## How to Build Queries

### Querying by Publication Number

When users provide a patent publication number (e.g., CN115099012A, US20230012345A1), pass it via the `patentNumber` parameter:

```
patentNumber: "CN115099012A"
```

### Querying by Patent ID

When users provide internal Zhihuiya patent IDs, pass them via the `patentId` parameter:

```
patentId: "abc123def456"
```

### Single-Patent Queries

Only one patent may be passed per request. If the user has multiple patents, obtain explicit consent and make a separate call for each. Do NOT pass comma-separated values to `patentId` or `patentNumber`.

```
patentNumber: "CN115099012A"
```

### Family Substitution

When a patent's description is not available in the database and the user still wants content, enable family substitution:

```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

## Usage Examples

**1. Look up a single patent description by publication number**
```
patentNumber: "CN115099012A"
```

**2. Look up with family substitution enabled**
```
patentNumber: "CN115099012A"
replaceByRelated: "1"
```

**3. Look up by patent ID**
```
patentId: "some-patent-id"
```

## Display Rules

1. **Present data faithfully**: Show the returned description content clearly without altering technical details or adding subjective interpretation.
2. **Structured output**: When the description contains multiple sections (background, summary, detailed description, claims, etc.), present them with clear headings for readability.
3. **Family substitution notice**: If the response includes a `pnRelated` field, explicitly inform the user that the description was sourced from a related family patent and state the substitute publication number.
4. **Single-patent results**: Results contain a single patent's data per call. If the user needs multiple patents, make separate single-patent calls (with explicit consent).
5. **Error handling**: When a query fails or returns no data, explain the reason and suggest the user verify the patent ID or publication number.
6. **Large content warning**: Patent descriptions can be very long. Summarize key sections first and offer to show the full text if the user wants it.

## Important Limitations

- **Identifier requirement**: At least one of `patentId` or `patentNumber` must be provided; the tool cannot search by keyword or applicant name.
- **Single patent per request**: Only one patent ID or publication number may be passed per call (no comma-separated batches).
- **Availability**: Not all patents have descriptions available in the database. Use `replaceByRelated: "1"` to attempt family substitution when needed.
- **Priority rule**: If both `patentId` and `patentNumber` are supplied, `patentId` takes precedence.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries about patent description / specification content:

| User Says | Scenario |
|-----------|----------|
| "Show me the description of patent XX" | Single patent description lookup |
| "I need the detailed text of CN115099012A" | Lookup by publication number |
| "Can you find a family patent's description instead" | Family substitution query |
| "What does this patent describe technically" | Description content review |

**Not applicable** -- Needs beyond patent description data:
- Patent search by keyword, applicant, or classification
- Patent claim analysis or claim chart generation
- Patent legal status or prosecution history
- Patent landscape or statistical analysis
- Freedom-to-operate or infringement opinions
