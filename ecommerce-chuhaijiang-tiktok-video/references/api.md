# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Video Market Intelligence API Reference

## Request Specification

- **Protocol**: HTTPS `POST`, JSON request body
- **Endpoints**:
  - `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/search`
  - `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/detail`
  - `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/related-products`
  - `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/reviews`
- **Gateway variable**: `NEXSCOPE_PROXY_BASE`; when unset, the scripts fall back to `https://api.nexscope.ai`
- **Authentication**: `Authorization: Bearer <api_key>`; read api_key from `NEXSCOPE_API_KEY` first
- **Fixed headers**: `Content-Type: application/json`, `User-Agent: Nexscope-Skill/1.0`
- **Pass-through headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME`
- **Timeout**: 150 seconds
- **Runtime**: Python 3.9+, standard library only

## Entry Scripts and Caching

| Capability | Script | Gateway Path |
|---|---|---|
| Video Search | `chuhaijiang_video_search.py` | `/api/v1/tools/research/chuhaijiang/videos/search` |
| Video Detail | `chuhaijiang_video_detail.py` | `/api/v1/tools/research/chuhaijiang/videos/detail` |
| Video Commerce Products | `chuhaijiang_video_related_products.py` | `/api/v1/tools/research/chuhaijiang/videos/related-products` |
| Video Reviews | `chuhaijiang_video_reviews.py` | `/api/v1/tools/research/chuhaijiang/videos/reviews` |

The four business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making another paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may consume credits again; use it only when the user explicitly agrees to the extra consumption or for debugging.

## Common Conventions

### Common Request Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase request context/site code: `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`; a returned row's `country_code` may differ, so preserve both separately |
| `page` | integer | Optional for search/related products/reviews | Page number, starting at 1 |
| `pageSize` | integer | Optional for search/related products/reviews | Items per page, maximum 10; verify with a small page before increasing as needed |
| `id` | string | Yes for detail/related products/reviews | 19-digit video ID; must be passed as a string |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

### Common Success Response

The outer success response verified in real calls is:

```json
{
  "data": {
    "total_count": 1,
    "items": []
  },
  "request_id": "uuid"
}
```

The row structure of `data.items` depends on the endpoint. `total_count` may exceed the current page length. Fields may be missing or `null`; do not fill them with zeros.

## Video Search

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/search`
- **Script**: `chuhaijiang_video_search.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

Gateway requests use camelCase; the Java service maps these to Chuhaijiang upstream snake_case. Request fields are:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `keyword` | string | No | Video description or related keywords |
| `category` | string | No | Video category; the Java contract provides no enum of valid values, so use only provider-approved categories |
| `isCommercial` | boolean | No | Whether it promotes products |
| `minViews` / `maxViews` | number | No | View count range |
| `minLikes` / `maxLikes` | number | No | Like count range |
| `minGmv30d` / `maxGmv30d` | number | No | 30-day GMV range |
| `minEngagement` / `maxEngagement` | number | No | Engagement rate range; the Java contract specifies neither units nor bounds. Preserve the provider's original definition without converting to percentages |
| `accountType` | integer | No | Account type; only `0`, `3`, and `4` are allowed |
| `sort` | string | No | `field:asc` or `field:desc`; default `views:desc` |
| `country` | string | Yes | Request context/site code |
| `page` | integer | No | Page number, starting at 1 |
| `pageSize` | integer | No | Items per page, maximum 10 |

The upstream aliases of these fields are `is_commercial`, `min_views`, `max_views`, `min_likes`, `max_likes`, `min_gmv_30d`, `max_gmv_30d`, `min_engagement`, `max_engagement`, `account_type`, and `page_size`, respectively. Skills must use the camelCase names in the table when calling the gateway.

The Java side does not define a `category` enum, business labels for `accountType`, or a complete sort-field enum beyond `views`. In real tests, arbitrary use of `beauty` or an author category label from a response row as `category` returned an upstream rejection with an upstream HTTP 502 / `BACKEND_ERROR` message. Do not guess category values or automatically retry with other values.

Send only filters explicitly requested by the user. Do not automatically broaden ranges, change keywords, or paginate because a result is empty.

Real differential verification covered a combined request with `isCommercial`, minimum and maximum views/likes/30-day GMV/engagement rate, `accountType=0`, and `sort=views:desc`. A separate `isCommercial=true` request returned product, 30-day sales, and GMV fields.

### Key Fields in Real Responses

| Field | Description |
|---|---|
| `id` | Video ID |
| `video_desc` / `share_url` | Copy and public link |
| `video_launch_time` / `video_duration` | Publication timestamp and duration |
| `author_id` / `author_unique_id` / `author_nickname` | Author identity |
| `country_code` / `account_type` | Region and account type of the returned row |
| `video_play_count` / `video_like_count` | Views and likes |
| `video_comment_count` / `video_share_count` / `video_collect_count` | Engagement counts |
| `video_engagement_rate` | Engagement rate as a decimal |
| `video_total_like_count_to_follower_count_ratio` | Likes-to-followers ratio |
| `video_30d_gpm` | 30-day GPM in `{unit,value}` format |
| `is_ad` / `is_aigc_video` | Ad and AIGC flags; fields may be missing |

```bash
python scripts/chuhaijiang_video_search.py '{"country":"us","keyword":"beauty","isCommercial":true,"sort":"views:desc","page":1,"pageSize":3}'
```

## Video Detail

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/detail`
- **Script**: `chuhaijiang_video_detail.py`
- **Success data**: `data.items[]`; `data.core.items[]` is also returned for `include=core`

### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase site code |
| `id` | string | Yes | Video ID |
| `include` | string | No | Use `core` to obtain standardized core performance fields |

The verified `data.items[0]` includes fields such as `video_cover`, `user_avatar`, `video_duration`, `unique_id`, `nickname`, `follower_count`, `had_product`, `has_comment`, `share_url`, `video_count`, `video_avg_play_count`, `video_avg_like_count`, and `author_avg_engagement_rate`.

`data.core.items[0]` contains `core_video_play_count`, `core_video_like_count`, `core_video_comment_count`, `core_video_share_count`, `core_video_collect_count`, `core_video_engagement_rate`, `core_video_like_play_ratio`, `core_video_30d_gpm`, and `core_country_code`.

```bash
python scripts/chuhaijiang_video_detail.py '{"country":"us","id":"6788833646091504902","include":"core"}'
```

## Video Commerce Products

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/related-products`
- **Script**: `chuhaijiang_video_related_products.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

Inherits `country`, `id`, `page`, and `pageSize`. Ordinary non-commerce videos can return platform `code: 0` with business `total_count=0` and empty `items`; this is a valid result.

Real non-empty responses include:

- Product: `tiktok_video_detail_product_id`, `tiktok_product_detail_product_name`, `tiktok_product_detail_product_rating`, categories, images, SKU, inventory, and status.
- Price: `tiktok_product_detail_floor_price` / `ceiling_price`; preserve `{unit,value}` for both.
- Commerce: `tiktok_product_detail_commission_rate`, `tiktok_video_detail_product_total_sold_count`, `tiktok_video_detail_product_total_gmv`.
- Video attribution: `tiktok_video_detail_video_id`, `tiktok_video_detail_video_30d_sold_count`, `tiktok_video_detail_video_30d_gmv`.

```bash
python scripts/chuhaijiang_video_related_products.py '{"country":"us","id":"7672655263672864013","page":1,"pageSize":3}'
```

## Video Reviews

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/reviews`
- **Script**: `chuhaijiang_video_reviews.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

Inherits `country`, `id`, `page`, and `pageSize`.

| Field | Description |
|---|---|
| `tiktok_video_detail_comment_id` | Comment ID |
| `tiktok_video_detail_comment_text` | Comment text |
| `tiktok_video_detail_comment_create_time` | Creation timestamp |
| `tiktok_video_detail_comment_like_count` | Like count |
| `tiktok_video_detail_comment_reply_count` | Reply count |
| `tiktok_video_detail_comment_unique_id` | Commenter handle |
| `tiktok_video_detail_comment_nickname` | Commenter nickname |
| `tiktok_video_detail_comment_user_avatar` | Avatar object in `{thumb_url,url}` format |
| `tiktok_video_detail_video_id` | Parent video ID |

```bash
python scripts/chuhaijiang_video_reviews.py '{"country":"us","id":"6788833646091504902","page":1,"pageSize":3}'
```

## Errors and Failure Detection

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

## Nexscope billing rules

| Capability | Nexscope billing |
|---|---:|
| Video Search | Consumes credits |
| Video Detail | Consumes credits |
| Video Commerce Products | Consumes credits |
| Video Reviews | Consumes credits |

## curl Examples

```bash
curl --request POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/search" \
  --header "Authorization: Bearer $NEXSCOPE_API_KEY" \
  --header "Content-Type: application/json" \
  --header "User-Agent: Nexscope-Skill/1.0" \
  --data '{"country":"us","keyword":"beauty","isCommercial":true,"sort":"views:desc","page":1,"pageSize":3}' \
  --max-time 150
```

```bash
curl --request POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/videos/detail" \
  --header "Authorization: Bearer $NEXSCOPE_API_KEY" \
  --header "Content-Type: application/json" \
  --header "User-Agent: Nexscope-Skill/1.0" \
  --data '{"country":"us","id":"6788833646091504902","include":"core"}' \
  --max-time 150
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
