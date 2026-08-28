---
name: ecommerce-patent-title-abstract-translation
description: "Retrieve translated patent titles and abstracts from the Zhihuiya (PatSnap) patent database. Triggered when users request patent abstract translation, patent title translation, translated patent abstracts, patent content in other languages, patent abstracts in Chinese/English/Japanese, or need to look up abstracts and titles of specific patents by patent ID or publication number, patent abstract translation, patent title translation, PatSnap, patent translation, or abstract lookup. Also triggered when users mention Zhihuiya, PatSnap, or patent abstract queries, even if \"translation\" is not explicitly mentioned."
---

# Zhihuiya Patent Abstract (Translated)

This skill guides you on how to retrieve translated patent titles and abstracts from the Zhihuiya (PatSnap) patent database, supporting Chinese, English, and Japanese translations.

## Core Concepts

Zhihuiya (PatSnap) is a leading patent intelligence platform. This tool queries its database to return translated titles and abstracts for a single patent per request. You can look up patents by **patent ID** or **publication (announcement) number**, and receive translations in Chinese, English, or Japanese.

**Patent identification**: Each patent can be identified by either a `patentId` (internal Zhihuiya identifier) or a `patentNumber` (public publication/announcement number such as `US20200012345A1` or `CN112345678A`). If both are provided, the patent ID takes priority.

**Family patent fallback**: When the original patent has no abstract available, you can optionally substitute the abstract from a related family patent by enabling the replacement option.

## Parameter Guide

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | At least one of patentId or patentNumber | Zhihuiya internal patent ID. Single patent ID only. Do NOT pass comma-separated multiple IDs. Max length 60,000 characters. |
| patentNumber | string | At least one of patentId or patentNumber | Publication (announcement) number. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. Max length 60,000 characters. |
| replaceByRelated | integer | No | Whether to substitute a family patent abstract when the original is unavailable. `1` = yes, `0` = no. Default `0`. |
| lang | string | No | Target translation language. `en` = English (default), `cn` = Chinese, `jp` = Japanese. |

### Key Rules

1. **At least one identifier is required**: You must provide either `patentId` or `patentNumber` (or both). If both are supplied, `patentId` takes priority.
2. **Single patent per request**: Only one patent may be passed per request. If the user has multiple patents, obtain explicit consent and make a separate call for each.
3. **Default language is English**: When the user does not specify a language, use `en`.
4. **Family fallback**: Set `replaceByRelated` to `1` only when the user explicitly wants a substitute abstract from a family patent if the original is missing.

> **Single Patent Limit**: This endpoint consumes many credits. If you need to check multiple patents, you must obtain explicit user consent and make separate requests. Each call can only pass one patent (`patentId` and `patentNumber` cannot be comma-separated into multiple values).

## Response Fields

| Field | Description |
|-------|-------------|
| total | Number of patent records returned |
| data | Array of patent objects (see below) |
| data[].patentId | Zhihuiya internal patent ID |
| data[].pn | Publication (announcement) number |
| data[].title | Translated patent title |
| data[].abstractText | Translated patent abstract |
| data[].pnRelated | Publication number of the substitute family patent (only present when family replacement was used) |
| costToken | Tokens consumed by this request |

## Usage Examples

**1. Translate a single patent abstract to English by publication number**
```
Look up patent number US20200012345A1 and give me the English abstract.
```
Parameters: `patentNumber = "US20200012345A1"`, `lang = "en"`

**2. Look up by patent ID with family fallback**
```
Get the Japanese abstract for patent ID 12345678. If the abstract is unavailable, use a family patent instead.
```
Parameters: `patentId = "12345678"`, `lang = "jp"`, `replaceByRelated = 1`

## Display Rules

1. **Present data clearly**: Show results in a well-structured table with patent number, title, and abstract.
2. **Indicate language**: Mention the translation language in the output header so users know which language the results are in.
3. **Family patent notice**: If `pnRelated` is present in any result, explicitly inform the user that the abstract was sourced from a family patent and show the substitute publication number.
4. **Long abstracts**: For very long abstracts, display the full text without truncation so users can review the complete content.
5. **Error handling**: When a query fails or returns no results, explain the likely cause (e.g., invalid patent number, patent not found in database) and suggest corrections.
6. **No subjective commentary**: Present the translated text as-is without adding interpretation or legal analysis of the patent content.

## Invocation

- **API Endpoint**: `POST /zhihuiya/abstractDataTranslated` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_title_abstract_translation.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search. **Single Patent Limit**: This endpoint consumes many credits. Each call can only pass one patent; if you need to check multiple patents, you must obtain explicit user consent and make separate requests.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-abstract-data-translated-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Important Limitations

- **Identifier required**: At least one of patent ID or publication number must be provided; the tool cannot perform keyword-based searches.
- **Translation languages**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **No full-text retrieval**: This tool returns only titles and abstracts, not full patent claims or descriptions.
- **Family replacement is optional**: The substitute family patent abstract is only provided when explicitly requested via `replaceByRelated = 1`.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent abstract and title translation queries:

| User Says | Scenario |
|-----------|----------|
| "Translate this patent abstract" | Single patent translation |
| "What does patent XX say / what is it about" | Abstract lookup |
| "Get the Chinese/Japanese version of this patent" | Specific language translation |
| "Look up the abstract for patent number XX" | Publication number lookup |
| "The abstract is missing, try a family patent" | Family patent fallback |

**Not applicable** -- Needs beyond abstract translation:

- Full patent text, claims, or description retrieval
- Patent search by keyword, classification, or applicant
- Patent legal status, citation analysis, or landscape reports
- Patent valuation or infringement analysis
