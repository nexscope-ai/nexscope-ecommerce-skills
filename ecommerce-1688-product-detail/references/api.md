## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# 1688 商品详情 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/alibaba1688/productDetail`；`NEXSCOPE_PROXY_BASE` 未配置时脚本回退 `https://api.nexscope.ai`
- **请求方式**：POST，`Content-Type: application/json`
- **认证方式**：Header `Authorization: Bearer <api_key>`；api_key 优先从环境变量 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`
- **User-Agent**：`NexScope-Skill/2.0`
- **上下文透传 Header**：`SESSION_ID`、`MODE_ID`、`APP_NAME`，均读取同名环境变量，未配置时传空字符串
- **超时**：150s

## 请求参数

POST Body（JSON）只需传 1688 业务参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| offerId | string | 是 | - | 正整数格式的 1688 商品 ID；必须使用字符串，避免大数精度丢失；最大长度 1000 |
| country | string | 否 | `en` | 上游兼容字段；本 Skill 不将其作为用户能力，通常省略 |
| currency | string | 否 | 1688 默认币种 | 三位字母币种编码，如 `USD`、`HKD`；服务端会转为大写；最大长度 3 |

以下字段由平台按上下文自动注入，普通脚本调用不要填写：`uid`、`chatId`、`requestId`、`groupId`、`stepId`、`messageId`、`userInput`、`memberId`。

### 参数校验

- `offerId` 缺失或空字符串：返回参数错误。
- `offerId` 不是十进制整数或小于等于 0：返回参数错误。
- `country` 空白时使用服务端默认值；非空时去除首尾空白并原样传给 1688。
- `currency` 非空时必须匹配三位英文字母，服务端转为大写；例如 `usd` 会按 `USD` 请求。

最小有效请求：

```json
{
  "offerId": "1040473674152"
}
```

带币种的请求：

```json
{
  "offerId": "1040473674152",
  "currency": "USD"
}
```

## 响应结构

成功响应为一个 JSON object。网关会加入 `errcode=200` 与 `errmsg=ok`；业务字段来自标准化的 1688 商详模型。上游未返回的可选字段可能不出现在 JSON 中，不应把“字段缺失”解释为 `false`、`0` 或空字符串。

### 网关与核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关业务状态；`200` 表示成功 |
| errmsg | string | 网关消息；成功为 `ok` |
| offerId | string | 1688 商品 ID |
| subject | string | 中文标题 |
| subjectTrans | string | 上游扩展标题字段，可能为空或与 `subject` 相同 |
| description | string | 中文商品详情，常含 HTML |
| descriptionTrans | string | 上游扩展详情字段，可能缺失 |
| categoryId | string | 当前类目 ID |
| topCategoryId | string | 一级类目 ID |
| secondCategoryId | string | 二级类目 ID |
| thirdCategoryId | string | 三级类目 ID |
| categoryName | string | 类目名称，可能缺失 |
| status | string | 商品状态 |
| createDate | string | 商品创建时间 |
| productUrl | string | 1688 商品推广链接 |
| sourceType | string | 数据来源，当前为 `1688` |
| type | string | 结果样式，当前为 `productDetail` |
| sourceTool | string | 内部来源标签；面向用户展示时无需输出 |
| costToken | integer | 调用消耗 token；当前成功响应为 `1000` |

### 商品、媒体与采购字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productImage | object | 原始图片：`images[]`、`whiteImage` |
| productImageTrans | object | 上游扩展图片字段，结构同上，可能缺失 |
| mainVideo | string | 主视频地址 |
| detailVideo | string | 详情视频地址 |
| productAttributes | array | 商品属性：`attributeId`、`attributeName`、`attributeNameTrans`、`value`、`valueTrans` |
| sellingPoints | array | 商品卖点，可能为空 |
| skuList | array | SKU、规格、库存、价格与 SKU 图片，详见下节 |
| saleInfo | object | 库存、阶梯价、单位和分销销售信息，详见下节 |
| shippingInfo | object | 发货地、时效与商品/SKU 件重尺，详见下节 |
| companyName | string | 供应商/店铺名称 |
| sellerOpenId | string | 商家加密 ID |
| sellerDataInfo | object | 卖家服务与交易指标，详见下节 |
| sellerMixSetting | object | 混批设置：`generalHunpi`、`mixAmount`、`mixNumber` |
| channelPrice | object | 渠道 SKU 价格：`skuPrices[].skuId/currentPrice` |
| promotion | object | 营销信息：`hasPromotion`、`promotionType` |
| minOrderQuantity | integer | 最小起批量 |
| batchNumber | integer | 一手数量 |
| productCargoNumber | string | 商品货号 |
| soldOut | string | 商品销量 |
| isJxhy | boolean | 是否精选货源 |
| isSelect | boolean | 是否跨境 Select 货盘 |
| tradeScore | string | 商品交易评分 |
| offerIdentities | array | 商品或商家身份标识 |
| tags | array | 服务标签：`key`、`value` |
| certificates | array | 证书：`certificateName`、`certificateCode`、`certificatePhotoList[]` |
| invoiceInfo | object | 发票：`supportOnlineInvoice`、`supportFastInvoice`、`invoiceTypes[]`、`taxpayerType` |

### `skuList[]`

| 字段 | 类型 | 说明 |
|------|------|------|
| skuId | string | SKU ID |
| specId | string | 规格 ID |
| cargoNumber | string | SKU 货号 |
| amountOnSale | integer | 可售库存 |
| price | string | SKU 价格（人民币）；新零售价模型中是采购数量大于等于 2 件的批发价，旧商品模型语义结合阶梯和订单预览判断 |
| retailPrice | string | SKU 零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| foreignCurrencyRetailPrice | number | SKU 外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| promotionPrice | string | 营销价 |
| consignPrice | string | 一件代发价格；上游废弃兼容字段，可能缺失 |
| jxhyPrice / pfJxhyPrice | string | 精选货源兼容价格字段，可能缺失 |
| skuImageUrl / skuImageUrlTrans | string | SKU 图片及上游扩展图片字段 |
| attributes | array | SKU 属性；包含名称、值以及可选图片 |
| fenxiaoPriceInfo | object | `offerPrice`、`onePiecePrice`、`foreignCurrencyPrice`、`foreignCurrencyPromotionPrice` |

`currency` 对应 `foreignCurrencyRetailPrice`、`fenxiaoPriceInfo.foreignCurrencyPrice` 和其他 `foreignCurrency*` 字段。不要把人民币 `retailPrice`、`price`、`offerPrice` 直接标成请求币种。

### `saleInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| amountOnSale | integer | 商品总库存 |
| retailPrice | string | 商品级零售价（人民币），适用于采购数量 1 件；上游无零售价时缺失 |
| foreignCurrencyRetailPrice | number | 商品级外币零售价，适用于采购数量 1 件；未请求币种、无零售价或换算失败时缺失 |
| quoteType | integer | `0` 无 SKU 按商品数量；`1` 按 SKU 规格；`2` 有 SKU 按商品数量 |
| priceRanges | array | 批发阶梯价：`startQuantity`、`price`、`promotionPrice`、`foreignCurrencyPrice`、`foreignCurrencyPromotionPrice`；新零售价模型首档大于等于 2，旧商品模型可能仍从 1 件起 |
| unitInfo | object | 单位字段 `unit` 与上游扩展字段 `transUnit` |
| fenxiaoSaleInfo | object | `startQuantity`、`offerPrice`、`onePiecePrice`、`onePieceFreePostage` |
| consignPrice / jxhyPrice | string | 上游废弃兼容字段，可能缺失 |

