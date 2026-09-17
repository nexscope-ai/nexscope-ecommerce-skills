# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# TikTok Live Commerce Intelligence API Reference

## Request Specification

- **Endpoint (live search)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/search`
- **Endpoint (live detail)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/detail`
- **Endpoint (related products)**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/related-products`
- **Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; read api_key from the `NEXSCOPE_API_KEY` environment variable first
- **User-Agent**：`Nexscope-Skill/1.0`
- **Pass-through headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

If `${NEXSCOPE_PROXY_BASE}` is unset, the entry scripts fall back to `https://api.nexscope.ai`.

## Entry Scripts and Credits

| Capability | Script | Nexscope billing |
|---|---|---:|
| Live Search | `chuhaijiang_live_search.py` | Consumes credits |
| Live Detail | `chuhaijiang_live_detail.py` | Consumes credits |
| Live Related Products | `chuhaijiang_live_related_products.py` | Consumes credits |

The three business entry scripts cache successful responses for 24 hours by default. Cache entries are isolated by current working directory, caller identity, gateway, endpoint, and complete request parameters. A matching entry prints `Cache hit` without making another paid request. HTTP or business failures are not cached; successful empty results may be cached. `--inline` does not bypass the cache. `--no-cache` skips cache reads and writes and forces a real request, which may consume credits again; use it only when the user explicitly agrees to the extra consumption or for debugging.

## Common Conventions

- Gateway request fields use camelCase. The Java service maps them to upstream snake_case parameters; script callers must not send snake_case aliases directly.
- `country` is a required lowercase country code: `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`.
- When `id` is a 19-digit livestream or product identifier, pass it as a JSON string to avoid numeric precision loss.
- Monetary fields usually use `{ "unit": "US", "value": 2015752.25 }`. Preserve the original `unit` and `value`; do not convert them yourself.

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

In real gateway calls on 2026-08-29, all three endpoints returned non-empty business data under the historical contract; these business fields are now inside platform `data`:

| Field | Type | Description |
|---|---|---|
| `request_id` | string | Request trace ID |
| `data` | object | Endpoint business data; shape depends on the endpoint |

The entry scripts preserve the complete original JSON without removing unknown business fields.

## Live Search

### Endpoint Information

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/search`
- **Script**: `chuhaijiang_live_search.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Lowercase country code |
| `page` | integer | No | 1 | Page number, minimum 1 |
| `pageSize` | integer | No | - | Items per page, maximum 10; the Java route declares no default |
| `keyword` | string | No | - | Search keyword |
| `category` | string | No | - | Livestream category |
| `productCategory` | string | No | - | Product category |
| `isLiving` | boolean | No | - | Whether currently live |
| `isCommercial` | boolean | No | - | Whether it promotes products |
| `minSold` / `maxSold` | number | No | - | Minimum/maximum sales volume |
| `minGmv` / `maxGmv` | number | No | - | Minimum/maximum GMV |
| `minAudience` / `maxAudience` | number | No | - | Minimum/maximum audience count |
| `sort` | string | No | `gmv:desc` | `field:asc` or `field:desc`; `gmv:desc` has been verified in real calls |

```bash
python scripts/chuhaijiang_live_search.py '{"country":"us","isCommercial":true,"sort":"gmv:desc","page":1,"pageSize":3}'
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `data.total_count` | integer | Total matches |
| `data.items[].id` | string | Livestream room ID; reuse it for detail and related-product requests |
| `title` / `room_link` | string | Livestream title / public livestream link |
| `user_id` / `user_unique_id` / `user_nickname` | string | Host ID, account, and nickname |
| `user_category_label` | string | Host category label |
| `country_code` | string | Actual country code of the record |
| `start_time` / `end_time` | integer | Timestamp in milliseconds |
| `cover` | object | `url` and `thumb_url` |
| `product_count` / `total_sold_count` | integer | Product count / total sales volume |
| `total_user` / `max_user_count` | integer | Total audience / peak audience |
| `new_follow_count` | integer | New follower count |
| `gmv` / `gpm` | object | GMV / GPM with `unit` and `value` |
| `opm` | number | Orders per thousand viewers |
| `most_product_category_label` | string | Main product category label |

Fields may be missing or `null`; the scripts preserve the complete original JSON.

## Live Detail

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/detail`
- **Script**: `chuhaijiang_live_detail.py`
- **Success data**: basic information in `data.items[]`; `data.core.items[]` is also returned when requesting `include=core`

### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `country` | string | Yes | Lowercase country code |
| `id` | string | Yes | Livestream room ID |
| `include` | string | No | Optional expansion: `core`; separate multiple values with commas |

```bash
python scripts/chuhaijiang_live_detail.py '{"country":"us","id":"7643101948819835678","include":"core"}'
```

### Basic Details `data.items[]`

| Field | Type | Description |
|---|---|---|
| `id` | string | Livestream room ID |
| `title` / `room_link` | string | Title / public link |
| `country_code` | string | Country code of the record |
| `start_time` / `end_time` | integer | Timestamp in milliseconds |
| `cover` / `user_avatar` | object | `url` and `thumb_url` |
| `user_id` / `user_nickname` | string | Host ID / nickname |
| `user_follower_count` / `user_live_count` | integer | Host follower count / livestream count |
| `user_avg_audience_count` / `user_avg_max_audience_count` | number | Host historical average audience / average peak audience |
| `most_product_category_label` | string | Main product category label |

### Core Metrics `data.core.items[]`

The real response for `include=core` includes `id`, `core_room_id`, `core_country_code`, `core_gmv`, `core_gpm`, `core_avg_price`, `core_product_count`, `core_sold_product_id_count`, `core_total_sold_count`, `core_total_user`, `core_avg_online_viewer`, `core_max_user_count`, `core_new_follow_count`, and `core_follower_conversion_rate`.

`core_gmv`, `core_gpm`, and `core_avg_price` are monetary objects. `core_follower_conversion_rate` is a decimal ratio; for example, `0.0007` means `0.07%`.

## Live Related Products

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/related-products`
- **Script**: `chuhaijiang_live_related_products.py`
- **Success data**: `data.items[]`; total count: `data.total_count`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---|---|
| `country` | string | Yes | - | Lowercase country code |
| `id` | string | Yes | - | Livestream room ID |
| `page` | integer | No | 1 | Page number, minimum 1 |
| `pageSize` | integer | No | - | Items per page, maximum 10; the Java route declares no default |

```bash
python scripts/chuhaijiang_live_related_products.py '{"country":"us","id":"7643101948819835678","page":1,"pageSize":3}'
```

### Response Fields `data.items[]`

| Field | Type | Description |
|---|---|---|
| `id` / `tiktok_live_detail_product_id` | string | Product ID |
| `tiktok_live_detail_product_title` | string | Product title |
| `tiktok_live_detail_product_images` | object | Product image `url` / `thumb_url` |
| `tiktok_live_detail_product_country_code` | string | Product country code |
| `tiktok_live_detail_product_floor_price` / `ceiling_price` | object | Minimum/maximum price, with `unit` and `value` |
| `tiktok_live_detail_product_sold_count` | integer | Livestream-attributed sales volume |
| `tiktok_live_detail_product_gmv` | object | Livestream-attributed GMV, with `unit` and `value` |
| `tiktok_live_detail_product_commission_rate_num` | number | Commission rate as a decimal; the field may be missing |
| `tiktok_live_detail_product_conversion_rate` | number | Conversion rate as a decimal |
| `tiktok_live_detail_product_seller_id` / `seller_name` | string | Seller ID / name |
| `tiktok_live_detail_product_seller_avatar` | object | Seller avatar |
| `tiktok_live_detail_product_seller_info` | array | Seller description text |
| `tiktok_live_detail_product_l1_category` / `l2_category` / `l3_category` | string | Product category labels |
| `tiktok_live_detail_product_seller_category_name_label` | string | Seller category label |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | Follow "Authentication and Nexscope billing errors" in `SKILL.md` |
| Insufficient credits or balance | Stop retrying and guide the user to resolve the balance issue |
| Parameter validation failed | Correct fields according to `msg`; do not automatically probe paid APIs repeatedly |

The entry scripts display HTTP errors and gateway JSON errors as structured content; there should be no unhandled Python traceback.

## curl Examples

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/chuhaijiang/lives/search" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","isCommercial":true,"sort":"gmv:desc","page":1,"pageSize":3}'
```

---

Legacy local cache: a still-valid cache created before this response contract remains usable without a new paid request. The scripts mark its copied metadata as `_nexscope.responseContract = "legacy-cache"`, with `_nexscope.code` and `_nexscope.msg` set to `null` because the original platform status/message is unavailable. Do not infer platform success from business `errcode`, `code`, or `status`. Existing business data, billing metadata, cache contents and expiration are preserved; the marker is added only to the in-memory output.
