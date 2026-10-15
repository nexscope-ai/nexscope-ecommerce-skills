# Existing Nexscope APIs used by this expert

Base: `NEXSCOPE_PROXY_BASE` (default `https://api.nexscope.ai`). Authentication: `Authorization: Bearer ${NEXSCOPE_API_KEY}`. Every business query consumes credits. No extra seller account or browser plugin is required for these public research capabilities. HTTP 401 is Nexscope authentication failure; 402 is insufficient credits. Keep market/account selection on authorization errors. Never repeat an ambiguous call automatically.

The CLI sends POST JSON to `/api/skill-api/v1/skills/{slug}/run`. Existing `/api/v1/tools/research/` compatibility routes remain available; this expert adds no new API.

## Per-API credit references

This expert has no separate fixed workflow charge. Show the APIs selected for the user's plan and their current credit references before execution. The following references were reviewed on 2026-10-14. Sample-based values use the raw tokens shown in the test operations diagnostics and the production coefficient; untested discovery/fallback operations retain existing production catalog references. These are display estimates, not guaranteed charges. Production uses coefficient 0.001041; test charges using 0.003 must not replace these references. The current billable-call minimum is 10 credits.

| Operation | Credits per API call (reference) |
|---|---:|
| keywords | 19 |
| summary | 19 |
| detail | 32 |
| reviews | 110 |
| competitors | 21 |
| related | 12 |
| aba | 13 (sample request; usage varies) |
| overview | 19 |
| fallback | 21 |
| search | 32 |

Each requested page and each child-ASIN request counts separately. Optional discovery, verification and ABA calls add only their own API charges. Local planning and HTML rendering make no API calls. Estimate the selected plan as the sum of each API's reference multiplied by its planned request count; never present that sum as a fixed expert fee. Actual request costs, cache rules and billing configuration prevail; check API usage records.

| CLI operation | Existing slug | Request essentials |
|---|---|---|
| keywords | amazon-asin-keywords | asin; country; timePieceType=latelyDay; timePieceValue="7" or "30"; pageNum/pageSize; optional keyword |
| summary | amazon-asin-traffic-summary | searchValue=ASIN; country; last7d; pageNum/pageSize; optional startDate/endDate |
| detail | amazon-product-detail | asins (comma-separated); amazonDomain (e.g. amazon.com) |
| reviews | amazon-reviews-list | asin; domainCode (e.g. com); star1Num through star5Num for sample sizes |
| competitors | amazon-competitor-lookup | marketplace; asinList or keyword; page/size |
| related | amazon-related-asins | asin; countryCode; page/pageSize |
| aba | amazon-keyword-intelligence | analysisDescription; region; createDownloadUrl=false |
| overview | amazon-keyword-overview | keyword; country; last7d; optional startDate/endDate |
| fallback | amazon-traffic-keywords | asin; marketplace; page/size; optional month/keyword |
| search | amazon-search | keyword; amazonDomain; page |

Use only fields supported by the current operation. Supplementary requests are agent-prepared JSON objects; inspect the current public definition before changing query semantics. Keywords support only one ASIN per request. Competitor discovery and optional evidence require separate approved calls.

```bash
python scripts/traffic_gap.py call keywords --params-file verify-keyword.json --out ./nexscope/traffic-gap-run
# Plan only. Add --execute only after the additional paid call is approved.
```

`verify-keyword.json`:

```json
{"asin":"B072MQ5BRX","country":"US","keyword":"phone case","timePieceType":"latelyDay","timePieceValue":"7","pageNum":1,"pageSize":50}
```

Successful platform envelope: `{"code":0,"msg":null,"data":{...},"ts":"...","time":"...","cost":"...","traceId":"..."}`. `cost` is elapsed milliseconds, not credits. Require HTTP success and numeric `code:0`. Business lists for the core Nexscope keyword and review operations are at platform `data.data`; source pagination metadata is alongside that list. The CLI saves the complete platform response and selected billing headers.

Do not infer complete pagination from `total` alone: it may describe returned rows. Stop when a valid `totalPage` is reached or an empty page is returned; an approved max-page limit may leave `complete=false`. Repeated pages stop as an error. Preserve source timestamp and period; unavailable fields stay unknown.

Important keyword fields: keyword, asin, productNaturalRank, productAdRank, weeklySearchVolume, naturalTrafficShare, paidTrafficShare, trafficShare, clickToPurchaseConversionRate, displayPositionTypes. Shares are ratios where 1=100%; ranks are lower-is-better. Nexscope traffic scores are exposure proxies. SB and SBV may overlap; do not double-count them. Review fields include reviewId/title/text/rating; use source excerpts and filenames to substantiate proposed benefits.
