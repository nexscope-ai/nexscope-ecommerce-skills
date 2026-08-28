---
name: ecommerce-temu-product-source-query
description: "Filter Temu products by multiple dimensions (keyword/product ID/store ID, front/backend categories, price, rating, reviews, total/weekly/daily sales, listing date, fully-managed/semi-managed, semi-managed regions, tags, etc.). Triggered when users mention Temu products, Temu product selection, Pinduoduo cross-border, Temu bestsellers, Temu semi-managed, fully-managed products, Temu product query, or temu items. Even if the user does not mention the tool name, this skill should be triggered whenever searching for products, viewing sales/ratings/prices, or filtering products on Temu."
---

# Temu Product Query

## Quick Reference

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100 (recommended <= 50).
- **Range parameters**: `*Begin` / `*End` come in pairs (price, rating, reviews, total/weekly/daily sales, listing date), forming upstream ranges.
- **Categories**: `categoryHome` frontend category ID, `categoryBackend` backend category ID; use Temu Category Search first to get the ID.
- **Fulfillment mode**: `isLocal` (0=fully-managed, 1=semi-managed); for semi-managed, use `region` to specify regions (multiple separated by commas).
- **Listing status**: `soldOut` (0=active, 1=delisted).
- **Tags**: `tags` / `customTags` -- multiple separated by commas.
- **Sorting**: `sortBy` is a "field-direction" string, e.g., `order_week-0` (weekly sales descending, default), `price-0`, `order_total-0`, `rating-0`.

## Script (Optional)

Command-line debugging: `python scripts/temu_product_source_query.py '<JSON>'` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

See [references/api.md](references/api.md) for input/output parameter tables.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
