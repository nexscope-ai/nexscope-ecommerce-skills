# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Product Market Intelligence API Reference

## Request conventions

- **Endpoint (Product search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/search`
- **Endpoint (Product details)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/detail`
- **Endpoint (Related creators)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-creators`
- **Endpoint (Related livestreams)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-lives`
- **Endpoint (Product reviews)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/reviews`
- **Endpoint (Related videos)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-videos`
- **Endpoint (Most-promoted product ranking)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/most-promoted`
- **Endpoint (New-arrival product ranking)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/new-arrivals`
- **Endpoint (Top-selling product ranking)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/top-selling`
- **Endpoint (Image search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/image-search`
- **Image asset upload**: `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/presign` → presigned HTTPS `PUT` → `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/confirm`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; prefer reading api_key from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings if unset)
- **Timeout**: 150s

> If `${NEXSCOPE_PROXY_BASE}` is unset, the script falls back to `https://api.nexscope.ai`. The conventions above apply only to product research gateway POST requests; image uploads use the Skill Asset presign, external HTTPS PUT, and confirm workflow. External PUT requests do not carry the Nexscope API Key or forwarded headers.

## Entry scripts and consumption

| Capability | Script | Nexscope billing |
|---|---|---:|
| Product search | `chuhaijiang_product_search.py` | Response-header billing |
| Product details | `chuhaijiang_product_detail.py` | Response-header billing |
| Related creators | `chuhaijiang_product_related_creators.py` | Response-header billing |
| Related livestreams | `chuhaijiang_product_related_lives.py` | Response-header billing |
| Product reviews | `chuhaijiang_product_reviews.py` | Response-header billing |
| Related videos | `chuhaijiang_product_related_videos.py` | Response-header billing |
| Most-promoted product ranking | `chuhaijiang_product_rank_most_promoted.py` | Response-header billing |
| New-arrival product ranking | `chuhaijiang_product_rank_new_arrivals.py` | Response-header billing |
| Top-selling product ranking | `chuhaijiang_product_rank_top_selling.py` | Response-header billing |
| Image search | `chuhaijiang_product_image_search.py` | Response-header billing |
| Upload presigning | `upload_image.py` | Response-header billing |

## Common conventions

- Gateway/MCP request parameters use camelCase; do not use internal upstream snake_case fields as script parameters.

### Common request parameters

Except for image search and upload presigning, product endpoints use the common fields below. Each endpoint accepts only fields listed in its request table.

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Lowercase country code: `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `page` | integer | No | - | Page number, minimum 1; not used by the detail endpoint |
| `pageSize` | integer | No | - | Search/related data: maximum 10; rankings: 1–20; not used by the detail endpoint |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

### Common response envelope

In the complete real end-to-end verification on 2026-08-29, all 10 product business endpoints returned successful provider responses under the historical contract, and the external PUT after upload presigning returned HTTP 200; product details returned `data.items`, `data.core.items`, and `data.channel.items` together. The following business fields are inside platform `data`:

| Field | Type | Description |
|---|---|---|
| `request_id` | string | Request trace ID |
| `data` | object | Endpoint business data; the shape varies by endpoint |

The 10 product business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making a new paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may incur another charge; use it only when the user explicitly agrees to additional consumption or when debugging. Upload presigning and external PUT requests do not use response caching.

### Pagination and monetary value types

- Search and related-data endpoints allow `pageSize` up to 10; ranking endpoints allow 1–20.
- Monetary fields usually have the form `{ "unit": "US", "value": 31 }`, but some ranking fields return numbers directly.
- The same `interval_gmv` field may be a number or an object in different rankings. Check the runtime type before parsing; display objects using their original `unit` and `value`, and numbers as returned, without converting them yourself.

## Product search

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/search`
- **Script**: `chuhaijiang_product_search.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

### Request parameters

Inherits the common fields `country`, `page`, and `pageSize`, and also supports:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `keyword` | string | No | Search keyword |
| `category` | string | No | Product category ID |
| `sellerType` | string | No | `1`=overseas non-brand, `2`=local, `3`=brand, `4`=non-brand |
| `minPrice` / `maxPrice` | number | No | Minimum/maximum price (USD) |
| `minRating` / `maxRating` | number | No | Rating range, 0–5 |
| `minSold7d` / `maxSold7d` | number | No | 7-day sales range |
| `minSold30d` / `maxSold30d` | number | No | 30-day sales range |
| `freeShipping` | boolean | No | Whether shipping is free |
| `sort` | string | No | `field:asc` or `field:desc`; fields: `daily_sold`, `gmv_30d`, `gmv_7d`, `price`, `rating`, `sold_30d`, `sold_7d`; default `gmv_7d:desc` |

### Usage examples

```bash
python scripts/chuhaijiang_product_search.py '{"country":"us","keyword":"beauty","minRating":4,"freeShipping":true,"pageSize":5}'
```

## Product details

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/detail`
- **Script**: `chuhaijiang_product_detail.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: Basic information is in `data.items[]`; optional metrics are in `data.core.items[]` and `data.channel.items[]`

### Request parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Product ID |
| `include` | string | No | `channel` or `core`; separate multiple values with ASCII commas |

### Usage examples

```bash
python scripts/chuhaijiang_product_detail.py '{"country":"us","id":"1732052189676081387","include":"core,channel"}'
```

## Product related data

### Shared request fields

Related creators, related livestreams, product reviews, and related videos share the following request structure:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Product ID |
| `page` | integer | No | Minimum 1 |
| `pageSize` | integer | No | Maximum 10 |

### Related creators

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-creators`
- **Script**: `chuhaijiang_product_related_creators.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_product_related_creators.py '{"country":"us","id":"1732052189676081387","page":1,"pageSize":10}'
```

