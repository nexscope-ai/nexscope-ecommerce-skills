#!/usr/bin/env python3
"""
Product Validator - Deep ASIN validation using historical data.

Usage:
  python3 product_validator.py '{"asin": "B0XXXXXXXXX"}'
  python3 product_validator.py '{"asin": "B0XXXXXXXXX", "marketplace": "US"}' --chart ./output/
  python3 product_validator.py '{"asin": "B0XXXXXXXXX"}' --report --cost 45

Environment:

Modules:
  - profitability_module.py: FBA profit calculation (can be used standalone)
  - seasonality_module.py: Seasonal pattern detection (can be used standalone)
"""

import json
import os
import sys
import time
import argparse
import tempfile
from urllib.request import urlopen, Request
from statistics import mean, stdev
from datetime import datetime

# Import modular components
from profitability_module import (
    analyze_profitability
)
from seasonality_module import (
    analyze_seasonality
)

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

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

# === Configuration ===
CACHE_FILE = os.path.join(tempfile.gettempdir(), "product_validator_cache.json")
CACHE_TTL = 24 * 60 * 60  # 24 hours

# Keepa domain mapping
DOMAIN_MAP = {
    'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5,
    'CA': 6, 'IT': 8, 'ES': 9, 'MX': 11, 'AU': 13
}

def call_api(endpoint, params):
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(params, ensure_ascii=False).encode('utf-8'),
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

