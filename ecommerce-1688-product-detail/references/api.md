## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# 1688 Product Detail API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/productDetail`; when `NEXSCOPE_PROXY_BASE` is unset, the script falls back to `https://api.nexscope.ai`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: Bearer <api_key>`; api_key is read first from the `NEXSCOPE_API_KEY` environment variable, with `NEXSCOPE_API_KEY` as the fallback
- **User-Agent**：`Nexscope-Skill/2.0`
- **Context Headers**: `SESSION_ID`, `MODE_ID`, `APP_NAME`; each is read from the environment variable with the same name, or passed as an empty string when unset
- **Timeout**: 150s

## Request Parameters

The POST body (JSON) only needs 1688 business parameters:

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| offerId | string | Yes | - | 1688 product ID as a positive integer; must be a string to avoid precision loss for large numbers; maximum length 1000 |
| country | string | No | `en` | Upstream compatibility field; not exposed as a user capability by this Skill and usually omitted |
| currency | string | No | 1688 default currency | Three-letter currency code, e.g. `USD`, `HKD`; uppercased by the server; maximum length 3 |

The platform automatically injects these fields from context; do not populate them in ordinary script calls: `uid`, `chatId`, `requestId`, `groupId`, `stepId`, `messageId`, `userInput`, `memberId`.

### Parameter Validation

- Missing or empty `offerId`: returns a parameter error.
- `offerId` is not a decimal integer or is less than or equal to 0: returns a parameter error.
- Blank `country` uses the server default; nonblank values are trimmed and passed to 1688 unchanged.
- Nonblank `currency` must match three English letters and is uppercased by the server; for example, `usd` is requested as `USD`.

Minimal valid request:

```json
{
  "offerId": "1040473674152"
}
```

Request with currency:

```json
{
  "offerId": "1040473674152",
  "currency": "USD"
}
```

## Response Structure

A successful response is a JSON object. The gateway adds `errcode=200` and `errmsg=ok`; business fields come from the normalized 1688 product detail model. Optional fields not returned upstream may be absent from the JSON; do not interpret missing fields as `false`, `0`, or empty strings.

### Gateway and Core Fields

| Field | Type | Description |
|------|------|------|
| errcode | integer | Gateway business status; `200` indicates success |
| errmsg | string | Gateway message; `ok` on success |
| offerId | string | 1688 product ID |
| subject | string | Chinese title |
| subjectTrans | string | Upstream extended title field; may be empty or identical to `subject` |
| description | string | Chinese product description, often containing HTML |
| descriptionTrans | string | Upstream extended description field; may be absent |
| categoryId | string | Current category ID |
| topCategoryId | string | First-level category ID |
| secondCategoryId | string | Second-level category ID |
| thirdCategoryId | string | Third-level category ID |
| categoryName | string | Category name; may be absent |
| status | string | Product status |
| createDate | string | Product creation time |
| productUrl | string | 1688 product promotion URL |
| sourceType | string | Data source, currently `1688` |
| type | string | Result style, currently `productDetail` |
| sourceTool | string | Internal source label; not needed in user-facing output |
| costToken | integer | Tokens consumed by the call; currently `1000` in successful responses |

### Product, Media, and Procurement Fields

| Field | Type | Description |
|------|------|------|
| productImage | object | Original images: `images[]`, `whiteImage` |
| productImageTrans | object | Upstream extended image field with the same structure; may be absent |
| mainVideo | string | Main video URL |
| detailVideo | string | Detail video URL |
| productAttributes | array | Product attributes: `attributeId`, `attributeName`, `attributeNameTrans`, `value`, `valueTrans` |
| sellingPoints | array | Product selling points; may be empty |
| skuList | array | SKUs, specifications, stock, prices, and SKU images; see the next section |
| saleInfo | object | Stock, tiered prices, units, and distribution sales information; see the next section |
| shippingInfo | object | Shipping origin, lead times, and product/SKU package weights and dimensions; see the next section |
| companyName | string | Supplier/store name |
| sellerOpenId | string | Encrypted seller ID |
| sellerDataInfo | object | Seller service and transaction metrics; see the next section |
| sellerMixSetting | object | Mixed wholesale settings: `generalHunpi`, `mixAmount`, `mixNumber` |
| channelPrice | object | Channel SKU prices: `skuPrices[].skuId/currentPrice` |
| promotion | object | Promotion information: `hasPromotion`, `promotionType` |
| minOrderQuantity | integer | Minimum order quantity |
| batchNumber | integer | Units per lot |
| productCargoNumber | string | Product item number |
| soldOut | string | Product units sold |
| isJxhy | boolean | Whether this is a selected sourcing product |
| isSelect | boolean | Whether this belongs to a cross-border Select product collection |
| tradeScore | string | Product transaction score |
| offerIdentities | array | Product or seller identity labels |
| tags | array | Service tags: `key`, `value` |
| certificates | array | Certificates: `certificateName`, `certificateCode`, `certificatePhotoList[]` |
| invoiceInfo | object | Invoice information: `supportOnlineInvoice`, `supportFastInvoice`, `invoiceTypes[]`, `taxpayerType` |

