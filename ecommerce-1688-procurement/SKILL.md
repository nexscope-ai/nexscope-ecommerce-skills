---
name: ecommerce-1688-procurement
description: Assist with authorized 1688 procurement through Nexscope, including OAuth authorization, addresses, SKUs, order previews, confirmed order creation, payment links, order status, logistics, cancellation, receipt confirmation and invoices. Use when users ask to buy on 1688, manage a 1688 order, authorize a buyer account or request an invoice. Use ecommerce-1688-search-by-image for product discovery.
---

# 1688 Procurement

Read [API reference](references/api.md) before calling an operation and [workflow](references/workflow.md) before a multistep purchase. Use the user's `NEXSCOPE_API_KEY`; no separate supplier account or API key is required. The buyer still completes 1688 OAuth in their browser.

Before the user opens the authorization URL, explain: "Authorization is supported by LinkFox Agent, Nexscope's strategic partner in China. You will see 'LinkFox Agent' on the 1688 authorization page. Authorize your own 1688 account; Nexscope links it to your Nexscope user account."

Also explain: "The permission descriptions and agreement notice on the 1688 authorization page are in Chinese. Use your browser's translation feature and select English to read them. Changing your browser's language alone does not switch these sections to English."

Share the [English reference translation of the authorization page](references/1688-authorization-reference-en.png) when helpful. Explain that it is for reference only; the actual 1688 authorization page and applicable agreements must be consulted. The translation does not change the official page or prove authorization.

Tell the user: "Use data only within the scope of your authorization and in accordance with applicable local laws, regulations, and platform terms."

Complete authorization within 10 minutes of requesting the URL. If authorization fails or the link expires, request a new URL and try again, then verify `authorizedStores` reports `ACTIVE` and `expired=false`. Do not treat the redirect page alone as proof of authorization.

## Invocation

- All 14 operations use `POST /api/v1/tools/research/alibaba1688/<operation>`.
- Set `NEXSCOPE_API_KEY`; optional `NEXSCOPE_PROXY_BASE` defaults to `https://api.nexscope.ai`. Authentication is `Authorization: Bearer <NEXSCOPE_API_KEY>`.
- Run `python scripts/<script>.py '<JSON parameters>' [--inline] [--save] [--no-save]`.
- Windows: use `--payload-file request.json` or `--payload-env PAYLOAD` to avoid shell escaping.
- Invoking this Skill consumes credits. Each procurement script except the two authorization scripts calls `authorizedStores` first, then the requested operation only when authorization is active. This precheck is a separate billable public call in addition to the requested operation; internal token exchange and refresh are not extra public calls.
- No local response cache, polling loop, automatic retry or automatic replay is used.

```powershell
$env:PAYLOAD = "{}"
python scripts/authorized_stores.py --payload-env PAYLOAD --inline
```

## Available operations

| Script | Operation | Separate confirmation |
|---|---|---|
| `authorize_url.py` | `authorizeUrl` | No |
| `authorized_stores.py` | `authorizedStores` | No |
| `receive_address_list.py` | `receiveAddressList` | No |
| `sku.py` | `sku` | No |
| `order_preview.py` | `orderPreview` | No |
| `create_order.py` | `createOrder` | Yes |
| `payment_url.py` | `paymentUrl` | Yes |
| `order_status.py` | `orderStatus` | No |
| `logistics.py` | `logistics` | No |
| `logistics_trace.py` | `logisticsTrace` | No |
| `confirm_receive.py` | `confirmReceive` | Yes |
| `cancel_order.py` | `cancelOrder` | Yes |
| `invoice_amount.py` | `invoiceAmount` | No |
| `invoice_apply.py` | `invoiceApply` | Yes |

## Operating rules

