#!/usr/bin/env python3
"""
Niche Evaluator v2.0.0 - Quantitative niche assessment with multi-source validation.

Enhanced with:
- Keepa deep data (BSR trends, competition intensity)
- ABA data (Search Frequency Rank, market concentration)
- eBay sold listings (cross-platform demand verification)
- TikTok Shop (social commerce signals)

Usage:
  python3 niche_evaluator.py '{"keyword": "pet water fountain"}'
  python3 niche_evaluator.py '{"keyword": "dog toys"}' --chart ./output/

"""

import json
import os
import sys
import argparse
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


def _fetch_google_trends(keyword: str, region: str = 'US', months: int = 12) -> dict:
    """Fetch Google Trends data for trend momentum scoring."""
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    result = call_api('/googleTrend/getTrendByKeys', {
        'keyword': keyword,
        'region': region,
        'dayRangeStart': start_date.strftime('%Y-%m-%d'),
        'dayRangeEnd': end_date.strftime('%Y-%m-%d')
    })
    if not result:
        return {'trend_score': 50, 'direction': 'STABLE', 'available': False}
    # API returns: {"trendInfoForKeys": [{"keyword": "...", "trendValues": [{"value": "84", ...}]}]}
    trend_info = result.get('trendInfoForKeys', [])
    if trend_info and isinstance(trend_info, list):
        raw_points = trend_info[0].get('trendValues', [])
    else:
        # Fallback for legacy response shapes
        raw_points = result.get('trendValues', result.get('data', result.get('interestOverTime', [])))
    values = []
    for p in raw_points:
        val = p.get('value', p) if isinstance(p, dict) else p
        try:
            values.append(int(val))
        except (ValueError, TypeError):
            pass
    if len(values) < 4:
        return {'trend_score': 50, 'direction': 'STABLE', 'available': False}
    third = max(len(values) // 3, 1)
    o_avg = sum(values[:third]) / third
    r_avg = sum(values[-third:]) / third
    trend_score = int(r_avg)
    direction = 'STABLE'
    if o_avg > 0:
        change = (r_avg - o_avg) / o_avg
        if change > 0.2:
            direction = 'RISING'
        elif change < -0.2:
            direction = 'DECLINING'
    return {'trend_score': trend_score, 'direction': direction, 'available': True}


def _fetch_aba_data(keyword, region='US'):
    """Fetch ABA (Brand Analytics) data via direct API call.

    API returns table format:
    {"tables": [{"data": [{"reportstartdate": "...", "searchFrequencyRank": "485"}, ...]}]}
    """
    try:
        result = call_api('/aba/intelligentQuery', {
            'analysisDescription': f'Get search frequency rank trend for {keyword} over past 12 weeks',
            'region': region
        })
        if not result:
            return None

        # Parse table-format response: tables[0].data contains rows with searchFrequencyRank
        tables = result.get('tables', [])
        if not tables or not isinstance(tables, list):
            # Fallback: try legacy flat response
            sfr = result.get('searchFrequencyRank') or result.get('search_frequency_rank')
            if not sfr:
                return None
            # If legacy format works, continue with it
            tables = None
        else:
            table_data = tables[0].get('data', []) if isinstance(tables[0], dict) else []
            if not table_data:
                return None

            # Extract SFR values from time series (use most recent week)
            sfr = None
            sfr_trend = []
            for row in table_data:
                if isinstance(row, dict):
                    rank = row.get('searchFrequencyRank') or row.get('searchfrequencyrank')
                    if rank is not None:
                        try:
                            sfr_trend.append(int(rank))
                        except (ValueError, TypeError):
                            pass

            # Use the most recent value as current SFR
            if sfr_trend:
                sfr = sfr_trend[-1]
            else:
                return None

        # Classify volume tier based on SFR
        volume_tier = 'UNKNOWN'
        if sfr:
            try:
                sfr_num = int(sfr)
                if sfr_num <= 1000: volume_tier = 'VERY_HIGH'
                elif sfr_num <= 5000: volume_tier = 'HIGH'
                elif sfr_num <= 20000: volume_tier = 'MEDIUM'
                elif sfr_num <= 100000: volume_tier = 'LOW'
                else: volume_tier = 'VERY_LOW'
            except (ValueError, TypeError):
                pass

        # Fetch click share data (separate query for market concentration)
        top_asins = []
        concentration = 'UNKNOWN'
        try:
            cs_result = call_api('/aba/intelligentQuery', {
                'analysisDescription': f'Get top 3 clicked ASINs and click share percentage for keyword {keyword} in the most recent week',
                'region': region
            })
            if cs_result:
                cs_tables = cs_result.get('tables', [])
                if cs_tables and isinstance(cs_tables, list):
                    cs_data = cs_tables[0].get('data', []) if isinstance(cs_tables[0], dict) else []
                    for row in cs_data:
                        if isinstance(row, dict):
                            asin = row.get('clickedasin', row.get('clickedAsin', ''))
                            share_val = row.get('clickShare', row.get('clickshare', 0)) or 0
                            share = float(share_val) * 100 if float(share_val) <= 1 else float(share_val)
                            name = row.get('clickeditemname', row.get('clickedItemName', ''))
                            if asin:
                                top_asins.append({'asin': asin, 'share': round(share, 2), 'title': name[:60] if name else ''})
                    if top_asins:
                        top_share = top_asins[0].get('share', 0)
                        total_top3 = sum(a.get('share', 0) for a in top_asins[:3])
                        if top_share > 30: concentration = 'MONOPOLY'
                        elif total_top3 > 40: concentration = 'CONCENTRATED'
                        else: concentration = 'FRAGMENTED'
        except Exception as e:
            print(f"    ⚠️ ABA click share fetch error: {e}", file=sys.stderr)

        return {
            'search_frequency_rank': sfr,
            'search_volume_tier': volume_tier,
            'market_concentration': {'level': concentration},
            'top_asins': top_asins
        }
    except Exception as e:
        print(f"  ABA fetch error: {e}", file=sys.stderr)
        return None


def _fetch_ebay_sold(keyword):
    """Fetch eBay sold listings via direct API call"""
    try:
        result = call_api('/ebay/search', {
            'keyword': keyword,
            'ebayDomain': 'ebay.com',
            'pageSize': 50,
            'showOnly': 'Sold'
        })
        if not result:
            return None
        products = result.get('products', []) if isinstance(result, dict) else result if isinstance(result, list) else []
        new_items = [p for p in products if (p.get('condition', '') or '').lower() in ('new', '')]
        prices = [p.get('price', 0) or 0 for p in new_items if (p.get('price', 0) or 0) > 0]
        sold_count = len(products)
        if sold_count >= 20: demand_level = 'HIGH'
        elif sold_count >= 10: demand_level = 'MEDIUM'
        elif sold_count > 0: demand_level = 'LOW'
        else: demand_level = 'NONE'
        return {
            'has_sales': sold_count > 0,
            'sold_count': sold_count,
            'demand_level': demand_level,
            'demand_verified': sold_count >= 10,
            'price_range': {'avg': sum(prices) / len(prices) if prices else 0, 'min': min(prices) if prices else 0, 'max': max(prices) if prices else 0}
        }
    except Exception as e:
        print(f"  eBay sold fetch error: {e}", file=sys.stderr)
        return None


def _fetch_tiktok_sales(keyword):
    """Fetch TikTok Shop data via direct API call"""
    try:
        result = call_api('/echotik/listProduct', {
            'keyword': keyword,
            'region': 'US',
            'minTotalSale30dCnt': 50,
            'pageSize': 30
        })
        if not result:
            return None
        products = result.get('products', result.get('data', []))
        if not isinstance(products, list):
            products = []
        product_count = len(products)
        total_sales = sum(int(p.get('totalSale30dCnt', p.get('sales', 0)) or 0) for p in products)
        total_gmv = sum(float(p.get('gmv30d', p.get('revenue', 0)) or 0) for p in products)
        if product_count >= 20 and total_sales >= 1000:
            opportunity, signal = 'HOT', 'Strong social commerce category'
        elif product_count >= 10 and total_sales >= 200:
            opportunity, signal = 'GROWING', 'Emerging social commerce presence'
        elif product_count > 0:
            opportunity, signal = 'EARLY', 'Limited social commerce activity'
        else:
            opportunity, signal = 'NONE', 'No social commerce presence'
        return {
            'has_presence': product_count > 0,
            'product_count': product_count,
            'total_sales': total_sales,
            'estimated_gmv': total_gmv,
            'opportunity': opportunity,
            'signal': signal
        }
    except Exception as e:
        print(f"  TikTok fetch error: {e}", file=sys.stderr)
        return None


def _fetch_keepa_deep(asin, domain=1):
    """Fetch Keepa deep analysis (BSR/seller/price trends) via direct API call"""
    try:
        result = call_api('/keepa/productSeries', {
            'asin': asin,
            'domain': str(domain),
            'days': 90,
            'showBsrMain': 1,
            'showSellerCount': 1,
            'showPrice': 1
        })
        if not result:
            return None

        def _analyze_series(data_key, invert=False):
            series = result.get(data_key, [])
            points = []
            if isinstance(series, list):
                for item in series:
                    if isinstance(item, dict) and 'points' in item:
                        points = [pt.get('y', pt.get('value', 0)) for pt in item['points'] if isinstance(pt, dict)]
                        break
                    elif isinstance(item, (int, float)):
                        points.append(item)
            if len(points) < 6:
                return None
            third = max(len(points) // 3, 1)
            early_avg = sum(points[:third]) / third
            recent_avg = sum(points[-third:]) / third
            if early_avg <= 0:
                return None
            change = (recent_avg - early_avg) / early_avg * 100
            if invert:
                trend = 'IMPROVING' if change < -15 else 'DECLINING' if change > 15 else 'STABLE'
                momentum = 'UP' if change < -10 else 'DOWN' if change > 10 else 'FLAT'
            else:
                trend = 'INCREASING' if change > 15 else 'DECREASING' if change < -15 else 'STABLE'
                momentum = 'UP' if change > 10 else 'DOWN' if change < -10 else 'FLAT'
            return {'trend': trend, 'momentum': momentum, 'change_pct': round(change, 1), 'current': round(recent_avg, 1)}

        bsr_data = _analyze_series('bsrMain', invert=True)
        seller_data = _analyze_series('sellerCount')
        price_data = _analyze_series('price')

        bsr = {}
        if bsr_data:
            bsr = {'trend': bsr_data['trend'], 'momentum': bsr_data['momentum'],
                   'sales_signal': 'STRONG' if bsr_data['trend'] == 'IMPROVING' else 'WEAK' if bsr_data['trend'] == 'DECLINING' else 'NEUTRAL'}
        sellers = {}
        if seller_data:
            current = seller_data['current']
            sellers = {'current': int(current), 'trend': seller_data['trend'],
                       'competition_signal': 'INTENSIFYING' if seller_data['trend'] == 'INCREASING' else 'EASING' if seller_data['trend'] == 'DECREASING' else 'STABLE',
                       'buybox_difficulty': 'HARD' if current > 10 else 'MEDIUM' if current > 5 else 'EASY'}
        price = {}
        if price_data:
            price = {'volatility_pct': abs(price_data['change_pct']), 'price_war_risk': 'HIGH' if price_data['trend'] == 'DECREASING' else 'LOW'}
        seasonality = {'detected': False, 'peak_months': []}
        if bsr_data and abs(bsr_data.get('change_pct', 0)) > 30:
            seasonality['detected'] = True
        return {'bsr': bsr, 'sellers': sellers, 'price': price, 'seasonality': seasonality}
    except Exception as e:
        print(f"  Keepa deep fetch error: {e}", file=sys.stderr)
        return None


def calculate_niche_score(market_data):
    """
    Calculate Niche Score (0-100)
    Demand(25) + Competition(25) + Profit(25) + Opportunity(25)
    """
    # Demand Score (0-25)
    search_volume = market_data.get('search_volume', 0)
    monthly_sales = market_data.get('total_monthly_sales', 0)
    
    if search_volume > 50000 or monthly_sales > 100000: demand = 25
    elif search_volume > 20000 or monthly_sales > 50000: demand = 20
    elif search_volume > 10000 or monthly_sales > 20000: demand = 15
    elif search_volume > 5000 or monthly_sales > 10000: demand = 10
    else: demand = 5
    
    # Competition Score (0-25) - lower competition = higher score
    avg_reviews = market_data.get('avg_reviews', 500)
    top3_share = market_data.get('top3_market_share', 50)
    
    if avg_reviews < 100 and top3_share < 30: comp = 25
    elif avg_reviews < 200 and top3_share < 40: comp = 20
    elif avg_reviews < 500 and top3_share < 50: comp = 15
    elif avg_reviews < 1000 and top3_share < 60: comp = 10
    else: comp = 5
    
    # Profit Score (0-25)
    avg_price = market_data.get('avg_price', 30)
    
    if 30 <= avg_price <= 80: profit = 25
    elif 20 <= avg_price <= 100: profit = 20
    elif 15 <= avg_price <= 150: profit = 15
    else: profit = 10
    
    # Opportunity Score (0-25)
    avg_rating = market_data.get('avg_rating', 4.5)
    low_rating_pct = market_data.get('low_rating_pct', 0)
    
    if avg_rating < 4.0 or low_rating_pct > 30: opp = 25
    elif avg_rating < 4.2 or low_rating_pct > 20: opp = 20
    elif avg_rating < 4.4 or low_rating_pct > 10: opp = 15
    else: opp = 10
    
    total = demand + comp + profit + opp
    
    # Grade
    if total >= 80: grade = 'A'
    elif total >= 70: grade = 'B+'
    elif total >= 60: grade = 'B'
    elif total >= 50: grade = 'C+'
    elif total >= 40: grade = 'C'
    else: grade = 'D'
    
    return {
        'total_score': total,
        'grade': grade,
        'demand': demand,
        'competition': comp,
        'profit': profit,
        'opportunity': opp,
        'raw_metrics': market_data
    }


def get_recommendation(grade):
    recommendations = {
        'A': {'status': 'Highly Recommended', 'action': 'Strong opportunity - proceed with product research'},
        'B+': {'status': 'Recommended', 'action': 'Good potential - find differentiation angle'},
        'B': {'status': 'Viable', 'action': 'Moderate opportunity - needs clear USP'},
        'C+': {'status': 'Caution', 'action': 'Challenging market - requires strong execution'},
        'C': {'status': 'Not Recommended', 'action': 'High competition or limited demand'},
        'D': {'status': 'Avoid', 'action': 'Poor market conditions'}
    }
    return recommendations.get(grade, recommendations['C'])


# === Chart Analysis ===
def generate_chart_analysis(result):
    """Generate analytical text for each chart"""
    analysis = {}
    scores = result.get('scores', {})
    market_data = result.get('market_data', {})
    keyword = result.get('keyword', 'niche')
    
    # Chart 1: Score Gauge Analysis
    lines = ["**📊 Niche Score Analysis:**"]
    total = scores.get('total_score', 0)
    grade = scores.get('grade', 'C')
    
    dims = [
        ('Demand', scores.get('demand', 0), 25),
        ('Competition', scores.get('competition', 0), 25),
        ('Profit', scores.get('profit', 0), 25),
        ('Opportunity', scores.get('opportunity', 0), 25)
    ]
    
    strongest = max(dims, key=lambda x: x[1]/x[2])
    weakest = min(dims, key=lambda x: x[1]/x[2])
    
    lines.append(f"- Total: **{total}/100** (Grade: {grade})")
    lines.append(f"- ✅ Strength: {strongest[0]} ({strongest[1]}/{strongest[2]})")
    lines.append(f"- ⚠️ Weakness: {weakest[0]} ({weakest[1]}/{weakest[2]})")
    
    if grade in ['A', 'B+']:
        lines.append("- 🟢 Recommended: Strong market opportunity")
    elif grade in ['B', 'C+']:
        lines.append("- 🟡 Moderate: Proceed with caution")
    else:
        lines.append("- 🔴 Not recommended: High risk market")
    analysis['gauge'] = "\n".join(lines)
    
    # Chart 2: Market Analysis
    lines = ["**📈 Market Overview:**"]
    if market_data:
        lines.append(f"- Avg Price: ${market_data.get('avg_price', 0):.2f}")
        lines.append(f"- Avg Reviews: {market_data.get('avg_reviews', 0):.0f}")
        lines.append(f"- Monthly Sales: {market_data.get('total_monthly_sales', 0):,}")
        
        low_rating = market_data.get('low_rating_pct', 0)
        if low_rating > 20:
            lines.append(f"- ✅ Quality gap: {low_rating:.0f}% products under 4.0 stars (opportunity!)")
        else:
            lines.append(f"- Competition well-rated: Only {low_rating:.0f}% under 4.0 stars")
    analysis['market'] = "\n".join(lines)
    
    # Chart 3: Radar Analysis
    lines = ["**🎯 Competitive Position:**"]
    demand_pct = scores.get('demand', 0) / 25 * 100
    comp_pct = scores.get('competition', 0) / 25 * 100
    
    if demand_pct >= 70 and comp_pct >= 60:
        lines.append("- ✅ Blue Ocean potential: High demand + Low competition")
    elif demand_pct >= 70:
        lines.append("- 🟡 High demand but competitive market")
    elif comp_pct >= 70:
        lines.append("- 🟡 Low competition but limited demand")
    else:
        lines.append("- ⚠️ Challenging market conditions")
    analysis['radar'] = "\n".join(lines)
    
    return analysis


# === Chart Generation ===
def generate_charts(result, output_dir):
    """Generate niche evaluation charts"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not installed, skipping charts", file=sys.stderr)
        return [], {}
    
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    chart_analysis = generate_chart_analysis(result)
    
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    keyword = result.get('keyword', 'niche')
    scores = result.get('scores', {})

    # Chart 1: Niche Score Gauge
    if not scores or scores.get('total_score', 0) == 0:
        print("  ⚠️ waterfall_chart.png skipped: no scores available", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(8, 6))
    
    total = scores.get('total_score', 0)
    grade = scores.get('grade', 'C')
    
    # Create gauge-like visualization
    categories = ['Demand', 'Competition', 'Profit', 'Opportunity']
    values = [scores.get('demand', 0), scores.get('competition', 0), 
              scores.get('profit', 0), scores.get('opportunity', 0)]
    max_val = 25
    
    colors = [get_color('primary'), get_color('good'), get_color('secondary'), get_color('secondary')]
    y_pos = np.arange(len(categories))
    
    ax.barh(y_pos, [max_val]*4, height=0.6, color='#333', alpha=0.5)
    bars = ax.barh(y_pos, values, height=0.6, color=colors)
    
    for i, (v, c) in enumerate(zip(values, categories)):
        ax.text(v + 0.5, i, f'{v}/{max_val}', va='center', fontsize=11, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=11)
    ax.set_xlim(0, 30)
    ax.set_xlabel('Score', fontsize=10)
    
    grade_color = get_color('good') if grade in ['A', 'B+'] else get_color('warning') if grade in ['B', 'C+'] else get_color('hot')
    ax.set_title(f'Niche Evaluation: {keyword}\nTotal: {total}/100 | Grade: {grade}',
                 fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'waterfall_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)
    
    # Chart 2: Market Metrics Overview
    market_data = result.get('market_data', {})
    if market_data:
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        
        # Price distribution
        ax1 = axes[0, 0]
        prices = market_data.get('price_distribution', [20, 30, 40, 50, 30, 20])
        ax1.bar(range(len(prices)), prices, color=get_color('primary'), alpha=0.8)
        ax1.set_title('Price Distribution', fontsize=11)
        ax1.set_xlabel('Price Range')
        ax1.set_ylabel('Products')
        
        # Review distribution
        ax2 = axes[0, 1]
        reviews = market_data.get('review_distribution', {'<100': 30, '100-500': 25, '500-1K': 20, '>1K': 25})
        ax2.pie(reviews.values(), labels=reviews.keys(), autopct='%1.0f%%', colors=[get_color('good'), get_color('primary'), get_color('secondary'), get_color('hot')])
        ax2.set_title('Review Distribution', fontsize=11)
        
        # Rating distribution
        ax3 = axes[1, 0]
        ratings = market_data.get('rating_distribution', {'4.5+': 40, '4.0-4.5': 35, '3.5-4.0': 15, '<3.5': 10})
        bars = ax3.bar(ratings.keys(), ratings.values(), color=[get_color('good'), get_color('primary'), get_color('warning'), get_color('hot')])
        ax3.set_title('Rating Distribution', fontsize=11)
        ax3.set_ylabel('% Products')
        
        # BSR distribution
        ax4 = axes[1, 1]
        bsr = market_data.get('bsr_distribution', {'Top 10K': 20, '10K-50K': 35, '50K-100K': 25, '>100K': 20})
        ax4.barh(list(bsr.keys()), list(bsr.values()), color=get_color('secondary'), alpha=0.8)
        ax4.set_title('BSR Distribution', fontsize=11)
        ax4.set_xlabel('% Products')
        
        plt.suptitle(f'Market Analysis: {keyword}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'price_segment.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    
    # Chart 3: Competition Radar
    if not scores:
        print("  ⚠️ radar_chart.png skipped: no scores available", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    categories = ['Demand', 'Low Competition', 'Profit Margin', 'Quality Gap', 'Entry Barrier']
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    # Normalize scores to 0-100
    values = [
        scores.get('demand', 0) / 25 * 100,
        scores.get('competition', 0) / 25 * 100,
        scores.get('profit', 0) / 25 * 100,
        scores.get('opportunity', 0) / 25 * 100,
        70  # Entry barrier estimate
    ]
    values += values[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, color=get_color('good'))
    ax.fill(angles, values, alpha=0.25, color=get_color('good'))
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 100)
    ax.set_title(f'Niche Radar: {keyword}', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'radar_chart.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)

    # Chart 4: Comparison Matrix — dimension breakdown for this niche
    if not scores or all(v == 0 for v in [scores.get('demand', 0), scores.get('competition', 0), scores.get('profit', 0), scores.get('opportunity', 0)]):
        print("  ⚠️ comparison.png skipped: all dimension scores are zero", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(9, 5))

    dimensions = ['Demand', 'Competition', 'Profit', 'Opportunity']
    dim_values = [
        scores.get('demand', 0),
        scores.get('competition', 0),
        scores.get('profit', 0),
        scores.get('opportunity', 0),
    ]
    max_val = 25
    normalized = [v / max_val * 100 for v in dim_values]

    bar_colors = [get_color('primary'), get_color('good'), get_color('secondary'), get_color('secondary')]
    bars = ax.bar(dimensions, normalized, color=bar_colors, edgecolor='white', linewidth=1.5, alpha=0.9)

    for bar, raw, pct in zip(bars, dim_values, normalized):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f'{raw}/{max_val}\n({pct:.0f}%)', ha='center', va='bottom', fontsize=10)

    ax.set_ylim(0, 115)
    ax.set_ylabel('Score (%)', fontsize=10)
    ax.set_title(f'Dimension Comparison: {keyword}', fontsize=14, fontweight='bold', pad=15)
    ax.axhline(y=60, color=get_color('warning'), linestyle='--', linewidth=1, alpha=0.6, label='60% threshold')
    ax.legend(fontsize=9)

    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'comparison.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)

    return charts, chart_analysis


def run_evaluator(params):
    keyword = params.get('keyword', '')
    marketplace = params.get('marketplace', 'amazon.com')
    
    if not keyword:
        return {"error": "keyword required"}
    
    # Get market data
    try:
        search_data = call_api("/amazon/search", {
            "keyword": keyword,
            "amazonDomain": marketplace
        })
        products = (search_data or {}).get('products', [])
    except Exception as e:
        return {"error": str(e)}
    
    if not products:
        return {"error": "No products found", "keyword": keyword}
    
    # Aggregate market data
    prices = [p.get('price', 0) for p in products if p.get('price')]
    reviews = [p.get('ratings', 0) or 0 for p in products]
    ratings = [p.get('rating', 0) for p in products if p.get('rating')]
    sales = [int(p.get('monthlySalesUnits', 0) or 0) for p in products]
    
    # Fetch real search volume from Jungle Scout
    js_kw_result = js_api_call('/keywords/by-keyword', {
        'searchTerms': keyword,
        'marketplace': marketplace.lower() if marketplace else 'us'
    })
    search_volume = 10000  # fallback
    if js_kw_result and isinstance(js_kw_result, dict):
        kw_list = js_kw_result.get('data', [])
        if kw_list and isinstance(kw_list, list):
            attrs = kw_list[0].get('attributes', {}) if isinstance(kw_list[0], dict) else {}
            search_volume = attrs.get('monthlySearchVolumeExact', 10000) or 10000

    market_data = {
        'keyword': keyword,
        'product_count': len(products),
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'avg_reviews': sum(reviews) / len(reviews) if reviews else 0,
        'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
        'total_monthly_sales': sum(sales),
        'search_volume': search_volume,
        'top3_market_share': 40,  # Estimate
        'low_rating_pct': len([r for r in ratings if r < 4.0]) / len(ratings) * 100 if ratings else 0,
        'price_distribution': [len([p for p in prices if i*20 <= p < (i+1)*20]) for i in range(6)],
        'review_distribution': {
            '<100': len([r for r in reviews if r < 100]),
            '100-500': len([r for r in reviews if 100 <= r < 500]),
            '500-1K': len([r for r in reviews if 500 <= r < 1000]),
            '>1K': len([r for r in reviews if r >= 1000])
        },
        'rating_distribution': {
            '4.5+': len([r for r in ratings if r >= 4.5]) / len(ratings) * 100 if ratings else 0,
            '4.0-4.5': len([r for r in ratings if 4.0 <= r < 4.5]) / len(ratings) * 100 if ratings else 0,
            '3.5-4.0': len([r for r in ratings if 3.5 <= r < 4.0]) / len(ratings) * 100 if ratings else 0,
            '<3.5': len([r for r in ratings if r < 3.5]) / len(ratings) * 100 if ratings else 0
        }
    }
    
    scores = calculate_niche_score(market_data)
    rec = get_recommendation(scores['grade'])
    
    result = {
        'keyword': keyword,
        'marketplace': marketplace,
        'scores': scores,
        'market_data': market_data,
        'recommendation': rec,
        'top_products': [{
            'asin': p.get('asin'),
            'title': p.get('title', '')[:60],
            'price': p.get('price'),
            'reviews': p.get('ratings'),
            'rating': p.get('rating')
        } for p in products[:5]]
    }
    
    # === Enhanced Data Sources (v2.0.0) ===
    result['cross_validation'] = {}
    enhanced_insights = []
    score_adjustment = 0

    # Google Trends (trend momentum)
    print("[+] Fetching Google Trends data...", file=sys.stderr)
    try:
        region = 'US'
        google_trends = _fetch_google_trends(keyword, region=region)
        trend_score = google_trends.get('trend_score', 50)
        trend_direction = google_trends.get('direction', 'STABLE')
        result['cross_validation']['google_trends'] = {
            'trend_score': trend_score,
            'direction': trend_direction,
            'available': google_trends.get('available', False)
        }
        if trend_direction == 'RISING':
            enhanced_insights.append('📈 Google Trends: Rising interest')
            score_adjustment += 5
        elif trend_direction == 'DECLINING':
            enhanced_insights.append('📉 Google Trends: Declining interest')
            score_adjustment -= 5
        else:
            enhanced_insights.append('➡️ Google Trends: Stable interest')
    except Exception as e:
        print(f"    ⚠️ Google Trends: {e}", file=sys.stderr)
        google_trends = {'trend_score': 50, 'direction': 'STABLE', 'available': False}

    # ABA Data
    print("[+] Fetching ABA data...", file=sys.stderr)
    try:
        aba = _fetch_aba_data(keyword)
        if aba and 'error' not in aba:
            result['cross_validation']['aba'] = {
                'sfr': aba.get('search_frequency_rank'),
                'volume_tier': aba.get('search_volume_tier'),
                'concentration': (aba.get('market_concentration') or {}).get('level')
            }
            if aba.get('search_volume_tier') in ['VERY_HIGH', 'HIGH']:
                enhanced_insights.append('✅ ABA confirms strong search demand')
                score_adjustment += 5
            if (aba.get('market_concentration') or {}).get('level') == 'FRAGMENTED':
                enhanced_insights.append('🎯 Fragmented market - easier entry')
                score_adjustment += 5
            elif (aba.get('market_concentration') or {}).get('level') == 'MONOPOLY':
                enhanced_insights.append('⚠️ Market dominated by 1 player')
                score_adjustment -= 10
    except Exception as e:
        print(f"    ⚠️ ABA: {e}", file=sys.stderr)

    # eBay Sold
    print("[+] Fetching eBay sold data...", file=sys.stderr)
    try:
        ebay = _fetch_ebay_sold(keyword)
        if ebay and ebay.get('has_sales'):
            result['cross_validation']['ebay'] = {
                'sold_count': ebay.get('sold_count'),
                'demand_level': ebay.get('demand_level'),
                'verified': ebay.get('demand_verified')
            }
            if ebay.get('demand_verified'):
                enhanced_insights.append('✅ eBay confirms real demand')
                score_adjustment += 5
        else:
            enhanced_insights.append('⚠️ Low eBay activity - verify demand')
    except Exception as e:
        print(f"    ⚠️ eBay: {e}", file=sys.stderr)

    # TikTok
    print("[+] Fetching TikTok data...", file=sys.stderr)
    try:
        tiktok = _fetch_tiktok_sales(keyword)
        if tiktok and tiktok.get('has_presence'):
            result['cross_validation']['tiktok'] = {
                'sales': tiktok.get('total_sales'),
                'opportunity': tiktok.get('opportunity')
            }
            if tiktok.get('opportunity') in ['HOT', 'GROWING']:
                enhanced_insights.append(f"📱 TikTok: {tiktok.get('opportunity')}")
                score_adjustment += 3
    except Exception as e:
        print(f"    ⚠️ TikTok: {e}", file=sys.stderr)

    # Keepa Deep (for top product)
    if products:
        top_asin = products[0].get('asin')
        if top_asin:
            print(f"[+] Fetching Keepa deep for {top_asin}...", file=sys.stderr)
            try:
                keepa = _fetch_keepa_deep(top_asin)
                if keepa and 'error' not in keepa:
                    result['cross_validation']['keepa'] = {
                        'bsr_trend': (keepa.get('bsr') or {}).get('trend'),
                        'seasonality': (keepa.get('seasonality') or {}).get('detected'),
                        'peak_months': (keepa.get('seasonality') or {}).get('peak_months', []),
                        'competition': (keepa.get('sellers') or {}).get('competition_signal')
                    }
                    if (keepa.get('bsr') or {}).get('trend') == 'IMPROVING':
                        enhanced_insights.append('📈 Market growing (BSR improving)')
                        score_adjustment += 5
                    if (keepa.get('seasonality') or {}).get('detected'):
                        peaks = ', '.join((keepa.get('seasonality') or {}).get('peak_months', []))
                        enhanced_insights.append(f'📅 Seasonal: peaks {peaks}')
                    if (keepa.get('sellers') or {}).get('competition_signal') == 'INTENSIFYING':
                        enhanced_insights.append('⚠️ Competition intensifying')
                        score_adjustment -= 5
            except Exception as e:
                print(f"    ⚠️ Keepa: {e}", file=sys.stderr)

    # Apply score adjustment
    if enhanced_insights and 'total_score' in scores:
        adjusted_score = min(100, max(0, scores['total_score'] + score_adjustment))
        result['enhanced_evaluation'] = {
            'original_score': scores['total_score'],
            'adjusted_score': adjusted_score,
            'adjustment': score_adjustment,
            'insights': enhanced_insights,
            'sources_checked': list(result['cross_validation'].keys())
        }

    # Add google_trends as top-level key for easy access
    result['google_trends'] = result['cross_validation'].get('google_trends', {
        'trend_score': 50, 'direction': 'STABLE', 'available': False
    })

    return result


def main():
    parser = argparse.ArgumentParser(description='Niche Evaluator')
    parser.add_argument('params', help='JSON parameters: {"keyword": "pet water fountain"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to specified directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = run_evaluator(params)
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
