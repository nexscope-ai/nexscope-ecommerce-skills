---
name: ecommerce.amazon-keyword-expansion
description: Jungle Scout keyword expansion tool that expands a seed keyword into a list of related keywords with search volume, trends, PPC bids, ranking difficulty, and other metrics, covering 10 Amazon marketplaces including US, UK, DE, JP, etc. Trigger when the user mentions keyword expansion, keyword mining, long-tail keyword mining, related keywords, keyword suggestions, keyword discovery, PPC bid research, keyword competition, keyword discovery, Jungle Scout keywords, keyword expansion, keyword discovery, keyword scout, related keywords, long-tail keywords, keyword suggestions, PPC bid research, keyword competition, seed keyword expansion, keyword mining. Even if the user does not explicitly mention "Jungle Scout", if their need involves finding more related keywords and their search volume, competition, and other metrics starting from a seed keyword, this skill should also be triggered.
---

# Jungle Scout -- Keyword by Keyword Expansion

This skill expands a seed keyword into a list of related keywords with search volume, trends, PPC bids, ranking difficulty, and other competitive metrics via the Jungle Scout data source, covering 10 Amazon marketplaces.

## Core Concepts

The Jungle Scout Keyword by Keyword tool is one of the core tools for Amazon keyword research. Starting from a **seed keyword**, it mines a large number of related keywords and their competitive metrics. Main use cases include:

- **Keyword expansion/discovery**: Input a core keyword and get hundreds of related keywords to expand your listing keyword library
- **Long-tail keyword mining**: Use `minWordCount` to filter for 3+ word long-tail keywords, discovering low-competition, high-conversion opportunities
- **PPC bid research**: View exact/broad match PPC bids and brand ad bids to plan advertising budgets
- **Competition assessment**: Evaluate keyword ranking difficulty through `easeOfRankingScore` and `organicProductCount`
- **Trend analysis**: View monthly and quarterly trend percentage changes to identify growing keywords

## Data Fields

### Output Fields (keywordInfoList)

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Keyword | name | Keyword text | yoga mat thick |
| Marketplace | country | Market code | us |
| Exact Search Volume | monthlySearchVolumeExact | Monthly exact match search volume | 45000 |
| Broad Search Volume | monthlySearchVolumeBroad | Monthly broad match search volume | 120000 |
| Monthly Trend | monthlyTrend | Month-over-month search volume change percentage | 15.3 |
| Quarterly Trend | quarterlyTrend | Quarter-over-quarter search volume change percentage | -5.2 |
| Dominant Category | dominantCategory | Category with the highest share in search results | Sports & Outdoors |
| Relevancy Score | relevancyScore | Relevance score to the seed keyword | 856 |
| Ease of Ranking | easeOfRankingScore | Ranking ease score (higher = easier) | 3 |
| Organic Products | organicProductCount | Number of organic ranking products in search results | 342 |
| Sponsored Products | sponsoredProductCount | Number of ad products in search results | 28 |
| PPC Exact Bid | ppcBidExact | Exact match PPC suggested bid (USD) | 1.25 |
| PPC Broad Bid | ppcBidBroad | Broad match PPC suggested bid (USD) | 0.89 |
| Brand Ad Bid | spBrandAdBid | Sponsored Brand ad suggested bid (USD) | 2.50 |
| Recommended Promotions | recommendedPromotions | Recommended promotional giveaway count | 150 |
| Cost Token | costToken | Tokens consumed by this call | 1 |

## Supported Marketplaces

10 Amazon marketplaces: `us` (default), `uk`, `de`, `in`, `ca`, `fr`, `it`, `es`, `mx`, `jp`. When the user does not specify a marketplace, use `us`.

| Marketplace | marketplace value | Description |
|-------------|-------------------|-------------|
| United States | us | Amazon.com |
| United Kingdom | uk | Amazon.co.uk |
| Germany | de | Amazon.de |
| India | in | Amazon.in |
| Canada | ca | Amazon.ca |
| France | fr | Amazon.fr |
| Italy | it | Amazon.it |
| Spain | es | Amazon.es |
| Mexico | mx | Amazon.com.mx |
| Japan | jp | Amazon.co.jp |

## How to Invoke

