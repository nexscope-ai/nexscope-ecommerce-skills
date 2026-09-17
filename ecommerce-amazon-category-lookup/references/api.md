# Amazon category lookup API

The script supports two modes and must preserve the user's marketplace.

## Browse child nodes

`POST /api/v1/tools/research/amazon/nodes/lookup`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `marketId` | string | No | `1` | Amazon marketplace ID. |
| `nodeId` | string | No | root | Parent category node. |
| `table` | string | No | `bsr_sales_nearly` | Current data or a historical month such as `202508`. |

## Search by label

`POST /api/v1/tools/research/amazon/nodes/lookup/like`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `nodeLabel` | string | Yes | — | Category-name keyword, maximum 1000 characters. |
| `marketId` | string | No | `1` | Amazon marketplace ID. |
| `nodeId` | string | No | — | Optional exact node filter. |

Common marketplace IDs: US `1`, UK `3`, DE `4`, FR `5`, JP `6`, CA `7`, IT `35691`, ES `44551`, IN `44571`, MX `771770`.

Read `items` and preserve `nodeId`, `label`, `nodeLabel`, localized labels, product count, child count, and parent ID. Business success is `code: "OK"`; surface `message` when `code` is `ERROR`.

```bash
python scripts/amazon_category_lookup.py --mode lookup '{"marketId":"1","nodeId":"-1"}'
python scripts/amazon_category_lookup.py --mode like '{"marketId":"1","nodeLabel":"Electronics"}'
```

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.
