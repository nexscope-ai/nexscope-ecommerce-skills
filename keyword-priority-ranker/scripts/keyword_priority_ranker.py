#!/usr/bin/env python3
"""
Keyword Priority Ranker v1.0.0

Rank and prioritize keywords by actionable opportunity score.
Answers: "Which keywords should I target first?"

Data Sources:
- Keywords API: keywords_by_keyword_query (via NexScope proxy)
- Keywords API: keywords_by_asin_query (via NexScope proxy)

Usage:
    python3 keyword_priority_ranker.py '{"keyword": "face wash"}'
    python3 keyword_priority_ranker.py '{"asin": "B07RL88DD2"}'
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

# Default weights
DEFAULT_WEIGHTS = {
    'volume': 0.25,
    'ease': 0.25,
    'relevancy': 0.15,
    'trend': 0.15,
    'ppc_value': 0.10,
    'competition': 0.10
}

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

def get_keywords_by_keyword(seed: str, market: str = 'us', min_volume: int = 100) -> List[dict]:
    """Get related keywords for a seed keyword"""
    payload = {
        "data": {
            "type": "keywords_by_keyword_query",
            "attributes": {
                "search_terms": seed,
                "min_monthly_search_volume_exact": min_volume
            }
        }
    }
    
    result = js_api_call('/keywords/keywords_by_keyword_query', payload, market)
    return result.get('data', []) if result else []

def get_keywords_by_asin(asins: List[str], market: str = 'us', min_volume: int = 100) -> List[dict]:
    """Get keywords an ASIN ranks for"""
    payload = {
        "data": {
            "type": "keywords_by_asin_query",
            "attributes": {
                "asins": asins[:5],
                "include_variants": False,
                "min_monthly_search_volume_exact": min_volume
            }
        }
    }
    
    result = js_api_call('/keywords/keywords_by_asin_query', payload, market)
    return result.get('data', []) if result else []

# === Analysis Functions ===

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale"""
    if max_val == min_val:
        return 50
    return min(100, max(0, (value - min_val) / (max_val - min_val) * 100))

def calculate_priority_score(keyword: dict, weights: dict, 
                              volume_range: tuple, competition_range: tuple) -> float:
    """Calculate priority score for a keyword"""
    
    # Volume score (0-100)
    volume = keyword.get('search_volume_exact', 0)
    volume_score = normalize_score(volume, volume_range[0], volume_range[1])
    
    # Ease score (already 0-100)
    ease_score = keyword.get('ease_of_ranking', 50)
    
    # Relevancy score (already 0-100 from API, but often higher)
    relevancy = min(100, keyword.get('relevancy_score', 50))
    
    # Trend score (convert % to 0-100, centered at 50)
    trend = keyword.get('monthly_trend', 0)
    trend_score = min(100, max(0, 50 + trend))  # -50% = 0, 0% = 50, +50% = 100
    
    # PPC value score (higher PPC = more valuable to rank organically)
    ppc = keyword.get('ppc_bid_exact') or keyword.get('ppc_bid_broad') or 0
    ppc_score = min(100, ppc * 20)  # $5 = 100
    
    # Competition score (inverse - fewer competitors = higher score)
    competition = keyword.get('organic_products', 500)
    competition_score = 100 - normalize_score(competition, competition_range[0], competition_range[1])
    
    # Weighted sum
    score = (
        volume_score * weights.get('volume', 0.25) +
        ease_score * weights.get('ease', 0.25) +
        relevancy * weights.get('relevancy', 0.15) +
        trend_score * weights.get('trend', 0.15) +
        ppc_score * weights.get('ppc_value', 0.10) +
        competition_score * weights.get('competition', 0.10)
    )
    
    # Store component scores for debugging
    keyword['_scores'] = {
        'volume': round(volume_score, 1),
        'ease': round(ease_score, 1),
        'relevancy': round(relevancy, 1),
        'trend': round(trend_score, 1),
        'ppc': round(ppc_score, 1),
        'competition': round(competition_score, 1)
    }
    
    return round(score, 1)

def assign_tier(score: float) -> tuple:
    """Assign priority tier based on score"""
    if score >= 80:
        return ('P0', '🥇 NOW', 'Attack immediately')
    elif score >= 60:
        return ('P1', '🥈 SOON', 'Target within 2 weeks')
    elif score >= 40:
        return ('P2', '🥉 LATER', 'Add to backlog')
    elif score >= 20:
        return ('P3', '⏸️ HOLD', 'Monitor only')
    else:
        return ('SKIP', '❌ SKIP', "Don't waste resources")

