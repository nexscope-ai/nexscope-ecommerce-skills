# Opportunity Patterns — Keyword Opportunity Finder v1.2

## 4 Key Opportunity Types

Auto-detect these high-value keyword patterns during analysis.

---

## 1. 🔥 Rising Trend

**Definition:** Search volume surged 50%+ in last 30 days, but ad placements not yet saturated.

### Detection Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| 30-day volume change | > +50% | JS Historical / Google Trends |
| 90-day volume change | > +20% | JS Historical |
| Sponsored density | < 40% of page 1 | Amazon Search |
| ABA rank change | Improved 10,000+ positions | ABA |

### Implementation

```python
def detect_rising_trend(keyword_data, search_results):
    """
    Detect keywords with explosive growth but low ad saturation
    """
    # Check 30-day surge
    volume_30d_change = keyword_data.get('monthly_trend', 0)
    
    # Check sponsored saturation
    page_1 = search_results[:16]
    sponsored_count = sum(1 for p in page_1 if p.get('sponsored', False))
    sponsored_pct = sponsored_count / len(page_1) * 100
    
    is_rising = (
        volume_30d_change >= 50 and
        sponsored_pct < 40
    )
    
    if is_rising:
        return {
            'type': 'rising_trend',
            'emoji': '🔥',
            'label': 'Rising Trend',
            'reason': f'+{volume_30d_change}% surge, only {sponsored_pct:.0f}% ads',
            'confidence': 'high' if volume_30d_change > 100 else 'medium',
            'action': 'Launch quickly before competitors notice',
            'urgency': 'HIGH - window closing fast'
        }
    return None
```

### Data Sources

| Source | Metric | Use |
|--------|--------|-----|
| JS Historical | Weekly volume data | Calculate 30-day change |
| Google Trends | Breakout detection | Confirm surge |
| Amazon Search | Sponsored flag | Ad saturation |
| ABA | Search rank change | Demand validation |

### Example

```
Keyword: "stanley tumbler dupe"
- 30-day change: +180%
- Sponsored density: 25%
- ABA rank: Jumped from #85,000 to #12,000
→ 🔥 Rising Trend - Act fast!
```

---

## 2. 💎 High-Conv Longtail

**Definition:** Medium search volume (2,000-5,000/month), but clicks concentrate on specific ASINs with extremely high conversion rates.

### Detection Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| Monthly volume | 2,000 - 5,000 | JS Keyword Research |
| Top 3 click share | > 50% | ABA |
| Top 3 conversion share | > 60% | ABA |
| Word count | 3+ words | Keyword structure |

### Implementation

```python
def detect_high_conv_longtail(keyword, volume, aba_data):
    """
    Detect long-tail keywords with concentrated high conversion
    """
    word_count = len(keyword.split())
    
    # Get ABA metrics
    top3_click = aba_data.get('top3_click_share', 0)
    top3_conv = aba_data.get('top3_conversion_share', 0)
    
    is_high_conv = (
        2000 <= volume <= 5000 and
        word_count >= 3 and
        top3_click > 50 and
        top3_conv > 60
    )
    
    if is_high_conv:
        # Calculate conversion efficiency
        conv_efficiency = top3_conv / top3_click if top3_click > 0 else 0
        
        return {
            'type': 'high_conv_longtail',
            'emoji': '💎',
            'label': 'High-Conv Longtail',
            'reason': f'{volume:,}/mo, {top3_conv:.0f}% conv concentration',
            'conv_efficiency': conv_efficiency,
            'confidence': 'high' if conv_efficiency > 1.2 else 'medium',
            'action': 'Study top 3 ASINs, replicate success factors',
            'strategy': 'Match or beat the winning product features'
        }
    return None
```

### Why This Matters

- **High intent:** Specific searches = ready to buy
- **Lower competition:** Most sellers chase volume
- **Better conversion:** Qualified traffic
- **Lower ACoS:** Less bidding competition

