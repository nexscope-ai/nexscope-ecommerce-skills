---
name: ecommerce.ozon-product-trend
description: MPSTATS Ozon Russia single SKU daily time-series performance. Returns daily sales units, price, stock, rating, and optionally search position/visibility data for one Ozon product by date granularity. Use for validating growth trends, seasonality, and anomaly detection. Trigger when the user mentions Ozon trend, Ozon sales trend, Ozon price trend, Ozon daily data, Ozon stock trend, Ozon search ranking, Ozon product history, MPSTATS trend, Ozon daily performance, Ozon time series, Ozon search visibility, Russian marketplace product history. Also trigger when the intent is to view the daily/period trend of an Ozon product, even without explicitly mentioning MPSTATS.
---

# MPSTATS Ozon Product Trend (Daily Time-Series)

This skill returns a daily time-series of a single Ozon (Russia) SKU — sales units, price, stock, rating, and optionally search-position / visibility metrics. It is the go-to for validating growth, seasonality, or anomalies for a specific product.

## Core Concepts

**Single-SKU scope**: Each call analyzes exactly **one** `productId`. For batch per-SKU snapshots (period aggregates), use `ecommerce.ozon-product-detail` instead.

**Daily granularity**: The response is an array of daily points (top-level field `data`) across the `[startDate, endDate]` window. Each point carries a `hasData` boolean — if `hasData=false`, the day has no observation (distinct from `sales=0` with `hasData=true`).

**T-1 delay**: MPSTATS trend data is delayed by one day; the latest selectable end date is **yesterday**. Today or future dates are rejected.

**Search-visibility add-on**: Set `includeSearchStats: true` to append search-position / visibility signals. Some niches (especially small categories) may not have search-stats coverage — expect partial or empty fields in those cases.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| productId | integer | yes | Ozon SKU (numeric) |
| startDate | string | no | Window start, `YYYY-MM-DD`; latest = yesterday |
| endDate | string | no | Window end, `YYYY-MM-DD`; latest = yesterday |
| includeFbs | boolean | no | Include FBS data alongside FBO |
| includeSearchStats | boolean | no | Attach search position / visibility signals |

## Calling the Tool

- **API Endpoint**: `/mpstats/ozon/productTrend` (full parameters/responses/error codes in `references/api.md`)
- **Python Script**: `python scripts/ozon_product_trend.py '<JSON params>' [--inline]`
- **Cost constraint**: This tool consumes credits. Within the same session and same parameter combination, it defaults to a single call with a 24-hour local cache. Do not automatically retry with different keywords, pagination, or parameters on failure/empty results. Inform the user of additional credit consumption before continuing retrieval.

**Output strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.ozon-product-trend-<timestamp>.json` (`<cwd>` is the working directory when the script executes, which in Claude Code is the current project directory; `<session>` is taken from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**; error if the current directory is not writable)
- Response body <= 8 KB: write to disk then print full JSON to stdout
- Response body > 8 KB: write to disk then print only a summary to stdout (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Reading data**: Check the summary first to determine if it is sufficient. When specific fields are needed, use `jq` or `ConvertFrom-Json` to extract from the saved JSON file as needed, avoiding loading the entire JSON into context.
## Authentication & Credits

If you encounter authentication or credit issues:

### Error conditions
- **API Key not configured**: The `NEXSCOPE_API_KEY` environment variable is not set.
- **HTTP 401 or 402 status code**
- **Insufficient credits/balance**: Response message indicates credit balance exhausted, quota exceeded, subscription expired, or recharge required.

### Resolution steps
1. Set the `NEXSCOPE_API_KEY` environment variable with a valid API key.
2. If credits are insufficient, visit https://os.nexscope.com/ to top up your balance.
3. For onboarding and setup guidance, refer to https://skill.nexscope.com/nexscopeskills/guide.htm
## Usage Examples

**1. Monthly trend for a SKU**
```json
{
  "productId": 1786874757,
  "startDate": "2025-03-01",
  "endDate": "2025-03-31"
}
```

**2. Trend with search visibility**
```json
{
  "productId": 1786874757,
  "startDate": "2025-02-01",
  "endDate": "2025-02-28",
  "includeSearchStats": true
}
```

**3. Combined FBO+FBS trend**
```json
{
  "productId": 151623766,
  "startDate": "2025-01-01",
  "endDate": "2025-01-31",
  "includeFbs": true
}
```

## How to Chain with Other Ozon Skills

1. **Discovery → trend**: Use `ecommerce.ozon-product-search` to find a SKU, then check growth / volatility here before committing.
2. **Aggregate vs time-series**: `ecommerce.ozon-product-detail` gives a one-number-per-metric period view; this skill shows the day-by-day shape behind those numbers.
3. **Drill-down → trend**: After `brand-products` / `category-products` / `seller-products` surfaces a hot SKU, use this skill to validate whether the hotness is recent, seasonal, or sustained.

## Display Rules

1. **Prefer a simple table or sparkline-friendly output** — one row per date with `date`, `price`, `sales`, `balance`, `rating`, `comments`; do not overfit a 90-point series into a single paragraph.
2. **Use `hasData` to distinguish gaps from zero sales** — `hasData=false` means the day has no observation; don't report it as a zero-sale day.
3. **Call out anomalies** — large single-day spikes or stockouts (`balance=0` runs where `hasData=true`) should be flagged factually, not as buying advice.
4. **Currency is RUB** unless upstream layer is already converting (the `currency` field per point carries the symbol, e.g. `₽`); state the currency when showing price movement.
5. **Revenue is not returned per day** — if the user asks for daily revenue, estimate via `sales * price` and note it's an estimate.
6. **`includeSearchStats` gaps** — when no search-visibility fields come back, note "search position data is not available for this niche" rather than silently omitting.
7. **No business advice** — present the shape; leave "should we buy this listing?" to the user.

## Important Limitations

- **Single SKU per call** — cannot pass a list of `productId`s; loop at the Agent layer if needed.
- **T-1 data** — `endDate` cannot be today or a future date.
- **Search stats optional** — `includeSearchStats=true` doesn't guarantee coverage for all niches.
- **Ozon-only** — Wildberries and other Russian marketplaces are not covered.
- **Missing days** — the series may have nulls / gaps where no data was captured; do not treat nulls as zero sales.

## User Expression & Scenario Quick Reference

**Applicable** — Single-SKU temporal analysis:

| User Says | Scenario |
|-----------|----------|
| "What's the sales trend of Ozon SKU 1786874757 last month" | Monthly time-series |
| "Is this Ozon listing seasonal or stable" | Seasonality check |
| "Did this Ozon product have stockouts recently" | Stock anomaly detection |
| "Price walk for this Ozon product over Q1" | Price movement |
| "Did this listing's search position improve" | Search visibility (requires `includeSearchStats`) |

**Not applicable** — Needs beyond single-SKU time-series:

- Batch snapshot of many SKUs → `ecommerce.ozon-product-detail`
- Brand / category / seller drill-down → matching `*-products` skill
- Pre-IDed discovery → `ecommerce.ozon-product-search`

**Boundary judgment**: Use this skill when the question starts with "how did this ONE product change over time". For multi-SKU comparisons or dimension-level filtering, go elsewhere.