def assign_strategy(keyword: dict) -> str:
    """Assign keyword strategy type"""
    volume = keyword.get('search_volume_exact', 0)
    ease = keyword.get('ease_of_ranking', 50)
    relevancy = keyword.get('relevancy_score', 50)
    current_rank = keyword.get('organic_rank')
    name = keyword.get('keyword', '').lower()
    
    # Brand keywords (common brand names)
    brands = ['cerave', 'neutrogena', 'cetaphil', 'la roche', 'aveeno', 'olay',
              'garnier', 'nivea', 'dove', 'clinique', 'panoxyl', 'cosrx']
    if any(b in name for b in brands):
        return 'BRAND_TERM'
    
    # Already ranking well - defend/improve
    if current_rank and current_rank <= 10:
        return 'DEFEND'
    
    # Quick Win: High ease + decent volume
    if ease >= 85 and 300 <= volume <= 3000:
        return 'QUICK_WIN'
    
    # Big Bet: High volume, moderate difficulty
    if volume >= 3000 and ease >= 60:
        return 'BIG_BET'
    
    # Long-tail Gold: High relevancy + low competition
    if relevancy >= 80 and ease >= 90 and volume < 1000:
        return 'LONG_TAIL'
    
    # Competitive: Hard to rank
    if ease < 50:
        return 'COMPETITIVE'
    
    return 'STANDARD'

def parse_keywords(raw_data: List[dict], source: str = 'keyword') -> List[dict]:
    """Parse raw API data into standard format"""
    keywords = []
    
    for item in raw_data:
        attr = item.get('attributes', {})
        kw = {
            'keyword': attr.get('name', ''),
            'search_volume_exact': int(attr.get('monthly_search_volume_exact', 0) or 0),
            'search_volume_broad': int(attr.get('monthly_search_volume_broad', 0) or 0),
            'monthly_trend': int(attr.get('monthly_trend', 0) or 0),
            'ease_of_ranking': int(attr.get('ease_of_ranking_score', 50) or 50),
            'relevancy_score': int(attr.get('relevancy_score', 50) or 50),
            'organic_products': int(attr.get('organic_product_count', 500) or 500),
            'sponsored_products': int(attr.get('sponsored_product_count', 0) or 0),
            'ppc_bid_exact': attr.get('ppc_bid_exact') and float(attr.get('ppc_bid_exact')),
            'ppc_bid_broad': attr.get('ppc_bid_broad') and float(attr.get('ppc_bid_broad')),
            'category': attr.get('dominant_category', ''),
            'source': source
        }
        
        # Add ranking info if from ASIN source
        if source == 'asin':
            kw['organic_rank'] = attr.get('organic_rank')
            kw['sponsored_rank'] = attr.get('sponsored_rank')
        
        keywords.append(kw)
    
    return keywords

def rank_keywords(keywords: List[dict], weights: dict = None) -> dict:
    """Main ranking function"""
    if not keywords:
        return {'error': 'No keywords to rank'}
    
    weights = weights or DEFAULT_WEIGHTS
    
    # Calculate ranges for normalization
    volumes = [k['search_volume_exact'] for k in keywords]
    competitions = [k['organic_products'] for k in keywords]
    
    volume_range = (min(volumes), max(volumes)) if volumes else (0, 1)
    competition_range = (min(competitions), max(competitions)) if competitions else (0, 1000)
    
    # Calculate scores
    for kw in keywords:
        kw['priority_score'] = calculate_priority_score(
            kw, weights, volume_range, competition_range
        )
        tier_info = assign_tier(kw['priority_score'])
        kw['tier'] = tier_info[0]
        kw['tier_label'] = tier_info[1]
        kw['tier_action'] = tier_info[2]
        kw['strategy'] = assign_strategy(kw)
    
    # Sort by priority score
    keywords.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Group by tier
    tiers = {
        'P0': [], 'P1': [], 'P2': [], 'P3': [], 'SKIP': []
    }
    for kw in keywords:
        tiers[kw['tier']].append(kw)
    
    # Strategy distribution
    strategies = {}
    for kw in keywords:
        s = kw['strategy']
        strategies[s] = strategies.get(s, 0) + 1
    
    # Summary stats
    total = len(keywords)
    avg_score = sum(k['priority_score'] for k in keywords) / total if total else 0
    
    return {
        'total_keywords': total,
        'avg_priority_score': round(avg_score, 1),
        'weights_used': weights,
        
        'tier_distribution': {
            'P0_now': len(tiers['P0']),
            'P1_soon': len(tiers['P1']),
            'P2_later': len(tiers['P2']),
            'P3_hold': len(tiers['P3']),
            'skip': len(tiers['SKIP'])
        },
        
        'strategy_distribution': strategies,
        
        'p0_keywords': tiers['P0'][:20],
        'p1_keywords': tiers['P1'][:20],
        'p2_keywords': tiers['P2'][:10],
        'p3_keywords': tiers['P3'][:5],
        
        'top_20': keywords[:20],
        'quick_wins': [k for k in keywords if k['strategy'] == 'QUICK_WIN'][:10],
        'big_bets': [k for k in keywords if k['strategy'] == 'BIG_BET'][:10],
        
        'all_keywords': keywords
    }

