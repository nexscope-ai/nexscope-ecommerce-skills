#!/usr/bin/env python3
"""
Market Share Analyzer v2.1.0

Analyze market concentration and brand dominance using enhanced data sources:
1. SOV API - Brand visibility/impressions share (via NexScope proxy)
2. Amazon Search API - Product listings, prices, reviews
3. Keepa Deep - Sales volume, BSR trends, competition intensity
4. ABA - Click/Conversion Share for top ASINs

Cross-validates data for more accurate market analysis.

Usage:
    python3 market_share_analyzer.py '{"keyword": "wireless earbuds"}'
    python3 market_share_analyzer.py '{"keyword": "dog food", "limit": 100}' --deep
    python3 market_share_analyzer.py '{"keyword": "yoga mat"}' --chart /tmp/charts
"""

import json
import sys
import os
import argparse
from collections import defaultdict
from typing import Optional
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

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

# Keywords/SOV API config

DOMAIN_MAP = {
    'US': 1, 'UK': 2, 'DE': 3, 'FR': 4, 'JP': 5,
    'CA': 6, 'IT': 8, 'ES': 9, 'MX': 11, 'AU': 13
}

# === Amazon Private Labels ===

AMAZON_BRANDS = {
    'amazon basics', 'amazonbasics', 'amazon essentials', 'amazon commercial',
    'solimo', 'presto!', 'mama bear', 'happy belly', 'wickedly prime',
    'rivet', 'stone & beam', 'pinzon', 'goodthreads', 'daily ritual',
    'lark & ro', 'core 10', 'find.', 'wag', 'denali', 'eero', 'blink'
}

# === Major Brands by Category ===

MAJOR_BRANDS = {
    'electronics': {
        'apple', 'samsung', 'sony', 'lg', 'bose', 'jbl', 'sennheiser', 'beats',
        'anker', 'belkin', 'logitech', 'microsoft', 'razer', 'corsair'
    },
    'home': {
        'cuisinart', 'kitchenaid', 'ninja', 'instant pot', 'vitamix', 'oxo',
        'dyson', 'shark', 'bissell', 'irobot', 'rubbermaid', 'pyrex'
    },
    'beauty': {
        'loreal', 'maybelline', 'neutrogena', 'cerave', 'olay', 'revlon',
        'nyx', 'elf', 'dove', 'pantene', 'garnier', 'tresemme'
    },
    'pet': {
        'purina', 'blue buffalo', 'hills', 'royal canin', 'iams', 'pedigree',
        'kong', 'nylabone', 'petsafe', 'furminator', 'wellness', 'merrick'
    },
    'sports': {
        'nike', 'adidas', 'under armour', 'puma', 'reebok', 'new balance',
        'coleman', 'yeti', 'stanley', 'hydro flask', 'the north face'
    },
    'baby': {
        'pampers', 'huggies', 'graco', 'chicco', 'fisher-price', 'philips avent',
        'dr. browns', 'munchkin', 'baby jogger', 'uppababy'
    },
    'general': set()
}

PRIVATE_LABEL_INDICATORS = [
    'generic', 'unbranded', 'no brand', 'n/a', 'unknown', 'oem', 
    'custom', 'house brand', 'store brand', 'none'
]

# === API Functions ===

def api_call(endpoint: str, payload: dict) -> Optional[dict]:
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
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

