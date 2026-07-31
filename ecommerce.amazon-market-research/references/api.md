# Seller Sprite - Market Research API Reference

This document aligns with the `inputSchema` / `outputSchema` of the tool `_sellersprite_market_research` (see `temp/tools20260430.txt`).

## API Specification

- **Endpoint**: `${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/market/research`
- **HTTP Method**: POST, `Content-Type: application/json`
- **Authentication**: Header `Authorization: <api_key>`, api_key is read from environment variable `NEXSCOPE_API_KEY` or `NEXSCOPE_API_KEY` (if not configured, follow the **## Resolving Authentication and Credits Issues** section in SKILL.md)

## Request Parameters

**Required**: `marketplace` only.

**Note**: Numeric parameters labeled with "gross margin" etc. and where the schema states "input N means N%" generally have a value range of **0-100**. **Exception**: The following **GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion** `min*` / `max*` input parameters must be passed as **decimals**; see [Concentration and Structure Ratios](#concentration-and-structure-ratios).

### Category, Region, and Top Samples

| Parameter | Type | Required | Constraints | Description |
|------|------|------|------|------|
| marketplace | string | Yes | maxLength 1000, default `US` | Site code, see [marketplace](#marketplace-options) |
| nodeIdPath | string | No | maxLength 1000 | Category node ID path, e.g. `172282:281407` |
| departmentKeyword | string | No | maxLength 1000 | Category keyword path, e.g. `Electronics:Accessories & Supplies` |
| sellerLocation | string | No | maxLength 1000 | Seller location, multiple values comma-separated; see Seller Sprite table 1.3 for values |
| newProduct | integer | No | Default `3` | New product definition (months) |
| topNum | integer | No | Default `10` | Top Listing count |

### Time, Pagination, and Sort

| Parameter | Type | Required | Constraints | Description |
|------|------|------|------|------|
| month | string | No | See [month](#month) | Filter date: `nearly` or `yyyyMM` |
| page | integer | No | Default `1` | Page number, starting from 1 |
| size | integer | No | Default `50`, min `1`, max `200` | Results per page |
| orderField | string | No | maxLength 1000 | Sort field, see [orderField](#orderfield-options) |
| orderDesc | boolean | No | Default `true` | `true` descending, `false` ascending |

### Market Size and Entity Count

| Parameter | Type | Description |
|------|------|------|
| minAvgRevenue / maxAvgRevenue | number | Minimum / maximum average monthly sales revenue |
| minAvgUnits / maxAvgUnits | integer | Minimum / maximum average monthly sales volume |
| minGoodsCount / maxGoodsCount | integer | Minimum / maximum product count |
| minSellers / maxSellers | integer | Minimum / maximum seller count |
| minBrands / maxBrands | integer | Minimum / maximum brand count |
| minAvgSellers / maxAvgSellers | number | Minimum / maximum average seller count |

### Concentration and Structure Ratios

The following **7 groups** of filter input parameters (corresponding to Seller Sprite fields **GoodsCrn, BrandCrn, SellerCrn, EbcProportion, FbaProportion, FbmProportion, AmazonSelfProportion**) must be passed as **decimals**, with a convention of **0-1** ratio (e.g. **`0.35` means 35%**). Do **not** pass integer percentages in the 0-100 range (e.g. do not use `40` to mean 40%, unless confirmed against actual network behavior).

| Parameter | Type | Description |
|------|------|------|
| minGoodsCrn / maxGoodsCrn | number | Minimum / maximum product concentration (decimal 0-1) |
| minSellerCrn / maxSellerCrn | number | Minimum / maximum seller concentration (decimal 0-1) |
| minBrandCrn / maxBrandCrn | number | Minimum / maximum brand concentration (decimal 0-1) |
| minAmazonSelfProportion / maxAmazonSelfProportion | number | Minimum / maximum Amazon self-operated share (decimal 0-1) |
| minFbaProportion / maxFbaProportion | number | Minimum / maximum FBA share (decimal 0-1) |
| minFbmProportion / maxFbmProportion | number | Minimum / maximum FBM share (decimal 0-1) |
| minEbcProportion / maxEbcProportion | number | Minimum / maximum A+ share (decimal 0-1) |

### New Product Share (input scale based on schema)

| Parameter | Type | Description |
|------|------|------|
| minNewProportion / maxNewProportion | number | Minimum / maximum new product share (scale may differ from other ratio fields; refer to tool schema / actual network behavior) |

### Price, Rating, Margin, BSR (Market Average)

| Parameter | Type | Description |
|------|------|------|
| minAvgPrice / maxAvgPrice | number | Minimum / maximum average price |
| minAvgRating / maxAvgRating | number | Minimum / maximum average rating value |
| minAvgRatings / maxAvgRatings | integer | Minimum / maximum average review count |
| minAvgProfit / maxAvgProfit | number | Minimum / maximum average gross margin (input N means N%, 0-100) |
| minAvgBsr / maxAvgBsr | integer | Minimum / maximum average BSR rank |

### New Product Dimensions

| Parameter | Type | Description |
|------|------|------|
| minNewCount / maxNewCount | integer | Minimum / maximum new product count |
| minNewAvgPrice / maxNewAvgPrice | number | Minimum / maximum new product average price |
| minNewAvgRating / maxNewAvgRating | number | Minimum / maximum new product average star rating |
| minNewAvgRatings / maxNewAvgRatings | integer | Minimum / maximum new product average review count |
| minNewAvgUnits / maxNewAvgUnits | number | Minimum / maximum new product average monthly sales |
| minNewAvgRevenue / maxNewAvgRevenue | number | Minimum / maximum new product average monthly revenue |

### Top Listing Metrics

| Parameter | Type | Description |
|------|------|------|
| minTopAvgUnits / maxTopAvgUnits | integer | Minimum / maximum top listing average monthly sales |
| minTopAvgRevenue / maxTopAvgRevenue | number | Minimum / maximum top listing average monthly revenue |
| minTopAvgBsr / maxTopAvgBsr | integer | Minimum / maximum top listing average BSR |

### Weight and Volume

| Parameter | Type | Description |
|------|------|------|
| minWeight / maxWeight | number | Minimum / maximum weight |
| minVolume / maxVolume | number | Minimum / maximum volume |

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

### orderField Options

Consistent with tool schema "table 1.6".

| Value | Meaning |
|------|------|
| total_units | Monthly sales volume |
| total_amount | Monthly sales revenue |
| bsr_rank | BSR rank |
| price | Price |
| rating | Rating |
| reviews | Review count |
| profit | Gross margin |
| reviews_rate | Review rate |
| available_date | Listing time |
| questions | Q&A |
| total_units_growth | Monthly sales volume growth rate |
| total_amount_growth | Monthly sales revenue growth rate |
| reviews_increasement | Monthly new review count |
| bsr_rank_cv | 7-day BSR growth count |
| bsr_rank_cr | 7-day BSR growth rate |
| amz_unit | Variant sales volume |

## Response Structure

### Top-Level Fields

| Field | Type | Description |
|------|------|------|
| total | integer | Total record count |
| marketplace | string | Site code |
| data | array | Category market list (corresponds to third-party `data.items`) |
| columns | array | Render columns |
| costToken | integer | Tokens consumed |
| type | string | Render style |

### data[] Element (Single Category Market)

| Field | Type | Description |
|------|------|------|
| nodeId | string | Node ID |
| nodeIdPath | string | Node ID path |
| nodeLabelName | string | Node name |
| nodeLabelPath | string | Node name path |
| nodeLabelLocale | string | Node name translation |
| nodeLabelPathLocale | string | Node name path translation |
| marketplace | string | Market identifier |
| currency | string | Currency type for this market |
| ranking | integer | Rank |
| totalProducts | integer | Total product count |
| topProducts | integer | Sample count |
| sellers | integer | Seller count |
| brands | integer | Brand count |
| avgSellers | number | Average seller count |
| avgUnits | integer | Average monthly sales volume |
| totalUnits | integer | Total monthly sales volume |
| avgRevenue | number | Average monthly sales revenue |
| totalRevenue | number | Total monthly sales revenue |
| avgPrice | number | Average price |
| avgRating | number | Average rating value |
| avgRatings | integer | Average review count |
| avgBsr | integer | Average BSR |
| avgProfit | number | Average profit margin (%) |
| fbaProportion | number | FBA share (%) |
| fbmProportion | number | FBM share (%) |
| amazonSelfProportion | number | Amazon self-operated share (%) |
| ebcProportion | number | A+ product share (%) |
| returnRatio | number | Return rate (%) |
| avgReturnRatio | number | Category average return rate (%) |
| searchToPurchaseRatio | number | Search-to-purchase ratio (per mille) |
| sellerNation | string | Most common seller location code |
| sellerNationLabel | string | Most common seller location label |
| sellerProportion | number | Most common seller location share (%) |
| avgWeight | number | Average weight (pound) |
| baseAvgWeight | number | Average weight (g) |
| avgVolume | number | Average volume (in³) |
| baseAvgVolume | number | Average volume (cm³) |
| top10Images | array | Top 10 product images, elements see table below |

### top10Images[] Element

| Field | Type | Description |
|------|------|------|
| image | string | Image link |
| asin | string | ASIN |

## curl Example

```bash
curl -X POST ${NEXSCOPE_PROXY_BASE}/api/v1/tools/research/sellersprite/market/research   -H "Authorization: Bearer ${NEXSCOPE_API_KEY}"   -H "Content-Type: application/json"   -d '{
    "marketplace": "US",
    "month": "nearly",
    "minAvgRevenue": 10000,
    "maxGoodsCrn": 0.4,
    "orderField": "total_amount",
    "orderDesc": true,
    "page": 1,
    "size": 50
  }'
```

---
