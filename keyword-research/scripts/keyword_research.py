#!/usr/bin/env python3
"""
Keyword Research v1.1.0

Discover and expand keyword opportunities from a seed keyword.

Data Source:
- Keywords API: keywords_by_keyword_query (via NexScope proxy)

Changes in v1.1.0:

Usage:
    python3 keyword_research.py '{"keyword": "face wash"}'
    python3 keyword_research.py '{"keyword": "yoga mat", "min_volume": 1000}'
"""

import json
import sys
import os
import argparse
from datetime import datetime
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

MARKET_MAP = {'US': 'us', 'UK': 'uk', 'DE': 'de', 'FR': 'fr', 'CA': 'ca', 'JP': 'jp'}

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

# === API Functions ===

def get_related_keywords(seed_keyword: str, market: str = 'us', 
                         min_volume: int = 100) -> Optional[List[dict]]:
    """Get related keywords for a seed keyword"""
    
    # Fallback: direct API call
    payload = {
        "data": {
            "type": "keywords_by_keyword_query",
            "attributes": {
                "search_terms": seed_keyword,
                "min_monthly_search_volume_exact": min_volume
            }
        }
    }
    
    return _js_api_call('/keywords/keywords_by_keyword_query', payload, market)

def _js_api_call(endpoint: str, payload: dict, market: str = 'us') -> Optional[List[dict]]:
    """Fallback API call (when shared module not available)"""
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
    # Convert payload → flat proxy format
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
        return [{'attributes': {_c2s(k): v for k, v in item.items()}} for item in items]
    except Exception as e:
        print(f"Proxy API Error [{endpoint}]: {e}", file=sys.stderr)
        return None

# === Analysis Functions ===

def classify_keyword(keyword: str, seed: str) -> str:
    """Classify keyword relationship to seed"""
    kw_lower = keyword.lower()
    seed_lower = seed.lower()
    seed_words = set(seed_lower.split())
    kw_words = set(kw_lower.split())
    
    # Exact match
    if kw_lower == seed_lower:
        return 'SEED'
    
    # Contains all seed words
    if seed_words.issubset(kw_words):
        return 'EXPANSION'
    
    # Contains some seed words
    if seed_words & kw_words:
        return 'RELATED'
    
    return 'ADJACENT'

def normalize_trend(value) -> str:
    """Convert float monthly_trend to categorical string"""
    if isinstance(value, (int, float)):
        if value > 5:
            return 'GROWING'
        elif value < -5:
            return 'DECLINING'
        else:
            return 'FLAT'
    return value if value in ('GROWING', 'FLAT', 'DECLINING') else 'FLAT'

def categorize_opportunity(attrs: dict) -> dict:
    """Categorize keyword opportunity"""
    volume = int(attrs.get('monthly_search_volume_exact', 0) or 0)
    trend = normalize_trend(attrs.get('monthly_trend', 0))

    # Use API-provided ease_of_ranking_score (0-100, higher = easier)
    ease = int(attrs.get('ease_of_ranking_score', 50) or 50)

    if ease >= 70:
        difficulty = 'EASY'
    elif ease >= 40:
        difficulty = 'MEDIUM'
    else:
        difficulty = 'HARD'

    # Opportunity score
    volume_score = min(100, volume / 1000)  # Normalize to 100
    trend_bonus = 20 if trend == 'GROWING' else 0

    opportunity_score = (volume_score * 0.5) + (ease * 0.3) + trend_bonus

    # Categorize
    if opportunity_score > 70 and trend == 'GROWING':
        category = '🔥 Hot Opportunity'
    elif difficulty == 'EASY' and volume > 5000:
        category = '💎 Hidden Gem'
    elif trend == 'GROWING':
        category = '📈 Rising Star'
    elif difficulty == 'HARD' and volume > 50000:
        category = '⚠️ Competitive'
    elif trend == 'DECLINING':
        category = '📉 Declining'
    else:
        category = '📊 Standard'

    return {
        'difficulty': difficulty,
        'ease_of_ranking': ease,
        'opportunity_score': round(opportunity_score, 1),
        'category': category
    }

