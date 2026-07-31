---
name: ecommerce.ruiguan-detection-patent-design
description: Detect design patent infringement risks by comparing a product image against a global design patent database across 25+ jurisdictions. Triggered when users mention design patent detection, patent infringement check, patent risk analysis, TRO case lookup, design patent search, product design patent screen, or visual patent similarity. Even if the user does not explicitly say "design patent," this skill should be triggered whenever the need involves checking whether a product image may infringe existing design patents.
---

# Design Patent Detection

This skill guides you on how to perform design patent infringement detection, helping e-commerce sellers and IP professionals identify potential design patent risks before listing products.

## Core Concepts

Design patent detection compares a product image against a global design patent database using visual similarity algorithms. The system returns patents ranked by similarity score, along with TRO (Temporary Restraining Order) litigation history, helping users assess infringement risk.

**Similarity score**: A value between 0 and 1. Higher values indicate greater visual resemblance to the patent drawing. Patents with `similarity >= 0.7` or those flagged with TRO enforcement history deserve special attention and should be reviewed carefully.

**Radar analysis**: When radar is enabled, each patent result includes a `radarResult` with a `same` flag (suspected infringement: true/false) and an `exp` field (explanation). This provides an AI-powered judgment beyond raw similarity.

**LOC classification**: The Locarno Classification (LOC) is an international system for categorizing industrial designs. You can optionally specify LOC codes to narrow the search scope, or leave it unset to let the model predict the appropriate categories automatically.

## Parameters Guide

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| imageUrl | Yes | - | Product image URL to check against the patent database |
| queryMode | Yes | hybrid | Search mode: `physical` (real product photo), `line` (line drawing), `hybrid` (combined) |
| topNumber | Yes | 100 | Number of patent results to return (max 100) |
| regions | No | US | Country/region codes, comma-separated for multiple (e.g., `US,EU,CN`) |
| productTitle | No | - | Product title for supplementary context |
| productDescription | No | - | Product description for supplementary context |
| patentStatus | No | 1 | Patent validity: `1` (active), `0` (expired), `1,0` (both) |
| enableRadar | No | true | Enable AI radar analysis for suspected infringement judgment |
| topLoc | No | - | LOC level-1 codes to restrict search scope (e.g., `06,07`). Omit to use auto-prediction |
| sourceLanguage | No | - | Source language code for translation (e.g., `zh-CN`). Leave empty if text is already in English |

### Supported Regions

US (United States), EU (European Union), CN (China), JP (Japan), KR (South Korea), DE (Germany), GB (United Kingdom), FR (France), IT (Italy), AU (Australia), CA (Canada), BR (Brazil), MX (Mexico), IN (India), TH (Thailand), SE (Sweden), CH (Switzerland), IE (Ireland), IL (Israel), DK (Denmark), NZ (New Zealand), AT (Austria), BX (Bolivia), FI (Finland), WO (WIPO)

Default region is **US**. Use US when the user does not specify a region.

### LOC Level-1 Categories

| Code | Category |
|------|----------|
| 01 | Food |
| 02 | Clothing, haberdashery and sewing accessories |
| 03 | Travel goods, cases, parasols and personal items |
| 04 | Brushes |
| 05 | Textiles, artificial and natural sheet material |
| 06 | Furniture and household goods |
| 07 | Household items |
| 08 | Tools and hardware |
| 09 | Packages and containers for transport or handling of goods |
| 10 | Clocks, watches, measuring/checking/signaling instruments |
| 11 | Ornamental articles |
| 12 | Means of transport or hoisting |
| 13 | Equipment for production, distribution or transformation of electricity |
| 14 | Recording, telecommunication or data processing equipment |
| 15 | Machines |
| 16 | Photographic, cinematographic and optical apparatus |
| 17 | Musical instruments |
| 18 | Printing and office machinery |
| 19 | Stationery, office equipment, art materials, teaching materials |
| 20 | Sales and advertising equipment, signs |
| 21 | Games, toys, tents and sports goods |
| 22 | Arms, pyrotechnic articles, hunting/fishing/pest-killing articles |
| 23 | Fluid distribution, sanitary, heating, ventilation, air-conditioning equipment, solid fuel |
| 24 | Medical and laboratory equipment |
| 25 | Building units and construction elements |
| 26 | Lighting apparatus |
| 27 | Tobacco and smoking supplies |
| 28 | Pharmaceutical/cosmetic products, toilet articles and apparatus |
| 29 | Devices and equipment against fire, for accident prevention and rescue |
| 30 | Articles for care and handling of animals |
| 31 | Machines and apparatus for preparing food or drink |
| 32 | Graphic symbols, logos, surface patterns, ornamentation, interior/exterior arrangements |
| ALL | All categories |

