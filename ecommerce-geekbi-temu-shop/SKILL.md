---
name: ecommerce-geekbi-temu-shop
description: Search and benchmark public Temu shops through GeekBI and NexScope.
---

# GeekBI Temu Shop Intelligence

## Scope

Shop discovery and comparison using average order value, active products, followers, product count, sales, revenue, and daily, weekly, or monthly changes.

Public-market research only. It does not authorize or operate a Temu seller account.

Read [references/api.md](references/api.md) for the authoritative source-derived request and response contract.

## Operations

| Script | NexScope route |
|---|---|
| `geekbi_temu_category_list.py` | `POST /api/v1/tools/research/geekbi/temu/categoryList` |
| `geekbi_temu_mall_search.py` | `POST /api/v1/tools/research/geekbi/temu/mallSearch` |
| `geekbi_temu_site_list.py` | `POST /api/v1/tools/research/geekbi/temu/siteList` |

## Authentication and safety

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Send the NexScope key as `Authorization: Bearer <key>`.
- No marketplace account authorization is required; these operations read public-market data.
- Provider credentials and upstream tokens remain backend-owned. Never accept, print, or persist them.
- Treat HTTP 401 as NexScope authentication failure and HTTP 402 as insufficient NexScope credits.
- Do not substitute another account, market, region, creator, product, or operation after an authorization or ambiguous network failure.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata.

## Workflow

1. Identify the exact operation, market/account context, filters, dates, pagination, and requested output.
2. Validate required fields, types, enums, ranges, and operation-specific limits against `references/api.md` before any request.
3. Explain that additional pages, markets, or operations may consume more credits and obtain approval before a paid call.
4. Run only the selected entry script, for example: `python scripts/geekbi_temu_category_list.py '<JSON parameters>' --no-cache` when the script supports that flag.
5. Preserve the full response under `nexscope/<date>/<session>/data`; return a concise summary and the saved path.
6. On an ambiguous timeout or upstream failure, do not retry automatically. Report the trace ID and reconcile state first.

## Output rules

- Distinguish the NexScope transport envelope from the nested business response.
- Report only returned facts. Preserve absent values as unknown and keep provider-specific metric definitions intact.
- Never expose API keys, provider tokens, presigned URL query strings, internal account records, or raw secrets.
- Do not submit feedback or make any unrelated external mutation unless the user explicitly requests it.


## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.
