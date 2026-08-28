---
name: ecommerce-amazon-product-detail
description: "Retrieve detailed Amazon product information by ASIN, including title, images, bullet points, specifications, A+ content, pricing, ratings & reviews, variants, and more. Trigger when users mention Amazon product details, ASIN lookup, product page data, listing analysis, bullet point extraction, product image retrieval, variant inspection, competitor listing research, price lookup, review breakdown, product specification query, or similar terms. Even if the user does not explicitly say \"product details,\" trigger this skill whenever the request involves retrieving structured data from Amazon product pages via ASIN."
---

# Amazon Product Detail Lookup

This skill guides you on how to retrieve and analyze detailed Amazon product information by ASIN, helping Amazon sellers and researchers extract comprehensive listing data from product pages across 22 Amazon marketplaces.

## Core Concepts

This tool performs front-end simulation of Amazon product pages to extract structured detail data. It returns rich information including the product title, main image, additional images, bullet points (About This Item), product specifications, A+ content description, pricing, ratings distribution, variant structure, and optionally "Frequently Bought Together" and "Related Products" data.

**Billing note**: This tool is billed per ASIN queried. Because the cost is higher than search-based tools, guide users to query only the ASINs they truly need rather than large exploratory batches.

**Batch support**: Up to 40 ASINs can be queried in a single request, provided as a comma-separated string.

## Parameter Guide

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| asins | Yes | -- | Comma-separated ASIN list (up to 40). Example: `B072MQ5BRX,B08N5WRWNW` |
| amazonDomain | No | `amazon.com` | Amazon marketplace domain. See Supported Marketplaces below |
| language | No | -- | Locale code for response language, e.g. `en_US`, `de_DE`, `ja_JP` |
| deliveryZip | No | -- | Postal/ZIP code for delivery-dependent pricing and availability |
| device | No | `desktop` | Device type: `desktop`, `mobile`, or `tablet` |
| returnBoughtTogether | No | `false` | Include "Frequently Bought Together" products in the response |
| returnRelatedProducts | No | `false` | Include "Related Products" list in the response |
| returnAuthorsReviews | No | `false` | Include top customer reviews in the response |

### Supported Marketplaces

| Domain | Country |
|--------|---------|
| amazon.com | United States |
| amazon.co.uk | United Kingdom |
| amazon.de | Germany |
| amazon.fr | France |
| amazon.it | Italy |
| amazon.es | Spain |
| amazon.co.jp | Japan |
| amazon.ca | Canada |
| amazon.com.au | Australia |
| amazon.com.br | Brazil |
| amazon.in | India |
| amazon.nl | Netherlands |
| amazon.se | Sweden |
| amazon.pl | Poland |
| amazon.sg | Singapore |
| amazon.sa | Saudi Arabia |
| amazon.ae | United Arab Emirates |
| amazon.com.tr | Turkey |
| amazon.com.mx | Mexico |
| amazon.eg | Egypt |
| amazon.cn | China |
| amazon.com.be | Belgium |

Default marketplace is **amazon.com** (US). Use `amazon.com` when the user does not specify a marketplace.

## API Invocation

- **API Endpoint**: `POST /amazon/product/detail` (full parameters/responses/error codes see `references/api.md`)
- **Python Script**: `python scripts/amazon_product_detail.py '<JSON params>' [--inline]`
- **Cost Constraint**: This tool consumes credits; the same parameter combination is called only once per session by default, with a 24h local cache in the script. Do not automatically retry with different keywords, pagination, or zip codes after failures/empty results; inform the user about additional cost before continuing.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-amazon-product-detail-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do NOT write to /tmp** -- error out if the current directory is not writable)
- Response body <= 8 KB: after writing to disk, print the full JSON to stdout
- Response body > 8 KB: after writing to disk, stdout outputs only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (while still writing to disk)

**Data Reading Tips**: First check the summary to see if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Usage Examples

