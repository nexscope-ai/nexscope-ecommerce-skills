#!/usr/bin/env python3
"""
Market Alert v3.0.0

Monitor market changes: new competitors, trend shifts, price movements.
Answers: "Are there market changes?"

Data Source: Keywords API (via NexScope proxy)

Features:
- New competitor detection (recently launched products)
- Price movement analysis (price wars, increases)
- Market composition changes
- SOV analysis based on actual sales revenue
- Review Velocity & Rating Drift analysis
- Price Tier Distribution & Vacuum zones

Usage:
    python3 market_alert.py '{"keyword": "bluetooth earbuds"}'
    python3 market_alert.py '{"keyword": "yoga mat", "market": "uk"}'
    python3 market_alert.py '{"keyword": "bluetooth earbuds"}' --chart /tmp/charts
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Optional, List
from urllib.request import Request, urlopen
from collections import Counter
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

# Use hardcoded key for testing, can be overridden by env var in format KeyName:ApiKey
NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

_PROXY_ENDPOINTS = {
    'product_database_query': '/product-database/query',
    '/product_database_query': '/product-database/query',
    'keywords/keywords_by_keyword_query': '/keywords/by-keyword',
    '/keywords/keywords_by_keyword_query': '/keywords/by-keyword',
}
_PROXY_LIST_FIELDS = {
    '/product-database/query': 'productDatabaseList',
    '/keywords/by-keyword': 'keywordInfoList',
}

# Supported marketplaces
SUPPORTED_MARKETS = ['us', 'uk', 'de', 'fr', 'it', 'es', 'ca', 'mx', 'jp', 'in']

MARKET_TO_CURRENCY = {
    'us': '$', 'uk': '£', 'de': '€', 'fr': '€', 
    'it': '€', 'es': '€', 'ca': 'C$', 'mx': 'MX$',
    'jp': '¥', 'in': '₹'
}

AMAZON_DOMAINS = {
    'us': 'amazon.com', 'uk': 'amazon.co.uk', 'de': 'amazon.de',
    'fr': 'amazon.fr', 'it': 'amazon.it', 'es': 'amazon.es',
    'ca': 'amazon.ca', 'mx': 'amazon.com.mx', 'jp': 'amazon.co.jp',
    'in': 'amazon.in',
}

# === API Functions ===

def js_api_call(endpoint: str, payload: dict, marketplace: str = 'us') -> Optional[dict]:
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
    proxy_payload = {'marketplace': marketplace}
    for k, v in attrs.items():
        parts = k.split('_')
        camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        proxy_payload[camel] = v
    try:
        data = json.dumps(proxy_payload).encode('utf-8')
        req = Request(url, data=data, headers=headers, method='POST')
        with urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if raw.get('code') != 0:
            print(f"Proxy error: {raw.get('msg', 'unknown')}", file=sys.stderr)
            return None
        list_field = _PROXY_LIST_FIELDS.get(proxy_ep, '')
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

def _amazon_search(keyword: str, marketplace: str = 'us') -> List[dict]:
    """Search Amazon via SerpApi (returns actual search results ranked by relevance)."""
    domain = AMAZON_DOMAINS.get(marketplace, 'amazon.com')
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/search"
    headers = {
        'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = json.dumps({'keyword': keyword, 'amazonDomain': domain}).encode('utf-8')
    try:
        req = Request(url, data=payload, headers=headers, method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        data = raw.get('data', raw)
        if isinstance(data, dict) and 'code' in data:
            data = data.get('data', data)
        return data.get('products', [])
    except Exception as e:
        print(f"Amazon Search API Error: {e}", file=sys.stderr)
        return []

def _js_enrich_by_keyword(keyword: str, marketplace: str = 'us') -> dict:
    """Get monthly sales estimates from Jungle Scout keyword data (SOV/share-of-voice style)."""
    # JS keywords/by-keyword returns top products with revenue estimates
    result = js_api_call('keywords/keywords_by_keyword_query', {
        'data': {
            'type': 'keywords_by_keyword_query',
            'attributes': {
                'search_terms': keyword,
                'marketplace': marketplace
            }
        }
    }, marketplace)
    # Build ASIN -> revenue map from keyword data if available
    return result

# Keepa domain mapping
KEEPA_DOMAIN_MAP = {
    'us': 1, 'uk': 2, 'de': 3, 'fr': 4, 'jp': 5,
    'ca': 6, 'it': 8, 'es': 9, 'in': 10, 'mx': 11,
}

def _keepa_enrich_dates(asins: List[str], marketplace: str = 'us') -> dict:
    """Batch fetch availableDate from Keepa for new competitor detection.
    
    Returns: {asin: date_str or None}
    """
    if not asins:
        return {}
    
    domain = KEEPA_DOMAIN_MAP.get(marketplace, 1)
    # Keepa supports comma-separated ASINs (batch)
    asin_str = ','.join(asins[:50])  # Keepa limit
    
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/keepa/productRequest"
    headers = {
        'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = json.dumps({'domain': str(domain), 'asin': asin_str}).encode('utf-8')
    
    try:
        req = Request(url, data=payload, headers=headers, method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        
        data = raw.get('data', raw)
        if isinstance(data, dict) and 'code' in data:
            data = data.get('data', data)
        
        products = data.get('products', [])
        result = {}
        for p in products:
            asin = p.get('asin', '')
            available_date = p.get('availableDate')  # e.g. "2020-03-18 01:26:00"
            result[asin] = available_date
        return result
    except Exception as e:
        print(f"  Keepa enrichment error: {e}", file=sys.stderr)
        return {}

def search_products_js(keyword: str, marketplace: str = 'us', min_price: float = 1, max_price: float = 500) -> dict:
    """Search products using Amazon Search API for accurate results.
    
    Uses SerpApi Amazon Search (returns ranked search results) instead of
    Jungle Scout product-database (returns random keyword-matched products).
    Enriches with monthly sales estimates from SerpApi's monthlySalesUnits.
    """
    raw_products = _amazon_search(keyword, marketplace)
    
    if not raw_products:
        print("  Amazon Search returned no results, falling back to product-database", file=sys.stderr)
        # Fallback to old method
        result = js_api_call('product_database_query', {
            'data': {
                'type': 'product_database_query',
                'attributes': {
                    'include_keywords': [keyword],
                    'min_price': min_price,
                    'max_price': max_price
                }
            }
        }, marketplace)
        if result and 'data' in result:
            products = []
            for item in result['data']:
                attrs = item.get('attributes', {})
                products.append({
                    'asin': item.get('id', '').split('/')[-1],
                    'title': attrs.get('title', ''),
                    'brand': attrs.get('brand', 'Unknown'),
                    'price': attrs.get('price', 0),
                    'rating': float(attrs.get('rating') or 0),
                    'reviews': int(attrs.get('reviews') or 0),
                    'monthly_revenue': attrs.get('approximate30_day_revenue', 0) or attrs.get('approximate_30_day_revenue', 0),
                    'monthly_units': attrs.get('approximate30_day_units_sold', 0) or attrs.get('approximate_30_day_units_sold', 0),
                    'bsr': attrs.get('product_rank'),
                    'date_first_available': attrs.get('date_first_available'),
                    'seller_type': attrs.get('seller_type'),
                    'buy_box_owner': attrs.get('buy_box_owner'),
                    'listing_quality_score': attrs.get('listing_quality_score'),
                    'category': attrs.get('category'),
                    'is_available': attrs.get('is_available', True),
                    'fee_breakdown': attrs.get('fee_breakdown', {})
                })
            return {'products': products, 'total': len(products)}
        return {'products': [], 'total': 0, 'error': 'No data returned'}
    
    # Parse Amazon Search results
    products = []
    for p in raw_products:
        price = p.get('extractedPrice') or p.get('price') or 0
        if isinstance(price, str):
            try:
                price = float(price.replace('$', '').replace(',', ''))
            except (ValueError, TypeError):
                price = 0
        
        monthly_units = p.get('monthlySalesUnits') or 0
        monthly_revenue = price * monthly_units if price and monthly_units else 0
        
        products.append({
            'asin': p.get('asin', ''),
            'title': p.get('title', ''),
            'brand': p.get('brand', 'Unknown'),
            'price': price,
            'rating': float(p.get('rating') or 0),
            'reviews': int(p.get('ratings') or 0),  # SerpApi uses 'ratings' for review count
            'monthly_revenue': monthly_revenue,
            'monthly_units': monthly_units,
            'bsr': None,
            'date_first_available': None,
            'seller_type': 'FBA',  # SerpApi doesn't provide this
            'buy_box_owner': None,
            'listing_quality_score': None,
            'category': p.get('category', ''),
            'is_available': True,
            'fee_breakdown': {},
            'position': p.get('position', 0),
            'sponsored': p.get('sponsored', False),
        })
    
    # Filter by price range
    if min_price or max_price:
        products = [p for p in products if (not min_price or (p['price'] or 0) >= min_price) 
                    and (not max_price or (p['price'] or 0) <= max_price)]
    
    # Enrich with Keepa availableDate for new competitor detection
    asins_to_enrich = [p['asin'] for p in products if p.get('asin')]
    if asins_to_enrich:
        print(f"  Enriching {len(asins_to_enrich)} products with Keepa dates...", file=sys.stderr)
        date_map = _keepa_enrich_dates(asins_to_enrich, marketplace)
        enriched_count = 0
        for p in products:
            available_date = date_map.get(p['asin'])
            if available_date:
                # Keepa returns "2020-03-18 01:26:00", normalize to "2020-03-18"
                p['date_first_available'] = available_date.split(' ')[0] if available_date else None
                enriched_count += 1
        if enriched_count:
            print(f"  ✓ Got dates for {enriched_count}/{len(asins_to_enrich)} products", file=sys.stderr)
    
    return {'products': products, 'total': len(products)}

def get_keyword_stats_js(keyword: str, marketplace: str = 'us') -> dict:
    """Get keyword statistics via proxy"""
    result = js_api_call('keywords/keywords_by_keyword_query', {
        'data': {
            'type': 'keywords_by_keyword_query',
            'attributes': {
                'search_terms': keyword
            }
        }
    }, marketplace)
    
    if result and 'data' in result:
        keywords = []
        for item in result['data']:
            attrs = item.get('attributes', {})
            keywords.append({
                'keyword': attrs.get('name', ''),
                'monthly_search_volume': attrs.get('monthly_search_volume_exact', 0),
                'monthly_trend': attrs.get('monthly_trend', 0),
                'quarterly_trend': attrs.get('quarterly_trend', 0),
                'organic_product_count': attrs.get('organic_product_count', 0),
                'sponsored_product_count': attrs.get('sponsored_product_count', 0),
                'ease_of_ranking_score': attrs.get('ease_of_ranking_score', 0),
                'relevancy_score': attrs.get('relevancy_score', 0),
                'dominant_category': attrs.get('dominant_category', '')
            })
        return {'keywords': keywords}
    
    return {'keywords': [], 'error': 'No data returned'}

# === Analysis Functions ===

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime"""
    if not date_str:
        return None
    
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except:
            continue
    return None

