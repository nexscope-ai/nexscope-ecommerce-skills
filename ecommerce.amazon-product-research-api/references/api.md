# API contract for `ecommerce.amazon-product-research-api`

## Scope

Route Amazon product-selection work across market, keyword, competitor, trend, review, and profitability capabilities.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `aba_query`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/aba/intelligentQuery`
- Package script: `scripts/aba_query.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_alexa_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/alexaSearch`
- Package script: `scripts/amazon_alexa_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_opportunity_report`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/opportunity/reportByKeyword`
- Package script: `scripts/amazon_opportunity_report.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_opportunity_screener`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/opportunity/searchByMetrics`
- Package script: `scripts/amazon_opportunity_screener.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_product_detail`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/product/detail`
- Package script: `scripts/amazon_product_detail.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_reviews`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/reviews/list`
- Package script: `scripts/amazon_reviews.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/search`
- Package script: `scripts/amazon_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `amazon_search_by_image`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/amazon/searchByImage`
- Package script: `scripts/amazon_search_by_image.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `jiimore_get_niche_info`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/jiimore/getNicheInfo`
- Package script: `scripts/jiimore_get_niche_info.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `jiimore_get_niche_info_by_keyword`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/jiimore/getNicheInfoByKeyword`
- Package script: `scripts/jiimore_get_niche_info_by_keyword.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `jiimore_get_niche_review`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/jiimore/getNicheReviewFromKeyword`
- Package script: `scripts/jiimore_get_niche_review.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `jiimore_page_asins_by_asin`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/jiimore/pageAsinsByAsin`
- Package script: `scripts/jiimore_page_asins_by_asin.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `jiimore_product_discovery`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/jiimore/productDiscovery`
- Package script: `scripts/jiimore_product_discovery.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_keyword_by_asin`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/keywords/by-asin`
- Package script: `scripts/junglescout_keyword_by_asin.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_keyword_by_keyword`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/keywords/by-keyword`
- Package script: `scripts/junglescout_keyword_by_keyword.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_keyword_history`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/keywords/historical-search-volume`
- Package script: `scripts/junglescout_keyword_history.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_keyword_sov`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/keywords/share-of-voice`
- Package script: `scripts/junglescout_keyword_sov.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_product_database`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/product-database/query`
- Package script: `scripts/junglescout_product_database.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_sales_estimates`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/sales-estimates/query`
- Package script: `scripts/junglescout_sales_estimates.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `keepa_product_detail`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/keepa/productRequest`
- Package script: `scripts/keepa_product_detail.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `keepa_product_history`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/keepa/productSeries`
- Package script: `scripts/keepa_product_history.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `keepa_product_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/keepa/productSearch`
- Package script: `scripts/keepa_product_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `onboarding`

- Execution mode: `local-script`
- Callable: `true`
- Mutation: `false`
- Gateway path: `none`
- Upstream semantic path: `scripts/onboarding.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sellersprite_competitor_lookup`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sellersprite/competitor-lookup`
- Package script: `scripts/sellersprite_competitor_lookup.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sellersprite_market_research`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sellersprite/market/research`
- Package script: `scripts/sellersprite_market_research.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sellersprite_market_statistics`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sellersprite/market/statistics`
- Package script: `scripts/sellersprite_market_statistics.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sellersprite_product_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sellersprite/productSearch`
- Package script: `scripts/sellersprite_product_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sellersprite_traffic_keyword`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sellersprite/traffic/keyword`
- Package script: `scripts/sellersprite_traffic_keyword.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sif_asin_keywords`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sif/asinKeywords`
- Package script: `scripts/sif_asin_keywords.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sif_asin_summary`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sif/asinSummary`
- Package script: `scripts/sif_asin_summary.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sif_keyword_overview`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sif/keywordOverview`
- Package script: `scripts/sif_keyword_overview.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sif_keyword_traffic`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sif/keywordSummary`
- Package script: `scripts/sif_keyword_traffic.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sorftime_product_detail`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sorftime/amazon/productDetail`
- Package script: `scripts/sorftime_product_detail.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `sorftime_product_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/sorftime/amazon/productQuery`
- Package script: `scripts/sorftime_product_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `upload_image`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `true`
- Gateway workflow: `POST /api/skill-asset/presign` -> `PUT <presigned HTTPS URL>` -> `POST /api/skill-asset/confirm`
- Upstream semantic path: `scripts/upload_image.py`
- Required inputs: `localImagePath`
- Presign payload: `fileName`, `contentType`, `fileSize`
- Confirm payload: `ossKey`, `expectedSize`, `expectedSha256`
- Output: confirmed `publicUrl` as `url`, plus `assetId`, `name`, `size`, and `ext`
- Security: send `NEXSCOPE_API_KEY` only to the two gateway endpoints. Do not send it to the presigned upload host, do not follow upload redirects, and do not derive the public URL from the presigned URL.

## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/aba_query.py --help
# Run the selected local script with its documented arguments.

python scripts/upload_image.py --confirm --confirm-mutation /path/to/product.png
# The final URL comes from the confirm response.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
