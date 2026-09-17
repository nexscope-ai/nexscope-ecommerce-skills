---
name: ecommerce.amazon-opportunity-search-by-metrics
description: Amazon reverse product selection: filter Amazon niches and keywords by 30+ business dimensions (market size & growth, price tiers & share, competition density & top concentration, demographics such as age/gender/income, review highlights & pain points) from a metrics pool aggregated from historical business insight reports. Trigger when users mention reverse product selection, metrics filtering, niche reverse lookup, blue ocean niche discovery, low-competition niche, newcomer-friendly niche, brand-fragmented market, pain-point entry, feature reverse lookup, pricing tier opportunity, demographic-based selection, or similar terms. Even if the user does not explicitly say "reverse product selection," trigger this skill whenever the request involves filtering Amazon niches that match specific business criteria.
---

# Amazon Opportunity Screener by Metrics

This skill guides you on how to reverse-search Amazon niches and keywords from a metrics pool aggregated from historical opportunity reports, helping sellers turn vague selection ideas (low competition, growing demand, blue ocean, pain-point opportunity, etc.) into concrete niche candidates.

## Core Concepts

This tool exposes a queryable pool of **niche-level metrics** (~37 fields per record) distilled from past Amazon opportunity reports. Instead of generating a fresh report (forward analysis), it lets you **reverse-filter** the existing pool by 30+ business dimensions and returns matching `(marketplace, keyword)` records ranked by collection time (most recent first).

Records are at the **niche / keyword** level, not ASIN level. Each record represents a niche snapshot -- its market size, growth, competition, price tiers, demographics, top features, and review themes.

**Forward vs. reverse**: Use `nexscope-amazon-opportunity-report` when the user has a keyword and wants a comprehensive AI report. Use this skill when the user has business criteria (filters) and wants to discover which keywords / niches fit.

## Filter Dimensions

Filters are grouped into six business dimensions. All filter parameters are optional, but **at least one of `keyword` / `nicheName` or any metric filter must be provided** -- fully empty calls are rejected.

| Dimension | Example Parameters | Typical User Intent |
|-----------|---------------------|---------------------|
| Market size & growth | `nicheRevenue360dMinUsdAtLeastGte`, `nichePeakSearchVolumeAtLeastGte`, `nicheSearchVolumeYoyChangePctAtLeastGte`, `nichePeakMonthGte/Lte` | "Big enough market", "fast-growing", "Q4 seasonal" |
| Competition density | `nicheBrandCountLte`, `nicheBrandCountYoyChangePctAtLeastLte`, `nicheTop5ProductClickSharePctAtLeastLte`, `featureTop5BrandSharePctAtLeastLte` | "Newcomer-friendly", "brands fragmented", "no oligopoly", "brands exiting" |
| Price & tier | `priceMinUsdGte`, `priceMaxUsdLte`, `priceSweetSpotMinUsdGte/Lte`, `priceEntryClickSharePctAtLeastGte`, `priceMidClickSharePctAtLeastLte`, `priceHighClickSharePctAtLeastGte` | "Affordable focus", "premium-friendly", "mid-tier blue ocean" |
| Demographics | `demoPrimaryAgeMinGte`, `demoPrimaryAgeMaxLte`, `demoGenderDominant`, `demoPrimaryIncomeTier`, `demoLifeStageTagsContains` | "Female-driven", "high-income", "parents", "fitness enthusiasts" |
| Product features | `featureNewAvgReviewCountAtLeastLte`, `featureEstablishedAvgReviewCountAtLeastLte`, `featureEmergingTrendTagsContains`, `featureUncommonFeatureTagsContains`, `searchTopCategory1Label` | "New-product entry barrier low", "emerging trend", "uncommon feature edge", "set/kit niches" |
| Review insights | `reviewPositiveTop1Topic`, `reviewPositiveTop1PctAtLeastGte/Lte`, `reviewNegativeTop1Topic`, `reviewNegativeTop1PctAtLeastGte/Lte`, `reviewNegativeTop2Topic`, `reviewStrategicInsightTagsContains` | "Pain-point niche", "comfort-driven sellers", "size-issue opportunity" |

