---
name: ecommerce.1688-search-by-image
description: Perform image-based product search on the 1688 platform. Use an image URL to find visually similar supplier products, returning title, price, minimum order quantity, monthly sales, repurchase rate, trade score, and seller identity. Triggered when users mention 1688 image search, 1688 visual search, find supplier by image, reverse image search 1688, 1688 product sourcing by image, or Alibaba 1688 image search. Even if the user does not explicitly mention "image search," this skill should be triggered whenever a user provides an image URL and wants to find matching or similar products on the 1688 wholesale platform.
---

# 1688 Image-Based Product Search

This skill performs visual product searches on the 1688 platform using an image URL, helping cross-border sellers find visually similar supplier products for sourcing.

## Core Concepts

1688 Image Search uses visual recognition to find products with similar appearance on the 1688 wholesale marketplace. It returns supplier product data including title, price, minimum order quantity, monthly sales, repurchase rate, trade score, and seller identity badges.

## Data Fields

| Field | Description |
|-------|-------------|
| offerId | Product ID on 1688 |
| title | Product title |
| imageUrl | Product main image |
| price | Wholesale price (CNY) |
| consignPrice | Dropship price (CNY) |
| salesQuantity | Monthly sales volume |
| estimatedSalesAmount | Estimated monthly revenue |
| quantityBegin | Minimum order quantity |
| repurchaseRate | Repurchase rate |
| tradeScore | Product trade score |
| compositeServiceScore | Composite service experience score |
| sellerIdentities | Seller identity (Super Factory / Verified Supplier / TrustPass member) |
| offerIdentities | Product badge (Premium Selection) |
| sendGoodsAddressText | Shipping origin |
| deliveryTime | Delivery time (24/48 hours) |
| isOnePsale | Supports dropshipping (Yes/No) |
| isJxhy | Premium sourcing (Yes/No) |
| hasPromotion | Has promotion (Yes/No) |
| isPatentProduct | Patent product (Yes/No) |

## Parameter Guide

**Image Rules:**
1. Only png, jpg, jpeg formats are supported. webp, gif, and other formats are NOT supported.
2. Base64 string must be pure encoded content WITHOUT the `data:image/jpeg;base64,` prefix.
3. Image source — one of imageUrl, imageBase64, or imageId must be provided (at least one required).

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| imageUrl | Conditional | - | Public image URL (max 1000 chars). Only png/jpg/jpeg formats supported |
| imageBase64 | Conditional | - | Pure Base64 encoded image string, without `data:image/...;base64,` prefix. Only png/jpg/jpeg supported |
| imageId | Conditional | - | 1688 image ID from previous search result (speeds up pagination) |
| page | No | 1 | Page number, starting from 1 |
| pageSize | No | 20 | Results per page (1-50) |
| priceStart | No | - | Min price filter (CNY) |
| priceEnd | No | - | Max price filter (CNY) |
| filter | No | - | Filter conditions, comma-separated (see supported filters below) |
| sort | No | {"monthSold":"desc"} | Sort as JSON: {field: direction} (see supported sort fields below) |
| keyword | No | - | Keyword to further filter results |
| productCollectionId | No | - | Product collection ID (see supported IDs below) |

### Supported Filters

Multiple filters can be combined with commas (e.g. `1688Selection,totalEpScoreLv1,qrr0`).

| Filter Value | Description |
|--------------|-------------|
| 1688Selection | 1688 Premium Selection |
| certifiedFactory | Certified factory |
| totalEpScoreLv1 | Composite experience 5-star |
| totalEpScoreLv2 | Composite experience 4-star |
| totalEpScoreLv3 | Composite experience 3-star |
| totalEpScoreLv4 | Composite experience 2-star |
| qrr0 | No quality refunds |
| qrr1 | Quality refund rate <1% |
| qrr5 | Quality refund rate <5% |
| qrr10 | Quality refund rate <10% |
| shipInToday | Same-day shipping |
| shipIn24Hours | 24-hour shipping |
| shipIn48Hours | 48-hour shipping |
| noReason7DReturn | 7-day no-reason return |
| isOnePsale | Dropshipping supported |
| isOnePsaleFreePost | Dropshipping with free shipping |
| new7 | Listed within 7 days |
| new30 | Listed within 30 days |
| isQqyx | Global premium selection |
| JPFL | Japan express line |
| USFL | US express line |
| KRFL | Korea express line |
| VNFL | Vietnam express line |
| SAFL | Saudi Arabia express line |
| RUFL | Russia express line |
| KZFL | Kazakhstan express line |
| HKFL | Hong Kong express line |
| MOFL | Macau express line |
| TWFL | Taiwan express line |

