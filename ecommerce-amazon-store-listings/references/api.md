# Amazon Store Listings API reference

Migration reference: `linkfox-amazon-store-listings` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `deletelistingsitem` | `/spapi/deleteListingsItem` | Authorized connection where required |
| `getlistingsitem` | `/spapi/getListingsItem` | Authorized connection where required |
| `getlistingsrestrictions` | `/spapi/getListingsRestrictions` | Authorized connection where required |
| `patchlistingsitem` | `/spapi/patchListingsItem` | Authorized connection where required |
| `putlistingsitem` | `/spapi/putListingsItem` | Authorized connection where required |
| `searchlistingsitems` | `/spapi/searchListingsItems` | Authorized connection where required |
| `getdefinitionsproducttype` | `/spapi/getDefinitionsProductType` | Authorized connection where required |
| `searchdefinitionsproducttypes` | `/spapi/searchDefinitionsProductTypes` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-listings-deletelistingsitem`

MCP tool: `nexscope_amazon_sp_api_listings_deletelistingsitem`.

Amazon operation: `DELETE /listings/2021-08-01/items/{sellerId}/{sku}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerId, sku.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerId": "EXAMPLE_SELLER",
    "sku": "EXAMPLE"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER",
  "action": "preview"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "confirmationToken": "EXAMPLE_NOT_VALID",
    "expiresAt": 1893456000000,
    "confirmationRequired": true,
    "summary": {
      "connectionId": 123,
      "sellerId": "EXAMPLE_SELLER",
      "marketplaceId": "ATVPDKIKX0DER",
      "region": "NA",
      "method": "DELETE",
      "path": "/listings/2021-08-01/items/EXAMPLE_SELLER/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-listings-getlistingsitem`

MCP tool: `nexscope_amazon_sp_api_listings_getlistingsitem`.

Amazon operation: `GET /listings/2021-08-01/items/{sellerId}/{sku}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerId, sku.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerId": "EXAMPLE_SELLER",
    "sku": "EXAMPLE"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER"
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
        "sku": "EXAMPLE"
      }
    }
  }
}
```

### `amazon-sp-api-listings-getlistingsrestrictions`

MCP tool: `nexscope_amazon_sp_api_listings_getlistingsrestrictions`.

Amazon operation: `GET /listings/2021-08-01/restrictions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "asin=B000EXAMPL&sellerId=EXAMPLE_SELLER&marketplaceIds=ATVPDKIKX0DER"
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
        "restrictions": [
          {
            "marketplaceId": "ATVPDKIKX0DER"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-listings-patchlistingsitem`

MCP tool: `nexscope_amazon_sp_api_listings_patchlistingsitem`.

Amazon operation: `PATCH /listings/2021-08-01/items/{sellerId}/{sku}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerId, sku.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerId": "EXAMPLE_SELLER",
    "sku": "EXAMPLE"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER",
  "body": {
    "productType": "EXAMPLE",
    "patches": [
      {
        "op": "add",
        "path": "EXAMPLE"
      }
    ]
  },
  "action": "preview"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "confirmationToken": "EXAMPLE_NOT_VALID",
    "expiresAt": 1893456000000,
    "confirmationRequired": true,
    "summary": {
      "connectionId": 123,
      "sellerId": "EXAMPLE_SELLER",
      "marketplaceId": "ATVPDKIKX0DER",
      "region": "NA",
      "method": "PATCH",
      "path": "/listings/2021-08-01/items/EXAMPLE_SELLER/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-listings-putlistingsitem`

MCP tool: `nexscope_amazon_sp_api_listings_putlistingsitem`.

Amazon operation: `PUT /listings/2021-08-01/items/{sellerId}/{sku}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerId, sku.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerId": "EXAMPLE_SELLER",
    "sku": "EXAMPLE"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER",
  "body": {
    "productType": "EXAMPLE",
    "attributes": {}
  },
  "action": "preview"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "confirmationToken": "EXAMPLE_NOT_VALID",
    "expiresAt": 1893456000000,
    "confirmationRequired": true,
    "summary": {
      "connectionId": 123,
      "sellerId": "EXAMPLE_SELLER",
      "marketplaceId": "ATVPDKIKX0DER",
      "region": "NA",
      "method": "PUT",
      "path": "/listings/2021-08-01/items/EXAMPLE_SELLER/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-listings-searchlistingsitems`

MCP tool: `nexscope_amazon_sp_api_listings_searchlistingsitems`.

Amazon operation: `GET /listings/2021-08-01/items/{sellerId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerId": "EXAMPLE_SELLER"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER"
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
        "numberOfResults": 1,
        "items": [
          {
            "sku": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-product-types-getdefinitionsproducttype`

MCP tool: `nexscope_amazon_sp_api_product_types_getdefinitionsproducttype`.

Amazon operation: `GET /definitions/2020-09-01/productTypes/{productType}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: productType.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "productType": "EXAMPLE"
  },
  "queryString": "marketplaceIds=ATVPDKIKX0DER"
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
        "locale": "en_US",
        "marketplaceIds": [
          "ATVPDKIKX0DER"
        ],
        "productType": "EXAMPLE",
        "displayName": "EXAMPLE",
        "productTypeVersion": {
          "latest": false,
          "version": "EXAMPLE"
        },
        "propertyGroups": {},
        "requirements": "LISTING",
        "requirementsEnforced": "ENFORCED",
        "schema": {
          "checksum": "EXAMPLE",
          "link": {
            "resource": "EXAMPLE",
            "verb": "GET"
          }
        }
      }
    }
  }
}
```

### `amazon-sp-api-product-types-searchdefinitionsproducttypes`

MCP tool: `nexscope_amazon_sp_api_product_types_searchdefiniti_bcca1638e413`.

Amazon operation: `GET /definitions/2020-09-01/productTypes`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceIds=ATVPDKIKX0DER"
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
        "productTypes": [
          {
            "marketplaceIds": [
              "ATVPDKIKX0DER"
            ],
            "name": "EXAMPLE",
            "displayName": "EXAMPLE"
          }
        ],
        "productTypeVersion": "EXAMPLE"
      }
    }
  }
}
```
