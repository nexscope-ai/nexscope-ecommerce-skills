FastMoss-TikTok Top Selling Rankings API Reference (NexScope)

Calling Convention:
- URL: {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/fastmoss/productRankTopSelling
- Method: POST, Content-Type: application/json
- Auth: Header Authorization: Bearer {NEXSCOPE_API_KEY}

Request Parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| region | string | Yes | Market region: US/GB/MX/ES/ID/VN/MY/TH/PH |
| dateInfo | object | Yes | Date spec with type and value fields |
| dateInfo.type | string | Yes | Granularity: day/week/month |
| dateInfo.value | string | Yes | day=YYYY-MM-DD, week=YYYY-WW, month=YYYY-MM |
| category | string | No | English category name |
| orderby | object | No | Sort rule with field and order |
| orderby.field | string | No | units_sold/gmv/total_units_sold/total_gmv/growth_rate |
| orderby.order | string | No | desc (default) / asc |
| page | int | No | Page number, default 1 |
| pageSize | int | No | Items per page, max 10, default 10 |

Response (NexScope Proxy wraps with {code, msg, data, ts, traceId}):
Script auto-unwraps data field. Inner payload:
- errcode: 200=success
- total: matching record count
- products: array of product objects
- columns: render columns
- costToken: token consumption

Product Object Fields:
- title, productId, region
- price, minPrice, maxPrice, currency
- totalSaleCnt (total units sold)
- totalSale1dCnt (day sales, when dateInfo.type=day)
- totalSale7dCnt (week sales, when dateInfo.type=week)
- totalSale30dCnt (month sales, when dateInfo.type=month)
- totalSaleGmvAmt (total GMV)
- totalSaleGmv1dAmt (day GMV, when dateInfo.type=day)
- totalSaleGmv7dAmt (week GMV, when dateInfo.type=week)
- totalSaleGmv30dAmt (month GMV, when dateInfo.type=month)
- growthRate (percentage)
- shopName, shopSellerId, shopTotalUnitsSold
- categoryName
- productCommissionRate (basis points, 1000=10%)
- imageUrl
- offShelvesText (Yes=delisted, No=active)

Error Codes:
- 200: Success
- 401: Auth failed - check Bearer token
- Other: Business error - read errmsg field
