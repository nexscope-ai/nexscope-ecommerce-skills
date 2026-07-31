---
name: ecommerce.text-trademark-detector
description: Text trademark detection and infringement risk analysis for e-commerce product listings. Trigger when users mention trademark detection, trademark risk check, brand infringement screening, product title trademark scan, text trademark search, listing compliance check, intellectual property risk assessment, text trademark detection, trademark infringement, brand infringement screening, listing compliance, intellectual property risk, Ruiguan. Even if the user does not explicitly say "trademark", trigger this skill whenever their need involves checking whether product text (titles, descriptions, bullet points) contains potentially infringing trademarks.
---

# Ruiguan Text Trademark Detection

This skill guides you on how to perform text-based trademark detection against product titles and other product text, helping e-commerce sellers identify potential trademark infringement risks before publishing listings.

## Core Concepts

Text Trademark Detection scans product text (titles, descriptions, bullet points) against registered trademark databases across 15 countries/regions. It returns matched trademarks along with risk scores, registration details, and holder information so sellers can avoid intellectual property violations.

**Risk score logic**: The `highestModeScore` field ranges from 0 to 5 -- a higher value indicates greater infringement risk. The `textTrademarkRadar` field classifies overall product risk into three levels: 0 (low risk), 1 (needs manual review), 2 (high risk).

**Blacklist and whitelist**: The response may include `blacklistTrademarks` (known dangerous trademarks to always avoid) and `whitelistTrademarks` (safe trademarks that can be ignored). Always surface blacklist matches prominently to the user.

## Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| productTitle | string | Yes | Product title to scan (max 1000 chars) | Wireless Bluetooth Headphones Noise Cancelling |
| regions | string | No | Country/region codes, comma-separated. Supported: US, EM, GB, DE, FR, IT, ES, AU, CA, MX, JP, CN, WO, TR, BX | US,EM,GB |
| limit | integer | Yes | Max number of results to return (default 100, max 500) | 100 |
| productText | string | No | Additional product text such as bullet points, description (max 1000 chars) | Ergonomic design with premium sound quality |

### Supported Regions

| Code | Region |
|------|--------|
| US | United States |
| EM | European Union |
| GB | United Kingdom |
| DE | Germany |
| FR | France |
| IT | Italy |
| ES | Spain |
| AU | Australia |
| CA | Canada |
| MX | Mexico |
| JP | Japan |
| CN | China |
| WO | WIPO (World Intellectual Property Organization) |
| TR | Turkey |
| BX | Bolivia |

When the user does not specify a region, default to **US**.

## How to Call

- **API Endpoint**: `POST /ruiguan/textTrademarkDetection` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/text_trademark_detection.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-ruiguan-text-trademark-detection-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.

## How to Build Requests

### Principles

1. **Include the full product title**: Always pass the complete product title in `productTitle` -- partial text may miss trademark matches.
2. **Choose target regions**: Select regions matching the marketplaces where the product will be sold. Use comma-separated codes for multi-region checks.
3. **Provide additional text when available**: If the user has bullet points, descriptions, or backend keywords, include them in `productText` for a more thorough scan.
4. **Set an appropriate limit**: Use the default of 100 for standard checks. Increase up to 500 when scanning titles with many potential matches.

### Usage Examples

**1. Basic US Trademark Check for a Product Title**
```
productTitle: "Wireless Bluetooth Headphones Noise Cancelling Over Ear"
regions: "US"
limit: 100
```

**2. Multi-Region Check (US + EU + UK)**
```
productTitle: "Portable USB-C Charger Fast Charging Power Bank"
regions: "US,EM,GB"
limit: 100
```

**3. Full Listing Scan with Additional Text**
```
productTitle: "Stainless Steel Vacuum Insulated Water Bottle"
productText: "BPA-free, double-wall insulation, keeps drinks cold 24 hours, fits standard cup holders"
regions: "US,JP"
limit: 200
```

**4. Broad Global Check**
```
productTitle: "LED Ring Light with Tripod Stand for Streaming"
regions: "US,EM,GB,DE,FR,IT,ES,AU,CA,MX,JP,CN"
limit: 500
```

**5. China Domestic Market Check**
```
productTitle: "Bluetooth noise cancelling headphones"
regions: "CN"
limit: 100
```

## Display Rules

1. **Risk-first presentation**: Always highlight the overall risk level (`textTrademarkRadar`) at the top of results. Use clear language: "Low Risk", "Needs Manual Review", or "High Risk".
2. **Blacklist prominence**: If `blacklistTrademarks` is non-empty, display them first with a clear warning.
3. **Table format**: Present trademark matches in a table with columns: Trademark Name, Region, Risk Score, Status, Holder, Application Number, Famous, Amazon Brand, Active Holder.
4. **Score explanation**: Remind users that `highestModeScore` ranges from 0 (safe) to 5 (highest risk).
5. **Whitelist reassurance**: If `whitelistTrademarks` contains entries, note them as safe/exempted trademarks.
6. **Error handling**: When a request fails, explain the issue and suggest the user check their product title or adjust regions.
7. **No legal advice**: Always remind users that results are for reference only and do not constitute legal advice. Recommend consulting an IP attorney for definitive trademark clearance.

## Important Limitations

- **Text-only detection**: This tool detects trademarks in text. It does not analyze logos, images, or design marks.
- **Result cap**: Maximum 500 results per request.
- **Character limit**: Both `productTitle` and `productText` are limited to 1000 characters each.
- **Database coverage**: Covers 15 countries/regions. Trademarks registered in other jurisdictions may not be detected.

## User Expression & Scenario Quick Reference

**Applicable** -- Trademark risk analysis for product text:

| User Says | Scenario |
|-----------|----------|
| "Check my title for trademark issues" | Basic trademark scan |
| "Is this product name safe to use" | Infringement risk check |
| "Scan my listing for brand violations" | Full listing scan |
| "Any trademark risks in this title" | Risk assessment |
| "Check trademarks in US and EU" | Multi-region check |
| "Is XX a registered trademark" | Specific term lookup |
| "Will my listing get taken down for IP" | Compliance screening |
| "Check if this keyword infringes any brand" | Keyword safety check |

**Not applicable** -- Needs beyond text trademark detection:

- Logo or image-based trademark analysis
- Patent infringement checks
- Copyright detection
- Legal opinions or litigation strategy
- Trademark registration or filing assistance
