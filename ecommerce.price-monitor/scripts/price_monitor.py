#!/usr/bin/env python3
"""
Product Price Monitor v1.0.0

Monitor competitor price changes and BSR trends.
Answers: "Did competitors change their prices?"

Features:
- Price history tracking (Buybox, FBA, FBM, List, Deal, Prime)
- BSR trend analysis
- Seller count monitoring
- Price change detection and alerts
- Multi-ASIN comparison

Usage:
    python3 price_monitor.py '{"asin": "B0BTYCRJSS"}'
    python3 price_monitor.py '{"asins": ["B0BTYCRJSS", "B0D635YLCT"], "days": 30}'
    python3 price_monitor.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
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

# Domain mapping
MARKET_TO_DOMAIN = {
    'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5,
    'CA': 6, 'IT': 8, 'ES': 9, 'IN': 10, 'MX': 11, 'BR': 12, 'AU': 13
}

DOMAIN_TO_CURRENCY = {
    '1': '$', '2': '£', '3': '€', '4': '€', '5': '¥',
    '6': 'C$', '8': '€', '9': '€', '10': '₹', '11': 'MX$', '12': 'R$'
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

def get_price_history(
    asin: str,
    domain: str = '1',
    days: int = 90
) -> dict:
    """Get price and BSR history from Keepa"""
    result = api_call('/keepa/productSeries', {
        'asin': asin,
        'domain': str(domain),
        'days': days,
        'showPrice': 1,
        'showPriceList': 1,
        'showPriceFba': 1,
        'showPriceFbm': 1,
        'showPriceDeal': 1,
        'showBsrMain': 1,
        'showSellerCount': 1
    })
    
    if result and result.get('errcode') == 200:
        return {
            'asin': result.get('asin', asin),
            'buybox_price': result.get('buyboxPrice', []),
            'price': result.get('price', []),
            'price_list': result.get('priceList', []),
            'price_fba': result.get('priceFba', []),
            'price_fbm': result.get('priceFbm', []),
            'price_deal': result.get('priceDeal', []),
            'bsr_main': result.get('bsrMain', []),
            'seller_count': result.get('sellerCount', []),
            'rating': result.get('rating', []),
            'rating_count': result.get('ratingCount', []),
            'monthly_sold': result.get('monthlySold', []),
            'cost_token': result.get('costToken', 0)
        }
    return {'error': result.get('errmsg', 'No data'), 'asin': asin}

# === Analysis Functions ===

def filter_valid_prices(price_data: List[dict]) -> List[dict]:
    """Filter out invalid price points (-1 = out of stock)"""
    return [p for p in price_data if p.get('value', -1) > 0]

def analyze_price_series(price_data: List[dict], currency: str = '$') -> dict:
    """Analyze a price series"""
    valid_prices = filter_valid_prices(price_data)
    
    if not valid_prices:
        return {'has_data': False}
    
    values = [p['value'] for p in valid_prices]
    
    # Current and historical
    current = values[-1] if values else 0
    oldest = values[0] if values else 0
    
    # Stats
    min_val = min(values)
    max_val = max(values)
    avg_val = statistics.mean(values)
    
    # Change calculation
    change = current - oldest
    change_pct = (change / oldest * 100) if oldest > 0 else 0
    
    # Recent trend (last 7 data points)
    recent = values[-7:] if len(values) >= 7 else values
    if len(recent) >= 2:
        recent_change = recent[-1] - recent[0]
        recent_trend = 'up' if recent_change > 0.5 else 'down' if recent_change < -0.5 else 'stable'
    else:
        recent_trend = 'unknown'
    
    # Find price drops/increases
    price_events = []
    for i in range(1, len(valid_prices)):
        prev_val = valid_prices[i-1]['value']
        curr_val = valid_prices[i]['value']
        pct_change = ((curr_val - prev_val) / prev_val * 100) if prev_val > 0 else 0
        
        if abs(pct_change) >= 10:  # Significant change (10%+)
            price_events.append({
                'time': valid_prices[i]['time'],
                'from': prev_val,
                'to': curr_val,
                'change_pct': round(pct_change, 1),
                'type': 'increase' if pct_change > 0 else 'decrease'
            })
    
    return {
        'has_data': True,
        'data_points': len(valid_prices),
        'current': round(current, 2),
        'oldest': round(oldest, 2),
        'min': round(min_val, 2),
        'max': round(max_val, 2),
        'avg': round(avg_val, 2),
        'change': round(change, 2),
        'change_pct': round(change_pct, 1),
        'trend': recent_trend,
        'currency': currency,
        'significant_events': price_events[-5:]  # Last 5 events
    }

def analyze_bsr_series(bsr_data: List[dict]) -> dict:
    """Analyze BSR series"""
    if not bsr_data:
        return {'has_data': False}
    
    # Get first category (main category)
    main_cat = bsr_data[0] if bsr_data else {}
    category_name = main_cat.get('categoryName', 'Unknown')
    points = main_cat.get('points', [])
    
    if not points:
        return {'has_data': False, 'category': category_name}
    
    values = [p['value'] for p in points if p.get('value', 0) > 0]
    
    if not values:
        return {'has_data': False, 'category': category_name}
    
    current = values[-1]
    oldest = values[0]
    
    # BSR improvement = lower number = better
    change = current - oldest
    change_pct = (change / oldest * 100) if oldest > 0 else 0
    improved = change < 0  # Lower BSR is better
    
    return {
        'has_data': True,
        'category': category_name,
        'data_points': len(values),
        'current': int(current),
        'oldest': int(oldest),
        'min': int(min(values)),
        'max': int(max(values)),
        'change': int(change),
        'change_pct': round(change_pct, 1),
        'improved': improved,
        'trend': 'improving' if improved else 'declining' if change > 0 else 'stable'
    }

def analyze_seller_count(seller_data: List[dict]) -> dict:
    """Analyze seller count changes"""
    valid_data = [s for s in seller_data if s.get('value', 0) >= 0]
    
    if not valid_data:
        return {'has_data': False}
    
    values = [s['value'] for s in valid_data]
    current = int(values[-1])
    oldest = int(values[0])
    change = current - oldest
    
    return {
        'has_data': True,
        'current': current,
        'oldest': oldest,
        'min': int(min(values)),
        'max': int(max(values)),
        'change': change,
        'trend': 'increasing' if change > 0 else 'decreasing' if change < 0 else 'stable'
    }

def generate_alerts(
    buybox_analysis: dict,
    fba_analysis: dict,
    bsr_analysis: dict,
    seller_analysis: dict
) -> List[dict]:
    """Generate alerts based on analysis"""
    alerts = []
    
    # Price alerts
    for name, analysis in [('Buybox', buybox_analysis), ('FBA', fba_analysis)]:
        if analysis.get('has_data'):
            change_pct = analysis.get('change_pct', 0)
            currency = analysis.get('currency', '$')
            
            if change_pct <= -15:
                alerts.append({
                    'type': 'price_drop',
                    'severity': 'HIGH',
                    'icon': '🔴',
                    'message': f'{name} price dropped {abs(change_pct):.1f}% ({currency}{analysis["oldest"]} → {currency}{analysis["current"]})'
                })
            elif change_pct <= -5:
                alerts.append({
                    'type': 'price_drop',
                    'severity': 'MEDIUM',
                    'icon': '🟡',
                    'message': f'{name} price decreased {abs(change_pct):.1f}%'
                })
            elif change_pct >= 15:
                alerts.append({
                    'type': 'price_increase',
                    'severity': 'INFO',
                    'icon': '📈',
                    'message': f'{name} price increased {change_pct:.1f}%'
                })
            
            # Significant events
            for event in analysis.get('significant_events', []):
                if event['type'] == 'decrease' and event['change_pct'] <= -20:
                    alerts.append({
                        'type': 'flash_sale',
                        'severity': 'HIGH',
                        'icon': '⚡',
                        'message': f"Flash sale detected on {event['time']}: {currency}{event['from']} → {currency}{event['to']} ({event['change_pct']}%)"
                    })
    
    # BSR alerts
    if bsr_analysis.get('has_data'):
        change_pct = bsr_analysis.get('change_pct', 0)
        if change_pct <= -30:
            alerts.append({
                'type': 'bsr_surge',
                'severity': 'HIGH',
                'icon': '🚀',
                'message': f"BSR improved significantly: #{bsr_analysis['oldest']:,} → #{bsr_analysis['current']:,} ({abs(change_pct):.0f}% better)"
            })
        elif change_pct >= 50:
            alerts.append({
                'type': 'bsr_drop',
                'severity': 'MEDIUM',
                'icon': '📉',
                'message': f"BSR declined: #{bsr_analysis['oldest']:,} → #{bsr_analysis['current']:,}"
            })
    
    # Seller count alerts
    if seller_analysis.get('has_data'):
        change = seller_analysis.get('change', 0)
        if change >= 3:
            alerts.append({
                'type': 'new_sellers',
                'severity': 'MEDIUM',
                'icon': '👥',
                'message': f"New competitors entered: {seller_analysis['oldest']} → {seller_analysis['current']} sellers"
            })
        elif change <= -2:
            alerts.append({
                'type': 'sellers_left',
                'severity': 'INFO',
                'icon': '📤',
                'message': f"Sellers left the listing: {seller_analysis['oldest']} → {seller_analysis['current']}"
            })
    
    # Sort by severity
    severity_order = {'HIGH': 0, 'MEDIUM': 1, 'INFO': 2}
    alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'INFO'), 2))
    
    return alerts

def generate_insights(
    buybox_analysis: dict,
    fba_analysis: dict,
    bsr_analysis: dict,
    seller_analysis: dict,
    alerts: List[dict]
) -> dict:
    """Generate narrative insights"""
    insights = []
    
    # Price summary
    if buybox_analysis.get('has_data'):
        currency = buybox_analysis.get('currency', '$')
        current = buybox_analysis.get('current', 0)
        change_pct = buybox_analysis.get('change_pct', 0)
        trend = buybox_analysis.get('trend', 'stable')
        
        if change_pct != 0:
            direction = 'up' if change_pct > 0 else 'down'
            insights.append(f"💰 Buybox price is {currency}{current:.2f}, {direction} {abs(change_pct):.1f}% from period start")
        else:
            insights.append(f"💰 Buybox price stable at {currency}{current:.2f}")
        
        if trend == 'down':
            insights.append("📉 Recent trend: Price declining")
        elif trend == 'up':
            insights.append("📈 Recent trend: Price increasing")
    
    # BSR summary
    if bsr_analysis.get('has_data'):
        current_bsr = bsr_analysis.get('current', 0)
        category = bsr_analysis.get('category', 'Unknown')
        trend = bsr_analysis.get('trend', 'stable')
        
        if trend == 'improving':
            insights.append(f"🚀 BSR improving: Currently #{current_bsr:,} in {category}")
        elif trend == 'declining':
            insights.append(f"📉 BSR declining: Currently #{current_bsr:,} in {category}")
        else:
            insights.append(f"📊 BSR stable: #{current_bsr:,} in {category}")
    
    # Competition
    if seller_analysis.get('has_data'):
        sellers = seller_analysis.get('current', 0)
        change = seller_analysis.get('change', 0)
        
        if change > 0:
            insights.append(f"👥 Competition increased: Now {sellers} sellers (+{change})")
        elif change < 0:
            insights.append(f"👥 Competition decreased: Now {sellers} sellers ({change})")
    
    # Alert summary
    high_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
    if high_alerts:
        insights.append(f"⚠️ {len(high_alerts)} high-priority alert(s) detected")
    
    return {
        'key_findings': insights[:5],
        'alert_count': len(alerts),
        'high_priority_alerts': len(high_alerts)
    }

# === Main Function ===

def monitor_price(
    asin: str = None,
    asins: List[str] = None,
    market: str = 'US',
    days: int = 90
) -> dict:
    """Main price monitoring function"""
    
    domain = MARKET_TO_DOMAIN.get(market.upper(), 1)
    currency = DOMAIN_TO_CURRENCY.get(domain, '$')
    
    target_asins = asins if asins else ([asin] if asin else [])
    
    if not target_asins:
        return {'error': 'Provide asin or asins parameter'}
    
    result = {
        'marketplace': market.upper(),
        'currency': currency,
        'days': days,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0',
        'products': []
    }
    
    total_cost = 0
    all_alerts = []
    
    for i, target_asin in enumerate(target_asins[:5]):  # Max 5 ASINs
        print(f"[{i+1}/{len(target_asins[:5])}] Fetching price history for {target_asin}...", file=sys.stderr)
        
        history = get_price_history(target_asin, domain, days)
        
        if 'error' in history:
            result['products'].append({'asin': target_asin, 'error': history['error']})
            continue
        
        total_cost += history.get('cost_token', 0)
        
        # Analyze each price type
        buybox_analysis = analyze_price_series(history.get('buybox_price', []), currency)
        fba_analysis = analyze_price_series(history.get('price_fba', []), currency)
        fbm_analysis = analyze_price_series(history.get('price_fbm', []), currency)
        list_analysis = analyze_price_series(history.get('price_list', []), currency)
        deal_analysis = analyze_price_series(history.get('price_deal', []), currency)
        
        bsr_analysis = analyze_bsr_series(history.get('bsr_main', []))
        seller_analysis = analyze_seller_count(history.get('seller_count', []))
        
        # Generate alerts
        alerts = generate_alerts(buybox_analysis, fba_analysis, bsr_analysis, seller_analysis)
        all_alerts.extend([{**a, 'asin': target_asin} for a in alerts])
        
        # Generate insights
        insights = generate_insights(buybox_analysis, fba_analysis, bsr_analysis, seller_analysis, alerts)
        
        product_result = {
            'asin': target_asin,
            'price_analysis': {
                'buybox': buybox_analysis if buybox_analysis.get('has_data') else None,
                'fba': fba_analysis if fba_analysis.get('has_data') else None,
                'fbm': fbm_analysis if fbm_analysis.get('has_data') else None,
                'list_price': list_analysis if list_analysis.get('has_data') else None,
                'deal_price': deal_analysis if deal_analysis.get('has_data') else None
            },
            'bsr_analysis': bsr_analysis if bsr_analysis.get('has_data') else None,
            'seller_analysis': seller_analysis if seller_analysis.get('has_data') else None,
            'alerts': alerts,
            'insights': insights,
            'raw_data_points': {
                'buybox': len(history.get('buybox_price', [])),
                'fba': len(history.get('price_fba', [])),
                'bsr': sum(len(cat.get('points', [])) for cat in history.get('bsr_main', []))
            }
        }
        
        result['products'].append(product_result)
        print(f"    ✓ {len(alerts)} alerts generated", file=sys.stderr)
    
    result['total_cost_token'] = total_cost
    result['total_alerts'] = len(all_alerts)
    result['all_alerts'] = sorted(all_alerts, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'INFO': 2}.get(x.get('severity'), 2))[:10]
    
    # Summary
    high_alerts = [a for a in all_alerts if a.get('severity') == 'HIGH']
    result['summary'] = {
        'products_monitored': len(result['products']),
        'total_alerts': len(all_alerts),
        'high_priority': len(high_alerts),
        'status': '🔴 Action Required' if high_alerts else '🟢 All Normal'
    }
    
    return result

# === Chart Generation ===

def generate_charts(result: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib.dates import DateFormatter
        import matplotlib.dates as mdates
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
    
    products = result.get('products', [])
    currency = result.get('currency', '$')
    
    if not products:
        return []
    
    # For first product, generate detailed charts
    product = products[0]
    asin = product.get('asin', 'Unknown')[:15]
    
    price_analysis = product.get('price_analysis', {})
    
    # Chart 1: Price Summary
    price_types = []
    current_prices = []
    min_prices = []
    max_prices = []
    colors = []
    
    for name, analysis, color in [
        ('Buybox', price_analysis.get('buybox'), BLUE),
        ('FBA', price_analysis.get('fba'), GREEN),
        ('FBM', price_analysis.get('fbm'), ORANGE),
        ('List', price_analysis.get('list_price'), PURPLE)
    ]:
        if analysis and analysis.get('has_data'):
            price_types.append(name)
            current_prices.append(analysis['current'])
            min_prices.append(analysis['min'])
            max_prices.append(analysis['max'])
            colors.append(color)
    
    if price_types:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        x = range(len(price_types))
        width = 0.25
        
        bars1 = ax.bar([i - width for i in x], min_prices, width, label='Min', color=[c + '60' for c in colors], edgecolor='white')
        bars2 = ax.bar(x, current_prices, width, label='Current', color=colors, edgecolor='white')
        bars3 = ax.bar([i + width for i in x], max_prices, width, label='Max', color=[c + '80' for c in colors], edgecolor='white')
        
        ax.set_ylabel(f'Price ({currency})', fontsize=11)
        ax.set_title(f'PRICE SUMMARY: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(price_types)
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add value labels
        for bars in [bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{currency}{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_price_summary.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Price Summary", file=sys.stderr)
    
    # Chart 2: Price Change
    changes = []
    change_labels = []
    change_colors = []
    
    for name, analysis in [
        ('Buybox', price_analysis.get('buybox')),
        ('FBA', price_analysis.get('fba')),
        ('FBM', price_analysis.get('fbm'))
    ]:
        if analysis and analysis.get('has_data'):
            change_pct = analysis.get('change_pct', 0)
            changes.append(change_pct)
            change_labels.append(name)
            change_colors.append(GREEN if change_pct < 0 else RED if change_pct > 0 else BLUE)
    
    if changes:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        bars = ax.bar(change_labels, changes, color=change_colors, edgecolor='white', linewidth=2)
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_ylabel('Price Change %', fontsize=11)
        ax.set_title(f'PRICE CHANGES: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, change in zip(bars, changes):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3),
                   f'{change:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_price_change.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Price Change", file=sys.stderr)
    
    # Chart 3: BSR Trend
    bsr = product.get('bsr_analysis')
    if bsr and bsr.get('has_data'):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        labels = ['Start', 'Min', 'Current', 'Max']
        values = [bsr['oldest'], bsr['min'], bsr['current'], bsr['max']]
        colors = [BLUE, GREEN, ORANGE if bsr['current'] > bsr['oldest'] else GREEN, RED]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        ax.set_ylabel('BSR Rank', fontsize=11)
        ax.set_title(f'BSR RANGE: {bsr["category"][:30]}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'#{val:,}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_bsr_range.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: BSR Range", file=sys.stderr)
    
    # Chart 4: Alert Summary (if multiple products)
    all_alerts = result.get('all_alerts', [])
    if all_alerts:
        fig, ax = plt.subplots(figsize=(10, 4))
        
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'INFO': 0}
        for alert in all_alerts:
            sev = alert.get('severity', 'INFO')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        labels = list(severity_counts.keys())
        values = list(severity_counts.values())
        colors = [RED, ORANGE, BLUE]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        ax.set_ylabel('Number of Alerts', fontsize=11)
        ax.set_title('ALERT SUMMARY', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                       str(val), ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_alerts.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Alerts", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Product Price Monitor v1.0.0')
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
    asins = params.get('asins')
    
    if not asin and not asins:
        print("Missing required parameter: asin or asins", file=sys.stderr)
        sys.exit(1)
    
    result = monitor_price(
        asin=asin,
        asins=asins,
        market=params.get('market', 'US'),
        days=params.get('days', 90)
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
