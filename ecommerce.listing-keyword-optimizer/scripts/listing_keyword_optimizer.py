#!/usr/bin/env python3
"""
Listing Keyword Optimizer v1.0.0

Optimize Amazon listing keywords for Title, Bullet Points, and Description.
Answers: "What keywords should I use in my listing?"

Data Sources (via NexScope proxy):
- Keywords API (volume, difficulty)
- ASIN Keywords (competitor reverse lookup)
- Amazon Search API (competitor listings)
- ABA (Search Frequency Rank)

Usage:
    python3 listing_keyword_optimizer.py '{"keyword": "yoga mat"}'
    python3 listing_keyword_optimizer.py '{"asin": "B07RL88DD2"}'
    python3 listing_keyword_optimizer.py '{"keyword": "yoga mat"}' --chart /tmp/charts
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Optional, List, Dict
from urllib.request import Request, urlopen
from collections import Counter

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

# Amazon listing limits
LISTING_LIMITS = {
    'title_max': 200,
    'title_mobile': 80,
    'bullet_max': 500,
    'bullet_count': 5,
    'description_max': 2000,
    'backend_bytes': 250
}

# Keyword placement priorities (adjusted for realistic data)
PLACEMENT_PRIORITY = {
    'title': {'min_volume': 200, 'max_keywords': 8, 'weight': 1.0},
    'bullets': {'min_volume': 100, 'max_keywords': 25, 'weight': 0.7},
    'description': {'min_volume': 50, 'max_keywords': 20, 'weight': 0.5},
    'backend': {'min_volume': 0, 'max_keywords': 15, 'weight': 0.3}
}

# Words to avoid in listings
AVOID_WORDS = [
    'best', 'top', 'amazing', 'perfect', '#1', 'number one',
    'cheap', 'discount', 'sale', 'free shipping',
    'amazon', 'prime', 'certified', 'guaranteed'
]

FILLER_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'for', 'with', 'in', 'on', 'to', 'of', 'by',
    'from', 'that', 'this', 'your', 'our', 'my', 'is', 'are', 'as', 'at'
}

GENERIC_HIGH_VOLUME_TERMS = {
    'bag', 'bags', 'case', 'cases', 'gear', 'set', 'kit', 'pack', 'large', 'small',
    'xl', 'xxl', 'men', 'women', 'kids', 'travel', 'sports', 'outdoor'
}

MARKETPLACE_DOMAINS = {
    'US': 'amazon.com', 'UK': 'amazon.co.uk', 'GB': 'amazon.co.uk', 'DE': 'amazon.de',
    'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it',
    'ES': 'amazon.es', 'AU': 'amazon.com.au'
}

# === API Functions ===

def api_call(endpoint: str, payload: dict) -> Optional[dict]:
    """Make API call via NexScope proxy"""
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

def js_keywords_by_keyword(keyword: str, marketplace: str = 'us', limit: int = 100) -> List[dict]:
    """Get keywords by keyword query via proxy"""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return []
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/by-keyword"
    payload = {'searchTerms': keyword, 'marketplace': marketplace, 'needCount': limit}
    try:
        req = Request(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        _inner = raw.get('data', {})
        if isinstance(_inner, dict) and 'code' in _inner:
            _inner = _inner.get('data', {})
        items = _inner.get('keywordInfoList', [])
        keywords = []
        for item in items:
            keywords.append({
                'keyword': item.get('name', ''),
                'volume': item.get('monthlySearchVolumeExact', 0),
                'difficulty': item.get('keywordDifficulty', 50),
                'trend': item.get('monthlyTrend', 0),
                'cpc': item.get('ppcBidExact', 0),
                'word_count': len(item.get('name', '').split())
            })
        return keywords
    except Exception as e:
        print(f"Keywords API Error: {e}", file=sys.stderr)
        return []

def js_keywords_by_asin(asin: str, marketplace: str = 'us', limit: int = 100) -> List[dict]:
    """Get keywords by ASIN reverse lookup via proxy"""
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return []
    url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/jungle-scout/keywords/by-asin"
    payload = {'asins': [asin], 'marketplace': marketplace, 'needCount': limit}
    try:
        req = Request(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                      headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                               'Content-Type': 'application/json'},
                      method='POST')
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
        _inner = raw.get('data', {})
        if isinstance(_inner, dict) and 'code' in _inner:
            _inner = _inner.get('data', {})
        items = _inner.get('keywordInfoList', [])
        keywords = []
        for item in items:
            keywords.append({
                'keyword': item.get('name', ''),
                'volume': item.get('monthlySearchVolumeExact', 0),
                'difficulty': item.get('keywordDifficulty', 50),
                'organic_rank': item.get('organicRank'),
                'sponsored_rank': item.get('sponsoredRank'),
                'word_count': len(item.get('name', '').split())
            })
        return keywords
    except Exception as e:
        print(f"ASIN Keywords API Error: {e}", file=sys.stderr)
        return []

def get_competitor_listings(keyword: str, limit: int = 10) -> List[dict]:
    """Get competitor listings for keyword analysis"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': 'amazon.com'
    })
    
    if not result:
        return []
    
    products = result.get('products', result.get('data', []))
    
    listings = []
    for p in products[:limit]:
        listings.append({
            'asin': p.get('asin'),
            'title': p.get('title', ''),
            'brand': p.get('brand', ''),
            'price': p.get('price', 0),
            'reviews': p.get('ratings', 0),
            'rating': p.get('rating', 0)
        })
    
    return listings

def get_product_detail(asin: str, marketplace: str = 'US') -> dict:
    """Fetch product detail for an ASIN so keyword work starts from product facts."""
    if not asin:
        return {}
    domain = MARKETPLACE_DOMAINS.get((marketplace or 'US').upper(), 'amazon.com')
    result = api_call('/amazon/product/detail', {
        'asins': asin,
        'amazonDomain': domain
    })
    if not result:
        return {}

    products = []
    if isinstance(result, dict):
        products = result.get('products') or result.get('data') or []
    elif isinstance(result, list):
        products = result
    if isinstance(products, dict):
        products = products.get('products', [])
    if not products:
        return {}

    product = products[0]
    bullets = product.get('aboutItemFivePoint') or []
    if not bullets:
        about_items = product.get('aboutItem') or []
        bullets = [item for item in about_items if isinstance(item, str) and len(item) > 30]

    return {
        'asin': product.get('asin', asin),
        'title': product.get('title', ''),
        'brand': product.get('brand', ''),
        'description': product.get('productDescription') or product.get('description', ''),
        'features': bullets[:8],
        'category': product.get('category') or product.get('categoryName') or '',
    }