### 零售价改造后的价格选择

- 新零售价模型、采购数量为 1 件：读取匹配 SKU 的 `skuList[].retailPrice`；无 SKU 商品读取 `saleInfo.retailPrice`。
- 新零售价模型、采购数量大于等于 2 件：读取匹配 SKU 的 `skuList[].price`，并结合 `saleInfo.priceRanges[]` 选择数量所在的批发阶梯。
- `minOrderQuantity` 仍可能为 `1`，但新零售价模型的 `priceRanges` 批发首档从 2 件起；不要因为最小起批量为 1 就把批发价当成 1 件价。
- `retailPrice` 缺失可能表示旧商品模型或未设置零售价。保持零售价缺失，不要自动回退到 `price`、`consignPrice`、`jxhyPrice`、`offerPrice`、`onePiecePrice` 或 `promotionPrice`。若阶梯明确从 `startQuantity=1` 起，只能标为旧模型阶梯信息；涉及成本、利润或下单时仍须用实时订单预览确认 1 件成交价。
- `promotionPrice` 的含义未因本次零售价改造而改变；不得用它代替零售价。最终可购性、优惠、运费和成交价以实时订单预览为准。

### `shippingInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| sendGoodsAddressText | string | 发货地 |
| shippingTimeGuarantee | string | 发货保障 |
| length / width / height | number | 商品长宽高，单位 cm |
| weight | number | 商品重量，单位 kg |
| officialLength / officialWidth / officialHeight | number | 官方测量长宽高，单位 cm |
| officialWeight | number | 官方测量重量，单位 kg |
| pkgSizeSource | string | 商品件重尺数据来源 |
| skuShippingInfoList | array | SKU 物流规格；`weight` 单位 g，其余尺寸单位 cm |
| skuShippingDetails | array | SKU 件重尺；`weight`/`officialWeight`/`aiWeight` 单位 kg，尺寸单位 cm |

