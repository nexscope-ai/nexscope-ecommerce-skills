---
name: ecommerce-patent-core-bibliography
description: "Query patent simple bibliographic (catalog) data from the Zhihuiya patent database. Triggered when users mention patent bibliographic information queries, patent basic info retrieval, patent catalog data, patent publication details, searching by patent number for inventors, patent applicant information, patent abstract retrieval, patent classification codes (IPC/CPC), patent citation queries, or any request to search for structured metadata by patent ID or publication number, patent brief bibliography, patent basic info, patent number lookup, patent abstract, PatSnap, or patent metadata. Even if the user does not explicitly mention \"Zhihuiya\" or \"bibliographic info,\" this skill should be triggered whenever their need involves querying core bibliographic fields of specific patents."
---

# Zhihuiya Patent Simple Bibliography

This skill guides you on how to query simple bibliographic data for patents using the Zhihuiya patent database, helping users retrieve structured patent metadata efficiently.

## Core Concepts

The Zhihuiya Simple Bibliography tool retrieves basic bibliographic (front-page) information for one or more patents, including title, abstract, applicants, inventors, assignees, classification codes, filing dates, priority claims, and citation references.

**Lookup modes**: Use either `patentId` (Zhihuiya internal patent ID) or `patentNumber` (public publication/grant number). If both are supplied, `patentId` takes priority. Either field may contain up to 100 comma-separated values.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Up to 100 comma-separated patent IDs. At least one of `patentId` or `patentNumber` must be provided. |
| patentNumber | string | Conditionally | Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. At least one of `patentId` or `patentNumber` must be provided. |

**Priority rule**: When both `patentId` and `patentNumber` are present, the API uses `patentId` and ignores `patentNumber`.

> **Batch limit**: `patentId` or `patentNumber` may contain up to 100 comma-separated values. Because the endpoint consumes significant credits, confirm the intended batch before submitting a multi-patent request.

## Response Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | Zhihuiya internal patent identifier |
| Title | title | Patent title |
| Abstract | abstractContent | Patent abstract text |
| Publication Number | publicationNumber | Publication number |
| Publication/Grant Number | pn | Full publication/grant number |
| Country Code | country | Country code of the patent |
| Publication Country | publicationCountry | Country where the patent was published |
| Publication Date | publicationDate | Publication date |
| Publication Kind | publicationKind | Kind code of the publication |
| Patent Type | patentType | Type of patent (e.g., invention, utility model, design) |
| Kind Code | kind | Patent kind code |
| Application Number | applicationNo | Application number |
| Application Date | applicationDate | Application filing date |
| Applicants | applicants | List of applicants |
| Inventors | inventors | List of inventors |
| Assignees | assignees | List of patent assignees/owners |
| Assignee Addresses | assigneeAddresses | List of assignee addresses |
| IPC Main | ipcMain | Main IPC classification code |
| IPC Further | ipcFurther | Additional IPC classification codes |
| CPC Main | cpcMain | Main CPC classification code |
| CPC Further | cpcFurther | Additional CPC classification codes |
| LOC | loc | Locarno classification codes (design patents) |
| GBC | gbc | GBC classification codes |
| Priority Claims | priorityClaims | List of priority claim entries |
| PCT Application No | pctApplicationNo | PCT international application number |
| PCT Filing Date | pctFilingDate | PCT international filing date |
| PCT Entry Date | pctEntryDate | PCT national phase entry date |
| Cited Patents | citedPatents | List of cited patent references |
| Cited Non-Patents | citedNonPatents | List of cited non-patent literature |

## Invocation

- **API Endpoint**: `POST /zhihuiya/simpleBibliography` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_core_bibliography.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry after failure or empty results. Batch requests may contain up to 100 comma-separated patents; confirm the intended batch first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-simple-bibliography-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.

## Usage Examples

**1. Look up a single patent by publication number**
```
User: "Show me the bibliographic info for patent US11234567B2."
Action: Call with patentNumber = "US11234567B2"
```

**2. Retrieve inventor and applicant information**
```
User: "Who are the inventors and applicants for patent US20230001234A1?"
Action: Call with patentNumber = "US20230001234A1", then extract the inventors and applicants fields from the response.
```

**3. Check patent classification codes**
```
User: "What IPC and CPC codes does patent EP3999999B1 have?"
Action: Call with patentNumber = "EP3999999B1", then present ipcMain, ipcFurther, cpcMain, and cpcFurther from the response.
```

**4. Get patent abstract and citation references**
```
User: "Show me the abstract and cited patents for CN114000000B."
Action: Call with patentNumber = "CN114000000B", then display abstractContent and citedPatents.
```

## Display Rules

1. **Present data clearly**: Show each returned patent in a separate, well-structured section or table.
2. **Selective display**: When results contain many fields, prioritize showing title, publication number, applicants, inventors, application date, publication date, IPC/CPC main codes, and abstract. Show additional fields only when the user specifically asks.
3. **List fields**: For array fields (inventors, applicants, assignees, classification codes, citations), present them as comma-separated values or bulleted lists depending on length.
4. **Empty fields**: Omit fields that are null or empty from the display rather than showing blank entries.
5. **Error handling**: When a query fails, explain the reason based on the error message and suggest the user verify the patent number or ID format.

## Important Limitations

- **Batch size**: At most 100 comma-separated patent IDs or publication numbers per request.
- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; omitting both will cause an error.
- **patentId takes priority**: If both parameters are supplied, only `patentId` is used.
- **Data scope**: This tool returns simple bibliographic data only. It does not return full-text claims, detailed descriptions, legal status, or patent family information.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent bibliographic data retrieval:

| User Says | Scenario |
|-----------|----------|
| "Look up patent XX" / "Get info for patent XX" | Single patent bibliography lookup |
| "Who invented patent XX" / "Who is the applicant" | Inventor / applicant retrieval |
| "What's the IPC code for XX" / "Classification of XX" | Classification code lookup |
| "Show me the abstract of XX" | Abstract retrieval |
| "When was patent XX filed" / "Publication date of XX" | Date information lookup |
| "What patents does XX cite" | Citation reference lookup |
| "Patent basic info" / "Patent front page data" | General bibliography retrieval |

**Not applicable** -- Needs beyond simple bibliographic data:

- Full-text patent claims or detailed description
- Patent legal status or prosecution history
- Patent family / equivalents analysis
- Patent valuation or landscaping
- Freedom-to-operate or infringement analysis
- Patent search by keyword or semantic query (this tool requires specific patent identifiers)
