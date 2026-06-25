#!/usr/bin/env python3
"""
Trend Discovery v2.0.0 - Find trending categories and rising niches.

Enhanced with:
- TikTok Shop sales data (not just product counts)
- Cross-platform trend validation
- eBay sold listings for demand verification

Usage:
  python3 trend_discovery.py '{"keywords": ["pet water fountain", "dog toys"]}'
  python3 trend_discovery.py '{"category": "pet supplies"}' --chart ./output/

"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

# --- Shared chart styling (from display-rules.md via chart_style.json) ---
try:
    from ecommerce_chart_helpers import load_style, apply_style, save_chart, get_color, get_palette, get_bar_kwargs, get_font_size, setup_plt, merge_and_chart
except ImportError:
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


def _get_js_historical_volume(keyword: str, marketplace: str = 'us') -> dict:
    """Get Jungle Scout historical search volume to validate trend direction."""
    result = None
    try:
        _end_dt = datetime.now().strftime('%Y-%m-%d')
        _start_dt = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        _url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/historical-search-volume"
        _payload = json.dumps({'keyword': keyword, 'marketplace': marketplace or 'us', 'startDate': _start_dt, 'endDate': _end_dt}).encode('utf-8')
        _req = Request(_url, data=_payload, headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}', 'Content-Type': 'application/json'}, method='POST')
        with urlopen(_req, timeout=30) as _r:
            _raw = json.loads(_r.read().decode('utf-8'))
        if isinstance(_raw, dict) and _raw.get('code') == 0:
            result = _raw.get('data', _raw)
        else:
            result = _raw
    except Exception as _e:
        print(f"  JS historical error: {_e}", file=sys.stderr)
    if not result:
        return {}
    hist_list = result.get('historicalSearchVolumeList', result.get('data', []))
    if not hist_list or not isinstance(hist_list, list):
        return {}
    volumes = []
    for entry in hist_list:
        if isinstance(entry, dict):
            vol = entry.get('estimatedExactSearchVolume')
            if vol is None:
                vol = entry.get('searchVolume')
            if vol is None:
                vol = entry.get('exact')
            if vol is None:
                vol = entry.get('value', 0)
            if vol is not None and vol != 0:
                volumes.append(int(vol))
        elif isinstance(entry, (int, float)):
            volumes.append(int(entry))
    if not volumes:
        return {}
    # Calculate 30d vs 90d trend
    trend_30d = 'STABLE'
    trend_90d = 'STABLE'
    if len(volumes) >= 2:
        recent_avg = sum(volumes[-4:]) / max(len(volumes[-4:]), 1)
        older_avg = sum(volumes[:4]) / max(len(volumes[:4]), 1)
        if older_avg > 0:
            total_change = (recent_avg - older_avg) / older_avg
            if total_change > 0.3: trend_90d = 'STRONGLY_RISING'
            elif total_change > 0.1: trend_90d = 'RISING'
            elif total_change < -0.3: trend_90d = 'STRONGLY_DECLINING'
            elif total_change < -0.1: trend_90d = 'DECLINING'
    if len(volumes) >= 2:
        change_30d = (volumes[-1] - volumes[-2]) / max(volumes[-2], 1)
        if change_30d > 0.15: trend_30d = 'RISING'
        elif change_30d < -0.15: trend_30d = 'DECLINING'
    return {
        'current_volume': volumes[-1] if volumes else 0,
        'peak_volume': max(volumes),
        'trend_30d': trend_30d,
        'trend_90d': trend_90d,
        'data_points': len(volumes)
    }


def check_google_trends(keyword, months: int = 12):
    """Check Google Trends for keyword over the specified time range"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        data = call_api("/googleTrend/getTrendByKeys", {
            "keyword": keyword,
            "region": "US",
            "dayRangeStart": start_date.strftime('%Y-%m-%d'),
            "dayRangeEnd": end_date.strftime('%Y-%m-%d')
        })
        if not data:
            return None
        
        # API returns: {"trendInfoForKeys": [{"keyword": "...", "trendValues": [...]}]}
        trend_info = data.get('trendInfoForKeys', []) if isinstance(data, dict) else []
        if trend_info and isinstance(trend_info, list):
            values = trend_info[0].get('trendValues', [])
        else:
            values = data.get('trendValues', data.get('values', [])) if isinstance(data, dict) else []
        if not values:
            return None

        # Calculate trend direction
        recent = [int(v.get('value', 0)) for v in values[-4:] if v.get('value')]
        early = [int(v.get('value', 0)) for v in values[:4] if v.get('value')]
        
        if recent and early:
            recent_avg = sum(recent) / len(recent)
            early_avg = sum(early) / len(early)
            change = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            
            return {
                'keyword': keyword,
                'trend_change': round(change, 1),
                'direction': 'rising' if change > 20 else 'declining' if change < -20 else 'stable',
                'current_interest': recent_avg,
                'historical': [int(v.get('value', 0) or 0) for v in values]
            }
    except Exception as e:
        print(f"Google Trends error [{keyword}]: {e}", file=sys.stderr)
        return None


