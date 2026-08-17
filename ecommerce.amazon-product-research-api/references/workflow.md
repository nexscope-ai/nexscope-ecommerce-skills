# Workflow contract for `ecommerce.amazon-product-research-api`

## Objective

Route Amazon product-selection work across market, keyword, competitor, trend, review, and profitability capabilities.

## Domain procedure

1. Route the request to the smallest set of installed Amazon product, keyword, niche, trend, review, and competitor capabilities.
2. Define a bounded funnel: broad discovery, eligibility filters, evidence enrichment, profitability and risk checks, then a ranked shortlist.
3. Do not rerun equivalent paid queries or merge incompatible time windows without disclosure.

## Inputs and dependencies

Gateway-backed steps require the approved NexScope proxy. Agent-guided steps may call other installed ecommerce skills named in the user's plan, but must not assume they are installed or authorized.

Use `references/api.json` to determine whether an operation is gateway-backed, agent-guided, or unavailable. Ask for missing identifiers only when they are required for the next operation.

## Deliverable contract

- State the scope, marketplace, time window, and user constraints.
- Separate retrieved facts, deterministic calculations, assumptions, and recommendations.
- Include artifact paths for large JSON, HTML, CSV, or spreadsheet-compatible results.
- Report unavailable sources and partial coverage explicitly.
