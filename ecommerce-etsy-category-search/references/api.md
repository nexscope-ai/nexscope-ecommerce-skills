# `_ehunt_etsyCategorySearch` API Reference

## Call Notes

- **Tool Name**: `_ehunt_etsyCategorySearch` (Nexscope MCP, `serverName`: Third-party data service).
- **MCP Display Name**: Etsy Category Query.
- **Data Scope**: Queries Etsy categories that have been written to the MCP database. Data in the database must first be synced via **`_ehunt_syncEtsyCategory`** (MCP display name: Etsy Category Sync).

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string, maxLen=200 | **Yes** | Keyword: matches category name, category id, or parentIds fields (substring) |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~200, default 50 | No | Items per page, max 200 |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Main Response Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records returned on this page |
| costToken | integer | Token consumption (local retrieval is free) |
| categories | array | List of matching categories |
| title | string | Title |

### `categories[]` Elements

| Field | Type | Description |
|------|------|------|
| categoryLevel | integer | Category level |
| id | string | Category ID |
| name | string | Category name |
| parentId | string | Canonical primary parent category ID |
| parentIds | string | All non-empty parent category IDs (comma-separated) |

## Script Debugging (Optional)

The repository provides **`scripts/etsy_category_search.py`** (Python 3, standard library only).

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/etsy/etsyCategorySearch` (can be overridden via `NEXSCOPE_PROXY_BASE_BASE`); **Authentication**: `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/etsy_category_search.py '{"keyword": "jewelry", "page": 1, "pageSize": 50}'
```

Category data must first be synced to the MCP database via **`_ehunt_syncEtsyCategory`**, otherwise results may be empty.
