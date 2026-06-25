#!/usr/bin/env python3
"""
Review Checker v3.0.0

Comprehensive review analysis with REAL review content:
1. Barrier Analysis - How many reviews needed to compete?
2. Pain Point Mining - Extract real complaints from review text
3. Sentiment Analysis - What do customers love/hate?
4. Opportunity Discovery - How to differentiate based on reviews?

NEW in v3.0.0:
- Uses /amazon/reviews/list API for actual review content
- Real pain point extraction from review text
- Supports 15 marketplaces (US via /amazon/usReviewsList, others via /amazon/reviews/list)

Usage:
    python3 review_checker.py '{"keyword": "yoga mat"}'
    python3 review_checker.py '{"keyword": "yoga mat", "market": "UK"}'
    python3 review_checker.py '{"asin": "B01LP0U5X0", "market": "UK"}'
    python3 review_checker.py '{"keyword": "yoga mat"}' --chart /tmp/charts
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Optional, List, Tuple
from urllib.request import Request, urlopen
import statistics
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

# Marketplace mapping for non-US reviews API (/amazon/reviews/list)
# US uses dedicated endpoint /amazon/usReviewsList (no domainCode needed)
MARKET_TO_DOMAIN = {
    'UK': 'co.uk',
    'CA': 'ca',
    'DE': 'de',
    'FR': 'fr',
    'IT': 'it',
    'ES': 'es',
    'JP': 'co.jp',
    'AU': 'com.au',
    'BR': 'com.br',
    'NL': 'nl',
    'SE': 'se',
    'MX': 'com.mx',
    'AE': 'ae',
    'IN': 'in'
}

# Pain point keywords for classification
PAIN_CATEGORIES = {
    'quality': ['cheap', 'flimsy', 'poor quality', 'low quality', 'poorly made', 'defective', 'broken', 'terrible', 'awful', 'horrible'],
    'durability': ['broke', 'fell apart', 'didnt last', "didn't last", 'wore out', 'stopped working', 'peeling', 'tearing', 'cracked', 'ripped'],
    'size_fit': ['too small', 'too big', 'wrong size', 'doesnt fit', "doesn't fit", 'sizing', 'dimensions', 'smaller than', 'bigger than'],
    'functionality': ['doesnt work', "doesn't work", 'not working', 'malfunction', 'useless', 'ineffective', 'failed', 'wont', "won't"],
    'shipping': ['damaged', 'arrived broken', 'packaging', 'shipping damage', 'dented', 'crushed', 'arrived damaged'],
    'value': ['overpriced', 'not worth', 'waste of money', 'rip off', 'expensive for', 'too expensive', 'ripoff'],
    'smell': ['smell', 'odor', 'stink', 'chemical', 'toxic smell', 'fumes', 'stinky', 'smelly'],
    'instructions': ['instructions', 'manual', 'confusing', 'hard to assemble', 'no directions', 'assembly'],
    'customer_service': ['customer service', 'no response', 'refund', 'return', 'support', 'seller'],
    'misleading': ['false advertising', 'not as described', 'misleading', 'fake', 'scam', 'different from picture', 'not as shown', 'looks nothing like']
}

# Positive aspects for sentiment
POSITIVE_ASPECTS = {
    'quality': ['high quality', 'well made', 'great quality', 'excellent quality', 'premium', 'sturdy', 'solid'],
    'value': ['great value', 'worth every', 'good price', 'affordable', 'bang for buck', 'worth the money'],
    'ease_of_use': ['easy to use', 'simple', 'user friendly', 'intuitive', 'straightforward', 'no fuss'],
    'durability': ['durable', 'lasts', 'lasting', 'holds up', 'long lasting', 'sturdy'],
    'appearance': ['looks great', 'beautiful', 'gorgeous', 'stylish', 'looks nice', 'attractive'],
    'comfort': ['comfortable', 'comfy', 'soft', 'cozy', 'feels great', 'feels good'],
    'fast_shipping': ['fast shipping', 'quick delivery', 'arrived early', 'prompt delivery'],
    'recommend': ['highly recommend', 'would recommend', 'love it', 'perfect', 'exactly what i needed']
}

SEVERITY_MAP = {
    'quality': 'HIGH',
    'durability': 'HIGH',
    'functionality': 'HIGH',
    'misleading': 'HIGH',
    'size_fit': 'MEDIUM',
    'value': 'MEDIUM',
    'smell': 'MEDIUM',
    'shipping': 'LOW',
    'instructions': 'LOW',
    'customer_service': 'MEDIUM'
}

# === API Functions ===

def api_call(endpoint: str, payload: dict, method: str = 'POST') -> Optional[dict]:
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(payload).encode('utf-8'),
                         headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}',
                                  'Content-Type': 'application/json'},
                         method=method)
    try:
        with urlopen(_proxy_req, timeout=60) as _proxy_resp:
            _proxy_result = json.loads(_proxy_resp.read().decode('utf-8'))
        if isinstance(_proxy_result, dict) and 'code' in _proxy_result:
            return _proxy_result.get('data', _proxy_result) if _proxy_result.get('code') == 0 else None
        return _proxy_result
    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        return None

def search_products(keyword: str, market: str = 'US', limit: int = 60) -> List[dict]:
    """Search Amazon products"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(market, 'amazon.com')
    })
    
    if result and isinstance(result, dict):
        if 'data' in result:
            return result['data'] if isinstance(result['data'], list) else []
        elif 'products' in result:
            return result['products']
    elif result and isinstance(result, list):
        return result
    return []

