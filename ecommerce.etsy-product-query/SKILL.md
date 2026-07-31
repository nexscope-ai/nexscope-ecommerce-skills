---
name: ecommerce.etsy-product-query
description: Query Etsy products with multi-dimensional filters (keyword/URL, price, sales, favorites, reviews, listing date, category, handmade/vintage types, Pick/Bestseller/Raving tags). Trigger when user mentions Etsy products, Etsy listings, Etsy product sourcing, Etsy bestsellers, Etsy handmade, Etsy vintage, Etsy items, or Etsy product query — even if the tool name is not mentioned, as long as the need is to search products, view sales/price/tags, or filter items on Etsy.
---

# Etsy Product Query (`_ehunt_productQuery`)

## Key Points

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, maximum 100 (recommended <= 50).
- **Range Parameters**: Same approach as the store interface — `begin*` / `end*` pairs.
- **Sorting**: `sortBy` is **1~6** (upstream `sort_by`). `sortDesc`: **1=descending, 2=ascending** (different from `_ehunt_storeQuery` which uses 1/0).
- **Product Type** `productType`: `1` Handmade, `2` Vintage, `3` Digital, `4` Custom, `9` Other, use commas for multiple selection.
- **Currency**: `currencyCode` defaults to `USD`.
- **Category ID**: `category` is a single category ID; use the category search skill to find the ID first.

## Script (Optional)

Command-line debugging: `python scripts/etsy_product_query.py ''<JSON>''` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

Input/output parameter tables are in [references/api.md](references/api.md).

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## Credit Consumption

Dynamic pricing: credits consumed = number of products returned x 1.8. Billed per page of results returned; fetching the next page is essentially a new request, billed again based on the new page''s result count.

> **Important**: This skill''s cost scales dynamically and may consume a significant number of credits in a single call. You must warn the user and let them decide whether to continue.