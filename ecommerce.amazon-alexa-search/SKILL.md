---
name: ecommerce.amazon-alexa-search
description: Initiate natural language Q&A through Amazon's storefront Alexa shopping assistant to get shopping guidance answers, recommended product groups, ASIN lists, and follow-up questions. Each call supports only 1 prompt; for follow-ups, the agent must summarize context and concatenate a new question for a new request. A url can be used to supplement Amazon page context. Trigger when the user mentions Amazon Alexa, Alexa shopping assistant, Amazon smart assistant, AI shopping guide, conversational product selection, natural language shopping, Amazon chat Q&A, Amazon Alexa shopping, conversational shopping, AI shopping assistant, follow-up questions, product recommendation conversation, context follow-ups. Even if the user does not explicitly mention "Alexa", if their need is to "ask for product recommendations on Amazon using natural language", this skill should also be triggered.
---

# Amazon Alexa Shopping Assistant

This skill drives Amazon's storefront Alexa shopping assistant: pose a natural-language question and get an answer, a curated product list (with ASINs and links), and a set of follow-up questions Alexa is willing to continue with. Each call supports only one prompt. For multi-turn conversations, the agent must summarize prior context and concatenate it with the new question in a fresh call.

## Core Concepts

1. **Single-turn per call**: `prompts` is an array but only supports **1 element**. Each API call sends exactly one question to Alexa and returns one answer. Do not pass multiple elements.
2. **Cross-call context is not preserved**: every call starts a brand-new Alexa session. To ask follow-up questions, the agent must summarize the previous answer (key recommendations, ASINs, relevant context) and concatenate it with the new question as `prompts[0]` in a new call.
3. **Optional page context (`url`)**: pass an Amazon page URL only when you want the conversation anchored to a **specific** page (a category page, search results page, or product detail page). Do **not** pass a plain marketplace homepage URL like `https://www.amazon.com/` -- it adds no useful context. Omit `url` entirely when there is no specific page to anchor on.
4. **Two output formats**:
   - `markdown` (default) -- a single readable Markdown report containing the question, Alexa's answer, recommended product groups, and follow-up questions.
   - `json` -- a structured array under `data`, where each entry carries `prompt`, `content`, `products` (grouped recommendations), `followUpQuestions`, and `screenshot`.

`resultsNum` is the number of conversation turns Alexa actually answered; if `0`, Alexa did not produce a usable reply for the input.

## Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| prompts | string[] | Yes | Conversation prompts. Only **1 element** is allowed per call. To ask follow-up questions, make a new call with context summary + new question as `prompts[0]`. | - |
| format | string | No | Response format: `markdown` returns a readable report; `json` returns a structured array. | markdown |
| url | string | No | Specific Amazon page URL (category, search results, or product detail) to anchor the conversation. Skip when there is no specific page; do **not** pass a plain homepage URL such as `https://www.amazon.com/`. | - |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| stdout | string | Markdown report when `format=markdown`: per-turn question, Alexa answer, recommended product groups, follow-up questions |
| data | array | Structured turns when `format=json`. Each item has `prompt`, `content`, `products[]`, `followUpQuestions[]`, `screenshot` |
| resultsNum | integer | Number of answered turns (0 = Alexa did not respond) |
| code / errcode | string / integer | `200` on success; non-200 indicates a business error |
| msg / errmsg | string | `ok` on success; otherwise an error description |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Tokens consumed (only billed on success) |
| taskId | string | Upstream task identifier for tracing |
| type | string | Render hint: `stdoutWorkbenches` for markdown, `json` for json |

### Structured `data[*]` shape (`format=json`)

| Field | Type | Description |
|-------|------|-------------|
| prompt | string | The question or follow-up sent for this turn |
| content | string | Alexa's natural-language answer |
| products[].title | string | Group title (e.g. "Top picks", "Best for running") |
| products[].items[].asin | string | Product ASIN |
| products[].items[].title | string | Product title |
| products[].items[].url | string | Product detail page URL |
| products[].items[].cover | string | Product cover image URL |
| products[].items[].price | string | Current price string (with currency) |
| products[].items[].originalPrice | string | List price / strikethrough price |
| products[].items[].score | string | Star rating |
| products[].items[].ratingsCount | string | Review count |
| products[].items[].describe | string | Short product blurb |
| followUpQuestions | string[] | Questions Alexa offers to continue with |
| screenshot | string | Screenshot URL for this turn |

## How to Invoke

- **API Endpoint**: `POST /amazon/alexaSearch` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_alexa_search.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-amazon-alexa-search-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

