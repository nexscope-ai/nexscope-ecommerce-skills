# Workflow contract for `ecommerce.reverse-product-image-search-api`

## Objective

Find visual or keyword-derived competitors from a product image or URL across supported marketplaces.

## Domain procedure

1. Identify or confirm one target marketplace and site from the image or product URL.
2. Use image search for Amazon; for Walmart, TikTok, eBay, and Ozon, recognize product attributes first and search localized keywords.
3. Normalize competitor price, demand, rating, seller, category, and listing evidence into a comparable sourcing table.

## Inputs and dependencies

Gateway-backed steps require the approved NexScope proxy. Agent-guided steps may call other installed ecommerce skills named in the user's plan, but must not assume they are installed or authorized.

Use `references/api.json` to determine whether an operation is gateway-backed, agent-guided, or unavailable. Ask for missing identifiers only when they are required for the next operation.

## Deliverable contract

- State the scope, marketplace, time window, and user constraints.
- Separate retrieved facts, deterministic calculations, assumptions, and recommendations.
- Include artifact paths for large JSON, HTML, CSV, or spreadsheet-compatible results.
- Report unavailable sources and partial coverage explicitly.
