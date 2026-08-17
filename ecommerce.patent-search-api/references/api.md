# API contract for `ecommerce.patent-search-api`

## Scope

Search a patent database with Analytics query expressions and return matching patent identifiers and publication numbers.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `zhihuiya_query_search_patent`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/zhihuiya/querySearchPatent`
- Package script: `scripts/zhihuiya_query_search_patent.py`
- Required inputs: `none cataloged`
- Optional inputs: `cliArgs`
## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/zhihuiya_query_search_patent.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
