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
4. Execute the cataloged mode exactly: run `gateway-script` and `local-script` operations with the package-local script recorded in `upstreamPath`, and follow this document for `agent-guided` operations.
5. Validate returned fields and preserve the distinction between source facts, calculations, and recommendations.
6. Save large results through the runtime and present a concise user-facing summary with the artifact path.

## Operation Catalog

| Operation | Mode | Mutation | Callable |
|---|---|---:|---:|
| `aba_query` | gateway-script | no | yes |
| `amazon_alexa_search` | gateway-script | no | yes |
| `amazon_opportunity_report` | gateway-script | no | yes |
| `amazon_opportunity_screener` | gateway-script | no | yes |
| `amazon_product_detail` | gateway-script | no | yes |
| `amazon_reviews` | gateway-script | no | yes |
| `amazon_search` | gateway-script | no | yes |
| `amazon_search_by_image` | gateway-script | no | yes |
| `jiimore_get_niche_info` | gateway-script | no | yes |
| `jiimore_get_niche_info_by_keyword` | gateway-script | no | yes |
| `jiimore_get_niche_review` | gateway-script | no | yes |
| `jiimore_page_asins_by_asin` | gateway-script | no | yes |
| `jiimore_product_discovery` | gateway-script | no | yes |
| `junglescout_keyword_by_asin` | gateway-script | no | yes |
| `junglescout_keyword_by_keyword` | gateway-script | no | yes |
| `junglescout_keyword_history` | gateway-script | no | yes |
| `junglescout_keyword_sov` | gateway-script | no | yes |
| `junglescout_product_database` | gateway-script | no | yes |
| `junglescout_sales_estimates` | gateway-script | no | yes |
| `keepa_product_detail` | gateway-script | no | yes |
| `keepa_product_history` | gateway-script | no | yes |
| `keepa_product_search` | gateway-script | no | yes |
| `onboarding` | local-script | no | yes |
| `sellersprite_competitor_lookup` | gateway-script | no | yes |
| `sellersprite_market_research` | gateway-script | no | yes |
| `sellersprite_market_statistics` | gateway-script | no | yes |
| `sellersprite_product_search` | gateway-script | no | yes |
| `sellersprite_traffic_keyword` | gateway-script | no | yes |
| `sif_asin_keywords` | gateway-script | no | yes |
| `sif_asin_summary` | gateway-script | no | yes |
| `sif_keyword_overview` | gateway-script | no | yes |
| `sif_keyword_traffic` | gateway-script | no | yes |
| `sorftime_product_detail` | gateway-script | no | yes |
| `sorftime_product_search` | gateway-script | no | yes |
| `upload_image` | gateway-script | yes | yes |

The machine-readable source of truth is `references/api.json`. Field-level payload rules remain operation-specific; do not invent identifiers, filters, credentials, or marketplace facts.

## API Invocation

Every research-tool request must use the full path recorded in `references/api.json`, beginning with `/api/v1/tools/research/`. Set `NEXSCOPE_PROXY_BASE` to the gateway origin only; never call a legacy short path such as `/amazon/**`, `/kalodata/**`, or `/aigc/**` directly.

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
