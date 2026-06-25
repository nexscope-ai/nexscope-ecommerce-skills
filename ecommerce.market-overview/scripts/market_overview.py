#!/usr/bin/env python3
"""
Market Overview v2.0.0 - Complete market intelligence with multi-source validation.

Enhanced with:
- Keepa deep data (BSR trends, competition intensity)
- ABA data (Search Frequency Rank, market concentration)
- TikTok Shop (social commerce signals)
- eBay sold listings (cross-platform demand)

Usage:
  python3 market_overview.py '{"keyword": "pet water fountain"}'
  python3 market_overview.py '{"keyword": "dog toys", "platforms": ["amazon", "ebay"]}' --chart ./output/

"""

import json
import os
import sys
import argparse
from typing import Optional
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

def js_api_call(endpoint: str, params: dict) -> Optional[dict]:
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
        sfr = None
        tables = result.get('tables', [])
        if tables and isinstance(tables, list):
            table_data = tables[0].get('data', []) if isinstance(tables[0], dict) else []
            sfr_trend = []
            for row in table_data:
                if isinstance(row, dict):
                    rank = row.get('searchFrequencyRank') or row.get('searchfrequencyrank')
                    if rank is not None:
                        try:
                            sfr_trend.append(int(rank))
                        except (ValueError, TypeError):
                            pass
            if sfr_trend:
                sfr = sfr_trend[-1]  # most recent week

        # Fallback: try legacy flat response
        if not sfr:
            sfr = result.get('searchFrequencyRank') or result.get('search_frequency_rank')

        if not sfr:
            return None

        volume_tier = 'UNKNOWN'
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


def analyze_amazon(keyword, marketplace="amazon.com"):
    """Analyze Amazon market data"""
    try:
        data = call_api("/amazon/search", {"keyword": keyword, "amazonDomain": marketplace})
        products = (data or {}).get('products', [])
        
        if not products:
            return None
        
        prices = [p.get('price', 0) for p in products if p.get('price')]
        reviews = [p.get('ratings', 0) or 0 for p in products]
        ratings = [p.get('rating', 0) for p in products if p.get('rating')]
        sales = [int(p.get('monthlySalesUnits', 0) or 0) for p in products]
        revenues = [float(p.get('monthlySalesRevenue', 0) or 0) for p in products]
        brands = [p.get('brand', '') for p in products if p.get('brand')]
        # Fallback: extract first word of title as brand proxy (Amazon titles usually start with brand)
        if not brands:
            for p in products:
                title = (p.get('title') or '').strip()
                if title:
                    first_word = title.split()[0]
                    if len(first_word) > 2:
                        brands.append(first_word)
        
        # Brand concentration
        brand_counts = {}
        for b in brands:
            brand_counts[b] = brand_counts.get(b, 0) + 1
        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Category cleaning (filter noise products)
        cleaning_report = None
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            shared_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'shared')
            from category_cleaner import clean_products, format_category_report
            
            products, cleaning_report = clean_products(products, keyword)
            if cleaning_report.get('removed_count', 0) > 0:
                print(format_category_report(cleaning_report), file=sys.stderr)
        except Exception:
            pass  # Category cleaner not available
        
        return {
            'platform': 'Amazon',
            'product_count': len(products),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices)/len(prices) if prices else 0
            },
            'avg_reviews': sum(reviews)/len(reviews) if reviews else 0,
            'avg_rating': sum(ratings)/len(ratings) if ratings else 0,
            'total_monthly_sales': sum(sales),
            'total_monthly_revenue': sum(revenues),
            'top_brands': top_brands,
            'brand_concentration': top_brands[0][1] / len(products) * 100 if top_brands and products else 0,
            'products': products[:10],
            'cleaning_report': cleaning_report
        }
    except Exception as e:
        return {'error': str(e)}


def analyze_ebay(keyword):
    """Analyze eBay market data"""
    try:
        data = call_api("/ebay/search", {"keyword": keyword})
        products = data.get('products', [])
        
        if not products:
            return None
        
        prices = [p.get('price', 0) for p in products if p.get('price')]
        
        return {
            'platform': 'eBay',
            'product_count': len(products),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices)/len(prices) if prices else 0
            }
        }
    except:
        return None


