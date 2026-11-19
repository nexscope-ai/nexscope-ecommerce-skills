# Amazon Store Pricing API reference

Migration reference: `linkfox-amazon-store-pricing` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `getcompetitivepricing` | `/spapi/getCompetitivePricing` | Authorized connection where required |
| `getcompetitivesummary` | `/spapi/getCompetitiveSummary` | Authorized connection where required |
| `getfeaturedofferexpectedpricebatch` | `/spapi/getFeaturedOfferExpectedPriceBatch` | Authorized connection where required |
| `getitemoffers` | `/spapi/getItemOffers` | Authorized connection where required |
| `getitemoffersbatch` | `/spapi/getItemOffersBatch` | Authorized connection where required |
| `getlistingoffers` | `/spapi/getListingOffers` | Authorized connection where required |
| `getlistingoffersbatch` | `/spapi/getListingOffersBatch` | Authorized connection where required |
| `getpricing` | `/spapi/getPricing` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-pricing-getcompetitivepricing`

MCP tool: `nexscope_amazon_sp_api_pricing_getcompetitivepricing`.

Amazon operation: `GET /products/pricing/v0/competitivePrice`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemType=Asin&Asins=B000EXAMPL"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "payload": [
          {
            "status": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getcompetitivesummary`

MCP tool: `nexscope_amazon_sp_api_pricing_getcompetitivesummary`.

Amazon operation: `POST /batches/products/pricing/2022-05-01/items/competitiveSummary`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "requests": [
      {
        "asin": "B000EXAMPL",
        "marketplaceId": "ATVPDKIKX0DER",
        "includedData": [
          "featuredBuyingOptions"
        ],
        "method": "GET",
        "uri": "/products/pricing/2022-05-01/items/competitiveSummary"
      }
    ]
  }
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "responses": [
          {
            "status": {},
            "body": {
              "asin": "B000EXAMPL",
              "marketplaceId": "ATVPDKIKX0DER"
            }
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getfeaturedofferexpectedpricebatch`

MCP tool: `nexscope_amazon_sp_api_pricing_getfeaturedofferexpe_954a6e2e73a2`.

Amazon operation: `POST /batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "requests": [
      {
        "uri": "/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice",
        "method": "GET",
        "marketplaceId": "ATVPDKIKX0DER",
        "sku": "EXAMPLE"
      }
    ]
  }
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "responses": [
          {
            "status": {},
            "headers": {},
            "request": {
              "marketplaceId": "ATVPDKIKX0DER",
              "sku": "EXAMPLE"
            }
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getitemoffers`

MCP tool: `nexscope_amazon_sp_api_pricing_getitemoffers`.

Amazon operation: `GET /products/pricing/v0/items/{Asin}/offers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: Asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "Asin": "B000EXAMPL"
  },
  "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemCondition=New"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "payload": {
          "Identifier": {
            "ItemCondition": "New",
            "MarketplaceId": "ATVPDKIKX0DER"
          },
          "ItemCondition": "New",
          "Offers": [
            {
              "IsFulfilledByAmazon": false,
              "ListingPrice": {},
              "Shipping": {},
              "ShippingTime": {},
              "SubCondition": "EXAMPLE"
            }
          ],
          "Summary": {
            "TotalOfferCount": 1
          },
          "status": "EXAMPLE",
          "marketplaceId": "ATVPDKIKX0DER"
        }
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getitemoffersbatch`

MCP tool: `nexscope_amazon_sp_api_pricing_getitemoffersbatch`.

Amazon operation: `POST /batches/products/pricing/v0/itemOffers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "requests": [
      {
        "uri": "/products/pricing/v0/items/B000EXAMPL/offers",
        "method": "GET",
        "MarketplaceId": "ATVPDKIKX0DER",
        "ItemCondition": "New"
      }
    ]
  }
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "responses": [
          {
            "body": {},
            "request": {
              "MarketplaceId": "ATVPDKIKX0DER",
              "ItemCondition": "New"
            }
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getlistingoffers`

MCP tool: `nexscope_amazon_sp_api_pricing_getlistingoffers`.

Amazon operation: `GET /products/pricing/v0/listings/{SellerSKU}/offers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: SellerSKU.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "SellerSKU": "EXAMPLE"
  },
  "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemCondition=New"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "payload": {
          "Identifier": {
            "ItemCondition": "New",
            "MarketplaceId": "ATVPDKIKX0DER"
          },
          "ItemCondition": "New",
          "Offers": [
            {
              "IsFulfilledByAmazon": false,
              "ListingPrice": {},
              "Shipping": {},
              "ShippingTime": {},
              "SubCondition": "EXAMPLE"
            }
          ],
          "Summary": {
            "TotalOfferCount": 1
          },
          "status": "EXAMPLE",
          "marketplaceId": "ATVPDKIKX0DER"
        }
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getlistingoffersbatch`

MCP tool: `nexscope_amazon_sp_api_pricing_getlistingoffersbatch`.

Amazon operation: `POST /batches/products/pricing/v0/listingOffers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "requests": [
      {
        "uri": "/products/pricing/v0/listings/EXAMPLE-SKU/offers",
        "method": "GET",
        "MarketplaceId": "ATVPDKIKX0DER",
        "ItemCondition": "New"
      }
    ]
  }
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "responses": [
          {
            "body": {}
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-pricing-getpricing`

MCP tool: `nexscope_amazon_sp_api_pricing_getpricing`.

Amazon operation: `GET /products/pricing/v0/price`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "MarketplaceId=ATVPDKIKX0DER&ItemType=Asin&Asins=B000EXAMPL"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "sellerId": "EXAMPLE_SELLER",
    "requestId": "example-request-id",
    "source": "BACKEND_AMAZON_SP_API",
    "response": {
      "httpStatus": 200,
      "payload": {
        "payload": [
          {
            "status": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```
