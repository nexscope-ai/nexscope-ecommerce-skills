# Amazon Store Reports API reference

Migration reference: `linkfox-amazon-store-report` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `createreport` | `/spapi/createReport` | Authorized connection where required |
| `getreport` | `/spapi/getReport` | Authorized connection where required |
| `getreportdocument` | `/spapi/getReportDocument` | Authorized connection where required |
| `getreports` | `/spapi/getReports` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-reports-createreport`

MCP tool: `nexscope_amazon_sp_api_reports_createreport`.

Amazon operation: `POST /reports/2021-06-30/reports`.
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
    "marketplaceIds": [
      "ATVPDKIKX0DER"
    ],
    "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA"
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
      "path": "/reports/2021-06-30/reports"
    }
  }
}
```

### `amazon-sp-api-reports-getreport`

MCP tool: `nexscope_amazon_sp_api_reports_getreport`.

Amazon operation: `GET /reports/2021-06-30/reports/{reportId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: reportId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "reportId": "EXAMPLE"
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
        "processingStatus": "CANCELLED",
        "reportId": "EXAMPLE",
        "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
        "createdTime": "2026-01-01T00:00:00Z"
      }
    }
  }
}
```

### `amazon-sp-api-reports-getreportdocument`

MCP tool: `nexscope_amazon_sp_api_reports_getreportdocument`.

Amazon operation: `GET /reports/2021-06-30/documents/{reportDocumentId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: reportDocumentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "reportDocumentId": "EXAMPLE"
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
        "reportDocumentId": "EXAMPLE",
        "url": "https://example.invalid/amazon-sp-api-fixture"
      }
    }
  }
}
```

### `amazon-sp-api-reports-getreports`

MCP tool: `nexscope_amazon_sp_api_reports_getreports`.

Amazon operation: `GET /reports/2021-06-30/reports`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA"
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
        "reports": [
          {
            "processingStatus": "CANCELLED",
            "reportId": "EXAMPLE",
            "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
            "createdTime": "2026-01-01T00:00:00Z"
          }
        ]
      }
    }
  }
}
```
