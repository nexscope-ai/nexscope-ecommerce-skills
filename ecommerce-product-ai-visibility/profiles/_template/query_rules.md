# Query Generation Rules

## Six Query Types and Distribution

| Type | Share | Trigger Pattern |
|------|-------|-----------------|
| Discovery | 30% | best ... for ..., top rated ..., recommended ... |
| Comparison | 15% | A vs B, ... compared to ..., which is better |
| Purchase Advice | 20% | what should I buy, what do experts recommend |
| Alternatives | 10% | alternatives to ..., similar to ..., instead of |
| Platform-Specific | 15% | for Amazon sellers, for Shopify, for TikTok Shop |
| Trust Validation | 10% | is X worth it, X review, is X reliable |

## Year Reference Rules

- **Never hardcode a specific year**
- Use `{{year}}` variable when year is needed; auto-replaced at runtime with current year
- Prefer year-free phrasing unless user search habits genuinely include year

## Generation Principles

1. Each query must represent real user search behavior (conversational, natural)
2. Competitor names come from the competitors list in product.md
3. Use cases derive from the user profile in product.md
4. Budget range derives from the price range in product.md
5. Comparison queries must include at least one direct competitor
6. Alternative queries must anchor on a well-known competitor (one the user likely already uses)