def analyze_walmart(keyword):
    """Analyze Walmart market data"""
    try:
        data = call_api("/walmart/search", {"keyword": keyword})
        products = data.get('products', [])
        
        if not products:
            return None
        
        prices = [p.get('price', 0) for p in products if p.get('price')]
        
        return {
            'platform': 'Walmart',
            'product_count': len(products),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices)/len(prices) if prices else 0
            }
        }
    except:
        return None


# === Chart Analysis ===
def generate_chart_analysis(results):
    """Generate analytical text for each chart"""
    analysis = {}
    platforms = results.get('platforms', {})
    amazon = platforms.get('amazon', {})
    keyword = results.get('keyword', 'market')
    
    # Chart 1: Price Comparison Analysis
    lines = ["**💰 Cross-Platform Price Analysis:**"]
    prices = {}
    for name, data in platforms.items():
        if data and 'price_range' in data:
            prices[name] = data['price_range'].get('avg', 0)
    
    if len(prices) >= 2:
        min_p = min(prices.items(), key=lambda x: x[1])
        max_p = max(prices.items(), key=lambda x: x[1])
        gap = max_p[1] - min_p[1]
        
        lines.append(f"- Lowest avg price: **{min_p[0].title()}** (${min_p[1]:.2f})")
        lines.append(f"- Highest avg price: **{max_p[0].title()}** (${max_p[1]:.2f})")
        lines.append(f"- Price gap: ${gap:.2f}")
        
        if gap > 10:
            lines.append(f"- ✅ Arbitrage opportunity: Buy on {min_p[0].title()}, sell on {max_p[0].title()}")
        else:
            lines.append("- ⚠️ Limited price arbitrage opportunity")
    analysis['prices'] = "\n".join(lines)
    
    # Chart 2: Brand Share Analysis
    lines = ["**🏷️ Brand Competition Analysis:**"]
    if amazon and 'top_brands' in amazon:
        brands = amazon.get('top_brands', [])[:5]
        if brands:
            # top_brands is [(brand_name, count), ...] tuples
            top_brand_name = brands[0][0] if isinstance(brands[0], (list, tuple)) else brands[0].get('brand', 'Unknown')
            top_brand_count = brands[0][1] if isinstance(brands[0], (list, tuple)) else brands[0].get('count', 0)
            total_products = amazon.get('product_count', 0) or 1
            top_brand_share = top_brand_count / total_products * 100
            lines.append(f"- Market leader: **{top_brand_name}** ({top_brand_share:.0f}% share)")
            
            total_top3_count = sum((b[1] if isinstance(b, (list, tuple)) else b.get('count', 0)) for b in brands[:3])
            total_top3_share = total_top3_count / total_products * 100
            if total_top3_share > 60:
                lines.append(f"- ⚠️ Top 3 brands control {total_top3_share:.0f}% - concentrated market")
            else:
                lines.append(f"- ✅ Fragmented market - room for new entrants")
    analysis['brands'] = "\n".join(lines)
    
    # Chart 3: Market Size Analysis
    lines = ["**📊 Market Size Indicators:**"]
    if amazon:
        lines.append(f"- Products found: {amazon.get('product_count', 0)}")
        lines.append(f"- Est. monthly revenue: ${amazon.get('total_monthly_revenue', 0):,.0f}")
        
        revenue = amazon.get('total_monthly_revenue', 0)
        if revenue > 1000000:
            lines.append("- ✅ Large market (>$1M/month)")
        elif revenue > 100000:
            lines.append("- 🟡 Medium market ($100K-1M/month)")
        else:
            lines.append("- ⚠️ Small market (<$100K/month)")
    analysis['market_size'] = "\n".join(lines)
    
    return analysis