def generate_insights(ranking: dict) -> dict:
    """Generate actionable insights"""
    tiers = ranking.get('tier_distribution', {})
    strategies = ranking.get('strategy_distribution', {})
    top = ranking.get('top_20', [])
    
    p0_count = tiers.get('P0_now', 0)
    total = ranking.get('total_keywords', 0)
    
    # Summary
    if p0_count >= 10:
        summary = f"🔥 Excellent! {p0_count} P0 keywords to attack immediately."
    elif p0_count >= 5:
        summary = f"👍 Good opportunity! {p0_count} P0 keywords ready for targeting."
    elif p0_count > 0:
        summary = f"📊 {p0_count} P0 keywords found. Consider expanding keyword research."
    else:
        summary = f"⚠️ No P0 keywords. Focus on P1 tier or find better opportunities."
    
    # Action plan
    actions = []
    
    if p0_count > 0:
        top_p0 = ranking.get('p0_keywords', [])[0] if ranking.get('p0_keywords') else None
        if top_p0:
            actions.append(f"🥇 Start with: '{top_p0['keyword']}' (Score: {top_p0['priority_score']})")
    
    quick_wins = strategies.get('QUICK_WIN', 0)
    if quick_wins > 0:
        actions.append(f"⚡ {quick_wins} quick wins available — low effort, fast results")
    
    big_bets = strategies.get('BIG_BET', 0)
    if big_bets > 0:
        actions.append(f"🎯 {big_bets} big bets — high volume targets worth investment")
    
    long_tail = strategies.get('LONG_TAIL', 0)
    if long_tail > 0:
        actions.append(f"📝 {long_tail} long-tail keywords — great for conversion")
    
    # Warnings
    warnings = []
    
    competitive = strategies.get('COMPETITIVE', 0)
    if competitive > total * 0.3:
        warnings.append(f"⚠️ {competitive} competitive keywords ({round(competitive/total*100)}%) — consider niching down")
    
    skip_count = tiers.get('skip', 0)
    if skip_count > total * 0.2:
        warnings.append(f"⚠️ {skip_count} keywords not worth targeting — filter your list")
    
    return {
        'summary': summary,
        'action_plan': actions,
        'warnings': warnings,
        'recommended_sequence': [
            '1. Quick Wins first (build momentum)',
            '2. Defend existing rankings',
            '3. Big Bets (allocate resources)',
            '4. Long-tail (conversion focus)'
        ]
    }

# === Main Function ===

