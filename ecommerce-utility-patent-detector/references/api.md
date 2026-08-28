# Ruiguan Utility Patent Detection API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/utilityPatentDetection`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credit Issues** section in SKILL.md)

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| productTitle | string | Yes | Product title, max 1000 characters |
| productDescription | string | Yes | Product description, max 1000 characters |
| region | string | Yes | Country/region code(s) where the product is intended for sale, multiple separated by commas. Currently supports US. Default `US` |
| topNumber | integer | Yes | Number of results to recall, range: 10--200, default `100` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Record count |
| detectId | string | Detection ID |
| costToken | integer | Token cost |
| type | string | Render style |
| columns | array | Render column definitions |
| data | array | Patent list (see below) |

### Patent Object Fields

| Field | Type | Description |
|------|------|------|
| globalUtilityId | string | Patent ID |
| title | string | Utility patent title |
| titleCn | string | Utility patent title (Chinese) |
| similarity | number | Similarity between the product and this patent (0--1) |
| patentValidity | string | Patent validity: `Active` or `Invalid` |
| applicationNumber | string | Application number |
| applicationDate | string | Application date (yyyy-MM-dd) |
| publicationNumber | string | Publication number |
| publicationDate | string | Publication date (yyyy-MM-dd) |
| estimatedDueDate | string | Estimated expiration date (yyyy-MM-dd) |
| region | string | Receiving office |
| patentAbstract | string | Abstract |
| patentAbstractCn | string | Abstract (Chinese) |
| claims | string | Claims |
| claimsCn | string | Claims (Chinese) |
| specification | string | Specification |
| specificationCn | string | Specification (Chinese) |
| inventors | array | Inventors and countries concatenated, array format |
| inventorAddresses | array | Inventor addresses, array format |
| applicants | array | Applicants and countries concatenated, array format |
| applicantAddresses | array | Rights holder addresses, array format |
| priorityNumber | array | Priority numbers, array format |
| relatedPublicationDate | array | First publication dates (yyyy-MM-dd), array format |
| patentImageUrl | string | Patent cover image |
| images | array | Patent drawings |
| classNumList | array | Classification number path list, format: classNum1 > classNum2 > classNum3 |
| cpcKindRaw | array | CPC classification (raw JSONArray) |
| troCase | boolean | Whether there is a TRO enforcement history |
| troHolder | boolean | Whether it is a patent of a TRO rights holder |

## Error Codes

Under normal circumstances, the HTTP status code of the API is always 200. Business success or failure is distinguished by the `errorCode` field in the response body (`errorCode = 200` indicates success, other values indicate business errors). In cases such as unauthorized access, the HTTP status code is 401, and the corresponding `errorCode` is also 401.

| errcode | Meaning | Action |
|---------|---------|--------|
| 200 | Success | Parse business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| 402 | Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/utilityPatentDetection \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"productTitle": "Portable USB-C 65W GaN Fast Charger", "productDescription": "A compact 65W GaN USB-C fast charger, equipped with foldable prongs, supporting PD3.0 and QC4.0 protocols, dual USB-C ports and one USB-A port, suitable for laptops, phones, and tablets.", "region": "US", "topNumber": 100}'
```

---
