#!/usr/bin/env python3
"""
Competitor Analyzer v2.0.0 - Analyze competitive landscape for Amazon products.

Enhanced with:
- Keepa deep data (BSR trends, seller count, seasonality)
- Competition intensity tracking
- Sales momentum analysis

Usage:
  python3 competitor_analyzer.py '{"asin": "B0XXXXXXXXX"}'
  python3 competitor_analyzer.py '{"keyword": "dog water fountain"}'
  python3 competitor_analyzer.py '{"asins": ["B0XXX", "B0YYY"]}' --report

"""

import json
import os
import sys
import re
import argparse
from urllib.request import urlopen, Request
from statistics import mean, median
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

# Chart imports
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

# Domain mapping
DOMAIN_MAP = {
    'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5,
    'CA': 6, 'IT': 8, 'ES': 9, 'MX': 11, 'AU': 13
}

AMAZON_DOMAINS = {
    'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de',
    'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca'
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

def search_competitors(keyword, marketplace='US', limit=20):
    """Search Amazon competitors by keyword using API data."""
    domain = AMAZON_DOMAINS.get(marketplace, 'amazon.com')
    
    data = call_api("/amazon/search", {
        "keyword": keyword,
        "amazonDomain": domain
    })
    
    products = (data or {}).get('products', [])[:limit]
    
    sponsored_map = {}
    
    # Extract key info. Sponsored status is taken from API data when available.
    results = []
    for p in products:
        asin = p.get('asin')
        is_sponsored = sponsored_map.get(asin, p.get('sponsored', False))
        
        results.append({
            'asin': asin,
            'title': p.get('title', '')[:80],
            'price': p.get('price', 0),
            'rating': p.get('rating', 0),
            'reviews': p.get('ratings', 0),
            'position': p.get('position', 0),
            'sponsored': is_sponsored,
            'monthly_sales': p.get('monthlySalesUnits', 0),
            'image': p.get('imageUrl', '')
        })
    
    return results


def get_product_details(asin, marketplace='US'):
    """Get detailed product data from Keepa"""
    domain = DOMAIN_MAP.get(marketplace, 1)
    
    data = call_api("/keepa/productRequest", {
        "asin": asin,
        "domain": domain
    })
    
    products = (data or {}).get('products', [])
    if not products:
        return None

    p = products[0]
    
    # Extract subcategory BSR
    subcategories = p.get('subcategories', [])
    sub_bsr = None
    sub_cat = None
    if subcategories:
        sub_bsr = subcategories[0].get('rank')
        sub_cat = subcategories[0].get('label', '')
    
    return {
        'asin': asin,
        'title': p.get('title', '')[:80],
        'price': p.get('price', 0),
        'rating': p.get('rating', 0),
        'reviews': p.get('reviewCount', p.get('ratings', 0)),
        'bsr': p.get('salesRank', 0),
        'bsr_sub': sub_bsr,
        'bsr_category': sub_cat,
        'bsr_30': p.get('salesRank30', 0),
        'bsr_90': p.get('salesRank90', 0),
        'seller_count': p.get('sellerNum', 0),
        'monthly_sales': p.get('monthlySalesUnits', 0),
        'monthly_revenue': p.get('monthlySalesRevenue', 0),
        'brand': p.get('brand', ''),
        'fulfillment': p.get('fulfillment', ''),
        'images': len(p.get('productImageUrls', [])),
        'available_date': p.get('availableDate', '')
    }


def get_bsr_history(asin, marketplace='US', days=90):
    """Get BSR history from productSeries API"""
    domain = DOMAIN_MAP.get(marketplace, 1)
    
    try:
        data = call_api("/keepa/productSeries", {
            "asin": asin,
            "domain": domain,
            "days": days
        })
        if not data:
            return None
        
        if data.get('errcode') != 200:
            return None
        
        bsr_sub = data.get('bsrSub', [])
        if bsr_sub and len(bsr_sub) > 0:
            points = bsr_sub[0].get('points', [])
            return [p['value'] for p in points]
        
        # Also try monthlySold as fallback for sales trend
        return None
    except Exception as e:
        print(f"BSR history error [{asin}]: {e}", file=sys.stderr)
        return None





def calculate_bsr_trend(bsr_history):
    """Calculate BSR trend from history"""
    if not bsr_history or len(bsr_history) < 2:
        return 'unknown', 0
    
    first_q = bsr_history[:len(bsr_history)//4]
    last_q = bsr_history[-len(bsr_history)//4:]
    
    if not first_q or not last_q:
        return 'unknown', 0
    
    first_avg = mean(first_q)
    last_avg = mean(last_q)
    
    if first_avg == 0:
        return 'unknown', 0
    
    # Positive change = improving (BSR went down)
    change_pct = (first_avg - last_avg) / first_avg * 100
    
    if change_pct > 20:
        return 'improving', change_pct
    elif change_pct < -20:
        return 'declining', change_pct
    else:
        return 'stable', change_pct


def analyze_traffic_distribution(search_results):
    """Analyze organic vs sponsored distribution"""
    if not search_results:
        return None
    
    total = len(search_results)
    sponsored = sum(1 for p in search_results if p.get('sponsored'))
    organic = total - sponsored
    
    sponsored_pct = (sponsored / total * 100) if total > 0 else 0
    organic_pct = (organic / total * 100) if total > 0 else 0
    
    # Classify market type
    if sponsored_pct >= 70:
        market_type = 'EXTREMELY_AD_HEAVY'
        entry_assessment = 'Very high ad spend required. Extremely competitive.'
    elif sponsored_pct >= 50:
        market_type = 'AD_HEAVY'
        entry_assessment = 'Significant ad budget needed. Top positions dominated by ads.'
    elif sponsored_pct >= 30:
        market_type = 'BALANCED'
        entry_assessment = 'Mix of organic and paid. Moderate ad spend recommended.'
    else:
        market_type = 'ORGANIC_DRIVEN'
        entry_assessment = 'Organic ranking achievable. Focus on SEO and reviews.'
    
    # Top 5 analysis
    top5 = search_results[:5]
    top5_sponsored = sum(1 for p in top5 if p.get('sponsored'))
    
    return {
        'total_analyzed': total,
        'sponsored_count': sponsored,
        'organic_count': organic,
        'sponsored_pct': round(sponsored_pct, 1),
        'organic_pct': round(organic_pct, 1),
        'top5_sponsored': top5_sponsored,
        'market_type': market_type,
        'assessment': entry_assessment
    }


def analyze_price_distribution(competitors):
    """Analyze price distribution and find sweet spots"""
    prices = [float(c['price']) for c in competitors if float(c.get('price') or 0) > 0]
    
    if not prices:
        return None
    
    # Define price brackets
    brackets = [
        (0, 25, 'Budget'),
        (25, 50, 'Value'),
        (50, 100, 'Mid-range'),
        (100, 200, 'Premium'),
        (200, float('inf'), 'Luxury')
    ]
    
    bracket_counts = {}
    bracket_revenue = {}
    
    for c in competitors:
        price = c.get('price', 0)
        revenue = c.get('monthly_revenue', 0) or (price * c.get('monthly_sales', 0))
        
        for low, high, name in brackets:
            if low <= price < high:
                bracket_counts[name] = bracket_counts.get(name, 0) + 1
                bracket_revenue[name] = bracket_revenue.get(name, 0) + revenue
                break
    
    # Find sweet spot (most revenue)
    sweet_spot = max(bracket_revenue.keys(), key=lambda k: bracket_revenue.get(k, 0)) if bracket_revenue else 'Unknown'
    
    return {
        'min': min(prices),
        'max': max(prices),
        'avg': round(mean(prices), 2),
        'median': round(median(prices), 2),
        'brackets': bracket_counts,
        'bracket_revenue': bracket_revenue,
        'sweet_spot': sweet_spot
    }


def analyze_review_barrier(competitors):
    """Analyze review requirements to compete"""
    reviews = sorted([c['reviews'] for c in competitors if (c.get('reviews') or 0) > 0], reverse=True)
    
    if not reviews:
        return None
    
    top3_avg = mean(reviews[:3]) if len(reviews) >= 3 else mean(reviews)
    top10_avg = mean(reviews[:10]) if len(reviews) >= 10 else mean(reviews)
    
    # Classify barrier
    if top3_avg >= 5000:
        barrier = 'EXTREME'
        assessment = 'Extremely difficult to compete. Established brands dominate.'
    elif top3_avg >= 1000:
        barrier = 'HIGH'
        assessment = 'High review barrier. Expect 12+ months to establish.'
    elif top3_avg >= 500:
        barrier = 'MEDIUM'
        assessment = 'Moderate review barrier. 6-12 months to compete.'
    else:
        barrier = 'LOW'
        assessment = 'Low review barrier. New entrants can compete quickly.'
    
    return {
        'top3_avg': round(top3_avg),
        'top10_avg': round(top10_avg),
        'min': min(reviews),
        'max': max(reviews),
        'barrier_level': barrier,
        'assessment': assessment
    }


def generate_gap_analysis(competitors, price_analysis, traffic_analysis):
    """Generate gap analysis and opportunities"""
    gaps = []
    
    # Price gap analysis
    if price_analysis:
        brackets = price_analysis.get('brackets', {})
        sweet_spot = price_analysis.get('sweet_spot')
        
        # Find underserved brackets
        for bracket, count in brackets.items():
            if count <= 1:
                gaps.append({
                    'type': 'price_gap',
                    'detail': f'{bracket} segment underserved ({count} competitor)',
                    'opportunity': 'low_competition'
                })
    
    # Traffic gap
    if traffic_analysis:
        if traffic_analysis['market_type'] == 'ORGANIC_DRIVEN':
            gaps.append({
                'type': 'traffic_opportunity',
                'detail': 'Organic-driven market - SEO/review focus viable',
                'opportunity': 'organic_growth'
            })
        
        if traffic_analysis['top5_sponsored'] <= 2:
            gaps.append({
                'type': 'traffic_opportunity',
                'detail': 'Top 5 not dominated by ads - organic ranking achievable',
                'opportunity': 'top_position_achievable'
            })
    
    # Sales concentration gap
    high_sales = [c for c in competitors if c.get('monthly_sales', 0) > 300]
    if len(high_sales) <= 2 and competitors:
        gaps.append({
            'type': 'sales_gap',
            'detail': 'Few competitors show strong monthly sales, leaving room for differentiated entrants',
            'opportunity': 'sales_upside'
        })
    
    return gaps


def calculate_competitive_strength(review_analysis, competitors):
    """Estimate incumbent strength using signals that are available from APIs."""
    score = 50

    barrier = (review_analysis or {}).get('barrier_level')
    barrier_scores = {'LOW': 25, 'MEDIUM': 45, 'HIGH': 70, 'EXTREME': 90}
    if barrier in barrier_scores:
        score = barrier_scores[barrier]

    sales = [c.get('monthly_sales', 0) for c in competitors if c.get('monthly_sales', 0) > 0]
    if sales:
        avg_sales = mean(sales)
        if avg_sales >= 1000:
            score += 10
        elif avg_sales <= 100:
            score -= 10

    sellers = [c.get('seller_count', 0) for c in competitors if c.get('seller_count', 0) > 0]
    if sellers and mean(sellers) >= 10:
        score += 5

    return max(0, min(100, score))


def generate_entry_matrix(traffic_analysis, review_analysis, competitors):
    """Generate market entry recommendation matrix"""
    traffic_score = 100 - traffic_analysis['sponsored_pct'] if traffic_analysis else 50
    strength_score = calculate_competitive_strength(review_analysis, competitors)
    
    if traffic_score >= 50 and strength_score < 50:
        quadrant = 'SWEET_SPOT'
        recommendation = 'Best entry opportunity: High organic traffic + moderate incumbent strength'
    elif traffic_score >= 50 and strength_score >= 50:
        quadrant = 'TOUGH_FIGHT'
        recommendation = 'Competitive market: Good traffic but strong incumbent signals'
    elif traffic_score < 50 and strength_score < 50:
        quadrant = 'TEST_FIRST'
        recommendation = 'Uncertain market: Ad-heavy, but incumbent strength is moderate. Test with small investment.'
    else:
        quadrant = 'AVOID'
        recommendation = 'Difficult market: Ad-heavy + strong incumbents. High barrier to entry.'
    
    return {
        'quadrant': quadrant,
        'traffic_score': round(traffic_score),
        'competitive_strength_score': round(strength_score),
        'recommendation': recommendation
    }


def generate_competitor_charts(analysis, output_dir):
    """Generate competitor comparison charts"""
    if not HAS_MATPLOTLIB:
        print("Warning: matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    competitors = analysis.get('competitors', [])
    if not competitors:
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    keyword = analysis.get('keyword', 'competitors')[:20]
    
    # Set style - follow established chart display rules
    style = load_style()
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Chart 1: Price vs Reviews Scatter (Competitive Positioning)
    try:
        if len(competitors) < 2:
            print(f"  ⚠️ competitive_positioning.png skipped: need ≥2 items, got {len(competitors)}", file=sys.stderr)
        else:
            fig, ax = plt.subplots(figsize=(10, 6))

            prices = [c.get('price', 0) for c in competitors]
            reviews = [c.get('reviews', 0) for c in competitors]
            asins = [c.get('asin', '')[:10] for c in competitors]
            sponsored = [c.get('sponsored', False) for c in competitors]

            # Color by sponsored status - use consistent colors
            colors = [get_color('ebay') if s else get_color('primary') for s in sponsored]  # Red for sponsored, blue for organic
            sizes = [max(80, min(400, r/50)) for r in reviews]  # Size by reviews

            scatter = ax.scatter(prices, reviews, c=colors, s=sizes, alpha=0.7, edgecolors='white', linewidth=2, zorder=5)

            # Add ASIN labels - positioned outside data area to avoid overlap
            # Sort by price to assign labels left-to-right
            sorted_indices = sorted(range(len(prices)), key=lambda i: (prices[i], reviews[i]))

            for idx, i in enumerate(sorted_indices):
                asin = asins[i]
                # Alternate label positions: above/below, with increasing horizontal offset
                y_pos = reviews[i] * 1.3 if idx % 2 == 0 else reviews[i] * 0.7

                ax.annotate(
                    asin,
                    xy=(prices[i], reviews[i]),
                    xytext=(prices[i], y_pos),
                    fontsize=9,
                    fontweight='bold',
                    ha='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#cccccc', alpha=0.9),
                    arrowprops=dict(arrowstyle='-', color='#cccccc', alpha=0.5, lw=1)
                )

            ax.set_xlabel('Price ($)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Reviews', fontsize=11, fontweight='bold')
            ax.set_title(f'COMPETITIVE POSITIONING: {keyword.upper()}', fontsize=14, fontweight='bold', pad=15)

            # Legend - positioned outside plot area
            ax.scatter([], [], c=get_color('primary'), label='Organic', s=100, edgecolors='white')
            ax.scatter([], [], c=get_color('ebay'), label='Sponsored', s=100, edgecolors='white')
            ax.legend(loc='upper right', framealpha=0.9)

            # Log scale for reviews if range is large
            if max(reviews) > 10 * min(r for r in reviews if r > 0):
                ax.set_yscale('log')

            # Clean spines - follow UX rules
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            chart_path = os.path.join(output_dir, 'competitive_positioning.png')
            save_chart(fig, chart_path, style)
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate positioning chart: {e}", file=sys.stderr)

    # Chart 2: Price Distribution (Bar)
    try:
        if len(competitors) < 1:
            print(f"  ⚠️ price_distribution.png skipped: need ≥1 items, got {len(competitors)}", file=sys.stderr)
        else:
            fig, ax = plt.subplots(figsize=(10, 5))

            # Define price brackets
            brackets = ['<$15', '$15-25', '$25-40', '$40-60', '$60+']
            bracket_ranges = [(0, 15), (15, 25), (25, 40), (40, 60), (60, float('inf'))]
            counts = [0] * len(brackets)

            for c in competitors:
                price = c.get('price', 0)
                for i, (low, high) in enumerate(bracket_ranges):
                    if low <= price < high:
                        counts[i] += 1
                        break

            # Colors: highlight sweet spot (max count) in green, others in gray
            colors = [get_color('good') if c == max(counts) else get_color('muted') for c in counts]
            bars = ax.bar(brackets, counts, color=colors, edgecolor='white', linewidth=2)

            # Add count labels - positioned above bars with proper offset
            max_count = max(counts) if max(counts) > 0 else 1
            for bar, count in zip(bars, counts):
                if count > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_count * 0.05,
                           str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')

            ax.set_xlabel('Price Range', fontsize=11, fontweight='bold')
            ax.set_ylabel('Number of Competitors', fontsize=11, fontweight='bold')
            ax.set_title(f'PRICE DISTRIBUTION: {keyword.upper()}', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylim(0, max_count * 1.3)  # Leave room for labels

            # Highlight sweet spot with label
            max_idx = counts.index(max(counts))
            if counts[max_idx] > 0:
                ax.annotate('SWEET SPOT', xy=(max_idx, counts[max_idx] + max_count * 0.08),
                           ha='center', fontsize=10, color=get_color('good'), fontweight='bold')

            # Clean spines - follow UX rules
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            chart_path = os.path.join(output_dir, 'price_distribution.png')
            save_chart(fig, chart_path, style)
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate price chart: {e}", file=sys.stderr)
    
    # Chart 3: Market Entry Matrix (Quadrant)
    try:
        traffic = analysis.get('traffic_analysis', {})
        entry = analysis.get('entry_matrix', {})
        
        if traffic and entry:
            fig, ax = plt.subplots(figsize=(8, 8))
            
            traffic_score = entry.get('traffic_score', 50)
            strength_score = entry.get('competitive_strength_score', 50)
            quadrant = entry.get('quadrant', 'UNKNOWN')
            
            # Draw quadrants
            ax.axhline(y=50, color='gray', linestyle='-', alpha=0.3)
            ax.axvline(x=50, color='gray', linestyle='-', alpha=0.3)
            
            # Quadrant labels (no emojis - use text only for font compatibility)
            ax.text(25, 75, 'TEST FIRST\n(Low Traffic, Moderate Strength)', ha='center', va='center',
                   fontsize=10, alpha=0.5, style='italic',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
            ax.text(75, 75, '>>> SWEET SPOT <<<\n(High Traffic, Moderate Strength)', ha='center', va='center',
                   fontsize=11, color='green', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
            ax.text(25, 25, 'X AVOID X\n(Low Traffic, Strong Incumbents)', ha='center', va='center',
                   fontsize=10, color='red', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
            ax.text(75, 25, 'TOUGH FIGHT\n(High Traffic, Strong Incumbents)', ha='center', va='center',
                   fontsize=10, alpha=0.5, style='italic',
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
            
            # Plot current market position
            ax.scatter([traffic_score], [100 - strength_score], s=300, c='blue',
                      edgecolors='black', linewidth=2, zorder=5)
            ax.annotate(f'THIS MARKET\n({quadrant})', 
                       xy=(traffic_score, 100 - strength_score),
                       xytext=(traffic_score + 10, 100 - strength_score + 10),
                       fontsize=10, fontweight='bold',
                       arrowprops=dict(arrowstyle='->', color='blue'))
            
            ax.set_xlabel('Traffic Score (Organic %)', fontsize=12)
            ax.set_ylabel('Opportunity Score (100 - Competitive Strength)', fontsize=12)
            ax.set_title('Market Entry Matrix', fontsize=14, fontweight='bold')
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            
            chart_path = os.path.join(output_dir, 'entry_matrix.png')
            save_chart(fig, chart_path, style)
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate entry matrix chart: {e}", file=sys.stderr)
    
    return charts


def format_report(analysis):
    """Format analysis as text report"""
    lines = []
    
    keyword = analysis.get('keyword', analysis.get('target_asin', 'Unknown'))
    marketplace = analysis.get('marketplace', 'US')
    competitors = analysis.get('competitors', [])
    
    # Header
    lines.append("=" * 70)
    lines.append(f"🎯 COMPETITOR ANALYSIS: {keyword}")
    lines.append(f"   Market: Amazon {marketplace} | Analyzed: {len(competitors)} competitors")
    lines.append("=" * 70)
    lines.append("")
    
    # Market Overview
    price_analysis = analysis.get('price_analysis')
    if price_analysis:
        lines.append("📊 MARKET OVERVIEW")
        lines.append(f"   Price Range: ${price_analysis['min']:.2f} - ${price_analysis['max']:.2f}")
        lines.append(f"   Average: ${price_analysis['avg']:.2f} | Median: ${price_analysis['median']:.2f}")
        lines.append(f"   Sweet Spot: {price_analysis['sweet_spot']}")
        lines.append("")
    
    # Review Barrier
    review_analysis = analysis.get('review_analysis')
    if review_analysis:
        lines.append("📝 REVIEW BARRIER")
        lines.append(f"   Top 3 Average: {review_analysis['top3_avg']:,} reviews")
        lines.append(f"   Barrier Level: {review_analysis['barrier_level']}")
        lines.append(f"   → {review_analysis['assessment']}")
        lines.append("")
    
    # Traffic Distribution
    traffic = analysis.get('traffic_analysis')
    if traffic:
        lines.append("📡 TRAFFIC DISTRIBUTION")
        lines.append(f"   Organic: {traffic['organic_pct']}% | Sponsored: {traffic['sponsored_pct']}%")
        lines.append(f"   Top 5 Sponsored: {traffic['top5_sponsored']}/5")
        lines.append(f"   Market Type: {traffic['market_type']}")
        lines.append(f"   → {traffic['assessment']}")
        lines.append("")
    
    # Competitive Matrix
    lines.append("📈 COMPETITIVE MATRIX")
    lines.append("┌" + "─" * 68 + "┐")
    lines.append(f"│ {'ASIN':<12} │ {'Price':>7} │ {'Reviews':>7} │ {'Rating':>6} │ {'BSR':>8} │ {'Trend':>8} │")
    lines.append("├" + "─" * 68 + "┤")
    
    for c in competitors:  # All competitors
        asin = c.get('asin', 'N/A')[:12]
        price = f"${c.get('price', 0):.0f}"
        reviews = f"{c.get('reviews', 0):,}"
        rating = f"{c.get('rating', 0):.1f}⭐" if c.get('rating') else 'N/A'
        bsr = f"#{c.get('bsr_sub', c.get('bsr', 0)):,}" if c.get('bsr_sub') or c.get('bsr') else 'N/A'
        
        trend_dir, trend_pct = c.get('trend', ('unknown', 0))
        if trend_dir == 'improving':
            trend = f"↗️ +{abs(trend_pct):.0f}%"
        elif trend_dir == 'declining':
            trend = f"↘️ -{abs(trend_pct):.0f}%"
        else:
            trend = "→ stable"
        
        sponsored = "💰" if c.get('sponsored') else ""
        
        lines.append(f"│ {asin:<12} │ {price:>7} │ {reviews:>7} │ {rating:>6} │ {bsr:>8} │ {trend:>8} │{sponsored}")
    
    lines.append("└" + "─" * 68 + "┘")
    lines.append("   💰 = Sponsored position")
    lines.append("")
    
    # Gap Analysis
    gaps = analysis.get('gap_analysis', [])
    if gaps:
        lines.append("🎯 GAP ANALYSIS")
        for gap in gaps:
            icon = "✅" if gap['opportunity'] in ['low_competition', 'organic_growth', 'top_position_achievable'] else "⚠️"
            lines.append(f"   {icon} {gap['detail']}")
        lines.append("")
    
    # Entry Matrix
    entry = analysis.get('entry_matrix')
    if entry:
        lines.append("🧭 MARKET ENTRY MATRIX")
        lines.append(f"   Quadrant: {entry['quadrant']}")
        lines.append(f"   Traffic Score: {entry['traffic_score']}/100 | Competitive Strength: {entry['competitive_strength_score']}/100")
        lines.append(f"   → {entry['recommendation']}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Competitor Analyzer')
    parser.add_argument('input', nargs='?', help='JSON input with asin, keyword, or asins')
    parser.add_argument('--report', action='store_true', help='Generate text report')
    parser.add_argument('--chart', type=str, help='Output directory for charts')
    parser.add_argument('--limit', type=int, default=10, help='Number of competitors to analyze (default: 10)')
    parser.add_argument('--listing-quality', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--fast', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--output', type=str, help='Save raw JSON result to file path for later merging')
    parser.add_argument('--merge', nargs='+', type=str, help='Merge batch JSON files and generate unified charts')
    parser.add_argument('--sort', default='score', choices=['score', 'sales', 'growth'], help='Sort key for --merge output')
    
    args = parser.parse_args()

    if args.merge:
        result = merge_and_chart(args.merge, sort_key=args.sort, chart_dir=args.chart)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not args.input:
        parser.error('input is required unless --merge is used')
    
    # Parse input
    try:
        params = json.loads(args.input)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    
    if not any(k in params for k in ('keyword', 'asin', 'asins')):
        print(json.dumps({'error': 'Missing required parameter: keyword, asin, or asins'}, indent=2, ensure_ascii=False))
        sys.exit(1)

    marketplace = params.get('marketplace', 'US')
    limit = params.get('limit', args.limit)

    # Determine analysis mode
    search_results = []
    target_asin = None
    keyword = None
    
    if 'keyword' in params:
        # Keyword search mode
        keyword = params['keyword']
        print(f"Searching for: {keyword}", file=sys.stderr)
        search_results = search_competitors(keyword, marketplace, limit + 10)
    
    elif 'asin' in params:
        # Single ASIN mode - find similar products
        target_asin = params['asin']
        print(f"Finding competitors for: {target_asin}", file=sys.stderr)
        
        # Get target product details to determine category
        target_details = get_product_details(target_asin, marketplace)
        if target_details:
            # Use category name as search keyword
            category = target_details.get('bsr_category', '')
            if category:
                search_results = search_competitors(category, marketplace, limit + 10)
    
    elif 'asins' in params:
        # Direct ASIN comparison mode
        asins = params['asins']
        print(f"Comparing ASINs: {asins}", file=sys.stderr)
        
        for asin in asins[:limit]:
            details = get_product_details(asin, marketplace)
            if details:
                search_results.append(details)
    
    if not search_results:
        print("Error: No competitors found", file=sys.stderr)
        sys.exit(1)
    
    # Get detailed data for each competitor
    competitors = []
    for i, sr in enumerate(search_results[:limit]):
        asin = sr.get('asin')
        print(f"Analyzing {i+1}/{min(len(search_results), limit)}: {asin}", file=sys.stderr)
        
        # Get detailed product data
        details = get_product_details(asin, marketplace)
        if details:
            comp = {**sr, **details}
        else:
            comp = sr
        
        # Get BSR trend
        bsr_history = get_bsr_history(asin, marketplace)
        if bsr_history:
            trend_dir, trend_pct = calculate_bsr_trend(bsr_history)
            comp['trend'] = (trend_dir, trend_pct)
        else:
            comp['trend'] = ('unknown', 0)
        
        competitors.append(comp)
    
    # Perform analysis
    analysis = {
        'keyword': keyword,
        'target_asin': target_asin,
        'marketplace': marketplace,
        'analyzed_at': datetime.now().isoformat(),
        'competitors': competitors,
        'traffic_analysis': analyze_traffic_distribution(search_results),
        'price_analysis': analyze_price_distribution(competitors),
        'review_analysis': analyze_review_barrier(competitors)
    }
    
    # Gap analysis
    analysis['gap_analysis'] = generate_gap_analysis(
        competitors,
        analysis['price_analysis'],
        analysis['traffic_analysis']
    )
    
    # Entry matrix
    analysis['entry_matrix'] = generate_entry_matrix(
        analysis['traffic_analysis'],
        analysis['review_analysis'],
        competitors
    )
    
    # Generate charts if requested
    if args.chart:
        print(f"Generating charts to {args.chart}...", file=sys.stderr)
        charts = generate_competitor_charts(analysis, args.chart)
        if charts:
            print(f"Generated {len(charts)} charts:", file=sys.stderr)
            for chart in charts:
                print(f"  📊 {chart}", file=sys.stderr)
        analysis['charts'] = charts

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str, ensure_ascii=False)
    
    # Output
    if args.report:
        report = format_report(analysis)
        print(report)
        
        # Show chart locations if generated
        if args.chart and analysis.get('charts'):
            print("\n📊 Charts saved to:", file=sys.stderr)
            for chart in analysis['charts']:
                print(f"   {chart}", file=sys.stderr)
    else:
        # Clean up for JSON output
        output = {k: v for k, v in analysis.items()}
        print(json.dumps(output, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
