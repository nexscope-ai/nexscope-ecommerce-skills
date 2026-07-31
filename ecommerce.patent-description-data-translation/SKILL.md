---
name: ecommerce.patent-description-data-translation
description: Retrieve translated patent description (specification) text from Zhihuiya. Triggered when users request patent specification translation, patent full text in other languages, translated patent full text, or want to view patent specifications in Chinese, English, or Japanese, patent specification translation, patent description translation, PatSnap, or patent translation. Also triggered when users provide a patent ID or publication number and request specification/description content in another language, or mention "patent specification translation," "description translation," "translated full text," or similar intent.
---

# Zhihuiya Patent Description (Translated)

This skill guides you on how to retrieve translated patent description (specification) text via the Zhihuiya data service. It supports translation into Chinese, English, or Japanese, and can look up patents by patent ID or publication number.

## Core Concepts

A patent description (also called "specification") is the full technical text of a patent document. This tool fetches the **translated** version of that text from the Zhihuiya patent database, supporting three target languages: Chinese (`cn`), English (`en`), and Japanese (`jp`).

When a patent's description is unavailable, the tool can optionally substitute it with a description from a **patent family member** (a related patent filed in another jurisdiction covering the same invention).

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Patent ID. At least one of `patentId` or `patentNumber` must be provided. If both are given, `patentId` takes priority. Single patent ID only. Do NOT pass comma-separated multiple IDs. |
| patentNumber | string | Conditionally | Publication (announcement) number. At least one of `patentId` or `patentNumber` must be provided. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers. |
| lang | string | No | Target translation language. Supported values: `en` (English, default), `cn` (Chinese), `jp` (Japanese). |
| replaceByRelated | integer | No | Whether to substitute with a patent family member's description when the original is unavailable. `1` = yes, `0` = no (default). |

### Key Rules

1. **At least one identifier required**: Either `patentId` or `patentNumber` must be provided. If the user gives a publication number like "US10123456B2", use `patentNumber`. If they give a numeric patent ID, use `patentId`.
2. **Priority**: When both identifiers are supplied, `patentId` takes precedence.
3. **Single patent per request**: Only one patent may be passed per request. If the user has multiple patents, obtain explicit consent and make a separate call for each.
4. **Default language**: If the user does not specify a language, default to `en` (English).

> **Single Patent Limit**: This endpoint consumes many credits. If you need to check multiple patents, you must obtain explicit user consent and make separate requests. Each call can only pass one patent (`patentId` and `patentNumber` cannot be comma-separated into multiple values).

## Invocation

- **API Endpoint**: `POST /zhihuiya/descriptionDataTranslated` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_description_data_translation.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search. **Single Patent Limit**: This endpoint consumes many credits. Each call can only pass one patent; if you need to check multiple patents, you must obtain explicit user consent and make separate requests.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-description-data-translated-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## Usage Examples

**1. Get English translation of a patent description by publication number**
```
patentNumber: "US10123456B2"
lang: "en"
```

**2. Get Chinese translation of a patent description by patent ID**
```
patentId: "abc123def"
lang: "cn"
```

**3. Japanese translation of a specific patent**
```
patentNumber: "JP2021012345A"
lang: "jp"
```

## Display Rules

1. **Present the translated text clearly**: Show the patent description text directly. For long descriptions, present a summary or the first section and inform the user the full text is available.
2. **Identify substitutions**: When `pnRelated` is present in the response, clearly inform the user that the description was sourced from a family member patent and show the related publication number.
3. **Single patent results**: Results contain a single patent's data per call.
4. **Error handling**: When a query fails, explain the reason based on the response and suggest checking the patent ID or publication number for correctness.
5. **No fabrication**: Never invent or paraphrase patent text. Only display what the API returns.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent description/specification translation queries:

| User Says | Scenario |
|-----------|----------|
| "Translate this patent description to English" | Single patent translation |
| "I need the Chinese version of patent US10123456" | Specific language translation |
| "What does patent CN112345678A describe?" | Patent description lookup |
| "Show me the Japanese translation of this patent's full text" | Japanese translation |
| "The description is missing, can you try a family member?" | Family member fallback |

**Not applicable** -- Needs beyond patent description translation:
- Patent search or discovery (finding patents by keyword/topic)
- Patent claim analysis or claim chart generation
- Patent legal status or prosecution history
- Patent citation or reference analysis
- Patent portfolio analytics or statistics
