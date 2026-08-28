from datetime import date


def build_next_steps(mention_rate, primary_rate, top_competitors, product_name,
                     by_category, by_query, engine_stats, CATEGORY_LABELS, CATEGORY_ORDER, _pct):
    name = product_name or 'target product'
    top_comp = top_competitors[0]['name'] if top_competitors else 'competitors'
    top_comp2 = top_competitors[1]['name'] if len(top_competitors) > 1 else 'other brands'

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
            'Add Product + Review schema markup and Amazon/retailer purchase links.'))

    if primary_rate < 0.4:
        steps.append(('P0',
            'Get 2-3 editorial reviews naming ' + name + ' as top pick',
            'Pitch product samples to Serious Eats, The Spruce Eats, Food & Wine, or niche coffee blogs (The Coffee Folk, Bean Ground). '
            'Ask for a dedicated review or category roundup update. '
            'The review must include a sentence like "Our top pick is..." or "Best overall:", plus price and buy link.'))

    if weak_engine:
        steps.append(('P0',
            'Fix ' + weak_engine.title() + ' indexing (' + _pct(lowest_mr) + ' mention rate)',
            '(1) Submit sitemap to Google Search Console + Bing Webmaster Tools. '
            '(2) Verify product pages return 200 and are not blocked by robots.txt/noindex. '
            '(3) Ensure official page loads in under 3s with clean HTML text (not image-only content). '
            'Check that brand site + Amazon listing + 3 review articles appear in top 20 search results for your product name.'))

    steps.append(('P1',
        'Create a dedicated comparison page: ' + name + ' vs ' + top_comp,
        'Publish at /compare/ with: '
        '(1) side-by-side spec table (capacity, mechanism, materials, price, warranty), '
        '(2) use-case verdicts ("Best for daily use: ' + name + '"), '
        '(3) FAQ schema with 5+ Q&As about differences, '
        '(4) both products purchase links. Use the exact query as H1.'))

    steps.append(('P1',
        'Rewrite Amazon bullets with quotable factual claims',
        'Each bullet = one specific, extractable fact: '
        '(1) exact capacity in oz/grams/lbs, '
        '(2) patented mechanism name, '
        '(3) freshness claim with timeframe ("keeps beans fresh 50%% longer vs standard containers"), '
        '(4) award or best-seller text, '
        '(5) price-value statement. Mention full product name 3+ times. No vague marketing fluff.'))

    steps.append(('P1',
        'Seed authentic mentions in Reddit and coffee forums',
        'Find threads in r/coffee, r/espresso, r/BuyItForLife asking about coffee storage. '
        'Post genuine helpful answers mentioning ' + name + ' with specific usage details (capacity, freshness, price paid). '
        'Target threads less than 6 months old. Must be authentic, not promotional.'))

    steps.append(('P2',
        'Add FAQPage schema with 10+ questions on product page',
        'Add FAQ structured data covering: capacity, cleaning, warranty, vs competitors, use cases, material safety, price, where to buy, and freshness mechanism. '
        'Each answer: 2-3 sentences, factual, includes product name. Mirror the buyer questions from this evaluation.'))

    steps.append(('P2',
        'Update all existing review content to ' + current_year,
        'Contact bloggers with existing ' + name + ' articles. Ask them to update: '
        '(1) add ' + current_year + ' to title, '
        '(2) current retail price, '
        '(3) latest competitor comparisons. '
        'Offer affiliate commission increase or exclusive info. Target 3+ articles with current year in title.'))

    steps.append(('P2',
        'Send product to 3-5 coffee YouTubers for video review',
        'Target channels 10K-500K subs in the coffee niche. '
        'Video title must include product name + "review ' + current_year + '". '
        'Description should have specs, price, and purchase links. Ask reviewer to state a clear verdict.'))

    return steps