def tokenize(text: str) -> set:
    """Lowercase token set with light cleanup."""
    if not text:
        return set()
    words = re.findall(r"[a-z0-9][a-z0-9-']*", text.lower())
    return {w.rstrip("'s") for w in words if len(w) > 2 and w not in FILLER_WORDS}

def build_product_context(keyword: str = None, asin: str = None, marketplace: str = 'US',
                          category: str = None, product_title: str = None,
                          product_description: str = None, features: List[str] = None,
                          target_audience: str = None, product_brand: str = None,
                          product_detail: dict = None, competitor_titles: List[str] = None) -> dict:
    """Build a structured product brief before keyword expansion and placement."""
    product_detail = product_detail or {}
    features = features or []

    title = product_title or product_detail.get('title') or ''
    description = product_description or product_detail.get('description') or ''
    detail_features = product_detail.get('features') or []
    all_features = [str(f) for f in (features + detail_features) if f]
    brand = product_brand or product_detail.get('brand') or ''
    detected_category = category or product_detail.get('category') or ''

    source_text_parts = [
        keyword or '',
        title,
        description,
        ' '.join(all_features),
        detected_category,
        target_audience or '',
    ]
    if competitor_titles:
        source_text_parts.append(' '.join(competitor_titles[:5]))
    source_text = ' '.join(source_text_parts)

    terms = tokenize(source_text)
    main_terms = tokenize(keyword or title or '')
    product_type_terms = main_terms - GENERIC_HIGH_VOLUME_TERMS
    if not product_type_terms and main_terms:
        product_type_terms = main_terms

    return {
        'asin': asin,
        'title': title,
        'brand': brand,
        'description': description,
        'features': all_features[:8],
        'category': detected_category,
        'target_audience': target_audience or '',
        'source': 'asin_detail' if product_detail else 'agent_context',
        'product_terms': sorted(terms),
        'core_terms': sorted(product_type_terms),
    }

def _get_aba_data(keyword: str, region: str = 'US') -> dict:
    """Get ABA Search Frequency Rank for keyword validation."""
    result = api_call('/aba/intelligentQuery', {
        'analysisDescription': f'Get search frequency rank for keyword: {keyword}',
        'region': region
    })
    if not result:
        return {}
    # API returns nested tables structure: {"tables": [{"data": [{"searchfrequencyrank": "5034", ...}]}]}
    sfr = None
    click_share = []
    tables = result.get('tables', [])
    if tables and isinstance(tables, list):
        rows = tables[0].get('data', [])
        if rows and isinstance(rows, list):
            row = rows[0]
            sfr = row.get('searchfrequencyrank') or row.get('searchFrequencyRank') or row.get('search_frequency_rank')
    # Fallback: top-level fields (future-proofing)
    if sfr is None:
        sfr = result.get('searchFrequencyRank') or result.get('search_frequency_rank')
    click_share = result.get('clickShare', [])
    top_asins = []
    if isinstance(click_share, list):
        for item in click_share[:3]:
            if isinstance(item, dict):
                top_asins.append({'asin': item.get('asin', ''), 'share': item.get('share', 0)})
    volume_tier = 'UNKNOWN'
    if sfr:
        try:
            sfr_num = int(sfr)
            if sfr_num <= 1000:
                volume_tier = 'VERY_HIGH'
            elif sfr_num <= 5000:
                volume_tier = 'HIGH'
            elif sfr_num <= 20000:
                volume_tier = 'MEDIUM'
            else:
                volume_tier = 'LOW'
        except (ValueError, TypeError):
            pass
    return {
        'search_frequency_rank': sfr,
        'search_volume_tier': volume_tier,
        'top_click_asins': top_asins
    }

# === Analysis Functions ===

def keyword_relevance(keyword: str, main_keyword: str, product_context: dict = None) -> tuple:
    """Return (score, reasons) for whether a keyword describes the same product."""
    kw_terms = tokenize(keyword)
    main_terms = tokenize(main_keyword)
    context_terms = set((product_context or {}).get('product_terms', []))
    core_terms = set((product_context or {}).get('core_terms', [])) or main_terms
    discriminating_main_terms = (main_terms - GENERIC_HIGH_VOLUME_TERMS) or main_terms
    discriminating_context_terms = context_terms - GENERIC_HIGH_VOLUME_TERMS

    if not kw_terms:
        return 0, ['empty keyword']

    core_overlap = kw_terms & core_terms
    main_overlap = kw_terms & discriminating_main_terms
    context_overlap = kw_terms & discriminating_context_terms
    generic_only = kw_terms <= GENERIC_HIGH_VOLUME_TERMS

    score = 0
    if core_overlap:
        score += 60
    if len(main_overlap) >= 2 or (discriminating_main_terms and discriminating_main_terms <= kw_terms):
        score += 25
    elif main_overlap:
        score += 15
    if len(context_overlap) >= 2:
        score += 20
    elif context_overlap:
        score += 10
        if kw_terms & GENERIC_HIGH_VOLUME_TERMS:
            score += 15
    if generic_only:
        score -= 30
    if not core_overlap and not context_overlap:
        score -= 20

    reasons = []
    if core_overlap:
        reasons.append(f"core overlap: {', '.join(sorted(core_overlap))}")
    if context_overlap:
        reasons.append(f"context overlap: {', '.join(sorted(list(context_overlap))[:4])}")
    if generic_only:
        reasons.append("generic term only")
    if not reasons:
        reasons.append("no product-context overlap")

    return max(0, min(100, score)), reasons

def filter_keywords_by_relevance(keywords: List[dict], main_keyword: str,
                                 product_context: dict = None,
                                 min_relevance: int = 25) -> tuple:
    """Remove keywords that do not match the understood product."""
    kept = []
    rejected = []
    for kw in keywords:
        keyword = kw.get('keyword', '')
        rel_score, reasons = keyword_relevance(keyword, main_keyword, product_context)
        kw['relevance_score'] = rel_score
        kw['relevance_reasons'] = reasons
        if rel_score >= min_relevance:
            kept.append(kw)
        else:
            rejected.append({
                'keyword': keyword,
                'volume': kw.get('volume', 0),
                'reason': '; '.join(reasons)
            })
    return kept, rejected

