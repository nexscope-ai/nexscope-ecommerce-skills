#!/usr/bin/env python3
"""
Differentiation Advisor v2.0.0

Analyze competitors and suggest differentiation strategies based on REAL review data.
Answers: "How should I differentiate my product?"

NEW in v2.0.0:
- Uses /amazon/reviews/list API for actual review content
- Real pain point extraction from customer complaints
- Competitor strength analysis from positive reviews
- Enhanced USP recommendations with evidence

Data Sources:
- Amazon Search API (via NexScope proxy)
- Amazon Reviews List API (via NexScope proxy)
- Product detail extraction

Usage:
    python3 differentiation_advisor.py '{"keyword": "yoga mat"}'
    python3 differentiation_advisor.py '{"keyword": "bluetooth earbuds", "market": "UK"}'
    python3 differentiation_advisor.py '{"keyword": "yoga mat"}' --chart /tmp/charts
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Tuple
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
    'IN': 'in'
}

# Feature keywords to detect in bullets/titles
FEATURE_KEYWORDS = {
    'material': ['foam', 'rubber', 'tpe', 'pvc', 'cork', 'cotton', 'leather', 'silicone', 'bamboo', 'natural', 'metal', 'plastic', 'wood'],
    'thickness': ['thick', 'thin', 'mm', 'inch', '6mm', '8mm', '10mm', '1/4', '1/2', 'ultra-thin', 'slim'],
    'grip': ['non-slip', 'anti-slip', 'grip', 'traction', 'sticky', 'non slip'],
    'portability': ['portable', 'travel', 'foldable', 'lightweight', 'carrying', 'strap', 'bag', 'compact', 'folding'],
    'eco': ['eco', 'sustainable', 'recycled', 'biodegradable', 'organic', 'natural', 'green', 'eco-friendly'],
    'durability': ['durable', 'long-lasting', 'heavy-duty', 'tear-resistant', 'sturdy', 'reinforced'],
    'comfort': ['cushion', 'padding', 'soft', 'comfortable', 'support', 'joint', 'ergonomic'],
    'size': ['large', 'extra-large', 'wide', 'long', 'compact', 'standard', 'oversized'],
    'waterproof': ['waterproof', 'water-resistant', 'moisture', 'sweat-proof', 'easy clean', 'washable'],
    'odor': ['odorless', 'no smell', 'low odor', 'chemical-free', 'non-toxic'],
    'warranty': ['warranty', 'guarantee', 'replacement', 'lifetime', 'money back'],
    'certification': ['certified', 'tested', 'approved', 'dermatologist', 'hypoallergenic', 'fda', 'ce'],
    'wireless': ['wireless', 'bluetooth', 'wifi', 'cordless'],
    'battery': ['battery', 'rechargeable', 'long battery', 'fast charging', 'usb-c'],
    'noise_cancel': ['noise canceling', 'noise cancelling', 'anc', 'active noise', 'noise reduction'],
    'microphone': ['microphone', 'mic', 'call', 'voice'],
    'touch': ['touch control', 'touch sensor', 'tap control'],
    # Skincare / beauty specific
    'ingredients': ['hyaluronic', 'salicylic', 'niacinamide', 'retinol', 'vitamin c', 'ceramide', 'peptide', 'aha', 'bha', 'glycolic', 'benzoyl peroxide', 'tea tree', 'aloe', 'collagen'],
    'skin_type': ['oily skin', 'dry skin', 'sensitive skin', 'combination', 'acne-prone', 'all skin', 'normal skin', 'mature skin'],
    'fragrance_free': ['fragrance free', 'fragrance-free', 'unscented', 'no fragrance', 'scent-free'],
    'gentle': ['gentle', 'mild', 'soothing', 'calming', 'non-irritating', 'non-drying'],
    'clinical': ['clinically proven', 'dermatologist recommended', 'dermatologist tested', 'clinical strength', 'doctor recommended'],
    'cruelty_free': ['cruelty free', 'cruelty-free', 'not tested on animals', 'vegan', 'leaping bunny'],
    'paraben_free': ['paraben free', 'paraben-free', 'sulfate free', 'sulfate-free', 'phthalate free', 'no parabens'],
}

# Category detection: map product category signals to relevant feature subsets
CATEGORY_FEATURE_MAP = {
    'skincare': ['ingredients', 'skin_type', 'fragrance_free', 'gentle', 'clinical', 'cruelty_free', 'paraben_free', 'eco', 'certification', 'odor', 'portability', 'size'],
    'electronics': ['wireless', 'battery', 'noise_cancel', 'microphone', 'touch', 'waterproof', 'durability', 'comfort', 'portability', 'warranty', 'certification'],
    'fitness': ['material', 'thickness', 'grip', 'portability', 'eco', 'durability', 'comfort', 'size', 'waterproof', 'odor', 'warranty', 'certification'],
    'general': None,  # Use all features
}

# Signals to detect product category from keyword + titles
CATEGORY_SIGNALS = {
    'skincare': ['face wash', 'cleanser', 'moisturizer', 'serum', 'sunscreen', 'toner', 'lotion', 'cream', 'lip balm',
                 'shampoo', 'conditioner', 'body wash', 'soap', 'skincare', 'skin care', 'facial', 'acne', 'anti-aging',
                 'eye cream', 'makeup', 'cosmetic', 'beauty', 'exfoliat', 'retinol', 'vitamin c serum', 'spf'],
    'electronics': ['earbuds', 'headphones', 'speaker', 'charger', 'cable', 'bluetooth', 'wireless', 'tablet', 'keyboard',
                    'mouse', 'camera', 'monitor', 'microphone', 'smart watch', 'fitness tracker', 'power bank'],
    'fitness': ['yoga mat', 'exercise', 'resistance band', 'dumbbell', 'jump rope', 'foam roller', 'gym', 'workout',
                'fitness mat', 'pull up bar', 'kettlebell', 'ab roller'],
}

def detect_product_category(keyword: str, titles: List[str] = None) -> str:
    """Detect product category from keyword and product titles to filter relevant features."""
    text = keyword.lower()
    if titles:
        text += ' ' + ' '.join(t.lower() for t in titles[:10])
    
    scores = {}
    for category, signals in CATEGORY_SIGNALS.items():
        score = sum(1 for s in signals if s in text)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return 'general'

def get_feature_keywords_for_category(category: str) -> dict:
    """Return filtered FEATURE_KEYWORDS for the detected product category."""
    allowed = CATEGORY_FEATURE_MAP.get(category)
    if allowed is None:
        return FEATURE_KEYWORDS
    return {k: v for k, v in FEATURE_KEYWORDS.items() if k in allowed}

# Pain point categories with keywords
PAIN_CATEGORIES = {
    'quality': ['cheap', 'flimsy', 'poor quality', 'low quality', 'poorly made', 'defective', 'broken', 'terrible', 'awful'],
    'durability': ['broke', 'fell apart', "didn't last", 'wore out', 'stopped working', 'peeling', 'tearing', 'cracked'],
    'size_fit': ['too small', 'too big', 'wrong size', "doesn't fit", 'sizing', 'uncomfortable fit'],
    'functionality': ["doesn't work", 'not working', 'malfunction', 'useless', 'ineffective', 'failed'],
    'shipping': ['damaged', 'arrived broken', 'packaging', 'shipping damage', 'dented'],
    'value': ['overpriced', 'not worth', 'waste of money', 'rip off', 'expensive for'],
    'smell': ['smell', 'odor', 'stink', 'chemical', 'toxic smell', 'fumes'],
    'connection': ['disconnect', 'connection', 'pairing', 'bluetooth issues', 'drops', 'cutting out'],
    'sound': ['sound quality', 'audio', 'bass', 'tinny', 'muffled', 'distortion'],
    'battery': ['battery life', 'dies quickly', 'short battery', "won't charge", 'charging issues'],
    'comfort': ['uncomfortable', 'hurts', 'painful', 'too tight', 'falls out']
}

# Positive aspects
POSITIVE_ASPECTS = {
    'quality': ['high quality', 'well made', 'great quality', 'excellent quality', 'premium', 'sturdy'],
    'value': ['great value', 'worth every', 'good price', 'affordable', 'bang for buck'],
    'ease_of_use': ['easy to use', 'simple', 'user friendly', 'intuitive', 'straightforward'],
    'durability': ['durable', 'lasts', 'long lasting', 'holds up', 'sturdy'],
    'comfort': ['comfortable', 'comfy', 'soft', 'cozy', 'feels great'],
    'sound': ['great sound', 'amazing sound', 'clear sound', 'good bass', 'crisp'],
    'battery': ['great battery', 'long battery', 'lasts all day', 'charges fast'],
    'recommend': ['highly recommend', 'would recommend', 'love it', 'perfect']
}

SEVERITY_MAP = {
    'quality': 'HIGH', 'durability': 'HIGH', 'functionality': 'HIGH',
    'connection': 'HIGH', 'sound': 'HIGH', 'battery': 'MEDIUM',
    'size_fit': 'MEDIUM', 'value': 'MEDIUM', 'smell': 'MEDIUM',
    'comfort': 'MEDIUM', 'shipping': 'LOW'
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

def search_products(keyword: str, marketplace: str = 'US', limit: int = 20) -> List[dict]:
    """Search for products by keyword"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(marketplace, 'amazon.com')
    })
    
    if result and isinstance(result, dict):
        # Response format: {errcode: 200, products: [...]}
        if 'products' in result:
            return result['products']
        elif 'data' in result:
            return result['data'] if isinstance(result['data'], list) else []
    elif result and isinstance(result, list):
        return result
    return []