def calculate_product_age_days(date_str: str) -> Optional[int]:
    """Calculate product age in days"""
    if not date_str:
        return None
    
    date = parse_date(date_str)
    if date:
        return (datetime.now() - date).days
    return None

def analyze_market_composition(products: List[dict], currency: str = '$') -> dict:
    """Analyze market composition"""
    if not products:
        return {'error': 'No products'}
    
    # Filter available products with valid prices
    valid_products = [p for p in products if p.get('price', 0) > 0 and p.get('is_available', True)]
    
    if not valid_products:
        return {'error': 'No valid products'}
    
    # Price analysis
    prices = [p['price'] for p in valid_products]
    
    # Rating analysis
    ratings = [p['rating'] for p in valid_products if p.get('rating') and p['rating'] > 0]
    
    # Review count analysis
    reviews = [p.get('reviews', 0) or 0 for p in valid_products]
    
    # Brand distribution
    brands = [p.get('brand', 'Unknown') for p in valid_products if p.get('brand')]
    brand_counts = Counter(brands)
    
    # Monthly revenue
    revenues = [p.get('monthly_revenue', 0) or 0 for p in valid_products]
    total_revenue = sum(revenues)
    
    # Monthly units
    units = [p.get('monthly_units', 0) or 0 for p in valid_products]
    total_units = sum(units)
    
    # Seller type distribution
    seller_types = Counter(p.get('seller_type', 'Unknown') for p in valid_products)
    
    return {
        'total_products': len(valid_products),
        'price': {
            'min': round(min(prices), 2) if prices else 0,
            'max': round(max(prices), 2) if prices else 0,
            'avg': round(statistics.mean(prices), 2) if prices else 0,
            'median': round(statistics.median(prices), 2) if len(prices) > 1 else (round(prices[0], 2) if prices else 0)
        },
        'rating': {
            'avg': round(statistics.mean(ratings), 2) if ratings else 0,
            'min': round(min(ratings), 1) if ratings else 0,
            'max': round(max(ratings), 1) if ratings else 0
        },
        'reviews': {
            'avg': int(statistics.mean(reviews)) if reviews else 0,
            'median': int(statistics.median(reviews)) if len(reviews) > 1 else (reviews[0] if reviews else 0),
            'total': sum(reviews)
        },
        'revenue': {
            'total': round(total_revenue, 2),
            'avg': round(total_revenue / len(valid_products), 2) if valid_products else 0
        },
        'units': {
            'total': total_units,
            'avg': int(total_units / len(valid_products)) if valid_products else 0
        },
        'brands': {
            'unique_count': len(brand_counts),
            'top_brands': dict(brand_counts.most_common(5))
        },
        'seller_types': dict(seller_types),
        'currency': currency
    }

