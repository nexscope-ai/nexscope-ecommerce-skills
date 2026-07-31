# Temu Category Search API Reference

## Usage Notes

- **Gateway route**: `POST ehunt/temu/temuCategorySearch` (full: `${NEXSCOPE_PROXY_BASE}CategorySearch`).
- **MCP display name**: Temu Category Query (the exact tool name is subject to the tool metadata deployed in the current environment).
- **Authentication**: Request header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)
- **Data scope**: Queries Temu categories that have been written to the local database; data must first be synced via **`ehunt/temu/syncTemuCategory`** (MCP display name: Temu Category Sync). Local search does not incur charges.

## Request Parameters (JSON)

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string, maxLen=200 | **Yes** | Keyword: matches against category Chinese name, English name, category ID (substring) |
| page | integer, >=1, default 1 | No | Page number (starting from 1) |
| pageSize | integer, 1~200, default 50 | No | Results per page, max 200 |

## Main Response Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Number of results returned on this page |
| categories | array | List of matching categories |
| title | string | Title (`Temu Category Search`) |

### `categories[]` Elements

| Field | Type | Description |
|------|------|------|
| id | string | Category ID |
| categoryId | string | Category ID (upstream category id) |
| parentId | string | Parent category ID (empty string for top-level) |
| level | integer | Category hierarchy level |
| categoryName | string | Category name (Chinese) |
| categoryNameEn | string | Category name (English) |
| isDeleted | integer | Whether deleted: 0=Normal, 1=Deleted |
| hasChildren | boolean | Whether has child categories |

## Category Sync (Prerequisite)

Category data must first be pulled by **`ehunt/temu/syncTemuCategory`** (MCP display name: Temu Category Sync, no input parameters) to fetch the category tree and write it to the local database; otherwise search results may be empty. It returns `result` (success value is `success`) and `totalRows` (number of category rows written by the sync).

## Script Debugging (Optional)

The repository provides **`scripts/temu_category_search.py`** (Python 3, standard library only).

- **Gateway**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ehunt/temu/temuCategorySearch` (can override with `NEXSCOPE_PROXY_BASE_BASE`)
- **Authentication**: `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

```bash
export NEXSCOPE_API_KEY="<your-key>"
python scripts/temu_category_search.py '{"keyword": "kitchen", "page": 1, "pageSize": 50}'
```

Category data must first be synced via **`ehunt/temu/syncTemuCategory`** to the local database; otherwise results may be empty.
