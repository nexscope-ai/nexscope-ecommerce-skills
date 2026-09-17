# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Creator Market Intelligence API Reference

## Request conventions

- **Gateway**: `${NEXSCOPE_PROXY_BASE}`; the script falls back to `https://api.nexscope.ai` if unset
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; prefer reading `NEXSCOPE_API_KEY`
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings if unset)
- **Timeout**: 150s
- **Parameter naming**: Gateway/MCP uses camelCase; do not use internal upstream snake_case fields as script parameters

## Entry scripts and consumption

| Capability | Endpoint | Script | Nexscope billing |
|---|---|---|---:|
| Creator search | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/search` | `chuhaijiang_creator_search.py` | Response-header billing |
| Creator details | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/detail` | `chuhaijiang_creator_detail.py` | Response-header billing |
| Related livestreams | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-lives` | `chuhaijiang_creator_related_lives.py` | Response-header billing |
| Promoted products | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-products` | `chuhaijiang_creator_related_products.py` | Response-header billing |
| Related videos | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-videos` | `chuhaijiang_creator_related_videos.py` | Response-header billing |
| Creator agency ranking | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/agencies` | `chuhaijiang_creator_rank_agencies.py` | Response-header billing |
| Commercial creator ranking | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/commercial` | `chuhaijiang_creator_rank_commercial.py` | Response-header billing |
| Creator follower-growth ranking | `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/growth` | `chuhaijiang_creator_rank_growth.py` | Response-header billing |

The eight business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making a new paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may incur another charge; use it only when the user explicitly agrees to additional consumption or when debugging.

## Common conventions

### Common request parameters

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

Successful gateway responses use the following top-level structure; business fields are in `data`:

| Field | Type | Description |
|---|---|---|
| `request_id` | string | Request trace ID |
| `data` | object | Endpoint business data; the shape varies by endpoint |

On a cache hit, the script prints `Cache hit`, but the returned and saved JSON retain the original response structure without injected local cache fields.

### Pagination and monetary value types

- Search and related-data endpoints allow `pageSize` up to 10; ranking endpoints allow 1–20.
- Monetary fields may be numbers or objects containing `unit` and `value`. Check the runtime type before parsing and preserve the original units; do not convert them yourself.

## Creator search

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/search`
- **Script**: `chuhaijiang_creator_search.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

### Request parameters

Inherits the common fields `country`, `page`, and `pageSize`, and also supports:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `keyword` | string | No | Search keyword |
| `category` | string | No | Creator category |
| `minFollowers` / `maxFollowers` | number | No | Follower count range |
| `minGmv30d` / `maxGmv30d` | number | No | 30-day GMV range |
| `minAvgViews` / `maxAvgViews` | number | No | Average view count range |
| `minEngagement` / `maxEngagement` | number | No | Engagement rate range |
| `hasContact` | boolean | No | Whether contact information is available |
| `sort` | string | No | `field:asc` or `field:desc`; default `gmv_30d:desc` |

### Usage examples

```bash
python scripts/chuhaijiang_creator_search.py '{"country":"us","keyword":"beauty","page":1,"pageSize":5}'
```

## Creator details

### Endpoint information

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/detail`
- **Script**: `chuhaijiang_creator_detail.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: Basic information is in `data.items[]`; optional metrics are in `data.core.items[]`, `data.channel.items[]`, and `data.portrait.items[]`

### Request parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Creator ID |
| `include` | string | No | `channel`, `core` or `portrait`; separate multiple values with ASCII commas |

### Usage examples

```bash
python scripts/chuhaijiang_creator_detail.py '{"country":"us","id":"7302162228386776110","include":"channel,core,portrait"}'
```

## Creator related data

### Shared request fields

Related livestreams, promoted products, and related videos share the following request structure:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Creator ID |
| `page` | integer | No | Minimum 1 |
| `pageSize` | integer | No | Maximum 10 |

### Related livestreams

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-lives`
- **Script**: `chuhaijiang_creator_related_lives.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_creator_related_lives.py '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

### Promoted products

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-products`
- **Script**: `chuhaijiang_creator_related_products.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_creator_related_products.py '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

### Related videos

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/related-videos`
- **Script**: `chuhaijiang_creator_related_videos.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

```bash
python scripts/chuhaijiang_creator_related_videos.py '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

## Creator rankings

### Shared request fields

All three rankings use the common fields `country`, `page`, and `pageSize`; `pageSize` is 1–20.