def detect_new_competitors(products: List[dict], days_threshold: int = 90) -> dict:
    """Detect new competitors (products launched recently)"""
    new_products = []
    established = []
    unknown_age = []
    
    for p in products:
        if not p.get('is_available', True):
            continue
            
        date_str = p.get('date_first_available')
        age_days = calculate_product_age_days(date_str)
        
        product_info = {
            'asin': p.get('asin'),
            'title': (p.get('title') or '')[:60],
            'brand': p.get('brand', 'Unknown'),
            'price': p.get('price', 0),
            'rating': p.get('rating', 0),
            'reviews': p.get('reviews', 0) or 0,
            'monthly_revenue': float(p.get('monthly_revenue', 0) or 0),
            'monthly_units': p.get('monthly_units', 0) or 0,
            'date_first_available': date_str,
            'age_days': age_days,
            'listing_quality_score': p.get('listing_quality_score', 0)
        }
        
        if age_days is not None:
            if age_days <= days_threshold:
                product_info['is_new'] = True
                new_products.append(product_info)
            else:
                established.append(product_info)
        else:
            unknown_age.append(product_info)
    
    # Sort new products by revenue (highest first)
    new_products.sort(key=lambda x: -(x.get('monthly_revenue') or 0))
    
    # Find fast risers (new but already selling well - $1000+/month revenue)
    fast_risers = [p for p in new_products if (p.get('monthly_revenue') or 0) >= 1000]
    
    total = len(new_products) + len(established) + len(unknown_age)
    
    return {
        'new_count': len(new_products),
        'established_count': len(established),
        'unknown_count': len(unknown_age),
        'new_percentage': round(len(new_products) / total * 100, 1) if total > 0 else 0,
        'new_products': new_products[:10],
        'fast_risers': fast_risers[:5],
        'threshold_days': days_threshold
    }

