#!/usr/bin/env python3
"""
Keyword Reverse Lookup v1.0.0

Reverse-engineer competitor traffic by finding what keywords they rank for.
Answers: "What keywords drive competitor sales?"

Data Source:
- Keywords API: keywords_by_asin_query (via NexScope proxy)

Usage:
    python3 keyword_reverse_lookup.py '{"asin": "B07RL88DD2"}'
    python3 keyword_reverse_lookup.py '{"asins": ["B07RL88DD2", "B01MSSDEPK"]}'
"""

import json
import sys
import os
from datetime import datetime
from typing import Optional, List
from urllib.request import Request, urlopen

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

_PROXY_ENDPOINTS = {
    '/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
    '/keywords/keywords_by_asin_query': '/keywords/by-asin',
}
_PROXY_LIST_FIELDS = {
    '/keywords/by-keyword': 'keywordInfoList',
    '/keywords/by-asin': 'keywordInfoList',
}

MARKET_MAP = {'US': 'us', 'UK': 'uk', 'DE': 'de', 'FR': 'fr', 'CA': 'ca', 'JP': 'jp'}

# === API Functions ===

def js_api_call(endpoint: str, payload: dict, market: str = 'us') -> Optional[dict]:
    """Call Keywords API via NexScope proxy"""
    import re

    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    proxy_ep = _PROXY_ENDPOINTS.get(endpoint, endpoint)
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout{proxy_ep}"
    headers = {
        'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    attrs = (payload.get('data') or {}).get('attributes', payload)
    proxy_payload = {'marketplace': market}
    for k, v in attrs.items():
        parts = k.split('_')
        camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        proxy_payload[camel] = v
    try:
        data = json.dumps(proxy_payload).encode('utf-8')
        req = Request(url, data=data, headers=headers, method='POST')
        with urlopen(req, timeout=60) as response:
            raw = json.loads(response.read().decode('utf-8'))
        if raw.get('code') != 0:
            print(f"Proxy error: {raw.get('msg', 'unknown')}", file=sys.stderr)
            return None
        list_field = _PROXY_LIST_FIELDS.get(proxy_ep, 'keywordInfoList')
        _inner = raw.get('data', {})
        if isinstance(_inner, dict) and 'code' in _inner:
            _inner = _inner.get('data', {})
        items = _inner.get(list_field, [])
        def _c2s(name):
            s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
            return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return {'data': [{'attributes': {_c2s(k): v for k, v in item.items()}} for item in items]}
    except Exception as e:
        print(f"Proxy API Error [{endpoint}]: {e}", file=sys.stderr)
        return None

def get_keywords_by_asin(asins: List[str], market: str = 'us', 
                          min_volume: int = 100) -> Optional[List[dict]]:
    """Get keywords that ASINs rank for (one API call per ASIN, proxy requires string not array)"""
    all_keywords = []
    for asin in asins[:5]:  # API limit 5 ASINs
        payload = {
            "data": {
                "type": "keywords_by_asin_query",
                "attributes": {
                    "asins": asin,  # proxy expects string, not array
                    "include_variants": False,
                    "min_monthly_search_volume_exact": min_volume
                }
            }
        }
        result = js_api_call('/keywords/keywords_by_asin_query', payload, market)
        if result and 'data' in result:
            all_keywords.extend(result['data'])
    return all_keywords if all_keywords else None

# === Analysis Functions ===

def classify_keyword(keyword: str, asin_title: str = '') -> str:
    """Classify keyword type"""
    keyword_lower = keyword.lower()
    
    # Brand keywords (contains brand name)
    brand_indicators = ['cerave', 'neutrogena', 'la roche', 'cetaphil', 'aveeno', 
                       'olay', 'nivea', 'garnier', 'bioré', 'panoxyl', 'cosrx',
                       'the ordinary', 'clinique', 'dove', 'clean & clear']
    for brand in brand_indicators:
        if brand in keyword_lower:
            return 'BRAND'
    
    # Long-tail (4+ words or specific modifiers)
    words = keyword_lower.split()
    long_tail_modifiers = ['for', 'with', 'without', 'best', 'good', 'sensitive', 
                           'oily', 'dry', 'acne', 'anti', 'natural', 'organic']
    if len(words) >= 4 or any(m in words for m in long_tail_modifiers):
        return 'LONG_TAIL'
    
    # Generic (1-3 words, no brand)
    return 'GENERIC'

def analyze_keywords(keywords_data: List[dict], asin: str) -> dict:
    """Analyze keyword data for an ASIN"""
    if not keywords_data:
        return {'error': 'No keyword data'}
    
    # Filter to keywords for this ASIN
    asin_keywords = [k for k in keywords_data 
                     if (k.get('attributes') or {}).get('primary_asin') == asin]
    
    if not asin_keywords:
        asin_keywords = keywords_data  # Use all if filtering fails
    
    total_keywords = len(asin_keywords)
    
    # Extract and sort by volume
    keyword_list = []
    for kw in asin_keywords:
        attr = kw.get('attributes', {})
        _rank = attr.get('organic_rank')
        keyword_list.append({
            'keyword': attr.get('name', ''),
            'search_volume_exact': int(attr.get('monthly_search_volume_exact', 0) or 0),
            'search_volume_broad': int(attr.get('monthly_search_volume_broad', 0) or 0),
            'organic_rank': int(_rank) if _rank is not None else None,
            'sponsored_rank': int(attr.get('sponsored_ranking_asins_count') or 0) > 0,
            'overall_rank': attr.get('overall_rank') and int(attr.get('overall_rank')),
            'ease_of_ranking': int(attr.get('ease_of_ranking_score', 0) or 0),
            'relevancy_score': int(attr.get('relevancy_score', 0) or 0),
            'ppc_bid_exact': attr.get('ppc_bid_exact') and float(attr.get('ppc_bid_exact')),
            'ppc_bid_broad': attr.get('ppc_bid_broad') and float(attr.get('ppc_bid_broad')),
            'monthly_trend': int(attr.get('monthly_trend', 0) or 0),
            'category': attr.get('dominant_category', '')
        })
    
    # Sort by search volume
    keyword_list.sort(key=lambda x: x['search_volume_exact'], reverse=True)
    
    # Calculate statistics
    total_volume = sum(k['search_volume_exact'] for k in keyword_list)
    
    # Ranking distribution (organic_rank=0 means no organic position, exclude like None)
    top_10 = sum(1 for k in keyword_list if k['organic_rank'] is not None and k['organic_rank'] > 0 and k['organic_rank'] <= 10)
    top_20 = sum(1 for k in keyword_list if k['organic_rank'] is not None and k['organic_rank'] > 0 and k['organic_rank'] <= 20)
    top_50 = sum(1 for k in keyword_list if k['organic_rank'] is not None and k['organic_rank'] > 0 and k['organic_rank'] <= 50)

    # Traffic source analysis
    organic_only = sum(1 for k in keyword_list
                       if k['organic_rank'] is not None and k['organic_rank'] > 0 and not k['sponsored_rank'])
    sponsored_only = sum(1 for k in keyword_list
                         if k['sponsored_rank'] and (k['organic_rank'] is None or k['organic_rank'] == 0))
    both = sum(1 for k in keyword_list
               if k['organic_rank'] is not None and k['organic_rank'] > 0 and k['sponsored_rank'])
    
    # Keyword type classification
    types = {'BRAND': 0, 'GENERIC': 0, 'LONG_TAIL': 0}
    for k in keyword_list:
        ktype = classify_keyword(k['keyword'])
        types[ktype] += 1
        k['type'] = ktype
    
    # High volume keywords (>1000)
    high_volume = [k for k in keyword_list if k['search_volume_exact'] >= 1000]
    
    # Opportunity keywords (good volume, easy to rank, poor current rank)
    opportunities = [k for k in keyword_list
                     if k['search_volume_exact'] >= 500
                     and k['ease_of_ranking'] >= 70
                     and (k['organic_rank'] is None or k['organic_rank'] == 0 or k['organic_rank'] > 20)]
    opportunities.sort(key=lambda x: x['search_volume_exact'], reverse=True)
    
    # Trending keywords
    trending_up = [k for k in keyword_list if k['monthly_trend'] > 10]
    trending_down = [k for k in keyword_list if k['monthly_trend'] < -10]
    
    # Calculate estimated traffic (rough: sum of volume * position factor)
    est_traffic = 0
    for k in keyword_list:
        if k['organic_rank'] is not None and k['organic_rank'] > 0:
            # CTR approximation: rank 1 = 30%, rank 10 = 3%, rank 50 = 0.5%
            ctr = max(0.5, 30 / k['organic_rank']) / 100
            est_traffic += k['search_volume_exact'] * ctr
    
    return {
        'asin': asin,
        'total_keywords': total_keywords,
        'total_search_volume': total_volume,
        'estimated_monthly_traffic': round(est_traffic),
        
        'ranking_distribution': {
            'top_10': top_10,
            'top_20': top_20,
            'top_50': top_50,
            'below_50': total_keywords - top_50
        },
        
        'traffic_sources': {
            'organic_only': organic_only,
            'sponsored_only': sponsored_only,
            'both': both,
            'organic_pct': round(organic_only / total_keywords * 100, 1) if total_keywords else 0
        },
        
        'keyword_types': types,
        
        'high_volume_keywords': len(high_volume),
        'top_keywords': keyword_list[:15],
        'opportunity_keywords': opportunities[:10],
        
        'trending': {
            'up': len(trending_up),
            'down': len(trending_down),
            'top_trending': sorted(trending_up, key=lambda x: x['monthly_trend'], reverse=True)[:5]
        },
        
        'all_keywords': keyword_list
    }

def generate_insights(analysis: dict) -> dict:
    """Generate narrative insights"""
    total = analysis.get('total_keywords', 0)
    est_traffic = analysis.get('estimated_monthly_traffic', 0)
    ranking = analysis.get('ranking_distribution', {})
    sources = analysis.get('traffic_sources', {})
    types = analysis.get('keyword_types', {})
    opportunities = analysis.get('opportunity_keywords', [])
    
    # Traffic assessment
    if est_traffic > 50000:
        traffic_level = 'HIGH'
        traffic_emoji = '🔥'
    elif est_traffic > 10000:
        traffic_level = 'MEDIUM'
        traffic_emoji = '📈'
    else:
        traffic_level = 'LOW'
        traffic_emoji = '📉'
    
    # Summary
    summary = f"{traffic_emoji} Est. {est_traffic:,} monthly traffic from {total} keywords. "
    summary += f"Top 10 rankings: {ranking.get('top_10', 0)}. "
    summary += f"Organic: {sources.get('organic_pct', 0)}%."
    
    # Assessments
    assessments = []
    
    if ranking.get('top_10', 0) > 10:
        assessments.append(f"Strong rankings: {ranking['top_10']} keywords in top 10")
    elif ranking.get('top_10', 0) < 3:
        assessments.append(f"Weak rankings: Only {ranking['top_10']} keywords in top 10")
    
    if types.get('BRAND', 0) > total * 0.3:
        assessments.append(f"Brand-dependent: {types['BRAND']} brand keywords ({round(types['BRAND']/total*100)}%)")
    
    if types.get('GENERIC', 0) > total * 0.4:
        assessments.append(f"Good generic reach: {types['GENERIC']} generic keywords")
    
    if sources.get('both', 0) > total * 0.2:
        assessments.append(f"Heavy PPC investment: {sources['both']} keywords with both organic + ads")
    
    # Recommendations
    recommendations = []
    
    if opportunities:
        top_opp = opportunities[0]
        recommendations.append(f"💡 Target '{top_opp['keyword']}' — {top_opp['search_volume_exact']:,}/mo, Ease: {top_opp['ease_of_ranking']}")
    
    if types.get('LONG_TAIL', 0) < total * 0.2:
        recommendations.append("Consider more long-tail keywords for easier ranking")
    
    if sources.get('organic_pct', 0) > 90:
        recommendations.append("Competitor relies on organic — vulnerable to PPC attack")
    elif sources.get('organic_pct', 0) < 50:
        recommendations.append("Competitor heavily PPC-dependent — may have weak organic")
    
    return {
        'summary': summary,
        'traffic_level': traffic_level,
        'assessments': assessments,
        'recommendations': recommendations
    }

def compare_asins(all_keywords: List[dict], asins: List[str]) -> dict:
    """Compare keyword overlap between ASINs"""
    asin_keywords = {}
    
    for asin in asins:
        kws = set()
        for kw in all_keywords:
            attr = kw.get('attributes', {})
            if attr.get('primary_asin') == asin:
                kws.add(attr.get('name', ''))
        asin_keywords[asin] = kws
    
    # Find overlaps
    if len(asins) >= 2:
        overlap = asin_keywords[asins[0]].intersection(asin_keywords[asins[1]])
        unique_a = asin_keywords[asins[0]] - asin_keywords[asins[1]]
        unique_b = asin_keywords[asins[1]] - asin_keywords[asins[0]]
        
        return {
            'overlap_count': len(overlap),
            'overlap_keywords': list(overlap)[:20],
            f'{asins[0]}_unique': len(unique_a),
            f'{asins[1]}_unique': len(unique_b),
            'unique_samples': {
                asins[0]: list(unique_a)[:10],
                asins[1]: list(unique_b)[:10]
            }
        }
    
    return {}

# === Main Analysis Function ===

def reverse_lookup(asins: List[str], market: str = 'US') -> dict:
    """Main reverse lookup function"""
    market_code = MARKET_MAP.get(market, 'us')
    
    print(f"Reverse lookup for: {', '.join(asins)}", file=sys.stderr)
    print("[1/2] Fetching keywords via proxy...", file=sys.stderr)
    
    keywords_data = get_keywords_by_asin(asins, market_code, min_volume=100)
    
    if not keywords_data:
        return {'error': 'Failed to fetch keyword data', 'asins': asins}
    
    print(f"  ✓ Got {len(keywords_data)} keywords", file=sys.stderr)
    
    print("[2/2] Analyzing keyword patterns...", file=sys.stderr)
    
    result = {
        'asins': asins,
        'marketplace': market,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'total_keywords_found': len(keywords_data)
    }
    
    # Analyze each ASIN
    asin_analyses = {}
    for asin in asins:
        analysis = analyze_keywords(keywords_data, asin)
        insights = generate_insights(analysis)
        analysis['insights'] = insights
        asin_analyses[asin] = analysis
    
    result['asin_analyses'] = asin_analyses
    
    # If multiple ASINs, compare
    if len(asins) > 1:
        result['comparison'] = compare_asins(keywords_data, asins)
    
    # Primary ASIN summary (first one)
    primary = asin_analyses.get(asins[0], {})
    result['summary'] = {
        'primary_asin': asins[0],
        'total_keywords': primary.get('total_keywords', 0),
        'estimated_traffic': primary.get('estimated_monthly_traffic', 0),
        'top_10_rankings': (primary.get('ranking_distribution') or {}).get('top_10', 0),
        'organic_pct': (primary.get('traffic_sources') or {}).get('organic_pct', 0),
        'top_keywords': [k['keyword'] for k in primary.get('top_keywords', [])[:5]],
        'insights': (primary.get('insights') or {}).get('summary', '')
    }
    
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
    
    GOOD = get_color('good')
    NEUTRAL = get_color('muted')
    WARNING = get_color('secondary')
    BAD = get_color('hot')
    BLUE = get_color('primary')
    
    primary_asin = result.get('asins', [''])[0]
    analysis = (result.get('asin_analyses') or {}).get(primary_asin, {})
    
    if not analysis or 'error' in analysis:
        return []
    
    # Chart 1: Keyword Type Distribution (Pie)
    types = analysis.get('keyword_types', {})
    if types:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Brand', 'Generic', 'Long-tail']
        sizes = [types.get('BRAND', 0), types.get('GENERIC', 0), types.get('LONG_TAIL', 0)]
        colors = [WARNING, BLUE, GOOD]
        explode = (0.05, 0.05, 0.05)
        
        if sum(sizes) > 0:
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=False, startangle=90, textprops={'fontsize': 11})
            ax.set_title('KEYWORD TYPE DISTRIBUTION', fontweight='bold', fontsize=12, pad=15)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/1_keyword_types.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 1: Keyword Types", file=sys.stderr)
    
    # Chart 2: Ranking Distribution (Bar)
    ranking = analysis.get('ranking_distribution', {})
    if ranking:
        categories = ['Top 10', 'Top 11-20', 'Top 21-50', 'Below 50']
        values = [
            ranking.get('top_10', 0),
            ranking.get('top_20', 0) - ranking.get('top_10', 0),
            ranking.get('top_50', 0) - ranking.get('top_20', 0),
            ranking.get('below_50', 0)
        ]
        if sum(values) < 1:
            print(f"  ⚠️ 2_ranking_distribution.png skipped: need ≥1 items, got {sum(values)}", file=sys.stderr)
        else:
            fig, ax = plt.subplots(figsize=(10, 5))
            colors_bar = [GOOD, BLUE, WARNING, NEUTRAL]

            bars = ax.bar(categories, values, color=colors_bar, edgecolor='white', linewidth=2)

            for bar, val in zip(bars, values):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                           str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')

            ax.set_ylabel('Number of Keywords', fontsize=10)
            ax.set_title('RANKING POSITION DISTRIBUTION', fontweight='bold', fontsize=12, pad=15)
            ax.set_ylim(0, max(values) * 1.2 if values else 10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            plt.tight_layout()
            plt.savefig(f'{output_dir}/2_ranking_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 2: Ranking Distribution", file=sys.stderr)
    
    # Chart 3: Traffic Sources (Pie)
    sources = analysis.get('traffic_sources', {})
    if sources:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Organic Only', 'Sponsored Only', 'Both']
        sizes = [sources.get('organic_only', 0), sources.get('sponsored_only', 0), sources.get('both', 0)]
        colors = [GOOD, WARNING, BLUE]
        
        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=False, startangle=90, textprops={'fontsize': 11})
            ax.set_title('TRAFFIC SOURCES', fontweight='bold', fontsize=12, pad=15)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/3_traffic_sources.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 3: Traffic Sources", file=sys.stderr)
    
    # Chart 4: Top Keywords Bar
    top_kws = analysis.get('top_keywords', [])[:10]
    if top_kws:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        keywords = [k['keyword'][:25] + '...' if len(k['keyword']) > 25 else k['keyword'] 
                    for k in top_kws]
        volumes = [k['search_volume_exact'] for k in top_kws]
        
        y_pos = np.arange(len(keywords))
        bars = ax.barh(y_pos, volumes, color=BLUE, edgecolor='white', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(keywords, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Monthly Search Volume', fontsize=10)
        ax.set_title('TOP TRAFFIC KEYWORDS', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add rank labels
        for i, (bar, kw) in enumerate(zip(bars, top_kws)):
            rank = kw.get('organic_rank', '-')
            ax.text(bar.get_width() + max(volumes)*0.02, bar.get_y() + bar.get_height()/2,
                   f'Rank #{rank}', va='center', fontsize=9, color='gray')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_top_keywords.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Top Keywords", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    if len(sys.argv) < 2:
        print('Usage: python3 keyword_reverse_lookup.py \'{"asin": "B07RL88DD2"}\' [--chart <dir>]', file=sys.stderr)
        sys.exit(1)
    
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(f"Invalid JSON: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    
    # Support both single asin and list
    if 'asin' in params:
        asins = [params['asin']]
    elif 'asins' in params:
        asins = params['asins']
    else:
        print("Missing required parameter: asin or asins", file=sys.stderr)
        sys.exit(1)
    
    market = params.get('market', 'US')
    
    chart_dir = None
    if '--chart' in sys.argv:
        chart_idx = sys.argv.index('--chart')
        if chart_idx + 1 < len(sys.argv):
            chart_dir = sys.argv[chart_idx + 1]
    
    result = reverse_lookup(asins, market)
    
    if chart_dir and 'error' not in result:
        print(f"Generating charts in {chart_dir}...", file=sys.stderr)
        result['charts'] = generate_charts(result, chart_dir) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
