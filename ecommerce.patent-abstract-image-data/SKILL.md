---
name: ecommerce.patent-abstract-image-data
description: Retrieves patent abstract images (drawings) from the Zhihuiya (PatSnap) patent database by patent ID or publication number. Trigger when the user mentions patent abstract drawings, patent diagrams, patent figures, patent images, abstract drawing retrieval, patent image lookup, patent abstract images, patent drawings, patent illustrations, PatSnap, abstract image lookup. Also trigger when the user needs to view the drawings or figures in patent documents, even without explicitly mentioning PatSnap.
---

# Zhihuiya Patent Abstract Image

This skill guides you on how to retrieve abstract images (drawings) from the Zhihuiya patent database, helping users quickly obtain the illustrative figures associated with specific patents.

## Core Concepts

Abstract images (abstract drawings) are the representative figures attached to a patent document's abstract section. They provide a quick visual overview of the invention. This tool queries the Zhihuiya patent database and returns download paths for these images.

**Lookup logic**: You must provide at least one of two identifiers -- a patent ID or a publication number. If both are provided, patent ID takes priority. Only one patent may be passed per request; do not pass comma-separated multiple patents.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | Conditionally (one of the two must be provided) | Internal patent identifier; single patent ID only. Do NOT pass comma-separated multiple IDs | 5e6f7a8b9c |
| Publication Number | patentNumber | Conditionally (one of the two must be provided) | Patent publication/announcement number; single number only. Do NOT pass comma-separated multiple numbers | CN115059423A |

- At least one of `patentId` or `patentNumber` must be supplied.
- If both are supplied, `patentId` takes precedence.
- Only one patent may be passed per request. If the user has multiple patents, obtain explicit consent and make a separate call for each.

> **Single-patent limit**: This endpoint consumes significant credits. To query multiple patents, obtain explicit user consent and make separate calls for each. Only 1 patent per call (`patentId` and `patentNumber` do not accept comma-separated multiple values).

## Response Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Patent ID | patentId | The internal patent identifier |
| Publication Number | pn | The publication/announcement number |
| Abstract Drawing Path | abstractDrawingPath | URL path to the abstract image file |
| Total | total | Total number of records returned |
| Cost Token | costToken | Tokens consumed by the query |

## Calling the Tool

- **API Endpoint**: `/zhihuiya/abstractImage` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/patent_abstract_image_data.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.patent-abstract-image-data-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
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
## Usage Examples

**1. Single patent lookup by publication number**
```
Retrieve the abstract image for patent CN115059423A.
```

**3. Lookup by patent ID**
```
Fetch the abstract image for patent ID 5e6f7a8b9c.
```

## Display Rules

1. **Show the image**: When the response includes an `abstractDrawingPath`, display the image directly using Markdown image syntax so the user can see the drawing inline.
2. **Patent identification**: Always show the publication number (`pn`) alongside each image so the user knows which patent each drawing belongs to.
3. **Missing images**: If a patent has no abstract drawing (empty `abstractDrawingPath`), explicitly inform the user that no abstract image is available for that patent.
4. **Single-patent results**: Each call returns data for a single patent; present that patent's image and metadata clearly.
5. **Error handling**: When a query fails, explain the reason based on the response and suggest the user verify their patent IDs or publication numbers.
6. **No subjective analysis**: Present the retrieved images and metadata without adding subjective patent analysis or legal interpretations.
## User Expression & Scenario Quick Reference

**Applicable** -- Patent abstract image retrieval:

| User Says | Scenario |
|-----------|----------|
| "Show me the abstract image for patent XX" | Single patent image lookup |
| "What does the patent figure look like" | Abstract drawing retrieval |
| "Retrieve patent illustrations for XX" | Image download path retrieval |
| "I need the abstract drawing for publication number XX" | Lookup by publication number |

**Not applicable** -- Needs beyond abstract image retrieval:
- Full patent text or claims analysis
- Patent search by keyword or classification
- Patent legal status or family information
- Patent citation or prior art analysis
- Patent valuation or infringement analysis