def detect_price_movements(products: List[dict]) -> dict:
    """Detect price movements and potential price wars"""
    # Group by price ranges to detect clustering
    price_ranges = {'under_20': 0, '20_50': 0, '50_100': 0, 'over_100': 0}
    low_price_products = []
    
    for p in products:
        if not p.get('is_available', True):
            continue
        price = p.get('price', 0)
        if price <= 0:
            continue
        
        if price < 20:
            price_ranges['under_20'] += 1
            low_price_products.append({
                'asin': p.get('asin'),
                'title': (p.get('title') or '')[:50],
                'price': price,
                'monthly_revenue': p.get('monthly_revenue', 0)
            })
        elif price < 50:
            price_ranges['20_50'] += 1
        elif price < 100:
            price_ranges['50_100'] += 1
        else:
            price_ranges['over_100'] += 1
    
    # Price war detection: many products under $20 with high revenue
    low_price_high_revenue = [p for p in low_price_products if (p.get('monthly_revenue') or 0) >= 5000]
    price_war_signal = len(low_price_high_revenue) >= 3
    
    return {
        'price_ranges': price_ranges,
        'low_price_count': len(low_price_products),
        'price_war_signal': price_war_signal,
        'low_price_leaders': sorted(low_price_products, key=lambda x: -(x.get('monthly_revenue') or 0))[:5]
    }

def analyze_review_velocity(products: List[dict], new_competitors: dict) -> dict:
    """Analyze review velocity and rating patterns"""
    suspicious_velocity = []
    high_quality_new = []
    
    for p in products:
        if not p.get('is_available', True):
            continue
            
        reviews = p.get('reviews', 0) or 0
        rating = p.get('rating', 0) or 0
        age_days = calculate_product_age_days(p.get('date_first_available'))
        
        if age_days and age_days > 0 and reviews > 0:
            reviews_per_day = reviews / age_days
            
            # Suspicious: >3 reviews/day for products <90 days old
            if age_days <= 90 and reviews_per_day > 3:
                suspicious_velocity.append({
                    'asin': p.get('asin'),
                    'title': (p.get('title') or '')[:50],
                    'reviews': reviews,
                    'age_days': age_days,
                    'reviews_per_day': round(reviews_per_day, 2),
                    'rating': rating,
                    'risk_level': 'HIGH' if reviews_per_day > 5 else 'MEDIUM'
                })
            
            # High quality new products: good rating + decent reviews
            if age_days <= 90 and rating >= 4.3 and reviews >= 50:
                high_quality_new.append({
                    'asin': p.get('asin'),
                    'brand': p.get('brand'),
                    'rating': rating,
                    'reviews': reviews,
                    'monthly_revenue': p.get('monthly_revenue', 0)
                })
    
    # Sort by revenue
    high_quality_new.sort(key=lambda x: -(x.get('monthly_revenue') or 0))
    
    return {
        'suspicious_review_patterns': suspicious_velocity,
        'high_quality_new_products': high_quality_new[:5],
        'suspicious_count': len(suspicious_velocity)
    }

