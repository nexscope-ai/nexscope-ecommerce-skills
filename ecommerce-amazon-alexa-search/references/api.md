# Amazon Alexa Shopping Assistant API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/alexaSearch`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| prompts | string[] | Yes | Conversation prompt array, supports only **1 entry**. Each call accepts only 1 question. For follow-up questions, the agent must summarize key information from the previous response (recommended products, ASINs, key conclusions, etc.), concatenate it with the new question, and send it as a new `prompts[0]`. Each call is an independent new session and does not retain cross-call conversation history |
| format | string | No | Response format: `markdown` (default) returns a readable report; `json` returns a structured data array |
| url | string | No | Linked page URL, used to supplement the page context of Alexa's current response. Only pass this when the user provides a **specific page** (category page / search results page / product detail page, etc.); do **not** pass this parameter for the Amazon homepage (e.g. `https://www.amazon.com/`) |

## Response Structure

| Field | Type | Description |
|------|------|------|
| stdout | string | Markdown format Q&A report, containing each round's user question, Alexa answer, recommended products, and follow-up questions; only returned when `format=markdown` |
| data | array | Structured conversation result array; only returned when `format=json` |
| resultsNum | integer | Number of conversation rounds Alexa actually answered; 0 means no valid response was produced |
| code | string | Business status code, `"200"` on success (same as numeric `errcode`) |
| errcode | integer | Business status code (HTTP layer is generally 200; use this field to determine business success/failure) |
| msg / errmsg | string | Response message, `ok` on success |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Tokens consumed by this call; charged only if upstream succeeds |
| taskId | string | Task identifier returned by upstream |
| type | string | Render style: `stdoutWorkbenches` (markdown) or `json` |

### `data[*]` Structure (`format=json`)

| Field | Type | Description |
|------|------|------|
| prompt | string | Prompt sent to Alexa for this round |
| content | string | Text content of Alexa's response for this round |
| screenshot | string | Screenshot link for this round's conversation |
| followUpQuestions | string[] | List of follow-up questions recommended by Alexa |
| products | array | Recommended product group list, each group containing `title` and `items` |
| products[].title | string | Recommended group title |
| products[].items[].asin | string | Product ASIN |
| products[].items[].title | string | Product title |
| products[].items[].url | string | Product detail page URL |
| products[].items[].cover | string | Product cover image URL |
| products[].items[].price | string | Current price (with currency) |
| products[].items[].originalPrice | string | Original or strikethrough price |
| products[].items[].score | string | Rating |
| products[].items[].ratingsCount | string | Review count |
| products[].items[].describe | string | Product description |

## Error Codes

Under normal circumstances, the HTTP status code is 200. Business success or failure is determined by the `errcode` / `code` field in the response body (`200` indicates success; other values indicate business errors). When encountering unauthorized access, the HTTP status code is 401 and the corresponding `errcode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse `stdout` or `data` fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | Billing/insufficient credits | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business error | Refer to the `errmsg` / `msg` field for specific error details |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

**Markdown format (default):**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/alexaSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "prompts": ["best wireless earbuds for running"]
      }'
```

**JSON format:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/alexaSearch \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
        "prompts": ["best electric kettle on Amazon US"],
        "format": "json"
      }'
```

Success response (excerpt):

```json
{
  "msg": "ok",
  "errcode": 200,
  "code": "200",
  "stdout": "# Amazon Alexa Shopping Assistant\n\n## Question 1: best wireless earbuds for running\n\n### Alexa Answer\n- ...\n\n### Recommended Products\n- ...\n\n### Follow-up Questions\n- ...\n",
  "resultsNum": 1,
  "costTime": 12000,
  "costToken": 1500,
  "type": "stdoutWorkbenches",
  "taskId": "1779367311421-d728ce53704fc86e"
}
```

---
