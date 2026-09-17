---
name: ecommerce.google-patent-search
description: Query Google Patents public search through the Nexscope research proxy. Use when the user requests this public marketplace or patent data; do not use for seller-console or store-authorized operations.
---

# ecommerce.google-patent-search

Use this skill to query Google Patents public search. Read [references/api.md](references/api.md) before constructing a request.


## Request contract

- Endpoint: `POST /api/v1/tools/research/googlePatent/search`
- Required: `q` (non-empty query, maximum 1000 characters).
- Optional: `num` (10-100), `page`, `country`, `language`, `before`, `after`, `sort`, `type`, `status`, `patents`, `scholar`, `litigation`, `inventor`, `assignee`, `clustered`, `dups`.
- Send only documented fields; reject unknown fields before network access.

Minimal example:

```json
{"q":"wireless earbuds","num":10,"page":1}
```

## Workflow

1. Confirm the requested public entity, market, operation, filters, and expected cost.
2. Validate parameters against the API reference. Send only documented business fields.
3. Run `python scripts/google_patent_search.py '<JSON parameters>' --no-cache` once. Do not probe alternate products, markets, pages, or operations after a paid failure without user approval.
4. Preserve the full response file. Distinguish the Nexscope transport envelope from the inner business response and report `traceId` on errors.
5. Summarize only returned facts. Preserve missing values as unknown and identify the requested market and operation.

## Cost

Do not reuse the source Skill's point value. This operation consumes Nexscope credits. Preserve `X-Cost-Token` and `X-Cost-Credit` from the response headers as server-reported billing metadata. The exact charge is unknown before the first live response.

## Error and credit handling

- HTTP 401 means Nexscope authentication failed. Verify `NEXSCOPE_API_KEY` and `NEXSCOPE_PROXY_BASE`; do not ask the user to paste credentials into chat or operation JSON.
- HTTP 402 means the account lacks credits. Stop the workflow and direct the user to the access-help page below.
- Marketplace authorization failures require the platform-specific account or token to be renewed. Do not substitute a different store, region, or creator automatically.
- For ambiguous network failures, report whether the attempted operation was a read or mutation. Never repeat a mutation without reconciling its upstream state.

## Response handling

For the research HTTP response, require a numeric outer `code` equal to `0` before using `data`. Nonzero codes are platform failures; display outer `msg` without interpreting its wording as a retry instruction. Nexscope preserves upstream messages and translates Chinese to English; successful responses may have `msg: null`. HTTP 200 alone and nested business `code` / `status` do not replace the platform check. See `references/api.md` for response paths and task-specific states.

Package scripts that unwrap the response keep the platform `code` and `msg` under `_nexscope`; their remaining fields are the business payload. `_nexscope.cost` is elapsed time, not credits.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit [https://www.nexscope.ai/help/skills-external-access?co-from=skillNS](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS) to top up credits.

## Presenting results

- Lead with the requested entity, market, operation, and the most decision-relevant returned fields.
- Preserve source currencies, units, identifiers, dates, and missing values; do not invent conversions or defaults.
- Keep the full JSON artifact and present compact tables for repeated records when useful.
- Report the `X-Cost-Token`, calculated Nexscope credits, and trace ID from the saved billing metadata.

## Boundaries and privacy

- This migration is public-data and read-only. Do not invoke seller-console, store-authorized, favorite-write, or account mutation operations.
- One explicit request per call. Do not silently change entity, market, date, operation, or page after an error.
- Redact credentials, signed URLs, cookies, and internal account identifiers from user-facing output and saved request examples.
- Do not claim live, ZIP-install, or production validation unless the matching evidence exists in `references/testing.md`.

## References

- Read [references/api.md](references/api.md) for the complete parameter, response, and error contract.
- Read [references/testing.md](references/testing.md) before executing a live request or claiming a validation level.
