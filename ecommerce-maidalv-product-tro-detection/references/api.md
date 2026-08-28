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

Allow at least 120 seconds. Treat `errcode: 200` and `status: success` as business success. Prefer the upstream `X-Cost-Token` header when available; the outer NexScope wrapper may not expose it.
