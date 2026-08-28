# API contract for `ecommerce-reverse-product-image-search-api`

## Scope

Find visual or keyword-derived competitors from a product image or URL across supported marketplaces.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `step_3_5_junglescout`

- Execution mode: `local-script`
- Callable: `true`
- Mutation: `false`
- Gateway path: `none`
- Upstream semantic path: `scripts/step_3_5_junglescout.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `step_4_merge_rank`

- Execution mode: `local-script`
- Callable: `true`
- Mutation: `false`
- Gateway path: `none`
- Upstream semantic path: `scripts/step_4_merge_rank.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
### `junglescout_sales_estimates`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/tool-jungle-scout/sales-estimates/query`
- Package script: `scripts/junglescout_sales_estimates.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/step_3_5_junglescout.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
