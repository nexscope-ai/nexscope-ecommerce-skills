# Amazon Fulfillment Outbound API reference

Migration reference: `linkfox-amazon-store-fulfillment-outbound` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `getInvoiceHeaders` | `/spapi/getInvoiceHeaders` | Authorized connection where required |
| `cancelOrder` | `/spapi/cancelOrder` | Authorized connection where required |
| `createOrder` | `/spapi/createOrder` | Authorized connection where required |
| `getOffers` | `/spapi/getOffers` | Authorized connection where required |
| `getOrder` | `/spapi/getOrder` | Authorized connection where required |
| `getOrderPreview` | `/spapi/getOrderPreview` | Authorized connection where required |
| `listOrders` | `/spapi/listOrders` | Authorized connection where required |
| `updateOrder` | `/spapi/updateOrder` | Authorized connection where required |
| `updateOrderStatus` | `/spapi/updateOrderStatus` | Amazon sandbox only |
| `updatePackage` | `/spapi/outbound2026UpdatePackage` | Amazon sandbox only |
| `cancelFulfillmentOrder` | `/spapi/cancelFulfillmentOrder` | Authorized connection where required |
| `createFulfillmentOrder` | `/spapi/createFulfillmentOrder` | Authorized connection where required |
| `createFulfillmentReturn` | `/spapi/createFulfillmentReturn` | Authorized connection where required |
| `deliveryOffers` | `/spapi/deliveryOffers` | Authorized connection where required |
| `getFeatureInventory` | `/spapi/getFeatureInventory` | Authorized connection where required |
| `getFeatureSKU` | `/spapi/getFeatureSKU` | Authorized connection where required |
| `getFeatures` | `/spapi/getFeatures` | Authorized connection where required |
| `getFulfillmentOrder` | `/spapi/getFulfillmentOrder` | Authorized connection where required |
| `getFulfillmentPreview` | `/spapi/getFulfillmentPreview` | Authorized connection where required |
| `getPackageTrackingDetails` | `/spapi/getPackageTrackingDetails` | Authorized connection where required |
| `listAllFulfillmentOrders` | `/spapi/listAllFulfillmentOrders` | Authorized connection where required |
| `listReturnReasonCodes` | `/spapi/listReturnReasonCodes` | Authorized connection where required |
| `submitFulfillmentOrderStatusUpdate` | `/spapi/submitFulfillmentOrderStatusUpdate` | Amazon sandbox only |
| `updateFulfillmentOrder` | `/spapi/updateFulfillmentOrder` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-invoices-get-invoice-headers`

MCP tool: `nexscope_amazon_sp_api_invoices_get_invoice_headers`.

Amazon operation: `GET /finances/invoices/2026-06-25/invoices`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER"
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
        "invoices": [
          {
            "invoiceNumber": "EXAMPLE",
            "invoiceIdentifier": "EXAMPLE",
            "invoiceStatus": "IN_PROGRESS",
            "invoiceType": "AP_INVENTORY",
            "payer": {
              "partnerId": "EXAMPLE",
              "partnerType": "SELLER"
            },
            "payee": {
              "partnerId": "EXAMPLE",
              "partnerType": "SELLER"
            },
            "issueDate": "2026-01-01T00:00:00Z",
            "invoiceAmount": {
              "currencyCode": "USD",
              "currencyAmount": 1
            },
            "creationDate": "2026-01-01T00:00:00Z",
            "lastUpdatedDate": "2026-01-01T00:00:00Z"
          }
        ],
        "numOfRecords": 1,
        "nextToken": "EXAMPLE"
      }
    }
  }
}
```

### `amazon-sp-api-outbound-2026-cancel-order`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_cancel_order`.

Amazon operation: `PUT /fulfillment/outbound/2026-07-04/orders/{orderId}/cancel`.
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
      "path": "/fulfillment/outbound/2026-07-04/orders/000-0000000-0000000/cancel"
    }
  }
}
```

### `amazon-sp-api-outbound-2026-create-order`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_create_order`.

