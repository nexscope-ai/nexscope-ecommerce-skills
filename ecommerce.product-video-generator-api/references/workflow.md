# Workflow contract for `ecommerce.product-video-generator-api`

## Objective

Generate video asynchronously from one image or controlled first and last frames.

## Domain procedure

1. Confirm the entity identifiers, marketplace, time range, filters, and output required by the selected operation.
2. Run the smallest cataloged operation that satisfies the request and preserve the original response fields.
3. Validate business status, redact secrets, and explain missing or unsupported fields instead of inventing values.

## Inputs and dependencies

Gateway-backed steps require the approved NexScope proxy. Agent-guided steps may call other installed ecommerce skills named in the user's plan, but must not assume they are installed or authorized.

Use `references/api.json` to determine whether an operation is gateway-backed, agent-guided, or unavailable. Ask for missing identifiers only when they are required for the next operation.

## Deliverable contract

- State the scope, marketplace, time window, and user constraints.
- Separate retrieved facts, deterministic calculations, assumptions, and recommendations.
- Include artifact paths for large JSON, HTML, CSV, or spreadsheet-compatible results.
- Report unavailable sources and partial coverage explicitly.
