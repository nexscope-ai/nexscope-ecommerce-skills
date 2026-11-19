# Amazon Fulfillment Inbound API reference

Migration reference: `linkfox-amazon-store-fulfillment-inbound` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `cancelInboundPlan` | `/spapi/cancelInboundPlan` | Authorized connection where required |
| `cancelSelfShipAppointment` | `/spapi/cancelSelfShipAppointment` | Authorized connection where required |
| `confirmDeliveryWindowOptions` | `/spapi/confirmDeliveryWindowOptions` | Authorized connection where required |
| `confirmPackingOption` | `/spapi/confirmPackingOption` | Authorized connection where required |
| `confirmPlacementOption` | `/spapi/confirmPlacementOption` | Authorized connection where required |
| `confirmShipmentContentUpdatePreview` | `/spapi/confirmShipmentContentUpdatePreview` | Authorized connection where required |
| `confirmTransportationOptions` | `/spapi/confirmTransportationOptions` | Authorized connection where required |
| `createInboundPlan` | `/spapi/createInboundPlan` | Authorized connection where required |
| `createMarketplaceItemLabels` | `/spapi/createMarketplaceItemLabels` | Authorized connection where required |
| `generateDeliveryWindowOptions` | `/spapi/generateDeliveryWindowOptions` | Authorized connection where required |
| `generatePackingOptions` | `/spapi/generatePackingOptions` | Authorized connection where required |
| `generatePlacementOptions` | `/spapi/generatePlacementOptions` | Authorized connection where required |
| `generateSelfShipAppointmentSlots` | `/spapi/generateSelfShipAppointmentSlots` | Authorized connection where required |
| `generateShipmentContentUpdatePreviews` | `/spapi/generateShipmentContentUpdatePreviews` | Authorized connection where required |
| `generateTransportationOptions` | `/spapi/generateTransportationOptions` | Authorized connection where required |
| `getDeliveryChallanDocument` | `/spapi/getDeliveryChallanDocument` | Authorized connection where required |
| `getInboundOperationStatus` | `/spapi/getInboundOperationStatus` | Authorized connection where required |
| `getInboundPlan` | `/spapi/getInboundPlan` | Authorized connection where required |
| `getSelfShipAppointmentSlots` | `/spapi/getSelfShipAppointmentSlots` | Authorized connection where required |
| `getShipment` | `/spapi/inboundGetShipment` | Authorized connection where required |
| `getShipmentContentUpdatePreview` | `/spapi/getShipmentContentUpdatePreview` | Authorized connection where required |
| `listDeliveryWindowOptions` | `/spapi/listDeliveryWindowOptions` | Authorized connection where required |
| `listInboundPlanBoxes` | `/spapi/listInboundPlanBoxes` | Authorized connection where required |
| `listInboundPlanItems` | `/spapi/listInboundPlanItems` | Authorized connection where required |
| `listInboundPlanPallets` | `/spapi/listInboundPlanPallets` | Authorized connection where required |
| `listInboundPlans` | `/spapi/listInboundPlans` | Authorized connection where required |
| `listItemComplianceDetails` | `/spapi/listItemComplianceDetails` | Authorized connection where required |
| `listPackingGroupBoxes` | `/spapi/listPackingGroupBoxes` | Authorized connection where required |
| `listPackingGroupItems` | `/spapi/listPackingGroupItems` | Authorized connection where required |
| `listPackingOptions` | `/spapi/listPackingOptions` | Authorized connection where required |
| `listPlacementOptions` | `/spapi/listPlacementOptions` | Authorized connection where required |
| `listPrepDetails` | `/spapi/listPrepDetails` | Authorized connection where required |
| `listShipmentBoxes` | `/spapi/listShipmentBoxes` | Authorized connection where required |
| `listShipmentContentUpdatePreviews` | `/spapi/listShipmentContentUpdatePreviews` | Authorized connection where required |
| `listShipmentItems` | `/spapi/listShipmentItems` | Authorized connection where required |
| `listShipmentPallets` | `/spapi/listShipmentPallets` | Authorized connection where required |
| `listTransportationOptions` | `/spapi/listTransportationOptions` | Authorized connection where required |
| `scheduleSelfShipAppointment` | `/spapi/scheduleSelfShipAppointment` | Authorized connection where required |
| `setPackingInformation` | `/spapi/setPackingInformation` | Authorized connection where required |
| `setPrepDetails` | `/spapi/setPrepDetails` | Authorized connection where required |
| `updateInboundPlanName` | `/spapi/updateInboundPlanName` | Authorized connection where required |
| `updateItemComplianceDetails` | `/spapi/updateItemComplianceDetails` | Authorized connection where required |
| `updateShipmentName` | `/spapi/updateShipmentName` | Authorized connection where required |
| `updateShipmentSourceAddress` | `/spapi/updateShipmentSourceAddress` | Authorized connection where required |
| `updateShipmentTrackingDetails` | `/spapi/updateShipmentTrackingDetails` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-inbound-cancel-inbound-plan`

MCP tool: `nexscope_amazon_sp_api_inbound_cancel_inbound_plan`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/cancellation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/cancellation"
    }
  }
}
```