def get_reviews_content(asin: str, domain_code: str = 'co.uk',
                       is_us: bool = False,
                       star1: int = 25, star2: int = 15, star3: int = 10,
                       star4: int = 15, star5: int = 25) -> dict:
    """Get review content. US uses /amazon/usReviewsList, others use /amazon/reviews/list."""
    payload = {
        'asin': asin,
        'star1Num': star1,
        'star2Num': star2,
        'star3Num': star3,
        'star4Num': star4,
        'star5Num': star5,
        'sortBy': 'helpful',
        'reviewerType': 'all_reviews'
    }
    if is_us:
        endpoint = '/amazon/usReviewsList'
    else:
        endpoint = '/amazon/reviews/list'
        payload['domainCode'] = domain_code
    result = api_call(endpoint, payload)
    
    if result and 'data' in result:
        return {'reviews': result['data'], 'total': result.get('total', len(result['data']))}
    return {'error': (result or {}).get('errmsg', 'No data'), 'reviews': []}

# === Analysis Functions ===

def parse_rating(rating_str) -> float:
    """Parse rating string to float"""
    if isinstance(rating_str, (int, float)):
        return float(rating_str)
    if isinstance(rating_str, str):
        match = re.search(r'(\d+\.?\d*)', rating_str)
        if match:
            return float(match.group(1))
    return 5.0