### `skuList[]`

| Field | Type | Description |
|------|------|------|
| skuId | string | SKU ID |
| specId | string | Specification ID |
| cargoNumber | string | SKU item number |
| amountOnSale | integer | Available stock |
| price | string | SKU price (CNY); in the new retail price model, the wholesale price for purchases of at least 2 units. For the legacy product model, determine its meaning using price tiers and the order preview |
| retailPrice | string | SKU retail price (CNY) for a purchase of 1 unit; absent when no retail price is returned upstream |
| foreignCurrencyRetailPrice | number | SKU retail price in the requested foreign currency for a purchase of 1 unit; absent when no currency was requested, no retail price exists, or conversion failed |
| promotionPrice | string | Promotional price |
| consignPrice | string | Single-item dropship price; deprecated upstream compatibility field that may be absent |
| jxhyPrice / pfJxhyPrice | string | Selected sourcing compatibility price fields; may be absent |
| skuImageUrl / skuImageUrlTrans | string | SKU image and upstream extended image field |
| attributes | array | SKU attributes, including names, values, and optional images |
| fenxiaoPriceInfo | object | `offerPrice`、`onePiecePrice`、`foreignCurrencyPrice`、`foreignCurrencyPromotionPrice` |

`currency` applies to `foreignCurrencyRetailPrice`, `fenxiaoPriceInfo.foreignCurrencyPrice`, and other `foreignCurrency*` fields. Do not label the CNY `retailPrice`, `price`, or `offerPrice` as the requested currency.

### `saleInfo`

| Field | Type | Description |
|------|------|------|
| amountOnSale | integer | Total product stock |
| retailPrice | string | Product-level retail price (CNY) for a purchase of 1 unit; absent when no retail price is returned upstream |
| foreignCurrencyRetailPrice | number | Product-level retail price in the requested foreign currency for a purchase of 1 unit; absent when no currency was requested, no retail price exists, or conversion failed |
| quoteType | integer | `0`: by product quantity without SKUs; `1`: by SKU specification; `2`: by product quantity with SKUs |
| priceRanges | array | Wholesale price tiers: `startQuantity`, `price`, `promotionPrice`, `foreignCurrencyPrice`, `foreignCurrencyPromotionPrice`; the first tier in the new retail price model starts at 2 or more units, while the legacy product model may still start at 1 unit |
| unitInfo | object | Unit field `unit` and upstream extended field `transUnit` |
| fenxiaoSaleInfo | object | `startQuantity`、`offerPrice`、`onePiecePrice`、`onePieceFreePostage` |
| consignPrice / jxhyPrice | string | Deprecated upstream compatibility fields; may be absent |

### Price Selection After the Retail Price Update

- New retail price model, purchase quantity of 1 unit: read `skuList[].retailPrice` for the matching SKU; for products without SKUs, read `saleInfo.retailPrice`.
- New retail price model, purchase quantity of at least 2 units: read `skuList[].price` for the matching SKU and use `saleInfo.priceRanges[]` to select the wholesale tier for that quantity.
- `minOrderQuantity` may still be `1`, but the first wholesale tier in `priceRanges` starts at 2 units in the new retail price model; do not treat the wholesale price as a single-unit price merely because the minimum order quantity is 1.
- Missing `retailPrice` may indicate the legacy product model or an unset retail price. Keep the retail price absent; do not automatically fall back to `price`, `consignPrice`, `jxhyPrice`, `offerPrice`, `onePiecePrice`, or `promotionPrice`. If a tier explicitly starts at `startQuantity=1`, label it only as legacy-model tier information; when calculating costs or profits or placing an order, still confirm the single-unit transaction price using a live order preview.
- The meaning of `promotionPrice` has not changed with this retail price update; do not use it in place of the retail price. Final availability, discounts, shipping costs, and transaction prices are determined by the live order preview.

### `shippingInfo`

