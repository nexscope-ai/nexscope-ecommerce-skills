---
name: ecommerce-amazon-reviews-list
description: "Fetch and analyze Amazon product reviews by ASIN, supporting 15 marketplaces (including US) with star rating filtering. Triggered when users mention Amazon reviews, US reviews, product reviews, buyer complaints, negative reviews, positive reviews, star ratings, review analysis, review sentiment, product improvement suggestions, Vine reviews, verified purchase reviews, competitor review research, Amazon reviews, US reviews, Amazon.com reviews, product feedback, negative review analysis, positive review analysis, star rating filter, review sentiment analysis, product improvement insights, Vine reviews, competitor reviews, customer feedback. Even if users do not explicitly say \"reviews\", this skill should be triggered whenever the task involves reading, filtering, or analyzing Amazon product customer reviews."
---

# Amazon Product Reviews

Fetch and analyze Amazon product reviews to help sellers extract actionable insights from customer feedback.

## Core Concepts

This tool retrieves real customer reviews for a given Amazon ASIN across **15 marketplaces**. You can control how many reviews to fetch per star rating (1-5 stars, up to 100 each), sort by recency or helpfulness, and apply various filters. Only one ASIN per request; for multiple ASINs, make separate calls.

## API Invocation

- **API Endpoint**: `POST /amazon/reviews/list` (see `references/api.md` for full parameters/responses/error codes)
- **Python Script**: `python scripts/amazon_reviews.py '<JSON params>' [--inline]`
- **Cost Constraints**: This tool consumes credits. The same parameter combination in the same session is only called once by default, with 24h local caching in the script. Failed or empty results should not trigger automatic retries with different keywords, pagination, or postal codes. Inform the user before making additional queries that will incur extra costs.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-amazon-reviews-list-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body less than or equal to 8 KB: print the full JSON to stdout after saving to disk
- Response body greater than 8 KB: after saving, stdout prints only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data Reading Tips**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Parameter Guide

| Parameter | Type | Required | Scope | Description | Default |
|-----------|------|----------|-------|-------------|---------|
| asin | string | Yes | All | Amazon product ASIN | - |
| star1Num | integer | No | Main endpoint | 1-star reviews to fetch (0-100) | 10 |
| star2Num | integer | No | Main endpoint | 2-star reviews to fetch (0-100) | 10 |
| star3Num | integer | No | Main endpoint | 3-star reviews to fetch (0-100) | 10 |
| star4Num | integer | No | Main endpoint | 4-star reviews to fetch (0-100) | 10 |
| star5Num | integer | No | Main endpoint | 5-star reviews to fetch (0-100) | 10 |
| sortBy | string | No | All | `recent` (newest) or `helpful` (most helpful) | `recent` |
| formatType | string | No | All | `all_formats` or `current_format` | `all_formats` |
| domainCode | string | No | Main endpoint | Marketplace code (see Supported Marketplaces); use `com` for US | `com` |
| filterByKeyword | string | No | Main endpoint | Filter reviews by keyword (max 1000 chars) | - |
| reviewerType | string | No | Main endpoint | `all_reviews` or `avp_only_reviews` (verified only) | `all_reviews` |
| mediaType | string | No | Main endpoint | `all_contents` or `media_reviews_only` | `all_contents` |

### Star Count Defaults

- If no star count fields are provided, `star1Num` to `star5Num` all default to `10`.
- If any star count field is provided, unspecified star counts default to `0`.

## Supported Marketplaces

| Marketplace | Code |
|-------------|------|
| United States | `com` |
| Canada | `ca` |
| United Kingdom | `co.uk` |
| Germany | `de` |
| France | `fr` |
| Italy | `it` |
| Spain | `es` |
| Japan | `co.jp` |
| India | `in` |
| Australia | `com.au` |
| Brazil | `com.br` |
| Mexico | `com.mx` |
| Netherlands | `nl` |
| Sweden | `se` |
| United Arab Emirates | `ae` |

Use `domainCode` for every supported marketplace. Always confirm the user's intended marketplace.

## Usage Examples

**1. Fetch US reviews (Amazon.com)**
```json
{"asin": "B08N5WRWNW", "domainCode": "com", "star1Num": 10, "star2Num": 10, "star3Num": 10, "star4Num": 10, "star5Num": 10, "sortBy": "recent"}
```

**2. Fetch negative reviews with keyword filter (Germany)**
```json
{"asin": "B08N5WRWNW", "domainCode": "de", "star1Num": 30, "star2Num": 30, "filterByKeyword": "quality", "reviewerType": "avp_only_reviews"}
```

**3. Fetch 5-star reviews with media (Japan)**
```json
{"asin": "B08N5WRWNW", "domainCode": "co.jp", "star5Num": 50, "star1Num": 0, "star2Num": 0, "star3Num": 0, "star4Num": 0, "sortBy": "helpful", "mediaType": "media_reviews_only"}
```

**4. Fetch only 3-star reviews (explicit star mode)**
```json
{"asin": "B0FP5C63HZ", "domainCode": "com", "star3Num": 100}
```

## Display Rules

1. **Present data clearly**: Show reviews grouped by star rating with key fields: rating, title, text, date, verified status, helpful count.
2. **Summarize when appropriate**: For many reviews, provide a theme/pain-point summary before listing individuals.
3. **Highlight actionable insights**: Call out recurring complaints in negative reviews; note praised features in positive reviews.
4. **Vine and verified labels**: Clearly indicate Vine Voice and verified purchase status.
5. **Media indicators**: Note when reviews include images or videos.
6. **Response normalization**: Normalize rating and helpful-count fields for consistent display when the raw response uses marketplace-specific text formats.
7. **Error handling**: When a query fails, explain the reason based on the response message and suggest adjusting parameters.
8. **Single ASIN limitation**: If the user asks about multiple ASINs, make separate requests for each.

## Important Limitations

- **One ASIN per request**: Only a single ASIN can be queried at a time.
- **Per-star cap**: Each star rating returns max 100 reviews per request.
- **Parameter scope**: `filterByKeyword`, `reviewerType`, `mediaType` are available on `/amazon/reviews/list`, including `domainCode: "com"`.
- **No historical snapshots**: Reviews are fetched in real-time.
- **Review text language**: Reviews are returned in their original language as posted.

## User Expression and Scenario Quick Reference

**Applicable** -- Tasks involving Amazon product reviews:

| User Says | Scenario |
|-----------|----------|
| "Show me the reviews for this ASIN" | Direct review lookup |
| "Get US reviews for B08N5WRWNW" | Marketplace-specific lookup |
| "What are customers complaining about" | Negative review analysis |
| "Get me all the 1-star reviews" | Star-filtered retrieval |
| "Any common issues in the bad reviews" | Pain point mining |
| "What do people like about this product" | Positive review analysis |
| "Find reviews mentioning battery" | Keyword-filtered reviews |
| "Show me reviews with photos" | Media-filtered reviews |
| "Verified purchase reviews only" | Reviewer-type filtering |
| "Help me analyze competitor reviews" | Competitor review research |
| "Product improvement suggestions from reviews" | Actionable insight extraction |

**Not applicable** -- Needs beyond product review data:

- ABA search term data / keyword research (use ABA Data Explorer instead)
- Sales estimation or revenue analysis
- Listing copywriting or A+ content creation
- Advertising / PPC strategy
- Pricing strategy or profit margin calculations

**Boundary judgment**: If "product research" or "competitor analysis" boils down to reading customer reviews for specific ASINs, this skill applies. If it involves search volume, keyword rankings, sales estimates, or market sizing, it does not.
