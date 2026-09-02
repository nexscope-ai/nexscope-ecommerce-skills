# Testing evidence for `ecommerce-shopee-product-detail`

## Required user information

- One direct public Shopee product URL on a supported marketplace.
- The URL must contain numeric shop and item IDs in the `-i.<shopId>.<itemId>` suffix.
- No seller-account authorization is required; the NexScope API key and sufficient credits are required to call the gateway.

## English prompt coverage

1. Basic: `Look up this Shopee product and show its current price, stock, sold count, rating, and shop: https://shopee.sg/example-i.9641401.29691169956`
2. Filtered: `From this Shopee Malaysia listing, show only the current and original prices, discount, total stock, and official-store signals: https://shopee.com.my/example-i.123456.789012`
3. Advanced: `Analyze this Shopee listing as a competitor page. Summarize its identity and shop, then tabulate all returned SKU models and variant stock, and show up to three images: https://shopee.ph/example-i.123456.789012`

Expected routing: all three prompts select `ecommerce-shopee-product-detail`, make at most one call for the supplied URL, and present only fields returned by the service.

## Error tests

- `{}`: reject because `productUrl` is required.
- `{"productUrl":"not-a-url"}`: reject before network access.
- `{"productUrl":"http://shopee.sg/example-i.1.2"}`: reject because HTTPS is required.
- `{"productUrl":"https://example.com/example-i.1.2"}`: reject because the host is unsupported.
- `{"productUrl":"https://shopee.sg/product/1/2"}`: reject because the required suffix is missing.
- Extra top-level parameters: reject to preserve the one-parameter public contract.

## Evidence

- [x] Static package validation: frontmatter, manifest file list, endpoint prefix, JSON, Python syntax, and `git diff --check` verified locally on 2026-08-27 with `python -m unittest transfer/script/test_shopee_product_detail_staging.py` and focused shell checks. The bundled `quick_validate.py` could not run because PyYAML is absent from both available Python runtimes.
- [x] Offline mock request: request URL, method, authorization, tracing headers, JSON body, 150-second timeout, response parsing, ID matching, cache, and disk-output location verified locally on 2026-08-27 by `transfer/script/test_shopee_product_detail_staging.py`.
- [x] Sandbox or test-environment request: one paid `curl` call to the NexScope test gateway succeeded on 2026-08-27 with HTTP 200, outer `code=0`, inner `data.errcode=200`, one product, and matching `shopId=9641401` / `itemId=29691169956`. Evidence: `transfer/test-results/shopee-product-detail-curl.json`. The test also found that the gateway wraps the documented business payload in an outer NexScope `code/data` envelope; the migrated client currently expects top-level `errcode/data` and therefore requires a compatibility fix before final acceptance.
- [ ] Real-account request: not run; this is a paid call and no production call was authorized.
- [ ] ZIP import and installation: not run; the user requested staging migration and tests, not packaging/import.
- [x] English trigger and output review: the three prompts above and the display rules were reviewed locally on 2026-08-27.

Unchecked items are not failures; they remain unverified. Never mark connected-environment or paid-call evidence complete without durable output from that environment.

## NEX-198 validation evidence

- Static/frontmatter/manifest and offline Mock checks: passed.
- Previously saved test Curl: HTTP 200, outer `code=0`, inner `errcode=200`, requested entity matched.
- External Curl did not expose upstream billing headers; backend monitoring `response.headers` supplied array-valued evidence. `X-Cost-Token=105000`, calculated credits `109.305`, reported `X-Cost-Credit=53`, trace `b0b3a1605c608f1ce954a00dbc8670e9`. Do not substitute body `costToken`.
- ZIP/local install: passed in the isolated `transfer/test-results/public-ecommerce-migration/local-install/skills` root.
- Production publication: not performed.
