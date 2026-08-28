---
name: ecommerce-ebay-search
description: "Search and browse product listings across multiple eBay international sites. Trigger when user mentions eBay product search, eBay listing query, eBay price comparison, eBay market browsing, eBay sold items, eBay auction search, eBay product research, eBay products, eBay pricing, eBay competitors, eBay auctions, eBay market analysis — even if \"eBay\" is not explicitly mentioned, as long as the need involves searching products on eBay, comparing eBay prices, finding sold listings, or analyzing eBay market data."
---

# eBay Product Search

This skill guides you on how to search and retrieve eBay product listing data, helping e-commerce sellers and buyers find products, compare prices, and analyze market trends across eBay''s global marketplaces.

## Core Concepts

eBay Product Search provides access to eBay''s front-end product listing data. It supports keyword-based search with rich filtering options including price range, item condition, buying format, sort order, seller location, and more. Results include product details such as title, price, shipping info, seller rating, sold quantity, and item condition.

**Marketplace logic**: The `ebayDomain` parameter controls which regional eBay site is searched. The default is `ebay.com` (US). When a user refers to a country or region, map it to the corresponding eBay domain (e.g., UK -> `ebay.co.uk`, Germany -> `ebay.de`).

**Buying format**: eBay supports multiple buying formats -- `Auction` for bid-based listings, `BIN` (Buy It Now) for fixed-price listings, and `BO` (Best Offer) for negotiable listings.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| keyword | string | No | Search keyword, up to 1024 characters | - |
| ebayDomain | string | No | eBay marketplace domain | ebay.com |
| page | integer | No | Page number for pagination | 1 |
| pageSize | integer | No | Results per page: 25, 50, 100, or 200 | 50 |
| orderBy | string | No | Sort order (see Sort Options below) | 12 (Best Match) |
| priceMin | number | No | Minimum price filter | - |
| priceMax | number | No | Maximum price filter | - |
| itemCondition | string | No | Item condition code(s), pipe-separated (e.g., `1000|3000`) | - |
| buyingFormat | string | No | Buying format: Auction, BIN, or BO | - |
| showOnly | string | No | Display filters, comma-separated (e.g., `Sold,Complete`) | - |
| location | integer | No | Seller location country code | - |
| prefLoc | string | No | Preferred location scope: 1=Domestic, 2=Regional, 3=Worldwide | - |
| zipCode | string | No | ZIP/postal code for regional delivery filtering | - |
| categoryId | integer | No | eBay category ID | - |
| noCache | boolean | No | Bypass cache for fresh results | false |

### Sort Options

| Code | Meaning |
|------|---------|
| 12 | Best Match (default) |
| 1 | Time: ending soonest |
| 10 | Time: newly listed |
| 15 | Price + Shipping: lowest first |
| 16 | Price + Shipping: highest first |
| 2 | Price: lowest first |
| 3 | Price: highest first |
| 7 | Distance: nearest first |
| 18 | Condition: new first |
| 19 | Condition: used first |

### Item Condition Codes

| Code | Condition |
|------|-----------|
| 1000 | New |
| 1500 | New other (see details) |
| 1750 | New with defects |
| 2000 | Certified Refurbished |
| 2010 | Excellent - Refurbished |
| 2020 | Very Good - Refurbished |
| 2030 | Good - Refurbished |
| 2500 | Seller refurbished / Remanufactured |
| 2750 | Like New |
| 3000 | Used / Pre-owned |
| 7000 | For parts or not working |

### showOnly Filter Values

| Value | Meaning |
|-------|---------|
| Complete | Completed listings |
| Sold | Sold listings only |
| FR | Free returns |
| RPA | Returns accepted |
| AS | Authorized seller |
| Savings | Deals & savings |
| SaleItems | Sale items |
| Lots | Lots |
| FS | Free shipping |
| LPickup | Local pickup |

### Supported eBay Domains

| Domain | Country |
|--------|---------|
| ebay.com | United States (default) |
| ebay.co.uk | United Kingdom |
| ebay.de | Germany |
| ebay.fr | France |
| ebay.it | Italy |
| ebay.es | Spain |
| ebay.ca | Canada |
| ebay.com.au | Australia |
| ebay.nl | Netherlands |
| ebay.at | Austria |
| ebay.ch | Switzerland |
| ebay.pl | Poland |
| ebay.ie | Ireland |
| ebay.com.hk | Hong Kong |
| ebay.com.my | Malaysia |
| ebay.com.sg | Singapore |

## API Invocation

- **API Endpoint**: `POST /ebay/search` (full parameters/response/error codes in `references/api.md`)
- **Python Script**: `python scripts/ebay_search.py ''<JSON params>'' [--inline]`
- **Cost**: This tool consumes credits. The same parameter combination is only called once per session by default; the script has a 24h local cache. Do not automatically retry with different keywords, pages, or zip codes on failure/empty results. If further retrieval is needed, explain the additional cost to the user first.

