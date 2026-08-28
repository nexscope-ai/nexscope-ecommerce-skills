---
name: ecommerce-shopify-store-query
description: "Filter Shopify standalone stores by multiple dimensions (store name/domain, country, years since creation, product count, ad count, monthly visits, monthly orders, social media followers, etc.). Triggered when users mention Shopify stores, Shopify store analysis, standalone stores, Shopify sellers, competitor standalone stores, Shopify monthly visits, standalone store ad library, shopify stores, or Shopify store query. Even if the user does not mention the tool name, this skill should be triggered whenever searching for stores, filtering store data, or analyzing store performance on Shopify standalone stores."
---

# Shopify Store Query

## Quick Reference

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100.
- **Range parameters**: `*Min` / `*Max` come in pairs (product count, ad count, monthly visits, monthly orders), forming upstream ranges.
- **Store age** `year`: 1=within last year, 2=1-2 years, 3=2-3 years, 4=3+ years.
- **Sorting**: `sortBy` integer enum (0=product count, 1=category count, 2=monthly visits, 3=FB followers, 4=Ins followers, 5=ad count, 6=relevance, 7=monthly orders default); `orderBy` is `desc` (default) / `asc`.
- **Country**: `country` takes a country code (e.g., `US`, `CN`).

## Script (Optional)

Command-line debugging: `python scripts/shopify_store_query.py '<JSON>'` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

See [references/api.md](references/api.md) for input/output parameter tables.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
