---
name: ecommerce-amazon-advertising-api
description: "Authorize Amazon Ads accounts, manage SP, SB, and SD entities, and retrieve advertising reports."
metadata:
  version: "2.0.0"
  category: "ecommerce"
---

# Amazon Ads

Authorize Amazon Ads accounts, manage SP, SB, and SD entities, and retrieve advertising reports.

The package preserves 67 Amazon-platform operations (23 read or connection operations and 44 mutations). It uses only `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Provider credentials, refresh, request signing, authorization state, upload locations, and document locations remain on the backend.

## Core Concepts

- Use one backend-owned Ads connection for authorization, SP/SB/SD entity management, and v3 reporting.
- The aggregate catalog routes connection and report operations to dedicated scripts and ordinary entity operations to the generic client.
- Amazon Ads uses the separate Advertising API and authorization service, not the Seller SP-API; SP here means Sponsored Products.

## Operation Catalog

The concise index below is generated from the same contract consumed by the runtime. See `references/api.md` for full request, validation, pagination, result, status, and example details, and `references/api.json` for the machine-readable contract.

### `ads_auth.authorize_url` - Authorize Url

- Request: `POST /api/skill/amazon/connections/amazon-ads/authorize`; access: `write`; execution: `specialized`.
- Required: `region`, `marketplaceId`.- Optional: `workspaceId`, `accountName`, `returnPath`.- Query: None; body: `workspaceId`, `region`, `marketplaceId`, `accountName`, `returnPath`.
- Constraints: `none`. 
### `ads_auth.authorized_stores` - Authorized Stores

- Request: `GET /api/skill/amazon/connections/amazon-ads`; access: `read`; execution: `specialized`.
- Required: None.- Optional: `workspaceId`.- Query: `workspaceId`; body: None.
- Constraints: `none`. 
### `ads_auth.profiles` - Profiles

- Request: `GET /api/skill/amazon/connections/amazon-ads/profiles`; access: `read`; execution: `specialized`.
- Required: `connectionId`.- Optional: `workspaceId`.- Query: `workspaceId`, `connectionId`; body: None.
- Constraints: `none`. 
### `ads_auth.refresh_token` - Refresh Token

- Request: `NONE backend-owned token refresh`; access: `write`; execution: `removed`.
- Required: None.
- Optional: None.
- Query: None; body: None.
- Constraints: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.
### `ads_auth.store_tokens` - Store Tokens

- Request: `NONE backend-owned OAuth callback token storage`; access: `write`; execution: `removed`.
- Required: None.
- Optional: None.
- Query: None; body: None.
- Constraints: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.
### `ads_manager.sb.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sb/v4/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.create_ads` - Create Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sb/v4/ads/{adType}`; access: `write`; execution: `generic`.
- Required: `connectionId`, `adType`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sb/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sb/v4/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sb/v4/adGroups/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sb.list_ads` - List Ads

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sb/v4/ads/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sb.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sb/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `ads_manager.sb.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sb/v4/campaigns/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sb.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sb/v4/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.update_ads` - Update Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sb/v4/ads`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sb/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sb.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sb/v4/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_creatives` - Create Creatives

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/creatives`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_negative_targets` - Create Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_product_ads` - Create Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.create_targets` - Create Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sd/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/adGroups`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/campaigns`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_creatives` - List Creatives

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/creatives`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `creativeIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`.- Query: `adGroupIdFilter`, `creativeIdFilter`, `maxResults`, `nextToken`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_negative_targets` - List Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/negativeTargets`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_product_ads` - List Product Ads

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/productAds`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`.- Query: `adGroupIdFilter`, `adIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.list_targets` - List Targets

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sd/targets`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`.- Query: `adGroupIdFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`; body: None.
- Constraints: `none`. 
### `ads_manager.sd.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_creatives` - Update Creatives

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/creatives`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_negative_targets` - Update Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_product_ads` - Update Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sd.update_targets` - Update Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sd/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_ad_groups` - Create Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_budget_rules` - Create Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_budget_rules_association` - Create Budget Rules Association

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/budgetRulesAssociation`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_campaign_negative_keywords` - Create Campaign Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/campaignNegativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_campaign_negative_targets` - Create Campaign Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/campaignNegativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_campaigns` - Create Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_keywords` - Create Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/keywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_negative_keywords` - Create Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/negativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_negative_targets` - Create Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_product_ads` - Create Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.create_targets` - Create Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `POST /sp/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.list_ad_groups` - List Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/adGroups/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `campaignTargetingTypeFilter`, `maxResults`, `nameFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sp.list_budget_rules` - List Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `GET /sp/budgetRules`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `fetchAll`, `maxPages`, `nextToken`, `queryString`, `requestId`.- Query: `nextToken`; body: None.
- Constraints: `none`. 
### `ads_manager.sp.list_campaigns` - List Campaigns

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/campaigns/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `campaignIdFilter`, `maxResults`, `nameFilter`, `nextToken`, `portfolioIdFilter`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sp.list_keywords` - List Keywords

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/keywords/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `keywordIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sp.list_negative_keywords` - List Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/negativeKeywords/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `fetchAll`, `keywordTextFilter`, `matchTypeFilter`, `maxPages`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `queryString`, `requestId`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `keywordTextFilter`, `matchTypeFilter`, `maxResults`, `negativeKeywordIdFilter`, `nextToken`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sp.list_product_ads` - List Product Ads

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/productAds/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `skuFilter`, `stateFilter`.- Query: None; body: `adGroupIdFilter`, `adIdFilter`, `asinFilter`, `campaignIdFilter`, `maxResults`, `nextToken`, `skuFilter`, `stateFilter`.
- Constraints: `none`. 
### `ads_manager.sp.list_targets` - List Targets