### `amazon-sp-api-inbound-cancel-self-ship-appointment`

MCP tool: `nexscope_amazon_sp_api_inbound_cancel_self_ship_appointment`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentCancellation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "reasonComment": "APPOINTMENT_REQUESTED_BY_MISTAKE"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/selfShipAppointmentCancellation"
    }
  }
}
```

### `amazon-sp-api-inbound-confirm-delivery-window-options`

MCP tool: `nexscope_amazon_sp_api_inbound_confirm_delivery_window_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions/{deliveryWindowOptionId}/confirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId, deliveryWindowOptionId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000",
    "deliveryWindowOptionId": "EXAMPLE00000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/deliveryWindowOptions/EXAMPLE00000000000000000000000000000/confirmation"
    }
  }
}
```

### `amazon-sp-api-inbound-confirm-packing-option`

MCP tool: `nexscope_amazon_sp_api_inbound_confirm_packing_option`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions/{packingOptionId}/confirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, packingOptionId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "packingOptionId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/packingOptions/EXAMPLE0000000000000000000000000000000/confirmation"
    }
  }
}
```

### `amazon-sp-api-inbound-confirm-placement-option`

MCP tool: `nexscope_amazon_sp_api_inbound_confirm_placement_option`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions/{placementOptionId}/confirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, placementOptionId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "placementOptionId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/placementOptions/EXAMPLE0000000000000000000000000000000/confirmation"
    }
  }
}
```

### `amazon-sp-api-inbound-confirm-shipment-content-update-preview`

MCP tool: `nexscope_amazon_sp_api_inbound_confirm_shipment_con_ad9ebf6b0029`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}/confirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId, contentUpdatePreviewId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000",
    "contentUpdatePreviewId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/contentUpdatePreviews/EXAMPLE0000000000000000000000000000000/confirmation"
    }
  }
}
```

### `amazon-sp-api-inbound-confirm-transportation-options`

MCP tool: `nexscope_amazon_sp_api_inbound_confirm_transportation_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions/confirmation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "transportationSelections": [
      {
        "shipmentId": "EXAMPLE0000000000000000000000000000000",
        "transportationOptionId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/transportationOptions/confirmation"
    }
  }
}
```

### `amazon-sp-api-inbound-create-inbound-plan`

MCP tool: `nexscope_amazon_sp_api_inbound_create_inbound_plan`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans`.
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
    "destinationMarketplaces": [
      "ATVPDKIKX0DER"
    ],
    "items": [
      {
        "labelOwner": "AMAZON",
        "msku": "EXAMPLE",
        "prepOwner": "AMAZON",
        "quantity": 1
      }
    ],
    "sourceAddress": {
      "addressLine1": "EXAMPLE",
      "city": "EXAMPLE",
      "countryCode": "US",
      "name": "EXAMPLE",
      "phoneNumber": "EXAMPLE",
      "postalCode": "00000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans"
    }
  }
}
```

### `amazon-sp-api-inbound-create-marketplace-item-labels`

MCP tool: `nexscope_amazon_sp_api_inbound_create_marketplace_item_labels`.

