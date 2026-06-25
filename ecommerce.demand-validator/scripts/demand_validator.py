#!/usr/bin/env python3
"""
Demand Validator v2.0.0

Validate if demand is real and stable using multi-source verification.
Answers: "Is this market's demand real or inflated?"

Data Sources:
1. SOV API - Search volume (via NexScope proxy)
2. Amazon Search API - Sales estimates
3. Keepa Deep - BSR trends, seasonality, seller count
4. ABA (Amazon Brand Analytics) - Search Frequency Rank, Click Share
5. eBay Sold Listings - Cross-platform demand verification
6. TikTok Shop - Social commerce signals

Usage:
    python3 demand_validator.py '{"keyword": "yoga mat"}'
    python3 demand_validator.py '{"keyword": "air fryer"}' --chart /tmp/charts
"""

import json
import sys
import os
from typing import Optional, List
from urllib.request import Request, urlopen
import statistics

# --- Shared chart styling (from display-rules.md via chart_style.json) ---
try:
    from ecommerce_chart_helpers import load_style, apply_style, save_chart, get_color, get_palette, get_bar_kwargs, get_font_size, setup_plt
except ImportError:
    # Fallback if shared module not available
    def load_style(**kw): return {}
    def apply_style(ax, style=None): pass
    def save_chart(fig, path, style=None):
        import matplotlib.pyplot as _p; fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white'); _p.close(fig)
    def get_color(key, style=None): return '#90A4AE'
    def get_palette(n=8, style=None): return ['#2196F3','#4CAF50','#FF9800','#EF5350','#9C27B0','#00BCD4','#795548','#607D8B'][:n]
    def get_bar_kwargs(style=None): return {'edgecolor':'white','linewidth':1.5}
    def get_font_size(el='label', style=None): return 10
    def setup_plt(style=None): pass
# --- End shared chart styling ---

# === Configuration ===

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

DOMAIN_MAP = {
    'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5,
    'CA': 6, 'IT': 8, 'ES': 9, 'MX': 11, 'AU': 13
}

JS_MARKETPLACE_MAP = {
    'US': 'us', 'UK': 'uk', 'DE': 'de', 'FR': 'fr', 'JP': 'jp',
    'CA': 'ca', 'IT': 'it', 'ES': 'es', 'MX': 'mx'
}

# === API Functions ===

def api_call(endpoint: str, payload: dict) -> Optional[dict]:
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(payload).encode('utf-8'),
                         headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                                  'Content-Type': 'application/json'},
                         method='POST')
    try:
        with urlopen(_proxy_req, timeout=60) as _proxy_resp:
            _proxy_result = json.loads(_proxy_resp.read().decode('utf-8'))
        if isinstance(_proxy_result, dict) and 'code' in _proxy_result:
            return _proxy_result.get('data', _proxy_result) if _proxy_result.get('code') == 0 else None
        return _proxy_result
    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        return None