def analyze_sov(products: List[dict], new_competitors: dict) -> dict:
    """Analyze Share of Voice based on actual sales revenue"""
    # Filter available products with revenue data
    valid_products = [p for p in products if p.get('is_available', True) and (p.get('monthly_revenue') or 0) > 0]
    
    if not valid_products:
        return {'has_data': False}
    
    total_revenue = sum(p.get('monthly_revenue', 0) for p in valid_products)
    
    if total_revenue <= 0:
        return {'has_data': False}
    
    # Get new product ASINs
    new_asins = set(p.get('asin') for p in new_competitors.get('new_products', []))
    
    # Brand-level SOV
    brand_revenue = {}
    new_brand_revenue = 0
    
    for p in valid_products:
        brand = p.get('brand', 'Unknown')
        revenue = p.get('monthly_revenue', 0) or 0
        
        if brand not in brand_revenue:
            brand_revenue[brand] = {'revenue': 0, 'products': 0, 'units': 0}
        brand_revenue[brand]['revenue'] += revenue
        brand_revenue[brand]['products'] += 1
        brand_revenue[brand]['units'] += p.get('monthly_units', 0) or 0
        
        # Track new brand revenue
        if p.get('asin') in new_asins:
            new_brand_revenue += revenue
    
    # Calculate SOV percentages
    brand_ranking = []
    for brand, data in brand_revenue.items():
        sov_pct = round(data['revenue'] / total_revenue * 100, 1)
        brand_ranking.append({
            'brand': brand,
            'revenue': round(data['revenue'], 2),
            'sov_pct': sov_pct,
            'products': data['products'],
            'units': data['units']
        })
    
    # Sort by revenue
    brand_ranking.sort(key=lambda x: -x['revenue'])
    
    # Top 3 concentration
    top3_revenue = sum(x['revenue'] for x in brand_ranking[:3])
    top3_concentration = round(top3_revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
    
    # New brands SOV
    new_sov_pct = round(new_brand_revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
    
    return {
        'has_data': True,
        'total_market_revenue': round(total_revenue, 2),
        'new_brands_sov_pct': new_sov_pct,
        'established_sov_pct': round(100 - new_sov_pct, 1),
        'top3_concentration': top3_concentration,
        'brand_ranking': brand_ranking[:10]
    }

def analyze_price_tiers(products: List[dict], new_competitors: dict, currency: str = '$') -> dict:
    """Analyze price tier distribution and identify vacuum zones"""
    valid_products = [p for p in products if p.get('is_available', True) and (p.get('price') or 0) > 0]
    
    if not valid_products:
        return {'has_data': False}
    
    prices = [p['price'] for p in valid_products]
    min_price = min(prices)
    max_price = max(prices)
    
    # Create dynamic tiers
    if max_price <= 50:
        tier_boundaries = [0, 10, 20, 30, 40, 50]
    elif max_price <= 100:
        tier_boundaries = [0, 20, 40, 60, 80, 100]
    elif max_price <= 200:
        tier_boundaries = [0, 30, 60, 100, 150, 200]
    else:
        tier_boundaries = [0, 50, 100, 150, 200, 300, max_price + 1]
    
    # Initialize tiers
    tiers = {}
    for i in range(len(tier_boundaries) - 1):
        low = tier_boundaries[i]
        high = tier_boundaries[i + 1]
        tier_name = f"{currency}{low}-{high}"
        tiers[tier_name] = {
            'range': (low, high),
            'total_count': 0,
            'new_count': 0,
            'total_revenue': 0,
            'products': []
        }
    
    # Get new product ASINs
    new_asins = set(p.get('asin') for p in new_competitors.get('new_products', []))
    
    # Categorize products into tiers
    for p in valid_products:
        price = p['price']
        
        for tier_name, tier_data in tiers.items():
            low, high = tier_data['range']
            if low <= price < high:
                tier_data['total_count'] += 1
                tier_data['total_revenue'] += p.get('monthly_revenue', 0) or 0
                tier_data['products'].append(p)
                if p.get('asin') in new_asins:
                    tier_data['new_count'] += 1
                break
    
    # Calculate tier statistics
    tier_summary = []
    battleground = None
    max_revenue = 0
    vacuum_zones = []
    new_entrant_focus = None
    max_new_pct = 0
    
    for tier_name, tier_data in tiers.items():
        if tier_data['total_count'] > 0:
            ratings = [p.get('rating') or 0 for p in tier_data['products'] if p.get('rating')]
            new_pct = round(tier_data['new_count'] / tier_data['total_count'] * 100, 1)
            
            tier_info = {
                'tier': tier_name,
                'total': tier_data['total_count'],
                'new': tier_data['new_count'],
                'new_pct': new_pct,
                'revenue': round(tier_data['total_revenue'], 2),
                'avg_rating': round(statistics.mean(ratings), 2) if ratings else 0
            }
            tier_summary.append(tier_info)
            
            # Main battleground (highest revenue)
            if tier_data['total_revenue'] > max_revenue:
                max_revenue = tier_data['total_revenue']
                battleground = tier_info
            
            # New entrant focus (highest new %)
            if tier_data['new_count'] > 0 and new_pct > max_new_pct:
                max_new_pct = new_pct
                new_entrant_focus = tier_info
        else:
            vacuum_zones.append(tier_name)
    
    # Sort by revenue
    tier_summary.sort(key=lambda x: -x['revenue'])
    
    return {
        'has_data': True,
        'tier_distribution': tier_summary,
        'main_battleground': battleground,
        'new_entrant_focus': new_entrant_focus,
        'vacuum_zones': vacuum_zones,
        'price_range': {'min': round(min_price, 2), 'max': round(max_price, 2)}
    }

def analyze_keyword_trends(keyword_data: dict) -> dict:
    """Analyze keyword trends"""
    keywords = keyword_data.get('keywords', [])
    
    if not keywords:
        return {'has_data': False}
    
    # Find main keyword stats
    total_search_volume = sum(k.get('monthly_search_volume', 0) for k in keywords)
    avg_trend = statistics.mean([k.get('monthly_trend', 0) for k in keywords]) if keywords else 0
    
    # Trend assessment
    if avg_trend > 20:
        trend_status = 'growing_fast'
        trend_icon = '🚀'
    elif avg_trend > 5:
        trend_status = 'growing'
        trend_icon = '📈'
    elif avg_trend < -20:
        trend_status = 'declining_fast'
        trend_icon = '📉'
    elif avg_trend < -5:
        trend_status = 'declining'
        trend_icon = '⬇️'
    else:
        trend_status = 'stable'
        trend_icon = '➡️'
    
    # Competition level
    avg_organic = statistics.mean([k.get('organic_product_count', 0) for k in keywords]) if keywords else 0
    avg_sponsored = statistics.mean([k.get('sponsored_product_count', 0) for k in keywords]) if keywords else 0
    
    if avg_sponsored > 20:
        competition = 'high'
    elif avg_sponsored > 10:
        competition = 'medium'
    else:
        competition = 'low'
    
    return {
        'has_data': True,
        'total_search_volume': total_search_volume,
        'avg_monthly_trend': round(avg_trend, 1),
        'trend_status': trend_status,
        'trend_icon': trend_icon,
        'competition_level': competition,
        'avg_organic_products': int(avg_organic),
        'avg_sponsored_products': int(avg_sponsored),
        'top_keywords': keywords[:5]
    }

def generate_alerts(
    composition: dict,
    new_competitors: dict,
    price_movements: dict,
    keyword_trends: dict,
    review_velocity: dict,
    sov_analysis: dict,
    price_tiers: dict
) -> List[dict]:
    """Generate market alerts"""
    alerts = []
    
    # Review Velocity Alerts
    suspicious = review_velocity.get('suspicious_review_patterns', [])
    if len(suspicious) >= 2:
        alerts.append({
            'type': 'suspicious_reviews',
            'severity': 'HIGH',
            'icon': '🚩',
            'message': f'{len(suspicious)} products with suspicious review velocity (possible manipulation)'
        })
    elif len(suspicious) == 1:
        alerts.append({
            'type': 'suspicious_reviews',
            'severity': 'MEDIUM',
            'icon': '🚩',
            'message': f"Suspicious review pattern: {suspicious[0]['reviews_per_day']} reviews/day"
        })
    
    # SOV Alerts
    if sov_analysis.get('has_data'):
        new_sov = sov_analysis.get('new_brands_sov_pct', 0)
        top3 = sov_analysis.get('top3_concentration', 0)
        
        if new_sov >= 15:
            alerts.append({
                'type': 'sov_shift',
                'severity': 'HIGH',
                'icon': '📢',
                'message': f'New brands capturing {new_sov:.0f}% of market revenue'
            })
        elif new_sov >= 8:
            alerts.append({
                'type': 'sov_shift',
                'severity': 'MEDIUM',
                'icon': '📢',
                'message': f'New brands gaining {new_sov:.0f}% market share'
            })
        
        if top3 >= 70:
            alerts.append({
                'type': 'market_concentration',
                'severity': 'INFO',
                'icon': '👑',
                'message': f'Market concentrated: Top 3 brands hold {top3:.0f}% share'
            })
    
    # Price Tier Alerts
    if price_tiers.get('has_data'):
        new_focus = price_tiers.get('new_entrant_focus')
        vacuum = price_tiers.get('vacuum_zones', [])
        
        if new_focus and new_focus.get('new_pct', 0) >= 40:
            alerts.append({
                'type': 'tier_concentration',
                'severity': 'MEDIUM',
                'icon': '🎯',
                'message': f"New entrants targeting {new_focus['tier']} ({new_focus['new_pct']:.0f}% new)"
            })
        
        if vacuum:
            alerts.append({
                'type': 'price_vacuum',
                'severity': 'INFO',
                'icon': '💡',
                'message': f"Price vacuum: {', '.join(vacuum[:2])} (opportunity?)"
            })
    
    # New competitor alerts
    new_count = new_competitors.get('new_count', 0)
    new_pct = new_competitors.get('new_percentage', 0)
    fast_risers = new_competitors.get('fast_risers', [])
    
    if new_pct >= 20:
        alerts.append({
            'type': 'new_competitors',
            'severity': 'HIGH',
            'icon': '🆕',
            'message': f'{new_count} new competitors ({new_pct:.0f}% of market) in 90 days'
        })
    elif new_count >= 5:
        alerts.append({
            'type': 'new_competitors',
            'severity': 'MEDIUM',
            'icon': '🆕',
            'message': f'{new_count} new competitors detected'
        })
    
    if fast_risers:
        alerts.append({
            'type': 'fast_riser',
            'severity': 'HIGH',
            'icon': '⚡',
            'message': f'{len(fast_risers)} fast-rising new product(s) with $1k+/mo revenue'
        })
    
    # Price war alert
    if price_movements.get('price_war_signal'):
        alerts.append({
            'type': 'price_war',
            'severity': 'HIGH',
            'icon': '⚔️',
            'message': 'Price war signal: Multiple low-price products with high revenue'
        })
    
    # Keyword trend alerts
    if keyword_trends.get('has_data'):
        trend = keyword_trends.get('trend_status', 'stable')
        trend_pct = keyword_trends.get('avg_monthly_trend', 0)
        
        if trend == 'growing_fast':
            alerts.append({
                'type': 'demand_surge',
                'severity': 'HIGH',
                'icon': '🚀',
                'message': f'Search demand surging: +{trend_pct:.0f}% monthly trend'
            })
        elif trend == 'declining_fast':
            alerts.append({
                'type': 'demand_decline',
                'severity': 'HIGH',
                'icon': '📉',
                'message': f'Search demand declining: {trend_pct:.0f}% monthly trend'
            })
    
    # Sort by severity
    severity_order = {'HIGH': 0, 'MEDIUM': 1, 'INFO': 2}
    alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'INFO'), 2))
    
    return alerts

