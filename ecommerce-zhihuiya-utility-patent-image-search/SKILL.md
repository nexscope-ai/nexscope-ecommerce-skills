---
name: ecommerce-zhihuiya-utility-patent-image-search
description: "Perform visual similarity search for utility model patents using an image URL, with filtering by country, legal status, date ranges, and assignee. Supports utility model patents only (type U) with shape-only or shape+pattern+color matching models. Triggered when users mention utility patent image search, utility model patent search, utility patent infringement check, product structure patent search, or utility model visual search. Even if the user does not explicitly mention \"utility patent,\" this skill should be triggered whenever the need involves searching for similar utility model patents through an image. For design patents, use ecommerce-zhihuiya-patent-image-search instead."
---

# Utility Patent Image Search

This skill guides you on how to perform patent image similarity search via the patent database for utility model patents only (type U). Given a single image URL, it finds visually similar patents in the utility model patent database, supporting multiple search models and extensive filtering options.

This skill supports **utility model patents only**. For design patents, use `ecommerce-zhihuiya-patent-image-search`.

## Core Concepts

**Patent Image Search** uses visual AI models to compare a given product or design image against a global patent image database. It returns a ranked list of similar patents, enabling users to evaluate infringement risks or conduct prior-art research.

**Patent type** for this skill:
| Type | Code | Description |
|------|------|-------------|
| Utility Model Patent | `U` | Protects the functional shape/structure of a product |

**Search models** for utility model patents:
| Model ID | Strategy | Recommendation |
|----------|----------|----------------|
| 3 | Match Shape | Shape-only comparison |
| 4 | Match Shape/Pattern/Color | Recommended for utility model patents (default) |

**Scoring logic**: A higher `score` value means greater visual similarity. When presenting results, sort by score in descending order (highest similarity first) so users can prioritize the most relevant patents for review.

## Parameter Guide

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| url | The image URL to search against | `https://example.com/product.jpg` |
| patentType | Patent type, fixed to `U` (utility model) by this skill | `U` |
| model | Search model ID: `3` (shape only) or `4` (recommended) | `4` |

### Common Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| country | Patent authority country codes, comma-separated (e.g., `CN,US,JP`) | All countries |
| legalStatus | Legal status codes, comma-separated | None |
| simpleLegalStatus | Simple legal status: `0` (expired), `1` (active), `2` (pending) | None |
| assignees | Applicant / patent holder name | None |
| applyStartTime | Application start date (`yyyyMMdd`) | None |
| applyEndTime | Application end date (`yyyyMMdd`) | None |
| publicStartTime | Publication start date (`yyyyMMdd`) | None |
| publicEndTime | Publication end date (`yyyyMMdd`) | None |
| limit | Number of results to return (1-100) | 10 |
| offset | Pagination offset (0-1000) | 0 |
| field | Sort field: `SCORE`, `APD`, `PBD`, `ISD` | `SCORE` |
| order | Sort order: `desc` or `asc` (for APD/PBD/ISD) | `desc` |
| lang | Title language preference: `original`, `cn`, `en` | `original` |
| preFilter | Enable country pre-filtering: `1` (on) / `0` (off) | `1` |
| stemming | Enable stemming: `1` (on) / `0` (off) | `0` |
| mainField | Search within title, abstract, claims, description, publication number, application number, applicant, inventor, IPC/UPC/LOC | None |
| includeMachineTranslation | Include machine-translated content in search | None |
| scoreExpansion | Enable score expansion | None |
| isHttps | Return HTTPS image URLs: `1` (yes) / `0` (no) | `0` |
| returnImgId | Return image IDs in results | `false` |

> Note: The `loc` (Locarno classification) parameter applies to design patents only and is not relevant for utility model searches.

### Commonly Used Country Codes

| Code | Country/Region |
|------|---------------|
| CN | China |
| US | United States |
| JP | Japan |
| KR | South Korea |
| EP | European Patent Office |
| WO | WIPO |
| DE | Germany |
| GB | United Kingdom |
| FR | France |
| AU | Australia |

## Usage

- **API Endpoint**: `POST /zhihuiya/patentImageSearch` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/zhihuiya_utility_patent_image_search.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic utility model patent search (recommended starting point)**
Search for utility model patents similar to a product image, matching shape/pattern/color across all countries:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "limit": 20
}
```

**2. Utility model patent search limited to specific countries**
Search only in China and the United States:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "country": "CN,US",
  "limit": 20
}
```

**3. Shape-only utility model patent search**
Compare by shape only (ignore pattern/color):
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 3,
  "country": "CN",
  "limit": 20
}
```

**4. Search only active patents within a date range**
Find active utility model patents filed after 2020:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "simpleLegalStatus": "1",
  "applyStartTime": "20200101",
  "limit": 30
}
```

**5. Search by specific assignee**
Find patents held by a particular company:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "assignees": "Apple Inc.",
  "limit": 20
}
```

**6. Get results with Chinese-translated titles**
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "U",
  "model": 4,
  "lang": "cn",
  "limit": 20
}
```

## Display Rules

1. **Sort by score**: Always sort results by `score` in descending order (highest similarity first) to help users quickly identify the most relevant infringement risks.

2. **Show complete details**: When summarizing results or generating reports, include ALL of the following for each patent -- do NOT omit or abbreviate:
   - Application number (`apno`)
   - Patent title in Chinese (use `lang: cn` or provide translation)
   - Inventor (`inventor`)
   - Patent drawing (the matched `url` image)
   - **Every** patent image in the image list
   - Patent abstract
   - Patent description
   - IPC/UPC classification information
   - Radar result (`radarResult`) if available
   - Patent specification

3. **Legal disclaimer**: Always append: "This search result was generated by Nexscope. It is recommended to consult a professional patent attorney for legal advice."

4. **Score explanation**: Remind users that the score represents visual similarity -- a higher score indicates a closer match, but does not constitute a legal determination of infringement.

5. **Pagination guidance**: When the total count exceeds the returned results, inform users about the total number of matching patents and guide them to use `offset` and `limit` for additional pages.

6. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., verify the image URL is publicly accessible, check country codes, adjust date formats).

## User Expression & Scenario Quick Reference

**Applicable** -- Image-based utility model patent similarity searches:

| User Says | Scenario |
|-----------|----------|
| "Check if my product structure infringes any utility patents" | Utility model patent infringement check |
| "Search for similar utility model patents" | Utility model patent similarity search |
| "Find utility patents that look like this image" | Visual utility model patent lookup |
| "Are there any utility patents similar to my product structure" | Utility model risk assessment |
| "Utility model patent search by image" | Utility model search |
| "Check utility patent risks for this product in China and US" | Multi-country utility patent check |
| "Find active utility model patents" | Filtered utility patent search |
| "Who holds utility patents similar to this design" | Competitor patent discovery |

**Not applicable** -- Needs beyond utility model patent image search:
- Text-based patent search (keyword/abstract/claim search)
- Design patent image search (use ecommerce-zhihuiya-patent-image-search)
- Patent legal status monitoring or annuity management
- Patent valuation or licensing negotiation
- Freedom-to-operate (FTO) legal opinions
- Patent family or citation analysis

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