## Usage

- **API Endpoint**: `POST /ruiguan/detectionPatentDesign` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/ruiguan_detection_patent_design.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic patent check for a product image (US market)**
```json
{
  "imageUrl": "https://example.com/product.jpg",
  "queryMode": "hybrid",
  "topNumber": 50,
  "regions": "US"
}
```

**2. Multi-region check with product context**
```json
{
  "imageUrl": "https://example.com/product.jpg",
  "queryMode": "physical",
  "topNumber": 100,
  "regions": "US,EU,CN",
  "productTitle": "Portable Wireless Charger Stand",
  "productDescription": "A foldable wireless charging stand for smartphones",
  "enableRadar": true
}
```

**3. Narrowed search using LOC classification (furniture)**
```json
{
  "imageUrl": "https://example.com/chair.jpg",
  "queryMode": "hybrid",
  "topNumber": 80,
  "regions": "US,DE",
  "topLoc": "06",
  "patentStatus": "1"
}
```

**4. Line drawing mode for sketch-based search**
```json
{
  "imageUrl": "https://example.com/sketch.png",
  "queryMode": "line",
  "topNumber": 50,
  "regions": "CN,JP,KR"
}
```

**5. Check both active and expired patents**
```json
{
  "imageUrl": "https://example.com/product.jpg",
  "queryMode": "hybrid",
  "topNumber": 100,
  "regions": "US",
  "patentStatus": "1,0"
}
```

## Display Rules

1. **High-risk patent highlighting**: When generating summaries or reports, display ALL patents with `similarity >= 0.7` or `troCase = true` in full detail. For each such patent, include: application number, patent title, inventors, TRO enforcement history, the most-similar patent drawing, every image in the patent image list, patent abstract, patent specification, LOC info, radar analysis result, and specification text. Do NOT abbreviate or omit these fields.
2. **Disclaimer**: Always append: "This detection result is generated by Nexscope. It is recommended to consult a professional IP attorney for legal advice."
3. **Similarity interpretation**: Clearly explain that higher similarity scores indicate greater visual resemblance and higher infringement risk.
4. **Radar result display**: When `radarResult.same` is true, prominently flag the patent as a suspected infringement match and display the `exp` explanation.
5. **TRO warning**: Patents with `troCase = true` or `troHolder = true` should be highlighted with a warning, as they indicate the patent holder has a history of active enforcement via Temporary Restraining Orders.
6. **Image display**: Show both `patentImageUrl` (the most similar patent drawing) and the full `images` list so users can visually compare their product against all patent drawings.
7. **Error handling**: When a request fails, explain the issue and suggest corrective actions (e.g., check image URL accessibility, verify region codes).
8. **Present data faithfully**: Show query results as-is without adding subjective legal conclusions beyond the tool's own analysis.

## User Expression & Scenario Quick Reference

**Applicable** -- Design patent risk assessment:

| User Says | Scenario |
|-----------|----------|
| "Check if this product infringes any design patents" | Basic patent detection |
| "Patent risk check for this image" | Image-based patent search |
| "Does this product have TRO risk" | TRO enforcement history lookup |
| "Design patent search for US and EU" | Multi-region patent detection |
| "Check appearance patent for this product" | Category-specific patent search |
| "Is this product design safe to sell" | Pre-listing patent clearance |
| "Find similar design patents" | Similarity-based patent discovery |
| "Patent infringement analysis" | Comprehensive patent risk report |

**Not applicable** -- Needs beyond design patent detection:
- Utility patent or invention patent searches
- Trademark infringement checks
- Copyright/DMCA issues
- Legal case management or litigation strategy
- Patent application or filing assistance

**Boundary judgment**: When users mention "patent check" or "IP risk," if the concern is about product appearance/design similarity to existing patents, this skill applies. If they are asking about utility patents, trademarks, copyrights, or need actual legal counsel, this skill does not apply.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
