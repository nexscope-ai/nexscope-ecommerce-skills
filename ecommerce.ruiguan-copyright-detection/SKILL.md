---
name: ecommerce.ruiguan-copyright-detection
description: Detect image copyright infringement risks by comparing against a database of registered copyrighted works with similarity scoring, TRO litigation history, and radar-based infringement assessment. Triggered when users mention copyright detection, image infringement check, copyright risk analysis, TRO risk, copyright similarity search, rights owner lookup, or copyright compliance verification. Even if the user does not explicitly say "copyright," this skill should be triggered whenever the need involves checking whether an image may infringe registered copyright works.
---

# Copyright Detection

This skill guides you on how to perform image copyright detection, helping e-commerce sellers and designers identify potential copyright infringement risks before using images.

## Core Concepts

Copyright detection works by comparing a given image against a database of registered copyrighted works. The system returns visually similar copyrighted images along with key risk indicators such as similarity score, rights owner information, TRO (Temporary Restraining Order) litigation history, and radar-based infringement assessment.

**Similarity**: A decimal string (e.g., `"0.85"`) representing how closely the input image matches a copyrighted work. Higher values indicate greater risk.

**Radar detection**: An additional layer of analysis that provides a binary infringement judgment (`1` = infringing, `0` = not infringing). When enabled, each result includes this secondary assessment.

**TRO history**: TRO (Temporary Restraining Order) is a legal mechanism commonly used in copyright enforcement. Results flagged with TRO history indicate the rights owner has previously pursued legal action, signaling elevated risk.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| imageUrl | string | Yes | - | URL of the image to check for copyright infringement (max 1000 characters) |
| topNumber | integer | No | 100 | Number of results to return (min: 10, max: 200) |
| enableRadar | boolean | No | true | Whether to enable radar-based infringement detection |

### Parameter Guidelines

1. **imageUrl**: Must be a publicly accessible image URL. Supports common image formats. The URL must not exceed 1000 characters.
2. **topNumber**: Controls how many matching copyrighted works are returned. Use a smaller number (e.g., 10-20) for quick checks; use the maximum (200) for thorough audits.
3. **enableRadar**: When set to `true`, each result includes a radar-based infringement judgment. Keep enabled for comprehensive analysis; disable only when a faster, similarity-only scan is sufficient.

## Usage

- **API Endpoint**: `POST /ruiguan/copyrightDetection` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/ruiguan_copyright_detection.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic Copyright Check for a Single Image**
User: "Check if this image has any copyright issues: https://example.com/my-image.jpg"
Action: Call with `imageUrl` set to the provided URL, using defaults for other parameters.

**2. Quick Scan with Fewer Results**
User: "Do a quick copyright scan on this product image, I just need the top matches: https://example.com/product.png"
Action: Call with `topNumber` set to 10 for faster results.

**3. Thorough Audit with Maximum Results**
User: "I need a full copyright audit on this design: https://example.com/design.jpg"
Action: Call with `topNumber` set to 200 for the most comprehensive scan.

**4. Similarity-Only Check (No Radar)**
User: "Just check the similarity of this image against copyrighted works, no need for detailed infringement analysis: https://example.com/photo.jpg"
Action: Call with `enableRadar` set to `false`.

**5. Batch Checking (Multiple Images)**
User: "Check these three images for copyright: url1, url2, url3"
Action: Call the API once for each image URL and consolidate results.

## Display Rules

1. **Present data clearly**: Show detection results in a well-structured table. Key columns to display include: similarity score, rights owner, copyright code, radar result, TRO history, and copyright source link.
2. **Highlight high-risk results**: When similarity is high (e.g., >= 0.80) or radar detection flags infringement, clearly mark these as high-risk entries.
3. **TRO warnings**: When `troCase` or `troHolder` is `true`, prominently warn the user about existing TRO litigation history associated with the rights owner.
4. **Image previews**: When `path` or `pathThumb` URLs are available, mention that thumbnail previews of the copyrighted works can be viewed at those URLs.
5. **Result count notice**: Inform the user of the `total` number of matches found. If many results are returned, show the most relevant (highest similarity) entries first.
6. **Error handling**: When a request fails, explain the reason and suggest checking that the image URL is publicly accessible and correctly formatted.
7. **No legal advice**: Present detection results factually. Do not provide legal conclusions — recommend the user consult legal counsel for definitive copyright assessments.

## Important Limitations

- **Image URL required**: The tool accepts image URLs only. The image must be publicly accessible.
- **URL length**: The image URL must not exceed 1000 characters.
- **Result cap**: A maximum of 200 results can be returned per query.
- **Detection scope**: Results are limited to the copyrighted works database maintained by the detection service.

## User Expression & Scenario Quick Reference

**Applicable** -- Image copyright risk assessment:

| User Says | Scenario |
|-----------|----------|
| "Check if this image has copyright issues" | Basic copyright detection |
| "Is this image safe to use" | Infringement risk check |
| "Find similar copyrighted images" | Copyright similarity search |
| "Does this image have TRO risk" | TRO litigation risk analysis |
| "Who owns the copyright for this image" | Rights owner lookup |
| "Copyright audit for product images" | Batch copyright compliance check |
| "Is this design original or copied" | Originality verification |

**Not applicable** -- Needs beyond image copyright detection:
- Trademark or patent searches
- Text or music copyright checks
- Image editing or modification
- Reverse image search for non-copyright purposes
- Legal advice or litigation strategy

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