def generate_insights(
    composition: dict,
    new_competitors: dict,
    price_movements: dict,
    keyword_trends: dict,
    alerts: List[dict],
    review_velocity: dict,
    sov_analysis: dict,
    price_tiers: dict
) -> dict:
    """Generate market insights"""
    insights = []
    currency = composition.get('currency', '$')
    
    # Market size (using actual revenue)
    total = composition.get('total_products', 0)
    total_revenue = (composition.get('revenue') or {}).get('total', 0)
    avg_price = (composition.get('price') or {}).get('avg', 0)
    
    if total_revenue > 0:
        insights.append(f"💰 Market: {currency}{total_revenue:,.0f}/mo revenue across {total} products")
    else:
        insights.append(f"📊 Market: {total} products, avg price {currency}{avg_price:.2f}")
    
    # SOV insight
    if sov_analysis.get('has_data'):
        top_brand = sov_analysis.get('brand_ranking', [{}])[0]
        if top_brand:
            insights.append(f"👑 Leader: {top_brand.get('brand')} ({top_brand.get('sov_pct')}% market share)")
    
    # New competitor summary
    new_count = new_competitors.get('new_count', 0)
    if new_count > 0:
        insights.append(f"🆕 {new_count} new entrants in last 90 days")
    
    # Review velocity warning
    suspicious = review_velocity.get('suspicious_count', 0)
    if suspicious > 0:
        insights.append(f"🚩 Warning: {suspicious} product(s) with suspicious review patterns")
    
    # Price tier insight
    if price_tiers.get('has_data'):
        battleground = price_tiers.get('main_battleground')
        if battleground:
            insights.append(f"🎯 Battleground: {battleground['tier']} ({currency}{battleground['revenue']:,.0f} revenue)")
    
    # Keyword trend
    if keyword_trends.get('has_data'):
        trend_icon = keyword_trends.get('trend_icon', '➡️')
        trend_status = keyword_trends.get('trend_status', 'stable')
        competition = keyword_trends.get('competition_level', 'medium')
        insights.append(f"{trend_icon} Demand: {trend_status.replace('_', ' ').title()}, {competition} competition")
    
    # Alert summary
    high_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
    if high_alerts:
        insights.append(f"🚨 {len(high_alerts)} high-priority alert(s)")
    
    return {
        'key_findings': insights[:8],
        'alert_count': len(alerts),
        'high_priority': len(high_alerts),
        'status': '🔴 Major Changes' if len(high_alerts) >= 2 else '🟡 Changes Detected' if alerts else '🟢 Stable'
    }

