---
name: ecommerce-shopee-product-detail
description: Retrieve the current public details of one Shopee listing from a supported product URL, including price, discount, sales, stock, variants, media, brand, category, shop, and rating data. Use when a user provides a Shopee product URL and asks for listing details, SKU variants, inventory, pricing, or competitor-page analysis. Do not use for keyword search, historical trends, reviews, or seller-account operations.
---

# Shopee Product Detail

Retrieve one public Shopee listing from its direct product URL.

## Required input

Pass exactly one `productUrl`. It must be an HTTPS URL on one of these hosts:

- `shopee.sg`
- `shopee.co.id`
- `shopee.com.my`
- `shopee.ph`
- `shopee.co.th`
- `shopee.tw`
- `shopee.vn`
- `shopee.com.br`

The URL path must end in `-i.<numeric shopId>.<numeric itemId>`. Canonical `/product/<shopId>/<itemId>` URLs are not supported.

## Invocation

- Endpoint: `POST /api/v1/tools/research/shopee/product/detail`
- Script: `python scripts/shopee_product_detail.py '<JSON params>' [--inline] [--no-cache]`
- Full contract: read [references/api.md](references/api.md) before diagnosing validation or response errors.
- Testing instructions and evidence: see [references/testing.md](references/testing.md).

Example:

```bash
python scripts/shopee_product_detail.py '{"productUrl":"https://shopee.sg/example-i.9641401.29691169956"}'
```

Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. The script sends the request through the NexScope research proxy, uses a 150-second timeout, caches identical parameters for 24 hours, and always writes the full response under `<cwd>/nexscope/<date>/<session>/data/`.

Do not reuse the source Skill's point value. The actual NexScope charge is calculated after the response as `X-Cost-Token × 0.001041`. For example, `105000 × 0.001041 = 109.305` credits. Record `X-Cost-Credit` when present, but do not use it as the migrated Skill's billing basis. The exact charge is unknown before the first live response.

## Error and credit handling

- HTTP 401 means Nexscope authentication failed. Verify `NEXSCOPE_API_KEY` and `NEXSCOPE_PROXY_BASE`; do not ask the user to paste credentials into chat or operation JSON.
- HTTP 402 means the account lacks credits. Stop the workflow and direct the user to the access-help page below.
- Marketplace authorization failures require the platform-specific account or token to be renewed. Do not substitute a different store, region, or creator automatically.
- For ambiguous network failures, report whether the attempted operation was a read or mutation. Never repeat a mutation without reconciling its upstream state.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [Nexscope external access help](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.

## Presenting results

1. Lead with the listing name, item ID, shop, marketplace, current price, currency, stock, and public sold count.
2. Preserve returned currencies and price values; do not convert them unless requested.
3. Show SKU models and per-variant stock in a compact table when available.
4. Show only a small useful selection of images.
5. Treat Mall, official-shop, and verified-seller flags as separate signals.
6. State clearly when descriptions, variants, inventory, sales, or other enrichment fields are absent.

## Boundaries

- One listing per call; this is not a keyword-search or bulk-screening tool.
- Values are a current public snapshot, not historical data.
- Customer review rows are not returned; rating aggregates may be available.
- Field coverage varies by marketplace and listing state.
- Invalid, removed, mismatched, or unsupported listings return an error rather than an empty successful result.
- This skill does not manage an authorized Shopee seller account.

## Privacy

Redact credentials, signed URLs, cookies, and internal account identifiers from user-facing output and saved request examples.

## References

- Read [references/api.md](references/api.md) for the complete parameter, response, and error contract.
- Read [references/testing.md](references/testing.md) before executing a live request or claiming a validation level.
