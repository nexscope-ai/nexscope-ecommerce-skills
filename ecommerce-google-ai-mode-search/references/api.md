# Google AI Mode Search API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aiMode/googleSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| keyword | string | Yes | Google search keyword, passed as the `q=` parameter to initiate a Google AI Mode search. Only supports single-turn conversation; follow-up prompts are not supported. To ask follow-up questions, the agent must independently summarize key information from the previous AI overview, concatenate the new question, and send it as a new keyword in a new request |

## Response Structure

| Field | Type | Description |
|------|------|------|
| stdout | string | AI overview content in Markdown format; outputs key points and reference source links for each question's AI overview in order |
| sourceUrl | string | Target URL that was crawled, the final Google search page URL |
| resultsNum | integer | Number of AI overview blocks; >0 indicates the page rendered an AI Overview, 0 indicates the keyword did not trigger an AI Overview |
| code | string | Business status code, success is `"200"` (same as the numeric `errcode`) |
| errcode | integer | Business status code (HTTP layer is generally 200; business success/failure is determined by this field) |
| msg / errmsg | string | Response message, `ok` on success |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Token consumption for this call; billed only when upstream returns success |
| taskId | string | Upstream capture task identifier for this request |
| type | string | Render style, fixed `stdoutWorkbenches`, used with the `stdout` field for Markdown rendering |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the `errcode` / `code` fields in the response body (`200` indicates success; other values indicate business errors). In cases of unauthorized access, the HTTP status code will be 401, with the corresponding `errcode` also being 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `stdout` and other business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Billing/insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` / `msg` fields for specific error cause |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/aiMode/googleSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "keyword": "best wireless earbuds 2026"
      }'
```

Success response (excerpt):

```json
{
  "msg": "ok",
  "sourceUrl": "https://www.google.com/search?num=10&udm=50&q=best+wireless+earbuds+2026",
  "errcode": 200,
  "code": "200",
  "stdout": "# Google AI Mode Overview - best wireless earbuds 2026\n\n## AI Overview Key Points\n- ...\n",
  "costTime": 10799,
  "costToken": 11200,
  "resultsNum": 1,
  "type": "stdoutWorkbenches",
  "taskId": "1779367311421-d728ce53704fc86e"
}
```

---
