---
name: ecommerce.google-ai-mode-search
description: AI Overview (AI Mode) scraping via Google Search. Returns AI-summarized key points for a single keyword, ideal for deep research, technical Q&A, long-tail product selection, and cross-border consumer preference analysis using the latest web information. Single-round only; follow-ups require the agent to summarize context and issue a new request. Triggered by: Google AI, AI Overview, AI Mode, Google AI search, AI search, deep research, consumer preference analysis, web summary, long-tail product research, cross-border market insights.
---

# Google AI Search

This skill calls Google Search in AI Mode to get the AI Overview answer for a single keyword. Only one question per call is supported -- there is no multi-turn follow-up within a single request. The response is unstructured Markdown -- summarize it directly, do not route it to a data-analysis sandbox.

## Core Concepts

The tool drives Google's AI Mode (the panel that appears at the top of Google search results and synthesizes an answer with citations):

1. The required `keyword` is sent to Google as the query and the AI Overview for it is captured.
2. **Single-round only**: each call handles exactly one question. There is no `prompts` parameter for follow-ups.
3. **For follow-up questions**: the agent must summarize the previous AI Overview answer (key points, citations, relevant context) and concatenate it with the new question into a new `keyword`, then make a fresh API call.
4. All answers are returned as a single Markdown document under `stdout`, with citations linked to the source pages.

`resultsNum` reports how many AI Overview blocks were rendered; `0` means the keyword did not trigger an AI Overview on Google for the requested locale.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Google search keyword. Sent as the `q=` parameter to Google AI Mode. For follow-up questions, the agent should summarize the previous answer and concatenate with the new question into this field. |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| stdout | string | Markdown document with the AI Overview for the keyword, plus inline citation links |
| sourceUrl | string | The Google AI Mode search URL that was actually requested |
| resultsNum | integer | Number of AI Overview blocks rendered (0 = keyword did not trigger AI Overview) |
| code / errcode | string / integer | `200` on success; non-200 indicates a business error |
| msg / errmsg | string | `ok` on success; otherwise an error description |
| costTime | integer | API latency in milliseconds |
| costToken | integer | Tokens consumed (only billed on success) |
| taskId | string | Upstream task identifier for tracing |
| type | string | Render hint, fixed value `stdoutWorkbenches` |

## API Invocation

