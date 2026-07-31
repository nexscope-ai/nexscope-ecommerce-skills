---
name: ecommerce.patent-fulltext-images
description: Retrieve fulltext images (drawings, diagrams, charts) from patent documents by patent ID or publication number. Triggered when users ask about patent images, patent drawings, patent diagrams, patent illustrations, fulltext drawings, patent charts, patent technical drawings, or want to view/download embedded images in patent documents, patent fulltext drawings, patent diagrams, technical drawings, patent images, or PatSnap. Even if the user does not explicitly mention "fulltext drawings," this skill should be triggered whenever their need involves obtaining visual content (drawings, diagrams, charts) from specific patents.
---

# Zhihuiya Patent Fulltext Image

This skill guides you on how to retrieve fulltext images (drawings, figures, diagrams) from patent documents using the Zhihuiya patent data service, helping users access and analyze visual content within patents.

## Core Concepts

Patent fulltext images are the figures, drawings, and diagrams embedded in patent documents. They are essential for understanding the technical details of an invention. This tool queries the Zhihuiya patent database and returns image metadata including download paths and image types for a given patent.

**Lookup methods**: You can look up images by either **patent ID** (an internal identifier) or **publication number** (the publicly visible patent number such as US20230012345A1 or CN115000000A). At least one of these must be provided.

## Parameter Guide

| Parameter | API Name | Required | Description | Example |
|-----------|----------|----------|-------------|---------|
| Patent ID | patentId | No* | Internal patent identifier | 8a7b6c5d-... |
| Publication Number | patentNumber | No* | Public patent publication/grant number | US20230012345A1 |
| Limit | limit | No | Maximum number of images to return (max 100, default 100) | 50 |
| Offset | offset | No | Pagination offset for image results | 0 |

> *At least one of patentId or patentNumber must be provided.

## Response Fields

| Field | Description |
|-------|-------------|
| total | Total number of image records available |
| data | Array of image entries |
| data[].patentId | Patent identifier |
| data[].pn | Publication/grant number |
| data[].fulltextImagePath | URL path to download the image |
| data[].imageType | Type/category of the image |
| columns | Column rendering metadata |
| costToken | Token cost of the request |
| type | Rendering style hint |

## Invocation

- **API Endpoint**: POST /zhihuiya/fulltextImage (full parameters/response/error codes in 
eferences/api.md)
- **Python Script**: python scripts/patent_fulltext_images.py '<JSON params>' [--inline]
- **Cost Constraints**: This tool consumes credits. The same parameter combination defaults to a single call per session. The script includes a 24-hour local cache. Do not automatically retry with different keywords, pagination, or modified parameters on failure or empty results; inform the user that additional costs will be incurred before continuing to search.

**Output Strategy (default script behavior)**:
- **Always** write the full response to <cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-zhihuiya-fulltext-image-<timestamp>.json (<cwd> is the working directory at script execution time, which in Claude Code is the current project directory; <session> is taken from the SESSION_ID environment variable, auto-grouped by user task; **writing to /tmp is forbidden** -- error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: print only a summary to stdout after writing to disk (top-level fields, common counts like 	otal/costToken, length of the largest list field + first 3 samples)
- Add --inline to force full output to stdout (still writes to disk)

**Data Reading Tip**: Check the summary first to determine if it is sufficient; when specific fields are needed, prefer using jq or ConvertFrom-Json to extract from the saved JSON file on demand to avoid loading the entire JSON into context.

## Authentication

Set NEXSCOPE_API_KEY. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Get all images for a patent by publication number**
`
Retrieve fulltext images for patent US20230012345A1.
`
Parameters: {"patentNumber": "US20230012345A1"}

**2. Get images for a patent by patent ID**
`
Fetch the drawings for patent ID abc123def456.
`
Parameters: {"patentId": "abc123def456"}

**3. Paginated retrieval of images**
`
Get the first 20 images for patent CN115000000A.
`
Parameters: {"patentNumber": "CN115000000A", "limit": "20", "offset": "0"}

**4. Get the next page of images**
`
Get images 21-40 for patent CN115000000A.
`
Parameters: {"patentNumber": "CN115000000A", "limit": "20", "offset": "20"}

## Display Rules

1. **Present data clearly**: Show image results in a structured table with image type, download path, and patent number
2. **Image links**: Always present ulltextImagePath values as clickable links so users can view or download images directly
3. **Pagination notice**: When 	otal exceeds the number of returned results, inform the user that more images are available and offer to fetch the next page
4. **Error handling**: When a query fails, explain the reason and suggest verifying the patent ID or publication number
5. **No fabrication**: Never invent patent IDs, publication numbers, or image URLs -- only display data returned by the API
6. **Total count**: Always mention the total number of images available for the patent

## Important Limitations

- **Image limit**: Each request returns a maximum of 100 images
- **Identifier required**: At least one of patentId or patentNumber must be supplied
- **All parameters are strings**: Even numeric values like limit and offset must be passed as strings

## User Expression & Scenario Quick Reference

**Applicable** -- Requests involving patent visual content:

| User Says | Scenario |
|-----------|----------|
| "Show me the drawings for patent XX" | Fulltext image retrieval |
| "Get the figures from this patent" | Fulltext image retrieval |
| "Download patent images for XX" | Fulltext image retrieval |
| "What diagrams does patent XX contain" | Fulltext image listing |
| "How many figures are in patent XX" | Image count query |
| "Show me the technical drawings" | Fulltext image retrieval |

**Not applicable** -- Needs beyond patent fulltext images:
- Patent text/abstract/claims search
- Patent family or citation analysis
- Patent legal status queries
- Patent assignee or inventor search
- General image search unrelated to patents
