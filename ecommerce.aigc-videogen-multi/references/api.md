# Multi-image video API

## Create task

`POST /api/v1/tools/research/aigc/multiImageVideoGenAsync`

| Field | Type | Required | Rules |
|---|---|---:|---|
| `imageList` | string[] | Yes | Public image URLs. KLING supports up to 7; SEED, SEED_FAST, and HAPPY_HORSE up to 9. |
| `videoType` | string | Yes | `KLING`, `SEED`, `SEED_FAST`, or `HAPPY_HORSE`. |
| `videoTime` | integer | Yes | KLING: 5/10; other models: 5/10/15 seconds. |
| `prompt` | string | Yes | Video description, maximum 2000 characters. The gateway currently rejects requests without it. |
| `promptOptimizer` | boolean | No | Default `false`. |
| `isPro` | boolean | No | Supported by KLING and SEED. |
| `voice` | boolean | No | Supported by SEED and SEED_FAST. |
| `aspectRatio` | string | No | `16:9` or `9:16`; default `16:9`. |
| `resolution` | string | No | Model-dependent: `480p`, `720p`, or `1080p`. SEED_FAST does not support `1080p`. |
| `memberId` | string | No | Forward only when supplied by the runtime. |

Success returns a `taskId`. This operation is asynchronous, consumes credits, and must not be retried after an ambiguous timeout. Query the returned task first.

## Query task

`POST /api/v1/tools/research/aigc/taskQuery`

Request: `{"taskId":"...","memberId":"..."}`. `memberId` is optional.

Statuses are `PROCESSING`, `SUCCESS`, and `FAILED`. On success, read `resultList[].url`; on failure, surface `errorMsg`. Poll every 10 seconds, wait about 120 seconds before the first poll, and stop after 20 minutes.

## Example

```bash
python scripts/aigc_videogen_multi.py '{"imageList":["https://example.com/product.jpg"],"videoType":"KLING","videoTime":5,"prompt":"Slow product rotation on a clean studio background"}'
```

Treat HTTP success separately from `code`/`errcode` and task status. Prefer `X-Cost-Token`; otherwise read `costToken`.
