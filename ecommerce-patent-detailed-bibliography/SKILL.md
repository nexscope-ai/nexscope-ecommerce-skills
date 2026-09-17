---
name: ecommerce.patent-detailed-bibliography
description: Query patent bibliographic (catalog) information from the Zhihuiya patent database by patent ID or publication number. Triggered when users mention patent bibliographic info queries, patent catalog information, patent applicant queries, patent inventor queries, patent classification codes, patent abstract retrieval, patent citation analysis, patent priority claims, patent application citations, patent examiner information, patent bibliographic data, inventor lookup, applicant lookup, patent classification, patent metadata, PatSnap, or patent citations. Even if the user does not explicitly mention "bibliographic info," this skill should be triggered whenever their need involves querying detailed metadata for a specific patent by patent ID or publication number.
---

# Zhihuiya Patent Bibliography

This skill guides you on how to query patent bibliography (bibliographic) data from the Zhihuiya patent database, helping users retrieve detailed metadata for specific patents.

## Core Concepts

Patent bibliography data (also called bibliographic data) is the structured metadata associated with a patent document. It includes the patent title, applicants, inventors, classification codes, priority claims, cited references, abstracts, and more. This tool allows querying by **patent ID** or **publication number**, returning comprehensive bibliographic records for a single patent per request.

**Patent types**: The `patentType` field indicates the type of patent document:
- `APPLICATION` -- Invention application (published but not yet granted)
- `PATENT` -- Granted invention patent
- `UTILITY` -- Utility model
- `DESIGN` -- Design patent

## Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | Internal patent identifier |
| Publication Number | pn | Publication/announcement number |
| Invention Title | inventionTitle | Patent title with language info |
| Abstracts | abstracts | Patent abstract text |
| Patent Type | patentType | APPLICATION, PATENT, UTILITY, or DESIGN |
| Applicants | applicants | Original applicant(s) |
| Assignees | assignees | Current patent holder(s) / assignee(s) |
| Inventors | inventors | Inventor(s) listed on the patent |
| Agents | agents | Patent attorney / agent(s) |
| Agency | agency | Filing agency / patent firm |
| Examiners | examiners | Patent examiner(s) |
| Priority Claims | priorityClaims | Priority right declarations |
| Application Reference | applicationReference | Application filing data |
| Publication Reference | publicationReference | Publication data |
| Dates of Public Availability | datesOfPublicAvailability | Public availability dates |
| IPC Classification | classificationIpcr | International Patent Classification |
| CPC Classification | classificationCpc | Cooperative Patent Classification |
| UPC Classification | classificationUpc | US Patent Classification |
| LOC Classification | classificationLoc | Locarno Classification (designs) |
| FI Classification | classificationFi | FI classification codes (Japan) |
| F-term Classification | classificationFterm | F-term codes (Japan) |
| GBC Classification | classificationGbc | GBC classification |
| Cited Patents | referenceCitedPatents | Patent documents cited as references |
| Cited Non-Patent Literature | referenceCitedOthers | Non-patent literature cited |
| Related Documents | relatedDocuments | Divisional / continuation application info |
| PCT Filing Data | pctOrRegionalFilingData | PCT or regional phase filing data |
| PCT Publishing Data | pctOrRegionalPublishingData | PCT or regional phase publication data |
| Estimated Expiry Date | exdt | Estimated patent expiration date (Zhihuiya) |

## Invocation

- **API Endpoint**: `POST /zhihuiya/bibliography` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_detailed_bibliography.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search. **Single Patent Limit**: This endpoint consumes many credits. Each call can only pass one patent; if you need to check multiple patents, you must obtain explicit user consent and make separate requests.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-bibliography-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Parameter Guide

The tool accepts two parameters. **At least one must be provided**; if both are supplied, `patentId` takes priority.

| Parameter | When to Use | Format |
|-----------|-------------|--------|
| `patentId` | When the user provides an internal Zhihuiya patent ID | Single patent ID only. Do NOT pass comma-separated multiple IDs. |
| `patentNumber` | When the user provides a publication/announcement number | Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. |

### Tips for Identifying Input Type

- If the user provides something like `US10123456B2`, `CN112345678A`, `EP3456789B1`, or `WO2023123456A1`, treat it as a **publication number** and use `patentNumber`.
- If the user provides a purely numeric or opaque identifier that does not match standard publication number patterns, treat it as a **patent ID** and use `patentId`.
- Only one patent may be passed per request. If the user has multiple patents, obtain explicit consent and make a separate call for each.

## Usage Examples

**1. Look up a single patent by publication number**
```
User: "Show me the bibliography for US10123456B2"
Action: Call with patentNumber = "US10123456B2"
```

**2. Look up a patent by internal ID**
```
User: "Query bibliography for patent ID 8fa3b2c1-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
Action: Call with patentId = "8fa3b2c1-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables or organized sections. For each patent, highlight the most commonly needed fields: title, applicants/assignees, inventors, filing/publication dates, classification codes, and abstract.
2. **Respect the query scope**: Only display the fields the user asked about. If they asked for "inventors", do not dump the entire bibliography unless requested.
3. **Patent type labels**: Translate `patentType` codes into human-readable labels (APPLICATION = Invention Application, PATENT = Granted Invention, UTILITY = Utility Model, DESIGN = Design Patent).
4. **Single-patent results**: Results contain a single patent's data; present it clearly.
5. **Error handling**: When a query returns an error or empty results, explain clearly and suggest the user verify their patent ID or publication number.
6. **No subjective analysis**: Present factual bibliographic data without speculative legal or commercial interpretations.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent bibliography / metadata lookups:

| User Says | Scenario |
|-----------|----------|
| "Look up patent info for XX" | Single patent bibliography |
| "Who are the inventors of patent XX" | Inventor lookup |
| "Who owns patent XX", "current assignee" | Assignee / applicant query |
| "What IPC/CPC class is patent XX" | Classification lookup |
| "Show me the abstract of patent XX" | Abstract retrieval |
| "What patents does XX cite" | Citation analysis |
| "When does patent XX expire" | Expiry date query |
| "Patent details", "patent metadata" | General bibliography |

**Not applicable** -- Needs beyond patent bibliography:

- Full-text patent search by keyword or semantic query
- Patent landscape / analytics reports
- Patent valuation or legal status tracking
- Freedom-to-operate or infringement analysis
- Patent family tree exploration (unless specific publication numbers are given)

**Boundary judgment**: When users say "find patents about X" or "search for patents in field Y", that is a patent search task, not a bibliography lookup. This skill only applies when the user already has a patent ID or publication number and wants to retrieve its metadata.
