---
name: ecommerce.ruiguan-gun-parts-search
description: Check product images against a database of policy-violating items using visual similarity matching. Triggered when users mention policy compliance check, product image compliance review, violation detection, prohibited product screening, image-based compliance audit, pre-listing risk screening, or product image risk check. Even if the user does not explicitly say "compliance," this skill should be triggered whenever the need involves comparing product images against a violation database.
---

# Policy Compliance Image Detection

This skill guides you on how to use the policy compliance detection tool to identify potential policy violations in product images. It performs image-based similarity search against a known database of prohibited products.

## Core Concepts

Policy Compliance Image Detection is an image-based compliance screening service. Given a product image URL, it searches for visually similar products in a database of known policy-violating items. The tool returns matching violations ranked by visual similarity.

**Similarity score (cosine)**: A value between 0 and 1. Higher values indicate stronger visual resemblance to known violating products. A score close to 1.0 means the product image is nearly identical to a flagged violation.

## Parameter Guide

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| Image URL | imageUrl | Yes | The URL of the product image to check (max 1000 chars) | https://example.com/product.jpg |

**Key notes:**
- The image URL must be publicly accessible
- Supported formats include common image types (JPG, PNG, etc.)
- The URL must not exceed 1000 characters

## Response Fields

| Field | API Name | Description |
|-------|----------|-------------|
| Total Matches | total | Number of matching violation records found |
| Violation List | data | Array of matched violating products |
| Violation Image | pdImgOssUrl | Image URL of the matched violating product |
| Similarity Score | cosine | Similarity between the input image and the violation (0~1) |
| Product Title (EN) | pdTitle | English title of the matched violating product |
| Product Title (CN) | pdTitleCHNCensored | Chinese title of the matched violating product |
| Detection ID | detectId | Unique identifier for this detection session |
| Token Cost | costToken | Number of tokens consumed by this request |

## Usage

- **API Endpoint**: `POST /ruiguan/gunPartsSearch` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/ruiguan_image_compliance_search.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic compliance check for a single product image**
```
Check this product image for policy compliance: https://example.com/images/product-123.jpg
```

**2. Batch checking multiple product images**
```
Please scan these product images for potential policy violations:
- https://example.com/images/item-a.jpg
- https://example.com/images/item-b.jpg
```

**3. Pre-listing compliance screening**
```
Before I list this product, can you check if the image triggers any policy flags?
Image: https://example.com/new-product.png
```

## Display Rules

1. **Show results in a clear table**: Present each matched violation with its image, similarity score, and product titles
2. **Highlight high-similarity matches**: When the cosine score exceeds 0.8, clearly flag the result as a strong match that likely requires attention
3. **Include violation images**: When results contain `pdImgOssUrl`, display the matched violation image so the user can visually compare
4. **Score interpretation**: Always explain what the similarity score means -- higher values indicate closer resemblance to known violations
5. **Error handling**: When a query fails, explain the issue and suggest checking whether the image URL is valid and publicly accessible
6. **No legal advice**: Present detection results factually without providing legal conclusions; remind users to verify with platform policies

## Important Limitations

- **Image-only detection**: This tool works exclusively with image URLs; it does not analyze text descriptions or product metadata
- **URL accessibility**: The image URL must be publicly reachable by the detection service
- **URL length cap**: Image URLs must not exceed 1000 characters
- **Similarity-based**: Results are based on visual similarity and do not constitute a definitive policy ruling

## User Expression & Scenario Quick Reference

**Applicable** -- Image-based product policy compliance checks:

| User Says | Scenario |
|-----------|----------|
| "Check if this product image has compliance risks" | Single image compliance check |
| "Scan my product images for policy violations" | Batch compliance screening |
| "Is this image flagged as a prohibited product" | Specific violation inquiry |
| "Pre-screen my listing images for policy risks" | Pre-listing compliance audit |
| "Find similar violations for this product image" | Similarity-based violation search |

**Not applicable** -- Needs beyond image-based policy compliance detection:
- Text-based product compliance analysis
- General product category classification
- Intellectual property / trademark infringement
- Patent or copyright detection (use other detection skills)

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
