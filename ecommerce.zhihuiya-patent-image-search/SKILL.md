---
name: ecommerce.zhihuiya-patent-image-search
description: Perform visual similarity search for design patents using an image URL, with filtering by country, legal status, date ranges, Locarno classification, and assignee. Supports design patent types only (type D). Triggered when users mention patent image search, design patent search, search patent by image, visual patent lookup, patent similarity detection, patent image matching, or design patent infringement check. Even if the user does not explicitly mention "patent image," this skill should be triggered whenever the need involves searching for similar design patents through an image. For utility model patents, use ecommerce.zhihuiya-utility-patent-image-search instead.
---

# Patent Image Search (Design Patents)

This skill guides you on how to perform patent image similarity search via the patent database for design patents only (type D). Given a single image URL, it finds visually similar patents in the design patent database, supporting multiple search models and extensive filtering options.

This skill supports **design patents only**. For utility model patents, use `ecommerce.zhihuiya-utility-patent-image-search`.

## Core Concepts

**Patent Image Search** uses visual AI models to compare a given product or design image against a global patent image database. It returns a ranked list of similar patents, enabling users to evaluate infringement risks or conduct prior-art research.

**Patent type** for this skill:
| Type | Code | Description |
|------|------|-------------|
| Design Patent | `D` | Protects the ornamental appearance of a product |

**Search models** for design patents:
| Model ID | Strategy | Recommendation |
|----------|----------|----------------|
| 1 | Intelligent Association | Recommended for design patents (default) |
| 2 | Search This Image | Exact visual match |

**Scoring logic**: A higher `score` value means greater visual similarity. When presenting results, sort by score in descending order (highest similarity first) so users can prioritize the most relevant patents for review.

## Parameter Guide

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| url | The image URL to search against | `https://example.com/product.jpg` |
| patentType | Patent type, fixed to `D` (design) by this skill | `D` |
| model | Search model ID: `1` (recommended) or `2` | `1` |

### Common Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| country | Patent authority country codes, comma-separated (e.g., `CN,US,JP`) | All countries |
| loc | Locarno classification codes, connectable with AND/OR/NOT | None |
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
| preFilter | Enable country/LOC pre-filtering: `1` (on) / `0` (off) | `1` |
| stemming | Enable stemming: `1` (on) / `0` (off) | `0` |
| mainField | Search within title, abstract, claims, description, publication number, application number, applicant, inventor, IPC/UPC/LOC | None |
| includeMachineTranslation | Include machine-translated data in search | None |
| scoreExpansion | Enable score expansion | None |
| isHttps | Return HTTPS image URLs: `1` (yes) / `0` (no) | `0` |
| returnImgId | Return image IDs in results | `false` |

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
- **Python Script**: `python scripts/zhihuiya_patent_image_search.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic design patent search (recommended starting point)**
Search for design patents similar to a product image across all countries:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "limit": 20
}
```

**2. Design patent search limited to specific countries**
Search only in China and the United States:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "country": "CN,US",
  "limit": 20
}
```

**3. Search with Locarno classification filter**
Narrow results to a specific product category (e.g., LOC 07-01 for tableware):
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
  "loc": "07-01",
  "preFilter": 1,
  "limit": 20
}
```

**4. Search only active patents within a date range**
Find active design patents filed after 2020:
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
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
  "patentType": "D",
  "model": 1,
  "assignees": "Apple Inc.",
  "limit": 20
}
```

**6. Get results with Chinese-translated titles**
```json
{
  "url": "https://example.com/my-product.jpg",
  "patentType": "D",
  "model": 1,
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
   - LOC classification information (`loc`)
   - Radar result (`radarResult`) if available
   - Patent specification

3. **Legal disclaimer**: Always append: "This search result was generated by Nexscope. It is recommended to consult a professional patent attorney for legal advice."

4. **Score explanation**: Remind users that the score represents visual similarity -- a higher score indicates a closer match, but does not constitute a legal determination of infringement.

5. **Pagination guidance**: When the total count exceeds the returned results, inform users about the total number of matching patents and guide them to use `offset` and `limit` for additional pages.

6. **Error handling**: When a query fails, explain the reason and suggest adjustments (e.g., verify the image URL is publicly accessible, check country codes, adjust date formats).

## User Expression & Scenario Quick Reference

**Applicable** -- Image-based patent similarity searches:

| User Says | Scenario |
|-----------|----------|
| "Check if my product design infringes any patents" | Design patent infringement check |
| "Search for similar design patents" | Design patent similarity search |
| "Find patents that look like this image" | Visual patent lookup |
| "Are there any patents similar to my product appearance" | Appearance risk assessment |
| "Check patent risks for this product in China and US" | Multi-country patent check |
| "Find active design patents in this category" | Filtered patent search |
| "Who holds patents similar to this design" | Competitor patent discovery |

**Not applicable** -- Needs beyond patent image search:
- Text-based patent search (keyword/abstract/claim search)
- Utility model patent search (use ecommerce.zhihuiya-utility-patent-image-search)
- Patent legal status monitoring or annuity management
- Patent valuation or licensing negotiation
- Freedom-to-operate (FTO) legal opinions
- Patent family or citation analysis

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.
