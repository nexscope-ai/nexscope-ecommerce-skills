#!/usr/bin/env python3
"""
Image Similarity Finder v1.0.0

Find similar products on Amazon using image-based search.
Answers: "Are there similar products?"

Features:
- Visual product search across 8 Amazon marketplaces
- Competitive analysis of similar products
- Price/rating/sales comparison
- Opportunity scoring
- Cross-market comparison

Usage:
    python3 image_similarity_finder.py '{"image_url": "https://..."}'
    python3 image_similarity_finder.py '{"image_url": "https://...", "market": "US"}'
    python3 image_similarity_finder.py '{"image_url": "https://...", "with_keepa": true}'
"""

import json
import os
import sys
import argparse
from datetime import datetime
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

# Market mapping
MARKET_TO_DOMAIN = {
    'US': 'amazon.com',
    'UK': 'amazon.co.uk',
    'DE': 'amazon.de',
    'FR': 'amazon.fr',
    'IT': 'amazon.it',
    'ES': 'amazon.es',
    'JP': 'amazon.co.jp',
    'IN': 'amazon.in'
}

DOMAIN_TO_CURRENCY = {
    'amazon.com': '$',
    'amazon.co.uk': '£',
    'amazon.de': '€',
    'amazon.fr': '€',
    'amazon.it': '€',
    'amazon.es': '€',
    'amazon.co.jp': '¥',
    'amazon.in': '₹'
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

def search_by_image(
    image_url: str,
    domain: str = 'amazon.com',
    sort: str = 'default',
    with_keepa: bool = False
) -> dict:
    """Search Amazon by image"""
    result = api_call('/amazon/searchByImage', {
        'imageUrl': image_url,
        'amazonDomain': domain,
        'sort': sort,
        'aggregateByKeepaData': with_keepa
    })
    
    if result and 'products' in result:
        return {
            'products': result['products'],
            'total': result.get('total', len(result['products'])),
            'cost_token': result.get('costToken', 0)
        }
    elif result and 'errcode' in result:
        return {'error': result.get('errmsg', 'Unknown error')}
    return {'error': 'No response', 'products': []}

# === Analysis Functions ===

def analyze_similar_products(products: List[dict], domain: str) -> dict:
    """Analyze similar products for competitive insights"""
    if not products:
        return {'error': 'No products to analyze'}
    
    currency = DOMAIN_TO_CURRENCY.get(domain, '$')
    
    # Extract metrics
    prices = [float(p.get('price', 0)) for p in products if float(p.get('price') or 0) > 0]
    ratings = [float(p.get('rating', 0)) for p in products if float(p.get('rating') or 0) > 0]
    reviews = [p.get('ratings', 0) for p in products if p.get('ratings')]
    
    # Sales data (if Keepa enabled)
    monthly_sales = [p.get('monthlySalesUnits', 0) for p in products if p.get('monthlySalesUnits')]
    
    # Brand distribution
    brands = {}
    for p in products:
        brand = p.get('brand', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1
    
    # Price tiers
    price_tiers = {'budget': 0, 'mid': 0, 'premium': 0}
    if prices:
        median_price = statistics.median(prices)
        for price in prices:
            if price < median_price * 0.7:
                price_tiers['budget'] += 1
            elif price > median_price * 1.3:
                price_tiers['premium'] += 1
            else:
                price_tiers['mid'] += 1
    
    analysis = {
        'total_similar': len(products),
        'price_analysis': {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'median': round(statistics.median(prices), 2) if prices else 0,
            'mean': round(statistics.mean(prices), 2) if prices else 0,
            'currency': currency
        },
        'rating_analysis': {
            'min': min(ratings) if ratings else 0,
            'max': max(ratings) if ratings else 0,
            'median': round(statistics.median(ratings), 2) if ratings else 0,
            'avg': round(statistics.mean(ratings), 2) if ratings else 0
        },
        'review_analysis': {
            'min': min(reviews) if reviews else 0,
            'max': max(reviews) if reviews else 0,
            'median': int(statistics.median(reviews)) if reviews else 0,
            'total': sum(reviews) if reviews else 0
        },
        'brand_distribution': dict(sorted(brands.items(), key=lambda x: -x[1])[:10]),
        'price_tiers': price_tiers
    }
    
    # Add sales analysis if Keepa data available
    if monthly_sales:
        analysis['sales_analysis'] = {
            'products_with_sales_data': len(monthly_sales),
            'total_monthly_units': sum(monthly_sales),
            'avg_monthly_units': int(statistics.mean(monthly_sales)),
            'top_seller_units': max(monthly_sales)
        }
    
    return analysis

def calculate_opportunity_score(analysis: dict, products: List[dict]) -> dict:
    """Calculate opportunity score based on market analysis"""
    score = 50  # Base score
    factors = []
    
    # Factor 1: Competition level (fewer similar = better)
    total = analysis.get('total_similar', 0)
    if total < 10:
        score += 20
        factors.append(('Low competition', '+20', f'Only {total} similar products'))
    elif total < 20:
        score += 10
        factors.append(('Moderate competition', '+10', f'{total} similar products'))
    elif total > 50:
        score -= 15
        factors.append(('High competition', '-15', f'{total} similar products'))
    
    # Factor 2: Rating gap (low avg rating = opportunity)
    avg_rating = (analysis.get('rating_analysis') or {}).get('avg', 0)
    if avg_rating < 4.0:
        score += 15
        factors.append(('Quality gap', '+15', f'Avg rating only {avg_rating}★'))
    elif avg_rating > 4.5:
        score -= 10
        factors.append(('High quality competitors', '-10', f'Avg rating {avg_rating}★'))
    
    # Factor 3: Price spread (large spread = niche opportunities)
    price_analysis = analysis.get('price_analysis', {})
    if price_analysis.get('max', 0) > 0 and price_analysis.get('min', 0) > 0:
        spread = price_analysis['max'] / price_analysis['min']
        if spread > 5:
            score += 10
            factors.append(('Price diversity', '+10', 'Room for different positioning'))
    
    # Factor 4: Brand concentration
    brands = analysis.get('brand_distribution', {})
    if brands:
        top_brand_share = list(brands.values())[0] / analysis['total_similar'] * 100
        if top_brand_share < 30:
            score += 10
            factors.append(('Fragmented market', '+10', 'No dominant brand'))
        elif top_brand_share > 50:
            score -= 10
            factors.append(('Brand dominated', '-10', f'Top brand has {top_brand_share:.0f}% share'))
    
    # Cap score
    score = max(0, min(100, score))
    
    # Determine level
    if score >= 70:
        level = 'HIGH'
        recommendation = 'Good opportunity - market has gaps you can fill'
    elif score >= 50:
        level = 'MODERATE'
        recommendation = 'Viable opportunity - differentiation needed'
    elif score >= 30:
        level = 'LOW'
        recommendation = 'Challenging market - strong differentiation required'
    else:
        level = 'VERY LOW'
        recommendation = 'Difficult market - consider alternative products'
    
    return {
        'score': score,
        'level': level,
        'recommendation': recommendation,
        'factors': factors
    }

def find_price_gaps(products: List[dict], currency: str) -> List[dict]:
    """Find price gaps in the market"""
    prices = sorted([float(p.get('price', 0)) for p in products if float(p.get('price') or 0) > 0])
    
    if len(prices) < 3:
        return []
    
    gaps = []
    for i in range(len(prices) - 1):
        gap = prices[i + 1] - prices[i]
        gap_pct = (gap / prices[i]) * 100 if prices[i] > 0 else 0
        
        if gap_pct > 30:  # Significant gap (30%+)
            gaps.append({
                'lower_price': round(prices[i], 2),
                'upper_price': round(prices[i + 1], 2),
                'gap_amount': round(gap, 2),
                'gap_percentage': round(gap_pct, 1),
                'opportunity_price': round((prices[i] + prices[i + 1]) / 2, 2),
                'currency': currency
            })
    
    return sorted(gaps, key=lambda x: -x['gap_percentage'])[:3]

def generate_insights(
    analysis: dict,
    opportunity: dict,
    price_gaps: List[dict],
    products: List[dict]
) -> dict:
    """Generate narrative insights"""
    total = analysis.get('total_similar', 0)
    price = analysis.get('price_analysis', {})
    rating = analysis.get('rating_analysis', {})
    
    # Summary
    currency = price.get('currency', '$')
    summary = f"Found {total} similar products. "
    summary += f"Price range: {currency}{price.get('min', 0):.2f} - {currency}{price.get('max', 0):.2f}. "
    summary += f"Avg rating: {rating.get('avg', 0):.1f}★"
    
    # Recommendations
    recommendations = []
    
    # Based on opportunity score
    if opportunity['level'] == 'HIGH':
        recommendations.append(f"✅ {opportunity['recommendation']}")
    elif opportunity['level'] == 'MODERATE':
        recommendations.append(f"⚠️ {opportunity['recommendation']}")
    else:
        recommendations.append(f"🔴 {opportunity['recommendation']}")
    
    # Price positioning
    if price_gaps:
        gap = price_gaps[0]
        recommendations.append(
            f"💰 Price gap opportunity: Position between {currency}{gap['lower_price']} and {currency}{gap['upper_price']} "
            f"(target ~{currency}{gap['opportunity_price']})"
        )
    
    # Quality positioning
    if rating.get('avg', 5) < 4.2:
        recommendations.append(
            f"⭐ Quality opportunity: Competitors average only {rating['avg']:.1f}★ - room to excel"
        )
    
    # Brand positioning
    brands = analysis.get('brand_distribution', {})
    if brands:
        top_brand = list(brands.keys())[0]
        recommendations.append(f"🏷️ Top brand in this space: {top_brand}")
    
    return {
        'summary': summary,
        'opportunity_score': f"{opportunity['score']}/100 ({opportunity['level']})",
        'recommendations': recommendations
    }

# === Main Function ===

def find_similar_products(
    image_url: str,
    market: str = 'US',
    sort: str = 'default',
    with_keepa: bool = False,
    cross_market: bool = False
) -> dict:
    """Main function to find and analyze similar products"""
    
    domain = MARKET_TO_DOMAIN.get(market.upper(), 'amazon.com')
    
    result = {
        'image_url': image_url,
        'marketplace': market,
        'domain': domain,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0'
    }
    
    # Step 1: Search by image
    print(f"[1/3] Searching similar products on {domain}...", file=sys.stderr)
    search_result = search_by_image(image_url, domain, sort, with_keepa)
    
    if 'error' in search_result:
        result['error'] = search_result['error']
        return result
    
    products = search_result.get('products', [])
    result['total_found'] = search_result.get('total', len(products))
    result['cost_token'] = search_result.get('cost_token', 0)
    
    if not products:
        result['error'] = 'No similar products found'
        return result
    
    print(f"    ✓ Found {len(products)} similar products", file=sys.stderr)
    
    # Step 2: Analyze similar products
    print(f"[2/3] Analyzing competitive landscape...", file=sys.stderr)
    analysis = analyze_similar_products(products, domain)
    result['market_analysis'] = analysis
    
    # Step 3: Calculate opportunity and insights
    print(f"[3/3] Generating insights...", file=sys.stderr)
    opportunity = calculate_opportunity_score(analysis, products)
    result['opportunity_assessment'] = opportunity
    
    price_gaps = find_price_gaps(products, analysis['price_analysis']['currency'])
    if price_gaps:
        result['price_gaps'] = price_gaps
    
    insights = generate_insights(analysis, opportunity, price_gaps, products)
    result['insights'] = insights
    
    # Similar products list (top 10)
    result['similar_products'] = [
        {
            'rank': i + 1,
            'asin': p.get('asin'),
            'title': (p.get('title', '')[:70] + '...') if len(p.get('title', '')) > 70 else p.get('title'),
            'price': p.get('price'),
            'currency': p.get('currency', analysis['price_analysis']['currency']),
            'rating': p.get('rating'),
            'reviews': p.get('ratings', 0),
            'brand': p.get('brand', 'Unknown'),
            'image_url': p.get('imageUrl'),
            'monthly_sales': p.get('monthlySalesUnits') if with_keepa else None
        }
        for i, p in enumerate(products[:10])
    ]
    
    # Cross-market search (optional)
    if cross_market:
        print(f"[+] Cross-market search...", file=sys.stderr)
        cross_results = {}
        other_markets = [m for m in MARKET_TO_DOMAIN.keys() if m != market.upper()][:3]
        
        for other_market in other_markets:
            other_domain = MARKET_TO_DOMAIN[other_market]
            print(f"    Searching {other_domain}...", file=sys.stderr)
            
            other_search = search_by_image(image_url, other_domain, 'default', False)
            if 'products' in other_search and other_search['products']:
                cross_results[other_market] = {
                    'total': len(other_search['products']),
                    'price_range': f"{min([p.get('price', 0) for p in other_search['products'] if p.get('price')]):.2f} - {max([p.get('price', 0) for p in other_search['products'] if p.get('price')]):.2f}",
                    'top_product': other_search['products'][0].get('title', '')[:50]
                }
        
        if cross_results:
            result['cross_market'] = cross_results
    
    return result

# === Chart Generation ===

def generate_charts(result: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
    except ImportError:
        print("matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    BLUE = get_color('primary')
    GREEN = get_color('good')
    ORANGE = get_color('secondary')
    RED = get_color('hot')
    PURPLE = '#9C27B0'
    
    analysis = result.get('market_analysis', {})
    products = result.get('similar_products', [])
    
    # Chart 1: Price Distribution
    if products:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        prices = [p.get('price', 0) for p in products if p.get('price')]
        titles = [f"#{p['rank']}" for p in products if p.get('price')]

        median_price = statistics.median(prices) if prices else 0
        colors = [GREEN if p < median_price * 0.8 else RED if p > median_price * 1.2 else BLUE for p in prices]
        
        bars = ax.bar(titles[:10], prices[:10], color=colors, edgecolor='white', linewidth=2)
        
        currency = (analysis.get('price_analysis') or {}).get('currency', '$')
        for bar, price in zip(bars, prices[:10]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(prices)*0.02,
                   f'{currency}{price:.0f}', ha='center', fontsize=9)
        
        median = (analysis.get('price_analysis') or {}).get('median', 0)
        ax.axhline(y=median, color=ORANGE, linestyle='--', label=f'Median: {currency}{median:.2f}')
        
        ax.set_ylabel(f'Price ({currency})', fontsize=11)
        ax.set_xlabel('Similar Products', fontsize=11)
        ax.set_title('PRICE COMPARISON: SIMILAR PRODUCTS', fontweight='bold', fontsize=12, pad=15)
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_price_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Price Comparison", file=sys.stderr)
    
    # Chart 2: Rating vs Reviews
    if len(products) < 2:
        print(f"  ⚠️ 2_rating_reviews.png skipped: need ≥2 items, got {len(products)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ratings = [p.get('rating') or 0 for p in products]
        reviews = [p.get('reviews') or 0 for p in products]
        prices = [p.get('price') or 0 for p in products]
        
        # Size by price, color by rating
        sizes = [max(50, min(500, p * 5)) for p in prices]
        colors = [GREEN if r >= 4.5 else BLUE if r >= 4.0 else ORANGE if r >= 3.5 else RED for r in ratings]
        
        scatter = ax.scatter(reviews, ratings, s=sizes, c=colors, alpha=0.7, edgecolors='white', linewidth=2)
        
        for i, p in enumerate(products[:5]):
            ax.annotate(f"#{p['rank']}", (reviews[i], ratings[i]), fontsize=9, ha='center')
        
        ax.set_xlabel('Number of Reviews', fontsize=11)
        ax.set_ylabel('Rating (★)', fontsize=11)
        ax.set_title('RATING vs REVIEWS: SIMILAR PRODUCTS', fontweight='bold', fontsize=12, pad=15)
        ax.set_ylim(0, 5.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_rating_reviews.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Rating vs Reviews", file=sys.stderr)
    
    # Chart 3: Brand Distribution
    brands = analysis.get('brand_distribution', {})
    if brands:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        brand_names = list(brands.keys())[:8]
        brand_counts = list(brands.values())[:8]
        
        colors = [BLUE if i == 0 else PURPLE if i < 3 else ORANGE for i in range(len(brand_names))]
        
        bars = ax.barh(brand_names, brand_counts, color=colors, edgecolor='white', linewidth=2)
        
        for bar, count in zip(bars, brand_counts):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   str(count), va='center', fontsize=10)
        
        ax.set_xlabel('Number of Products', fontsize=11)
        ax.set_title('BRAND DISTRIBUTION: SIMILAR PRODUCTS', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_brand_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Brand Distribution", file=sys.stderr)
    
    # Chart 4: Opportunity Score Gauge
    opportunity = result.get('opportunity_assessment', {})
    if opportunity.get('score') is not None:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        score = opportunity['score']
        level = opportunity['level']
        
        gauge_colors = [RED, ORANGE, get_color('warning'), GREEN]
        ranges = [30, 20, 20, 30]
        starts = [0, 30, 50, 70]
        labels = ['VERY LOW\n(0-30)', 'LOW\n(30-50)', 'MODERATE\n(50-70)', 'HIGH\n(70-100)']
        
        for start, width, color in zip(starts, ranges, gauge_colors):
            ax.barh(0, width, left=start, height=0.3, color=color, edgecolor='white', linewidth=2)
        
        ax.scatter([score], [0], s=300, c='black', marker='^', zorder=5)
        ax.text(score, 0.25, f'Score: {score}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        for start, width, label in zip(starts, ranges, labels):
            ax.text(start + width/2, -0.25, label, ha='center', va='top', fontsize=9)
        
        ax.set_xlim(-5, 105)
        ax.set_ylim(-0.6, 0.5)
        ax.set_title(f'OPPORTUNITY SCORE: {level}', fontweight='bold', fontsize=13, pad=15)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_opportunity_score.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Opportunity Score", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Image Similarity Finder v1.0.0')
    parser.add_argument('params', help='JSON parameters: {"image_url": "https://..."}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    image_url = params.get('image_url')
    if not image_url:
        print("Missing required parameter: image_url", file=sys.stderr)
        sys.exit(1)
    
    result = find_similar_products(
        image_url=image_url,
        market=params.get('market', 'US'),
        sort=params.get('sort', 'default'),
        with_keepa=params.get('with_keepa', False),
        cross_market=params.get('cross_market', False)
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
