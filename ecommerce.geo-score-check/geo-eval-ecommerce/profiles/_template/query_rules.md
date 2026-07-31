# Query 生成规则

## 六大类型及占比

| 类型 | 占比 | 触发词模式 |
|------|------|-----------|
| 发现型 (discovery) | 30% | best ... for ..., top rated ..., recommended ... |
| 对比型 (comparison) | 15% | A vs B, ... compared to ..., which is better |
| 购买建议型 (purchase_advice) | 20% | what should I buy, what do experts recommend |
| 替代品型 (alternatives) | 10% | alternatives to ..., similar to ..., instead of |
| 场景型 (platform_specific) | 15% | for Amazon sellers, for Shopify, for TikTok Shop |
| 信任验证型 (trust_validation) | 10% | is X worth it, X review, is X reliable |

## 时间引用规则

- **禁止硬编码具体年份**
- 需要年份时使用 `{{year}}` 变量，运行时自动替换为当前年份
- 优先使用无年份写法，除非用户搜索习惯确实带年份

## 生成原则

1. 每条 query 必须代表真实用户的搜索习惯（口语化、自然）
2. 竞品名从 product.md 的竞品列表中取
3. 使用场景从 product.md 的用户画像中推导
4. 预算范围从 product.md 的价格区间推导
5. 对比型必须包含至少一个直接竞品
6. 替代品型的锚点必须是知名竞品（用户可能正在用的）