- **API Endpoint**: `POST /aiMode/googleSearch` (see `references/api.md` for full parameters, responses, and error codes)
- **Python Script**: `python scripts/google_ai_search.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same session + parameter combination is called only once by default; the script includes a 24-hour local cache. Do not automatically retry failed or empty results by changing keywords, paginating, or switching region codes. If further retrieval is needed, inform the user of the additional cost first.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-ai-mode-google-search-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouping by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body <= 8 KB: after saving to disk, print the full JSON to stdout
- Response body > 8 KB: after saving to disk, stdout prints a summary only (top-level fields, common counts like `total`/`costToken`, the length of the largest list field plus the first 3 sample items)
- Use `--inline` to force full output to stdout (also saves to disk)

**Data Reading Tips**: First check the summary to determine if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract on demand from the saved JSON file, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://os.nexscope.com/ to get an API Key or top up credits.

## How to Build Queries

Each call takes a single `keyword`. For follow-up questions, the agent must summarize the previous result and build a new query.

### Tips

1. **Front-load context in `keyword`**: include market/region cues when relevant (`"open-ear bone-conduction headphones US 2026"`) -- the AI Overview is sensitive to phrasing.
2. **Match the language to the target market**: ask in English for US/UK/AU markets, Japanese for JP, German for DE, etc. -- the AI Overview is biased toward the locale's language.
3. **Use natural-language questions**: phrasing like "compare against" / "what are the unsolved pain points" elicits richer AI Overview output than single keywords.
4. **For follow-ups, summarize and re-ask**: when the user wants to dig deeper, the agent should summarize key points from the previous AI Overview response and concatenate with the new question into a new `keyword` for a fresh call. Example: `"Based on the AI overview that top bone-conduction headphones are Shokz OpenRun Pro and AfterShokz Aeropex, what are the unsolved technical pain points compared to in-ear earbuds?"`

### Usage Examples

**1. Single-shot AI Overview**

```json
{
  "keyword": "GaN charger vs traditional charger comparison"
}
```

**2. Cross-border product research**
```json
{
  "keyword": "best open-ear bone conduction headphones 2026 US"
}
```

**3. Follow-up question (agent summarizes prior result and re-asks in a new call)**

First call:
```json
{
  "keyword": "best open-ear bone conduction headphones 2026 US"
}
```

Second call (agent builds context summary + new question):
```json
{
  "keyword": "The AI overview mentioned OpenRun Pro and AfterShokz Aeropex as top picks for bone conduction headphones. What unsolved technical pain points still exist compared to in-ear earbuds?"
}
```

**4. Consumer preference snapshot**
```json
{
  "keyword": "robot vacuum buying preferences 2026 reddit"
}
```

**5. Long-tail keyword exploration for selection**
```json
{
  "keyword": "smart pet feeder for cats with camera"
}
```

## Display Rules

1. **Render the Markdown directly**: `stdout` is already structured Markdown with headings, bullets, and citation links -- preserve that structure when answering the user.
2. **Cite sources**: keep the inline reference links from `stdout` so the user can verify each claim.
3. **Flag empty AI Overview**: if `resultsNum` is `0`, tell the user Google AI Overview did not trigger for that keyword and suggest rephrasing or trying a different region.
4. **Don't reroute to a data-analysis sandbox**: the output is unstructured text and not suitable for SQL-like processing.
5. **Indicate freshness**: results reflect Google AI Mode at call time; mention this when the user asks about recency.
6. **Handle business errors**: if `code` / `errcode` is not `200`, surface the `msg` / `errmsg` to the user and suggest retrying or refining the input.

## Important Limitations

- **Unstructured output**: Markdown text only -- no structured tables, no second-pass data query.
- **AI Overview not guaranteed**: some keywords (especially niche, ambiguous, or sensitive ones) do not trigger AI Overview at all (`resultsNum = 0`).
- **Single-round only**: no multi-turn follow-up within one call. For follow-ups, the agent must summarize previous context and make a new call.
- **Locale follows Google's defaults**: the tool uses Google's standard AI Mode endpoint without an explicit region switch; bias the language and wording of `keyword` to match the market you care about.
- **Real-time fetch**: results are pulled live, so output for the same keyword can vary across calls.

## User Expression & Scenario Quick Reference

**Applicable** -- when the user wants AI-summarized live web information:

| User Says | Scenario |
|-----------|----------|
| "Search with Google AI for...", "Google AI Overview for..." | Direct AI Overview lookup |
| "What do overseas consumers think about XX", "US market preference for XX" | Cross-border consumer preference |
| "Latest trends / pain points / use cases for XX" | Deep research |
| "By the way / follow up on..." | Follow-up needed (agent summarizes prior result and re-asks in new call) |
| "Web summary of XX", "What are people saying on search engines about XX" | Web-wide summarization |
| "Long-tail product research / blue ocean product direction" | Long-tail product exploration |

**Not applicable** -- better routed elsewhere:

- Querying internal structured datasets (use the appropriate data query tool).
- Amazon ABA search-term analytics (use the ABA data explorer).
- Pulling structured product listings, prices, reviews from a specific platform (use the matching platform skill).
- Plain web search where the user only needs raw page content with no AI synthesis (use the standard web search skill).
- Image generation, image recognition, or file analysis.

**Boundary judgment**: when the user wants "AI to summarize what's being said online" or "search on Google", this skill applies. If the user wants to ask follow-up questions, the agent should summarize the previous answer and make a new call. If they explicitly want raw search results, structured data, or already have a specialized data source, do not use this skill.
