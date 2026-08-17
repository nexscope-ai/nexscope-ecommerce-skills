# API contract for `ecommerce.product-description-generator-api`

## Scope

Create asynchronous text-generation tasks and query their status and results by `taskId`. Both routes are exposed through the NexScope research gateway.

## Operations

### `create_text_task`

- Method and path: `POST /api/v1/tools/research/aigc/textGenAsync`
- Script mode: `python scripts/aigc_textgen.py --create-only --inline '<JSON>'`
- Required inputs: `prompt`, `imageUrls`, `thinkingLevel`
- Optional inputs: `model`, `memberId`
- Result: returns a `taskId` immediately; it does not wait for generated content.

Supported models are `GEM_3_FLASH` and `GEM_3_1_PRO`. Use an empty `imageUrls` array for text-only generation. Image or video URLs may be supplied when multimodal analysis is required. `thinkingLevel` accepts `minimal`, `low`, `medium`, or `high`; `GEM_3_1_PRO` does not support `minimal`.

### `query_text_task`

- Method and path: `POST /api/v1/tools/research/aigc/textTaskQuery`
- Script mode: `python scripts/aigc_textgen.py --query-task --inline '<JSON>'`
- Required input: `taskId`
- Optional input: `memberId`
- Result: returns `PROCESSING`, `SUCCESS`, or `FAILED`; successful results include generated `content` and may include token-usage fields.

Do not create another task when a previous create request timed out ambiguously. Query the known `taskId` first.

## Combined workflow

The default script mode creates a task and polls the query route until completion:

```bash
python scripts/aigc_textgen.py --inline '{"prompt":"Write a concise product description for a wireless speaker","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}'
```

Create and query separately:

```bash
python scripts/aigc_textgen.py --create-only --inline '{"prompt":"Write a concise product description for a wireless speaker","imageUrls":[],"model":"GEM_3_FLASH","thinkingLevel":"minimal"}'
python scripts/aigc_textgen.py --query-task --inline '{"taskId":"123456789"}'
```

## Runtime and errors

Set `NEXSCOPE_PROXY_BASE` to the gateway origin, without the research route suffix, and set `NEXSCOPE_API_KEY`. The script sends `Authorization: Bearer <key>` and JSON request bodies.

Treat HTTP failures, non-success response envelopes, `FAILED` task status, malformed responses, and polling timeouts as distinct errors. Never expose the API key.

The script accepts both the standard gateway envelope (`code`, `data`) and the legacy flat business response. It unwraps a successful gateway response before reading `taskId`, `status`, `content`, and `costToken`.
