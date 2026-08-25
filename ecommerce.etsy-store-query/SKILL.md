---
name: ecommerce.etsy-store-query
description: Query Etsy stores with multi-dimensional filters (sales, favorites, reviews, store opening date, country, primary category, Raving/Star ratings). Trigger when user mentions Etsy store, Etsy shop search, Etsy seller, Etsy shop ranking, Etsy weekly sales stores, Etsy stores, or Etsy store query — even if the tool name is not mentioned, as long as the need is to find stores, filter store data, or analyze store performance on Etsy.
---

# Etsy Store Query

## Key Points

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, maximum 100.
- **Range Parameters**: `begin*` / `end*` pairs correspond to upstream comma-delimited ranges. Filling only one side means the upstream treats it as "start~" or "~end".
- **Sorting**: `sortBy` only supports **8~11** (8 total sales, 9 weekly sales, 10 review count, 11 favorite count). `sortDesc`: **1=descending, 0=ascending** (do not confuse with the product query interface''s `sortDesc`).

## Script (Optional)

Command-line debugging: `python scripts/etsy_store_query.py ''<JSON>''` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

Input/output parameter tables are in [references/api.md](references/api.md).

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.

## Credit Consumption

Dynamic pricing: credits consumed = number of stores returned x 1.8. Billed per page of results returned; fetching the next page is essentially a new request, billed again based on the new page''s result count.

> **Important**: This skill''s cost scales dynamically and may consume a significant number of credits in a single call. You must warn the user and let them decide whether to continue.
