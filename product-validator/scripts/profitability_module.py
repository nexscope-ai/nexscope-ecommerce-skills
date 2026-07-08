"""
Profitability Calculator Module
Calculate FBA profitability metrics for Amazon products.

Can be used standalone or imported by Product Validator.

Usage standalone:
  from profitability_module import calculate_profitability, analyze_profitability

# --- Shared chart styling (from display-rules.md via chart_style.json) ---
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
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

  result = calculate_profitability(price=29.99, cost=10, category='home')
"""

# Amazon Referral Fee by Category (simplified)
REFERRAL_FEES = {
    'default': 0.15,
    'electronics': 0.08,
    'computers': 0.08,
    'camera': 0.08,
    'video_games': 0.15,
    'books': 0.15,
    'clothing': 0.17,
    'shoes': 0.15,
    'jewelry': 0.20,
    'watches': 0.15,
    'furniture': 0.15,
    'kitchen': 0.15,
    'home': 0.15,
    'garden': 0.15,
    'pet': 0.15,
    'beauty': 0.15,
    'health': 0.15,
    'baby': 0.15,
    'toys': 0.15,
    'sports': 0.15,
    'automotive': 0.12,
    'grocery': 0.15,
}

# FBA Fee Tiers (US, 2024 estimates)
FBA_SIZE_TIERS = [
    {'name': 'Small Standard', 'max_weight': 16, 'max_dim': [15, 12, 0.75], 'fee': 3.22},
    {'name': 'Large Standard', 'max_weight': 320, 'max_dim': [18, 14, 8], 'fee': 5.90},
    {'name': 'Small Oversize', 'max_weight': 1120, 'max_dim': [60, 30, 30], 'fee': 9.73},
    {'name': 'Medium Oversize', 'max_weight': 2240, 'max_dim': [108, 999, 999], 'fee': 19.05},
    {'name': 'Large Oversize', 'max_weight': 2240, 'max_dim': [108, 999, 999], 'fee': 89.98},
]


def get_referral_fee_rate(category):
    """Get Amazon referral fee rate by category"""
    if not category:
        return REFERRAL_FEES['default']
    
    category_lower = category.lower()
    for key, rate in REFERRAL_FEES.items():
        if key in category_lower:
            return rate
    return REFERRAL_FEES['default']


def estimate_fba_fee(weight_lb=None, dimensions=None, price=None):
    """Estimate FBA fulfillment fee
    
    Args:
        weight_lb: Product weight in pounds
        dimensions: [length, width, height] in inches
        price: Product price (for variable closing fee)
    
    Returns:
        dict with fee breakdown
    """
    if weight_lb is None:
        weight_lb = 1.0
    
    weight_oz = weight_lb * 16
    
    # Find applicable tier
    tier = FBA_SIZE_TIERS[1]  # Default: Large Standard
    for t in FBA_SIZE_TIERS:
        if weight_oz <= t['max_weight']:
            tier = t
            break
    
    base_fee = tier['fee']
    
    # Add weight handling for heavier items
    if weight_lb > 3:
        extra_weight = weight_lb - 3
        base_fee += extra_weight * 0.46  # Per additional lb
    
    return {
        'tier': tier['name'],
        'fulfillment_fee': round(base_fee, 2),
        'weight_lb': weight_lb
    }


def calculate_profitability(price, cost, category=None, weight_lb=None, 
                           shipping_to_amazon=None, prep_cost=None,
                           monthly_storage_fee=None):
    """Calculate FBA profitability metrics
    
    Args:
        price: Selling price on Amazon
        cost: Product cost (sourcing/wholesale)
        category: Product category for referral fee
        weight_lb: Product weight in pounds
        shipping_to_amazon: Inbound shipping cost per unit
        prep_cost: Prep/labeling cost per unit
        monthly_storage_fee: Monthly storage fee per unit
    
    Returns:
        dict with profitability breakdown
    """
    if price <= 0:
        return {'error': 'Invalid price'}
    
    # Set defaults
    if shipping_to_amazon is None:
        shipping_to_amazon = 0.50
    if prep_cost is None:
        prep_cost = 0.30
    if monthly_storage_fee is None:
        monthly_storage_fee = 0.50
    if cost is None:
        cost = 0
    
    # Calculate fees
    referral_rate = get_referral_fee_rate(category)
    referral_fee = price * referral_rate
    
    fba_result = estimate_fba_fee(weight_lb, price=price)
    fba_fee = fba_result['fulfillment_fee']
    
    # Total Amazon fees
    total_amazon_fees = referral_fee + fba_fee
    
    # Total costs
    total_cost = cost + shipping_to_amazon + prep_cost
    
    # Revenue and profit
    net_revenue = price - total_amazon_fees
    gross_profit = net_revenue - total_cost
    
    # Margins
    profit_margin = (gross_profit / price * 100) if price > 0 else 0
    roi = (gross_profit / total_cost * 100) if total_cost > 0 else 0
    
    # Break-even analysis
    break_even_price = total_cost + total_amazon_fees
    min_margin_price = total_cost / (1 - referral_rate - 0.10) if (1 - referral_rate - 0.10) > 0 else 0
    
    return {
        'selling_price': round(price, 2),
        'product_cost': round(cost, 2),
        'fees': {
            'referral_fee': round(referral_fee, 2),
            'referral_rate': f"{referral_rate*100:.0f}%",
            'fba_fee': round(fba_fee, 2),
            'fba_tier': fba_result['tier'],
            'total_amazon_fees': round(total_amazon_fees, 2)
        },
        'costs': {
            'product': round(cost, 2),
            'shipping_inbound': round(shipping_to_amazon, 2),
            'prep': round(prep_cost, 2),
            'total_landed_cost': round(total_cost, 2)
        },
        'profitability': {
            'net_revenue': round(net_revenue, 2),
            'gross_profit': round(gross_profit, 2),
            'profit_margin': round(profit_margin, 1),
            'roi': round(roi, 1)
        },
        'analysis': {
            'break_even_price': round(break_even_price, 2),
            'min_20pct_margin_price': round(min_margin_price, 2) if min_margin_price > 0 else None,
            'monthly_storage': round(monthly_storage_fee, 2),
            'profitable': gross_profit > 0,
            'good_margin': profit_margin >= 20,
            'good_roi': roi >= 100
        }
    }


