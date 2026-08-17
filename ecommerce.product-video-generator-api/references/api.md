# API contract for `ecommerce.product-video-generator-api`

## Scope

Generate video asynchronously from one image or controlled first and last frames.

`references/api.json` is the machine-readable source of truth. The runtime accepts an operation identifier plus one JSON object. Gateway-backed operations forward only to the configured NexScope host.

All research-tool gateway paths are absolute paths relative to the `NEXSCOPE_PROXY_BASE` origin and begin with `/api/v1/tools/research/`. Do not call the legacy short provider paths directly.

## Operations

### `create_video_task`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/aigc/videoGenAsync`
- Package script: `scripts/aigc_videogen.py`
- Required inputs: `imageUrl, videoType, videoTime`
- Optional inputs: `prompt, promptOptimizer, isPro, voice, lastFrameImageUrl, aspectRatio, resolution, memberId`

### `query_video_task`

- Execution mode: `gateway-script`
- Callable: `true`
- Mutation: `false`
- Method and gateway path: `POST /api/v1/tools/research/aigc/taskQuery`
- Package script: `scripts/aigc_videogen.py`
- Required inputs: `taskId`
- Optional inputs: `memberId`

## Response and errors

Package scripts validate their arguments and write only the requested local artifact. Agent-guided operations report missing evidence instead of fabricating gateway responses.

## Example

```bash
python scripts/aigc_videogen.py --help
# Run the selected local script with its documented arguments.
```

Unavailable operations describe a missing approved connector and must not be rerouted to a direct provider host.
