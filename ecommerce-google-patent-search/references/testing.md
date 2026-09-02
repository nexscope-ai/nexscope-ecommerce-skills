# Testing ecommerce-google-patent-search

## Static and mock gates

- Compile `scripts/google_patent_search.py` with Python.
- Verify the request URL begins with `/api/v1/tools/research/`, authentication uses `Bearer`, and timeout remains compatible with the source contract.
- Mock a successful NexScope envelope (`code=0`, business object in `data`), an outer failure, HTTP 401, HTTP 402, malformed JSON, and a network failure.
- Verify full responses are stored below `nexscope/<date>/<session>/data` and secrets are never written.

## English invocation checks

1. Query the documented public entity with the smallest valid request and summarize the result.
2. Explain the expected credit cost before requesting a second page, region, or paid operation.
3. Reject an undocumented parameter without making a request.

## Live test evidence

Record the timestamp, test base URL, redacted request, HTTP status, outer `code`, inner status, `traceId`, `X-Cost-Token`, calculated credits (`token × 0.001041`), reported `X-Cost-Credit`, and saved response path. A paid live call requires explicit approval and must not be retried automatically.

## NEX-198 validation evidence

- Static/frontmatter/manifest and offline Mock checks: passed.
- 2026-08-27 test Curl: HTTP 200, outer `code=0`, inner `errcode=200`; raw header and body saved under `transfer/test-results/public-ecommerce-migration/`.
- External Curl did not expose upstream billing headers; backend monitoring `response.headers` supplied array-valued evidence. `X-Cost-Token=15000`, calculated credits `15.615`, reported `X-Cost-Credit=8`, trace `458a5d69b71b6bd408c9bb597cab45d3`. Do not substitute body `costToken`.
- ZIP/local install: passed in the isolated `transfer/test-results/public-ecommerce-migration/local-install/skills` root.
- Production publication: not performed.