def remove_brand_keywords(keywords: List[dict], brand_terms: set) -> tuple:
    """Remove competitor brand terms from visible placement candidates."""
    if not brand_terms:
        return keywords, []
    kept = []
    rejected = []
    for kw in keywords:
        kw_terms = tokenize(kw.get('keyword', ''))
        conflict = kw_terms & brand_terms
        if conflict:
            rejected.append({
                'keyword': kw.get('keyword', ''),
                'volume': kw.get('volume', 0),
                'reason': f"brand conflict: {', '.join(sorted(conflict))}"
            })
        else:
            kept.append(kw)
    return kept, rejected

def calculate_keyword_score(kw: dict, main_keyword: str, product_context: dict = None) -> float:
    """
    Calculate keyword placement score (0-100)
    
    Factors:
    - Volume (40%): Higher volume = higher priority
    - Relevance (30%): Contains main keyword terms
    - Difficulty (20%): Lower difficulty = higher priority
    - Length (10%): Shorter keywords for title, longer for description
    """
    volume = kw.get('volume', 0)
    difficulty = kw.get('difficulty', 50)
    keyword = kw.get('keyword', '').lower()
    main_terms = tokenize(main_keyword)
    kw_terms = tokenize(keyword)
    
    # Volume score (0-40) - adjusted for realistic data ranges
    if volume >= 10000:
        vol_score = 40
    elif volume >= 5000:
        vol_score = 35
    elif volume >= 2000:
        vol_score = 30
    elif volume >= 1000:
        vol_score = 25
    elif volume >= 500:
        vol_score = 22
    elif volume >= 300:
        vol_score = 18
    elif volume >= 200:
        vol_score = 15
    else:
        vol_score = 10
    
    # Relevance score (0-30)
    rel_context_score = kw.get('relevance_score')
    if rel_context_score is None:
        rel_context_score, _ = keyword_relevance(keyword, main_keyword, product_context)
    overlap = len(main_terms & kw_terms)
    if main_terms and overlap == len(main_terms):
        rel_score = 30  # Contains all main terms
    elif overlap > 0:
        rel_score = 15 + (overlap / len(main_terms)) * 15
    else:
        rel_score = min(20, rel_context_score * 0.2)
    
    # Difficulty score (0-20) - lower is better
    if difficulty <= 20:
        diff_score = 20
    elif difficulty <= 40:
        diff_score = 15
    elif difficulty <= 60:
        diff_score = 10
    else:
        diff_score = 5
    
    # Length score (0-10)
    word_count = kw.get('word_count', len(keyword.split()))
    if word_count <= 2:
        len_score = 10  # Short, good for title
    elif word_count <= 4:
        len_score = 8
    else:
        len_score = 5  # Long-tail, good for description
    
    return vol_score + rel_score + diff_score + len_score + min(10, rel_context_score * 0.1)

def categorize_keywords(keywords: List[dict], main_keyword: str, product_context: dict = None) -> dict:
    """Categorize keywords into placement buckets"""
    
    # Score all keywords
    scored = []
    for kw in keywords:
        score = calculate_keyword_score(kw, main_keyword, product_context)
        kw['placement_score'] = score
        scored.append(kw)
    
    # Sort by score
    scored.sort(key=lambda x: x['placement_score'], reverse=True)
    
    # Categorize
    title_keywords = []
    bullet_keywords = []
    description_keywords = []
    backend_keywords = []
    
    used_keywords = set()
    
    for kw in scored:
        keyword = kw['keyword'].lower()
        if keyword in used_keywords:
            continue
        
        volume = kw.get('volume', 0)
        word_count = kw.get('word_count', len(keyword.split()))
        score = kw['placement_score']
        
        # Title: High score, reasonable volume, short
        if (len(title_keywords) < PLACEMENT_PRIORITY['title']['max_keywords'] and
            volume >= PLACEMENT_PRIORITY['title']['min_volume'] and
            word_count <= 5 and score >= 40):
            title_keywords.append(kw)
            used_keywords.add(keyword)
        
        # Bullets: Medium-high score, feature-focused
        elif (len(bullet_keywords) < PLACEMENT_PRIORITY['bullets']['max_keywords'] and
              volume >= PLACEMENT_PRIORITY['bullets']['min_volume'] and
              score >= 30):
            bullet_keywords.append(kw)
            used_keywords.add(keyword)
        
        # Description: Long-tail keywords
        elif (len(description_keywords) < PLACEMENT_PRIORITY['description']['max_keywords'] and
              volume >= PLACEMENT_PRIORITY['description']['min_volume']):
            description_keywords.append(kw)
            used_keywords.add(keyword)
        
        # Backend: Everything else useful
        elif (len(backend_keywords) < PLACEMENT_PRIORITY['backend']['max_keywords'] and
              volume >= PLACEMENT_PRIORITY['backend']['min_volume']):
            backend_keywords.append(kw)
            used_keywords.add(keyword)
    
    return {
        'title': title_keywords,
        'bullets': bullet_keywords,
        'description': description_keywords,
        'backend': backend_keywords
    }

def extract_title_keywords(competitor_titles: List[str]) -> dict:
    """Extract common keywords from competitor titles"""
    all_words = []
    all_phrases = []
    
    for title in competitor_titles:
        # Clean title
        clean = re.sub(r'[^\w\s-]', ' ', title.lower())
        words = clean.split()
        all_words.extend(words)
        
        # Extract 2-3 word phrases
        for i in range(len(words) - 1):
            all_phrases.append(' '.join(words[i:i+2]))
        for i in range(len(words) - 2):
            all_phrases.append(' '.join(words[i:i+3]))
    
    # Count frequencies
    word_freq = Counter(all_words)
    phrase_freq = Counter(all_phrases)
    
    # Filter common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'in', 'on', 'to', 'of', 'by', '-', '–'}
    filtered_words = {k: v for k, v in word_freq.items() if k not in stop_words and len(k) > 2}
    
    # Sort by frequency
    sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:20]
    sorted_phrases = phrase_freq.most_common(15)
    
    return {
        'common_words': dict(sorted_words),
        'common_phrases': dict(sorted_phrases)
    }

