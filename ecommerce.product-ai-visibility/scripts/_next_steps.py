from datetime import date


def _infer_niche(product_name, category, channels):
    """Infer niche context for relevant subreddit/community/publication suggestions."""
    cat_lower = (category or "").lower()
    name_lower = (product_name or "").lower()
    combined = cat_lower + " " + name_lower

    if any(k in combined for k in ('phone', 'smartphone', 'iphone', 'galaxy', 'pixel')):
        return {
            "subreddits": 'r/smartphones, r/Android, r/iphone, r/PickAnAndroidForMe',
            "publications": "The Verge, Tom's Guide, MKBHD, GSMArena",
            "youtube_niche": 'tech review',
            "forum_topic": 'smartphone recommendations',
        }
    if any(k in combined for k in ('laptop', 'macbook', 'notebook', 'chromebook')):
        return {
            "subreddits": 'r/laptops, r/SuggestALaptop, r/macbookpro',
            "publications": 'The Verge, Laptop Mag, Notebookcheck, Dave2D',
            "youtube_niche": 'tech/laptop review',
            "forum_topic": 'laptop buying advice',
        }
    if any(k in combined for k in ('headphone', 'earbuds', 'earphone', 'airpods', 'audio')):
        return {
            "subreddits": 'r/headphones, r/HeadphoneAdvice, r/audiophile',
            "publications": 'Rtings, SoundGuys, What Hi-Fi, Crinacle',
            "youtube_niche": 'audio/headphone review',
            "forum_topic": 'headphone and audio gear recommendations',
        }
    if any(k in combined for k in ('hair', 'wig', 'extension', 'shampoo', 'conditioner')):
        return {
            "subreddits": 'r/Hair, r/Wigs, r/curlyhair, r/HaircareScience',
            "publications": 'Allure, Byrdie, NaturallyCurly, The Cut',
            "youtube_niche": 'hair/beauty',
            "forum_topic": 'hair care and styling',
        }
    if any(k in combined for k in ('skincare', 'beauty', 'makeup', 'cosmetic', 'serum', 'cream')):
        return {
            "subreddits": 'r/SkincareAddiction, r/MakeupAddiction, r/beauty',
            "publications": 'Allure, Byrdie, Cosmopolitan, Into The Gloss',
            "youtube_niche": 'beauty/skincare',
            "forum_topic": 'beauty and skincare recommendations',
        }

    if any(k in combined for k in ('coffee', 'espresso', 'grinder', 'canister', 'bean')):
        return {
            "subreddits": 'r/coffee, r/espresso, r/BuyItForLife',
            "publications": 'Serious Eats, The Spruce Eats, Bean Ground, The Coffee Folk',
            "youtube_niche": 'coffee',
            "forum_topic": 'coffee gear and storage',
        }
    if any(k in combined for k in ('kitchen', 'cookware', 'blender', 'mixer', 'knife', 'pan')):
        return {
            "subreddits": 'r/Cooking, r/BuyItForLife, r/cookware',
            "publications": "Serious Eats, America's Test Kitchen, Wirecutter",
            "youtube_niche": 'cooking/kitchen',
            "forum_topic": 'kitchen gear and cookware',
        }
    if any(k in combined for k in ('fitness', 'gym', 'workout', 'protein', 'supplement')):
        return {
            "subreddits": 'r/Fitness, r/homegym, r/supplements',
            "publications": "GQ, Men's Health, Wirecutter, Garage Gym Reviews",
            "youtube_niche": 'fitness/supplement',
            "forum_topic": 'fitness equipment and supplements',
        }
    if any(k in combined for k in ('watch', 'smartwatch', 'wearable')):
        return {
            "subreddits": 'r/Watches, r/AppleWatch, r/WearOS',
            "publications": 'Hodinkee, Wareable, The Verge',
            "youtube_niche": 'watch/wearable tech',
            "forum_topic": 'watch and wearable recommendations',
        }
    if any(k in combined for k in ('camera', 'lens', 'photography', 'mirrorless', 'dslr')):
        return {
            "subreddits": 'r/photography, r/Cameras, r/AskPhotography',
            "publications": 'DPReview, PetaPixel, Fstoppers',
            "youtube_niche": 'photography/camera',
            "forum_topic": 'camera and photography gear',
        }
    if any(k in combined for k in ('gaming', 'console', 'controller', 'gpu', 'graphics')):
        return {
            "subreddits": 'r/gaming, r/buildapc, r/pcgaming, r/PS5, r/XboxSeriesX',
            "publications": "IGN, Digital Foundry, Tom's Hardware, GameSpot",
            "youtube_niche": 'gaming/tech',
            "forum_topic": 'gaming hardware recommendations',
        }
    if any(k in combined for k in ('tablet', 'ipad')):
        return {
            "subreddits": 'r/tablets, r/ipad, r/GalaxyTab',
            "publications": "The Verge, Tom's Guide, 9to5Mac",
            "youtube_niche": 'tech/tablet review',
            "forum_topic": 'tablet recommendations and comparisons',
        }
    # Fallback: generic product
    return {
        "subreddits": "r/BuyItForLife, r/ProductReviews, relevant category subreddits",
        "publications": "Wirecutter, relevant category review sites",
        "youtube_niche": "product review",
        "forum_topic": "product recommendations in this category",
    }


