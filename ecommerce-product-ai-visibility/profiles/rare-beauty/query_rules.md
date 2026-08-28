# Query Generation Rules

## Six Categories and Distribution

| Type | Share | Trigger Pattern |
|------|-------|----------------|
| Discovery | 30% | best ... for ..., top rated ..., recommended ... |
| Comparison | 15% | A vs B, ... compared to ..., which is better |
| Purchase Advice | 20% | what should I buy, what do experts recommend |
| Alternatives | 10% | alternatives to ..., similar to ..., instead of |
| Scenario/Platform | 15% | for sensitive skin, TikTok viral, vegan brands |
| Trust Validation | 10% | is X worth it, X review, is X reliable |

## Time Reference Rules

- Never hardcode specific years
- Use {{year}} variable when year is needed (auto-replaced at runtime)
- Prefer no-year phrasing unless user search habits include year

## Generation Principles

1. Each query must represent real user search behavior (conversational, natural)
2. Competitor names taken from product.md competitor list
3. Use scenarios derived from product.md user profile
4. Budget ranges derived from product.md price range
5. Comparison type must include at least one direct competitor
6. Alternatives anchor must be a well-known competitor
