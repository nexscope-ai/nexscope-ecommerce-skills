# 1688 Image Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/imageSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; api_key is read first from the `nexscope_AGENT_API_KEY` environment variable, with `nexscopeAGENT_API_KEY` as the fallback (if unset, follow **## Resolving Authentication and Credits Issues** in SKILL.md)
- **User-Agent**：`nexscope-Skill/1.0`
- **Timeout**: 60s

## Request Parameters

POST Body（JSON）：

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| imageUrl | string | Conditionally required | - | Image URL; ensure it is valid and publicly accessible. Maximum length: 1000. Only png/jpg/jpeg are supported; webp/gif and other formats are not supported. One of imageUrl/imageBase64/imageId is required |
| imageBase64 | string | Conditionally required | - | Raw Base64-encoded image string without the `data:image/jpeg;base64,` prefix. Only png/jpg/jpeg are supported (used when imageUrl is empty) |
| imageId | string | Conditionally required | - | Image ID (1688 image ID), also returned in image search results. Include imageId when requesting page>1 to speed up responses |
| page | int | No | 1 | Page number, starting from 1 |
| pageSize | int | No | 20 | Products returned per page, maximum 50 |
| priceStart | string | No | - | Minimum price filter (CNY), e.g. 10 |
| priceEnd | string | No | - | Maximum price filter (CNY), e.g. 100 |
| filter | string | No | - | Filters, separated by commas. See Supported Filters below for valid values |
| sort | string | No | {"monthSold":"desc"} | Sort criteria in JSON format {sortField: sortOrder}. Valid fields: price, rePurchaseRate, monthSold; orders: asc/desc |
| keyword | string | No | - | Keyword to search within results |
| productCollectionId | string | No | - | Product collection ID; select one. See Supported Product Collection IDs below for valid values |

### Supported Filters

Separate multiple filters with commas, for example `1688Selection,totalEpScoreLv1,qrr0`.

| Value | Description |
|----|------|
| 1688Selection | 1688 Select |
| certifiedFactory | Certified factory |
| totalEpScoreLv1 | 5-star overall experience score |
| totalEpScoreLv2 | 4-star overall experience score |
| totalEpScoreLv3 | 3-star overall experience score |
| totalEpScoreLv4 | 2-star overall experience score |
| qrr0 | No quality-related refunds |
| qrr1 | Quality-related refund rate <1% |
| qrr5 | Quality-related refund rate <5% |
| qrr10 | Quality-related refund rate <10% |
| shipInToday | Same-day dispatch |
| shipIn24Hours | Dispatch within 24 hours |
| shipIn48Hours | Dispatch within 48 hours |
| noReason7DReturn | 7-day no-reason returns |
| isOnePsale | Single-item dropshipping |
| isOnePsaleFreePost | Single-item dropshipping with free shipping |
| new7 | New within 7 days |
| new30 | New within 30 days |
| isQqyx | Global Select |
| JPFL | Japan shipping route |
| USFL | United States shipping route |
| KRFL | South Korea shipping route |
| VNFL | Vietnam shipping route |
| SAFL | Saudi Arabia shipping route |
| RUFL | Russia shipping route |
| KZFL | Kazakhstan shipping route |
| HKFL | Hong Kong shipping route |
| MOFL | Macao shipping route |
| TWFL | Taiwan shipping route |

### Supported Sort Fields

| Field | Description |
|------|------|
| price | Price |
| monthSold | Monthly units sold |
| rePurchaseRate | Repurchase rate |

Sort order: `asc` (ascending), `desc` (descending). Format example: `{"price":"asc"}`

### Supported Product Collection IDs

| ID | Description |
|----|------|
| 262105288 | Cross-border product collection |
| 262105286 | Cross-border product collection |
| 262105253 | Cross-border product collection |
| 262105281 | Cross-border product collection |
| 262105280 | Cross-border product collection |
| 262105277 | Cross-border product collection |
| 262105276 | Cross-border product collection |
| 262105274 | Cross-border product collection |
| 262105269 | Cross-border product collection |
| 262185282 | Cross-border product collection |

## Response Structure

| Field | Type | Description |
|------|------|------|
| imageId | string | Uploaded image ID (send it back in pagination requests for faster responses) |
| total | integer | Product count on this page |
| totalPage | integer | Total pages |
| sourceType | string | Source type (fixed value "1688") |
| type | string | Render style (fixed value "productWorkbenches") |
| columns | array | Render column definitions |
| costToken | integer | Tokens consumed |
| products | array | Product list (see product fields below) |

### Product Fields

| Field | Type | Description |
|------|------|------|
| offerId | string | Product ID |
| asin | string | Product number (same as offerId) |
| imageUrl | string | Product image |
| title | string | Product title |
| price | number | Wholesale price (yuan) |
| consignPrice | number | Single-item dropship price (yuan) |
| salesQuantity | integer | Monthly units sold |
| estimatedSalesAmount | number | Estimated sales revenue |
| asinUrl | string | Product URL |
| isOnePsale | string | Whether single-item dropshipping is supported (`是` = yes / `否` = no) |
| isJxhy | string | Whether this is a selected sourcing product (`是` = yes / `否` = no) |
| sellerIdentities | string | Seller identity (`超级工厂` = Super Factory / `实力商家` = Power Seller / `诚信通会员` = TrustPass member) |
| offerIdentities | string | Product tag (`严选` = Select) |
| repurchaseRate | string | Repurchase rate |
| tradeScore | string | Product transaction score |
| compositeServiceScore | string | Overall service experience score |
| sendGoodsAddressText | string | Shipping origin |
| deliveryTime | string | Dispatch time (24/48 hours) |
| quantityBegin | integer | Minimum order quantity |
| hasPromotion | string | Whether a promotion is available (`是` = yes / `否` = no) |
| promotionType | string | Promotion type |
| isPatentProduct | string | Whether this is a patented product (`是` = yes / `否` = no) |
| isSelect | string | Cross-border Select product collection indicator |
| currency | string | Currency (fixed value "¥") |
| sourceType | string | Source type (fixed value "1688") |
| sourceTool | string | Source tool (fixed value "1688以图搜图") |
| dataType | string | Data type (fixed value "monthlyData") |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). For unauthorized access, the HTTP status code is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|------|----------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credits Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credits Issues** in SKILL.md. |
| Other non-200 values | Business error | Refer to `errmsg` for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Examples

### Basic Image Search

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/imageSearch \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: nexscope-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20
  }'
```

### With Filters and Sorting

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/imageSearch \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: nexscope-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20,
    "filter": "1688Selection,totalEpScoreLv1,qrr0",
    "sort": "{\"price\":\"desc\"}"
  }'
```

### Pagination (Using imageId)

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/imageSearch \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: nexscope-Skill/1.0" \
  -d '{
    "imageId": "abc123456",
    "page": 2,
    "pageSize": 20
  }'
```

### Price Range Filter

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/imageSearch \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: nexscope-Skill/1.0" \
  -d '{
    "imageUrl": "https://m.media-amazon.com/images/I/719mRAn2VrL._AC_SL1500_.jpg",
    "page": 1,
    "pageSize": 20,
    "priceStart": "10",
    "priceEnd": "100"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-1688-search-by-image",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`nexscope-1688-search-by-image`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
