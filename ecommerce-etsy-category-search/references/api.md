# `_ehunt_etsyCategorySearch` API Reference

## Call Notes

- **Tool Name**: `_ehunt_etsyCategorySearch` (NexScope MCP, `serverName`: Third-party data service).
- **MCP Display Name**: Etsy Category Query.
- **Data Scope**: Queries Etsy categories that have been written to the MCP database. Data in the database must first be synced via **`_ehunt_syncEtsyCategory`** (MCP display name: Etsy Category Sync).

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string, maxLen=200 | **Yes** | Keyword: matches category name, category id, or parentIds fields (substring) |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~200, default 50 | No | Items per page, max 200 |

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