def extract_features_from_text(text: str, feature_kw: dict = None) -> Dict[str, List[str]]:
    """Extract features from text (title, bullets)"""
    text_lower = text.lower()
    features_found = {}
    kw_dict = feature_kw or FEATURE_KEYWORDS
    
    for category, keywords in kw_dict.items():
        matches = []
        for kw in keywords:
            if kw in text_lower:
                matches.append(kw)
        if matches:
            features_found[category] = list(set(matches))
    
    return features_found

def analyze_competitor_features(products: List[dict], feature_kw: dict = None) -> Dict[str, dict]:
    """Analyze features across all competitors"""
    kw_dict = feature_kw or FEATURE_KEYWORDS
    feature_counts = Counter()
    feature_products = {cat: [] for cat in kw_dict.keys()}
    
    for product in products:
        title = product.get('title', '')
        features = extract_features_from_text(title, kw_dict)
        
        for category, keywords in features.items():
            feature_counts[category] += 1
            if len(feature_products[category]) < 3:
                feature_products[category].append({
                    'asin': product.get('asin'),
                    'title': title[:60] + '...' if len(title) > 60 else title,
                    'keywords': keywords
                })
    
    total = len(products)
    result = {}
    
    for category, count in feature_counts.most_common():
        pct = (count / total * 100) if total > 0 else 0
        if pct >= 80:
            status = 'table_stakes'
        elif pct >= 50:
            status = 'common'
        elif pct >= 20:
            status = 'differentiator'
        else:
            status = 'rare'
        
        result[category] = {
            'category': category.replace('_', ' ').title(),
            'count': count,
            'percentage': round(pct),
            'status': status,
            'examples': feature_products.get(category, [])
        }
    
    return result