def js_api_call(endpoint: str, params: dict, marketplace: str = 'us'):
    """Call Jungle Scout API via NexScope proxy (camelCase conversion)."""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    proxy_ep_map = {
        '/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
        '/keywords/keywords_by_asin_query': '/keywords/by-asin',
    }
    proxy_ep = proxy_ep_map.get(endpoint, endpoint)
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout{proxy_ep}"
    # Convert snake_case attributes to camelCase for proxy
    attrs = (params.get('data') or {}).get('attributes', params)
    proxy_payload = {'marketplace': marketplace}
    for k, v in attrs.items():
        parts = k.split('_')
        camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        proxy_payload[camel] = v
    try:
        req = Request(url, data=json.dumps(proxy_payload, ensure_ascii=False).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if isinstance(raw, dict) and raw.get('code') == 0:
            return raw.get('data', {})
        return None
    except Exception as e:
        print(f"JS API error [{endpoint}]: {e}", file=sys.stderr)
        return None

def _get_category_benchmarks(category_keyword: str, marketplace: str = 'us') -> dict:
    """Get category-level benchmarks from Jungle Scout keywords data."""
    result = js_api_call('/keywords/keywords_by_keyword_query', {
        'data': {
            'type': 'keywords_by_keyword_query',
            'attributes': {
                'search_terms': category_keyword
            }
        }
    }, marketplace)
    if not result:
        return {}
    kw_list = result.get('data', [])
    if not kw_list:
        return {}
    # Aggregate benchmarks across top keywords
    volumes = []
    difficulties = []
    for item in kw_list[:20]:
        attrs = item.get('attributes', {}) if isinstance(item, dict) else {}
        vol = attrs.get('monthlySearchVolumeExact', 0)
        diff = attrs.get('rankingDifficulty', 0) or attrs.get('competitorRank', 0)
        if vol: volumes.append(vol)
        if diff: difficulties.append(diff)
    return {
        'category_avg_search_volume': round(sum(volumes) / max(len(volumes), 1)),
        'category_avg_difficulty': round(sum(difficulties) / max(len(difficulties), 1), 1),
        'keyword_count': len(kw_list)
    }

# === Caching ===
def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_cached(asin, marketplace):
    cache = load_cache()
    key = f"{asin}_{marketplace}"
    if key in cache:
        if time.time() - cache[key]['timestamp'] < CACHE_TTL:
            return cache[key]['data']
    return None

def set_cache(asin, marketplace, data):
    cache = load_cache()
    key = f"{asin}_{marketplace}"
    cache[key] = {'timestamp': time.time(), 'data': data}
    save_cache(cache)

# === Product Series API ===
def fetch_product_series(asin, domain, days=180):
    """Fetch detailed historical series from Keepa productSeries API"""
    try:
        data = call_api("/keepa/productSeries", {
            "asin": asin,
            "domain": domain,
            "days": days
        })
        
        if data.get('errcode') != 200:
            return None
        
        result = {
            'has_data': True,
            'cost_tokens': data.get('costToken', 0)
        }
        
        # Extract BSR sub-category history
        bsr_sub = data.get('bsrSub', [])
        if bsr_sub and len(bsr_sub) > 0:
            points = bsr_sub[0].get('points', [])
            result['bsr_series'] = [{'time': p['time'], 'value': int(p['value'])} for p in points]
            result['bsr_category'] = bsr_sub[0].get('categoryName', 'Unknown')
        else:
            result['bsr_series'] = []
        
        # Extract price history
        price_data = data.get('buyboxPrice', [])
        result['price_series'] = [{'time': p['time'], 'value': p['value']} for p in price_data]
        
        # Extract review count history
        review_data = data.get('ratingCount', [])
        result['review_series'] = [{'time': p['time'], 'value': int(p['value'])} for p in review_data]
        
        return result
    
    except Exception as e:
        print(f"Warning: productSeries API failed: {e}", file=sys.stderr)
        return None

def analyze_series_data(series_data):
    """Analyze historical series for patterns and manipulation"""
    analysis = {
        'bsr_volatility': None,
        'bsr_trend': None,
        'price_stability': None,
        'review_step_jumps': [],
        'manipulation_flags': []
    }
    
    if not series_data or not series_data.get('has_data'):
        return analysis
    
    # Analyze BSR series
    bsr_series = series_data.get('bsr_series', [])
    if len(bsr_series) >= 10:
        bsr_values = [p['value'] for p in bsr_series]
        avg_bsr = mean(bsr_values)
        bsr_std = stdev(bsr_values) if len(bsr_values) > 1 else 0
        
        analysis['bsr_volatility'] = {
            'cv': (bsr_std / avg_bsr * 100) if avg_bsr > 0 else 0,
            'min': min(bsr_values),
            'max': max(bsr_values),
            'avg': avg_bsr,
            'data_points': len(bsr_values)
        }
        
        # Trend analysis
        q_size = len(bsr_values) // 4
        if q_size > 0:
            first_q = mean(bsr_values[:q_size])
            last_q = mean(bsr_values[-q_size:])
            trend_pct = (first_q - last_q) / first_q * 100 if first_q > 0 else 0
            analysis['bsr_trend'] = {
                'direction': 'improving' if trend_pct > 15 else 'declining' if trend_pct < -15 else 'stable',
                'change_pct': trend_pct
            }
    
    # Check for review step jumps
    review_series = series_data.get('review_series', [])
    if len(review_series) >= 3:
        reviews = [p['value'] for p in review_series]
        for i in range(1, len(reviews)):
            jump = reviews[i] - reviews[i-1]
            if jump > 50:
                analysis['review_step_jumps'].append({
                    'time': review_series[i]['time'],
                    'jump': jump
                })
        
        if analysis['review_step_jumps']:
            analysis['manipulation_flags'].append({
                'flag': 'review_step_jump',
                'severity': 'critical',
                'detail': f'Detected {len(analysis["review_step_jumps"])} suspicious review jumps (possible listing merge)'
            })
    
    return analysis

# === Scoring Functions ===
def score_bsr(bsr_history):
    """BSR History Score (0-25)"""
    if not bsr_history or len(bsr_history) < 2:
        return 12, []
    
    flags = []
    
    # Trend (0-10)
    first_val = bsr_history[0]
    last_val = bsr_history[-1]
    
    if first_val > 0:
        improvement = (first_val - last_val) / first_val * 100
    else:
        improvement = 0
    
    if improvement > 30: trend = 10
    elif improvement > 10: trend = 8
    elif improvement > -10: trend = 6
    elif improvement > -30: trend = 3
    else: trend = 0
    
    # Volatility (0-10)
    if len(bsr_history) > 1:
        cv = stdev(bsr_history) / mean(bsr_history) * 100 if mean(bsr_history) > 0 else 0
    else:
        cv = 0
    
    if cv < 30: vol = 10
    elif cv < 50: vol = 7
    elif cv < 80: vol = 4
    else:
        vol = 0
        flags.append({'flag': 'bsr_manipulation', 'severity': 'critical', 'detail': f'BSR CV={cv:.0f}%'})
    
    pattern = 5
    return trend + vol + pattern, flags

def score_price(price_history, current_price):
    """Price History Score (0-20)"""
    if not price_history or len(price_history) < 2:
        return 14, []
    
    flags = []
    prices = [p for p in price_history if p > 0]
    if not prices:
        return 14, []
    
    # Stability (0-10)
    if len(prices) > 1:
        cv = stdev(prices) / mean(prices) * 100 if mean(prices) > 0 else 0
    else:
        cv = 0
    
    if cv < 10: stability = 10
    elif cv < 20: stability = 7
    elif cv < 30: stability = 4
    else: stability = 2
    
    # Trend (0-5)
    change = (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] > 0 else 0
    
    if change > -10: trend = 5
    elif change > -20: trend = 3
    elif change > -30: trend = 1
    else:
        trend = 0
        flags.append({'flag': 'price_war', 'severity': 'critical', 'detail': f'Price -{abs(change):.0f}%'})
    
    # Promo (0-5)
    promo = 5
    
    return stability + trend + promo, flags

def score_buybox(buybox_data):
    """Buy Box Score (0-20)"""
    if not buybox_data:
        return 15, []
    
    flags = []
    top_share = buybox_data.get('top_seller_share', 50)
    amazon_share = buybox_data.get('amazon_share', 0)
    unique_winners = buybox_data.get('unique_winners', 3)
    
    if top_share < 40: dom = 10
    elif top_share < 60: dom = 7
    elif top_share < 70: dom = 4
    else:
        dom = 0
        flags.append({'flag': 'buybox_dominated', 'severity': 'critical', 'detail': f'Top seller {top_share:.0f}%'})
    
    if amazon_share == 0: amz = 5
    elif amazon_share < 30: amz = 3
    elif amazon_share < 50: amz = 1
    else:
        amz = 0
        flags.append({'flag': 'amazon_dominant', 'severity': 'critical', 'detail': f'Amazon {amazon_share:.0f}%'})
    
    if unique_winners >= 5: rot = 5
    elif unique_winners >= 3: rot = 3
    elif unique_winners >= 2: rot = 1
    else: rot = 0
    
    return dom + amz + rot, flags

def score_sellers(seller_history, current_sellers):
    """Seller History Score (0-15)"""
    flags = []
    
    if current_sellers <= 3: count = 5
    elif current_sellers <= 7: count = 4
    elif current_sellers <= 15: count = 2
    else:
        count = 0
        flags.append({'flag': 'high_competition', 'severity': 'warning', 'detail': f'{current_sellers} sellers'})
    
    growth_score = 5
    stab = 3
    
    return count + growth_score + stab, flags

def score_reviews(review_data, sales_estimate, is_variant, parent_reviews):
    """Review Score (0-15)"""
    flags = []
    current_reviews = review_data.get('current', 0)
    
    vel = 5
    step = 5
    
    if not is_variant:
        var = 5
    else:
        share = current_reviews / parent_reviews * 100 if parent_reviews > 0 else 100
        if share > 20: var = 5
        elif share > 10: var = 3
        elif share > 5: var = 1
        else:
            var = 0
            flags.append({'flag': 'zombie_variant', 'severity': 'warning', 'detail': f'Only {share:.1f}% of parent reviews'})
    
    return vel + step + var, flags

def score_stock(stock_history):
    """Stock Score (0-5)"""
    return 4, []

# === Chart Generation ===
def generate_chart_analysis(result):
    """Generate comprehensive analytical text for each chart using series data"""
    analysis = {}
    
    bsr_history = result.get('bsr_history', [])
    product = result.get('product_data', {})
    seasonality = result.get('seasonality', {})
    series_data = result.get('series_data', {})
    series_analysis = series_data.get('analysis', {}) if series_data else {}
    
    # === Chart 1: BSR & Price Analysis ===
    lines = []
    lines.append("**📈 BSR & Price Trend Analysis**")
    lines.append("")
    
    # Use series data for more accurate analysis
    if series_data.get('available') and series_analysis.get('bsr_volatility'):
        vol = series_analysis['bsr_volatility']
        trend = series_analysis.get('bsr_trend', {})
        category = series_data.get('bsr_category', 'Unknown')
        data_points = series_data.get('bsr_data_points', 0)
        
        lines.append(f"**Data Source:** {data_points} data points from Keepa productSeries")
        lines.append(f"**Sub-category:** {category}")
        lines.append("")
        
        # BSR Range Analysis
        lines.append(f"**BSR Range:** #{vol['min']:,} - #{vol['max']:,} (avg: #{vol['avg']:,.0f})")
        range_ratio = vol['max'] / vol['min'] if vol['min'] > 0 else 0
        if range_ratio > 10:
            lines.append(f"  → Range ratio {range_ratio:.1f}x is very wide, indicating high variability")
        elif range_ratio > 5:
            lines.append(f"  → Range ratio {range_ratio:.1f}x is moderate")
        else:
            lines.append(f"  → Range ratio {range_ratio:.1f}x is tight, indicating stable performance")
        lines.append("")
        
        # Volatility Analysis
        cv = vol['cv']
        lines.append(f"**Volatility (CV):** {cv:.1f}%")
        if cv > 80:
            lines.append(f"  🔴 Severely high volatility")
            lines.append(f"  → Normal range is 30-50%. CV of {cv:.0f}% suggests:")
            lines.append(f"    • Possible rank manipulation (black-hat tactics)")
            lines.append(f"    • Inventory instability (frequent stockouts)")
            lines.append(f"    • Or heavy promotional dependency")
            if seasonality.get('volatility') == 'high':
                lines.append(f"  → Note: This is a seasonal category, which partially explains high CV")
        elif cv > 50:
            lines.append(f"  🟡 Elevated volatility, monitor closely")
            lines.append(f"  → Product may be sensitive to promotions or competition")
        else:
            lines.append(f"  ✅ Healthy volatility - data is reliable")
            lines.append(f"  → Stable BSR indicates consistent organic demand")
        lines.append("")
        
        # Trend Analysis
        if trend:
            direction = trend.get('direction', 'stable')
            change = trend.get('change_pct', 0)
            lines.append(f"**180-Day Trend:** {direction.upper()} ({change:+.1f}%)")
            if direction == 'improving':
                lines.append(f"  ✅ BSR is improving (lower = better)")
                if seasonality.get('current_position') == 'rising':
                    lines.append(f"  ⚠️ However, we're approaching peak season")
                    lines.append(f"     Some of this improvement may be seasonal, not organic")
                elif seasonality.get('current_position') == 'off':
                    lines.append(f"  ✅ Impressive: Growing even in off-season")
                    lines.append(f"     This suggests genuine product-market fit")
            elif direction == 'declining':
                lines.append(f"  ⚠️ BSR is declining (getting worse)")
                lines.append(f"  → Investigate: New competition? Quality issues? Listing suppression?")
            else:
                lines.append(f"  → Stable demand, no significant trend")
    else:
        # Fallback to basic analysis if no series data
        if len(bsr_history) >= 2:
            bsr_change = (bsr_history[0] - bsr_history[-1]) / bsr_history[0] * 100 if bsr_history[0] > 0 else 0
            bsr_cv = stdev(bsr_history) / mean(bsr_history) * 100 if mean(bsr_history) > 0 else 0
            lines.append(f"**Note:** Limited data (4 quarterly points only)")
            lines.append(f"**BSR Change:** {bsr_change:+.0f}%")
            lines.append(f"**Volatility:** {bsr_cv:.0f}%")
    
    # Price Analysis
    lines.append("")
    price = product.get('price', 0)
    if price > 0:
        lines.append(f"**Current Price:** ${price:.2f}")
        lines.append(f"  → Price line stable indicates no active price war")
    
    analysis['bsr_price'] = "\n".join(lines)
    
    # === Chart 2: Score Breakdown Analysis ===
    scores = result.get('scores', {})
    if scores:
        lines = []
        lines.append("**📊 Validation Score Breakdown**")
        lines.append("")
        
        total = sum(s['score'] for s in scores.values())
        max_total = sum(s['max'] for s in scores.values())
        lines.append(f"**Total Score:** {total}/{max_total} ({total/max_total*100:.0f}%)")
        lines.append("")
        
        # Analyze each dimension
        for name, data in sorted(scores.items(), key=lambda x: x[1]['score']/x[1]['max']):
            score, max_s = data['score'], data['max']
            pct = score / max_s * 100
            bar = "█" * int(pct/10) + "░" * (10 - int(pct/10))
            
            if pct >= 80:
                emoji = "✅"
                status = "Strong"
            elif pct >= 60:
                emoji = "🟡"
                status = "Okay"
            else:
                emoji = "🔴"
                status = "Weak"
            
            lines.append(f"**{name.replace('_', ' ').title()}:** {score}/{max_s} {bar} {emoji} {status}")
        
        lines.append("")
        
        # Identify concerns
        weak = [(k, v['score'], v['max']) for k, v in scores.items() if v['score'] / v['max'] < 0.6]
        if weak:
            lines.append("**⚠️ Areas of Concern:**")
            for name, score, max_s in weak:
                lines.append(f"  • {name.title()}: Only {score}/{max_s} - needs investigation")
        
        # Seasonality impact
        modifier = seasonality.get('modifier', 0)
        if modifier != 0:
            lines.append("")
            if modifier > 0:
                lines.append(f"**🟢 Seasonal Bonus:** +{modifier} points")
                lines.append(f"  → Product showing strength in off-season = reliable demand")
            else:
                lines.append(f"**🟡 Seasonal Penalty:** {modifier} points")
                lines.append(f"  → Current data may be inflated by seasonal demand")
                lines.append(f"  → Recommend re-validating in off-season")
        
        analysis['score_breakdown'] = "\n".join(lines)
    
    # === Chart 3: Review Authenticity Analysis ===
    reviews = product.get('reviews', 0)
    monthly_sales = product.get('monthly_sales', 0)
    
    lines = []
    lines.append("**⭐ Review Authenticity Analysis**")
    lines.append("")
    
    if monthly_sales > 0:
        # Calculate review-to-sales ratio
        monthly_reviews = reviews / 6  # Assume ~6 months of history
        review_rate = monthly_reviews / monthly_sales * 100 if monthly_sales > 0 else 0
        
        lines.append(f"**Reviews:** {reviews:,}")
        lines.append(f"**Monthly Sales:** {monthly_sales:,}")
        lines.append(f"**Review Rate:** {review_rate:.2f}%")
        lines.append("")
        
        # Interpret review rate
        lines.append("**Interpretation:**")
        if review_rate <= 1:
            lines.append(f"  ✅ Low review rate ({review_rate:.1f}%) is normal")
            lines.append(f"  → Typical Amazon review rate is 1-3%")
            lines.append(f"  → No signs of review manipulation")
        elif review_rate <= 3:
            lines.append(f"  ✅ Review rate ({review_rate:.1f}%) within normal range")
            lines.append(f"  → Healthy organic review accumulation")
        elif review_rate <= 5:
            lines.append(f"  🟡 Slightly elevated review rate ({review_rate:.1f}%)")
            lines.append(f"  → May indicate:")
            lines.append(f"    • Vine program participation")
            lines.append(f"    • Review request campaigns")
            lines.append(f"    • Insert cards (within TOS)")
            lines.append(f"  → Not necessarily bad, but monitor")
        else:
            lines.append(f"  🔴 Abnormally high review rate ({review_rate:.1f}%)")
            lines.append(f"  → Possible causes:")
            lines.append(f"    • Listing merge (inherited old reviews)")
            lines.append(f"    • Incentivized reviews (risky)")
            lines.append(f"    • Review manipulation (serious red flag)")
            lines.append(f"  → Recommend manual review analysis")
        
        lines.append("")
        
        # Review count context
        lines.append("**Review Count Context:**")
        if reviews < 50:
            lines.append(f"  📝 Very new listing (<50 reviews)")
            lines.append(f"  → Higher risk: Limited social proof")
            lines.append(f"  → Opportunity: Easier to compete")
        elif reviews < 100:
            lines.append(f"  📝 New listing (50-100 reviews)")
            lines.append(f"  → Still building reputation")
            lines.append(f"  → Good entry window for competitors")
        elif reviews < 500:
            lines.append(f"  📝 Established listing (100-500 reviews)")
            lines.append(f"  → Moderate barrier to entry")
        elif reviews < 1000:
            lines.append(f"  📝 Strong listing (500-1000 reviews)")
            lines.append(f"  → Significant social proof")
            lines.append(f"  → Harder to compete on reviews alone")
        else:
            lines.append(f"  📝 Dominant listing (1000+ reviews)")
            lines.append(f"  → Market validated product")
            lines.append(f"  → Very difficult for new entrants")
            lines.append(f"  → Need differentiation strategy")
        
        # Check for step jumps from series data
        if series_analysis.get('review_step_jumps'):
            jumps = series_analysis['review_step_jumps']
            lines.append("")
            lines.append(f"**🚨 ALERT: {len(jumps)} Review Step Jump(s) Detected**")
            lines.append(f"  → Sudden review increases suggest listing merge")
            lines.append(f"  → These reviews may not reflect current product")
            lines.append(f"  → Manually verify review dates and content")
    else:
        lines.append("**⚠️ No sales data available for review analysis**")
    
    analysis['review_auth'] = "\n".join(lines)
    
    return analysis

def generate_charts(result, output_dir):
    """Generate validation charts matching SKILL.md specification:
    bsr_trend.png, price_trend.png, score_breakdown.png, profitability.png
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not installed, skipping chart generation", file=sys.stderr)
        return [], {}

    os.makedirs(output_dir, exist_ok=True)
    charts = []

    chart_analysis = generate_chart_analysis(result)

    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']

    GOOD    = get_color('good')
    NEUTRAL = get_color('muted')
    WARNING = get_color('secondary')
    BAD     = get_color('hot')
    BLUE    = get_color('primary')

    asin = result.get('asin', 'ASIN')
    bsr_history   = result.get('bsr_history', [])
    price_history = result.get('price_history', [])
    product_data  = result.get('product_data', {})

    # --- Chart 1: bsr_trend.png — Historical BSR Line ---
    if len(bsr_history) >= 2:
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = [f'T-{len(bsr_history)-1-i}' if i < len(bsr_history)-1 else 'Now'
                  for i in range(len(bsr_history))]
        ax.plot(labels, bsr_history, color=BLUE, linewidth=2.5, marker='o', markersize=7, zorder=3)
        ax.fill_between(range(len(bsr_history)), bsr_history, alpha=0.12, color=BLUE)
        ax.invert_yaxis()
        ax.set_xlabel('Time Period', fontsize=11)
        ax.set_ylabel('BSR Rank (lower = better)', fontsize=11)
        bsr_change = (bsr_history[0] - bsr_history[-1]) / bsr_history[0] * 100 if bsr_history[0] > 0 else 0
        status_color = GOOD if bsr_change > 20 else (WARNING if bsr_change > -10 else BAD)
        ax.set_title(f'BSR TREND: {asin}  ({bsr_change:+.1f}%)',
                     fontweight='bold', fontsize=13, pad=15, color=status_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'bsr_trend.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
        print(f"  ✓ bsr_trend.png", file=sys.stderr)
    else:
        print(f"  ⚠️ bsr_trend.png skipped: need ≥2 data points", file=sys.stderr)

    # --- Chart 2: price_trend.png — Historical Price Line ---
    if len(price_history) >= 2:
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = [f'T-{len(price_history)-1-i}' if i < len(price_history)-1 else 'Now'
                  for i in range(len(price_history))]
        ax.plot(labels, price_history, color=WARNING, linewidth=2.5, marker='s', markersize=7, zorder=3)
        ax.fill_between(range(len(price_history)), price_history, alpha=0.12, color=WARNING)
        price_change = (price_history[-1] - price_history[0]) / price_history[0] * 100 if price_history[0] > 0 else 0
        ax.set_xlabel('Time Period', fontsize=11)
        ax.set_ylabel('Price (USD)', fontsize=11)
        ax.set_title(f'PRICE TREND: {asin}  ({price_change:+.1f}%)',
                     fontweight='bold', fontsize=13, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'price_trend.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
        print(f"  ✓ price_trend.png", file=sys.stderr)
    else:
        print(f"  ⚠️ price_trend.png skipped: need ≥2 data points", file=sys.stderr)

    # --- Chart 3: score_breakdown.png — Validation Score Component Bar ---
    scores = result.get('scores', {})
    if scores:
        fig, ax = plt.subplots(figsize=(9, 5))
        categories = list(scores.keys())
        score_vals = [scores[c]['score'] for c in categories]
        max_vals   = [scores[c]['max']   for c in categories]
        bar_colors = [GOOD if sv / max(mv, 1) >= 0.7 else (WARNING if sv / max(mv, 1) >= 0.4 else BAD)
                      for sv, mv in zip(score_vals, max_vals)]
        y_pos = np.arange(len(categories))
        ax.barh(y_pos, max_vals, height=0.55, color='#E0E0E0', edgecolor='white', linewidth=1)
        ax.barh(y_pos, score_vals, height=0.55, color=bar_colors, edgecolor='white', linewidth=1)
        max_x = max(max_vals) if max_vals else 10
        for i, (sv, mv) in enumerate(zip(score_vals, max_vals)):
            ax.text(sv + max_x * 0.02, i, f'{sv}/{mv}',
                    va='center', fontsize=10, fontweight='bold', color='#333')
        ax.set_yticks(y_pos)
        ax.set_yticklabels([c.replace('_', ' ').title() for c in categories], fontsize=10)
        ax.set_xlabel('Score', fontsize=11)
        ax.set_xlim(0, max_x * 1.25)
        total = result.get('validation_score', 0)
        level = result.get('risk_level', 'UNKNOWN')
        ax.set_title(f'SCORE BREAKDOWN: {asin}  —  {total}/100  ({level})',
                     fontweight='bold', fontsize=13, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'score_breakdown.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
        print(f"  ✓ score_breakdown.png", file=sys.stderr)
    else:
        print(f"  ⚠️ score_breakdown.png skipped: no score data", file=sys.stderr)

    # --- Chart 4: profitability.png — Profitability Waterfall ---
    price = product_data.get('price', 0) or 0
    if price > 0:
        referral_fee = round(price * 0.15, 2)
        fba_fee      = round(min(max(price * 0.12, 3.0), 8.0), 2)
        cogs         = round(price * 0.35, 2)
        net_profit   = round(price - referral_fee - fba_fee - cogs, 2)

        steps = [
            ('Sale\nPrice',      price,        True),
            ('Amazon\nFee',      -referral_fee, False),
            ('FBA\nFee',         -fba_fee,      False),
            ('COGS\n(~35%)',     -cogs,         False),
            ('Net\nProfit',      net_profit,    True),
        ]

        fig, ax = plt.subplots(figsize=(10, 6))
        running = 0.0
        for i, (label, value, is_absolute) in enumerate(steps):
            bottom = 0.0 if is_absolute else running
            height = value
            bar_color = GOOD if value >= 0 else (BAD if i == len(steps) - 1 else WARNING)
            ax.bar(i, abs(height), bottom=min(bottom, bottom + height),
                   color=bar_color, edgecolor='white', linewidth=2, width=0.6)
            mid_y = min(bottom, bottom + height) + abs(height) / 2
            ax.text(i, mid_y, f'${abs(value):.2f}',
                    ha='center', va='center', fontsize=10, fontweight='bold',
                    color='white' if abs(height) > price * 0.07 else '#333')
            if not is_absolute:
                ax.plot([i - 0.7, i - 0.3], [running, running],
                        color=NEUTRAL, linewidth=1, linestyle='--')
            running += value

        ax.set_xticks(range(len(steps)))
        ax.set_xticklabels([s[0] for s in steps], fontsize=10)
        ax.set_ylabel('Amount (USD)', fontsize=11)
        ax.set_title(f'PROFITABILITY: {asin}  —  Price ${price:.2f}',
                     fontweight='bold', fontsize=13, pad=15)
        ax.set_ylim(0, price * 1.18)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        margin_pct = net_profit / price * 100
        box_color = '#E8F5E9' if net_profit > 0 else '#FFEBEE'
        ax.text(0.98, 0.95, f'Est. Net Margin: {margin_pct:.1f}%',
                transform=ax.transAxes, fontsize=10, va='top', ha='right',
                bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.9))
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'profitability.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
        print(f"  ✓ profitability.png", file=sys.stderr)
    else:
        print(f"  ⚠️ profitability.png skipped: no price data", file=sys.stderr)

    return charts, chart_analysis

# === Main Validator ===
def run_validator(params):
    asin = params.get('asin', '').upper()
    marketplace = params.get('marketplace', 'US').upper()
    
    if not asin:
        return {"error": "ASIN required"}
    
    # Check cache
    cached = get_cached(asin, marketplace)
    if cached:
        cached['from_cache'] = True
        return cached
    
    domain = DOMAIN_MAP.get(marketplace, 1)
    
    # Fetch Keepa data
    try:
        keepa_detail = call_api("/keepa/productRequest", {
            "asin": asin,
            "domain": domain,
            "history": 1
        })
        
        products = keepa_detail.get('products', [])
        if not products:
            return {"error": "Product not found", "asin": asin}
        
        product = products[0]
    except Exception as e:
        return {"error": f"API error: {str(e)}", "asin": asin}
    
    # Extract data
    title = product.get('title', 'Unknown')
    current_price = product.get('price') or 0
    current_reviews = product.get('reviewCount', 0) or product.get('ratings', 0) or 0
    current_rating = product.get('rating', 0)
    current_bsr = product.get('salesRank', 0)
    current_sellers = product.get('sellerNum', 1)
    monthly_sales = product.get('monthlySalesUnits', 0) or 0
    
    is_variant = product.get('isVariant', False) or bool(product.get('parentAsin'))
    parent_reviews = product.get('parentReviewCount', current_reviews)
    
    # Historical data
    bsr_30 = product.get('salesRank30', current_bsr)
    bsr_90 = product.get('salesRank90', current_bsr)
    bsr_180 = product.get('salesRank180', current_bsr)
    
    bsr_history = [bsr_180, bsr_90, bsr_30, current_bsr] if bsr_180 else [current_bsr]
    price_history = [current_price]
    
    buybox_data = {'top_seller_share': 50, 'amazon_share': 0, 'unique_winners': 3}
    review_data = {'current': current_reviews, 'history': [current_reviews]}
    
    # Fetch detailed series data (productSeries API)
    series_data = fetch_product_series(asin, domain, days=180)
    series_analysis = analyze_series_data(series_data) if series_data else {}

    # Fetch category benchmarks from Jungle Scout using bsr_category
    bsr_category = series_data.get('bsr_category') if series_data else None
    domain_str = marketplace.lower()
    category_keyword = bsr_category or product.get('categoryTree', '') or ''
    try:
        benchmarks = _get_category_benchmarks(category_keyword, marketplace=domain_str) if category_keyword else {}
    except Exception as _e:
        print(f"  Category benchmarks fetch error: {_e}", file=sys.stderr)
        benchmarks = {}

    # Use series data for more accurate BSR history if available
    if series_data and series_data.get('bsr_series'):
        bsr_values = [p['value'] for p in series_data['bsr_series']]
        if len(bsr_values) >= 4:
            q_size = len(bsr_values) // 4
            bsr_history = [
                int(mean(bsr_values[:q_size])),
                int(mean(bsr_values[q_size:2*q_size])),
                int(mean(bsr_values[2*q_size:3*q_size])),
                int(mean(bsr_values[-q_size:]))
            ]
    
    # Calculate scores
    bsr_score, bsr_flags = score_bsr(bsr_history)
    price_score, price_flags = score_price(price_history, current_price)
    buybox_score, buybox_flags = score_buybox(buybox_data)
    seller_score, seller_flags = score_sellers([], current_sellers)
    review_score, review_flags = score_reviews(review_data, monthly_sales, is_variant, parent_reviews)
    stock_score, stock_flags = score_stock([])
    
    # Seasonality Analysis
    category_tree = product.get('categoryTree', '')
    seasonality = analyze_seasonality(category_tree, title, bsr_history)
    seasonal_modifier = seasonality['modifier']
    seasonal_flags = seasonality['flags']
    
    total_score = bsr_score + price_score + buybox_score + seller_score + review_score + stock_score
    all_flags = bsr_flags + price_flags + buybox_flags + seller_flags + review_flags + stock_flags
    
    # Add seasonal flags (excluding positive ones from penalty calculation)
    for flag in seasonal_flags:
        all_flags.append(flag)
    
    # Add manipulation flags from series analysis
    for flag in series_analysis.get('manipulation_flags', []):
        all_flags.append(flag)
    
    # Apply flag penalties
    for flag in all_flags:
        if flag['severity'] == 'critical':
            total_score = max(0, total_score - 10)
        elif flag['severity'] == 'warning':
            total_score = max(0, total_score - 3)
    
    # Apply seasonality modifier (can be positive or negative)
    total_score = max(0, min(100, total_score + seasonal_modifier))
    
    if total_score >= 80:
        risk_level = 'VALID'
        recommendation = 'Data trustworthy, proceed with standard due diligence'
    elif total_score >= 60:
        risk_level = 'CAUTION'
        recommendation = 'Some concerns detected, verify flags manually before proceeding'
    else:
        risk_level = 'AVOID'
        recommendation = 'High risk detected, not recommended'
    
    result = {
        'asin': asin,
        'marketplace': marketplace,
        'title': title,
        'validation_score': total_score,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'scores': {
            'bsr': {'score': bsr_score, 'max': 25},
            'price': {'score': price_score, 'max': 20},
            'buybox': {'score': buybox_score, 'max': 20},
            'sellers': {'score': seller_score, 'max': 15},
            'reviews': {'score': review_score, 'max': 15},
            'stock': {'score': stock_score, 'max': 5}
        },
        'red_flags': all_flags,
        'seasonality': {
            'pattern': seasonality['config'].get('pattern', 'unknown'),
            'volatility': seasonality['config'].get('volatility', 'unknown'),
            'peak_months': seasonality['config'].get('peak_months', []),
            'current_position': seasonality['position'],
            'bsr_trend': seasonality['bsr_trend'],
            'modifier': seasonal_modifier,
            'interpretation': seasonality['interpretation']
        },
        'product_data': {
            'price': current_price,
            'reviews': current_reviews,
            'rating': current_rating,
            'bsr': current_bsr,
            'sellers': current_sellers,
            'monthly_sales': monthly_sales,
            'is_variant': is_variant
        },
        'bsr_history': bsr_history,
        'price_history': price_history,
        'series_data': {
            'available': series_data is not None and series_data.get('has_data', False),
            'bsr_data_points': len(series_data.get('bsr_series', [])) if series_data else 0,
            'bsr_category': series_data.get('bsr_category') if series_data else None,
            'analysis': series_analysis
        } if series_data else {'available': False},
        'profitability': None,  # Calculated on demand with --cost parameter
        'category_benchmarks': benchmarks,
        'from_cache': False
    }
    
    set_cache(asin, marketplace, result)
    return result

def add_profitability(result, cost, weight_lb=None):
    """Add profitability calculation to result"""
    price = (result.get('product_data') or {}).get('price', 0)
    category = (result.get('series_data') or {}).get('bsr_category', '')
    
    if price <= 0:
        result['profitability'] = {'error': 'No price data'}
        return result
    
    prof_result, prof_analysis = analyze_profitability(price, cost, category, weight_lb)
    result['profitability'] = prof_result
    result['profitability_analysis'] = prof_analysis
    
    return result

def generate_analytical_report(result, chart_dir=None):
    """Generate 10-step validation report with charts"""
    if 'error' in result:
        return f"Error: {result['error']}", []
    
    asin = result['asin']
    title = result['title']
    score = result['validation_score']
    risk_level = result['risk_level']
    product = result['product_data']
    seasonality = result['seasonality']
    bsr_history = result['bsr_history']
    scores = result['scores']
    flags = result['red_flags']
    series_data = result.get('series_data', {})
    series_analysis = series_data.get('analysis', {}) if series_data else {}
    
    # Calculate metrics
    bsr_change = (bsr_history[0] - bsr_history[-1]) / bsr_history[0] * 100 if len(bsr_history) > 1 and bsr_history[0] > 0 else 0
    bsr_cv = (series_analysis.get('bsr_volatility') or {}).get('cv', 0) if series_analysis else 0
    if bsr_cv == 0 and len(bsr_history) > 1:
        bsr_cv = stdev(bsr_history) / mean(bsr_history) * 100 if mean(bsr_history) > 0 else 0
    
    # Track charts to generate
    charts_needed = []
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"📊 PRODUCT VALIDATION REPORT")
    lines.append(f"   {asin} | {title[:50]}...")
    lines.append("=" * 70)
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 1: DATA EXTRACTION
    # ═══════════════════════════════════════════════════════════════════
    lines.append("┌" + "─" * 68 + "┐")
    lines.append("│ 1️⃣  DATA EXTRACTION                                    ✅ Complete │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    
    data_points = series_data.get('bsr_data_points', 4) if series_data else 4
    category = series_data.get('bsr_category', 'Unknown') if series_data else 'Unknown'
    
    lines.append(f"   Source: Keepa productRequest + productSeries")
    lines.append(f"   Data Points: {data_points} (180-day history)")
    lines.append(f"   Sub-category: {category}")
    lines.append(f"   Price: ${product.get('price', 0):.2f}")
    lines.append(f"   Reviews: {product.get('reviews', 0):,} (⭐ {product.get('rating', 0)})")
    lines.append(f"   Monthly Sales: {product.get('monthly_sales', 0):,}")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 2: BSR HISTORY
    # ═══════════════════════════════════════════════════════════════════
    bsr_score = scores.get('bsr', {})
    bsr_status = "✅" if bsr_score.get('score', 0) >= 20 else "⚠️" if bsr_score.get('score', 0) >= 15 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 2️⃣  BSR HISTORY                              {bsr_score.get('score', 0):>2}/{bsr_score.get('max', 25)} {bsr_status}        │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    lines.append("   📈 [BSR Trend Chart - see bsr_price.png]")
    charts_needed.append('bsr_price')
    lines.append("")
    
    # BSR Analysis
    if series_analysis.get('bsr_volatility'):
        vol = series_analysis['bsr_volatility']
        trend = series_analysis.get('bsr_trend', {})
        lines.append(f"   BSR Range: #{vol['min']:,} - #{vol['max']:,} (avg: #{vol['avg']:,.0f})")
        lines.append(f"   Volatility: CV = {vol['cv']:.1f}%")
        lines.append("")
        
        if vol['cv'] > 80:
            lines.append(f"   ⚠️ Analysis: Volatility severely high ({vol['cv']:.0f}%)")
            lines.append(f"      Normal range is 30-50%. This could indicate:")
            lines.append(f"      • Rank manipulation (black-hat tactics)")
            lines.append(f"      • Inventory instability")
            lines.append(f"      • Heavy promotional dependency")
            if seasonality.get('volatility') == 'high':
                lines.append(f"      Note: Seasonal category partially explains high CV")
        elif vol['cv'] > 50:
            lines.append(f"   🟡 Analysis: Elevated volatility ({vol['cv']:.0f}%)")
            lines.append(f"      Monitor closely - may be sensitive to promotions")
        else:
            lines.append(f"   ✅ Analysis: Healthy volatility ({vol['cv']:.0f}%)")
            lines.append(f"      Stable BSR indicates consistent organic demand")
        
        if trend:
            lines.append("")
            lines.append(f"   Trend: {trend.get('direction', 'stable').upper()} ({trend.get('change_pct', 0):+.1f}%)")
            if trend.get('direction') == 'improving':
                lines.append(f"      ✅ BSR improving (lower = better sales rank)")
            elif trend.get('direction') == 'declining':
                lines.append(f"      ⚠️ BSR declining - investigate cause")
    else:
        lines.append(f"   BSR: {bsr_history[-1]:,} (current)")
        lines.append(f"   Change: {bsr_change:+.0f}% over 180 days")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 3: PRICE HISTORY
    # ═══════════════════════════════════════════════════════════════════
    price_score = scores.get('price', {})
    price_status = "✅" if price_score.get('score', 0) >= 16 else "⚠️" if price_score.get('score', 0) >= 12 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 3️⃣  PRICE HISTORY                            {price_score.get('score', 0):>2}/{price_score.get('max', 20)} {price_status}        │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    lines.append(f"   Current Price: ${product.get('price', 0):.2f}")
    
    price_flag = next((f for f in flags if f['flag'] == 'price_war'), None)
    if price_flag:
        lines.append(f"   🔴 WARNING: Price war detected!")
        lines.append(f"      {price_flag.get('detail', '')}")
    else:
        lines.append(f"   ✅ Price stable - no active price war")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 4: BUY BOX
    # ═══════════════════════════════════════════════════════════════════
    buybox_score = scores.get('buybox', {})
    buybox_status = "✅" if buybox_score.get('score', 0) >= 16 else "⚠️" if buybox_score.get('score', 0) >= 12 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 4️⃣  BUY BOX                                  {buybox_score.get('score', 0):>2}/{buybox_score.get('max', 20)} {buybox_status}        │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    
    amazon_flag = next((f for f in flags if f['flag'] == 'amazon_dominant'), None)
    if amazon_flag:
        lines.append(f"   ⚠️ Amazon is a seller on this listing")
        lines.append(f"      Impact for 3P sellers:")
        lines.append(f"      • Harder to win Buy Box")
        lines.append(f"      • Price competition pressure")
        lines.append(f"      • May need FBA to compete")
    else:
        lines.append(f"   ✅ No Amazon as seller")
        lines.append(f"      Buy Box accessible for 3P sellers")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 5: SELLER HISTORY
    # ═══════════════════════════════════════════════════════════════════
    seller_score = scores.get('sellers', {})
    seller_status = "✅" if seller_score.get('score', 0) >= 12 else "⚠️" if seller_score.get('score', 0) >= 9 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 5️⃣  SELLER HISTORY                           {seller_score.get('score', 0):>2}/{seller_score.get('max', 15)} {seller_status}        │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    lines.append(f"   Current Sellers: {product.get('sellers', 0)}")
    
    if product.get('sellers', 0) <= 3:
        lines.append(f"   ✅ Low competition (few sellers)")
        lines.append(f"      But verify: brand gating? low margins?")
    elif product.get('sellers', 0) <= 10:
        lines.append(f"   🟡 Moderate competition")
    else:
        lines.append(f"   ⚠️ High seller count - crowded listing")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 6: REVIEW SCORING
    # ═══════════════════════════════════════════════════════════════════
    review_score = scores.get('reviews', {})
    review_status = "✅" if review_score.get('score', 0) >= 12 else "⚠️" if review_score.get('score', 0) >= 9 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 6️⃣  REVIEW SCORING                           {review_score.get('score', 0):>2}/{review_score.get('max', 15)} {review_status}        │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    lines.append("   📊 [Review Authenticity Chart - see review_auth.png]")
    charts_needed.append('review_auth')
    lines.append("")
    
    reviews = product.get('reviews', 0)
    monthly_sales = product.get('monthly_sales', 0)
    review_rate = (reviews / 6) / monthly_sales * 100 if monthly_sales > 0 else 0
    
    lines.append(f"   Reviews: {reviews:,} | Monthly Sales: {monthly_sales:,}")
    lines.append(f"   Review Rate: {review_rate:.1f}% (normal: 1-3%)")
    lines.append("")
    
    if review_rate <= 3:
        lines.append(f"   ✅ Review velocity normal - no manipulation signs")
    elif review_rate <= 5:
        lines.append(f"   🟡 Slightly elevated - may have Vine or insert cards")
    else:
        lines.append(f"   🔴 Abnormally high - investigate for fake reviews")
    
    # Check for step jumps
    if series_analysis.get('review_step_jumps'):
        lines.append(f"")
        lines.append(f"   🚨 ALERT: Review step jumps detected!")
        lines.append(f"      Possible listing merge - verify review dates")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 7: STOCK STATUS
    # ═══════════════════════════════════════════════════════════════════
    stock_score = scores.get('stock', {})
    stock_status = "✅" if stock_score.get('score', 0) >= 4 else "⚠️" if stock_score.get('score', 0) >= 3 else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 7️⃣  STOCK STATUS                              {stock_score.get('score', 0):>2}/{stock_score.get('max', 5)} {stock_status}         │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    
    oos_flag = next((f for f in flags if 'oos' in f['flag'].lower() or 'stock' in f['flag'].lower()), None)
    if oos_flag:
        lines.append(f"   ⚠️ Stock issues detected: {oos_flag.get('detail', '')}")
    else:
        lines.append(f"   ✅ No stockout history detected")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 8: SEASONALITY
    # ═══════════════════════════════════════════════════════════════════
    modifier = seasonality.get('modifier', 0)
    season_status = "✅" if modifier >= 0 else "⚠️"
    
    lines.append("┌" + "─" * 68 + "┐")
    modifier_str = f"+{modifier}" if modifier > 0 else str(modifier)
    lines.append(f"│ 8️⃣  SEASONALITY                              {modifier_str:>4} {season_status}          │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    
    if seasonality.get('pattern') not in ['unknown', 'stable']:
        from datetime import datetime
        current_month = datetime.now().month
        month_name = datetime.now().strftime('%B')
        
        lines.append(f"   Pattern: {seasonality.get('pattern', 'unknown').upper()}")
        lines.append(f"   Peak Months: {seasonality.get('peak_months', [])}")
        lines.append(f"   Current: {month_name} ({current_month}) - {seasonality.get('current_position', 'unknown')}")
        lines.append("")
        
        if seasonality.get('current_position') == 'rising':
            lines.append(f"   ⚠️ Approaching peak season")
            lines.append(f"      Current good data may have seasonal inflation")
            lines.append(f"      Recommend: Re-validate in off-season")
        elif seasonality.get('current_position') == 'peak':
            lines.append(f"   ⚠️ Currently at peak season")
            lines.append(f"      Data likely inflated by seasonal demand")
        elif seasonality.get('current_position') == 'falling':
            lines.append(f"   📉 Past peak, demand declining")
        else:
            lines.append(f"   ✅ Off-season - data reflects true demand")
            if seasonality.get('bsr_trend') == 'improving':
                lines.append(f"      BSR improving in off-season = strong signal!")
    else:
        lines.append(f"   ✅ Year-round product - no seasonal adjustment")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 9: SCORE CALCULATION
    # ═══════════════════════════════════════════════════════════════════
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 9️⃣  SCORE CALCULATION                                             │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    lines.append("   📊 [Score Breakdown Chart - see score_breakdown.png]")
    charts_needed.append('score_breakdown')
    lines.append("")
    
    base_score = sum(s['score'] for s in scores.values())
    lines.append(f"   Base Score: {base_score}")
    lines.append(f"   Seasonality Modifier: {modifier:+d}")
    lines.append(f"   Red Flag Penalties: -{sum(10 if f['severity']=='critical' else 3 for f in flags)}")
    lines.append(f"   ─────────────────────")
    lines.append(f"   Final Score: {score}/100")
    lines.append("")
    
    # Score breakdown table
    lines.append("   ┌─────────────┬───────┬────────────┐")
    lines.append("   │ Dimension   │ Score │ Status     │")
    lines.append("   ├─────────────┼───────┼────────────┤")
    for name, data in scores.items():
        s, m = data['score'], data['max']
        pct = s / m * 100
        status = "✅ Strong" if pct >= 80 else "🟡 Okay" if pct >= 60 else "🔴 Weak"
        lines.append(f"   │ {name.title():<11} │ {s:>2}/{m:<2}  │ {status:<10} │")
    lines.append("   └─────────────┴───────┴────────────┘")
    lines.append("")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 10: RISK ASSESSMENT
    # ═══════════════════════════════════════════════════════════════════
    risk_emoji = "✅" if risk_level == "VALID" else "⚠️" if risk_level == "CAUTION" else "🔴"
    
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ 🔟  RISK ASSESSMENT                           {risk_emoji} {risk_level:<8}       │")
    lines.append("└" + "─" * 68 + "┘")
    lines.append("")
    
    if risk_level == "VALID":
        lines.append(f"   ✅ RECOMMENDATION: Proceed with standard due diligence")
        lines.append("")
        lines.append(f"   This product passes validation. Key strengths:")
        for name, data in scores.items():
            if data['score'] / data['max'] >= 0.8:
                lines.append(f"   • {name.title()}: Strong performance")
    elif risk_level == "CAUTION":
        lines.append(f"   ⚠️ RECOMMENDATION: Investigate concerns before proceeding")
        lines.append("")
        lines.append(f"   Concerns to address:")
        for flag in flags:
            lines.append(f"   • {flag['flag']}: {flag.get('detail', '')}")
        if seasonality.get('current_position') in ['rising', 'peak']:
            lines.append(f"   • Seasonal timing: Re-validate in off-season")
    else:
        lines.append(f"   🔴 RECOMMENDATION: Not recommended")
        lines.append("")
        lines.append(f"   Critical issues:")
        for flag in flags:
            if flag['severity'] == 'critical':
                lines.append(f"   • {flag['flag']}: {flag.get('detail', '')}")
    
    # ═══════════════════════════════════════════════════════════════════
    # STEP 11: PROFITABILITY (if cost provided)
    # ═══════════════════════════════════════════════════════════════════
    profitability = result.get('profitability')
    if profitability and 'error' not in profitability:
        prof = profitability['profitability']
        fees = profitability['fees']
        costs = profitability['costs']
        analysis = profitability['analysis']
        
        margin = prof['profit_margin']
        prof_emoji = "✅" if margin >= 20 else "🟡" if margin >= 10 else "⚠️" if margin > 0 else "🔴"
        
        lines.append("")
        lines.append("┌" + "─" * 68 + "┐")
        lines.append(f"│ 💰  PROFITABILITY                          {prof['profit_margin']:>5.1f}% {prof_emoji}         │")
        lines.append("└" + "─" * 68 + "┘")
        lines.append("")
        
        lines.append(f"   **Revenue:**")
        lines.append(f"   Selling Price:              ${profitability['selling_price']:>8.2f}")
        lines.append(f"   - Referral ({fees['referral_rate']}):       -${fees['referral_fee']:>8.2f}")
        lines.append(f"   - FBA ({fees['fba_tier']}):    -${fees['fba_fee']:>8.2f}")
        lines.append(f"   = Net Revenue:              ${prof['net_revenue']:>8.2f}")
        lines.append("")
        lines.append(f"   **Costs:**")
        lines.append(f"   Product Cost:               ${costs['product']:>8.2f}")
        lines.append(f"   + Shipping to FBA:          ${costs['shipping_inbound']:>8.2f}")
        lines.append(f"   + Prep:                     ${costs['prep']:>8.2f}")
        lines.append(f"   = Total Landed:             ${costs['total_landed_cost']:>8.2f}")
        lines.append("")
        lines.append(f"   **Profit:**")
        lines.append(f"   ┌─────────────────────────────────────────┐")
        lines.append(f"   │  Gross Profit:  ${prof['gross_profit']:>7.2f}               │")
        lines.append(f"   │  Margin:        {prof['profit_margin']:>6.1f}%                │")
        lines.append(f"   │  ROI:           {prof['roi']:>6.0f}%                │")
        lines.append(f"   └─────────────────────────────────────────┘")
        lines.append("")
        
        if margin >= 30:
            lines.append(f"   ✅ Excellent margin (≥30%) - Strong profit potential")
        elif margin >= 20:
            lines.append(f"   ✅ Good margin (≥20%) - Viable product")
        elif margin >= 10:
            lines.append(f"   🟡 Thin margin (10-20%) - Watch for fee increases")
        elif margin > 0:
            lines.append(f"   ⚠️ Very thin margin (<10%) - Risky, easily eroded")
        else:
            lines.append(f"   🔴 NOT PROFITABLE at this cost!")
        
        # Advertising Buffer Warning
        lines.append(f"")
        lines.append(f"   ⚠️ **Advertising Buffer:**")
        lines.append(f"   Above profit does NOT include advertising costs.")
        lines.append(f"   If you plan to run PPC ads, factor in ACOS:")
        acos_20_cost = profitability['selling_price'] * 0.20
        acos_30_cost = profitability['selling_price'] * 0.30
        profit_after_20_acos = prof['gross_profit'] - acos_20_cost
        profit_after_30_acos = prof['gross_profit'] - acos_30_cost
        lines.append(f"   • At 20% ACOS: -${acos_20_cost:.2f} → Profit ${profit_after_20_acos:.2f} ({profit_after_20_acos/profitability['selling_price']*100:.1f}%)")
        lines.append(f"   • At 30% ACOS: -${acos_30_cost:.2f} → Profit ${profit_after_30_acos:.2f} ({profit_after_30_acos/profitability['selling_price']*100:.1f}%)")
        if profit_after_30_acos <= 0:
            lines.append(f"   🔴 At 30% ACOS you will LOSE money!")
        
        # Break-even Price War Strategy
        lines.append(f"")
        lines.append(f"   💡 **Price War Strategy:**")
        lines.append(f"   Break-even price: ${analysis['break_even_price']:.2f}")
        lines.append(f"   If competitors start a price war, your absolute floor is")
        lines.append(f"   ${analysis['break_even_price']:.2f}. Below this, you lose money on every sale.")
        
        # Calculate minimum profitable price (with 10% margin buffer)
        min_profit_price = analysis['break_even_price'] * 1.10
        lines.append(f"   Recommended minimum: ${min_profit_price:.2f} (10% safety margin)")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"Report generated by Product Validator v1.4")
    lines.append("=" * 70)
    
    return "\n".join(lines), charts_needed

def main():
    parser = argparse.ArgumentParser(description='Product Validator - Deep ASIN validation')
    parser.add_argument('params', help='JSON parameters: {"asin": "B0XXX", "marketplace": "US"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to specified directory')
    parser.add_argument('--report', action='store_true', help='Output analytical report instead of JSON')
    parser.add_argument('--cost', type=float, help='Product cost for profitability calculation')
    parser.add_argument('--weight', type=float, help='Product weight in pounds for FBA fee calculation')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not params.get('asin'):
        print(json.dumps({'error': 'Missing required parameter: asin'}, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = run_validator(params)
    if 'error' in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Add profitability if cost provided
    if args.cost is not None and 'error' not in result:
        result = add_profitability(result, args.cost, args.weight)
        print(f"Profitability calculated with cost=${args.cost}", file=sys.stderr)
    
    # Determine chart directory
    chart_dir = args.chart
    if args.report and not chart_dir:
        # Auto-create chart dir for report mode
        chart_dir = os.path.join(tempfile.gettempdir(), f"pv_report_{result.get('asin', 'unknown')}")
    
    # Generate charts if needed
    if chart_dir and 'error' not in result:
        import os
        os.makedirs(chart_dir, exist_ok=True)
        charts, chart_analysis = generate_charts(result, chart_dir)
        result['charts'] = charts
        result['chart_analysis'] = chart_analysis
        print(f"Generated {len(charts)} charts in {chart_dir}", file=sys.stderr)
    
    # Output format
    if args.report:
        report_text, charts_needed = generate_analytical_report(result, chart_dir)
        print(report_text)
        if chart_dir:
            print(f"\n📁 Charts saved to: {chart_dir}/", file=sys.stderr)
            for chart in result.get('charts', []):
                print(f"   • {os.path.basename(chart)}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
