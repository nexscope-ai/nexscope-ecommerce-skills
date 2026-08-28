# API contract for `ecommerce-tiktok-product-analytics-api`

## Scope

Retrieve price, sales, revenue, commission, lifecycle, and shop data for a specific TikTok product.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `kalodata_product_detail`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/kalodata/product/detail`
- Package script: `scripts/kalodata_product_detail.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/kalodata_product_detail.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
