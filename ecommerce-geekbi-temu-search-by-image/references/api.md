# Nexscope migration contract

- All callable routes use `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/`.
- Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Successful transport responses use the Nexscope envelope; the provider business response is nested in `data`.
- This operation consumes credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from response headers as server-reported billing metadata; do not inherit or convert source-platform point values.
- HTTP 401 means Nexscope authentication failed. HTTP 402 means insufficient Nexscope credits. Do not retry paid or ambiguous failures automatically.

# Temu Image Search for Matching Products API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsImageSearch`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable
- **User-Agent**：`Nexscope-Skill/1.0`
- **Forwarded Headers**: `SESSION_ID`, `MESSAGE_ID`, `MODE_ID`, `APP_NAME` (empty strings when unset)
- **Timeout**: 150s

> By default, entry scripts cache only successful responses for 24 hours, including successful empty results; HTTP or business failures are not cached. `--inline` does not bypass the cache; `--no-cache` skips cache reads/writes and forces a live request, which may incur another charge reported in Nexscope response headers.

> When `${NEXSCOPE_PROXY_BASE}` is unset, the script falls back to `https://api.nexscope.ai`. Clients call only the Nexscope tool gateway, not upstream data services directly.

## Request Parameters

The POST body is a JSON object containing only the following verified fields:

| Parameter | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `imageUrl` | string | Yes | Nonempty; maximum 2048 characters; must be a resource URL in the provider OSS temporary image directory | Source image for visually similar product search |
| `contentType` | string | No | Maximum 100 characters; only `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/bmp` | Image MIME type; if supplied, must match both the OSS response type and the actual image byte format |

The downloaded image must not exceed 10 MB, and its actual bytes must be JPEG, PNG, GIF, WebP, or BMP. When `contentType` is omitted, the server detects the type from the OSS response and image bytes.

The following requests are rejected:

- `{}` or missing `imageUrl`: HTTP 400, `imageUrl 为必填参数` (imageUrl is required)
- Any external image URL: HTTP 400; configured OSS resources are required
- Image exceeds 10 MB, format is unsupported, or `contentType` differs from the OSS response/actual bytes: HTTP 400

The verified request contract for this endpoint has no Base64, pagination, page size, sorting, filtering, keyword, or site fields. Do not copy these parameters from related product search endpoints.

## Image Upload

Local or external images must first be uploaded through `scripts/upload_image.py`. The helper performs the following steps:

1. Submit `contentType` and `fileExtension` (for example, `image/png` and `png`) to `POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/oss/file/presignedPut` with Nexscope bearer authentication.
2. Read `data.url` from a successful Nexscope response (`code: 0`, provider `data.errcode: 200`). Receiving this presigned URL does not mean the image has been uploaded.
3. PUT image bytes to the exact signed HTTPS URL with matching `Content-Type` and `x-oss-object-acl: public-read`. Never send Nexscope authentication headers to OSS.
4. Only after PUT succeeds (HTTP 200 or 201), remove the query parameters and fragment and use that URL as `imageUrl`. No system asset confirmation call is used.

The original provider uses `agent-files.linkfox.com/third-data/temp-image/`. Do not substitute a system S3 URL. The maximum image size is 10,000,000 bytes.

The helper uses only the Python standard library. Do not expose API Keys or presigned URL query parameters in logs, feedback, or user-facing output.

## Response Structure

| Field | Type | Observed Value / Description |
|---|---|---|
| `errcode` | integer | `200` on success |
| `errmsg` | string | `ok` on success |
| `total` | integer | Number of similar product rows returned; varies by source image and may be `0` |
| `items` | array | Similar product rows; successful responses may contain an empty array, so do not assume a fixed 100 rows |
| `columns` | array | Render column definitions |
| `title` | string | Observed value: `Temu 图搜同款` (Temu image search for matching products) |
| `sourceType` | string | Observed value: `temu` |
| `sourceTool` | string | Observed value: `geekbi_temu` |
| `type` | string | Observed value: `tableListWorkbenches` |

Observed successful responses did not contain `page`, `size`, or `regionId`; do not invent pagination fields in documentation.

### `items[]` Product Fields

All business fields may be absent or `null`; do not parse them as required fields.

