---
name: ecommerce.amazon-product-research-api
version: 1.0.0
category: ecommerce
description: Route Amazon product-selection work across market, keyword, competitor, trend, review, and profitability capabilities. Use this skill when the user asks for this exact ecommerce workflow, analysis, data lookup, or deliverable.
---

# Amazon Product Research Api

## Core Concepts

Route Amazon product-selection work across market, keyword, competitor, trend, review, and profitability capabilities.

## Core workflow

1. Identify the marketplace, entity identifiers, date range, filters, and requested output.
2. Ask only for missing inputs that materially change the result.
3. Read `references/api.json` and select the exact package-local script for the required connector, calculation, transformation, or account workflow.
4. Execute the cataloged mode exactly: run `local-script` operations from this package, and follow this document for `agent-guided` operations.
5. Validate returned fields and preserve the distinction between source facts, calculations, and recommendations.
6. Save large results through the runtime and present a concise user-facing summary with the artifact path.

## Operation Catalog

| Operation | Mode | Mutation | Callable |
|---|---|---:|---:|
| `aba_query` | local-script | no | yes |
| `amazon_alexa_search` | local-script | no | yes |
| `amazon_opportunity_report` | local-script | no | yes |
| `amazon_opportunity_screener` | local-script | no | yes |
| `amazon_product_detail` | local-script | no | yes |
| `amazon_reviews` | local-script | no | yes |
| `amazon_search` | local-script | no | yes |
| `amazon_search_by_image` | local-script | no | yes |
| `jiimore_get_niche_info` | local-script | no | yes |
| `jiimore_get_niche_info_by_keyword` | local-script | no | yes |
| `jiimore_get_niche_review` | local-script | no | yes |
| `jiimore_page_asins_by_asin` | local-script | no | yes |
| `jiimore_product_discovery` | local-script | no | yes |
| `junglescout_keyword_by_asin` | local-script | no | yes |
| `junglescout_keyword_by_keyword` | local-script | no | yes |
| `junglescout_keyword_history` | local-script | no | yes |
| `junglescout_keyword_sov` | local-script | no | yes |
| `junglescout_product_database` | local-script | no | yes |
| `junglescout_sales_estimates` | local-script | no | yes |
| `keepa_product_detail` | local-script | no | yes |
| `keepa_product_history` | local-script | no | yes |
| `keepa_product_search` | local-script | no | yes |
| `onboarding` | local-script | no | yes |
| `sellersprite_competitor_lookup` | local-script | no | yes |
| `sellersprite_market_research` | local-script | no | yes |
| `sellersprite_market_statistics` | local-script | no | yes |
| `sellersprite_product_search` | local-script | no | yes |
| `sellersprite_traffic_keyword` | local-script | no | yes |
| `sif_asin_keywords` | local-script | no | yes |
| `sif_asin_summary` | local-script | no | yes |
| `sif_keyword_overview` | local-script | no | yes |
| `sif_keyword_traffic` | local-script | no | yes |
| `sorftime_product_detail` | local-script | no | yes |
| `sorftime_product_search` | local-script | no | yes |
| `upload_image` | gateway-script | yes | yes |

The machine-readable source of truth is `references/api.json`. Field-level payload rules remain operation-specific; do not invent identifiers, filters, credentials, or marketplace facts.

## API Invocation

Run only the package-local script recorded in the selected operation's `upstreamPath`. Business/tool operations may use the NexScope proxy; authorization/account operations use their configured Agent/Login service, and third-party connectors use their documented provider endpoint. Never invoke a script from another Skill.

## Usage Examples

```bash
python scripts/aba_query.py --help
# Then run the selected local script with its documented arguments.

python scripts/upload_image.py --confirm --confirm-mutation /path/to/product.png
# Upload through the shared Skill Asset presign -> PUT -> confirm workflow.
```

For a cataloged mutation, obtain explicit user approval and then pass both `--confirm` and `--confirm-mutation`. Never infer confirmation from an earlier read request.

For `upload_image`, use only `POST /api/skill-asset/presign`, the returned presigned HTTPS `PUT` URL, and `POST /api/skill-asset/confirm`. Treat only the `confirm` response's `publicUrl` as the final image URL. Never send `NEXSCOPE_API_KEY` to the presigned upload host.

## Runtime configuration

Business/tool operations require `NEXSCOPE_PROXY_BASE` plus `NEXSCOPE_API_KEY`; authorization/account operations require the relevant `NEXSCOPE_AGENT_*` or `NEXSCOPE_LOGIN_*` base because those proxy routes are not implemented. Third-party connectors require their documented provider configuration. Install optional libraries named by a script only when that operation is selected. Read `references/credentials.md` and set only the variables required by the selected script. Never pass secrets in command arguments or persist them in output artifacts.

Use only the hosts, credentials, and endpoints implemented by the package-local script and documented in `references/credentials.md`. Never substitute an undocumented legacy host or expose secret values.

## Display Rules

- Keep full JSON in the generated `nexscope/<date>/<session>/data/` artifact.
- Show the user the relevant records, assumptions, calculations, and limitations.
- Redact authorization, tokens, cookies, secrets, and passwords recursively.
- Do not treat an HTTP 200 response as success when the response envelope or upstream payload reports a business failure.

## Important Limitations

- Do not fabricate marketplace data or silently fill required business identifiers.
- Do not retry a mutation after an ambiguous timeout; query status first.
- Treat legal, compliance, tax, and profitability outputs as decision support, not professional advice.
- Do not claim real-account, sandbox, ZIP-install, or production validation unless that evidence exists.

## References

- Read `references/workflow.md` before executing the domain procedure.
- Read `references/api.md` for the package contract and examples.
- Read `references/testing.md` before claiming a validation level.

## Privacy and Errors

Treat marketplace, account, product, advertising, order, supplier, and generated-asset data as private. Keep credentials out of payloads and artifacts. Surface HTTP, application-envelope, upstream-business, malformed-response, and unavailable-connector failures distinctly.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
