## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Walmart 类目市场 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
- **超时**：120s
- **透传 Header**：`SESSION_ID`、`MODE_ID`、`APP_NAME`
- **市场**：Walmart 美国站；后端固定使用 Sorftime `domain=21`

请求体为扁平 JSON。一次请求只允许一个大小写严格匹配的 `operation`，不得批量或自动串行执行多个操作。上游普通 JSON 与 Base64/GZip 响应的识别、校验和解码均由服务端完成。

## 操作与请求参数

| operation | 用途 | 其他参数 | 必填规则 | Sorftime Request |
|---|---|---|---|---:|
| `tree` | 完整类目树 | 无 | 只需 `operation` | 5 |
| `searchByName` | 按自然语言类目名称搜索相关类目 | `name`: string | `name` 必填且非空 | 1 |
| `marketReport` | 类目市场报告与 Best Seller Top 80 | `nodePath`: string | `nodePath` 必填 | 5 |

`name` 是自然语言类目名称，例如 `patio furniture`。该操作对应 Sorftime `CategorySearchFromName`，最多返回 3 个相关类目；匹配结果不代表精确分类。

`nodePath` 是由数字类目 ID 组成、以下划线分隔的完整路径，例如 `4044_623679_1032619_5842891_9823303`。应从类目树获得，不要凭名称猜测。

请求示例：

```json
{"operation":"tree"}
```

```json
{"operation":"searchByName","name":"patio furniture"}
```

```json
{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}
```

## 响应结构

网关使用两层状态：框架层为 `errcode` / `errmsg`，业务成功体内为 `code` / `msg`。成功时通常同时返回 `errcode=200`、`errmsg="ok"` 和 `code=200`、`msg="success"`；参数或服务异常时可能只返回 `errcode` / `errmsg`，应先判断框架层状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；`data.value` 按 operation 保留 Sorftime 原始数组、对象、标量或 `null` |
| `operation` | string | 本次实际执行的 `tree`、`searchByName` 或 `marketReport` |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer | 业务体兼容字段；NexScope 独立计费必须读取响应头 `X-Cost-Token` |
| `sourceType` | string | `sorftime` |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`costToken=0`，不按文档消耗补全。

业务结果统一从 `data.value` 读取。`tree` 节点可含 `Id`、`ParentId`、`NodeId`、`Name`、`CNName`、`URL`，整体约 10 MB。`searchByName` 返回 Sorftime `CategorySearchFromName` 数据，最多 3 个相关类目，每项包含 `NodeId` 与 `CategoryName`。`marketReport` 返回类目市场数据和最多 Top 80 的 Best Seller 产品；具体字段以实际响应为准。

## 错误码

| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 200 | 成功 | 按所选 operation 解析 `data.value` |
| 400 / 4000 | 缺少必填参数；框架校验全局必填字段时返回 400，业务条件必填校验返回 4000 | 补充 `operation`、`searchByName` 的 `name` 或 `marketReport` 的 `nodePath` |
| 4001 | 参数格式错误 | 检查 operation 大小写、name 是否非空及 nodePath 格式 |
| 401 | 认证失败 | 按 SKILL.md 的认证引导处理 |
| 402 | 积分不足 | 按 SKILL.md 的积分引导处理 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换参数连续重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"tree"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"patio furniture"}'
```

```bash
curl --max-time 120 -X POST "${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sorftime/walmart/categoryMarket" \
  -H "Authorization: $API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}'
```

## Feedback API

此端点与工具 API 独立：`POST https://skill-api.nexscope.com/api/v1/public/feedback`，`Content-Type: application/json`。

```json
{"skillName":"nexscope-sorftime-walmart-category-market","sentiment":"NEUTRAL","category":"SUGGESTION","content":"Describe intent, result, and feedback."}
```

`sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE` 之一；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 之一。
