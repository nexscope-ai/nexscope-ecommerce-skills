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

## Nexscope response envelope

These research endpoints return a platform object with numeric `code`, nullable `msg`, and business `data`. Only outer `code: 0` means success; `200`, string codes, missing codes, and HTTP 200 alone do not. A nonzero code is a platform error: show `msg` and do not interpret the payload as a successful result.

`msg` preserves the upstream message when available; Chinese messages are translated to English by Nexscope. A successful response without a message has `msg: null`. Do not infer success or retry behavior from the message text. Root provider `errcode`, `errmsg`, and `errorCode` are removed from the business payload; nested business `code` and `status` retain their own meanings.

Package scripts unwrap this platform object for their business output and retain its `code`, `msg`, and timing metadata under `_nexscope`; for those outputs, inspect `_nexscope.code` / `_nexscope.msg`. Business `code` or `error` fields are not platform success markers.

Business field tables and abbreviated business examples below describe `data`, unless explicitly labeled as a complete platform response. For example, a business `products` field is at HTTP `data.products`, and a business `data` array is at HTTP `data.data`. The research endpoints already had this outer envelope; no additional wrapper is added.

```json
{"code":0,"msg":null,"data":{}}
```

Metadata includes string `ts` (epoch milliseconds), string `cost` (elapsed milliseconds, not credits), `time`, and nullable `traceId`. Handle network/HTTP failures before the platform code; gateway failures may not be platform JSON. Keep the existing billing-header guidance separate from elapsed time.

## Response structure

> The fields below describe the Google Patents business payload inside platform `data`; billing metadata is separate from platform status.

| Field | Type | Description |
|------|------|------|
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

HTTP 200 does not prove business success. Read only the numeric outer platform `code`: `0` succeeds and any other value fails. Show outer `msg`; never test removed provider codes or nested business `code` as the platform status. Authentication, permissions, balance, and validation failures may be platform errors even with HTTP 200; also handle non-2xx HTTP and non-JSON responses.

### Recovery guidance

| Condition | Action |
|---|---|
| Invalid parameters | Check that `q` is provided, `num` is within 10–100, and date formats are correct |
| Authentication failed | HTTP 401 or authorized error: follow **## Resolve authentication and credit issues** in SKILL.md |
| Insufficient credits | HTTP 402: follow **## Resolve authentication and credit issues** in SKILL.md |
| Permission unavailable or plan quota exhausted | The current key does not have Google Patent Search access or has exhausted its quota. This is a permission/plan issue, not simply insufficient balance; adding credits will not resolve it. Do not retry; ask the user to activate/enable the corresponding API plan before retrying |

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
