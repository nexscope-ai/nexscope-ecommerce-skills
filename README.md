# Nexscope E-commerce Skills 🛍️

> Professional AI agent skills for e-commerce research, analysis, and intelligence. Powered by Nexscope API.

Transform your AI agent into an e-commerce expert with 34 production-ready skills covering product research, competitor analysis, market intelligence, and more.

## 🚀 Quick Start

**Requirements:**
- Nexscope API key ([Get yours here](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubns))
- AI agent that supports Skills format (OpenClaw, Claude Code, Cursor, etc.)

**Installation:**
1. Clone this repository to your agent's skills directory:
   ```bash
   git clone https://github.com/nexscope-ai/nexscope-ecommerce-skills.git
   ```
2. Configure environment variables:
   ```bash
   export NEXSCOPE_PROXY_BASE=https://api.nexscope.ai/
   export NEXSCOPE_API_KEY=<your_api_key>
   ```

📖 **Detailed Setup Guide:** [https://www.nexscope.ai/help/skills-external-access](https://www.nexscope.ai/help/skills-external-access?co-from=githubns)

## 🎯 Skills Overview

### 🔍 Product Discovery & Opportunity Analysis (5 skills)
Find winning products and untapped market opportunities.

| Skill | Description | Best For |
|-------|-------------|----------|
| **product-opportunity-finder** | Find blue-ocean product opportunities and market gaps | Product discovery, market entry |
| **niche-evaluator** | Evaluate niche viability and competition levels | Market validation, niche analysis |
| **demand-validator** | Validate market demand for product concepts | Product validation, demand research |
| **product-validator** | Comprehensive product viability analysis | Due diligence, risk assessment |
| **new-product-tracker** | Track emerging products and market trends | Trend monitoring, early opportunity detection |

### 🔑 Keyword Research & SEO (6 skills)
Optimize listings and discover high-value keywords.

| Skill | Description | Best For |
|-------|-------------|----------|
| **keyword-research** | Comprehensive keyword research and analysis | SEO strategy, content planning |
| **keyword-opportunity-finder** | Identify high-opportunity, low-competition keywords | Keyword strategy, market gaps |
| **keyword-priority-ranker** | Rank keywords by opportunity and difficulty | Campaign planning, resource allocation |
| **listing-keyword-optimizer** | Optimize product listings for search visibility | Listing optimization, conversion improvement |
| **keyword-reverse-lookup** | Reverse engineer competitor keyword strategies | Competitive research, strategy development |
| **keyword-rank-tracker** | Monitor keyword ranking performance over time | Performance tracking, SEO monitoring |

### 🏆 Competitive Intelligence (3 skills)
Understand your competition and find strategic advantages.

| Skill | Description | Best For |
|-------|-------------|----------|
| **competitor-analyzer** | Deep competitive analysis and benchmarking | Market positioning, strategic planning |
| **competitor-listing-analyzer** | Analyze competitor product listings and strategies | Listing optimization, competitive gaps |
| **differentiation-advisor** | Find ways to differentiate from competitors | Product development, positioning strategy |

### 💰 Pricing & Market Monitoring (2 skills)
Track prices and market dynamics in real-time.

| Skill | Description | Best For |
|-------|-------------|----------|
| **price-monitor** | Real-time price monitoring and alerts | Pricing strategy, competitive intelligence |
| **price-history-analyzer** | Analyze historical pricing patterns and trends | Market analysis, pricing optimization |

### ⚖️ Patent & IP Analysis (5 skills)
Avoid legal risks and understand intellectual property landscape.

| Skill | Description | Best For |
|-------|-------------|----------|
| **patent-risk-checker** | Screen products for patent infringement risk | Legal risk assessment, product clearance |
| **design-patent-analyzer** | Analyze design patent landscape and risks | Design development, IP strategy |
| **patent-claim-analyzer** | Detailed patent claim analysis and interpretation | Legal research, IP due diligence |
| **patent-family-explorer** | Explore patent families and related IP | IP landscape analysis, prior art research |
| **patent-legal-status** | Check patent legal status and validity | IP verification, legal compliance |

### ⭐ Review & Feedback Analysis (2 skills)
Understand customer sentiment and product performance.

| Skill | Description | Best For |
|-------|-------------|----------|
| **review-checker** | Analyze product reviews and customer feedback | Product improvement, market research |
| **review-monitor** | Monitor review changes and sentiment trends | Brand monitoring, quality control |

### 📱 Platform-Specific Tools (5 skills)
Specialized tools for major e-commerce platforms.

| Skill | Description | Best For |
|-------|-------------|----------|
| **tiktok-product-research** | Search and analyze TikTok Shop products | TikTok commerce, trend research |
| **tiktok-product-video** | Analyze TikTok product videos and performance | Content strategy, viral analysis |
| **tiktok-top-selling** | Identify top-selling products on TikTok Shop | Product discovery, trend identification |
| **temu-product-query** | Research products and trends on Temu | Cross-platform analysis, market expansion |
| **temu-store-query** | Analyze Temu stores and seller strategies | Competitive research, market entry |

### 📊 Market Intelligence & Analytics (6 skills)
Deep market insights and trend analysis.

| Skill | Description | Best For |
|-------|-------------|----------|
| **market-overview** | Comprehensive market analysis and sizing | Market entry, strategic planning |
| **market-share-analyzer** | Analyze market share distribution and trends | Competitive intelligence, market positioning |
| **trend-discovery** | Identify emerging trends and opportunities | Innovation, product development |
| **market-alert** | Real-time market change notifications | Monitoring, opportunity alerts |
| **image-similarity-finder** | Find visually similar products and designs | Design research, competitive analysis |
| **patent-report-generator** | Generate comprehensive patent analysis reports | Documentation, legal compliance |

## 🛠️ Technical Requirements

### Environment Setup
```bash
# Required environment variables
export NEXSCOPE_PROXY_BASE=https://api.nexscope.ai/
export NEXSCOPE_API_KEY=<your_nexscope_api_key>

# Verify setup
echo $NEXSCOPE_PROXY_BASE
echo $NEXSCOPE_API_KEY
```

### Supported AI Agents
- **OpenClaw** - Native skills support
- **Claude Code** - Full compatibility
- **Cursor** - Complete integration
- **Windsurf** - Full feature support
- **Any agent supporting Skills format**

### API Requirements
- **Nexscope API Key** - [Create here](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubns)
- **Active Subscription** - Credits required for API calls
- **Network Access** - HTTPS access to api.nexscope.ai

## 💡 Usage Examples

### Product Research Workflow
```
# Find product opportunities
"What products should I sell in the kitchen gadgets category?"
→ Uses: ecommerce.product-opportunity-finder

# Validate demand
"Validate demand for wireless phone chargers"
→ Uses: ecommerce.demand-validator

# Check competition
"Analyze competitors for bluetooth speakers under $50"
→ Uses: ecommerce.competitor-analyzer
```

### Market Analysis Workflow
```
# Market overview
"Give me a market overview for fitness equipment"
→ Uses: ecommerce.market-overview

# Trend analysis
"What are the trending products in home decor?"
→ Uses: ecommerce.trend-discovery

# Price monitoring
"Monitor prices for gaming keyboards"
→ Uses: ecommerce.price-monitor
```

### IP & Legal Risk Workflow
```
# Patent risk screening
"Check if this phone case design has patent risks"
→ Uses: ecommerce.patent-risk-checker

# Design patent analysis
"Analyze design patents for smartwatch bands"
→ Uses: ecommerce.design-patent-analyzer
```

## 🔧 Troubleshooting

### Common Issues

**❌ API Key Error**
```
Error: Authentication failed
```
**✅ Solution:** Verify your API key is correct and active
- Check [API Keys page](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubns)
- Ensure key has sufficient credits

**❌ Environment Variable Missing**
```
Error: NEXSCOPE_API_KEY not found
```
**✅ Solution:** Set required environment variables
```bash
export NEXSCOPE_PROXY_BASE=https://api.nexscope.ai/
export NEXSCOPE_API_KEY=<your_key>
```

**❌ Skill Not Found**
```
Error: Skill package not found
```
**✅ Solution:** 
- Ensure skill folder is in correct directory
- Check folder name matches skill name exactly
- Pull latest updates from GitHub: `git pull origin main`

**❌ Network Connection Issues**
```
Error: Connection timeout
```
**✅ Solution:**
- Check internet connection
- Verify firewall allows HTTPS to api.nexscope.ai
- Try different network if corporate firewall blocks access

### Getting Help

1. **Documentation**: [https://www.nexscope.ai/help/skills-external-access](https://www.nexscope.ai/help/skills-external-access?co-from=githubns)
2. **API Keys**: [https://www.nexscope.ai/seller/integrations?tab=api-keys](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubns)
3. **GitHub Issues**: [https://github.com/nexscope-ai/nexscope-ecommerce-skills/issues](https://github.com/nexscope-ai/nexscope-ecommerce-skills/issues)

## 📈 Skill Performance

### Processing Power
- **34 Production Skills** covering complete e-commerce workflow
- **Real-time API** integration with sub-second response
- **Multi-platform Support** for Amazon, TikTok, Temu, and more
- **Advanced AI** powered by Nexscope's e-commerce intelligence

### Data Sources
- **Real-time Market Data** from major e-commerce platforms
- **Patent Database** integration for IP risk analysis  
- **Review Intelligence** across platforms and regions
- **Pricing Intelligence** with historical trend analysis
- **Keyword Intelligence** with search volume and competition data

### Accuracy & Reliability
- **Production-tested** across thousands of products and markets
- **Continuously updated** with latest market intelligence
- **Enterprise-grade** reliability and performance
- **Global coverage** across major e-commerce markets

## 🚀 Advanced Usage

### Batch Processing
Many skills support batch analysis for efficiency:
```
"Analyze patent risks for these 10 product designs"
"Check keyword opportunities for these 20 products"
"Monitor prices for my entire product catalog"
```

### Cross-Platform Intelligence
Leverage skills across multiple platforms:
```
"Compare this product's performance on Amazon vs TikTok Shop"
"Find trending products on Temu that aren't on Amazon yet"
"Analyze keyword strategies across platforms"
```

### Automated Workflows
Chain skills together for comprehensive analysis:
```
1. Product Opportunity Finder → Find opportunities
2. Patent Risk Checker → Validate IP safety
3. Competitor Analyzer → Understand competition
4. Keyword Research → Optimize for search
5. Price Monitor → Track market dynamics
```

## 📊 Business Impact

### ROI Optimization
- **Reduce Research Time** from days to minutes
- **Identify Opportunities** others miss with AI-powered analysis
- **Avoid Legal Risks** with comprehensive IP screening
- **Optimize Pricing** with real-time market intelligence
- **Stay Competitive** with automated monitoring and alerts

### Strategic Advantages
- **Data-Driven Decisions** based on real market intelligence
- **First-Mover Advantage** with trend discovery and monitoring
- **Risk Mitigation** through comprehensive analysis and screening
- **Scalable Intelligence** that grows with your business

## 🔗 Resources

- **🌐 Nexscope Platform**: [https://www.nexscope.ai](https://www.nexscope.ai?co-from=githubns)
- **📚 Skills Documentation**: [https://www.nexscope.ai/help/skills-external-access](https://www.nexscope.ai/help/skills-external-access?co-from=githubns)
- **🔑 API Keys**: [https://www.nexscope.ai/seller/integrations?tab=api-keys](https://www.nexscope.ai/seller/integrations?tab=api-keys&co-from=githubns)
- **🐙 GitHub Repository**: [https://github.com/nexscope-ai/nexscope-ecommerce-skills](https://github.com/nexscope-ai/nexscope-ecommerce-skills)

---

## License

These skills are proprietary software owned by Nexscope. Usage requires a valid Nexscope API key and active subscription.

**© 2026 Nexscope AI** - Advanced E-commerce Intelligence Platform

---

*Transform your AI agent into an e-commerce expert. Get your API key and start analyzing markets, products, and opportunities with professional-grade intelligence.*