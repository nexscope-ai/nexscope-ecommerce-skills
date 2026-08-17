# API contract for `ecommerce.tiktok-creator-search-api`

## Scope

Search TikTok ecommerce creator rankings by market and date range.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

## Operations

### `kalodata_creator_search`

- Execution mode: `local-script`
- Callable: `true`
- Mutation: `false`
- Gateway path: `none`
- Upstream semantic path: `scripts/kalodata_creator_search.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`

## Response and errors

Local scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/kalodata_creator_search.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
