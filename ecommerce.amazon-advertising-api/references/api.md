# Amazon API reference

This package preserves 67 cataloged operations. Use `references/api.json` as the machine-readable contract and the scripts declared by `SKILL.md`. Provider credentials remain server-side.

## Invocation contract

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`.
- Supply `workspaceId` and an owned `connectionId`; never supply a provider token.
- Reads return provider data. Paginated reads also expose `success`, `total` when a result list is known, `pagesFetched`, and `truncated`.
- Ads entity mutations require preview, explicit user approval, and a separate confirm invocation with the one-use token; authorization uses the connection route.
- HTTP 401/403 indicates authentication or ownership failure; 429 requires bounded backoff; 5xx is a sanitized upstream failure.
- Ads report downloads are decoded by the backend. `outputFile` is an optional safe local destination; no local HTTP listener is started.

## `ads_auth.authorize_url` - Authorize Url

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

## `ads_auth.authorized_stores` - Authorized Stores

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

## `ads_auth.profiles` - Profiles

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

## `ads_auth.refresh_token` - Refresh Token

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

## `ads_auth.store_tokens` - Store Tokens

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

## `ads_manager.sb.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sb/v4/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadgroupresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `ads_manager.sb.create_ads` - Create Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sb/v4/ads/{adType}`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `adType`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: `adType`
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{"adType": ["autoCollection","manualCollection","brandVideo","video","productCollection","productCollectionExtended","storeSpotlight"]},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.create_ads","workspaceId":"user:42","connectionId":7,"adType":"video","payload":{"ads":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `ads_manager.sb.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sb/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sb.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sb/v4/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbcampaignresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `ads_manager.sb.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sb/v4/adGroups/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadgroupresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sb.list_ads` - List Ads

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sb/v4/ads/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.list_ads","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sb.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sb/budgetRules`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`- Path inputs: None
- Query inputs: `nextToken`
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-query', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sb.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sb/v4/campaigns/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbcampaignresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sb.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sb/v4/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadgroupresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `ads_manager.sb.update_ads` - Update Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sb/v4/ads`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbadresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.update_ads","workspaceId":"user:42","connectionId":7,"payload":{"ads":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `ads_manager.sb.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sb/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sb.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sb/v4/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sbcampaignresource.v4+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sb.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `ads_manager.sd.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}],"phase":"preview"}'`

## `ads_manager.sd.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sd.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}],"phase":"preview"}'`

## `ads_manager.sd.create_creatives` - Create Creatives

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/creatives`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_creatives","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","creativeId":"7001","campaignId":"1001","adGroupId":"2001"}],"phase":"preview"}'`

## `ads_manager.sd.create_negative_targets` - Create Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/negativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_negative_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `ads_manager.sd.create_product_ads` - Create Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/productAds`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_product_ads","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}],"phase":"preview"}'`

