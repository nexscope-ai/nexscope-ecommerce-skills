# Amazon A+ Content API reference

Migration reference: `linkfox-amazon-store-aplus-content` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `createMedia` | `/spapi/createMedia` | Authorized connection where required |
| `createcontentdocument` | `/spapi/createContentDocument` | Authorized connection where required |
| `getMedia` | `/spapi/getMedia` | Authorized connection where required |
| `getcontentdocument` | `/spapi/getContentDocument` | Authorized connection where required |
| `listcontentdocumentasinrelations` | `/spapi/listContentDocumentAsinRelations` | Authorized connection where required |
| `postcontentdocumentapprovalsubmission` | `/spapi/postContentDocumentApprovalSubmission` | Authorized connection where required |
| `postcontentdocumentasinrelations` | `/spapi/postContentDocumentAsinRelations` | Authorized connection where required |
| `postcontentdocumentsuspendsubmission` | `/spapi/postContentDocumentSuspendSubmission` | Authorized connection where required |
| `searchcontentdocuments` | `/spapi/searchContentDocuments` | Authorized connection where required |
| `searchcontentpublishrecords` | `/spapi/searchContentPublishRecords` | Authorized connection where required |
| `updatecontentdocument` | `/spapi/updateContentDocument` | Authorized connection where required |
| `validatecontentdocumentasinrelations` | `/spapi/validateContentDocumentAsinRelations` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-aplus-create-media`

MCP tool: `nexscope_amazon_sp_api_aplus_create_media`.

Amazon operation: `POST /aplus/2020-11-01/media`.
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
    "mediaType": "VIDEO"
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
      "path": "/aplus/2020-11-01/media"
    }
  }
}
```

### `amazon-sp-api-aplus-createcontentdocument`

MCP tool: `nexscope_amazon_sp_api_aplus_createcontentdocument`.

Amazon operation: `POST /aplus/2020-11-01/contentDocuments`.
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
    "contentDocument": {
      "contentModuleList": [
        {
          "contentModuleType": "STANDARD_COMPANY_LOGO"
        }
      ],
      "contentType": "EBC",
      "locale": "en_US",
      "name": "EXAMPLE"
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
      "path": "/aplus/2020-11-01/contentDocuments"
    }
  }
}
```

### `amazon-sp-api-aplus-get-media`

MCP tool: `nexscope_amazon_sp_api_aplus_get_media`.

Amazon operation: `GET /aplus/2020-11-01/media/{mediaId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: mediaId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "mediaId": "EXAMPLE"
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
        "warnings": [
          {
            "code": "EXAMPLE",
            "message": "EXAMPLE"
          }
        ],
        "mediaId": "EXAMPLE",
        "mediaType": "VIDEO",
        "title": "EXAMPLE",
        "status": [
          "PENDING_PROCESSING"
        ]
      }
    }
  }
}
```

### `amazon-sp-api-aplus-getcontentdocument`

MCP tool: `nexscope_amazon_sp_api_aplus_getcontentdocument`.

Amazon operation: `GET /aplus/2020-11-01/contentDocuments/{contentReferenceKey}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER&includedDataSet=CONTENTS"
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
        "warnings": [
          {
            "code": "EXAMPLE",
            "message": "EXAMPLE"
          }
        ],
        "contentRecord": {
          "contentReferenceKey": "EXAMPLE"
        }
      }
    }
  }
}
```

### `amazon-sp-api-aplus-listcontentdocumentasinrelations`

MCP tool: `nexscope_amazon_sp_api_aplus_listcontentdocumentasinrelations`.

Amazon operation: `GET /aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
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
        "asinMetadataSet": [
          {
            "asin": "B000EXAMPL"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-aplus-postcontentdocumentapprovalsubmission`

MCP tool: `nexscope_amazon_sp_api_aplus_postcontentdocumentapp_4ee55e29cc56`.

Amazon operation: `POST /aplus/2020-11-01/contentDocuments/{contentReferenceKey}/approvalSubmissions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
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
      "method": "POST",
      "path": "/aplus/2020-11-01/contentDocuments/EXAMPLE/approvalSubmissions"
    }
  }
}
```

### `amazon-sp-api-aplus-postcontentdocumentasinrelations`

MCP tool: `nexscope_amazon_sp_api_aplus_postcontentdocumentasinrelations`.

Amazon operation: `POST /aplus/2020-11-01/contentDocuments/{contentReferenceKey}/asins`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER",
  "body": {
    "asinSet": [
      "EXAMPLE000"
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
      "path": "/aplus/2020-11-01/contentDocuments/EXAMPLE/asins"
    }
  }
}
```

