## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart 关键词研究 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
- **超时**：120s
- **透传 Header**：`SESSION_ID`、`MODE_ID`、`APP_NAME`
- **市场**：Walmart 美国站；后端固定使用 Sorftime `domain=21`

请求体使用扁平 lowerCamel JSON，一次只选择一个大小写严格匹配的 `operation`。`marketQuery` 的 `pattern` 是唯一业务嵌套对象；不要外套 `params`，也不要自动串行多个 operation。上游普通 JSON 与 Base64/GZip 响应的识别、校验和解码均由服务端完成。

## 操作矩阵

| operation | 用途 | 必填参数 | 可选参数 | 默认 | Sorftime Request |
|---|---|---|---|---|---:|
| `marketQuery` | 筛选当前热词 | 无 | `pattern`, `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `searchByName` | 商品/类目名称反查热词 | `name` | `pageIndex` | 第 1 页 | 1 |
| `searchProducts` | 热词搜索结果商品 | `keyword` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `detail` | 关键词详情 | `keyword` | 无 | - | 1 |
| `productKeywords` | 商品关联关键词 | `productId` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 1 |
| `relatedKeywords` | 关联词拓展 | `keyword` | `pageIndex`, `pageSize` | 第 1 页、20 条 | 5 |
| `favoriteList` | 查询收藏词或目录 | `command` | `pageIndex` | 第 1 页 | 1 |

## 参数规则

### marketQuery

`pattern` 可含：`keyword`（非空字符串）、`rankCondition` 和 `searchVolumeCondition`。两个条件字段均为 1 或 2 个非负整数；下界不得大于上界。单元素 `[10000]` 表示大于 10000；双元素 `[0,10000]` 按官方语义表示小于 10000。`pageSize` 范围 20–200。

### 查询类操作

- `searchByName.name` 是商品或类目名称；`pageIndex` 从 1 开始，每页最多返回 200 条。
- `searchProducts` 仅支持当前热词，返回最近 15 天搜索结果出现的商品；`pageSize` 20–200。
- `detail.keyword` 为一个非空关键词。
- `productKeywords` 返回最近 30 天商品曾出现在搜索结果前三页的关键词；`productId` 为字符串，`pageSize` 20–200。
- `relatedKeywords` 使用一个种子关键词；`pageSize` 20–200。

### Public favorite lookup

- `favoriteList`: `command` 仅允许 `all`、`dict`、`dict=<目录>`；对外参数统一为 `pageIndex`，后端映射成上游 `Page`；每页最多 100 条。
- `favoriteAdd` and `favoriteChange` are intentionally excluded from this public read-only migration.
- API 词库与 Sorftime 专业版收藏夹彼此独立，收藏数据不互通。

## 请求示例

```json
{"operation":"marketQuery","pattern":{"keyword":"wireless","searchVolumeCondition":[10000]},"pageIndex":1,"pageSize":20}
```

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

```json
{"operation":"favoriteList","command":"dict","pageIndex":1}
```

写操作格式示例（不得在未获授权时执行）：

```json
The client rejects `favoriteAdd` and `favoriteChange` before any HTTP request.
```

## 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

所有 operation 的业务成功体使用相同结构：`data`、`operation`、`requestConsumed`、`costTime`、`costToken`、`sourceType`。`operation` 回显本次实际执行的操作；`data` 是固定对象容器，`data.value` 可为对象、数组、数字、字符串或 `null`，按 Sorftime 上游原样保留；`requestConsumed` 为本次上游消耗，上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时不补全消耗，保持 `requestConsumed=0`、`costToken=0`；`sourceType` 为 `sorftime`。

| operation | `data.value` 语义 |
|---|---|
| `marketQuery` | 关键词摘要数据 |
| `searchByName` | 与商品或类目名称相关的热词 |
| `searchProducts` | ProductSummeryObject 商品摘要；最近 15 天窗口 |
| `detail` | KeywordSummeryObject |
| `productKeywords` | ProductKeywordItemObject；最近 30 天窗口 |
| `relatedKeywords` | KeywordSummeryObject 扩展词 |
| `favoriteList` | 字符串数组，内容由 `command` 决定 |

具体业务对象字段以实际 Sorftime 响应为准。

## 错误码

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 200 | 成功 | 按 operation 解析 `data.value`；写操作再检查其中的结果码 |
| 400 / 4000 | 缺少必填参数；框架校验全局必填字段时返回 400，业务条件必填校验返回 4000 | 补充 operation 的条件必填字段 |
| 4001 | 参数格式错误 | 检查 operation 大小写、分页、条件数组和 command |
| 401 | 认证失败 | 按 SKILL.md 的认证引导处理 |
| 402 | 积分不足 | 按 SKILL.md 的积分引导处理 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换词、翻页或切换 operation |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketQuery","pattern":{"keyword":"wireless"},"pageIndex":1,"pageSize":20}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/keywordResearch" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"favoriteList","command":"dict","pageIndex":1}'
```

## Feedback API

工具反馈使用独立端点 `POST https://skill-api.nexscope.com/api/v1/public/feedback`，`Content-Type: application/json`。

```json
{"skillName":"nexscope-sorftime-walmart-keyword-research","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。
