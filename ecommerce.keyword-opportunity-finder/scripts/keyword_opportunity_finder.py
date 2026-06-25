#!/usr/bin/env python3
"""
Keyword Opportunity Finder - Find blue ocean keywords with scoring.

Usage:
  python3 keyword_opportunity_finder.py '{"keyword": "pet water fountain"}'
  python3 keyword_opportunity_finder.py '{"keyword": "dog toys", "marketplace": "US"}' --chart ./output/

"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request

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

_PROXY_ENDPOINTS = {
    '/api/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
    '/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
    '/api/keywords/historical-search-volume': '/keywords/historical-search-volume',
}

def api_call(endpoint: str, params: dict) -> 'Optional[dict]':
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    if not NEXSCOPE_PROXY_BASE:
        print("Error: NEXSCOPE_PROXY_BASE not configured", file=sys.stderr)
        return None
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    try:
        req = Request(url, data=json.dumps(params).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if isinstance(raw, dict) and raw.get('code') == 0:
            return raw.get('data', raw)
        return raw if isinstance(raw, (list, dict)) else None
    except Exception as e:
        print(f"API error [{endpoint}]: {e}", file=sys.stderr)
        return None

_PROXY_LIST_FIELDS = {
    '/keywords/by-keyword': 'keywordInfoList',
    '/keywords/historical-search-volume': 'historicalSearchVolumeList',
}

def call_js_api(endpoint, params, market='us'):
    """Call Keywords API via NexScope proxy"""
    import re

    if not NEXSCOPE_API_KEY:
        raise RuntimeError("NEXSCOPE_API_KEY not configured")
    if not NEXSCOPE_PROXY_BASE:
        raise RuntimeError("NEXSCOPE_PROXY_BASE not configured")
    proxy_ep = _PROXY_ENDPOINTS.get(endpoint, endpoint)
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout{proxy_ep}"
    headers = {
        'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    # params here is the attributes dict (not wrapped in data.attributes)
    proxy_payload = {'marketplace': market}
    for k, v in params.items():
        parts = k.split('_')
        camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        proxy_payload[camel] = v
    try:
        data = json.dumps(proxy_payload).encode('utf-8')
        req = Request(url, data=data, headers=headers, method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if raw.get('code') != 0:
            raise Exception(f"Proxy error: {raw.get('msg', 'unknown')}")
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
        raise Exception(f"Proxy API Error [{endpoint}]: {e}")

def calculate_keyword_score(kw_data):
    """
    Calculate Keyword Opportunity Score (0-100)
    
    Volume (30) + Difficulty (30) + Efficiency (25) + Relevance (15) = 100
    """
    volume = kw_data.get('exact_volume', 0) or kw_data.get('monthly_search_volume', 0)
    difficulty = kw_data.get('keyword_difficulty', 50)
    cpc = kw_data.get('ppc_bid_exact', 1.0) or 1.0
    
    # Volume Score (0-30)
    if volume >= 50000: vol_score = 30
    elif volume >= 20000: vol_score = 25
    elif volume >= 10000: vol_score = 20
    elif volume >= 5000: vol_score = 15
    elif volume >= 1000: vol_score = 10
    else: vol_score = 5
    
    # Difficulty Score (0-30) - Lower is better
    if difficulty <= 20: diff_score = 30
    elif difficulty <= 35: diff_score = 25
    elif difficulty <= 50: diff_score = 20
    elif difficulty <= 65: diff_score = 15
    elif difficulty <= 80: diff_score = 10
    else: diff_score = 5
    
    # Efficiency Score (0-25) - Volume/Difficulty ratio
    efficiency = volume / (difficulty + 1)
    if efficiency >= 1000: eff_score = 25
    elif efficiency >= 500: eff_score = 20
    elif efficiency >= 200: eff_score = 15
    elif efficiency >= 100: eff_score = 10
    else: eff_score = 5
    
    # Value Score (0-15) - CPC indicates commercial intent
    if cpc >= 3.0: val_score = 15
    elif cpc >= 2.0: val_score = 12
    elif cpc >= 1.0: val_score = 9
    elif cpc >= 0.5: val_score = 6
    else: val_score = 3
    
    total = vol_score + diff_score + eff_score + val_score
    
    return {
        'total_score': total,
        'volume_score': vol_score,
        'difficulty_score': diff_score,
        'efficiency_score': eff_score,
        'value_score': val_score,
        'raw': {
            'volume': volume,
            'difficulty': difficulty,
            'cpc': cpc,
            'efficiency': efficiency
        }
    }

def detect_pattern(kw_data, score_data):
    """Detect keyword opportunity patterns"""
    patterns = []
    
    volume = score_data['raw']['volume']
    difficulty = score_data['raw']['difficulty']
    efficiency = score_data['raw']['efficiency']
    
    # Rising Trend: High 30-day surge
    surge_30d = kw_data.get('monthly_trend', 0)
    if surge_30d > 50:
        patterns.append({
            'pattern': 'Rising Trend',
            'emoji': '📈',
            'detail': f'+{surge_30d}% in 30 days'
        })
    
    # Blue Ocean: High volume, low competition
    if volume >= 10000 and difficulty <= 35:
        patterns.append({
            'pattern': 'Blue Ocean',
            'emoji': '🌊',
            'detail': f'Volume {volume:,}, Difficulty {difficulty}'
        })
    
    # High-Conv Longtail: Lower volume but high efficiency
    if efficiency >= 500 and volume < 10000:
        patterns.append({
            'pattern': 'High-Conv Longtail',
            'emoji': '🎯',
            'detail': f'Efficiency {efficiency:.0f}'
        })
    
    # Under-optimized: Low CPC despite volume
    cpc = score_data['raw']['cpc']
    if volume >= 5000 and cpc < 0.8:
        patterns.append({
            'pattern': 'Under-optimized',
            'emoji': '💎',
            'detail': f'CPC ${cpc:.2f} for {volume:,} volume'
        })
    
    return patterns

# === Chart Analysis ===
def generate_chart_analysis(results):
    """Generate analytical text for each chart"""
    analysis = {}
    keywords = results.get('keywords', [])
    
    if not keywords:
        return analysis
    
    top_kw = sorted(keywords, key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)[:5]
    blue_ocean = [k for k in keywords if k.get('is_blue_ocean')]
    
    # Chart 1: Radar Analysis
    lines = ["**📊 Keyword Radar Analysis:**"]
    if top_kw:
        best = top_kw[0]
        score = best.get('score', {})
        lines.append(f"- Top keyword: **{best['keyword']}** (Score: {score.get('total_score', 0)})")
        
        # Find strongest dimension
        dims = [
            ('Volume', score.get('volume_score', 0), 30),
            ('Low Difficulty', score.get('difficulty_score', 0), 30),
            ('Efficiency', score.get('efficiency_score', 0), 25),
            ('Value', score.get('value_score', 0), 15)
        ]
        strongest = max(dims, key=lambda x: x[1]/x[2])
        weakest = min(dims, key=lambda x: x[1]/x[2])
        lines.append(f"- ✅ Strength: {strongest[0]} ({strongest[1]}/{strongest[2]})")
        lines.append(f"- ⚠️ Weakness: {weakest[0]} ({weakest[1]}/{weakest[2]})")
    analysis['radar'] = "\n".join(lines)
    
    # Chart 2: Score Bar Analysis
    lines = ["**📈 Opportunity Score Analysis:**"]
    lines.append(f"- Total keywords analyzed: {len(keywords)}")
    lines.append(f"- Blue Ocean keywords (70+): {len(blue_ocean)}")
    if blue_ocean:
        lines.append(f"- ✅ Best opportunities: {', '.join([k['keyword'][:20] for k in blue_ocean[:3]])}")
    else:
        lines.append("- ⚠️ No Blue Ocean keywords found - consider broader search")
    analysis['scores'] = "\n".join(lines)
    
    # Chart 3: Volume/Difficulty Scatter Analysis
    lines = ["**🎯 Volume vs Difficulty Analysis:**"]
    low_diff_high_vol = [k for k in keywords 
                         if ((k.get('score') or {}).get('raw') or {}).get('difficulty', 100) < 35 
                         and ((k.get('score') or {}).get('raw') or {}).get('volume', 0) > 5000]
    if low_diff_high_vol:
        lines.append(f"- ✅ Found {len(low_diff_high_vol)} keywords in Blue Ocean zone (low difficulty + high volume)")
        lines.append(f"- Best: **{low_diff_high_vol[0]['keyword']}**")
    else:
        lines.append("- ⚠️ No keywords in ideal Blue Ocean zone")
        lines.append("- Consider targeting moderate difficulty (35-50) keywords")
    analysis['scatter'] = "\n".join(lines)
    
    return analysis

# === Chart Generation ===
def generate_charts(results, output_dir):
    """Generate keyword analysis charts"""
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
    
    keywords = results.get('keywords', [])
    if not keywords:
        return charts
    
    # Chart 1: Keyword Radar (Top 5)
    top_keywords = sorted(keywords, key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)[:5]
    
    if len(top_keywords) >= 3:
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        categories = ['Volume', 'Low Difficulty', 'Efficiency', 'Value']
        num_vars = len(categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        colors = [get_color('primary'), get_color('secondary'), get_color('good'), get_color('secondary'), '#C73E1D']
        
        for i, kw in enumerate(top_keywords):
            score = kw.get('score', {})
            values = [
                score.get('volume_score', 0) / 30 * 100,
                score.get('difficulty_score', 0) / 30 * 100,
                score.get('efficiency_score', 0) / 25 * 100,
                score.get('value_score', 0) / 15 * 100
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=kw['keyword'][:20], color=colors[i])
            ax.fill(angles, values, alpha=0.15, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.set_title('Keyword Comparison Radar', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'keyword_radar.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    
    # Chart 2: Score Breakdown Bar
    if not top_keywords:
        print("  ⚠️ keyword_scores.png skipped: no keyword data", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        kw_names = [k['keyword'][:25] for k in top_keywords[:8]]
        scores = [(k.get('score') or {}).get('total_score', 0) for k in top_keywords[:8]]

        colors = [get_color('good') if s >= 70 else get_color('warning') if s >= 50 else get_color('hot') for s in scores]

        y_pos = np.arange(len(kw_names))
        bars = ax.barh(y_pos, scores, color=colors, height=0.6)

        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 1, i, f'{score}', va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(kw_names)
        ax.set_xlabel('Opportunity Score', fontsize=10)
        ax.set_xlim(0, 110)
        ax.axvline(x=70, color=get_color('good'), linestyle='--', alpha=0.5, label='Blue Ocean (70+)')
        ax.axvline(x=50, color=get_color('warning'), linestyle='--', alpha=0.5, label='Moderate (50+)')
        ax.legend(loc='lower right')
        ax.set_title('Keyword Opportunity Scores', fontsize=14, fontweight='bold', pad=15)

        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'keyword_scores.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    
    # Chart 3: Volume vs Difficulty Scatter
    if len(keywords) >= 3:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        volumes = [((k.get('score') or {}).get('raw') or {}).get('volume', 0) for k in keywords]
        difficulties = [((k.get('score') or {}).get('raw') or {}).get('difficulty', 50) for k in keywords]
        scores = [(k.get('score') or {}).get('total_score', 0) for k in keywords]
        
        scatter = ax.scatter(difficulties, volumes, c=scores, cmap='RdYlGn', s=100, alpha=0.7, edgecolors='white')
        plt.colorbar(scatter, label='Opportunity Score')
        
        # Annotate top 3
        for kw in top_keywords[:3]:
            vol = ((kw.get('score') or {}).get('raw') or {}).get('volume', 0)
            diff = ((kw.get('score') or {}).get('raw') or {}).get('difficulty', 50)
            ax.annotate(kw['keyword'][:15], xy=(diff, vol), xytext=(diff+3, vol*1.1),
                       fontsize=8, color='#333333',
                       arrowprops=dict(arrowstyle='->', color='#333333', alpha=0.5))
        
        # Blue Ocean zone
        ax.axvspan(0, 35, alpha=0.1, color=get_color('good'), label='Low Difficulty Zone')
        ax.axhline(y=10000, color=get_color('warning'), linestyle=':', alpha=0.5, label='High Volume (10K+)')
        
        ax.set_xlabel('Keyword Difficulty', fontsize=10)
        ax.set_ylabel('Monthly Search Volume', fontsize=10)
        ax.set_title('Volume vs Difficulty Analysis\nTop-left = Blue Ocean', fontsize=12, fontweight='bold', pad=15)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'volume_difficulty.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    
    return charts, chart_analysis

def run_finder(params):
    keyword = params.get('keyword', '')
    marketplace = params.get('marketplace', 'us')
    
    if not keyword:
        return {"error": "keyword required"}
    
    results = {
        'seed_keyword': keyword,
        'marketplace': marketplace,
        'keywords': []
    }
    
    # Fetch real keyword data. Do not synthesize mock opportunities on failure.
    try:
        js_data = call_js_api("/api/keywords/keywords_by_keyword_query", {
            "search_terms": keyword,
            "marketplace": marketplace,
            "sort": "-monthly_search_volume_exact",
            "need_count": 20
        })
        
        for item in (js_data or {}).get('data', []):
            attrs = item.get('attributes', {})
            kw_data = {
                'keyword': attrs.get('name', ''),
                'exact_volume': attrs.get('monthly_search_volume_exact', 0),
                'broad_volume': attrs.get('monthly_search_volume_broad', 0),
                'keyword_difficulty': 100 - int(attrs.get('ease_of_ranking_score', 50) or 50),
                'ppc_bid_exact': attrs.get('ppc_bid_exact', 1.0),
                'monthly_trend': attrs.get('monthly_trend', 0),
            }
            
            score = calculate_keyword_score(kw_data)
            patterns = detect_pattern(kw_data, score)

            # Historical search volume for trend direction (POST endpoint)
            kw = attrs.get('name', '')
            hist_data = None
            try:
                _end_dt = datetime.now().strftime('%Y-%m-%d')
                _start_dt = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                _hist_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume"
                _hist_payload = json.dumps({'keyword': kw, 'marketplace': marketplace or 'us', 'startDate': _start_dt, 'endDate': _end_dt}).encode('utf-8')
                _hist_req = Request(_hist_url, data=_hist_payload, headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}', 'Content-Type': 'application/json'}, method='POST')
                with urlopen(_hist_req, timeout=30) as _r:
                    _raw = json.loads(_r.read().decode('utf-8'))
                if isinstance(_raw, dict) and _raw.get('code') == 0:
                    hist_data = _raw.get('data', _raw)
                else:
                    hist_data = _raw
            except Exception as _e:
                print(f"  JS historical error: {_e}", file=sys.stderr)
            hist_list = (hist_data or {}).get('historicalSearchVolumeList', [])
            trend_direction = 'STABLE'
            if len(hist_list) >= 2:
                recent = hist_list[-1].get('estimatedExactSearchVolume', 0) if isinstance(hist_list[-1], dict) else 0
                older = hist_list[0].get('estimatedExactSearchVolume', 0) if isinstance(hist_list[0], dict) else 0
                if older > 0:
                    change_pct = (recent - older) / older * 100
                    if change_pct > 15:
                        trend_direction = 'RISING'
                    elif change_pct < -15:
                        trend_direction = 'DECLINING'
            kw_data['trend_direction'] = trend_direction

            kw_data['score'] = score
            kw_data['patterns'] = patterns
            kw_data['is_blue_ocean'] = score['total_score'] >= 70

            results['keywords'].append(kw_data)
    except Exception as e:
        return {
            "error": "keyword API unavailable",
            "detail": str(e),
            "seed_keyword": keyword,
            "marketplace": marketplace
        }

    if not results['keywords']:
        return {
            "error": "no keyword data returned",
            "detail": "The keyword API returned no related keyword records; no mock data was generated.",
            "seed_keyword": keyword,
            "marketplace": marketplace
        }
    
    # Amazon search enrichment for competition data
    amazon_data = api_call('/amazon/search', {'keyword': keyword, 'amazonDomain': 'amazon.com'})
    amazon_products = (amazon_data or {}).get('products', [])
    competition_count = len(amazon_products)
    avg_price = sum(float(p.get('price') or 0) for p in amazon_products) / max(len(amazon_products), 1)
    results['competition_count'] = competition_count
    results['avg_competitor_price'] = round(avg_price, 2)

    # Sort by score
    results['keywords'].sort(key=lambda x: (x.get('score') or {}).get('total_score', 0), reverse=True)
    
    # Summary
    blue_ocean_count = sum(1 for k in results['keywords'] if k.get('is_blue_ocean'))
    results['summary'] = {
        'total_keywords': len(results['keywords']),
        'blue_ocean_keywords': blue_ocean_count,
        'top_opportunity': results['keywords'][0] if results['keywords'] else None
    }
    
    # Generate insights
    results['insights'] = generate_insights(results)
    
    return results

def generate_insights(results: dict) -> dict:
    """Generate actionable insights from keyword analysis"""
    keywords = results.get('keywords', [])
    if not keywords:
        return {'summary': 'No keywords found', 'recommendations': []}
    
    blue_ocean = [k for k in keywords if k.get('is_blue_ocean')]
    high_volume = [k for k in keywords if k.get('exact_volume', 0) >= 10000]
    low_difficulty = [k for k in keywords if k.get('keyword_difficulty', 100) <= 30]
    trending = [k for k in keywords if k.get('monthly_trend', 0) > 10]
    
    # Summary
    if len(blue_ocean) >= 5:
        summary = f"🔥 Excellent! {len(blue_ocean)} blue ocean keywords found with high opportunity scores."
    elif len(blue_ocean) >= 2:
        summary = f"👍 Good potential! {len(blue_ocean)} blue ocean keywords worth targeting."
    elif low_difficulty:
        summary = f"📊 Moderate market. {len(low_difficulty)} low-difficulty keywords available."
    else:
        summary = f"⚠️ Competitive market. Consider niching down for better opportunities."
    
    # Recommendations
    recommendations = []
    
    if blue_ocean:
        top = blue_ocean[0]
        recommendations.append(f"🎯 Top pick: '{top.get('keyword')}' — Score {(top.get('score') or {}).get('total_score', 0)}, Volume {top.get('exact_volume', 0):,}")
    
    if high_volume:
        recommendations.append(f"📈 {len(high_volume)} high-volume keywords (>10K) — focus for traffic")
    
    if low_difficulty:
        recommendations.append(f"🏖️ {len(low_difficulty)} low-difficulty keywords — quick wins for ranking")
    
    if trending:
        recommendations.append(f"📈 {len(trending)} trending keywords — capitalize on momentum")
    
    # Pattern analysis
    patterns_found = {}
    for k in keywords:
        for p in k.get('patterns', []):
            pname = p.get('pattern', str(p)) if isinstance(p, dict) else str(p)
            patterns_found[pname] = patterns_found.get(pname, 0) + 1

    if patterns_found.get('Rising Trend', 0) > 2:
        recommendations.append(f"🔥 {patterns_found['Rising Trend']} rising trend keywords detected")

    if patterns_found.get('Under-optimized', 0) > 0:
        recommendations.append(f"💎 {patterns_found['Under-optimized']} under-optimized opportunities")
    
    return {
        'summary': summary,
        'blue_ocean_count': len(blue_ocean),
        'high_volume_count': len(high_volume),
        'low_difficulty_count': len(low_difficulty),
        'trending_count': len(trending),
        'patterns_found': patterns_found,
        'recommendations': recommendations,
        'market_assessment': 'EXCELLENT' if len(blue_ocean) >= 5 else 'GOOD' if len(blue_ocean) >= 2 else 'MODERATE' if low_difficulty else 'COMPETITIVE'
    }

def main():
    parser = argparse.ArgumentParser(description='Keyword Opportunity Finder')
    parser.add_argument('params', help='JSON parameters: {"keyword": "pet water fountain"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to specified directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = run_finder(params)
    if 'error' in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    if args.chart and 'error' not in result:
        charts, chart_analysis = generate_charts(result, args.chart)
        result['charts'] = charts
        result['chart_analysis'] = chart_analysis
        print(f"Generated {len(charts)} charts in {args.chart}", file=sys.stderr)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
