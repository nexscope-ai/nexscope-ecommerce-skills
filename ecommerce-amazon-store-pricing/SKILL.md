---
name: ecommerce.amazon-store-pricing
description: Inspect pricing, competitive summaries, offers, and batch offer information.
version: 1.0.0
---

# Amazon Store Pricing

Inspect pricing, competitive summaries, offers, and batch offer information.

1. Use [the operation reference](references/api.md) to select the exact action and API version. When a connection is required, use an owned connection for the intended marketplace. Use `ecommerce.amazon-store-auth` to list, inspect, or authorize connections.
2. Create a JSON object using the documented fields and real inputs. The packaged examples use fictional values. Use the local dry run to check inputs before a network request.
3. Use `--execute` only after the user approves the call. Online calls consume Nexscope credits. Review returned business and Amazon status codes before using the data.
4. For writes, show the target and proposed change first. Preview only when supported, then ask for confirmation before sending the unchanged inputs and the issued token. A disconnect instead requires the latest revision and explicit confirmation. Do not automatically retry an ambiguous mutation.
5. Keep account selection, OAuth consent, and credentials in their existing authorized channels. Present an authorization link only to the requesting user. Do not request or expose Amazon access or refresh tokens.

## Local runner

Set `NEXSCOPE_API_KEY` for online requests and optionally `NEXSCOPE_PROXY_BASE` to the Nexscope HTTPS origin. List operations with:

```sh
python scripts/amazon_sp_api.py --list
```

Validate a JSON file locally with `python scripts/amazon_sp_api.py <api-slug> --input request.json`. Add `--execute` to send it. Add `--confirm-write` only for an approved confirmation or disconnect. The runner does not fan out, poll, download provider documents, or complete seller OAuth consent.

HTTP 401 indicates Nexscope authentication failure. HTTP 402 indicates insufficient credits. Inspect wrapper and provider errors. Keep the selected account and marketplace when handling authorization errors.

On HTTP 429, honor the returned Retry-After. Nexscope code 13012 indicates a request-rate limit and 13013 indicates a concurrent-request limit. Reconcile uncertain outcomes before requesting another paid call.

## Amazon Store Pricing workflow

Choose ASIN or SKU explicitly. For batch operations inspect each subresponse and report partial failures independently.

See [verification steps](references/testing.md) for local and test-environment acceptance.