def analyze_keywords(keywords: List[dict], seed: str) -> dict:
    """Analyze keyword list"""
    if not keywords:
        return {'error': 'No keywords to analyze'}
    
    analysis = {
        'total': len(keywords),
        'by_relationship': {'SEED': 0, 'EXPANSION': 0, 'RELATED': 0, 'ADJACENT': 0},
        'by_category': {},
        'by_trend': {'GROWING': 0, 'FLAT': 0, 'DECLINING': 0},
        'volume_stats': {'total': 0, 'avg': 0, 'max': 0},
        'top_keywords': []
    }
    
    volumes = []
    
    for item in keywords:
        attrs = item.get('attributes', {})
        keyword = attrs.get('name', '')
        volume = int(attrs.get('monthly_search_volume_exact', 0) or 0)
        trend = normalize_trend(attrs.get('monthly_trend', 0))

        # Relationship
        rel = classify_keyword(keyword, seed)
        analysis['by_relationship'][rel] += 1

        # Trend
        analysis['by_trend'][trend] = analysis['by_trend'].get(trend, 0) + 1
        
        # Category
        opp = categorize_opportunity(attrs)
        cat = opp['category']
        analysis['by_category'][cat] = analysis['by_category'].get(cat, 0) + 1
        
        # Volume
        if volume > 0:
            volumes.append(volume)
        
        # Top keywords (by opportunity score)
        analysis['top_keywords'].append({
            'keyword': keyword,
            'monthly_volume': volume,
            'trend': trend,
            'relationship': rel,
            'category': opp['category'],
            'opportunity_score': opp['opportunity_score']
        })
    
    # Volume stats
    if volumes:
        analysis['volume_stats'] = {
            'total': sum(volumes),
            'avg': int(sum(volumes) / len(volumes)),
            'max': max(volumes)
        }
    
    # Sort top keywords by opportunity score
    analysis['top_keywords'].sort(key=lambda x: -x['opportunity_score'])
    analysis['top_keywords'] = analysis['top_keywords'][:15]
    
    return analysis

def generate_insights(analysis: dict, seed: str) -> dict:
    """Generate insights from analysis"""
    total = analysis.get('total', 0)
    by_rel = analysis.get('by_relationship', {})
    by_trend = analysis.get('by_trend', {})
    by_cat = analysis.get('by_category', {})
    
    insights = []
    
    # Expansion potential
    expansions = by_rel.get('EXPANSION', 0)
    if expansions > 10:
        insights.append(f"✅ Strong expansion potential: {expansions} keywords contain '{seed}'")
    
    # Growth trend
    growing = by_trend.get('GROWING', 0)
    if growing > total * 0.2:
        insights.append(f"📈 {growing} keywords ({growing/total*100:.0f}%) are growing")
    
    # Hot opportunities
    hot = by_cat.get('🔥 Hot Opportunity', 0)
    if hot > 0:
        insights.append(f"🔥 {hot} hot opportunities identified")
    
    # Hidden gems
    gems = by_cat.get('💎 Hidden Gem', 0)
    if gems > 0:
        insights.append(f"💎 {gems} hidden gems (low competition, decent volume)")
    
    # Volume
    vol_stats = analysis.get('volume_stats', {})
    total_vol = vol_stats.get('total', 0)
    if total_vol > 100000:
        insights.append(f"📊 Total addressable volume: {total_vol:,}/month")
    
    return {
        'summary': f"Found {total} related keywords for '{seed}'",
        'insights': insights[:5]
    }

# === Chart Generation ===