### `amazon-sp-api-aplus-postcontentdocumentsuspendsubmission`

MCP tool: `nexscope_amazon_sp_api_aplus_postcontentdocumentsus_d9bff00567fb`.

Amazon operation: `POST /aplus/2020-11-01/contentDocuments/{contentReferenceKey}/suspendSubmissions`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
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
      "method": "POST",
      "path": "/aplus/2020-11-01/contentDocuments/EXAMPLE/suspendSubmissions"
    }
  }
}
```

### `amazon-sp-api-aplus-searchcontentdocuments`

MCP tool: `nexscope_amazon_sp_api_aplus_searchcontentdocuments`.

Amazon operation: `GET /aplus/2020-11-01/contentDocuments`.
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
        "contentMetadataRecords": [
          {
            "contentMetadata": {
              "badgeSet": [
                "BULK"
              ],
              "marketplaceId": "ATVPDKIKX0DER",
              "name": "EXAMPLE",
              "status": "APPROVED",
              "updateTime": "2026-01-01T00:00:00Z"
            },
            "contentReferenceKey": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-aplus-searchcontentpublishrecords`

MCP tool: `nexscope_amazon_sp_api_aplus_searchcontentpublishrecords`.

Amazon operation: `GET /aplus/2020-11-01/contentPublishRecords`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER&asin=B000EXAMPL"
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
        "publishRecordList": [
          {
            "asin": "B000EXAMPL",
            "contentReferenceKey": "EXAMPLE",
            "contentType": "EBC",
            "locale": "en_US",
            "marketplaceId": "ATVPDKIKX0DER"
          }
        ]
      }
    }
  }
}
```

### `amazon-sp-api-aplus-updatecontentdocument`

MCP tool: `nexscope_amazon_sp_api_aplus_updatecontentdocument`.

Amazon operation: `POST /aplus/2020-11-01/contentDocuments/{contentReferenceKey}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: contentReferenceKey.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "contentReferenceKey": "EXAMPLE"
  },
  "queryString": "marketplaceId=ATVPDKIKX0DER",
  "body": {
    "contentDocument": {
      "contentModuleList": [
        {
          "contentModuleType": "STANDARD_COMPANY_LOGO"
        }
      ],
      "contentType": "EBC",
      "locale": "en_US",
      "name": "EXAMPLE"
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
      "path": "/aplus/2020-11-01/contentDocuments/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-aplus-validatecontentdocumentasinrelations`

MCP tool: `nexscope_amazon_sp_api_aplus_validatecontentdocumen_9bb4b9286073`.

Amazon operation: `POST /aplus/2020-11-01/contentAsinValidations`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "queryString": "marketplaceId=ATVPDKIKX0DER",
  "body": {
    "contentDocument": {
      "contentModuleList": [
        {
          "contentModuleType": "STANDARD_COMPANY_LOGO"
        }
      ],
      "contentType": "EBC",
      "locale": "en_US",
      "name": "EXAMPLE"
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
        "warnings": [
          {
            "code": "EXAMPLE",
            "message": "EXAMPLE"
          }
        ],
        "errors": [
          {
            "code": "EXAMPLE",
            "message": "EXAMPLE"
          }
        ]
      }
    }
  }
}
```