# === Main Function ===

def monitor_market(
    keyword: str,
    market: str = 'us',
    new_threshold_days: int = 90
) -> dict:
    """Main market monitoring function"""
    
    market = market.lower()
    if market not in SUPPORTED_MARKETS:
        return {'error': f"Unsupported market: {market}. Supported: {', '.join(SUPPORTED_MARKETS)}"}
    
    currency = MARKET_TO_CURRENCY.get(market, '$')
    
    result = {
        'keyword': keyword,
        'marketplace': market.upper(),
        'currency': currency,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v3.0.0',
        'data_source': 'NexScope'
    }
    
    # Fetch products
    print(f"[1/6] Searching products for '{keyword}'...", file=sys.stderr)
    search_result = search_products_js(keyword, market)
    
    products = search_result.get('products', [])
    if not products:
        result['error'] = search_result.get('error', 'No products found')
        return result
    
    print(f"    ✓ Found {len(products)} products", file=sys.stderr)
    result['total_products_found'] = search_result.get('total', len(products))
    
    # Fetch keyword data
    print(f"[2/6] Fetching keyword trends...", file=sys.stderr)
    keyword_data = get_keyword_stats_js(keyword, market)
    
    # Analyze market composition
    print(f"[3/6] Analyzing market composition...", file=sys.stderr)
    composition = analyze_market_composition(products, currency)
    result['composition'] = composition
    
    # Detect new competitors
    new_competitors = detect_new_competitors(products, new_threshold_days)
    result['new_competitors'] = {
        'count': new_competitors['new_count'],
        'percentage': new_competitors['new_percentage'],
        'fast_risers': new_competitors['fast_risers'],
        'top_new_products': new_competitors['new_products'][:5]
    }
    
    # Detect price movements
    price_movements = detect_price_movements(products)
    result['price_movements'] = price_movements
    
    # Analyze keyword trends
    keyword_trends = analyze_keyword_trends(keyword_data)
    result['keyword_trends'] = keyword_trends
    
    # Analyze review velocity
    print(f"[4/6] Analyzing review velocity...", file=sys.stderr)
    review_velocity = analyze_review_velocity(products, new_competitors)
    result['review_velocity'] = review_velocity
    
    # Analyze SOV
    print(f"[5/6] Analyzing SOV (Share of Voice)...", file=sys.stderr)
    sov_analysis = analyze_sov(products, new_competitors)
    result['sov_analysis'] = sov_analysis
    
    # Analyze price tiers
    price_tiers = analyze_price_tiers(products, new_competitors, currency)
    result['price_tiers'] = price_tiers
    
    # Generate alerts
    print(f"[6/6] Generating alerts...", file=sys.stderr)
    alerts = generate_alerts(
        composition, new_competitors, price_movements, keyword_trends,
        review_velocity, sov_analysis, price_tiers
    )
    result['alerts'] = alerts
    
    # Generate insights
    insights = generate_insights(
        composition, new_competitors, price_movements, keyword_trends,
        alerts, review_velocity, sov_analysis, price_tiers
    )
    result['insights'] = insights
    
    print(f"    ✓ {len(alerts)} alerts generated", file=sys.stderr)
    
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
    GRAY = get_color('muted')
    
    keyword = result.get('keyword', 'Unknown')[:20]
    currency = result.get('currency', '$')
    
    # Chart 1: SOV by Brand
    sov = result.get('sov_analysis', {})
    if sov.get('has_data') and sov.get('brand_ranking'):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        brand_ranking = sov['brand_ranking'][:8]
        brands = [b['brand'][:15] for b in brand_ranking]
        revenues = [b['revenue'] for b in brand_ranking]
        
        colors_list = [BLUE, GREEN, ORANGE, PURPLE, RED, GRAY, '#00BCD4', '#E91E63']
        bars = ax.barh(brands, revenues, color=colors_list[:len(brands)], edgecolor='white', linewidth=2)
        
        for bar, brand_data in zip(bars, brand_ranking):
            ax.text(bar.get_width() + max(revenues)*0.02, bar.get_y() + bar.get_height()/2,
                   f"{brand_data['sov_pct']}%", va='center', fontsize=10)
        
        ax.set_xlabel(f'Monthly Revenue ({currency})', fontsize=11)
        ax.set_title(f'MARKET SHARE (SOV): {keyword}', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{currency}{x:,.0f}'))
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_sov.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: SOV", file=sys.stderr)
    
    # Chart 2: Price Tier Distribution
    price_tiers = result.get('price_tiers', {})
    tier_dist = price_tiers.get('tier_distribution', [])
    if tier_dist:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        tiers = [t['tier'] for t in tier_dist if t['total'] > 0][:6]
        totals = [t['total'] for t in tier_dist if t['total'] > 0][:6]
        news = [t['new'] for t in tier_dist if t['total'] > 0][:6]
        
        x = range(len(tiers))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], totals, width, label='Total', color=BLUE, edgecolor='white')
        bars2 = ax.bar([i + width/2 for i in x], news, width, label='New (<90d)', color=ORANGE, edgecolor='white')
        
        ax.set_ylabel('Number of Products', fontsize=11)
        ax.set_title(f'PRICE TIER DISTRIBUTION: {keyword}', fontweight='bold', fontsize=12, pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(tiers, rotation=45, ha='right')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_price_tiers.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Price Tiers", file=sys.stderr)
    
    # Chart 3: Market Composition (New vs Established)
    new_comp = result.get('new_competitors', {})
    composition = result.get('composition', {})
    if new_comp:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        new_count = new_comp.get('count', 0)
        total = composition.get('total_products', 0)
        established = total - new_count
        
        labels = ['New (<90d)', 'Established']
        sizes = [new_count, established]
        colors = [ORANGE, BLUE]
        explode = (0.05, 0)
        
        if sum(sizes) > 0:
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.0f%%',
                   shadow=False, startangle=90)
            ax.set_title(f'MARKET COMPOSITION: {keyword}', fontweight='bold', fontsize=12, pad=15)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/3_composition.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 3: Market Composition", file=sys.stderr)
    
    # Chart 4: Alert Summary
    alerts = result.get('alerts', [])
    if alerts:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'INFO': 0}
        for alert in alerts:
            sev = alert.get('severity', 'INFO')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        labels = list(severity_counts.keys())
        values = list(severity_counts.values())
        colors = [RED, ORANGE, BLUE]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                       str(val), ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Number of Alerts', fontsize=11)
        ax.set_title('MARKET ALERTS', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
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
    parser = argparse.ArgumentParser(description='Market Alert v3.0.0')
    parser.add_argument('params', help='JSON parameters: {"keyword": "bluetooth earbuds"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    if not keyword:
        print("Missing required parameter: keyword", file=sys.stderr)
        sys.exit(1)
    
    result = monitor_market(
        keyword=keyword,
        market=params.get('market', 'us'),
        new_threshold_days=params.get('new_threshold_days', 90)
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