### Related livestreams

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-lives`
- **Script**: `chuhaijiang_product_related_lives.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_product_related_lives.py '{"country":"us","id":"1732052189676081387","page":1,"pageSize":10}'
```

### Product reviews

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/reviews`
- **Script**: `chuhaijiang_product_reviews.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_product_reviews.py '{"country":"us","id":"1732052189676081387","page":1,"pageSize":10}'
```

### Related videos

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/related-videos`
- **Script**: `chuhaijiang_product_related_videos.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_product_related_videos.py '{"country":"us","id":"1732052189676081387","page":1,"pageSize":10}'
```

## Product rankings

### Shared request fields

All three rankings use the common fields `country`, `page`, and `pageSize`, with `pageSize` from 1–20. `sellerType` accepts `1`, `2`, `3`, or `4`.

### Most-promoted product ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/most-promoted`
- **Script**: `chuhaijiang_product_rank_most_promoted.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `date` | string | Yes | `YYYYMMDD` |
| `granularity` | string | Yes | `daily`, `weekly`, `monthly`, `0`, `1` or `2` |
| `category` | string | No | Product category |
| `sellerType` | string | No | `1`, `2`, `3` or `4` |
| `sort` | string | No | `interval_gmv`, `interval_sold_count`, `live_count`, `live_user_count`, `related_creator_count`, `video_play_count`; format: `field:asc` or `field:desc`, default `related_creator_count:desc` |

```bash
python scripts/chuhaijiang_product_rank_most_promoted.py '{"country":"us","date":"20260824","granularity":"daily","pageSize":10}'
```

### New-arrival product ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/new-arrivals`
- **Script**: `chuhaijiang_product_rank_new_arrivals.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `category` | string | No | Product category |
| `sellerType` | string | No | `1`, `2`, `3` or `4` |
| `listedFrom` / `listedTo` | string | No | Listing date range, `YYYYMMDD` |
| `productStatus` | string | No | `1`, `2`, `3` or `4` |
| `sort` | string | No | `gmv_3d`, `sold_count_3d`, `total_gmv`, `total_sold_count`; format: `field:asc` or `field:desc`, default `gmv_3d:desc` |

```bash
python scripts/chuhaijiang_product_rank_new_arrivals.py '{"country":"us","page":1,"pageSize":10}'
```

### Top-selling product ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/rankings/top-selling`
- **Script**: `chuhaijiang_product_rank_top_selling.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `date` | string | Yes | `YYYYMMDD` |
| `granularity` | string | Yes | `daily`, `weekly`, `monthly`, `0`, `1` or `2` |
| `category` | string | No | Product category |
| `sellerType` | string | No | `1`, `2`, `3` or `4` |
| `sort` | string | No | `gmv_growth_rate`, `interval_gmv`, `interval_sold_count`, `sold_count_growth_rate`, `total_gmv`, `total_sold_count`; format: `field:asc` or `field:desc`, default `interval_sold_count:desc` |

```bash
python scripts/chuhaijiang_product_rank_top_selling.py '{"country":"us","date":"20260824","granularity":"daily","pageSize":10}'
```

## Image search workflow

### Upload presigning

- **URL**: `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/presign` → presigned HTTPS `PUT` → `POST ${NEXSCOPE_PROXY_BASE}/api/skill-asset/confirm`
- **Script**: `upload_image.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `publicUrl` and `assetId` returned by confirm, plus the `ossKey` corresponding to the confirmed upload

