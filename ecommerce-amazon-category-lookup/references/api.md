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
