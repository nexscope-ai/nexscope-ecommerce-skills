# Testing evidence for `ecommerce-patent-search-api`

## Required user information

- Marketplace, region, or account context when applicable.
- Entity identifiers and filters required by the selected operation.
- Explicit confirmation for every mutation.

## Prompt coverage

1. Basic: request the core capability with one valid entity or input.
2. Filtered: add marketplace, time range, pagination, or business filters.
3. Advanced: request a structured deliverable or a multi-step analysis using returned evidence.
4. Error: omit a required identifier or provide malformed JSON.

## Evidence levels

- [ ] Static package validation recorded.
- [ ] Offline mock request recorded.
- [ ] Sandbox or test-environment request recorded.
- [ ] Real-account request recorded.
- [ ] ZIP import and installation recorded.
- [ ] English trigger and output review recorded.

Unchecked items are not evidence of failure; they have not been demonstrated yet. Never mark them complete without durable command output or an external test record.
- Assert every research-tool request path begins with `/api/v1/tools/research/`; reject legacy short paths in mocks and fixtures.
