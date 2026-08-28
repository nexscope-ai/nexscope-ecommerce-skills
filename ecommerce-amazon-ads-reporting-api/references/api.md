# Amazon API reference

This package preserves 1 cataloged operations. Use `references/api.json` as the machine-readable contract and the scripts declared by `SKILL.md`. Provider credentials remain server-side.

## Invocation contract

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`.
- Supply `workspaceId` and an owned `connectionId`; never supply a provider token.
- Reads return provider data. Paginated reads also expose `success`, `total` when a result list is known, `pagesFetched`, and `truncated`.
- Ads report creation is a read-only asynchronous data workflow; it does not use entity write preview/confirm.
- HTTP 401/403 indicates authentication or ownership failure; 429 requires bounded backoff; 5xx is a sanitized upstream failure.
- Ads report downloads are decoded by the backend. `outputFile` is an optional safe local destination; no local HTTP listener is started.

## `get_report` - Get Report

- Provider request: `POST /reporting/reports`
- Gateway action: `ADS_REPORT_START -> ADS_REPORT_POLL -> ADS_REPORT_DOWNLOAD`
- Callable: `true`; execution mode: `specialized`; dedicated script: `scripts/amazon_ads_report_workflow.py`. 
- Source access: `write`; target mutation requiring confirmation: `false`. write means the provider uses HTTP POST to create a read-only report job; mutation is false, so no write confirmation is required.
- Required inputs: `connectionId`- Required input alternatives: `reportId` or `startDate` + `endDate` + `configuration` or `startDate` + `endDate` + `reportTypeId` + `adProduct` + `groupBy` + `columns`
- Optional inputs: `workspaceId`, `reportId`, `reportTypeId`, `adProduct`, `groupBy`, `columns`, `name`, `startDate`, `endDate`, `timeUnit`, `format`, `filters`, `configuration`, `timeoutSeconds`, `pollIntervalSeconds`, `outputFile`, `overwrite`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `name`, `startDate`, `endDate`, `configuration`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.createasyncreportrequest.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure.","425":"Recover a duplicate report ID when supplied and resume polling."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_ads_report_workflow.py '{"workspaceId":"user:42","connectionId":7,"startDate":"2026-07-01","endDate":"2026-07-31","reportTypeId":"spCampaigns","adProduct":"SPONSORED_PRODUCTS","groupBy":["campaign"],"columns":["campaignId","impressions","clicks"]}'`
