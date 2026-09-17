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

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response Structure

| Field | Type | Description |
|------|------|------|
| stdout | string | AI overview content in Markdown format; outputs key points and reference source links for each question's AI overview in order |
| sourceUrl | string | Target URL that was crawled, the final Google search page URL |
| resultsNum | integer | Number of AI overview blocks; >0 indicates the page rendered an AI Overview, 0 indicates the keyword did not trigger an AI Overview |
| code | string | Provider business value retained inside `data`; not the outer platform status |
| msg | string | Response message, `ok` on success |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Token consumption for this call; billed only when upstream returns success |
| taskId | string | Upstream capture task identifier for this request |
| type | string | Render style, fixed `stdoutWorkbenches`, used with the `stdout` field for Markdown rendering |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Billing/insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |

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