### Example

```
Keyword: "leak proof bento box for toddlers"
- Volume: 3,200/month
- Top 3 click share: 65%
- Top 3 conversion share: 78%
- Conv efficiency: 1.2x
→ 💎 High-Conv Longtail - Precision opportunity!
```

---

## 3. 🛡️ Under-optimized Main

**Definition:** High-volume main keyword where page 1-2 is filled with 3-star or lower products, or products with extremely poor images.

### Detection Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| Monthly volume | > 10,000 | JS Keyword Research |
| Products with rating < 3.5 | > 30% of page 1-2 | Amazon Search |
| Products with poor images | > 25% of page 1-2 | Amazon Search |
| Avg main image quality | Low (single angle, white bg only) | Visual analysis |

### Implementation

```python
def detect_underoptimized_main(keyword, volume, search_results):
    """
    Detect high-volume keywords with weak competition
    """
    if volume < 10000:
        return None
    
    # Analyze first 32 results (page 1-2)
    page_1_2 = search_results[:32]
    
    # Count weak competitors
    low_rating = sum(1 for p in page_1_2 if p.get('rating', 5) < 3.5)
    poor_images = sum(1 for p in page_1_2 if p.get('image_count', 7) < 4)
    low_reviews = sum(1 for p in page_1_2 if p.get('reviews', 1000) < 50)
    
    weak_pct = (low_rating + poor_images + low_reviews) / (len(page_1_2) * 3) * 100
    
    is_underoptimized = (
        low_rating / len(page_1_2) > 0.30 or
        poor_images / len(page_1_2) > 0.25
    )
    
    if is_underoptimized:
        return {
            'type': 'underoptimized_main',
            'emoji': '🛡️',
            'label': 'Under-optimized Main',
            'reason': f'{volume:,}/mo, {low_rating} low-rated, {poor_images} poor images',
            'weak_spots': {
                'low_rating_count': low_rating,
                'poor_images_count': poor_images,
                'low_reviews_count': low_reviews
            },
            'confidence': 'high' if weak_pct > 40 else 'medium',
            'action': 'Enter with superior listing quality',
            'strategy': 'Professional images + A+ content + video'
        }
    return None
```

### Weak Listing Indicators

| Indicator | Detection Method | Weight |
|-----------|------------------|--------|
| Rating < 3.5★ | `product.rating < 3.5` | High |
| Images < 4 | `product.image_count < 4` | High |
| No A+ content | Missing enhanced brand content | Medium |
| No video | No product video | Medium |
| Poor title | < 80 chars or keyword-stuffed | Low |

### Example

```
Keyword: "portable blender"
- Volume: 45,000/month
- Page 1-2 analysis:
  - 12/32 products rated < 3.5★
  - 9/32 have only 2-3 images
  - 15/32 have < 100 reviews
→ 🛡️ Under-optimized Main - Quality gap opportunity!
```

---

## 4. 📱 Social Signal

**Definition:** Frequently mentioned on TikTok/Reddit but not yet in Amazon's top 50,000 search rankings.

### Detection Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| TikTok mentions | Trending hashtag or viral video | Social listening |
| Reddit mentions | Multiple posts in relevant subs | Reddit search |
| Amazon search rank | > 50,000 (not yet discovered) | ABA |
| Google Trends spike | Recent 7-day surge | Google Trends |

### Implementation

