# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Advertising and Creative Intelligence API Reference

## Request Specification

- **Endpoint (ad search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/search`
- **Endpoint (ad detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/detail`
- **Endpoint (ad related products)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/related-products`
- **Endpoint (creative search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/creatives/search`
- **Endpoint (creative detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/creatives/detail`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; read api_key from the `NEXSCOPE_API_KEY` environment variable first
- **User-Agent**：`Nexscope-Skill/1.0`
- **Pass-through headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

If `${NEXSCOPE_PROXY_BASE}` is unset, the entry scripts fall back to `https://api.nexscope.ai`.

## Entry Scripts and Endpoints

| Capability | Script | Nexscope billing |
|---|---|---:|
| Ad Search | `chuhaijiang_ad_search.py` | Consumes credits |
| Ad Detail | `chuhaijiang_ad_detail.py` | Consumes credits |
| Ad Related Products | `chuhaijiang_ad_related_products.py` | Consumes credits |
| Creative Search | `chuhaijiang_creative_search.py` | Consumes credits |
| Creative Detail | `chuhaijiang_creative_detail.py` | Consumes credits |

The five business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making another paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may consume credits again; use it only when the user explicitly agrees to the extra consumption or for debugging.

## Common Conventions

- Gateway request fields use Java/MCP camelCase names; the server maps them to upstream snake_case. Script callers must not send snake_case fields such as `page_size`, `ad_type`, or `has_product` directly.
- `country` in normal requests must be lowercase: `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`.
- For search and related products, `page` defaults to 1 with a minimum of 1; `pageSize` is optional with a maximum of 10.
- `sort` uses `field:asc` or `field:desc`. The Java layer does not maintain an enum of available fields. Do not invent sort fields; when unknown, omit the field and use the upstream default.
- Monetary amounts/GMV/GPM/spend usually use `{ "unit": string, "value": number }`, but callers must still parse the runtime type.

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

When the five endpoints were verified through the real gateway on 2026-08-29, all successful responses returned HTTP 200 with the following top-level structure:

| Field | Type | Description |
|---|---|---|
| `request_id` | string | Request trace ID |
| `data` | object | Endpoint business data; see each section for its structure |

The entry scripts preserve the complete original JSON without removing unknown business fields.

## Ad Search

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/search`
- **Script**: `chuhaijiang_ad_search.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Supported lowercase country code |
| `page` | integer | No | 1 | Page number, minimum 1 |
| `pageSize` | integer | No | Upstream default | Items per page, maximum 10 |
| `keyword` | string | No | - | Search keyword |
| `category` | string | No | - | Product category |
| `adType` | string | No | - | Upstream ad type category value |
| `excludeSparkAds` | boolean | No | - | Whether to exclude Spark Ads |
| `minViews` / `maxViews` | number | No | - | Minimum/maximum views |
| `minGmv` / `maxGmv` | number | No | - | Minimum/maximum GMV |
| `minDays` / `maxDays` | number | No | - | Minimum/maximum days running |
| `sort` | string | No | `gmv:desc` | `field:asc` or `field:desc` |

```bash
python scripts/chuhaijiang_ad_search.py '{"country":"us","keyword":"beauty","page":1,"pageSize":3}'
```

### Response Fields

In real non-empty samples, `data.items[]` contains:

- Identifiers/links: `id`, `video_id`, `product_id`, `advertiser_id`, `ad_url`, `web_url`, `advertiser_url`
- Copy/entities: `ad_title`, `advertiser_name`, `button_text`, `product_title`
- Time/delivery: `create_time`, `ad_create_time`, `last_update_time`, `duration`, `ad_day_count`
- Performance: `video_play_count`, `video_like_count`, `video_like_rate`, `video_engagement_rate`, `video_popularity`, `total_sc`
- Business metrics: `total_gmv`, `video_gpm_30d`, `ad_maximum_cost`, `ad_roas`
- Categories: `product_l1_category`, `product_l2_category`, `product_l3_category`

Subsequent ad detail and related-product requests must use this object's `id`, not `video_id` or `product_id`.

## Ad Detail

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/detail`
- **Script**: `chuhaijiang_ad_detail.py`
- **Success data**: basic information in `data.items[]`; `data.core.items[]` is also returned when requesting `include=core`

### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Supported lowercase country code |
| `id` | string | Yes | `id` returned by ad search |
| `include` | string | No | Supported value: `core`; the syntax for multiple values is comma-separated |

```bash
python scripts/chuhaijiang_ad_detail.py '{"country":"us","id":"7658119807128046879","include":"core"}'
```

### Response Fields

- `data.items[]`：`id`、`ad_title`、`advertiser_id`、`advertiser_name`、`advertiser_avatar`、`ad_cover`、`ad_url`、`web_url`、`button_text`、`duration`、`ad_create_time`、`create_time`、`last_update_time`。
- `data.core.items[]`: `core_creative_id`, `core_ad_type`, `core_ad_day_count`, `core_ad_play_ratio`, `core_ad_gmv_ratio`, `core_ad_maximum_cost`, `core_ad_roas`, `core_total_gmv`, `core_total_sc`, `core_video_play_count`, `core_video_like_count`, `core_video_comment_count`, `core_video_share_count`, `core_video_collect_count`, `core_video_gpm_30d`, `core_video_popularity` and `id`.

`ad_cover`, `advertiser_avatar`, and monetary fields are nested objects. Check their properties before use; do not treat them as plain strings or numbers.

## Ad Related Products

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/related-products`
- **Script**: `chuhaijiang_ad_related_products.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Supported lowercase country code |
| `id` | string | Yes | - | `id` returned by ad search |
| `page` | integer | No | 1 | Page number, minimum 1 |
| `pageSize` | integer | No | Upstream default | Items per page, maximum 10 |

```bash
python scripts/chuhaijiang_ad_related_products.py '{"country":"us","id":"7658119807128046879","page":1,"pageSize":3}'
```

### Response Fields

Real samples use field names with source prefixes. Do not remove these prefixes or map them to ad search fields:

- Product identifiers/basic information: `tiktok_ads_detail_product_id`, `tiktok_product_detail_product_name`, `tiktok_product_detail_product_images`, `tiktok_product_detail_region`, `tiktok_product_detail_product_status`
- Categories/prices/ratings: `tiktok_product_detail_l1_category`, `tiktok_product_detail_l2_category`, `tiktok_product_detail_l3_category`, `tiktok_product_detail_floor_price`, `tiktok_product_detail_ceiling_price`, `tiktok_product_detail_product_rating`
- SKU/commission: `tiktok_product_detail_product_sku_props`, `tiktok_product_detail_product_skus`, `tiktok_product_detail_commission_rate`
- Sales relationships: `tiktok_ads_detail_video_id`, `tiktok_ads_detail_product_total_sold_count`, `tiktok_ads_detail_product_total_gmv`, `tiktok_ads_detail_video_30d_sold_count`, `tiktok_ads_detail_video_30d_gmv`, `tiktok_ads_detail_product_launch_time`, `tiktok_ads_detail_product_country_code`
- `id`: ID of the current related record; for subsequent product detail requests, prefer `tiktok_ads_detail_product_id`

## Creative Search

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/creatives/search`
- **Script**: `chuhaijiang_creative_search.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Supported lowercase country code |
| `page` | integer | No | 1 | Page number, minimum 1 |
| `pageSize` | integer | No | Upstream default | Items per page, maximum 10 |
| `keyword` | string | No | - | Search keyword |
| `category` | string | No | - | Creative category |
| `hasProduct` | boolean | No | - | Whether products are associated |
| `isSponsored` | boolean | No | - | Whether the content is sponsored |
| `isAigc` | boolean | No | - | Whether the content is AIGC |
| `sort` | string | No | `gmv:desc` | `field:asc` or `field:desc` |

```bash
python scripts/chuhaijiang_creative_search.py '{"country":"us","hasProduct":true,"page":1,"pageSize":3}'
```

### Response Fields

In real non-empty samples, `data.items[]` contains:

- Identifiers/authors: `id`, `video_id`, `product_id`, `author_uid`, `author_unique_id`, `author_nickname`, `user_avatar`, `follower_cnt`
- Content: `video_desc`, `content_tag_v2`, `content_intent`, `platform`, `country_code`, `is_aigc_video`
- Time/duration: `video_date`, `video_launch_time`, `video_duration`
- Performance: `video_play_count`, `video_like_count`, `video_comment_count`, `video_share_count`, `video_collect_count`, `video_engagement_rate`
- Business metrics: `video_30d_gmv`, `video_total_gmv`, `video_30d_gpm`

Creative detail requests must use this object's `id`, not `video_id` or `product_id`.

## Creative Detail

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/creatives/detail`
- **Script**: `chuhaijiang_creative_detail.py`
- **Success data**: basic information in `data.items[]`; `data.analysis.items[]` and/or `data.embedding.items[]` are returned according to `include`

### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Supported lowercase country code |
| `id` | string | Yes | `id` returned by creative search |
| `include` | string | No | `analysis`, `embedding`; separate multiple values with commas |

```bash
python scripts/chuhaijiang_creative_detail.py '{"country":"us","id":"7668708053428047118","include":"analysis,embedding"}'
```

### Response Fields

- `data.items[]`: combined creative/author/product/performance data, including `id`, `video_id`, `uid`, `unique_id`, `nickname`, `follower_count`, `share_url`, `product_id`, `product_name`, `product_images`, categories, prices, ratings, commissions, status, sales/GMV, and video views/engagement/30-day sales metrics.
- `data.analysis.items[]`：`id`、`video_id`、`video_uri`、`video_cover`、`country_code`、`platform`、`is_aigc_video`、`hook_type`、`hook_subtype`、`formula_type`、`formula_subtype`、`angle_type`、`angle_subtype`、`transcription_with_structure`、`storyboards`。
- `data.embedding.items[]`：`id`、`video_id`、`video_uri`、`video_cover`、`country_code`、`platform`、`extracted_content`、`matched_tags`、`embedding`。

`embedding` is a numeric array and may significantly increase response size. Request it only when similarity analysis or downstream model input is explicitly needed. Summarize analysis fields in user-facing replies; do not inline the full vector.

## Error Codes and Failure Handling

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Request error, such as missing required parameters | Add or correct parameters according to `msg`; do not retry unchanged |
| Authentication failed | Follow "Authentication and Nexscope billing errors" in `SKILL.md` |
| Insufficient credits/balance | Stop retrying and guide the user through authorization or a top-up |
| Parameter validation or upstream call failed | Display `msg` and stop; do not retry automatically. Before retrying, explain the additional credit consumption to the user |

## curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/ads/search" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","page":1,"pageSize":3}'
```

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/ad-creative/creatives/detail" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -d '{"country":"us","id":"7668708053428047118","include":"analysis,embedding"}'
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
