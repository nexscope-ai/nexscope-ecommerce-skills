# Configuration and report contract

Collect real evidence into a fresh local folder. Replace example ASINs with the user's confirmed products. `products[].asins` contains the confirmed children for that product. Use a child-only scope explicitly if variants cannot be established. `max_pages` is an approved per-child limit, not a claim that the source is exhausted.

```json
{
  "country": "US",
  "days": 7,
  "page_size": 50,
  "max_pages": 5,
  "products": [
    {"id":"own","role":"own","asins":["B072MQ5BRX"]},
    {"id":"peer","role":"competitor","asins":["B08N5WRWNW"]}
  ]
}
```

The collection plan reports the maximum calls for all confirmed children: `(max_pages + 3) × child count`. Supplemental discovery, fallback, ABA, keyword overview and verification calls are separate and consume credits. Do not assume approval for them from the base budget.

The local preliminary report calculates observed keyword/rank gaps and preserves source provenance. It is not a final semantic diagnosis. Read source summary/detail/review evidence, then supply a UTF-8 analysis JSON with these five arrays. Each entry contains `text`, `sources` (filenames recorded in dataset.calls), and optional `status`. A statement without source evidence must use `status:"missing"`. The renderer escapes all text and refuses references to unregistered evidence.

```json
{
  "trafficStructure":[{"text":"Explain only the returned comparable source shares and child coverage.","sources":[],"status":"missing"}],
  "indexingChecks":[{"text":"Targeted keyword evidence has not been collected; indexing remains unconfirmed.","sources":[],"status":"missing"}],
  "reviewToListing":[{"text":"Review sample unavailable; no pain-point claims are made.","sources":[],"status":"missing"}],
  "listingActions":[{"text":"Listing evidence unavailable; no factual benefit claims are added.","sources":[],"status":"missing"}],
  "fourWeekPlan":[{"text":"Week 1: verify gaps. Week 2: review compliant listing edits. Week 3: compare like-for-like coverage. Week 4: reassess and hand off advertising strategy if requested.","sources":[],"status":"missing"}]
}
```

Replace missing entries with real findings where possible; do not merely copy the example to claim successful analysis. Explain partial pagination and unknown variants. Semantic root/long-tail/scenario/paid gaps require agent review of the actual rows; the script's baseline covers observed keyword absence and organic rank differences only. Evidence citations establish provenance, not automatic factual validation: the agent must verify every statement and number against the cited file.

Use a new output directory for each report. Keep JSON data and the HTML report local. Report all absolute paths. Four-week actions are recommendations, not scheduled tasks or automatic advertising mutations.
