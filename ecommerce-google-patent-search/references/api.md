## Nexscope billing

The migrated Skill does not inherit the source platform's point value. This operation consumes Nexscope credits. Preserve X-Cost-Token and X-Cost-Credit from the HTTP response headers as server-reported billing metadata, and preserve X-Kong-Trace-Id for diagnostics.

# Nexscope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a Nexscope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Google Patent Search API Reference

## Request conventions

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search`
- **Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: Bearer <api_key>`, Read api_key from the `NEXSCOPE_API_KEY` environment variable, falling back to `NEXSCOPE_API_KEY` (if unset, follow **## Resolve authentication and credit issues** in SKILL.md)
- **User-Agent**: `Nexscope-Skill/2.0`, timeout 150s (consistent with the script); forward `SESSION_ID` / `MODE_ID` / `APP_NAME`

## Request parameters

POST body (JSON):

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| q | string | Yes | - | Google Patents search query; supports official advanced syntax such as `owner:"Company"`, `inventor:"Name"`, and date operators. Maximum 1000 characters |
| num | integer | No | 10 | Results per page, range 10–100 |
| page | integer | No | 1 | Page number, starting at 1 |
| country | string | No | - | Country codes, separated by ASCII commas for multiple values, such as `US,CN,WO` |
| language | string | No | - | Languages, separated by ASCII commas for multiple values; use official Google Patents language values |
| before | string | No | - | Maximum date, format `priority|filing|publication:YYYYMMDD` |
| after | string | No | - | Minimum date, same format as `before` |
| sort | string | No | - | Sort order: `new` (newest) or `old` (oldest); relevance order when omitted |
| type | string | No | - | Result type: `PATENT` or `DESIGN` |
| status | string | No | - | Patent status: `GRANT` or `APPLICATION` |
| patents | boolean | No | true | Whether to include patent results |
| scholar | boolean | No | false | Whether to include Google Scholar results |
| litigation | string | No | - | Litigation status: `YES` or `NO` |
| inventor | string | No | - | Inventors, separated by ASCII commas for multiple values |
| assignee | string | No | - | Assignees, separated by ASCII commas for multiple values |
| clustered | boolean | No | - | Whether to aggregate by classification; upstream currently supports only `true` |
| dups | string | No | - | Deduplication mode; defaults to patent-family deduplication when omitted; `language` deduplicates by publication text |

> `q` is the primary search input; a missing or empty value produces no meaningful search results.

> **Query syntax examples**: `wireless earbuds` (full-text keywords); `owner:"Apple"` (by assignee); `inventor:"J Lee"` (by inventor); `before:publication:20250101` (upper date bound, also accepted through the `before` parameter).

## Response structure

> The field structure below was verified with a real call (`{"q":"wireless earbuds","num":10}` → errcode 200, costToken 10000). The gateway wraps upstream Google Patents results with `errcode`/`errmsg`/`costToken`.

| Field | Type | Description |
|------|------|------|
| errcode | integer | 200 indicates success |
| errmsg | string | `ok` indicates success; otherwise an error description |
| organicResults | array | Patent search result list |
| searchParameters | object | Echoed query parameters (`q`/`engine`/`num`/`patents`/`page`/`scholar`, etc.) |
| searchInformation | object | Search information, including `total_results` (total matches), `total_pages` (total pages), and `page_number` (current page) |
| searchMetadata | object | Search processing metadata |
| pagination | object | Pagination information (`next`, `current`) |
| serpapiPagination | object | Upstream pagination information |
| summary | object | Result summary, including `cpc` classification aggregations and related data; some fields are returned only when aggregating by classification |
| costToken | integer | Tokens consumed |
| message | string | Upstream notice; may appear on successful responses with special circumstances (absent from most successful responses) |

### Result fields (each object in the `organicResults` array)

| Field | Type | Description |
|------|------|------|
| publicationNumber | string | Publication number |
| patentId | string | Patent ID |
| title | string | Patent or scholarly result title |
| snippet | string | Patent or scholarly result summary |
| inventor | string | Inventor |
| assignee | string | Assignee |
| filingDate | string | Filing date |
| publicationDate | string | Publication or release date |
| grantDate | string | Grant date |
| priorityDate | string | Priority date |
| language | string | Patent language |
| cpc | string | Cooperative Patent Classification (returned only when aggregating by classification) |
| cpcDescription | string | Cooperative Patent Classification description |
| countryStatus | object | Legal status by country |
| position | integer | Search result position |
| rank | integer | Result rank (may differ from position when aggregating) |
| patentLink | string | Google Patents patent link |
| pdf | string | Patent PDF link |
| thumbnail | string | Patent thumbnail |
| figures | array | Patent image list; each item contains `thumbnail` and `full` |
| scholar | boolean | Whether this is a Google Scholar result |
| scholarId | string | Scholar result ID |
| scholarLink | string | Google Scholar result link |
| author | string | Scholar result author |
| authorEtal | boolean | Whether the Scholar result has three or more authors |
| publicationVenue | string | Scholar result publication venue |
| urlHostname | string | Scholar result source domain |
| serpapiLink | string | Result details API link |

## Error codes

Normally, the API returns HTTP 200 and indicates business success or failure through the errcode field in the response body (errcode = 200 means success; other values indicate business errors). For unauthorized requests and similar cases, both the HTTP status and errcode are 401.

| errcode | Meaning | Recommended action |
|---------|------|----------|
| 200 | Success | Parse business fields such as `organicResults` and `searchInformation` normally |
| 400 | Invalid parameters | Check that `q` is provided, `num` is within 10–100, and date formats are correct |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolve authentication and credit issues** in SKILL.md |
| 402 | Insufficient credits | HTTP 402: follow **## Resolve authentication and credit issues** in SKILL.md |
| 501 | Permission unavailable or plan quota exhausted | The current key does not have Google Patent Search access or has exhausted its quota. This is a permission/plan issue, not simply insufficient balance; adding credits will not resolve it. Do not retry; ask the user to activate/enable the corresponding API plan before retrying |
| Other non-200 values | Business error | See `errmsg` for the specific cause |

Error response examples:

```json
{"errcode": 400, "errmsg": "参数错误"}

{"errcode": 401, "errmsg": "authorized error"}
```

## curl examples

**Basic search:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "num": 10}'
```

**Filter by country and status:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "country": "US", "status": "GRANT"}'
```

**Date range + newest first:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "after": "publication:20240101", "sort": "new"}'
```

**Paginated search:**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Nexscope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "page": 2, "num": 20}'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-google-patent-search",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`nexscope-google-patent-search`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
