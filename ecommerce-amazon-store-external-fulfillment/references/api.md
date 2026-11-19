# Amazon External Fulfillment API reference

Migration reference: `linkfox-amazon-store-external-fulfillment` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `batchInventory` | `/spapi/batchInventory` | Authorized connection where required |
| `createPackages` | `/spapi/createPackages` | Authorized connection where required |
| `generateInvoice` | `/spapi/generateInvoice` | Authorized connection where required |
| `generateShipLabels` | `/spapi/generateShipLabels` | Authorized connection where required |
| `getReturn` | `/spapi/getReturn` | Authorized connection where required |
| `getShipment` | `/spapi/externalFulfillmentGetShipment` | Authorized connection where required |
| `getShipments` | `/spapi/getShipments` | Authorized connection where required |
| `listReturns` | `/spapi/listReturns` | Authorized connection where required |
| `processShipment` | `/spapi/processShipment` | Authorized connection where required |
| `retrieveInvoice` | `/spapi/retrieveInvoice` | Authorized connection where required |
| `retrieveShippingOptions` | `/spapi/retrieveShippingOptions` | Authorized connection where required |
| `updatePackage` | `/spapi/externalFulfillmentUpdatePackage` | Authorized connection where required |
| `updatePackageStatus` | `/spapi/updatePackageStatus` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-external-fulfillment-batch-inventory`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_batch_inventory`.

