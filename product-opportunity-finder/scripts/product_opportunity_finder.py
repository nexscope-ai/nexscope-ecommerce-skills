#!/usr/bin/env python3
"""
Product Opportunity Finder v2.2.0

Find blue ocean products with multi-dimensional filtering and cross-platform validation.
Answers: "What products should I sell?"

Data Sources:
- Amazon Search API (product discovery)
- eBay Sold (cross-platform demand verification)
- Walmart Search (multi-channel validation)
- Google Trends (trend direction)
- Keepa (BSR/price history, listing age)
- Jungle Scout Historical (seasonality)

Usage:
    python3 product_opportunity_finder.py '{"keyword": "yoga accessories"}'
    python3 product_opportunity_finder.py '{"keyword": "pet supplies", "max_reviews": 500}'
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional, List
from urllib.request import Request, urlopen

# --- Shared chart styling (from display-rules.md via chart_style.json) ---
try:
    from ecommerce_chart_helpers import load_style, apply_style, save_chart, get_color, get_palette, get_bar_kwargs, get_font_size, setup_plt, merge_and_chart
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

OPPORTUNITY_TYPES = {
    'LOW_COMPETITION': '🏖️ Low reviews, weak competitors',
    'QUALITY_GAP': '⭐ Low ratings, room for improvement',
    'PRICE_GAP': '💵 Missing price tiers',
    'RISING_STAR': '📈 Growing BSR trend',
    'BUNDLE_OPPORTUNITY': '📦 Frequently bought together potential',
    'NICHE_SEGMENT': '🎯 Underserved sub-niche',
    'CHANNEL_ARBITRAGE': '🔄 Cross-platform price difference',
}

PRESETS = {
    'conservative': {'max_reviews': 300, 'min_rating': 3.5, 'min_sales': 100},
    'balanced': {'max_reviews': 500, 'min_rating': 3.0, 'min_sales': 50},
    'aggressive': {'max_reviews': 1000, 'min_rating': 2.5, 'min_sales': 30},
    'premium': {'min_price': 50, 'max_reviews': 500},
    'budget': {'max_price': 25, 'min_sales': 200},
}

RED_LINE_KEYWORDS = [
    'hazmat', 'flammable', 'battery', 'lithium',
    'fragile', 'glass',
    'weapon', 'knife', 'gun',
    'medicine', 'drug', 'pharmaceutical',
    'alcohol', 'tobacco',
]

# === API Functions ===

def api_call(endpoint: str, payload: dict) -> Optional[dict]:
    """Call API via NexScope proxy"""
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

# === Data Source Functions ===

def search_products(keyword: str, market: str = 'US', limit: int = 60) -> List[dict]:
    """Search Amazon products"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(market, 'amazon.com')
    })
    if result and 'products' in result:
        return result['products']
    elif result and 'data' in result:
        return result['data'] if isinstance(result['data'], list) else []
    return []

def get_ebay_sold(keyword: str) -> Optional[dict]:
    """Get eBay sold items for cross-platform demand validation"""
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
        new_items = [p for p in products if (p.get('condition', '') or '').lower() in ('new', 'brand new', '')]
        prices = [p.get('price', 0) or 0 for p in new_items if (p.get('price', 0) or 0) > 0]
        return {
            'sold_count': len(products),
            'new_sold_count': len(new_items),
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'price_range': (min(prices), max(prices)) if prices else (0, 0),
            'demand_verified': len(products) >= 10
        }
    except Exception as e:
        print(f"  eBay error: {e}", file=sys.stderr)
        return None

def get_walmart_search(keyword: str) -> Optional[dict]:
    """Get Walmart search results for multi-channel validation"""
    try:
        result = api_call('/walmart/search', {
            'keyword': keyword,
            'sort': 'best_seller'
        })
        if not result:
            return None
        products = result.get('products', []) if isinstance(result, dict) else result if isinstance(result, list) else []
        prices = [p.get('price', 0) or 0 for p in products if (p.get('price', 0) or 0) > 0]
        return {
            'product_count': len(products),
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'price_range': (min(prices), max(prices)) if prices else (0, 0),
            'has_competition': len(products) > 0
        }
    except Exception as e:
        print(f"  Walmart error: {e}", file=sys.stderr)
        return None