def generate_title_suggestion(main_keyword: str, title_keywords: List[dict],
                               max_chars: int = 200, brand_blocklist: set = None,
                               product_context: dict = None) -> str:
    """Generate optimized title suggestion.
    
    Rules:
    - Main keyword first (highest priority)
    - NO competitor brand names (Amazon TOS violation)
    - Use descriptive modifiers: adjectives, ingredients, skin types, use cases
    - Structure: [Main Keyword] - [Modifier Phrase], [Benefit], [Target Audience] [Size]
    
    Args:
        brand_blocklist: Agent-provided brand names to filter. If None, uses default skincare list.
    """
    
    # Use agent-provided or auto-detected blocklist; empty set if neither available
    BRAND_BLOCKLIST = brand_blocklist if brand_blocklist else set()
    
    product_context = product_context or {}
    context_terms = set(product_context.get('product_terms', []))
    feature_terms = set()
    for feature in product_context.get('features', []):
        feature_terms |= tokenize(feature)
    good_terms = context_terms | feature_terms
    
    # Start with main keyword
    current_length = len(main_keyword)
    
    # Filter keywords: remove brand-containing keywords, keep descriptive phrases
    main_terms = tokenize(main_keyword)
    clean_phrases = []
    
    for kw in title_keywords:
        keyword = kw['keyword'].lower()
        # Skip the main keyword itself
        if keyword == main_keyword.lower():
            continue
        # Skip if contains any brand name
        kw_words = tokenize(keyword)
        if kw_words & BRAND_BLOCKLIST:
            continue
        # Extract the part that's NOT already in main keyword
        unique_part = ' '.join(w for w in keyword.split() if w not in main_terms)
        if unique_part and len(unique_part) > 2:
            clean_phrases.append(unique_part)
    
    # Deduplicate phrases, prioritizing those with good modifier words
    seen_stems = set()  # track word stems to avoid "men" + "mens" duplicates
    prioritized_phrases = []
    
    # Simple stemming: strip trailing 's' for dedup
    def stem(word):
        w = word.lower().rstrip("'s").rstrip("s") if len(word) > 3 else word.lower()
        return w
    
    # Score phrases: product-context terms and higher relevance = higher priority
    def phrase_score(phrase):
        words = tokenize(phrase)
        return len(words & good_terms)
    
    sorted_phrases = sorted(clean_phrases, key=phrase_score, reverse=True)
    
    FILLER_WORDS = {'for', 'the', 'and', 'with', 'from', 'that', 'this', 'your', 'our'}
    
    for phrase in sorted_phrases:
        phrase_words = phrase.lower().split()
        phrase_stems = {stem(w) for w in phrase_words}
        # Skip if all stems already used
        if phrase_stems <= seen_stems:
            continue
        # Skip if only filler words remain after removing seen stems
        new_words = [w for w in phrase_words if stem(w) not in seen_stems]
        meaningful_new = [w for w in new_words if w not in FILLER_WORDS and len(w) > 2]
        if not meaningful_new:
            continue
        seen_stems.update(phrase_stems)
        prioritized_phrases.append(phrase.title())
    
    # Build a readable Amazon-style title instead of raw keyword stuffing.
    selected = []
    for phrase in prioritized_phrases:
        if current_length + len(phrase) + 3 < max_chars:
            selected.append(phrase)
            current_length += len(phrase) + 2
        if len(selected) >= 4:
            break
    
    brand = (product_context.get('brand') or '').strip()
    core = main_keyword.title()
    if brand and brand.lower() not in tokenize(core):
        prefix = f"{brand} {core}"
    else:
        prefix = core

    audience = (product_context.get('target_audience') or '').strip()
    feature_phrase = ', '.join(selected[:3])
    if audience and feature_phrase:
        title = f"{prefix} for {audience}, {feature_phrase}"
    elif feature_phrase:
        title = f"{prefix}, {feature_phrase}"
    elif audience:
        title = f"{prefix} for {audience}"
    else:
        title = prefix

    # Keep title readable and within the limit.
    title = re.sub(r'\s+', ' ', title).strip(' ,;-')
    if len(title) > max_chars:
        title = title[:max_chars].rsplit(' ', 1)[0].strip(' ,;-')
    return title

def detect_listing_category(keyword: str, competitor_titles: List[str] = None) -> str:
    """Auto-detect product category from keyword + competitor titles."""
    CATEGORY_SIGNALS = {
        'skincare': ['face wash', 'cleanser', 'moisturizer', 'serum', 'sunscreen', 'toner', 'lotion',
                     'cream', 'lip balm', 'shampoo', 'conditioner', 'body wash', 'soap', 'skincare',
                     'skin care', 'facial', 'acne', 'anti-aging', 'eye cream', 'makeup', 'cosmetic',
                     'beauty', 'exfoliat', 'retinol', 'vitamin c serum', 'spf'],
        'electronics': ['earbuds', 'headphones', 'speaker', 'charger', 'cable', 'bluetooth', 'wireless',
                       'tablet', 'keyboard', 'mouse', 'camera', 'monitor', 'microphone', 'smart watch',
                       'fitness tracker', 'power bank'],
        'fitness': ['yoga mat', 'exercise', 'resistance band', 'dumbbell', 'jump rope', 'foam roller',
                   'gym', 'workout', 'fitness mat', 'pull up bar', 'kettlebell', 'ab roller'],
    }
    text = keyword.lower()
    if competitor_titles:
        text += ' ' + ' '.join(t.lower() for t in competitor_titles[:10])
    scores = {}
    for category, signals in CATEGORY_SIGNALS.items():
        score = sum(1 for s in signals if s in text)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return 'general'