def get_reviews_content(asin: str, domain_code: str = 'co.uk',
                        is_us: bool = False,
                        star1: int = 20, star2: int = 20, star3: int = 10,
                        star4: int = 10, star5: int = 20,
                        sort_by: str = 'recent') -> dict:
    """
    Get actual review content using Reviews API via proxy.
    US market uses /amazon/usReviewsList, other markets use /amazon/reviews/list.
    """
    payload = {
        'asin': asin,
        'star1Num': star1,
        'star2Num': star2,
        'star3Num': star3,
        'star4Num': star4,
        'star5Num': star5,
        'sortBy': sort_by,
        'reviewerType': 'all_reviews',
        'mediaType': 'all_contents'
    }
    if is_us:
        endpoint = '/amazon/usReviewsList'
    else:
        endpoint = '/amazon/reviews/list'
        payload['domainCode'] = domain_code
    result = api_call(endpoint, payload)
    
    if result and 'data' in result:
        return {
            'reviews': result['data'],
            'total': result.get('total', len(result['data'])),
            'cost_token': result.get('costToken', 0)
        }
    elif result and 'errcode' in result:
        return {'error': result.get('errmsg', 'Unknown error'), 'errcode': result['errcode']}
    return {'error': 'No response', 'reviews': []}

# === Barrier Analysis Functions ===

def classify_review_tier(count: int) -> str:
    """Classify review count into tier"""
    if count == 0:
        return 'zero'
    elif count < 50:
        return 'starter'
    elif count < 200:
        return 'established'
    elif count < 1000:
        return 'competitive'
    elif count < 5000:
        return 'dominant'
    else:
        return 'fortress'

def calculate_barrier_score(median: float, top_10_avg: float, tier_breakdown: dict) -> Tuple[int, str]:
    """Calculate barrier score and level"""
    # Base score from median
    if median < 50:
        base_score = 85
    elif median < 100:
        base_score = 75
    elif median < 200:
        base_score = 65
    elif median < 500:
        base_score = 55
    elif median < 1000:
        base_score = 45
    elif median < 2000:
        base_score = 35
    elif median < 5000:
        base_score = 25
    else:
        base_score = 15
    
    # Adjustments
    starter_pct = (tier_breakdown.get('starter') or {}).get('pct', 0)
    established_pct = (tier_breakdown.get('established') or {}).get('pct', 0)
    fortress_pct = (tier_breakdown.get('fortress') or {}).get('pct', 0)
    
    if starter_pct + established_pct > 30:
        base_score += 10
    
    if fortress_pct > 30:
        base_score -= 15
    elif fortress_pct > 20:
        base_score -= 10
    
    if top_10_avg > 50000:
        base_score -= 15
    elif top_10_avg > 20000:
        base_score -= 10
    elif top_10_avg > 10000:
        base_score -= 5
    
    score = max(0, min(100, base_score))
    
    if score >= 70:
        level = 'LOW'
    elif score >= 50:
        level = 'MODERATE'
    elif score >= 30:
        level = 'HIGH'
    else:
        level = 'FORTRESS'
    
    return score, level

