---
name: ecommerce.amazon-ads-api-access
version: 2.0.0
category: ecommerce
description: Authorize Amazon Ads accounts and inspect safe connection and profile metadata.
---

# Amazon Ads Auth

Authorize Amazon Ads accounts and inspect safe connection and profile metadata.

The package preserves 5 Amazon-platform operations (4 read or connection operations and 1 mutation). It uses only `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`. Provider credentials, refresh, request signing, authorization state, upload locations, and document locations remain on the backend.

## Core Concepts

- Authorization creates a backend-owned connection; provider access and refresh tokens never enter the skill runtime.
- Profiles are safe account metadata used to choose the correct advertising account before reads or mutations.
- The backend Ads authorization service resolves OAuth application parameters; the local database stores OAuth state, encrypted credentials, and connection/profile metadata.
- This Advertising API authorization flow is separate from Seller Central and does not use the Seller SP-API connector.

## Operation Catalog

The concise index below is generated from the same contract consumed by the runtime. See `references/api.md` for full request, validation, pagination, result, status, and example details, and `references/api.json` for the machine-readable contract.

### `authorize_url` - Authorize Url

- Request: `POST /api/skill/amazon/connections/amazon-ads/authorize`; access: `write`; execution: `specialized`.
- Required: `region`, `marketplaceId`.- Optional: `workspaceId`, `accountName`, `returnPath`.- Query: None; body: `workspaceId`, `region`, `marketplaceId`, `accountName`, `returnPath`.
- Constraints: `none`. 
### `authorized_stores` - Authorized Stores

- Request: `GET /api/skill/amazon/connections/amazon-ads`; access: `read`; execution: `specialized`.
- Required: None.- Optional: `workspaceId`.- Query: `workspaceId`; body: None.
- Constraints: `none`. 
### `profiles` - Profiles

- Request: `GET /api/skill/amazon/connections/amazon-ads/profiles`; access: `read`; execution: `specialized`.
- Required: `connectionId`.- Optional: `workspaceId`.- Query: `workspaceId`, `connectionId`; body: None.
- Constraints: `none`. 
### `refresh_token` - Refresh Token

- Request: `NONE backend-owned token refresh`; access: `write`; execution: `removed`.
- Required: None.
- Optional: None.
- Query: None; body: None.
- Constraints: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.
### `store_tokens` - Store Tokens

- Request: `NONE backend-owned OAuth callback token storage`; access: `write`; execution: `removed`.
- Required: None.
- Optional: None.
- Query: None; body: None.
- Constraints: `none`. The backend owns token storage and refresh; use authorization status and connection metadata.


## API Invocation

Ask for an owned `connectionId`, the intended account, marketplace, and region. `workspaceId` is optional: omit it when the API key is already bound to the workspace. Select an exact callable operation from `references/api.json`; do not invent paths or use a removed compatibility row. Run the relevant script from: `scripts/amazon_connection.py`.

Reads may follow a continuation token only when `fetchAll` is true and always stop at `maxPages`. Paginated reads expose stable execution metadata: `success`, `pagesFetched`, `truncated`, and `total` when the list field is known. Client-side ASIN/SKU filters additionally report `serverTotalBeforeClientFilter` and `clientSideFilters`.

Authorization is a connection-lifecycle action executed once through the dedicated connection route; it is not an Ads entity mutation and does not use write preview/confirm.

Authorization state, OAuth application parameters, token exchange, encrypted credential storage, and profile discovery remain backend-owned. The skill receives only the authorization URL and safe connection metadata.

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

Examples use placeholders. The authorization command starts the backend-owned Ads OAuth flow and never accepts provider credentials.

## Display Rules

1. Identify the selected account, marketplace, operation, and whether it is read-only or a mutation.
2. For a mutation, show the preview and wait. Never print or reuse a confirmation token outside the separate approved confirm call.
3. For pagination, show `pagesFetched`, `total` when known, `truncated`, and the continuation token only when another bounded call is required.
4. For client-side filters, show the provider count before filtering and the filters applied.
5. For a pending report or feed, preserve the returned resource ID and show the structured resume instruction.
6. For documents, show `outputFile`, byte count, content type, and decode/compression metadata when returned; never expose a provider download location.
7. Treat 401/403 as authentication or ownership failures, 429 as a bounded-backoff condition, and 5xx as a sanitized upstream failure. Ads report 425 recovery applies only to the Ads report workflow.

## Important Limitations

- Legacy token storage and refresh commands are intentionally not callable; inspect connection status instead.
- Provider rate limits vary by operation and account. Honor returned rate-limit metadata and `Retry-After`; do not hardcode a universal requests-per-second value.
- The gateway allowlists exact API families. An unsupported path is a contract error, not a reason to bypass the gateway.
- Official API names and versions are recorded in `references/api.md`; this package intentionally contains no direct external host URL.

## User Expression and Scenario Quick Reference

| Classification | Guidance |
|---|---|
| Applicable | Authorize Ads and list safe profiles or connections |
| Not applicable | Manage campaigns or download reports |

When the request crosses package boundaries, use the aggregate package only if its catalog contains the exact operation; otherwise choose the narrower package.

## Privacy and Errors

Do not request, print, cache, or store provider credentials. Treat advertising account, campaign, targeting, metric, and report data as private. Scripts exit nonzero for HTTP, application, upstream, invalid JSON, and malformed response failures. See `references/testing.md` for executable prompts, expected routes, error cases, and evidence.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
