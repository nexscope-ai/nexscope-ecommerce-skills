## NexScope billing

The migrated Skill does not inherit the source platform's point value. Read X-Cost-Token from the HTTP response headers and calculate NexScope credits as X-Cost-Token × 0.001041. Example: 105000 × 0.001041 = 109.305. Preserve X-Cost-Credit as reported metadata only; it is not the calculation basis. Also preserve X-Kong-Trace-Id for diagnostics.

# NexScope proxy contract

The endpoint uses the `/api/v1/tools/research/` prefix. Successful HTTP responses use a NexScope envelope (`code`, `msg`, `data`, `traceId`, and cost metadata); the original business response is nested in `data`.

# EchoTik-TikTok视频排行 API 参考

## 调用规范

- **请求地址**：`${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank`
- **请求方式**：POST，Content-Type: application/json
- **认证方式**：Header `Authorization: Bearer <api_key>`，api_key 优先从环境变量 `NEXSCOPE_API_KEY` 读取，回退 `NEXSCOPE_API_KEY`（如未配置 按 SKILL.md 的 **## 解决认证和积分问题** 处理）
- **User-Agent**：`NexScope-Skill/2.0`
- **超时**：150s

## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| date | string | 是 | - | 榜单查询日期，格式 `YYYY-MM-DD` |
| rankType | integer | 是 | - | 榜单类型：`1` = 日榜，`2` = 周榜，`3` = 月榜 |
| region | string | 是 | - | 区域码。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| videoRankField | integer | 是 | - | 视频排名指标：`1` = 按播放量排名，`2` = 按视频销量排名 |
| productCategoryId | string | 否 | - | 商品一级类目 ID，用于带货视频榜单的商品分类筛选 |
| createdByAi | string | 否 | - | 是否 AI 视频，可选字符串 `true` / `false` |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；官方接口单页上限10，内部按10每页多次拉取后合并 |

### rankType 枚举

| 值 | 含义 |
|----|------|
| 1 | 日榜（day） |
| 2 | 周榜（week） |
| 3 | 月榜（month） |

### videoRankField 枚举

| 值 | 含义 | 实测 |
|----|------|------|
| 1 | 按播放量排名（`totalViewsCnt`） | ✓ 200，返回高播放量视频 |
| 2 | 按视频销量排名（`totalVideoSaleCnt`） | ✓ 200，返回高销量视频 |

> **指标稀疏现象**：按某 `videoRankField` 排序时，非该指标的计数字段可能返回 0（按销量排名时播放/点赞/评论等可能为 0；按播放量排名时销量/GMV 可能为 0）。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功（详见下方错误码） |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| data | array | 视频列表（已按 `videoRankField` 排序，详见下方视频字段） |
| columns | array | 渲染的列（前端渲染元数据，长度可能大于 `data`，取数据请以 `data` 为准） |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

### 视频对象字段

> 以下 25 个字段为 `data[*]` 返回字段，与 `columns` 定义对应。指标字段名虽以 `total` 开头，但表示**所选排行周期内**的累计值（`columns` 列标题为"周期…"）。

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| officialUrl | string | TikTok官方视频地址 |
| userId | string | 达人ID |
| uniqueId | string | TikTok账号ID |
| nickName | string | 达人昵称 |
| avatar | string | 达人头像 |
| category | string | 达人分类 |
| videoDesc | string | 视频描述 |
| createDate | string | 视频发布日期 |
| coverUrl | string | 视频封面URL |
| region | string | 区域代码 |
| duration | integer | 视频时长(秒) |
| createdByAiText | string | 是否AI视频（是/否） |
| salesFlagText | string | 是否带货视频（是/否） |
| productCategoryList | string | 带货商品分类 |
| videoProducts | string | 视频带货商品 |
| totalCommentsCnt | integer | 周期评论数 |
| totalDiggCnt | integer | 周期点赞数 |
| totalFavoritesCnt | integer | 周期收藏数 |
| totalSharesCnt | integer | 周期分享数 |
| totalViewsCnt | integer | 周期播放量 |
| totalVideoSaleCnt | integer | 周期视频销量(估算) |
| totalVideoSaleGmvAmt | number | 周期视频销售GMV(估算) |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errcode 字段区分（errcode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errcode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 400 | 参数校验错误 | 缺少必填参数（如 `date`/`rankType`/`region`/`videoRankField` 为必填参数）或取值非法。参考 `errmsg` 获取具体字段与合法值集合 |
| 401 | 认证失败 | HTTP 401 或 `authorized error`：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。|
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 400,
    "errmsg": "date 为必填参数"
}
```

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl 示例

### 指定日期的美国视频播放量排行

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "date": "2026-08-10",
    "rankType": 1,
    "region": "US",
    "videoRankField": 1,
    "pageNum": 1,
    "pageSize": 20
  }'
```

### 英国视频排行

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "date": "2026-08-10",
    "rankType": 2,
    "region": "GB",
    "videoRankField": 1
  }'
```

### 美国月度 AI 带货视频销量排行

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/echotik/listVideoRank \
  -H "Authorization: $NEXSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/2.0" \
  -d '{
    "date": "2026-08-01",
    "rankType": 3,
    "region": "US",
    "videoRankField": 2,
    "createdByAi": "true",
    "productCategoryId": "601450",
    "pageNum": 1,
    "pageSize": 10
  }'
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.nexscope.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "nexscope-echotik-list-video-rank",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter (`nexscope-echotik-list-video-rank`)
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
