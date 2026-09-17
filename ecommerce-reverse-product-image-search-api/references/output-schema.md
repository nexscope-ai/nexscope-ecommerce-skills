# Output Schema

This reference covers the `references/output-schema.md` topic for `ecommerce.reverse-product-image-search-api`.
It preserves the reusable intent of the source document while removing retired account, billing, gateway, and brand-specific instructions.

## Purpose

Find visual or keyword-derived competitors from a product image or URL across supported marketplaces.

## Operational Guidance

1. Identify or confirm one target marketplace and site from the image or product URL.
2. Use image search for Amazon; for Walmart, TikTok, eBay, and Ozon, recognize product attributes first and search localized keywords.
3. Normalize competitor price, demand, rating, seller, category, and listing evidence into a comparable sourcing table.

## Contract Rules

- Use `api.json` as the machine-readable operation catalog and `api.md` for invocation details.
- Keep source facts, derived values, assumptions, and recommendations distinguishable.
- Do not call retired product gateways or request legacy account credentials.
- Validate required identifiers and record missing evidence instead of inventing results.

## Preserved Source Terms

- |------|------|------|-----------|
- | `asin` | string | ASIN | amazon |

## Migration Note

The original path is retained for one-to-one coverage. Product-internal prose was replaced with this English provider-neutral contract; executable behavior is defined by the package-local scripts and operation catalog.