**Output Strategy (script default behavior)**:
- **Always** write the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/nexscope-ebay-search-<timestamp>.json` (`<cwd>` is the working directory at script execution time, i.e. the current project directory in Claude Code; `<session>` comes from the `SESSION_ID` environment variable, automatically grouped by user task; **do not write to /tmp**, error out if the current directory is not writable)
- Response body <= 8 KB: print the full JSON to stdout after writing to disk
- Response body > 8 KB: after writing to disk, stdout only outputs a summary (top-level fields, common counts like `total`/`costToken`, length of the largest list field + first 3 samples)
- Add `--inline` to force full output to stdout (still writes to disk)

**Data Reading Tips**: Check the summary first to see if it is sufficient. When specific fields are needed, prefer using `jq` or `ConvertFrom-Json` to extract from the saved JSON file on demand, avoiding loading the entire JSON into context.

## Authentication

Set the `NEXSCOPE_API_KEY` environment variable. If authentication fails (401/402) or you see insufficient balance errors, visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to get an API Key or top up credits.

## Usage Examples

**1. Basic Keyword Search**
Search for "wireless earbuds" on the US eBay marketplace:
```json
{"keyword": "wireless earbuds"}
```

**2. Search Sold Listings for Price Research**
Find sold listings for "iPhone 15 Pro" to gauge market value:
```json
{"keyword": "iPhone 15 Pro", "showOnly": "Sold,Complete", "orderBy": "10"}
```

**3. Search on a Specific Marketplace with Price Range**
Find new laptops priced between $500 and $1000 on eBay UK:
```json
{"keyword": "laptop", "ebayDomain": "ebay.co.uk", "priceMin": 500, "priceMax": 1000, "itemCondition": "1000"}
```

**4. Auction Items Ending Soon**
Find active auctions for "vintage watch" ending soonest:
```json
{"keyword": "vintage watch", "buyingFormat": "Auction", "orderBy": "1"}
```

**5. Find the Cheapest New Items**
Find the cheapest new "USB-C cable" with free shipping:
```json
{"keyword": "USB-C cable", "itemCondition": "1000", "orderBy": "15", "showOnly": "FS"}
```

**6. Paginated Results**
Get page 3 of results with 100 items per page for "running shoes":
```json
{"keyword": "running shoes", "page": 3, "pageSize": 100}
```

**7. Category-Specific Search**
Search within a specific eBay category:
```json
{"keyword": "mechanical keyboard", "categoryId": 33963}
```

**8. Location-Filtered Search**
Find products located in Germany on the German eBay site:
```json
{"keyword": "Kopfhoerer", "ebayDomain": "ebay.de", "location": 77}
```

## Display Rules

1. **Present data clearly**: Show search results in well-formatted tables including key fields such as title, price, condition, seller info, and shipping
2. **Price formatting**: Always display prices with their currency symbol. When showing price ranges (minPrice to maxPrice), format as a range
3. **Sold/completed data**: When showing sold items, highlight the sold price and quantity to help users with pricing research
4. **Seller trust indicators**: When available, show seller feedback percentage and review count to help users evaluate seller reliability
5. **Pagination notice**: When total results exceed the current page, inform the user of the total count and suggest pagination to see more
6. **Sponsored items**: Clearly mark sponsored listings so users can distinguish organic results from promoted ones
7. **Error handling**: When a query fails, explain the issue and suggest adjusting search parameters
8. **Link presentation**: Provide product links so users can view full details on eBay

## Important Limitations

- **No historical data**: This tool returns current live listings only, not historical pricing trends
- **Result cap**: Maximum 200 results per page
- **Rate limiting**: Excessive requests may be throttled; use `noCache: true` sparingly
- **Currency**: Prices are returned in the local currency of the eBay domain being searched

## User Expression & Scenario Quick Reference

**Applicable** -- Product search and listing data on eBay:

| User Says | Scenario |
|-----------|----------|
| "Search eBay for XX" | Basic product search |
| "How much does XX sell for on eBay" | Sold listing price research |
| "Find cheapest XX on eBay" | Price comparison / lowest price |
| "eBay auctions for XX" | Auction listing search |
| "What''s selling on eBay UK/Germany" | Regional marketplace browsing |
| "New XX under $50 on eBay" | Filtered search by condition and price |
| "eBay sold prices for XX" | Completed/sold listing analysis |
| "Find refurbished XX on eBay" | Condition-specific search |

**Not applicable** -- Needs beyond eBay product listings:
- eBay seller account management or store analytics
- eBay listing creation or editing
- eBay order tracking or purchase history
- Cross-platform price comparison (eBay vs Amazon vs others)
- eBay advertising or promoted listing management

## Credit Consumption

Consumes 15 credits.

> Users pay for credit consumption. When high-frequency calls to this skill are needed, or when the user may underestimate the credit cost, be sure to remind them and let them decide whether to continue.