1. **Front-load the user's intent in `prompts[0]`** -- include marketplace cue ("on Amazon US"), use case, and any hard constraints (budget, key feature). Alexa weights the opening question heavily.
2. **One question per call** -- `prompts` only accepts 1 element. Do not pass multiple elements.
3. **For follow-ups, summarize and re-ask** -- when the user wants to continue the conversation, the agent must: (a) summarize the key points from the previous Alexa response (answer highlights, recommended ASINs, relevant context); (b) concatenate the summary with the new question; (c) send as `prompts[0]` in a new API call. Alexa has no memory of prior calls.
4. **Anchor with `url` only when there's a specific page** -- pass a category, search results, or product detail URL when the user is reasoning over that page. Skip `url` for general questions; do not pass a plain homepage like `https://www.amazon.com/`.
5. **Pick `format` deliberately** -- `markdown` is best for showing the user a polished answer; `json` is better when downstream code needs to extract ASINs, prices, or follow-up questions programmatically.

### Usage Examples

**1. Single-turn shopping question**

```json
{
  "prompts": ["best wireless earbuds for running on Amazon US under $100"]
}
```

**2. Follow-up question (agent summarizes prior context and re-asks)**

First call:
```json
{
  "prompts": ["best electric kettle on Amazon US"]
}
```

Second call (agent summarizes the previous answer and appends the follow-up):
```json
{
  "prompts": ["Previously Alexa recommended: 1) Cosori Electric Kettle (B07T1KY5TZ, $35.99, 4.7 star), 2) Mueller Ultra Kettle (B09KC7D3HR, $29.97, 4.5 star). Now compare these two on noise level and boil time."]
}
```

**3. Question anchored to a category page**

```json
{
  "prompts": ["What are the most popular picks on this page?"],
  "url": "https://www.amazon.com/s?k=electric+kettle"
}
```

**4. Structured output for downstream extraction**

```json
{
  "prompts": ["best gift ideas for a 10-year-old who likes science"],
  "format": "json"
}
```

## Display Rules

1. **Render the Markdown directly** when `format=markdown`: `stdout` is already structured with turn headings, product cards, and follow-up questions -- preserve that structure.
2. **Surface the recommended ASINs** so the user can click through; show `title`, `price`, `score`/`ratingsCount`, and the product URL.
3. **Show the follow-up questions** Alexa returned -- they are usable prompts the user can pick to continue digging. When the user picks one, summarize the current answer and use the selected follow-up as `prompts[0]` in a new call.
4. **Don't reroute to a data-analysis sandbox**: the answer body is conversational and the recommended products are nested groups, not a flat tabular dataset suitable for SQL-like aggregation.
5. **Flag empty results**: if `resultsNum` is `0` or `data` is empty, tell the user Alexa did not produce a usable reply and suggest rephrasing or anchoring with a `url`.
6. **Indicate freshness**: results reflect Alexa's live answer at call time; mention this when the user asks about timing.
7. **Handle business errors**: if `code` / `errcode` is not `200`, surface `msg` / `errmsg` and suggest retrying with simpler prompts.

## Important Limitations

- **Alexa-driven, not deterministic**: same prompts can yield different answers across calls -- Alexa's response varies with time, traffic, and context.
- **No cross-call memory**: each tool call is a fresh Alexa session; the agent must summarize prior context and embed it in the new question.
- **One prompt per call**: `prompts` only accepts 1 element. For follow-ups, the agent must summarize context + new question into a single `prompts[0]` and make a new call.
- **Marketplace coverage**: anchored on Amazon's storefront Alexa experience (primarily amazon.com); availability on non-US marketplaces depends on Alexa rollout.
- **Output mix**: primary value is the conversational answer plus a curated handful of products; this is not a substitute for SERP-wide product extraction.

## User Expression & Scenario Quick Reference

**Applicable** -- natural-language conversational shopping on Amazon:

| User Says | Scenario |
|-----------|----------|
| "Use Alexa to recommend...", "Ask Amazon Alexa..." | Direct Alexa Q&A |
| "Chat to find product recommendations on Amazon...", "Conversational product selection" | Conversational discovery |
| "Also ask a follow-up / continue asking..." | Follow-up (agent summarizes prior result and re-asks in new call) |
| "Recommend from this page / this category...", "Ask again based on this page" | Page-anchored conversation (use `url`) |
| "best XX for YY under $Z on Amazon" | Goal + constraint + budget Q&A |
| "Compare the first two recommendations from Alexa" | Compare within Alexa's reply |
| "What else can Alexa ask / give me some follow-up ideas" | Surface follow-up questions |

**Not applicable** -- better routed elsewhere:

- Pulling the full SERP for a keyword with positions, sponsored flags, etc. (use the storefront search-simulation skill).
- Historical search-term analytics or volume trends (use the ABA data explorer).
- Detailed product detail / A+ / bullets for a known ASIN (use the Amazon product detail skill).
- Review-level sentiment analysis (use the Amazon reviews skill).
- Image-based similar product discovery (use the image search skill).
- Aggregated statistics over a flat product list (no structured table here).

**Boundary judgment**: when the user wants a **conversation** -- "ask Amazon, get a recommendation, then keep asking" -- this skill applies. If they want raw search-result rows, structured analytics, or a specific ASIN's data, route to the matching specialized skill instead.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://os.nexscope.com/ to top up credits.
