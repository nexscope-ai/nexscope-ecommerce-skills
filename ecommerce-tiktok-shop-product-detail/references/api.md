## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# TikTok Shop 商品详情 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/tiktok/shop/product/detail`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`（未配置时按 SKILL.md 的「解决认证和积分问题」处理）
- **User-Agent**：`NexScope-Skill/2.0`
- **透传请求头**：`SESSION_ID`、`MODE_ID`、`APP_NAME`（均从同名环境变量读取，未配置时为空字符串）
- **超时**：150s

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| productInput | string | 是 | - | TikTok HTTPS 商品 URL（host 必须为 `tiktok.com` 或其子域，端口须省略或为 `443`，路径须包含连续的 `product/<19位数字ID>`），或 19 位商品 ID。商品 ID 必须以字符串传递，避免数字精度丢失 |
| region | string | 否 | `US` | 大写站点代码：`US`、`GB`、`ID`、`MY`、`TH`、`VN`、`PH`、`SG`、`DE`、`FR`、`IT`、`ES` |

仅接受上表中的公共请求参数，不支持切换其他响应模式。每次调用仅查询一个商品；若上游返回的有效商品数量不是 1，接口返回业务错误。

最小请求：

```json
{
  "productInput": "1729937400435937604"
}
```

## 响应结构

成功响应为 NexScope 统一包装：

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；`200` 表示成功 |
| errmsg | string | 业务状态消息；成功时为 `ok` |
| data | array | 整理后的商品数组；成功时固定 1 条 |
| total | integer | 成功时固定为 `1` |
| costToken | integer | 消耗 token |
| type | string | 固定为 `tableListWorkbenches` |
| columns | array | 根据商品顶层字段生成的渲染列定义 |

### 商品对象

商品顶层字段使用 camelCase；各业务分组内部保留来源字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | string | 商品 ID |
| status | integer | 平台商品状态码；不能单独用于判断可售性 |
| title | string | 商品标题 |
| category | object | 类目名称与 ID |
| pricing | object | 币种、售价、原价、折扣及价格原始字段 |
| sales | object | 公开售出数量及销售展示字段 |
| inventory | object | 总库存、SKU、销售属性、SKU 价格及默认选择 |
| media | object | 图片 URL 与图片元数据 |
| seller | object | 店铺 ID、名称、评分、地区及可用店铺字段 |
| reviews | object | 公开评论概况（可能为空） |
| shipping | object | 物流与配送模块（可能为空） |
| actions | object | 加购、购买与收藏状态 |
| additional | object | 促销、用户权益及其他可读产品模块，可能很大 |

示例（部分商品字段与嵌套字段已截短）：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "data": [
    {
      "productId": "1729937400435937604",
      "status": 3,
      "title": "CARER SPARK Double Side Multifunctional Facial Cleanser Beauty Device...",
      "category": {"name": "Beauty & Personal Care", "id": "601450"},
      "pricing": {"currency": "USD", "currency_symbol": "$", "sale_price": "$59.99"},
      "sales": {"sold_count": 1},
      "inventory": {
        "total_stock": 0,
        "skus": [{"sku_id": "1730030266154783044", "stock": 0}],
        "sale_props": [{"prop_name": "Color"}]
      },
      "media": {"image_urls": ["https://..."]},
      "seller": {
        "seller_id": "7495351603438586180",
        "name": "CARER SPARK",
        "rating": "3.9",
        "location": "United States of America"
      }
    }
  ],
  "total": 1,
  "costToken": 84000,
  "type": "tableListWorkbenches",
  "columns": [
    {
      "filterable": true,
      "cellType": "text",
      "field": "productId",
      "sortable": true,
      "title": "商品ID"
    }
  ]
}
```

## 错误码与边界

| 情况 | 表现 | 处理建议 |
|------|------|----------|
| 成功 | HTTP 200 且返回上述统一包装 | 按 `data` 解析 |
| productInput 为空或格式非法 | 网关业务错误 | 传路径含 `product/<19位ID>` 的 TikTok HTTPS 商品链接，或直接传 19 位字符串 ID |
| region 不支持 | 网关业务错误 | 改用文档列出的站点代码 |
| 商品不存在、地区不可访问或返回空商品数组 | 网关业务错误，不返回“成功空列表” | 核对商品与地区；不要自动轮询其他地区 |
| 上游返回多个有效商品 | 网关业务错误 | 视为上游结果异常；本接口不截断、不返回批量结果 |
| 401 | 鉴权失败 | 按 SKILL.md 的「解决认证和积分问题」处理 |
| 402 | 积分不足 | 按 SKILL.md 的「解决认证和积分问题」处理 |
| 超时或上游异常 | 连接错误、5xx 或业务错误 | 告知用户；不要连续自动重试产生额外费用 |

返回字段可能因商品、卖家、地区和页面上下文而缺失。即使商品下架或库存为 0，也可能返回结构化详情。

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"
curl -X POST "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/tiktok/shop/product/detail" \
  -H "Authorization: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID:-}" \
  -H "MODE_ID: ${MODE_ID:-}" \
  -H "APP_NAME: ${APP_NAME:-}" \
  -d '{
    "productInput": "1729937400435937604",
    "region": "US"
  }'
```

---

## Feedback API

> 此端点与上方工具 API 分离，不要混用 Base URL。

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-tiktok-shop-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The product detail matched the requested TikTok Shop listing."
}
```

- `skillName`：固定使用本 Skill frontmatter 的 `name`
- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一
- `content`：简述用户意图、实际表现以及问题或表扬原因
