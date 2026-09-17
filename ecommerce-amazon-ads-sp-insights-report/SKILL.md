---
name: ecommerce.amazon-ads-sp-insights-report
version: 1.0.1
category: ecommerce
description: Retrieve Amazon Ads Sponsored Products audience and search-term impression-share reports through Nexscope.
---

# Amazon Ads Sponsored Products Insights Reports

## Scope

Amazon Ads Reporting API v1 beta audience performance and search-term impression share/rank reports, including advertiser-account mapping, report creation, polling, and multipart CSV download.

Requires an existing Amazon Ads connection through ecommerce.amazon-ads-api-access. It does not replace ordinary SP search-term performance, Sponsored Brands, Sponsored Display, or DSP reporting.

Read [references/api.md](references/api.md) for the authoritative contract and `references/api.json` for the machine-readable operation catalog.

## Operations

| Script | Nexscope route |
|---|---|
| `get_sp_audience_report.py` | `POST /api/v1/tools/research/amazonAds/developerProxy` |
| `get_sp_search_impression_share.py` | `POST /api/v1/tools/research/amazonAds/developerProxy` |

## Response handling

For the research HTTP response, require a numeric outer `code` equal to `0` before using `data`. Nonzero codes are platform failures; display outer `msg` without interpreting its wording as a retry instruction. Nexscope preserves upstream messages and translates Chinese to English; successful responses may have `msg: null`. HTTP 200 alone and nested business `code` / `status` do not replace the platform check. See `references/api.md` for response paths and task-specific states.

Package scripts that unwrap the response keep the platform `code` and `msg` under `_nexscope`; their remaining fields are the business payload. `_nexscope.cost` is elapsed time, not credits.

## Authentication and safety

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Send the Nexscope key as `Authorization: Bearer <key>`.
- This skill requires `ecommerce.amazon-ads-api-access` and an authorized Amazon Ads connection. Resolve the intended profile before requesting a report; never accept Amazon access or refresh tokens.
- Follow the online Ads packages' connection lifecycle: authorization state, OAuth exchange, encrypted credentials, token refresh, profile discovery, and provider request signing remain backend-owned.
- The allowlisted v1 beta operations still use the dedicated Nexscope `developerProxy`; do not substitute direct Amazon endpoints or the v3 reporting workflow.
- Provider credentials and upstream tokens remain backend-owned. Never accept, print, or persist them.
- Treat HTTP 401 as Nexscope authentication failure and HTTP 402 as insufficient Nexscope credits.
- Do not substitute another account, market, region, creator, product, or operation after an authorization or ambiguous network failure.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata.

## Workflow

1. Identify the exact operation, market/account context, filters, dates, pagination, and requested output.
2. Validate required fields, types, enums, ranges, and operation-specific limits against `references/api.md` before any request.
3. Explain that additional pages, markets, or operations may consume more credits and obtain approval before a paid call.
4. Run only the selected entry script, for example: `python scripts/get_sp_audience_report.py '<JSON parameters>' --no-cache` when the script supports that flag.
5. Preserve the full response under `nexscope/<date>/<session>/data`; return a concise summary and the saved path.
6. On an ambiguous timeout or upstream failure, do not retry automatically. Report the trace ID and reconcile state first.

## Output rules

- Distinguish the Nexscope transport envelope from the nested business response.
- Report only returned facts. Preserve absent values as unknown and keep provider-specific metric definitions intact.
- Never expose API keys, provider tokens, presigned URL query strings, internal account records, or raw secrets.
- Do not submit feedback or make any unrelated external mutation unless the user explicitly requests it.


## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.
