---
name: ecommerce.temu-category-search
description: Search synced Temu category data in the local database by keyword to find category Chinese names, English names, and category IDs for use in product/store filtering. Triggered when users mention Temu categories, Temu category ID, Temu category tree, Temu backend categories, temu categories, syncTemuCategory (Temu category sync) followed by category queries, or Temu category search. Even if the user does not mention the tool name, this skill should be triggered whenever searching for category IDs by keyword in the locally synced Temu category database.
---

# Temu Category Search

## Quick Reference

- **Required**: `keyword` (substring match against category Chinese name, English name, and category ID).
- **Pagination**: `page` starts at 1; `pageSize` defaults to 50, max 200.
- The returned **`id` / `categoryId`** can be used as category identifiers for Temu product queries (`categoryHome`/`categoryBackend`), store queries (`category`), etc. (as long as it matches the specific tool schema).

## Script (Optional)

Command-line debugging: `python scripts/temu_category_search.py '<JSON>'` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

See [references/api.md](references/api.md) for input/output parameter tables.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.
