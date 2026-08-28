# Zhihuiya Simple Bibliography API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/simpleBibliography`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| patentId | string | Conditionally required | Patent IDs, up to 100 comma-separated values. At least one input field is required; `patentId` takes priority when both are present. |
| patentNumber | string | Conditionally required | Publication/grant numbers, up to 100 comma-separated values. At least one input field is required. |

> **Batch limit**: Up to 100 comma-separated patents are accepted. Confirm the intended batch because the endpoint consumes significant credits.

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records |
| allRecordsCount | integer | Total number of records |
| data | array | Bibliography list (see data field descriptions below) |
| columns | array | Column definitions for rendering |
| type | string | Render style |
| costToken | integer | Tokens consumed |

### Data fields (each element in the `data` array)

| Field | Type | Description |
|------|------|------|
| patentId | string | Patent ID |
| title | string | Patent title |
| abstractContent | string | Patent abstract |
| publicationNumber | string | Publication number |
| pn | string | Publication/grant number |
| country | string | Country code |
| publicationCountry | string | Publication country |
| publicationDate | string | Publication date |
| publicationKind | string | Publication kind code |
| patentType | string | Patent type (invention, utility model, design, etc.) |
| kind | string | Patent kind code |
| applicationNo | string | Application number |
| applicationDate | string | Application date |
| applicants | array | List of applicants |
| inventors | array | List of inventors |
| assignees | array | List of patent assignees |
| assigneeAddresses | array | List of assignee addresses |
| ipcMain | string | IPC main classification |
| ipcFurther | array | IPC secondary classification list |
| cpcMain | string | CPC main classification |
| cpcFurther | array | CPC secondary classification list |
| loc | array | LOC classification list |
| gbc | array | GBC classification list |
| priorityClaims | array | Priority claim list |
| pctApplicationNo | string | PCT application number |
| pctFilingDate | string | PCT filing date |
| pctEntryDate | string | PCT entry date |
| citedPatents | array | Cited patent list |
| citedNonPatents | array | Cited non-patent literature list |

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

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/simpleBibliography \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"patentNumber": "US11234567B2"}'
```

---