- **API Endpoint**: `POST /tool-jungle-scout/keywords/by-keyword` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/amazon_keyword_expansion.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-junglescout-keyword-by-keyword-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

Required parameters: `marketplace`, `searchTerms` (single seed keyword string).

### Principles for Building API Calls

1. **Marketplace mapping**: "US marketplace" -> `us`, "Japan marketplace" -> `jp`, "Germany marketplace" -> `de`; default to `us` when unspecified
2. **Seed keyword**: Pass the user-provided keyword as-is (lowercase English preferred), only a single keyword is supported
3. **Result count**: Default return count is limited; if the user needs more results, set `needCount`
4. **Sort selection**: Default sort by exact search volume descending (`-monthly_search_volume_exact`); switch sort field based on user intent
5. **Filtering**: Make full use of `min/max` parameters to narrow results and avoid returning irrelevant low-quality keywords

### Common Query Scenarios

**1. Expand seed keyword -- get related keyword list**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat"
}
```

**2. Mine long-tail keywords (3+ words)**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minWordCount": 3,
  "needCount": 50
}
```

**3. Low-competition keyword discovery**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "maxOrganicProductCount": 200,
  "minMonthlySearchVolumeExact": 1000,
  "sort": "-ease_of_ranking_score"
}
```

**4. High search volume keyword filtering**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 10000,
  "sort": "-monthly_search_volume_exact",
  "needCount": 30
}
```

**5. PPC bid research -- sort by broad bid**
```json
{
  "marketplace": "us",
  "searchTerms": "yoga mat",
  "minMonthlySearchVolumeExact": 500,
  "sort": "ppc_bid_broad",
  "needCount": 30
}
```

**6. Germany marketplace broad search volume keywords**
```json
{
  "marketplace": "de",
  "searchTerms": "yogamatte",
  "minMonthlySearchVolumeBroad": 5000,
  "sort": "-monthly_search_volume_broad"
}
```

## Display Rules

1. **Table priority**: Display keyword lists in tables with core columns: Keyword, Exact Search Volume, Broad Search Volume, Monthly Trend, PPC Exact Bid, Ease of Ranking
2. **Contextual column trimming**: Choose columns based on user intent -- PPC research scenarios focus on bid columns, expansion scenarios focus on search volume and trends
3. **Trend annotation**: Mark positive monthly and quarterly trends with up arrow, negative with down arrow
4. **Ranking difficulty interpretation**: `easeOfRankingScore` 1-3 = difficult, 4-6 = medium, 7-10 = easy
5. **Data insights**: Provide a brief summary after the table, e.g., which category high-search-volume keywords concentrate in, competitive advantages of long-tail keywords
6. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters

## Important Limitations

- **One keyword per call**: `searchTerms` only accepts one seed keyword; multiple keywords require separate calls
- **Data period**: Search volume is a monthly estimated value, not real-time data
- **Marketplace limits**: Only covers 10 Amazon marketplaces, excluding Australia, Netherlands, etc.
- **Fixed sort fields**: Only supports predefined sort fields; custom combination sorting is not supported

## User Expression & Scenario Quick Reference

**Applicable** -- Keyword expansion and competition analysis:

| User Says | Scenario |
|-----------|----------|
| "Expand this keyword for me" | Seed keyword expansion |
| "What related keywords does this term have" | Related keyword mining |
| "Find some long-tail keywords" | Long-tail keyword filtering (minWordCount >= 3) |
| "Which keywords have low competition" | Low-competition keywords (ranking difficulty + product count filtering) |
| "What's the PPC bid for this keyword" | PPC bid data query |
| "Related keywords with high search volume" | High search volume keyword filtering |
| "What related keywords are there on the Germany marketplace" | Non-US marketplace keyword expansion |
| "Help me with keyword research" | Comprehensive keyword research |

**Not applicable** -- Beyond keyword expansion scope:
- Keyword historical search volume trends (requires the keyword-history tool)
- ABA search term rankings (requires the ABA tool)
- Product search or listing analysis
- Non-Amazon platform keyword data
- ASIN reverse keyword lookup

**Boundary judgment**: When users say "keywords", "keyword expansion", or "keyword research", if they want to expand a seed keyword into a list of related keywords with metrics, this skill applies. If they want to see a single keyword's historical search volume trend over time, use the keyword-history skill instead.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