### Supported Sort Fields

| Field | Direction | Description |
|-------|-----------|-------------|
| price | asc/desc | Price ascending/descending |
| monthSold | asc/desc | Monthly sales ascending/descending |
| rePurchaseRate | asc/desc | Repurchase rate ascending/descending |

Sort format example: `{"price":"asc"}` for price low to high.

### Supported Product Collection IDs

| ID | Usage |
|----|-------|
| 262105288 | Cross-border product collection |
| 262105286 | Cross-border product collection |
| 262105253 | Cross-border product collection |
| 262105281 | Cross-border product collection |
| 262105280 | Cross-border product collection |
| 262105277 | Cross-border product collection |
| 262105276 | Cross-border product collection |
| 262105274 | Cross-border product collection |
| 262105269 | Cross-border product collection |
| 262185282 | Cross-border product collection |

## Usage

- **API Endpoint**: `POST /alibaba1688/imageSearch` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/alibaba1688_image_search.py '<JSON parameters>'`

**Output strategy (script default behavior)**:
- Prints the full JSON response to stdout

**Data reading tip**: Use `jq` or `ConvertFrom-Json` to extract specific fields from the response as needed.

## Usage Examples

**1. Basic image search**
```
Search 1688 for products visually similar to this image: https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg
```

**2. Search with filters**
```
Search 1688 for products similar to this image: https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg -- filter by 1688 Premium Selection, sort by price descending, page 1
```

**3. Search with sorting**
```
Search 1688 for products similar to this image: https://example.com/product.jpg -- sort by price from high to low
```

**4. Paginated search**
```
Search 1688 for products similar to this image: https://example.com/product.jpg -- page 2, 50 results per page
```

**5. Price range filter**
```
Search 1688 for products similar to this image: https://example.com/product.jpg -- price range 10-100 CNY
```

## Display Rules

1. **Present data clearly**: Show results in a structured table with key columns: product image, title, price, dropship price, monthly sales, minimum order quantity, repurchase rate, and seller identity
2. **Image display**: When the response includes imageUrl for products, display them inline for visual comparison
3. **Price display**: Always show price in CNY format
4. **Seller badges**: Display seller identity badges (Super Factory / Verified Supplier / TrustPass member) and product badges (Premium Selection) prominently
5. **Result count**: Always inform the user of total results and current page/total pages
6. **Pagination hint**: When more pages are available, suggest the user can request the next page
7. **Filter/sort limitation**: If the user requests a sort or filter not in the supported list, do NOT attempt any workaround. Inform the user of the supported options
8. **No secondary processing**: Results are real-time and not stored in a database, so secondary SQL/data processing is not available

## Important Limitations

1. **Data real-time nature**: Results are live searches, not stored in any database.
2. **Logic constraint**: If the user requests sort or filter conditions not in the preset supported list, do NOT call any other tool or logic to compensate.
3. **Image input**: One of imageUrl, imageBase64, or imageId is required. For page > 1, prefer passing imageId from the first page result to speed up queries.
4. **Image format**: Only png, jpg, jpeg are supported. webp, gif, and other formats will be rejected.
5. **Base64 format**: The imageBase64 value must be the raw Base64 string only — do NOT include the `data:image/jpeg;base64,` prefix.
6. **Page size**: Maximum 50 results per page.

## User Expression & Scenario Quick Reference

**Applicable** -- Visual product sourcing scenarios on 1688:

| User Says | Scenario |
|-----------|----------|
| "Search 1688 by image" / "Find supplier by product image on 1688" | Basic image search |
| "Find same-style products on 1688 with this image" | Find same-style products |
| "Cross-border sourcing by image" | Cross-border supplier sourcing |
| "Is this Amazon product available on 1688" | Reverse sourcing from Amazon image |
| "Filter 1688 Premium Selection similar products" | Filtered image search |
| "Sort similar products by monthly sales" | Sorted image search |
| "Show page 2 results" | Pagination |

**Not applicable** -- Needs beyond 1688 image search:

- Text/keyword-based 1688 search
- 1688 product rankings/trending
- Amazon image search (use ecommerce.amazon-search-by-image)
- Image generation or editing
- Product review analysis
- Price history or trend analysis

**Boundary judgment**: When users say "find supplier" or "find same style," if they provide an image URL and the intent is to find visually similar products on 1688, this skill applies. If they want keyword-based search or ranking data on 1688, use other tools instead.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://os.nexscope.com/ to manage credits.
