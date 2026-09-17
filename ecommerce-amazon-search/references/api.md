# Amazon Frontend Search Simulation API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/search`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No | Keyword; please translate to the language of the target country whenever possible, e.g., use English keywords for the US, German keywords for Germany, etc. (max length 1024) |
| amazonDomain | string | No | Amazon country site, default `amazon.com` |
| node | string | No | Amazon category node (max length 1000) |
| language | string | No | Language/region code, e.g., en_US, de_DE, ja_JP, fr_FR (max length 1000) |
| sort | string | No | Sort order: `relevanceblender` (Featured, default), `price-asc-rank` (Price low to high), `price-desc-rank` (Price high to low), `review-rank` (Avg. customer review), `date-desc-rank` (Newest arrivals), `exact-aware-popularity-rank` (Best sellers) |
| page | integer | No | Page number (starting from 1, ~20 items per page), default `1` |
| deliveryZip | string | No | Delivery zip code, used to simulate Amazon frontend address. It is recommended to use commonly used zip codes for major cities in the target country, e.g., New York zip code 10001 for the US site (max length 1000) |
| device | string | No | Device type: `desktop`, `mobile`, `tablet`, default `desktop` (max length 1000) |

### Supported amazonDomain Values

| Domain | Country |
|------|------|
| amazon.com | United States |
| amazon.co.uk | United Kingdom |
| amazon.de | Germany |
| amazon.fr | France |
| amazon.it | Italy |
| amazon.es | Spain |
| amazon.co.jp | Japan |
| amazon.ca | Canada |
| amazon.com.au | Australia |
| amazon.com.br | Brazil |
| amazon.in | India |
| amazon.nl | Netherlands |
| amazon.se | Sweden |
| amazon.pl | Poland |
| amazon.sg | Singapore |
| amazon.sa | Saudi Arabia |
| amazon.ae | UAE |
| amazon.com.mx | Mexico |
| amazon.com.tr | Turkey |
| amazon.com.be | Belgium |
| amazon.cn | China |
| amazon.eg | Egypt |

### Common language Values

| Region Code | Description |
|----------|------|
| en_US | US English |
| en_GB | UK English |
| de_DE | Germany German |
| fr_FR | France French |
| it_IT | Italy Italian |
| es_ES | Spain Spanish |
| ja_JP | Japan Japanese |
| en_CA | Canada English |
| fr_CA | Canada French |
| en_AU | Australia English |
| pt_BR | Brazil Portuguese |
| en_IN | India English |
| hi_IN | India Hindi |
| nl_NL | Netherlands Dutch |
| sv_SE | Sweden Swedish |
| pl_PL | Poland Polish |
| en_SG | Singapore English |
| ar_AE | UAE/Saudi Arabia/Egypt Arabic |
| en_AE | UAE/Saudi Arabia/Egypt English |
| tr_TR | Turkey Turkish |
| nl_BE | Belgium Dutch |
| fr_BE | Belgium French |
| zh_CN | China Chinese |
| pt_MX | Mexico Spanish |

### Common deliveryZip Values

| Country | City | Zip Code |
|------|------|------|
| United States | New York | 10001 |
| United Kingdom | London | EC1A 1BB |
| Germany | Berlin | 10115 |
| France | Paris | 75001 |
| Italy | Rome | 00100 |
| Spain | Madrid | 28001 |
| Japan | Tokyo | 100-0001 |
| Canada | Toronto | M5A 1A1 |
| Australia | Sydney | 2000 |
| Brazil | Sao Paulo | 01000-000 |
| India | New Delhi | 110001 |
| Netherlands | Amsterdam | 1012 |
| Sweden | Stockholm | 111 22 |
| Poland | Warsaw | 00-001 |
| Singapore | Singapore | 018989 |
| Saudi Arabia | Riyadh | 11564 |
| UAE | Abu Dhabi | 00000 |
| Mexico | Mexico City | 01000 |
| Turkey | Istanbul | 34349 |
| Belgium | Brussels | 1000 |
| China | Beijing | 100000 |
| Egypt | Cairo | 11511 |

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total rows |
| keyword | string | Search keyword |
| type | string | Render style |
| columns | array | Rendered column definitions |
| costToken | integer | Token consumption |
| products | array | Search result list (see below) |

### Product Object Fields in products

| Field | Type | Description |
|------|------|------|
| asin | string | ASIN |
| title | string | Title |
| brand | string | Brand |
| price | number | Price |
| extractedPrice | number | Parsed price |
| oldPrice | number | Strikethrough price |
| extractedOldPrice | number | Parsed strikethrough price |
| currency | string | Currency |
| priceUnit | string | Price unit |
| extractedPriceUnit | number | Parsed price unit |
| rating | number | Rating |
| ratings | integer | Number of ratings |
| position | integer | Position |
| sponsored | boolean | Whether sponsored |
| imageUrl | string | Thumbnail |
| asinUrl | string | Link |
| delivery | string | Delivery information |
| fulfillment | string | Fulfillment information (e.g., FBA) |
| availableDate | string (date) | Listing time |
| monthlySalesUnits | integer | Monthly sales units |
| monthlySalesRevenue | string | Monthly sales revenue |
| sellerNation | string | Seller nationality |
| dimension | string | Dimensions |
| weight | string | Weight |
| options | string | Options |
| offers | string | Offer information |
| badges | string | Amazon frontend search badges |
| tags | string | Tags |
| snapEbtEligible | boolean | SNAP/EBT eligibility |
| sourceType | string | Source type: amazon |
| sourceTool | string | Source tool |
| keyword | string | Keyword |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "amazonDomain": "amazon.com", "page": 1}'
```

---