Amazon operation: `POST /inbound/fba/2024-03-20/items/labels`.
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
    "labelType": "STANDARD_FORMAT",
    "marketplaceId": "ATVPDKIKX0DER",
    "mskuQuantities": [
      {
        "msku": "EXAMPLE",
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
      "path": "/inbound/fba/2024-03-20/items/labels"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-delivery-window-options`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_delivery_window_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/deliveryWindowOptions"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-packing-options`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_packing_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/packingOptions"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-placement-options`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_placement_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "customPlacement": [
      {
        "items": [
          {
            "labelOwner": "AMAZON",
            "msku": "EXAMPLE",
            "prepOwner": "AMAZON",
            "quantity": 1
          }
        ],
        "warehouseId": "EXAMPLE"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/placementOptions"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-self-ship-appointment-slots`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_self_ship_a_b16671d5a54e`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "desiredEndDate": "2026-01-02T00:00:00Z",
    "desiredStartDate": "2026-01-01T00:00:00Z"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/selfShipAppointmentSlots"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-shipment-content-update-previews`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_shipment_co_28382962a8b4`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "boxes": [
      {
        "contentInformationSource": "BOX_CONTENT_PROVIDED",
        "dimensions": {
          "height": 0,
          "length": 0,
          "unitOfMeasurement": "IN",
          "width": 0
        },
        "quantity": 1,
        "weight": {
          "unit": "LB",
          "value": 0
        }
      }
    ],
    "items": [
      {
        "labelOwner": "AMAZON",
        "msku": "EXAMPLE",
        "prepOwner": "AMAZON",
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/contentUpdatePreviews"
    }
  }
}
```

### `amazon-sp-api-inbound-generate-transportation-options`

MCP tool: `nexscope_amazon_sp_api_inbound_generate_transportation_options`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "placementOptionId": "EXAMPLE0000000000000000000000000000000",
    "shipmentTransportationConfigurations": [
      {
        "readyToShipWindow": {
          "start": "2026-01-01T00:00:00Z"
        },
        "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/transportationOptions"
    }
  }
}
```

### `amazon-sp-api-inbound-get-delivery-challan-document`

MCP tool: `nexscope_amazon_sp_api_inbound_get_delivery_challan_document`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryChallanDocument`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "documentDownload": {
          "downloadType": "EXAMPLE",
          "uri": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-get-inbound-operation-status`

MCP tool: `nexscope_amazon_sp_api_inbound_get_inbound_operation_status`.

Amazon operation: `GET /inbound/fba/2024-03-20/operations/{operationId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: operationId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "operationId": "EXAMPLE00000000000000000000000000000"
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
        "operation": "EXAMPLE",
        "operationId": "EXAMPLE00000000000000000000000000000",
        "operationProblems": [
          {
            "code": "EXAMPLE",
            "message": "EXAMPLE",
            "severity": "EXAMPLE"
          }
        ],
        "operationStatus": "SUCCESS"
      }
    }
  }
}
```

### `amazon-sp-api-inbound-get-inbound-plan`

MCP tool: `nexscope_amazon_sp_api_inbound_get_inbound_plan`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "createdAt": "2026-01-01T00:00:00Z",
        "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
        "lastUpdatedAt": "2026-01-01T00:00:00Z",
        "marketplaceIds": [
          "ATVPDKIKX0DER"
        ],
        "name": "EXAMPLE",
        "sourceAddress": {
          "addressLine1": "EXAMPLE",
          "city": "EXAMPLE",
          "countryCode": "US",
          "name": "EXAMPLE",
          "postalCode": "00000"
        },
        "status": "EXAMPLE"
      }
    }
  }
}
```

### `amazon-sp-api-inbound-get-self-ship-appointment-slots`

MCP tool: `nexscope_amazon_sp_api_inbound_get_self_ship_appointment_slots`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "selfShipAppointmentSlotsAvailability": {
          "expiresAt": "2026-01-01T00:00:00Z",
          "slots": [
            {
              "slotId": "EXAMPLE0000000000000000000000000000000",
              "slotTime": {
                "endTime": "2026-01-02T00:00:00Z",
                "startTime": "2026-01-01T00:00:00Z"
              }
            }
          ]
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-get-shipment`

