# Seller Sprite - Market Statistics API Reference

This document aligns with the `inputSchema` / `outputSchema` of the tool `_sellersprite_market_statistics` (see `temp/tools20260430.txt`).

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/market/statistics`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

| Parameter | Type | Required | Constraints | Description |
|------|------|------|------|------|
| marketplace | string | Yes | maxLength 1000, default `US` | Site code, see [marketplace](#marketplace-options) |
| nodeIdPath | string | Yes | maxLength 1000 | Node ID path string, e.g. `1064954:1069242:1069784:1069820:1069838:1069828` |
| month | string | No | See [month](#month) | Filter date: `nearly` or `yyyyMM` |
| topN | integer | No | Default `10` | Top Listing count (used for top-related metric definitions) |
| newProduct | integer | No | Default `6` | New product definition (months) |

### marketplace Options

| Value | Meaning |
|------|------|
| US | US marketplace USD($) |
| JP | Japan marketplace JPY(￥) |
| UK | UK marketplace GBP(£) |
| DE | Germany marketplace EUR(€) |
| FR | France marketplace EUR(€) |
| IT | Italy marketplace EUR(€) |
| ES | Spain marketplace EUR(€) |
| CA | Canada marketplace C$($) |
| IN | India marketplace INR(₹) |

### month

- **Format**: Regex `^(nearly|(19|20)\d{2}(0[1-9]|1[0-2]))$`
- **`nearly`**: Last 30 days
- **`yyyyMM`**: Specific month (e.g. `202507`); supports up to **24 months** of historical months from the current month

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Total record count |
| marketplace | string | Site code |
| data | array | Statistics result list (corresponds to third-party `data`) |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |

### data[] Element (Single Node Statistics)

In the tool schema, `hl*` denotes **Top N Top Listings** (where N is determined by the request parameter `topN`).

#### Node and Site

| Field | Type | Description |
|------|------|------|
| nodeIdPath | string | Node ID path |
| nodeLabelPath | string | Node name path |
| nodeLabelLocale | string | Node name translation |
| nodeLabelPathLocale | string | Node name path translation |
| marketplace | string | Market identifier |
| countryCode | string | Two-letter country code |
| currency | string | Currency type for this market |

#### Scale and Sample

| Field | Type | Description |
|------|------|------|
| totalProducts | integer | Total product count |
| products | integer | Sample product count |
| sellers | integer | Seller count |
| brands | integer | Brand count |
| avgSellers | number | Average seller count |
| hlProducts | integer | Top N Listing sample product count |

#### Overall Market Metrics

| Field | Type | Description |
|------|------|------|
| avgUnits | integer | Average monthly sales volume |
| avgRevenue | number | Average monthly sales revenue |
| avgPrice | number | Average price |
| avgRating | number | Average star rating |
| avgRatings | integer | Average review count |
| avgRatingsCv | integer | Average monthly review growth count |
| avgBsr | integer | Average BSR |
| avgProfit | number | Average profit margin |
| avgWeight | number | Average weight (pound) |
| baseAvgWeight | number | Average weight (g) |
| avgVolume | number | Average volume (in³) |
| baseAvgVolume | number | Average volume (cm³) |

#### Top Listings (Top N, N = topN)

| Field | Type | Description |
|------|------|------|
| hlAvgUnits | integer | Top N Listing average monthly sales volume |
| hlAvgRevenue | number | Top N Listing average monthly sales revenue |
| hlAvgPrice | number | Top N Listing average price |
| hlAvgRating | number | Top N Listing average star rating |
| hlAvgRatings | integer | Top N Listing average review count |
| hlAvgRatingsCv | integer | Top N Listing average monthly review growth count |
| hlAvgBsr | integer | Top N Listing average BSR |

#### New Products (definition determined by newProduct)

| Field | Type | Description |
|------|------|------|
| newProducts | integer | New product count |
| newProductProportion | number | New product share |
| newAvgUnits | integer | New product average monthly sales volume |
| newAvgRevenue | number | New product average monthly sales revenue |
| newAvgPrice | number | New product average price |
| newAvgRating | number | New product average star rating |
| newAvgRatings | integer | New product average review count |
| minNewRatings | integer | Minimum new product review count |
| maxNewRatings | integer | Maximum new product review count |

#### Listing Time

| Field | Type | Description |
|------|------|------|
| firstShelfDate | string | Product first listing date |
| lastShelfDate | string | Product latest listing date |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/market/statistics   -H "Authorization: Bearer ${NEXSCOPE_API_KEY}"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "nodeIdPath": "172282:281407",
    "month": "nearly",
    "topN": 10,
    "newProduct": 6
  }'
```

---
