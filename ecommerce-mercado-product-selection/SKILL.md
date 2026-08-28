---
name: ecommerce-mercado-product-selection
description: "Mercado Libre product selection data query and analysis via the NexScope gateway, covering 24 tools for products, catalog, keywords, categories, trends, sellers, reviews, exchange rates, and plan usage across Mexico, Brazil, Argentina, Chile, and Colombia sites. Triggered by: Mercado Libre, MercadoLibre, product selection, product search, category trends, hot keywords, reverse traffic keywords, seller search, review search, exchange rate, plan usage, Lanjing, Mercado product research."
---

# Lanjing Mercado Libre Product Selection

This skill queries Mercado Libre product, catalog, keyword, category, trend, seller, review, exchange-rate, and plan-usage data through the NexScope gateway. The gateway exposes one unified route, `POST /lingdong/call`, and the skill selects one of 24 supported `toolName` values with matching `arguments`.

## Core Concepts

- Call only `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/lingdong/call`. Do not call the upstream Lanjing XP-MCP server directly, and do not ask the user for upstream `secret-key` / `X-API-Key` -- upstream credentials are owned by the backend.
- The request body is always `{"toolName":"...","arguments":{...}}`. The script takes this whole object as a single JSON argument.
- Field names inside `arguments` must match `references/mercado-tools.md` exactly, including camelCase names such as `siteId`, `itemId`, `productId`, `categoryId`, `runDate`, `runMonth`, `pageNo`, `pageSize`.
- Read `data` first when presenting results. Read `contentText` when `data` is text or ambiguous. Show `rawResponse` only when the user asks for raw diagnostics.
- Paid tools currently cost `16000` tokens per call; free tools cost `0`. Trust the backend `costToken` field.

## Reference Files

- `references/api.md`: NexScope gateway contract, request/response structure, error codes, and curl example.
- `references/mercado-tools.md`: reference for the 24 Mercado Libre tools, argument fields, site IDs, date formats, pagination, sorting, and billing status.

## Tool Selection

| User intent | Use these tools |
|---|---|
| Product detail, product sales history, product search | `itemInfo`, `itemHistory`, `itemSearch` |
| Catalog/product page detail, catalog sales history, catalog search | `catalogInfo`, `catalogHistory`, `catalogSearch` |
| Daily/monthly hot keywords and reverse traffic keywords | `keywordDateSearch`, `keywordMonthSearch`, `keywordReverse` |
| Category lookup before paid analysis | `categorySearch`, `categorySmallSearch` |
| Category brand, item, seller, new item, price, sales, sold-history, statistics, warehouse distribution | `trendBrandTopBrand`, `trendBrandTopItem`, `trendBrandTopSeller`, `trendNewItems`, `trendPrice`, `trendSale`, `trendSoldHis`, `trendStatistical`, `trendStoreInventoryType` |
| Seller search | `sellerSearch` |
| Product reviews | `reviewSearch` |
| Exchange rate and package usage | `rateInfo`, `myUsage` |

Free tools: `categorySearch`, `categorySmallSearch`, `reviewSearch`, `rateInfo`, `myUsage`. All others are paid.

## Parameter Guide

- `toolName` (string, required): one of the 24 tools above.
- `arguments` (object, required): the tool's parameter object. Must be a JSON object, not an array/string/number. The backend strips `uId`/`uid`/`memberId` and trims empty values.
- Sites: `MLM` (Mexico), `MLB` (Brazil), `MLA` (Argentina), `MLC` (Chile), `MCO` (Colombia -- only for tools whose reference explicitly lists it).
- When the user gives a category name instead of a `categoryId`, call `categorySearch` or `categorySmallSearch` first, then use the returned category ID for paid trend/product/catalog tools.
- `reviewSearch` takes `itemId` only (no `siteId`). `myUsage` takes `{}`.
- For broad research questions, narrow paid calls with site, category, keyword, date/month, pagination, price, sales, or sorting filters. Avoid exploratory paid calls not anchored to the user's goal.

## API Invocation

- **API Endpoint**: `POST /lingdong/call` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/mercado_product_selection.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same session + parameter combination is called only once by default; the script includes a 24-hour local cache. Do not automatically retry failed or empty results by changing keywords, paginating, or switching region codes. If further retrieval is needed, inform the user of the additional cost first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce-mercado-product-selection-mercado_product_selection-<timestamp>.json` (`<session>` is taken from `SESSION_ID` when present).
- Response body <= 8 KB: after saving to disk, print the full JSON to stdout
- Response body > 8 KB: after saving to disk, stdout prints a summary only (top-level fields, common counts like `total`/`costToken`, the length of the largest list field plus the first 3 sample items)
- Use `--inline` to force full output to stdout (also saves to disk)

**Data Reading Tips**: First check the summary to determine if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract on demand from the saved JSON file, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.

## Usage Examples

The single JSON argument is the full payload `{"toolName":...,"arguments":{...}}`.

```bash
# Free: search Mexico categories by name
python scripts/mercado_product_selection.py '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'

# Paid: product detail for a real MLM item
python scripts/mercado_product_selection.py '{"toolName":"itemInfo","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}'

# Free: my plan usage (no arguments)
python scripts/mercado_product_selection.py '{"toolName":"myUsage","arguments":{}}'

# Paid: monthly hot keywords for Brazil, 2026-06
python scripts/mercado_product_selection.py '{"toolName":"keywordMonthSearch","arguments":{"siteId":"MLB","runMonth":"202606"}}'
```

On PowerShell, wrap the JSON in single quotes the same way; if quoting is troublesome, write the payload to a file and pass it via `--inline` after loading, or use `ConvertTo-Json` to build the argument.

## Display Rules

1. Present the returned data clearly without inventing unsupported business conclusions.
2. Preserve the meaning and important field names from results; translate labels only when it improves readability.
3. For large arrays or time series, summarize the visible slice and read only needed fields from the persisted JSON file.
4. For "no data" or business-level failure messages, explain that the upstream Mercado data provider returned that result; do not label it as a system outage unless the wrapper response contains an actual error.
5. Never expose internal NexScope API keys, upstream secrets, or full sensitive raw payloads in user-facing output.

## Important Limitations

- The NexScope route is a unified backend gateway; the skill does not publish separate HTTP endpoints for each `toolName`.
- Required-field validation happens in the backend and is also documented in `references/mercado-tools.md`.
- Paid tools charge per backend invocation, even if the upstream business result is empty.
- Response shapes vary by tool. Most tools return business results as **text** in `data`; use real responses and `references/api.md` as the source of truth instead of forcing a single table schema.

## User Expression & Scenario Quick Reference

| User says | Likely action |
|---|---|
| "Look up this Mercado Libre product", "Product details", "Sales history" | Use `itemInfo` or `itemHistory` |
| "Search headphones on Mexico site", "Filter products" | Use `itemSearch`; use `categorySearch` first if only category text is known |
| "Catalog", "Official link", "Catalog listing" | Use a `catalog*` tool |
| "Hot keywords", "Monthly keywords", "Reverse traffic keywords" | Use `keywordDateSearch`, `keywordMonthSearch`, or `keywordReverse` |
| "Category trends", "New product opportunities", "Sales distribution", "Brand rankings" | Resolve `categoryId`, then use a `trend*` tool |
| "Shop", "Seller" | Use `sellerSearch` |
| "Reviews" | Use `reviewSearch` |
| "Exchange rate", "Plan usage" | Use `rateInfo` or `myUsage` |