**1. Basic single-ASIN lookup**
```
Look up the details of ASIN B072MQ5BRX on Amazon US.
```
Parameters: `{"asins": "B072MQ5BRX"}`

**2. Multi-ASIN batch lookup**
```
Get product details for B072MQ5BRX and B08N5WRWNW.
```
Parameters: `{"asins": "B072MQ5BRX,B08N5WRWNW"}`

**3. Lookup on a non-US marketplace**
```
Fetch product info for B09V3KXJPB on Amazon Germany.
```
Parameters: `{"asins": "B09V3KXJPB", "amazonDomain": "amazon.de"}`

**4. Lookup with reviews and bought-together**
```
Get full product details including reviews and frequently bought together for B08N5WRWNW on Amazon Japan.
```
Parameters: `{"asins": "B08N5WRWNW", "amazonDomain": "amazon.co.jp", "returnBoughtTogether": true, "returnAuthorsReviews": true}`

**5. Competitor listing comparison**
```
Compare bullet points and pricing for these 3 ASINs: B072MQ5BRX, B08N5WRWNW, B09V3KXJPB.
```
Parameters: `{"asins": "B072MQ5BRX,B08N5WRWNW,B09V3KXJPB"}`

**6. Mobile-specific product page check**
```
Show me how product B072MQ5BRX looks on mobile in the UK.
```
Parameters: `{"asins": "B072MQ5BRX", "amazonDomain": "amazon.co.uk", "device": "mobile"}`

## Display Rules

1. **Present data clearly**: Show product details in a well-structured format -- use tables for specifications and pricing comparisons, bullet lists for "About This Item" content
2. **Image handling**: When the response includes image URLs (`productImageUrls`, `thumbnail`, `imageUrl`), present them as clickable links or embedded images as appropriate
3. **Multi-ASIN results**: When multiple ASINs are queried, organize results so each product is clearly separated and labeled by ASIN and title
4. **Price formatting**: Always include the currency symbol/code alongside price values. Show both current price and original price (if discounted) to highlight deals
5. **Rating breakdown**: When `customerReviews` data is present, show the star distribution (5-star through 1-star percentages) alongside the overall rating and total review count
6. **Variant display**: When variants exist, present them in a compact table grouped by variant dimension (color, size, etc.)
7. **Error handling**: When a query fails, explain the reason and suggest checking that the ASIN is valid and the marketplace domain is correct
8. **Cost awareness**: Remind users that this tool charges per ASIN, so they should batch only what they need

## User Expression & Scenario Quick Reference

**Applicable** -- Tasks that require structured Amazon product page data:

| User Says | Scenario |
|-----------|----------|
| "Look up this ASIN", "Get product details for ..." | Single/batch ASIN detail lookup |
| "What are the bullet points for this product" | Listing content extraction |
| "Show me competitor listings" | Multi-ASIN comparison |
| "What is the price of this ASIN on Amazon DE" | Cross-marketplace price check |
| "How many reviews does this product have" | Rating & review analysis |
| "What variants does this product offer" | Variant structure inspection |
| "Get the A+ content / product description" | Product description retrieval |
| "What is the main image for this ASIN" | Product image extraction |
| "Is this product Prime eligible" | Eligibility / badge check |
| "What are the product specs / dimensions" | Specification lookup |

**Not applicable** -- Needs beyond product detail page data:

- Keyword / search term analysis (use ABA Data Explorer instead)
- Search result rankings or organic position tracking
- Advertising / PPC campaign data
- Sales estimation or revenue calculations
- Inventory management or FBA fee analysis
- Review sentiment analysis requiring NLP beyond raw review text
- Historical price tracking over time (this tool returns current snapshot only)

**Boundary judgment**: When users say "analyze this product" or "research this ASIN", if it boils down to retrieving the current product page data (title, price, bullets, images, reviews, variants), this skill applies. If they need historical trends, sales estimates, or advertising insights, it does not apply.