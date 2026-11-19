# Amazon Feeds API reference

Migration reference: `linkfox-amazon-store-feeds` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `cancelfeed` | `/spapi/cancelFeed` | Authorized connection where required |
| `createfeed` | `/spapi/createFeed` | Authorized connection where required |
| `createfeeddocument` | `/spapi/createFeedDocument` | Authorized connection where required |
| `getfeed` | `/spapi/getFeed` | Authorized connection where required |
| `getfeeddocument` | `/spapi/getFeedDocument` | Authorized connection where required |
| `getfeeds` | `/spapi/getFeeds` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-feeds-cancelfeed`

MCP tool: `nexscope_amazon_sp_api_feeds_cancelfeed`.

Amazon operation: `DELETE /feeds/2021-06-30/feeds/{feedId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: feedId.
- `body` (object, optional). Official operation request body.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "feedId": "EXAMPLE"
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
      "method": "DELETE",
      "path": "/feeds/2021-06-30/feeds/EXAMPLE"
    }
  }
}
```

### `amazon-sp-api-feeds-createfeed`

MCP tool: `nexscope_amazon_sp_api_feeds_createfeed`.

Amazon operation: `POST /feeds/2021-06-30/feeds`.
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
    "inputFeedDocumentId": "EXAMPLE",
    "feedType": "JSON_LISTINGS_FEED",
    "marketplaceIds": [
      "ATVPDKIKX0DER"
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
      "path": "/feeds/2021-06-30/feeds"
    }
  }
}
```

### `amazon-sp-api-feeds-createfeeddocument`

MCP tool: `nexscope_amazon_sp_api_feeds_createfeeddocument`.

Amazon operation: `POST /feeds/2021-06-30/documents`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `contentBase64` (string, required). Base64 content to upload through the backend; maximum 20 MiB decoded.
- `contentType` (string, optional). Uploaded content MIME type.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "contentBase64": "eyJtZXNzYWdlcyI6W119",
  "contentType": "application/json",
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
      "path": "/feeds/2021-06-30/documents"
    }
  }
}
```

### `amazon-sp-api-feeds-getfeed`

MCP tool: `nexscope_amazon_sp_api_feeds_getfeed`.

Amazon operation: `GET /feeds/2021-06-30/feeds/{feedId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: feedId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "feedId": "EXAMPLE"
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
        "createdTime": "2026-01-01T00:00:00Z",
        "feedId": "EXAMPLE",
        "feedType": "JSON_LISTINGS_FEED",
        "processingStatus": "CANCELLED"
      }
    }
  }
}
```

### `amazon-sp-api-feeds-getfeeddocument`

MCP tool: `nexscope_amazon_sp_api_feeds_getfeeddocument`.

Amazon operation: `GET /feeds/2021-06-30/documents/{feedDocumentId}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: feedDocumentId.
- `queryString` (string, optional). Operation query string, percent encoded, without the leading ?.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "feedDocumentId": "EXAMPLE"
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
        "feedDocumentId": "EXAMPLE",
        "url": "https://example.invalid/amazon-sp-api-fixture"
      }
    }
  }
}
```

### `amazon-sp-api-feeds-getfeeds`

MCP tool: `nexscope_amazon_sp_api_feeds_getfeeds`.

Amazon operation: `GET /feeds/2021-06-30/feeds`.
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
        "feeds": [
          {
            "createdTime": "2026-01-01T00:00:00Z",
            "feedId": "EXAMPLE",
            "feedType": "JSON_LISTINGS_FEED",
            "processingStatus": "CANCELLED"
          }
        ]
      }
    }
  }
}
```
