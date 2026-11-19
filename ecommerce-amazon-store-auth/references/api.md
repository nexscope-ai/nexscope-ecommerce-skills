# Amazon Store Authorization API reference

Migration reference: `linkfox-amazon-store-auth` from the reviewed supplier master.

These operations use Nexscope public Data API endpoints below. The legacy `/api/v1/tools/research/` routes do not implement this contract.
Use `NEXSCOPE_API_KEY` and optionally `NEXSCOPE_PROXY_BASE`. All request and response JSON in `api.json` is illustrative.

| Operation | Nexscope POST path | Scope |
| --- | --- | --- |
| `authorize` | `/spapi/authorize` | Authorized connection where required |
| `connection-status` | `/spapi/connectionStatus` | Authorized connection where required |
| `disconnect` | `/spapi/disconnect` | Authorized connection where required |
| `list-connections` | `/spapi/listConnections` | Authorized connection where required |
| `refresh-connection` | `/spapi/refreshConnection` | Authorized connection where required |

## Parameters and examples

See the field definitions and JSON examples below, or use the machine-readable `api.json`.

### `amazon-sp-api-auth-authorize`

MCP tool: `nexscope_amazon_sp_api_auth_authorize`.

- `marketplaceId` (string, required). Amazon marketplace ID.
- `region` (string, optional). Amazon region inferred from marketplace if omitted.
- `accountName` (string, optional). Optional connection display name.

Illustrative request

```json
{
  "marketplaceId": "ATVPDKIKX0DER"
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "authorizationUrl": "https://sellercentral.amazon.com/apps/authorize/consent?state=EXAMPLE_STATE",
    "expiresAt": 1893456000000
  }
}
```

### `amazon-sp-api-auth-connection-status`

MCP tool: `nexscope_amazon_sp_api_auth_connection_status`.

- `connectionId` (integer, required). Owned Seller connection ID.

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
    "connection": {
      "id": 123,
      "status": "CONNECTED",
      "revision": 2
    }
  }
}
```

### `amazon-sp-api-auth-disconnect`

MCP tool: `nexscope_amazon_sp_api_auth_disconnect`.

- `connectionId` (integer, required). Owned Seller connection ID.
- `revision` (integer, required). Current connection revision from status.
- `confirm` (boolean, required). Explicit confirmation to disconnect.

Illustrative request

```json
{
  "connectionId": 123,
  "revision": 2,
  "confirm": true
}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "connection": {
      "id": 123,
      "status": "EXPIRED"
    }
  }
}
```

### `amazon-sp-api-auth-list-connections`

MCP tool: `nexscope_amazon_sp_api_auth_list_connections`.


Illustrative request

```json
{}
```

Illustrative response

```json
{
  "code": 0,
  "data": {
    "connections": []
  }
}
```

### `amazon-sp-api-auth-refresh-connection`

MCP tool: `nexscope_amazon_sp_api_auth_refresh_connection`.

- `connectionId` (integer, required). Owned Seller connection ID.

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
    "prepared": true,
    "expiresAt": 1893456000000
  }
}
```
