#!/usr/bin/env python3
"""
Product Review Monitor v1.0.0

Monitor new reviews and analyze what customers are saying.
Answers: "What do new reviews say?"

Features:
- Fetch recent reviews sorted by date
- Sentiment analysis (positive/negative/neutral)
- Topic extraction from review content
- Alert on negative reviews
- Rating trend analysis

Usage:
    python3 review_monitor.py '{"asin": "B0BTYCRJSS"}'
    python3 review_monitor.py '{"asin": "B0BTYCRJSS", "market": "UK"}'
    python3 review_monitor.py '{"asin": "B0BTYCRJSS"}' --chart /tmp/charts
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from typing import Optional, List, Tuple
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

# Market to domain code mapping for non-US reviews API (/amazon/reviews/list)
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

# Sentiment keywords
NEGATIVE_KEYWORDS = [
    'terrible', 'awful', 'horrible', 'worst', 'waste', 'garbage', 'trash',
    'disappointed', 'disappointing', 'broke', 'broken', 'defective', 'faulty',
    'cheap', 'flimsy', 'poor quality', 'not working', "doesn't work", "don't buy",
    'returned', 'returning', 'refund', 'scam', 'fake', 'misleading',
    'useless', 'junk', 'regret', 'mistake', 'hate', 'avoid'
]

POSITIVE_KEYWORDS = [
    'excellent', 'amazing', 'perfect', 'love', 'great', 'fantastic', 'wonderful',
    'best', 'awesome', 'highly recommend', 'must buy', 'worth every',
    'impressed', 'exceeded', 'beautiful', 'quality', 'sturdy', 'durable',
    'comfortable', 'easy to use', 'works great', 'happy', 'satisfied'
]

# Topic keywords for categorization
TOPIC_KEYWORDS = {
    'quality': ['quality', 'well made', 'build', 'construction', 'material', 'sturdy', 'cheap', 'flimsy'],
    'price_value': ['price', 'value', 'worth', 'expensive', 'cheap', 'money', 'cost', 'affordable'],
    'shipping': ['shipping', 'delivery', 'arrived', 'package', 'packaging', 'box', 'damaged'],
    'functionality': ['works', 'working', 'function', 'features', 'performance', 'effective'],
    'durability': ['lasted', 'durable', 'broke', 'broken', 'fell apart', 'stopped working'],
    'size_fit': ['size', 'fit', 'fitting', 'small', 'big', 'large', 'tight', 'loose'],
    'appearance': ['looks', 'color', 'design', 'style', 'beautiful', 'ugly', 'appearance'],
    'ease_of_use': ['easy', 'simple', 'difficult', 'complicated', 'setup', 'instructions'],
    'customer_service': ['customer service', 'seller', 'response', 'support', 'return', 'refund']
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

def get_recent_reviews(
    asin: str,
    domain_code: str = 'co.uk',
    is_us: bool = False,
    count_per_star: int = 20
) -> dict:
    """Get recent reviews. US uses /amazon/usReviewsList, others use /amazon/reviews/list."""
    payload = {
        'asin': asin,
        'star1Num': count_per_star,
        'star2Num': count_per_star,
        'star3Num': count_per_star,
        'star4Num': count_per_star,
        'star5Num': count_per_star,
        'sortBy': 'recent',
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
            'product_rating': result.get('productRating'),
            'cost_token': result.get('costToken', 0)
        }
    elif result and 'errcode' in result:
        return {'error': result.get('errmsg', 'Unknown error')}
    return {'error': 'No response', 'reviews': []}

# === Analysis Functions ===

def parse_rating(rating_str) -> float:
    """Parse rating string to float"""
    if isinstance(rating_str, (int, float)):
        return float(rating_str)
    if isinstance(rating_str, str):
        match = re.search(r'(\d+\.?\d*)', rating_str)
        if match:
            return float(match.group(1))
    return 0.0

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse review date string"""
    if not date_str:
        return None
    
    # Try to extract date from various formats
    # "Reviewed in the United States on March 15, 2026"
    patterns = [
        r'(\d{1,2}\s+\w+\s+\d{4})',  # "15 March 2026"
        r'(\w+\s+\d{1,2},?\s+\d{4})',  # "March 15, 2026"
        r'(\d{4}-\d{2}-\d{2})',  # "2026-03-15"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            date_part = match.group(1)
            for fmt in ['%d %B %Y', '%B %d, %Y', '%B %d %Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_part, fmt)
                except ValueError:
                    continue
    
    return None

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analyze sentiment of review text"""
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return 'neutral', 0.5
    
    score = positive_count / total
    
    if score >= 0.7:
        return 'positive', score
    elif score <= 0.3:
        return 'negative', score
    else:
        return 'mixed', score

def extract_topics(text: str) -> List[str]:
    """Extract topics from review text"""
    text_lower = text.lower()
    topics = []
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            topics.append(topic)
    
    return topics

def classify_review(review: dict) -> dict:
    """Classify a single review"""
    rating = parse_rating(review.get('rating', 0))
    title = review.get('title', '')
    text = review.get('text', '')
    full_text = f"{title} {text}"
    
    # Sentiment
    sentiment, sentiment_score = analyze_sentiment(full_text)
    
    # Override sentiment based on rating
    if rating >= 4:
        sentiment = 'positive'
    elif rating <= 2:
        sentiment = 'negative'
    elif rating == 3:
        sentiment = 'mixed' if sentiment == 'neutral' else sentiment
    
    # Topics
    topics = extract_topics(full_text)
    
    # Parse date
    review_date = parse_date(review.get('date', ''))
    
    return {
        'rating': rating,
        'sentiment': sentiment,
        'sentiment_score': round(sentiment_score, 2),
        'topics': topics,
        'title': title,
        'text': text[:300] + '...' if len(text) > 300 else text,
        'full_text_length': len(text),
        'date': review.get('date'),
        'parsed_date': review_date.strftime('%Y-%m-%d') if review_date else None,
        'verified': review.get('verified', False),
        'vine': review.get('vine', False),
        'helpful_count': int(review.get('numberOfHelpful', 0) or 0),
        'has_media': bool(review.get('imageUrlList') or review.get('videoUrlList')),
        'user': review.get('userName', 'Anonymous')
    }

def analyze_reviews(reviews: List[dict]) -> dict:
    """Analyze all reviews"""
    if not reviews:
        return {'error': 'No reviews to analyze'}
    
    classified = [classify_review(r) for r in reviews]
    
    # Rating distribution
    ratings = [r['rating'] for r in classified]
    rating_dist = Counter(int(r) for r in ratings if r > 0)
    
    # Sentiment distribution
    sentiments = [r['sentiment'] for r in classified]
    sentiment_dist = Counter(sentiments)
    
    # Topic frequency
    all_topics = []
    for r in classified:
        all_topics.extend(r['topics'])
    topic_freq = Counter(all_topics)
    
    # Recent negative reviews (critical alerts)
    negative_reviews = [r for r in classified if r['sentiment'] == 'negative']
    
    # Verified vs non-verified
    verified_count = sum(1 for r in classified if r['verified'])
    
    # Average rating
    avg_rating = statistics.mean(ratings) if ratings else 0
    
    # Reviews with media
    media_count = sum(1 for r in classified if r['has_media'])
    
    return {
        'total_analyzed': len(classified),
        'rating_distribution': {f'{k}_star': v for k, v in sorted(rating_dist.items())},
        'average_rating': round(avg_rating, 2),
        'sentiment_distribution': dict(sentiment_dist),
        'topic_frequency': dict(topic_freq.most_common(10)),
        'verified_percentage': round(verified_count / len(classified) * 100, 1),
        'media_percentage': round(media_count / len(classified) * 100, 1),
        'negative_count': len(negative_reviews),
        'negative_percentage': round(len(negative_reviews) / len(classified) * 100, 1),
        'classified_reviews': classified
    }

def generate_alerts(analysis: dict, reviews: List[dict]) -> List[dict]:
    """Generate alerts based on review analysis"""
    alerts = []
    
    negative_pct = analysis.get('negative_percentage', 0)
    negative_count = analysis.get('negative_count', 0)
    avg_rating = analysis.get('average_rating', 5)
    
    # High negative percentage
    if negative_pct >= 30:
        alerts.append({
            'type': 'high_negative',
            'severity': 'HIGH',
            'icon': '🔴',
            'message': f'{negative_pct:.0f}% of recent reviews are negative ({negative_count} reviews)'
        })
    elif negative_pct >= 15:
        alerts.append({
            'type': 'moderate_negative',
            'severity': 'MEDIUM',
            'icon': '🟡',
            'message': f'{negative_pct:.0f}% negative reviews - monitor closely'
        })
    
    # Low average rating
    if avg_rating < 3.5:
        alerts.append({
            'type': 'low_rating',
            'severity': 'HIGH',
            'icon': '⭐',
            'message': f'Average rating is only {avg_rating:.1f} stars'
        })
    
    # Check for specific issues in negative reviews
    classified = analysis.get('classified_reviews', [])
    negative_reviews = [r for r in classified if r['sentiment'] == 'negative']
    
    if negative_reviews:
        # Topic-based alerts
        negative_topics = []
        for r in negative_reviews:
            negative_topics.extend(r['topics'])
        topic_counts = Counter(negative_topics)
        
        for topic, count in topic_counts.most_common(3):
            if count >= 3:
                alerts.append({
                    'type': 'topic_issue',
                    'severity': 'MEDIUM',
                    'icon': '⚠️',
                    'message': f'Multiple complaints about {topic.replace("_", " ")}: {count} mentions'
                })
        
        # Recent 1-star reviews
        one_star = [r for r in negative_reviews if r['rating'] <= 1.5]
        if one_star:
            alerts.append({
                'type': 'one_star',
                'severity': 'HIGH',
                'icon': '❌',
                'message': f'{len(one_star)} one-star review(s) detected',
                'examples': [r['title'][:50] for r in one_star[:3]]
            })
    
    # Sort by severity
    severity_order = {'HIGH': 0, 'MEDIUM': 1, 'INFO': 2}
    alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'INFO'), 2))
    
    return alerts

def generate_insights(analysis: dict, alerts: List[dict]) -> dict:
    """Generate narrative insights"""
    insights = []
    
    total = analysis.get('total_analyzed', 0)
    avg_rating = analysis.get('average_rating', 0)
    sentiment_dist = analysis.get('sentiment_distribution', {})
    topic_freq = analysis.get('topic_frequency', {})
    
    # Rating summary
    if avg_rating >= 4.5:
        insights.append(f"⭐ Excellent reviews: {avg_rating:.1f} average rating")
    elif avg_rating >= 4.0:
        insights.append(f"⭐ Good reviews: {avg_rating:.1f} average rating")
    elif avg_rating >= 3.5:
        insights.append(f"⚠️ Mixed reviews: {avg_rating:.1f} average rating")
    else:
        insights.append(f"🔴 Poor reviews: {avg_rating:.1f} average rating - needs attention")
    
    # Sentiment breakdown
    positive = sentiment_dist.get('positive', 0)
    negative = sentiment_dist.get('negative', 0)
    if total > 0:
        insights.append(f"📊 Sentiment: {positive} positive, {negative} negative out of {total}")
    
    # Top topics
    if topic_freq:
        top_topics = list(topic_freq.keys())[:3]
        insights.append(f"💬 Common topics: {', '.join(t.replace('_', ' ') for t in top_topics)}")
    
    # Verified review percentage
    verified_pct = analysis.get('verified_percentage', 0)
    insights.append(f"✅ {verified_pct:.0f}% verified purchases")
    
    # Alert summary
    high_alerts = [a for a in alerts if a.get('severity') == 'HIGH']
    if high_alerts:
        insights.append(f"🚨 {len(high_alerts)} high-priority issue(s) detected")
    
    return {
        'summary': f"Analyzed {total} recent reviews (avg {avg_rating:.1f}★)",
        'key_findings': insights,
        'alert_count': len(alerts),
        'status': '🔴 Issues Detected' if high_alerts else '🟢 Looking Good' if avg_rating >= 4 else '🟡 Monitor'
    }

def get_sample_reviews(classified: List[dict], count: int = 5) -> dict:
    """Get sample positive and negative reviews"""
    positive = [r for r in classified if r['sentiment'] == 'positive']
    negative = [r for r in classified if r['sentiment'] == 'negative']
    
    # Sort by helpful count
    positive.sort(key=lambda x: -(x.get('helpful_count', 0) or 0))
    negative.sort(key=lambda x: -(x.get('helpful_count', 0) or 0))
    
    return {
        'top_positive': [
            {
                'rating': r['rating'],
                'title': r['title'],
                'snippet': (r['text'] or '')[:200] + '...' if len(r['text'] or '') > 200 else (r['text'] or ''),
                'helpful': r['helpful_count'],
                'verified': r['verified']
            }
            for r in positive[:count]
        ],
        'recent_negative': [
            {
                'rating': r['rating'],
                'title': r['title'],
                'snippet': (r['text'] or '')[:200] + '...' if len(r['text'] or '') > 200 else (r['text'] or ''),
                'topics': r['topics'],
                'verified': r['verified']
            }
            for r in negative[:count]
        ]
    }

# === Main Function ===

def monitor_reviews(
    asin: str,
    market: str = 'US',
    count_per_star: int = 20
) -> dict:
    """Main review monitoring function"""
    
    is_us = market.upper() == 'US'
    domain_code = None if is_us else MARKET_TO_DOMAIN.get(market.upper(), 'co.uk')

    result = {
        'asin': asin,
        'marketplace': market.upper(),
        'domain_code': domain_code,
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0'
    }

    # Fetch reviews
    print(f"[1/3] Fetching recent reviews for {asin}...", file=sys.stderr)
    review_data = get_recent_reviews(asin, domain_code, is_us=is_us, count_per_star=count_per_star)
    
    if 'error' in review_data:
        result['error'] = review_data['error']
        return result
    
    reviews = review_data.get('reviews', [])
    result['total_reviews'] = review_data.get('total', len(reviews))
    result['product_rating'] = review_data.get('product_rating')
    result['cost_token'] = review_data.get('cost_token', 0)
    
    if not reviews:
        result['error'] = 'No reviews found'
        return result
    
    print(f"    ✓ Got {len(reviews)} reviews", file=sys.stderr)
    
    # Analyze reviews
    print(f"[2/3] Analyzing review content...", file=sys.stderr)
    analysis = analyze_reviews(reviews)
    
    result['analysis'] = {
        'total_analyzed': analysis['total_analyzed'],
        'average_rating': analysis['average_rating'],
        'rating_distribution': analysis['rating_distribution'],
        'sentiment_distribution': analysis['sentiment_distribution'],
        'topic_frequency': analysis['topic_frequency'],
        'verified_percentage': analysis['verified_percentage'],
        'media_percentage': analysis['media_percentage'],
        'negative_percentage': analysis['negative_percentage']
    }
    
    # Generate alerts
    print(f"[3/3] Generating alerts...", file=sys.stderr)
    alerts = generate_alerts(analysis, reviews)
    result['alerts'] = alerts
    
    # Generate insights
    insights = generate_insights(analysis, alerts)
    result['insights'] = insights
    
    # Sample reviews
    sample = get_sample_reviews(analysis['classified_reviews'])
    result['sample_reviews'] = sample
    
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
    
    analysis = result.get('analysis', {})
    asin = result.get('asin', 'Unknown')[:15]
    
    # Chart 1: Rating Distribution
    rating_dist = analysis.get('rating_distribution', {})
    if rating_dist:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        stars = ['1★', '2★', '3★', '4★', '5★']
        values = [rating_dist.get(f'{i}_star', 0) for i in range(1, 6)]
        colors = [RED, ORANGE, GRAY, GREEN, GREEN]
        
        bars = ax.bar(stars, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Reviews', fontsize=11)
        ax.set_title(f'RATING DISTRIBUTION: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_rating_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Rating Distribution", file=sys.stderr)
    
    # Chart 2: Sentiment Distribution
    sentiment_dist = analysis.get('sentiment_distribution', {})
    if sentiment_dist:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = list(sentiment_dist.keys())
        values = list(sentiment_dist.values())
        color_map = {'positive': GREEN, 'negative': RED, 'mixed': ORANGE, 'neutral': GRAY}
        colors = [color_map.get(l, GRAY) for l in labels]
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Reviews', fontsize=11)
        ax.set_title(f'SENTIMENT ANALYSIS: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_sentiment.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Sentiment", file=sys.stderr)
    
    # Chart 3: Topic Frequency
    topic_freq = analysis.get('topic_frequency', {})
    if topic_freq:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        topics = [t.replace('_', ' ').title() for t in list(topic_freq.keys())[:8]]
        values = list(topic_freq.values())[:8]
        
        bars = ax.barh(topics, values, color=BLUE, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=10)
        
        ax.set_xlabel('Mentions', fontsize=11)
        ax.set_title(f'COMMON TOPICS: {asin}', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/3_topics.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 3: Topics", file=sys.stderr)
    
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
        ax.set_title('REVIEW ALERTS', fontweight='bold', fontsize=12, pad=15)
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
    parser = argparse.ArgumentParser(description='Product Review Monitor v1.0.0')
    parser.add_argument('params', help='JSON parameters: {"asin": "B0XXXXXXXX"}')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    asin = params.get('asin')
    if not asin:
        print("Missing required parameter: asin", file=sys.stderr)
        sys.exit(1)
    
    result = monitor_reviews(
        asin=asin,
        market=params.get('market', 'US'),
        count_per_star=params.get('count_per_star', 20)
    )
    
    if args.chart and 'error' not in result:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        result['charts'] = generate_charts(result, args.chart) or []

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if 'error' in result:
        sys.exit(1)

if __name__ == '__main__':
    main()
