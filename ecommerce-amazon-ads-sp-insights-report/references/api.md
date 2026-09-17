# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# Amazon Ads SP Insights Reports API Reference

This Skill combines Sponsored Products Audience and Search Term Impression Share/Rank reports from Reporting API v1 beta.

## Request Conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazonAds/developerProxy`
- **Method**: POST JSON
- **Authentication**: Header `Authorization: Bearer <api_key>`; read `NEXSCOPE_API_KEY` first
- **Headers**: `Content-Type: application/json`, `User-Agent: Nexscope-Skill/1.0`; forward `SESSION_ID` / `MODE_ID` / `APP_NAME`
- **Timeout**: 150 seconds for both gateway requests and report-part downloads
- **Default gateway**: `https://api.nexscope.ai`
- **Amazon token**: The caller supplies only `profileId`; the backend selects and refreshes the token. Never pass Amazon credentials in parameters
- **Maturity**: Reporting API v1 is currently in Amazon open beta
- **Generation time**: Asynchronous reports usually take about 2–10 minutes, occasionally longer. The script emits progress about every 5 minutes; reaching the client wait limit does not mean the report failed

## Entry Points and Parameters

| Report | Entry Point | Dedicated Reference |
|---|---|---|
| Sponsored Products Audience | `scripts/get_sp_audience_report.py` | `sp-audience-reporting-v1.md` |
| Sponsored Products Search Term Impression Share/Rank | `scripts/get_sp_search_impression_share.py` | `sp-search-impression-share-v1.md` |

Shared parameters: `profileId`, `region`, `startDate`, `endDate`, `timeUnit`, `advertiserAccountId`, `pollInterval`, `maxAttempts`, `reportId`. Audience also accepts `detailLevel`; Search Impression Share does not accept custom dimensions or fields.

## Internal Request Workflow

All three paths are forwarded through the same Nexscope `developerProxy`:

1. `POST adsApi/v1/query/advertiserAccounts`: Map `profileId` to a unique `advertiserAccountId`.
2. `POST adsApi/v1/create/reports`: Create a CSV report using a fixed combination of official fields.
3. `POST adsApi/v1/retrieve/reports`: Query status by `reportId`; download all `completedReportParts[]` when complete.

Ads v1 requests do not send `Amazon-Advertising-API-Scope`; the backend uses `profileId` only to select the current user's authorized token.

## developerProxy Request Example

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazonAds/developerProxy" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -d '{
    "region":"NA",
    "path":"adsApi/v1/retrieve/reports",
    "method":"POST",
    "profileId":1234567890,
    "body":"{\"reportIds\":[\"REPORT_ID\"]}",
    "contentType":"application/json"
  }'
```

Prefer the entry scripts for business requests instead of assembling the three stages manually.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Successful Response

```json
{
  "success": true,
  "status": "COMPLETED",
  "reportId": "report-id",
  "reportKind": "audience",
  "profileId": 1234567890,
  "advertiserAccountId": "account-id",
  "totalRows": 42,
  "dataFiles": [{"part":1,"path":"C:/.../part-01.csv","rowCount":42}],
  "preview": [{"audienceSegment.name":"In-market ..."}],
  "pollAttempts": 2,
  "elapsedSeconds": 60.2
}
```

`reportKind` is `audience` or `search-impression-share`. A response with `success=true` and `totalRows=0` is a valid empty report.

## Pending Reports and Caching

When the polling window expires, the response includes `status=STILL_PROCESSING`, `message`, `reportId`, `resumeHint.mode=poll-only`, `resumeHint.params`, and `_cacheable=false`. Amazon is still generating the report; this is not a report failure. Resume with the same `reportId` rather than creating a duplicate. Failed and pending results are not cached. Successful results are cached for 24 hours, with checks that `dataFiles[].path` still exists. Caches are isolated by `SESSION_ID`, report type, and parameters; `--no-cache` forces a refresh.

## Errors

| Status/Error | Meaning | Action |
|---|---|---|
| 400 | Invalid dates, field combination, or request body | Inspect `details`, correct the request once, then call again |
| 401 | Invalid Nexscope API key or Amazon token | For Nexscope 401, follow the Nexscope authentication guidance; for Amazon 401, refresh Ads authorization |
| 402 | Nexscope plan or balance issue | Follow `../SKILL.md#authentication-and-safety` |
| 403 | v1 access is not enabled | Check Amazon Ads application and authorized-account permissions |
| 404 | reportId does not exist or is inaccessible | Do not automatically recreate the report |
| 429 | Amazon rate limit | Reduce polling frequency; avoid rapid retries |
| `FAILED` | Report generation failed | Forward failure details |
| exit 42 | Ads Auth Skill is not installed | Install `ecommerce.amazon-ads-api-access` |
