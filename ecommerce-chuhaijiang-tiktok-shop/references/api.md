# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Shop Intelligence API Reference

## Request conventions

- **Endpoint (Shop search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/search`
- **Endpoint (Shop details)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/detail`
- **Endpoint (Related creators)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-creators`
- **Endpoint (Related products)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-products`
- **Endpoint (Related videos)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-videos`
- **Endpoint (Most-promoted shop ranking)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/rankings/most-promoted`
- **Endpoint (Top-selling shop ranking)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/rankings/top-selling`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; prefer reading api_key from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings if unset)
- **Timeout**: 150s

If `${NEXSCOPE_PROXY_BASE}` is unset, the script falls back to `https://api.nexscope.ai`. All seven endpoints above are Nexscope gateway POST requests; the Feedback API and onboarding flow are separate from these shop endpoints.

## Entry scripts

| Capability | Script | Nexscope billing |
|---|---|---:|
| Shop search | `chuhaijiang_seller_search.py` | Response-header billing |
| Shop details | `chuhaijiang_seller_detail.py` | Response-header billing |
| Related creators | `chuhaijiang_seller_related_creators.py` | Response-header billing |
| Related products | `chuhaijiang_seller_related_products.py` | Response-header billing |
| Related videos | `chuhaijiang_seller_related_videos.py` | Response-header billing |
| Most-promoted shop ranking | `chuhaijiang_seller_rank_most_promoted.py` | Response-header billing |
| Top-selling shop ranking | `chuhaijiang_seller_rank_top_selling.py` | Response-header billing |

The seven business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making a new paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may incur another charge; use it only when the user explicitly agrees to additional consumption or when debugging.

## Common conventions

- Gateway/MCP request parameters use camelCase; the Java service maps them to upstream snake_case. Do not pass internal fields such as `page_size`, `seller_type`, or `shop_type` to scripts.
- Send and save IDs as JSON strings to prevent loss of precision for 64-bit identifiers in JavaScript or spreadsheet tools.
- Successful data fields may be missing, be `null`, or expand as upstream adds fields; entry scripts preserve the complete original JSON.
- Monetary values usually have the form `{ "unit": "US", "value": 31 }`. Parse according to the runtime type; do not convert values or change currencies yourself.

### Common request parameters

Search, related-data, and ranking endpoints use pagination fields; the detail endpoint does not. Each endpoint accepts only parameters listed in its own request table.

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Lowercase country code: `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `page` | integer | No | - | Page number, minimum 1 |
| `pageSize` | integer | No | - | Search/related data: maximum 10; rankings: 1–20 |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

### Common successful response

Historical calls on 2026-08-29 returned nonempty business data. The fields below describe the current business payload inside platform `data`:

| Field | Type | Description |
|---|---|---|
| `request_id` | string | Request trace ID |
| `data` | object | Endpoint business data |

On business success, `data.items[]` is the main list and `data.total_count` is the total count. Details may also return `data.core` and `data.channel`. Entry scripts preserve the complete original JSON without removing unknown business fields.

## Shop search

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/search`
- **Script**: `chuhaijiang_seller_search.py`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

### Request parameters

Inherits `country`, `page`, and `pageSize`, and also supports:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `keyword` | string | No | Shop search keyword |
| `category` | string | No | Product category ID |
| `sellerType` | string | No | Seller type; use type values supported by the service |
| `minRating` / `maxRating` | number | No | Shop rating range |
| `minSold7d` / `maxSold7d` | number | No | 7-day sales range |
| `minGmv7d` / `maxGmv7d` | number | No | 7-day GMV range |
| `sort` | string | No | `field:asc` or `field:desc`; the service default is `gmv_7d:desc`, verified with real calls |

```bash
python scripts/chuhaijiang_seller_search.py '{"country":"us","keyword":"beauty","minRating":4,"page":1,"pageSize":3,"sort":"gmv_7d:desc"}'
```

### response fields

The fields below come from real results; different shops may omit fields such as trends or business entities.

| Field | Type | Description |
|---|---|---|
| `id` | string | Shop ID, accepted by the detail and three related-data endpoints |
| `shop_name` | string | Shop name |
| `region` | string | Shop market |
| `shop_rating` | number | Shop rating |
| `shop_main_category` | string | Primary category ID |
| `shop_product_count` | integer | Product count |
| `shop_total_sold_count` | number | Cumulative sales |
| `shop_total_gmv` | object | Cumulative GMV, including `unit` and `value` |
| `shop_sold_count_for_last_7_days` | number | Sales in the last 7 days |
| `shop_gmv_for_last_7_days` | object | GMV in the last 7 days |
| `total_related_creator_count` | number | Cumulative related creator count |
| `seller_business_info` | array<string> | Merchant business entity information |
| `sold_count_trend` | array<object> | Sales trend points, including `timestamp` and `value` |

## Shop details

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/detail`
- **Script**: `chuhaijiang_seller_detail.py`
- **Basic data**: `data.items[]`
- **Optional core data**: `data.core.items[]`
- **Optional channel data**: `data.channel.items[]`

### Request parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Shop ID |
| `include` | string | No | `core`, `channel`, or both separated by an ASCII comma: `core,channel` / `channel,core` |

```bash
python scripts/chuhaijiang_seller_detail.py '{"country":"us","id":"7495205878591949358","include":"core,channel"}'
```

### Basic details `data.items[]`

| Field | Type | Description |
|---|---|---|
| `id` / `seller_id` | string | Shop ID |
| `shop_name` / `region` | string | Shop name and market |
| `shop_rating` | number | Shop rating |
| `shop_total_gmv` | object | Cumulative GMV |
| `shop_main_category` | string | Primary category ID |
| `business_info` | array<string> | Merchant business entity |
| `seller_avatar` | object | `thumb_url`、`url` |
| `create_time` / `last_update_time` | integer | Millisecond timestamps |
| `creator_user_id` / `creator_user_name` / `creator_nickname` | string | Identity of the account associated with the shop |
| `creator_role` | integer | Account role value |

### Core details `data.core.items[]`

`data.core.total_count` is the core detail record count; it was 1 in a real single-shop response.

Real responses include: `id`, `core_seller_id`, `core_region`, `core_seller_shop_product_count`, `core_seller_shop_total_product_count`, `core_shop_total_sold_count`, `core_seller_shop_total_gmv`, `core_seller_sold_count_for_last_30_days`, `core_seller_gmv_for_last_30_days`, `core_seller_total_related_creator_count`, `core_seller_total_related_live_creator_count`, `core_seller_total_related_video_creator_count`, `core_seller_total_related_shop_creator_count`.

### Channel details `data.channel.items[]`

`data.channel.total_count` is the channel detail record count; it was 1 in a real single-shop response.

Real responses include: `id`, `channel_seller_id`, `channel_seller_sold_count_for_last_30_days`, `channel_seller_gmv_for_last_30_days`, `channel_video_30d_sold_count`, `channel_video_30d_gmv`, `channel_live_30d_sold_count`, `channel_live_30d_gmv`, `channel_product_card_30d_sold_count`, `channel_product_card_30d_gmv`, `channel_personal_creator_30d_sold_count`, `channel_personal_creator_30d_gmv`, `channel_seller_creator_30d_sold_count`, `channel_seller_creator_30d_gmv`.

## Shop related data

### Shared request fields

Related creators, related products, and related videos share:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Shop ID |
| `page` | integer | No | Minimum 1 |
| `pageSize` | integer | No | Maximum 10 |

### Related creators

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-creators`
- **Script**: `chuhaijiang_seller_related_creators.py`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_seller_related_creators.py '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

Real creator rows contain the following fields:

- Identity: `id`, `tiktok_seller_detail_creator_user_id`, `tiktok_seller_detail_creator_unique_id`, `tiktok_seller_detail_creator_nickname`, `tiktok_seller_detail_creator_country_code`, `tiktok_seller_detail_creator_account_type`, `tiktok_seller_detail_creator_category_label`, `tiktok_seller_detail_creator_user_avatar`, `tiktok_seller_detail_creator_seller_id`, `tiktok_seller_detail_creator_youtube_channel_id`.
- Audience and engagement: `tiktok_seller_detail_creator_follower_count`, `tiktok_seller_detail_creator_total_favorited`, `tiktok_seller_detail_creator_video_count`, `tiktok_seller_detail_creator_related_total_video`, `tiktok_seller_detail_creator_author_avg_like_cnt`, `tiktok_seller_detail_creator_author_avg_play_cnt`, `tiktok_seller_detail_creator_author_total_play_cnt`, `tiktok_seller_detail_creator_author_avg_engagement_rate`.
- Commerce channels: `tiktok_seller_detail_creator_by_live`, `tiktok_seller_detail_creator_by_shop`, `tiktok_seller_detail_creator_by_video`.
- GMV：`tiktok_seller_detail_creator_video_7d_gmv`、`tiktok_seller_detail_creator_video_30d_gmv`、`tiktok_seller_detail_live_7d_gmv`、`tiktok_seller_detail_creator_live_30d_gmv`、`tiktok_seller_detail_total_video_live_7d_gmv`、`tiktok_seller_detail_creator_total_video_live_30d_gmv`。
- Contact information: `tiktok_seller_detail_creator_bio_email`, which may be empty or missing.

### Related products

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-products`
- **Script**: `chuhaijiang_seller_related_products.py`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_seller_related_products.py '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

Product rows contain:

- Identity and links: `id`, `tiktok_seller_product_product_id`, `tiktok_seller_product_product_name`, `tiktok_seller_detail_product_link`, `tiktok_seller_detail_product_detail_link`, `tiktok_seller_product_region`.
- Categories and status: `tiktok_seller_product_l1_category`, `tiktok_seller_product_l2_category`, `tiktok_seller_product_l3_category`, `tiktok_seller_product_product_status`, `tiktok_seller_product_create_time`.
- Performance: `tiktok_seller_product_product_sold_count`, `tiktok_seller_product_product_sold_count_for_last_7_days`, `tiktok_seller_product_product_gmv`, `tiktok_seller_product_product_gmv_for_last_7_days`, `tiktok_seller_product_product_rating`, `tiktok_seller_product_review_count`, `tiktok_seller_product_commission_rate`, `tiktok_seller_product_total_related_creator_count`, `tiktok_seller_product_total_related_video_count`.
- Prices and media: `tiktok_seller_product_floor_price`, `tiktok_seller_product_ceiling_price`, `tiktok_seller_product_product_images[]` (`thumb_url`, `url`).
- SKU: `tiktok_seller_product_product_skus[]` contains `sku_id`, `price`, `sku_sale_props[]`, `stock`, `sale_prop_value_ids`, `status`; `price` contains `original_price`, `original_price_value`, `real_price`, `discount`, `unit_price_desc`.
- Specifications: `tiktok_seller_product_product_sku_props[]` contains `prop_id`, `prop_name`, `has_image`, `sale_prop_values[]`; specification values contain `prop_value_id`, `prop_value`, `image`.

### Related videos

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/related-videos`
- **Script**: `chuhaijiang_seller_related_videos.py`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_seller_related_videos.py '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

Real video row fields: `id`, `tiktok_seller_detail_video_id`, `tiktok_seller_detail_video_seller_id`, `tiktok_seller_detail_video_desc`, `tiktok_seller_detail_video_launch_time`, `tiktok_seller_detail_video_duration`, `tiktok_seller_detail_cover_url`, `tiktok_seller_detail_share_url`, `tiktok_seller_detail_video_play_count`, `tiktok_seller_detail_video_30d_play_count`, `tiktok_seller_detail_video_like_count`, `tiktok_seller_detail_video_comment_count`, `tiktok_seller_detail_video_engagement_rate`, `tiktok_seller_detail_video_30d_sold_count`, `tiktok_seller_detail_video_30d_gmv`, `tiktok_seller_detail_is_ad`, `tiktok_seller_detail_video_ad_source`, `tiktok_seller_detail_is_aigc_video`, `tiktok_seller_detail_user_id`, `tiktok_seller_detail_user_unique_id`, `tiktok_seller_detail_user_nickname`, `tiktok_seller_detail_user_avatar`, `tiktok_seller_detail_follower_count`.

## Shop rankings

### Shared request fields

Both rankings use `country`, `date`, `granularity`, `page`, and `pageSize`, with `pageSize` from 1–20.

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `date` | string | Yes | `YYYYMMDD` |
| `granularity` | string | Yes | `daily`, `weekly`, `monthly`, `0`, `1` or `2` |
| `category` | string | No | Product category ID |
| `shopType` | string | No | Shop type: `1`, `2`, `3`, or `4` |
| `sort` | string | No | `field:asc` or `field:desc`; see below for defaults by endpoint |

### Most-promoted shop ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/rankings/most-promoted`
- **Script**: `chuhaijiang_seller_rank_most_promoted.py`
- **Default sort**: `related_creator_count:desc`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_seller_rank_most_promoted.py '{"country":"us","date":"20260824","granularity":"daily","page":1,"pageSize":10}'
```

Real row fields: `id`, `seller_id`, `shop_name`, `region`, `shop_rating`, `shop_product_count`, `seller_main_category`, `seller_business_info`, `seller_avatar`, `biz_type`, `interval_related_creator_count`, `interval_total_related_creator_count`, `interval_total_related_video_creator_count`, `interval_total_related_shop_creator_count`, `interval_total_related_videos_count`.

### Top-selling shop ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/rankings/top-selling`
- **Script**: `chuhaijiang_seller_rank_top_selling.py`
- **Default sort**: `interval_sold_count:desc`
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_seller_rank_top_selling.py '{"country":"us","date":"20260824","granularity":"daily","page":1,"pageSize":10}'
```

Real row fields: `id`, `seller_id`, `shop_name`, `region`, `shop_rating`, `shop_product_count`, `seller_main_category`, `seller_business_info`, `seller_avatar`, `biz_type`, `interval_sold_count`, `interval_total_sold_count`, `interval_sold_count_growth_rate`, `interval_gmv`, `interval_total_gmv`, `interval_gmv_pop_growth_rate`, `interval_related_creator_count`, `interval_total_related_creator_count`.

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | Follow "Authentication and Nexscope billing errors" in `SKILL.md` |
| Insufficient consumption allowance/balance | Stop retrying and guide the user through authorization or adding credits |
| Parameter validation failed | Correct parameters according to `msg`; real requests with an invalid country code return this code |

Entry scripts save and echo HTTP or business errors without caching failed results. Parameter errors do not trigger automatic retries with changed criteria.

## curl examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/sellers/search" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","minRating":4,"pageSize":3,"sort":"gmv_7d:desc"}'
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
