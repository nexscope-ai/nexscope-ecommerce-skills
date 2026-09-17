# Zhihuiya Bibliography API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/bibliography`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | No* | Patent ID (at least one of patentId and patentNumber must be provided; if both are present, patentId takes priority). Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60,000 characters |
| patentNumber | string | No* | Publication/grant number (at least one of patentId and patentNumber must be provided; if both are present, patentId takes priority). Only a single value is supported; multiple values separated by commas are not allowed. Max length: 60,000 characters |

> \* At least one of `patentId` and `patentNumber` must be provided.

> **Single patent limit**: This API consumes significant credits. To query multiple patents, you must obtain explicit user consent and make separate requests. Only 1 patent per request.

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
| total | integer | Number of records |
| data | array | Bibliography data list (see data fields below) |
| columns | array | Columns for rendering |
| type | string | Render style |
| costToken | integer | Tokens consumed |

### Data fields (each object in the `data` array)

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| pn | string | Publication/grant number |
| inventionTitle | array | Patent title language and name |
| abstracts | array | Patent abstract |
| patentType | string | Patent type. APPLICATION: invention application, PATENT: granted invention, UTILITY: utility model, DESIGN: design |
| applicants | array | Original applicants |
| assignees | array | Current applicants (patentees) |
| inventors | array | Inventors |
| agents | array | Patent applicants |
| agency | array | Application agency |
| examiners | array | Examiner information |
| priorityClaims | array | Priority claims |
| applicationReference | object | Application filing reference data |
| publicationReference | object | Publication reference data |
| datesOfPublicAvailability | object | Public availability dates |
| classificationIpcr | object | IPC classification |
| classificationCpc | object | CPC classification |
| classificationUpc | object | US patent classification |
| classificationLoc | array | LOC classification |
| classificationFi | array | FI classification |
| classificationFterm | array | F-term classification |
| classificationGbc | object | GBC classification |
| referenceCitedPatents | array | Cited patent documents |
| referenceCitedOthers | array | Cited non-patent literature |
| relatedDocuments | array | Divisional/continuation application information |
| pctOrRegionalFilingData | object | PCT or regional phase filing data |
| pctOrRegionalPublishingData | object | PCT or regional phase publication data |
| exdt | integer | Zhihuiya estimated patent expiration date |

## Error Codes

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |

## curl Example

**Query by publication/grant number (single patent):**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/bibliography \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US10123456B2"}'
```

**Query by patent ID:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/bibliography \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentId": "some-patent-id-here"}'
```

---
