---
name: ecommerce.utility-patent-detector
description: Detect and search for similar utility/invention patents based on product information. Trigger when users mention utility patent detection, patent infringement risk, patent similarity search, patent screening, invention patent search, patent risk assessment, TRO (Temporary Restraining Order) risk analysis, utility patent, invention patent detection, patent infringement risk, patent search, TRO risk, Ruiguan. Even if the user does not explicitly say "utility patent", trigger this skill whenever their need involves checking whether a product may infringe existing utility/invention patents before selling in a target market.
---

# Ruiguan Utility Patent Detection

This skill guides you on how to search for similar utility (invention) patents based on a product's title, description, and target selling region. It helps cross-border e-commerce sellers identify potential patent infringement risks before listing products.

## Core Concepts

**Utility patent** (also called invention patent) protects new and useful inventions or functional improvements. Unlike design patents that protect appearance, utility patents protect how a product works, its structure, or its composition. Infringing on a utility patent can lead to product removal, lawsuits, or TRO orders.

**Similarity score**: Each returned patent includes a `similarity` field (0 to 1). A higher value means the patent is more closely related to the queried product. Patents with high similarity scores deserve careful review.

**TRO risk indicators**: Two boolean fields flag enforcement history:
- `troCase` -- whether the patent has a history of TRO enforcement actions
- `troHolder` -- whether the patent holder is known for initiating TRO cases

Patents flagged with either indicator require extra caution.

**Patent validity**: The `patentValidity` field shows whether a patent is `Active` or `Invalid`. Only active patents pose infringement risk.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productTitle | string | Yes | Product title (max 1000 characters) |
| productDescription | string | Yes | Product description (max 1000 characters) |
| region | string | Yes | Target selling country/region code, comma-separated for multiple. Currently supports: US. Default: `US` |
| topNumber | integer | Yes | Number of patent results to return. Range: 10--200. Default: `100` |

### Parameter Guidelines

1. **productTitle**: Use the product's actual listing title or a concise descriptive title. Be specific rather than generic -- "portable USB-C fast charger 65W" is better than "charger".
2. **productDescription**: Include key features, materials, mechanisms, and technical attributes. The more detail provided, the more accurate the similarity matching.
3. **region**: Currently only `US` is supported. Always set to `US` unless the user specifies otherwise.
4. **topNumber**: Default is 100. Increase to 200 for a broader search when doing thorough patent clearance. Decrease to 10--20 for a quick preliminary scan.

## How to Call

- **API Endpoint**: `POST /ruiguan/utilityPatentDetection` (see `references/api.md` for full parameters/response/error codes)
- **Python Script**: `python scripts/utility_patent_detector.py '<JSON parameters>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same parameter combination in the same session is called only once by default, with 24h local caching in the script. On failure/empty results, do not automatically retry with different keywords, pagination, or filter changes; inform the user before making additional queries.

**Output strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-ruiguan-utility-patent-detection-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e., the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data reading tip**: Check the summary first to see if sufficient; for specific fields, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## Usage Examples

**1. Basic patent risk check for a product**

User: "Check if this silicone kitchen spatula has any patent risks in the US."

Build the request with a descriptive product title and description, region set to US, and a reasonable topNumber.

**2. Thorough patent clearance before launch**

User: "I'm about to launch a new wireless earbuds product. Do a comprehensive patent check."

Use topNumber=200 for maximum coverage. Include detailed product description covering Bluetooth version, charging case design, noise cancellation features, etc.

**3. Quick scan for TRO risk**

User: "Any TRO risks for selling LED strip lights in the US?"

After retrieving results, filter and highlight patents where `troCase` or `troHolder` is true.

**4. Investigating a specific product category**

User: "Check patent risks for a portable blender with USB charging."

Provide both the product title and a detailed description emphasizing the functional aspects (motor type, blade design, charging mechanism, capacity).

## Display Rules

1. **Present data in tables**: Show results in a clear, structured table format. Key columns to display: patent title, similarity score, patent validity, application number, publication date, TRO flags, and estimated expiration date.
2. **Sort by relevance**: Display patents sorted by similarity score in descending order (highest similarity first).
3. **Highlight high-risk patents**: Call attention to patents with similarity above 0.7, active validity status, and/or TRO flags.
4. **TRO warnings**: If any returned patents have `troCase=true` or `troHolder=true`, display a prominent warning about elevated enforcement risk.
5. **Validity filtering**: When presenting results, clearly distinguish between Active and Invalid patents. Emphasize that only Active patents require attention.
6. **Volume notice**: When results are large, show the most relevant patents (e.g., top 10--20 by similarity) and summarize the rest.
7. **Error handling**: When a query fails, explain the reason and suggest adjusting the product title or description for better results.
8. **Bilingual titles**: When available, show both the English title (`title`) and Chinese title (`titleCn`) to aid understanding.
9. **No legal advice**: Present patent data factually. Do not provide legal conclusions about infringement -- recommend consulting a patent attorney for definitive assessments.

## Important Limitations

- **Region support**: Currently only US patents are searchable
- **Result cap**: Maximum 200 patents per query
- **Input length**: Both productTitle and productDescription are limited to 1000 characters each
- **Not legal advice**: Results indicate similarity, not confirmed infringement. Professional patent review is always recommended.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent-related queries for product risk assessment:

| User Says | Scenario |
|-----------|----------|
| "Check patent risk for my product" | Basic patent detection |
| "Any utility/invention patent issues" | Utility patent search |
| "Is this product safe to sell (patent-wise)" | Patent clearance check |
| "TRO risk for this product" | TRO enforcement risk |
| "Similar patents for this product" | Patent similarity search |
| "Patent infringement check" | Pre-launch risk assessment |
| "Will I get sued for selling this" | Patent risk evaluation |

**Not applicable** -- Needs beyond utility patent detection:

- Design patent searches (appearance/ornamental design)
- Trademark or brand infringement checks
- Copyright issues
- Product compliance or certification (FCC, CE, etc.)
- General legal advice or contract review
