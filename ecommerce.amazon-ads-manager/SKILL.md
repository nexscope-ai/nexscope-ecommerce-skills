---
name: ecommerce.amazon-ads-manager
version: 2.0.0
category: ecommerce
description: Read and mutate SP, SB, and SD campaigns, ad groups, ads, targeting, and budget rules.
---

# Amazon Ads Manager

Read and mutate SP, SB, and SD campaigns, ad groups, ads, targeting, and budget rules.

The package preserves 61 Amazon-platform operations (18 read or connection operations and 43 mutations). It uses only `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Provider credentials, refresh, request signing, authorization state, upload locations, and document locations remain on the backend.

## Core Concepts

- Manage Sponsored Products, Sponsored Brands, and Sponsored Display entities through exact cataloged paths and media types.
- List operations retain product-specific pagination and local ASIN/SKU filtering where the provider does not support those filters.
- SP paths are Sponsored Products Advertising API paths and are unrelated to the Seller SP-API.

## Operation Catalog

The concise index below is generated from the same contract consumed by the runtime. See `references/api.md` for full request, validation, pagination, result, status, and example details, and `references/api.json` for the machine-readable contract.

### `sb.create_ad_groups` - Create Ad Groups

- Request: `POST /sb/v4/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.create_ads` - Create Ads

- Request: `POST /sb/v4/ads/{adType}`; access: `write`; execution: `generic`.
- Required: `connectionId`, `adType`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.create_budget_rules` - Create Budget Rules

- Request: `POST /sb/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.create_campaigns` - Create Campaigns

- Request: `POST /sb/v4/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.list_ad_groups` - List Ad Groups

- Request: `POST /sb/v4/adGroups/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `sb.list_ads` - List Ads

- Request: `POST /sb/v4/ads/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `sb.list_budget_rules` - List Budget Rules

- Request: `GET /sb/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `sb.list_campaigns` - List Campaigns

- Request: `POST /sb/v4/campaigns/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`.
- Constraints: `none`. 
### `sb.update_ad_groups` - Update Ad Groups

- Request: `PUT /sb/v4/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.update_ads` - Update Ads

- Request: `PUT /sb/v4/ads`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.update_budget_rules` - Update Budget Rules

- Request: `PUT /sb/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sb.update_campaigns` - Update Campaigns

- Request: `PUT /sb/v4/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_ad_groups` - Create Ad Groups

- Request: `POST /sd/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_budget_rules` - Create Budget Rules

- Request: `POST /sd/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_campaigns` - Create Campaigns

- Request: `POST /sd/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_creatives` - Create Creatives

- Request: `POST /sd/creatives`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_negative_targets` - Create Negative Targets

- Request: `POST /sd/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_product_ads` - Create Product Ads

- Request: `POST /sd/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.create_targets` - Create Targets

- Request: `POST /sd/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.list_ad_groups` - List Ad Groups

- Request: `GET /sd/adGroups`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `sd.list_budget_rules` - List Budget Rules

- Request: `GET /sd/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `sd.list_campaigns` - List Campaigns

- Request: `GET /sd/campaigns`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`; body: None.
- Constraints: `none`. 
### `sd.list_creatives` - List Creatives

- Request: `GET /sd/creatives`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `creativeIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`.- Query: `adGroupIdFilter`, `creativeIdFilter`, `maxResults`, `nextToken`; body: None.
- Constraints: `none`. 
### `sd.list_negative_targets` - List Negative Targets

- Request: `GET /sd/negativeTargets`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `sd.list_product_ads` - List Product Ads

- Request: `GET /sd/productAds`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`.- Query: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `sd.list_targets` - List Targets

- Request: `GET /sd/targets`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`; body: None.
- Constraints: `none`. 
### `sd.update_ad_groups` - Update Ad Groups

- Request: `PUT /sd/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_budget_rules` - Update Budget Rules

- Request: `PUT /sd/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_campaigns` - Update Campaigns

- Request: `PUT /sd/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_creatives` - Update Creatives

- Request: `PUT /sd/creatives`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_negative_targets` - Update Negative Targets

- Request: `PUT /sd/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_product_ads` - Update Product Ads

- Request: `PUT /sd/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sd.update_targets` - Update Targets

- Request: `PUT /sd/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_ad_groups` - Create Ad Groups

- Request: `POST /sp/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_budget_rules` - Create Budget Rules

- Request: `POST /sp/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_budget_rules_association` - Create Budget Rules Association

- Request: `POST /sp/budgetRulesAssociation`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_campaign_negative_keywords` - Create Campaign Negative Keywords

- Request: `POST /sp/campaignNegativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_campaign_negative_targets` - Create Campaign Negative Targets

- Request: `POST /sp/campaignNegativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_campaigns` - Create Campaigns

- Request: `POST /sp/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_keywords` - Create Keywords

- Request: `POST /sp/keywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_negative_keywords` - Create Negative Keywords

- Request: `POST /sp/negativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_negative_targets` - Create Negative Targets

- Request: `POST /sp/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_product_ads` - Create Product Ads

- Request: `POST /sp/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.create_targets` - Create Targets

- Request: `POST /sp/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.list_ad_groups` - List Ad Groups

- Request: `POST /sp/adGroups/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `sp.list_budget_rules` - List Budget Rules