def extract_pain_points_from_reviews(reviews: List[dict]) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    """Extract pain points AND positive aspects from actual review content"""
    negative_reviews = []
    positive_reviews = []
    
    for review in reviews:
        rating = parse_rating(review.get('rating', 5))
        review_data = {
            'rating': rating,
            'title': review.get('title', ''),
            'text': review.get('text', ''),
            'verified': review.get('verified', False),
            'helpful': review.get('numberOfHelpful', 0)
        }
        
        if rating <= 3:
            negative_reviews.append(review_data)
        elif rating >= 4:
            positive_reviews.append(review_data)
    
    # Analyze pain points
    pain_counts = Counter()
    pain_examples = {cat: [] for cat in PAIN_CATEGORIES.keys()}
    pain_phrases = {cat: Counter() for cat in PAIN_CATEGORIES.keys()}
    
    for review in negative_reviews:
        full_text = f"{review['title']} {review['text']}".lower()
        
        for category, keywords in PAIN_CATEGORIES.items():
            for kw in keywords:
                if kw in full_text:
                    pain_counts[category] += 1
                    pain_phrases[category][kw] += 1
                    if len(pain_examples[category]) < 2:
                        snippet = (review['text'] or '')[:150] + '...' if len(review['text'] or '') > 150 else (review['text'] or '')
                        pain_examples[category].append({
                            'rating': review['rating'],
                            'title': review['title'],
                            'snippet': snippet
                        })
                    break
    
    # Analyze positive aspects
    positive_counts = Counter()
    positive_examples = {cat: [] for cat in POSITIVE_ASPECTS.keys()}
    
    for review in positive_reviews:
        full_text = f"{review['title']} {review['text']}".lower()
        
        for category, keywords in POSITIVE_ASPECTS.items():
            for kw in keywords:
                if kw in full_text:
                    positive_counts[category] += 1
                    if len(positive_examples[category]) < 2:
                        snippet = (review['text'] or '')[:150] + '...' if len(review['text'] or '') > 150 else (review['text'] or '')
                        positive_examples[category].append({
                            'rating': review['rating'],
                            'snippet': snippet
                        })
                    break
    
    # Build pain points result
    total_negative = len(negative_reviews) or 1
    pain_points = {}
    for category, count in pain_counts.most_common():
        if count > 0:
            top_phrases = [p for p, _ in pain_phrases[category].most_common(3)]
            pain_points[category] = {
                'category': category.replace('_', ' ').title(),
                'count': count,
                'percentage': round(count / total_negative * 100, 1),
                'severity': SEVERITY_MAP.get(category, 'MEDIUM'),
                'phrases': top_phrases,
                'examples': pain_examples.get(category, [])
            }
    
    # Build positive aspects result
    total_positive = len(positive_reviews) or 1
    positive_aspects = {}
    for category, count in positive_counts.most_common():
        if count > 0:
            positive_aspects[category] = {
                'category': category.replace('_', ' ').title(),
                'count': count,
                'percentage': round(count / total_positive * 100, 1),
                'examples': positive_examples.get(category, [])
            }
    
    return pain_points, positive_aspects

def generate_differentiation_opportunities(
    feature_analysis: Dict[str, dict],
    pain_points: Dict[str, dict],
    positive_aspects: Dict[str, dict]
) -> List[dict]:
    """Generate differentiation opportunities based on analysis"""
    opportunities = []
    
    # Priority 1: Solve HIGH severity pain points
    for cat_key, data in pain_points.items():
        if data['severity'] == 'HIGH' and data['percentage'] >= 10:
            solution_map = {
                'quality': ('Premium Quality Materials', 'Use higher-grade materials, add quality certifications'),
                'durability': ('Built to Last', 'Reinforce weak points, offer extended warranty'),
                'functionality': ('Reliable Performance', 'Extensive QA testing, clear instructions'),
                'connection': ('Rock-Solid Connection', 'Latest Bluetooth chip, better antenna design'),
                'sound': ('Superior Audio', 'Premium drivers, tuned by audio engineers')
            }
            
            name, solution = solution_map.get(cat_key, (f'Fix {data["category"]}', f'Address {cat_key} issues'))
            
            opportunities.append({
                'priority': 'CRITICAL',
                'type': 'pain_point_solver',
                'opportunity': name,
                'insight': f'{data["percentage"]:.0f}% of negative reviews mention {data["category"].lower()}',
                'evidence': data.get('phrases', []),
                'action': solution,
                'usp_hook': f'"{name}" - No more {data["category"].lower()} issues',
                'difficulty': 'MEDIUM'
            })
    
    # Priority 2: Rare features that could differentiate
    for cat_key, data in feature_analysis.items():
        if data['status'] in ['rare', 'differentiator'] and data['percentage'] >= 5:
            opportunities.append({
                'priority': 'HIGH',
                'type': 'feature_gap',
                'opportunity': f'Add {data["category"]} Focus',
                'insight': f'Only {data["percentage"]}% of competitors emphasize {data["category"].lower()}',
                'evidence': [ex.get('title', '')[:50] for ex in data.get('examples', [])[:2]],
                'action': f'Develop strong {data["category"].lower()} features and highlight in listing',
                'usp_hook': f'"Best-in-Class {data["category"]}"',
                'difficulty': 'MEDIUM'
            })
    
    # Priority 3: Match competitor strengths (from positive reviews)
    for cat_key, data in positive_aspects.items():
        if data['percentage'] >= 20:
            opportunities.append({
                'priority': 'MEDIUM',
                'type': 'strength_match',
                'opportunity': f'Match {data["category"]} Excellence',
                'insight': f'{data["percentage"]:.0f}% of positive reviews praise {data["category"].lower()}',
                'evidence': [ex.get('snippet', '')[:80] for ex in data.get('examples', [])[:1]],
                'action': f'Ensure your product matches or exceeds competitor {data["category"].lower()}',
                'usp_hook': None,  # Not a differentiator, just table stakes
                'difficulty': 'LOW'
            })
    
    # Sort by priority
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    opportunities.sort(key=lambda x: priority_order.get(x.get('priority', 'LOW'), 3))
    
    return opportunities

