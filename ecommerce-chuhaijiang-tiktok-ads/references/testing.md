# Testing ecommerce.chuhaijiang-tiktok-ads

## Static and offline gates

- Compile `scripts/chuhaijiang_ad_detail.py` with Python.
- Compile `scripts/chuhaijiang_ad_related_products.py` with Python.
- Compile `scripts/chuhaijiang_ad_search.py` with Python.
- Compile `scripts/chuhaijiang_creative_detail.py` with Python.
- Compile `scripts/chuhaijiang_creative_search.py` with Python.
- Verify every request URL begins with `/api/v1/tools/research/` and authentication uses `NEXSCOPE_API_KEY` with Bearer authorization.
- Mock a successful Nexscope envelope, an outer nonzero code, HTTP 401, HTTP 402, malformed JSON, and a network timeout.
- Verify the response preserves `X-Cost-Token` and `X-Cost-Credit` as server-reported billing metadata without client-side conversion.
- Verify full responses are stored below `nexscope/<date>/<session>/data` and secrets are never written.
- Verify that no marketplace account or seller credential is requested.

## Live-test status

Not run during staging migration. A paid or credentialed call requires explicit approval. Record timestamp, environment, redacted request, HTTP status, outer code, business status, trace ID, `X-Cost-Token`, calculated credits, `X-Cost-Credit`, and saved response path when testing is approved.
