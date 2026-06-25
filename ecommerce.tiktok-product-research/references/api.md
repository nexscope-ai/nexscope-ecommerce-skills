FastMoss-TikTok Product Search API Reference (NexScope)

Calling Convention:
- URL: {NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/fastmoss/productSearch
- Method: POST, Content-Type: application/json
- Auth: Header Authorization: Bearer {NEXSCOPE_API_KEY}

Request Parameters (all optional):
- keyword (string): Product title fuzzy match
- region (string): US/GB/MX/ES/DE/IT/FR/ID/VN/MY/TH/PH/BR/JP/SG
- category (string): English category name
- shopType (int): 1=local, 2=cross-border
- isTopSelling (bool): Hot-selling only
- isNewListed (bool): New products only
- isSshop (bool): Fully-managed only
- isFreeShipping (bool): Free shipping only
- isLocalWarehouse (bool): Local warehouse only
- unitsSoldRange (object): {min, max}
- commissionRateRange (object): {min, max} decimal (0.10=10%)
- creatorCountRange (object): {min, max}
- orderField (string): day7_units_sold/day7_gmv/commission_rate/total_units_sold/total_gmv/creator_count
- page (int): default 1
- pageSize (int): max 10, default 10

Response (NexScope Proxy wraps with {code, msg, data, ts, traceId}):
Script auto-unwraps data field. Inner payload:
- errcode: 200=success
- total: matching record count
- products: array of product objects
- costToken: token consumption

Product Object Fields:
- title, productId, region
- price, minPrice, maxPrice, currency
- totalSaleCnt, totalSale1dCnt, totalSale7dCnt, totalSale28dCnt, totalSale90dCnt
- totalSaleGmvAmt, totalSaleGmv7dAmt, totalSaleGmv28dAmt
- totalVideoCnt, totalLiveCnt, totalIflCnt
- productCommissionRate (decimal, 0.10=10%)
- productRating, reviewCount, skuCount
- shopName, shopSellerId, shopTotalUnitsSold
- isCrossBorder (1=cross-border, 0=local)
- isSShopText, freeShippingText
- availableDate, categoryName, salesTrendFlagText
- tiktokUrl, fastmossUrl, imageUrl

Error Codes:
- 200: Success
- 401: Auth failed - check Bearer token
- Other: Business error - read errmsg field