def generate_usp_recommendations(
    opportunities: List[dict],
    pain_points: Dict[str, dict],
    positive_aspects: Dict[str, dict],
    market_data: dict
) -> List[dict]:
    """Generate specific USP recommendations"""
    recommendations = []
    
    # USP 1: From top pain point
    critical_opps = [o for o in opportunities if o['priority'] == 'CRITICAL']
    if critical_opps:
        opp = critical_opps[0]
        recommendations.append({
            'strategy': 'Pain Point Solver',
            'usp': opp['usp_hook'],
            'target': 'Customers frustrated with current options',
            'price_position': 'Premium (+15-25%)',
            'title_element': opp['opportunity'],
            'first_bullet': f"✓ {opp['action']}",
            'evidence': f"Based on {pain_points.get(next(iter(pain_points), ''), {}).get('percentage', 0):.0f}% complaint rate"
        })
    
    # USP 2: Feature differentiation
    feature_opps = [o for o in opportunities if o['type'] == 'feature_gap']
    if feature_opps:
        opp = feature_opps[0]
        recommendations.append({
            'strategy': 'Feature Leader',
            'usp': opp['usp_hook'],
            'target': f'Customers who value {opp["opportunity"].lower()}',
            'price_position': 'Premium (+10-20%)',
            'title_element': opp['opportunity'].replace('Add ', '').replace(' Focus', ''),
            'first_bullet': f"✓ Industry-leading {opp['opportunity'].lower().replace('add ', '')}",
            'evidence': opp['insight']
        })
    
    # USP 3: Value play
    avg_price = market_data.get('avg_price', 0)
    recommendations.append({
        'strategy': 'Value Champion',
        'usp': 'Premium Features, Smart Price',
        'target': 'Price-conscious buyers who don\'t want to compromise',
        'price_position': f'Value (-10-15% below ${avg_price:.2f} avg)' if avg_price else 'Value (-10-15%)',
        'title_element': 'Professional Grade',
        'first_bullet': '✓ Same premium features, better value',
        'evidence': 'Price-sensitive segment always exists'
    })
    
    return recommendations

def generate_action_plan(
    opportunities: List[dict],
    usps: List[dict],
    feature_analysis: Dict[str, dict],
    pain_points: Dict[str, dict]
) -> List[dict]:
    """Generate step-by-step action plan"""
    actions = []
    
    # Step 1: Table stakes
    table_stakes = [f for f, d in feature_analysis.items() if d['status'] == 'table_stakes']
    if table_stakes:
        features_str = ', '.join([f.replace('_', ' ') for f in table_stakes[:4]])
        actions.append({
            'step': 1,
            'phase': 'MUST HAVE',
            'action': f'Ensure product has: {features_str}',
            'reason': 'These are expected by 80%+ of customers',
            'timeline': 'Before launch'
        })
    
    # Step 2: Key differentiator
    if opportunities:
        top_opp = opportunities[0]
        actions.append({
            'step': 2,
            'phase': 'DIFFERENTIATE',
            'action': top_opp['action'],
            'reason': top_opp['insight'],
            'timeline': 'Product development'
        })
    
    # Step 3: Listing optimization
    if usps:
        top_usp = usps[0]
        actions.append({
            'step': 3,
            'phase': 'LISTING',
            'action': f'Lead title with "{top_usp["title_element"]}", first bullet: {top_usp["first_bullet"]}',
            'reason': f'Target: {top_usp["target"]}',
            'timeline': 'Listing creation'
        })
    
    # Step 4: Visual proof
    actions.append({
        'step': 4,
        'phase': 'IMAGES',
        'action': 'Create comparison infographic showing your key advantage vs competitors',
        'reason': 'Visual proof of differentiation',
        'timeline': 'Before launch'
    })
    
    # Step 5: Price positioning
    if usps:
        actions.append({
            'step': 5,
            'phase': 'PRICING',
            'action': f'Position as {usps[0]["price_position"]}',
            'reason': 'Price signals quality for differentiated product',
            'timeline': 'Launch'
        })
    
    # Step 6: Review strategy
    if pain_points:
        top_pain = list(pain_points.keys())[0] if pain_points else 'quality'
        actions.append({
            'step': 6,
            'phase': 'REVIEWS',
            'action': f'Encourage reviews mentioning how you solved {top_pain.replace("_", " ")} issues',
            'reason': 'Social proof of differentiation',
            'timeline': 'Post-launch'
        })
    
    return actions

