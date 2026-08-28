# Amazon API reference

This package preserves 61 cataloged operations. Use `references/api.json` as the machine-readable contract and the scripts declared by `SKILL.md`. Provider credentials remain server-side.

## Invocation contract

- Set `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`.
- Supply `workspaceId` and an owned `connectionId`; never supply a provider token.
- Reads return provider data. Paginated reads also expose `success`, `total` when a result list is known, `pagesFetched`, and `truncated`.
- Ads entity mutations require preview, explicit user approval, and a separate confirm invocation with the one-use token; authorization uses the connection route.
- HTTP 401/403 indicates authentication or ownership failure; 429 requires bounded backoff; 5xx is a sanitized upstream failure.
- Provider credentials and sensitive locations remain backend-owned.

## `sb.create_ad_groups` - Create Ad Groups

- Provider request: `POST /sb/v4/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `sb.create_ads` - Create Ads

- Provider request: `POST /sb/v4/ads/{adType}`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.create_ads","workspaceId":"user:42","connectionId":7,"adType":"video","payload":{"ads":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `sb.create_budget_rules` - Create Budget Rules

- Provider request: `POST /sb/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sb.create_campaigns` - Create Campaigns

- Provider request: `POST /sb/v4/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `sb.list_ad_groups` - List Ad Groups

- Provider request: `POST /sb/v4/adGroups/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `sb.list_ads` - List Ads

- Provider request: `POST /sb/v4/ads/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.list_ads","workspaceId":"user:42","connectionId":7}'`

## `sb.list_budget_rules` - List Budget Rules

- Provider request: `GET /sb/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `sb.list_campaigns` - List Campaigns

- Provider request: `POST /sb/v4/campaigns/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `sb.update_ad_groups` - Update Ad Groups

- Provider request: `PUT /sb/v4/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `sb.update_ads` - Update Ads

- Provider request: `PUT /sb/v4/ads`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.update_ads","workspaceId":"user:42","connectionId":7,"payload":{"ads":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `sb.update_budget_rules` - Update Budget Rules

- Provider request: `PUT /sb/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sb.update_campaigns` - Update Campaigns

- Provider request: `PUT /sb/v4/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sb.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `sd.create_ad_groups` - Create Ad Groups

- Provider request: `POST /sd/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}],"phase":"preview"}'`

## `sd.create_budget_rules` - Create Budget Rules

- Provider request: `POST /sd/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sd.create_campaigns` - Create Campaigns

- Provider request: `POST /sd/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}],"phase":"preview"}'`

## `sd.create_creatives` - Create Creatives

- Provider request: `POST /sd/creatives`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_creatives","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","creativeId":"7001","campaignId":"1001","adGroupId":"2001"}],"phase":"preview"}'`

## `sd.create_negative_targets` - Create Negative Targets

- Provider request: `POST /sd/negativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_negative_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `sd.create_product_ads` - Create Product Ads

- Provider request: `POST /sd/productAds`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_product_ads","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}],"phase":"preview"}'`

## `sd.create_targets` - Create Targets

- Provider request: `POST /sd/targets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.create_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `sd.list_ad_groups` - List Ad Groups

- Provider request: `GET /sd/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `sd.list_budget_rules` - List Budget Rules

- Provider request: `GET /sd/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `sd.list_campaigns` - List Campaigns

- Provider request: `GET /sd/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `sd.list_creatives` - List Creatives

- Provider request: `GET /sd/creatives`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_creatives","workspaceId":"user:42","connectionId":7}'`

## `sd.list_negative_targets` - List Negative Targets

- Provider request: `GET /sd/negativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_negative_targets","workspaceId":"user:42","connectionId":7}'`

## `sd.list_product_ads` - List Product Ads

- Provider request: `GET /sd/productAds`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_product_ads","workspaceId":"user:42","connectionId":7}'`

## `sd.list_targets` - List Targets

- Provider request: `GET /sd/targets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.list_targets","workspaceId":"user:42","connectionId":7}'`

## `sd.update_ad_groups` - Update Ad Groups

- Provider request: `PUT /sd/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}],"phase":"preview"}'`

## `sd.update_budget_rules` - Update Budget Rules

- Provider request: `PUT /sd/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesDetails":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sd.update_campaigns` - Update Campaigns

- Provider request: `PUT /sd/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}],"phase":"preview"}'`

## `sd.update_creatives` - Update Creatives

- Provider request: `PUT /sd/creatives`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_creatives","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","creativeId":"7001","campaignId":"1001","adGroupId":"2001"}],"phase":"preview"}'`

## `sd.update_negative_targets` - Update Negative Targets

- Provider request: `PUT /sd/negativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_negative_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `sd.update_product_ads` - Update Product Ads

- Provider request: `PUT /sd/productAds`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_product_ads","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}],"phase":"preview"}'`

## `sd.update_targets` - Update Targets

- Provider request: `PUT /sd/targets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sd.update_targets","workspaceId":"user:42","connectionId":7,"payload":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}],"phase":"preview"}'`

## `sp.create_ad_groups` - Create Ad Groups

- Provider request: `POST /sp/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `sp.create_budget_rules` - Create Budget Rules

- Provider request: `POST /sp/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRules":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sp.create_budget_rules_association` - Create Budget Rules Association