Amazon operation: `POST /fulfillment/outbound/2026-07-04/orders`.
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
    "orderId": "000-0000000-0000000",
    "lineItems": [
      {
        "lineItemId": "EXAMPLE",
        "product": {
          "productIdentifier": {
            "amazonSku": "EXAMPLE"
          }
        },
        "amount": {
          "value": "EXAMPLE"
        }
      }
    ],
    "destination": {
      "deliveryAddress": {
        "addressLine1": "EXAMPLE",
        "countryCode": "US",
        "name": "EXAMPLE",
        "postalCode": "00000"
      }
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
      "path": "/fulfillment/outbound/2026-07-04/orders"
    }
  }
}
```

### `amazon-sp-api-outbound-2026-get-offers`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_get_offers`.

Amazon operation: `POST /fulfillment/outbound/2026-07-04/offers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "items": [
      {}
    ],
    "origin": {
      "countryCode": "US"
    }
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
        "offerResults": [
          {}
        ]
      }
    }
  }
}
```

### `amazon-sp-api-outbound-2026-get-order`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_get_order`.

Amazon operation: `GET /fulfillment/outbound/2026-07-04/orders/{orderId}`.
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
          "receiveTime": "2026-01-01T00:00:00Z",
          "lineItems": [
            {
              "lineItemId": "EXAMPLE",
              "product": {
                "productIdentifier": {
                  "amazonSku": "EXAMPLE"
                }
              },
              "amount": {
                "value": "EXAMPLE"
              }
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-2026-get-order-preview`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_get_order_preview`.

Amazon operation: `POST /fulfillment/outbound/2026-07-04/previews`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "lineItems": [
      {
        "product": {
          "productIdentifier": {
            "amazonSku": "EXAMPLE"
          }
        },
        "amount": {
          "value": "EXAMPLE"
        }
      }
    ],
    "destination": {
      "deliveryAddress": {
        "addressLine1": "EXAMPLE",
        "countryCode": "US",
        "name": "EXAMPLE",
        "postalCode": "00000"
      }
    }
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
        "plannedShipments": [
          {
            "items": [
              {
                "productIdentifier": {
                  "amazonSku": "EXAMPLE"
                },
                "amount": {
                  "value": "EXAMPLE"
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-outbound-2026-list-orders`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_list_orders`.

Amazon operation: `GET /fulfillment/outbound/2026-07-04/orders`.
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
            "receiveTime": "2026-01-01T00:00:00Z",
            "lineItems": [
              {
                "lineItemId": "EXAMPLE",
                "product": {
                  "productIdentifier": {
                    "amazonSku": "EXAMPLE"
                  }
                },
                "amount": {
                  "value": "EXAMPLE"
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-outbound-2026-update-order`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_update_order`.

Amazon operation: `PUT /fulfillment/outbound/2026-07-04/orders/{orderId}`.
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
    "fulfillmentConfiguration": {
      "action": "EXAMPLE"
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
      "method": "PUT",
      "path": "/fulfillment/outbound/2026-07-04/orders/000-0000000-0000000"
    }
  }
}
```

### `amazon-sp-api-outbound-2026-update-order-status`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_update_order_status`.

Amazon operation: `PUT /fulfillment/outbound/2026-07-04/orders/{orderId}/status`.
This Amazon operation runs only in the sandbox.
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
    "status": "EXAMPLE"
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
      "path": "/fulfillment/outbound/2026-07-04/orders/000-0000000-0000000/status"
    }
  }
}
```

### `amazon-sp-api-outbound-2026-update-package`

MCP tool: `nexscope_amazon_sp_api_outbound_2026_update_package`.

Amazon operation: `PUT /fulfillment/outbound/2026-07-04/orders/{orderId}/packages/{packageId}`.
This Amazon operation runs only in the sandbox.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: orderId, packageId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "orderId": "000-0000000-0000000",
    "packageId": "EXAMPLE"
  },
  "body": {
    "status": "EXAMPLE"
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
      "path": "/fulfillment/outbound/2026-07-04/orders/000-0000000-0000000/packages/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-outbound-cancel-fulfillment-order`

MCP tool: `nexscope_amazon_sp_api_outbound_cancel_fulfillment_order`.

Amazon operation: `PUT /fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/cancel`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerFulfillmentOrderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerFulfillmentOrderId": "EXAMPLE"
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
      "path": "/fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE/cancel"
    }
  }
}
```

### `amazon-sp-api-outbound-create-fulfillment-order`

MCP tool: `nexscope_amazon_sp_api_outbound_create_fulfillment_order`.

Amazon operation: `POST /fba/outbound/2020-07-01/fulfillmentOrders`.
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
    "destinationAddress": {
      "addressLine1": "EXAMPLE",
      "countryCode": "US",
      "name": "EXAMPLE",
      "postalCode": "00000"
    },
    "displayableOrderComment": "EXAMPLE",
    "displayableOrderDate": "2026-01-01T00:00:00Z",
    "displayableOrderId": "EXAMPLE",
    "items": [
      {
        "quantity": 1,
        "sellerFulfillmentOrderItemId": "EXAMPLE",
        "sellerSku": "EXAMPLE"
      }
    ],
    "sellerFulfillmentOrderId": "EXAMPLE",
    "shippingSpeedCategory": "Standard"
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
      "path": "/fba/outbound/2020-07-01/fulfillmentOrders"
    }
  }
}
```

### `amazon-sp-api-outbound-create-fulfillment-return`

MCP tool: `nexscope_amazon_sp_api_outbound_create_fulfillment_return`.

Amazon operation: `PUT /fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/return`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerFulfillmentOrderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerFulfillmentOrderId": "EXAMPLE"
  },
  "body": {
    "items": [
      {
        "amazonShipmentId": "EXAMPLE",
        "returnReasonCode": "EXAMPLE",
        "sellerFulfillmentOrderItemId": "EXAMPLE",
        "sellerReturnItemId": "EXAMPLE"
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
      "method": "PUT",
      "path": "/fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE/return"
    }
  }
}
```

### `amazon-sp-api-outbound-delivery-offers`

MCP tool: `nexscope_amazon_sp_api_outbound_delivery_offers`.

Amazon operation: `POST /fba/outbound/2020-07-01/deliveryOffers`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "product": {
      "productIdentifier": {
        "merchantSku": "EXAMPLE"
      }
    },
    "terms": {
      "origin": {
        "countryCode": "US"
      },
      "destination": {}
    }
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
          "deliveryOffers": [
            {}
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-feature-inventory`

MCP tool: `nexscope_amazon_sp_api_outbound_get_feature_inventory`.

Amazon operation: `GET /fba/outbound/2020-07-01/features/inventory/{featureName}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: featureName.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "featureName": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
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
          "featureName": "EXAMPLE",
          "marketplaceId": "ATVPDKIKX0DER"
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-feature-sku`

MCP tool: `nexscope_amazon_sp_api_outbound_get_feature_sku`.

Amazon operation: `GET /fba/outbound/2020-07-01/features/inventory/{featureName}/{sellerSku}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: featureName, sellerSku.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "featureName": "EXAMPLE",
    "sellerSku": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER"
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
          "featureName": "EXAMPLE",
          "isEligible": false,
          "marketplaceId": "ATVPDKIKX0DER"
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-features`

MCP tool: `nexscope_amazon_sp_api_outbound_get_features`.

Amazon operation: `GET /fba/outbound/2020-07-01/features`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER"
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
          "features": [
            {
              "featureDescription": "EXAMPLE",
              "featureName": "EXAMPLE"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-fulfillment-order`

MCP tool: `nexscope_amazon_sp_api_outbound_get_fulfillment_order`.

Amazon operation: `GET /fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerFulfillmentOrderId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerFulfillmentOrderId": "EXAMPLE"
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
          "fulfillmentOrder": {
            "destinationAddress": {
              "addressLine1": "EXAMPLE",
              "countryCode": "US",
              "name": "EXAMPLE",
              "postalCode": "00000"
            },
            "displayableOrderComment": "EXAMPLE",
            "displayableOrderDate": "2026-01-01T00:00:00Z",
            "displayableOrderId": "EXAMPLE",
            "fulfillmentOrderStatus": "New",
            "marketplaceId": "ATVPDKIKX0DER",
            "receivedDate": "2026-01-01T00:00:00Z",
            "sellerFulfillmentOrderId": "EXAMPLE",
            "shippingSpeedCategory": "Standard",
            "statusUpdatedDate": "2026-01-01T00:00:00Z"
          },
          "fulfillmentOrderItems": [
            {
              "cancelledQuantity": 1,
              "quantity": 1,
              "sellerFulfillmentOrderItemId": "EXAMPLE",
              "sellerSku": "EXAMPLE",
              "unfulfillableQuantity": 1
            }
          ],
          "returnAuthorizations": [
            {
              "amazonRmaId": "EXAMPLE",
              "fulfillmentCenterId": "EXAMPLE",
              "returnAuthorizationId": "EXAMPLE",
              "returnToAddress": {
                "addressLine1": "EXAMPLE",
                "countryCode": "US",
                "name": "EXAMPLE",
                "postalCode": "00000"
              },
              "rmaPageURL": "https://example.invalid/amazon-sp-api-fixture"
            }
          ],
          "returnItems": [
            {
              "amazonShipmentId": "EXAMPLE",
              "sellerFulfillmentOrderItemId": "EXAMPLE",
              "sellerReturnItemId": "EXAMPLE",
              "sellerReturnReasonCode": "EXAMPLE",
              "status": "New",
              "statusChangedDate": "2026-01-01T00:00:00Z"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-fulfillment-preview`

MCP tool: `nexscope_amazon_sp_api_outbound_get_fulfillment_preview`.

Amazon operation: `POST /fba/outbound/2020-07-01/fulfillmentOrders/preview`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "body": {
    "address": {
      "addressLine1": "EXAMPLE",
      "countryCode": "US",
      "name": "EXAMPLE",
      "postalCode": "00000"
    },
    "items": [
      {
        "quantity": 1,
        "sellerFulfillmentOrderItemId": "EXAMPLE",
        "sellerSku": "EXAMPLE"
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
        "payload": {
          "fulfillmentPreviews": [
            {
              "isCODCapable": false,
              "isFulfillable": false,
              "marketplaceId": "ATVPDKIKX0DER",
              "shippingSpeedCategory": "Standard"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-get-package-tracking-details`

MCP tool: `nexscope_amazon_sp_api_outbound_get_package_tracking_details`.

Amazon operation: `GET /fba/outbound/2020-07-01/tracking`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "packageNumber=1"
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
          "packageNumber": 1
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-list-all-fulfillment-orders`

MCP tool: `nexscope_amazon_sp_api_outbound_list_all_fulfillment_orders`.

Amazon operation: `GET /fba/outbound/2020-07-01/fulfillmentOrders`.
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
        "payload": {
          "nextToken": "EXAMPLE",
          "fulfillmentOrders": [
            {
              "destinationAddress": {
                "addressLine1": "EXAMPLE",
                "countryCode": "US",
                "name": "EXAMPLE",
                "postalCode": "00000"
              },
              "displayableOrderComment": "EXAMPLE",
              "displayableOrderDate": "2026-01-01T00:00:00Z",
              "displayableOrderId": "EXAMPLE",
              "fulfillmentOrderStatus": "New",
              "marketplaceId": "ATVPDKIKX0DER",
              "receivedDate": "2026-01-01T00:00:00Z",
              "sellerFulfillmentOrderId": "EXAMPLE",
              "shippingSpeedCategory": "Standard",
              "statusUpdatedDate": "2026-01-01T00:00:00Z"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-list-return-reason-codes`

MCP tool: `nexscope_amazon_sp_api_outbound_list_return_reason_codes`.

Amazon operation: `GET /fba/outbound/2020-07-01/returnReasonCodes`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "sellerSku=EXAMPLE"
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
          "reasonCodeDetails": [
            {
              "description": "EXAMPLE",
              "returnReasonCode": "EXAMPLE"
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-outbound-submit-fulfillment-order-status-update`

MCP tool: `nexscope_amazon_sp_api_outbound_submit_fulfillment__ca58fff49c24`.

Amazon operation: `PUT /fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}/status`.
This Amazon operation runs only in the sandbox.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerFulfillmentOrderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerFulfillmentOrderId": "EXAMPLE"
  },
  "body": {
    "fulfillmentOrderStatus": "New"
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
      "path": "/fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE/status"
    }
  }
}
```

### `amazon-sp-api-outbound-update-fulfillment-order`

MCP tool: `nexscope_amazon_sp_api_outbound_update_fulfillment_order`.

Amazon operation: `PUT /fba/outbound/2020-07-01/fulfillmentOrders/{sellerFulfillmentOrderId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: sellerFulfillmentOrderId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "sellerFulfillmentOrderId": "EXAMPLE"
  },
  "body": {
    "items": [
      {
        "quantity": 1,
        "sellerFulfillmentOrderItemId": "EXAMPLE"
      }
    ],
    "marketplaceId": "ATVPDKIKX0DER",
    "displayableOrderId": "EXAMPLE"
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
      "path": "/fba/outbound/2020-07-01/fulfillmentOrders/EXAMPLE"
    }
  }
}
```
