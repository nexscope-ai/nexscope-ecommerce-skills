---
name: ecommerce.etsy-category-search
description: Search Etsy category data by name, ID, or parent IDs to find category identifiers for product/store filtering. Trigger when user mentions Etsy category, Etsy category ID, Etsy category tree, Etsy category lookup, syncEtsyCategory, or category search — even if the tool name is not mentioned, as long as the need is to find a category ID by keyword in a locally synced Etsy category library.
---

# Etsy Category Search

## Key Points

- **Required**: `keyword` (substring match against category name, category ID, `parentIds`).
- **Pagination**: `page` starts at 1; `pageSize` defaults to 50, maximum 200.
- The returned **`id`** can be used as the category identifier for Etsy product search / store query `category` parameters (consistent with the specific tool schema).

## Script (Optional)

Command-line debugging: `python scripts/etsy_category_search.py ''<JSON>''` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

Input/output parameter tables are in [references/api.md](references/api.md).

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Credit Consumption

Does not consume credits.

## API Key request rate

All Nexscope API Keys belonging to the same user share one request-rate allowance for public API execution. The allowance is measured over any rolling 1-second window. Your RPS depends on your account entitlements; do not assume every user has a fixed 1 RPS. A single Skill operation may make multiple public API requests, and each request uses this allowance.

If an execution request returns HTTP 429 with outer code `13012`, the request-rate allowance was exceeded. Honor the returned `Retry-After` before considering another request. Outer code `13013` means the concurrent-request limit was exceeded, not the rate limit; honor its `Retry-After` when supplied. Inspect the response and reconcile state before retrying. Never automatically replay a write operation or a request whose outcome is unclear.