### Creator agency ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/agencies`
- **Script**: `chuhaijiang_creator_rank_agencies.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `category` | string | No | Agency category |
| `sort` | string | No | Sort order; default `gmv_30d:desc` |

```bash
python scripts/chuhaijiang_creator_rank_agencies.py '{"country":"us","page":1,"pageSize":10}'
```

### Commercial creator ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/commercial`
- **Script**: `chuhaijiang_creator_rank_commercial.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `date` | string | Yes | `YYYYMMDD` |
| `granularity` | string | Yes | `daily`, `weekly`, `monthly`, `0`, `1` or `2` |
| `creatorCategory` | string | No | Creator category |
| `productCategory` | string | No | Product category |
| `sort` | string | No | Sort order; default `total_gmv:desc` |

```bash
python scripts/chuhaijiang_creator_rank_commercial.py '{"country":"us","date":"20260828","granularity":"daily","pageSize":10}'
```

### Creator follower-growth ranking

- **URL**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/rankings/growth`
- **Script**: `chuhaijiang_creator_rank_growth.py`
- **Consumption**: Nexscope response-header billing
- **Successful data**: `data.items[]`; total count is in `data.total_count`

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `date` | string | Yes | `YYYYMMDD` |
| `granularity` | string | Yes | `daily`, `weekly`, `monthly`, `0`, `1` or `2` |
| `creatorCategory` | string | No | Creator category |
| `productCategory` | string | No | Product category |
| `sort` | string | No | Sort order; default `new_follower_count:desc` |

```bash
python scripts/chuhaijiang_creator_rank_growth.py '{"country":"us","date":"20260828","granularity":"daily","pageSize":10}'
```

## Response structure and key fields

The fields below come from real production responses on 2026-08-29. Search, related-data, and ranking endpoints use `data.items[]`, with the total count in `data.total_count`; detail extensions are in `data.core.items[]`, `data.channel.items[]`, and `data.portrait.items[]`, respectively.

### Creator search response fields

- **List item fields**: `account_type`, `author_avg_engagement_rate`, `bio_email`, `category_label`, `country_code`, `ecom_video_avg_play_count`, `facebook_url`, `follower_count`, `follower_count_growth_for_last_7_days`, `has_live_product`, `has_shop_product`, `has_video_product`, `id`, `ins_id`, `live_30d_gmv`, `live_30d_gpm`, `nickname`, `product_category_label_list`, `total_favorited`, `total_video_live_30d_gmv`, `unique_id`, `user_avatar`, `user_sell_product_l3_category`, `video_30d_gmv`, `video_30d_gpm`, `video_avg_like_count`, `video_avg_play_count`, `video_total_like_count_to_follower_count_ratio`, `youtube_channel_id`

Use `bio_email` and external social account fields only to determine the availability of public profile information; do not proactively display or aggregate contact information in results unless the user has an explicit, compliant business need.

### Creator details response fields

- **Basic profile `data.items[]`**: `bio_email`, `bio_url`, `category_label`, `enterprise_verify_reason`, `facebook_url`, `has_live_product`, `has_shop_product`, `has_video_product`, `id`, `ins_id`, `last_update_time`, `nickname`, `partnered_brand`, `product_category_label_list`, `signature`, `unique_id`, `user_avatar`, `youtube_channel_id`
- **Core metrics `data.core.items[]`**: `core_author_avg_engagement_rate`, `core_follower_count`, `core_product_count`, `core_total_favorited`, `core_uid`, `core_video_total_like_count_to_follower_count`, `id`, `tioktok_creator_detail_core_ec_video_count`, `tioktok_creator_detail_core_ecom_video_avg_play_count`, `tioktok_creator_detail_core_med_commission_rate`
- **Channel metrics `data.channel.items[]`**: `channel_country_code`, `channel_ec_video_30d_avg_engagement_rate`, `channel_ec_video_30d_avg_play_count`, `channel_live_30d_gmv`, `channel_live_30d_gpm`, `channel_total_video_live_30d_gmv`, `channel_uid`, `channel_video_30d_gmv`, `channel_video_30d_gpm`, `id`
- **Audience demographics `data.portrait.items[]`**: `id`, `portrait_age_distribution`, `portrait_follower_count`, `portrait_gender_distribution`, `portrait_region_distribution`, `portrait_uid`

Actual upstream field names include the spelling `tioktok_*`; read them exactly as returned and do not change them to `tiktok_*`.

### Related livestreams response fields

- **List item fields**: `id`, `tiktok_creator_detail_live_country_code`, `tiktok_creator_detail_live_cover`, `tiktok_creator_detail_live_end_time`, `tiktok_creator_detail_live_gmv`, `tiktok_creator_detail_live_gpm`, `tiktok_creator_detail_live_max_user_count`, `tiktok_creator_detail_live_most_product_category_label`, `tiktok_creator_detail_live_new_follow_count`, `tiktok_creator_detail_live_opm`, `tiktok_creator_detail_live_product_count`, `tiktok_creator_detail_live_room_id`, `tiktok_creator_detail_live_room_link`, `tiktok_creator_detail_live_start_time`, `tiktok_creator_detail_live_title`, `tiktok_creator_detail_live_total_sold_count`, `tiktok_creator_detail_live_total_user`, `tiktok_creator_detail_live_user_follower_count`

### Promoted products response fields

