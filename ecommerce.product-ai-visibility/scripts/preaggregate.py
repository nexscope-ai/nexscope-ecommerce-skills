"""Aggregate eval results into ecommerce GEO statistics."""
import json
from pathlib import Path
from collections import Counter, defaultdict


def build_preaggregate(run_dir):
    """Build preaggregate statistics from eval results."""
    eval_dir = Path(run_dir) / "eval"
    normalized_dir = Path(run_dir) / "normalized"

    evals = []
    for f in sorted(eval_dir.glob("*.json")):
        try:
            evals.append(json.loads(f.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, IOError):
            continue

    if not evals:
        return {"error": "No eval files found"}

    # Basic counts
    total = len(evals)
    engines = list(set(e.get("engine", "") for e in evals))
    queries = list(set(e.get("query_id", "") for e in evals))

    # Target product visibility
    mentioned_count = sum(1 for e in evals if e.get("mentioned"))
    mention_rate = mentioned_count / total if total else 0

    # Mention forms
    mention_forms = Counter(e.get("mention_form", "not_mentioned") for e in evals)

    # Recommendation strength
    rec_strengths = Counter(e.get("recommendation_strength", "not_mentioned") for e in evals)

    # Position stats (when mentioned)
    positions = [e.get("position") for e in evals if e.get("position") and isinstance(e.get("position"), int)]
    avg_position = sum(positions) / len(positions) if positions else None

    # Sentiment
    sentiments = Counter(e.get("sentiment", "n/a") for e in evals)

    # Per-engine breakdown
    engine_stats = {}
    for engine in engines:
        engine_evals = [e for e in evals if e.get("engine") == engine]
        engine_mentioned = sum(1 for e in engine_evals if e.get("mentioned"))
        engine_stats[engine] = {
            "total": len(engine_evals),
            "mentioned": engine_mentioned,
            "mention_rate": engine_mentioned / len(engine_evals) if engine_evals else 0,
            "avg_position": None,
            "mention_forms": dict(Counter(e.get("mention_form", "not_mentioned") for e in engine_evals)),
            "rec_strengths": dict(Counter(e.get("recommendation_strength", "not_mentioned") for e in engine_evals)),
        }
        ep = [e.get("position") for e in engine_evals if e.get("position") and isinstance(e.get("position"), int)]
        if ep:
            engine_stats[engine]["avg_position"] = sum(ep) / len(ep)

    # Competitor analysis
    competitor_counts = Counter()
    competitor_positions = defaultdict(list)
    competitor_strengths = defaultdict(list)
    for e in evals:
        for comp in e.get("competitors_mentioned", []):
            name = comp.get("name", "")
            if name:
                competitor_counts[name] += 1
                if comp.get("position"):
                    competitor_positions[name].append(comp["position"])
                competitor_strengths[name].append(comp.get("recommendation_strength", "mention_only"))

    top_competitors = []
    for name, count in competitor_counts.most_common(10):
        positions_list = competitor_positions.get(name, [])
        top_competitors.append({
            "name": name,
            "mention_count": count,
            "mention_rate": count / total,
            "avg_position": sum(positions_list) / len(positions_list) if positions_list else None,
            "primary_rate": competitor_strengths[name].count("primary") / len(competitor_strengths[name]) if competitor_strengths[name] else 0,
        })

    # Product recommendations aggregation
    all_products = []
    for e in evals:
        for pr in e.get("product_recommendations", []):
            all_products.append(pr)

    product_counts = Counter(p.get("product_name", "") for p in all_products if p.get("product_name"))
    brand_counts = Counter(p.get("brand", "") for p in all_products if p.get("brand"))
    merchant_counts = Counter(p.get("merchant_source", "") for p in all_products if p.get("merchant_source"))

    # Shopping signals
    signal_stats = {
        "has_price_info": sum(1 for e in evals if e.get("shopping_signals", {}).get("has_price_info")),
        "has_purchase_links": sum(1 for e in evals if e.get("shopping_signals", {}).get("has_purchase_links")),
        "has_comparison_table": sum(1 for e in evals if e.get("shopping_signals", {}).get("has_product_comparison_table")),
        "has_pros_cons": sum(1 for e in evals if e.get("shopping_signals", {}).get("has_pros_cons")),
    }

    buy_signals = Counter(e.get("shopping_signals", {}).get("buy_signal_strength", "none") for e in evals)

    all_merchants = []
    for e in evals:
        all_merchants.extend(e.get("shopping_signals", {}).get("merchants_mentioned", []))
    merchant_coverage = dict(Counter(all_merchants).most_common(10))

    # Citation/source analysis
    all_sources = {}
    for e in evals:
        sa = e.get("source_analysis", {})
        if isinstance(sa, dict):
            all_sources.update(sa)

    source_types = Counter(v.get("content_type", "other") for v in all_sources.values() if isinstance(v, dict))
    source_platforms = Counter(v.get("platform", "other") for v in all_sources.values() if isinstance(v, dict))
    official_sources = sum(1 for v in all_sources.values() if isinstance(v, dict) and v.get("is_official"))

    # Missed opportunities
    missed = [e.get("missed_opportunity") for e in evals if e.get("missed_opportunity")]

    return {
        "schema_version": "preaggregate.v1",
        "summary": {
            "total_evaluations": total,
            "engines": engines,
            "queries": queries,
            "mention_rate": round(mention_rate, 3),
            "mentioned_count": mentioned_count,
            "avg_position": round(avg_position, 1) if avg_position else None,
        },
        "mention_forms": dict(mention_forms),
        "recommendation_strengths": dict(rec_strengths),
        "sentiments": dict(sentiments),
        "engine_stats": engine_stats,
        "top_competitors": top_competitors,
        "product_recommendations": {
            "total_products_recommended": len(all_products),
            "unique_products": len(product_counts),
            "top_products": [{"name": n, "count": c} for n, c in product_counts.most_common(10)],
            "top_brands": [{"name": n, "count": c} for n, c in brand_counts.most_common(10)],
            "merchant_distribution": [{"name": n, "count": c} for n, c in merchant_counts.most_common(10)],
        },
        "shopping_signals": {
            "signal_rates": {k: v / total for k, v in signal_stats.items()},
            "buy_signal_distribution": dict(buy_signals),
            "merchant_coverage": merchant_coverage,
        },
        "source_analysis": {
            "total_sources": len(all_sources),
            "content_types": dict(source_types),
            "platforms": dict(source_platforms),
            "official_source_count": official_sources,
        },
        "missed_opportunities": missed[:10],
    }


def save_preaggregate(run_dir, preaggregate):
    """Save preaggregate to run directory."""
    path = Path(run_dir) / "preaggregate.json"
    path.write_text(json.dumps(preaggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
