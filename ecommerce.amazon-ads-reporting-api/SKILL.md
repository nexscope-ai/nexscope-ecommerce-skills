---
name: ecommerce.amazon-ads-reporting-api
version: 2.0.0
category: ecommerce
description: Create, poll, resume, download, and save Amazon Ads v3 reports.
---

# Amazon Ads Report

Create, poll, resume, download, and save Amazon Ads v3 reports.

The package preserves 1 Amazon-platform operations (1 read or connection operations and 0 mutations). It uses only `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Provider credentials, refresh, request signing, authorization state, upload locations, and document locations remain on the backend.

## Core Concepts

- Build a v3 report configuration from the bundled report-type catalog, then create, poll, resume, download, decode, and optionally save it.
- A report ID is the durable resume handle; a document location is represented only by a short-lived opaque backend token.
- Report creation, polling, and download use the Amazon Advertising API connection and never a Seller SP-API connection.

## Operation Catalog

The concise index below is generated from the same contract consumed by the runtime. See `references/api.md` for full request, validation, pagination, result, status, and example details, and `references/api.json` for the machine-readable contract.

### `get_report` - Get Report

- Request: `POST /reporting/reports`; access: `write`; execution: `specialized`.
- Required: `connectionId`.- Optional: `workspaceId`, `reportId`, `reportTypeId`, `adProduct`, `groupBy`, `columns`, `name`, `startDate`, `endDate`, `timeUnit`, `format`, `filters`, `configuration`, `timeoutSeconds`, `pollIntervalSeconds`, `outputFile`, `overwrite`.- Query: None; body: `name`, `startDate`, `endDate`, `configuration`.
- Constraints: `none`. 


## API Invocation

Ask for an owned `connectionId`, the intended account, marketplace, and region. `workspaceId` is optional: omit it when the API key is already bound to the workspace. Select an exact callable operation from `references/api.json`; do not invent paths or use a removed compatibility row. Run the relevant script from: `scripts/amazon_ads_report_workflow.py`.

Reads may follow a continuation token only when `fetchAll` is true and always stop at `maxPages`. Paginated reads expose stable execution metadata: `success`, `pagesFetched`, `truncated`, and `total` when the list field is known. Client-side ASIN/SKU filters additionally report `serverTotalBeforeClientFilter` and `clientSideFilters`.

Creating an Ads report job is a read-only data workflow and does not use the Ads entity write-preview route.

Ads report workflows accept resume IDs and validated polling timeouts. Download locations are replaced by opaque tokens; `outputFile` safely publishes at most 20 MiB and refuses overwrite unless `overwrite:true` is explicit.

## Authentication and Connection Lifecycle

- Set `NEXSCOPE_PROXY_BASE` to the approved gateway base and `NEXSCOPE_API_KEY` to the caller credential.
- Use the workspace resolved from the API key (or an explicit `workspaceId` override) and an owned `connectionId` to select the account. Do not ask for Ads access tokens, refresh tokens, OAuth client credentials, or signing secrets.
- If authorization is missing or expired, use the corresponding connection script to authorize or inspect status. Token persistence and refresh remain backend-owned.
- Billing or credit behavior is determined by the gateway contract; do not repeat legacy credit claims or onboarding instructions.

## Usage Examples

```bash
python scripts/amazon_ads_report_workflow.py '{"workspaceId":"user:42","connectionId":7,"startDate":"2026-07-01","endDate":"2026-07-31","reportTypeId":"spCampaigns","adProduct":"SPONSORED_PRODUCTS","groupBy":["campaign"],"columns":["campaignId","impressions","clicks"]}'
```

Examples use placeholders. Save the reportId whenever the workflow returns a pending result.

## Display Rules

1. Identify the selected account, marketplace, operation, and whether it is read-only or a mutation.
2. For a mutation, show the preview and wait. Never print or reuse a confirmation token outside the separate approved confirm call.
3. For pagination, show `pagesFetched`, `total` when known, `truncated`, and the continuation token only when another bounded call is required.
4. For client-side filters, show the provider count before filtering and the filters applied.
5. For a pending report or feed, preserve the returned resource ID and show the structured resume instruction.
6. For documents, show `outputFile`, byte count, content type, and decode/compression metadata when returned; never expose a provider download location.
7. Treat 401/403 as authentication or ownership failures, 429 as a bounded-backoff condition, and 5xx as a sanitized upstream failure. Ads report 425 recovery applies only to the Ads report workflow.

## Important Limitations

- Report creation may return a duplicate-report recovery response; resume with the returned reportId.
- No local HTTP listener is started; decoded bytes are returned safely or atomically written to outputFile.
- Provider rate limits vary by operation and account. Honor returned rate-limit metadata and `Retry-After`; do not hardcode a universal requests-per-second value.
- The gateway allowlists exact API families. An unsupported path is a contract error, not a reason to bypass the gateway.
- Official API names and versions are recorded in `references/api.md`; this package intentionally contains no direct external host URL.

## User Expression and Scenario Quick Reference

| Classification | Guidance |
|---|---|
| Applicable | Create, resume, or download an Ads v3 report |
| Not applicable | Campaign mutation or Seller reports |

When the request crosses package boundaries, use the aggregate package only if its catalog contains the exact operation; otherwise choose the narrower package.

## Privacy and Errors

Do not request, print, cache, or store provider credentials. Treat advertising account, campaign, targeting, metric, and report data as private. Scripts exit nonzero for HTTP, application, upstream, invalid JSON, and malformed response failures. See `references/testing.md` for executable prompts, expected routes, error cases, and evidence.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
