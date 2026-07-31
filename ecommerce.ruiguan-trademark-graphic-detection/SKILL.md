---
name: ecommerce.ruiguan-trademark-graphic-detection
description: Detect graphic trademarks in product images by comparing against registered trademark databases across 15 major trademark offices using YOLO-based object detection and visual similarity. Triggered when users mention graphic trademark detection, logo infringement check, trademark similarity analysis, image trademark risk assessment, product image trademark screening, or logo detection. Even if the user does not explicitly say "trademark detection," this skill should be triggered whenever the need involves comparing a product image against registered graphic trademarks or assessing trademark infringement risk.
---

# Graphic Trademark Detection

This skill guides you on how to detect graphic trademarks in product images, helping e-commerce sellers and brand owners identify potential trademark infringement risks before listing products.

## Core Concepts

Graphic trademark detection analyzes a product image to find visually similar registered trademarks across multiple countries and regions. The tool uses YOLO-based object detection to locate logo-like regions in the image, then compares them against trademark databases worldwide.

**Similarity score**: A higher `similarity` value means the detected graphic is more visually similar to the registered trademark. Values closer to 1.0 indicate near-identical matches and higher infringement risk.

**Trademark status meanings**:
| Status | Meaning |
|--------|---------|
| registered | Trademark is actively registered |
| act | Trademark is active |
| pend | Trademark application is pending |
| filed | Trademark application has been filed |
| ended | Trademark has expired |
| DEL | Trademark has been deleted/cancelled |

## Parameter Guide

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| imageUrl | Yes | Product image URL or base64-encoded image data | - |
| topNumber | Yes | Maximum number of detection results to return (1-100) | 5 |
| productTitle | No | Product title, helps improve detection accuracy | - |
| trademarkName | No | Suspected logo name, helps narrow down results | - |
| regions | No | Country/region codes to check, comma-separated. If omitted, all countries are searched | All |
| enableLocalizing | No | Whether to enable image cropping for detected regions | false |
| enableRadar | No | Whether to enable radar monitoring | true |

### Supported Regions

US (United States), WO (WIPO), ES (Spain), GB (United Kingdom), DE (Germany), IT (Italy), CA (Canada), MX (Mexico), EM (European Union), AU (Australia), FR (France), JP (Japan), TR (Turkey), BX (Benelux), CN (China)

When the user does not specify a region, omit the `regions` parameter so all countries are searched by default.

## Usage Examples

**1. Basic image trademark check**
Detect trademarks in a product image across all regions, returning up to 10 results:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 10
```

**2. Region-specific trademark check**
Check a product image against US and EU trademark databases only:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 5
regions: "US,EM"
```

**3. Detailed check with product context**
Provide product title and suspected logo name for more accurate detection:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 10
productTitle: "Wireless Bluetooth Headphones with Noise Cancellation"
trademarkName: "SonicWave"
regions: "US,GB,DE"
```

**4. Full detection with image cropping**
Enable localizing to get cropped images of detected logo regions:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 20
enableLocalizing: true
regions: "US"
```

## Usage

- **API Endpoint**: `POST /ruiguan/trademarkGraphicDetection` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/ruiguan_trademark_graphic_detection.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Display Rules

1. **Present results clearly**: Show detection results in a well-structured table including trademark image, similarity score, trademark name, status, registration office, Nice classification, applicant name, and key dates
2. **Highlight high-risk matches**: When similarity is above 0.8, explicitly warn the user about high infringement risk
3. **Explain trademark status**: When showing results, clarify what each trademark status means for the user's risk assessment
4. **Radar results**: If `radarResult` is present in the response, display it prominently as it contains aggregated risk assessment
5. **Sub-radar results**: If individual items contain `subRadarResult`, include this information alongside each match
6. **Region context**: Always indicate which regions were searched so the user understands the scope of the check
7. **Error handling**: When a detection fails, explain the reason based on the response and suggest adjustments (e.g., using a clearer image, specifying regions, adjusting topNumber)

## Important Limitations

- **Image requirement**: The `imageUrl` parameter is mandatory; the tool cannot perform detection without an image
- **Result cap**: The `topNumber` parameter caps at 100 results per request
- **Image quality**: Detection accuracy depends on image resolution and clarity; higher quality images yield better results
- **Region coverage**: Not all countries are covered; the supported list includes 15 major trademark offices

## User Expression & Scenario Quick Reference

**Applicable** -- Graphic trademark detection tasks:

| User Says | Scenario |
|-----------|----------|
| "Check if this image has trademark issues" | Basic trademark detection |
| "Is this logo registered anywhere" | Multi-region trademark search |
| "Trademark risk for my product image" | Product listing risk assessment |
| "Find similar trademarks to this graphic" | Similarity search |
| "Check this image against US trademarks" | Region-specific detection |
| "Does this design infringe any trademark" | Infringement risk check |
| "Scan my product photo for logos" | Logo detection in product images |

**Not applicable** -- Needs beyond graphic trademark detection:
- Text/word trademark search (no image involved)
- Trademark registration or filing
- Patent or copyright checks
- Legal advice on trademark disputes

**Boundary judgment**: When users say "check my product" or "is this safe to sell," if the concern relates to graphic elements or logos in product images potentially infringing registered trademarks, this skill applies. If they are asking about text trademarks, patent issues, or general legal compliance, it does not apply.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
