![E-commerce Skills Banner](./banner.png)

<div align="center">

# E-commerce Skills by Nexscope

**99 ready-to-use AI agent skills for ecommerce research, marketplace intelligence, product discovery, keyword analysis, trend research, sourcing, patent and trademark screening, multimodal tasks, and GEO workflows.**

For Amazon, TikTok Shop, Ozon, 1688, Shopify, Temu, Walmart, Shopee, Etsy, eBay, and more.

</div>

---

## Quick Start

### 1. Clone the collection

```bash
git clone https://github.com/nexscope-ai/nexscope-ecommerce-skills.git
cd nexscope-ecommerce-skills
```

### 2. Install the skills you need

Each top-level `ecommerce.*` directory is an individual skill package. Copy the complete directory into the skills location used by your AI agent. Keep its `SKILL.md`, scripts, references, assets, and manifest files together.

Example:

```bash
cp -R ecommerce.amazon-search <your-agent-skills-directory>/
```

You can also install the whole collection if your agent supports loading multiple skill directories from one repository. See the [external skills setup guide](https://www.nexscope.ai/help/skills-external-access?co-from=githubNS) for agent-specific instructions.

### 3. Configure API access

Most API-backed skills require these environment variables:

```bash
export NEXSCOPE_PROXY_BASE=https://api.nexscope.ai/
export NEXSCOPE_API_KEY=<your_api_key>
```

Get or manage an API key on the [Nexscope API Keys page](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubNS). API calls may consume credits; check the selected skill's `SKILL.md` before running additional queries or retries.

### 4. Ask naturally

Examples:

> "Search Amazon US for wireless earbuds and show the current organic and sponsored results."

> "Find TikTok Shop beauty products with strong 30-day sales and at least a 10% commission rate."

> "Show Ozon products for this seller and summarize their pricing and sales metrics."

> "Search 1688 for visually similar suppliers using this product image."

> "Check this product image for similar design patents."

> "Score this product page for SEO and GEO readiness."

> "Evaluate whether AI search engines mention and recommend this product."

---

## Collection at a Glance

| Category | Skills |
|---|---:|
| Amazon Intelligence | 34 |
| TikTok Shop Intelligence | 13 |
| Ozon Intelligence | 13 |
| Patent, Trademark & Compliance | 17 |
| 1688 Sourcing | 3 |
| Other Marketplaces & Storefronts | 11 |
| Web, Trends, Multimodal & GEO | 8 |
| **Total** | **99** |

---

## All 99 Skills

### Amazon Intelligence (34)

| Skill | What it does |
|---|---|
| [`ecommerce.amazon-alexa-search`](./ecommerce.amazon-alexa-search/) | Search Amazon Alexa shopping results. |
| [`ecommerce.amazon-asin-keywords`](./ecommerce.amazon-asin-keywords/) | Retrieve keywords associated with an Amazon ASIN. |
| [`ecommerce.amazon-asin-traffic-summary`](./ecommerce.amazon-asin-traffic-summary/) | Retrieve an Amazon ASIN traffic summary. |
| [`ecommerce.amazon-broad-product-search`](./ecommerce.amazon-broad-product-search/) | Search broadly for Amazon products. |
| [`ecommerce.amazon-competitor-lookup`](./ecommerce.amazon-competitor-lookup/) | Look up competing Amazon products. |
| [`ecommerce.amazon-keyword-expansion`](./ecommerce.amazon-keyword-expansion/) | Expand an Amazon keyword. |
| [`ecommerce.amazon-keyword-intelligence`](./ecommerce.amazon-keyword-intelligence/) | Query Amazon keyword intelligence data. |
| [`ecommerce.amazon-keyword-overview`](./ecommerce.amazon-keyword-overview/) | Retrieve an overview for an Amazon keyword. |
| [`ecommerce.amazon-keyword-search-history`](./ecommerce.amazon-keyword-search-history/) | Retrieve historical Amazon keyword search volume. |
| [`ecommerce.amazon-keyword-share-of-voice`](./ecommerce.amazon-keyword-share-of-voice/) | Retrieve Amazon keyword share of voice. |
| [`ecommerce.amazon-keyword-summary`](./ecommerce.amazon-keyword-summary/) | Retrieve a summary for an Amazon keyword. |
| [`ecommerce.amazon-market-product-detail`](./ecommerce.amazon-market-product-detail/) | Retrieve Amazon marketplace product details. |
| [`ecommerce.amazon-market-product-search`](./ecommerce.amazon-market-product-search/) | Search for products in the Amazon marketplace. |
| [`ecommerce.amazon-market-research`](./ecommerce.amazon-market-research/) | Research an Amazon market. |
| [`ecommerce.amazon-market-statistics`](./ecommerce.amazon-market-statistics/) | Analyze Amazon market statistics. |
| [`ecommerce.amazon-niche-info`](./ecommerce.amazon-niche-info/) | Retrieve Amazon niche information. |
| [`ecommerce.amazon-niche-info-by-asin`](./ecommerce.amazon-niche-info-by-asin/) | Retrieve Amazon niche information by ASIN. |
| [`ecommerce.amazon-niche-info-by-keyword`](./ecommerce.amazon-niche-info-by-keyword/) | Retrieve Amazon niche information by keyword. |
| [`ecommerce.amazon-niche-reviews-by-keyword`](./ecommerce.amazon-niche-reviews-by-keyword/) | Retrieve Amazon niche reviews by keyword. |
| [`ecommerce.amazon-opportunity-report-by-keyword`](./ecommerce.amazon-opportunity-report-by-keyword/) | Retrieve Amazon opportunity reports by keyword. |
| [`ecommerce.amazon-opportunity-search-by-metrics`](./ecommerce.amazon-opportunity-search-by-metrics/) | Search Amazon opportunities by metrics. |
| [`ecommerce.amazon-policy-feed`](./ecommerce.amazon-policy-feed/) | Retrieve marketplace policy updates and full article details. |
| [`ecommerce.amazon-product-database`](./ecommerce.amazon-product-database/) | Query the Amazon product database. |
| [`ecommerce.amazon-product-database-search`](./ecommerce.amazon-product-database-search/) | Search the Amazon product database. |
| [`ecommerce.amazon-product-detail`](./ecommerce.amazon-product-detail/) | Retrieve Amazon product details. |
| [`ecommerce.amazon-product-discovery`](./ecommerce.amazon-product-discovery/) | Discover Amazon products. |
| [`ecommerce.amazon-product-history`](./ecommerce.amazon-product-history/) | Retrieve Amazon product history and product details. |
| [`ecommerce.amazon-product-price-series`](./ecommerce.amazon-product-price-series/) | Retrieve Amazon product price and metric series. |
| [`ecommerce.amazon-related-asins`](./ecommerce.amazon-related-asins/) | Retrieve Amazon ASINs related to an ASIN. |
| [`ecommerce.amazon-reviews-list`](./ecommerce.amazon-reviews-list/) | Retrieve Amazon product reviews. |
| [`ecommerce.amazon-sales-estimates`](./ecommerce.amazon-sales-estimates/) | Estimate historical daily sales for an Amazon product. |
| [`ecommerce.amazon-search`](./ecommerce.amazon-search/) | Search Amazon products. |
| [`ecommerce.amazon-search-by-image`](./ecommerce.amazon-search-by-image/) | Search for visually similar products on Amazon using an image across eight marketplaces. |
| [`ecommerce.amazon-traffic-keywords`](./ecommerce.amazon-traffic-keywords/) | Research Amazon traffic keywords. |

### TikTok Shop Intelligence (13)

| Skill | What it does |
|---|---|
| [`ecommerce.tiktok-batch-product-detail`](./ecommerce.tiktok-batch-product-detail/) | Retrieve batch TikTok product details. |
| [`ecommerce.tiktok-creator-analytics`](./ecommerce.tiktok-creator-analytics/) | Retrieve TikTok creator rankings and creator-level analytics. |
| [`ecommerce.tiktok-livestream-analytics`](./ecommerce.tiktok-livestream-analytics/) | Retrieve TikTok livestream rankings and livestream details. |
| [`ecommerce.tiktok-new-product-rank`](./ecommerce.tiktok-new-product-rank/) | Retrieve TikTok new-product rankings. |
| [`ecommerce.tiktok-product-analytics`](./ecommerce.tiktok-product-analytics/) | Retrieve TikTok product rankings and product details. |
| [`ecommerce.tiktok-product-discovery`](./ecommerce.tiktok-product-discovery/) | Discover TikTok products. |
| [`ecommerce.tiktok-product-search`](./ecommerce.tiktok-product-search/) | Search TikTok products. |
| [`ecommerce.tiktok-seller-detail`](./ecommerce.tiktok-seller-detail/) | Get detailed metrics and attributes for one TikTok Shop seller. |
| [`ecommerce.tiktok-shop-analytics`](./ecommerce.tiktok-shop-analytics/) | Retrieve TikTok shop rankings and shop details. |
| [`ecommerce.tiktok-top-selling-products`](./ecommerce.tiktok-top-selling-products/) | Retrieve TikTok Shop top-selling product rankings. |
| [`ecommerce.tiktok-video-analytics`](./ecommerce.tiktok-video-analytics/) | Retrieve TikTok video rankings and video details. |
| [`ecommerce.tiktok-video-download-url`](./ecommerce.tiktok-video-download-url/) | Retrieve a TikTok video download URL. |
| [`ecommerce.tiktok-video-search`](./ecommerce.tiktok-video-search/) | Search TikTok videos by market, creator, product, engagement, and publication filters. |

### Ozon Intelligence (13)

| Skill | What it does |
|---|---|
| [`ecommerce.ozon-brand-products`](./ecommerce.ozon-brand-products/) | Retrieve Ozon products for a brand. |
| [`ecommerce.ozon-category-products`](./ecommerce.ozon-category-products/) | Retrieve Ozon products for a category. |
| [`ecommerce.ozon-category-search`](./ecommerce.ozon-category-search/) | Search Ozon category products. |
| [`ecommerce.ozon-keyword-back-search`](./ecommerce.ozon-keyword-back-search/) | Find Ozon keywords associated with product SKUs. |
| [`ecommerce.ozon-keyword-mining`](./ecommerce.ozon-keyword-mining/) | Mine related Ozon search keywords. |
| [`ecommerce.ozon-market-keyword-search`](./ecommerce.ozon-market-keyword-search/) | Search Ozon marketplace keyword metrics. |
| [`ecommerce.ozon-product-detail`](./ecommerce.ozon-product-detail/) | Retrieve batch Ozon product details. |
| [`ecommerce.ozon-product-detail-search`](./ecommerce.ozon-product-detail-search/) | Retrieve Ozon product detail history. |
| [`ecommerce.ozon-product-report-search`](./ecommerce.ozon-product-report-search/) | Search Ozon product reports. |
| [`ecommerce.ozon-product-search`](./ecommerce.ozon-product-search/) | Search Ozon products by keyword or product ID. |
| [`ecommerce.ozon-product-trend`](./ecommerce.ozon-product-trend/) | Retrieve daily Ozon product trends. |
| [`ecommerce.ozon-seller-products`](./ecommerce.ozon-seller-products/) | Retrieve Ozon products for a seller. |
| [`ecommerce.ozon-shop-search`](./ecommerce.ozon-shop-search/) | Search Ozon shops and seller metrics. |

### Patent, Trademark & Compliance (17)

| Skill | What it does |
|---|---|
| [`ecommerce.patent-abstract-image-data`](./ecommerce.patent-abstract-image-data/) | Retrieve patent abstract image data. |
| [`ecommerce.patent-claims`](./ecommerce.patent-claims/) | Retrieve original patent claims and claim counts. |
| [`ecommerce.patent-claims-translation`](./ecommerce.patent-claims-translation/) | Retrieve translated patent claims. |
| [`ecommerce.patent-description-data`](./ecommerce.patent-description-data/) | Retrieve original patent description data. |
| [`ecommerce.patent-description-data-translation`](./ecommerce.patent-description-data-translation/) | Retrieve translated patent description data. |
| [`ecommerce.patent-detailed-bibliography`](./ecommerce.patent-detailed-bibliography/) | Retrieve detailed patent bibliography data. |
| [`ecommerce.patent-fulltext-images`](./ecommerce.patent-fulltext-images/) | Retrieve patent full-text image data. |
| [`ecommerce.patent-legal-status-data`](./ecommerce.patent-legal-status-data/) | Retrieve patent legal status data. |
| [`ecommerce.patent-title-abstract-translation`](./ecommerce.patent-title-abstract-translation/) | Retrieve translated patent titles and abstracts. |
| [`ecommerce.ruiguan-copyright-detection`](./ecommerce.ruiguan-copyright-detection/) | Detect image copyright infringement risks by comparing against a database of registered copyrighted works. |
| [`ecommerce.ruiguan-detection-patent-design`](./ecommerce.ruiguan-detection-patent-design/) | Detect design patent infringement risks by comparing a product image against a global design patent database across more than 25 jurisdictions. |
| [`ecommerce.ruiguan-gun-parts-search`](./ecommerce.ruiguan-gun-parts-search/) | Check product images against a database of policy-violating items using visual similarity. |
| [`ecommerce.ruiguan-trademark-graphic-detection`](./ecommerce.ruiguan-trademark-graphic-detection/) | Detect graphic trademarks in product images by comparing against registered trademark databases across multiple regions. |
| [`ecommerce.text-trademark-detector`](./ecommerce.text-trademark-detector/) | Detect trademark risks in product titles and text. |
| [`ecommerce.utility-patent-detector`](./ecommerce.utility-patent-detector/) | Check products for utility patent similarity. |
| [`ecommerce.zhihuiya-patent-image-search`](./ecommerce.zhihuiya-patent-image-search/) | Search for visually similar design patents using an image, with country, legal status, and date filters. |
| [`ecommerce.zhihuiya-utility-patent-image-search`](./ecommerce.zhihuiya-utility-patent-image-search/) | Search for visually similar utility model patents using an image, with country, legal status, and date filters. |

These skills support research and screening workflows. Their results are not legal advice and do not replace review by a qualified intellectual property professional.

### 1688 Sourcing (3)

| Skill | What it does |
|---|---|
| [`ecommerce.1688-product-billboard`](./ecommerce.1688-product-billboard/) | Retrieve 1688 bestseller ranking data. |
| [`ecommerce.1688-product-search`](./ecommerce.1688-product-search/) | Search 1688 products with sourcing and sales filters. |
| [`ecommerce.1688-search-by-image`](./ecommerce.1688-search-by-image/) | Search for visually similar products on 1688 using an image. |

### Other Marketplaces & Storefronts (11)

| Skill | What it does |
|---|---|
| [`ecommerce.ebay-search`](./ecommerce.ebay-search/) | Search eBay products. |
| [`ecommerce.etsy-category-search`](./ecommerce.etsy-category-search/) | Search Etsy marketplace categories. |
| [`ecommerce.etsy-product-query`](./ecommerce.etsy-product-query/) | Query Etsy product listings and performance data. |
| [`ecommerce.shopee-product-search`](./ecommerce.shopee-product-search/) | Search Shopee product information and metrics. |
| [`ecommerce.shopify-product-query`](./ecommerce.shopify-product-query/) | Query Shopify products with filters. |
| [`ecommerce.shopify-store-query`](./ecommerce.shopify-store-query/) | Query Shopify stores with filters. |
| [`ecommerce.temu-category-search`](./ecommerce.temu-category-search/) | Search Temu categories. |
| [`ecommerce.temu-product-source-query`](./ecommerce.temu-product-source-query/) | Query Temu products for sourcing research. |
| [`ecommerce.temu-store-source-query`](./ecommerce.temu-store-source-query/) | Query Temu stores for sourcing research. |
| [`ecommerce.walmart-product-detail`](./ecommerce.walmart-product-detail/) | Retrieve Walmart product details. |
| [`ecommerce.walmart-search`](./ecommerce.walmart-search/) | Search Walmart products. |

### Web, Trends, Multimodal & GEO (8)

| Skill | What it does |
|---|---|
| [`ecommerce.geo-score-check`](./ecommerce.geo-score-check/) | Score an ecommerce URL for SEO and GEO readiness from crawlable evidence. |
| [`ecommerce.google-ai-mode-search`](./ecommerce.google-ai-mode-search/) | Search Google AI Mode results. |
| [`ecommerce.google-trends-by-keywords`](./ecommerce.google-trends-by-keywords/) | Retrieve Google Trends data for keywords. |
| [`ecommerce.google-trends-by-time`](./ecommerce.google-trends-by-time/) | Retrieve Google Trends data by time range. |
| [`ecommerce.multimodal-generate-image`](./ecommerce.multimodal-generate-image/) | Generate and edit images from text prompts and optional reference images. |
| [`ecommerce.multimodal-recognize-image`](./ecommerce.multimodal-recognize-image/) | Analyze images and extract information with multimodal AI recognition. |
| [`ecommerce.product-ai-visibility`](./ecommerce.product-ai-visibility/) | Evaluate product mentions and recommendation positions across AI search engines. |
| [`ecommerce.web-search`](./ecommerce.web-search/) | Search the web for a keyword. |

---

## How Each Skill Works

Start with the selected directory's `SKILL.md`. It defines:

- when the skill should trigger;
- required and optional inputs;
- supported marketplaces, filters, and limits;
- the API endpoint or local workflow;
- safe handling for credits, retries, missing data, and errors;
- the expected output format.

Most API-backed packages also include:

```text
ecommerce.example-skill/
├── SKILL.md
├── manifest.json
├── references/
│   └── api.md
└── scripts/
    └── example_skill.py
```

Do not copy only `SKILL.md` when a package contains scripts, references, assets, configuration, or manifest files.

---

## Usage Notes

- **Evidence first:** Results depend on the data returned for the exact marketplace, keyword, product, seller, date range, and filters used.
- **No automatic extra spend:** Many API-backed skills instruct the agent not to retry with changed parameters or fetch additional pages without approval.
- **Marketplace differences:** Supported countries, domains, languages, currencies, and available fields vary by skill.
- **Image workflows:** Image-search and image-analysis skills may require an accessible image URL or the included upload helper.
- **Readiness is not visibility:** `ecommerce.geo-score-check` evaluates crawlable SEO/GEO readiness. It does not measure live AI mentions.
- **Time-bound AI results:** `ecommerce.product-ai-visibility` evaluates current AI responses; results can change as models and source content change.

---

## Troubleshooting

### Missing credentials

```text
NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required
```

Set both environment variables in the same shell or runtime that launches the skill.

### Authentication or credit errors

Confirm that the API key is valid and that the account has enough credits for the requested call. Manage access on the [Nexscope API Keys page](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubNS).

### Skill not detected

- Copy the complete `ecommerce.*` directory into the correct skills location.
- Keep the folder name unchanged.
- Restart or reload the agent if it discovers skills only at startup.
- Read the agent-specific [setup guide](https://www.nexscope.ai/help/skills-external-access?co-from=githubNS).

### Request or response details

Read the selected skill's `references/api.md` and script usage section. Parameters and supported marketplaces differ between skills.

---

## License

These skills are proprietary software owned by Nexscope. API-backed usage requires valid Nexscope access and may consume credits.

© 2026 Nexscope AI

---

Built by **[Nexscope](https://www.nexscope.ai/?co-from=githubNS)** — an all-in-one AI agent for ecommerce sellers, helping them research products, uncover keywords and review insights, improve GEO visibility, and scale their businesses.
