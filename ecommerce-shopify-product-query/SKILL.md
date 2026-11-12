---
name: ecommerce.shopify-product-query
description: Filter Shopify standalone store products by multiple dimensions (keyword/URL, price, weekly sales, listing date, Facebook ads, competitiveness, supplier availability, shipping country, etc.). Triggered when users mention Shopify products, Shopify product selection, standalone store product selection, Shopify bestsellers, Shopify dropshipping, standalone store sourcing, Facebook ad products, Shopify product query, or shopify items. Even if the user does not mention the tool name, this skill should be triggered whenever searching for products, viewing weekly sales/revenue/competitiveness, or filtering products on Shopify standalone stores.
---

# Shopify Product Query

## Quick Reference

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100 (recommended <= 50).
- **Range parameters**: `*Min` / `*Max` come in pairs, forming upstream ranges; filling only one side means "from ~" or "up to ~".
- **Sorting**: `sortBy` is an integer enum (default `14` = weekly sales descending; also includes price/ad count/competitiveness/revenue and many other values -- see `references/api.md` for details).
- **Boolean filters**: `facebookAd` (1=has ads), `hasSupplier` (1=has supplier, 0=none), `showDeleted` (1=include delisted) -- all integer switches.
- **Shipping country**: `country` takes a two-letter country code (e.g., `US`).

## Script (Optional)

Command-line debugging: `python scripts/shopify_product_query.py '<JSON>'` (requires `NEXSCOPE_API_KEY`). See [references/api.md](references/api.md) for details.

## Reference

See [references/api.md](references/api.md) for input/output parameter tables.

## Authentication

Set `NEXSCOPE_API_KEY`. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to manage credits.

## API Key request rate

All Nexscope API Keys belonging to the same user share one request-rate allowance for public API execution. The allowance is measured over any rolling 1-second window. Your RPS depends on your account entitlements; do not assume every user has a fixed 1 RPS. A single Skill operation may make multiple public API requests, and each request uses this allowance.

If an execution request returns HTTP 429 with outer code `13012`, the request-rate allowance was exceeded. Honor the returned `Retry-After` before considering another request. Outer code `13013` means the concurrent-request limit was exceeded, not the rate limit; honor its `Retry-After` when supplied. Inspect the response and reconcile state before retrying. Never automatically replay a write operation or a request whose outcome is unclear.
