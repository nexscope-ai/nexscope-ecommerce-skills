# Lanjing Mercado Libre Product Selection API Reference

## API Specification

This Skill only calls the Nexscope backend production gateway and does not directly connect to the Lanjing XP-MCP upstream service.

- **Gateway**: Specified by environment variable `NEXSCOPE_PROXY_BASE`, falls back to `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/lingdong/call` if not set
- **Endpoint**: `POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/lingdong/call`
- **Content-Type**: `application/json`
- **User-Agent**: `Nexscope-Skill/2.0`
- **Timeout**: 120s
- **Authentication**: Header `Authorization: <api_key>`, api_key first read from environment variable `NEXSCOPE_API_KEY`, fallback `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

The script also forwards the `SESSION_ID`, `MODE_ID`, and `APP_NAME` environment variables with the same names (empty string by default). Do not pass Lanjing upstream `secret-key`, `X-API-Key`, or backend internal environment variables to the Skill; upstream credentials are managed by the backend.

## Request Parameters

The request body is fixed as:

```json
{
  "toolName": "categorySearch",
  "arguments": {
    "siteId": "MLM",
    "searchText": "Auriculares"
  }
}
```

  | Field | Type | Required | Description |
|---|---|---|---|
| `toolName` | string | Yes | One of the 24 Lanjing Mercado Libre tool names, see "Tools and Required Fields" below. |
| `arguments` | object | Yes | Parameter object for the corresponding tool. Field names must match `mercado-tools.md` exactly. |

`arguments` must be a JSON object, not an array, string, or number. The backend removes `uId`, `uid`, `memberId` and trims empty values.

## Tools and Required Fields

The following required fields come from the backend `LingdongToolDefinition` contract (for optional parameters, see `mercado-tools.md`):

| Tool | Paid | Required Fields | Purpose |
|---|---:|---|---|
| `itemInfo` | Yes | `siteId`, `itemId` | Query basic product information |
| `itemHistory` | Yes | `itemId` | Query product sales history |
| `itemSearch` | Yes | `siteId` | Product search and filtering |
| `catalogInfo` | Yes | `siteId`, `productId` | Query official catalog/directory basic info |
| `catalogHistory` | Yes | `siteId`, `productId` | Query official catalog/directory sales history |
| `catalogSearch` | Yes | `siteId` | Official catalog/directory search |
| `keywordDateSearch` | Yes | `siteId`, `runDate` | Query hot search keywords by day |
| `keywordMonthSearch` | Yes | `siteId`, `runMonth` | Query hot search keywords by month |
| `keywordReverse` | Yes | `siteId`, `itemId` | Traffic keyword reverse lookup |
| `categorySearch` | No | `siteId`, `searchText` | Search categories |
| `categorySmallSearch` | No | `siteId`, `searchText` | Search smallest subcategories |
| `trendBrandTopBrand` | Yes | `siteId`, `categoryId` | Category hot brand ranking |
| `trendBrandTopItem` | Yes | `siteId`, `categoryId` | Category hot product ranking |
| `trendBrandTopSeller` | Yes | `siteId`, `categoryId` | Category hot store ranking |
| `trendNewItems` | Yes | `siteId`, `categoryId` | New product opportunity analysis |
| `trendPrice` | Yes | `siteId`, `categoryId` | Price distribution trends |
| `trendSale` | Yes | `siteId`, `categoryId` | Sales distribution |
| `trendSoldHis` | Yes | `siteId`, `categoryId` | Sales history trends |
| `trendStatistical` | Yes | `siteId`, `categoryId` | Category summary statistics |
| `trendStoreInventoryType` | Yes | `siteId`, `categoryId` | Inventory type distribution |
| `sellerSearch` | Yes | `siteId` | Store search |
| `reviewSearch` | No | `itemId` | Query product reviews |
| `rateInfo` | No | `siteId` | Exchange rate query |
| `myUsage` | No | None | Query plan usage |

Free tools: `categorySearch`, `categorySmallSearch`, `reviewSearch`, `rateInfo`, `myUsage`. Paid tools: all tools except the free ones. The current backend policy is that each paid tool call returns a fixed `costToken = 16000`, and will not be free even if results are empty.

## Site IDs

| Site | Meaning |
|---|---|
| `MLM` | Mexico |
| `MLB` | Brazil |
| `MLA` | Argentina |
| `MLC` | Chile |
| `MCO` | Colombia, only supported by some search and trend tools |

See `mercado-tools.md` for the supported sites and common field formats.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

Normal response example (using `myUsage` as an example; most Lanjing tools return business results as text, and `data` is often a string):

```json
{
  "code": "200",
  "msg": "ok",
  "type": "rawMcpToolResult",
  "toolName": "myUsage",
  "charged": false,
  "data": "=== My Plan & Usage ===\n...",
  "rawResponse": {},
  "contentText": "\"=== My Plan & Usage ===\\n...\"",
  "textParsedAsJson": true,
  "costToken": 0,
  "costTime": 308
}
```

| Field | Description |
|---|---|
| `code`, `msg` | Provider business values inside platform `data`; not the outer platform status. |
| `type` | Currently usually `rawMcpToolResult`. |
| `toolName` | The actual Lanjing tool name that was called. |
| `charged` | Whether this tool is paid. |
| `data` | Business data unpacked from MCP `content.text`. Most Lanjing tools return results as **text** (category lists, product fields, plan usage, etc. are all formatted text), so `data` is often a string; it is only parsed into the corresponding structure when the upstream returns a JSON array/object. |
| `rawResponse` | Raw result from MCP `tools/call`; the current gateway returns an empty object `{}` (the raw result is not exposed to the Skill; use `contentText`/`data` when the raw text is needed). |
| `contentText` | The concatenated original text from MCP text content. |
| `textParsedAsJson` | Whether `contentText` was successfully parsed as JSON (also true when text is wrapped as a JSON string, in which case `data` is still a string). |
| `total` | Record count inferred by the backend; only appears when inferable (e.g., list-type results), **omitted** for text-type results (not `null`). |
| `costToken` | Token cost of this call (16000 for paid tools, 0 for free tools). |
| `costTime` | Backend latency in milliseconds. |

## Script Usage

The entry script uses the official template as the sole reference: copy the template in full + replace placeholders, with built-in gateway, authentication, 120s timeout, 24h local cache, `--inline` and auto-save. The request body is passed as a **single JSON parameter** (i.e., the complete `{"toolName":...,"arguments":{...}}`):

```bash
# Free tool: search Mexican categories by name
python scripts/nexscope_lanjing_mercado_product_selection.py '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'

