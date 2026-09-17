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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |
| Insufficient credits or balance | HTTP 402: Follow the **## Resolving Authentication and Credit Issues** section in SKILL.md. |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/utilityPatentDetection \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"productTitle": "Portable USB-C 65W GaN Fast Charger", "productDescription": "A compact 65W GaN USB-C fast charger, equipped with foldable prongs, supporting PD3.0 and QC4.0 protocols, dual USB-C ports and one USB-A port, suitable for laptops, phones, and tablets.", "region": "US", "topNumber": 100}'
```

---