def analyze_barrier(products: List[dict]) -> dict:
    """Analyze review barrier from product list"""
    review_counts = []
    
    for p in products:
        count = p.get('ratings', 0) or p.get('reviewCount', 0) or p.get('reviews', 0) or 0
        if isinstance(count, str):
            count = int(count.replace(',', '')) if count.replace(',', '').isdigit() else 0
        review_counts.append(count)
    
    if not review_counts:
        return {'error': 'No review data'}
    
    sorted_counts = sorted(review_counts, reverse=True)
    top_10 = sorted_counts[:10]
    
    distribution = {
        'min': min(review_counts),
        'max': max(review_counts),
        'median': statistics.median(review_counts),
        'mean': round(statistics.mean(review_counts), 1),
        'p25': sorted_counts[int(len(sorted_counts) * 0.75)] if len(sorted_counts) >= 4 else sorted_counts[-1],
        'p75': sorted_counts[int(len(sorted_counts) * 0.25)] if len(sorted_counts) >= 4 else sorted_counts[0],
        'std': round(statistics.stdev(review_counts), 1) if len(review_counts) > 1 else 0
    }
    
    tiers = {'zero': 0, 'starter': 0, 'established': 0, 'competitive': 0, 'dominant': 0, 'fortress': 0}
    for count in review_counts:
        tier = classify_review_tier(count)
        tiers[tier] += 1
    
    total = len(review_counts)
    tier_breakdown = {
        tier: {'count': count, 'pct': round(count / total * 100, 1)}
        for tier, count in tiers.items()
    }
    
    top_10_avg = round(statistics.mean(top_10), 1) if top_10 else 0
    barrier_score, barrier_level = calculate_barrier_score(
        distribution['median'], top_10_avg, tier_breakdown
    )
    
    low_review_high_rank = [
        {'rank': i+1, 'reviews': review_counts[i]}
        for i in range(min(20, len(review_counts)))
        if review_counts[i] < 200
    ]
    
    return {
        'products_analyzed': len(products),
        'distribution': distribution,
        'tier_breakdown': tier_breakdown,
        'barrier_score': barrier_score,
        'barrier_level': barrier_level,
        'top_10_avg': top_10_avg,
        'low_review_opportunities': low_review_high_rank[:5]
    }

# === Pain Point Analysis (NEW in v3.0.0) ===

def parse_rating(rating_str) -> float:
    """Parse rating string to float"""
    if isinstance(rating_str, (int, float)):
        return float(rating_str)
    if isinstance(rating_str, str):
        match = re.search(r'(\d+\.?\d*)', rating_str)
        if match:
            return float(match.group(1))
    return 5.0

def classify_pain_point(text: str) -> List[Tuple[str, str]]:
    """Classify review text into pain point categories with matched phrase"""
    text_lower = text.lower()
    results = []
    
    for category, keywords in PAIN_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text_lower:
                results.append((category, keyword))
                break
    
    return results if results else [('other', '')]

def classify_positive_aspect(text: str) -> List[Tuple[str, str]]:
    """Classify review text into positive categories"""
    text_lower = text.lower()
    results = []
    
    for category, keywords in POSITIVE_ASPECTS.items():
        for keyword in keywords:
            if keyword in text_lower:
                results.append((category, keyword))
                break
    
    return results

