#!/usr/bin/env python3
# Enhanced data sources v2.0.0
"""
New Product Tracker - Find rising products before they become saturated.

Usage:
  python3 new_product_tracker.py '{"keyword": "pet water fountain"}'
  python3 new_product_tracker.py '{"keyword": "wireless earbuds", "max_age_days": 180}' --chart ./output/

"""

import json
import os
import sys
import argparse
from urllib.request import urlopen, Request
from datetime import datetime

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

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

# Category BSR thresholds
BSR_THRESHOLDS = {
    'pet_supplies': {'top': 1000, 'great': 10000, 'good': 50000},
    'home_kitchen': {'top': 2000, 'great': 20000, 'good': 100000},
    'electronics': {'top': 1000, 'great': 15000, 'good': 75000},
    'beauty': {'top': 3000, 'great': 30000, 'good': 150000},
    'default': {'top': 2000, 'great': 20000, 'good': 100000}
}

def call_api(endpoint, params):
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(params).encode('utf-8'),
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

def js_api_call(endpoint: str, params: dict):
    """Call Jungle Scout API via NexScope proxy."""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout{endpoint}"
    try:
        req = Request(url, data=json.dumps(params).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if isinstance(raw, dict) and raw.get('code') == 0:
            data = raw.get('data', {})
            if isinstance(data, dict) and 'code' in data:
                data = data.get('data', data)
            return data
        return None
    except Exception as e:
        print(f"JS API error [{endpoint}]: {e}", file=sys.stderr)
        return None

def _fetch_keepa_bsr_history(asin: str, domain: int = 1) -> dict:
    """Fetch BSR history from Keepa to verify product age and growth trend."""
    result = call_api('/keepa/productSeries', {
        'asin': asin,
        'domain': str(domain),
        'days': 180,
        'showBsrMain': 1,
        'showBsrSub': 1
    })
    if not result:
        return {}
    bsr_series = result.get('bsrMain', [])
    if not bsr_series:
        bsr_series = result.get('bsrSub', [{}])[0].get('points', []) if result.get('bsrSub') else []
    first_seen_days = None
    bsr_points = []
    if isinstance(bsr_series, list):
        for pt in bsr_series:
            if isinstance(pt, dict) and pt.get('value') is not None and pt.get('time') is not None:
                bsr_points.append({'time': pt.get('time'), 'value': pt.get('value')})
        if bsr_points:
            # Estimate first seen: earliest data point
            first_seen_days = len(bsr_points)  # proxy for age in tracking periods
    return {
        'bsr_history_points': len(bsr_points),
        'has_bsr_history': len(bsr_points) > 0,
        'first_seen_days_approx': first_seen_days,
        'bsr_series': bsr_points[-10:] if bsr_points else []  # last 10 points
    }

def calculate_product_age(available_date):
    """Calculate product age in days"""
    if not available_date:
        return 365
    try:
        launch = datetime.strptime(available_date.split()[0], "%Y-%m-%d")
        return (datetime.now() - launch).days
    except:
        return 365

def calculate_new_product_score(product, category='default'):
    """
    Calculate New Product Score (0-100)

    Freshness(25) + Sales Momentum(30) + Market Position(20) + Potential(15) + Quality(10)

    Uses only fields actually returned by Amazon Search API:
    availableDate, monthlySalesUnits, monthlySalesRevenue, ratings, rating, fulfillment
    """
    # Freshness (0-25): based on availableDate — already reliable
    age_days = product.get('age_days', 365)
    if age_days <= 30: fresh = 25
    elif age_days <= 60: fresh = 22
    elif age_days <= 90: fresh = 18
    elif age_days <= 120: fresh = 14
    elif age_days <= 180: fresh = 10
    else: fresh = 5

    # Sales Momentum (0-30): monthlySalesUnits + monthlySalesRevenue
    # replaces BSR growth (salesRank30 not returned by API)
    monthly_units = product.get('monthlySalesUnits') or 0
    monthly_revenue = product.get('monthlySalesRevenue') or 0

    if monthly_units >= 500 or monthly_revenue >= 10000: momentum = 30
    elif monthly_units >= 200 or monthly_revenue >= 5000: momentum = 25
    elif monthly_units >= 100 or monthly_revenue >= 2000: momentum = 20
    elif monthly_units >= 50 or monthly_revenue >= 1000: momentum = 15
    elif monthly_units > 0 or monthly_revenue > 0: momentum = 10
    else: momentum = 5  # no sales data available

    # Market Position (0-20): monthlySalesUnits rank signal
    # replaces BSR velocity (salesRank not reliably returned)
    if monthly_units >= 1000: position = 20
    elif monthly_units >= 500: position = 15
    elif monthly_units >= 100: position = 10
    elif monthly_units > 0: position = 7
    else: position = 3

    # Potential (0-15): low reviews + good sales = high opportunity
    reviews = product.get('reviewCount', 0) or product.get('ratings', 0) or 0
    if reviews < 50 and monthly_units > 100: pot = 15
    elif reviews < 100 and monthly_units > 200: pot = 12
    elif reviews < 200: pot = 9
    else: pot = 5

    # Quality (0-10): rating + fulfillment
    # replaces sellerNum stability (sellerNum not returned by API)
    rating = product.get('rating') or 0
    fulfillment = (product.get('fulfillment') or '').upper()
    if rating >= 4.5: quality_base = 7
    elif rating >= 4.0: quality_base = 5
    elif rating >= 3.5: quality_base = 3
    elif rating > 0: quality_base = 1
    else: quality_base = 0
    fba_bonus = 3 if 'FBA' in fulfillment or 'AMAZON' in fulfillment else 0
    quality = min(quality_base + fba_bonus, 10)

    total = fresh + momentum + position + pot + quality

    return {
        'total_score': total,
        'freshness': fresh,
        'growth': momentum,    # key kept for chart compatibility
        'velocity': position,  # key kept for chart compatibility
        'potential': pot,
        'stability': quality,  # key kept for chart compatibility
        'metrics': {
            'age_days': age_days,
            'monthly_units': monthly_units,
            'monthly_revenue': monthly_revenue,
            'growth_30d': monthly_units,  # repurposed for pattern detection
            'bsr_current': product.get('salesRank') or 0,
            'reviews': reviews,
            'rating': rating,
            'fulfillment': fulfillment,
        }
    }

def detect_opportunity_pattern(product, score):
    """Detect opportunity patterns using monthlySalesUnits-based metrics"""
    metrics = score['metrics']
    age_days = metrics['age_days']
    monthly_units = metrics.get('monthly_units', 0)
    reviews = metrics['reviews']
    bsr = metrics.get('bsr_current', 0)

    # Fast Starter: <90d, strong sales already established
    if age_days < 90 and monthly_units >= 200:
        return {'pattern': 'Fast Starter', 'emoji': '🚀',
                'detail': f'{age_days}d old, {monthly_units} units/month'}

    # Fast Starter (BSR fallback): <90d, top BSR if available
    if age_days < 90 and bsr > 0 and bsr < 10000:
        return {'pattern': 'Fast Starter', 'emoji': '🚀',
                'detail': f'{age_days}d old, BSR {bsr:,}'}

    # Rising Star: 90-180d with solid sales momentum
    if 90 <= age_days <= 180 and monthly_units >= 100:
        return {'pattern': 'Rising Star', 'emoji': '📈',
                'detail': f'{monthly_units} units/month, {age_days}d old'}

    # Hidden Gem: selling well but very few reviews
    if reviews < 100 and monthly_units >= 50:
        return {'pattern': 'Hidden Gem', 'emoji': '💎',
                'detail': f'{monthly_units} units/mo, only {reviews} reviews'}

    # Viral Launch: very high sales volume
    if monthly_units >= 500:
        return {'pattern': 'Viral Launch', 'emoji': '🔥',
                'detail': f'{monthly_units} units/month'}

    return {'pattern': 'Standard', 'emoji': '📦', 'detail': 'Normal growth pattern'}

# === Chart Analysis ===
def generate_chart_analysis(results):
    """Generate analytical text for each chart"""
    analysis = {}
    products = results.get('products', [])
    
    if not products:
        return analysis
    
    top_products = sorted(products, key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)[:5]
    patterns = (results.get('summary') or {}).get('patterns', {})
    
    # Chart 1: Scatter Analysis
    lines = ["**📊 New Product Opportunities:**"]
    young_products = [p for p in products if p.get('age_days', 999) < 90]
    high_score = [p for p in products if (p.get('score') or {}).get('total_score', 0) >= 60]
    
    lines.append(f"- Products under 90 days: {len(young_products)}")
    lines.append(f"- High opportunity (60+): {len(high_score)}")
    
    if top_products:
        best = top_products[0]
        lines.append(f"- ✅ Top pick: **{best.get('asin')}** (Score: {(best.get('score') or {}).get('total_score', 0)})")
        _bsr = best.get('salesRank')
        lines.append(f"  Age: {best.get('age_days')}d | BSR: {_bsr:,}" if isinstance(_bsr, int) else f"  Age: {best.get('age_days')}d | BSR: N/A")
    analysis['scatter'] = "\n".join(lines)
    
    # Chart 2: Score Breakdown Analysis
    lines = ["**📈 Top Products Breakdown:**"]
    if top_products:
        for i, p in enumerate(top_products[:3], 1):
            score = p.get('score', {})
            strongest = max([
                ('Freshness', score.get('freshness', 0)),
                ('Growth', score.get('growth', 0)),
                ('Velocity', score.get('velocity', 0)),
            ], key=lambda x: x[1])
            lines.append(f"- #{i} {p.get('asin')}: Best in **{strongest[0]}** ({strongest[1]} pts)")
    analysis['breakdown'] = "\n".join(lines)
    
    # Chart 3: Pattern Distribution Analysis
    lines = ["**🎯 Opportunity Patterns:**"]
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        if pattern == 'Fast Starter':
            lines.append(f"- 🚀 Fast Starter: {count} - Young products already top BSR")
        elif pattern == 'Rising Star':
            lines.append(f"- 📈 Rising Star: {count} - Consistent upward momentum")
        elif pattern == 'Hidden Gem':
            lines.append(f"- 💎 Hidden Gem: {count} - Good BSR, few reviews (opportunity!)")
        elif pattern == 'Viral Launch':
            lines.append(f"- 🔥 Viral Launch: {count} - Explosive recent growth")
        else:
            lines.append(f"- 📦 Standard: {count}")
    analysis['patterns'] = "\n".join(lines)
    
    return analysis

# === Chart Generation ===
def generate_charts(results, output_dir):
    """Generate new product analysis charts"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not installed, skipping charts", file=sys.stderr)
        return [], {}
    
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    chart_analysis = generate_chart_analysis(results)
    
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    products = results.get('products', [])
    if not products:
        return charts
    
    # Chart 1: Score vs Age Scatter
    if len(products) < 2:
        print("  ⚠️ bsr_trajectory.png skipped: need ≥2 products", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(10, 6))
    
    ages = [((p.get('score') or {}).get('metrics') or {}).get('age_days', 180) for p in products]
    scores = [(p.get('score') or {}).get('total_score', 0) for p in products]
    bsr = [p.get('salesRank') or 50000 for p in products]
    
    # Size based on BSR (smaller BSR = bigger dot)
    sizes = [max(50, 500 - b/200) for b in bsr]
    
    scatter = ax.scatter(ages, scores, c=scores, cmap='RdYlGn', s=sizes, alpha=0.7, edgecolors='white')
    plt.colorbar(scatter, label='Opportunity Score')
    
    # Highlight top 3
    top_products = sorted(products, key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)[:3]
    for p in top_products:
        age = ((p.get('score') or {}).get('metrics') or {}).get('age_days', 180)
        score = (p.get('score') or {}).get('total_score', 0)
        ax.annotate(p.get('asin', '')[:10], xy=(age, score), xytext=(age+5, score+3),
                   fontsize=8, color=get_color('good'),
                   arrowprops=dict(arrowstyle='->', color=get_color('good'), alpha=0.5))
    
    # Opportunity zones
    ax.axhspan(70, 100, alpha=0.1, color=get_color('good'), label='High Opportunity')
    ax.axvline(x=90, color=get_color('warning'), linestyle=':', alpha=0.5, label='90-day mark')
    ax.axvline(x=180, color=get_color('hot'), linestyle=':', alpha=0.5, label='180-day mark')
    
    ax.set_xlabel('Product Age (Days)', fontsize=10)
    ax.set_ylabel('Opportunity Score', fontsize=10)
    ax.set_title(f'New Product Opportunities: {results.get("keyword", "")}\nBubble size = BSR rank (bigger = better)',
                 fontsize=12, fontweight='bold', pad=15)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(ages) + 20)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'bsr_trajectory.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)
    
    # Chart 2: Top Products Score Breakdown
    top_5 = top_products[:5]
    if len(top_5) < 1:
        print("  ⚠️ age_performance.png skipped: no top products available", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(10, 6))

    labels = [p.get('asin', '')[:10] for p in top_5]
    
    freshness = [(p.get('score') or {}).get('freshness', 0) for p in top_5]
    growth = [(p.get('score') or {}).get('growth', 0) for p in top_5]
    velocity = [(p.get('score') or {}).get('velocity', 0) for p in top_5]
    potential = [(p.get('score') or {}).get('potential', 0) for p in top_5]
    stability = [(p.get('score') or {}).get('stability', 0) for p in top_5]
    
    x = np.arange(len(labels))
    width = 0.15
    
    ax.bar(x - 2*width, freshness, width, label='Freshness (25)', color=get_color('primary'))
    ax.bar(x - width, growth, width, label='Sales Momentum (30)', color=get_color('good'))
    ax.bar(x, velocity, width, label='Market Position (20)', color=get_color('secondary'))
    ax.bar(x + width, potential, width, label='Potential (15)', color=get_color('secondary'))
    ax.bar(x + 2*width, stability, width, label='Quality (10)', color='#6A4C93')
    
    ax.set_ylabel('Score', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_title('Top 5 Products - Score Breakdown', fontsize=12, fontweight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_ylim(0, 35)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'age_performance.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)
    
    # Chart 3: Pattern Distribution Pie
    patterns = {}
    for p in products:
        pattern = (p.get('pattern') or {}).get('pattern', 'Standard')
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    if patterns:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = {'Fast Starter': get_color('good'), 'Rising Star': get_color('primary'), 'Hidden Gem': get_color('secondary'), 
                  'Viral Launch': get_color('hot'), 'Standard': get_color('muted')}
        
        wedges, texts, autotexts = ax.pie(
            patterns.values(), 
            labels=patterns.keys(),
            colors=[colors.get(p, get_color('muted')) for p in patterns.keys()],
            autopct='%1.0f%%',
            startangle=90,
            explode=[0.05 if p != 'Standard' else 0 for p in patterns.keys()]
        )
        
        ax.set_title('Opportunity Pattern Distribution', fontsize=12, fontweight='bold', pad=15)

        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'patterns.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)

    # Chart 4: Review Authenticity Validation
    top_products_rv = sorted(products, key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)[:8]
    if len(top_products_rv) >= 2:
        fig, ax = plt.subplots(figsize=(10, 6))

        labels_rv = [p.get('asin', '')[:10] for p in top_products_rv]
        reviews_rv = [(p.get('score') or {}).get('metrics', {}).get('reviews', 0) for p in top_products_rv]
        ages_rv = [(p.get('score') or {}).get('metrics', {}).get('age_days', 180) for p in top_products_rv]

        # Review velocity = reviews per day (higher is suspicious for new products)
        velocities = [r / max(a, 1) for r, a in zip(reviews_rv, ages_rv)]

        # Color-code: velocity > 2/day = suspicious (red), 0.5-2 = caution (yellow), <0.5 = authentic (green)
        bar_colors = []
        for v in velocities:
            if v > 2.0:
                bar_colors.append(get_color('hot'))
            elif v > 0.5:
                bar_colors.append(get_color('warning'))
            else:
                bar_colors.append(get_color('good'))

        y_pos = np.arange(len(labels_rv))
        bars = ax.barh(y_pos, velocities, color=bar_colors, height=0.6)

        for bar, v, r in zip(bars, velocities, reviews_rv):
            ax.text(v + 0.02, bar.get_y() + bar.get_height()/2,
                    f'{v:.2f}/day ({r} total)', va='center', fontsize=8)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels_rv)
        ax.set_xlabel('Review Velocity (reviews/day)', fontsize=10)
        ax.axvline(x=0.5, color=get_color('warning'), linestyle='--', alpha=0.7, label='Caution (>0.5/day)')
        ax.axvline(x=2.0, color=get_color('hot'), linestyle='--', alpha=0.7, label='Suspicious (>2/day)')
        ax.legend(loc='lower right', fontsize=8)
        ax.set_title('Review Authenticity Validation\n(Top Products by Opportunity Score)',
                     fontsize=12, fontweight='bold', pad=15)

        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'review_validation.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)

    return charts, chart_analysis

def run_tracker(params):
    keyword = params.get('keyword', '')
    max_age = params.get('max_age_days', 180)
    marketplace = params.get('marketplace', 'amazon.com')
    
    if not keyword:
        return {"error": "keyword required"}
    
    # Search for products
    try:
        search_data = call_api("/amazon/search", {
            "keyword": keyword,
            "amazonDomain": marketplace
        })
        products = (search_data or {}).get('products', [])
    except Exception as e:
        return {"error": str(e)}
    
    results = {
        'keyword': keyword,
        'marketplace': marketplace,
        'products': []
    }
    
    for p in products:
        age_days = calculate_product_age(p.get('availableDate'))
        
        if age_days > max_age:
            continue
        
        p['age_days'] = age_days
        
        # Detect category
        category = 'default'
        cat_tree = (p.get('categoryTree', '') or '').lower()
        if 'pet' in cat_tree: category = 'pet_supplies'
        elif 'kitchen' in cat_tree or 'home' in cat_tree: category = 'home_kitchen'
        elif 'electronics' in cat_tree: category = 'electronics'
        elif 'beauty' in cat_tree: category = 'beauty'
        
        score = calculate_new_product_score(p, category)
        pattern = detect_opportunity_pattern(p, score)
        
        results['products'].append({
            'asin': p.get('asin'),
            'title': p.get('title', '')[:80],
            'price': p.get('price'),
            'salesRank': p.get('salesRank'),
            'rating': p.get('rating'),
            'reviews': p.get('ratings') or p.get('reviewCount', 0),
            'monthlySales': p.get('monthlySalesUnits'),
            'age_days': age_days,
            'category': category,
            'score': score,
            'pattern': pattern
        })
    
    # Sort by score
    results['products'].sort(key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)

    # Enrich top products with Keepa BSR history
    domain_id = 1  # default to US; adapt if marketplace var exists
    for i, product in enumerate(results['products'][:10]):
        asin = product.get('asin', '')
        if asin:
            try:
                keepa_data = _fetch_keepa_bsr_history(asin, domain_id)
            except Exception as _e:
                print(f"  Keepa BSR fetch error for {asin}: {_e}", file=sys.stderr)
                keepa_data = {}
            product['keepa_bsr_history'] = keepa_data
            # Refine age estimate: if has extensive BSR history, not truly new
            if keepa_data.get('bsr_history_points', 0) > 30:
                product['likely_truly_new'] = False
            else:
                product['likely_truly_new'] = True

    # JS: verify search demand for this niche
    js_kw_data = js_api_call('/keywords/by-keyword', {
        'searchTerms': keyword,
        'marketplace': 'us'
    })
    niche_search_volume = 0
    if js_kw_data and isinstance(js_kw_data, dict):
        kw_list = js_kw_data.get('data', [])
        if kw_list:
            attrs = kw_list[0].get('attributes', {})
            niche_search_volume = attrs.get('monthlySearchVolumeExact', 0)

    results['niche_search_volume'] = niche_search_volume

    # Summary
    high_opp = [p for p in results['products'] if (p.get('score') or {}).get('total_score', 0) >= 60]
    results['summary'] = {
        'total_products': len(results['products']),
        'high_opportunity': len(high_opp),
        'top_opportunity': results['products'][0] if results['products'] else None,
        'patterns': {(p.get('pattern') or {}).get('pattern', 'Standard'): 0 for p in results['products']}
    }
    
    for p in results['products']:
        pattern = (p.get('pattern') or {}).get('pattern', 'Standard')
        results['summary']['patterns'][pattern] = results['summary']['patterns'].get(pattern, 0) + 1
    
    # Generate insights
    results['insights'] = generate_insights(results)
    
    return results

def generate_insights(results: dict) -> dict:
    """Generate actionable insights from new product analysis"""
    products = results.get('products', [])
    patterns = (results.get('summary') or {}).get('patterns', {})
    
    if not products:
        return {'summary': 'No new products found', 'recommendations': []}
    
    high_opp = [p for p in products if (p.get('score') or {}).get('total_score', 0) >= 60]
    fast_starters = patterns.get('Fast Starter', 0)
    rising_stars = patterns.get('Rising Star', 0)
    hidden_gems = patterns.get('Hidden Gem', 0)
    
    # Summary
    if fast_starters >= 3:
        summary = f"🚀 Hot market! {fast_starters} fast starters found — new products gaining traction quickly."
    elif rising_stars >= 3:
        summary = f"📈 Growing market! {rising_stars} rising stars detected — consistent growth patterns."
    elif hidden_gems >= 2:
        summary = f"💎 Hidden opportunities! {hidden_gems} hidden gems with low reviews but good sales."
    elif high_opp:
        summary = f"👍 {len(high_opp)} high-opportunity new products found."
    else:
        summary = f"📊 {len(products)} new products tracked. Market appears stable."
    
    # Recommendations
    recommendations = []
    
    if fast_starters > 0:
        recommendations.append(f"🚀 {fast_starters} Fast Starters — study what's working, move quickly")
    
    if rising_stars > 0:
        recommendations.append(f"📈 {rising_stars} Rising Stars — consistent performers, lower risk")
    
    if hidden_gems > 0:
        recommendations.append(f"💎 {hidden_gems} Hidden Gems — under-reviewed but selling well")
    
    # Age analysis
    avg_age = sum(p.get('age_days', 0) for p in products) / len(products) if products else 0
    if avg_age < 60:
        recommendations.append(f"⏱️ Very new market (avg {avg_age:.0f} days) — early mover advantage possible")
    elif avg_age < 120:
        recommendations.append(f"⏱️ Relatively new market (avg {avg_age:.0f} days)")
    
    # Top performer insight
    if products:
        top = products[0]
        score = (top.get('score') or {}).get('total_score', 0)
        recommendations.append(f"🎯 Top opportunity: {top.get('title', '')[:30]}... (Score: {score})")
    
    # Review analysis
    low_review_sellers = [p for p in products if (p.get('reviews', 0) or 0) < 50 and (p.get('monthlySales', 0) or 0) > 100]
    if low_review_sellers:
        recommendations.append(f"🌟 {len(low_review_sellers)} products selling well with <50 reviews — achievable benchmark")
    
    return {
        'summary': summary,
        'patterns_found': patterns,
        'high_opportunity_count': len(high_opp),
        'recommendations': recommendations,
        'market_stage': 'EMERGING' if avg_age < 60 else 'GROWING' if avg_age < 120 else 'ESTABLISHED'
    }

def main():
    parser = argparse.ArgumentParser(description='New Product Tracker')
    parser.add_argument('params', nargs='?', help='JSON parameters: {"keyword": "pet water fountain"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to specified directory')
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
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = run_tracker(params)
    
    if args.chart and 'error' not in result:
        charts, chart_analysis = generate_charts(result, args.chart)
        result['charts'] = charts
        result['chart_analysis'] = chart_analysis
        print(f"Generated {len(charts)} charts in {args.chart}", file=sys.stderr)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == "__main__":
    main()
