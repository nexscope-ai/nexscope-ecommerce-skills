# AI Image Generation API Reference

## Request Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/multimodal/generateImage`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; read api_key from `nexscope_AGENT_API_KEY` or `nexscopeAGENT_API_KEY`. If neither is configured, follow the authentication and credits guidance in SKILL.md.

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| prompt | string | Yes | Prompt (supports text-to-image, image-to-image, image editing, and model replacement); maximum length 1000 |
| referenceImageUrl | string | No | Reference image URLs, separated by commas; up to 3 images; maximum length 1000 |
| aspectRatio | string | No | Aspect ratio: `1:1` (square, default), `3:4` (portrait), `4:3` (landscape), `9:16` (full-screen portrait), or `16:9` (full-screen landscape); default `1:1` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| id | string | id |
| finished | boolean | Whether generation is complete |
| status | string | Status |
| text | string | Image content |
| type | string | Markdown type |
| title | string | Image |
| costToken | integer | Tokens used |

## Error Codes

Normally, the API returns HTTP 200, and the errorCode field in the response body indicates business success or failure (errorCode = 200 means success; other values indicate business errors). For unauthorized requests, the HTTP status is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Recommended Action |
|---------|------|----------|
| 200 | Success | Parse the business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the authentication and credits guidance in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: follow the authentication and credits guidance in SKILL.md. |
| Other non-200 values | Business error | See `errmsg` for the specific cause of the error |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Examples

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/multimodal/generateImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a professional product photo of a red handbag with a white background and studio lighting",
    "aspectRatio": "1:1"
  }'
```

### Example with a Reference Image

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/multimodal/generateImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Change the background of image 1 to a tropical beach scene",
    "referenceImageUrl": "https://example.com/product.jpg",
    "aspectRatio": "4:3"
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
