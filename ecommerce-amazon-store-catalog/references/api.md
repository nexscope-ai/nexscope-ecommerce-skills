# Amazon Store Catalog API reference

Migration reference: `linkfox-amazon-store-catalog` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `getcatalogitem-2020-12-01` | `/spapi/getCatalogItemV20201201` | Authorized connection where required |
| `getcatalogitem-2022-04-01` | `/spapi/getCatalogItemV20220401` | Authorized connection where required |
| `listcatalogcategories` | `/spapi/listCatalogCategories` | Authorized connection where required |
| `searchcatalogitems-2020-12-01` | `/spapi/searchCatalogItemsV20201201` | Authorized connection where required |
| `searchcatalogitems-2022-04-01` | `/spapi/searchCatalogItemsV20220401` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-catalog-getcatalogitem-2020-12-01`

MCP tool: `nexscope_amazon_sp_api_catalog_getcatalogitem_2020_12_01`.

Amazon operation: `GET /catalog/2020-12-01/items/{asin}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "asin": "B000EXAMPL"
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
        "asin": "B000EXAMPL"
      }
    }
  }
}
```

### `amazon-sp-api-catalog-getcatalogitem-2022-04-01`

MCP tool: `nexscope_amazon_sp_api_catalog_getcatalogitem_2022_04_01`.

Amazon operation: `GET /catalog/2022-04-01/items/{asin}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: asin.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "asin": "B000EXAMPL"
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
        "asin": "B000EXAMPL"
      }
    }
  }
}
```

### `amazon-sp-api-catalog-listcatalogcategories`

MCP tool: `nexscope_amazon_sp_api_catalog_listcatalogcategories`.

Amazon operation: `GET /catalog/v0/categories`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "MarketplaceId=ATVPDKIKX0DER&ASIN=B000EXAMPL"
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
          {}
        ]
      }
    }
  }
}
```

### `amazon-sp-api-catalog-searchcatalogitems-2020-12-01`

MCP tool: `nexscope_amazon_sp_api_catalog_searchcatalogitems_2020_12_01`.

Amazon operation: `GET /catalog/2020-12-01/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "keywords=travel%20mug&marketplaceIds=ATVPDKIKX0DER"
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
        "pagination": {
          "nextToken": "EXAMPLE",
          "previousToken": "EXAMPLE"
        },
        "refinements": {
          "brands": [
            {
              "numberOfResults": 1,
              "brandName": "EXAMPLE"
            }
          ],
          "classifications": [
            {
              "numberOfResults": 1,
              "displayName": "EXAMPLE",
              "classificationId": "EXAMPLE"
            }
          ]
        },
        "items": [
          {
            "asin": "B000EXAMPL"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-catalog-searchcatalogitems-2022-04-01`

MCP tool: `nexscope_amazon_sp_api_catalog_searchcatalogitems_2022_04_01`.

Amazon operation: `GET /catalog/2022-04-01/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceIds=ATVPDKIKX0DER&keywords=travel%20mug"
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
            "asin": "B000EXAMPL"
          }
        ]
      }
    }
  }
}
```