- **List item fields**: `id`, `tiktok_creator_detail_by_live`, `tiktok_creator_detail_by_shop`, `tiktok_creator_detail_by_video`, `tiktok_creator_detail_live_30d_gmv`, `tiktok_creator_detail_live_30d_sold_count`, `tiktok_creator_detail_product_country_code`, `tiktok_creator_detail_product_id`, `tiktok_creator_detail_product_launch_time`, `tiktok_creator_detail_total_video_live_30d_gmv`, `tiktok_creator_detail_total_video_live_30d_sold_count`, `tiktok_creator_detail_user_id`, `tiktok_creator_detail_video_30d_gmv`, `tiktok_creator_detail_video_30d_sold_count`, `tiktok_product_detail_ceiling_price`, `tiktok_product_detail_commission_rate`, `tiktok_product_detail_floor_price`, `tiktok_product_detail_l1_category`, `tiktok_product_detail_l2_category`, `tiktok_product_detail_l3_category`, `tiktok_product_detail_product_images`, `tiktok_product_detail_product_name`, `tiktok_product_detail_product_rating`, `tiktok_product_detail_product_sku_props`, `tiktok_product_detail_product_skus`, `tiktok_product_detail_product_status`, `tiktok_product_detail_region`

### Related videos response fields

- **List item fields**: `id`, `tiktok_creator_detail_is_ad`, `tiktok_creator_detail_is_aigc_video`, `tiktok_creator_detail_video_30d_gmv`, `tiktok_creator_detail_video_30d_sold_count`, `tiktok_creator_detail_video_ad_source`, `tiktok_creator_detail_video_author_category_label`, `tiktok_creator_detail_video_author_nickname`, `tiktok_creator_detail_video_author_uid`, `tiktok_creator_detail_video_author_unique_id`, `tiktok_creator_detail_video_collect_count`, `tiktok_creator_detail_video_comment_count`, `tiktok_creator_detail_video_country_code`, `tiktok_creator_detail_video_cover`, `tiktok_creator_detail_video_desc`, `tiktok_creator_detail_video_duration`, `tiktok_creator_detail_video_engagement_rate`, `tiktok_creator_detail_video_id`, `tiktok_creator_detail_video_launch_time`, `tiktok_creator_detail_video_like_count`, `tiktok_creator_detail_video_play_count`, `tiktok_creator_detail_video_product_id`, `tiktok_creator_detail_video_product_images`, `tiktok_creator_detail_video_product_l1_category`, `tiktok_creator_detail_video_product_l2_category`, `tiktok_creator_detail_video_product_l3_category`, `tiktok_creator_detail_video_product_title`, `tiktok_creator_detail_video_share_count`, `tiktok_creator_detail_video_share_url`, `tiktok_creator_detail_video_total_like_count_to_follower_count_ratio`, `tiktok_creator_detail_video_user_avatar`

### Creator agency ranking response fields

- **List item fields**: `avg_commission_rate`, `follower_count`, `has_email_address`, `has_phone`, `has_whats_app`, `id`, `partner_icon`, `partner_id`, `partner_name`, `partner_top3_category`, `partner_top3_category_list`, `total_30d_video_live_gmv`, `total_30d_video_live_sold_count`, `total_related_creator_count`, `total_related_product_count`, `total_related_seller_count`, `video_count`

### Commercial creator ranking response fields

- **List item fields**: `bio_email`, `category_label`, `country_code`, `creator_oecuid`, `follower_count`, `handle`, `id`, `interval_ecom_video_play_count_growth`, `interval_live_user`, `interval_new_follower`, `l1_category_aggregated_live_gmv`, `l1_category_aggregated_total_gmv`, `l1_category_aggregated_video_gmv`, `nickname`, `product_count`, `titkok_creator_commercial_interval_live_gmv`, `titkok_creator_commercial_interval_total_video_live_gmv`, `titkok_creator_commercial_interval_video_gmv`, `uid`, `unique_id`, `user_avatar`, `user_sell_product_l1_category`

### Creator follower-growth ranking response fields

- **List item fields**: `bio_email`, `category_label`, `channel_id`, `creator_oecuid`, `follower_count`, `handle`, `id`, `interval_new_follower`, `nickname`, `tioktok_creator_growth_interval_new_follower_ratio`, `uid`, `unique_id`, `user_avatar`, `user_sell_product_l1_category`, `video_count`

Present ratios, times, and windowed metrics as returned; do not convert them to percentages or another period yourself.

## Error codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | Follow the authentication guidance in `SKILL.md` |
| Insufficient consumption allowance or balance | Stop retrying and guide the user through authorization or adding credits |
| Permission unavailable | Stop calling and contact the gateway operator to confirm whether the tool is enabled |
| Parameter validation failed | Correct parameters according to `msg` |

## curl examples

### Creator search

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/creators/search" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","page":1,"pageSize":5}'
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
