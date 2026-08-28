# eBay Product Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ebay/search`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | No | Search keyword, max 1024 characters |
| ebayDomain | string | No | eBay site domain, default `ebay.com`. Options: ebay.com (United States), ebay.co.uk (United Kingdom), ebay.de (Germany), ebay.fr (France), ebay.it (Italy), ebay.es (Spain), ebay.ca (Canada), ebay.com.au (Australia), ebay.nl (Netherlands), ebay.at (Austria), ebay.ch (Switzerland), ebay.pl (Poland), ebay.ie (Ireland), ebay.com.hk (Hong Kong, China), ebay.com.my (Malaysia), ebay.com.sg (Singapore) |
| page | integer | No | Page number for pagination, default `1` |
| pageSize | integer | No | Maximum results per page, default `50`. Options: 25, 50, 100, 200 |
| orderBy | string | No | Sort order, default `12` (Best Match). Options: 1 (Ending soonest), 2 (Price lowest), 3 (Price highest), 7 (Distance nearest), 10 (Newly listed), 12 (Best Match), 15 (Price + shipping lowest), 16 (Price + shipping highest), 18 (New first), 19 (Used first) |
| priceMin | number | No | Minimum price filter |
| priceMax | number | No | Maximum price filter |
| itemCondition | string | No | Item condition code, multiple separated by `\|`. Options: 1000 (New), 1500 (New other), 1750 (New with defects), 2000 (Manufacturer refurbished), 2010 (Excellent refurbished), 2020 (Good refurbished), 2030 (Fair refurbished), 2500 (Seller refurbished), 2750 (Like new), 3000 (Used/Pre-owned), 7000 (For parts or not working) |
| buyingFormat | string | No | Buying format. Options: Auction, BIN (Buy It Now), BO (Best Offer) |
| showOnly | string | No | Filter conditions, comma-separated for multiple values. Options: Complete (Ended), Sold (Sold), FR (Free returns), RPA (Returns accepted), AS (Authorized seller), Savings (Discounts), SaleItems (Sale items), Lots (Lots), Charity (Charity), AV, FS (Free shipping), LPickup (Local pickup) |
| location | integer | No | Country/region code of item location (e.g., 1=United States, 2=Canada, 3=United Kingdom, 45=China, 77=Germany) |
| prefLoc | string | No | Preferred location scope. Options: 1 (Domestic), 2 (Regional), 3 (Worldwide) |
| zipCode | string | No | ZIP or postal code for filtering shippable items by region |
| categoryId | integer | No | eBay category ID for category-specific search |
| noCache | boolean | No | Whether to bypass cache, default `false` |

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total matching results |
| products | array | Product list array (see product fields below) |
| columns | array | Rendered column definitions |
| type | string | Render style identifier |
| costToken | integer | Token consumption |

### Product Fields

| Field | Type | Description |
|------|------|------|
| productId | string | eBay product ID |
| title | string | Product title |
| subtitle | string | Product subtitle |
| price | number | Current price / transaction price |
| minPrice | number | Price range start value (for multi-SKU items) |
| maxPrice | number | Price range end value (for multi-SKU items) |
| oldPrice | number | Original price before discount |
| currency | string | Currency unit (e.g., USD, GBP, EUR) |
| condition | string | Item condition description |
| link | string | eBay product detail page link |
| imageUrl | string | Product thumbnail URL |
| shipping | string | Shipping information |
| location | string | Item location |
| sellerName | string | Seller name |
| sellerReviews | integer | Seller feedback count |
| positiveFeedbackInPercentage | number | Seller positive feedback percentage |
| salesQuantity | integer | Quantity sold |
| bidsCount | integer | Bid count (for auction items) |
| returns | string | Return information |
| promotion | string | Promotion information |
| sponsored | boolean | Whether sponsored/promoted item |
| sourceType | string | Source platform identifier (`ebay`) |
| sourceTool | string | Source tool identifier |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ebay/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "wireless earbuds", "ebayDomain": "ebay.com", "pageSize": 50, "orderBy": "12"}'
```

### Search for Sold Items

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ebay/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "iPhone 15 Pro", "showOnly": "Sold,Complete", "orderBy": "10"}'
```

### Filter by Price Range and Condition

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ebay/search \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "laptop", "ebayDomain": "ebay.co.uk", "priceMin": 500, "priceMax": 1000, "itemCondition": "1000"}'
```

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the errorCode field in the response body (errorCode = 200 indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding errorCode also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

---