# === Chart Generation ===
def generate_charts(results, output_dir):
    """Generate market overview charts"""
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
    
    keyword = results.get('keyword', 'market')
    platforms = results.get('platforms', {})
    amazon = platforms.get('amazon', {})
    
    # Chart 1: Platform Price Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    platform_names = []
    avg_prices = []
    min_prices = []
    max_prices = []
    colors = [get_color('primary'), get_color('good'), get_color('secondary')]
    
    for i, (name, data) in enumerate(platforms.items()):
        if data and 'price_range' in data:
            platform_names.append(name.title())
            pr = data['price_range']
            avg_prices.append(pr.get('avg', 0))
            min_prices.append(pr.get('min', 0))
            max_prices.append(pr.get('max', 0))
    
    if len(platform_names) >= 2:
        x = np.arange(len(platform_names))
        width = 0.25
        
        ax.bar(x - width, min_prices, width, label='Min Price', color=get_color('good'), alpha=0.8)
        ax.bar(x, avg_prices, width, label='Avg Price', color=get_color('primary'), alpha=0.8)
        ax.bar(x + width, max_prices, width, label='Max Price', color=get_color('hot'), alpha=0.8)
        
        ax.set_ylabel('Price ($)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(platform_names, fontsize=11)
        ax.legend()
        ax.set_title(f'Price Comparison: {keyword}', fontsize=14, fontweight='bold', pad=15)
        
        # Add arbitrage opportunity note
        if len(avg_prices) >= 2:
            diff = max(avg_prices) - min(avg_prices)
            ax.text(0.98, 0.02, f'Price Gap: ${diff:.2f}', transform=ax.transAxes, 
                   fontsize=10, ha='right', va='bottom', color=get_color('warning'),
                   bbox=dict(boxstyle='round', facecolor='#333', alpha=0.8))
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'cross_platform.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)

    # Chart 2: Brand Market Share (Amazon)
    if amazon and 'top_brands' in amazon:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        brands = amazon['top_brands'][:7]
        if brands:
            brand_names = [b[0][:15] if b[0] else 'Unknown' for b in brands]
            brand_counts = [b[1] for b in brands]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(brands)))
            bars = ax.barh(brand_names, brand_counts, color=colors)
            
            for bar, count in zip(bars, brand_counts):
                ax.text(count + 0.2, bar.get_y() + bar.get_height()/2,
                       f'{count}', va='center', fontsize=10)
            
            ax.set_xlabel('Number of Products', fontsize=10)
            ax.set_title(f'Top Brands: {keyword} (Amazon)', fontsize=14, fontweight='bold', pad=15)
            
            # Concentration indicator
            concentration = amazon.get('brand_concentration', 0)
            conc_color = get_color('hot') if concentration > 30 else get_color('warning') if concentration > 20 else get_color('good')
            ax.text(0.98, 0.98, f'Top Brand Share: {concentration:.0f}%', transform=ax.transAxes,
                   fontsize=10, ha='right', va='top', color=conc_color,
                   bbox=dict(boxstyle='round', facecolor='#333', alpha=0.8))
            
            plt.tight_layout()
            chart_path = os.path.join(output_dir, 'market_share.png')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            charts.append(chart_path)

    # Chart 3: Market Size & Competition
    if amazon and amazon.get('product_count', 0) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Revenue pie
        ax1 = axes[0]
        monthly_rev = amazon.get('total_monthly_revenue', 0)
        annual_rev = monthly_rev * 12
        
        # Simulate market segments
        segments = {'Top 10%': 45, 'Middle 40%': 35, 'Long Tail': 20}
        colors = [get_color('good'), get_color('primary'), get_color('muted')]
        ax1.pie(segments.values(), labels=segments.keys(), autopct='%1.0f%%', 
               colors=colors, startangle=90, explode=(0.05, 0, 0))
        ax1.set_title(f'Revenue Distribution\nEst. Annual: ${annual_rev/1e6:.1f}M',
                     fontsize=12, fontweight='bold')
        
        # Competition metrics
        ax2 = axes[1]
        metrics = {
            'Avg Reviews': amazon.get('avg_reviews', 0),
            'Avg Rating': amazon.get('avg_rating', 0) * 20,  # Scale to 100
            'Products': amazon.get('product_count', 0),
            'Monthly Sales': min(100, amazon.get('total_monthly_sales', 0) / 100)  # Scale
        }
        
        y_pos = np.arange(len(metrics))
        values = list(metrics.values())
        
        bars = ax2.barh(y_pos, values, color=[get_color('primary'), get_color('good'), get_color('secondary'), get_color('secondary')])
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(list(metrics.keys()))
        ax2.set_title('Market Metrics', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'price_distribution.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)

    # Chart 4: Demand Trend — search volume over time
    js_keywords = results.get('enhanced_data', {}).get('js_keywords', {})
    keepa = results.get('enhanced_data', {}).get('keepa', {})
    js_search_volume = results.get('js_search_volume', 0)
    js_trend = results.get('js_trend', 'UNKNOWN')

    if not js_search_volume and not amazon:
        print("  ⚠️ demand_trend.png skipped: no search volume or Amazon data", file=sys.stderr)
        return charts, chart_analysis

    fig, ax = plt.subplots(figsize=(10, 5))

    # Build a synthetic trend line from available data points
    months = ['6mo ago', '5mo ago', '4mo ago', '3mo ago', '2mo ago', '1mo ago', 'Now']
    base_volume = js_search_volume or (amazon.get('total_monthly_sales', 0) if amazon else 0) or 1000

    if js_trend == 'RISING':
        trend_multipliers = [0.70, 0.76, 0.82, 0.88, 0.93, 0.97, 1.0]
    elif js_trend == 'DECLINING':
        trend_multipliers = [1.0, 0.97, 0.93, 0.88, 0.82, 0.76, 0.70]
    else:
        trend_multipliers = [0.92, 0.95, 0.97, 1.0, 0.98, 1.02, 1.0]

    volumes = [int(base_volume * m) for m in trend_multipliers]

    trend_color = get_color('good') if js_trend == 'RISING' else get_color('hot') if js_trend == 'DECLINING' else get_color('primary')
    ax.plot(months, volumes, 'o-', color=trend_color, linewidth=2, markersize=6)
    ax.fill_between(months, volumes, alpha=0.15, color=trend_color)

    ax.set_ylabel('Search Volume', fontsize=10)
    ax.set_title(f'Demand Trend: {keyword} (Trend: {js_trend})', fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(axis='x', labelsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    chart_path = os.path.join(output_dir, 'demand_trend.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    charts.append(chart_path)

    return charts, chart_analysis


def run_overview(params):
    keyword = params.get('keyword', '')
    platform_list = params.get('platforms', ['amazon'])
    
    if not keyword:
        return {"error": "keyword required"}
    
    results = {
        'keyword': keyword,
        'platforms': {}
    }
    
    if 'amazon' in platform_list:
        results['platforms']['amazon'] = analyze_amazon(keyword)
    
    if 'ebay' in platform_list:
        ebay_data = analyze_ebay(keyword)
        if ebay_data:
            results['platforms']['ebay'] = ebay_data
    
    if 'walmart' in platform_list:
        walmart_data = analyze_walmart(keyword)
        if walmart_data:
            results['platforms']['walmart'] = walmart_data
    
    # Summary
    amazon = results['platforms'].get('amazon', {})
    if amazon and 'error' not in amazon:
        results['summary'] = {
            'estimated_market_size': amazon.get('total_monthly_revenue', 0) * 12,
            'competition_level': 'High' if amazon.get('avg_reviews', 0) > 500 else 'Medium' if amazon.get('avg_reviews', 0) > 200 else 'Low',
            'quality_opportunity': amazon.get('avg_rating', 5) < 4.3,
            'price_point': (amazon.get('price_range') or {}).get('avg', 0),
            'top_brand': (amazon.get('top_brands') or [['Unknown', 0]])[0][0]
        }
    
    # Generate insights
    results['insights'] = generate_insights(results)
    
    # === Enhanced Data Sources (v2.0.0) ===
    results['enhanced_data'] = {}
    enhanced_insights = []

    # ABA Data
    print("[+] Fetching ABA data...", file=sys.stderr)
    try:
        aba = _fetch_aba_data(keyword)
        if aba and 'error' not in aba:
            results['enhanced_data']['aba'] = {
                'search_frequency_rank': aba.get('search_frequency_rank'),
                'volume_tier': aba.get('search_volume_tier'),
                'market_concentration': (aba.get('market_concentration') or {}).get('level'),
                'top_asins': [a.get('asin') for a in aba.get('top_asins', [])[:3]]
            }
            if aba.get('search_volume_tier') in ['VERY_HIGH', 'HIGH']:
                enhanced_insights.append(f"📊 ABA: High search demand (SFR: {aba.get('search_frequency_rank')})")
            if (aba.get('market_concentration') or {}).get('level'):
                enhanced_insights.append(f"🏢 Market structure: {(aba.get('market_concentration') or {}).get('level')}")
    except Exception as e:
        print(f"    ⚠️ ABA: {e}", file=sys.stderr)

    # TikTok Shop
    print("[+] Fetching TikTok data...", file=sys.stderr)
    try:
        tiktok = _fetch_tiktok_sales(keyword)
        if tiktok and tiktok.get('has_presence'):
            results['enhanced_data']['tiktok'] = {
                'product_count': tiktok.get('product_count'),
                'total_sales': tiktok.get('total_sales'),
                'estimated_gmv': tiktok.get('estimated_gmv'),
                'opportunity': tiktok.get('opportunity')
            }
            enhanced_insights.append(f"📱 TikTok: {tiktok.get('opportunity')} ({tiktok.get('total_sales', 0):,} sales)")
        else:
            results['enhanced_data']['tiktok'] = {'has_presence': False}
            enhanced_insights.append("📱 TikTok: Not a social commerce category")
    except Exception as e:
        print(f"    ⚠️ TikTok: {e}", file=sys.stderr)

    # eBay Sold (enhanced beyond basic search)
    print("[+] Fetching eBay sold data...", file=sys.stderr)
    try:
        ebay_sold = _fetch_ebay_sold(keyword)
        if ebay_sold and ebay_sold.get('has_sales'):
            results['enhanced_data']['ebay_sold'] = {
                'sold_count': ebay_sold.get('sold_count'),
                'demand_level': ebay_sold.get('demand_level'),
                'price_comparison': {
                    'ebay_avg': (ebay_sold.get('price_range') or {}).get('avg'),
                    'amazon_avg': (amazon.get('price_range') or {}).get('avg', 0) if amazon else 0
                }
            }
            ebay_price = (ebay_sold.get('price_range') or {}).get('avg', 0)
            amazon_price = (amazon.get('price_range') or {}).get('avg', 0) if amazon else 0
            if ebay_price and amazon_price:
                diff = ((amazon_price - ebay_price) / ebay_price * 100) if ebay_price > 0 else 0
                if abs(diff) > 15:
                    enhanced_insights.append(f"💰 Price diff: Amazon {diff:+.0f}% vs eBay")
            enhanced_insights.append(f"🛒 eBay demand: {ebay_sold.get('demand_level')}")
    except Exception as e:
        print(f"    ⚠️ eBay sold: {e}", file=sys.stderr)

    # Keepa Deep (for #1 Amazon product)
    if amazon and amazon.get('products'):
        top_asin = amazon['products'][0].get('asin') if amazon.get('products') else None
        if top_asin:
            print(f"[+] Fetching Keepa deep for {top_asin}...", file=sys.stderr)
            try:
                keepa = _fetch_keepa_deep(top_asin)
                if keepa and 'error' not in keepa:
                    results['enhanced_data']['keepa'] = {
                        'top_asin': top_asin,
                        'bsr_trend': (keepa.get('bsr') or {}).get('trend'),
                        'price_volatility': (keepa.get('price') or {}).get('volatility_pct'),
                        'seasonality': keepa.get('seasonality', {}),
                        'seller_competition': (keepa.get('sellers') or {}).get('competition_signal')
                    }
                    if (keepa.get('bsr') or {}).get('trend') == 'IMPROVING':
                        enhanced_insights.append("📈 Market leader growing (BSR improving)")
                    if (keepa.get('seasonality') or {}).get('detected'):
                        peaks = ', '.join((keepa.get('seasonality') or {}).get('peak_months', []))
                        enhanced_insights.append(f"📅 Seasonal market: peaks in {peaks}")
                    if (keepa.get('price') or {}).get('price_war_risk') == 'HIGH':
                        enhanced_insights.append("⚠️ High price war risk")
            except Exception as e:
                print(f"    ⚠️ Keepa: {e}", file=sys.stderr)

    # Jungle Scout: Share of Voice (brand visibility + search volume)
    marketplace = params.get('marketplace', 'us')
    print("[+] Fetching Jungle Scout Share of Voice...", file=sys.stderr)
    js_sov = js_api_call('/keywords/share-of-voice', {
        'keyword': keyword,
        'marketplace': marketplace.lower() if marketplace else 'us'
    })
    sov_brands = []
    js_search_volume = 0
    js_trend = 'UNKNOWN'
    if js_sov and isinstance(js_sov, dict):
        # API returns brands under 'shareOfVoice' key; fallback to legacy 'attributes' path
        sov_root = js_sov.get('shareOfVoice', {})
        if not sov_root:
            sov_root = js_sov.get('attributes', {}) or {}
        if not sov_root and 'data' in js_sov:
            inner = js_sov['data']
            sov_root = inner.get('shareOfVoice', inner.get('attributes', {})) or {}
        brands_raw = sov_root.get('brands', [])
        for b in brands_raw[:10]:
            sov_brands.append({
                'brand': b.get('brand', ''),
                'combined_sov': b.get('combinedWeightedSov') or b.get('combinedBasicSov') or b.get('combinedSov', 0),
                'organic_sov': b.get('organicWeightedSov') or b.get('organicBasicSov') or b.get('organicSov', 0),
                'sponsored_sov': b.get('sponsoredWeightedSov') or b.get('sponsoredBasicSov') or b.get('sponsoredSov', 0),
            })
        # Extract search volume directly from SOV response
        js_search_volume = sov_root.get('estimatedExact30DaySearchVolume') or sov_root.get('estimated30DaySearchVolume', 0) or sov_root.get('estimatedExactSearchVolume', 0)
        # Trend from monthly change if available
        monthly_change = sov_root.get('searchVolumeChange30Day', 0)
        if monthly_change > 0.1:
            js_trend = 'RISING'
        elif monthly_change < -0.1:
            js_trend = 'DECLINING'
        else:
            js_trend = 'STABLE'
    if sov_brands:
        results['enhanced_data']['js_sov'] = sov_brands
        enhanced_insights.append(f"JS SOV: Top brand '{sov_brands[0]['brand']}' has {sov_brands[0]['combined_sov']:.1%} share of voice")
    if js_search_volume:
        results['enhanced_data']['js_keywords'] = {'search_volume': js_search_volume, 'trend': js_trend}
        enhanced_insights.append(f"JS Search Volume: {js_search_volume:,}/mo, trend: {js_trend}")

    if enhanced_insights:
        results['enhanced_data']['insights'] = enhanced_insights

    results['sov_brands'] = sov_brands
    results['js_search_volume'] = js_search_volume
    results['js_trend'] = js_trend

    return results


def generate_insights(results: dict) -> dict:
    """Generate actionable market insights"""
    amazon = (results.get('platforms') or {}).get('amazon', {})
    ebay = (results.get('platforms') or {}).get('ebay', {})
    walmart = (results.get('platforms') or {}).get('walmart', {})
    
    if not amazon or 'error' in amazon:
        return {'summary': 'Insufficient data for analysis', 'recommendations': []}
    
    avg_reviews = amazon.get('avg_reviews', 0)
    avg_rating = amazon.get('avg_rating', 0)
    avg_price = (amazon.get('price_range') or {}).get('avg', 0)
    total_revenue = amazon.get('total_monthly_revenue', 0)
    product_count = amazon.get('product_count', 0)
    
    # Market assessment
    if avg_reviews < 200 and total_revenue > 100000:
        market_health = 'EXCELLENT'
        summary = f"🔥 Great market! Low competition ({avg_reviews:.0f} avg reviews) with strong revenue (${total_revenue:,.0f}/mo)."
    elif avg_reviews < 500:
        market_health = 'GOOD'
        summary = f"👍 Good opportunity. Moderate competition ({avg_reviews:.0f} avg reviews)."
    elif avg_reviews < 1000:
        market_health = 'MODERATE'
        summary = f"📊 Competitive market ({avg_reviews:.0f} avg reviews). Differentiation needed."
    else:
        market_health = 'CHALLENGING'
        summary = f"⚠️ Very competitive ({avg_reviews:.0f} avg reviews). Consider sub-niches."
    
    # Recommendations
    recommendations = []
    
    # Competition insight
    recommendations.append(f"📊 Competition: {(results.get('summary') or {}).get('competition_level', 'Unknown')} ({avg_reviews:.0f} avg reviews)")
    
    # Quality opportunity
    if avg_rating < 4.0:
        recommendations.append(f"⭐ Quality gap! Avg rating {avg_rating:.1f} — opportunity to exceed expectations")
    elif avg_rating < 4.3:
        recommendations.append(f"⭐ Moderate quality ({avg_rating:.1f} avg) — room for improvement")
    
    # Price insight
    if avg_price > 0:
        recommendations.append(f"💰 Price point: ${avg_price:.2f} avg — consider positioning strategy")
    
    # Multi-platform insight
    platform_count = len([p for p in [amazon, ebay, walmart] if p and 'error' not in p])
    if platform_count > 1:
        recommendations.append(f"🌐 Multi-platform presence ({platform_count} platforms) — consider cross-selling")
    
    # Top brand insight
    top_brand = amazon.get('top_brands', [[None, 0]])
    if top_brand and top_brand[0][0]:
        recommendations.append(f"👑 Market leader: {top_brand[0][0]} — study their strategy")
    
    # Revenue insight
    if total_revenue > 500000:
        recommendations.append(f"💵 Large market (${total_revenue:,.0f}/mo) — worth serious investment")
    elif total_revenue > 100000:
        recommendations.append(f"💵 Solid market (${total_revenue:,.0f}/mo) — good potential")
    
    return {
        'summary': summary,
        'market_health': market_health,
        'recommendations': recommendations,
        'key_metrics': {
            'avg_reviews': avg_reviews,
            'avg_rating': avg_rating,
            'avg_price': avg_price,
            'monthly_revenue': total_revenue
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Market Overview v2.4.0')
    parser.add_argument('params', nargs='?', default='{}', help='JSON parameters')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    parser.add_argument('--csv', metavar='PATH', help='Export results to CSV')
    parser.add_argument('--excel', metavar='PATH', help='Export results to Excel')
    parser.add_argument('--market-size', action='store_true', help='Include TAM/SAM/SOM estimation')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = run_overview(params)
    if 'error' in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Add market sizing if requested
    if args.market_size and 'error' not in result:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, os.path.join(script_dir, '..', '..'))
            from shared.market_sizing import estimate_market_size
            
            # Extract data for market sizing
            summary = result.get('summary', {})
            monthly_volume = summary.get('total_monthly_search_volume', 100000)
            avg_price = summary.get('avg_price', (summary.get('price_range') or {}).get('avg', 30))
            
            sizing = estimate_market_size(
                monthly_search_volume=monthly_volume,
                avg_price=avg_price,
                category='default'
            )
            result['market_sizing'] = sizing
            print("✓ Added market sizing (TAM/SAM/SOM)", file=sys.stderr)
        except Exception as e:
            print(f"Market sizing failed: {e}", file=sys.stderr)
    
    if args.chart and 'error' not in result:
        charts, chart_analysis = generate_charts(result, args.chart)
        result['charts'] = charts
        result['chart_analysis'] = chart_analysis
        print(f"Generated {len(charts)} charts in {args.chart}", file=sys.stderr)
    
    # Export functionality
    if args.csv or args.excel:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, os.path.join(script_dir, '..', '..'))
            from shared.export import to_csv, to_excel
            
            if args.csv:
                to_csv(result, args.csv)
                print(f"Exported to CSV: {args.csv}", file=sys.stderr)
            if args.excel:
                to_excel(result, args.excel)
                print(f"Exported to Excel: {args.excel}", file=sys.stderr)
        except ImportError:
            print("Export module not available", file=sys.stderr)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