def build_next_steps(mention_rate, primary_rate, top_competitors, product_name,
                     by_category, by_query, engine_stats, CATEGORY_LABELS, CATEGORY_ORDER, _pct,
                     category="", channels=None):
    name = product_name or 'target product'
    top_comp = top_competitors[0]['name'] if top_competitors else 'competitors'
    top_comp2 = top_competitors[1]['name'] if len(top_competitors) > 1 else 'other brands'
    niche = _infer_niche(product_name, category, channels)

    weak_cats = []
    for cat in CATEGORY_ORDER:
        qids = by_category.get(cat, [])
        misses = 0
        for qid in qids:
            engines_data = by_query.get(qid, {})
            misses += sum(1 for d in engines_data.values() if not (d.get('eval') or {}).get('mentioned'))
        if misses > 0:
            weak_cats.append((cat, misses))
    weak_cats.sort(key=lambda x: -x[1])

    weak_engine = None
    lowest_mr = 1.0
    for eng, stats in engine_stats.items():
        mr = stats.get('mention_rate', 1.0)
        if mr < lowest_mr:
            lowest_mr = mr
            weak_engine = eng

    current_year = str(date.today().year)
    steps = []

    if weak_cats:
        weak_label = CATEGORY_LABELS.get(weak_cats[0][0], weak_cats[0][0])
        steps.append(('P0',
            'Publish a ' + current_year + ' buyer guide targeting ' + weak_label.lower() + ' queries',
            'Write a 2000+ word article titled "Best [Category] ' + current_year + ': Expert Tested" on your brand blog or a partnered review site. '
            'Place ' + name + ' as the #1 pick with a clear verdict paragraph. '
            'Include a comparison table (specs/price/pros-cons) vs ' + top_comp + ' and ' + top_comp2 + '. '
            'Add Product + Review schema markup and retailer purchase links.'))

    if primary_rate < 0.4:
        steps.append(('P0',
            'Get 2-3 editorial reviews naming ' + name + ' as top pick',
            'Pitch product samples to ' + niche["publications"] + '. '
            'Ask for a dedicated review or category roundup update. '
            'The review must include a sentence like "Our top pick is..." or "Best overall:", plus price and buy link.'))

    if weak_engine:
        steps.append(('P0',
            'Fix ' + weak_engine.title() + ' indexing (' + _pct(lowest_mr) + ' mention rate)',
            '(1) Submit sitemap to Google Search Console + Bing Webmaster Tools. '
            '(2) Verify product pages return 200 and are not blocked by robots.txt/noindex. '
            '(3) Ensure official page loads in under 3s with clean HTML text (not image-only content). '
            'Check that brand site + retailer listing + 3 review articles appear in top 20 search results for your product name.'))

    steps.append(('P1',
        'Create a dedicated comparison page: ' + name + ' vs ' + top_comp,
        'Publish at /compare/ with: '
        '(1) side-by-side spec table (key differentiating specs, price, warranty), '
        '(2) use-case verdicts ("Best for [scenario]: ' + name + '"), '
        '(3) FAQ schema with 5+ Q&As about differences, '
        '(4) purchase links for both products. Use the exact comparison query as H1.'))

    steps.append(('P1',
        'Rewrite product listing bullets with quotable factual claims',
        'Each bullet = one specific, extractable fact: '
        '(1) exact key specification with numbers, '
        '(2) unique feature or technology name, '
        '(3) quantified performance claim with comparison, '
        '(4) awards, certifications, or best-seller ranking, '
        '(5) price-value statement. Mention full product name 3+ times. No vague marketing fluff.'))

    steps.append(('P1',
        'Seed authentic mentions in Reddit and community forums',
        'Find threads in ' + niche["subreddits"] + ' asking about ' + niche["forum_topic"] + '. '
        'Post genuine helpful answers mentioning ' + name + ' with specific usage details. '
        'Target threads less than 6 months old. Must be authentic, not promotional.'))

    steps.append(('P2',
        'Add FAQPage schema with 10+ questions on product page',
        'Add FAQ structured data covering: key specs, maintenance, warranty, vs competitors, use cases, materials, price, where to buy, and unique selling points. '
        'Each answer: 2-3 sentences, factual, includes product name. Mirror the buyer questions from this evaluation.'))

    steps.append(('P2',
        'Update all existing review content to ' + current_year,
        'Contact bloggers with existing ' + name + ' articles. Ask them to update: '
        '(1) add ' + current_year + ' to title, '
        '(2) current retail price, '
        '(3) latest competitor comparisons. '
        'Offer affiliate commission increase or exclusive info. Target 3+ articles with current year in title.'))

    steps.append(('P2',
        'Send product to 3-5 ' + niche["youtube_niche"] + ' YouTubers for video review',
        'Target channels 10K-500K subs in the ' + niche["youtube_niche"] + ' niche. '
        'Video title must include product name + "review ' + current_year + '". '
        'Description should have specs, price, and purchase links. Ask reviewer to state a clear verdict.'))

    return steps
