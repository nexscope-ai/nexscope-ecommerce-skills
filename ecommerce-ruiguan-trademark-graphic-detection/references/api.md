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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Authentication failed | HTTP 401 or authorized error: follow the authentication and credits guidance in SKILL.md. |
| Insufficient credits or balance | HTTP 402: follow the authentication and credits guidance in SKILL.md. |

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
