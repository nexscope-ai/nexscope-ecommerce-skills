---
name: ecommerce.product-description-generator-api
version: 1.0.0
category: ecommerce
description: Generate product descriptions and other text asynchronously, or query an existing text-generation task by taskId. Use this skill for ecommerce copywriting, text/image/video-assisted content generation, task creation, status polling, and result retrieval.
---

# Product Description Generator Api

## Core Concepts

Generate text and analyze text, image, or video inputs with supported language models. The API is asynchronous: create a task first, then query it by `taskId` until it succeeds or fails.

## Core workflow

1. Identify the marketplace, entity identifiers, date range, filters, and requested output.
2. Ask only for missing inputs that materially change the result.
3. Submit the generation payload to `POST /api/v1/tools/research/aigc/textGenAsync` and retain the returned `taskId`.
4. Query `POST /api/v1/tools/research/aigc/textTaskQuery` with that `taskId` until the status is `SUCCESS` or `FAILED`.
5. Validate returned fields and preserve the distinction between source facts, calculations, and recommendations.
6. Save large results through the runtime and present a concise user-facing summary with the artifact path.

## Operation Catalog

| Operation | Mode | Mutation | Callable |
|---|---|---:|---:|
| `create_text_task` | gateway-script | no | yes |
| `query_text_task` | gateway-script | no | yes |

The machine-readable source of truth is `references/api.json`. Field-level payload rules remain operation-specific; do not invent identifiers, filters, credentials, or marketplace facts.

## API Invocation

Run only this package's `scripts/aigc_textgen.py`. Both operations use `NEXSCOPE_PROXY_BASE` and `NEXSCOPE_API_KEY`; do not call the legacy short paths directly.

## Usage Examples

```bash
# Create a task and return its taskId without polling.
python scripts/aigc_textgen.py --create-only --inline '{"prompt":"Write a product description for a wireless speaker","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}'

# Query one task by taskId.
python scripts/aigc_textgen.py --query-task --inline '{"taskId":"123456789"}'

# Default mode: create the task and poll until completion.
python scripts/aigc_textgen.py --inline '{"prompt":"Write a product description for a wireless speaker","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}'
```

For a cataloged mutation, obtain explicit user approval and then pass both `--confirm` and `--confirm-mutation`. Never infer confirmation from an earlier read request.

## Runtime configuration

Business/tool operations require `NEXSCOPE_PROXY_BASE` plus `NEXSCOPE_API_KEY`; authorization/account operations require the relevant `NEXSCOPE_AGENT_*` or `NEXSCOPE_LOGIN_*` base because those proxy routes are not implemented. Third-party connectors require their documented provider configuration. Install optional libraries named by a script only when that operation is selected. Read `references/credentials.md` and set only the variables required by the selected script. Never pass secrets in command arguments or persist them in output artifacts.

Use only the hosts, credentials, and endpoints implemented by the package-local script and documented in `references/credentials.md`. Never substitute an undocumented legacy host or expose secret values.

## Display Rules

- Keep full JSON in the generated `nexscope/<date>/<session>/data/` artifact.
- Show the user the relevant records, assumptions, calculations, and limitations.
- Redact authorization, tokens, cookies, secrets, and passwords recursively.
- Do not treat an HTTP 200 response as success when the response envelope or upstream payload reports a business failure.

## Important Limitations

- Do not fabricate marketplace data or silently fill required business identifiers.
- Do not retry a mutation after an ambiguous timeout; query status first.
- Treat legal, compliance, tax, and profitability outputs as decision support, not professional advice.
- Do not claim real-account, sandbox, ZIP-install, or production validation unless that evidence exists.

## References

- Read `references/workflow.md` before executing the domain procedure.
- Read `references/api.md` for the package contract and examples.
- Read `references/testing.md` before claiming a validation level.

## Privacy and Errors

Treat marketplace, account, product, advertising, order, supplier, and generated-asset data as private. Keep credentials out of payloads and artifacts. Surface HTTP, application-envelope, upstream-business, malformed-response, and unavailable-connector failures distinctly.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
