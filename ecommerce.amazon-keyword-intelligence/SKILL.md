---
name: ecommerce.amazon-keyword-intelligence
description: Query and analyze Amazon ABA (Brand Analytics) search term data, covering 15 marketplaces with nearly 3 years of weekly data. Trigger when the user mentions ABA data, Amazon search term analysis, keyword mining, search ranking trends, market opportunity analysis, seasonal keywords, high-click low-conversion analysis, blue ocean keyword discovery, competitor keyword analysis, ABA data, search term report, keyword mining, search ranking trends, blue ocean keywords, click share, conversion share, seasonal keywords, market opportunity analysis, competitor keywords. Even if the user does not explicitly mention "ABA", if their need involves Amazon search term data and ranking analysis, this skill should also be triggered.
---

# ABA Data Explorer

This skill guides you on how to query and analyze ABA search term data, helping Amazon sellers extract valuable insights from ABA search term reports.

## Core Concepts

ABA (Amazon Brand Analytics) Search Term Report is official Amazon search behavior data that reflects real consumer search activity on Amazon. This tool holds nearly 3 years of **weekly-granularity** data across 15 Amazon marketplaces.

**Ranking logic**: A smaller `searchFrequencyRank` value means higher search popularity. Rank 1 is the most popular search term. This is an easy point of confusion - when a user says "ranking improved," it means the numeric value decreased; "ranking dropped" means the value increased.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Search Term | searchTerm | Consumer search keyword | rimel loreal |
| Report Start Date | reportStartDate | Week start date for data collection | 2025-10-26 |
| Region | region | Amazon marketplace code | US |
| Search Frequency Rank | searchFrequencyRank | Search popularity rank (lower = better) | 82135 |
| Clicked ASIN | clickedAsin | ASIN of the clicked product | B0XXXXXXXX |
| Clicked Item Name | clickedItemName | Name of the clicked product | xxx |
| Click Share Rank | clickShareRank | This ASIN's click share rank for the search term | 1 |
| Click Share | clickShare | Click share captured by this ASIN (0~1) | 0.28 |
| Conversion Share | conversionShare | Conversion share captured by this ASIN (0~1) | 0.3333 |

## Supported Marketplaces

US (United States), DE (Germany), BR (Brazil), CA (Canada), AU (Australia), JP (Japan), AE (United Arab Emirates), ES (Spain), FR (France), IT (Italy), SA (Saudi Arabia), TR (Turkey), MX (Mexico), SE (Sweden), NL (Netherlands)

Default marketplace is **US**. Use US when the user doesn't specify a marketplace.

## How to Invoke

