---
name: ecommerce.chuhaijiang-tiktok-product
description: Research public TikTok Shop products and related market entities through Chuhaijiang and Nexscope.
---

# Chuhaijiang TikTok Product Intelligence

## Scope

Product search and detail, related creators, livestreams, videos and reviews, product rankings, and image-based similar-product discovery.

Public-market intelligence only. It does not access seller-console product management, orders, fulfillment, advertising accounts, or content publishing.

Read [references/api.md](references/api.md) for the authoritative source-derived request and response contract.

## Operations

| Script | Nexscope route |
|---|---|
| `chuhaijiang_product_detail.py` | `POST /api/v1/tools/research/chuhaijiang/products/detail` |
| `chuhaijiang_product_image_search.py` | `POST /api/v1/tools/research/chuhaijiang/products/image-search` |
| `chuhaijiang_product_rank_most_promoted.py` | `POST /api/v1/tools/research/chuhaijiang/products/rankings/most-promoted` |
| `chuhaijiang_product_rank_new_arrivals.py` | `POST /api/v1/tools/research/chuhaijiang/products/rankings/new-arrivals` |
| `chuhaijiang_product_rank_top_selling.py` | `POST /api/v1/tools/research/chuhaijiang/products/rankings/top-selling` |
| `chuhaijiang_product_related_creators.py` | `POST /api/v1/tools/research/chuhaijiang/products/related-creators` |
| `chuhaijiang_product_related_lives.py` | `POST /api/v1/tools/research/chuhaijiang/products/related-lives` |
| `chuhaijiang_product_related_videos.py` | `POST /api/v1/tools/research/chuhaijiang/products/related-videos` |
| `chuhaijiang_product_reviews.py` | `POST /api/v1/tools/research/chuhaijiang/products/reviews` |
| `chuhaijiang_product_search.py` | `POST /api/v1/tools/research/chuhaijiang/products/search` |
| `upload_image.py` | `POST /api/skill-asset/presign` → presigned `PUT` → `POST /api/skill-asset/confirm` |

## Response handling

For the research HTTP response, require a numeric outer `code` equal to `0` before using `data`. Nonzero codes are platform failures; display outer `msg` without interpreting its wording as a retry instruction. Nexscope preserves upstream messages and translates Chinese to English; successful responses may have `msg: null`. HTTP 200 alone and nested business `code` / `status` do not replace the platform check. See `references/api.md` for response paths and task-specific states.

Package scripts that unwrap the response keep the platform `code` and `msg` under `_nexscope`; their remaining fields are the business payload. `_nexscope.cost` is elapsed time, not credits.

## Authentication and safety

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Send the Nexscope key as `Authorization: Bearer <key>`.
- No marketplace account authorization is required; these operations read public-market data.
- Provider credentials and upstream tokens remain backend-owned. Never accept, print, or persist them.
- Treat HTTP 401 as Nexscope authentication failure and HTTP 402 as insufficient Nexscope credits.
- Do not substitute another account, market, region, creator, product, or operation after an authorization or ambiguous network failure.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata.

## Workflow

1. Identify the exact operation, market/account context, filters, dates, pagination, and requested output.
2. Validate required fields, types, enums, ranges, and operation-specific limits against `references/api.md` before any request.
3. Explain that additional pages, markets, or operations may consume more credits and obtain approval before a paid call.
4. Run only the selected entry script, for example: `python scripts/chuhaijiang_product_detail.py '<JSON parameters>' --no-cache` when the script supports that flag.
5. Preserve the full response under `nexscope/<date>/<session>/data`; return a concise summary and the saved path.
6. On an ambiguous timeout or upstream failure, do not retry automatically. Report the trace ID and reconcile state first.

## Output rules

- Distinguish the Nexscope transport envelope from the nested business response.
- Report only returned facts. Preserve absent values as unknown and keep provider-specific metric definitions intact.
- Never expose API keys, provider tokens, presigned URL query strings, internal account records, or raw secrets.
- Do not submit feedback or make any unrelated external mutation unless the user explicitly requests it.


## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