## `ads_manager.sd.create_targets` - Create Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sd/targets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.create_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `ads_manager.sd.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/adGroups`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`
- Provider query-name map: `{"maxResults":"count","nameFilter":"name"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'adGroups', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/budgetRules`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`- Path inputs: None
- Query inputs: `nextToken`
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-query', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/campaigns`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`
- Provider query-name map: `{"maxResults":"count","nameFilter":"name"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'campaigns', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_creatives` - List Creatives

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/creatives`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `creativeIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`- Path inputs: None
- Query inputs: `adGroupIdFilter`, `creativeIdFilter`, `maxResults`, `nextToken`
- Provider query-name map: `{"maxResults":"count"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'creatives', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_creatives","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_negative_targets` - List Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/negativeTargets`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`
- Provider query-name map: `{"maxResults":"count"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'negativeTargetingClauses', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_negative_targets","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_product_ads` - List Product Ads

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/productAds`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`- Path inputs: None
- Query inputs: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`
- Provider query-name map: `{"maxResults":"count"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'productAds', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_product_ads","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.list_targets` - List Targets

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sd/targets`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`- Path inputs: None
- Query inputs: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`
- Provider query-name map: `{"maxResults":"count"}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'offset-query', 'startIndexField': 'startIndex', 'pageSizeField': 'count', 'resultField': 'targetingClauses', 'defaultPageSize': 100, 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.list_targets","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sd.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}],"phase":"preview"}'`

## `ads_manager.sd.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sd.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}],"phase":"preview"}'`

## `ads_manager.sd.update_creatives` - Update Creatives

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/creatives`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_creatives","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","creativeId":"7001","campaignId":"1001","adGroupId":"2001"}],"phase":"preview"}'`

## `ads_manager.sd.update_negative_targets` - Update Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/negativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_negative_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `ads_manager.sd.update_product_ads` - Update Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/productAds`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_product_ads","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}],"phase":"preview"}'`

## `ads_manager.sd.update_targets` - Update Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sd/targets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sd.update_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `ads_manager.sp.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spAdGroup.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRules":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sp.create_budget_rules_association` - Create Budget Rules Association

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/budgetRulesAssociation`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_budget_rules_association","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesAssociation":[{"state":"PAUSED","campaignId":"1001","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sp.create_campaign_negative_keywords` - Create Campaign Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/campaignNegativeKeywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaignNegativeKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_campaign_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeKeywords":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"keywordId":"3001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.create_campaign_negative_targets` - Create Campaign Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/campaignNegativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaignNegativeTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_campaign_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeTargetingClauses":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"targetId":"4001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_manager.sp.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaign.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `ads_manager.sp.create_keywords` - Create Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/keywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_keywords","workspaceId":"user:42","connectionId":7,"payload":{"keywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.create_negative_keywords` - Create Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/negativeKeywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spNegativeKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"negativeKeywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.create_negative_targets` - Create Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/negativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spNegativeTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"negativeTargetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_manager.sp.create_product_ads` - Create Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/productAds`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spProductAd.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_product_ads","workspaceId":"user:42","connectionId":7,"payload":{"productAds":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `ads_manager.sp.create_targets` - Create Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `POST /sp/targets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.create_targets","workspaceId":"user:42","connectionId":7,"payload":{"targetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_manager.sp.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/adGroups/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spadgroup.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `GET /sp/budgetRules`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`- Path inputs: None
- Query inputs: `nextToken`
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: None
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `none`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-query', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/campaigns/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spcampaign.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_keywords` - List Keywords

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/keywords/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `campaignIdFilter`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `nextToken`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spkeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_keywords","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_negative_keywords` - List Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/negativeKeywords/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `campaignIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spnegativekeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_negative_keywords","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_product_ads` - List Product Ads

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/productAds/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `skuFilter`, `stateFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spproductad.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_product_ads","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.list_targets` - List Targets

- Gateway request: `POST /api/skill/amazon/ads/read`
- Provider request (request-body `path`): `POST /sp/targets/list`
- Gateway action: `read`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `read`; target mutation requiring confirmation: `false`. 
- Required inputs: `connectionId`- Required input alternatives: None
- Optional inputs: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.sptargetingclause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: {'mode': 'next-token-body', 'responseTokenField': 'nextToken', 'requestTokenField': 'nextToken', 'defaultFetchAll': True}
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.list_targets","workspaceId":"user:42","connectionId":7}'`

## `ads_manager.sp.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/adGroups`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spAdGroup.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/budgetRules`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRules":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `ads_manager.sp.update_campaign_negative_keywords` - Update Campaign Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/campaignNegativeKeywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaignNegativeKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_campaign_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeKeywords":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"keywordId":"3001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.update_campaign_negative_targets` - Update Campaign Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/campaignNegativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaignNegativeTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_campaign_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeTargetingClauses":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"targetId":"4001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_manager.sp.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/campaigns`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spCampaign.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `ads_manager.sp.update_keywords` - Update Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/keywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_keywords","workspaceId":"user:42","connectionId":7,"payload":{"keywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.update_negative_keywords` - Update Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/negativeKeywords`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spNegativeKeyword.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"negativeKeywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `ads_manager.sp.update_negative_targets` - Update Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/negativeTargets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spNegativeTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"negativeTargetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_manager.sp.update_product_ads` - Update Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/productAds`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spProductAd.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_product_ads","workspaceId":"user:42","connectionId":7,"payload":{"productAds":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `ads_manager.sp.update_targets` - Update Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`
- Provider request (request-body `path`): `PUT /sp/targets`
- Gateway action: `write-preview/confirm`
- Callable: `true`; execution mode: `generic`; dedicated script: `none`. 
- Source access: `write`; target mutation requiring confirmation: `true`. 
- Required inputs: `connectionId`, `payload`- Required input alternatives: None
- Optional inputs: `workspaceId`, `queryString`, `requestId`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `payload`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.spTargetingClause.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_api.py '{"operation":"ads_manager.sp.update_targets","workspaceId":"user:42","connectionId":7,"payload":{"targetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `ads_report.get_report` - Get Report

- Provider request: `POST /reporting/reports`
- Gateway action: `ADS_REPORT_START -> ADS_REPORT_POLL -> ADS_REPORT_DOWNLOAD`
- Callable: `true`; execution mode: `specialized`; dedicated script: `scripts/amazon_ads_report_workflow.py`. 
- Source access: `write`; target mutation requiring confirmation: `false`. write means the provider uses HTTP POST to create a read-only report job; mutation is false, so no write confirmation is required.
- Required inputs: `connectionId`- Required input alternatives: `reportId` or `startDate` + `endDate` + `configuration` or `startDate` + `endDate` + `reportTypeId` + `adProduct` + `groupBy` + `columns`
- Optional inputs: `workspaceId`, `reportId`, `reportTypeId`, `adProduct`, `groupBy`, `columns`, `name`, `startDate`, `endDate`, `timeUnit`, `format`, `filters`, `configuration`, `timeoutSeconds`, `pollIntervalSeconds`, `outputFile`, `overwrite`- Path inputs: None
- Query inputs: Use `queryString` when applicable
- Provider query-name map: `{}`; comma-separated arrays: none.
- Body inputs: `name`, `startDate`, `endDate`, `configuration`
- Direct body input: `none`
- Body wrapper: `none`; batch transformer: `none`
- Content type: `application/vnd.createasyncreportrequest.v3+json`
- Defaults: `{}`
- Validation constraints: `{"mutuallyExclusiveGroups":[],"dependentInputs":{},"maxItems":{},"numericRanges":{},"enumInputs":{},"conditionalInputs":{}}`
- Pagination: Not defined for this operation.
- Result: Unwrapped provider response data; non-success application and upstream statuses exit nonzero.
- Status behavior: `{"2xx":"Return normalized provider data and execution metadata.","400":"Reject invalid path, query, body, or operation-specific constraints.","401/403":"Reject missing access or account ownership.","404":"Return missing provider resource.","409":"Return provider state conflict.","429":"Stop or retry with bounded backoff.","5xx":"Exit nonzero with a sanitized upstream failure.","425":"Recover a duplicate report ID when supplied and resume polling."}`
- Errors: invalid input, unauthorized connection, rate limit, upstream failure, non-JSON response.
- Example: `python scripts/amazon_ads_report_workflow.py '{"workspaceId":"user:42","connectionId":7,"startDate":"2026-07-01","endDate":"2026-07-31","reportTypeId":"spCampaigns","adProduct":"SPONSORED_PRODUCTS","groupBy":["campaign"],"columns":["campaignId","impressions","clicks"]}'`