| Field Group | Fields and Meanings |
|---|---|
| Identifiers and Titles | `goodsId`, `mallId`, `goodsName`, `goodsNameCn`, `goodsNameEn`, `brand`, `thumbnail` |
| Categories | `catIds`; `catItems[]` contains `catId`, `catName`, `catLevel`, `parentCatId`, `isLeaf` |
| Cumulative Metrics | `sold`: historical units sold, `sales`: historical sales revenue, `quantity`: stock, `mallSold`: shop units sold |
| Periodic Sales Volume | `daySold`, `weekSold`, `monthSold`, `daySoldRate`, `weekSoldRate`, `monthSoldRate` |
| Periodic Sales Revenue | `daySales`, `weekSales`, `monthSales`, `daySalesRate`, `weekSalesRate`, `monthSalesRate` |
| Prices | `minPrice`, `maxPrice` (site local currency) |
| Supply Prices | `supplyPrice`, `minSupplyPrice`, `medianSupplyPrice`, `maxSupplyPrice` (upstream supply price fields) |
| Reviews | `goodsScore`, `reviewNum` |
| Status | `hostingMode` (1=fully managed, 2=semi-managed), `status` (1=normal, 2=out of stock, 3=delisted), `isAd`, `isCustom`, `isPresale` |
| Time | `onSaleTime`, `mallOpenTime`, `createTime`, `updateTime` |
| Other | `similarNum`; `sku` may be a JSON-encoded string |

Observed responses may repeat the same `goodsId` with different metrics or times; Chinese titles and text within `sku` may be garbled; some price fields may contradict one another. Callers must not silently correct, merge, or fabricate data.

### `columns[]` Structure

Render columns usually contain `field`, `title`, `cellType`, `sortable`, `filterable`. Observed responses returned 44 column definitions covering the product fields above; business parsing must use fields actually present in `items[]`.

## Response Example

The following example shows only the hierarchy confirmed by live responses; business values are simplified:

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "total": 100,
  "items": [
    {
      "goodsId": "601100240999226",
      "mallId": "634418220884840",
      "goodsNameEn": "Men's thick-soled hiking shoes",
      "thumbnail": "https://img.kwcdn.com/product/fancy/example.jpg",
      "sold": 53000,
      "monthSold": 1494,
      "minPrice": 22.32,
      "goodsScore": 4.7,
      "reviewNum": 5070,
      "hostingMode": 1,
      "status": 1
    }
  ],
  "columns": [],
  "title": "Temu 图搜同款",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches"
}
```

## Error Codes

The entry script returns HTTP JSON errors unchanged; non-JSON XML/text error bodies are wrapped as `error` / `details`. Business errors should not be replaced with Python stack traces.

| HTTP / Business Code | Meaning | Action |
|---|---|---|
| 200 with `errcode=200` | Success | Parse `items`; an empty array is also a valid result, so do not automatically switch images and retry |
| 400 | Invalid parameters or image URL | Check that `imageUrl` is nonempty and from Nexscope OSS; do not automatically switch images and retry |
| 401 | Authentication failed | Check `NEXSCOPE_API_KEY` and follow the authentication guidance in `SKILL.md` |
| 402 | Insufficient compute credits or balance | Stop calling and follow the authentication/compute-credit guidance |
| 403 | Access denied | Stop calling and contact the tool administrator; do not treat this as a top-up issue |
| 429 | Too many requests | Stop repeated calls and try again later |
| 502 / 503 / 504 | Gateway or upstream error | Do not automatically retry; explain that another charge may occur and obtain user confirmation before retrying once with the original parameters |

Verified error example:

```xml
<ToolErrorResponse><errcode>400</errcode><errmsg>imageUrl 为必填参数</errmsg></ToolErrorResponse>
```

## curl Examples

```bash
NEXSCOPE_UPLOAD_RESULT="$(python scripts/upload_image.py ./product.jpg)"
NEXSCOPE_OSS_URL="$(printf '%s' "${NEXSCOPE_UPLOAD_RESULT}" | jq -r '.url')"
NEXSCOPE_CONTENT_TYPE="$(printf '%s' "${NEXSCOPE_UPLOAD_RESULT}" | jq -r '.contentType')"

curl --max-time 150 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/geekbi/temu/goodsImageSearch" \
  -H "Authorization: Bearer $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/1.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d "{\"imageUrl\":\"${NEXSCOPE_OSS_URL}\",\"contentType\":\"${NEXSCOPE_CONTENT_TYPE}\"}"
```
