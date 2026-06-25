#!/usr/bin/env python3
"""
Price History Analyzer v2.0.0

Analyze price wars, volatility, Buy Box stability, and competition trends using KEEPA deep data.
Answers: "Is there a price war?", "Are prices stable?", "Can I win Buy Box?", "Is competition increasing?"

Data Sources:
1. Keepa Deep API - Price history, BSR trends, Seller count, Review growth
2. Amazon Search - Current prices, product list

New in v2.0.0:
- BSR trend analysis (sales momentum)
- Seller count history (competition intensity)
- Seasonality detection
- Competition intensity tracking

Usage:
    python3 price_history_analyzer.py '{"keyword": "face wash"}'
    python3 price_history_analyzer.py '{"asin": "B07RL88DD2"}'
"""

import json
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
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

DOMAIN_MAP = {'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5, 'CA': 6, 'IT': 8, 'ES': 9, 'MX': 11, 'AU': 13}

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
    with urlopen(_proxy_req, timeout=60) as _proxy_resp:
        _proxy_result = json.loads(_proxy_resp.read().decode('utf-8'))
    if isinstance(_proxy_result, dict) and 'code' in _proxy_result:
        return _proxy_result.get('data', _proxy_result) if _proxy_result.get('code') == 0 else None
    return _proxy_result

def _fetch_keepa_deep(asin: str, domain: int = 1, preloaded: dict = None) -> Optional[dict]:
    """Fetch Keepa deep analysis (BSR/seller/price trends). Uses preloaded data if provided."""
    try:
        if preloaded is not None:
            result = preloaded
        else:
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
                    elif isinstance(item, dict) and 'value' in item:
                        v = item.get('value')
                        if isinstance(v, (int, float)):
                            points.append(v)
                    elif isinstance(item, (int, float)):
                        points.append(item)
            if len(points) < 3:
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
            bsr = {
                'trend': bsr_data['trend'],
                'momentum': bsr_data['momentum'],
                'sales_signal': 'STRONG' if bsr_data['trend'] == 'IMPROVING' else 'WEAK' if bsr_data['trend'] == 'DECLINING' else 'NEUTRAL'
            }
        sellers = {}
        if seller_data:
            current = seller_data['current']
            sellers = {
                'current': int(current),
                'trend': seller_data['trend'],
                'competition_signal': 'INTENSIFYING' if seller_data['trend'] == 'INCREASING' else 'EASING' if seller_data['trend'] == 'DECREASING' else 'STABLE',
                'buybox_difficulty': 'HARD' if current > 10 else 'MEDIUM' if current > 5 else 'EASY'
            }
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

def search_products(keyword: str, market: str = 'US', limit: int = 20) -> List[dict]:
    """Search Amazon products"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(market, 'amazon.com')
    })
    
    if result and 'products' in result:
        return result['products']
    elif result and 'data' in result:
        return result['data'] if isinstance(result['data'], list) else []
    elif result and isinstance(result, list):
        return result
    return []

def get_keepa_series(asin: str, domain: int = 1) -> Optional[dict]:
    """Get Keepa product series data (price history, BSR, etc.)"""
    result = api_call('/keepa/productSeries', {
        'asin': asin,
        'domain': str(domain),
        'days': 90,
        'showBsrMain': 1,
        'showSellerCount': 1,
        'showPrice': 1
    })
    return result

# === Analysis Functions ===

def analyze_price_history(buybox_data: List[dict], days: int = 90) -> dict:
    """Analyze price history from Keepa buyboxPrice data"""
    if not buybox_data:
        return {'error': 'No price history data'}
    
    # Parse and filter recent data
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_prices = []
    all_prices = []
    price_changes = []
    last_price = None
    
    for point in buybox_data:
        time_str = point.get('time', '')
        value = point.get('value', -1)
        
        if value <= 0:
            continue
        
        all_prices.append(value)
        
        # Parse date
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            if dt >= cutoff_date:
                recent_prices.append(value)
                
                # Track price changes
                if last_price is not None and last_price != value:
                    change_pct = ((value - last_price) / last_price) * 100
                    price_changes.append({
                        'time': time_str,
                        'from': last_price,
                        'to': value,
                        'change_pct': round(change_pct, 2)
                    })
                last_price = value
        except:
            pass
    
    if not recent_prices:
        recent_prices = all_prices[-30:] if all_prices else []
    
    if not recent_prices:
        return {'error': 'No valid price data'}
    
    # Calculate volatility
    mean_price = statistics.mean(recent_prices)
    std_dev = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
    pvi = (std_dev / mean_price * 100) if mean_price > 0 else 0
    
    # Classify volatility
    if pvi < 5:
        vol_level = 'LOW'
    elif pvi < 10:
        vol_level = 'MEDIUM'
    elif pvi < 20:
        vol_level = 'HIGH'
    else:
        vol_level = 'EXTREME'
    
    # Count price drops (potential price war indicator)
    price_drops = sum(1 for c in price_changes if c['change_pct'] < -3)
    price_increases = sum(1 for c in price_changes if c['change_pct'] > 3)
    
    # Calculate trend
    if len(recent_prices) >= 5:
        early_avg = statistics.mean(recent_prices[:len(recent_prices)//3])
        late_avg = statistics.mean(recent_prices[-len(recent_prices)//3:])
        trend_pct = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
    else:
        trend_pct = 0
    
    if trend_pct > 5:
        trend_dir = 'RISING'
    elif trend_pct > -5:
        trend_dir = 'STABLE'
    elif trend_pct > -15:
        trend_dir = 'DECLINING'
    else:
        trend_dir = 'CRASHED'
    
    return {
        'data_points': len(recent_prices),
        'period_days': days,
        'current_price': recent_prices[-1] if recent_prices else 0,
        'min_price': round(min(recent_prices), 2),
        'max_price': round(max(recent_prices), 2),
        'avg_price': round(mean_price, 2),
        'std_dev': round(std_dev, 2),
        'pvi': round(pvi, 1),
        'volatility_level': vol_level,
        'price_changes_count': len(price_changes),
        'price_drops': price_drops,
        'price_increases': price_increases,
        'trend_pct': round(trend_pct, 1),
        'trend_direction': trend_dir,
        'recent_changes': price_changes[-5:] if price_changes else []
    }

def analyze_buybox_stability(buybox_data: List[dict], days: int = 30) -> dict:
    """Analyze Buy Box price stability"""
    if not buybox_data:
        return {'stability': 'UNKNOWN', 'changes_per_day': 0}
    
    cutoff_date = datetime.now() - timedelta(days=days)
    changes = 0
    outages = 0
    
    for point in buybox_data:
        time_str = point.get('time', '')
        value = point.get('value', 0)
        
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            if dt >= cutoff_date:
                changes += 1
                if value <= 0:
                    outages += 1
        except:
            pass
    
    changes_per_day = changes / days if days > 0 else 0
    
    # Classify stability
    if changes_per_day < 0.5:
        stability = 'VERY_STABLE'
        stability_score = 90
    elif changes_per_day < 1:
        stability = 'STABLE'
        stability_score = 70
    elif changes_per_day < 2:
        stability = 'MODERATE'
        stability_score = 50
    elif changes_per_day < 5:
        stability = 'UNSTABLE'
        stability_score = 30
    else:
        stability = 'CHAOTIC'
        stability_score = 10
    
    return {
        'stability': stability,
        'stability_score': stability_score,
        'total_changes': changes,
        'changes_per_day': round(changes_per_day, 2),
        'outages': outages,
        'outage_pct': round(outages / changes * 100, 1) if changes > 0 else 0
    }

def calculate_price_war_score(price_analysis: dict, buybox_analysis: dict) -> dict:
    """Calculate overall price war score"""
    score = 0
    factors = {}
    
    # Volatility factor (0-35 points)
    pvi = price_analysis.get('pvi', 0)
    vol_score = min(pvi * 1.5, 35)
    factors['volatility'] = round(vol_score)
    score += vol_score
    
    # Trend factor (0-25 points)
    trend = price_analysis.get('trend_direction', 'STABLE')
    if trend == 'CRASHED':
        trend_score = 25
    elif trend == 'DECLINING':
        trend_score = 15
    else:
        trend_score = 0
    factors['trend'] = trend_score
    score += trend_score
    
    # Price drop frequency factor (0-25 points)
    drops = price_analysis.get('price_drops', 0)
    drop_score = min(drops * 3, 25)
    factors['price_drops'] = drop_score
    score += drop_score
    
    # Buy Box instability factor (0-15 points)
    bb_stability = buybox_analysis.get('stability_score', 50)
    bb_score = max(0, (100 - bb_stability) * 0.15)
    factors['buybox_instability'] = round(bb_score)
    score += bb_score
    
    # Classify level
    score = min(score, 100)
    if score < 25:
        level = 'LOW'
        emoji = '🟢'
    elif score < 50:
        level = 'MODERATE'
        emoji = '🟡'
    elif score < 75:
        level = 'HIGH'
        emoji = '🟠'
    else:
        level = 'SEVERE'
        emoji = '🔴'
    
    return {
        'score': round(score),
        'level': level,
        'emoji': emoji,
        'factors': factors
    }

def generate_insights(price_analysis: dict, buybox_analysis: dict, 
                      price_war: dict, monthly_sold: List[dict] = None) -> dict:
    """Generate narrative insights"""
    pws = price_war.get('score', 0)
    pvi = price_analysis.get('pvi', 0)
    trend = price_analysis.get('trend_direction', 'STABLE')
    drops = price_analysis.get('price_drops', 0)
    bb_stability = buybox_analysis.get('stability', 'UNKNOWN')
    
    # Summary
    if pws < 25:
        summary = f"🟢 Healthy pricing. Score {pws}, volatility {pvi:.1f}%. Safe market."
    elif pws < 50:
        summary = f"🟡 Moderate competition. Score {pws}, {drops} price drops detected."
    elif pws < 75:
        summary = f"🟠 Active price war! Score {pws}, volatility {pvi:.1f}%. Caution!"
    else:
        summary = f"🔴 Severe price war! Score {pws}. Avoid this market."
    
    # Detailed assessments
    assessments = []
    
    if pvi > 15:
        assessments.append(f"High volatility ({pvi:.1f}%) - prices swing significantly")
    elif pvi < 5:
        assessments.append(f"Low volatility ({pvi:.1f}%) - stable pricing")
    
    if drops > 5:
        assessments.append(f"{drops} price drops in period - active competition")
    
    if trend == 'DECLINING':
        assessments.append(f"Downward trend ({price_analysis.get('trend_pct', 0):+.1f}%) - margin erosion")
    elif trend == 'RISING':
        assessments.append(f"Upward trend ({price_analysis.get('trend_pct', 0):+.1f}%) - healthy market")
    
    if bb_stability == 'CHAOTIC':
        assessments.append("Buy Box extremely unstable - hard to win consistently")
    elif bb_stability == 'VERY_STABLE':
        assessments.append("Buy Box very stable - likely single dominant seller")
    
    # Recommendations
    recommendations = []
    
    if pws < 25:
        recommendations.append("✅ Pricing stable - normal competitive strategy viable")
    elif pws < 50:
        recommendations.append("⚠️ Monitor prices weekly, build margin buffer")
    else:
        recommendations.append("🔴 Avoid price competition - differentiate on value")
        recommendations.append("💡 Consider bundling or premium positioning")
    
    if trend == 'DECLINING':
        recommendations.append(f"📉 Factor declining prices into margin calculations")
    
    return {
        'summary': summary,
        'assessments': assessments,
        'recommendations': recommendations,
        'price_war_assessment': ' | '.join(assessments) if assessments else 'No major concerns'
    }

# === Main Analysis Function ===

def analyze_prices(keyword: str = None, asin: str = None, market: str = 'US') -> dict:
    """Main analysis function"""
    print(f"Analyzing prices for: {keyword or asin}", file=sys.stderr)
    
    domain = DOMAIN_MAP.get(market, 1)
    products = []
    asins_to_analyze = []
    
    if keyword:
        # Search products
        print("[1/3] Fetching products...", file=sys.stderr)
        products = search_products(keyword, market, 20)
        
        if not products:
            return {'error': 'No products found', 'keyword': keyword}
        
        # Apply category cleaning
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            shared_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'shared')
            from category_cleaner import clean_products
            products, _ = clean_products(products, keyword)
        except:
            pass
        
        print(f"  ✓ Got {len(products)} products", file=sys.stderr)
        asins_to_analyze = [p.get('asin') for p in products[:5] if p.get('asin')]
    
    elif asin:
        asins_to_analyze = [asin]
    
    # Get Keepa data
    print("[2/3] Fetching Keepa price history...", file=sys.stderr)
    keepa_results = []
    
    for i, a in enumerate(asins_to_analyze):
        print(f"  Fetching ASIN {i+1}/{len(asins_to_analyze)}: {a}...", file=sys.stderr)
        keepa = get_keepa_series(a, domain)
        if keepa and keepa.get('errcode') == 200:
            keepa_results.append({
                'asin': a,
                'data': keepa
            })
            print(f"    ✓ Got {len(keepa.get('buyboxPrice', []))} price points", file=sys.stderr)
    
    if not keepa_results:
        return {'error': 'No Keepa data available', 'keyword': keyword, 'asin': asin}
    
    # Analyze
    print("[3/3] Analyzing price patterns...", file=sys.stderr)
    
    # Collect monthly sold data
    all_monthly_sold = []
    for kr in keepa_results:
        all_monthly_sold.extend(kr['data'].get('monthlySold', []))

    # Per-product price analysis (avoid mixing prices from different products)
    product_price_analyses = []
    product_bb_analyses = []
    for kr in keepa_results:
        bp = kr['data'].get('buyboxPrice', [])
        if not bp:
            continue
        pa = analyze_price_history(bp, days=90)
        ba = analyze_buybox_stability(bp, days=30)
        if 'error' not in pa:
            product_price_analyses.append(pa)
            product_bb_analyses.append(ba)

    if not product_price_analyses:
        return {'error': 'No valid price data', 'keyword': keyword, 'asin': asin}

    # Weighted-average PVI across products
    total_pts = sum(a['data_points'] for a in product_price_analyses)
    agg_pvi = (sum(a['pvi'] * a['data_points'] for a in product_price_analyses) / total_pts) if total_pts > 0 else 0.0

    # Worst-case trend (most pessimistic signal)
    trend_order = {'CRASHED': 0, 'DECLINING': 1, 'STABLE': 2, 'RISING': 3}
    worst_pa = min(product_price_analyses, key=lambda a: trend_order.get(a['trend_direction'], 2))

    if agg_pvi < 5:
        vol_level = 'LOW'
    elif agg_pvi < 10:
        vol_level = 'MEDIUM'
    elif agg_pvi < 20:
        vol_level = 'HIGH'
    else:
        vol_level = 'EXTREME'

    price_analysis = {
        'data_points': total_pts,
        'period_days': 90,
        'current_price': product_price_analyses[0].get('current_price', 0),
        'min_price': round(min(a['min_price'] for a in product_price_analyses), 2),
        'max_price': round(max(a['max_price'] for a in product_price_analyses), 2),
        'avg_price': round(sum(a['avg_price'] * a['data_points'] for a in product_price_analyses) / total_pts, 2) if total_pts > 0 else 0,
        'std_dev': round(statistics.mean([a['std_dev'] for a in product_price_analyses]), 2),
        'pvi': round(agg_pvi, 1),
        'volatility_level': vol_level,
        'price_changes_count': sum(a['price_changes_count'] for a in product_price_analyses),
        'price_drops': sum(a['price_drops'] for a in product_price_analyses),
        'price_increases': sum(a['price_increases'] for a in product_price_analyses),
        'trend_pct': round(worst_pa['trend_pct'], 1),
        'trend_direction': worst_pa['trend_direction'],
        'recent_changes': worst_pa.get('recent_changes', []),
        'products_analyzed': len(product_price_analyses)
    }

    # Worst-case buybox stability
    buybox_analysis = min(product_bb_analyses, key=lambda b: b['stability_score']) if product_bb_analyses else {
        'stability': 'UNKNOWN', 'stability_score': 50, 'total_changes': 0,
        'changes_per_day': 0, 'outages': 0, 'outage_pct': 0
    }

    price_war = calculate_price_war_score(price_analysis, buybox_analysis)
    insights = generate_insights(price_analysis, buybox_analysis, price_war, all_monthly_sold)
    
    result = {
        'keyword': keyword,
        'asin': asin,
        'marketplace': market,
        'products_analyzed': len(keepa_results),
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        
        'price_analysis': price_analysis,
        'buybox_analysis': buybox_analysis,
        'price_war_score': price_war,
        'insights': insights
    }
    
    # Add product details if available
    if products:
        result['top_products'] = [
            {
                'asin': p.get('asin'),
                'title': (p.get('title', '')[:50] + '...') if len(p.get('title', '')) > 50 else p.get('title'),
                'current_price': p.get('extractedPrice') or p.get('price'),
                'reviews': p.get('ratings', 0)
            }
            for p in products[:10]
        ]
    
    # Add sample price history for charts
    if keepa_results:
        first_keepa = keepa_results[0]['data']
        result['price_history_sample'] = first_keepa.get('buyboxPrice', [])[-50:]
    
    # === Enhanced Keepa Analysis (v2.0.0) ===
    if keepa_results:
        print("[+] Running enhanced Keepa analysis...", file=sys.stderr)
        enhanced_data = []
        
        for kr in keepa_results[:5]:  # Top 5 products
            asin_to_check = kr['asin']
            try:
                deep = _fetch_keepa_deep(asin_to_check, domain, preloaded=kr['data'])
                if deep and 'error' not in deep:
                    enhanced_data.append({
                        'asin': asin_to_check,
                        'bsr_trend': (deep.get('bsr') or {}).get('trend'),
                        'bsr_momentum': (deep.get('bsr') or {}).get('momentum'),
                        'sales_signal': (deep.get('bsr') or {}).get('sales_signal'),
                        'seller_count': (deep.get('sellers') or {}).get('current'),
                        'seller_trend': (deep.get('sellers') or {}).get('trend'),
                        'competition': (deep.get('sellers') or {}).get('competition_signal'),
                        'buybox_difficulty': (deep.get('sellers') or {}).get('buybox_difficulty'),
                        'seasonality': (deep.get('seasonality') or {}).get('detected'),
                        'peak_months': (deep.get('seasonality') or {}).get('peak_months', [])
                    })
                    print(f"    ✓ {asin_to_check}: BSR {(deep.get('bsr') or {}).get('trend')}, Sellers {(deep.get('sellers') or {}).get('current')}", file=sys.stderr)
            except Exception as e:
                print(f"    ⚠️ Enhanced Keepa failed for {asin_to_check}: {e}", file=sys.stderr)
        
        if enhanced_data:
            # Aggregate competition insights
            improving_count = sum(1 for d in enhanced_data if d.get('bsr_trend') == 'IMPROVING')
            intensifying_count = sum(1 for d in enhanced_data if d.get('competition') == 'INTENSIFYING')
            seasonal_count = sum(1 for d in enhanced_data if d.get('seasonality'))
            
            result['enhanced_keepa'] = {
                'products': enhanced_data,
                'market_signals': {
                    'bsr_improving': improving_count,
                    'competition_intensifying': intensifying_count,
                    'seasonal_products': seasonal_count
                },
                'competition_summary': {
                    'avg_sellers': sum(d.get('seller_count', 0) for d in enhanced_data if d.get('seller_count')) / len(enhanced_data) if enhanced_data else 0,
                    'trend': 'INTENSIFYING' if intensifying_count > len(enhanced_data) / 2 else 'STABLE',
                    'buybox_outlook': 'DIFFICULT' if any(d.get('buybox_difficulty') == 'HARD' for d in enhanced_data) else 'MODERATE' if any(d.get('buybox_difficulty') == 'MEDIUM' for d in enhanced_data) else 'EASIER'
                }
            }
            
            # Add enhanced insights
            enhanced_insights = []
            if improving_count > 0:
                enhanced_insights.append(f"📈 {improving_count}/{len(enhanced_data)} products have improving BSR (growing demand)")
            if intensifying_count > 0:
                enhanced_insights.append(f"⚠️ {intensifying_count}/{len(enhanced_data)} products show intensifying competition")
            if seasonal_count > 0:
                all_peaks = set()
                for d in enhanced_data:
                    all_peaks.update(d.get('peak_months', []))
                if all_peaks:
                    enhanced_insights.append(f"📅 Seasonal category - peak months: {', '.join(sorted(all_peaks))}")
            
            result['enhanced_keepa']['insights'] = enhanced_insights
    
    return result

# === Chart Generation ===

def generate_charts(result: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        import numpy as np
        from datetime import datetime
    except ImportError:
        print("matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    keyword = result.get('keyword') or result.get('asin', 'Unknown')
    GOOD = get_color('good')
    NEUTRAL = get_color('muted')
    WARNING = get_color('secondary')
    BAD = get_color('hot')
    
    # Chart 1: Price History Line
    price_history = result.get('price_history_sample', [])
    if price_history:
        dates = []
        prices = []
        for point in price_history:
            if point.get('value', -1) > 0:
                try:
                    dt = datetime.strptime(point['time'], '%Y-%m-%d %H:%M')
                    dates.append(dt)
                    prices.append(point['value'])
                except:
                    pass

        if len(dates) < 2:
            print(f"  ⚠️ 1_price_history.png skipped: need ≥2 points, got {len(dates)}", file=sys.stderr)
        else:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(dates, prices, color=get_color('primary'), linewidth=2, marker='o', markersize=3)
            ax.fill_between(dates, prices, alpha=0.3, color=get_color('primary'))

            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Buy Box Price ($)', fontsize=10)
            ax.set_title(f'BUYBOX PRICE HISTORY: {keyword.upper()}', fontweight='bold', fontsize=12, pad=15)
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Add stats annotation
            price_analysis = result.get('price_analysis', {})
            stats_text = f"Avg: ${price_analysis.get('avg_price', 0):.2f} | Range: ${price_analysis.get('min_price', 0):.2f}-${price_analysis.get('max_price', 0):.2f}"
            ax.annotate(stats_text, xy=(0.02, 0.98), xycoords='axes fraction', ha='left', va='top',
                       fontsize=9, bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/1_price_history.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 1: Price History", file=sys.stderr)
    
    # Chart 2: Price War Score Gauge
    price_war = result.get('price_war_score', {})
    if price_war:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        score = price_war.get('score', 0)
        level = price_war.get('level', 'UNKNOWN')
        
        colors_gauge = [GOOD, get_color('warning'), WARNING, BAD]
        labels_gauge = ['LOW\n(0-25)', 'MODERATE\n(25-50)', 'HIGH\n(50-75)', 'SEVERE\n(75-100)']
        ranges = [25, 25, 25, 25]
        starts = [0, 25, 50, 75]
        
        for start, width, color in zip(starts, ranges, colors_gauge):
            ax.barh(0, width, left=start, height=0.4, color=color, edgecolor='white', linewidth=2)
        
        ax.scatter([score], [0], s=400, c='black', marker='^', zorder=5)
        ax.text(score, 0.35, f'Score: {score}', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        for start, width, label in zip(starts, ranges, labels_gauge):
            ax.text(start + width/2, -0.35, label, ha='center', va='top', fontsize=10)
        
        ax.set_xlim(-5, 105)
        ax.set_ylim(-0.7, 0.6)
        ax.set_title(f'PRICE WAR SCORE: {level}', fontweight='bold', fontsize=14, pad=15)
        ax.axis('off')
        
        factors = price_war.get('factors', {})
        factor_text = f"Volatility: {factors.get('volatility', 0)} | Trend: {factors.get('trend', 0)} | Drops: {factors.get('price_drops', 0)} | BuyBox: {factors.get('buybox_instability', 0)}"
        ax.text(50, -0.55, factor_text, ha='center', va='top', fontsize=9, color='gray')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_price_war_score.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Price War Score", file=sys.stderr)
    
    # Chart 3: Volatility & Buy Box Summary
    price_analysis = result.get('price_analysis', {})
    bb = result.get('buybox_analysis', {})
    if not price_analysis or not bb:
        print(f"  ⚠️ 3_volatility_buybox.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Volatility
        ax1 = axes[0]
        pvi = price_analysis.get('pvi', 0)
        vol_level = price_analysis.get('volatility_level', 'UNKNOWN')

        vol_colors = {'LOW': GOOD, 'MEDIUM': get_color('warning'), 'HIGH': WARNING, 'EXTREME': BAD, 'UNKNOWN': NEUTRAL}
        ax1.barh(0, min(pvi, 40), height=0.5, color=vol_colors.get(vol_level, NEUTRAL), edgecolor='white', linewidth=2)
        ax1.set_xlim(0, 40)
        ax1.axvline(x=5, color='gray', linestyle='--', alpha=0.5, label='Low')
        ax1.axvline(x=10, color='gray', linestyle='--', alpha=0.5, label='Medium')
        ax1.axvline(x=20, color='gray', linestyle='--', alpha=0.5, label='High')
        ax1.set_title(f'VOLATILITY: {vol_level} ({pvi:.1f}%)', fontweight='bold', fontsize=12)
        ax1.set_xlabel('Price Volatility Index (%)')
        ax1.set_yticks([])

        # Buy Box Stability
        ax2 = axes[1]
        bb_score = bb.get('stability_score', 50)
        bb_level = bb.get('stability', 'UNKNOWN')

        bb_colors = {'VERY_STABLE': GOOD, 'STABLE': GOOD, 'MODERATE': get_color('warning'), 'UNSTABLE': WARNING, 'CHAOTIC': BAD, 'UNKNOWN': NEUTRAL}
        ax2.barh(0, bb_score, height=0.5, color=bb_colors.get(bb_level, NEUTRAL), edgecolor='white', linewidth=2)
        ax2.set_xlim(0, 100)
        ax2.set_title(f'BUYBOX STABILITY: {bb_level} ({bb_score})', fontweight='bold', fontsize=12)
        ax2.set_xlabel('Stability Score (higher = more stable)')
        ax2.set_yticks([])

        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_volatility_buybox.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Volatility & Buy Box", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 price_history_analyzer.py '{\"keyword\": \"yoga mat\"}' [--chart <dir>]", file=sys.stderr)
        sys.exit(1)
    
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(f"Invalid JSON: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    asin = params.get('asin')
    market = params.get('market', 'US')
    
    if not keyword and not asin:
        print("Missing required parameter: keyword or asin", file=sys.stderr)
        sys.exit(1)
    
    chart_dir = None
    if '--chart' in sys.argv:
        chart_idx = sys.argv.index('--chart')
        if chart_idx + 1 < len(sys.argv):
            chart_dir = sys.argv[chart_idx + 1]
    
    result = analyze_prices(keyword, asin, market)
    
    if chart_dir and 'error' not in result:
        print(f"Generating charts in {chart_dir}...", file=sys.stderr)
        result['charts'] = generate_charts(result, chart_dir) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