MCP tool: `nexscope_amazon_sp_api_inbound_get_shipment`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "destination": {
          "destinationType": "EXAMPLE"
        },
        "placementOptionId": "EXAMPLE0000000000000000000000000000000",
        "shipmentId": "EXAMPLE0000000000000000000000000000000",
        "source": {
          "sourceType": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-get-shipment-content-update-preview`

MCP tool: `nexscope_amazon_sp_api_inbound_get_shipment_content_a2c8f3191c68`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews/{contentUpdatePreviewId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId, contentUpdatePreviewId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000",
    "contentUpdatePreviewId": "EXAMPLE0000000000000000000000000000000"
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
        "contentUpdatePreviewId": "EXAMPLE0000000000000000000000000000000",
        "expiration": "2026-01-01T00:00:00Z",
        "requestedUpdates": {
          "items": [
            {
              "labelOwner": "AMAZON",
              "msku": "EXAMPLE",
              "prepOwner": "AMAZON",
              "quantity": 1
            }
          ],
          "boxes": [
            {
              "contentInformationSource": "BOX_CONTENT_PROVIDED",
              "dimensions": {
                "height": 0,
                "length": 0,
                "unitOfMeasurement": "IN",
                "width": 0
              },
              "quantity": 1,
              "weight": {
                "unit": "LB",
                "value": 0
              }
            }
          ]
        },
        "transportationOption": {
          "carrier": {},
          "preconditions": [
            "EXAMPLE"
          ],
          "shipmentId": "EXAMPLE0000000000000000000000000000000",
          "shippingMode": "EXAMPLE",
          "shippingSolution": "EXAMPLE",
          "transportationOptionId": "EXAMPLE0000000000000000000000000000000"
        }
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-delivery-window-options`

MCP tool: `nexscope_amazon_sp_api_inbound_list_delivery_window_options`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/deliveryWindowOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "deliveryWindowOptions": [
          {
            "availabilityType": "EXAMPLE",
            "deliveryWindowOptionId": "EXAMPLE00000000000000000000000000000",
            "endDate": "2026-01-02T00:00:00Z",
            "startDate": "2026-01-01T00:00:00Z",
            "validUntil": "2026-01-01T00:00:00Z"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-inbound-plan-boxes`

MCP tool: `nexscope_amazon_sp_api_inbound_list_inbound_plan_boxes`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/boxes`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "boxes": [
          {
            "packageId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-inbound-plan-items`

MCP tool: `nexscope_amazon_sp_api_inbound_list_inbound_plan_items`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "items": [
          {
            "asin": "B000EXAMPL",
            "fnsku": "EXAMPLE",
            "labelOwner": "EXAMPLE",
            "msku": "EXAMPLE",
            "prepInstructions": [
              {}
            ],
            "quantity": 1
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-inbound-plan-pallets`

MCP tool: `nexscope_amazon_sp_api_inbound_list_inbound_plan_pallets`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/pallets`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "pallets": [
          {
            "packageId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-inbound-plans`

MCP tool: `nexscope_amazon_sp_api_inbound_list_inbound_plans`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans`.
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
        "pagination": {
          "nextToken": "EXAMPLE"
        },
        "inboundPlans": [
          {
            "createdAt": "2026-01-01T00:00:00Z",
            "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
            "lastUpdatedAt": "2026-01-01T00:00:00Z",
            "marketplaceIds": [
              "ATVPDKIKX0DER"
            ],
            "name": "EXAMPLE",
            "sourceAddress": {
              "addressLine1": "EXAMPLE",
              "city": "EXAMPLE",
              "countryCode": "US",
              "name": "EXAMPLE",
              "postalCode": "00000"
            },
            "status": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-item-compliance-details`

MCP tool: `nexscope_amazon_sp_api_inbound_list_item_compliance_details`.

Amazon operation: `GET /inbound/fba/2024-03-20/items/compliance`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "mskus=EXAMPLE&marketplaceId=ATVPDKIKX0DER"
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
        "complianceDetails": [
          {}
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-packing-group-boxes`

MCP tool: `nexscope_amazon_sp_api_inbound_list_packing_group_boxes`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/boxes`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, packingGroupId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "packingGroupId": "EXAMPLE0000000000000000000000000000000"
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
        "boxes": [
          {
            "packageId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-packing-group-items`

MCP tool: `nexscope_amazon_sp_api_inbound_list_packing_group_items`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingGroups/{packingGroupId}/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, packingGroupId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "packingGroupId": "EXAMPLE0000000000000000000000000000000"
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
        "items": [
          {
            "asin": "B000EXAMPL",
            "fnsku": "EXAMPLE",
            "labelOwner": "EXAMPLE",
            "msku": "EXAMPLE",
            "prepInstructions": [
              {}
            ],
            "quantity": 1
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-packing-options`

MCP tool: `nexscope_amazon_sp_api_inbound_list_packing_options`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "packingOptions": [
          {
            "discounts": [
              {
                "description": "EXAMPLE",
                "target": "EXAMPLE",
                "type": "EXAMPLE",
                "value": {
                  "amount": 1,
                  "code": "EXA"
                }
              }
            ],
            "fees": [
              {
                "description": "EXAMPLE",
                "target": "EXAMPLE",
                "type": "EXAMPLE",
                "value": {
                  "amount": 1,
                  "code": "EXA"
                }
              }
            ],
            "packingGroups": [
              "EXAMPLE0000000000000000000000000000000"
            ],
            "packingOptionId": "EXAMPLE0000000000000000000000000000000",
            "status": "EXAMPLE",
            "supportedConfigurations": [
              {}
            ],
            "supportedShippingConfigurations": [
              {}
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-placement-options`

MCP tool: `nexscope_amazon_sp_api_inbound_list_placement_options`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/placementOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "placementOptions": [
          {
            "discounts": [
              {
                "description": "EXAMPLE",
                "target": "EXAMPLE",
                "type": "EXAMPLE",
                "value": {
                  "amount": 1,
                  "code": "EXA"
                }
              }
            ],
            "fees": [
              {
                "description": "EXAMPLE",
                "target": "EXAMPLE",
                "type": "EXAMPLE",
                "value": {
                  "amount": 1,
                  "code": "EXA"
                }
              }
            ],
            "placementOptionId": "EXAMPLE0000000000000000000000000000000",
            "shipmentIds": [
              "EXAMPLE0000000000000000000000000000000"
            ],
            "status": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-prep-details`

MCP tool: `nexscope_amazon_sp_api_inbound_list_prep_details`.

Amazon operation: `GET /inbound/fba/2024-03-20/items/prepDetails`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER&mskus=EXAMPLE"
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
        "mskuPrepDetails": [
          {
            "msku": "EXAMPLE",
            "prepCategory": "ADULT",
            "prepTypes": [
              "ITEM_BLACK_SHRINKWRAP"
            ]
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-shipment-boxes`

MCP tool: `nexscope_amazon_sp_api_inbound_list_shipment_boxes`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/boxes`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "boxes": [
          {
            "packageId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-shipment-content-update-previews`

MCP tool: `nexscope_amazon_sp_api_inbound_list_shipment_conten_898bb5b92c18`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/contentUpdatePreviews`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "contentUpdatePreviews": [
          {
            "contentUpdatePreviewId": "EXAMPLE0000000000000000000000000000000",
            "expiration": "2026-01-01T00:00:00Z",
            "requestedUpdates": {},
            "transportationOption": {
              "carrier": {},
              "preconditions": [
                "EXAMPLE"
              ],
              "shipmentId": "EXAMPLE0000000000000000000000000000000",
              "shippingMode": "EXAMPLE",
              "shippingSolution": "EXAMPLE",
              "transportationOptionId": "EXAMPLE0000000000000000000000000000000"
            }
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-shipment-items`

MCP tool: `nexscope_amazon_sp_api_inbound_list_shipment_items`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/items`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "items": [
          {
            "asin": "B000EXAMPL",
            "fnsku": "EXAMPLE",
            "labelOwner": "EXAMPLE",
            "msku": "EXAMPLE",
            "prepInstructions": [
              {}
            ],
            "quantity": 1
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-shipment-pallets`

MCP tool: `nexscope_amazon_sp_api_inbound_list_shipment_pallets`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/pallets`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
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
        "pallets": [
          {
            "packageId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-list-transportation-options`

MCP tool: `nexscope_amazon_sp_api_inbound_list_transportation_options`.

Amazon operation: `GET /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/transportationOptions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
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
        "transportationOptions": [
          {
            "carrier": {},
            "preconditions": [
              "EXAMPLE"
            ],
            "shipmentId": "EXAMPLE0000000000000000000000000000000",
            "shippingMode": "EXAMPLE",
            "shippingSolution": "EXAMPLE",
            "transportationOptionId": "EXAMPLE0000000000000000000000000000000"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-inbound-schedule-self-ship-appointment`

MCP tool: `nexscope_amazon_sp_api_inbound_schedule_self_ship_appointment`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/selfShipAppointmentSlots/{slotId}/schedule`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId, slotId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000",
    "slotId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "reasonComment": "APPOINTMENT_REQUESTED_BY_MISTAKE"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/selfShipAppointmentSlots/EXAMPLE0000000000000000000000000000000/schedule"
    }
  }
}
```

### `amazon-sp-api-inbound-set-packing-information`

MCP tool: `nexscope_amazon_sp_api_inbound_set_packing_information`.

Amazon operation: `POST /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/packingInformation`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "packageGroupings": [
      {
        "boxes": [
          {
            "contentInformationSource": "BOX_CONTENT_PROVIDED",
            "dimensions": {
              "height": 0,
              "length": 0,
              "unitOfMeasurement": "IN",
              "width": 0
            },
            "quantity": 1,
            "weight": {
              "unit": "LB",
              "value": 0
            }
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/packingInformation"
    }
  }
}
```

### `amazon-sp-api-inbound-set-prep-details`

MCP tool: `nexscope_amazon_sp_api_inbound_set_prep_details`.

Amazon operation: `POST /inbound/fba/2024-03-20/items/prepDetails`.
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
    "marketplaceId": "ATVPDKIKX0DER",
    "mskuPrepDetails": [
      {
        "msku": "EXAMPLE",
        "prepCategory": "ADULT",
        "prepTypes": [
          "ITEM_BLACK_SHRINKWRAP"
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
      "path": "/inbound/fba/2024-03-20/items/prepDetails"
    }
  }
}
```

### `amazon-sp-api-inbound-update-inbound-plan-name`

MCP tool: `nexscope_amazon_sp_api_inbound_update_inbound_plan_name`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/name`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "name": "EXAMPLE"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/name"
    }
  }
}
```

### `amazon-sp-api-inbound-update-item-compliance-details`

MCP tool: `nexscope_amazon_sp_api_inbound_update_item_compliance_details`.

Amazon operation: `PUT /inbound/fba/2024-03-20/items/compliance`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER",
  "body": {
    "msku": "EXAMPLE",
    "taxDetails": {
      "declaredValue": {
        "amount": 1,
        "code": "EXA"
      },
      "hsnCode": "EXAMPLE",
      "taxRates": [
        {}
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
      "method": "PUT",
      "path": "/inbound/fba/2024-03-20/items/compliance"
    }
  }
}
```

### `amazon-sp-api-inbound-update-shipment-name`

MCP tool: `nexscope_amazon_sp_api_inbound_update_shipment_name`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/name`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "name": "EXAMPLE"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/name"
    }
  }
}
```

### `amazon-sp-api-inbound-update-shipment-source-address`

MCP tool: `nexscope_amazon_sp_api_inbound_update_shipment_source_address`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/sourceAddress`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "address": {
      "addressLine1": "EXAMPLE",
      "city": "EXAMPLE",
      "countryCode": "US",
      "name": "EXAMPLE",
      "phoneNumber": "EXAMPLE",
      "postalCode": "00000"
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
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/sourceAddress"
    }
  }
}
```

### `amazon-sp-api-inbound-update-shipment-tracking-details`

MCP tool: `nexscope_amazon_sp_api_inbound_update_shipment_tracking_details`.

Amazon operation: `PUT /inbound/fba/2024-03-20/inboundPlans/{inboundPlanId}/shipments/{shipmentId}/trackingDetails`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: inboundPlanId, shipmentId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "inboundPlanId": "EXAMPLE0000000000000000000000000000000",
    "shipmentId": "EXAMPLE0000000000000000000000000000000"
  },
  "body": {
    "trackingDetails": {
      "ltlTrackingDetail": {
        "freightBillNumber": [
          "EXAMPLE"
        ]
      },
      "spdTrackingDetail": {
        "spdTrackingItems": [
          {
            "boxId": "EXAMPLE",
            "trackingId": "EXAMPLE"
          }
        ]
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
      "method": "PUT",
      "path": "/inbound/fba/2024-03-20/inboundPlans/EXAMPLE0000000000000000000000000000000/shipments/EXAMPLE0000000000000000000000000000000/trackingDetails"
    }
  }
}
```