def generate_charts(analysis: dict, seed: str, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
    except ImportError:
        print("matplotlib not available", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    BLUE = get_color('primary')
    GREEN = get_color('good')
    ORANGE = get_color('secondary')
    RED = get_color('hot')
    GOLD = '#FFD700'
    
    # Chart 1: Keyword Relationship
    by_rel = analysis.get('by_relationship', {})
    if by_rel:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['Expansion', 'Related', 'Adjacent']
        values = [by_rel.get('EXPANSION', 0), by_rel.get('RELATED', 0), by_rel.get('ADJACENT', 0)]
        colors = [GREEN, BLUE, ORANGE]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Keywords', fontsize=11)
        ax.set_title(f'KEYWORD RELATIONSHIPS: "{seed[:20]}"', fontweight='bold', fontsize=12)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_opportunity_matrix.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print("  ✓ Chart 1: Opportunity Matrix", file=sys.stderr)
    
    # Chart 2: Trend Distribution
    by_trend = analysis.get('by_trend', {})
    if by_trend:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['Growing', 'Flat', 'Declining']
        values = [by_trend.get('GROWING', 0), by_trend.get('FLAT', 0), by_trend.get('DECLINING', 0)]
        colors = [GREEN, BLUE, RED]
        
        non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
        if non_zero:
            labels, values, colors = zip(*non_zero)
            
            ax.pie(values, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
            ax.set_title(f'TREND DISTRIBUTION', fontweight='bold', fontsize=12)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/2_category_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print("  ✓ Chart 2: Category Distribution", file=sys.stderr)
    
    # Chart 3: Top Keywords by Opportunity
    top_kws = analysis.get('top_keywords', [])[:10]
    if top_kws:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        keywords = [k['keyword'][:25] + '...' if len(k['keyword']) > 25 else k['keyword'] for k in top_kws]
        scores = [k['opportunity_score'] for k in top_kws]
        
        colors = [GREEN if s > 70 else BLUE if s > 50 else ORANGE for s in scores]
        
        bars = ax.barh(keywords, scores, color=colors, edgecolor='white', linewidth=2)
        
        for bar, score in zip(bars, scores):
            ax.text(score + 1, bar.get_y() + bar.get_height()/2,
                   f'{score:.0f}', va='center', fontsize=9)
        
        ax.set_xlabel('Opportunity Score', fontsize=11)
        ax.set_title('TOP KEYWORD OPPORTUNITIES', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_volume_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print("  ✓ Chart 3: Volume Distribution", file=sys.stderr)

    # Chart 4: Top Opportunities ranked bar
    top_kws = analysis.get('top_keywords', [])[:10]
    if top_kws:
        fig, ax = plt.subplots(figsize=(12, 6))

        keywords = [k['keyword'][:25] + '...' if len(k['keyword']) > 25 else k['keyword'] for k in top_kws]
        scores = [k['opportunity_score'] for k in top_kws]

        colors = [GREEN if s > 70 else BLUE if s > 50 else ORANGE for s in scores]

        bars = ax.barh(keywords, scores, color=colors, edgecolor='white', linewidth=2)

        for bar, score in zip(bars, scores):
            ax.text(score + 1, bar.get_y() + bar.get_height()/2,
                   f'{score:.0f}', va='center', fontsize=9)

        ax.set_xlabel('Opportunity Score', fontsize=11)
        ax.set_title(f'TOP OPPORTUNITIES: "{seed[:20]}"', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 110)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_top_opportunities.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print("  ✓ Chart 4: Top Opportunities", file=sys.stderr)

# === Main Function ===
    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

def research_keywords(keyword: str, market: str = 'us', min_volume: int = 100) -> dict:
    """Main function to research keywords"""
    
    market = market.lower()
    if market not in MARKET_MAP.values():
        market = MARKET_MAP.get(market.upper(), 'us')
    
    result = {
        'seed_keyword': keyword,
        'marketplace': market.upper(),
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.1.0',
        'data_source': 'NexScope',
        'using_shared_api': False
    }
    
    # Get keywords
    print(f"[1/2] Fetching keywords for '{keyword}'...", file=sys.stderr)
    keywords = get_related_keywords(keyword, market, min_volume)
    
    if not keywords:
        result['error'] = 'No keywords found'
        return result
    
    print(f"    ✓ Found {len(keywords)} keywords", file=sys.stderr)
    
    # Analyze
    print(f"[2/2] Analyzing keywords...", file=sys.stderr)
    analysis = analyze_keywords(keywords, keyword)
    result['analysis'] = analysis
    
    # Insights
    insights = generate_insights(analysis, keyword)
    result['insights'] = insights
    
    # Cache stats (if using shared API)
    return result

# === CLI Entry Point ===

def main():
    parser = argparse.ArgumentParser(description='Keyword Research v1.1.0')
    parser.add_argument('params', nargs='?', default='{}', help='JSON parameters')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    parser.add_argument('--output', type=str, help='Save raw JSON result to file path for later merging')
    parser.add_argument('--merge', nargs='+', type=str, help='Merge batch JSON files and generate unified charts')
    parser.add_argument('--sort', default='score', choices=['score', 'sales', 'growth'], help='Sort key for --merge output')
    
    args = parser.parse_args()

    if args.merge:
        result = merge_and_chart(args.merge, sort_key=args.sort, chart_dir=args.chart)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    if not keyword:
        print("Missing required parameter: keyword", file=sys.stderr)
        sys.exit(1)
    
    result = research_keywords(
        keyword=keyword,
        market=params.get('market', 'us'),
        min_volume=params.get('min_volume', 100)
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result.get('analysis', {}), keyword, args.chart) or []

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