def generate_insights(
    feature_analysis: Dict[str, dict],
    pain_points: Dict[str, dict],
    positive_aspects: Dict[str, dict],
    opportunities: List[dict],
    market_data: dict
) -> dict:
    """Generate narrative insights"""
    
    # Top pain point
    top_pain = None
    top_pain_pct = 0
    for cat, data in pain_points.items():
        if data['percentage'] > top_pain_pct:
            top_pain = data['category']
            top_pain_pct = data['percentage']
    
    # Top positive
    top_positive = None
    for cat, data in positive_aspects.items():
        top_positive = data['category']
        break
    
    # Feature gap
    rare_features = [f for f, d in feature_analysis.items() if d['status'] in ['rare', 'differentiator']]
    
    summary = f"Analyzed {market_data.get('analyzed', 0)} competitors."
    
    if top_pain:
        summary += f" Top complaint: {top_pain} ({top_pain_pct:.0f}%)."
    
    if rare_features:
        summary += f" Underutilized features: {', '.join(rare_features[:3])}."
    
    recommendations = []
    
    if opportunities:
        recommendations.append(f"🎯 Top opportunity: {opportunities[0]['opportunity']}")
    
    if top_pain:
        recommendations.append(f"💡 Solve '{top_pain}' to differentiate from {top_pain_pct:.0f}% of competitors")
    
    if top_positive:
        recommendations.append(f"✅ Must match: '{top_positive}' (key to positive reviews)")
    
    return {
        'summary': summary,
        'top_pain_point': top_pain,
        'top_competitor_strength': top_positive,
        'feature_gaps': rare_features[:5],
        'recommendations': recommendations
    }

# === Main Function ===