1. `authorizedStores` describes the current authenticated user's authorization. Continue only with `status=ACTIVE` and `expired=false`; a redirect alone is not proof. If unavailable, generate `authorizeUrl` with an account display name, let the user complete OAuth, then check again. Refresh is handled by the backend; do not collect tokens, callback codes or secrets.
2. Authorized operations may be used independently. Do not force an existing order through the entire purchase sequence.
3. Use live SKU information and a user-selected address. Check selling units, minimum quantities and specifications before previewing. SKU prices and stock are indicative; the preview determines availability, freight and final totals.
4. Preview must explicitly succeed. `status=false` is a failure even with HTTP 200 or a successful platform envelope. Show its message and stop order creation.
5. Immediately before each of the five confirmed operations, restate the exact action and object in English and obtain separate explicit confirmation. An immediate “Confirm” response is sufficient after an unambiguous action summary; an earlier “continue” is not authorization for later actions. Set the corresponding JSON boolean internally only after confirmation, and pass it through to the API. Strings or numbers are not valid confirmation.
6. Create with the same address, items, quantities and flow that were previewed. Ordinary procurement defaults internally to `general`; do not ask users to select technical flow names.
7. Getting a payment link requires its own confirmation. Return the link for the user to open manually; do not open it or pay automatically.
8. Cancellation is not a refund. Check order state; do not use cancellation as a workaround for paid orders. Paid, shipped or completed orders require refund/after-sales handling on 1688. Do not repeat an already completed cancellation.
9. Confirm receipt only for the exact order after the user confirms actual receipt. Treat receipt and invoice application as irreversible.
10. Before invoicing, query `invoiceAmount`. Copy each eligible order's returned amount in cents unchanged into `invoiceApply`. Confirm the order, amount, invoice type and title; inspect every `successList` and `failedList` entry, including when top-level success is false. Treat `INVOICE_ALREADY_APPLIED` as already invoiced. Do not replay a mixed batch or request invoice reversal.
11. Never automatically retry ambiguous writes. Reconcile order/invoice state before considering another user-approved attempt. Do not substitute another store or buyer when authorization fails.

## Output and privacy

Responses up to 8 KB print sanitized JSON without saving. Larger responses save under `<workspace>/nexscope/<YYYY-MM-DD>/<session>/data/` and print a summary. Workspace priority is the first `ACPX_WORKSPACES` directory, current directory, then home; temporary directories are excluded. `--save` or `NEXSCOPE_SKILL_SAVE_RESPONSE=1` forces saving; `--no-save` or `NEXSCOPE_SKILL_NO_SAVE=1` prevents saving. `--inline` prints the complete sanitized output without implicitly saving. Extract saved fields as needed instead of loading the whole file.

Preserve nested business data, batch results, server billing headers and `_nexscope` diagnostics. Outer `cost` is elapsed time, not credits. A nonzero exit code does not imply that a write had no effect; inspect the result. Do not expose API keys, access/refresh tokens, session secrets or token expiry. Display enough address information to select safely, with masked phone numbers and minimal detail. Logs and saved files contain buyer data and must not be shared indiscriminately.

## Authentication and credits

Missing key or HTTP 401 means Nexscope authentication needs correction; HTTP 402 means insufficient credits. Use [Nexscope external access help](https://www.nexscope.ai/help/skills-external-access?co-from=skillNS). Marketplace authorization failure is distinct: use the 1688 authorization workflow, without changing buyer identity. Network errors, empty results or failed parameters do not authorize further paid calls.

Also check Nexscope's outer JSON `code`, even with HTTP 200: `11209` identifies a missing/nonexistent API key, `99001` a validation/configuration issue, `13007` an authorization or procurement service failure, `13011` insufficient Nexscope credits and `99000` an unexpected service failure. Use the message to distinguish authorization problems from other `13007` failures. Keep available trace IDs for support. Supplier business codes are nested results, not Nexscope outer codes; see the API reference before deciding how to recover.

## Boundaries

Image search, keyword search and rankings belong to the four discovery Skills. OAuth callbacks/token management are backend responsibilities and are not exposed here. No refund application, invoice reversal, backend database access or automatic full purchase loop is provided. Disabling MCP exposure alone does not disable an HTTP endpoint.

## User-facing language

Use English for all user-facing explanations, examples, confirmations, results and error guidance. Translate provider-localized product titles, descriptions and business messages into English for presentation. Preserve identifiers, monetary values, units, URLs and original source data in saved artifacts. Keep official buyer, recipient, address and invoice details unchanged in API payloads; do not translate legal names or address records just to change their display language.
