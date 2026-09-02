## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# 谷歌专利检索 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: Bearer <api_key>`，api_key 优先从环境变量 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`NexScope-Skill/2.0`，超时 150s（与脚本一致），透传 `SESSION_ID` / `MODE_ID` / `APP_NAME`

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| q | string | 是 | - | Google Patents 搜索查询，支持官方高级查询语法（如 `owner:"Company"`、`inventor:"Name"`、日期算子）。最大 1000 字符 |
| num | integer | 否 | 10 | 每页结果数，范围 10–100 |
| page | integer | 否 | 1 | 页码，从 1 开始 |
| country | string | 否 | - | 国家代码，多个值用英文逗号分隔，例如 `US,CN,WO` |
| language | string | 否 | - | 语言，多个值用英文逗号分隔，使用 Google Patents 官方语言值 |
| before | string | 否 | - | 最大日期，格式 `priority|filing|publication:YYYYMMDD` |
| after | string | 否 | - | 最小日期，格式同 `before` |
| sort | string | 否 | - | 排序方式：`new`（最新）或 `old`（最早）；不传时按相关性排序 |
| type | string | 否 | - | 结果类型：`PATENT` 或 `DESIGN` |
| status | string | 否 | - | 专利状态：`GRANT` 或 `APPLICATION` |
| patents | boolean | 否 | true | 是否包含专利结果 |
| scholar | boolean | 否 | false | 是否包含 Google Scholar 结果 |
| litigation | string | 否 | - | 诉讼状态：`YES` 或 `NO` |
| inventor | string | 否 | - | 发明人，多个值用英文逗号分隔 |
| assignee | string | 否 | - | 受让人，多个值用英文逗号分隔 |
| clustered | boolean | 否 | - | 是否按分类聚合；上游当前仅支持 `true` |
| dups | string | 否 | - | 去重方式；不传时按专利族去重，`language` 表示按公开文本去重 |

> `q` 为检索的主要输入；缺失或为空时检索无有意义结果。

> **查询语法示例**：`wireless earbuds`（全文关键词）；`owner:"Apple"`（按受让人）；`inventor:"J Lee"`（按发明人）；`before:publication:20250101`（日期上界，也可作为 `before` 参数传入）。

## 响应结构

> 以下字段结构经真实调用核对（`{"q":"wireless earbuds","num":10}` → errcode 200, costToken 10000）。网关以 `errcode`/`errmsg`/`costToken` 包裹上游 Google Patents 结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 200 表示成功 |
| errmsg | string | `ok` 表示成功，否则为错误描述 |
| organicResults | array | 专利搜索结果列表 |
| searchParameters | object | 回显的查询参数（`q`/`engine`/`num`/`patents`/`page`/`scholar` 等） |
| searchInformation | object | 检索元信息，含 `total_results`（总命中数）、`total_pages`（总页数）、`page_number`（当前页） |
| searchMetadata | object | 检索处理元数据 |
| pagination | object | 分页信息（`next`、`current`） |
| serpapiPagination | object | 上游分页信息 |
| summary | object | 结果摘要（含 `cpc` 分类聚合等，仅分类聚合时部分返回） |
| costToken | integer | 消耗 token |
| message | string | 上游提示信息；成功但有特殊情况时可能出现（多数成功响应不含此字段） |

### 结果字段（`organicResults` 数组中的每个对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| publicationNumber | string | 公开号 |
| patentId | string | 专利 ID |
| title | string | 专利或学术结果标题 |
| snippet | string | 专利或学术结果摘要 |
| inventor | string | 发明人 |
| assignee | string | 受让人 |
| filingDate | string | 申请日期 |
| publicationDate | string | 公开或发布日期 |
| grantDate | string | 授权日期 |
| priorityDate | string | 优先权日期 |
| language | string | 专利语言 |
| cpc | string | 合作专利分类（仅分类聚合时返回） |
| cpcDescription | string | 合作专利分类说明 |
| countryStatus | object | 各国法律状态 |
| position | integer | 搜索结果位置 |
| rank | integer | 结果排名（聚合时可能与 position 不同） |
| patentLink | string | Google Patents 专利链接 |
| pdf | string | 专利 PDF 链接 |
| thumbnail | string | 专利缩略图 |
| figures | array | 专利图片列表，元素含 `thumbnail`、`full` |
| scholar | boolean | 是否为 Google Scholar 结果 |
| scholarId | string | Scholar 结果 ID |
| scholarLink | string | Google Scholar 结果链接 |
| author | string | Scholar 结果作者 |
| authorEtal | boolean | Scholar 结果是否含三位及以上作者 |
| publicationVenue | string | Scholar 结果发表场所 |
| urlHostname | string | Scholar 结果来源域名 |
| serpapiLink | string | 结果详情 API 链接 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errcode 字段区分（errcode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析 `organicResults`、`searchInformation` 等业务字段 |
| 400 | 参数错误 | 检查 `q` 是否提供、`num` 是否在 10–100 范围、日期格式是否正确 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理 |
| 501 | 无权限或套餐配额耗尽 | 当前 Key 未开通谷歌专利检索权限或配额已用尽。属权限/套餐问题（非单纯余额不足），充值无法解决，不要重试，提示用户开通/启用对应 API 套餐后重试 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{"errcode": 400, "errmsg": "参数错误"}

{"errcode": 401, "errmsg": "authorized error"}
```

## curl 示例

**基础检索：**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "num": 10}'
```

**按国家与状态筛选：**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "country": "US", "status": "GRANT"}'
```

**日期范围 + 最新排序：**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{"q": "wireless earbuds", "after": "publication:20240101", "sort": "new"}'
```

**分页查询：**

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/googlePatent/search \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
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
