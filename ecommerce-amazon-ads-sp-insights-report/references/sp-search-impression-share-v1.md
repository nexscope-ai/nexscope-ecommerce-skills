# Sponsored Products Search Term Impression Share (Reporting API v1) Reference

## Request Conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazonAds/developerProxy`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; read `NEXSCOPE_API_KEY` first
- **User-Agent**: `Nexscope-Skill/1.0`
- **Timeout**: 150s for both gateway requests and report-part downloads
- **Default production gateway**: `https://api.nexscope.ai`
- **Amazon authentication**: Supply only `profileId`; the backend selects the token. Never include access/refresh tokens in parameters
- **Upstream maturity**: Amazon currently marks Reporting API v1 as open beta. It may not be enabled for an account, and fields or rate limits may change; do not promise general-availability stability
- **Generation time**: Asynchronous reports usually take about 2–10 minutes; Search Impression Share can occasionally take longer. If still pending after about 5 minutes, the script advises waiting

Entry script: `python scripts/get_sp_search_impression_share.py '<JSON parameters>' [--inline] [--no-cache]`

## Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `profileId` | integer/string | Yes | - | Positive integer; obtained from the Ads authorization Skill |
| `region` | string | Yes | - | `NA` / `EU` / `FE` |
| `startDate` | string | Yes in create mode | - | `YYYY-MM-DD` |
| `endDate` | string | Yes in create mode | - | `YYYY-MM-DD`; must not be later than today |
| `timeUnit` | string | No | `DAILY` | `DAILY` / `SUMMARY` |
| `advertiserAccountId` | string | No | Automatically mapped | Ads v1 account ID; only for explicit recovery after mapping fails |
| `pollInterval` | integer | No | `60` | 5–300 seconds; official guidance recommends once per minute |
| `maxAttempts` | integer | No | `10` | 1–120 |
| `reportId` | string | No | - | When provided, skip account lookup and creation and use poll-only mode |

This report entry point does not accept custom dimensions such as campaign/adGroup/target/keyword because they conflict with the official field compatibility rules for impression share/rank.

## Internal Ads v1 Request Workflow

All requests are forwarded through `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazonAds/developerProxy`. Ads v1 does not send `Amazon-Advertising-API-Scope`; the backend uses `profileId` only to select the authorization record/token.

### 1. Map the Advertiser Account

`POST adsApi/v1/query/advertiserAccounts`

Query `{}` and then `{"isGlobalAccountFilter":{"include":[false]}}`, follow `nextToken`, and match the current profile against `alternateIds` to obtain a unique `advertiserAccountId`.

### 2. Create the SP Search Term Impression Share Report

`POST adsApi/v1/create/reports`

```json
{
  "accessRequestedAccounts": [{"advertiserAccountId": "ACCOUNT_ID"}],
  "reports": [{
    "format": "CSV",
    "periods": [{"datePeriod": {"startDate": "2026-08-01", "endDate": "2026-08-07"}}],
    "query": {
      "fields": [
        "date.value", "advertiserAccount.id", "adProduct.value",
        "searchTerm.value", "metric.impressionShare", "metric.impressionShareRank"
      ],
      "filter": {"on": {
        "field": "adProduct.value", "comparisonOperator": "EQUALS",
        "not": false, "values": ["SPONSORED_PRODUCTS"]
      }}
    }
  }]
}
```

`SUMMARY` replaces `date.value` with `dateRange.value`. The three non-time dimensions are officially required fields for impression share/rank and cannot be removed; campaign/ad group/target cannot be added either.

### 3. Poll and Download

`POST adsApi/v1/retrieve/reports`

```json
{"reportIds":["REPORT_ID"]}
```

Following official guidance, poll at most once per minute. After `COMPLETED`, download all `completedReportParts[].url` entries, supporting plain CSV and gzip-compressed CSV. Do not output presigned URLs.

## developerProxy Request Example

```json
{
  "region": "NA",
  "path": "adsApi/v1/create/reports",
  "method": "POST",
  "profileId": 1234567890,
  "body": "{...Amazon JSON body...}",
  "contentType": "application/json"
}
```

## Successful Response

```json
{
  "success": true,
  "status": "COMPLETED",
  "reportId": "report-id",
  "reportKind": "search-impression-share",
  "profileId": 1234567890,
  "advertiserAccountId": "account-id",
  "totalRows": 2,
  "dataFiles": [{"part":1,"path":"C:/.../part-01.csv","rowCount":2}],
  "preview": [{
    "searchTerm.value":"wireless charger",
    "metric.impressionShare":"0.34",
    "metric.impressionShareRank":"3"
  }]
}
```

`success=true` with `totalRows=0` is a valid empty report. Do not automatically widen the date range or switch accounts and retry.

## Pending Response

`status=STILL_PROCESSING` means the client wait window ended while Amazon is still generating the report; it is not a failure. The response includes `message`, `reportId`, `resumeHint.mode=poll-only`, and `resumeHint.params`. After user confirmation, use these parameters with `--no-cache` to resume polling the same report instead of creating a new one. Pending and failed responses are not cached.

## Error Handling

| Status/Error | Meaning | Recommendation |
|---|---|---|
| 400 | Invalid dates or field combination | Inspect `details.body`; do not add incompatible dimensions |
| 401 | Invalid Nexscope key or Amazon token | For Nexscope 401, follow the Nexscope authentication guidance; for upstream 401, refresh Ads authorization |
| 402 | Nexscope balance/plan issue | Follow `../SKILL.md#authentication-and-safety` |
| 403 | Insufficient Amazon Ads v1 permissions | Check Ads API application/authorized-account permissions |
| 404 | reportId does not exist or is inaccessible | Do not automatically recreate the report |
| 429 | Upstream rate limit | Reduce polling frequency; avoid rapid retries |
| `FAILED` | Amazon report generation failed | Forward failure details |

## Official References

- [Reporting API v1 overview](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/overview)
- [Reporting API v1 quickstart](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/quickstart)
- [Query advertiser accounts](https://advertising.amazon.com/API/docs/en-us/guides/account-management/query-advertiser-accounts)
- [Search term dimension](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/dimensions/targeting/search-term)
- [Search impression share metrics](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/impression-share/search)

## Feedback API

This endpoint is separate from the tool gateway: `POST https://skill-api.nexscope.com/api/v1/public/feedback`。

```json
{"skillName":"ecommerce.amazon-ads-sp-insights-report","sentiment":"NEUTRAL","category":"SUGGESTION","content":"..."}
```
