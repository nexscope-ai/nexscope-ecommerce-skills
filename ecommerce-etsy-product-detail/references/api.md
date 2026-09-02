## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# Etsy 商品详情 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/etsy/product/detail`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`（未配置时按 SKILL.md 的「解决认证和积分问题」处理）
- **User-Agent**：`NexScope-Skill/2.0`
- **透传请求头**：`SESSION_ID`、`MODE_ID`、`APP_NAME`（均从同名环境变量读取，未配置时为空字符串）
- **超时**：150s

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productUrl | string | 是 | - | Etsy 商品 HTTPS 直链。不得含 userinfo；Host 必须为 `etsy.com` 或其子域，端口须省略或为 `443`；路径须为 `/listing/<数字ID>`，最多再带一个非空标题 slug，可带尾斜杠与查询参数 |

不接受 Etsy 搜索页、店铺页、非 Etsy 域名或缺少数字 listing ID 的 URL。每次调用仅查询一个 Listing；若上游返回的有效商品数量不是 1，接口返回业务错误。

```json
{
  "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
}
```

## 响应结构

成功响应为 NexScope 统一包装：

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；`200` 表示成功 |
| errmsg | string | 业务状态消息；成功时为 `ok` |
| data | array | 商品对象数组；成功时固定 1 条 |
| total | integer | 成功时固定为 `1` |
| costToken | integer | 消耗 token |
| type | string | 固定为 `tableListWorkbenches` |
| columns | array | 根据商品顶层字段生成的渲染列定义 |

### 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | Etsy listing ID |
| shopId | string | 店铺 ID |
| shopUrl | string | 店铺 URL；页面异常时可能为空或误识别 |
| shopSales | string | 店铺公开销量文本 |
| shopName | string | 店铺名称；页面异常时可能为空或误识别 |
| productUrl | string | 商品 URL |
| searchPosition | string | 来源搜索位置；直链查询通常为空 |
| image | string | 主图 URL |
| images | array | 图片 URL 列表 |
| maxQuantity | integer | 页面报告的最大可购数量 |
| variants | array | 商品变体；无变体时为空数组 |
| title | string | 商品标题 |
| description | array | 描述段落列表 |
| deliveryDaysMin / deliveryDaysMax | integer/null | 预计送达天数范围；来源为空时可能为 null 或不返回该字段 |
| shopReviews | integer | 店铺评论数量 |
| reviews | integer | 当前 Listing 评论数量 |
| star | string | 当前评分，可能为空字符串 |
| highlightsTags | array | 买家反馈亮点标签 |
| reviewsTags | array | 评论标签及频次对象 |
| yearsOnEtsy | string | 店铺在 Etsy 的公开年限 |
| hasRatingsBadge | boolean | 是否有评分徽章 |
| hasConvosBadge | boolean | 是否有沟通徽章 |
| hasShippingBadge | boolean | 是否有配送徽章 |
| reviewsScores | object | 动态评论分项；键和值随页面而变 |
| category | string | 类目面包屑 |
| price / lowPrice / highPrice / oldPrice | string | 价格字段，部分字段可能为空 |
| countryShippingFrom | string | 发货国家/地区 |
| currency | string | 币种代码 |
| moreLikeUrl | string | 相似推荐链接，可能为空 |

接口只返回评论数量、标签与聚合分数，不返回逐条评论内容。

示例（部分商品字段、描述、图片与 `columns` 已截短）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "productId": "1710567856",
      "shopId": "35055979",
      "shopName": "",
      "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt",
      "title": "It's Okay To Make Some Mistakes Shirt...",
      "images": ["https://i.etsystatic.com/..."],
      "maxQuantity": 952,
      "variants": [],
      "reviews": 134,
      "star": "",
      "lowPrice": "9.76",
      "highPrice": "32.55",
      "currency": "EUR"
    }
  ],
  "total": 1,
  "costToken": 7000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品 ID"
    }
  ]
}
```

## 错误码与边界

| 情况 | 表现 | 处理建议 |
|------|------|----------|
| 成功 | HTTP 200 且返回上述统一包装 | 按 `data` 解析 |
| productUrl 为空或 URL 不合法 | 网关业务错误 | 传完整 Etsy Listing HTTPS URL |
| 非 Listing 页面、非 Etsy 域名或路径层级过深 | 网关业务错误 | 核对 host，并使用 `/listing/<数字ID>` 加至多一个标题 slug 的路径 |
| Listing 不存在、不可访问或返回空数组 | 网关业务错误，不应当作“成功空列表” | 核对链接；不要自动改链接连续试探 |
| 上游返回多个有效 Listing | 网关业务错误 | 视为上游结果异常；本接口不截断、不返回批量结果 |
| 401 | 鉴权失败 | 按 SKILL.md 的「解决认证和积分问题」处理 |
| 402 | 积分不足 | 按 SKILL.md 的「解决认证和积分问题」处理 |
| 超时或上游异常 | 连接错误、5xx 或业务错误 | 告知用户；不要连续自动重试产生额外费用 |

公开页面结构变化会导致字段缺失、空字符串、null 或偶发误识别。调用方应如实展示，不应自行推断或静默修复。

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl -X POST "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/etsy/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productUrl": "https://www.etsy.com/listing/1710567856/its-okay-to-make-some-mistakes-shirt"
  }'
```

---

## Feedback API

> 此端点与上方工具 API 分离，不要混用 Base URL。

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-etsy-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The listing detail matched the requested Etsy product."
}
```

- `skillName`：固定使用本 Skill frontmatter 的 `name`
- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一
- `content`：简述用户意图、实际表现以及问题或表扬原因
