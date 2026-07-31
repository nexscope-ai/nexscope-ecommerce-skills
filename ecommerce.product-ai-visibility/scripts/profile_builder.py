"""Auto-generate profile files from structured product info."""
import json, re
from pathlib import Path
from datetime import date


def slugify(name):
    """Convert product name to directory-safe slug."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:40]


def build_profile(base_dir, product_info):
    """
    Generate profile directory with product.md, queries.csv, query_rules.md.
    
    product_info dict:
    {
        "name": str,
        "brand": str,
        "asin": str | None,
        "category": str,
        "price_range": str,
        "usps": [str],
        "channels": [str],
        "product_url": str | None,
        "competitors": [{"name": str, "price": str, "description": str}],
        "target_users": str,
        "core_scenario": str,
        "pain_points": str
    }
    """
    base = Path(base_dir)
    slug = slugify(product_info["name"])
    profile_dir = base / "profiles" / slug
    profile_dir.mkdir(parents=True, exist_ok=True)

    _write_product_md(profile_dir, product_info)
    _write_queries_csv(profile_dir, product_info)
    _write_query_rules(profile_dir, product_info)

    print(f"[profile] Created: profiles/{slug}/")
    return slug


def _write_product_md(profile_dir, info):
    lines = []
    lines.append("# Product Information")
    lines.append("")
    lines.append("## Product Overview")
    lines.append("")
    lines.append(f"- Name: {info['name']}")
    lines.append(f"- Brand: {info['brand']}")
    if info.get("asin"):
        lines.append(f"- ASIN: {info['asin']}")
    lines.append(f"- Category: {info['category']}")
    lines.append(f"- Price Range: {info['price_range']}")
    lines.append(f"- Key Selling Points: {', '.join(info.get('usps', []))}")
    lines.append(f"- Sales Channels: {', '.join(info.get('channels', ['Amazon']))}")
    if info.get("product_url"):
        lines.append(f"- Product Link: {info['product_url']}")
    lines.append("")
    lines.append("## Competitive Landscape")
    lines.append("")
    lines.append("### Direct Competitors")
    lines.append("")
    for comp in info.get("competitors", [])[:3]:
        lines.append(f"- {comp['name']}: {comp['price']} - {comp['description']}")
    lines.append("")
    lines.append("## Target Users")
    lines.append("")
    lines.append(f"- User Profile: {info.get('target_users', '')}")
    lines.append(f"- Core Scenario: {info.get('core_scenario', '')}")
    lines.append(f"- Pain Points: {info.get('pain_points', '')}")

    (profile_dir / "product.md").write_text("\n".join(lines), encoding="utf-8")


def _write_queries_csv(profile_dir, info):
    name = info["name"]
    brand = info["brand"]
    category = info["category"]
    comp1 = info["competitors"][0]["name"] if len(info.get("competitors", [])) > 0 else "competitor"
    comp2 = info["competitors"][1]["name"] if len(info.get("competitors", [])) > 1 else "alternative"

    price_str = info.get("price_range", "$100")
    # Remove parenthetical content (e.g. "(256GB)") that contains non-price numbers
    clean_price = re.sub(r"\([^)]*\)", "", price_str)
    # Remove currency symbols, commas, and common prefixes
    clean_price = re.sub(r"[,$£€¥]", "", clean_price)
    clean_price = re.sub(r"(?i)starting\s+from|from|approx", "", clean_price)
    prices = re.findall(r"(\d+)", clean_price)
    if prices:
        # Take the largest number as the top price
        top_price = max(int(p) for p in prices)
        # Budget = 1.1x top price, rounded UP to human-friendly number
        import math
        raw_budget = int(top_price * 1.1)
        if raw_budget >= 10000:
            budget = str(math.ceil(raw_budget / 1000) * 1000)   # >= $10000: ceil to 1000 ($15000, $20000)
        elif raw_budget >= 1000:
            budget = str(math.ceil(raw_budget / 100) * 100)     # $1000-9999: ceil to 100 ($1200, $1800)
        elif raw_budget >= 100:
            budget = str(math.ceil(raw_budget / 50) * 50)       # $100-999: ceil to 50 ($150, $200, $250)
        else:
            budget = str(math.ceil(raw_budget / 5) * 5)         # < $100: ceil to 5 ($25, $30, $65)
    else:
        budget = "100"

    scenario = info.get("core_scenario", "daily use")
    if len(scenario) > 40:
        scenario = scenario[:40].rsplit(" ", 1)[0]

    primary_channel = info.get("channels", [""])[0] if info.get("channels") else ""
    channel_suffix = f" on {primary_channel}" if primary_channel else ""

    # Extract use_case from first USP or scenario
    usps = info.get("usps", [])
    use_case = usps[0].lower() if usps else scenario
    if len(use_case) > 35:
        use_case = use_case[:35].rsplit(" ", 1)[0]

    # Extract pain point as a "how to" question
    pain = info.get("pain_points", "")
    if pain:
        solve_pain = f"keep {category} in best condition"
        pain_lower = pain.lower()
        if "fresh" in pain_lower or "stale" in pain_lower:
            solve_pain = f"keep {category.split()[0]} fresh longer"
        elif "break" in pain_lower or "durable" in pain_lower:
            solve_pain = f"find a durable {category}"
        elif "expensive" in pain_lower or "cost" in pain_lower:
            solve_pain = f"find affordable {category}"
        else:
            solve_pain = f"choose the best {category}"
    else:
        solve_pain = f"choose the right {category}"

    # Extract persona
    persona = info.get("target_users", "someone who needs it")
    if len(persona) > 30:
        persona = persona[:30].rsplit(" ", 1)[0]

    # Extract key feature from USPs
    key_feature = usps[1].lower() if len(usps) > 1 else (usps[0].lower() if usps else "best quality")
    if len(key_feature) > 30:
        key_feature = key_feature[:30].rsplit(" ", 1)[0]

    rows = []
    rows.append("id,query,category,user_persona,notes")
    # Discovery (3)
    rows.append(f'Q001,"best {category} {{{{year}}}} for {scenario}",discovery,shopper,discovery-broad')
    rows.append(f'Q002,"best {category} under ${budget} {{{{year}}}}",discovery,budget_shopper,discovery-budget')
    rows.append(f'Q003,"top rated {category}{channel_suffix} {{{{year}}}}",discovery,shopper,discovery-channel')
    # Comparison (3)
    rows.append(f'Q004,"{name} vs {comp1} which is better",comparison,researcher,comparison-two')
    rows.append(f'Q005,"{name} vs {comp1} vs {comp2} comparison {{{{year}}}}",comparison,researcher,comparison-multi')
    rows.append(f'Q006,"{comp1} vs {comp2} vs {name} which should I buy {{{{year}}}}",comparison,buyer,comparison-reverse')
    # Purchase advice (3)
    rows.append(f'Q007,"what should I buy for {scenario} under ${budget}",purchase_advice,shopper,purchase-budget')
    rows.append(f'Q008,"what {category} do experts recommend {{{{year}}}}",purchase_advice,quality_seeker,purchase-expert')
    rows.append(f'Q009,"best {category} to buy right now {{{{year}}}}",purchase_advice,impulse_buyer,purchase-now')
    # Alternatives (3)
    rows.append(f'Q010,"alternatives to {comp1} for {scenario}",alternatives,switcher,alternatives-comp1')
    rows.append(f'Q011,"cheaper alternatives to {name} that work just as well",alternatives,budget_switcher,alternatives-budget')
    rows.append(f'Q012,"products similar to {comp2} but better quality",alternatives,upgrader,alternatives-upgrade')
    # Trust validation (3)
    rows.append(f'Q013,"is {name} worth it {{{{year}}}}",trust_validation,potential_buyer,trust-worth')
    rows.append(f'Q014,"{name} review {{{{year}}}} does it really work",trust_validation,skeptic,trust-review')
    rows.append(f'Q015,"{name} pros and cons {{{{year}}}} should I buy it",trust_validation,decision_maker,trust-proscons')
    # Scenario (1)
    rows.append(f'Q016,"best {category} for {use_case} {{{{year}}}}",scenario,targeted_buyer,scenario-usecase')
    # Problem-solving (1)
    rows.append(f'Q017,"how to {solve_pain}",problem_solving,problem_solver,problem-pain')
    # Gift (1)
    rows.append(f'Q018,"best {category} gift for {persona} {{{{year}}}}",gift,gift_buyer,gift-persona')
    # Feature-specific (1)
    rows.append(f'Q019,"best {category} with {key_feature} {{{{year}}}}",feature,feature_seeker,feature-specific')
    # Social proof (1)
    rows.append(f'Q020,"what {category} does everyone recommend {{{{year}}}}",social_proof,follower,social-popular')

    (profile_dir / "queries.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write_query_rules(profile_dir, info):
    content = f"""# Query Rules: {info['name']}

## Category Distribution (20 queries total)
- discovery: 3 (Q001-Q003) — broad product search
- comparison: 3 (Q004-Q006) — product vs product
- purchase_advice: 3 (Q007-Q009) — what should I buy
- alternatives: 3 (Q010-Q012) — looking for alternatives
- trust_validation: 3 (Q013-Q015) — is it worth it
- scenario: 1 (Q016) — specific use-case search
- problem_solving: 1 (Q017) — pain point driven, no product decided yet
- gift: 1 (Q018) — buying for someone else
- feature: 1 (Q019) — searching by specific feature
- social_proof: 1 (Q020) — what does everyone recommend

## Time Rules
- All queries with year use {{{{year}}}} variable
- Auto-replaced with current year at runtime
"""
    (profile_dir / "query_rules.md").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python profile_builder.py <json_file>")
        print("  json_file: path to product_info JSON")
        sys.exit(1)

    json_path = sys.argv[1]
    product_info = json.loads(Path(json_path).read_text(encoding="utf-8"))

    base_dir = str(Path(__file__).parent.parent)
    slug = build_profile(base_dir, product_info)
    print(f"Profile slug: {slug}")
