# Product infringement and TRO risk API

`POST /api/v1/tools/research/maidalv/checkApiFlash`

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `mainProductImage` | string | Yes | Public URL or image data URI; maximum 1000 characters. |
| `referenceImages` | string[] | No | Up to 3 similar-product images. |
| `otherProductImages` | string[] | No | Up to 5 additional product images. |
| `ipImages` | string[] | No | Up to 3 IP evidence images. |
| `referenceText` | string | No | Maximum 1000 characters. |
| `description` | string | No | Prefer a concise product title; maximum 1000 characters. |
| `ipKeywords` | string[] | No | Up to 20 keywords. |
| `language` | string | No | `zh` or `en`; default `zh`. |

For a local image, run `scripts/upload_image.py` first and pass the resulting public URL as `mainProductImage`.

The response includes `status`, `checkId`, `total`, overall `riskLevel`, `results`, `nonResults`, and rendering `columns`. Result entries may include `ipType`, `text`, `ipOwner`, `regNo`, `riskLevel`, `riskScore`, `riskDescription`, `ipAssetUrls`, TRO plaintiff/case fields, and an assessment `report`. Optional fields are omitted when unavailable; do not assume they are present.

```bash
python scripts/maidalv_check_api_flash.py '{"mainProductImage":"https://example.com/product.jpg","language":"zh"}'
```

Allow at least 120 seconds. Require outer platform `code: 0`, then inspect the business `status` for task completion. Prefer the upstream `X-Cost-Token` header when available; the outer Nexscope wrapper may not expose it.

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.