def _fetch_aba_data(keyword: str, region: str = 'US') -> Optional[dict]:
    """Fetch ABA (Brand Analytics) data via direct API call.
    
    API returns table format:
    {"tables": [{"data": [{"reportstartdate": "...", "searchFrequencyRank": "485"}, ...]}]}
    """
    try:
        result = api_call('/aba/intelligentQuery', {
            'analysisDescription': f'Get search frequency rank trend for {keyword} over past 12 weeks',
            'region': region
        })
        if not result:
            return None

        # Parse table-format response: tables[0].data contains rows with searchFrequencyRank
        tables = result.get('tables', [])
        if not tables or not isinstance(tables, list):
            return None
        
        table_data = tables[0].get('data', []) if isinstance(tables[0], dict) else []
        if not table_data:
            return None

        # Extract SFR values from time series (use most recent week)
        sfr = None
        sfr_trend = []
        for row in table_data:
            if isinstance(row, dict):
                rank = row.get('searchFrequencyRank')
                if rank is not None:
                    try:
                        sfr_trend.append(int(rank))
                    except (ValueError, TypeError):
                        pass
        
        # Use the most recent value as current SFR
        if sfr_trend:
            sfr = sfr_trend[-1]

        # Classify volume tier based on SFR
        volume_tier = 'UNKNOWN'
        if sfr:
            if sfr <= 1000: volume_tier = 'VERY_HIGH'
            elif sfr <= 5000: volume_tier = 'HIGH'
            elif sfr <= 20000: volume_tier = 'MEDIUM'
            elif sfr <= 100000: volume_tier = 'LOW'
            else: volume_tier = 'VERY_LOW'

        # Calculate SFR trend direction
        sfr_direction = 'STABLE'
        if len(sfr_trend) >= 4:
            early_avg = sum(sfr_trend[:4]) / 4
            recent_avg = sum(sfr_trend[-4:]) / 4
            # Lower SFR = higher rank = more popular
            if early_avg > 0:
                change = (early_avg - recent_avg) / early_avg
                if change > 0.15: sfr_direction = 'RISING'  # rank improving
                elif change < -0.15: sfr_direction = 'DECLINING'  # rank dropping

        # Fetch click share data (separate query)
        top_asins = []
        concentration = 'UNKNOWN'
        try:
            cs_result = api_call('/aba/intelligentQuery', {
                'analysisDescription': f'Get top 3 clicked ASINs and click share percentage for keyword {keyword} in the most recent week',
                'region': region
            })
            if cs_result:
                cs_tables = cs_result.get('tables', [])
                if cs_tables and isinstance(cs_tables, list):
                    cs_data = cs_tables[0].get('data', []) if isinstance(cs_tables[0], dict) else []
                    for row in cs_data:
                        if isinstance(row, dict):
                            asin = row.get('clickedasin', '')
                            share = float(row.get('clickShare', 0) or 0) * 100  # Convert to percentage
                            name = row.get('clickeditemname', '')
                            if asin:
                                top_asins.append({'asin': asin, 'share': round(share, 2), 'title': name[:60]})
                    # Determine market concentration from click share
                    if top_asins:
                        top_share = top_asins[0].get('share', 0)
                        total_top3 = sum(a.get('share', 0) for a in top_asins[:3])
                        if top_share > 30: concentration = 'MONOPOLY'
                        elif total_top3 > 40: concentration = 'CONCENTRATED'
                        else: concentration = 'FRAGMENTED'
        except Exception as e:
            print(f"    ⚠️ ABA click share fetch error: {e}", file=sys.stderr)

        return {
            'search_frequency_rank': sfr,
            'search_volume_tier': volume_tier,
            'sfr_trend': sfr_trend,
            'sfr_direction': sfr_direction,
            'market_concentration': {'level': concentration},
            'top_asins': top_asins
        }
    except Exception as e:
        print(f"  ABA fetch error: {e}", file=sys.stderr)
        return None

def _fetch_ebay_sold(keyword: str) -> Optional[dict]:
    """Fetch eBay sold listings via direct API call"""
    try:
        result = api_call('/ebay/search', {
            'keyword': keyword,
            'ebayDomain': 'ebay.com',
            'pageSize': 50,
            'showOnly': 'Sold'
        })
        if not result:
            return None
        products = result.get('products', []) if isinstance(result, dict) else result if isinstance(result, list) else []
        new_items = [p for p in products if (p.get('condition', '') or '').lower() in ('new', '')]
        prices = [p.get('price', 0) or 0 for p in new_items if (p.get('price', 0) or 0) > 0]
        sold_count = len(products)
        if sold_count >= 20: demand_level = 'HIGH'
        elif sold_count >= 10: demand_level = 'MEDIUM'
        elif sold_count > 0: demand_level = 'LOW'
        else: demand_level = 'NONE'
        return {
            'has_sales': sold_count > 0,
            'sold_count': sold_count,
            'demand_level': demand_level,
            'demand_verified': sold_count >= 10,
            'price_range': {
                'avg': sum(prices) / len(prices) if prices else 0,
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0
            }
        }
    except Exception as e:
        print(f"  eBay sold fetch error: {e}", file=sys.stderr)
        return None

def _fetch_tiktok_sales(keyword: str) -> Optional[dict]:
    """Fetch TikTok Shop data via direct API call"""
    try:
        result = api_call('/echotik/listProduct', {
            'keyword': keyword,
            'region': 'US',
            'minTotalSale30dCnt': 50,
            'pageSize': 30
        })
        if not result:
            return None
        products = result.get('products', result.get('data', []))
        if not isinstance(products, list):
            products = []
        product_count = len(products)
        total_sales = sum(int(p.get('totalSale30dCnt', p.get('sales', 0)) or 0) for p in products)
        total_gmv = sum(float(p.get('gmv30d', p.get('revenue', 0)) or 0) for p in products)
        if product_count >= 20 and total_sales >= 1000:
            opportunity, signal = 'HOT', 'Strong social commerce category'
        elif product_count >= 10 and total_sales >= 200:
            opportunity, signal = 'GROWING', 'Emerging social commerce presence'
        elif product_count > 0:
            opportunity, signal = 'EARLY', 'Limited social commerce activity'
        else:
            opportunity, signal = 'NONE', 'No social commerce presence'
        return {
            'has_presence': product_count > 0,
            'product_count': product_count,
            'total_sales': total_sales,
            'estimated_gmv': total_gmv,
            'opportunity': opportunity,
            'signal': signal
        }
    except Exception as e:
        print(f"  TikTok fetch error: {e}", file=sys.stderr)
        return None