def extract_pain_points_from_content(reviews: List[dict]) -> dict:
    """Extract pain points from actual review content"""
    negative_reviews = []
    positive_reviews = []
    
    for review in reviews:
        rating = parse_rating(review.get('rating', 5))
        review_data = {
            'rating': rating,
            'title': review.get('title', ''),
            'text': review.get('text', ''),
            'date': review.get('date', ''),
            'verified': review.get('verified', False),
            'vine': review.get('vine', False),
            'helpful': review.get('numberOfHelpful', 0),
            'has_media': bool(review.get('imageUrlList') or review.get('videoUrlList'))
        }
        
        if rating <= 3:
            negative_reviews.append(review_data)
        elif rating >= 4:
            positive_reviews.append(review_data)
    
    # Analyze negative reviews for pain points
    pain_category_counts = Counter()
    pain_examples = {cat: [] for cat in PAIN_CATEGORIES.keys()}
    pain_examples['other'] = []
    pain_phrases = {cat: Counter() for cat in PAIN_CATEGORIES.keys()}
    
    for review in negative_reviews:
        full_text = f"{review['title']} {review['text']}"
        classifications = classify_pain_point(full_text)
        
        for cat, phrase in classifications:
            pain_category_counts[cat] += 1
            if phrase:
                pain_phrases[cat][phrase] += 1
            
            if cat in pain_examples and len(pain_examples[cat]) < 3:
                snippet = (review['text'] or '')[:200] + '...' if len(review['text'] or '') > 200 else (review['text'] or '')
                pain_examples[cat].append({
                    'rating': review['rating'],
                    'title': review['title'],
                    'snippet': snippet,
                    'verified': review['verified']
                })
    
    # Analyze positive reviews for strengths
    positive_category_counts = Counter()
    positive_examples = {cat: [] for cat in POSITIVE_ASPECTS.keys()}
    
    for review in positive_reviews:
        full_text = f"{review['title']} {review['text']}"
        classifications = classify_positive_aspect(full_text)
        
        for cat, phrase in classifications:
            positive_category_counts[cat] += 1
            if cat in positive_examples and len(positive_examples[cat]) < 2:
                snippet = (review['text'] or '')[:150] + '...' if len(review['text'] or '') > 150 else (review['text'] or '')
                positive_examples[cat].append({
                    'rating': review['rating'],
                    'title': review['title'],
                    'snippet': snippet
                })
    
    # Build pain point list
    total_negative = len(negative_reviews)
    total_positive = len(positive_reviews)
    total_reviews = len(reviews)
    
    pain_points = []
    for category, count in pain_category_counts.most_common(10):
        if count > 0 and category != 'other':
            top_phrases = [p for p, _ in pain_phrases[category].most_common(3)]
            pain_points.append({
                'category': category.replace('_', ' ').title(),
                'category_key': category,
                'frequency': count,
                'percentage': round(count / total_negative * 100, 1) if total_negative > 0 else 0,
                'severity': SEVERITY_MAP.get(category, 'MEDIUM'),
                'common_phrases': top_phrases,
                'examples': pain_examples.get(category, [])[:2]
            })
    
    # Build positive aspects list
    positive_aspects = []
    for category, count in positive_category_counts.most_common(8):
        if count > 0:
            positive_aspects.append({
                'category': category.replace('_', ' ').title(),
                'frequency': count,
                'percentage': round(count / total_positive * 100, 1) if total_positive > 0 else 0,
                'examples': positive_examples.get(category, [])[:1]
            })
    
    # Calculate sentiment distribution
    rating_distribution = Counter()
    for review in reviews:
        rating = int(parse_rating(review.get('rating', 5)))
        rating_distribution[rating] += 1
    
    return {
        'reviews_analyzed': total_reviews,
        'negative_count': total_negative,
        'positive_count': total_positive,
        'negative_percentage': round(total_negative / total_reviews * 100, 1) if total_reviews > 0 else 0,
        'rating_distribution': {f'{k}_star': v for k, v in sorted(rating_distribution.items())},
        'pain_points': pain_points,
        'positive_aspects': positive_aspects,
        'verified_review_percentage': round(
            sum(1 for r in reviews if r.get('verified')) / total_reviews * 100, 1
        ) if total_reviews > 0 else 0,
        'vine_review_percentage': round(
            sum(1 for r in reviews if r.get('vine')) / total_reviews * 100, 1
        ) if total_reviews > 0 else 0,
        'media_review_percentage': round(
            sum(1 for r in reviews if r.get('imageUrlList') or r.get('videoUrlList')) / total_reviews * 100, 1
        ) if total_reviews > 0 else 0
    }

