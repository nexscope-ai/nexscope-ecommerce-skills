# Amazon FBA Inventory API reference

Migration reference: `linkfox-amazon-store-fba` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `getItemEligibilityPreview` | `/spapi/getItemEligibilityPreview` | Authorized connection where required |
| `getBillOfLading` | `/spapi/getBillOfLading` | Authorized connection where required |
| `getLabels` | `/spapi/getLabels` | Authorized connection where required |
| `getPrepInstructions` | `/spapi/getPrepInstructions` | Authorized connection where required |
| `getShipmentItems` | `/spapi/getShipmentItems` | Authorized connection where required |
| `getShipmentItemsByShipmentId` | `/spapi/getShipmentItemsByShipmentId` | Authorized connection where required |
| `getShipmentsV0` | `/spapi/getShipmentsV0` | Authorized connection where required |
| `addInventory` | `/spapi/addInventory` | Amazon sandbox only |
| `createInventoryItem` | `/spapi/createInventoryItem` | Amazon sandbox only |
| `deleteInventoryItem` | `/spapi/deleteInventoryItem` | Amazon sandbox only |
| `getInventorySummaries` | `/spapi/getInventorySummaries` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-eligibility-get-item-eligibility-preview`

MCP tool: `nexscope_amazon_sp_api_eligibility_get_item_eligibility_preview`.

Amazon operation: `GET /fba/inbound/v1/eligibility/itemPreview`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "asin=B000EXAMPL&program=INBOUND"
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
          "asin": "B000EXAMPL",
          "isEligibleForProgram": false,
          "program": "INBOUND"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-bill-of-lading`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_bill_of_lading`.

Amazon operation: `GET /fba/inbound/v0/shipments/{shipmentId}/billOfLading`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
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
        "payload": {
          "DownloadURL": "https://example.invalid/amazon-sp-api-fixture"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-labels`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_labels`.

Amazon operation: `GET /fba/inbound/v0/shipments/{shipmentId}/labels`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
  },
  "queryString": "PageType=PackageLabel_Letter_2&LabelType=BARCODE_2D"
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
          "DownloadURL": "https://example.invalid/amazon-sp-api-fixture"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-prep-instructions`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_prep_instructions`.

Amazon operation: `GET /fba/inbound/v0/prepInstructions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "ShipToCountryCode=EXAMPLE"
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
          "SKUPrepInstructionsList": [
            {}
          ],
          "InvalidSKUList": [
            {}
          ],
          "ASINPrepInstructionsList": [
            {}
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-shipment-items`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_shipment_items`.

Amazon operation: `GET /fba/inbound/v0/shipmentItems`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "QueryType=DATE_RANGE&MarketplaceId=ATVPDKIKX0DER"
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
          "ItemData": [
            {
              "QuantityShipped": 1,
              "SellerSKU": "EXAMPLE"
            }
          ],
          "NextToken": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-shipment-items-by-shipment-id`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_shipment_item_5db3eda79e03`.

Amazon operation: `GET /fba/inbound/v0/shipments/{shipmentId}/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
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
        "payload": {
          "ItemData": [
            {
              "QuantityShipped": 1,
              "SellerSKU": "EXAMPLE"
            }
          ],
          "NextToken": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-v0-get-shipments-v0`

MCP tool: `nexscope_amazon_sp_api_inbound_v0_get_shipments_v0`.

Amazon operation: `GET /fba/inbound/v0/shipments`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "QueryType=SHIPMENT&MarketplaceId=ATVPDKIKX0DER"
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
          "ShipmentData": [
            {
              "AreCasesRequired": false,
              "ShipFromAddress": {
                "AddressLine1": "EXAMPLE",
                "City": "EXAMPLE",
                "CountryCode": "US",
                "Name": "EXAMPLE",
                "PostalCode": "00000",
                "StateOrProvinceCode": "EXAMPLE"
              }
            }
          ],
          "NextToken": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inventory-add-inventory`

MCP tool: `nexscope_amazon_sp_api_inventory_add_inventory`.

Amazon operation: `POST /fba/inventory/v1/items/inventory`.
This Amazon operation runs only in the sandbox.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "inventoryItems": [
      {
        "sellerSku": "EXAMPLE",
        "marketplaceId": "ATVPDKIKX0DER",
        "quantity": 1
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
      "method": "POST",
      "path": "/fba/inventory/v1/items/inventory"
    }
  }
}
```

### `amazon-sp-api-inventory-create-inventory-item`

MCP tool: `nexscope_amazon_sp_api_inventory_create_inventory_item`.

Amazon operation: `POST /fba/inventory/v1/items`.
This Amazon operation runs only in the sandbox.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "sellerSku": "EXAMPLE",
    "marketplaceId": "ATVPDKIKX0DER",
    "productName": "EXAMPLE"
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
      "method": "POST",
      "path": "/fba/inventory/v1/items"
    }
  }
}
```

### `amazon-sp-api-inventory-delete-inventory-item`

MCP tool: `nexscope_amazon_sp_api_inventory_delete_inventory_item`.

Amazon operation: `DELETE /fba/inventory/v1/items/{sellerSku}`.
This Amazon operation runs only in the sandbox.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerSku.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerSku": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER",
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
      "path": "/fba/inventory/v1/items/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-inventory-get-inventory-summaries`

MCP tool: `nexscope_amazon_sp_api_inventory_get_inventory_summaries`.

Amazon operation: `GET /fba/inventory/v1/summaries`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "granularityType=Marketplace&granularityId=ATVPDKIKX0DER&marketplaceIds=ATVPDKIKX0DER"
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
          "granularity": {},
          "inventorySummaries": [
            {}
          ]
        },
        "pagination": {
          "nextToken": "EXAMPLE"
        }
      }
    }
  }
}
```
