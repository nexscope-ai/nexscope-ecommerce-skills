# Amazon API reference

This package preserves 5 cataloged operations. Use `references/api.json` as the machine-readable contract and the scripts declared by `SKILL.md`. Provider credentials remain server-side.

## Invocation contract

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`.
- Supply `workspaceId` and an owned `connectionId`; never supply a provider token.
- Reads return provider data. Paginated reads also expose `success`, `total` when a result list is known, `pagesFetched`, and `truncated`.
- Authorization uses the dedicated connection lifecycle route; token storage and refresh are not callable operations.
- HTTP 401/403 indicates authentication or ownership failure; 429 requires bounded backoff; 5xx is a sanitized upstream failure.
- Provider credentials and sensitive locations remain backend-owned.

## `authorize_url` - Authorize Url

- Provider request: `POST /api/skill/amazon/connections/amazon-ads/authorize`
- Gateway action: `authorize`
- Callable: `true`; execution mode: `specialized`; dedicated script: `scripts/amazon_connection.py`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `region`, `marketplaceId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `accountName`, `returnPath`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `workspaceId`, `region`, `marketplaceId`, `accountName`, `returnPath`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Safe authorization, connection, or profile metadata without provider credentials.
- Status behavior: `{"2xx":"Return safe connection metadata.","400":"Reject invalid authorization input.","401/403":"Reject missing access or workspace ownership.","429":"Retry only with bounded backoff.","5xx":"Exit nonzero."}`
- Errors: invalid input, unauthorized workspace, connection limit, authorization timeout.
- Example: `python scripts/amazon_connection.py '{"action":"authorize","workspaceId":"user:42","region":"NA","marketplaceId":"ATVPDKIKX0DER","accountName":"Example account"}'`

## `authorized_stores` - Authorized Stores

- Provider request: `GET /api/skill/amazon/connections/amazon-ads`
- Gateway action: `connections`
- Callable: `true`; execution mode: `specialized`; dedicated script: `scripts/amazon_connection.py`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: None- Required input alternatives: None
- Optional inputs: `workspaceId`- Path inputs: None
- Query inputs: `workspaceId`
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Safe authorization, connection, or profile metadata without provider credentials.
- Status behavior: `{"2xx":"Return safe connection metadata.","400":"Reject invalid authorization input.","401/403":"Reject missing access or workspace ownership.","429":"Retry only with bounded backoff.","5xx":"Exit nonzero."}`
- Errors: invalid input, unauthorized workspace, connection limit, authorization timeout.
- Example: `python scripts/amazon_connection.py '{"action":"connections","workspaceId":"user:42"}'`

## `profiles` - Profiles

- Provider request: `GET /api/skill/amazon/connections/amazon-ads/profiles`
- Gateway action: `profiles`
- Callable: `true`; execution mode: `specialized`; dedicated script: `scripts/amazon_connection.py`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`- Path inputs: None
- Query inputs: `workspaceId`, `connectionId`
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Safe authorization, connection, or profile metadata without provider credentials.
- Status behavior: `{"2xx":"Return safe connection metadata.","400":"Reject invalid authorization input.","401/403":"Reject missing access or workspace ownership.","429":"Retry only with bounded backoff.","5xx":"Exit nonzero."}`
- Errors: invalid input, unauthorized workspace, connection limit, authorization timeout.
- Example: `python scripts/amazon_connection.py '{"action":"profiles","workspaceId":"user:42","connectionId":7}'`

## `refresh_token` - Refresh Token

- Provider request: `NONE backend-owned token refresh`
- Gateway action: `legacy-only mechanism removed`
- Callable: `false`; execution mode: `removed`; dedicated script: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.
- Source access: `write`; target mutation requiring confirmation: `false`. 
- Required inputs: None
- Required input alternatives: None
- Optional inputs: None
- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Safe authorization, connection, or profile metadata without provider credentials.
- Status behavior: `{"2xx":"Return safe connection metadata.","400":"Reject invalid authorization input.","401/403":"Reject missing access or workspace ownership.","429":"Retry only with bounded backoff.","5xx":"Exit nonzero."}`
- Errors: invalid input, unauthorized workspace, connection limit, authorization timeout.
- Example: `Not callable: use the documented backend-owned replacement`

## `store_tokens` - Store Tokens

- Provider request: `NONE backend-owned OAuth callback token storage`
- Gateway action: `legacy-only mechanism removed`
- Callable: `false`; execution mode: `removed`; dedicated script: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.
- Source access: `write`; target mutation requiring confirmation: `false`. 
- Required inputs: None
- Required input alternatives: None
- Optional inputs: None
- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Safe authorization, connection, or profile metadata without provider credentials.
- Status behavior: `{"2xx":"Return safe connection metadata.","400":"Reject invalid authorization input.","401/403":"Reject missing access or workspace ownership.","429":"Retry only with bounded backoff.","5xx":"Exit nonzero."}`
- Errors: invalid input, unauthorized workspace, connection limit, authorization timeout.
- Example: `Not callable: use the documented backend-owned replacement`