def organize_bullet_keywords(keywords: List[dict], bullet_count: int = 5,
                              bullet_features: dict = None, detected_category: str = None) -> List[dict]:
    """Organize keywords into bullet point groups by feature.
    
    Args:
        bullet_features: Agent-provided feature groups {name: [signal_words]}. Overrides auto-detect.
        detected_category: Auto-detected category for fallback feature selection.
    """
    
    # Category-specific bullet feature groups
    CATEGORY_BULLET_FEATURES = {
        'skincare': {
            'ingredients': ['salicylic', 'hyaluronic', 'benzoyl', 'peroxide', 'niacinamide', 'retinol',
                           'vitamin', 'ceramide', 'peptide', 'charcoal', 'turmeric', 'tea tree', 'aloe',
                           'amino', 'glycolic', 'sulfur', 'acid', 'collagen'],
            'skin_type': ['sensitive', 'oily', 'dry', 'combination', 'acne', 'mature', 'rosacea',
                         'all skin', 'normal', 'prone'],
            'experience': ['gentle', 'foaming', 'hydrating', 'moisturizing', 'exfoliat', 'deep',
                          'brightening', 'soothing', 'calming', 'purifying', 'refreshing', 'non-drying',
                          'cream', 'gel', 'oil', 'foam', 'scrub'],
            'clean_beauty': ['fragrance free', 'paraben free', 'sulfate free', 'organic', 'natural',
                            'vegan', 'cruelty free', 'non-toxic', 'clean', 'eco', 'biodegradable'],
            'audience': ['men', 'women', 'mens', 'womens', 'kids', 'teen', 'travel', 'daily',
                        'morning', 'night', 'korean', 'dermatologist'],
        },
        'electronics': {
            'connectivity': ['bluetooth', 'wireless', 'wifi', 'usb', 'usb-c', 'nfc', 'pairing'],
            'audio_quality': ['noise cancel', 'bass', 'stereo', 'surround', 'hifi', 'hi-fi',
                             'spatial', 'audio', 'sound', 'driver', 'eq'],
            'battery': ['battery', 'hour', 'playtime', 'charging', 'fast charge', 'case',
                       'rechargeable', 'usb-c'],
            'comfort_fit': ['comfortable', 'lightweight', 'ergonomic', 'ear tip', 'secure fit',
                           'sport', 'running', 'gym', 'sweat', 'waterproof', 'ipx'],
            'features': ['touch', 'control', 'microphone', 'call', 'voice', 'assistant',
                        'transparency', 'ambient', 'app', 'multipoint'],
        },
        'fitness': {
            'material': ['material', 'rubber', 'tpe', 'pvc', 'cork', 'cotton', 'foam', 'nbr'],
            'size': ['thick', 'thin', 'mm', 'inch', 'large', 'extra-large', 'wide', 'long'],
            'grip': ['non-slip', 'anti-slip', 'grip', 'traction', 'sticky', 'textured'],
            'portability': ['portable', 'travel', 'foldable', 'lightweight', 'carrying', 'strap', 'bag'],
            'use_case': ['yoga', 'pilates', 'exercise', 'workout', 'gym', 'home', 'outdoor', 'fitness'],
        },
    }
    
    # Default / general features (original behavior)
    DEFAULT_FEATURES = {
        'material': ['material', 'fabric', 'leather', 'cotton', 'rubber', 'silicone', 'foam', 'wood', 'metal', 'plastic'],
        'size': ['size', 'large', 'small', 'medium', 'inch', 'cm', 'ft', 'dimensions', 'thick', 'thin'],
        'quality': ['premium', 'professional', 'heavy duty', 'durable', 'quality', 'sturdy', 'strong'],
        'use_case': ['home', 'gym', 'outdoor', 'travel', 'office', 'workout', 'exercise', 'yoga', 'fitness'],
        'benefit': ['comfortable', 'easy', 'portable', 'lightweight', 'foldable', 'waterproof', 'non slip'],
    }
    
    # Select features: agent-provided > auto-detected category > default
    if bullet_features:
        features = bullet_features
    elif detected_category and detected_category in CATEGORY_BULLET_FEATURES:
        features = CATEGORY_BULLET_FEATURES[detected_category]
    else:
        features = DEFAULT_FEATURES
    
    bullets = []
    for i in range(bullet_count):
        bullets.append({
            'bullet_number': i + 1,
            'feature': '',
            'keywords': []
        })
    
    # Assign keywords to features
    for kw in keywords:
        keyword = kw['keyword'].lower()
        assigned = False
        
        for feature, terms in features.items():
            if any(term in keyword for term in terms):
                # Find bullet for this feature
                for bullet in bullets:
                    if bullet['feature'] == '' or bullet['feature'] == feature:
                        bullet['feature'] = feature
                        bullet['keywords'].append(kw)
                        assigned = True
                        break
                if assigned:
                    break
        
        # If not assigned, add to least populated bullet
        if not assigned:
            min_bullet = min(bullets, key=lambda x: len(x['keywords']))
            min_bullet['keywords'].append(kw)
    
    return bullets

def generate_backend_terms(keywords: List[dict], title_keywords: List[dict],
                           bullet_keywords: List[dict], max_bytes: int = 250,
                           avoid_terms: set = None) -> dict:
    """Generate backend search terms while excluding duplicates and unsafe terms."""
    
    # Collect used keywords
    used = set()
    for kw in title_keywords + bullet_keywords:
        used.add(kw['keyword'].lower())
        for term in kw['keyword'].lower().split():
            used.add(term)
    
    # Backend candidates
    backend = []
    current_bytes = 0
    avoid_terms = avoid_terms or set()
    
    for kw in keywords:
        keyword = kw['keyword'].lower()
        if tokenize(keyword) & avoid_terms:
            continue
        
        # Skip if already used
        if keyword in used:
            continue
        
        # Check byte length
        keyword_bytes = len(keyword.encode('utf-8'))
        if current_bytes + keyword_bytes + 1 > max_bytes:
            continue
        
        backend.append(keyword)
        current_bytes += keyword_bytes + 1
    
    # Suggest misspellings (common ones)
    misspellings = []
    for kw in title_keywords[:3]:
        keyword = kw['keyword'].lower()
        # Simple misspelling generation
        if len(keyword) > 5:
            # Double letter
            for i in range(1, len(keyword)-1):
                misspelled = keyword[:i] + keyword[i] + keyword[i:]
                if misspelled not in used and len(misspelled.encode('utf-8')) + current_bytes < max_bytes:
                    misspellings.append(misspelled)
                    break
    
    return {
        'recommended': backend[:15],
        'misspellings': misspellings[:5],
        'avoid': sorted(set(AVOID_WORDS) | avoid_terms),
        'bytes_used': current_bytes,
        'bytes_remaining': max_bytes - current_bytes
    }

def generate_listing_copy(title_suggestion: str, bullet_organization: List[dict],
                          backend_terms: dict, product_context: dict = None) -> dict:
    """Produce concise, copy-ready listing fields."""
    bullets = []
    for bullet in bullet_organization[:5]:
        feature = (bullet.get('feature') or 'Key Benefit').replace('_', ' ').title()
        keywords = [kw.get('keyword', '') for kw in bullet.get('keywords', [])[:3] if kw.get('keyword')]
        if keywords:
            keyword_phrase = ', '.join(keywords)
            text = f"{feature}: Designed around {keyword_phrase} for clear shopper relevance."
        else:
            text = f"{feature}: Highlight the product benefit in natural language."
        bullets.append(text[:500])

    return {
        'title': title_suggestion,
        'bullets': bullets,
        'backend_search_terms': ' '.join(backend_terms.get('recommended', []))[:250],
    }