- Request: `GET /sp/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `sp.list_campaigns` - List Campaigns

- Request: `POST /sp/campaigns/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`.
- Constraints: `none`. 
### `sp.list_keywords` - List Keywords

- Request: `POST /sp/keywords/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `sp.list_negative_keywords` - List Negative Keywords

- Request: `POST /sp/negativeKeywords/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `sp.list_product_ads` - List Product Ads

- Request: `POST /sp/productAds/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `skuFilter`, `stateFilter`.
- Constraints: `none`. 
### `sp.list_targets` - List Targets

- Request: `POST /sp/targets/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`.
- Constraints: `none`. 
### `sp.update_ad_groups` - Update Ad Groups

- Request: `PUT /sp/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_budget_rules` - Update Budget Rules

- Request: `PUT /sp/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_campaign_negative_keywords` - Update Campaign Negative Keywords

- Request: `PUT /sp/campaignNegativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_campaign_negative_targets` - Update Campaign Negative Targets

- Request: `PUT /sp/campaignNegativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_campaigns` - Update Campaigns

- Request: `PUT /sp/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_keywords` - Update Keywords

- Request: `PUT /sp/keywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_negative_keywords` - Update Negative Keywords

- Request: `PUT /sp/negativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_negative_targets` - Update Negative Targets

- Request: `PUT /sp/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_product_ads` - Update Product Ads

- Request: `PUT /sp/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `sp.update_targets` - Update Targets

- Request: `PUT /sp/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 


## API Invocation

Ask for an owned `connectionId`, the intended account, marketplace, and region. `workspaceId` is optional: omit it when the API key is already bound to the workspace. Select an exact callable operation from `references/api.json`; do not invent paths or use a removed compatibility row. Run the relevant script from: `scripts/amazon_api.py`.

Reads may follow a continuation token only when `fetchAll` is true and always stop at `maxPages`. Paginated reads expose stable execution metadata: `success`, `pagesFetched`, `truncated`, and `total` when the list field is known. Client-side ASIN/SKU filters additionally report `serverTotalBeforeClientFilter` and `clientSideFilters`.

Ads entity mutations require preview, exact user approval, and a separate one-use confirmation. In the aggregate package, authorization remains a dedicated connection-lifecycle action rather than an entity mutation.

Ads requests use an owned Ads connection and the allowlisted Sponsored Products, Sponsored Brands, Sponsored Display, or reporting families. Report downloads use opaque backend tokens and optional safe `outputFile` publication.

## Authentication and Connection Lifecycle

- Set `NEXSCOPE_PROXY_BASE` to the approved gateway base and `NEXSCOPE_API_KEY` to the caller credential.
- Use the workspace resolved from the API key (or an explicit `workspaceId` override) and an owned `connectionId` to select the account. Do not ask for Ads access tokens, refresh tokens, OAuth client credentials, or signing secrets.
- If authorization is missing or expired, use the corresponding connection script to authorize or inspect status. Token persistence and refresh remain backend-owned.
- Billing or credit behavior is determined by the gateway contract; do not repeat legacy credit claims or onboarding instructions.

## Usage Examples

```bash
python scripts/amazon_api.py '{"operation":"sb.list_ad_groups","workspaceId":"user:42","connectionId":7}'
```

```bash
python scripts/amazon_api.py '{"operation":"sb.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'
```

Examples use placeholders. An Ads entity write preview is not approval; confirmation must be a separate command after the user accepts the exact preview.

## Display Rules

1. Identify the selected account, marketplace, operation, and whether it is read-only or a mutation.
2. For a mutation, show the preview and wait. Never print or reuse a confirmation token outside the separate approved confirm call.
3. For pagination, show `pagesFetched`, `total` when known, `truncated`, and the continuation token only when another bounded call is required.
4. For client-side filters, show the provider count before filtering and the filters applied.
5. For a pending report or feed, preserve the returned resource ID and show the structured resume instruction.
6. For documents, show `outputFile`, byte count, content type, and decode/compression metadata when returned; never expose a provider download location.
7. Treat 401/403 as authentication or ownership failures, 429 as a bounded-backoff condition, and 5xx as a sanitized upstream failure. Ads report 425 recovery applies only to the Ads report workflow.

## Important Limitations

- ASIN and SKU filters may run client-side after the provider page is received.
- Writes always require preview and a separate exact confirmation.
- Provider rate limits vary by operation and account. Honor returned rate-limit metadata and `Retry-After`; do not hardcode a universal requests-per-second value.
- The gateway allowlists exact API families. An unsupported path is a contract error, not a reason to bypass the gateway.
- Official API names and versions are recorded in `references/api.md`; this package intentionally contains no direct external host URL.

## User Expression and Scenario Quick Reference

| Classification | Guidance |
|---|---|
| Applicable | Read or change SP, SB, or SD campaign entities |
| Not applicable | Seller Central operations or report configuration discovery |

When the request crosses package boundaries, use the aggregate package only if its catalog contains the exact operation; otherwise choose the narrower package.

## Privacy and Errors

Do not request, print, cache, or store provider credentials. Treat advertising account, campaign, targeting, metric, and report data as private. Scripts exit nonzero for HTTP, application, upstream, invalid JSON, and malformed response failures. See `references/testing.md` for executable prompts, expected routes, error cases, and evidence.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