- **API Endpoint**: `POST /aba/intelligentQuery` (complete params/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/aba_query.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits; the same session and parameter combination is called only once by default, with a 24h local cache in the script. On failure or empty results, do not automatically retry with different keywords, pagination, or postal codes; inform the user about additional consumption before continuing to search.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-aba-intelligent-query-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` is taken from the `SESSION_ID` env var, auto-grouped by user task; **do not write to /tmp**, error if current directory is not writable)
- Response body <= 8 KB: print full JSON to stdout after saving
- Response body > 8 KB: print only summary to stdout after saving (top-level fields, common counts like `total`/`costToken`, length of largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still saves to disk)

**Data reading tip**: Check the summary first to decide if it's enough; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved json file on demand, avoiding loading the entire JSON into context.

## How to Build Queries

The key parameter when calling this tool is `analysisDescription` - a natural language description of the data you want to query. This description is converted into a structured query on the backend, so it needs to be **precise and specific**.

### Principles for Writing analysisDescription

1. **Specify the marketplace**: Always state the marketplace at the beginning, e.g., "Filter US marketplace"
2. **Use precise filter criteria**: Use specific numeric ranges rather than vague descriptions. "Rank within 50,000" is far more effective than "good ranking"
3. **Specify time ranges**: Use concrete time descriptions, e.g., "past 12 weeks", "Jan-Sep 2024", "last 3 months"
4. **Specify comparison baselines**: For trend analysis, clearly state the time points being compared, e.g., "rank 4 weeks ago improved 30% vs 8 weeks ago"
5. **Handle deduplication logic**: When there are multiple records for the same search term + ASIN combination, specify which to keep, e.g., "keep only the latest for identical search term + ASIN"
6. **Stay faithful to user intent**: Don't misinterpret or overextend the user's query - reflect exactly what they want

### analysisDescription Examples for Common Scenarios

**1. Search Term Popularity Trend**
```
Filter US marketplace, keyword "gift" search popularity ranking over the past 12 weeks.
```

**2. Rising Dark Horse Keywords**
```
Filter US marketplace, keywords containing "gift", average search rank in Q1 2025 and full year both above 500,000, but latest rank breaks into 50,000-100,000 range.
```

**3. Sustained Growth Trend Discovery**
```
Filter US marketplace, latest rank within 200,000, and rank 4 weeks ago improved 30% vs 8 weeks ago, and this week's rank improved 30% vs 4 weeks ago.
```

**4. Market Opportunity Discovery (High Search Volume, Low Monopoly)**
```
Filter US marketplace, current search rank within 20,000, last 3 months click share of the Top 1 ASIN's conversion rate share below 5%. For identical search term and ASIN, keep only the latest record.
```

**5. Seasonal / Holiday Keyword Targeting**
```
Filter US marketplace, keywords containing "cup", from Jan-Sep last year (2024) rank did not enter top 500,000, but Oct-Nov consistently entered top 200,000.
```

**6. High-Click Low-Conversion ASIN Mining**
```
Filter US marketplace keywords containing "hat", latest search rank between 50,000-200,000, and last 3 months click share above 20%, conversion share below 10%. For identical search term and ASIN, keep only the record with the smallest ratio of click share to conversion share.
```

**7. High-ROAS Long-Tail Blue Ocean Keywords**
```
Filter US marketplace, keywords containing "charger", current rank outside top 200,000, last 2 months average conversion share above 1.5x the overall average conversion share, along with corresponding ASINs.
```

**8. New Market Terms & Emerging Demand Detection**
```
Find all long-tail keywords for "charger" on the US marketplace that only entered the ranking list in the last month and currently rank within 500,000.
```

**9. Niche Trend / Variant Growth Capture**
```
Filter US marketplace long-tail keywords for "table", rank between 100,000-300,000, and search ranking growth in the last 4 weeks above 50%.
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Volume notice**: When results are large, show core data and remind users they can get the full dataset via the download link
4. **Download guidance**: If the response includes a `downloadUrl`, clearly inform the user of the download address; if the user needs full data but hasn't requested a download, proactively suggest generating a download link
5. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria
## Important Limitations

- **Result cap**: Download links contain a maximum of 10,000 records
- **Data granularity**: Data is at weekly granularity, not daily
- **Data range**: Approximately 3 years of historical data

## User Expression & Scenario Quick Reference

**Applicable** - Data queries around Amazon search terms:

| User Says | Scenario |
|-----------|----------|
| "How's the search volume/popularity for XX keyword" | Ranking trend |
| "Recently trending keywords", "newly emerging terms" | Dark horse / new term detection |
| "Blue ocean keywords", "low competition terms" | Market opportunity discovery |
| "Which keywords convert well", "high-conversion long-tail" | High-ROAS keyword library |
| "Seasonal keywords", "what terms surge in peak season" | Seasonal keywords |
| "Who's capturing the traffic", "any monopoly" | Click share / monopoly analysis |
| "ASINs with high clicks but low conversion" | High-click low-conversion diagnosis |

**Not applicable** - Needs beyond ABA search term data:
- Advertising / PPC (bids, campaign strategy)
- Product reviews, listing copywriting
- ASIN sales estimation
- User already has local ABA files to process

**Boundary judgment**: When users say "product research", "competitor analysis", or "is there market opportunity", if it boils down to search-term-level data queries (finding blue ocean keywords, analyzing competitor traffic distribution under keywords), then this skill applies. If they're asking about profit margins, pricing strategy, or comprehensive market reports, it does not apply.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If credentials are missing or expire, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to top up credits.