See `references/api.md` for the full parameter list, types, value ranges, and response field map.

## Supported Marketplaces

Currently only **US** (United States) is supported. Always set `amazonDomain` to `US` (or omit). If a user requests other marketplaces, inform them this tool currently only covers the US market.

## API Invocation

- **API Endpoint**: `POST /amazon/opportunity/searchByMetrics` (full parameters/responses/error codes see `references/api.md`)
- **Python Script**: `python scripts/amazon_opportunity_screener.py '<JSON params>' [--inline]`
- **Cost Constraint**: This tool consumes credits; the same parameter combination is called only once per session by default, with a 24h local cache in the script. Do not automatically retry with different keywords, pagination, or zip codes after failures/empty results; inform the user about additional cost before continuing.

**Output Strategy (default script behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-amazon-opportunity-search-by-metrics-<timestamp>.json` (`<cwd>` is the working directory at script execution time, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, auto-grouped by user task; **do NOT write to /tmp** -- error out if the current directory is not writable)
- Response body <= 8 KB: after writing to disk, print the full JSON to stdout
- Response body > 8 KB: after writing to disk, stdout outputs only a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (while still writing to disk)

**Data Reading Tips**: First check the summary to see if it is sufficient; when specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## How to Build Queries

The user expresses business intent in natural language; you map it to **the smallest viable set of filters**. Principles:

1. **Convert intent into specific bounds**: "low competition" -> `nicheBrandCountLte: 20`; "fast-growing" -> `nicheSearchVolumeYoyChangePctAtLeastGte: 100` (>=100% YoY); "newcomer-friendly" -> `featureNewAvgReviewCountAtLeastLte: 500`.
2. **Start narrow, then loosen**: First call usually with 2-4 strong filters and `limit=25`. If the result set is empty or too small, drop or widen the most aggressive filter rather than adding new ones.
3. **Pair complementary signals**: Brand-level + product-level concentration (`featureTop5BrandSharePctAtLeastLte` + `nicheTop5ProductClickSharePctAtLeastGte`) reveals "brands fragmented but products concentrated" -- a brand-extension entry signal.
4. **Snake_case fragments for tag fields**: `featureEmergingTrendTagsContains`, `demoLifeStageTagsContains`, `reviewNegativeTop1Topic`, etc. accept snake_case word fragments and use LIKE matching. Pass a root word (`size`, `parent`, `cordless`) to cover normalized variants.
5. **Faithful to user intent**: Do not silently add filters the user did not ask for. If they only said "growing", just filter on growth -- do not also constrain price unless they mentioned it.

### Common Scenarios

**1. Niche reverse-lookup by keyword**
```json
{"keyword": "whoop band", "limit": 25}
```

**2. Newcomer-friendly low-competition niches**
```json
{"nicheBrandCountLte": 20, "featureNewAvgReviewCountAtLeastLte": 500, "limit": 25}
```

**3. High-growth blue ocean (>=100% YoY, brands not yet flooding in)**
```json
{"nicheSearchVolumeYoyChangePctAtLeastGte": 100, "nicheBrandCountYoyChangePctAtLeastLte": 30, "limit": 25}
```

**4. Mid-tier price gap (low-price dominates, mid-tier scarce)**
```json
{"priceEntryClickSharePctAtLeastGte": 70, "priceMidClickSharePctAtLeastLte": 5, "limit": 25}
```

**5. Pain-point entry -- strong size complaints**
```json
{"reviewNegativeTop1Topic": "size", "reviewNegativeTop1PctAtLeastGte": 70, "limit": 25}
```

**6. Premium-friendly female-driven niches**
```json
{"demoGenderDominant": "female", "demoPrimaryIncomeTier": "high", "priceHighClickSharePctAtLeastGte": 25, "limit": 25}
```

**7. Q4 seasonal niches with >=100k peak search**
```json
{"nichePeakMonthGte": 11, "nichePeakMonthLte": 12, "nichePeakSearchVolumeAtLeastGte": 100000, "limit": 25}
```

**8. Track niches around a known competitor brand**
```json
{"featureTopBrandsContains": "WHOOP", "limit": 50}
```

## Display Rules

1. **Present data only**: Render the returned niches as a clean comparison table -- niche name / keyword, market size, growth, brand count, price range, key tags. No subjective business advice.
2. **Surface the active filters**: Echo the filter set you used so the user can adjust (e.g., "Current filters: brand count <= 20 AND search volume YoY >= 100%").
3. **Time-snapshot reminder**: Records reflect data at collection time and are not continuously updated. Mention this when results look stale or contradict a user's external knowledge.
4. **Empty / few-result handling**: If `data` is empty or very short, suggest widening the most aggressive filter rather than re-asking the user from scratch.
5. **Error handling**: When a query fails, explain the reason based on the `msg` field (most often the "fully empty parameters" guard) and suggest adding at least one filter.
6. **No secondary aggregation**: The results power frontend rendering and are not stored, so they cannot be fed into data query tools for further aggregation. If users ask for grouped statistics across niches, do the calculation locally or pull a wider `limit` first.

## Important Limitations

- **US only**: Currently only supports the United States marketplace (`amazonDomain` = `US`).
- **No pagination**: There is no `page` parameter. Increase `limit` (max 200) to widen the candidate pool; results are sorted by collection time (newest first).
- **At least one filter required**: Calls with no `keyword` / `nicheName` and no metric filter are rejected.
- **Snapshot data**: Records are aggregated from historical opportunity reports; new reports refresh the pool over time, but individual records are not real-time.
- **Niche-level granularity**: The output is niche / keyword level, not ASIN level. To dig into specific products inside a niche, hand off to `nexscope-amazon-search`, `nexscope-keepa-product-search`, etc.

## User Expression & Scenario Quick Reference

**Applicable** -- Niche-level reverse selection on the US Amazon market:

| User Says | Scenario |
|-----------|----------|
| "Low-competition niches", "newcomer-friendly", "brand-light" | Brand-density filter |
| "Brands are exiting", "old players retreating" | Negative brand-count YoY |
| "Fast-growing niche", "trending up", ">=100% YoY" | Search-volume YoY filter |
| "Mid-tier blue ocean", "low-price dominates but mid is scarce" | Price-tier share gap |
| "Premium-friendly", "high-income consumers" | Income tier + high-tier share |
| "Female / male / mixed market" | Gender dominance filter |
| "Parents / students / retirees / fitness enthusiasts" | Life-stage tag |
| "Strong size / quality / durability pain point" | Negative review topic + share |
| "Comfort-driven", "value-driven sellers" | Positive review topic + share |
| "Track all niches around brand X" | `featureTopBrandsContains` |
| "Q4 seasonal niches", "Prime Day window" | Peak month + peak volume |

**Not applicable** -- Use other tools instead:
- Need a comprehensive AI report on one keyword -> `nexscope-amazon-opportunity-report`
- ASIN-level competitor research, sales estimation -> SellerSprite / Keepa / Sorftime tools
- Real-time keyword ranking, search-term mining -> ABA / SIF tools
- Marketplaces other than US -> not yet supported by this tool
- Want to run group-by aggregation over niches via data query tools -> unsupported (data is not warehoused)

**Boundary judgment**: When users describe selection criteria in business language and want matching candidate niches, this skill applies. When they hand you a specific keyword and want the full multi-dimensional analysis, use `nexscope-amazon-opportunity-report`. When they want to drill into ASINs / sellers within a niche, hand off to product-search tools.