def check_tiktok_trends(keyword):
    """Check TikTok product trends"""
    try:
        data = call_api("/echotik/listProduct", {
            "keyword": keyword,
            "region": "US"
        })
        if not data:
            return None

        products = data.get('products', [])
        if not products:
            return None

        total_sales = 0
        top_products = []
        for p in products[:20]:
            # Echotik returns sales in totalSale30dCnt, not 'sold' or 'sales'
            # Use explicit None checks to avoid skipping legitimate 0 values
            sales = p.get('totalSale30dCnt')
            if sales is None:
                sales = p.get('monthlySalesUnits')
            if sales is None:
                sales = p.get('sold')
            if sales is None:
                sales = p.get('sales', 0)
            sales = sales or 0
            total_sales += sales
            if len(top_products) < 3:
                top_products.append({
                    'title': (p.get('productName') or p.get('title', '') or '')[:40],
                    'sales': sales,
                    'sales_total': p.get('totalSaleCnt', 0),
                    'revenue_30d': p.get('totalSaleGmv30dAmt', 0),
                })

        # Also compute total cumulative sales across top products
        total_all_time = sum(p.get('totalSaleCnt', 0) or 0 for p in products[:20])
        total_revenue_30d = sum(p.get('totalSaleGmv30dAmt', 0) or 0 for p in products[:20])

        return {
            'keyword': keyword,
            'tiktok_products': len(products),
            'has_tiktok_presence': True,
            'total_sales_30d': total_sales,
            'total_all_time_sales': total_all_time,
            'total_revenue_30d': total_revenue_30d,
            'trending': total_sales > 1000,
            'opportunity': 'HOT' if total_sales > 10000 else 'GROWING' if total_sales > 1000 else 'EARLY' if total_sales > 100 else 'MINIMAL',
            'top_products': top_products
        }
    except Exception as e:
        print(f"TikTok error [{keyword}]: {e}", file=sys.stderr)
        return None


def analyze_amazon_newness(keyword):
    """Check for new products on Amazon"""
    try:
        data = call_api("/amazon/search", {
            "keyword": keyword,
            "amazonDomain": "amazon.com"
        })
        if not data:
            return None
        
        products = data.get('products', [])
        if not products:
            return None
        
        # ratings = review count (e.g. 9800), rating = star score (e.g. 4.8)
        new_products = [p for p in products if (p.get('ratings', 0) or 0) < 100]
        
        # Extract price and sales data for richer analysis
        # API returns extractedPrice (camelCase), not extracted_price
        prices = [p.get('extractedPrice') or p.get('price', 0) or 0 for p in products if (p.get('extractedPrice') or p.get('price', 0))]
        monthly_units = [p.get('monthlySalesUnits', 0) or 0 for p in products]
        monthly_rev = [p.get('monthlySalesRevenue', 0) for p in products if p.get('monthlySalesRevenue')]
        # Parse monthlySalesRevenue which may be string like "3250.00"
        monthly_rev_parsed = []
        for r in monthly_rev:
            try:
                monthly_rev_parsed.append(float(r))
            except (ValueError, TypeError):
                pass
        
        return {
            'keyword': keyword,
            'total_products': len(products),
            'new_products_count': len(new_products),
            'new_products_pct': len(new_products) / len(products) * 100 if products else 0,
            'market_maturity': 'emerging' if len(new_products) / len(products) > 0.3 else 
                             'growing' if len(new_products) / len(products) > 0.15 else 'mature',
            'avg_price': round(sum(prices) / len(prices), 2) if prices else None,
            'price_range': [round(min(prices), 2), round(max(prices), 2)] if prices else None,
            'avg_monthly_units': round(sum(monthly_units) / len(monthly_units)) if monthly_units else None,
            'total_monthly_revenue': round(sum(monthly_rev_parsed)) if monthly_rev_parsed else None,
        }
    except Exception as e:
        print(f"Amazon error [{keyword}]: {e}", file=sys.stderr)
        return None