# Paid tool: real MLM product details
python scripts/nexscope_lanjing_mercado_product_selection.py '{"toolName":"itemInfo","arguments":{"siteId":"MLM","itemId":"MLM4979447466"}}'

# Free tool: plan usage (no parameters)
python scripts/nexscope_lanjing_mercado_product_selection.py '{"toolName":"myUsage","arguments":{}}'

# Force full print to stdout (also saves to disk)
python scripts/nexscope_lanjing_mercado_product_selection.py '{"toolName":"myUsage","arguments":{}}' --inline
```

Output strategy: when response body <= 8 KB, save to disk and print in full; when > 8 KB, save to disk and print only a summary (top-level fields, `total`/`costToken` counts, max list field length + first 3 samples). Duplicate requests within 24h hit the cache, with output containing `Cache hit`.

## curl Example

```bash
curl -X POST "${NEXSCOPE_PROXY_BASE}" \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"toolName":"categorySearch","arguments":{"siteId":"MLM","searchText":"Auriculares"}}'
```

## Error Handling

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Parameter validation failed (missing required fields / arguments not an object / unsupported toolName, etc.) | Complete fields according to "Tools and Required Fields" and `mercado-tools.md`, verify toolName spelling, and preserve case. |
| Upstream MCP call exception (e.g., `LingdongMcpClient$TransientMcpException`) | Mostly transient (MCP handshake occasional 404), retry 1-2 times; if still failing, record sanitized request/response for backend confirmation. |

> Upstream MCP protocol errors are normalized by the gateway to `1002` or `500`; the Skill should handle the normalized gateway error.
