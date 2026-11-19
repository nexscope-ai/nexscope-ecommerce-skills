# Amazon Store Orders API reference

Migration reference: `linkfox-amazon-store-orders` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `confirmshipment` | `/spapi/confirmShipment` | Authorized connection where required |
| `getorder-3` | `/spapi/getorder3` | Authorized connection where required |
| `getorderaddress` | `/spapi/getOrderAddress` | Authorized connection where required |
| `getorderbuyerinfo` | `/spapi/getOrderBuyerInfo` | Authorized connection where required |
| `getorderitems` | `/spapi/getOrderItems` | Authorized connection where required |
| `getorderitemsbuyerinfo` | `/spapi/getOrderItemsBuyerInfo` | Authorized connection where required |
| `getorderregulatedinfo` | `/spapi/getOrderRegulatedInfo` | Authorized connection where required |
| `searchorders` | `/spapi/searchOrders` | Authorized connection where required |
| `updateshipmentstatus` | `/spapi/updateShipmentStatus` | Authorized connection where required |
| `updateverificationstatus` | `/spapi/updateVerificationStatus` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-orders-confirmshipment`

MCP tool: `nexscope_amazon_sp_api_orders_confirmshipment`.

Amazon operation: `POST /orders/v0/orders/{orderId}/shipmentConfirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
  },
  "body": {
    "marketplaceId": "ATVPDKIKX0DER",
    "packageDetail": {
      "packageReferenceId": "EXAMPLE",
      "carrierCode": "EXAMPLE",
      "trackingNumber": "EXAMPLE",
      "shipDate": "2026-01-01T00:00:00Z",
      "orderItems": [
        {
          "orderItemId": "EXAMPLE",
          "quantity": 1
        }
      ]
    }
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
      "path": "/orders/v0/orders/000-0000000-0000000/shipmentConfirmation"
    }
  }
}
```

### `amazon-sp-api-orders-getorder-3`

MCP tool: `nexscope_amazon_sp_api_orders_getorder_3`.

Amazon operation: `GET /orders/2026-01-01/orders/{orderId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
        "order": {
          "orderId": "000-0000000-0000000",
          "createdTime": "2026-01-01T00:00:00Z",
          "lastUpdatedTime": "2026-01-01T00:00:00Z",
          "salesChannel": {
            "channelName": "EXAMPLE"
          },
          "orderItems": [
            {
              "orderItemId": "EXAMPLE",
              "quantityOrdered": 1,
              "product": {}
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-getorderaddress`

MCP tool: `nexscope_amazon_sp_api_orders_getorderaddress`.

Amazon operation: `GET /orders/v0/orders/{orderId}/address`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
          "AmazonOrderId": "000-0000000-0000000"
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-getorderbuyerinfo`

MCP tool: `nexscope_amazon_sp_api_orders_getorderbuyerinfo`.

Amazon operation: `GET /orders/v0/orders/{orderId}/buyerInfo`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
          "AmazonOrderId": "000-0000000-0000000"
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-getorderitems`

MCP tool: `nexscope_amazon_sp_api_orders_getorderitems`.

Amazon operation: `GET /orders/v0/orders/{orderId}/orderItems`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
          "AmazonOrderId": "000-0000000-0000000",
          "OrderItems": [
            {
              "ASIN": "B000EXAMPL",
              "OrderItemId": "EXAMPLE",
              "QuantityOrdered": 1
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-getorderitemsbuyerinfo`

MCP tool: `nexscope_amazon_sp_api_orders_getorderitemsbuyerinfo`.

Amazon operation: `GET /orders/v0/orders/{orderId}/orderItems/buyerInfo`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
          "AmazonOrderId": "000-0000000-0000000",
          "OrderItems": [
            {
              "OrderItemId": "EXAMPLE"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-getorderregulatedinfo`

MCP tool: `nexscope_amazon_sp_api_orders_getorderregulatedinfo`.

Amazon operation: `GET /orders/v0/orders/{orderId}/regulatedInfo`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
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
          "AmazonOrderId": "000-0000000-0000000",
          "RegulatedInformation": {
            "Fields": [
              {
                "FieldId": "EXAMPLE",
                "FieldLabel": "EXAMPLE",
                "FieldType": "Text",
                "FieldValue": "EXAMPLE"
              }
            ]
          },
          "RegulatedOrderVerificationStatus": {
            "Status": "Pending",
            "RequiresMerchantAction": false,
            "ValidRejectionReasons": [
              {
                "RejectionReasonId": "EXAMPLE",
                "RejectionReasonDescription": "EXAMPLE"
              }
            ]
          },
          "RequiresDosageLabel": false
        }
      }
    }
  }
}
```

### `amazon-sp-api-orders-searchorders`

MCP tool: `nexscope_amazon_sp_api_orders_searchorders`.

Amazon operation: `GET /orders/2026-01-01/orders`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123
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
        "orders": [
          {
            "orderId": "000-0000000-0000000",
            "createdTime": "2026-01-01T00:00:00Z",
            "lastUpdatedTime": "2026-01-01T00:00:00Z",
            "salesChannel": {
              "channelName": "EXAMPLE"
            },
            "orderItems": [
              {
                "orderItemId": "EXAMPLE",
                "quantityOrdered": 1,
                "product": {}
              }
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-orders-updateshipmentstatus`

MCP tool: `nexscope_amazon_sp_api_orders_updateshipmentstatus`.

Amazon operation: `POST /orders/v0/orders/{orderId}/shipment`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
  },
  "body": {
    "marketplaceId": "ATVPDKIKX0DER",
    "shipmentStatus": "ReadyForPickup"
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
      "path": "/orders/v0/orders/000-0000000-0000000/shipment"
    }
  }
}
```

### `amazon-sp-api-orders-updateverificationstatus`

MCP tool: `nexscope_amazon_sp_api_orders_updateverificationstatus`.

Amazon operation: `PATCH /orders/v0/orders/{orderId}/regulatedInfo`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000"
  },
  "body": {
    "regulatedOrderVerificationStatus": {
      "externalReviewerId": "EXAMPLE"
    }
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
      "path": "/orders/v0/orders/000-0000000-0000000/regulatedInfo"
    }
  }
}
```