def calculate_trend_score(google_data, tiktok_data, amazon_data):
    """Calculate overall trend score"""
    score = 50
    signals = []
    
    if google_data:
        if google_data['direction'] == 'rising':
            score += 20
            signals.append(f"Google Trends: +{google_data['trend_change']:.0f}%")
        elif google_data['direction'] == 'declining':
            score -= 15
            signals.append(f"Google Trends: {google_data['trend_change']:.0f}%")
    
    if tiktok_data and tiktok_data.get('has_tiktok_presence'):
        score += 15
        signals.append(f"TikTok: {tiktok_data['tiktok_products']} products")
    
    if amazon_data:
        if amazon_data['market_maturity'] == 'emerging':
            score += 15
            signals.append("Amazon: Emerging market")
        elif amazon_data['market_maturity'] == 'growing':
            score += 10
            signals.append("Amazon: Growing market")
    
    return {
        'score': min(100, max(0, score)),
        'signals': signals,
        'verdict': 'Hot Trend' if score >= 80 else 
                  'Rising' if score >= 65 else 
                  'Stable' if score >= 45 else 'Declining'
    }


# === Chart Analysis ===
def generate_chart_analysis(results):
    """Generate analytical text for each chart"""
    analysis = {}
    trends = results.get('trends', [])
    
    if not trends:
        return analysis
    
    # Chart 1: Trend Score Analysis
    lines = ["**📊 Trend Score Analysis:**"]
    hot = [t for t in trends if (t.get('trend_score') or {}).get('verdict') == 'Hot Trend']
    rising = [t for t in trends if (t.get('trend_score') or {}).get('verdict') == 'Rising']
    
    if hot:
        lines.append(f"- 🔥 Hot Trends ({len(hot)}): {', '.join([t['keyword'][:15] for t in hot[:3]])}")
    if rising:
        lines.append(f"- 📈 Rising ({len(rising)}): {', '.join([t['keyword'][:15] for t in rising[:3]])}")
    
    if not hot and not rising:
        lines.append("- ⚠️ No hot or rising trends found")
        lines.append("- Consider broader keyword research")
    else:
        best = max(trends, key=lambda x: (x.get('trend_score') or {}).get('score', 0))
        lines.append(f"- ✅ Best opportunity: **{best['keyword']}** (Score: {(best.get('trend_score') or {}).get('score', 0)})")
    analysis['scores'] = "\n".join(lines)
    
    # Chart 2: Google Trends Analysis
    lines = ["**📈 Search Interest Analysis:**"]
    gt_available = [t for t in trends if t.get('google_trends')]
    
    if gt_available:
        for t in gt_available[:3]:
            gt = t['google_trends']
            growth = gt.get('trend_change', 0)
            current = gt.get('current_interest', 0)
            
            if growth > 20:
                lines.append(f"- ✅ **{t['keyword'][:15]}**: +{growth:.0f}% growth (interest: {current})")
            elif growth > 0:
                lines.append(f"- 🟡 **{t['keyword'][:15]}**: +{growth:.0f}% (moderate growth)")
            else:
                lines.append(f"- ⚠️ **{t['keyword'][:15]}**: {growth:.0f}% (declining)")
    else:
        lines.append("- No Google Trends data available")
    analysis['google'] = "\n".join(lines)
    
    # Chart 3: Market Maturity Analysis
    lines = ["**🎯 Market Maturity Assessment:**"]
    
    emerging = [t for t in trends if (t.get('amazon') or {}).get('market_maturity') == 'emerging']
    growth = [t for t in trends if (t.get('amazon') or {}).get('market_maturity') == 'growing']
    mature = [t for t in trends if (t.get('amazon') or {}).get('market_maturity') == 'mature']
    
    if emerging:
        lines.append(f"- 🌱 Emerging markets ({len(emerging)}): Best entry timing")
    if growth:
        lines.append(f"- 📈 Growth phase ({len(growth)}): Good opportunity, competition building")
    if mature:
        lines.append(f"- 🏢 Mature markets ({len(mature)}): Established, harder to enter")
    
    if not emerging and not growth:
        lines.append("- ⚠️ Mostly mature markets - consider niche alternatives")
    analysis['maturity'] = "\n".join(lines)
    
    return analysis


