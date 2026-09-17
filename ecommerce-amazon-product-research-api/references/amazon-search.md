# Amazon Search

This reference covers the `references/amazon-search.md` topic for `ecommerce.amazon-product-research-api`.
It preserves the reusable intent of the source document while removing retired account, billing, gateway, and brand-specific instructions.

## Purpose

Route Amazon product-selection work across market, keyword, competitor, trend, review, and profitability capabilities.

## Operational Guidance

1. Route the request to the smallest set of installed Amazon product, keyword, niche, trend, review, and competitor capabilities.
2. Define a bounded funnel: broad discovery, eligibility filters, evidence enrichment, profitability and risk checks, then a ranked shortlist.
3. Do not rerun equivalent paid queries or merge incompatible time windows without disclosure.

## Contract Rules

- Use `api.json` as the machine-readable operation catalog and `api.md` for invocation details.
- Keep source facts, derived values, assumptions, and recommendations distinguishable.
- Do not call retired product gateways or request legacy account credentials.
- Validate required identifiers and record missing evidence instead of inventing results.

## Preserved Source Terms

- |--------|------|
- POST Body（JSON）：
- |------|------|------|------|
- |------|------|
- |----------|------|
- |------|------|------|
- | asin | string | ASIN |
- |---------|------|----------|

## Migration Note

The original path is retained for one-to-one coverage. Product-internal prose was replaced with this English provider-neutral contract; executable behavior is defined by the package-local scripts and operation catalog.
