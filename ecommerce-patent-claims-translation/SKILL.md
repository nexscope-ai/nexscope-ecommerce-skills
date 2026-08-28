---
name: ecommerce-patent-claims-translation
description: "Retrieves translated patent claims from the Zhihuiya (PatSnap) patent database. Trigger when the user asks about patent claims, claims translation, viewing claims in specific languages (Chinese, English, or Japanese), querying patent claims by patent ID or publication number, analyzing claim text, claim translation, patent claim translation, PatSnap, patent translation. Also trigger when the user needs patent claim content in a specific language, even without explicitly mentioning translated claims."
---

# Zhihuiya Patent Claims (Translated)

This skill guides you on how to query translated patent claims from the Zhihuiya (PatSnap) patent database, enabling users to retrieve claim texts in Chinese, English, or Japanese for a single patent per request.

## Core Concepts

Patent claims define the legal scope of protection granted by a patent. This tool retrieves the **translated text** of patent claims, supporting three languages: Chinese (`cn`), English (`en`), and Japanese (`jp`). You can look up patents by their internal patent ID or by their publication (announcement) number.

**Family patent substitution**: When claims are unavailable for a specific patent, the tool can optionally substitute claims from a related family patent. This is controlled by the `replaceByRelated` parameter.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Patent ID | patentId | Internal patent identifier | 84a1b2c3-... |
| Publication Number | pn | Publication (announcement) number of the patent | CN112345678A |
| Related Publication Number | pnRelated | Publication number of the substitute family patent (only present when family substitution is used) | US20210012345A1 |
| Claims | claims | Translated patent claim text | 1. A method for... |

## Supported Languages

| Code | Language |
|------|----------|
| en | English (default) |
| cn | Chinese |
| jp | Japanese |

Default language is **en** (English). Use English when the user does not specify a language.

## Calling the Tool

- **API Endpoint**: `/zhihuiya/claimDataTranslated` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_claims_translation.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-patent-claims-translated-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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
## Parameter Guide

### Patent Identification

You must provide **at least one** of the following:

- **patentId** -- The internal patent ID. When both `patentId` and `patentNumber` are provided, `patentId` takes precedence. Single patent ID only. Do NOT pass comma-separated multiple IDs.
- **patentNumber** -- The publication or announcement number. Single publication/announcement number only. Do NOT pass comma-separated multiple numbers.

### Optional Parameters

- **lang** -- Target translation language: `en` (English, default), `cn` (Chinese), or `jp` (Japanese).
- **replaceByRelated** -- Whether to substitute claims from a family patent when the original claims are unavailable: `1` = yes, `0` = no (default).

> **Single-patent limit**: This endpoint consumes significant credits. To query multiple patents, obtain explicit user consent and make separate calls for each. Only 1 patent per call (`patentId` and `patentNumber` do not accept comma-separated multiple values).

## Usage Examples

**1. Get English claims for a single patent by publication number**
```
patentNumber: "CN112345678A"
lang: "en"
```

**3. Get Japanese claims with family patent fallback**
```
patentNumber: "JP2021123456A"
lang: "jp"
replaceByRelated: 1
```

**4. Query by patent ID**
```
patentId: "84a1b2c3-d4e5-6f78-9abc-def012345678"
lang: "en"
```

## Display Rules

1. **Present claims clearly**: Show the translated claim text with proper formatting. Results contain a single patent's data per call.
2. **Family substitution notice**: When `pnRelated` is present in the response, clearly inform the user that the claims were sourced from a related family patent and show the substitute publication number.
3. **Language notice**: State the language of the returned claims so the user knows which translation they are viewing.
4. **Large results**: When the response is large, summarize the count and show a few representative entries, reminding the user of the total.
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest checking the patent ID or publication number.
## Important Limitations

- **At least one identifier required**: Either `patentId` or `patentNumber` must be provided; otherwise the query will fail.
- **Single patent per request**: Only one patent ID or publication number may be passed per call (no comma-separated batches).
- **Language support**: Only Chinese (`cn`), English (`en`), and Japanese (`jp`) are supported.
- **Family substitution**: Substitute claims are only returned when `replaceByRelated` is set to `1` and the original claims are unavailable.

## User Expression & Scenario Quick Reference

**Applicable** -- Queries related to patent claim text and translation:

| User Says | Scenario |
|-----------|----------|
| "Show me the claims for patent XX" | Single patent claim lookup |
| "Translate claims to Chinese/Japanese" | Claim translation |
| "What does patent XX claim?" | Claim content retrieval |
| "Claims unavailable, try family patent" | Family patent substitution |
| "Patent rights scope of XX" | Claim text retrieval |

**Not applicable** -- Needs beyond patent claim translation:

- Patent search or discovery (finding patents by keyword)
- Patent citation or legal status analysis
- Patent abstract or description retrieval
- Patent portfolio analytics or statistics
