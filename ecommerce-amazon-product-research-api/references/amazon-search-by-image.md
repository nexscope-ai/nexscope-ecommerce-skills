# Amazon Search By Image

This reference covers the image-search workflow for `ecommerce-amazon-product-research-api`.

## Purpose

Upload a user-provided product image through the shared NexScope asset service, then use its confirmed public URL to run Amazon product discovery.

## Operational Guidance

1. When the user supplies a local image, obtain explicit mutation confirmation and run `scripts/upload_image.py`.
2. The upload script calls `POST /api/skill-asset/presign`, uploads the image with `PUT` to the returned presigned HTTPS URL, and calls `POST /api/skill-asset/confirm`.
3. Pass only the confirm response's `publicUrl` to the `amazon_search_by_image` operation.
4. Route the returned products through only the additional market, keyword, review, or competitor operations required by the user's request.
5. Keep source facts, derived values, assumptions, and recommendations distinguishable.

## Contract Rules

- Use `api.json` as the machine-readable operation catalog and `api.md` for invocation details.
- The presign request contains `fileName`, `contentType`, and `fileSize`.
- The confirm request contains `ossKey`, `expectedSize`, and `expectedSha256`.
- Never derive a public image URL by stripping query parameters from the presigned upload URL.
- Never send `NEXSCOPE_API_KEY` to the presigned upload host.
- Validate required identifiers and record missing evidence instead of inventing results.

## Preserved Source Terms

- Request body: JSON.
- `asin`: string, Amazon Standard Identification Number.
- `urlSlug`: string, Keepa URL slug when required by the selected operation.

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