# === Chart Generation ===
def generate_charts(results, output_dir):
    """Generate trend discovery charts using style from chart_style.json."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not installed, skipping charts", file=sys.stderr)
        return [], {}
    
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    chart_analysis = generate_chart_analysis(results)
    style = load_style()
    
    font_cfg = style.get('font', {})
    bar_cfg = style.get('bar', {})
    verdict_colors = style.get('verdict_colors', {})
    maturity_colors = style.get('maturity_colors', {})
    
    plt.rcParams['font.family'] = font_cfg.get('family', ['DejaVu Sans', 'sans-serif'])
    
    trends = results.get('trends', [])
    if not trends:
        return charts, chart_analysis
    
    # Chart 1: Trend Score Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    keywords = [t['keyword'][:20] for t in trends]
    scores = [(t.get('trend_score') or {}).get('score', 0) for t in trends]
    verdicts = [(t.get('trend_score') or {}).get('verdict', 'Unknown') for t in trends]
    
    colors = [verdict_colors.get(v, get_color('muted')) for v in verdicts]
    
    y_pos = np.arange(len(keywords))
    bars = ax.barh(y_pos, scores, color=colors,
                   height=bar_cfg.get('height', 0.6),
                   edgecolor=bar_cfg.get('edgecolor', 'white'),
                   linewidth=bar_cfg.get('linewidth', 1.5))
    
    for i, (bar, score, verdict) in enumerate(zip(bars, scores, verdicts)):
        ax.text(score + 1, i, f'{score} ({verdict})', va='center', fontsize=font_cfg.get('label', 10))
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(keywords, fontsize=font_cfg.get('tick', 10))
    ax.set_xlabel('Trend Score', fontsize=font_cfg.get('axis', 11))
    ax.set_xlim(0, 110)
    ax.axvline(x=80, color=verdict_colors.get('Hot Trend', get_color('hot')), linestyle='--', alpha=0.5, label='Hot (80+)')
    ax.axvline(x=65, color=verdict_colors.get('Rising', get_color('good')), linestyle='--', alpha=0.5, label='Rising (65+)')
    ax.legend(loc='lower right', fontsize=font_cfg.get('legend', 10))
    ax.set_title('TREND SCORE COMPARISON', fontsize=font_cfg.get('title', 14), fontweight='bold', pad=15)
    apply_style(ax, style)
    
    chart_path = os.path.join(output_dir, 'trend_comparison.png')
    save_chart(fig, chart_path, style)
    charts.append(chart_path)
    
    # Chart 2: Google Trends Lines (if available)
    google_data_available = [t for t in trends if t.get('google_trends') and t['google_trends'].get('historical')]
    
    if google_data_available:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        line_colors = plt.cm.Set2(np.linspace(0, 1, len(google_data_available)))
        
        for i, t in enumerate(google_data_available[:5]):
            gt = t['google_trends']
            historical = gt.get('historical', [])
            if historical:
                weeks = list(range(len(historical)))
                ax.plot(weeks, historical, linewidth=2, label=t['keyword'][:20], color=line_colors[i])
        
        ax.set_xlabel('Weeks', fontsize=font_cfg.get('axis', 11))
        ax.set_ylabel('Search Interest', fontsize=font_cfg.get('axis', 11))
        ax.set_title('GOOGLE TRENDS - Search Interest Over Time', fontsize=font_cfg.get('title', 14), fontweight='bold', pad=15)
        ax.legend(loc='upper left', fontsize=font_cfg.get('legend', 10))
        ax.grid(True, alpha=0.3)
        apply_style(ax, style)
        
        chart_path = os.path.join(output_dir, 'google_trends.png')
        save_chart(fig, chart_path, style)
        charts.append(chart_path)
    
    # Chart 3: Market Maturity Distribution
    maturity_counts = {'emerging': 0, 'growing': 0, 'mature': 0, 'unknown': 0}
    for t in trends:
        amazon = t.get('amazon') or {}
        if amazon:
            mat = amazon.get('market_maturity', 'mature')
            maturity_counts[mat] = maturity_counts.get(mat, 0) + 1
        else:
            maturity_counts['unknown'] += 1
    
    if sum(maturity_counts.values()) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        mat_keys = ['emerging', 'growing', 'mature', 'unknown']
        mat_labels = ['Emerging', 'Growing', 'Mature', 'No Data']
        mat_colors = [maturity_colors.get(k, get_color('muted')) for k in mat_keys]
        values = [maturity_counts[k] for k in mat_keys]
        
        # Filter out zero slices to avoid empty wedges
        filtered = [(l, v, c) for l, v, c in zip(mat_labels, values, mat_colors) if v > 0]
        if filtered:
            f_labels, f_values, f_colors = zip(*filtered)
            explode = [0.08] * len(f_values)
            
            wedges, texts, autotexts = ax.pie(
                f_values, labels=f_labels, autopct='%1.0f%%',
                colors=f_colors, startangle=90, explode=explode,
                textprops={'fontsize': font_cfg.get('label', 10)}
            )
            for at in autotexts:
                at.set_fontweight('bold')
            
            ax.set_title('MARKET MATURITY DISTRIBUTION', fontsize=font_cfg.get('title', 14), fontweight='bold', pad=15)
            
            chart_path = os.path.join(output_dir, 'market_maturity.png')
            save_chart(fig, chart_path, style)
            charts.append(chart_path)
        else:
            plt.close(fig)
    
    # Chart 4: Score Breakdown (for top trend)
    top = results.get('top_opportunity')
    if top:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        components = {
            'Google Trend': 20 if (top.get('google_trends') or {}).get('direction') == 'rising' else 0,
            'TikTok Presence': 15 if (top.get('tiktok') or {}).get('has_tiktok_presence') else 0,
            'Market Maturity': 15 if (top.get('amazon') or {}).get('market_maturity') == 'emerging' else 10 if (top.get('amazon') or {}).get('market_maturity') == 'growing' else 0,
            'Base Score': 50
        }
        
        breakdown_colors = style.get('score_breakdown_colors', [get_color('hot'), get_color('secondary'), get_color('good'), get_color('primary')])
        y_pos = np.arange(len(components))
        
        bars = ax.barh(y_pos, list(components.values()), color=breakdown_colors,
                       height=bar_cfg.get('height', 0.6),
                       edgecolor=bar_cfg.get('edgecolor', 'white'),
                       linewidth=bar_cfg.get('linewidth', 1.5))
        
        for bar, val in zip(bars, components.values()):
            if val > 0:
                ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'+{val}',
                        va='center', fontsize=font_cfg.get('label', 10))
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(list(components.keys()), fontsize=font_cfg.get('tick', 10))
        ax.set_xlabel('Score Contribution', fontsize=font_cfg.get('axis', 11))
        ax.set_xlim(0, 60)
        ax.set_title(f'SCORE BREAKDOWN: {top["keyword"][:25].upper()}\nTotal: {(top.get("trend_score") or {}).get("score", 0)}',
                    fontsize=font_cfg.get('title', 14) - 2, fontweight='bold', pad=15)
        apply_style(ax, style)
        
        chart_path = os.path.join(output_dir, 'score_breakdown.png')
        save_chart(fig, chart_path, style)
        charts.append(chart_path)
    
    return charts, chart_analysis


def run_discovery(params):
    keywords = params.get('keywords', [])
    category = params.get('category', '')
    
    if category and not keywords:
        keywords = [category]
    
    if not keywords:
        return {"error": "No keywords provided"}
    
    results = []
    
    marketplace = params.get('marketplace', 'us')

    for keyword in keywords:
        google = check_google_trends(keyword)
        tiktok = check_tiktok_trends(keyword)
        amazon = analyze_amazon_newness(keyword)

        # Fetch JS historical search volume to validate trend direction
        js_hist = _get_js_historical_volume(keyword, marketplace=marketplace or 'us')
        if js_hist.get('trend_90d') in ('RISING', 'STRONGLY_RISING'):
            trend_score_boost = 10 if js_hist.get('trend_90d') == 'STRONGLY_RISING' else 5
        else:
            trend_score_boost = 0

        trend_score = calculate_trend_score(google, tiktok, amazon)
        # Apply JS historical volume boost
        if trend_score_boost:
            trend_score = dict(trend_score)
            trend_score['score'] = min(100, trend_score['score'] + trend_score_boost)
            trend_score['signals'] = list(trend_score.get('signals', []))
            trend_score['signals'].append(f"JS Historical: {js_hist.get('trend_90d')} (+{trend_score_boost})")
            # Recalculate verdict after boost
            s = trend_score['score']
            trend_score['verdict'] = ('Hot Trend' if s >= 80 else
                                      'Rising' if s >= 65 else
                                      'Stable' if s >= 45 else 'Declining')

        results.append({
            'keyword': keyword,
            'trend_score': trend_score,
            'google_trends': google,
            'tiktok': tiktok,
            'amazon': amazon,
            'js_historical_volume': js_hist if js_hist else None
        })
    
    results.sort(key=lambda x: x['trend_score']['score'], reverse=True)
    
    # Generate insights
    insights = generate_insights(results)
    
    return {
        'analyzed_keywords': len(keywords),
        'trends': results,
        'top_opportunity': results[0] if results else None,
        'insights': insights
    }


def generate_insights(trends: list) -> dict:
    """Generate actionable insights from trend analysis"""
    if not trends:
        return {'summary': 'No trends analyzed', 'recommendations': []}
    
    # Categorize trends
    hot_trends = [t for t in trends if (t.get('trend_score') or {}).get('score', 0) >= 70]
    rising_trends = [t for t in trends if 50 <= (t.get('trend_score') or {}).get('score', 0) < 70]
    stable_trends = [t for t in trends if 30 <= (t.get('trend_score') or {}).get('score', 0) < 50]
    declining_trends = [t for t in trends if (t.get('trend_score') or {}).get('score', 0) < 30]
    
    # Check for platform-specific signals
    tiktok_hot = [t for t in trends if (t.get('tiktok') or {}).get('trending', False)]
    google_rising = [t for t in trends if (t.get('google_trends') or {}).get('direction', '') == 'rising']
    # A market is favorable for new entrants if it's 'emerging' (>30% new products)
    amazon_new = [t for t in trends if (t.get('amazon') or {}).get('market_maturity') == 'emerging']
    
    # Summary
    if hot_trends:
        summary = f"🔥 {len(hot_trends)} hot trends detected! Strong momentum across platforms."
    elif rising_trends:
        summary = f"📈 {len(rising_trends)} rising trends found. Good entry opportunities."
    elif tiktok_hot:
        summary = f"📱 {len(tiktok_hot)} TikTok viral signals — may not translate to Amazon yet."
    else:
        summary = f"📊 {len(trends)} keywords analyzed. Market appears stable."
    
    # Recommendations
    recommendations = []
    
    if hot_trends:
        top = hot_trends[0]
        recommendations.append(f"🔥 Top trend: '{top['keyword']}' — Score {top['trend_score']['score']}, act fast!")
    
    if tiktok_hot:
        recommendations.append(f"📱 {len(tiktok_hot)} TikTok signals — validate with Amazon demand before investing")
    
    if google_rising:
        recommendations.append(f"📈 {len(google_rising)} keywords rising on Google — sustained interest")
    
    if amazon_new:
        recommendations.append(f"🆕 {len(amazon_new)} categories with successful new entrants — entry possible")
    
    if declining_trends:
        kws = ', '.join([t['keyword'] for t in declining_trends[:3]])
        recommendations.append(f"⚠️ Avoid: {kws} — declining trends")
    
    # Cross-platform validation
    validated = [t for t in trends if
                 (t.get('google_trends') or {}).get('direction') == 'rising' and
                 ((t.get('tiktok') or {}).get('trending') or (t.get('amazon') or {}).get('market_maturity') == 'emerging')]
    if validated:
        recommendations.append(f"✅ {len(validated)} trends validated across multiple platforms — highest confidence")
    
    return {
        'summary': summary,
        'trend_distribution': {
            'hot': len(hot_trends),
            'rising': len(rising_trends),
            'stable': len(stable_trends),
            'declining': len(declining_trends)
        },
        'platform_signals': {
            'tiktok_hot': len(tiktok_hot),
            'google_rising': len(google_rising),
            'amazon_new_success': len(amazon_new)
        },
        'recommendations': recommendations,
        'confidence_level': 'HIGH' if validated else 'MEDIUM' if hot_trends or rising_trends else 'LOW'
    }


def main():
    parser = argparse.ArgumentParser(description='Trend Discovery')
    parser.add_argument('params', nargs='?', help='JSON parameters: {"keywords": ["pet fountain", "dog toys"]}')
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
    
    result = run_discovery(params)
    if 'error' in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

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


if __name__ == "__main__":
    main()