### `sellerDataInfo`

| 字段 | 类型 | 说明 |
|------|------|------|
| tradeMedalLevel | string | 卖家交易勋章 |
| compositeServiceScore | string | 综合服务分 |
| logisticsExperienceScore | string | 物流体验分 |
| disputeComplaintScore | string | 纠纷解决分 |
| offerExperienceScore | string | 商品体验分 |
| consultingExperienceScore | string | 咨询体验分 |
| afterSalesExperienceScore | string | 退换体验分 |
| repeatPurchasePercent | string | 卖家回头率 |
| collect30DayWithin48HPercent | string | 最近 30 天 48 小时揽收率 |
| qualityRefundWithin30Day | string | 最近 30 天品质退款率 |

### 新零售价模型响应形状（字段示例）

以下示例用于说明新字段位置和类型，不代表指定 offerId 当前一定已切换到新零售价模型；实际字段和值以实时响应为准。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "offerId": "1040473674152",
  "subject": "专业采耳工具掏耳朵耳朵鹅绒毛毛棒打毛毛扣挖耳勺采耳按摩鹅毛棒",
  "skuList": [
    {
      "skuId": "6226287579433",
      "retailPrice": "4.80",
      "foreignCurrencyRetailPrice": 0.73,
      "price": "4.05",
      "amountOnSale": 457,
      "fenxiaoPriceInfo": {
        "offerPrice": "4.05",
        "onePiecePrice": "4.05"
      }
    }
  ],
  "saleInfo": {
    "amountOnSale": 1917,
    "retailPrice": "4.80",
    "foreignCurrencyRetailPrice": 0.73,
    "priceRanges": [
      {
        "startQuantity": 2,
        "price": "4.05",
        "foreignCurrencyPrice": 0.62
      }
    ]
  },
  "sourceType": "1688",
  "type": "productDetail",
  "costToken": 1000
}
```

## 错误码

脚本会把 HTTP 错误体尽量解析为 JSON 返回，不会因网关 4xx/5xx 打印 Python 堆栈。

| errcode / HTTP | 含义 | 处理建议 |
|----------------|------|----------|
| 200 | 成功 | 解析业务字段，并确认 `offerId` 与请求一致 |
| 400 | 路由层参数校验失败 | 检查必填、类型、格式与长度；错误响应可能回显已接收的参数 |
| 1002 | 服务层参数或登录上下文错误 | 检查 `offerId`、`currency`，或重新登录 |
| 1003 | 1688 商详服务/上游响应异常 | 稍后重试一次；仍失败则联系网关维护者 |
| 1005 | 当前用户未授权且默认授权不可回退 | 按 1688 授权流程处理 |
| HTTP 401 | API Key 鉴权失败 | 按 SKILL.md 的“解决认证和积分问题”处理 |
| HTTP 402 | 积分不足 | 按 SKILL.md 的“解决认证和积分问题”处理 |
| HTTP 403 | 无权限 | 不属于登录/充值引导，联系管理员确认工具权限 |

常见参数错误响应：

```json
{
  "errcode": 400,
  "offerId": "",
  "errmsg": "offerId 为必填参数"
}
```

## curl 示例

```bash
API_KEY="${NEXSCOPE_API_KEY:-$NEXSCOPE_API_KEY}"

curl --location "${NEXSCOPE_PROXY_BASE:-https://api.nexscope.ai}/api/v1/tools/research/alibaba1688/productDetail" \
  --header "Authorization: ${API_KEY}" \
  --header "Content-Type: application/json" \
  --header "User-Agent: NexScope-Skill/2.0" \
  --header "SESSION_ID: ${SESSION_ID:-}" \
  --header "MODE_ID: ${MODE_ID:-}" \
  --header "APP_NAME: ${APP_NAME:-}" \
  --data '{
    "offerId": "1040473674152",
    "currency": "USD"
  }'
```

---

## Feedback API

> 此地址与上方工具网关相互独立，不要混用 base URL。

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type**：`application/json`

```json
{
  "skillName": "nexscope-1688-product-detail",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "The product detail matched the requested 1688 offer."
}
```

**字段规则：**

- `skillName`：固定使用 YAML frontmatter 的 `nexscope-1688-product-detail`
- `sentiment`：`POSITIVE`、`NEUTRAL`、`NEGATIVE` 三选一
- `category`：`BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER` 四选一
- `content`：说明用户意图、实际结果，以及问题或表扬的原因