| Field | Type | Description |
|------|------|------|
| sendGoodsAddressText | string | Shipping origin |
| shippingTimeGuarantee | string | Dispatch guarantee |
| length / width / height | number | Product length, width, and height in cm |
| weight | number | Product weight in kg |
| officialLength / officialWidth / officialHeight | number | Officially measured length, width, and height in cm |
| officialWeight | number | Officially measured weight in kg |
| pkgSizeSource | string | Source of product package weight and dimension data |
| skuShippingInfoList | array | SKU shipping specifications; `weight` is in g and other dimensions are in cm |
| skuShippingDetails | array | SKU package weights and dimensions; `weight`/`officialWeight`/`aiWeight` are in kg and dimensions are in cm |

### `sellerDataInfo`

| Field | Type | Description |
|------|------|------|
| tradeMedalLevel | string | Seller transaction medal |
| compositeServiceScore | string | Overall service score |
| logisticsExperienceScore | string | Logistics experience score |
| disputeComplaintScore | string | Dispute resolution score |
| offerExperienceScore | string | Product experience score |
| consultingExperienceScore | string | Consultation experience score |
| afterSalesExperienceScore | string | Returns and exchanges experience score |
| repeatPurchasePercent | string | Seller repeat purchase rate |
| collect30DayWithin48HPercent | string | 48-hour carrier pickup rate over the last 30 days |
| qualityRefundWithin30Day | string | Quality-related refund rate over the last 30 days |

### New Retail Price Model Response Shape (Field Example)

The example below illustrates the locations and types of the new fields; it does not imply that the specified offerId has already switched to the new retail price model. Actual fields and values are determined by the live response.

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "offerId": "1040473674152",
  "subject": "专业采耳工具掏耳朵耳朵鹅绒毛毛棒打毛毛扣挖耳勺采耳按摩鹅毛棒",
  "skuList": [
    {
      "skuId": "6226287579433",
      "retailPrice": "4.80",
      "foreignCurrencyRetailPrice": 0.73,
      "price": "4.05",
      "amountOnSale": 457,
      "fenxiaoPriceInfo": {
        "offerPrice": "4.05",
        "onePiecePrice": "4.05"
      }
    }
  ],
  "saleInfo": {
    "amountOnSale": 1917,
    "retailPrice": "4.80",
    "foreignCurrencyRetailPrice": 0.73,
    "priceRanges": [
      {
        "startQuantity": 2,
        "price": "4.05",
        "foreignCurrencyPrice": 0.62
      }
    ]
  },
  "sourceType": "1688",
  "type": "productDetail",
  "costToken": 1000
}
```

## Error Codes

The script attempts to parse HTTP error bodies as JSON and return them without printing Python stack traces for gateway 4xx/5xx responses.

| errcode / HTTP | Meaning | Action |
|----------------|------|----------|
| 200 | Success | Parse business fields and confirm that `offerId` matches the request |
| 400 | Routing-layer parameter validation failed | Check required fields, types, formats, and lengths; error responses may echo received parameters |
| 1002 | Service-layer parameter or login context error | Check `offerId` and `currency`, or log in again |
| 1003 | 1688 product detail service or upstream response error | Retry once later; if it still fails, contact the gateway maintainer |
| 1005 | The current user is not authorized and default authorization is unavailable as a fallback | Follow the 1688 authorization process |
| HTTP 401 | API Key authentication failed | Follow Resolving Authentication and Credits Issues in SKILL.md |
| HTTP 402 | Insufficient credits | Follow Resolving Authentication and Credits Issues in SKILL.md |
| HTTP 403 | Access denied | This is not a login/top-up issue; contact an administrator to confirm tool permissions |

Common parameter error response:

```json
{
  "errcode": 400,
  "offerId": "",
  "errmsg": "offerId 为必填参数"
}
```

## curl Examples

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"

curl --location "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/alibaba1688/productDetail" \
  --header "Authorization: ${API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: Nexscope-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{
    "offerId": "1040473674152",
    "currency": "USD"
  }'
```

---

## Feedback API

> This endpoint is separate from the tool gateway above; do not mix their base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-1688-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The product detail matched the requested 1688 offer."
}
```

**Field rules:**

- `skillName`: Always use `nexscope-1688-product-detail` from the YAML frontmatter
- `sentiment`: Choose one of `POSITIVE`, `NEUTRAL`, `NEGATIVE`
- `category`: Choose one of `BUG`, `COMPLAINT`, `SUGGESTION`, `OTHER`
- `content`: Explain the user intent, actual result, and reason for the problem or praise
