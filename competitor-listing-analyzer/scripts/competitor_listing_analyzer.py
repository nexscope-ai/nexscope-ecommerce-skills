#!/usr/bin/env python3
"""
Competitor Listing Analyzer v1.0.0

Extract and analyze competitor Amazon listings structure.
Answers: "How do competitors write their listings?"

Data Sources:
- Amazon Product Detail API (via NexScope proxy)
- Amazon Search API (via NexScope proxy)

Usage:
    python3 competitor_listing_analyzer.py '{"asin": "B07RL88DD2"}'
    python3 competitor_listing_analyzer.py '{"keyword": "yoga mat"}'
    python3 competitor_listing_analyzer.py '{"asins": ["B07RL88DD2", "B08XYZ"]}' --chart /tmp/charts
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Optional, List, Dict
from urllib.request import Request, urlopen
from urllib.error import HTTPError
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

# Title structure patterns
TITLE_PATTERNS = {
    'brand_first': r'^([A-Z][a-zA-Z0-9]+)\s+',
    'size_pattern': r'(\d+(?:\.\d+)?\s*(?:inch|in|cm|mm|ft|pack|count|oz|lb|ml|L))',
    'color_pattern': r'\b(black|white|blue|red|green|gray|grey|pink|purple|orange|yellow|brown|silver|gold)\b',
    'material_pattern': r'\b(leather|cotton|silicone|rubber|foam|wood|metal|plastic|bamboo|cork|TPE|PVC|NBR)\b'
}

# Bullet feature types
FEATURE_TYPES = {
    'material': ['material', 'made of', 'constructed', 'fabric', 'leather', 'cotton', 'foam'],
    'size': ['size', 'dimension', 'inch', 'cm', 'length', 'width', 'thick', 'large', 'small'],
    'quality': ['premium', 'professional', 'durable', 'sturdy', 'heavy duty', 'quality'],
    'benefit': ['comfortable', 'easy', 'convenient', 'perfect for', 'ideal for', 'great for'],
    'use_case': ['home', 'gym', 'office', 'outdoor', 'travel', 'workout', 'yoga', 'fitness'],
    'warranty': ['warranty', 'guarantee', 'return', 'refund', 'replacement'],
    'package': ['includes', 'comes with', 'package', 'set of', 'bundle']
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

def get_product_details_batch(asins: List[str], marketplace: str = 'US') -> Dict[str, dict]:
    """Get detailed product information for multiple ASINs via batch API (up to 40)"""
    domain = {
        'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de',
        'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca',
        'IT': 'amazon.it', 'ES': 'amazon.es', 'AU': 'amazon.com.au'
    }.get(marketplace, 'amazon.com')
    
    results = {}
    
    # Batch in chunks of 40 (API limit)
    for i in range(0, len(asins), 40):
        batch = asins[i:i+40]
        asins_str = ','.join(batch)
        
        url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/amazon/product/detail"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {NEXSCOPE_API_KEY}'
        }
        
        payload = {
            'asins': asins_str,
            'amazonDomain': domain
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, headers=headers, method='POST')
            with urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode('utf-8'))

            # Unwrap nested response: {code, data: {errcode, products: [...]}}
            products_data = result
            if isinstance(result, dict) and result.get('code') == 0:
                products_data = result.get('data', result)
            elif isinstance(result, dict) and 'data' in result:
                products_data = result['data']

            product_list = []
            if isinstance(products_data, dict) and 'products' in products_data:
                product_list = products_data['products']
            elif isinstance(products_data, list):
                product_list = products_data

            for product in product_list:
                asin = product.get('asin')
                if asin:
                    results[asin] = parse_product_detail(product)
        except HTTPError as e:
            print(f"    API Error [batch {i//40+1}]: HTTP {e.code}", file=sys.stderr)
        except Exception as e:
            print(f"    API Error [batch {i//40+1}]: {e}", file=sys.stderr)
    
    return results

def parse_product_detail(product: dict) -> dict:
    """Parse product detail from API response"""
    # Real bullets are in aboutItemFivePoint; aboutItem contains key:value attributes
    bullets = product.get('aboutItemFivePoint', [])
    if not bullets:
        about_items = product.get('aboutItem', [])
        bullets = [item for item in about_items
                   if len(item) > 50 and not re.match(r'^[a-z_]+:\s', item)]
    
    # Note: API doesn't provide video detection - hasVideo is always unknown
    # To check for video, would need to scrape the actual Amazon page
    
    return {
        'asin': product.get('asin', ''),
        'title': product.get('title', ''),
        'brand': product.get('brand', ''),
        'price': product.get('price', product.get('extractedPrice', 0)),
        'rating': product.get('rating', 0),
        'reviews': product.get('ratings', 0),
        'featureBullets': bullets,
        'description': product.get('productDescription', product.get('description', '')),
        'images': product.get('productImageUrls', []),
        'hasVideo': None,  # API limitation - cannot detect video
        'hasAPlus': bool(product.get('productDescription')),
        'itemSpecifications': product.get('itemSpecifications', {}),
        'variants': product.get('variants', []),
        'boughtLastMonth': product.get('boughtLastMonthCount', 0),
        'badges': product.get('badges', '')
    }

def get_listing_from_search(product: dict) -> dict:
    """Convert search result to listing format for analysis"""
    return {
        'asin': product.get('asin', ''),
        'title': product.get('title', ''),
        'brand': product.get('brand', ''),
        'price': product.get('price', product.get('extractedPrice', 0)),
        'rating': product.get('rating', 0),
        'reviews': product.get('ratings', 0),
        'images': [{'url': product.get('imageUrl', '')}] if product.get('imageUrl') else [],
        'featureBullets': [],  # Not available in search
        'description': '',  # Not available in search
        'hasVideo': False,
        'hasAPlus': False,
        # Extra data from search
        'monthlySales': product.get('monthlySalesUnits', 0),
        'revenue': product.get('monthlySalesRevenue', '0'),
        'dimension': product.get('dimension', ''),
        'weight': product.get('weight', ''),
        'position': product.get('position', 0),
        'fulfillment': product.get('fulfillment', ''),
        'badges': product.get('badges', '')
    }

def search_products(keyword: str, marketplace: str = 'US', limit: int = 10) -> List[dict]:
    """Search for products by keyword"""
    result = api_call('/amazon/search', {
        'keyword': keyword,
        'amazonDomain': {'US': 'amazon.com', 'UK': 'amazon.co.uk', 'DE': 'amazon.de', 'FR': 'amazon.fr', 'JP': 'amazon.co.jp', 'CA': 'amazon.ca', 'IT': 'amazon.it', 'ES': 'amazon.es', 'MX': 'amazon.com.mx', 'AU': 'amazon.com.au'}.get(marketplace, 'amazon.com')
    })
    
    if result and 'products' in result:
        return result['products']
    elif result and 'data' in result:
        return result['data'] if isinstance(result['data'], list) else []
    return []

# === Analysis Functions ===

def analyze_title(title: str) -> dict:
    """Analyze listing title structure"""
    if not title:
        return {'error': 'No title provided'}
    
    # Basic metrics
    char_count = len(title)
    word_count = len(title.split())
    
    # Mobile truncation check
    mobile_cutoff = 80
    is_mobile_optimized = char_count <= 200
    mobile_preview = title[:mobile_cutoff] + '...' if char_count > mobile_cutoff else title
    
    # Detect structure components
    structure = []
    
    # Check for brand at start
    brand_match = re.match(TITLE_PATTERNS['brand_first'], title)
    if brand_match:
        structure.append('Brand')
    
    # Check for size
    if re.search(TITLE_PATTERNS['size_pattern'], title, re.IGNORECASE):
        structure.append('Size/Quantity')
    
    # Check for color
    if re.search(TITLE_PATTERNS['color_pattern'], title, re.IGNORECASE):
        structure.append('Color')
    
    # Check for material
    if re.search(TITLE_PATTERNS['material_pattern'], title, re.IGNORECASE):
        structure.append('Material')
    
    # Detect separators
    has_dash = ' - ' in title or ' – ' in title
    has_comma = ', ' in title
    has_pipe = ' | ' in title
    
    separator = 'dash' if has_dash else 'comma' if has_comma else 'pipe' if has_pipe else 'space'
    
    # Extract potential keywords (2-3 word phrases)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
    word_freq = Counter(words)
    keywords = [w for w, c in word_freq.most_common(10) if w not in {'the', 'and', 'for', 'with'}]
    
    # Score title (0-100)
    score = 50
    if char_count <= 200:
        score += 10
    if char_count >= 100:
        score += 10
    if brand_match:
        score += 10
    if 'Size/Quantity' in structure:
        score += 5
    if has_dash or has_pipe:
        score += 5
    if word_count >= 10:
        score += 5
    if word_count <= 25:
        score += 5
    
    return {
        'full_title': title,
        'char_count': char_count,
        'word_count': word_count,
        'mobile_preview': mobile_preview,
        'is_mobile_optimized': is_mobile_optimized,
        'structure': structure,
        'separator': separator,
        'keywords_detected': keywords[:8],
        'title_score': min(100, score)
    }

def analyze_bullet(bullet_text: str, index: int) -> dict:
    """Analyze a single bullet point"""
    if not bullet_text:
        return {'error': 'Empty bullet'}
    
    text = bullet_text.strip()
    char_count = len(text)
    word_count = len(text.split())
    
    # Check for emoji
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "]+", flags=re.UNICODE
    )
    has_emoji = bool(emoji_pattern.search(text))
    
    # Check for caps header
    caps_header_match = re.match(r'^([A-Z\s]{3,30})[-–:\s]', text)
    has_caps_header = bool(caps_header_match)
    caps_header = caps_header_match.group(1).strip() if caps_header_match else None
    
    # Detect feature type
    feature_type = 'general'
    text_lower = text.lower()
    for ftype, keywords in FEATURE_TYPES.items():
        if any(kw in text_lower for kw in keywords):
            feature_type = ftype
            break
    
    # Extract keywords
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
    stop_words = {'the', 'and', 'for', 'with', 'our', 'your', 'this', 'that', 'will', 'can'}
    keywords = [w for w in words if w not in stop_words][:5]
    
    # Detect pattern
    pattern = 'standard'
    if has_caps_header:
        pattern = 'CAPS_HEADER - description'
    elif text.startswith('✓') or text.startswith('✔') or text.startswith('•'):
        pattern = 'symbol_prefix'
    elif ':' in text[:50]:
        pattern = 'colon_split'
    
    # Score bullet (0-100)
    score = 50
    if 100 <= char_count <= 500:
        score += 15
    if has_caps_header:
        score += 10
    if feature_type != 'general':
        score += 10
    if word_count >= 20:
        score += 10
    if not has_emoji:  # Amazon generally prefers no emoji
        score += 5
    
    return {
        'bullet_number': index + 1,
        'text': text[:200] + '...' if len(text) > 200 else text,
        'full_text': text,
        'char_count': char_count,
        'word_count': word_count,
        'has_emoji': has_emoji,
        'has_caps_header': has_caps_header,
        'caps_header': caps_header,
        'feature_type': feature_type,
        'pattern': pattern,
        'keywords': keywords,
        'bullet_score': min(100, score)
    }

def analyze_bullets(bullets: List[str]) -> dict:
    """Analyze all bullet points"""
    if not bullets:
        return {'error': 'No bullets provided', 'bullet_count': 0}
    
    analyzed = [analyze_bullet(b, i) for i, b in enumerate(bullets) if b]
    
    # Aggregate stats
    total_chars = sum(b.get('char_count', 0) for b in analyzed)
    avg_chars = total_chars / len(analyzed) if analyzed else 0
    
    # Count feature types
    feature_counts = Counter(b.get('feature_type', 'general') for b in analyzed)
    
    # Detect dominant pattern
    patterns = [b.get('pattern', 'standard') for b in analyzed]
    pattern_counts = Counter(patterns)
    dominant_pattern = pattern_counts.most_common(1)[0][0] if pattern_counts else 'standard'
    
    # Has emoji anywhere
    has_any_emoji = any(b.get('has_emoji', False) for b in analyzed)
    
    # Average score
    avg_score = sum(b.get('bullet_score', 50) for b in analyzed) / len(analyzed) if analyzed else 0
    
    return {
        'bullet_count': len(analyzed),
        'bullets': analyzed,
        'total_chars': total_chars,
        'avg_chars_per_bullet': round(avg_chars),
        'feature_distribution': dict(feature_counts),
        'dominant_pattern': dominant_pattern,
        'has_emoji': has_any_emoji,
        'bullets_score': round(avg_score)
    }

def analyze_description(description: str, has_aplus: bool = False) -> dict:
    """Analyze product description"""
    if not description:
        return {
            'has_description': False,
            'has_aplus': has_aplus,
            'description_score': 30 if has_aplus else 0
        }
    
    text = description.strip()
    char_count = len(text)
    word_count = len(text.split())
    
    # Check for HTML (A+ Content indicator)
    has_html = bool(re.search(r'<[^>]+>', text))
    
    # Check for paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Check for CTA
    cta_patterns = ['buy now', 'order now', 'add to cart', 'click', 'shop now', 'get yours']
    has_cta = any(cta in text.lower() for cta in cta_patterns)
    
    # Extract keywords
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {'the', 'and', 'for', 'with', 'our', 'your', 'this', 'that', 'will', 'can', 'are', 'is'}
    word_freq = Counter(w for w in words if w not in stop_words)
    keywords = [w for w, c in word_freq.most_common(15)]
    
    # Detect structure
    structure = []
    if paragraph_count >= 3:
        structure.append('Multi-paragraph')
    if has_html:
        structure.append('HTML/A+')
    if has_cta:
        structure.append('Has CTA')
    if word_count > 200:
        structure.append('Long-form')
    
    # Score description (0-100)
    score = 40
    if char_count >= 500:
        score += 15
    if char_count >= 1000:
        score += 10
    if paragraph_count >= 2:
        score += 10
    if has_aplus:
        score += 15
    if has_cta:
        score += 5
    if not has_html or has_aplus:
        score += 5
    
    return {
        'has_description': True,
        'has_aplus': has_aplus,
        'char_count': char_count,
        'word_count': word_count,
        'paragraph_count': paragraph_count,
        'has_html': has_html,
        'has_cta': has_cta,
        'structure': structure,
        'keywords': keywords,
        'description_score': min(100, score)
    }

def analyze_images(images: List[dict], has_video = None) -> dict:
    """Analyze product images
    
    Note: has_video is None when API can't detect it (limitation)
    """
    if not images:
        return {
            'image_count': 0,
            'has_video': has_video,
            'video_status': 'unknown' if has_video is None else ('yes' if has_video else 'no'),
            'image_score': 0
        }
    
    image_count = len(images)
    
    # Try to categorize images (basic heuristics)
    # In reality, this would need image analysis
    infographic_estimate = max(0, image_count - 4) if image_count > 4 else 0
    lifestyle_estimate = min(2, image_count - 1) if image_count > 1 else 0
    
    # Score images (0-100) - don't penalize for unknown video status
    score = 30
    if image_count >= 5:
        score += 20
    if image_count >= 7:
        score += 15
    if has_video is True:
        score += 20
    elif has_video is None:
        score += 10  # Give partial credit when video status unknown
    if image_count >= 9:
        score += 15
    
    return {
        'image_count': image_count,
        'has_video': has_video,
        'video_status': 'unknown' if has_video is None else ('yes' if has_video else 'no'),
        'infographic_estimate': infographic_estimate,
        'lifestyle_estimate': lifestyle_estimate,
        'image_score': min(100, score)
    }

def analyze_listing(product_data: dict) -> dict:
    """Comprehensive listing analysis"""
    asin = product_data.get('asin', 'Unknown')
    
    # Extract components
    title = product_data.get('title', '')
    bullets = product_data.get('featureBullets', product_data.get('bullets', []))
    description = product_data.get('description', product_data.get('productDescription', ''))
    images = product_data.get('images', product_data.get('imageUrls', []))
    has_video = product_data.get('hasVideo', False)
    has_aplus = product_data.get('hasAPlus', product_data.get('hasEnhancedContent', False))
    
    # Handle image formats
    if isinstance(images, list) and images and isinstance(images[0], str):
        images = [{'url': img} for img in images]
    
    # Analyze each component
    title_analysis = analyze_title(title)
    bullet_analysis = analyze_bullets(bullets if isinstance(bullets, list) else [])
    description_analysis = analyze_description(description, has_aplus)
    image_analysis = analyze_images(images, has_video)
    
    # Calculate overall score
    weights = {
        'title': 0.25,
        'bullets': 0.30,
        'description': 0.20,
        'images': 0.25
    }
    
    overall_score = (
        title_analysis.get('title_score', 0) * weights['title'] +
        bullet_analysis.get('bullets_score', 0) * weights['bullets'] +
        description_analysis.get('description_score', 0) * weights['description'] +
        image_analysis.get('image_score', 0) * weights['images']
    )
    
    # Generate strengths and weaknesses
    strengths = []
    weaknesses = []
    
    # Title
    if title_analysis.get('title_score', 0) >= 70:
        strengths.append(f"Strong title ({title_analysis['char_count']} chars, well-structured)")
    elif title_analysis.get('char_count', 0) < 80:
        weaknesses.append("Title too short - missing keywords")
    
    # Bullets
    if bullet_analysis.get('bullet_count', 0) >= 5:
        strengths.append(f"Full {bullet_analysis['bullet_count']} bullets utilized")
    elif bullet_analysis.get('bullet_count', 0) < 5:
        weaknesses.append(f"Only {bullet_analysis.get('bullet_count', 0)} bullets - add more")
    
    if bullet_analysis.get('dominant_pattern') == 'CAPS_HEADER - description':
        strengths.append("Bullets use CAPS headers for scannability")
    
    # Description
    if description_analysis.get('has_aplus'):
        strengths.append("Has A+ Content (enhanced listing)")
    elif not description_analysis.get('has_description'):
        weaknesses.append("Missing product description")
    
    # Images
    if image_analysis.get('image_count', 0) >= 7:
        strengths.append(f"Excellent image count ({image_analysis['image_count']} images)")
    elif image_analysis.get('image_count', 0) < 5:
        weaknesses.append(f"Only {image_analysis.get('image_count', 0)} images - add more")
    
    video_status = image_analysis.get('video_status', 'unknown')
    if video_status == 'yes':
        strengths.append("Has product video")
    elif video_status == 'no':
        weaknesses.append("No video - consider adding")
    # Don't add weakness if video status is unknown (API limitation)
    
    return {
        'asin': asin,
        'brand': product_data.get('brand', 'Unknown'),
        'title_analysis': title_analysis,
        'bullet_analysis': bullet_analysis,
        'description_analysis': description_analysis,
        'image_analysis': image_analysis,
        'overall_score': round(overall_score),
        'strengths': strengths,
        'weaknesses': weaknesses,
        'price': product_data.get('price', 0),
        'rating': product_data.get('rating', 0),
        'reviews': product_data.get('reviews', product_data.get('reviewCount', 0))
    }

def compare_listings(analyses: List[dict]) -> dict:
    """Compare multiple listing analyses"""
    if len(analyses) < 2:
        return {'note': 'Need at least 2 listings to compare'}
    
    # Sort by overall score
    sorted_analyses = sorted(analyses, key=lambda x: x.get('overall_score', 0), reverse=True)
    
    # Find best practices from top performer
    top = sorted_analyses[0]
    
    # Average scores
    avg_title = sum((a.get('title_analysis') or {}).get('title_score', 0) for a in analyses) / len(analyses)
    avg_bullets = sum((a.get('bullet_analysis') or {}).get('bullets_score', 0) for a in analyses) / len(analyses)
    avg_description = sum((a.get('description_analysis') or {}).get('description_score', 0) for a in analyses) / len(analyses)
    avg_images = sum((a.get('image_analysis') or {}).get('image_score', 0) for a in analyses) / len(analyses)
    avg_overall = sum(a.get('overall_score', 0) for a in analyses) / len(analyses)
    
    # Common patterns
    patterns = [(a.get('bullet_analysis') or {}).get('dominant_pattern', 'standard') for a in analyses]
    common_pattern = Counter(patterns).most_common(1)[0][0]
    
    # Title lengths
    title_lengths = [(a.get('title_analysis') or {}).get('char_count', 0) for a in analyses]
    avg_title_length = sum(title_lengths) / len(title_lengths)
    
    # Image counts
    image_counts = [(a.get('image_analysis') or {}).get('image_count', 0) for a in analyses]
    avg_images_count = sum(image_counts) / len(image_counts)
    
    return {
        'listings_compared': len(analyses),
        'best_performer': {
            'asin': top.get('asin'),
            'score': top.get('overall_score'),
            'brand': top.get('brand')
        },
        'averages': {
            'title_score': round(avg_title),
            'bullets_score': round(avg_bullets),
            'description_score': round(avg_description),
            'images_score': round(avg_images),
            'overall_score': round(avg_overall),
            'title_length': round(avg_title_length),
            'image_count': round(avg_images_count, 1)
        },
        'common_bullet_pattern': common_pattern,
        'with_aplus': sum(1 for a in analyses if (a.get('description_analysis') or {}).get('has_aplus')),
        'video_detected': sum(1 for a in analyses if (a.get('image_analysis') or {}).get('has_video') is True),
        'ranking': [
            {'asin': a['asin'], 'score': a['overall_score'], 'brand': a.get('brand', '')}
            for a in sorted_analyses
        ]
    }

def generate_recommendations(analysis: dict, comparison: dict = None) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    title = analysis.get('title_analysis', {})
    bullets = analysis.get('bullet_analysis', {})
    description = analysis.get('description_analysis', {})
    images = analysis.get('image_analysis', {})
    
    # Title recommendations
    if title.get('char_count', 0) < 120:
        recommendations.append("📝 TITLE: Add more keywords - aim for 150-200 characters")
    if 'Brand' not in title.get('structure', []):
        recommendations.append("📝 TITLE: Start with brand name for recognition")
    if title.get('separator') == 'space':
        recommendations.append("📝 TITLE: Use dashes or pipes to separate concepts")
    
    # Bullet recommendations
    if bullets.get('bullet_count', 0) < 5:
        recommendations.append(f"📋 BULLETS: Add {5 - bullets.get('bullet_count', 0)} more bullets (5 total)")
    if bullets.get('dominant_pattern') == 'standard':
        recommendations.append("📋 BULLETS: Use CAPS HEADERS to improve scannability")
    if bullets.get('avg_chars_per_bullet', 0) < 200:
        recommendations.append("📋 BULLETS: Expand bullets with more detail and keywords")
    
    # Feature type diversity
    features = bullets.get('feature_distribution', {})
    if len(features) < 3:
        recommendations.append("📋 BULLETS: Cover more feature types (size, material, benefits, etc.)")
    
    # Description recommendations
    if not description.get('has_description'):
        recommendations.append("📄 DESCRIPTION: Add product description (2000 chars available)")
    elif not description.get('has_aplus'):
        recommendations.append("📄 DESCRIPTION: Consider A+ Content for Brand Registry")
    if description.get('has_description') and not description.get('has_cta'):
        recommendations.append("📄 DESCRIPTION: Add a call-to-action")
    
    # Image recommendations
    if images.get('image_count', 0) < 7:
        recommendations.append(f"🖼️ IMAGES: Add {7 - images.get('image_count', 0)} more images (aim for 7+)")
    if not images.get('has_video'):
        recommendations.append("🎥 VIDEO: Add a product video for higher conversion")
    
    # Comparison-based recommendations
    if comparison and comparison.get('best_performer'):
        best = comparison['best_performer']
        if analysis.get('asin') != best.get('asin'):
            score_diff = best.get('score', 0) - analysis.get('overall_score', 0)
            if score_diff > 10:
                recommendations.append(f"⭐ Study top performer {best.get('asin')} (score: {best.get('score')})")
    
    return recommendations

# === Main Function ===

def analyze_competitor_listings(asin: str = None, asins: List[str] = None, 
                                keyword: str = None, marketplace: str = 'US',
                                depth: str = 'standard') -> dict:
    """Main analysis function"""
    
    search_results = []  # Store search results for fallback
    target_asins = []
    
    # Determine which ASINs to analyze
    if asin:
        target_asins = [asin]
    elif asins:
        target_asins = asins
    elif keyword:
        print(f"[1/4] Searching for top competitors for '{keyword}'...", file=sys.stderr)
        search_results = search_products(keyword, marketplace, 10 if depth == 'deep' else 5)
        target_asins = [p.get('asin') for p in search_results if p.get('asin')]
        print(f"    ✓ Found {len(target_asins)} competitors", file=sys.stderr)
    else:
        return {'error': 'Provide asin, asins, or keyword'}
    
    if not target_asins:
        return {'error': 'No ASINs to analyze'}
    
    # Create lookup for search results
    search_lookup = {p.get('asin'): p for p in search_results}
    
    # Limit to reasonable number for analysis
    max_analyze = 10 if depth == 'deep' else 5
    target_asins = target_asins[:max_analyze]
    
    # Fetch product details in batch (much faster!)
    print(f"[2/4] Fetching {len(target_asins)} product details (batch API)...", file=sys.stderr)
    product_details = get_product_details_batch(target_asins, marketplace)
    print(f"    ✓ Got {len(product_details)} product details", file=sys.stderr)
    
    video_status = {}
    
    # Analyze each listing
    print("[3/5] Analyzing listings...", file=sys.stderr)
    analyses = []
    
    for i, target_asin in enumerate(target_asins):
        # Get product data from batch results or search fallback
        product_data = product_details.get(target_asin)
        
        if not product_data:
            if target_asin in search_lookup:
                product_data = get_listing_from_search(search_lookup[target_asin])
                print(f"    [{i+1}/{len(target_asins)}] {target_asin}: Using search data", file=sys.stderr)
            else:
                print(f"    [{i+1}/{len(target_asins)}] {target_asin}: ⚠️ No data", file=sys.stderr)
                continue
        else:
            print(f"    [{i+1}/{len(target_asins)}] {target_asin}: Full detail", file=sys.stderr)
        
        if target_asin in video_status:
            product_data['hasVideo'] = video_status[target_asin]
        
        analysis = analyze_listing(product_data)
        
        analysis['video_verified'] = target_asin in video_status
        
        # Add search metrics if available
        if target_asin in search_lookup:
            search_data = search_lookup[target_asin]
            analysis['search_metrics'] = {
                'position': search_data.get('position', 0),
                'monthly_sales': search_data.get('monthlySalesUnits', 0),
                'monthly_revenue': search_data.get('monthlySalesRevenue', '0'),
                'fulfillment': search_data.get('fulfillment', ''),
                'badges': search_data.get('badges', '')
            }
        
        analyses.append(analysis)
        print(f"        Score: {analysis.get('overall_score', 0)}", file=sys.stderr)
    
    if not analyses:
        return {'error': 'Could not analyze any listings'}
    
    # Compare if multiple
    print("[4/5] Comparing listings...", file=sys.stderr)
    comparison = compare_listings(analyses) if len(analyses) > 1 else None
    
    # Generate recommendations
    print("[5/5] Generating recommendations...", file=sys.stderr)
    primary_analysis = analyses[0]
    recommendations = generate_recommendations(primary_analysis, comparison)
    
    # Build result
    result = {
        'keyword': keyword,
        'marketplace': marketplace,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'listings_analyzed': len(analyses),
        'analyzed_listings': analyses,
        'recommendations': recommendations
    }
    
    if comparison:
        result['comparison'] = comparison
    
    # Summary insights
    result['insights'] = {
        'summary': f"Analyzed {len(analyses)} competitor listings",
        'top_score': max(a.get('overall_score', 0) for a in analyses),
        'avg_score': round(sum(a.get('overall_score', 0) for a in analyses) / len(analyses)),
        'key_patterns': [
            f"Most use {comparison.get('common_bullet_pattern', 'standard')} bullet pattern" if comparison else None,
            f"{comparison.get('with_aplus', 0)}/{len(analyses)} have A+ Content" if comparison else None,
        ]
    }
    # Filter None values and add notes
    result['insights']['key_patterns'] = [p for p in result['insights']['key_patterns'] if p]
    
    video_verified = sum(1 for a in analyses if a.get('video_verified', False))
    if video_verified > 0:
        video_count = sum(1 for a in analyses if (a.get('image_analysis') or {}).get('has_video') is True)
        result['insights']['key_patterns'].append(f"{video_count}/{len(analyses)} have verified video data")
        result['insights']['notes'] = [f'{video_verified}/{len(analyses)} listings have verified video data']
    else:
        result['insights']['notes'] = ['Video detection is limited to available API data']
    
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
    
    analyses = result.get('analyzed_listings', [])
    if not analyses:
        return []
    
    # Chart 1: Overall Score Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    asins = [a.get('asin', '')[:10] for a in analyses]
    scores = [a.get('overall_score', 0) for a in analyses]
    colors = [GREEN if s >= 70 else ORANGE if s >= 50 else get_color('hot') for s in scores]
    
    bars = ax.bar(asins, scores, color=colors, edgecolor='white', linewidth=2)
    
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               str(score), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Listing Score', fontsize=11)
    ax.set_xlabel('ASIN', fontsize=11)
    ax.set_title('COMPETITOR LISTING SCORES', fontweight='bold', fontsize=12, pad=15)
    ax.set_ylim(0, 100)
    ax.axhline(y=70, color=GREEN, linestyle='--', alpha=0.5, label='Good (70+)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/1_listing_scores.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Chart 1: Listing Scores", file=sys.stderr)
    
    # Chart 2: Score Breakdown for top listing
    top = analyses[0]
    fig, ax = plt.subplots(figsize=(8, 6))
    
    components = ['Title', 'Bullets', 'Description', 'Images']
    scores_breakdown = [
        (top.get('title_analysis') or {}).get('title_score', 0),
        (top.get('bullet_analysis') or {}).get('bullets_score', 0),
        (top.get('description_analysis') or {}).get('description_score', 0),
        (top.get('image_analysis') or {}).get('image_score', 0)
    ]
    colors_bd = [BLUE, GREEN, ORANGE, PURPLE]
    
    bars = ax.barh(components, scores_breakdown, color=colors_bd, edgecolor='white', linewidth=2)
    
    for bar, score in zip(bars, scores_breakdown):
        ax.text(score + 2, bar.get_y() + bar.get_height()/2,
               str(score), va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Score', fontsize=11)
    ax.set_title(f'SCORE BREAKDOWN: {top.get("asin", "")}', fontweight='bold', fontsize=12, pad=15)
    ax.set_xlim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/2_score_breakdown.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✓ Chart 2: Score Breakdown", file=sys.stderr)
    
    # Chart 3: Feature Distribution (if multiple listings)
    if len(analyses) >= 2:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Aggregate feature types
        all_features = {}
        for a in analyses:
            features = (a.get('bullet_analysis') or {}).get('feature_distribution', {})
            for f, count in features.items():
                all_features[f] = all_features.get(f, 0) + count
        
        if all_features:
            features = list(all_features.keys())
            counts = list(all_features.values())

            ax.bar(features, counts, color=BLUE, edgecolor='white', linewidth=2)
            ax.set_ylabel('Count Across Listings', fontsize=11)
            ax.set_title('BULLET FEATURE TYPES USED', fontweight='bold', fontsize=12, pad=15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.xticks(rotation=30, ha='right')

            plt.tight_layout()
            plt.savefig(f'{output_dir}/3_feature_types.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 3: Feature Types", file=sys.stderr)

    # Chart 4: Image Strategy Matrix
    if len(analyses) >= 1:
        # Collect image data per competitor
        img_asins = [a.get('asin', '')[:10] for a in analyses]
        img_counts = [(a.get('image_analysis') or {}).get('image_count', 0) for a in analyses]
        img_scores = [(a.get('image_analysis') or {}).get('image_score', 0) for a in analyses]
        has_aplus = [1 if (a.get('description_analysis') or {}).get('has_aplus') else 0 for a in analyses]

        x = np.arange(len(img_asins))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(max(8, len(img_asins) * 1.5), 6))

        bars1 = ax1.bar(x - width / 2, img_counts, width, color=BLUE, edgecolor='white',
                        linewidth=2, label='Image Count')
        bars2 = ax1.bar(x + width / 2, has_aplus, width, color=PURPLE, edgecolor='white',
                        linewidth=2, label='Has A+ (1=Yes)')

        for bar, val in zip(bars1, img_counts):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax2 = ax1.twinx()
        ax2.plot(x, img_scores, color=ORANGE, marker='o', linewidth=2,
                 markersize=7, label='Image Score')
        ax2.set_ylabel('Image Score (0–100)', fontsize=10, color=ORANGE)
        ax2.tick_params(axis='y', labelcolor=ORANGE)
        ax2.set_ylim(0, 110)

        ax1.set_xticks(x)
        ax1.set_xticklabels(img_asins, rotation=20, ha='right', fontsize=9)
        ax1.set_ylabel('Count', fontsize=11)
        ax1.set_title('IMAGE STRATEGY MATRIX', fontweight='bold', fontsize=12, pad=15)
        ax1.spines['top'].set_visible(False)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_image_strategy.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 4: Image Strategy Matrix", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

# === CLI Entry Point ===
def main():
    parser = argparse.ArgumentParser(description='Competitor Listing Analyzer')
    parser.add_argument('params', help='JSON parameters: {"asin": "B07RL88DD2"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_competitor_listings(
        asin=params.get('asin'),
        asins=params.get('asins'),
        keyword=params.get('keyword'),
        marketplace=params.get('marketplace', 'US'),
        depth=params.get('depth', 'standard')
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
