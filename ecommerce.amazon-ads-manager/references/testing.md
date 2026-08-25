# Verification guide

## Directly executable prompts

1. Basic: "Run `python scripts/amazon_api.py '{"operation":"sb.list_ad_groups","workspaceId":"user:42","connectionId":7}'` and show the unwrapped result without exposing credentials."
2. Filtered: "Run `python scripts/amazon_api.py '{"operation":"sb.list_ad_groups","workspaceId":"user:42","connectionId":7,"fetchAll":true,"maxPages":5}'` and summarize the bounded page, status, or alternate operation result."
3. Advanced: "Run `python scripts/amazon_api.py '{"operation":"sb.create_ad_groups","workspaceId":"user:42","connectionId":7,"payload":{"adGroups":[{"state":"PAUSED","adGroupId":"2001","campaignId":"1001","name":"Example ad group","defaultBid":0.5}]},"phase":"preview"}'`; if it returns a write preview, show the exact preview and wait for explicit approval before a separate confirm invocation."

## Required user information

Collect an owned `connectionId`, the intended Amazon account, marketplace, and region, plus the operation-specific path, query, and body fields in `api.json`. `workspaceId` is optional: omit it when the API key is already bound to the workspace. Never request provider access or refresh tokens.

## Expected route and result

- Ads reads use `POST /api/skill/amazon/ads/read`; Ads mutations use `POST /api/skill/amazon/ads/write-preview` followed after exact approval by `write-confirm`. The aggregate package also uses the Amazon Ads connection routes.
- Documents are represented by opaque tokens. Download envelopes may contain JSON, CSV, text, or binary `contentBase64`; an optional caller path may save at most 20 MiB. Existing files are not overwritten unless `overwrite:true` is supplied, and symlink or non-regular targets are rejected.

## Operational notes

Amazon may charge advertising spend or apply account mutations. Confirm writes explicitly. Respect region and marketplace selection, rate limits, next-token pagination, bounded `maxPages`, polling timeout, and resume IDs. Treat order, customer, advertising, and document content as private. Do not log secrets or opaque document tokens.

## Error cases

Test missing and invalid fields, invalid JSON, 401, 403, 429, 5xx, polling timeout, empty results, malformed or non-JSON gateway responses, a mismatched confirmation token, expired document tokens, and unsupported document encodings. No live provider request is part of static validation.

## Evidence

- [x] Static
- [x] Mock
- [ ] Sandbox
- [ ] Live
- [ ] ZIP
- [x] English