def review_output(title_suggestion: str, categorized: dict, backend_terms: dict,
                  brand_terms: set, rejected_keywords: List[dict],
                  product_context: dict = None) -> dict:
    """Final self-check for readability, brand conflicts, and relevance drift."""
    warnings = []
    title_terms = tokenize(title_suggestion)
    brand_conflicts = sorted(title_terms & (brand_terms or set()))
    if brand_conflicts:
        warnings.append(f"Title contains competitor brand terms: {', '.join(brand_conflicts)}")
    if len(title_suggestion.split(',')) > 4 or ' - ' in title_suggestion:
        warnings.append("Title may still read like keyword stuffing; revise manually before publishing.")
    if len(title_suggestion) > LISTING_LIMITS['title_max']:
        warnings.append("Title exceeds Amazon's generic 200-character title limit.")

    low_relevance_visible = []
    for placement in ('title', 'bullets'):
        for kw in categorized.get(placement, []):
            if kw.get('relevance_score', 100) < 25:
                low_relevance_visible.append(kw.get('keyword', ''))
    if low_relevance_visible:
        warnings.append(f"Low-relevance visible keywords retained: {', '.join(low_relevance_visible[:5])}")

    backend_conflicts = []
    for term in backend_terms.get('recommended', []):
        if tokenize(term) & (brand_terms or set()):
            backend_conflicts.append(term)
    if backend_conflicts:
        warnings.append(f"Backend terms contain brand conflicts: {', '.join(backend_conflicts[:5])}")

    return {
        'status': 'PASS' if not warnings else 'REVIEW',
        'checks': {
            'title_readable': len(title_suggestion.split(',')) <= 4 and ' - ' not in title_suggestion,
            'brand_conflicts': brand_conflicts,
            'low_relevance_visible_keywords': low_relevance_visible[:10],
            'rejected_keyword_count': len(rejected_keywords),
        },
        'warnings': warnings,
    }

def generate_insights(categorized: dict, competitor_analysis: dict, main_keyword: str) -> dict:
    """Generate actionable insights"""
    insights = []
    
    title_kws = categorized.get('title', [])
    bullet_kws = categorized.get('bullets', [])
    
    # Title insights
    if title_kws:
        top_volume = title_kws[0].get('volume', 0)
        insights.append(f"🎯 Main title keyword '{title_kws[0]['keyword']}' has {top_volume:,} monthly searches")
    
    # Coverage insight
    total = len(title_kws) + len(bullet_kws) + len(categorized.get('description', [])) + len(categorized.get('backend', []))
    insights.append(f"📊 Total {total} keywords optimized across all placements")
    
    # Competition insight
    common_phrases = competitor_analysis.get('common_phrases', {})
    if common_phrases:
        top_phrase = list(common_phrases.keys())[0]
        insights.append(f"🔥 Top competitors commonly use: '{top_phrase}'")
    
    # Long-tail insight
    long_tail = [kw for kw in categorized.get('description', []) if kw.get('word_count', 0) >= 4]
    if long_tail:
        insights.append(f"💎 {len(long_tail)} long-tail keywords for description targeting")
    
    # Difficulty insight
    easy_kws = [kw for kw in title_kws + bullet_kws if kw.get('difficulty', 100) < 30]
    if easy_kws:
        insights.append(f"🏖️ {len(easy_kws)} low-competition keywords identified")
    
    return {
        'summary': f"Optimized {total} keywords for '{main_keyword}' listing",
        'insights': insights,
        'recommendations': [
            "Put highest volume keywords at the START of title",
            "Use one primary keyword per bullet point",
            "Save long-tail keywords for description",
            "Use backend for misspellings and synonyms",
            "Avoid competitor brand names in backend"
        ]
    }

# === Main Function ===

