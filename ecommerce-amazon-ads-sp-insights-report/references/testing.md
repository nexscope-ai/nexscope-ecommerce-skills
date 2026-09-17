# Testing ecommerce.amazon-ads-sp-insights-report

## Static and offline gates

- Compile `scripts/check_auth_dependency.py` with Python.
- Compile `scripts/get_sp_audience_report.py` with Python.
- Compile `scripts/get_sp_search_impression_share.py` with Python.
- Compile `scripts/reporting_v1_workflow.py` with Python.
- Verify every request URL begins with `/api/v1/tools/research/` and authentication uses `NEXSCOPE_API_KEY` with Bearer authorization.
- Mock a successful Nexscope envelope, an outer nonzero code, HTTP 401, HTTP 402, malformed JSON, and a network timeout.
- Verify the response preserves `X-Cost-Token` and `X-Cost-Credit` as server-reported billing metadata without client-side conversion.
- Verify full responses are stored below `nexscope/<date>/<session>/data` and secrets are never written.
- Mock an authorized profile selection, a missing Ads connection, and an ambiguous multi-profile selection.

## Live-test status

Not run during staging migration. A paid or credentialed call requires explicit approval. Record timestamp, environment, redacted request, HTTP status, outer code, business status, trace ID, `X-Cost-Token`, calculated credits, `X-Cost-Credit`, and saved response path when testing is approved.