def search_products(keyword: str, market: str = 'US', limit: int = 50) -> list:
    """Search Amazon for products"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(market, 'amazon.com')
    })
    
    if not result:
        return []
    
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return result.get('products', [])
    return []

def get_product_detail(asin: str, domain: int = 1) -> Optional[dict]:
    """Get detailed product info from Keepa"""
    result = api_call('/keepa/productRequest', {
        'asin': asin,
        'domain': str(domain)
    })
    if result and isinstance(result, dict):
        # API returns product data nested under 'products' list
        products = result.get('products', [])
        if isinstance(products, list) and products:
            return products[0]
        return result  # fallback if no products key
    return None

def get_product_series(asin: str, domain: int = 1) -> Optional[dict]:
    """Get historical BSR and sales trends from Keepa productSeries."""
    result = api_call('/keepa/productSeries', {
        'asin': asin,
        'domain': domain,
        'days': 90,
        'showBsrMain': 1,
        'showSellerCount': 1,
        'showPrice': 1
    })
    if not result or not isinstance(result, dict):
        return None
    # Extract BSR trend
    bsr_main = result.get('bsrMain', [])
    bsr_trend = 'STABLE'
    if isinstance(bsr_main, list) and len(bsr_main) >= 2:
        try:
            first_bsr = int(bsr_main[0].get('value') or 0) if isinstance(bsr_main[0], dict) else 0
            last_bsr = int(bsr_main[-1].get('value') or 0) if isinstance(bsr_main[-1], dict) else 0
            if first_bsr > 0 and last_bsr > 0:
                change = (last_bsr - first_bsr) / first_bsr
                if change < -0.15: bsr_trend = 'IMPROVING'   # lower BSR = better rank
                elif change > 0.15: bsr_trend = 'DECLINING'
        except (ValueError, TypeError, ZeroDivisionError):
            pass
    seller_count_series = result.get('sellerCount', [])
    avg_sellers = 0
    if isinstance(seller_count_series, list) and seller_count_series:
        vals = [pt.get('value', 0) for pt in seller_count_series if isinstance(pt, dict)]
        avg_sellers = sum(vals) / max(len(vals), 1)
    return {
        'bsr_trend': bsr_trend,
        'avg_seller_count_90d': round(avg_sellers, 1),
        'bsr_data_points': len(bsr_main)
    }

# === Keywords/SOV API ===

def js_api_call(endpoint: str, params: dict = None) -> Optional[dict]:
    """Call Keywords/SOV API via NexScope proxy"""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout{endpoint}"
    try:
        req = Request(url, data=json.dumps(params or {}, ensure_ascii=False).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=30) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        if isinstance(raw, dict) and raw.get('code') == 0:
            data = raw.get('data', {})
            if isinstance(data, dict) and 'code' in data:
                data = data.get('data', {})
            return data
    except Exception as e:
        print(f"SOV API Error [{endpoint}]: {e}", file=sys.stderr)
    return None

def get_share_of_voice(keyword: str, marketplace: str = 'us') -> Optional[dict]:
    """
    Get brand Share of Voice data via proxy
    
    Returns brand-level SOV data including:
    - combined_weighted_sov: Total weighted share of voice
    - organic_weighted_sov: Organic share
    - sponsored_weighted_sov: Sponsored/ad share
    - combined_average_position: Average search position
    - combined_average_price: Average price
    """
    result = js_api_call('/keywords/share-of-voice', {
        'keyword': keyword,
        'marketplace': marketplace.lower()
    })
    
    if result and isinstance(result, dict):
        # API returns brand data under 'shareOfVoice' key
        if 'shareOfVoice' in result:
            return result['shareOfVoice']
        # Legacy/fallback paths
        if 'attributes' in result:
            return result['attributes']
        elif 'data' in result and 'attributes' in result.get('data', {}):
            return result['data']['attributes']
        return result
    return None

# === Brand Classification ===

def normalize_brand(brand: str) -> str:
    """Normalize brand name for comparison"""
    if not brand:
        return 'unknown'
    return brand.lower().strip().replace('-', ' ').replace('_', ' ')

def is_amazon_brand(brand: str) -> bool:
    """Check if brand is Amazon private label"""
    return normalize_brand(brand) in AMAZON_BRANDS

def is_private_label(brand: str, seller: str = '') -> bool:
    """Check if brand is likely private label/white label"""
    brand_norm = normalize_brand(brand)
    seller_norm = normalize_brand(seller) if seller else ''
    
    # Check explicit indicators
    for indicator in PRIVATE_LABEL_INDICATORS:
        if indicator in brand_norm:
            return True
    
    # Brand matches seller (seller's own brand)
    if seller_norm and (brand_norm == seller_norm or brand_norm in seller_norm):
        return True
    
    return False

def classify_brand(brand: str, category: str = 'general', seller: str = '') -> str:
    """
    Classify brand type
    Returns: 'MAJOR', 'AMAZON', 'PRIVATE', 'EMERGING'
    """
    brand_norm = normalize_brand(brand)
    
    if is_amazon_brand(brand):
        return 'AMAZON'
    
    if is_private_label(brand, seller):
        return 'PRIVATE'
    
    # Check major brands
    category_brands = MAJOR_BRANDS.get(category, set()) | MAJOR_BRANDS.get('general', set())
    if brand_norm in category_brands:
        return 'MAJOR'
    
    # Check all categories
    for cat_brands in MAJOR_BRANDS.values():
        if brand_norm in cat_brands:
            return 'MAJOR'
    
    return 'EMERGING'

def detect_category(keyword: str) -> str:
    """Detect category from keyword"""
    keyword_lower = keyword.lower()
    
    category_keywords = {
        'electronics': ['wireless', 'bluetooth', 'usb', 'charger', 'speaker', 'headphone', 'earbuds', 'cable'],
        'home': ['kitchen', 'cookware', 'appliance', 'storage', 'organizer', 'cleaning', 'vacuum'],
        'beauty': ['skincare', 'makeup', 'cosmetic', 'serum', 'cream', 'shampoo', 'beauty', 'hair'],
        'pet': ['dog', 'cat', 'pet', 'puppy', 'kitten', 'aquarium', 'fish', 'bird'],
        'sports': ['fitness', 'workout', 'gym', 'yoga', 'running', 'outdoor', 'camping', 'hiking'],
        'baby': ['baby', 'infant', 'toddler', 'nursery', 'diaper', 'stroller', 'pacifier'],
    }
    
    for category, keywords in category_keywords.items():
        if any(kw in keyword_lower for kw in keywords):
            return category
    
    return 'general'

# === Market Metrics Calculation ===

def calculate_hhi(market_shares: list) -> int:
    """
    Calculate Herfindahl-Hirschman Index
    
    Args:
        market_shares: List of market shares as percentages (0-100)
    
    Returns:
        HHI value (0-10000)
    """
    total = sum(market_shares)
    if total == 0:
        return 0
    
    # Normalize to 100%
    if abs(total - 100) > 1:
        market_shares = [s * 100 / total for s in market_shares]
    
    hhi = sum(share ** 2 for share in market_shares)
    return round(hhi)

def classify_hhi(hhi: int) -> dict:
    """Classify market concentration based on HHI"""
    if hhi < 1000:
        return {
            'level': 'HIGHLY_COMPETITIVE',
            'emoji': '🟢',
            'description': 'Highly competitive - many small players',
            'entry_difficulty': 'LOW'
        }
    elif hhi < 1500:
        return {
            'level': 'UNCONCENTRATED',
            'emoji': '🟢',
            'description': 'Unconcentrated - healthy competition',
            'entry_difficulty': 'LOW'
        }
    elif hhi < 2500:
        return {
            'level': 'MODERATE',
            'emoji': '🟡',
            'description': 'Moderately concentrated - some dominant players',
            'entry_difficulty': 'MEDIUM'
        }
    elif hhi < 5000:
        return {
            'level': 'CONCENTRATED',
            'emoji': '🔴',
            'description': 'Highly concentrated - few major players',
            'entry_difficulty': 'HIGH'
        }
    else:
        return {
            'level': 'NEAR_MONOPOLY',
            'emoji': '⛔',
            'description': 'Near monopoly - dominated by 1-2 players',
            'entry_difficulty': 'VERY_HIGH'
        }

def calculate_concentration_ratios(brand_shares: dict) -> dict:
    """
    Calculate CR1, CR4, CR10 concentration ratios
    
    Args:
        brand_shares: Dict of {brand: share_percentage}
    
    Returns:
        Dict with CR1, CR4, CR10 values
    """
    sorted_shares = sorted(brand_shares.values(), reverse=True)
    
    cr1 = sorted_shares[0] if len(sorted_shares) >= 1 else 0
    cr4 = sum(sorted_shares[:4]) if len(sorted_shares) >= 4 else sum(sorted_shares)
    cr10 = sum(sorted_shares[:10]) if len(sorted_shares) >= 10 else sum(sorted_shares)
    
    return {
        'cr1': round(cr1, 1),
        'cr4': round(cr4, 1),
        'cr10': round(cr10, 1),
        'long_tail': round(100 - cr10, 1)  # Remaining share outside top 10
    }

def classify_market_structure(cr4: float, hhi: int) -> dict:
    """Classify market structure based on CR4 and HHI"""
    if cr4 < 40 and hhi < 1500:
        return {
            'structure': 'COMPETITIVE',
            'emoji': '🟢',
            'description': 'Open market with healthy competition',
            'recommendation': 'Good opportunity for new brands'
        }
    elif cr4 < 60 and hhi < 2500:
        return {
            'structure': 'MONOPOLISTIC_COMPETITION',
            'emoji': '🟡',
            'description': 'Competitive but with some dominant players',
            'recommendation': 'Differentiation strategy recommended'
        }
    elif cr4 < 80:
        return {
            'structure': 'OLIGOPOLY',
            'emoji': '🟠',
            'description': 'Market controlled by few large brands',
            'recommendation': 'Consider niche positioning or premium segment'
        }
    else:
        return {
            'structure': 'NEAR_MONOPOLY',
            'emoji': '🔴',
            'description': 'Market dominated by top brands',
            'recommendation': 'High risk - consider adjacent markets or accessories'
        }

# === Entry Score Calculation ===

def calculate_entry_score(metrics: dict) -> dict:
    """
    Calculate market entry feasibility score
    Higher score = Easier to enter
    
    Args:
        metrics: Dict with hhi, cr1, cr4, cr10, private_label_pct, new_entrant_pct
    
    Returns:
        Dict with score and breakdown
    """
    score = 100
    breakdown = []
    
    # HHI penalty (max -30)
    hhi = metrics.get('hhi', 0)
    if hhi > 4000:
        penalty = 30
        breakdown.append(f"HHI {hhi} (near monopoly): -{penalty}")
    elif hhi > 2500:
        penalty = 25
        breakdown.append(f"HHI {hhi} (concentrated): -{penalty}")
    elif hhi > 1500:
        penalty = 15
        breakdown.append(f"HHI {hhi} (moderate): -{penalty}")
    else:
        penalty = 0
    score -= penalty
    
    # CR4 penalty (max -25)
    cr4 = metrics.get('cr4', 0)
    if cr4 > 80:
        penalty = 25
        breakdown.append(f"CR4 {cr4}% (oligopoly): -{penalty}")
    elif cr4 > 60:
        penalty = 15
        breakdown.append(f"CR4 {cr4}% (concentrated): -{penalty}")
    elif cr4 > 40:
        penalty = 5
        breakdown.append(f"CR4 {cr4}% (moderate): -{penalty}")
    else:
        penalty = 0
    score -= penalty
    
    # Dominant brand penalty (max -20)
    cr1 = metrics.get('cr1', 0)
    if cr1 > 50:
        penalty = 20
        breakdown.append(f"Top brand {cr1}% (dominant): -{penalty}")
    elif cr1 > 30:
        penalty = 10
        breakdown.append(f"Top brand {cr1}% (strong): -{penalty}")
    else:
        penalty = 0
    score -= penalty
    
    # Private label bonus (max +15)
    pl_pct = metrics.get('private_label_pct', 0)
    if pl_pct > 30:
        bonus = 15
        breakdown.append(f"Private label {pl_pct}% (high): +{bonus}")
    elif pl_pct > 15:
        bonus = 8
        breakdown.append(f"Private label {pl_pct}% (moderate): +{bonus}")
    else:
        bonus = 0
    score += bonus
    
    # New entrant bonus (max +15)
    ne_pct = metrics.get('new_entrant_pct', 0)
    if ne_pct > 25:
        bonus = 15
        breakdown.append(f"New entrants {ne_pct}% (open): +{bonus}")
    elif ne_pct > 10:
        bonus = 8
        breakdown.append(f"New entrants {ne_pct}% (some): +{bonus}")
    else:
        bonus = 0
    score += bonus
    
    # Classify score
    score = max(0, min(100, score))
    
    if score >= 75:
        rating = {'level': 'OPEN', 'emoji': '🟢', 'description': 'Good opportunity for new brands'}
    elif score >= 55:
        rating = {'level': 'MODERATE', 'emoji': '🟡', 'description': 'Feasible with differentiation'}
    elif score >= 35:
        rating = {'level': 'CHALLENGING', 'emoji': '🟠', 'description': 'Requires strong USP'}
    else:
        rating = {'level': 'DIFFICULT', 'emoji': '🔴', 'description': 'High barriers - consider alternatives'}
    
    return {
        'score': score,
        'rating': rating,
        'breakdown': breakdown
    }

# === Main Analysis Function ===

def analyze_market_share(keyword: str, market: str = 'US', limit: int = 50, deep: bool = False) -> dict:
    """
    Main analysis function - uses THREE data sources with cross-validation
    
    Data Sources:
    1. SOV API - Brand visibility/impressions share (via NexScope proxy)
    2. Amazon Search API - Product listings, prices, reviews
    3. Keepa Product Request - Sales volume, historical data
    
    Args:
        keyword: Search keyword
        market: Marketplace (US, UK, DE, etc.)
        limit: Number of products to analyze
        deep: Whether to fetch detailed Keepa data
    
    Returns:
        Complete market share analysis with cross-validated data
    """
    print(f"Analyzing market share for: {keyword}", file=sys.stderr)
    
    # === STEP 1: Fetch data sources IN PARALLEL ===
    print("[1/2] Fetching SOV + Amazon Search in parallel...", file=sys.stderr)
    
    # Run SOV and Amazon Search concurrently
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            sov_future = executor.submit(get_share_of_voice, keyword, market)
            search_future = executor.submit(search_products, keyword, market, limit)
            sov_data = sov_future.result(timeout=30)
            products = search_future.result(timeout=30)
    except Exception:
        # Fallback to sequential
        sov_data = get_share_of_voice(keyword, market)
        products = search_products(keyword, market, limit)
    
    # Process SOV data
    sov_brands = {}
    if sov_data and sov_data.get('brands'):
        print(f"  ✓ Got SOV data for {len(sov_data['brands'])} brands", file=sys.stderr)
        for b in sov_data.get('brands', []):
            brand_norm = normalize_brand(b.get('brand', ''))
            sov_brands[brand_norm] = {
                'sov_share': (b.get('combinedWeightedSov') or b.get('combined_weighted_sov') or 0) * 100,
                'organic_sov': (b.get('organicWeightedSov') or b.get('organic_weighted_sov') or 0) * 100,
                'sponsored_sov': (b.get('sponsoredWeightedSov') or b.get('sponsored_weighted_sov') or 0) * 100,
                'avg_position': b.get('combinedAveragePosition') or b.get('combined_average_position'),
                'avg_price_sov': b.get('combinedAveragePrice') or b.get('combined_average_price'),
                'product_count_sov': b.get('combinedProducts') or b.get('combined_products', 0)
            }
    else:
        print("  ✗ SOV data not available", file=sys.stderr)
    search_brands = {}
    if products:
        print(f"  ✓ Got {len(products)} products from search", file=sys.stderr)
        for p in products:
            brand_norm = normalize_brand(p.get('brand', 'Unknown'))
            if brand_norm not in search_brands:
                search_brands[brand_norm] = {
                    'products': [],
                    'total_reviews': 0,
                    'avg_price': 0,
                    'avg_rating': 0
                }
            search_brands[brand_norm]['products'].append(p)
            search_brands[brand_norm]['total_reviews'] += int(p.get('ratings', 0) or p.get('reviews', 0) or 0)
    else:
        print("  ✗ Amazon Search not available", file=sys.stderr)
    
    # Source 3: Keepa Product Request (for sales data)
    print("[3/3] Fetching Keepa sales data...", file=sys.stderr)
    domain = DOMAIN_MAP.get(market, 1)
    keepa_data = {}
    
    # Get top ASINs to fetch (limit to control API costs)
    asins_to_fetch = []
    if products:
        asins_to_fetch = [p.get('asin') for p in products[:20] if p.get('asin')]
    
    # Fetch Keepa productRequest + productSeries data in parallel
    series_cache = {}  # asin -> get_product_series result
    if asins_to_fetch:
        try:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=5) as executor:
                detail_futures = {executor.submit(get_product_detail, asin, domain): asin for asin in asins_to_fetch}
                series_futures = {executor.submit(get_product_series, asin, domain): asin for asin in asins_to_fetch}
                for future in detail_futures:
                    asin = detail_futures[future]
                    try:
                        detail = future.result(timeout=10)
                        if detail:
                            keepa_data[asin] = detail
                    except Exception:
                        pass
                for future in series_futures:
                    asin = series_futures[future]
                    try:
                        series = future.result(timeout=10)
                        if series:
                            series_cache[asin] = series
                    except Exception:
                        pass
        except Exception:
            # Fallback to sequential
            for asin in asins_to_fetch:
                detail = get_product_detail(asin, domain)
                if detail:
                    keepa_data[asin] = detail
                series = get_product_series(asin, domain)
                if series:
                    series_cache[asin] = series

    # Merge series data into keepa_data entries
    for asin, series in series_cache.items():
        if asin in keepa_data:
            keepa_data[asin].update({
                'bsr_trend': series.get('bsr_trend', 'UNKNOWN'),
                'avg_sellers_90d': series.get('avg_seller_count_90d', 0)
            })
        else:
            keepa_data[asin] = {
                'bsr_trend': series.get('bsr_trend', 'UNKNOWN'),
                'avg_sellers_90d': series.get('avg_seller_count_90d', 0)
            }

    print(f"  ✓ Got Keepa data for {len(keepa_data)} products", file=sys.stderr)
    
    # === STEP 2: Cross-validate and merge data ===
    print("Cross-validating data from all sources...", file=sys.stderr)
    
    # If we have all three sources, use fusion analysis
    if sov_brands and search_brands and keepa_data:
        return analyze_with_fusion(keyword, market, sov_data, sov_brands, search_brands, products, keepa_data)
    
    # If only SOV available, use SOV analysis
    if sov_brands:
        print("Using SOV-only analysis (search/Keepa unavailable)", file=sys.stderr)
        return analyze_with_sov(keyword, market, sov_data)
    
    # Fallback to search-based analysis
    print("Using search-based analysis (SOV unavailable)", file=sys.stderr)
    
    # Step 1: Search products
    products = search_products(keyword, market, limit)
    if not products:
        return {'error': 'No products found', 'keyword': keyword}
    
    print(f"Found {len(products)} products", file=sys.stderr)
    
    # Step 2: Detect category
    category = detect_category(keyword)
    
    # Step 3: Aggregate by brand
    brand_data = defaultdict(lambda: {
        'products': [],
        'total_revenue': 0,
        'total_units': 0,
        'avg_price': 0,
        'avg_rating': 0,
        'type': 'EMERGING'
    })
    
    domain = DOMAIN_MAP.get(market, 1)
    
    for i, product in enumerate(products):
        brand = product.get('brand', 'Unknown') or 'Unknown'
        brand_norm = normalize_brand(brand)
        
        if brand_norm in ['', 'unknown', 'n/a', 'none']:
            brand_norm = 'unknown'
        
        asin = product.get('asin')
        price = product.get('price', 0) or 0
        reviews = product.get('ratings', 0) or product.get('reviews', 0) or product.get('reviewCount', 0) or 0
        rating = product.get('rating', 0) or 0
        monthly_sales = product.get('monthlySalesUnits', 0) or product.get('monthly_sales', 0) or product.get('monthlySold', 0) or 0

        # Try to get data from Keepa if missing key metrics
        if (monthly_sales == 0 or reviews == 0) and asin:
            print(f"Fetching Keepa data for {asin}...", file=sys.stderr)
            detail = get_product_detail(asin, domain)
            if detail:
                if monthly_sales == 0:
                    monthly_sales = detail.get('monthlySalesUnits', 0) or detail.get('monthlySold', 0) or 0
                if reviews == 0:
                    reviews = detail.get('reviewCount', 0) or detail.get('ratings', 0) or detail.get('reviews', 0) or 0
                if price == 0:
                    price = detail.get('price', 0) or detail.get('buyBoxPrice', 0) or 0
                    if price > 100:  # Keepa returns cents
                        price = price / 100
        
        # Fallback: estimate from reviews (rough approximation)
        if monthly_sales == 0:
            if reviews > 0:
                # Assume ~2-3% review rate
                monthly_sales = max(50, reviews * 3)
            else:
                monthly_sales = 50  # Minimum baseline
        
        revenue = price * monthly_sales
        
        seller = product.get('seller', '') or ''
        brand_type = classify_brand(brand, category, seller)
        
        product_info = {
            'asin': product.get('asin'),
            'title': product.get('title', '')[:60],
            'price': price,
            'reviews': reviews,
            'rating': rating,
            'monthly_sales': monthly_sales,
            'revenue': revenue
        }

        # Enrich with Keepa productSeries (BSR trend + seller count)
        if asin and i < 20:
            series_data = get_product_series(asin, domain)
            if series_data:
                product_info.update({
                    'bsr_trend': series_data.get('bsr_trend', 'UNKNOWN'),
                    'avg_sellers_90d': series_data.get('avg_seller_count_90d', 0)
                })

        brand_data[brand_norm]['products'].append(product_info)
        brand_data[brand_norm]['total_revenue'] += revenue
        brand_data[brand_norm]['total_units'] += monthly_sales
        brand_data[brand_norm]['type'] = brand_type

        # Deep mode: get Keepa details for product age
        if deep and i < 20:  # Limit to top 20 for cost
            detail = get_product_detail(product.get('asin'), domain)
            if detail:
                available_since = detail.get('availableSince')
                if available_since:
                    brand_data[brand_norm]['first_seen'] = min(
                        brand_data[brand_norm].get('first_seen', available_since),
                        available_since
                    )
    
    # Step 4: Calculate market shares
    total_revenue = sum(b['total_revenue'] for b in brand_data.values())
    
    if total_revenue == 0:
        total_revenue = 1  # Avoid division by zero
    
    brand_shares = {}
    brand_summary = []
    
    for brand, data in brand_data.items():
        share = (data['total_revenue'] / total_revenue) * 100
        brand_shares[brand] = share
        
        avg_price = data['total_revenue'] / data['total_units'] if data['total_units'] > 0 else 0
        
        brand_summary.append({
            'brand': brand,
            'share': round(share, 2),
            'products': len(data['products']),
            'revenue': round(data['total_revenue']),
            'units': data['total_units'],
            'avg_price': round(avg_price, 2),
            'type': data['type']
        })
    
    # Sort by share
    brand_summary.sort(key=lambda x: x['share'], reverse=True)
    
    # Step 5: Calculate metrics
    shares_list = list(brand_shares.values())
    
    hhi = calculate_hhi(shares_list)
    hhi_classification = classify_hhi(hhi)
    
    cr = calculate_concentration_ratios(brand_shares)
    
    structure = classify_market_structure(cr['cr4'], hhi)
    
    # Brand type breakdown
    type_counts = defaultdict(int)
    type_revenue = defaultdict(float)
    for brand, data in brand_data.items():
        type_counts[data['type']] += 1
        type_revenue[data['type']] += data['total_revenue']
    
    private_label_pct = (type_revenue['PRIVATE'] + type_revenue['AMAZON']) / total_revenue * 100
    amazon_pct = type_revenue['AMAZON'] / total_revenue * 100
    major_brand_pct = type_revenue['MAJOR'] / total_revenue * 100
    
    # New entrant analysis (rough estimate based on review count)
    new_entrant_count = sum(1 for b in brand_summary if b['products'] <= 3 and b['share'] > 1)
    new_entrant_pct = new_entrant_count / len(brand_summary) * 100 if brand_summary else 0
    
    # Step 6: Calculate entry score
    metrics_for_score = {
        'hhi': hhi,
        'cr1': cr['cr1'],
        'cr4': cr['cr4'],
        'cr10': cr['cr10'],
        'private_label_pct': private_label_pct,
        'new_entrant_pct': new_entrant_pct
    }
    
    entry_score = calculate_entry_score(metrics_for_score)
    
    # Step 7: Generate insights
    insights = generate_insights(
        hhi_classification, structure, cr, brand_summary,
        private_label_pct, amazon_pct, major_brand_pct
    )
    
    return {
        'keyword': keyword,
        'marketplace': market,
        'category': category,
        'products_analyzed': len(products),
        'brands_found': len(brand_data),
        'total_revenue': round(total_revenue),
        
        'metrics': {
            'hhi': hhi,
            'hhi_classification': hhi_classification,
            'cr1': cr['cr1'],
            'cr4': cr['cr4'],
            'cr10': cr['cr10'],
            'long_tail': cr['long_tail'],
            'equivalent_firms': round(10000 / hhi, 1) if hhi > 0 else 'N/A'
        },
        
        'market_structure': structure,
        
        'brand_breakdown': {
            'major_brands': type_counts['MAJOR'],
            'amazon_brands': type_counts['AMAZON'],
            'private_label': type_counts['PRIVATE'],
            'emerging': type_counts['EMERGING'],
            'major_brand_share': round(major_brand_pct, 1),
            'amazon_share': round(amazon_pct, 1),
            'private_label_share': round(private_label_pct, 1)
        },
        
        'entry_score': entry_score,
        
        'top_brands': brand_summary[:15],
        
        'insights': insights
    }

def analyze_with_fusion(keyword: str, market: str, sov_data: dict, sov_brands: dict, 
                        search_brands: dict, products: list, keepa_data: dict) -> dict:
    """
    Cross-validate and merge data from THREE sources:
    1. SOV API - visibility/impressions
    2. Amazon Search - product listings
    3. Keepa - sales volume
    
    This produces the most accurate market analysis.
    """
    category = detect_category(keyword)
    
    # === Merge brand data from all sources ===
    all_brands = set(sov_brands.keys()) | set(search_brands.keys())
    
    merged_brands = {}
    total_revenue = 0
    total_sov = sum(b.get('sov_share', 0) for b in sov_brands.values())
    
    for brand_norm in all_brands:
        sov_info = sov_brands.get(brand_norm, {})
        search_info = search_brands.get(brand_norm, {})
        
        # Calculate revenue from Keepa data
        brand_revenue = 0
        brand_units = 0
        brand_prices = []
        brand_reviews = search_info.get('total_reviews', 0)
        
        bsr_trends_for_brand = []
        avg_sellers_for_brand = []

        for p in search_info.get('products', []):
            asin = p.get('asin')
            price = p.get('price', 0) or 0

            if asin and asin in keepa_data:
                kdata = keepa_data[asin]
                monthly_sold = kdata.get('monthlySalesUnits', 0) or kdata.get('monthlySold', 0) or 0
                if monthly_sold == 0 and brand_reviews > 0:
                    monthly_sold = max(50, brand_reviews // 10)
                brand_revenue += price * monthly_sold
                brand_units += monthly_sold
                # Collect series enrichment
                if kdata.get('bsr_trend'):
                    bsr_trends_for_brand.append(kdata['bsr_trend'])
                if kdata.get('avg_sellers_90d') is not None:
                    avg_sellers_for_brand.append(kdata['avg_sellers_90d'])
            else:
                # Estimate from reviews
                est_sales = max(50, (p.get('ratings', 0) or p.get('reviews', 0) or 0) // 10)
                brand_revenue += price * est_sales
                brand_units += est_sales

            if price > 0:
                brand_prices.append(price)

        total_revenue += brand_revenue

        # Summarise series data for brand
        brand_bsr_trend = 'UNKNOWN'
        if bsr_trends_for_brand:
            # Use most common trend
            from collections import Counter
            brand_bsr_trend = Counter(bsr_trends_for_brand).most_common(1)[0][0]
        brand_avg_sellers = round(sum(avg_sellers_for_brand) / len(avg_sellers_for_brand), 1) if avg_sellers_for_brand else 0

        # Classify brand
        brand_type = classify_brand(brand_norm, category, '')

        merged_brands[brand_norm] = {
            'brand': brand_norm,
            # SOV data
            'sov_share': sov_info.get('sov_share', 0),
            'organic_sov': sov_info.get('organic_sov', 0),
            'sponsored_sov': sov_info.get('sponsored_sov', 0),
            'avg_position': sov_info.get('avg_position'),
            # Revenue data (from Keepa)
            'revenue': brand_revenue,
            'units': brand_units,
            # Search data
            'products': len(search_info.get('products', [])),
            'total_reviews': brand_reviews,
            'avg_price': sum(brand_prices) / len(brand_prices) if brand_prices else (sov_info.get('avg_price_sov') or 0),
            # Classification
            'type': brand_type,
            # Keepa productSeries enrichment
            'bsr_trend': brand_bsr_trend,
            'avg_sellers_90d': brand_avg_sellers
        }
    
    # Calculate revenue share
    for brand_norm, data in merged_brands.items():
        data['revenue_share'] = (data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
    
    # Normalize SOV to 100%
    if total_sov > 0:
        for brand_norm, data in merged_brands.items():
            data['sov_share_normalized'] = data['sov_share'] / total_sov * 100
    else:
        for brand_norm, data in merged_brands.items():
            data['sov_share_normalized'] = 0
    
    # === Gap Analysis: SOV vs Revenue ===
    gap_analysis = []
    for brand_norm, data in merged_brands.items():
        sov = data.get('sov_share_normalized', 0)
        rev = data.get('revenue_share', 0)
        
        if sov > 0 and rev > 0:
            ratio = sov / rev
            if ratio > 1.5:
                gap_analysis.append({
                    'brand': brand_norm,
                    'sov_share': round(sov, 1),
                    'revenue_share': round(rev, 1),
                    'gap_type': 'HIGH_SOV_LOW_CONVERSION',
                    'insight': f'High visibility but low conversion - possible pricing or review issues'
                })
            elif ratio < 0.67:
                gap_analysis.append({
                    'brand': brand_norm,
                    'sov_share': round(sov, 1),
                    'revenue_share': round(rev, 1),
                    'gap_type': 'LOW_SOV_HIGH_CONVERSION',
                    'insight': f'Strong conversion despite low visibility - likely repeat buyers or external traffic'
                })
    
    # === Calculate metrics using both SOV and Revenue ===
    sov_shares = [d['sov_share_normalized'] for d in merged_brands.values() if d['sov_share_normalized'] > 0]
    rev_shares = [d['revenue_share'] for d in merged_brands.values() if d['revenue_share'] > 0]
    
    # Use average of SOV and Revenue for HHI (more balanced)
    if sov_shares and rev_shares:
        hhi_sov = calculate_hhi(sov_shares)
        hhi_rev = calculate_hhi(rev_shares)
        hhi = (hhi_sov + hhi_rev) // 2
    elif sov_shares:
        hhi = calculate_hhi(sov_shares)
    else:
        hhi = calculate_hhi(rev_shares) if rev_shares else 0
    
    hhi_classification = classify_hhi(hhi)
    
    # CR ratios from revenue (more accurate)
    brand_shares = {k: v['revenue_share'] for k, v in merged_brands.items()}
    cr = calculate_concentration_ratios(brand_shares)
    
    structure = classify_market_structure(cr['cr4'], hhi)
    
    # === Traffic analysis from SOV ===
    total_organic = sum(d.get('organic_sov', 0) for d in merged_brands.values())
    total_sponsored = sum(d.get('sponsored_sov', 0) for d in merged_brands.values())
    total_traffic = total_organic + total_sponsored
    
    organic_pct = (total_organic / total_traffic * 100) if total_traffic > 0 else 0
    sponsored_pct = (total_sponsored / total_traffic * 100) if total_traffic > 0 else 0
    
    if sponsored_pct > 40:
        traffic_type = 'AD_HEAVY'
        traffic_assessment = 'Significant ad spend required - top positions dominated by ads'
    elif sponsored_pct > 20:
        traffic_type = 'BALANCED'
        traffic_assessment = 'Mix of organic and paid - moderate ad budget needed'
    else:
        traffic_type = 'ORGANIC'
        traffic_assessment = 'Primarily organic - good SEO can drive traffic'
    
    # === Brand breakdown ===
    type_counts = defaultdict(int)
    type_revenue = defaultdict(float)
    for data in merged_brands.values():
        type_counts[data['type']] += 1
        type_revenue[data['type']] += data['revenue_share']
    
    # === Entry score ===
    metrics_for_score = {
        'hhi': hhi,
        'cr1': cr['cr1'],
        'cr4': cr['cr4'],
        'cr10': cr['cr10'],
        'private_label_pct': type_revenue['PRIVATE'] + type_revenue['AMAZON'],
        'new_entrant_pct': type_revenue['EMERGING']
    }
    entry_score = calculate_entry_score(metrics_for_score)
    
    # === Sort and prepare brand summary ===
    brand_summary = []
    for brand_norm, data in merged_brands.items():
        brand_summary.append({
            'brand': brand_norm,
            'sov_share': round(data['sov_share_normalized'], 2),
            'revenue_share': round(data['revenue_share'], 2),
            'gap': round(data['sov_share_normalized'] - data['revenue_share'], 2),
            'products': data['products'],
            'avg_price': round(data['avg_price'] or 0, 2),
            'avg_position': data['avg_position'],
            'organic_sov': round(data['organic_sov'] or 0, 2),
            'sponsored_sov': round(data['sponsored_sov'] or 0, 2),
            'type': data['type']
        })
    
    brand_summary.sort(key=lambda x: x['revenue_share'], reverse=True)
    
    # === Deep Analysis ===
    
    # Price segment analysis
    prices = [d['avg_price'] for d in merged_brands.values() if d['avg_price'] > 0]
    if prices:
        avg_price = sum(prices) / len(prices)
        price_segments = {
            'budget': [d for d in merged_brands.values() if 0 < d['avg_price'] < avg_price * 0.7],
            'mid': [d for d in merged_brands.values() if avg_price * 0.7 <= d['avg_price'] <= avg_price * 1.3],
            'premium': [d for d in merged_brands.values() if d['avg_price'] > avg_price * 1.3]
        }
    else:
        price_segments = {'budget': [], 'mid': [], 'premium': []}
        avg_price = 0
    
    # Find winning price segment
    segment_revenue = {
        'budget': sum(d['revenue_share'] for d in price_segments['budget']),
        'mid': sum(d['revenue_share'] for d in price_segments['mid']),
        'premium': sum(d['revenue_share'] for d in price_segments['premium'])
    }
    winning_segment = max(segment_revenue, key=segment_revenue.get) if segment_revenue else 'mid'
    
    # Competitive moat analysis - comprehensive brand profiling
    brands_with_moat = []
    for brand_norm, data in merged_brands.items():
        moat_signals = []
        selection_reasons = []
        threat_level = 'LOW'
        
        # High conversion moat
        if data['revenue_share'] > data['sov_share_normalized'] * 1.5 and data['revenue_share'] > 3:
            moat_signals.append('high_conversion')
            selection_reasons.append(f"Abnormally high conversion rate (SOV {data['sov_share_normalized']:.1f}% -> Revenue {data['revenue_share']:.1f}%)")
            threat_level = 'MEDIUM'
        
        # Review moat
        if data.get('total_reviews', 0) > 1000:
            moat_signals.append('review_moat')
            selection_reasons.append(f"Review moat ({data['total_reviews']} reviews, hard for new products to catch up)")
            threat_level = 'HIGH'
        elif data.get('total_reviews', 0) > 500:
            moat_signals.append('review_advantage')
            selection_reasons.append(f"Review advantage ({data['total_reviews']} reviews)")
        
        # Position lock
        if data.get('avg_position') and data['avg_position'] < 10 and data['revenue_share'] > 5:
            moat_signals.append('position_lock')
            selection_reasons.append(f"Locked top position (avg rank #{data['avg_position']:.0f})")
            threat_level = 'HIGH'
        
        # Price leader
        if data['avg_price'] > 0 and data['avg_price'] < avg_price * 0.7 and data['revenue_share'] > 5:
            moat_signals.append('price_leader')
            selection_reasons.append(f"Price leader (${data['avg_price']:.2f}, 30%+ below avg price)")
            threat_level = 'HIGH' if threat_level != 'HIGH' else threat_level
        
        # Premium player
        if data['avg_price'] > avg_price * 1.3 and data['revenue_share'] > 3:
            moat_signals.append('premium_player')
            selection_reasons.append(f"Premium player (${data['avg_price']:.2f}, 30%+ above avg price and still selling)")
        
        # Market leader
        if data['revenue_share'] > 15:
            moat_signals.append('market_leader')
            selection_reasons.append(f"Market leader ({data['revenue_share']:.1f}% share)")
            threat_level = 'HIGH'
        elif data['revenue_share'] > 8:
            moat_signals.append('major_player')
            selection_reasons.append(f"Major player ({data['revenue_share']:.1f}% share)")
            threat_level = 'MEDIUM' if threat_level == 'LOW' else threat_level
        
        # Ad-heavy player
        if data.get('sponsored_sov', 0) > data.get('organic_sov', 0) * 2 and data.get('sponsored_sov', 0) > 5:
            moat_signals.append('ad_heavy')
            selection_reasons.append(f"Ad-driven (Sponsored SOV {data['sponsored_sov']:.1f}% vs Organic {data['organic_sov']:.1f}%)")
        
        if moat_signals:
            brands_with_moat.append({
                'brand': brand_norm,
                'moat': moat_signals,
                'share': round(data['revenue_share'], 1),
                'threat_level': threat_level,
                'why_selected': selection_reasons,
                'profile': {
                    'avg_price': round(data['avg_price'] or 0, 2),
                    'products': data['products'],
                    'sov': round(data['sov_share_normalized'] or 0, 1),
                    'revenue': round(data['revenue_share'] or 0, 1)
                }
            })
    
    # Sort by threat level then share
    threat_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    brands_with_moat.sort(key=lambda x: (threat_order.get(x['threat_level'], 3), -x['share']))
    
    # Entry opportunity scoring
    entry_opportunities = []
    
    # Check for price gap opportunities
    if segment_revenue['premium'] < 20 and len(price_segments['premium']) < 3:
        entry_opportunities.append({
            'type': 'PREMIUM_GAP',
            'description': f'Premium segment underserved (<20% share, only {len(price_segments["premium"])} brands)',
            'recommendation': f'Enter at ${avg_price * 1.5:.0f}+ with quality differentiation',
            'difficulty': 'MEDIUM'
        })
    
    if segment_revenue['budget'] < 15:
        entry_opportunities.append({
            'type': 'BUDGET_GAP',
            'description': f'Budget segment opportunity (<15% share)',
            'recommendation': f'Enter at <${avg_price * 0.7:.0f} with volume strategy',
            'difficulty': 'LOW'
        })
    
    # Check for weak leaders (high SOV, low conversion)
    weak_leaders = [g for g in gap_analysis if g['gap_type'] == 'HIGH_SOV_LOW_CONVERSION' and g['sov_share'] > 5]
    if weak_leaders:
        entry_opportunities.append({
            'type': 'WEAK_LEADER',
            'description': f'{len(weak_leaders)} top brands converting poorly despite high visibility',
            'recommendation': 'Target their keywords with better product/pricing',
            'difficulty': 'MEDIUM',
            'targets': [w['brand'] for w in weak_leaders[:3]]
        })
    
    # Check organic opportunity
    if organic_pct > 80:
        entry_opportunities.append({
            'type': 'SEO_PLAY',
            'description': f'{organic_pct:.0f}% organic traffic - SEO dominates this market',
            'recommendation': 'Focus on listing optimization, A+ content, keyword ranking',
            'difficulty': 'LOW'
        })
    
    # === Build comprehensive insights ===
    insights = {
        'summary': '',
        'market_health': '',
        'opportunities': [],
        'challenges': [],
        'recommended_strategy': [],
        'entry_opportunities': entry_opportunities,
        'competitive_threats': brands_with_moat[:10],
        'competitive_threats_summary': '',  # Will be filled below
        'price_analysis': {
            'market_avg_price': round(avg_price, 2),
            'winning_segment': winning_segment,
            'segment_shares': {k: round(v, 1) for k, v in segment_revenue.items()},
            'analysis': '',
            'recommendation': '',
            'price_bands': {
                'budget': f'<${avg_price * 0.7:.0f}',
                'mid': f'${avg_price * 0.7:.0f}-${avg_price * 1.3:.0f}',
                'premium': f'>${avg_price * 1.3:.0f}'
            }
        },
        'data_quality': {
            'sov_brands': len(sov_brands),
            'search_products': len(products),
            'keepa_products': len(keepa_data),
            'cross_validation': 'FULL' if len(sov_brands) > 0 and len(keepa_data) > 0 else 'PARTIAL'
        }
    }
    
    # Generate summary narrative
    if hhi < 1000:
        insights['market_health'] = 'HIGHLY_FRAGMENTED'
        insights['summary'] = f"Highly fragmented market with {len(merged_brands)} brands competing, no clear leader."
    elif hhi < 1500:
        insights['market_health'] = 'HEALTHY_COMPETITION'
        insights['summary'] = f"Healthy competitive market, top brand ({cr['cr1']:.0f}%) has not formed a monopoly, opportunities for new brands."
    elif hhi < 2500:
        insights['market_health'] = 'MODERATELY_CONCENTRATED'
        insights['summary'] = f"Moderately concentrated market, Top 4 hold {cr['cr4']:.0f}%, differentiation strategy needed."
    else:
        insights['market_health'] = 'HIGHLY_CONCENTRATED'
        insights['summary'] = f"Highly concentrated market, dominated by top brand ({cr['cr1']:.0f}%), high barrier to entry."
    
    # Price analysis - narrative format
    budget_pct = segment_revenue.get('budget', 0)
    mid_pct = segment_revenue.get('mid', 0)
    premium_pct = segment_revenue.get('premium', 0)
    
    price_analysis_text = f"Market avg price ${avg_price:.2f}."
    
    if winning_segment == 'budget':
        price_analysis_text += f" Budget segment (<${avg_price*0.7:.0f}) accounts for {budget_pct:.0f}% of sales, price-sensitive market."
        insights['price_analysis']['analysis'] = price_analysis_text
        insights['price_analysis']['recommendation'] = f"Two paths: (1) Volume play at low price, price <${avg_price*0.7:.0f}; (2) Differentiate with mid-to-premium positioning, avoid price wars."
    elif winning_segment == 'premium':
        price_analysis_text += f" Premium segment (>${avg_price*1.3:.0f}) accounts for {premium_pct:.0f}% of sales, consumers willing to pay for quality."
        insights['price_analysis']['analysis'] = price_analysis_text
        insights['price_analysis']['recommendation'] = f"Go premium, price at ${avg_price*1.3:.0f}+, emphasize quality, design, and brand story."
    else:
        price_analysis_text += f" Mid-range (${avg_price*0.7:.0f}-${avg_price*1.3:.0f}) accounts for {mid_pct:.0f}% of sales, mainstream price range."
        insights['price_analysis']['analysis'] = price_analysis_text
        insights['price_analysis']['recommendation'] = f"Recommended pricing ${avg_price*0.8:.0f}-${avg_price*1.2:.0f}, compete in the mainstream range. Or differentiate at both ends."
    
    # Add segment breakdown narrative
    insights['price_analysis']['segment_breakdown'] = (
        f"Budget (<${avg_price*0.7:.0f}): {budget_pct:.0f}% | "
        f"Mid-range: {mid_pct:.0f}% | "
        f"Premium (>${avg_price*1.3:.0f}): {premium_pct:.0f}%"
    )
    
    # Competitive threats narrative summary
    high_threats = [b for b in brands_with_moat if b['threat_level'] == 'HIGH']
    medium_threats = [b for b in brands_with_moat if b['threat_level'] == 'MEDIUM']
    
    threat_summary_parts = []
    if high_threats:
        threat_summary_parts.append(f"⚠️ {len(high_threats)} high-threat brands require close attention")
    if medium_threats:
        threat_summary_parts.append(f"📊 {len(medium_threats)} medium-threat brands")
    if not brands_with_moat:
        threat_summary_parts.append("✅ No competitors with significant moats detected")
    
    insights['competitive_threats_summary'] = '; '.join(threat_summary_parts) if threat_summary_parts else "Fragmented competition, no significant threats"
    
    # Gap analysis insights
    if gap_analysis:
        high_sov_low_rev = [g for g in gap_analysis if g['gap_type'] == 'HIGH_SOV_LOW_CONVERSION']
        low_sov_high_rev = [g for g in gap_analysis if g['gap_type'] == 'LOW_SOV_HIGH_CONVERSION']
        
        if high_sov_low_rev:
            insights['opportunities'].append({
                'type': 'CONVERSION_GAP',
                'insight': f"{len(high_sov_low_rev)} brands with high visibility but poor conversion",
                'action': "Their customers are looking for alternatives, capture their traffic"
            })
        
        if low_sov_high_rev:
            insights['challenges'].append({
                'type': 'HIDDEN_COMPETITORS',
                'insight': f"{len(low_sov_high_rev)} brands with low visibility but strong conversion",
                'action': "Study their repeat purchase and direct-to-consumer strategies"
            })
    
    # Standard opportunities
    if cr['cr1'] < 25:
        insights['opportunities'].append({
            'type': 'NO_DOMINANT_LEADER',
            'insight': "No dominant brand, market leadership is up for grabs",
            'action': "Rapid positioning possible through product innovation + marketing"
        })
    
    if type_revenue['AMAZON'] < 5:
        insights['opportunities'].append({
            'type': 'LOW_AMAZON_PRESENCE',
            'insight': "Low Amazon private label presence, less platform competition pressure",
            'action': "Safe to invest, low risk of Amazon copying the product"
        })
    
    if organic_pct > 70:
        insights['opportunities'].append({
            'type': 'ORGANIC_MARKET',
            'insight': f"Organic traffic dominant ({organic_pct:.0f}%), manageable ad costs",
            'action': "Prioritize listing optimization and review accumulation"
        })
    
    # Standard challenges
    if cr['cr1'] > 40:
        insights['challenges'].append({
            'type': 'DOMINANT_LEADER',
            'insight': f"Top brand holds {cr['cr1']:.0f}% share, high brand loyalty",
            'action': "Avoid head-on competition, find a niche entry point"
        })
    
    if cr['cr4'] > 70:
        insights['challenges'].append({
            'type': 'OLIGOPOLY',
            'insight': f"Top 4 hold {cr['cr4']:.0f}% share, stable market structure",
            'action': "Differentiation or niche positioning required"
        })
    
    if sponsored_pct > 40:
        insights['challenges'].append({
            'type': 'AD_HEAVY',
            'insight': f"Ad traffic accounts for {sponsored_pct:.0f}%, high customer acquisition cost",
            'action': "Prepare adequate ad budget, or target long-tail keywords"
        })
    
    # Strategy recommendations
    if entry_opportunities:
        best_opp = entry_opportunities[0]
        insights['recommended_strategy'].append({
            'priority': 'HIGH',
            'strategy': best_opp['type'],
            'detail': best_opp['recommendation']
        })
    
    if hhi < 1500:
        insights['recommended_strategy'].append({
            'priority': 'MEDIUM',
            'strategy': 'DIRECT_ENTRY',
            'detail': "Open market, direct entry viable, focus on product quality and listing optimization"
        })
    else:
        insights['recommended_strategy'].append({
            'priority': 'MEDIUM',
            'strategy': 'DIFFERENTIATION',
            'detail': "Concentrated market, identify a differentiated positioning before entry"
        })
    
    # Top converting ASINs
    top_asins = sov_data.get('top_asins', [])
    
    return {
        'keyword': keyword,
        'marketplace': market,
        'category': category,
        'data_source': 'fusion_3_sources',
        'data_quality': {
            'js_sov': len(sov_brands) > 0,
            'amazon_search': len(products),
            'keepa_data': len(keepa_data),
            'cross_validated': True
        },
        'search_volume': sov_data.get('estimated_30_day_search_volume', 0),
        'brands_found': len(merged_brands),
        'total_revenue_estimated': round(total_revenue),
        
        'metrics': {
            'hhi': hhi,
            'hhi_sov': calculate_hhi(sov_shares) if sov_shares else 0,
            'hhi_revenue': calculate_hhi(rev_shares) if rev_shares else 0,
            'hhi_classification': hhi_classification,
            'cr1': cr['cr1'],
            'cr4': cr['cr4'],
            'cr10': cr['cr10'],
            'long_tail': cr['long_tail'],
            'equivalent_firms': round(10000 / hhi, 1) if hhi > 0 else 'N/A'
        },
        
        'market_structure': structure,
        
        'traffic_analysis': {
            'organic_pct': round(organic_pct, 1),
            'sponsored_pct': round(sponsored_pct, 1),
            'traffic_type': traffic_type,
            'assessment': traffic_assessment
        },
        
        'brand_breakdown': {
            'major_brands': type_counts['MAJOR'],
            'amazon_brands': type_counts['AMAZON'],
            'private_label': type_counts['PRIVATE'],
            'emerging': type_counts['EMERGING'],
            'major_brand_share': round(type_revenue['MAJOR'], 1),
            'amazon_share': round(type_revenue['AMAZON'], 1),
            'private_label_share': round(type_revenue['PRIVATE'] + type_revenue['AMAZON'], 1)
        },
        
        'entry_score': entry_score,
        
        'gap_analysis': gap_analysis[:10],  # Top 10 gaps
        
        'top_brands': brand_summary[:15],
        
        'top_converting_asins': [
            {
                'asin': a.get('asin'),
                'name': a.get('name', '')[:60] if a.get('name') else None,
                'brand': a.get('brand'),
                'clicks': a.get('clicks', 0),
                'conversions': a.get('conversions', 0),
                'conversion_rate': a.get('conversion_rate', 0)
            }
            for a in top_asins[:5]
        ],
        
        'insights': insights
    }

def analyze_with_sov(keyword: str, market: str, sov_data: dict) -> dict:
    """
    Analyze market using Share of Voice data
    This is the preferred method - more accurate than search-based analysis
    """
    brands_data = sov_data.get('brands', [])
    
    # Detect category
    category = detect_category(keyword)
    
    # Process brand data
    brand_summary = []
    brand_shares = {}
    
    total_sov = sum((b.get('combinedWeightedSov') or b.get('combined_weighted_sov') or 0) for b in brands_data)
    if total_sov == 0:
        total_sov = 1  # Avoid division by zero
    
    type_counts = defaultdict(int)
    type_sov = defaultdict(float)
    
    organic_total = 0
    sponsored_total = 0
    
    for b in brands_data:
        brand_name = b.get('brand', 'Unknown')
        brand_norm = normalize_brand(brand_name)
        
        # Calculate share (normalize to 100%)
        raw_sov = b.get('combinedWeightedSov') or b.get('combined_weighted_sov') or 0
        sov = raw_sov * 100 / total_sov if total_sov > 0 else 0
        brand_shares[brand_norm] = sov
        
        # Classify brand
        brand_type = classify_brand(brand_name, category, '')
        type_counts[brand_type] += 1
        type_sov[brand_type] += sov
        
        # Track organic vs sponsored
        organic_sov = b.get('organicWeightedSov') or b.get('organic_weighted_sov') or 0
        sponsored_sov = b.get('sponsoredWeightedSov') or b.get('sponsored_weighted_sov') or 0
        organic_total += organic_sov
        sponsored_total += sponsored_sov
        
        brand_summary.append({
            'brand': brand_name,
            'share': round(sov, 2),
            'products': b.get('combinedProducts') or b.get('combined_products', 0),
            'avg_price': (b.get('combinedAveragePrice') or b.get('combined_average_price')) or 0,
            'avg_position': (b.get('combinedAveragePosition') or b.get('combined_average_position')) or 0,
            'organic_sov': round((b.get('organicWeightedSov') or b.get('organic_weighted_sov') or 0) * 100, 2),
            'sponsored_sov': round((b.get('sponsoredWeightedSov') or b.get('sponsored_weighted_sov') or 0) * 100, 2),
            'organic_products': b.get('organicProducts') or b.get('organic_products', 0),
            'sponsored_products': b.get('sponsoredProducts') or b.get('sponsored_products', 0),
            'type': brand_type
        })
    
    # Sort by share
    brand_summary.sort(key=lambda x: x['share'], reverse=True)
    
    # Calculate metrics
    shares_list = list(brand_shares.values())
    hhi = calculate_hhi(shares_list)
    hhi_classification = classify_hhi(hhi)
    cr = calculate_concentration_ratios(brand_shares)
    structure = classify_market_structure(cr['cr4'], hhi)
    
    # Traffic type analysis
    total_traffic = organic_total + sponsored_total
    organic_pct = (organic_total / total_traffic * 100) if total_traffic > 0 else 0
    sponsored_pct = (sponsored_total / total_traffic * 100) if total_traffic > 0 else 0
    
    if sponsored_pct > 40:
        traffic_type = 'AD_HEAVY'
        traffic_assessment = 'Significant ad spend required - top positions dominated by ads'
    elif sponsored_pct > 20:
        traffic_type = 'BALANCED'
        traffic_assessment = 'Mix of organic and paid - moderate ad budget needed'
    else:
        traffic_type = 'ORGANIC'
        traffic_assessment = 'Primarily organic - good SEO can drive traffic'
    
    # Brand breakdown
    private_label_pct = type_sov['PRIVATE'] + type_sov['AMAZON']
    amazon_pct_val = type_sov['AMAZON']
    major_pct_val = type_sov['MAJOR']
    
    # Entry score
    metrics_for_score = {
        'hhi': hhi,
        'cr1': cr['cr1'],
        'cr4': cr['cr4'],
        'cr10': cr['cr10'],
        'private_label_pct': private_label_pct,
        'new_entrant_pct': 100 - major_pct_val - amazon_pct_val - private_label_pct  # Emerging brands
    }
    entry_score = calculate_entry_score(metrics_for_score)
    
    # Insights
    insights = generate_insights(
        hhi_classification, structure, cr, brand_summary,
        private_label_pct, amazon_pct_val, major_pct_val
    )
    
    # Add SOV-specific insights
    if sponsored_pct > 30:
        insights['challenges'].append(f"High ad competition ({sponsored_pct:.0f}% sponsored SOV)")
    if organic_pct > 70:
        insights['opportunities'].append(f"Organic-driven market ({organic_pct:.0f}% organic SOV) - SEO opportunity")
    
    # Top converting ASINs
    top_asins = sov_data.get('top_asins', [])
    
    return {
        'keyword': keyword,
        'marketplace': market,
        'category': category,
        'data_source': 'nexscope_sov',  # Indicate data source
        'search_volume': sov_data.get('estimated_30_day_search_volume', 0),
        'brands_found': len(brands_data),
        
        'metrics': {
            'hhi': hhi,
            'hhi_classification': hhi_classification,
            'cr1': cr['cr1'],
            'cr4': cr['cr4'],
            'cr10': cr['cr10'],
            'long_tail': cr['long_tail'],
            'equivalent_firms': round(10000 / hhi, 1) if hhi > 0 else 'N/A'
        },
        
        'market_structure': structure,
        
        'traffic_analysis': {
            'organic_pct': round(organic_pct, 1),
            'sponsored_pct': round(sponsored_pct, 1),
            'traffic_type': traffic_type,
            'assessment': traffic_assessment
        },
        
        'brand_breakdown': {
            'major_brands': type_counts['MAJOR'],
            'amazon_brands': type_counts['AMAZON'],
            'private_label': type_counts['PRIVATE'],
            'emerging': type_counts['EMERGING'],
            'major_brand_share': round(major_pct_val, 1),
            'amazon_share': round(amazon_pct_val, 1),
            'private_label_share': round(private_label_pct, 1)
        },
        
        'entry_score': entry_score,
        
        'top_brands': brand_summary[:15],
        
        'top_converting_asins': [
            {
                'asin': a.get('asin'),
                'name': a.get('name', '')[:60] if a.get('name') else None,
                'brand': a.get('brand'),
                'clicks': a.get('clicks', 0),
                'conversions': a.get('conversions', 0),
                'conversion_rate': a.get('conversion_rate', 0)
            }
            for a in top_asins[:5]
        ],
        
        'insights': insights
    }

def generate_insights(hhi_class: dict, structure: dict, cr: dict, 
                      brands: list, private_pct: float, amazon_pct: float,
                      major_pct: float) -> dict:
    """Generate actionable insights based on analysis"""
    
    opportunities = []
    challenges = []
    strategy = []
    
    # Opportunity assessment
    if cr['cr1'] < 25:
        opportunities.append("No single dominant brand - market leadership is attainable")
    
    if cr['long_tail'] > 30:
        opportunities.append(f"Long tail has {cr['long_tail']:.0f}% share - niche opportunities exist")
    
    if private_pct > 20:
        opportunities.append(f"High private label presence ({private_pct:.0f}%) - brand building can differentiate")
    
    if amazon_pct < 5:
        opportunities.append("Low Amazon brand presence - less direct competition from Amazon")
    
    # Challenge assessment
    if cr['cr1'] > 40:
        challenges.append(f"Dominant leader with {cr['cr1']:.0f}% share - hard to compete directly")
    
    if cr['cr4'] > 70:
        challenges.append(f"Top 4 brands control {cr['cr4']:.0f}% - oligopoly dynamics")
    
    if major_pct > 60:
        challenges.append(f"Established brands hold {major_pct:.0f}% - high brand loyalty expected")
    
    if amazon_pct > 15:
        challenges.append(f"Amazon brands have {amazon_pct:.0f}% share - price pressure likely")
    
    # Strategy recommendations
    if hhi_class['level'] in ['HIGHLY_COMPETITIVE', 'UNCONCENTRATED']:
        strategy.append("Direct entry viable - focus on product quality and marketing")
    elif hhi_class['level'] == 'MODERATE':
        strategy.append("Differentiation required - find underserved segment or unique value prop")
    else:
        strategy.append("Niche strategy recommended - avoid direct competition with leaders")
    
    if private_pct > 25:
        strategy.append("Premium positioning opportunity - private labels create price anchor")
    
    if cr['long_tail'] > 40:
        strategy.append("Consider acquisition or partnership with emerging brands")
    
    # Top brand analysis
    if brands:
        top_brand = brands[0]
        if top_brand['type'] == 'MAJOR':
            strategy.append(f"Leader is established ({top_brand['brand']}) - focus on gaps they don't cover")
        elif top_brand['type'] in ['PRIVATE', 'AMAZON']:
            strategy.append(f"Leader is private label - opportunity to build premium brand")
    
    return {
        'opportunities': opportunities,
        'challenges': challenges,
        'recommended_strategy': strategy,
        'verdict': structure['recommendation']
    }

# === Chart Generation ===

def generate_charts(analysis: dict, output_dir: str) -> list:
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        import numpy as np
    except ImportError:
        print("matplotlib not installed, skipping charts", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    charts = []
    keyword = analysis.get('keyword', 'market')[:20]
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Chart 1: Market Share Pie
    try:
        top_brands = analysis.get('top_brands', [])[:8]
        if top_brands:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            labels = [b['brand'][:15] for b in top_brands]
            sizes = [b['share'] for b in top_brands]
            
            # Add "Others" if there's remaining share
            others_share = 100 - sum(sizes)
            if others_share > 1:
                labels.append('Others')
                sizes.append(others_share)
            
            # Colors based on brand type
            colors = []
            for b in top_brands:
                if b['type'] == 'MAJOR':
                    colors.append(get_color('primary'))  # Blue
                elif b['type'] == 'AMAZON':
                    colors.append(get_color('secondary'))  # Orange
                elif b['type'] == 'PRIVATE':
                    colors.append(get_color('muted'))  # Gray
                else:
                    colors.append(get_color('good'))  # Green
            if others_share > 1:
                colors.append('#E0E0E0')  # Light gray
            
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                colors=colors, startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            # Style
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
            
            ax.set_title(f'MARKET SHARE DISTRIBUTION: {keyword.upper()}', 
                        fontsize=14, fontweight='bold', pad=20)
            
            # Legend for brand types
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('primary'), markersize=10, label='Major Brand'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('secondary'), markersize=10, label='Amazon Brand'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('muted'), markersize=10, label='Private Label'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('good'), markersize=10, label='Emerging'),
            ]
            ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
            
            chart_path = os.path.join(output_dir, 'market_share.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate pie chart: {e}", file=sys.stderr)
    
    # Chart 2: Concentration Metrics Bar
    try:
        metrics = analysis.get('metrics', {})
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left: CR ratios
        cr_labels = ['CR1\n(Top Brand)', 'CR4\n(Top 4)', 'CR10\n(Top 10)']
        cr_values = [metrics.get('cr1', 0), metrics.get('cr4', 0), metrics.get('cr10', 0)]
        
        colors = []
        for v, threshold in zip(cr_values, [30, 60, 80]):
            if v > threshold:
                colors.append(get_color('hot'))
            elif v > threshold * 0.7:
                colors.append(get_color('warning'))
            else:
                colors.append(get_color('good'))
        
        bars = ax1.bar(cr_labels, cr_values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, cr_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax1.set_ylabel('Market Share (%)', fontsize=11, fontweight='bold')
        ax1.set_title('CONCENTRATION RATIOS', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, 110)
        ax1.axhline(y=60, color='gray', linestyle='--', alpha=0.5, label='Concern threshold')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Right: HHI gauge
        hhi = metrics.get('hhi', 0)
        hhi_max = 5000  # Cap for visualization
        
        ax2.barh(['HHI'], [min(hhi, hhi_max)], color=get_color('primary'), edgecolor='white', linewidth=2)
        ax2.barh(['HHI'], [hhi_max], color='#E0E0E0', alpha=0.3)
        
        # Add threshold markers
        ax2.axvline(x=1500, color=get_color('good'), linestyle='--', linewidth=2, label='Low (<1500)')
        ax2.axvline(x=2500, color=get_color('warning'), linestyle='--', linewidth=2, label='Moderate (2500)')
        ax2.axvline(x=4000, color=get_color('hot'), linestyle='--', linewidth=2, label='High (4000)')
        
        ax2.text(min(hhi, hhi_max) + 100, 0, f'{hhi}', va='center', fontsize=14, fontweight='bold')
        
        ax2.set_xlabel('HHI Index', fontsize=11, fontweight='bold')
        ax2.set_title('HERFINDAHL-HIRSCHMAN INDEX', fontsize=12, fontweight='bold')
        ax2.set_xlim(0, hhi_max + 500)
        ax2.legend(loc='lower right', fontsize=8)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        chart_path = os.path.join(output_dir, 'concentration.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate metrics chart: {e}", file=sys.stderr)
    
    # Chart 3: Brand Type Breakdown
    try:
        breakdown = analysis.get('brand_breakdown', {})
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        types = ['Major\nBrands', 'Amazon\nBrands', 'Private\nLabel', 'Emerging']
        shares = [
            breakdown.get('major_brand_share', 0),
            breakdown.get('amazon_share', 0),
            breakdown.get('private_label_share', 0),
            100 - breakdown.get('major_brand_share', 0) - breakdown.get('amazon_share', 0) - breakdown.get('private_label_share', 0)
        ]
        colors = [get_color('primary'), get_color('secondary'), get_color('muted'), get_color('good')]
        
        bars = ax.bar(types, shares, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, shares):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Market Share (%)', fontsize=11, fontweight='bold')
        ax.set_title(f'BRAND TYPE BREAKDOWN: {keyword.upper()}', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylim(0, max(shares) * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        chart_path = os.path.join(output_dir, 'brand_types.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate breakdown chart: {e}", file=sys.stderr)

    # Chart 4: SOV vs Revenue Opportunity Bubble
    try:
        top_brands = analysis.get('top_brands', [])
        brands_with_sov = [b for b in top_brands if b.get('sov_share', 0) > 0 or b.get('revenue_share', 0) > 0]
        if len(brands_with_sov) >= 2:
            fig, ax = plt.subplots(figsize=(10, 7))

            x_vals = [b.get('sov_share', 0) for b in brands_with_sov]
            y_vals = [b.get('revenue_share', b.get('share', 0)) for b in brands_with_sov]
            sizes = [max(b.get('products', 1), 1) * 40 for b in brands_with_sov]
            brand_colors = []
            for b in brands_with_sov:
                if b['type'] == 'MAJOR':
                    brand_colors.append(get_color('primary'))
                elif b['type'] == 'AMAZON':
                    brand_colors.append(get_color('secondary'))
                elif b['type'] == 'PRIVATE':
                    brand_colors.append(get_color('muted'))
                else:
                    brand_colors.append(get_color('good'))

            scatter = ax.scatter(x_vals, y_vals, s=sizes, c=brand_colors,
                                 alpha=0.75, edgecolors='white', linewidth=1.5)

            # Diagonal line: SOV == Revenue
            max_val = max(max(x_vals, default=1), max(y_vals, default=1)) * 1.1
            ax.plot([0, max_val], [0, max_val], '--', color='#BDBDBD', linewidth=1.5,
                    label='SOV = Revenue (balanced)')

            # Label each bubble
            for b, x, y in zip(brands_with_sov, x_vals, y_vals):
                ax.annotate(b['brand'][:12], (x, y),
                            textcoords='offset points', xytext=(5, 5),
                            fontsize=8, color='#333333')

            ax.set_xlabel('Share of Voice (%)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Revenue Share (%)', fontsize=11, fontweight='bold')
            ax.set_title(f'SOV vs REVENUE OPPORTUNITY: {keyword.upper()}', fontsize=14,
                         fontweight='bold', pad=15)
            ax.legend(loc='upper left', fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Annotations for quadrants
            ax.text(0.97, 0.05, 'High Revenue\nLow SOV\n(underdog)', transform=ax.transAxes,
                    fontsize=8, color=get_color('good'), ha='right', va='bottom', style='italic')
            ax.text(0.03, 0.95, 'High SOV\nLow Revenue\n(weak converter)', transform=ax.transAxes,
                    fontsize=8, color=get_color('hot'), ha='left', va='top', style='italic')

            chart_path = os.path.join(output_dir, 'opportunity.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate opportunity chart: {e}", file=sys.stderr)

    # Chart 5: Revenue by Price Tier (horizontal bar)
    try:
        insights = analysis.get('insights', {})
        price_analysis = insights.get('price_analysis', {})
        segment_shares = price_analysis.get('segment_shares', {})
        price_bands = price_analysis.get('price_bands', {})

        # Fallback: try to derive from top_brands if segment_shares missing
        if not segment_shares:
            top_brands = analysis.get('top_brands', [])
            if top_brands:
                shares_list = [b.get('share', b.get('revenue_share', 0)) for b in top_brands]
                total = sum(shares_list) or 1
                n = len(shares_list)
                segment_shares = {
                    'budget': round(sum(shares_list[:n // 3]) / total * 100, 1),
                    'mid': round(sum(shares_list[n // 3: 2 * n // 3]) / total * 100, 1),
                    'premium': round(sum(shares_list[2 * n // 3:]) / total * 100, 1),
                }

        if segment_shares:
            segments = ['Budget', 'Mid-Range', 'Premium']
            keys = ['budget', 'mid', 'premium']
            values = [segment_shares.get(k, 0) for k in keys]

            # Build labels with price band info if available
            labels = []
            for seg, key in zip(segments, keys):
                band = price_bands.get(key, '')
                labels.append(f"{seg}\n{band}" if band else seg)

            seg_colors = [get_color('good'), get_color('primary'), '#9C27B0']
            fig, ax = plt.subplots(figsize=(9, 5))

            bars = ax.barh(labels, values, color=seg_colors, edgecolor='white',
                           linewidth=2, height=0.5)

            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                        f'{val:.1f}%', va='center', ha='left', fontsize=11, fontweight='bold')

            ax.set_xlabel('Revenue Share (%)', fontsize=11, fontweight='bold')
            ax.set_title(f'REVENUE BY PRICE TIER: {keyword.upper()}', fontsize=14,
                         fontweight='bold', pad=15)
            ax.set_xlim(0, max(values) * 1.25 if values else 100)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Mark winning segment
            winning = price_analysis.get('winning_segment', '')
            key_to_idx = {'budget': 0, 'mid': 1, 'premium': 2}
            if winning in key_to_idx:
                win_idx = key_to_idx[winning]
                bars[win_idx].set_edgecolor(get_color('warning'))
                bars[win_idx].set_linewidth(3)
                ax.annotate('★ Dominant', xy=(values[win_idx], win_idx),
                            xytext=(values[win_idx] * 0.6, win_idx),
                            fontsize=9, color=get_color('warning'), fontweight='bold')

            chart_path = os.path.join(output_dir, 'price_segments.png')
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            charts.append(chart_path)
    except Exception as e:
        print(f"Warning: Could not generate price segments chart: {e}", file=sys.stderr)

    return charts

# === CLI Entry Point ===

def main():
    parser = argparse.ArgumentParser(description='Market Share Analyzer v2.1.0')
    parser.add_argument('params', nargs='?', help='JSON parameters: {"keyword": "wireless earbuds"}')
    parser.add_argument('--deep', action='store_true', help='Run deeper market analysis')
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
    
    # Validate required parameters
    keyword = params.get('keyword', '')
    if not keyword:
        print(json.dumps({'error': 'Missing required parameter: keyword'}, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Run analysis
    result = analyze_market_share(
        keyword=keyword,
        market=params.get('market', 'US'),
        limit=params.get('limit', 50),
        deep=args.deep
    )
    
    # Generate charts if requested
    if args.chart and 'error' not in result:
        charts = generate_charts(result, args.chart)
        result['charts'] = charts

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Output
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