- Provider request: `POST /sp/budgetRulesAssociation`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_budget_rules_association","workspaceId":"user:42","connectionId":7,"payload":{"budgetRulesAssociation":[{"state":"PAUSED","campaignId":"1001","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sp.create_campaign_negative_keywords` - Create Campaign Negative Keywords

- Provider request: `POST /sp/campaignNegativeKeywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_campaign_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeKeywords":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"keywordId":"3001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.create_campaign_negative_targets` - Create Campaign Negative Targets

- Provider request: `POST /sp/campaignNegativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_campaign_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeTargetingClauses":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"targetId":"4001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `sp.create_campaigns` - Create Campaigns

- Provider request: `POST /sp/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `sp.create_keywords` - Create Keywords

- Provider request: `POST /sp/keywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_keywords","workspaceId":"user:42","connectionId":7,"payload":{"keywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.create_negative_keywords` - Create Negative Keywords

- Provider request: `POST /sp/negativeKeywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"negativeKeywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.create_negative_targets` - Create Negative Targets

- Provider request: `POST /sp/negativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"negativeTargetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `sp.create_product_ads` - Create Product Ads

- Provider request: `POST /sp/productAds`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_product_ads","workspaceId":"user:42","connectionId":7,"payload":{"productAds":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `sp.create_targets` - Create Targets

- Provider request: `POST /sp/targets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.create_targets","workspaceId":"user:42","connectionId":7,"payload":{"targetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `sp.list_ad_groups` - List Ad Groups

- Provider request: `POST /sp/adGroups/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_ad_groups","workspaceId":"user:42","connectionId":7}'`

## `sp.list_budget_rules` - List Budget Rules

- Provider request: `GET /sp/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_budget_rules","workspaceId":"user:42","connectionId":7}'`

## `sp.list_campaigns` - List Campaigns

- Provider request: `POST /sp/campaigns/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_campaigns","workspaceId":"user:42","connectionId":7}'`

## `sp.list_keywords` - List Keywords

- Provider request: `POST /sp/keywords/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_keywords","workspaceId":"user:42","connectionId":7}'`

## `sp.list_negative_keywords` - List Negative Keywords

- Provider request: `POST /sp/negativeKeywords/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_negative_keywords","workspaceId":"user:42","connectionId":7}'`

## `sp.list_product_ads` - List Product Ads

- Provider request: `POST /sp/productAds/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_product_ads","workspaceId":"user:42","connectionId":7}'`

## `sp.list_targets` - List Targets

- Provider request: `POST /sp/targets/list`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.list_targets","workspaceId":"user:42","connectionId":7}'`

## `sp.update_ad_groups` - Update Ad Groups

- Provider request: `PUT /sp/adGroups`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`

## `sp.update_budget_rules` - Update Budget Rules

- Provider request: `PUT /sp/budgetRules`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_budget_rules","workspaceId":"user:42","connectionId":7,"payload":{"budgetRules":[{"state":"PAUSED","budgetRuleId":"6001","name":"Example rule","ruleType":"SCHEDULE_BASED","budgetIncreaseBy":{"type":"PERCENTAGE","value":20}}]},"phase":"preview"}'`

## `sp.update_campaign_negative_keywords` - Update Campaign Negative Keywords

- Provider request: `PUT /sp/campaignNegativeKeywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_campaign_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeKeywords":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"keywordId":"3001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.update_campaign_negative_targets` - Update Campaign Negative Targets

- Provider request: `PUT /sp/campaignNegativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_campaign_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"campaignNegativeTargetingClauses":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"},"targetId":"4001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `sp.update_campaigns` - Update Campaigns

- Provider request: `PUT /sp/campaigns`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_campaigns","workspaceId":"user:42","connectionId":7,"payload":{"campaigns":[{"state":"PAUSED","campaignId":"1001","name":"Example campaign","budget":{"budget":10,"budgetType":"DAILY"}}]},"phase":"preview"}'`

## `sp.update_keywords` - Update Keywords

- Provider request: `PUT /sp/keywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_keywords","workspaceId":"user:42","connectionId":7,"payload":{"keywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.update_negative_keywords` - Update Negative Keywords

- Provider request: `PUT /sp/negativeKeywords`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_negative_keywords","workspaceId":"user:42","connectionId":7,"payload":{"negativeKeywords":[{"state":"PAUSED","keywordId":"3001","campaignId":"1001","adGroupId":"2001","keywordText":"example","matchType":"EXACT","bid":0.5}]},"phase":"preview"}'`

## `sp.update_negative_targets` - Update Negative Targets

- Provider request: `PUT /sp/negativeTargets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_negative_targets","workspaceId":"user:42","connectionId":7,"payload":{"negativeTargetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`

## `sp.update_product_ads` - Update Product Ads

- Provider request: `PUT /sp/productAds`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_product_ads","workspaceId":"user:42","connectionId":7,"payload":{"productAds":[{"state":"PAUSED","adId":"5001","campaignId":"1001","adGroupId":"2001","asin":"B012345678"}]},"phase":"preview"}'`

## `sp.update_targets` - Update Targets

- Provider request: `PUT /sp/targets`
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
- Example: `python scripts/amazon_api.py '{"operation":"sp.update_targets","workspaceId":"user:42","connectionId":7,"payload":{"targetingClauses":[{"state":"PAUSED","targetId":"4001","campaignId":"1001","adGroupId":"2001","expressionType":"MANUAL","expression":[{"type":"asinSameAs","value":"B012345678"}]}]},"phase":"preview"}'`
