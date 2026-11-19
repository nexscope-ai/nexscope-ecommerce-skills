# Amazon Store Uploads API reference

Migration reference: `linkfox-amazon-store-uploads` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `createuploaddestinationforresource` | `/spapi/createUploadDestinationForResource` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-uploads-createuploaddestinationforresource`

MCP tool: `nexscope_amazon_sp_api_uploads_createuploaddestinat_fdd522c9493a`.

Amazon operation: `POST /uploads/2020-11-01/uploadDestinations/{resource}`.
- `connectionId` (integer, required). Owned Amazon Seller connection ID.
- `pathParams` (object, required). Required path values: resource.
- `contentBase64` (string, required). Base64 content to upload through the backend; maximum 20 MiB decoded.
- `contentType` (string, optional). Uploaded content MIME type.
- `marketplaceId` (string, required). Amazon marketplace ID.
- `action` (string, optional). preview (default) or confirm.
- `confirmationToken` (string, optional). Single-use token returned by preview; required for confirm.

Illustrative request

```json
{
  "connectionId": 123,
  "pathParams": {
    "resource": "aplus/2020-11-01/contentDocuments"
  },
  "contentBase64": "ZXhhbXBsZQo=",
  "contentType": "text/plain",
  "marketplaceId": "ATVPDKIKX0DER",
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
      "path": "/uploads/2020-11-01/uploadDestinations/aplus/2020-11-01/contentDocuments"
    }
  }
}
```