Request parameters:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `fileName` | string | Yes | File name with extension; the helper script supports JPG/JPEG/PNG |

The helper script uses the Nexscope Skill Asset workflow to obtain a presigned URL, perform PUT, and confirm the asset. Use only the `publicUrl` from the confirm response, and never send `NEXSCOPE_API_KEY` to the presigned upload URL:

```bash
python scripts/upload_image.py /path/to/product.jpg
```

### External HTTP PUT

Send HTTP PUT only to the `putUrl` returned by presign, with image bytes as the body and `Content-Type` matching the image format. This PUT does not pass through `${NEXSCOPE_PROXY_BASE}` and does not carry the Nexscope API Key. After a successful PUT, call confirm; unconfirmed assets must not be used for image search.

On success, `upload_image.py` outputs only the confirmed public URL and safe asset metadata, never the presigned URL.

### Image search

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/image-search`
- **Script**: `chuhaijiang_product_image_search.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `osKey` | string | Yes | - | The `ossKey` returned after Skill Asset upload and confirmation |
| `country` | string | No | `US` | Uppercase two-letter country code |

```bash
python scripts/chuhaijiang_product_image_search.py '{"osKey":"returned-key","country":"US"}'
```

## Response structure and key fields

Except for product details and upload presigning, successful business data is usually in `data.items[]`, with the total count in `data.total_count`. Business object fields may be missing, be `null`, or expand as upstream adds fields; scripts preserve the complete original JSON, and callers should not discard unknown fields.

| Endpoint | Data path | Key fields for parsing and chained calls |
|---|---|---|
| Product search | `data.items[]` | `id` (used by detail and related-data endpoints), `product_name`, `product_images`, `floor_price`, `ceiling_price`, `product_rating`, `product_sold_count`, `product_gmv`, `seller_id`, `shop_name` |
| Product details | `data.items[]` | `id`, `product_id`, `product_name`, `product_images`, prices, ratings, SKUs, specifications, shop and seller information |
| Product details core metrics | `data.core.items[]` | `product_gmv`, `product_sold_count`, last 30-day metrics, advertising metrics, video metrics, and related creator/livestream/video counts |
| Product details channel metrics | `data.channel.items[]` | Last 30-day GMV and sales for video, livestream, product card, individual creator, and seller creator channels |
| Related creators | `data.items[]` | Creator `user_id`/`uid`/`unique_id`, nickname, follower count, engagement and view metrics, video/livestream GMV; contact fields may be missing |
| Related livestreams | `data.items[]` | `room_id`, title, livestream link, creator ID, start/end times, GMV, sales, and audience metrics |
| Product reviews | `data.items[]` | `review_id`, content, rating, publication time, images/media, and SKU information |
| Related videos | `data.items[]` | `video_id`, description, cover, share link, creator ID, views/likes/engagement metrics, and last 30-day GMV/sales |
| Most-promoted product ranking | `data.items[]` | `id`/`product_id`, product and shop information, period GMV/sales, livestream count, related creator count, and video views |
| New-arrival product ranking | `data.items[]` | `id`/`product_id`, product and shop information, cumulative and last 3/7-day GMV/sales, product status, and sales trends |
| Top-selling product ranking | `data.items[]` | `id`/`product_id`, product and shop information, period/cumulative GMV and sales, and their growth rates |
| Image search | `data.items[]` | `id`, `product_name`, `product_images`, prices, GMV, sales, category, and region |
| Skill Asset upload | confirm `data` | `publicUrl` is the confirmed public URL; `assetId` identifies the asset; the script also preserves the `ossKey` corresponding to the confirmed upload for image search |

For product details, do not read only `data.items`: when requesting `include=core,channel`, also parse `data.core.items` and `data.channel.items` separately. Never print, log, or persist the presigned `putUrl`. Check the actual JSON types before parsing nested objects and arrays.

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | Follow "Authentication and Nexscope billing errors" in `SKILL.md` |
| Insufficient consumption allowance/balance | Stop retrying and guide the user through authorization or adding credits |
| Parameter validation failed | Correct parameters according to `msg`; real requests with an invalid country code return this code |

## curl examples

### Product search

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/search" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","minRating":4,"pageSize":5}'
```

### Product details

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/products/detail" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"1732052189676081387"}'
```

### Image search

Prefer `python scripts/upload_image.py <local-image>` to keep presigned URLs out of terminal history. After the script returns `osKey`:

```bash
python scripts/chuhaijiang_product_image_search.py '{"osKey":"returned-key","country":"US"}'
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
