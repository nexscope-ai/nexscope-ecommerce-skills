---
name: ecommerce-chuhaijiang-tiktok-shop
description: Research public TikTok Shop stores and related entities through Chuhaijiang and NexScope.
---

# Chuhaijiang TikTok Shop Intelligence

## Scope

Store search and detail, related creators, products and videos, store rankings, ratings, product counts, sales, and GMV.

Public-market intelligence only. It does not authorize or operate a TikTok Shop seller account.

Read [references/api.md](references/api.md) for the authoritative source-derived request and response contract.

## Operations

| Script | NexScope route |
|---|---|
| `chuhaijiang_seller_detail.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/detail` |
| `chuhaijiang_seller_rank_most_promoted.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/rankings/most-promoted` |
| `chuhaijiang_seller_rank_top_selling.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/rankings/top-selling` |
| `chuhaijiang_seller_related_creators.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/related-creators` |
| `chuhaijiang_seller_related_products.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/related-products` |
| `chuhaijiang_seller_related_videos.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/related-videos` |
| `chuhaijiang_seller_search.py` | `POST /api/v1/tools/research/chuhaijiang/sellers/search` |

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
4. Run only the selected entry script, for example: `python scripts/chuhaijiang_seller_detail.py '<JSON parameters>' --no-cache` when the script supports that flag.
5. Preserve the full response under `nexscope/<date>/<session>/data`; return a concise summary and the saved path.
6. On an ambiguous timeout or upstream failure, do not retry automatically. Report the trace ID and reconcile state first.

## Output rules

- Distinguish the NexScope transport envelope from the nested business response.
- Report only returned facts. Preserve absent values as unknown and keep provider-specific metric definitions intact.
- Never expose API keys, provider tokens, presigned URL query strings, internal account records, or raw secrets.
- Do not submit feedback or make any unrelated external mutation unless the user explicitly requests it.


## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.