- Gateway request: `POST /api/skill/amazon/ads/read`; provider request (request-body `path`): `POST /sp/targets/list`; access: `read`; execution: `generic`.
- Required: `connectionId`.- Optional: `workspaceId`, `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `fetchAll`, `maxPages`, `maxResults`, `nextToken`, `queryString`, `requestId`, `stateFilter`, `targetIdFilter`.- Query: None; body: `adGroupIdFilter`, `campaignIdFilter`, `expressionTypeFilter`, `maxResults`, `nextToken`, `stateFilter`, `targetIdFilter`.
- Constraints: `none`. 
### `ads_manager.sp.update_ad_groups` - Update Ad Groups

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/adGroups`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_budget_rules` - Update Budget Rules

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/budgetRules`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_campaign_negative_keywords` - Update Campaign Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/campaignNegativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_campaign_negative_targets` - Update Campaign Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/campaignNegativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_campaigns` - Update Campaigns

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/campaigns`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_keywords` - Update Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/keywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_negative_keywords` - Update Negative Keywords

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/negativeKeywords`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_negative_targets` - Update Negative Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/negativeTargets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_product_ads` - Update Product Ads

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/productAds`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_manager.sp.update_targets` - Update Targets

- Gateway request: `POST /api/skill/amazon/ads/write-preview -> POST /api/skill/amazon/ads/write-confirm`; provider request (request-body `path`): `PUT /sp/targets`; access: `write`; execution: `generic`.
- Required: `connectionId`, `payload`.- Optional: `workspaceId`, `queryString`, `requestId`.- Query: None; body: `payload`.
- Constraints: `none`. 
### `ads_report.get_report` - Get Report

- Request: `POST /reporting/reports`; access: `write`; execution: `specialized`.
- Required: `connectionId`.- Optional: `workspaceId`, `reportId`, `reportTypeId`, `adProduct`, `groupBy`, `columns`, `name`, `startDate`, `endDate`, `timeUnit`, `format`, `filters`, `configuration`, `timeoutSeconds`, `pollIntervalSeconds`, `outputFile`, `overwrite`.- Query: None; body: `name`, `startDate`, `endDate`, `configuration`.
- Constraints: `none`. 


## API Invocation

Ask for an owned `connectionId`, the intended account, marketplace, and region. `workspaceId` is optional: omit it when the API key is already bound to the workspace. Select an exact callable operation from `references/api.json`; do not invent paths or use a removed compatibility row. Run the relevant script from: `scripts/amazon_api.py`, `scripts/amazon_connection.py`, `scripts/amazon_ads_report_workflow.py`.

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
python scripts/amazon_connection.py '{"action":"connections","workspaceId":"user:42"}'
```

```bash
python scripts/amazon_connection.py '{"action":"authorize","workspaceId":"user:42","region":"NA","marketplaceId":"ATVPDKIKX0DER","accountName":"Example account"}'
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

- Choose the connection bound to the intended Ads profile before any read or write.
- Use the report-type catalog instead of inventing v3 columns, groupBy, filters, or date ranges.
- Provider rate limits vary by operation and account. Honor returned rate-limit metadata and `Retry-After`; do not hardcode a universal requests-per-second value.
- The gateway allowlists exact API families. An unsupported path is a contract error, not a reason to bypass the gateway.
- Official API names and versions are recorded in `references/api.md`; this package intentionally contains no direct external host URL.

## User Expression and Scenario Quick Reference

| Classification | Guidance |
|---|---|
| Applicable | Ads authorization, entity management, or advertising reports |
| Not applicable | Seller catalog, orders, listings, or pricing |

When the request crosses package boundaries, use the aggregate package only if its catalog contains the exact operation; otherwise choose the narrower package.

## Privacy and Errors

Do not request, print, cache, or store provider credentials. Treat advertising account, campaign, targeting, metric, and report data as private. Scripts exit nonzero for HTTP, application, upstream, invalid JSON, and malformed response failures. See `references/testing.md` for executable prompts, expected routes, error cases, and evidence.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
