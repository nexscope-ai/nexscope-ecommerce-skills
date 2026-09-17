---
name: ecommerce.amazon-policy-feed
description: Query Amazon is latest policy, regulation, and compliance feed. Supports paginated browsing by marketplace and time range (with AI-generated Chinese summaries), and fetching full article body by record ID. Trigger when users mention Amazon policies & regulations, seller compliance announcements, platform rule changes, policy alerts, FBA/fee policy updates, multi-marketplace policy tracking, policy original text, news details, or similar terms. Even if the user does not explicitly mention "policy feed," trigger this skill whenever the request involves Amazon is officially published policies, regulations, and news for sellers, including their full text.
---

# Amazon Policy & Regulation Feed

This skill retrieves Amazon is latest **policy & regulation** feed for cross-border sellers. It is a two-step (list then detail) flow: first list feed items by site / time window, then fetch the full article body by its `id`.

## Core Concepts

- **Source**: Amazon official policy & regulation updates for sellers, curated by AI to surface items valuable to cross-border operations.
- **AI summary**: Each feed item includes a `summaryZh` field -- an AI-generated 1-3 sentence Chinese summary for quick scanning.
- **Two coupled tools**:
  1. `amazon/policyFeed` -- paginated **list**; returns structured records with title, AI summary, original URL, and publish time.
  2. `amazon/policyFeedDetail` -- full article **body** (Markdown) for a single record `id` obtained from the list.
- **Time range**: Defaults to the last 7 days; supports custom time windows via `publishedAtGte` / `publishedAtLte`.

## Parameters

### List (`amazon/policyFeed`)

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| site | string | No | Marketplace code (uppercase); site filtering only applies to some feed item types, others are always returned regardless of site | US |
| publishedAtGte | string | No | Publish/change time lower bound (incl.), `yyyy-MM-dd HH:mm:ss` | last 7 days |
| publishedAtLte | string | No | Publish/change time upper bound (incl.), `yyyy-MM-dd HH:mm:ss` | now |
| page | integer | No | Page number, starting at 1 | 1 |
| pageSize | integer | No | Items per page, 1-100 | 20 |

### Detail (`amazon/policyFeedDetail`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Record ID (32-char string) from the list response `data[].id` |

### Supported Marketplaces (for `site`)

US, JP, UK, AU, BE, BR, CA, EG, FR, DE, IN, IT, MX, NL, PL, SA, SG, ES, SE, TR, AE, ZA, IE. Default is **US** when not specified. Note: `site` filtering only applies to some feed item types; others are always returned regardless of site.

## API Invocation

- **API Endpoints**:
  - `POST /amazon/policyFeed` (`amazon_policy_feed.py`, full parameters/responses/error codes see `references/api.md`)
  - `POST /amazon/policyFeedDetail` (`amazon_policy_feed_detail.py`, full parameters/responses/error codes see `references/api.md`)
- **Python Script**: `python scripts/<script_name>.py '<JSON params>' [--inline]`
- **Cost Constraint**: This tool consumes credits; the same parameter combination is called only once per session by default, with a 24h local cache in the script. Do not automatically retry with different keywords, pagination, or zip codes after failures/empty results; inform the user about additional cost before continuing.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-amazon-policy-feed-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do NOT write to /tmp** -- error out if the current directory is not writable)
- Response body <= 8 KB: after writing to disk, print the full JSON to stdout
- Response body > 8 KB: after writing to disk, stdout outputs only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (while still writing to disk)

**Data Reading Tips**: First check the summary to see if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## How to Build Queries

1. **Set the time window**: convert user is time reference into `publishedAtGte` / `publishedAtLte`. Leave empty for the default last 7 days.
2. **Pick the marketplace**: map user is target country to the `site` code (default US). Note this only filters some feed item types.
3. **Paginate**: increase `page` to scan deeper; max 100 items per page.
4. **Drill into a record**: take a record is `id` from the list and call the detail script to read the full body.

### Usage Examples

**1. Recent feed (last 7 days, US)**
```json
{"site": "US", "pageSize": 20}
```
**2. Custom date range**
```json
{"site": "US", "publishedAtGte": "2026-05-01 00:00:00", "publishedAtLte": "2026-05-31 23:59:59"}
```
**3. Japan site feed, page 2**
```json
{"site": "JP", "page": 2, "pageSize": 50}
```
**4. Full body of one record**
```json
{"id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}
```

## Display Rules

1. **List view**: present results as a table with title, AI summary (`summaryZh`), publish time, and original URL link.
2. **Detail view**: render the `stdout` Markdown as-is; the response also includes `title` and `summaryZh` for context.
3. **Only present data**: report what the feed says; do not add subjective business advice or speculate on future policy.
4. **Timeliness note**: data may lag the live page by a short period; the Amazon original is authoritative.
5. **Error handling**: on a failed call, explain the reason from the error response (e.g. invalid `id` -> re-fetch from the list) instead of guessing.

## Important Limitations

- **Default window is 7 days**: without explicit time params, only the last 7 days are returned.
- **Max 100 items per page**: `pageSize` range is 1-100.
- **Detail needs a valid list `id`**: `amazon/policyFeedDetail` only accepts an `id` returned by `amazon/policyFeed`; unknown ids return an error.
- **Not for aggregation**: this skill is output is long-form text and metadata -- **not** suited for second-pass statistical/aggregation analysis via data query tools.

## User Expression & Scenario Quick Reference

**Applicable** -- Amazon official policy & regulation feed:

| User Says | Scenario |
|-----------|----------|
| "What are the latest Amazon policy changes?" | Recent policy feed overview |
| "Amazon US site policy news from the past week" | Site-filtered policy news |
| "What are the latest Amazon policy and regulation updates?" | General policy/regulation updates |
| "Amazon FBA latest policies and regulations" | Topic-specific policy lookup |
| "Show me the full text of this policy update" | Fetch full article body by id |
| "Amazon latest policy updates" | English trigger |

**Not applicable** -- beyond policy & regulation feed:
- Product / keyword / sales analytics, listing optimization, review analysis
- Real-time storefront search results or product detail
- Account-specific notifications inside an individual seller account
- Historical patent or trademark searches

**Boundary judgment**: if the user wants Amazon is **officially published policy, regulation, or compliance updates for sellers** (and its full text), this skill applies. If they want product/keyword/sales data, use the corresponding data skills.