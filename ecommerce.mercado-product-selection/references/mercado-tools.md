# Marketplace tool reference

The `/lingdong/call` route accepts this request shape:

```json
{"toolName": "itemSearch", "arguments": {"siteId": "MLM"}}
```

- `toolName` is required and must be one of the supported operation names below.
- `arguments` is required and must be a JSON object.
- Preserve every nested field name and value type.

## Supported operations

- `itemInfo`
- `itemHistory`
- `itemSearch`
- `catalogInfo`
- `catalogHistory`
- `catalogSearch`
- `keywordDateSearch`
- `keywordMonthSearch`
- `keywordReverse`
- `categorySearch`
- `categorySmallSearch`
- `trendBrandTopBrand`
- `trendBrandTopItem`
- `trendBrandTopSeller`
- `trendNewItems`
- `trendPrice`
- `trendSale`
- `trendSoldHis`
- `trendStatistical`
- `trendStoreInventoryType`
- `sellerSearch`
- `reviewSearch`
- `rateInfo`
- `myUsage`

## Argument fields

The union of argument field names documented by the source contract is:

- `siteId`
- `itemId`
- `productId`
- `title`
- `categoryId`
- `sellerId`
- `itemUrl`
- `priceBegin`
- `priceEnd`
- `soldTotalBegin`
- `soldTotalEnd`
- `sale30Start`
- `sale30End`
- `scoreStart`
- `scoreEnd`
- `commentBegin`
- `commentEnd`
- `weightStart`
- `weightEnd`
- `startTimeAdded`
- `startTimeBegin`
- `startTimeEnd`
- `storageType`
- `sellerType`
- `follow`
- `isUsaFull`
- `itemStatus`
- `sortKey`
- `sortOrder`
- `pageNo`
- `pageSize`
- `searchText`
- `catalogId`
- `bland`
- `priceVolStart`
- `priceVolEnd`
- `sales30VolStart`
- `sales30VolEnd`
- `hisVolStart`
- `hisVolEnd`
- `scoreVolStart`
- `scoreVolEnd`
- `commentVolStart`
- `commentVolEnd`
- `stockVolStart`
- `stockVolEnd`
- `bsrVolStart`
- `bsrVolEnd`
- `followVol`
- `storageTypeVol`
- `sellerTypeVol`
- `storeStatusVol`
- `month`
- `addedVol`
- `runDate`
- `sort`
- `sale30`
- `visit30`
- `totalItem`
- `adCount`
- `runMonth`
- `levelId`
- `powerType`
- `MLM`
- `MLB`
- `MLA`
- `MLC`
- `MCO`

## Common contract notes

- `siteId` commonly accepts `MLM`, `MLB`, `MLA`, `MLC`, or `MCO`, depending on the operation.
- `pageNo` starts at 1; `pageSize` commonly defaults to 50.
- Date and month values preserve the operation-specific formats, such as `YYYY-MM-DD`, `YYYYMMDD`, and `YYYYMM`.
- `myUsage` accepts an empty `arguments` object.
- The response is returned unchanged by the client.