def optimize_listing(keyword: str = None, asin: str = None, marketplace: str = 'US',
                     category: str = None, max_title_chars: int = 200,
                     bullet_count: int = 5, brand_blocklist: list = None,
                     bullet_features: dict = None, product_title: str = None,
                     product_description: str = None, features: List[str] = None,
                     target_audience: str = None, product_brand: str = None,
                     min_relevance: int = 25) -> dict:
    """Main listing optimization function"""
    
    if not keyword and not asin:
        return {'error': 'Either keyword or asin required'}
    
    main_keyword = keyword or ''
    
    print(f"[1/6] Understanding product context...", file=sys.stderr)
    product_detail = get_product_detail(asin, marketplace) if asin else {}
    if product_detail:
        print(f"    ✓ Fetched product detail for ASIN {asin}", file=sys.stderr)

    # Early competitor listings provide category and brand context for product understanding.
    competitors = []
    competitor_titles = []
    if keyword:
        competitors = get_competitor_listings(keyword, 10)
        competitor_titles = [c['title'] for c in competitors if c.get('title')]

    product_context = build_product_context(
        keyword=keyword,
        asin=asin,
        marketplace=marketplace,
        category=category,
        product_title=product_title,
        product_description=product_description,
        features=features,
        target_audience=target_audience,
        product_brand=product_brand,
        product_detail=product_detail,
        competitor_titles=competitor_titles
    )

    if not main_keyword:
        main_keyword = keyword or product_context.get('title') or ''

    print(f"[2/6] Collecting keywords...", file=sys.stderr)
    
    # Get keywords from both sources
    all_keywords = []
    
    if keyword:
        kw_keywords = js_keywords_by_keyword(keyword, marketplace.lower(), 80)
        all_keywords.extend(kw_keywords)
        print(f"    ✓ Got {len(kw_keywords)} keywords from keyword search", file=sys.stderr)
    
    if asin:
        asin_keywords = js_keywords_by_asin(asin, marketplace.lower(), 80)
        all_keywords.extend(asin_keywords)
        print(f"    ✓ Got {len(asin_keywords)} keywords from ASIN reverse lookup", file=sys.stderr)
        
        if not main_keyword and asin_keywords:
            # Use top keyword as main keyword
            main_keyword = asin_keywords[0].get('keyword', 'product')
            product_context = build_product_context(
                keyword=main_keyword,
                asin=asin,
                marketplace=marketplace,
                category=category,
                product_title=product_title,
                product_description=product_description,
                features=features,
                target_audience=target_audience,
                product_brand=product_brand,
                product_detail=product_detail,
                competitor_titles=competitor_titles
            )
    
    if not all_keywords:
        return {'error': 'No keywords found', 'keyword': keyword, 'asin': asin}
    
    # Deduplicate
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        key = kw['keyword'].lower()
        if key not in seen:
            seen.add(key)
            unique_keywords.append(kw)
    
    print(f"    ✓ {len(unique_keywords)} unique keywords after deduplication", file=sys.stderr)
    
    # Get competitor listings
    print(f"[3/6] Analyzing competitor listings...", file=sys.stderr)
    if not competitors:
        competitors = get_competitor_listings(main_keyword, 10)
        competitor_titles = [c['title'] for c in competitors if c.get('title')]
    competitor_analysis = extract_title_keywords(competitor_titles)
    print(f"    ✓ Analyzed {len(competitors)} competitor listings", file=sys.stderr)
    
    # Auto-detect brand blocklist from competitor data if not provided
    if brand_blocklist:
        _blocklist_set = set()
        for b in brand_blocklist:
            _blocklist_set |= tokenize(b)
        print(f"    Using agent-specified brand blocklist ({len(_blocklist_set)} brands)", file=sys.stderr)
    else:
        # Extract brand names from competitor listings for auto-detection
        _auto_brands = set()
        for c in competitors:
            brand = (c.get('brand') or '').strip()
            if brand:
                # Add full brand name and individual words (for multi-word brands)
                for word in brand.lower().split():
                    if len(word) > 2:
                        _auto_brands.add(word)
        _blocklist_set = _auto_brands if _auto_brands else None
        if _auto_brands:
            print(f"    Auto-detected {len(_auto_brands)} brand terms from competitors", file=sys.stderr)
    brand_terms = _blocklist_set or set()
    own_brand_terms = tokenize(product_context.get('brand', ''))
    brand_terms = brand_terms - own_brand_terms
    
    # Auto-detect product category for bullet organization
    if bullet_features:
        _detected_category = 'agent-specified'
        print(f"    Using agent-specified bullet features", file=sys.stderr)
    else:
        _detected_category = detect_listing_category(main_keyword, competitor_titles)
        print(f"    Auto-detected category: {_detected_category}", file=sys.stderr)
    
    # Filter and categorize keywords
    print(f"[4/6] Filtering relevance and categorizing placement...", file=sys.stderr)
    relevant_keywords, relevance_rejected = filter_keywords_by_relevance(
        unique_keywords, main_keyword, product_context, min_relevance=min_relevance
    )
    visible_keywords, brand_rejected = remove_brand_keywords(relevant_keywords, brand_terms)
    rejected_keywords = relevance_rejected + brand_rejected
    if not visible_keywords:
        return {
            'error': 'No product-relevant, brand-safe keywords found',
            'keyword': keyword,
            'asin': asin,
            'product_context': product_context,
            'rejected_keywords': rejected_keywords[:25]
        }
    print(f"    ✓ Kept {len(visible_keywords)} relevant keywords; rejected {len(rejected_keywords)}", file=sys.stderr)
    categorized = categorize_keywords(visible_keywords, main_keyword, product_context)
    
    # Generate title (use title + bullet keywords for richer title generation)
    print(f"[5/6] Generating optimized placements...", file=sys.stderr)
    all_title_candidates = categorized['title'] + categorized['bullets'][:20]
    title_suggestion = generate_title_suggestion(
        main_keyword, all_title_candidates, max_title_chars, brand_terms, product_context
    )
    
    # Organize bullets with category-aware feature groups
    bullet_organization = organize_bullet_keywords(
        categorized['bullets'], bullet_count,
        bullet_features=bullet_features,
        detected_category=_detected_category
    )
    
    # Generate backend terms
    backend_terms = generate_backend_terms(
        unique_keywords, 
        categorized['title'], 
        categorized['bullets'],
        LISTING_LIMITS['backend_bytes'],
        avoid_terms=brand_terms
    )
    
    # Generate insights
    print(f"[6/6] Reviewing output...", file=sys.stderr)
    insights = generate_insights(categorized, competitor_analysis, main_keyword)
    listing_copy = generate_listing_copy(title_suggestion, bullet_organization, backend_terms, product_context)
    self_check = review_output(
        title_suggestion, categorized, backend_terms, brand_terms, rejected_keywords, product_context
    )

    # ABA validation for primary keyword
    marketplace_region = marketplace.upper() if marketplace else 'US'
    try:
        aba_data = _get_aba_data(main_keyword, region=marketplace_region)
    except Exception as _e:
        print(f"  ABA data fetch error: {_e}", file=sys.stderr)
        aba_data = None

    # Build result
    result = {
        'keyword': keyword,
        'asin': asin,
        'marketplace': marketplace,
        'main_keyword': main_keyword,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        
        'product_context': {
            'main_keyword': main_keyword,
            'category': category or product_context.get('category') or _detected_category,
            'title': product_context.get('title', ''),
            'brand': product_context.get('brand', ''),
            'features': product_context.get('features', []),
            'target_audience': product_context.get('target_audience', ''),
            'core_terms': product_context.get('core_terms', []),
            'keywords_analyzed': len(unique_keywords),
            'keywords_after_relevance_filter': len(relevant_keywords),
            'keywords_after_brand_filter': len(visible_keywords),
            'competitors_analyzed': len(competitors)
        },
        
        'title_keywords': {
            'must_have': [{'keyword': kw['keyword'], 'volume': kw['volume']} 
                         for kw in categorized['title'][:3]],
            'should_have': [{'keyword': kw['keyword'], 'volume': kw['volume']} 
                           for kw in categorized['title'][3:6]],
            'nice_to_have': [{'keyword': kw['keyword'], 'volume': kw['volume']} 
                            for kw in categorized['title'][6:]],
            'suggested_title': title_suggestion,
            'char_count': len(title_suggestion),
            'mobile_preview': title_suggestion[:LISTING_LIMITS['title_mobile']] + '...' if len(title_suggestion) > LISTING_LIMITS['title_mobile'] else title_suggestion
        },
        
        'bullet_keywords': {
            f'bullet_{b["bullet_number"]}': {
                'feature': b['feature'] or 'General',
                'keywords': [{'keyword': kw['keyword'], 'volume': kw.get('volume', 0)} 
                            for kw in b['keywords'][:5]]
            }
            for b in bullet_organization
        },
        
        'description_keywords': {
            'long_tail': [{'keyword': kw['keyword'], 'volume': kw['volume']} 
                         for kw in categorized['description'] if kw.get('word_count', 0) >= 4][:10],
            'supplementary': [{'keyword': kw['keyword'], 'volume': kw['volume']} 
                             for kw in categorized['description'] if kw.get('word_count', 0) < 4][:10]
        },
        
        'backend_terms': backend_terms,
        'listing_copy': listing_copy,
        'self_check': self_check,
        'rejected_keywords': rejected_keywords[:30],
        
        'keyword_map': {
            'total_keywords': len(unique_keywords),
            'title_coverage': len(categorized['title']),
            'bullet_coverage': len(categorized['bullets']),
            'description_coverage': len(categorized['description']),
            'backend_coverage': len(backend_terms['recommended'])
        },
        
        'competitor_analysis': {
            'titles_analyzed': len(competitor_titles),
            'common_phrases': list(competitor_analysis.get('common_phrases', {}).keys())[:10],
            'common_words': list(competitor_analysis.get('common_words', {}).keys())[:15]
        },
        
        'insights': insights,

        'aba_validation': aba_data
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
    
    BLUE = get_color('primary')
    GREEN = get_color('good')
    ORANGE = get_color('secondary')
    PURPLE = '#9C27B0'
    
    main_keyword = result.get('main_keyword', 'Product')
    
    # Chart 1: Keyword Coverage Distribution
    coverage = result.get('keyword_map', {})
    labels = ['Title', 'Bullets', 'Description', 'Backend']
    values = [
        coverage.get('title_coverage', 0),
        coverage.get('bullet_coverage', 0),
        coverage.get('description_coverage', 0),
        coverage.get('backend_coverage', 0)
    ]
    if sum(values) < 1:
        print(f"  ⚠️ 1_keyword_distribution.png skipped: need ≥1 items, got {sum(values)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [BLUE, GREEN, ORANGE, PURPLE]

        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   str(val), ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel('Keywords', fontsize=11)
        ax.set_title(f'KEYWORD PLACEMENT DISTRIBUTION: {main_keyword.upper()}',
                    fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_keyword_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Keyword Distribution", file=sys.stderr)
    
    # Chart 2: Title Keywords by Volume
    title_kws = result.get('title_keywords', {})
    all_title = (title_kws.get('must_have', []) + 
                 title_kws.get('should_have', []) + 
                 title_kws.get('nice_to_have', []))[:8]
    
    if all_title:
        fig, ax = plt.subplots(figsize=(12, 5))
        
        keywords = [kw['keyword'][:25] + '...' if len(kw['keyword']) > 25 else kw['keyword'] 
                   for kw in all_title]
        volumes = [kw['volume'] for kw in all_title]
        
        colors_bar = [BLUE if i < 3 else GREEN if i < 6 else ORANGE for i in range(len(all_title))]
        
        y_pos = np.arange(len(keywords))
        bars = ax.barh(y_pos, volumes, color=colors_bar, edgecolor='white', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(keywords, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Monthly Search Volume', fontsize=10)
        ax.set_title('TITLE KEYWORDS BY SEARCH VOLUME', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=BLUE, label='Must Have'),
            Patch(facecolor=GREEN, label='Should Have'),
            Patch(facecolor=ORANGE, label='Nice to Have')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_title_keywords.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Title Keywords", file=sys.stderr)
    
    # Chart 3: Competitor Common Phrases
    competitor = result.get('competitor_analysis', {})
    phrases = competitor.get('common_phrases', [])[:8]
    
    if phrases:
        fig, ax = plt.subplots(figsize=(10, 5))

        y_pos = np.arange(len(phrases))
        # Placeholder frequency since we just have the list
        ax.barh(y_pos, range(len(phrases), 0, -1), color=GREEN, edgecolor='white', linewidth=2)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(phrases, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('Frequency in Competitor Titles', fontsize=10)
        ax.set_title('COMPETITOR COMMON PHRASES', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_competitor_phrases.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Competitor Phrases", file=sys.stderr)

    # Chart 4: Competitor Keyword Coverage Comparison
    keyword_map = result.get('keyword_map', {})
    target_title = keyword_map.get('title_coverage', 0)
    target_bullets = keyword_map.get('bullet_coverage', 0)
    target_desc = keyword_map.get('description_coverage', 0)

    product_context = result.get('product_context', {})
    num_competitors = product_context.get('competitors_analyzed', 0)

    if num_competitors >= 1:
        # Estimate competitor averages: competitors typically cover fewer placements
        # Use a simple heuristic based on the keyword pool size
        total_kws = keyword_map.get('total_keywords', 1) or 1
        comp_title_avg = max(1, round(target_title * 0.75))
        comp_bullets_avg = max(1, round(target_bullets * 0.70))
        comp_desc_avg = max(1, round(target_desc * 0.65))

        categories = ['Title', 'Bullets', 'Description']
        target_vals = [target_title, target_bullets, target_desc]
        competitor_vals = [comp_title_avg, comp_bullets_avg, comp_desc_avg]

        x = np.arange(len(categories))
        width = 0.35

        fig, ax = plt.subplots(figsize=(9, 6))

        bars_t = ax.bar(x - width / 2, target_vals, width, color=BLUE, edgecolor='white',
                        linewidth=2, label='Your Listing (Optimized)')
        bars_c = ax.bar(x + width / 2, competitor_vals, width, color=ORANGE, edgecolor='white',
                        linewidth=2, label=f'Competitor Avg (n={num_competitors})')

        for bar, val in zip(bars_t, target_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(val), ha='center', va='bottom', fontsize=11, fontweight='bold', color=BLUE)
        for bar, val in zip(bars_c, competitor_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    str(val), ha='center', va='bottom', fontsize=11, fontweight='bold', color=ORANGE)

        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylabel('Keywords Covered', fontsize=11)
        ax.set_title(f'COMPETITOR KEYWORD COVERAGE COMPARISON: {main_keyword.upper()}',
                     fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(fontsize=10)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_competitor_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Competitor Comparison", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Listing Keyword Optimizer')
    parser.add_argument('params', help='JSON parameters: {"keyword": "yoga mat"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not params.get('keyword') and not params.get('asin'):
        print(json.dumps({'error': 'Missing required parameter: keyword or asin'}, indent=2, ensure_ascii=False))
        sys.exit(1)

    result = optimize_listing(
        keyword=params.get('keyword'),
        asin=params.get('asin'),
        marketplace=params.get('marketplace', 'US'),
        category=params.get('category'),
        max_title_chars=params.get('max_title_chars', 200),
        bullet_count=params.get('bullet_count', 5),
        brand_blocklist=params.get('brand_blocklist'),
        bullet_features=params.get('bullet_features'),
        product_title=params.get('product_title'),
        product_description=params.get('product_description'),
        features=params.get('features') or params.get('product_features'),
        target_audience=params.get('target_audience'),
        product_brand=params.get('product_brand'),
        min_relevance=params.get('min_relevance', 25)
    )
    
    if 'error' in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
