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

Under normal circumstances, the HTTP status code is 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success; other values indicate business errors). When unauthorized, the HTTP status code is 401, and the corresponding errorCode is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| 402 | - | HTTP 402: follow the **## Resolving Authentication and Credits Issues** section in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `errmsg` field for the specific error reason |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

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
