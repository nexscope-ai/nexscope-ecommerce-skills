# Ruiguan Graphic Trademark Detection API Reference

## Request Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/trademarkGraphicDetection`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`; read api_key from `nexscope_AGENT_API_KEY` or `nexscopeAGENT_API_KEY`. If neither is configured, follow the authentication and credits guidance in SKILL.md.

## Request Parameters

POST Body (JSON):

| Parameter | Type | Required | Description |
|------|------|------|------|
| imageUrl | string | Yes | Product image URL or base64-encoded image data (maximum 1000 characters) |
| topNumber | integer | Yes | Maximum number of YOLO coordinates to return; default `5`, maximum `100`. The actual number returned may be lower than requested |
| productTitle | string | No | Product title for context-aware detection (maximum 1000 characters) |
| trademarkName | string | No | Possible graphic logo name to narrow the search (maximum 1000 characters) |
| regions | string | No | Country/region codes to check, separated by commas; defaults to all countries when omitted. Values: US (United States), WO (World Intellectual Property), ES (Spain), GB (United Kingdom), DE (Germany), IT (Italy), CA (Canada), MX (Mexico), EM (European Union), AU (Australia), FR (France), JP (Japan), TR (Turkey), BX (Bolivia), CN (China) |
| enableLocalizing | boolean | No | Whether to enable image cropping; default `false` |
| enableRadar | boolean | No | Whether to enable radar monitoring; default `true` |


## Response Structure

| Field | Type | Description |
|------|------|------|
| boundingBoxCount | integer | Number of detection results |
| radarResult | string | Radar detection result |
| total | integer | Number of records |
| data | array | List of detection results (see below) |
| detectId | string | Detection ID |
| columns | array | Rendering column definitions |
| costToken | integer | Tokens consumed |
| type | string | Rendering style |

### Fields of Each data Array Item

Each object in the `data` array contains the following fields:

| Field | Type | Description |
|------|------|------|
| image | string | Matched trademark image URL |
| boundingBox | string | YOLO coordinates (comma-separated) |
| subRadarResult | string | Sub-radar detection result |
| applicationNumber | string | Application number |
| niceClassName | string | Nice classification names (comma-separated) |
| applicantName | string | Rights holders (comma-separated) |
| tradeMarkStatus | string | Trademark status; enum values: `"DEL"`, `"ended"`, `"registered"`, `"act"`, `"pend"`, `"filed"`, `""` |
| niceClass | array | Nice classification details |
| similarity | number | Similarity (0 to 1; higher values mean greater similarity) |
| registrationNumber | string | Registration number |
| registrationOfficeCode | string | Trademark office |
| registrationDate | string | Registration date |
| bid | string | Logo identifier |
| trademarkName | string | Word mark name in the image |
| applicationDate | string | Application date |

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
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/ruiguan/trademarkGraphicDetection \
  -H "Authorization: $nexscopeAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageUrl": "https://example.com/product-image.jpg", "topNumber": 5, "productTitle": "Wireless Bluetooth headphones", "regions": "US,EM"}'
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