def generate_opportunities(pain_points: List[dict], positive_aspects: List[dict]) -> dict:
    """Generate improvement opportunities from pain points and positive aspects"""
    product_improvements = []
    listing_improvements = []
    differentiation_angles = []
    
    # From pain points - what to fix
    for pp in pain_points[:5]:
        cat = pp['category_key']
        severity = pp['severity']
        
        improvements = {
            'durability': (
                "Upgrade to more durable materials (reinforced stitching, premium plastics)",
                "Add durability claims with warranty info in title and bullets",
                "1-Year Durability Guarantee"
            ),
            'quality': (
                "Source higher quality materials, improve QC process",
                "Highlight quality certifications and material specs",
                "Premium Quality Promise"
            ),
            'size_fit': (
                "Offer multiple sizes or adjustable design, verify dimensions",
                "Add detailed size chart image, exact dimensions in bullets",
                "Size Guide + Easy Returns"
            ),
            'smell': (
                "Switch to odor-free, eco-certified materials",
                "Prominently mention 'odorless' or 'chemical-free' in title",
                "100% Odor-Free Guarantee"
            ),
            'functionality': (
                "Rigorous testing before launch, improve core mechanism",
                "Add demo video showing product in use",
                "Tested & Proven Performance"
            ),
            'value': (
                "Optimize costs or add bundle value",
                "Emphasize value comparison vs competitors",
                "Best Value in Category"
            ),
            'instructions': (
                "Create clear visual assembly guide, QR code to video",
                "Highlight 'Easy Setup' or 'No Tools Required'",
                "5-Minute Setup Guarantee"
            ),
            'shipping': (
                "Improve packaging with protective inserts",
                "Note 'Frustration-Free Packaging' if applicable",
                "Arrives Perfect Guarantee"
            ),
            'misleading': (
                "Ensure photos match exactly, update to real photos",
                "Use accurate dimensions and real customer photos",
                "What You See Is What You Get"
            ),
            'customer_service': (
                "Implement rapid response system (< 24h)",
                "Highlight 'Responsive Seller' and support contact",
                "24-Hour Support Response"
            )
        }
        
        if cat in improvements:
            prod, listing, diff = improvements[cat]
            product_improvements.append(prod)
            listing_improvements.append(listing)
            differentiation_angles.append(diff)
    
    # From positive aspects - what competitors do well (to match)
    competitor_strengths = []
    for pa in positive_aspects[:3]:
        cat = pa['category'].lower().replace(' ', '_')
        if pa['percentage'] > 20:
            competitor_strengths.append(f"{pa['category']}: {pa['percentage']:.0f}% of positive reviews mention this")
    
    return {
        'product_improvements': list(dict.fromkeys(product_improvements))[:5],
        'listing_improvements': list(dict.fromkeys(listing_improvements))[:5],
        'differentiation_angles': list(dict.fromkeys(differentiation_angles))[:5],
        'competitor_strengths_to_match': competitor_strengths
    }

def generate_insights(barrier: dict, pain_analysis: dict, opportunities: dict, market: str) -> dict:
    """Generate comprehensive narrative insights"""
    barrier_level = barrier.get('barrier_level', 'UNKNOWN')
    barrier_score = barrier.get('barrier_score', 0)
    median = (barrier.get('distribution') or {}).get('median', 0)
    top_10_avg = barrier.get('top_10_avg', 0)
    
    # Barrier assessment
    barrier_texts = {
        'LOW': f"Low barrier (score {barrier_score}). Median {median:.0f} reviews. Market accessible for new entrants.",
        'MODERATE': f"Moderate barrier (score {barrier_score}). Median {median:.0f} reviews. Need solid launch strategy with 100-200 reviews target.",
        'HIGH': f"High barrier (score {barrier_score}). Median {median:.0f} reviews. Requires strong differentiation and 300+ reviews to compete.",
        'FORTRESS': f"Fortress market (score {barrier_score}). Median {median:.0f} reviews, Top 10 avg {top_10_avg:.0f}. Extremely difficult entry - consider sub-niche."
    }
    barrier_text = barrier_texts.get(barrier_level, f"Barrier: {barrier_level}")
    
    # Pain point summary
    top_pains = pain_analysis.get('pain_points', [])[:3]
    if top_pains:
        pain_text = "Top customer complaints: " + ", ".join([
            f"**{p['category']}** ({p['percentage']:.0f}%)" for p in top_pains
        ])
        
        # Add specific examples
        if top_pains[0].get('common_phrases'):
            pain_text += f". Common phrases: '{', '.join(top_pains[0]['common_phrases'][:2])}'"
    else:
        pain_text = "No significant pain points identified from available reviews."
    
    # Positive aspects summary
    top_positives = pain_analysis.get('positive_aspects', [])[:3]
    if top_positives:
        positive_text = "Customers love: " + ", ".join([
            f"{p['category']} ({p['percentage']:.0f}%)" for p in top_positives
        ])
    else:
        positive_text = ""
    
    # Recommendations
    recommendations = []
    
    if barrier_level == 'LOW':
        recommendations.append("✅ Market entry feasible. Focus on quality and early review accumulation.")
    elif barrier_level == 'MODERATE':
        recommendations.append("⚠️ Competitive market. Strong launch with influencer/early reviewer strategy critical.")
    elif barrier_level == 'HIGH':
        recommendations.append("🔴 High barrier. Consider differentiated variant or niche targeting.")
    else:
        recommendations.append("⛔ Fortress market. Find a sub-niche or different angle to enter.")
    
    if top_pains:
        pain_cat = top_pains[0]['category']
        recommendations.append(f"🎯 Top opportunity: Address '{pain_cat}' issues that competitors fail at.")
        
        if top_pains[0]['severity'] == 'HIGH':
            recommendations.append(f"⚡ '{pain_cat}' is a HIGH severity issue - solving it could be a major differentiator.")
    
    if opportunities.get('differentiation_angles'):
        recommendations.append(f"💡 Differentiation: {opportunities['differentiation_angles'][0]}")
    
    
    return {
        'summary': f"Barrier: {barrier_level} ({barrier_score}/100) | Top Pain: {top_pains[0]['category'] if top_pains else 'N/A'}",
        'barrier_assessment': barrier_text,
        'pain_point_summary': pain_text,
        'positive_summary': positive_text,
        'recommendations': recommendations,
        'reviews_analyzed': pain_analysis.get('reviews_analyzed', 0),
        'negative_rate': f"{pain_analysis.get('negative_percentage', 0):.1f}%"
    }

