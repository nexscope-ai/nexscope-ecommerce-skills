# Sponsored Products Audience (Reporting API v1) Reference

## Request Conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazonAds/developerProxy`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; read `NEXSCOPE_API_KEY` first
- **User-Agent**: `Nexscope-Skill/1.0`
- **Timeout**: 150s for both gateway requests and report-part downloads
- **Default production gateway**: `https://api.nexscope.ai`
- **Amazon authentication**: The caller supplies only `profileId`; the backend selects the access token for that profile. Never include access tokens, refresh tokens, or LWA secrets in parameters
- **Upstream maturity**: Amazon currently marks Reporting API v1 as open beta. It may not be enabled for an account, and fields or rate limits may change; do not promise general-availability stability
- **Generation time**: Asynchronous reports usually take about 2–10 minutes, occasionally longer. If still pending after about 5 minutes, the script advises waiting

Entry script: `python scripts/get_sp_audience_report.py '<JSON parameters>' [--inline] [--no-cache]`

## Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `profileId` | integer/string | Yes | - | Positive integer; obtained from the Ads authorization Skill |
| `region` | string | Yes | - | `NA` / `EU` / `FE` |
| `startDate` | string | Yes in create mode | - | `YYYY-MM-DD` |
| `endDate` | string | Yes in create mode | - | `YYYY-MM-DD`; must not be later than today |
| `timeUnit` | string | No | `DAILY` | `DAILY` / `SUMMARY` |
| `detailLevel` | string | No | `ACCOUNT` | `ACCOUNT` / `CAMPAIGN` / `AD_GROUP` |
| `advertiserAccountId` | string | No | Automatically mapped | Ads v1 account ID; only for explicit recovery after mapping fails |
| `pollInterval` | integer | No | `60` | 5–300 seconds; official guidance recommends once per minute |
| `maxAttempts` | integer | No | `10` | 1–120 |
| `reportId` | string | No | - | When provided, skip account lookup and creation and use poll-only mode |

## Internal Ads v1 Request Workflow

All three steps use the same Nexscope `developerProxy`. v1 requests do not send `Amazon-Advertising-API-Scope`; the server uses `profileId` only to select the authorization record/token.

### 1. Map the Advertiser Account

`POST adsApi/v1/query/advertiserAccounts`

The script first queries global accounts, then uses the following non-global filter and follows `nextToken`, including when a page is empty but still returns a token:

```json
{"isGlobalAccountFilter":{"include":[false]}}
```

Match the current `profileId` against `alternateIds` to obtain a unique `advertiserAccountId`. Skip this step if `advertiserAccountId` is explicitly supplied.

### 2. Create the SP Audience Report

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
        "audienceSegment.id", "audienceSegment.name", "audienceSegment.type",
        "audienceSegment.classCode", "audienceSegment.source",
        "audienceSegmentCountry.code", "budgetCurrency.value",
        "metric.impressions", "metric.clicks",
        "metric.totalCost", "metric.purchases", "metric.sales", "metric.roas"
      ],
      "filter": {"on": {
        "field": "adProduct.value", "comparisonOperator": "EQUALS",
        "not": false, "values": ["SPONSORED_PRODUCTS"]
      }}
    }
  }]
}
```

`SUMMARY` replaces `date.value` with `dateRange.value`. `CAMPAIGN` adds `campaign.id/name`; `AD_GROUP` also adds `adGroup.id/name`. `budgetCurrency.value` is an officially required dependency of `metric.totalCost` and `metric.sales` and must not be removed.

### 3. Poll and Download

`POST adsApi/v1/retrieve/reports`

```json
{"reportIds":["REPORT_ID"]}
```

Statuses: `PENDING` / `PROCESSING` / `COMPLETED` / `FAILED`. The completed response may contain multiple `url` values in `completedReportParts[]`. The script downloads every part and supports plain CSV and gzip-compressed CSV. Presigned URLs are omitted from the final response.

## developerProxy Request Example

The script constructs the following request for each step:

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
  "reportKind": "audience",
  "profileId": 1234567890,
  "advertiserAccountId": "account-id",
  "totalRows": 42,
  "dataFiles": [{"part":1,"path":"C:/.../part-01.csv","rowCount":42}],
  "preview": [{"audienceSegment.name":"In-market ...","metric.impressions":"1000"}],
  "pollAttempts": 2,
  "elapsedSeconds": 60.2
}
```

`success=true` with `totalRows=0` is a valid empty report. Do not automatically change parameters and retry.

## Pending Response

```json
{
  "success": false,
  "status": "STILL_PROCESSING",
  "reportId": "report-id",
  "resumeHint": {"params": {
    "profileId": 1234567890, "region": "NA", "reportId": "report-id",
    "pollInterval": 60, "maxAttempts": 20
  }},
  "_cacheable": false
}
```

`STILL_PROCESSING` means the client wait window ended while Amazon is still generating the report; it is not a report failure. The response provides `message`, `resumeHint.mode=poll-only`, and resume parameters. Reuse the same `reportId` rather than creating a duplicate. Pending and failed responses are not written to the 24h cache.

## Error Handling

| Status/Error | Meaning | Recommendation |
|---|---|---|
| 400 | Invalid dates, field combination, or body | Inspect `details.body`, correct the request once, then call again |
| 401 | Invalid Nexscope key or Amazon token | For Nexscope 401, follow the Nexscope authentication guidance; for upstream 401, refresh Ads authorization |
| 402 | Nexscope balance/plan issue | Follow `../SKILL.md#authentication-and-safety` |
| 403 | Insufficient Amazon Ads v1 permissions | Check Ads API application/authorized-account permissions |
| 404 | reportId does not exist or is inaccessible | Do not automatically recreate the report; explain the issue to the user |
| 429 | Upstream rate limit | Respect Retry-After and reduce polling frequency; avoid rapid retries |
| `FAILED` | Amazon report generation failed | Forward failure details |

## Official References

- [Reporting API v1 overview](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/overview)
- [Reporting API v1 quickstart](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/quickstart)
- [Query advertiser accounts](https://advertising.amazon.com/API/docs/en-us/guides/account-management/query-advertiser-accounts)
- [Audience segment dimension](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/dimensions/audience/audience-segment)
- [Costs metrics: total cost](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/costs-and-fees/costs#total-cost)
- [Purchase metrics: sales and ROAS](https://advertising.amazon.com/API/docs/en-us/guides/reporting/ads-v1/metrics/amazon-retail-conversions/purchases#sales)

## Feedback API

This endpoint is separate from the tool gateway: `POST https://skill-api.nexscope.com/api/v1/public/feedback`。

```json
{"skillName":"ecommerce.amazon-ads-sp-insights-report","sentiment":"NEUTRAL","category":"SUGGESTION","content":"..."}
```