def analyze_profitability(price, cost, category=None, weight_lb=None):
    """Generate profitability analysis with text summary"""
    result = calculate_profitability(price, cost, category, weight_lb)
    
    if 'error' in result:
        return result, "Unable to calculate profitability"
    
    lines = []
    prof = result['profitability']
    fees = result['fees']
    analysis = result['analysis']
    
    lines.append(f"**💰 Profitability Analysis**")
    lines.append(f"")
    lines.append(f"**Revenue Breakdown:**")
    lines.append(f"  Selling Price: ${result['selling_price']:.2f}")
    lines.append(f"  - Referral Fee ({fees['referral_rate']}): -${fees['referral_fee']:.2f}")
    lines.append(f"  - FBA Fee ({fees['fba_tier']}): -${fees['fba_fee']:.2f}")
    lines.append(f"  = Net Revenue: ${prof['net_revenue']:.2f}")
    lines.append(f"")
    lines.append(f"**Cost Breakdown:**")
    lines.append(f"  Product Cost: ${result['costs']['product']:.2f}")
    lines.append(f"  + Shipping to FBA: ${result['costs']['shipping_inbound']:.2f}")
    lines.append(f"  + Prep Cost: ${result['costs']['prep']:.2f}")
    lines.append(f"  = Total Landed: ${result['costs']['total_landed_cost']:.2f}")
    lines.append(f"")
    lines.append(f"**Profit:**")
    lines.append(f"  Gross Profit: ${prof['gross_profit']:.2f}")
    lines.append(f"  Profit Margin: {prof['profit_margin']:.1f}%")
    lines.append(f"  ROI: {prof['roi']:.0f}%")
    lines.append(f"")
    
    # Assessment
    if prof['profit_margin'] >= 30:
        lines.append(f"  ✅ Excellent margin (≥30%)")
    elif prof['profit_margin'] >= 20:
        lines.append(f"  ✅ Good margin (≥20%)")
    elif prof['profit_margin'] >= 10:
        lines.append(f"  🟡 Thin margin (10-20%) - watch for fee increases")
    elif prof['profit_margin'] > 0:
        lines.append(f"  ⚠️ Very thin margin (<10%) - risky")
    else:
        lines.append(f"  🔴 Negative margin - NOT profitable at this cost")
    
    if prof['roi'] >= 100:
        lines.append(f"  ✅ Good ROI (≥100%)")
    elif prof['roi'] >= 50:
        lines.append(f"  🟡 Moderate ROI (50-100%)")
    else:
        lines.append(f"  ⚠️ Low ROI (<50%) - capital intensive")
    
    lines.append(f"")
    lines.append(f"**Break-even:** ${analysis['break_even_price']:.2f}")
    
    return result, "\n".join(lines)


# Standalone test
if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        price = float(sys.argv[1])
        cost = float(sys.argv[2])
        category = sys.argv[3] if len(sys.argv) > 3 else None
        
        result, analysis_text = analyze_profitability(price, cost, category)
        print(analysis_text, file=sys.stderr)
        print("\n--- Raw Data ---", file=sys.stderr)
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
    else:
        print("Usage: python3 profitability_module.py <price> <cost> [category]", file=sys.stderr)
        print("Example: python3 profitability_module.py 29.99 10.00 electronics", file=sys.stderr)
