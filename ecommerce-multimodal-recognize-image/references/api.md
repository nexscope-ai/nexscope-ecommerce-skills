# Image Recognition API Reference

## Request Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/multimodal/recognizeImage`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; read api_key from `nexscope_AGENT_API_KEY` or `nexscopeAGENT_API_KEY`. If neither is configured, follow the authentication and credits guidance in SKILL.md.

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| imageUrl | string | Yes | Image URL (jpg/jpeg/png/gif/webp/bmp only); maximum 1000 characters |
| requirement | string | No | User intent describing what to identify or analyze in the image; default literal is "描述这张图片里面的内容" (Describe the content of this image); maximum 1000 characters |


## Response Structure

| Field | Type | Description |
|------|------|------|
| text | string | Text result of the image analysis |
| stdout | string | Standard output content |
| status | string | Response status identifier |
| type | string | Component type |
| costToken | integer | Tokens consumed |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/multimodal/recognizeImage \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageUrl": "https://example.com/sample-product.jpg", "requirement": "Describe the content of this image and list its key visual features"}'
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
