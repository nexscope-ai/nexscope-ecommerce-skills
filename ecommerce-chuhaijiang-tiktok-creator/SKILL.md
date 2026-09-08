---
name: ecommerce-chuhaijiang-tiktok-creator
description: Research public TikTok creators and commerce relationships through Chuhaijiang and NexScope.
---

# Chuhaijiang TikTok Creator Intelligence

## Scope

Creator search and detail, related livestreams, products and videos, agency rankings, commerce-creator rankings, and follower-growth rankings.

Public-market intelligence only. It does not authorize creator accounts or publish content.

Read [references/api.md](references/api.md) for the authoritative source-derived request and response contract.

## Operations

| Script | NexScope route |
|---|---|
| `chuhaijiang_creator_detail.py` | `POST /api/v1/tools/research/chuhaijiang/creators/detail` |
| `chuhaijiang_creator_rank_agencies.py` | `POST /api/v1/tools/research/chuhaijiang/creators/rankings/agencies` |
| `chuhaijiang_creator_rank_commercial.py` | `POST /api/v1/tools/research/chuhaijiang/creators/rankings/commercial` |
| `chuhaijiang_creator_rank_growth.py` | `POST /api/v1/tools/research/chuhaijiang/creators/rankings/growth` |
| `chuhaijiang_creator_related_lives.py` | `POST /api/v1/tools/research/chuhaijiang/creators/related-lives` |
| `chuhaijiang_creator_related_products.py` | `POST /api/v1/tools/research/chuhaijiang/creators/related-products` |
| `chuhaijiang_creator_related_videos.py` | `POST /api/v1/tools/research/chuhaijiang/creators/related-videos` |
| `chuhaijiang_creator_search.py` | `POST /api/v1/tools/research/chuhaijiang/creators/search` |

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
4. Run only the selected entry script, for example: `python scripts/chuhaijiang_creator_detail.py '<JSON parameters>' --no-cache` when the script supports that flag.
5. Preserve the full response under `nexscope/<date>/<session>/data`; return a concise summary and the saved path.
6. On an ambiguous timeout or upstream failure, do not retry automatically. Report the trace ID and reconcile state first.

## Output rules

- Distinguish the NexScope transport envelope from the nested business response.
- Report only returned facts. Preserve absent values as unknown and keep provider-specific metric definitions intact.
- Never expose API keys, provider tokens, presigned URL query strings, internal account records, or raw secrets.
- Do not submit feedback or make any unrelated external mutation unless the user explicitly requests it.


## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.