def analyze_differentiation(
    keyword: str = None,
    asin: str = None,
    marketplace: str = 'US',
    depth: str = 'standard',
    feature_categories: List[str] = None
) -> dict:
    """Main differentiation analysis function"""
    
    if not keyword and not asin:
        return {'error': 'Provide keyword or asin'}
    
    is_us = marketplace.upper() == 'US'
    domain_code = None if is_us else MARKET_TO_DOMAIN.get(marketplace.upper(), 'co.uk')

    result = {
        'keyword': keyword,
        'marketplace': marketplace,
        'domain_code': domain_code,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v2.0.0'
    }
    
    # Step 1: Find competitors
    print(f"[1/4] Finding competitors for '{keyword}'...", file=sys.stderr)
    limit = 30 if depth == 'deep' else 20
    products = search_products(keyword, marketplace, limit)
    
    if not products:
        return {'error': 'No products found'}
    
    print(f"    ✓ Found {len(products)} products", file=sys.stderr)
    
    # Market data
    prices = [p.get('extractedPrice') or p.get('price', 0) for p in products if p.get('extractedPrice') or p.get('price')]
    ratings = [p.get('rating', 0) for p in products if p.get('rating')]
    reviews = [p.get('ratings', 0) or p.get('reviews', 0) for p in products]
    
    market_data = {
        'total_found': len(products),
        'analyzed': min(len(products), 5),
        'avg_price': round(statistics.mean(prices), 2) if prices else 0,
        'price_range': {'min': min(prices) if prices else 0, 'max': max(prices) if prices else 0},
        'avg_rating': round(statistics.mean(ratings), 2) if ratings else 0,
        'avg_reviews': round(statistics.mean(reviews)) if reviews else 0
    }
    result['market_data'] = market_data
    
    # Step 2: Analyze features from titles (with category-aware filtering)
    print(f"[2/4] Analyzing competitor features...", file=sys.stderr)
    if feature_categories:
        # Agent-provided feature list — use only these categories from FEATURE_KEYWORDS
        category_features = {k: v for k, v in FEATURE_KEYWORDS.items() if k in feature_categories}
        print(f"    Using agent-specified features: {', '.join(feature_categories)} ({len(category_features)} matched)", file=sys.stderr)
    else:
        # Fallback: auto-detect category from keyword + titles
        product_titles = [p.get('title', '') for p in products]
        detected_category = detect_product_category(keyword, product_titles)
        category_features = get_feature_keywords_for_category(detected_category)
        print(f"    Auto-detected category: {detected_category} ({len(category_features)} feature types)", file=sys.stderr)
    feature_analysis = analyze_competitor_features(products, category_features)
    print(f"    ✓ Found {len(feature_analysis)} feature categories", file=sys.stderr)
    
    result['feature_analysis'] = {
        'common_features': [
            {
                'feature': data['category'],
                'adoption': f"{data['percentage']}%",
                'status': data['status'],
                'count': data['count']
            }
            for data in sorted(feature_analysis.values(), key=lambda x: -x['percentage'])
        ]
    }
    
    # Step 3: Mine reviews for pain points and positive aspects (PARALLEL)
    print(f"[3/4] Mining review content from top competitors...", file=sys.stderr)
    
    all_reviews = []
    asins_to_analyze = [p.get('asin') for p in products[:5] if p.get('asin')]
    
    # Fetch reviews in parallel
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        print(f"    Fetching reviews for {len(asins_to_analyze)} ASINs in parallel...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(get_reviews_content, asin, domain_code, is_us): asin for asin in asins_to_analyze}
            for future in as_completed(futures):
                try:
                    review_result = future.result(timeout=15)
                    if review_result and review_result.get('reviews'):
                        all_reviews.extend(review_result['reviews'])
                except Exception:
                    pass
    except Exception:
        # Fallback to sequential
        for target_asin in asins_to_analyze:
            review_result = get_reviews_content(target_asin, domain_code, is_us=is_us)
            if review_result and review_result.get('reviews'):
                all_reviews.extend(review_result['reviews'])
                print(f"      ✓ Got {len(review_result['reviews'])} reviews", file=sys.stderr)
            else:
                print(f"      ⚠️ No reviews for {target_asin}", file=sys.stderr)
    
    print(f"    ✓ Total: {len(all_reviews)} reviews collected", file=sys.stderr)
    
    pain_points = {}
    positive_aspects = {}
    
    if all_reviews:
        pain_points, positive_aspects = extract_pain_points_from_reviews(all_reviews)
        
        result['review_analysis'] = {
            'reviews_analyzed': len(all_reviews),
            'pain_points': [
                {
                    'category': data['category'],
                    'frequency': f"{data['percentage']}%",
                    'severity': data['severity'],
                    'common_phrases': data.get('phrases', []),
                    'examples': data.get('examples', [])
                }
                for data in sorted(pain_points.values(), key=lambda x: -x['percentage'])[:6]
            ],
            'competitor_strengths': [
                {
                    'category': data['category'],
                    'frequency': f"{data['percentage']}%"
                }
                for data in sorted(positive_aspects.values(), key=lambda x: -x['percentage'])[:5]
            ]
        }
    else:
        result['review_analysis'] = {'note': 'No reviews retrieved'}
    
    # Step 4: Generate differentiation strategy
    print(f"[4/4] Generating differentiation strategy...", file=sys.stderr)
    
    opportunities = generate_differentiation_opportunities(feature_analysis, pain_points, positive_aspects)
    usps = generate_usp_recommendations(opportunities, pain_points, positive_aspects, market_data)
    action_plan = generate_action_plan(opportunities, usps, feature_analysis, pain_points)
    insights = generate_insights(feature_analysis, pain_points, positive_aspects, opportunities, market_data)
    
    result['differentiation_opportunities'] = opportunities[:6]
    result['usp_recommendations'] = usps
    result['action_plan'] = action_plan
    result['insights'] = insights
    
    # Top products reference
    result['top_competitors'] = [
        {
            'asin': p.get('asin'),
            'title': (p.get('title', '')[:60] + '...') if len(p.get('title', '')) > 60 else p.get('title'),
            'price': p.get('extractedPrice') or p.get('price'),
            'rating': p.get('rating'),
            'reviews': p.get('ratings') or p.get('reviews', 0)
        }
        for p in products[:8]
    ]
    
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
    
    keyword = result.get('keyword', 'Unknown')[:25]
    
    # Chart 1: Feature Adoption Matrix
    features = (result.get('feature_analysis') or {}).get('common_features', [])
    if features:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [f['feature'][:15] for f in features[:10]]
        values = [int(f['adoption'].replace('%', '')) for f in features[:10]]
        colors = [GREEN if v >= 80 else BLUE if v >= 50 else ORANGE if v >= 20 else RED for v in values]
        
        bars = ax.barh(names, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val, feat in zip(bars, values, features[:10]):
            status = feat['status'].upper()
            ax.text(val + 2, bar.get_y() + bar.get_height()/2,
                   f'{val}% ({status})', va='center', fontsize=9)
        
        ax.set_xlabel('Competitor Adoption %', fontsize=11)
        ax.set_title(f'FEATURE ADOPTION: {keyword.upper()}', fontweight='bold', fontsize=12, pad=15)
        ax.set_xlim(0, 110)
        ax.axvline(x=80, color=GREEN, linestyle='--', alpha=0.3)
        ax.axvline(x=50, color=BLUE, linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_feature_adoption.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Feature Adoption", file=sys.stderr)
    
    # Chart 2: Pain Points from Reviews
    pain_points = (result.get('review_analysis') or {}).get('pain_points', [])
    if pain_points:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [p['category'] for p in pain_points[:6]]
        values = [float(p['frequency'].replace('%', '')) for p in pain_points[:6]]
        severities = [p['severity'] for p in pain_points[:6]]
        colors = [RED if s == 'HIGH' else ORANGE if s == 'MEDIUM' else GRAY for s in severities]
        
        bars = ax.barh(names, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val, sev in zip(bars, values, severities):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2,
                   f'{val:.0f}% [{sev}]', va='center', fontsize=9)
        
        ax.set_xlabel('% of Negative Reviews', fontsize=11)
        ax.set_title(f'CUSTOMER PAIN POINTS: {keyword.upper()}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_pain_points.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Pain Points", file=sys.stderr)
    
    # Chart 3: Differentiation Opportunities
    opportunities = result.get('differentiation_opportunities', [])
    if opportunities:
        fig, ax = plt.subplots(figsize=(12, 5))
        
        priority_colors = {'CRITICAL': RED, 'HIGH': ORANGE, 'MEDIUM': BLUE, 'LOW': GRAY}
        
        for i, opp in enumerate(opportunities[:5]):
            color = priority_colors.get(opp.get('priority', 'LOW'), BLUE)
            ax.barh(i, 1, color=color, alpha=0.8, edgecolor='white', linewidth=2)
            
            # Opportunity name
            ax.text(0.02, i, opp['opportunity'][:35], va='center', fontsize=10, fontweight='bold', color='white')
            
            # Priority badge
            ax.text(0.98, i, opp['priority'], va='center', ha='right', fontsize=9,
                   color='white', fontweight='bold')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, min(5, len(opportunities)) - 0.5)
        ax.set_title(f'DIFFERENTIATION OPPORTUNITIES', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_opportunities.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Opportunities", file=sys.stderr)
    
    # Chart 4: Competitor Strengths (what they do well)
    strengths = (result.get('review_analysis') or {}).get('competitor_strengths', [])
    if strengths:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        names = [s['category'] for s in strengths[:6]]
        values = [float(s['frequency'].replace('%', '')) for s in strengths[:6]]
        
        bars = ax.bar(names, values, color=BLUE, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.0f}%', ha='center', fontsize=10)
        
        ax.set_ylabel('% of Positive Reviews', fontsize=11)
        ax.set_title(f'COMPETITOR STRENGTHS (Must Match)', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=30, ha='right')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_competitor_strengths.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Competitor Strengths", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Differentiation Advisor v2.0.0')
    parser.add_argument('params', help='JSON parameters: {"keyword": "yoga mat"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_differentiation(
        keyword=params.get('keyword'),
        asin=params.get('asin'),
        marketplace=params.get('market', params.get('marketplace', 'US')),
        depth=params.get('depth', 'standard'),
        feature_categories=params.get('feature_categories')
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