def get_google_trends(keyword: str, months: int = 12) -> Optional[dict]:
    """Get Google Trends data for trend direction"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        result = api_call('/googleTrend/getTrendByKeys', {
            'keyword': keyword,
            'region': 'US',
            'dayRangeStart': start_date.strftime('%Y-%m-%d'),
            'dayRangeEnd': end_date.strftime('%Y-%m-%d')
        })
        if not result:
            return None

        values = []
        if isinstance(result, dict):
            # API returns: {"trendInfoForKeys": [{"keyword": "...", "trendValues": [...]}]}
            trend_info = result.get('trendInfoForKeys', [])
            if trend_info and isinstance(trend_info, list):
                raw_values = trend_info[0].get('trendValues', [])
            else:
                # Fallback for legacy response shapes
                raw_values = result.get('trendValues', result.get('timeline_data', result.get('data', [])))
            if isinstance(raw_values, list):
                for v in raw_values:
                    val = v.get('value', v) if isinstance(v, dict) else v
                    try:
                        values.append(int(val))
                    except (ValueError, TypeError):
                        pass

        if len(values) < 5:
            return None

        early = sum(values[:len(values)//3]) / max(len(values)//3, 1)
        recent = sum(values[-len(values)//3:]) / max(len(values)//3, 1)
        change_pct = (recent - early) / max(early, 1) * 100

        if change_pct > 10:
            direction = 'rising'
        elif change_pct < -10:
            direction = 'declining'
        else:
            direction = 'stable'

        return {
            'direction': direction,
            'change_pct': round(change_pct, 1),
            'avg_interest': round(sum(values) / len(values), 1)
        }
    except Exception as e:
        print(f"  Google Trends error: {e}", file=sys.stderr)
        return None

def get_keepa_detail(asins_csv: str) -> Optional[List[dict]]:
    """Get Keepa product details in batch (listing age, monthly sales history)"""
    try:
        result = api_call('/keepa/productRequest', {
            'asin': asins_csv,
            'domain': '1',
            'history': 1
        })
        if not result:
            return None
        products = result.get('products', []) if isinstance(result, dict) else result if isinstance(result, list) else []
        parsed = []
        for p in products:
            listed_since = p.get('listedSince')
            age_days = None
            if listed_since:
                try:
                    age_days = (datetime.now() - datetime.fromtimestamp(listed_since)).days
                except Exception:
                    pass
            parsed.append({
                'asin': p.get('asin', ''),
                'listed_since': listed_since,
                'age_days': age_days,
                'monthly_sales': p.get('monthlySales', 0),
                'monthly_sales_history': p.get('monthlySalesHistory', []),
                'package_weight': p.get('packageWeight'),
                'fba_fees': p.get('fbaFees'),
            })
        return parsed
    except Exception as e:
        print(f"  Keepa detail error: {e}", file=sys.stderr)
        return None

def get_keepa_history(asin: str, days: int = 90) -> Optional[dict]:
    """Get Keepa BSR/price/seller history for trend analysis"""
    try:
        result = api_call('/keepa/productSeries', {
            'asin': asin,
            'domain': '1',
            'days': days,
            'showBsrMain': 1,
            'showSellerCount': 1,
            'showPrice': 1
        })
        if not result:
            return None

        def extract_trend(data_key):
            series = result.get(data_key, [])
            if isinstance(series, list) and len(series) >= 2:
                points = []
                for item in series:
                    if isinstance(item, dict) and 'points' in item:
                        points = [pt.get('y', pt.get('value', 0)) for pt in item['points'] if isinstance(pt, dict)]
                        break
                    elif isinstance(item, (int, float)):
                        points.append(item)
                if len(points) >= 6:
                    third = max(len(points) // 3, 1)
                    early_avg = sum(points[:third]) / third
                    recent_avg = sum(points[-third:]) / third
                    if early_avg > 0:
                        change = (recent_avg - early_avg) / early_avg * 100
                        return {'change_pct': round(change, 1), 'early_avg': round(early_avg, 1), 'recent_avg': round(recent_avg, 1)}
            return None

        bsr_trend = extract_trend('bsrMain')
        price_trend = extract_trend('price')
        seller_trend = extract_trend('sellerCount')

        return {
            'bsr_trend': bsr_trend,
            'price_trend': price_trend,
            'seller_trend': seller_trend,
        }
    except Exception as e:
        print(f"  Keepa history error: {e}", file=sys.stderr)
        return None

def get_seasonality(keyword: str, marketplace: str = 'us') -> Optional[dict]:
    """Get Jungle Scout historical search volume for seasonality analysis"""
    try:
        _end_dt = datetime.now().strftime('%Y-%m-%d')
        _start_dt = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        _url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume"
        _payload = json.dumps({'keyword': keyword, 'marketplace': marketplace or 'us', 'startDate': _start_dt, 'endDate': _end_dt}).encode('utf-8')
        _req = Request(_url, data=_payload, headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}', 'Content-Type': 'application/json'}, method='POST')
        with urlopen(_req, timeout=30) as _r:
            _raw = json.loads(_r.read().decode('utf-8'))
        if isinstance(_raw, dict) and _raw.get('code') == 0:
            result = _raw.get('data', _raw)
        else:
            result = None

        if not result:
            return None

        items = result.get('historicalSearchVolumeList', [])
        if isinstance(result, dict) and not items:
            items = result.get('data', [])
            if isinstance(items, list) and items and isinstance(items[0], dict) and 'attributes' in items[0]:
                items = [i['attributes'] for i in items]

        monthly = {}
        for item in items:
            vol = item.get('estimatedExactSearchVolume', item.get('estimated_exact_search_volume', item.get('estimate', 0)))
            date_str = item.get('estimateStartDate', item.get('estimate_start_date', ''))
            if date_str and vol:
                month_key = str(date_str)[:7]
                if month_key not in monthly:
                    monthly[month_key] = []
                monthly[month_key].append(vol)

        if len(monthly) < 3:
            return None

        monthly_avg = {m: sum(v) / len(v) for m, v in monthly.items()}
        values = list(monthly_avg.values())
        peak = max(values)
        trough = min(values) if min(values) > 0 else 1
        seasonality_index = peak / trough

        peak_months = [m for m, v in monthly_avg.items() if v >= peak * 0.8]

        if seasonality_index < 1.5:
            pattern = 'year-round'
        elif seasonality_index < 3:
            pattern = 'moderate-seasonal'
        else:
            pattern = 'highly-seasonal'

        return {
            'seasonality_index': round(seasonality_index, 2),
            'pattern': pattern,
            'peak_months': peak_months,
            'monthly_volumes': {m: round(v) for m, v in monthly_avg.items()}
        }
    except Exception as e:
        print(f"  Seasonality error: {e}", file=sys.stderr)
        return None

# === Analysis Functions ===

def check_red_lines(product: dict) -> List[str]:
    """Check for red line keywords"""
    flags = []
    title = (product.get('title', '') or '').lower()
    for keyword in RED_LINE_KEYWORDS:
        if keyword in title:
            flags.append(f"RED_LINE: {keyword}")
    return flags

def calculate_opportunity_score(product: dict, market_stats: dict,
                                trends: dict = None, keepa: dict = None,
                                cross_platform: dict = None) -> dict:
    """Calculate multi-dimensional opportunity score with enhanced data"""
    reviews = product.get('reviews', 0) or 0
    rating = product.get('rating', 0) or 0
    price = product.get('price', 0) or 0
    sales = product.get('monthly_sales', 0) or 0

    market_avg_reviews = market_stats.get('avg_reviews', 500)
    market_avg_price = market_stats.get('avg_price', 30)

    # === Demand Score (0-25) ===
    if sales > 500:
        demand = 22
    elif sales > 200:
        demand = 18
    elif sales > 100:
        demand = 14
    elif sales > 50:
        demand = 10
    else:
        demand = 5

    if trends and trends.get('google_trends'):
        gt = trends['google_trends']
        if gt.get('direction') == 'rising':
            demand = min(25, demand + 3)
        elif gt.get('direction') == 'declining':
            demand = max(0, demand - 3)

    if cross_platform and cross_platform.get('ebay'):
        ebay = cross_platform['ebay']
        if ebay.get('demand_verified'):
            demand = min(25, demand + 2)

    # === Competition Score (0-25) ===
    review_ratio = reviews / max(market_avg_reviews, 1)
    if review_ratio < 0.2:
        competition = 22
    elif review_ratio < 0.4:
        competition = 18
    elif review_ratio < 0.6:
        competition = 14
    elif review_ratio < 1.0:
        competition = 10
    else:
        competition = 5

    if keepa:
        bsr = keepa.get('bsr_trend')
        if bsr and bsr.get('change_pct', 0) < -15:
            competition = min(25, competition + 2)
        sellers = keepa.get('seller_trend')
        if sellers and sellers.get('change_pct', 0) > 20:
            competition = max(0, competition - 2)

    # === Profit Score (0-25) ===
    if 20 <= price <= 50:
        profit = 22
    elif 50 < price <= 100:
        profit = 18
    elif 15 <= price < 20:
        profit = 14
    elif price > 100:
        profit = 10
    else:
        profit = 5

    if keepa:
        pt = keepa.get('price_trend')
        if pt and abs(pt.get('change_pct', 0)) < 10:
            profit = min(25, profit + 2)

    if cross_platform:
        amz_price = price
        ebay_price = (cross_platform.get('ebay') or {}).get('avg_price', 0)
        walmart_price = (cross_platform.get('walmart') or {}).get('avg_price', 0)
        if ebay_price > 0 and amz_price > 0 and abs(ebay_price - amz_price) / amz_price > 0.15:
            profit = min(25, profit + 1)

    # === Opportunity Score (0-25) ===
    opportunity = 0
    opportunity_types = []

    if reviews < 200:
        opportunity += 6
        opportunity_types.append('LOW_COMPETITION')

    if 0 < rating < 4.0:
        opportunity += 6
        opportunity_types.append('QUALITY_GAP')

    price_segment = 'budget' if price < 25 else 'mid' if price < 50 else 'premium'
    segment_competition = market_stats.get(f'{price_segment}_competition', 'HIGH')
    if segment_competition == 'LOW':
        opportunity += 4
        opportunity_types.append('PRICE_GAP')

    if keepa:
        bsr = keepa.get('bsr_trend')
        if bsr and bsr.get('change_pct', 0) < -20 and reviews < 200:
            opportunity += 4
            opportunity_types.append('RISING_STAR')

    if cross_platform:
        ebay_data = cross_platform.get('ebay')
        walmart_data = cross_platform.get('walmart')
        if ebay_data and ebay_data.get('avg_price', 0) > 0 and price > 0:
            if abs(ebay_data['avg_price'] - price) / price > 0.2:
                opportunity += 3
                if 'CHANNEL_ARBITRAGE' not in opportunity_types:
                    opportunity_types.append('CHANNEL_ARBITRAGE')
        if walmart_data and not walmart_data.get('has_competition'):
            opportunity += 2
            if 'NICHE_SEGMENT' not in opportunity_types:
                opportunity_types.append('NICHE_SEGMENT')

    if trends and trends.get('seasonality'):
        season = trends['seasonality']
        if season.get('pattern') == 'year-round':
            opportunity = min(25, opportunity + 2)

    total = demand + competition + profit + min(25, opportunity)

    return {
        'total': min(100, total),
        'demand': demand,
        'competition': competition,
        'profit': profit,
        'opportunity': min(25, opportunity),
        'types': opportunity_types,
        'grade': 'A' if total >= 75 else 'B' if total >= 60 else 'C' if total >= 45 else 'D'
    }

def analyze_market_stats(products: List[dict]) -> dict:
    """Calculate market statistics for scoring context"""
    if not products:
        return {}

    reviews_list = [p.get('ratings', 0) or 0 for p in products]
    prices_list = [p.get('price', 0) or p.get('extractedPrice', 0) or 0 for p in products]
    prices_list = [p for p in prices_list if p > 0]

    avg_reviews = sum(reviews_list) / len(reviews_list) if reviews_list else 500
    avg_price = sum(prices_list) / len(prices_list) if prices_list else 30

    budget_count = sum(1 for p in prices_list if p < 25)
    mid_count = sum(1 for p in prices_list if 25 <= p < 50)
    premium_count = sum(1 for p in prices_list if p >= 50)
    total = len(prices_list) or 1

    return {
        'avg_reviews': avg_reviews,
        'avg_price': avg_price,
        'median_reviews': sorted(reviews_list)[len(reviews_list)//2] if reviews_list else 0,
        'budget_competition': 'LOW' if budget_count/total < 0.2 else 'HIGH',
        'mid_competition': 'LOW' if mid_count/total < 0.3 else 'HIGH',
        'premium_competition': 'LOW' if premium_count/total < 0.2 else 'HIGH',
        'price_distribution': {
            'budget': budget_count,
            'mid': mid_count,
            'premium': premium_count
        }
    }

def generate_insights(results: List[dict], market_stats: dict, keyword: str,
                      cross_platform: dict = None, trends: dict = None) -> dict:
    """Generate actionable insights"""
    if not results:
        return {'summary': 'No opportunities found', 'recommendations': []}

    type_counts = {}
    for r in results:
        for t in r.get('opportunity_types', []):
            type_counts[t] = type_counts.get(t, 0) + 1

    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for r in results:
        grade = r.get('grade', 'D')
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    a_count = grade_counts['A']
    b_count = grade_counts['B']

    if a_count >= 5:
        summary = f"🔥 Excellent market! {a_count} Grade-A opportunities found."
    elif a_count >= 2:
        summary = f"👍 Good potential! {a_count} Grade-A and {b_count} Grade-B opportunities."
    elif b_count >= 5:
        summary = f"📊 Moderate market. {b_count} Grade-B opportunities worth exploring."
    else:
        summary = f"⚠️ Competitive market. Limited opportunities found."

    recommendations = []

    if type_counts.get('LOW_COMPETITION', 0) > 3:
        recommendations.append(f"🏖️ {type_counts['LOW_COMPETITION']} low-competition products — great for new sellers")

    if type_counts.get('QUALITY_GAP', 0) > 2:
        recommendations.append(f"⭐ {type_counts['QUALITY_GAP']} products with low ratings — opportunity to improve")

    if type_counts.get('PRICE_GAP', 0) > 0:
        recommendations.append(f"💵 Price gap detected — underserved price segment")

    if type_counts.get('RISING_STAR', 0) > 0:
        recommendations.append(f"📈 {type_counts['RISING_STAR']} rising products — early entry opportunity")

    if type_counts.get('CHANNEL_ARBITRAGE', 0) > 0:
        recommendations.append(f"🔄 Cross-platform price difference detected — arbitrage opportunity")

    if trends and trends.get('google_trends'):
        gt = trends['google_trends']
        if gt.get('direction') == 'rising':
            recommendations.append(f"📈 Google Trends: demand rising ({gt['change_pct']:+.1f}%)")
        elif gt.get('direction') == 'declining':
            recommendations.append(f"📉 Google Trends: demand declining ({gt['change_pct']:+.1f}%) — proceed with caution")

    if trends and trends.get('seasonality'):
        s = trends['seasonality']
        if s.get('pattern') == 'highly-seasonal':
            recommendations.append(f"🗓️ Highly seasonal (index {s['seasonality_index']:.1f}x) — time entry around peak months: {', '.join(s.get('peak_months', []))}")
        elif s.get('pattern') == 'year-round':
            recommendations.append(f"✅ Year-round demand (seasonality index {s['seasonality_index']:.1f}x)")

    if cross_platform:
        ebay = cross_platform.get('ebay')
        if ebay and ebay.get('demand_verified'):
            recommendations.append(f"✅ eBay confirms real demand ({ebay['sold_count']} sold items)")
        elif ebay and not ebay.get('demand_verified'):
            recommendations.append(f"⚠️ Low eBay activity ({ebay.get('sold_count', 0)} sold) — verify demand")

    if results:
        top = results[0]
        recommendations.append(f"🎯 Top pick: {top.get('title', '')[:40]}... (Score: {top.get('score', 0)})")

    price_dist = market_stats.get('price_distribution', {})
    if price_dist.get('premium', 0) < price_dist.get('budget', 0) * 0.3:
        recommendations.append("💡 Premium segment underserved — consider higher-end positioning")

    return {
        'summary': summary,
        'grade_distribution': grade_counts,
        'opportunity_types': type_counts,
        'recommendations': recommendations,
        'market_health': 'GOOD' if a_count + b_count >= 5 else 'MODERATE' if a_count + b_count >= 2 else 'CHALLENGING'
    }

# === Main Function ===

def find_opportunities(keyword: str, market: str = 'US', preset: str = 'balanced',
                       max_reviews: int = None, min_rating: float = None,
                       min_price: float = None, max_price: float = None,
                       min_sales: int = None) -> dict:
    """Main opportunity finder function"""
    print(f"Finding opportunities for: {keyword}", file=sys.stderr)

    preset_config = PRESETS.get(preset, PRESETS['balanced'])
    max_reviews = max_reviews or preset_config.get('max_reviews', 500)
    min_rating = min_rating or preset_config.get('min_rating', 3.0)
    min_sales = min_sales or preset_config.get('min_sales', 50)
    min_price = min_price or preset_config.get('min_price', 0)
    max_price = max_price or preset_config.get('max_price', 9999)

    # [1/6] Amazon Search
    print(f"[1/6] Searching Amazon products...", file=sys.stderr)
    products = search_products(keyword, market, 60)
    if not products:
        return {'error': 'No products found', 'keyword': keyword}
    print(f"  ✓ Got {len(products)} products", file=sys.stderr)

    # [2/6] Cross-platform validation (eBay + Walmart)
    print(f"[2/6] Cross-platform validation...", file=sys.stderr)
    cross_platform = {}
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            ebay_future = executor.submit(get_ebay_sold, keyword)
            walmart_future = executor.submit(get_walmart_search, keyword)
            ebay_data = ebay_future.result(timeout=30)
            walmart_data = walmart_future.result(timeout=30)
    except Exception:
        ebay_data = get_ebay_sold(keyword)
        walmart_data = get_walmart_search(keyword)

    if ebay_data:
        cross_platform['ebay'] = ebay_data
        print(f"  ✓ eBay: {ebay_data.get('sold_count', 0)} sold items", file=sys.stderr)
    else:
        print(f"  ⚠️ eBay: no data", file=sys.stderr)

    if walmart_data:
        cross_platform['walmart'] = walmart_data
        print(f"  ✓ Walmart: {walmart_data.get('product_count', 0)} products", file=sys.stderr)
    else:
        print(f"  ⚠️ Walmart: no data", file=sys.stderr)

    # [3/6] Category clean
    print(f"[3/6] Cleaning category...", file=sys.stderr)
    clean_stats = None
    try:
        from category_cleaner import clean_products
        products, clean_stats = clean_products(products, keyword)
        print(f"  ✓ Cleaned to {len(products)} products", file=sys.stderr)
    except Exception:
        print(f"  ⚠️ Category cleaner not available", file=sys.stderr)

    # [4/6] Keepa batch detail for top ASINs
    print(f"[4/6] Fetching Keepa product details...", file=sys.stderr)
    top_asins = [p.get('asin') for p in products[:20] if p.get('asin')]
    keepa_details = {}
    if top_asins:
        asins_csv = ','.join(top_asins)
        detail_list = get_keepa_detail(asins_csv)
        if detail_list:
            for d in detail_list:
                if d.get('asin'):
                    keepa_details[d['asin']] = d
            print(f"  ✓ Keepa detail: {len(keepa_details)} products", file=sys.stderr)
        else:
            print(f"  ⚠️ Keepa detail: no data", file=sys.stderr)
    else:
        print(f"  ⚠️ No ASINs for Keepa", file=sys.stderr)

    # [5/6] Trend validation (Keepa History + Google Trends + Seasonality)
    print(f"[5/6] Trend validation...", file=sys.stderr)
    trends = {}

    top_asin = top_asins[0] if top_asins else None
    keepa_hist = None
    google_trends_data = None
    seasonality_data = None

    try:
        from concurrent.futures import ThreadPoolExecutor
        futures = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            if top_asin:
                futures['keepa'] = executor.submit(get_keepa_history, top_asin)
            futures['google'] = executor.submit(get_google_trends, keyword)
            futures['season'] = executor.submit(get_seasonality, keyword, market.lower())

            if 'keepa' in futures:
                keepa_hist = futures['keepa'].result(timeout=30)
            google_trends_data = futures['google'].result(timeout=30)
            seasonality_data = futures['season'].result(timeout=30)
    except Exception:
        if top_asin:
            keepa_hist = get_keepa_history(top_asin)
        google_trends_data = get_google_trends(keyword)
        seasonality_data = get_seasonality(keyword, market.lower())

    if google_trends_data:
        trends['google_trends'] = google_trends_data
        print(f"  ✓ Google Trends: {google_trends_data.get('direction', '?')} ({google_trends_data.get('change_pct', 0):+.1f}%)", file=sys.stderr)
    else:
        print(f"  ⚠️ Google Trends: no data", file=sys.stderr)

    if seasonality_data:
        trends['seasonality'] = seasonality_data
        print(f"  ✓ Seasonality: {seasonality_data.get('pattern', '?')} (index {seasonality_data.get('seasonality_index', 0):.1f}x)", file=sys.stderr)
    else:
        print(f"  ⚠️ Seasonality: no data", file=sys.stderr)

    if keepa_hist:
        print(f"  ✓ Keepa history: BSR trend available", file=sys.stderr)
    else:
        print(f"  ⚠️ Keepa history: no data", file=sys.stderr)

    # [6/6] Score and filter
    print(f"[6/6] Scoring opportunities...", file=sys.stderr)
    market_stats = analyze_market_stats(products)
    results = []

    for p in products:
        reviews = p.get('ratings', 0) or 0
        rating = p.get('rating', 0) or 0
        price = p.get('price', 0) or p.get('extractedPrice', 0) or 0
        sales = p.get('monthlySalesUnits', 0) or 0

        if reviews > max_reviews:
            continue
        if rating > 0 and rating < min_rating:
            continue
        if price < min_price or price > max_price:
            continue
        if sales < min_sales:
            continue

        red_flags = check_red_lines(p)
        if red_flags:
            continue

        asin = p.get('asin', '')
        product_keepa = keepa_details.get(asin)

        product_data = {
            'reviews': reviews,
            'rating': rating,
            'price': price,
            'monthly_sales': sales
        }

        product_keepa_trends = keepa_hist if asin == top_asin else None

        scores = calculate_opportunity_score(
            product_data, market_stats,
            trends=trends,
            keepa=product_keepa_trends,
            cross_platform=cross_platform
        )

        entry = {
            'asin': asin,
            'title': (p.get('title', '') or '')[:60] + '...' if len(p.get('title', '') or '') > 60 else p.get('title', ''),
            'brand': p.get('brand', ''),
            'price': price,
            'reviews': reviews,
            'rating': rating,
            'monthly_sales': sales,
            'score': scores['total'],
            'grade': scores['grade'],
            'scores': {
                'demand': scores['demand'],
                'competition': scores['competition'],
                'profit': scores['profit'],
                'opportunity': scores['opportunity']
            },
            'opportunity_types': scores['types']
        }

        if product_keepa:
            entry['listing_age_days'] = product_keepa.get('age_days')

        results.append(entry)

    results.sort(key=lambda x: x['score'], reverse=True)

    insights = generate_insights(results, market_stats, keyword,
                                  cross_platform=cross_platform, trends=trends)

    output = {
        'keyword': keyword,
        'marketplace': market,
        'preset': preset,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v2.2.0',
        'filters': {
            'max_reviews': max_reviews,
            'min_rating': min_rating,
            'min_sales': min_sales,
            'price_range': [min_price, max_price]
        },
        'products_searched': len(products),
        'opportunities_found': len(results),
        'market_stats': market_stats,
        'cross_platform': cross_platform if cross_platform else None,
        'trend_validation': trends if trends else None,
        'opportunities': results[:20],
        'by_grade': {
            'A': [r for r in results if r['grade'] == 'A'][:5],
            'B': [r for r in results if r['grade'] == 'B'][:5],
        },
        'insights': insights
    }

    return output

# === Chart Generation ===

def generate_charts(result: dict, output_dir: str):
    """Generate visualization charts matching SKILL.md specification:
    seasonality.png, segments.png, roi_waterfall.png, radar.png, comparison.png
    """
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

    # Color palette per display-rules.md
    GOOD = get_color('good')
    NEUTRAL = get_color('muted')
    WARNING = get_color('secondary')
    BAD = get_color('hot')
    BLUE = get_color('primary')
    PURPLE = '#9C27B0'

    keyword = result.get('keyword', 'Unknown')
    opportunities = result.get('opportunities', [])
    insights = result.get('insights', {})
    trend_validation = result.get('trend_validation') or {}

    # --- Chart 1: seasonality.png — Monthly Seasonality Trend ---
    seasonality = trend_validation.get('seasonality') or {}
    monthly_volumes = seasonality.get('monthly_volumes') or {}
    if len(monthly_volumes) >= 3:
        fig, ax = plt.subplots(figsize=(10, 5))

        months = sorted(monthly_volumes.keys())
        values = [monthly_volumes[m] for m in months]
        x_pos = range(len(months))

        ax.plot(x_pos, values, color=BLUE, linewidth=2.5, marker='o', markersize=6, zorder=3)
        ax.fill_between(x_pos, values, alpha=0.12, color=BLUE)

        peak_val = max(values)
        peak_idx = values.index(peak_val)
        ax.scatter([peak_idx], [peak_val], color=GOOD, s=120, zorder=5,
                   label=f"Peak: {months[peak_idx]} ({int(peak_val):,})")

        ax.set_xticks(x_pos)
        ax.set_xticklabels([m[5:] for m in months], rotation=45, fontsize=9)
        ax.set_xlabel('Month', fontsize=11)
        ax.set_ylabel('Search Volume', fontsize=11)
        ax.set_title(f'SEASONALITY TREND: {keyword.upper()}',
                     fontweight='bold', fontsize=13, pad=15)
        ax.set_ylim(0, peak_val * 1.25)

        pattern = seasonality.get('pattern', '')
        idx = seasonality.get('seasonality_index', 0)
        ax.text(0.02, 0.95, f'Pattern: {pattern}  |  Index: {idx:.1f}x',
                transform=ax.transAxes, fontsize=9, va='top',
                bbox=dict(boxstyle='round', facecolor='#FFF9C4', alpha=0.85))

        ax.legend(fontsize=9, loc='upper right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/seasonality.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ seasonality.png", file=sys.stderr)
    else:
        print(f"  ⚠️ seasonality.png skipped: need ≥3 months, got {len(monthly_volumes)}", file=sys.stderr)

    # --- Chart 2: segments.png — Opportunity Type Distribution (Horizontal Bar) ---
    opp_types = insights.get('opportunity_types') or {}
    active_types = {k: v for k, v in opp_types.items() if v > 0}
    if active_types:
        type_labels = {
            'LOW_COMPETITION': 'Low Competition',
            'QUALITY_GAP': 'Quality Gap',
            'PRICE_GAP': 'Price Gap',
            'RISING_STAR': 'Rising Star',
            'BUNDLE_OPPORTUNITY': 'Bundle Opportunity',
            'NICHE_SEGMENT': 'Niche Segment',
            'CHANNEL_ARBITRAGE': 'Channel Arbitrage',
        }

        sorted_types = sorted(active_types.items(), key=lambda x: x[1], reverse=True)
        labels = [type_labels.get(k, k) for k, _ in sorted_types]
        values = [v for _, v in sorted_types]

        fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.75)))

        y_pos = np.arange(len(labels))
        bars = ax.barh(y_pos, values, color=BLUE, edgecolor='white', linewidth=2)

        max_val = max(values)
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + max_val * 0.02, bar.get_y() + bar.get_height() / 2,
                    str(val), ha='left', va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel('Number of Products', fontsize=11)
        ax.set_title(f'OPPORTUNITY TYPE DISTRIBUTION: {keyword.upper()}',
                     fontweight='bold', fontsize=13, pad=15)
        ax.set_xlim(0, max_val * 1.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/segments.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ segments.png", file=sys.stderr)
    else:
        print(f"  ⚠️ segments.png skipped: no opportunity type data", file=sys.stderr)

    # --- Chart 3: roi_waterfall.png — Margin Breakdown Waterfall ---
    priced = [o for o in opportunities if o.get('price', 0) > 0]
    if priced:
        prices_sorted = sorted(o['price'] for o in priced[:10])
        ref_price = prices_sorted[len(prices_sorted) // 2]

        referral_fee = round(ref_price * 0.15, 2)
        fba_fee = round(min(max(ref_price * 0.12, 3.0), 8.0), 2)
        cogs = round(ref_price * 0.35, 2)
        net_profit = round(ref_price - referral_fee - fba_fee - cogs, 2)

        steps = [
            ('Sale\nPrice', ref_price, True),
            ('Amazon\nFee (~15%)', -referral_fee, False),
            ('FBA\nFee', -fba_fee, False),
            ('COGS\n(~35%)', -cogs, False),
            ('Net\nProfit', net_profit, True),
        ]

        fig, ax = plt.subplots(figsize=(10, 6))

        running = 0.0
        for i, (label, value, is_absolute) in enumerate(steps):
            if is_absolute:
                bottom = 0.0
                height = value
            else:
                bottom = running
                height = value

            bar_color = GOOD if value >= 0 else (BAD if i == len(steps) - 1 else WARNING)
            ax.bar(i, abs(height), bottom=min(bottom, bottom + height),
                   color=bar_color, edgecolor='white', linewidth=2, width=0.6)

            mid_y = min(bottom, bottom + height) + abs(height) / 2
            ax.text(i, mid_y, f'${abs(value):.2f}',
                    ha='center', va='center', fontsize=10, fontweight='bold',
                    color='white' if abs(height) > ref_price * 0.07 else '#333333')

            if not is_absolute:
                ax.plot([i - 0.7, i - 0.3], [running, running],
                        color=get_color('muted'), linewidth=1, linestyle='--')

            running += value

        ax.set_xticks(range(len(steps)))
        ax.set_xticklabels([s[0] for s in steps], fontsize=10)
        ax.set_ylabel('Amount (USD)', fontsize=11)
        ax.set_title(f'ROI WATERFALL: {keyword.upper()} — Median Price ${ref_price:.2f}',
                     fontweight='bold', fontsize=13, pad=15)
        ax.set_ylim(0, ref_price * 1.18)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        margin_pct = net_profit / ref_price * 100
        box_color = '#E8F5E9' if net_profit > 0 else '#FFEBEE'
        ax.text(0.98, 0.95, f'Est. Net Margin: {margin_pct:.1f}%',
                transform=ax.transAxes, fontsize=10, va='top', ha='right',
                bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.9))

        plt.tight_layout()
        plt.savefig(f'{output_dir}/roi_waterfall.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ roi_waterfall.png", file=sys.stderr)
    else:
        print(f"  ⚠️ roi_waterfall.png skipped: no price data", file=sys.stderr)

    # --- Chart 4: radar.png — Multi-Dimension Radar Score ---
    scored = [o for o in opportunities if o.get('scores')]
    if scored:
        top3 = scored[:min(3, len(scored))]
        dimensions = ['Demand', 'Competition', 'Profit', 'Opportunity']
        dim_keys = ['demand', 'competition', 'profit', 'opportunity']
        N = len(dimensions)

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        radar_colors = [GOOD, BLUE, WARNING]

        for i, opp in enumerate(top3):
            raw = opp.get('scores', {})
            vals = [min(100, raw.get(k, 0) * 4) for k in dim_keys]
            vals += vals[:1]

            short_title = (opp.get('title', '') or '')[:22]
            label = f"#{i+1} {short_title}{'...' if len(opp.get('title', '') or '') > 22 else ''}"
            ax.plot(angles, vals, 'o-', linewidth=2, color=radar_colors[i], label=label)
            ax.fill(angles, vals, alpha=0.10, color=radar_colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25', '50', '75', '100'], fontsize=8)
        ax.set_title(f'RADAR SCORE: {keyword.upper()}',
                     fontweight='bold', fontsize=13, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.12), fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/radar.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ radar.png", file=sys.stderr)
    else:
        print(f"  ⚠️ radar.png skipped: no scored products", file=sys.stderr)

    # --- Chart 5: comparison.png — Top Opportunities Multi-Metric Comparison ---
    if len(opportunities) >= 2:
        top_n = opportunities[:min(8, len(opportunities))]

        price_vals = [o.get('price', 0) for o in top_n]
        review_vals = [o.get('reviews', 0) for o in top_n]
        sales_vals = [o.get('monthly_sales', 0) for o in top_n]
        score_vals = [o.get('score', 0) for o in top_n]

        def _normalize(vals):
            mx = max(vals) if max(vals) > 0 else 1
            return [v / mx * 100 for v in vals]

        norm_price = _normalize(price_vals)
        norm_reviews = _normalize(review_vals)
        norm_sales = _normalize(sales_vals)
        norm_scores = _normalize(score_vals)

        x = np.arange(len(top_n))
        width = 0.2

        fig, ax = plt.subplots(figsize=(max(12, len(top_n) * 1.6), 6))

        b1 = ax.bar(x - 1.5 * width, norm_price,   width, label='Price',    color=BLUE,    edgecolor='white', linewidth=1.5)
        b2 = ax.bar(x - 0.5 * width, norm_reviews, width, label='Reviews',  color=WARNING, edgecolor='white', linewidth=1.5)
        b3 = ax.bar(x + 0.5 * width, norm_sales,   width, label='Sales/mo', color=GOOD,    edgecolor='white', linewidth=1.5)
        b4 = ax.bar(x + 1.5 * width, norm_scores,  width, label='Score',    color=PURPLE,  edgecolor='white', linewidth=1.5)

        for bar, val in zip(b1, price_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'${val:.0f}', ha='center', va='bottom', fontsize=7, rotation=90)
        for bar, val in zip(b2, review_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    str(int(val)), ha='center', va='bottom', fontsize=7, rotation=90)
        for bar, val in zip(b3, sales_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    str(int(val)), ha='center', va='bottom', fontsize=7, rotation=90)
        for bar, val in zip(b4, score_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    str(int(val)), ha='center', va='bottom', fontsize=7, rotation=90)

        tick_labels = [
            f"#{i+1} {(o.get('title', '') or '')[:18]}{'…' if len(o.get('title', '') or '') > 18 else ''}"
            for i, o in enumerate(top_n)
        ]
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels, rotation=20, ha='right', fontsize=9)
        ax.set_ylabel('Normalized Score (0–100)', fontsize=11)
        ax.set_title(f'PRODUCT COMPARISON: {keyword.upper()} — Top {len(top_n)} Opportunities',
                     fontweight='bold', fontsize=13, pad=15)
        ax.legend(fontsize=10, loc='upper right')
        ax.set_ylim(0, 135)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ comparison.png", file=sys.stderr)
    else:
        print(f"  ⚠️ comparison.png skipped: need ≥2 products, got {len(opportunities)}", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Product Opportunity Finder')
    parser.add_argument('params', nargs='?', help='JSON parameters: {"keyword": "yoga accessories"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    parser.add_argument('--output', type=str, help='Save raw JSON result to file path for later merging')
    parser.add_argument('--merge', nargs='+', type=str, help='Merge batch JSON files and generate unified charts')
    parser.add_argument('--sort', default='score', choices=['score', 'sales', 'growth'], help='Sort key for --merge output')

    args = parser.parse_args()

    if args.merge:
        result = merge_and_chart(args.merge, sort_key=args.sort, chart_dir=args.chart)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not args.params:
        parser.error('params is required unless --merge is used')

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(f"Invalid JSON: {args.params}", file=sys.stderr)
        sys.exit(1)

    keyword = params.get('keyword')
    if not keyword:
        print("Missing required parameter: keyword", file=sys.stderr)
        sys.exit(1)

    market = params.get('market', 'US')
    preset = params.get('preset', 'balanced')

    result = find_opportunities(
        keyword=keyword,
        market=market,
        preset=preset,
        max_reviews=params.get('max_reviews'),
        min_rating=params.get('min_rating'),
        min_price=params.get('min_price'),
        max_price=params.get('max_price'),
        min_sales=params.get('min_sales')
    )

    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    output = {k: v for k, v in result.items()}
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