# === Main Analysis Function ===

def analyze_reviews(keyword: str = None, asin: str = None, market: str = 'US', 
                   mode: str = 'full', limit: int = 60) -> dict:
    """
    Main analysis function
    
    Args:
        keyword: Search keyword (required if asin not provided)
        asin: Specific ASIN to analyze (optional)
        market: Marketplace (US, UK, DE, etc.)
        mode: 'full', 'barrier', or 'painpoints'
        limit: Number of products to analyze for barrier
    """
    is_us = market.upper() == 'US'
    domain_code = None if is_us else MARKET_TO_DOMAIN.get(market.upper(), 'co.uk')

    result = {
        'keyword': keyword,
        'asin': asin,
        'marketplace': market,
        'domain_code': domain_code,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'mode': mode,
        'api_version': 'v3.0.0'
    }
    
    products = []
    asins_to_analyze = []
    
    # Step 1: Get products/ASINs
    if keyword:
        print(f"Analyzing reviews for keyword: {keyword}", file=sys.stderr)
        print("[1/4] Fetching products...", file=sys.stderr)
        products = search_products(keyword, market, limit)
        
        if products:
            print(f"  ✓ Got {len(products)} products", file=sys.stderr)
            
            # Clean products if category cleaner available
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                shared_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'shared')
                from category_cleaner import clean_products, format_category_report
                
                products, cleaning_report = clean_products(products, keyword)
                if cleaning_report.get('removed_count', 0) > 0:
                    print(format_category_report(cleaning_report), file=sys.stderr)
                    result['category_cleaning'] = {
                        'applied': True,
                        'target_category': cleaning_report.get('target_category'),
                        'original_count': cleaning_report.get('original_count'),
                        'removed_count': cleaning_report.get('removed_count')
                    }
            except Exception as e:
                pass
            
            asins_to_analyze = [p.get('asin') for p in products[:10] if p.get('asin')]
        else:
            result['error'] = 'No products found'
            return result
    
    elif asin:
        print(f"Analyzing reviews for ASIN: {asin}", file=sys.stderr)
        asins_to_analyze = [asin]
    
    else:
        result['error'] = 'Either keyword or asin required'
        return result
    
    # Step 2: Barrier analysis (from search results)
    if products and mode in ['full', 'barrier']:
        print("[2/4] Analyzing review barrier...", file=sys.stderr)
        barrier = analyze_barrier(products)
        result['barrier_analysis'] = barrier
        print(f"  ✓ Barrier: {barrier.get('barrier_level', 'N/A')} (score {barrier.get('barrier_score', 0)})", file=sys.stderr)
    
    # Step 3: Fetch actual review content
    pain_analysis = {'pain_points': [], 'positive_aspects': [], 'reviews_analyzed': 0}
    opportunities = {'product_improvements': [], 'listing_improvements': [], 'differentiation_angles': []}
    
    if mode in ['full', 'painpoints'] and asins_to_analyze:
        print(f"[3/4] Fetching review content from {len(asins_to_analyze[:5])} products in parallel...", file=sys.stderr)
        
        all_reviews = []
        asins_batch = asins_to_analyze[:5]
        
        # Parallel review fetching
        def fetch_reviews_for_asin(asin):
            return get_reviews_content(
                asin=asin,
                domain_code=domain_code,
                is_us=is_us,
                star1=30, star2=20, star3=10, star4=10, star5=20,
                sort_by='helpful'
            )
        
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_reviews_for_asin, asin): asin for asin in asins_batch}
                for future in as_completed(futures):
                    asin = futures[future]
                    try:
                        review_result = future.result(timeout=15)
                        if review_result and review_result.get('reviews'):
                            all_reviews.extend(review_result['reviews'])
                    except Exception:
                        pass
        except Exception:
            # Fallback to sequential
            for asin in asins_batch:
                review_result = fetch_reviews_for_asin(asin)
                if review_result and review_result.get('reviews'):
                    all_reviews.extend(review_result['reviews'])
        
        print(f"  ✓ Fetched reviews from {len(asins_batch)} ASINs", file=sys.stderr)
        
        if all_reviews:
            print(f"  ✓ Total: {len(all_reviews)} reviews collected", file=sys.stderr)
            
            print("[4/4] Analyzing review content...", file=sys.stderr)
            pain_analysis = extract_pain_points_from_content(all_reviews)
            result['pain_point_analysis'] = pain_analysis
            
            opportunities = generate_opportunities(
                pain_analysis.get('pain_points', []),
                pain_analysis.get('positive_aspects', [])
            )
            result['opportunities'] = opportunities
            
            print(f"  ✓ Found {len(pain_analysis['pain_points'])} pain point categories", file=sys.stderr)
        else:
            print("  ⚠️ No reviews retrieved", file=sys.stderr)
            result['pain_point_analysis'] = {'note': 'No reviews available from API'}
    
    # Generate insights
    result['insights'] = generate_insights(
        result.get('barrier_analysis', {}),
        pain_analysis,
        opportunities,
        market
    )
    
    # Add top products for reference
    if products:
        result['top_products'] = [
            {
                'asin': p.get('asin'),
                'title': (p.get('title', '')[:60] + '...') if len(p.get('title', '')) > 60 else p.get('title'),
                'reviews': p.get('ratings', 0),
                'rating': p.get('rating'),
                'price': p.get('extractedPrice') or p.get('price')
            }
            for p in products[:10]
        ]
    
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
    
    keyword = result.get('keyword', result.get('asin', 'Unknown'))
    barrier = result.get('barrier_analysis', {})
    pain_points = result.get('pain_point_analysis', {})
    
    # Colors
    GOOD = get_color('good')
    NEUTRAL = get_color('muted')
    WARNING = get_color('secondary')
    BAD = get_color('hot')
    BLUE = get_color('primary')
    
    # Chart 1: Tier Distribution
    if barrier.get('tier_breakdown'):
        fig, ax = plt.subplots(figsize=(10, 6))
        
        tiers = barrier['tier_breakdown']
        labels = ['Zero\n(0)', 'Starter\n(1-49)', 'Established\n(50-199)', 
                  'Competitive\n(200-999)', 'Dominant\n(1K-5K)', 'Fortress\n(5K+)']
        values = [tiers.get(t, {}).get('pct', 0) for t in 
                  ['zero', 'starter', 'established', 'competitive', 'dominant', 'fortress']]
        colors = [GOOD, GOOD, NEUTRAL, WARNING, BAD, BAD]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                        f'{val:.1f}%', ha='center', va='bottom', fontsize=10)
        
        ax.set_ylabel('Percentage of Products', fontsize=11)
        ax.set_title(f'REVIEW TIER DISTRIBUTION: {keyword.upper()[:30]}', fontweight='bold', fontsize=13, pad=15)
        ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_tier_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Tier Distribution", file=sys.stderr)
    
    # Chart 2: Pain Points (from real reviews)
    pps = pain_points.get('pain_points', [])
    if pps:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = [p['category'] for p in pps[:8]]
        frequencies = [p['percentage'] for p in pps[:8]]
        severities = [p['severity'] for p in pps[:8]]
        
        colors = [BAD if s == 'HIGH' else WARNING if s == 'MEDIUM' else NEUTRAL for s in severities]
        
        y_pos = range(len(categories))
        bars = ax.barh(y_pos, frequencies, color=colors, edgecolor='white', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.invert_yaxis()
        ax.set_xlabel('% of Negative Reviews', fontsize=11)
        ax.set_title(f'PAIN POINTS FROM REVIEWS: {keyword.upper()[:30]}', fontweight='bold', fontsize=13, pad=15)
        
        for bar, val, pp in zip(bars, frequencies, pps[:8]):
            severity_icon = '🔴' if pp['severity'] == 'HIGH' else '🟡' if pp['severity'] == 'MEDIUM' else '⚪'
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_pain_points.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Pain Points", file=sys.stderr)
    
    # Chart 3: Rating Distribution
    rating_dist = pain_points.get('rating_distribution', {})
    if rating_dist:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        stars = ['1★', '2★', '3★', '4★', '5★']
        values = [rating_dist.get(f'{i}_star', 0) for i in range(1, 6)]
        colors = [BAD, WARNING, NEUTRAL, GOOD, GOOD]
        
        bars = ax.bar(stars, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.02,
                        str(val), ha='center', va='bottom', fontsize=11)
        
        ax.set_ylabel('Number of Reviews', fontsize=11)
        ax.set_title(f'RATING DISTRIBUTION: {keyword.upper()[:30]}', fontweight='bold', fontsize=13, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_rating_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Rating Distribution", file=sys.stderr)
    
    # Chart 4: Positive Aspects
    positives = pain_points.get('positive_aspects', [])
    if positives:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        categories = [p['category'] for p in positives[:6]]
        frequencies = [p['percentage'] for p in positives[:6]]
        
        y_pos = range(len(categories))
        bars = ax.barh(y_pos, frequencies, color=BLUE, edgecolor='white', linewidth=2)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories)
        ax.invert_yaxis()
        ax.set_xlabel('% of Positive Reviews', fontsize=11)
        ax.set_title(f'WHAT CUSTOMERS LOVE: {keyword.upper()[:30]}', fontweight='bold', fontsize=13, pad=15)
        
        for bar, val in zip(bars, frequencies):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}%', va='center', fontsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_positive_aspects.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Positive Aspects", file=sys.stderr)
    
    # Chart 5: Barrier Score Gauge
    if barrier.get('barrier_score') is not None:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        score = barrier['barrier_score']
        level = barrier['barrier_level']
        
        gauge_colors = [BAD, WARNING, get_color('warning'), GOOD]
        gauge_labels = ['FORTRESS\n(0-30)', 'HIGH\n(30-50)', 'MODERATE\n(50-70)', 'LOW\n(70-100)']
        ranges = [30, 20, 20, 30]
        starts = [0, 30, 50, 70]
        
        for start, width, color in zip(starts, ranges, gauge_colors):
            ax.barh(0, width, left=start, height=0.3, color=color, edgecolor='white', linewidth=2)
        
        ax.scatter([score], [0], s=300, c='black', marker='^', zorder=5)
        ax.text(score, 0.25, f'Score: {score}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        for start, width, label in zip(starts, ranges, gauge_labels):
            ax.text(start + width/2, -0.25, label, ha='center', va='top', fontsize=9)
        
        ax.set_xlim(-5, 105)
        ax.set_ylim(-0.6, 0.5)
        ax.set_title(f'BARRIER SCORE: {level}', fontweight='bold', fontsize=13, pad=15)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/5_barrier_score.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 5: Barrier Score", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Review Checker v3.1.0')
    parser.add_argument('params', nargs='?', default='{}', help='JSON parameters')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    parser.add_argument('--csv', metavar='PATH', help='Export results to CSV')
    parser.add_argument('--excel', metavar='PATH', help='Export results to Excel')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(f"Invalid JSON: {args.params}", file=sys.stderr)
        sys.exit(1)
    
    keyword = params.get('keyword')
    asin = params.get('asin')
    
    if not keyword and not asin:
        print("Missing required parameter: keyword or asin", file=sys.stderr)
        sys.exit(1)
    
    market = params.get('market', 'US')
    mode = params.get('mode', 'full')
    limit = params.get('limit', 60)
    
    result = analyze_reviews(keyword, asin, market, mode, limit)
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []
    
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
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
