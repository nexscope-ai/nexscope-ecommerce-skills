## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart 产品分析 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
- **超时**：120s
- **透传 Header**：`SESSION_ID`、`MODE_ID`、`APP_NAME`
- **市场**：Walmart 美国站；后端固定使用 Sorftime `domain=21`

请求体为扁平 JSON。一次只选择一个大小写严格匹配的 `operation`；不得批量或自动串行调用。上游普通 JSON 与 Base64/GZip 响应的识别、校验和解码均由服务端完成。

## 操作与请求参数

| operation | 用途 | 必填参数 | 可选参数 | 默认 | Sorftime Request |
|---|---|---|---|---|---:|
| `searchByName` | 按自然语言名称搜索相关商品 | `name` | `pageIndex` | 第 1 页 | 2 |
| `detail` | 商品详情 | `productId` | 无 | - | 1 |
| `trend` | 商品趋势 | `productId` | 无 | - | 2 |
| `salesVolume` | 按日/变体销量 | `productId` | `queryDate`, `queryEndDate`, `pageIndex` | 近 30 天；第 1 页 | 1 |

操作与对象字段：

| 参数 | 类型 | 规则 |
|---|---|---|
| `operation` | string | 必填；仅 `searchByName`、`detail`、`trend`、`salesVolume` |
| `name` | string | `searchByName` 必填；非空自然语言商品名称 |
| `productId` | string | `detail`、`trend`、`salesVolume` 必填；非空 Walmart ProductId |

分页与销量字段：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `queryDate` | string | 否 | 开始日期，`yyyy-MM-dd` |
| `queryEndDate` | string | 否 | 截止日期，`yyyy-MM-dd`；仅给开始日期时默认当前日 |
| `pageIndex` | integer | 否 | `searchByName`、`salesVolume` 从 1 开始，默认 1；每页最多 100 条 |

`searchByName` 对应上游 `ProductSearchFromName`，使用自然语言名称返回相关商品。`salesVolume` 两日期均省略时默认最近 30 天。可查询的最早日期以 Sorftime 当前数据覆盖为准；开始日期不得晚于截止日期。

## 请求示例

```json
{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}
```

```json
{"operation":"detail","productId":"5169493923"}
```

```json
{"operation":"trend","productId":"5169493923"}
```

```json
{"operation":"salesVolume","productId":"5169493923","queryDate":"2026-07-01","queryEndDate":"2026-07-31","pageIndex":1}
```

## 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息 |
| `data` | object | 固定响应容器；`data.value` 保留各 operation 的 Sorftime 原始对象、数组、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName`、`detail`、`trend` 或 `salesVolume` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer | 业务体兼容字段；NexScope 独立计费必须读取响应头 `X-Cost-Token` |
| `sourceType` | string | `sorftime` |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`costToken=0`，不按文档消耗补全。

| operation | `data.value` 语义 |
|---|---|
| `searchByName` | Sorftime ProductSummeryObject 相关商品结果；每页最多 100 条 |
| `detail` | Sorftime ProductSummeryObject |
| `trend` | Sorftime ProductTrendObject |
| `salesVolume` | 行数组；每行形如 `[date, sales, type]`，`type=2` 表示昨日销量 |

网关保留上游字段；具体对象字段和趋势单位以实际响应为准，不补造缺失值。

## 错误码

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 200 | 成功 | 按 operation 解析 `data.value` |
| 400 / 4000 | 缺少必填参数；框架校验 `operation` 时返回 400，operation 条件字段由业务校验返回 4000 | 补充 `operation`、`searchByName` 的 `name` 或其他操作的 `productId` |
| 4001 | 参数格式错误 | 检查 operation 大小写、日期和 pageIndex |
| 401 | 认证失败 | 按 SKILL.md 的认证引导处理 |
| 402 | 积分不足 | 按 SKILL.md 的积分引导处理 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动改变日期或操作重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"detail","productId":"5169493923"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"wireless earbuds","pageIndex":1}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/productAnalysis" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"salesVolume","productId":"5169493923","pageIndex":1}'
```

## Feedback API

工具反馈使用独立端点 `POST https://skill-api.nexscope.com/api/v1/public/feedback`，`Content-Type: application/json`。

```json
{"skillName":"nexscope-sorftime-walmart-product-analysis","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。
