#!/usr/bin/env python3
"""
Keyword Rank Tracker v2.0.0

Track and analyze keyword rankings for Amazon products.
Data Source: Keywords API (via NexScope proxy)

Features:
- Track all keywords an ASIN ranks for
- Analyze organic vs sponsored positions
- Identify high-value keywords (high search, good rank)
- Find ranking opportunities (high search, low rank)
- Compare keyword positions across rank tiers

Usage:
    python3 keyword_rank_tracker.py '{"asin": "B0BTYCRJSS"}'
    python3 keyword_rank_tracker.py '{"asin": "B0BTYCRJSS", "market": "us"}'
    python3 keyword_rank_tracker.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Optional, List, Tuple
from urllib.request import Request, urlopen
import statistics

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

_PROXY_ENDPOINTS = {
    '/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
    '/keywords/keywords_by_asin_query': '/keywords/by-asin',
}
_PROXY_LIST_FIELDS = {
    '/keywords/by-keyword': 'keywordInfoList',
    '/keywords/by-asin': 'keywordInfoList',
}

# Supported markets
SUPPORTED_MARKETS = ['us', 'uk', 'de', 'fr', 'it', 'es', 'ca', 'mx', 'jp', 'in']

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
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
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

def get_keywords_by_asin(asin: str, market: str = 'us', min_volume: int = 100) -> dict:
    """Get all keywords for an ASIN via proxy"""
    payload = {
        "data": {
            "type": "keywords_by_asin_query",
            "attributes": {
                "asins": asin,
                "include_variants": False,
                "min_monthly_search_volume_exact": min_volume
            }
        }
    }
    
    result = js_api_call('/keywords/keywords_by_asin_query', payload, market)
    
    if result and 'data' in result:
        return {
            'keywords': result['data'],
            'total': len(result['data'])
        }
    return {'error': 'No response', 'keywords': []}

# === Analysis Functions ===

def classify_rank(rank: int) -> Tuple[str, str]:
    """Classify rank into tier"""
    if rank is None or rank <= 0:
        return 'unranked', '⚪ Unranked'
    elif rank <= 3:
        return 'top3', '🥇 Top 3'
    elif rank <= 10:
        return 'page1', '🟢 Page 1'
    elif rank <= 20:
        return 'page2', '🟡 Page 2'
    elif rank <= 50:
        return 'page3_5', '🟠 Page 3-5'
    else:
        return 'beyond', '🔴 Beyond P5'

def classify_keyword_type(keyword: str) -> str:
    """Classify keyword type"""
    keyword_lower = keyword.lower()
    words = keyword_lower.split()
    
    # Long-tail (4+ words)
    if len(words) >= 4:
        return 'LONG_TAIL'
    
    # Generic (1-3 words)
    return 'GENERIC'

def analyze_keywords(keywords_data: List[dict], asin: str) -> dict:
    """Analyze keyword portfolio data"""
    if not keywords_data:
        return {'error': 'No keywords to analyze'}
    
    total_keywords = len(keywords_data)
    
    # Rank distribution
    rank_tiers = {'top3': 0, 'page1': 0, 'page2': 0, 'page3_5': 0, 'beyond': 0, 'unranked': 0}
    
    # Search volume stats
    search_volumes = []
    top_traffic_keywords = []
    
    # Position type distribution
    organic_count = 0
    sponsored_count = 0
    
    # Keyword type distribution
    keyword_types = {'GENERIC': 0, 'LONG_TAIL': 0}
    
    for item in keywords_data:
        attrs = item.get('attributes', {})
        keyword = attrs.get('name', '')
        
        # Get rank for the target ASIN directly from API fields
        _orank = attrs.get('organic_rank')
        organic_rank = int(_orank) if _orank is not None else None
        sponsored_rank = int(attrs.get('sponsored_ranking_asins_count') or 0) > 0

        # Use organic rank for position (sponsored has no specific rank number)
        rank = organic_rank if (organic_rank is not None and organic_rank > 0) else None

        # Rank tier
        tier, _ = classify_rank(rank)
        rank_tiers[tier] += 1

        # Position counts
        if organic_rank is not None and organic_rank > 0:
            organic_count += 1
        if sponsored_rank:
            sponsored_count += 1
        
        # Search volume
        monthly_volume = int(attrs.get('monthly_search_volume_exact', 0) or 0)
        if monthly_volume and monthly_volume > 0:
            search_volumes.append(monthly_volume)
        
        # Top traffic keywords (estimate traffic share based on rank and volume)
        if rank is not None and rank > 0 and rank <= 50 and monthly_volume > 0:
            # Estimate traffic share based on position
            ctr_estimate = max(0.01, 0.30 - (rank - 1) * 0.02)  # Rough CTR curve
            estimated_traffic = int(monthly_volume * ctr_estimate)
            
            top_traffic_keywords.append({
                'keyword': keyword,
                'organic_rank': organic_rank,
                'sponsored_rank': sponsored_rank,
                'monthly_search': monthly_volume,
                'estimated_traffic': estimated_traffic,
                'trend': attrs.get('monthly_trend', 'FLAT')
            })
        
        # Keyword type
        kw_type = classify_keyword_type(keyword)
        keyword_types[kw_type] += 1
    
    # Sort top traffic keywords by estimated traffic
    top_traffic_keywords.sort(key=lambda x: -x['estimated_traffic'])
    
    # Calculate totals
    total_monthly_volume = sum(search_volumes)
    total_estimated_traffic = sum(k['estimated_traffic'] for k in top_traffic_keywords)
    
    return {
        'total_keywords': total_keywords,
        'rank_distribution': rank_tiers,
        'position_types': {
            'organic': organic_count,
            'sponsored': sponsored_count,
            'both': min(organic_count, sponsored_count)
        },
        'keyword_types': keyword_types,
        'top_traffic_keywords': top_traffic_keywords[:10],
        'search_volume_stats': {
            'total_monthly': total_monthly_volume,
            'avg_monthly': int(statistics.mean(search_volumes)) if search_volumes else 0,
            'max_monthly': max(search_volumes) if search_volumes else 0
        },
        'estimated_total_traffic': total_estimated_traffic
    }

def find_opportunities(keywords_data: List[dict], asin: str) -> dict:
    """Find ranking opportunities"""
    opportunities = {
        'high_potential': [],  # High search, low rank
        'quick_wins': [],      # Close to page 1
        'defend': [],          # Top 3 positions to defend
        'trending': []         # Trending keywords
    }
    
    for item in keywords_data:
        attrs = item.get('attributes', {})
        keyword = attrs.get('name', '')
        monthly_volume = int(attrs.get('monthly_search_volume_exact', 0) or 0)
        _trend_raw = attrs.get('monthly_trend', 0)
        if isinstance(_trend_raw, (int, float)):
            trend = 'GROWING' if _trend_raw > 5 else ('DECLINING' if _trend_raw < -5 else 'FLAT')
        else:
            trend = _trend_raw if _trend_raw in ('GROWING', 'FLAT', 'DECLINING') else 'FLAT'

        # Get rank directly from API field
        _orank = attrs.get('organic_rank')
        organic_rank = int(_orank) if _orank is not None else None

        rank = (organic_rank if (organic_rank is not None and organic_rank > 0) else None) or 999
        
        # High potential: high search volume but not on page 1
        if monthly_volume > 50000 and rank > 10:
            opportunities['high_potential'].append({
                'keyword': keyword,
                'monthly_search': monthly_volume,
                'current_rank': rank if rank < 999 else 'N/A',
                'potential': 'HIGH' if monthly_volume > 100000 else 'MEDIUM'
            })
        
        # Quick wins: ranks 11-20 (close to page 1)
        if 11 <= rank <= 20 and monthly_volume > 10000:
            opportunities['quick_wins'].append({
                'keyword': keyword,
                'current_rank': rank,
                'monthly_search': monthly_volume,
                'positions_to_page1': rank - 10
            })
        
        # Defend: top 3 with high volume
        if rank <= 3 and monthly_volume > 30000:
            opportunities['defend'].append({
                'keyword': keyword,
                'current_rank': rank,
                'monthly_search': monthly_volume
            })
        
        # Trending keywords
        if trend == 'GROWING' and monthly_volume > 5000:
            opportunities['trending'].append({
                'keyword': keyword,
                'monthly_search': monthly_volume,
                'current_rank': rank if rank < 999 else 'N/A',
                'trend': '📈 GROWING'
            })
    
    # Sort by search volume and limit
    for key in opportunities:
        opportunities[key].sort(key=lambda x: -(x.get('monthly_search', 0)))
        opportunities[key] = opportunities[key][:5]
    
    return opportunities

def generate_insights(analysis: dict, opportunities: dict) -> dict:
    """Generate narrative insights"""
    total = analysis.get('total_keywords', 0)
    rank_dist = analysis.get('rank_distribution', {})
    
    # Summary
    page1_count = rank_dist.get('top3', 0) + rank_dist.get('page1', 0)
    page1_pct = (page1_count / total * 100) if total > 0 else 0
    
    summary = f"Tracking {total} keywords. "
    summary += f"{page1_count} ({page1_pct:.0f}%) on Page 1. "
    
    est_traffic = analysis.get('estimated_total_traffic', 0)
    summary += f"Est. monthly traffic: {est_traffic:,}"
    
    # Recommendations
    recommendations = []
    
    # Based on opportunities
    high_potential = opportunities.get('high_potential', [])
    if high_potential:
        top_opp = high_potential[0]
        recommendations.append(
            f"🎯 **High potential**: '{top_opp['keyword'][:30]}...' ({top_opp['monthly_search']:,}/mo) - "
            f"currently rank {top_opp['current_rank']}"
        )
    
    quick_wins = opportunities.get('quick_wins', [])
    if quick_wins:
        recommendations.append(
            f"⚡ **Quick win**: {len(quick_wins)} keywords close to Page 1"
        )
    
    defend = opportunities.get('defend', [])
    if defend:
        recommendations.append(
            f"🛡️ **Defend**: {len(defend)} top-3 positions driving significant traffic"
        )
    
    trending = opportunities.get('trending', [])
    if trending:
        recommendations.append(
            f"📈 **Trending**: {len(trending)} keywords showing growth"
        )
    
    # Position insights
    pos_types = analysis.get('position_types', {})
    organic = pos_types.get('organic', 0)
    sponsored = pos_types.get('sponsored', 0)
    
    if organic > 0:
        recommendations.append(
            f"🔵 Organic ranking on {organic} keywords"
        )
    
    if sponsored > 0:
        recommendations.append(
            f"🟢 Sponsored ads on {sponsored} keywords"
        )
    
    return {
        'summary': summary,
        'page1_percentage': f"{page1_pct:.1f}%",
        'recommendations': recommendations[:6]
    }

# === Main Function ===

def track_keyword_ranks(
    asin: str,
    market: str = 'us',
    min_volume: int = 100
) -> dict:
    """Main function to track keyword rankings"""
    
    market = market.lower()
    if market not in SUPPORTED_MARKETS:
        return {'error': f'Market {market} not supported. Use: {", ".join(SUPPORTED_MARKETS)}'}
    
    result = {
        'asin': asin,
        'marketplace': market.upper(),
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v2.0.0',
        'data_source': 'NexScope'
    }
    
    # Step 1: Get keywords
    print(f"[1/3] Fetching keywords for ASIN {asin}...", file=sys.stderr)
    kw_result = get_keywords_by_asin(asin, market, min_volume)
    
    if 'error' in kw_result:
        result['error'] = kw_result['error']
        return result
    
    keywords_data = kw_result.get('keywords', [])
    result['total_keywords'] = kw_result.get('total', len(keywords_data))
    
    if not keywords_data:
        result['error'] = 'No keywords found for this ASIN'
        return result
    
    print(f"    ✓ Found {len(keywords_data)} keywords", file=sys.stderr)
    
    # Step 2: Analyze keywords
    print(f"[2/3] Analyzing keyword portfolio...", file=sys.stderr)
    analysis = analyze_keywords(keywords_data, asin)
    result['analysis'] = analysis
    
    # Step 3: Find opportunities
    print(f"[3/3] Identifying opportunities...", file=sys.stderr)
    opportunities = find_opportunities(keywords_data, asin)
    result['opportunities'] = opportunities
    
    # Generate insights
    insights = generate_insights(analysis, opportunities)
    result['insights'] = insights
    
    # Top keywords table
    result['top_keywords'] = []
    for item in keywords_data[:15]:
        attrs = item.get('attributes', {})
        keyword = attrs.get('name', '')
        
        # Get ranks directly from API fields
        _orank = attrs.get('organic_rank')
        organic_rank = int(_orank) if _orank is not None else None
        sponsored_rank = int(attrs.get('sponsored_ranking_asins_count') or 0) > 0

        rank = organic_rank if (organic_rank is not None and organic_rank > 0) else None
        
        result['top_keywords'].append({
            'keyword': keyword,
            'organic_rank': organic_rank,
            'sponsored_rank': sponsored_rank,
            'monthly_search': attrs.get('monthly_search_volume_exact', 0),
            'trend': attrs.get('monthly_trend', 'FLAT'),
            'rank_tier': classify_rank(rank)[1]
        })
    
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
    GOLD = '#FFD700'
    
    asin = result.get('asin', 'Unknown')[:15]
    analysis = result.get('analysis', {})
    
    # Chart 1: Rank Distribution
    rank_dist = analysis.get('rank_distribution', {})
    if rank_dist:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        labels = ['Top 3', 'Page 1\n(4-10)', 'Page 2\n(11-20)', 'Page 3-5\n(21-50)', 'Beyond\nP5', 'Unranked']
        values = [
            rank_dist.get('top3', 0),
            rank_dist.get('page1', 0),
            rank_dist.get('page2', 0),
            rank_dist.get('page3_5', 0),
            rank_dist.get('beyond', 0),
            rank_dist.get('unranked', 0)
        ]
        colors = [GOLD, GREEN, BLUE, ORANGE, RED, get_color('muted')]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Keywords', fontsize=11)
        ax.set_title(f'KEYWORD RANK DISTRIBUTION: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_rank_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Rank Distribution", file=sys.stderr)
    
    # Chart 2: Top Traffic Keywords
    top_traffic = analysis.get('top_traffic_keywords', [])
    if top_traffic:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        keywords = [kw['keyword'][:25] + '...' if len(kw['keyword']) > 25 else kw['keyword'] for kw in top_traffic[:8]]
        traffic = [kw['estimated_traffic'] for kw in top_traffic[:8]]
        
        rank_key = 'organic_rank'
        colors = [GREEN if kw.get(rank_key) and kw[rank_key] <= 10 
                  else ORANGE if kw.get(rank_key) and kw[rank_key] <= 20 
                  else RED for kw in top_traffic[:8]]
        
        bars = ax.barh(keywords, traffic, color=colors, edgecolor='white', linewidth=2)
        
        for bar, t, kw in zip(bars, traffic, top_traffic[:8]):
            rank = kw.get('organic_rank') or kw.get('sponsored_rank') or 'N/A'
            rank_text = f"#{rank}" if isinstance(rank, int) else rank
            ax.text(t + max(traffic)*0.02, bar.get_y() + bar.get_height()/2,
                   f'{t:,} ({rank_text})', va='center', fontsize=9)
        
        ax.set_xlabel('Estimated Monthly Traffic', fontsize=11)
        ax.set_title(f'TOP TRAFFIC KEYWORDS: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_top_traffic.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Top Traffic Keywords", file=sys.stderr)
    
    # Chart 3: Position Type Distribution
    pos_types = analysis.get('position_types', {})
    if pos_types:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['Organic', 'Sponsored']
        values = [pos_types.get('organic', 0), pos_types.get('sponsored', 0)]
        colors = [BLUE, GREEN]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Keywords', fontsize=11)
        ax.set_title(f'POSITION TYPES: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_position_types.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Position Types", file=sys.stderr)
    
    # Chart 4: Keyword Type Distribution
    kw_types = analysis.get('keyword_types', {})
    if kw_types and sum(kw_types.values()) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['Generic\n(1-3 words)', 'Long-tail\n(4+ words)']
        values = [kw_types.get('GENERIC', 0), kw_types.get('LONG_TAIL', 0)]
        colors = [BLUE, GREEN]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Keywords', fontsize=11)
        ax.set_title(f'KEYWORD TYPES: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_keyword_types.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Keyword Types", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Keyword Rank Tracker v2.0.0')
    parser.add_argument('params', nargs='?', help='JSON parameters: {"asin": "B0XXXXXXXX"}')
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
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    asin = params.get('asin')
    if not asin:
        print("Missing required parameter: asin", file=sys.stderr)
        sys.exit(1)
    
    result = track_keyword_ranks(
        asin=asin,
        market=params.get('market', 'us'),
        min_volume=params.get('min_volume', 100)
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
