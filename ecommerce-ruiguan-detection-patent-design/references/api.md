# Ruiguan Design Patent Detection API Reference

## Request Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/detectionPatentDesign`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; read api_key from `nexscope_AGENT_API_KEY` or `nexscopeAGENT_API_KEY`. If neither is configured, follow the authentication and credits guidance in SKILL.md.

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| imageUrl | string | Yes | - | Product image file URL for comparison with the patent database (maximum 1000 characters) |
| queryMode | string | Yes | hybrid | Search mode: `physical` (physical image search), `line` (line drawing search), or `hybrid` (combined search). Maximum 1000 characters |
| topNumber | integer | Yes | 100 | Number of patents to retrieve (maximum 100) |
| regions | string | No | US | Country/region codes where the product is sold, separated by commas (e.g., `US,EU,CN`). Supported: US, EU, CN, JP, KR, DE, GB, FR, IT, AU, CA, BR, MX, IN, TH, SE, CH, IE, IL, DK, NZ, AT, BX, FI, WO. Maximum 1000 characters |
| productTitle | string | No | - | Product title providing additional search context (maximum 1000 characters) |
| productDescription | string | No | - | Product description providing additional search context (maximum 1000 characters) |
| patentStatus | string | No | 1 | Patent validity filter: `1` (valid patents), `0` (expired or invalid patents), or `1,0` (all). Maximum 1000 characters |
| enableRadar | boolean | No | true | Whether to enable radar analysis (AI infringement assessment) |
| topLoc | string | No | - | First-level LOC scope to search (e.g., `06,07`). Format: `^(0[1-9]\|1[0-9]\|2[0-9]\|3[0-2]\|ALL)(,(0[1-9]\|1[0-9]\|2[0-9]\|3[0-2]\|ALL))*$`. If omitted, use the results of the model LOC prediction service |
| sourceLanguage | string | No | - | Source language code for translation into English (e.g., `zh-CN`). Leave empty for English text. Maximum 1000 characters |


## Response Structure

| Field | Type | Description |
|------|------|------|
| total | integer | Total number of patent records returned |
| data | array | List of patents (see patent objects below) |
| columns | array | Rendering column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

### Patent Objects (Each Element of the `data` Array)

| Field | Type | Description |
|------|------|------|
| applicationNumber | string | Patent application number |
| publicationNumber | string | Patent publication number |
| patentProd | string | Patent title (English) |
| patentProdCn | string | Patent title (Chinese) |
| similarity | string | Similarity between the patent and product image (0-1) |
| patentImageUrl | string | URL of the patent drawing most similar to the product image |
| images | array | List of patent images |
| abstracts | string | Patent abstract |
| specification | string | Patent specification |
| inventors | array | List of inventors |
| applicants | array | List of applicants |
| applicantAddresses | array | Applicant addresses |
| troCase | boolean | Whether there is a history of TRO enforcement |
| troHolder | boolean | Whether the patent belongs to a TRO rights holder |
| radarResult | object | AI radar analysis result |
| radarResult.same | boolean | Whether infringement is suspected |
| radarResult.exp | string | Expected description (explanation of the radar assessment) |
| patentLoc | string | Patent LOC classifications (comma-separated) |
| locOneInfo | string | First-level LOC details |
| locTwoInfo | string | Second-level LOC details |
| patentValidity | string | Patent validity |
| applicationDate | string | Patent application date |
| publicationDate | string | Patent publication date |
| grantDate | string | Patent grant date |
| estimatedDueDate | string | Estimated expiration date |
| registrationOfficeCode | string | Patent registration office |
| patentFamily | array | List of patent family members |
| globalPatentId | string | Global patent ID |
| globalImageId | string | Patent image ID |
| isSketchText | string | Whether the image is a line drawing |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/detectionPatentDesign \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://example.com/product.jpg",
    "queryMode": "hybrid",
    "topNumber": 50,
    "regions": "US",
    "enableRadar": true
  }'
```

## Multi-region Search Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/detectionPatentDesign \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "imageUrl": "https://example.com/product.jpg",
    "queryMode": "physical",
    "topNumber": 100,
    "regions": "US,EU,CN",
    "productTitle": "Portable wireless charging stand",
    "productDescription": "A foldable wireless charging stand for smartphones",
    "patentStatus": "1",
    "enableRadar": true
  }'
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
