---
name: temu-store-query
version: 1.0.0
category: product-sourcing
description: |
  Query Temu stores/sellers via EHunt filters. Triggers: Temu store analysis, Temu seller, store ranking, revenue, followers, semi-managed stores. Use for seller/store-level analysis, not individual product sourcing; use temu-product-query for products.
---

# EHunt Temu Store Query (`ehunt/temu/storeQuery`)

## Core Question

Which Temu stores match the user's seller, revenue, category, region, or performance filters?

## When to Use

- User asks to find or rank Temu stores/sellers.
- User wants to compare Temu seller performance, revenue, followers, ratings, product count, or category focus.
- User asks for semi-managed or fully managed Temu stores in specific regions.
- User wants store-level sourcing leads rather than individual product listings.

## Clarify or Infer Before Querying

If the user request is broad or ambiguous, identify:

- target site or region
- category or seller niche
- performance metric to sort by, such as weekly sales, total revenue, rating, followers, or product count
- fulfillment mode if relevant
- desired result count and time window

Use sensible defaults when the user's intent is clear: US site, weekly sales descending, first page, 20 stores.

## Differs From / Not Applicable

- Use `ecommerce.temu-product-query` when the user wants individual Temu products, product prices, product sales, ratings, tags, or product sourcing.
- Use this skill when the unit of analysis is the seller/store.
- Do not use for TikTok Shop data, Amazon seller data, product detail pages, or listing copy optimization.

## Workflow

1. Understand the store-level goal and normalize filters.
2. Resolve region/site, category, fulfillment mode, ranges, and sort order.
3. Query EHunt Temu store data.
4. Return a compact seller table with the most relevant metrics.
5. Add a short interpretation: strongest stores, unusual outliers, and next filters to try.

## Output Structure

Default output should include:

- Query assumptions and filters used
- Store ranking table: store name/ID, site, category focus, sales, revenue, rating, followers, product count, fulfillment mode
- Key observations: top performers, fast-growing or high-efficiency stores, weak data points
- Suggested next step: refine category, inspect products from selected stores, or compare regions

Calls the EHunt data source via the Nexscope proxy gateway, route **`/api/v1/tools/linkfox/ehunt/temu/storeQuery`** (display name: **Temu Store Query**). Authentication and routing are handled by the Nexscope proxy; if the response contains a root-level `code` field, success is determined by the live response.

## Key Points

- **Pagination**: `page` starts at 1; `pageSize` defaults to 20, max 100.
- **Range parameters**: `*Min` / `*Max` pairs (total/weekly/monthly sales, total/weekly/monthly revenue, rating, reviews, followers, product count) form upstream range filters.
- **Site**: `siteId` country site ID, comma-separated for multiple values (`100` = US, `101` = UK, `102` = EU, `103` = JP, `105` = KR).
- **Category**: `category` back-end category ID, comma-separated for multiple values.
- **Fulfillment mode**: `isLocal` (0 = fully managed, 1 = semi-managed, string type).
- **Opening date**: `listedTimeBegin` / `listedTimeEnd` (YYYY-MM-DD).
- **Sorting**: `sortBy` is a "field-direction" string, e.g. `order_week_count-0` (weekly sales descending, default), `order_count-0`, `total_revenue-0`, `rating-0`.

## Scripts (Optional)

CLI debugging: `python scripts/ehunt_temu_store_query.py '<JSON>'` (requires environment variables `NEXSCOPE_API_KEY` and `NEXSCOPE_PROXY_BASE`). See [references/api.md](references/api.md) for details.

## Reference

Full request/response parameter tables: [references/api.md](references/api.md).

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/ehunt_temu_store_query.py --out-dir <DIR> '<params>'
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
