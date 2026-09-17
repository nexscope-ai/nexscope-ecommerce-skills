# Testing ecommerce.geekbi-temu-shop

## Static and offline gates

- Compile `scripts/geekbi_temu_category_list.py` with Python.
- Compile `scripts/geekbi_temu_mall_search.py` with Python.
- Compile `scripts/geekbi_temu_site_list.py` with Python.
- Verify every request URL begins with `/api/v1/tools/research/` and authentication uses `NEXSCOPE_API_KEY` with Bearer authorization.
- Mock a successful Nexscope envelope, an outer nonzero code, HTTP 401, HTTP 402, malformed JSON, and a network timeout.
- Verify the response preserves `X-Cost-Token` and `X-Cost-Credit` as server-reported billing metadata without client-side conversion.
- Verify full responses are stored below `nexscope/<date>/<session>/data` and secrets are never written.
- Verify that no marketplace account or seller credential is requested.

## Live-test status

Not run during staging migration. A paid or credentialed call requires explicit approval. Record timestamp, environment, redacted request, HTTP status, outer code, business status, trace ID, `X-Cost-Token`, calculated credits, `X-Cost-Credit`, and saved response path when testing is approved.
