# Amazon Business Insights Reverse Product Discovery API Reference

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/searchByMetrics`
- **HTTP Method**: POST, Content-Type: application/json
- **Authentication**: Header `Authorization: <api_key>`, read api_key from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow **## Resolving Authentication and Credit Issues** in SKILL.md)
- **User-Agent**: `NexScope-Skill/1.0`

## Request Parameters

POST Body (JSON). All parameters are optional, but **at least one of `keyword` / `nicheName` or any metric filter field must be provided**; leaving all empty is prohibited.

### Site and Pagination

  | Parameter | Type | Description | Example |
|------|------|------|------|
| amazonDomain | string | Amazon site code (closed enum), currently only supports `US`. Defaults to US only if not specified | `US` |
| limit | integer | Maximum number of results to return (1-200), default 25. No page parameter; returns the most recent N records sorted by collection time descending | `25` |

### Text Search

  | Parameter | Type | Description | Example |
|------|------|------|------|
| keyword | string | Search keyword text fragment (LIKE fuzzy match) | `whoop band` |
| nicheName | string | Normalized niche name fragment (LIKE, snake_case lowercase), suitable for niche time-series comparison | `wired_ribbon` |

### Market Size and Growth

  | Parameter | Type | Description |
|------|------|------|
| nicheRevenue360dMinUsdAtLeastGte | number | Minimum 360-day market revenue lower bound (USD) |
| nicheRevenue360dMinUsdAtLeastLte | number | Maximum 360-day market revenue lower bound (USD) |
| nicheRevenue360dMaxUsdAtLeastGte | number | Minimum 360-day market revenue upper bound (USD) |
| nicheRevenue360dMaxUsdAtLeastLte | number | Maximum 360-day market revenue upper bound (USD) |
| nichePeakSearchVolumeAtLeastGte | integer | Peak monthly search volume minimum (non-negative integer) |
| nichePeakSearchVolumeAtLeastLte | integer | Peak monthly search volume maximum (non-negative integer) |
| nicheSearchVolumeYoyChangePctAtLeastGte | number | Search volume YoY change rate minimum (%, signed) |
| nicheSearchVolumeYoyChangePctAtLeastLte | number | Search volume YoY change rate maximum (%, signed) |
| nichePeakMonthGte | integer | Search peak month minimum (1-12) |
| nichePeakMonthLte | integer | Search peak month maximum (1-12) |

### Competitive Landscape (Brand / Product Concentration)

  | Parameter | Type | Description |
|------|------|------|
| nicheBrandCountGte | integer | Active brand count minimum |
| nicheBrandCountLte | integer | Active brand count maximum |
| nicheBrandCountYoyChangePctAtLeastGte | number | Brand count YoY change rate minimum (%, signed) |
| nicheBrandCountYoyChangePctAtLeastLte | number | Brand count YoY change rate maximum (%, signed) |
| nicheTop5ProductClickSharePctAtLeastGte | number | Top 5 product click share minimum (0-100) |
| nicheTop5ProductClickSharePctAtLeastLte | number | Top 5 product click share maximum (0-100) |
| featureTop5BrandSharePctAtLeastGte | number | Top 5 brand combined share minimum (0-100) |
| featureTop5BrandSharePctAtLeastLte | number | Top 5 brand combined share maximum (0-100) |
| featureTopBrandsContains | string | Top 3 brand name fragment (original text LIKE, case-sensitive) |

### Price and Tiers

  | Parameter | Type | Description |
|------|------|------|
| priceMinUsdGte | number | Niche minimum product price lower bound (USD) |
| priceMinUsdLte | number | Niche minimum product price upper bound (USD) |
| priceMaxUsdGte | number | Niche maximum product price lower bound (USD) |
| priceMaxUsdLte | number | Niche maximum product price upper bound (USD) |
| priceSweetSpotMinUsdGte | number | Sweet spot lower bound minimum (USD) |
| priceSweetSpotMinUsdLte | number | Sweet spot lower bound maximum (USD) |
| priceSweetSpotMaxUsdGte | number | Sweet spot upper bound minimum (USD) |
| priceSweetSpotMaxUsdLte | number | Sweet spot upper bound maximum (USD) |
| priceEntryClickSharePctAtLeastGte | number | Entry tier click share minimum (0-100) |
| priceEntryClickSharePctAtLeastLte | number | Entry tier click share maximum (0-100) |
| priceMidClickSharePctAtLeastGte | number | Mid tier click share minimum (0-100) |
| priceMidClickSharePctAtLeastLte | number | Mid tier click share maximum (0-100) |
| priceHighClickSharePctAtLeastGte | number | High tier click share minimum (0-100) |
| priceHighClickSharePctAtLeastLte | number | High tier click share maximum (0-100) |

### Customer Profile (Age / Gender / Income / Life Stage)

  | Parameter | Type | Description |
|------|------|------|
| demoPrimaryAgeMinGte | integer | Primary audience age lower bound minimum (0-120 years) |
| demoPrimaryAgeMinLte | integer | Primary audience age lower bound maximum (0-120 years) |
| demoPrimaryAgeMaxGte | integer | Primary audience age upper bound minimum (0-120 years) |
| demoPrimaryAgeMaxLte | integer | Primary audience age upper bound maximum (0-120 years) |
| demoGenderDominant | string | Dominant gender (closed enum): `female` / `male` / `mixed` / `unspecified` |
| demoPrimaryIncomeTier | string | Income tier (closed enum): `low` / `middle_low` / `middle` / `middle_upper` / `upper_middle` / `high` |
| demoLifeStageTagsContains | string | Life stage tag fragment (snake_case, LIKE): `parent`, `student`, `retiree`, `athlete`, etc. |

### Product Features (Maturity / Trends / Differentiation / Search Patterns)

  | Parameter | Type | Description |
|------|------|------|
| featureNewAvgReviewCountAtLeastGte | integer | New product average review count minimum (non-negative integer) |
| featureNewAvgReviewCountAtLeastLte | integer | New product average review count maximum (non-negative integer) |
| featureEstablishedAvgReviewCountAtLeastGte | integer | Established product average review count minimum (non-negative integer) |
| featureEstablishedAvgReviewCountAtLeastLte | integer | Established product average review count maximum (non-negative integer) |
| featureEmergingTrendTagsContains | string | Emerging trend feature tag fragment (snake_case, LIKE): `cordless`, `portable`, `smart`, etc. |
| featureUncommonFeatureTagsContains | string | Rare differentiation feature tag fragment (snake_case, LIKE): `hema_free`, `medical_grade_silicone`, etc. |
| searchTopCategory1Label | string | Search traffic top category 1 label fragment (snake_case, LIKE): `core_product_terms`, `set_kit_configurations`, etc. |

### Review Highlights / Pain Points

  | Parameter | Type | Description |
|------|------|------|
| reviewPositiveTop1Topic | string | Positive review #1 topic fragment (snake_case, LIKE): `comfort`, `quality_overall_generic`, etc. |
| reviewPositiveTop1PctAtLeastGte | number | Positive review #1 topic share minimum (0-100, share among positive reviews) |
| reviewPositiveTop1PctAtLeastLte | number | Positive review #1 topic share maximum (0-100) |
| reviewNegativeTop1Topic | string | Negative review #1 topic fragment (snake_case, LIKE): `size`, `quality`, `durability`, etc. |
| reviewNegativeTop1PctAtLeastGte | number | Negative review #1 topic share minimum (0-100, share among negative reviews) |
| reviewNegativeTop1PctAtLeastLte | number | Negative review #1 topic share maximum (0-100) |
| reviewNegativeTop2Topic | string | Negative review #2 topic fragment (snake_case, LIKE) |
| reviewStrategicInsightTagsContains | string | Review strategic insight tag fragment (snake_case, LIKE): `sizing_clarity`, `material_transparency`, etc. |

## Response Structure

| Field | Type | Description |
|------|------|------|
| code | string | Response code, `200` indicates success |
| msg | string | Message, `ok` on success, error description on failure |
| data | array | Array of keyword metric records, each corresponding to a (site, keyword) combination, approximately 37 fields, sorted by collection time descending |

Key fields in `data[]` (excerpt):

| Field | Type | Description |
|------|------|------|
| amazonDomain | string | Site code (currently fixed `US`) |
| keyword | string | Original search keyword |
| nicheName | string | Normalized niche name (snake_case) |
| nicheRevenue360dMinUsdAtLeast / nicheRevenue360dMaxUsdAtLeast | number | Last 360 days market revenue lower bound / upper bound (USD) |
| nichePeakSearchVolumeAtLeast | integer | Peak monthly search volume |
| nichePeakMonth | integer | Search peak month (1-12) |
| nicheSearchVolumeYoyChangePctAtLeast | number | Search volume YoY change rate (%, signed) |
| nicheBrandCount / nicheBrandCountYoyChangePctAtLeast | integer / number | Active brand count and its YoY change rate |
| nicheTop5ProductClickSharePctAtLeast | number | Top 5 product click share (0-100) |
| featureTop5BrandSharePctAtLeast | number | Top 5 brand combined share (0-100) |
| featureTopBrands | array | Top 3 brand name list (original text) |
| priceMinUsd / priceMaxUsd | number | Niche overall minimum / maximum product price |
| priceSweetSpotMinUsd / priceSweetSpotMaxUsd | number | Value sweet spot price range lower bound / upper bound |
| priceEntryClickSharePctAtLeast / priceMidClickSharePctAtLeast / priceHighClickSharePctAtLeast | number | Entry / Mid / High tier click share (0-100) |
| demoPrimaryAgeMin / demoPrimaryAgeMax | integer | Core audience age lower bound / upper bound |
| demoGenderDominant | string | Dominant gender (`female` / `male` / `mixed` / `unspecified`) |
| demoPrimaryIncomeTier | string | Core audience income tier |
| demoLifeStageTags | array | Life stage tag list |
| featureNewAvgReviewCountAtLeast / featureEstablishedAvgReviewCountAtLeast | integer | New / Established product average review count |
| featureEmergingTrendTags / featureUncommonFeatureTags | array | Emerging trend / Rare differentiation feature tags |
| searchTopCategory1Label | string | Traffic top category 1 normalized label |
| reviewPositiveTop1Topic / reviewPositiveTop1PctAtLeast | string / number | Positive review #1 topic and its share among positive reviews |
| reviewNegativeTop1Topic / reviewNegativeTop1PctAtLeast / reviewNegativeTop2Topic | string / number / string | Negative review #1 topic, share, and secondary cause |
| reviewStrategicInsightTags | array | Review strategic insight tags |

## Error Codes

Under normal conditions, the HTTP status code is always 200. Business success or failure is determined by the `code` field in the response body. In cases of unauthorized access, the HTTP status code will be 401.

| errcode | Meaning | Action |
|--------|------|----------|
| 200 | Success | Parse the `data` array normally and display to the user |
| 401 | Authentication failed | HTTP 401 or authorized error: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| 402 | Insufficient credits | HTTP 402: follow **## Resolving Authentication and Credit Issues** in SKILL.md. |
| Other non-200 values | Business exception | Refer to the `msg` field for specific error cause; commonly all parameters empty or invalid parameter values |

Error response example:

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## curl Example

Filter for beginner-friendly niches with low brand density + high YoY growth:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/searchByMetrics \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "nicheBrandCountLte": 20,
    "nicheSearchVolumeYoyChangePctAtLeastGte": 100,
    "featureNewAvgReviewCountAtLeastLte": 500,
    "limit": 25
  }'
```

Trace niche history by keyword:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/searchByMetrics \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{"keyword": "whoop band", "limit": 50}'
```

Identify entry opportunities by negative review pain points + mid-tier scarcity:

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/amazon/opportunity/searchByMetrics \
  -H "Authorization: Bearer ${NEXSCOPE_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: NexScope-Skill/1.0" \
  -d '{
    "reviewNegativeTop1Topic": "size",
    "reviewNegativeTop1PctAtLeastGte": 70,
    "priceMidClickSharePctAtLeastLte": 5,
    "priceEntryClickSharePctAtLeastGte": 70
  }'
```

---
