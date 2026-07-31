---
name: ecommerce.amazon-search-by-image
description: Perform image-based visual product search on Amazon across 8 marketplaces. Use an image URL to find visually similar products, with optional Keepa enrichment for sales data. Triggered when users mention Amazon image search, Amazon visual search, find similar products on Amazon, reverse image lookup Amazon, Amazon search by photo, or competitor image search. Even if the user does not explicitly mention "image search," this skill should be triggered whenever a user provides an image URL and wants to find visually matching or similar products on Amazon.
---

# Amazon Image-Based Search

This skill guides you on how to perform visual product searches on Amazon using an image URL, helping Amazon sellers and researchers find visually similar products across multiple marketplaces.

## Core Concepts

Amazon Image-Based Search (visual search) allows you to submit a product image URL and retrieve Amazon listings that are visually similar. This is invaluable for competitive analysis, sourcing alternatives, identifying counterfeits, and discovering market opportunities based on product appearance.

The tool searches across **8 Amazon marketplaces** and returns rich product data including ASIN, title, image, price, rating, review count, brand, and optionally Keepa-enriched data (sales rank, monthly sales, FBA fees, dimensions, etc.).

## Supported Marketplaces

| Marketplace | Domain | Default Zip Code |
|-------------|--------|-------------------|
| United States | amazon.com | 10001 |
| United Kingdom | amazon.co.uk | EC1A 1BB |
| Germany | amazon.de | 10115 |
| France | amazon.fr | 75001 |
| Italy | amazon.it | 00100 |
| Spain | amazon.es | 28001 |
| Japan | amazon.co.jp | 100-0001 |
| India | amazon.in | 110034 |

Default marketplace is **amazon.com** (US). Use amazon.com when the user does not specify a marketplace.

## Parameter Guide

| Parameter | Required | Description |
|-----------|----------|-------------|
| imageUrl | Yes | A valid, publicly accessible image URL to search with |
| amazonDomain | Yes | Amazon marketplace domain (e.g., `amazon.com`, `amazon.de`). Defaults to `amazon.com` |
| sort | No | Sort order for results. Supported values: `default`, `price-asc-rank`, `price-desc-rank`, `rating-asc-rank`, `rating-desc-rank`, `ratings-asc-rank`, `ratings-desc-rank` |
| deliveryZip | No | Delivery address zip code within the marketplace country. Uses the marketplace default if not specified |
| countryOrAreaCode | No | Country/region code for cross-border delivery (e.g., `CN`, `JP`, `KR`). Cannot be used together with `deliveryZip`. Note: India marketplace does not support cross-border delivery |
| aggregateByKeepaData | No | Whether to enrich results with Keepa data (sales rank, monthly sales, FBA fees, dimensions, etc.) |

### Sort Options

| Value | Description |
|-------|-------------|
| `default` | Default relevance sorting |
| `price-asc-rank` | Price: low to high |
| `price-desc-rank` | Price: high to low |
| `rating-asc-rank` | Rating: low to high |
| `rating-desc-rank` | Rating: high to low |
| `ratings-asc-rank` | Review count: low to high |
| `ratings-desc-rank` | Review count: high to low |

**Important**: If the requested sort order is not in the supported list above, do NOT attempt to use any other tool or workaround to compensate. Inform the user of the supported sort options.

## Usage

- **API Endpoint**: `POST /amazon/searchByImage` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/amazon_search_by_image.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic image search on the US marketplace**
```
Search Amazon US for products that look similar to this image:
https://m.media-amazon.com/images/I/61pAlIX8SZL._AC_SY575_.jpg
```

**2. Find similar products on a specific marketplace**
```
Search Amazon Germany (amazon.de) for products visually similar to this image:
https://example.com/product-photo.jpg
```

**3. Image search sorted by price (low to high)**
```
Find similar products on Amazon US for this image, sorted by price from low to high:
https://example.com/my-product.jpg
```

**4. Image search with Keepa data enrichment**
```
Search Amazon US for products matching this image and include Keepa sales data:
https://example.com/competitor-product.jpg
```

**5. Cross-border delivery search**
```
Search Amazon Japan for similar products to this image, with delivery to China:
https://example.com/item.jpg
```

**6. Competitor lookalike discovery**
```
I found this product image on a competitor's listing. Find me all similar-looking products on Amazon UK:
https://example.com/competitor.jpg
```

## Display Rules

1. **Present data clearly**: Show search results in a well-structured table. Key columns to prioritize: product image, title, ASIN, price, rating, review count, and brand
2. **Image display**: When the response includes `imageUrl` for products, display them inline so users can visually compare results
3. **Price and currency**: Always show price alongside the currency code (e.g., $29.99 USD)
4. **Keepa data**: When `aggregateByKeepaData` is enabled and Keepa fields are present, show supplementary data (monthly sales, sales rank, FBA fees) in an expanded section or additional columns
5. **Result count**: Always inform the user of the total number of results found
6. **Error handling**: When a query fails, explain the issue and suggest checking that the image URL is valid and publicly accessible
7. **Sort limitation**: If the user requests a sort order not in the supported list, clearly explain which sort options are available rather than attempting unsupported workarounds
8. **No secondary processing**: Results from this tool are not stored in a database, so secondary SQL processing is not available

## User Expression & Scenario Quick Reference

**Applicable** -- Visual product search scenarios on Amazon:

| User Says | Scenario |
|-----------|----------|
| "Find similar products to this image" | Basic image search |
| "Search by image," "reverse image search on Amazon" | Visual search |
| "Find competitor lookalikes," "find same-style products" | Competitor analysis by appearance |
| "What products on Amazon look like this" | Product discovery |
| "Find cheaper alternatives that look the same" | Price-based visual comparison |
| "Search Amazon JP/DE/UK for this product image" | Cross-marketplace visual search |
| "Show me Keepa data for similar products" | Enriched visual search |
| "Find products similar to this photo, sorted by rating" | Sorted visual search |

**Not applicable** -- Needs beyond image-based product search:

- Text-based keyword search on Amazon (use keyword search tools instead)
- ABA search term data analysis
- Product review analysis or listing optimization
- Sales estimation without a source image
- Image editing or image generation

**Boundary judgment**: When users say "find similar products" or "competitor analysis," if they provide an image URL and the intent is to find visually similar Amazon listings, this skill applies. If they are asking for keyword-based search, sales data analysis, or product research without an image, it does not apply.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