def _fetch_keepa_deep(asin: str, domain: int = 1) -> Optional[dict]:
    """Fetch Keepa deep analysis (BSR/seller/price trends) via direct API call"""
    try:
        result = api_call('/keepa/productSeries', {
            'asin': asin,
            'domain': str(domain),
            'days': 90,
            'showBsrMain': 1,
            'showSellerCount': 1,
            'showPrice': 1
        })
        if not result:
            return None

        def _analyze_series(data_key, invert=False):
            series = result.get(data_key, [])
            points = []
            if isinstance(series, list):
                for item in series:
                    if isinstance(item, dict) and 'points' in item:
                        points = [pt.get('y', pt.get('value', 0)) for pt in item['points'] if isinstance(pt, dict)]
                        break
                    elif isinstance(item, (int, float)):
                        points.append(item)
            if len(points) < 6:
                return None
            third = max(len(points) // 3, 1)
            early_avg = sum(points[:third]) / third
            recent_avg = sum(points[-third:]) / third
            if early_avg <= 0:
                return None
            change = (recent_avg - early_avg) / early_avg * 100
            if invert:
                trend = 'IMPROVING' if change < -15 else 'DECLINING' if change > 15 else 'STABLE'
                momentum = 'UP' if change < -10 else 'DOWN' if change > 10 else 'FLAT'
            else:
                trend = 'INCREASING' if change > 15 else 'DECREASING' if change < -15 else 'STABLE'
                momentum = 'UP' if change > 10 else 'DOWN' if change < -10 else 'FLAT'
            return {'trend': trend, 'momentum': momentum, 'change_pct': round(change, 1), 'current': round(recent_avg, 1)}

        bsr_data = _analyze_series('bsrMain', invert=True)
        seller_data = _analyze_series('sellerCount')
        price_data = _analyze_series('price')

        bsr = {}
        if bsr_data:
            bsr = {'trend': bsr_data['trend'], 'momentum': bsr_data['momentum'],
                   'sales_signal': 'STRONG' if bsr_data['trend'] == 'IMPROVING' else 'WEAK' if bsr_data['trend'] == 'DECLINING' else 'NEUTRAL'}
        sellers = {}
        if seller_data:
            current = seller_data['current']
            sellers = {'current': int(current), 'trend': seller_data['trend'],
                       'competition_signal': 'INTENSIFYING' if seller_data['trend'] == 'INCREASING' else 'EASING' if seller_data['trend'] == 'DECREASING' else 'STABLE',
                       'buybox_difficulty': 'HARD' if current > 10 else 'MEDIUM' if current > 5 else 'EASY'}
        price = {}
        if price_data:
            price = {'volatility_pct': abs(price_data['change_pct']), 'price_war_risk': 'HIGH' if price_data['trend'] == 'DECREASING' else 'LOW'}
        seasonality = {'detected': False, 'peak_months': []}
        if bsr_data and abs(bsr_data.get('change_pct', 0)) > 30:
            seasonality['detected'] = True
        return {'bsr': bsr, 'sellers': sellers, 'price': price, 'seasonality': seasonality}
    except Exception as e:
        print(f"  Keepa deep fetch error: {e}", file=sys.stderr)
        return None

def get_js_sov(keyword: str, market: str = 'US') -> Optional[dict]:
    """Get Share of Voice data (includes search volume) via proxy"""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    marketplace = JS_MARKETPLACE_MAP.get(market, 'us')
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/share-of-voice"
    payload = {'keyword': keyword, 'marketplace': marketplace}
    try:
        req = Request(url, data=json.dumps(payload).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if isinstance(raw, dict) and raw.get('code') == 0:
            data = raw.get('data', {})
            if isinstance(data, dict) and 'code' in data:
                data = data.get('data', {})
            # SOV response nests volume under shareOfVoice — merge up for easy access
            if isinstance(data, dict) and 'shareOfVoice' in data:
                sov = data['shareOfVoice']
                if isinstance(sov, dict):
                    data = {**data, **sov}
            return data
    except Exception as e:
        print(f"SOV API Error: {e}", file=sys.stderr)
    return None

def search_products(keyword: str, market: str = 'US', limit: int = 60) -> List[dict]:
    """Search Amazon products with sales estimates"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(market, 'amazon.com')
    })
    
    if result and isinstance(result, list):
        return result
    elif result and 'products' in result:
        return result['products']
    return []

# === Analysis Functions ===

def calculate_demand_metrics(search_volume: int, total_sales: int, total_revenue: float) -> dict:
    """Calculate demand validation metrics"""
    if search_volume == 0:
        return {
            'search_to_sale_ratio': 0,
            'revenue_per_search': 0,
            'buying_intent': 'UNKNOWN'
        }
    
    ssr = (total_sales / search_volume) * 100
    rps = total_revenue / search_volume if search_volume > 0 else 0
    
    # Classify buying intent
    if ssr > 5:
        buying_intent = 'HIGH'
    elif ssr > 2:
        buying_intent = 'MODERATE'
    elif ssr > 0.5:
        buying_intent = 'LOW'
    else:
        buying_intent = 'VERY_LOW'
    
    return {
        'search_to_sale_ratio': round(ssr, 2),
        'revenue_per_search': round(rps, 2),
        'buying_intent': buying_intent
    }

def classify_demand_reality(ssr: float, stability_score: int) -> dict:
    """Classify demand reality based on SSR and stability"""
    # Base score from SSR
    if ssr > 5:
        base_score = 80
    elif ssr > 2:
        base_score = 60
    elif ssr > 0.5:
        base_score = 40
    else:
        base_score = 20
    
    # Adjust for stability
    score = base_score + (stability_score - 50) * 0.4
    score = max(0, min(100, score))
    
    # Classify level
    if score >= 70:
        level = 'VERIFIED'
        emoji = '🟢'
    elif score >= 50:
        level = 'MODERATE'
        emoji = '🟡'
    elif score >= 30:
        level = 'QUESTIONABLE'
        emoji = '🟠'
    else:
        level = 'WEAK'
        emoji = '🔴'
    
    return {
        'score': round(score),
        'level': level,
        'emoji': emoji
    }

def analyze_stability(sales_list: List[int]) -> dict:
    """Analyze sales distribution stability"""
    if not sales_list or len(sales_list) < 5:
        return {
            'sales_distribution': 'INSUFFICIENT_DATA',
            'top_10_share': 0,
            'variance_level': 'UNKNOWN',
            'stability_score': 50
        }
    
    total_sales = sum(sales_list)
    if total_sales == 0:
        return {
            'sales_distribution': 'NO_SALES',
            'top_10_share': 0,
            'variance_level': 'UNKNOWN',
            'stability_score': 20
        }
    
    # Sort descending
    sorted_sales = sorted(sales_list, reverse=True)
    
    # Top 10 share
    top_10_sales = sum(sorted_sales[:10])
    top_10_share = (top_10_sales / total_sales) * 100
    
    # Variance analysis
    if len(sales_list) > 1:
        mean_sales = statistics.mean(sales_list)
        std_sales = statistics.stdev(sales_list) if len(sales_list) > 1 else 0
        cv = (std_sales / mean_sales * 100) if mean_sales > 0 else 0  # Coefficient of variation
    else:
        cv = 0
    
    # Classify distribution
    if top_10_share > 80:
        distribution = 'CONCENTRATED'
        dist_score = 30
    elif top_10_share > 60:
        distribution = 'MODERATE'
        dist_score = 50
    else:
        distribution = 'BALANCED'
        dist_score = 70
    
    # Variance level
    if cv > 150:
        variance_level = 'HIGH'
        var_score = 30
    elif cv > 100:
        variance_level = 'MODERATE'
        var_score = 50
    else:
        variance_level = 'LOW'
        var_score = 70
    
    # Stability score
    stability_score = (dist_score + var_score) // 2
    
    return {
        'sales_distribution': distribution,
        'top_10_share': round(top_10_share, 1),
        'variance_level': variance_level,
        'coefficient_of_variation': round(cv, 1),
        'stability_score': stability_score
    }

def detect_demand_pattern(ssr: float, search_volume: int, stability: dict) -> dict:
    """Detect the demand pattern"""
    if ssr > 5 and stability['stability_score'] > 50:
        return {
            'pattern': 'REAL_DEMAND',
            'emoji': '🟢',
            'description': 'Real Demand - High search + High conversion + Stable',
            'risk': 'LOW'
        }
    elif ssr < 1 and search_volume > 100000:
        return {
            'pattern': 'WINDOW_SHOPPERS',
            'emoji': '🟠',
            'description': 'Window Shoppers - High search but low purchase',
            'risk': 'HIGH'
        }
    elif ssr > 10 and search_volume < 50000:
        return {
            'pattern': 'HIDDEN_GEM',
            'emoji': '💎',
            'description': 'Hidden Gem - Low search but high conversion',
            'risk': 'LOW'
        }
    elif ssr < 0.5 and search_volume > 500000:
        return {
            'pattern': 'HYPE_MARKET',
            'emoji': '🎭',
            'description': 'Hype Market - False prosperity',
            'risk': 'VERY_HIGH'
        }
    elif stability['sales_distribution'] == 'CONCENTRATED':
        return {
            'pattern': 'MONOPOLIZED',
            'emoji': '👑',
            'description': 'Monopolized Market - Dominated by top players',
            'risk': 'MEDIUM'
        }
    else:
        return {
            'pattern': 'NORMAL',
            'emoji': '📊',
            'description': 'Normal Market - Further analysis needed',
            'risk': 'MEDIUM'
        }

def generate_insights(search_volume: int, total_sales: int, total_revenue: float,
                      demand_metrics: dict, reality_score: dict, stability: dict,
                      pattern: dict) -> dict:
    """Generate narrative insights"""
    ssr = demand_metrics['search_to_sale_ratio']
    
    # Summary
    if reality_score['level'] == 'VERIFIED':
        summary = f"✅ Real demand verified. Monthly searches {search_volume:,}, monthly sales {total_sales:,} units, conversion rate {ssr}%."
    elif reality_score['level'] == 'MODERATE':
        summary = f"🟡 Demand appears real but proceed with caution. Monthly searches {search_volume:,}, monthly sales {total_sales:,} units, conversion rate {ssr}%."
    elif reality_score['level'] == 'QUESTIONABLE':
        summary = f"⚠️ Demand questionable, deeper validation recommended. Monthly searches {search_volume:,}, monthly sales only {total_sales:,} units, conversion rate {ssr}%."
    else:
        summary = f"❌ Weak demand, entry not recommended. Monthly searches {search_volume:,}, monthly sales only {total_sales:,} units, conversion rate {ssr}%."
    
    # Demand reality assessment
    if ssr > 5:
        demand_reality = f"Search-to-purchase conversion rate {ssr}%, above industry benchmark (1-5%), indicating real buying demand."
    elif ssr > 1:
        demand_reality = f"Search-to-purchase conversion rate {ssr}%, within normal range (1-5%), demand is relatively genuine."
    else:
        demand_reality = f"Search-to-purchase conversion rate only {ssr}%, far below benchmark. Possible causes: browsing without buying, price sensitivity, informational searches."
    
    # Stability assessment
    if stability['stability_score'] > 60:
        stability_assessment = f"Sales distribution {stability['sales_distribution']}, Top 10 accounts for {stability['top_10_share']}%, market is relatively stable."
    elif stability['stability_score'] > 40:
        stability_assessment = f"Sales distribution {stability['sales_distribution']}, Top 10 accounts for {stability['top_10_share']}%, moderate stability."
    else:
        stability_assessment = f"Sales distribution {stability['sales_distribution']}, Top 10 accounts for {stability['top_10_share']}%, market is unstable with higher risk."
    
    # Recommendations
    recommendations = []
    
    if reality_score['level'] in ['VERIFIED', 'MODERATE']:
        recommendations.append("✅ Demand verified, proceed to analyze competition and entry barriers")
    
    if pattern['pattern'] == 'WINDOW_SHOPPERS':
        recommendations.append("⚠️ High search but low conversion, investigate why: price? quality? trust?")
    
    if pattern['pattern'] == 'HIDDEN_GEM':
        recommendations.append("💎 Low visibility but high conversion market, likely repeat-purchase or word-of-mouth driven, worth deeper analysis")
    
    if pattern['pattern'] == 'HYPE_MARKET':
        recommendations.append("🎭 Hype market with high risk, recommend waiting for the hype to cool before re-evaluating")
    
    if stability['sales_distribution'] == 'CONCENTRATED':
        recommendations.append("👑 Market dominated by top players, new entrants need a differentiation strategy")
    
    if not recommendations:
        recommendations.append("📊 Recommend combining review threshold and brand concentration for a comprehensive assessment")
    
    return {
        'summary': summary,
        'demand_reality': demand_reality,
        'stability_assessment': stability_assessment,
        'pattern_insight': f"{pattern['emoji']} {pattern['description']}",
        'risk_level': pattern['risk'],
        'recommendations': recommendations
    }

# === Main Analysis Function ===

def validate_demand(keyword: str, market: str = 'US', limit: int = 60) -> dict:
    """
    Main analysis function
    
    Args:
        keyword: Search keyword
        market: Marketplace (US, UK, DE, etc.)
        limit: Number of products to analyze
    
    Returns:
        Complete demand validation analysis
    """
    print(f"Validating demand for: {keyword}", file=sys.stderr)
    
    # Step 1: Get search volume
    print("[1/3] Fetching search volume (SOV API)...", file=sys.stderr)
    sov_data = get_js_sov(keyword, market)
    
    search_volume = 0
    if sov_data:
        search_volume = (sov_data.get('estimated30DaySearchVolume')
                         or sov_data.get('estimated_30_day_search_volume')
                         or 0)
        print(f"  ✓ Search volume: {search_volume:,}", file=sys.stderr)
    else:
        print("  ⚠️ SOV data not available, using fallback", file=sys.stderr)
    
    # Step 2: Get sales data from Amazon Search
    print("[2/3] Fetching sales data (Amazon Search)...", file=sys.stderr)
    products = search_products(keyword, market, limit)
    
    if not products:
        return {'error': 'No products found', 'keyword': keyword}
    
    print(f"  ✓ Got {len(products)} products", file=sys.stderr)
    
    # Step 2.5: Clean products (filter noise categories)
    cleaning_report = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        shared_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'shared')
        from category_cleaner import clean_products, format_category_report
        
        products, cleaning_report = clean_products(products, keyword)
        if cleaning_report.get('removed_count', 0) > 0:
            print(format_category_report(cleaning_report), file=sys.stderr)
            print(f"  ✓ Cleaned to {len(products)} products", file=sys.stderr)
    except ImportError:
        pass  # Category cleaner not available
    except Exception as e:
        print(f"  ⚠️ Category cleaning skipped: {e}", file=sys.stderr)
    
    # Step 3: Aggregate sales data
    print("[3/3] Analyzing demand metrics...", file=sys.stderr)
    
    total_sales = 0
    total_revenue = 0
    sales_list = []
    products_with_sales = []
    
    for p in products:
        monthly_sales = p.get('monthlySalesUnits', 0) or 0
        if isinstance(monthly_sales, str):
            monthly_sales = int(monthly_sales.replace(',', '')) if monthly_sales.replace(',', '').isdigit() else 0
        
        price = p.get('extractedPrice') or p.get('price', 0) or 0
        revenue = monthly_sales * price
        
        total_sales += monthly_sales
        total_revenue += revenue
        sales_list.append(monthly_sales)
        
        products_with_sales.append({
            'asin': p.get('asin'),
            'title': p.get('title'),
            'monthly_sales': monthly_sales,
            'price': price,
            'revenue': revenue,
            'reviews': p.get('ratings', 0),
            'rating': p.get('rating')
        })
    
    # Calculate metrics
    demand_metrics = calculate_demand_metrics(search_volume, total_sales, total_revenue)
    stability = analyze_stability(sales_list)
    reality_score = classify_demand_reality(demand_metrics['search_to_sale_ratio'], stability['stability_score'])
    pattern = detect_demand_pattern(demand_metrics['search_to_sale_ratio'], search_volume, stability)
    insights = generate_insights(search_volume, total_sales, total_revenue, demand_metrics, reality_score, stability, pattern)
    
    # Sort products by sales
    products_with_sales.sort(key=lambda x: x['monthly_sales'], reverse=True)
    
    result = {
        'keyword': keyword,
        'marketplace': market,
        'products_analyzed': len(products),
        
        'search_data': {
            'monthly_search_volume': search_volume,
            'source': 'jungle_scout_sov' if sov_data else 'unavailable'
        },
        
        'sales_data': {
            'total_monthly_units': total_sales,
            'total_monthly_revenue': round(total_revenue, 2),
            'avg_sales_per_product': round(total_sales / len(products), 1) if products else 0,
            'avg_revenue_per_product': round(total_revenue / len(products), 2) if products else 0
        },
        
        'demand_metrics': demand_metrics,
        
        'reality_score': reality_score,
        
        'stability_analysis': stability,
        
        'demand_pattern': pattern,
        
        'insights': insights,
        
        'top_products': [
            {
                'asin': p['asin'],
                'title': (p['title'][:50] + '...') if p.get('title') and len(p['title']) > 50 else p.get('title'),
                'monthly_sales': p['monthly_sales'],
                'price': p['price'],
                'revenue': round(p['revenue'], 2)
            }
            for p in products_with_sales[:10]
        ]
    }
    
    # Add cleaning report if available
    if cleaning_report and cleaning_report.get('removed_count', 0) > 0:
        result['category_cleaning'] = {
            'applied': True,
            'target_category': cleaning_report.get('target_category'),
            'original_count': cleaning_report.get('original_count'),
            'removed_count': cleaning_report.get('removed_count'),
            'noise_categories': [n['category'] for n in cleaning_report.get('noise_removed', [])]
        }
    
    # === Enhanced Data Sources (v2.0.0) ===
    result['cross_platform_validation'] = {}
    enhanced_insights = []
    confidence_boost = 0

    # ABA Data
    print("[+] Fetching ABA (Brand Analytics) data...", file=sys.stderr)
    try:
        aba = _fetch_aba_data(keyword, market)
        if aba and 'error' not in aba:
            result['cross_platform_validation']['aba'] = {
                'search_frequency_rank': aba.get('search_frequency_rank'),
                'volume_tier': aba.get('search_volume_tier'),
                'market_concentration': (aba.get('market_concentration') or {}).get('level'),
                'top_asins': aba.get('top_asins', [])[:3]
            }
            if aba.get('search_volume_tier') in ['VERY_HIGH', 'HIGH']:
                enhanced_insights.append('✅ ABA confirms high search demand')
                confidence_boost += 15
            if (aba.get('market_concentration') or {}).get('level') == 'FRAGMENTED':
                enhanced_insights.append('🎯 ABA shows fragmented market - easier entry')
                confidence_boost += 10
            print(f"    ✓ ABA: SFR {aba.get('search_frequency_rank')}", file=sys.stderr)
    except Exception as e:
        print(f"    ⚠️ ABA unavailable: {e}", file=sys.stderr)

    # eBay Sold Listings
    print("[+] Fetching eBay sold listings...", file=sys.stderr)
    try:
        ebay = _fetch_ebay_sold(keyword)
        if ebay and ebay.get('has_sales'):
            result['cross_platform_validation']['ebay'] = {
                'sold_count': ebay.get('sold_count'),
                'demand_level': ebay.get('demand_level'),
                'avg_price': (ebay.get('price_range') or {}).get('avg'),
                'demand_verified': ebay.get('demand_verified')
            }
            if ebay.get('demand_verified'):
                enhanced_insights.append('✅ eBay sold listings confirm real demand')
                confidence_boost += 20
            else:
                enhanced_insights.append('⚠️ Low eBay sales - verify demand carefully')
            print(f"    ✓ eBay: {ebay.get('sold_count')} sold items", file=sys.stderr)
        else:
            result['cross_platform_validation']['ebay'] = {'has_sales': False}
            enhanced_insights.append('⚠️ No eBay sold listings found')
            print(f"    ⚠️ No eBay sales data", file=sys.stderr)
    except Exception as e:
        print(f"    ⚠️ eBay unavailable: {e}", file=sys.stderr)

    # TikTok Shop
    print("[+] Fetching TikTok Shop data...", file=sys.stderr)
    try:
        tiktok = _fetch_tiktok_sales(keyword)
        if tiktok and tiktok.get('has_presence'):
            result['cross_platform_validation']['tiktok'] = {
                'product_count': tiktok.get('product_count'),
                'total_sales': tiktok.get('total_sales'),
                'opportunity': tiktok.get('opportunity'),
                'signal': tiktok.get('signal')
            }
            if tiktok.get('opportunity') in ['HOT', 'GROWING']:
                enhanced_insights.append(f"📱 TikTok: {tiktok.get('opportunity')} - {tiktok.get('signal')}")
                confidence_boost += 10
            print(f"    ✓ TikTok: {tiktok.get('total_sales')} sales, {tiktok.get('opportunity')}", file=sys.stderr)
        else:
            result['cross_platform_validation']['tiktok'] = {'has_presence': False}
            print(f"    ⚠️ No TikTok presence", file=sys.stderr)
    except Exception as e:
        print(f"    ⚠️ TikTok unavailable: {e}", file=sys.stderr)

    # Keepa Deep (for top product)
    if products_with_sales:
        top_asin = products_with_sales[0].get('asin')
        if top_asin:
            print(f"[+] Fetching Keepa deep data for {top_asin}...", file=sys.stderr)
            try:
                keepa = _fetch_keepa_deep(top_asin, DOMAIN_MAP.get(market, 1))
                if keepa and 'error' not in keepa:
                    result['cross_platform_validation']['keepa'] = {
                        'bsr_trend': (keepa.get('bsr') or {}).get('trend'),
                        'bsr_momentum': (keepa.get('bsr') or {}).get('momentum'),
                        'seasonality': (keepa.get('seasonality') or {}).get('detected'),
                        'peak_months': (keepa.get('seasonality') or {}).get('peak_months', []),
                        'seller_competition': (keepa.get('sellers') or {}).get('competition_signal')
                    }
                    if (keepa.get('bsr') or {}).get('trend') == 'IMPROVING':
                        enhanced_insights.append('📈 Keepa: BSR improving - demand growing')
                        confidence_boost += 15
                    if (keepa.get('seasonality') or {}).get('detected'):
                        peaks = ', '.join((keepa.get('seasonality') or {}).get('peak_months', []))
                        enhanced_insights.append(f"📅 Seasonal product - peaks: {peaks}")
                    print(f"    ✓ Keepa: BSR {(keepa.get('bsr') or {}).get('trend')}", file=sys.stderr)
            except Exception as e:
                print(f"    ⚠️ Keepa unavailable: {e}", file=sys.stderr)

    # Add enhanced insights to result
    if enhanced_insights:
        result['enhanced_validation'] = {
            'insights': enhanced_insights,
            'confidence_boost': confidence_boost,
            'sources_checked': list(result['cross_platform_validation'].keys())
        }
        original_confidence = (result.get('reality_score') or {}).get('score', 50)
        result['reality_score']['cross_platform_confidence'] = min(100, original_confidence + confidence_boost)

    return result

# === Chart Generation ===

def generate_charts(result: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        import numpy as np
    except ImportError:
        print("matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    keyword = result.get('keyword', 'Unknown')
    search_volume = (result.get('search_data') or {}).get('monthly_search_volume', 0)
    total_sales = (result.get('sales_data') or {}).get('total_monthly_units', 0)
    ssr = (result.get('demand_metrics') or {}).get('search_to_sale_ratio', 0)
    reality_score = result.get('reality_score', {})
    
    # Colors
    SEARCH_COLOR = get_color('primary')
    SALES_COLOR = get_color('good')
    WARNING = get_color('secondary')
    BAD = get_color('hot')
    
    # Chart 1: Search vs Sales Comparison
    if not (search_volume or total_sales):
        print(f"  ⚠️ 1_search_vs_sales.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Search Volume\n(Monthly)', 'Sales Volume\n(Monthly)']
        values = [search_volume, total_sales]
        colors = [SEARCH_COLOR, SALES_COLOR]

        bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)

        ax.set_ylabel('Volume', fontsize=11)
        ax.set_title(f'SEARCH VS SALES: {keyword.upper()}', fontweight='bold', fontsize=13, pad=15)

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.02,
                    f'{val:,}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Add SSR annotation
        ax.annotate(f'Search-to-Sale Ratio: {ssr}%', xy=(0.95, 0.95), xycoords='axes fraction',
                    ha='right', va='top', fontsize=11,
                    bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, max(values) * 1.15)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_search_vs_sales.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Search vs Sales", file=sys.stderr)
    
    # Chart 2: Sales Distribution
    top_products = result.get('top_products', [])
    if top_products:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        names = [f"#{i+1}" for i in range(len(top_products[:10]))]
        sales = [p.get('monthly_sales', 0) for p in top_products[:10]]
        
        colors = [SALES_COLOR if s > 0 else '#BDBDBD' for s in sales]
        bars = ax.bar(names, sales, color=colors, edgecolor='white', linewidth=2)
        
        ax.set_ylabel('Monthly Sales (Units)', fontsize=11)
        ax.set_xlabel('Product Rank', fontsize=11)
        ax.set_title(f'TOP 10 SALES DISTRIBUTION: {keyword.upper()}', fontweight='bold', fontsize=13, pad=15)
        
        # Add value labels
        for bar, val in zip(bars, sales):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(sales)*0.02,
                        f'{val:,}', ha='center', va='bottom', fontsize=9, rotation=45)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_sales_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Sales Distribution", file=sys.stderr)
    
    # Chart 3: Reality Score Gauge
    if not reality_score:
        print(f"  ⚠️ 3_reality_score.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(8, 6))

        score = reality_score.get('score', 50)
        level = reality_score.get('level', 'MODERATE')

        # Create gauge
        colors_gauge = [get_color('hot'), get_color('secondary'), get_color('warning'), get_color('good')]
        labels_gauge = ['WEAK\n(0-30)', 'QUESTION\n(30-50)', 'MODERATE\n(50-70)', 'VERIFIED\n(70-100)']
        ranges = [30, 20, 20, 30]
        starts = [0, 30, 50, 70]

        for i, (start, width, color, label) in enumerate(zip(starts, ranges, colors_gauge, labels_gauge)):
            ax.barh(0, width, left=start, height=0.3, color=color, edgecolor='white', linewidth=2)
            ax.text(start + width/2, -0.25, label, ha='center', va='top', fontsize=9)

        # Add score marker
        ax.scatter([score], [0], s=300, c='black', marker='^', zorder=5)
        ax.text(score, 0.25, f'Score: {score}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_xlim(-5, 105)
        ax.set_ylim(-0.8, 0.6)
        ax.set_title(f'DEMAND REALITY SCORE: {level}', fontweight='bold', fontsize=13, pad=15)
        ax.axis('off')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_reality_score.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Reality Score", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 demand_validator.py '{\"keyword\": \"yoga mat\"}' [--chart <dir>]", file=sys.stderr)
        sys.exit(1)
    
    # Parse input
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(f"Invalid JSON: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    if not keyword:
        print("Missing required parameter: keyword", file=sys.stderr)
        sys.exit(1)
    
    market = params.get('market', 'US')
    limit = params.get('limit', 60)
    
    # Check for chart flag
    chart_dir = None
    if '--chart' in sys.argv:
        chart_idx = sys.argv.index('--chart')
        if chart_idx + 1 < len(sys.argv):
            chart_dir = sys.argv[chart_idx + 1]
    
    # Run analysis
    result = validate_demand(keyword, market, limit)
    
    # Generate charts if requested
    if chart_dir and 'error' not in result:
        print(f"Generating charts in {chart_dir}...", file=sys.stderr)
        result['charts'] = generate_charts(result, chart_dir) or []
    
    # Output result
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
