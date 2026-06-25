---
name: ecommerce.temu-product-query
version: 1.1.0
category: product-sourcing
description: |
  Query Temu products via EHunt filters. Triggers: Temu product search, Temu sourcing, bestsellers, semi-managed products, price/sales/rating filters. Use for product-level Temu discovery, not store rankings; use temu-store-query for sellers.
---

# EHunt Temu Product Query (`ehunt/temu/productQuery`)

## Product Understanding Step

Before running this skill, if the user provides a product, image, ASIN, listing, product ID, or product idea, first identify:

- product type/category
- main use case
- key physical, design, or functional features
- target marketplace, country, or platform
- user's analysis goal

Use this product understanding to choose parameters, filters, competitors, regions, keywords, or analysis dimensions before executing the script.

## Core Question

Which Temu products match the user's sourcing, category, sales, price, rating, fulfillment, or listing-activity filters?

## When to Use

- User asks to search, filter, or rank Temu products.
- User wants Temu product sourcing ideas by price, sales, reviews, rating, listing date, tags, or fulfillment mode.
- User asks for semi-managed Temu products or region-specific Temu opportunities.
- User provides a product idea and wants comparable Temu products or category examples.

## Clarify or Infer Before Querying

If the user request is broad or ambiguous, identify:

- product category or keyword
- target site, country, or semi-managed region
- price, sales, rating, review, or publish-time constraints
- fulfillment mode and listing status
- desired sort metric, such as weekly sales, total sales, price, rating, or revenue

Use sensible defaults when the user's intent is clear: first page, 20 products, weekly sales descending, active listings.

## Differs From / Not Applicable

- Use `ecommerce.temu-store-query` when the user wants seller/store rankings or seller performance.
- Use this skill when the unit of analysis is the individual product.
- Do not use for TikTok Shop products, Amazon products, patent checks, or listing keyword optimization.

## Workflow

1. Understand the product/category intent and normalize filters.
2. Resolve category name to ID when the user gives a category name.
3. Query EHunt Temu product data with explicit filters.
4. Return a compact product table with product, sales, revenue, price, rating, reviews, tags, and fulfillment.
5. Add short sourcing observations and recommended follow-up filters.

## Output Structure

Default output should include:

- Query assumptions and filters used
- Product table: title/product ID, site/region, category, price, sales, revenue, rating, reviews, tags, fulfillment mode, listing status
- Key observations: strongest products, low-price/high-sales candidates, review gaps, new listings, possible saturation
- Suggested next step: inspect stores, compare TikTok/Amazon demand, or narrow by category/price band


Calls the EHunt data source via the Nexscope proxy gateway, route **`/api/v1/tools/linkfox/ehunt/temu/productQuery`** (display name: **Temu Product Query**). Authentication and routing are handled by the Nexscope proxy; if the response contains a root-level `code` field, success is determined by the live response.

## Built-in Category Search

When the user specifies a category by name rather than ID, first call the category search script to resolve the name to an ID, then pass that ID as `categoryHome` or `categoryBackend`.

## Key Points

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100.
- **Range parameters**: `*Begin` / `*End` pairs (price, rating, reviews, total/weekly/daily sales, publish time) form upstream range filters.
- **Category**: `categoryHome` (front-end category ID), `categoryBackend` (back-end category ID).
- **Fulfillment mode**: `isLocal` (0 = fully managed, 1 = semi-managed); `region` for semi-managed regions.
- **Listing status**: `soldOut` (0 = listed, 1 = delisted).
- **Tags**: `tags` and `customTags`, comma-separated.
- **Sorting**: `sortBy` is a "field-direction" string, e.g. `order_week-0` (weekly sales descending, default), `price-0`, `order_total-0`, `rating-0`.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/ehunt_temu_product_query.py` | CLI debug tool; POSTs JSON to the proxy gateway |

## Reference

Full request/response parameter tables: [references/api.md](references/api.md).

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/ehunt_temu_product_query.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data -- do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** -- apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you do not need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

Warning: The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXSCOPE_PROXY_BASE` | Yes | NexScope proxy base URL |
| `NEXSCOPE_API_KEY` | Yes | NexScope proxy API key |