```python
def detect_social_signal(keyword, aba_rank, social_data):
    """
    Detect keywords with social buzz but low Amazon presence
    """
    # Check social signals
    tiktok_mentions = social_data.get('tiktok_hashtag_views', 0)
    reddit_posts = social_data.get('reddit_post_count', 0)
    google_7d_change = social_data.get('google_trends_7d_change', 0)
    
    has_social_buzz = (
        tiktok_mentions > 1000000 or  # 1M+ hashtag views
        reddit_posts > 10 or          # 10+ posts in 30 days
        google_7d_change > 100        # 100%+ spike in 7 days
    )
    
    not_on_amazon = aba_rank is None or aba_rank > 50000
    
    if has_social_buzz and not_on_amazon:
        return {
            'type': 'social_signal',
            'emoji': '📱',
            'label': 'Social Signal',
            'reason': f'Viral on social, Amazon rank #{aba_rank or "unranked"}',
            'social_proof': {
                'tiktok_views': tiktok_mentions,
                'reddit_posts': reddit_posts,
                'google_spike': google_7d_change
            },
            'confidence': 'high' if tiktok_mentions > 10000000 else 'medium',
            'action': 'First-mover advantage - list before others',
            'urgency': 'HIGH - social trends move fast',
            'risk': 'Trend may be short-lived'
        }
    return None
```

### Social Signal Sources

| Platform | How to Check | Signal Strength |
|----------|--------------|-----------------|
| TikTok | Hashtag search, viral videos | 🔥 Strongest |
| Reddit | Subreddit search (r/BuyItForLife, etc.) | Strong |
| Google Trends | "Breakout" label | Strong |
| Pinterest | Rising pins | Medium |
| Instagram | Hashtag volume | Medium |

### Example

```
Keyword: "sunset lamp projector"
- TikTok: #sunsetlamp has 500M views
- Reddit: 25 posts in r/RoomDecor this month
- Google Trends: "Breakout" label
- ABA rank: #120,000 (barely on Amazon radar)
→ 📱 Social Signal - TikTok trending, Amazon opportunity!
```

---

## Combined Detection

```python
def detect_all_opportunities(keyword, data):
    """
    Run all opportunity pattern detections
    """
    opportunities = []
    
    # 1. Rising Trend
    rising = detect_rising_trend(
        data['keyword_data'], 
        data['search_results']
    )
    if rising:
        opportunities.append(rising)
    
    # 2. High-Conv Longtail
    high_conv = detect_high_conv_longtail(
        keyword,
        data['volume'],
        data['aba_data']
    )
    if high_conv:
        opportunities.append(high_conv)
    
    # 3. Under-optimized Main
    underopt = detect_underoptimized_main(
        keyword,
        data['volume'],
        data['search_results']
    )
    if underopt:
        opportunities.append(underopt)
    
    # 4. Social Signal
    social = detect_social_signal(
        keyword,
        data.get('aba_rank'),
        data.get('social_data', {})
    )
    if social:
        opportunities.append(social)
    
    return {
        'keyword': keyword,
        'opportunities': opportunities,
        'opportunity_count': len(opportunities),
        'best_opportunity': opportunities[0] if opportunities else None
    }
```

---

## Output Format

```markdown
### 🎯 Opportunity Patterns Detected

| Keyword | Pattern | Signal | Confidence |
|---------|---------|--------|------------|
| [keyword] | 🔥 Rising Trend | +85% surge, 30% ads | High |
| [keyword] | 💎 High-Conv Longtail | 72% conv share | High |
| [keyword] | 🛡️ Under-optimized | 40% weak listings | Medium |
| [keyword] | 📱 Social Signal | TikTok 50M views | High |

---

### 🔥 Rising Trend: [keyword]

**Signal:** +85% volume surge in 30 days
**Ad Saturation:** Only 30% (room to enter)
**Urgency:** ⚠️ HIGH - Window closing

**Action:**
1. Launch listing immediately
2. Start PPC before CPC rises
3. Build review base quickly
```

---

## Priority Scoring

When multiple opportunities detected, prioritize:

| Pattern | Priority | Reason |
|---------|----------|--------|
| 🔥 Rising Trend | 1st | Time-sensitive |
| 📱 Social Signal | 2nd | First-mover advantage |
| 💎 High-Conv Longtail | 3rd | Sustainable |
| 🛡️ Under-optimized Main | 4th | Requires execution |
