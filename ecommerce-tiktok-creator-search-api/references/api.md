# API contract for `ecommerce.tiktok-creator-search-api`

## Scope

Search TikTok ecommerce creator rankings by market and date range.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured Nexscope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `kalodata_creator_search`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/kalodata/creator/rank`
- Package script: `scripts/kalodata_creator_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. On both success and failure, the direct fields `code`, `errcode`, `errorCode`, `msg`, `errmsg`, `message`, and `errorMsg` are removed from public `data`. Read the message only from outer `msg`; deeper business fields are preserved, including nested `code` and `status`.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/kalodata_creator_search.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.

## API Key request rate and retries

All API Keys of one Nexscope user share the public API execution request-rate allowance, measured in any rolling 1-second window. The allowed RPS depends on that user's entitlements; it is not a universal 1 RPS. One Skill operation may issue multiple public API requests, each of which uses the allowance.

HTTP 429 with Nexscope outer code `13012` means request-rate exhaustion: honor the response's `Retry-After`. Outer code `13013` means concurrent-request exhaustion, not rate exhaustion; honor `Retry-After` when supplied. Check the HTTP status and outer JSON code separately. Do not automatically replay writes or requests with uncertain outcomes; first reconcile the operation's state.