def prioritize_keywords(keyword: str = None, asin: str = None, 
                        market: str = 'US', min_volume: int = 100,
                        weights: dict = None) -> dict:
    """Main entry point"""
    market_code = MARKET_MAP.get(market, 'us')
    
    print(f"Prioritizing keywords...", file=sys.stderr)
    
    all_keywords = []
    
    # Fetch from seed keyword
    if keyword:
        print(f"[1/3] Fetching keywords for '{keyword}'...", file=sys.stderr)
        kw_data = get_keywords_by_keyword(keyword, market_code, min_volume)
        if kw_data:
            all_keywords.extend(parse_keywords(kw_data, 'keyword'))
            print(f"  ✓ Got {len(kw_data)} keywords from seed", file=sys.stderr)
    
    # Fetch from ASIN
    if asin:
        print(f"[2/3] Fetching keywords for ASIN {asin}...", file=sys.stderr)
        asin_data = get_keywords_by_asin([asin], market_code, min_volume)
        if asin_data:
            parsed = parse_keywords(asin_data, 'asin')
            # Merge, preferring ASIN data (has ranking info)
            existing = {k['keyword'] for k in all_keywords}
            for kw in parsed:
                if kw['keyword'] in existing:
                    # Update existing with ranking info
                    for existing_kw in all_keywords:
                        if existing_kw['keyword'] == kw['keyword']:
                            existing_kw.update({
                                'organic_rank': kw.get('organic_rank'),
                                'sponsored_rank': kw.get('sponsored_rank'),
                                'source': 'both'
                            })
                            break
                else:
                    all_keywords.append(kw)
            print(f"  ✓ Got {len(asin_data)} keywords from ASIN", file=sys.stderr)
    
    if not all_keywords:
        return {'error': 'No keywords found', 'keyword': keyword, 'asin': asin}
    
    # Deduplicate by keyword name
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        if kw['keyword'] not in seen:
            seen.add(kw['keyword'])
            unique_keywords.append(kw)
    
    print(f"[3/3] Ranking {len(unique_keywords)} unique keywords...", file=sys.stderr)
    
    ranking = rank_keywords(unique_keywords, weights)
    insights = generate_insights(ranking)
    
    result = {
        'seed_keyword': keyword,
        'asin': asin,
        'marketplace': market,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        
        'summary': ranking['tier_distribution'],
        'avg_score': ranking['avg_priority_score'],
        'total_keywords': ranking['total_keywords'],
        
        'tier_distribution': ranking['tier_distribution'],
        'strategy_distribution': ranking['strategy_distribution'],
        
        'p0_keywords': ranking['p0_keywords'],
        'p1_keywords': ranking['p1_keywords'],
        'quick_wins': ranking['quick_wins'],
        'big_bets': ranking['big_bets'],
        
        'top_20': ranking['top_20'],
        
        'insights': insights,
        
        'all_keywords': ranking['all_keywords']
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
    
    GOLD = '#FFD700'
    SILVER = '#C0C0C0'
    BRONZE = '#CD7F32'
    GRAY = get_color('muted')
    RED = get_color('hot')
    GREEN = get_color('good')
    BLUE = get_color('primary')
    
    # Chart 1: Tier Distribution (Pie)
    tiers = result.get('tier_distribution', {})
    if tiers:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['P0 NOW', 'P1 SOON', 'P2 LATER', 'P3 HOLD', 'SKIP']
        sizes = [
            tiers.get('P0_now', 0),
            tiers.get('P1_soon', 0),
            tiers.get('P2_later', 0),
            tiers.get('P3_hold', 0),
            tiers.get('skip', 0)
        ]
        colors = [GOLD, SILVER, BRONZE, GRAY, RED]
        
        # Filter out zero values
        non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
        if non_zero:
            labels, sizes, colors = zip(*non_zero)
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                               autopct='%1.0f%%', startangle=90,
                                               textprops={'fontsize': 10})
            ax.set_title('PRIORITY TIER DISTRIBUTION', fontweight='bold', fontsize=12, pad=15)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/1_tier_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 1: Tier Distribution", file=sys.stderr)
    
    # Chart 2: Strategy Mix (Bar)
    strategies = result.get('strategy_distribution', {})
    if strategies:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        strat_labels = {
            'QUICK_WIN': 'Quick Win',
            'BIG_BET': 'Big Bet',
            'LONG_TAIL': 'Long-tail',
            'DEFEND': 'Defend',
            'BRAND_TERM': 'Brand',
            'COMPETITIVE': 'Competitive',
            'STANDARD': 'Standard'
        }
        strat_colors = {
            'QUICK_WIN': GREEN,
            'BIG_BET': BLUE,
            'LONG_TAIL': '#9C27B0',
            'DEFEND': GOLD,
            'BRAND_TERM': get_color('secondary'),
            'COMPETITIVE': RED,
            'STANDARD': GRAY
        }
        
        labels = [strat_labels.get(k, k) for k in strategies.keys()]
        values = list(strategies.values())
        colors_bar = [strat_colors.get(k, GRAY) for k in strategies.keys()]
        
        bars = ax.bar(labels, values, color=colors_bar, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                       str(val), ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Keywords', fontsize=10)
        ax.set_title('KEYWORD STRATEGY MIX', fontweight='bold', fontsize=12, pad=15)
        ax.set_ylim(0, max(values) * 1.2 if values else 10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=15)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_strategy_mix.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Strategy Mix", file=sys.stderr)
    
    # Chart 3: Top 20 Priority (Horizontal Bar)
    top_20 = result.get('top_20', [])[:15]
    if top_20:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        keywords = [k['keyword'][:30] + '...' if len(k['keyword']) > 30 else k['keyword'] 
                    for k in top_20]
        scores = [k['priority_score'] for k in top_20]
        
        # Color by tier
        tier_colors = {'P0': GOLD, 'P1': SILVER, 'P2': BRONZE, 'P3': GRAY, 'SKIP': RED}
        colors_bar = [tier_colors.get(k['tier'], GRAY) for k in top_20]
        
        y_pos = np.arange(len(keywords))
        bars = ax.barh(y_pos, scores, color=colors_bar, edgecolor='white', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(keywords, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Priority Score', fontsize=10)
        ax.set_title('TOP PRIORITY KEYWORDS', fontweight='bold', fontsize=12, pad=15)
        ax.set_xlim(0, 100)
        ax.axvline(x=80, color=GOLD, linestyle='--', alpha=0.5, label='P0 threshold')
        ax.axvline(x=60, color=SILVER, linestyle='--', alpha=0.5, label='P1 threshold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add volume labels
        for i, (bar, kw) in enumerate(zip(bars, top_20)):
            vol = kw.get('search_volume_exact', 0)
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   f'{vol:,}/mo', va='center', fontsize=8, color='gray')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_top_priority.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Top Priority", file=sys.stderr)
    
    # Chart 4: Priority Matrix (Volume vs Score)
    all_kws = result.get('all_keywords', [])
    if len(all_kws) < 2:
        print(f"  ⚠️ 4_priority_matrix.png skipped: need ≥2 items, got {len(all_kws)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        volumes = [k['search_volume_exact'] for k in all_kws]
        scores = [k['priority_score'] for k in all_kws]
        
        tier_colors = {'P0': GOLD, 'P1': SILVER, 'P2': BRONZE, 'P3': GRAY, 'SKIP': RED}
        colors_scatter = [tier_colors.get(k['tier'], GRAY) for k in all_kws]
        
        ax.scatter(volumes, scores, c=colors_scatter, s=60, alpha=0.7, edgecolors='white', linewidth=0.5)
        
        ax.axhline(y=80, color=GOLD, linestyle='--', alpha=0.5, label='P0')
        ax.axhline(y=60, color=SILVER, linestyle='--', alpha=0.5, label='P1')
        ax.axhline(y=40, color=BRONZE, linestyle='--', alpha=0.5, label='P2')
        
        ax.set_xlabel('Monthly Search Volume', fontsize=10)
        ax.set_ylabel('Priority Score', fontsize=10)
        ax.set_title('KEYWORD PRIORITY MATRIX', fontweight='bold', fontsize=12, pad=15)
        ax.set_ylim(0, 100)
        ax.legend(loc='lower right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_priority_matrix.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Priority Matrix", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    if len(sys.argv) < 2:
        print('Usage: python3 keyword_priority_ranker.py \'{"keyword": "face wash"}\' [--chart <dir>]', file=sys.stderr)
        sys.exit(1)
    
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(f"Invalid JSON: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    asin = params.get('asin')
    
    if not keyword and not asin:
        print("Missing required parameter: keyword or asin", file=sys.stderr)
        sys.exit(1)
    
    market = params.get('market', 'US')
    min_volume = params.get('min_volume', 100)
    
    # Custom weights
    weights = None
    if any(k.endswith('_weight') for k in params):
        weights = DEFAULT_WEIGHTS.copy()
        for key in ['volume', 'ease', 'relevancy', 'trend', 'ppc_value', 'competition']:
            if f'{key}_weight' in params:
                weights[key] = params[f'{key}_weight']
    
    chart_dir = None
    if '--chart' in sys.argv:
        chart_idx = sys.argv.index('--chart')
        if chart_idx + 1 < len(sys.argv):
            chart_dir = sys.argv[chart_idx + 1]
    
    result = prioritize_keywords(keyword, asin, market, min_volume, weights)
    
    if chart_dir and 'error' not in result:
        print(f"Generating charts in {chart_dir}...", file=sys.stderr)
        result['charts'] = generate_charts(result, chart_dir) or []
    
    # Output (exclude all_keywords for readability)
    output = {k: v for k, v in result.items() if k != 'all_keywords'}
    output['all_keywords_count'] = len(result.get('all_keywords', []))
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
