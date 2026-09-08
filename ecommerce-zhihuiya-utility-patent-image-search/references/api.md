# Zhihuiya Patent Image Search API Reference

## Request Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentImageSearch`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; read api_key from `nexscope_AGENT_API_KEY` or `nexscopeAGENT_API_KEY`. If neither is configured, follow the authentication and credits guidance in SKILL.md.

## Request Parameters

POST Body (JSON):

### Required Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| url | string | Yes | Image URL (maximum 1000 characters) |
| patentType | string | Yes | Patent type: `D` (design patent) or `U` (utility model patent). Default: `D` |
| model | integer | Yes | Image search model. Design patents: `1` (smart association, recommended), `2` (search this image); utility model patents: `3` (match shape), `4` (match shape/pattern/color, recommended) |

### Optional Parameters

| Parameter | Type | Required | Description |
|------|------|------|------|
| country | string | No | Patent office (country/organization/region codes), separated by commas, e.g., `CN,US,JP`. Omit to search all patent offices |
| loc | string | No | LOC classification (Locarno classification numbers); combine multiple numbers with AND/OR/NOT |
| legalStatus | string | No | Patent legal status, comma-separated. Values: `1` (published), `2` (substantive examination), `3` (granted), `8` (avoidance of duplicate grants), `11` (withdrawn), `12` (withdrawn - unspecified type), `17` (withdrawn - deemed withdrawn), `18` (withdrawn - voluntarily withdrawn), `13` (rejected), `14` (fully revoked), `15` (term expired), `16` (annual fee unpaid), `21` (rights restored), `22` (rights terminated), `23` (partially invalidated), `24` (application terminated), `30` (abandoned), `19` (abandoned - deemed abandoned), `20` (abandoned - voluntarily abandoned), `25` (abandoned - unspecified type), `222` (PCT not entered a designated state - within the designation period), `223` (PCT entered a designated state - within the designation period), `224` (PCT entered a designated state - designation period expired), `225` (PCT not entered a designated state - designation period expired) |
| simpleLegalStatus | string | No | Simplified patent legal status, comma-separated. Values: `0` (invalid), `1` (valid), `2` (pending), `220` (PCT designation period expired), `221` (within the PCT designation period), `999` (unconfirmed) |
| assignees | string | No | Applicant (patent holder); maximum 1000 characters |
| applyStartTime | string | No | Patent application start date; format: `yyyyMMdd` |
| applyEndTime | string | No | Patent application end date; format: `yyyyMMdd` |
| publicStartTime | string | No | Patent publication start date; format: `yyyyMMdd` |
| publicEndTime | string | No | Patent publication end date; format: `yyyyMMdd` |
| limit | integer | No | Number of patents to return, 1-100. Default: `10` |
| offset | integer | No | Offset, 0-1000. Default: `0` |
| field | string | No | Result sort field: `SCORE` (relevance), `APD` (application date), `PBD` (publication date), or `ISD` (grant date). Default: `SCORE` |
| order | string | No | Applies when field is APD/PBD/ISD: `desc` (descending) or `asc` (ascending). Default: `desc` |
| lang | string | No | Preferred title language: `original` (original patent title), `cn` (Chinese translation), or `en` (English translation). Default: `original` |
| preFilter | integer | No | Whether to enable country/LOC pre-filtering: `1` (enabled), `0` (disabled). Default: `1` |
| stemming | integer | No | Whether to enable stemming: `1` (enabled), `0` (disabled). Default: `0` |
| mainField | string | No | Main patent fields, including title, abstract, claims, specification, publication number, application number, applicants, inventors, and IPC/UPC/LOC classification numbers (maximum 1000 characters) |
| includeMachineTranslation | boolean | No | Include machine-translated data in the search |
| scoreExpansion | boolean | No | Score expansion |
| isHttps | integer | No | Image URL protocol: `1` (return https), `0` (return http). Default: `0` |
| returnImgId | boolean | No | Whether to return img_id. Default: `false` |

**Note**:
- `model` must match `patentType`: models 1-2 are for design patents (`D`); models 3-4 are for utility model patents (`U`)

## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Number of records returned in this request |
| allRecordsCount | integer | Total matching records in the database |
| data | array | List of matching patent records |
| columns | array | Rendering column definitions |
| type | string | Rendering style |
| costToken | integer | Tokens consumed |

### Patent Record Fields (Each Record in `data`)

| Field | Type | Description |
|------|------|------|
| patentId | string | Similar patent ID |
| patentPn | string | Similar patent number |
| apno | string | Application number |
| title | string | Patent title |
| inventor | string | Inventor |
| originalAssignee | string | Original applicant |
| currentAssignee | string | Current applicant |
| authority | string | Patent office (country code) |
| url | string | URL of the similar patent drawing |
| score | number | Similarity score (higher scores mean greater similarity; applies only when field is `SCORE`) |
| loc | array | LOC classification (Locarno classification numbers) |
| locMatch | integer | Whether a high-weight LOC matches: `1` (match), `0` (no match). Applies only when model=1 and field=SCORE |
| apdt | integer | Application date (timestamp) |
| pbdt | integer | Publication date (timestamp) |
| imgId | string | Patent drawing img_id (returned only when `returnImgId` is true) |

## curl Examples

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/zhihuiya/patentImageSearch \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/product-image.jpg",
    "patentType": "D",
    "model": 1,
    "country": "CN,US",
    "limit": 20,
    "lang": "cn"
  }'
```

### Response Example

```json
{
  "total": 20,
  "allRecordsCount": 1523,
  "data": [
    {
      "patentId": "abcdef123456",
      "patentPn": "CN305123456S",
      "apno": "CN202130123456.7",
      "title": "台灯",
      "inventor": "张三",
      "originalAssignee": "示例公司",
      "currentAssignee": "示例公司",
      "authority": "CN",
      "url": "http://images.zhihuiya.com/patent/12345.jpg",
      "score": 0.95,
      "loc": ["26-05"],
      "locMatch": 1,
      "apdt": 1640995200000,
      "pbdt": 1656633600000
    }
  ],
  "columns": [],
  "type": "patent_image",
  "costToken": 100
}
```

## Error Codes

Normally, the API returns HTTP 200, and the errorCode field in the response body indicates business success or failure (errorCode = 200 means success; other values indicate business errors). For unauthorized requests, the HTTP status is 401 and the corresponding errorCode is also 401.

| errcode | Meaning | Recommended Action |
|---------|------|----------|
| 200 | Success | Parse the business fields normally |
| 401 | Authentication failed | HTTP 401 or authorized error: follow the authentication and credits guidance in SKILL.md. |
| 402 | - | HTTP 402: follow the authentication and credits guidance in SKILL.md. |
| Other non-200 values | Business error | See `errmsg` for the specific cause of the error |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
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
