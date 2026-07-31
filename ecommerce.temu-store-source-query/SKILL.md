---
name: ecommerce.temu-store-source-query
description: Filter Temu stores by multiple dimensions (store name/ID, country site, backend category, fully-managed/semi-managed, total/weekly/monthly sales and revenue, rating, reviews, followers, product count, store opening time, etc.). Trigger when users mention Temu store, Temu store analysis, Temu seller, Temu store ranking, Temu semi-managed store, Temu revenue, temu stores, Temu store query. Even if the user does not mention the tool name, trigger this skill whenever they are looking for stores on Temu, filtering store data, or analyzing store performance.
---

# Temu Store Query

When the NexScope "Third-Party Data Service" MCP is available, this maps to the gateway route **`ehunt/temu/storeQuery`** (MCP display name: **Temu Store Query**; exact tool name follows the tool metadata deployed in the current environment). Authentication and upstream routing are handled by the gateway; if the response contains a root-level `code` field, success is determined by the actual network response.

## Key Points

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100.
- **Range parameters**: `*Min` / `*Max` come in pairs (total/weekly/monthly sales, total/weekly/monthly revenue, rating, reviews, followers, product count), forming upstream ranges.
- **Site**: `siteId` is the country site ID, multiple values comma-separated (e.g., `211`=United States, `76`=United Kingdom).
- **Category**: `category` is the backend category ID, multiple values comma-separated.
- **Managed mode**: `isLocal` (0=fully-managed, 1=semi-managed, string type).
- **Store opening time**: `listedTimeBegin` / `listedTimeEnd` (YYYY-MM-DD).
- **Sorting**: `sortBy` is a "field-direction" string, e.g., `order_week_count-0` (weekly sales descending, default), `order_count-0`, `total_revenue-0`, `rating-0`.

## Script (Optional)

Command-line debugging: `python scripts/temu_store_source_query.py '<JSON>'` (requires `NEXSCOPE_API_KEY`). See the end of [references/api.md](references/api.md).

## Reference

See [references/api.md](references/api.md) for input/output parameter tables.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
