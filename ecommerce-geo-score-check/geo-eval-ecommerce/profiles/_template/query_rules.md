# Query Generation Rules

## Six Query Types and Their Shares

| Type | Share | Trigger Patterns |
|------|------|-----------|
| Discovery (discovery) | 30% | best ... for ..., top rated ..., recommended ... |
| Comparison (comparison) | 15% | A vs B, ... compared to ..., which is better |
| Purchase Advice (purchase_advice) | 20% | what should I buy, what do experts recommend |
| Alternatives (alternatives) | 10% | alternatives to ..., similar to ..., instead of |
| Platform-Specific Scenarios (platform_specific) | 15% | for Amazon sellers, for Shopify, for TikTok Shop |
| Trust Validation (trust_validation) | 10% | is X worth it, X review, is X reliable |

## Time Reference Rules

- **Do not hardcode a specific year**
- Use `{{year}}` when a year is needed; it is replaced with the current year at runtime
- Prefer wording without a year unless users typically include one in their searches

## Generation Principles

1. Each query must reflect real user search behavior with natural, conversational wording
2. Take competitor names from the competitor list in product.md
3. Derive use cases from the customer profile in product.md
4. Derive budget ranges from the price range in product.md
5. Comparison queries must include at least one direct competitor
6. Anchor alternatives queries to a well-known competitor that the user may already use
