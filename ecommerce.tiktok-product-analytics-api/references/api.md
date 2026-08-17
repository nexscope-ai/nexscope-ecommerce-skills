# API contract for `ecommerce.tiktok-product-analytics-api`

## Scope

Retrieve price, sales, revenue, commission, lifecycle, and shop data for a specific TikTok product.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

## Operations

### `kalodata_product_detail`

- Execution mode: `local-script`
- Callable: `true`
- Mutation: `false`
- Gateway path: `none`
- Upstream semantic path: `scripts/kalodata_product_detail.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`

## Response and errors

Local scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/kalodata_product_detail.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