Amazon operation: `POST /externalFulfillment/inventory/2024-09-11/inventories`.
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
    "requests": [
      {
        "uri": "EXAMPLE",
        "method": "GET"
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
      "path": "/externalFulfillment/inventory/2024-09-11/inventories"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-create-packages`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_create_packages`.

Amazon operation: `POST /externalFulfillment/2024-09-11/shipments/{shipmentId}/packages`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
  },
  "body": {
    "packages": [
      {
        "dimensions": {
          "length": {
            "value": 1,
            "dimensionUnit": "CM"
          },
          "width": {
            "value": 1,
            "dimensionUnit": "CM"
          },
          "height": {
            "value": 1,
            "dimensionUnit": "CM"
          }
        },
        "id": "EXAMPLE",
        "weight": {
          "value": 1,
          "weightUnit": "G"
        },
        "packageLineItems": [
          {
            "packageLineItemId": "EXAMPLE",
            "quantity": 1
          }
        ]
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
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE/packages"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-generate-invoice`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_generate_invoice`.

Amazon operation: `POST /externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
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
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE/invoice"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-generate-ship-labels`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_generate_ship_labels`.

Amazon operation: `PUT /externalFulfillment/2024-09-11/shipments/{shipmentId}/shipLabels`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
  },
  "queryString": "operation=GENERATE",
  "body": {
    "packageIds": [
      "EXAMPLE"
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
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE/shipLabels"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-get-return`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_get_return`.

Amazon operation: `GET /externalFulfillment/2024-09-11/returns/{returnId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: returnId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "returnId": "EXAMPLE"
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
        "id": "EXAMPLE",
        "returnMetadata": {
          "returnReason": "EXAMPLE"
        },
        "status": "CREATED",
        "fulfillmentLocationId": "EXAMPLE",
        "returnType": "CUSTOMER",
        "lastUpdatedDateTime": "EXAMPLE",
        "returnShippingInfo": {
          "deliveryDateTime": "EXAMPLE",
          "pickupDateTime": "EXAMPLE",
          "forwardTrackingInfo": {
            "carrierName": "EXAMPLE",
            "trackingId": "EXAMPLE"
          }
        },
        "marketplaceChannelDetails": {
          "marketplaceChannel": {},
          "merchantId": "EXAMPLE",
          "shipmentId": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-get-shipment`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_get_shipment`.

Amazon operation: `GET /externalFulfillment/2024-09-11/shipments/{shipmentId}`.
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
        "id": "EXAMPLE",
        "locationId": "EXAMPLE",
        "marketplaceAttributes": {
          "marketplaceId": "ATVPDKIKX0DER",
          "channelName": "EXAMPLE"
        },
        "shipmentInfo": {
          "shipmentType": "NEW",
          "numberOfUnits": 1,
          "priority": "HIGH",
          "buyerOrderId": "EXAMPLE"
        },
        "shipmentRequirements": {
          "pSlip": {},
          "invoice": {}
        },
        "charges": [
          {
            "baseCharge": {
              "baseAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "discountAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "netAmount": {
                "value": 1,
                "currencyCode": "USD"
              }
            },
            "chargeType": "product",
            "totalCharge": {
              "baseAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "discountAmount": {
                "value": 1,
                "currencyCode": "USD"
              },
              "netAmount": {
                "value": 1,
                "currencyCode": "USD"
              }
            },
            "totalTax": {
              "charge": {
                "baseAmount": {
                  "value": 1,
                  "currencyCode": "USD"
                },
                "discountAmount": {
                  "value": 1,
                  "currencyCode": "USD"
                },
                "netAmount": {
                  "value": 1,
                  "currencyCode": "USD"
                }
              }
            }
          }
        ],
        "status": "CREATED",
        "lineItems": [
          {
            "charges": [
              {
                "baseCharge": {
                  "baseAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "discountAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "netAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  }
                },
                "chargeType": "product",
                "totalCharge": {
                  "baseAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "discountAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "netAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  }
                },
                "totalTax": {
                  "charge": {
                    "baseAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    },
                    "discountAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    },
                    "netAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              }
            ],
            "merchantSku": "EXAMPLE",
            "numberOfUnits": 1,
            "shipmentLineItemId": "EXAMPLE",
            "complianceAttributes": {
              "serialNumberRequirement": "REQUIRED",
              "hazmatLabelsRequirement": "REQUIRED"
            }
          }
        ],
        "shippingInfo": {
          "expectedShippingDateTimeInUTC": "2026-01-01T00:00:00Z"
        },
        "creationDateTime": "2026-01-01T00:00:00Z",
        "lastUpdatedDateTime": "2026-01-01T00:00:00Z"
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-get-shipments`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_get_shipments`.

Amazon operation: `GET /externalFulfillment/2024-09-11/shipments`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "status=CREATED"
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
        "shipments": [
          {
            "id": "EXAMPLE",
            "locationId": "EXAMPLE",
            "marketplaceAttributes": {
              "marketplaceId": "ATVPDKIKX0DER",
              "channelName": "EXAMPLE"
            },
            "shipmentInfo": {
              "shipmentType": "NEW",
              "numberOfUnits": 1,
              "priority": "HIGH",
              "buyerOrderId": "EXAMPLE"
            },
            "shipmentRequirements": {
              "pSlip": {},
              "invoice": {}
            },
            "charges": [
              {
                "baseCharge": {
                  "baseAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "discountAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "netAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  }
                },
                "chargeType": "product",
                "totalCharge": {
                  "baseAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "discountAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  },
                  "netAmount": {
                    "value": 1,
                    "currencyCode": "USD"
                  }
                },
                "totalTax": {
                  "charge": {
                    "baseAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    },
                    "discountAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    },
                    "netAmount": {
                      "value": 1,
                      "currencyCode": "USD"
                    }
                  }
                }
              }
            ],
            "status": "CREATED",
            "lineItems": [
              {
                "charges": [
                  {
                    "baseCharge": {
                      "baseAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      },
                      "discountAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      },
                      "netAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      }
                    },
                    "chargeType": "product",
                    "totalCharge": {
                      "baseAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      },
                      "discountAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      },
                      "netAmount": {
                        "value": 1,
                        "currencyCode": "USD"
                      }
                    },
                    "totalTax": {
                      "charge": {
                        "baseAmount": {
                          "value": 1,
                          "currencyCode": "USD"
                        },
                        "discountAmount": {
                          "value": 1,
                          "currencyCode": "USD"
                        },
                        "netAmount": {
                          "value": 1,
                          "currencyCode": "USD"
                        }
                      }
                    }
                  }
                ],
                "merchantSku": "EXAMPLE",
                "numberOfUnits": 1,
                "shipmentLineItemId": "EXAMPLE",
                "complianceAttributes": {
                  "serialNumberRequirement": "REQUIRED",
                  "hazmatLabelsRequirement": "REQUIRED"
                }
              }
            ],
            "shippingInfo": {
              "expectedShippingDateTimeInUTC": "2026-01-01T00:00:00Z"
            },
            "creationDateTime": "2026-01-01T00:00:00Z",
            "lastUpdatedDateTime": "2026-01-01T00:00:00Z"
          }
        ],
        "pagination": {
          "nextToken": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-list-returns`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_list_returns`.

Amazon operation: `GET /externalFulfillment/2024-09-11/returns`.
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
        "returns": [
          {
            "id": "EXAMPLE",
            "returnMetadata": {
              "returnReason": "EXAMPLE"
            },
            "status": "CREATED",
            "fulfillmentLocationId": "EXAMPLE",
            "returnType": "CUSTOMER",
            "lastUpdatedDateTime": "EXAMPLE",
            "returnShippingInfo": {},
            "marketplaceChannelDetails": {}
          }
        ],
        "nextToken": "EXAMPLE"
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-process-shipment`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_process_shipment`.

Amazon operation: `POST /externalFulfillment/2024-09-11/shipments/{shipmentId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE"
  },
  "queryString": "operation=CONFIRM",
  "body": {
    "lineItems": [
      {
        "lineItem": {
          "id": "EXAMPLE"
        }
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
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-retrieve-invoice`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_retrieve_invoice`.

Amazon operation: `GET /externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`.
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
        "document": {
          "format": "ZPL",
          "content": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-retrieve-shipping-options`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_retriev_e8a93dbacfcd`.

Amazon operation: `GET /externalFulfillment/2024-09-11/shipments/{shipmentId}/shippingOptions`.
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
  "queryString": "packageId=EXAMPLE"
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
        "shippingOptions": [
          {
            "shippingOptionId": "EXAMPLE",
            "shipBy": "MARKETPLACE"
          }
        ],
        "recommendedShippingOption": {
          "shippingOptionId": "EXAMPLE",
          "shipBy": "MARKETPLACE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-update-package`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_update_package`.

Amazon operation: `PUT /externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId, packageId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE",
    "packageId": "EXAMPLE"
  },
  "body": {
    "dimensions": {
      "length": {
        "value": 1,
        "dimensionUnit": "CM"
      },
      "width": {
        "value": 1,
        "dimensionUnit": "CM"
      },
      "height": {
        "value": 1,
        "dimensionUnit": "CM"
      }
    },
    "id": "EXAMPLE",
    "weight": {
      "value": 1,
      "weightUnit": "G"
    },
    "packageLineItems": [
      {
        "packageLineItemId": "EXAMPLE",
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
      "method": "PUT",
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE/packages/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-external-fulfillment-update-package-status`

MCP tool: `nexscope_amazon_sp_api_external_fulfillment_update__cb240063a5f5`.

Amazon operation: `PATCH /externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: shipmentId, packageId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "shipmentId": "EXAMPLE",
    "packageId": "EXAMPLE"
  },
  "body": {
    "status": "SHIPPED",
    "subStatus": "OUT_FOR_DELIVERY",
    "reason": "EXAMPLE"
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
      "path": "/externalFulfillment/2024-09-11/shipments/EXAMPLE/packages/EXAMPLE"
    }
  }
}
```
