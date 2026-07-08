"""
Seasonality Analysis Module
Detect and analyze seasonal patterns in Amazon product categories.

Can be used standalone or imported by Product Validator.
"""

import os
import sys
from datetime import datetime

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


# === Seasonality Configuration ===
SEASONAL_CATEGORIES = {
    # Summer products
    'outdoor': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'pool': {'peak_months': [6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'patio': {'peak_months': [4, 5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'garden': {'peak_months': [3, 4, 5, 6], 'pattern': 'spring', 'volatility': 'high'},
    'grill': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'sunscreen': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'sun block': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'tanning': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'beach': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'swim': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    
    # Winter products
    'heater': {'peak_months': [10, 11, 12, 1], 'pattern': 'winter', 'volatility': 'high'},
    'snow': {'peak_months': [11, 12, 1, 2], 'pattern': 'winter', 'volatility': 'high'},
    
    # Summer cooling
    'fan': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    'air conditioner': {'peak_months': [5, 6, 7, 8], 'pattern': 'summer', 'volatility': 'high'},
    
    # Holiday (Q4)
    'christmas': {'peak_months': [11, 12], 'pattern': 'holiday', 'volatility': 'extreme'},
    'toys': {'peak_months': [11, 12], 'pattern': 'holiday', 'volatility': 'high'},
    'gift': {'peak_months': [11, 12], 'pattern': 'holiday', 'volatility': 'medium'},
    
    # Event-based
    'halloween': {'peak_months': [9, 10], 'pattern': 'event', 'volatility': 'extreme'},
    'valentine': {'peak_months': [1, 2], 'pattern': 'event', 'volatility': 'extreme'},
    'easter': {'peak_months': [3, 4], 'pattern': 'event', 'volatility': 'extreme'},
    
    # New Year
    'fitness': {'peak_months': [1, 2, 3], 'pattern': 'newyear', 'volatility': 'medium'},
    'gym': {'peak_months': [1, 2, 3], 'pattern': 'newyear', 'volatility': 'medium'},
    
    # Back to school
    'school': {'peak_months': [7, 8, 9], 'pattern': 'backtoschool', 'volatility': 'high'},
    'backpack': {'peak_months': [7, 8, 9], 'pattern': 'backtoschool', 'volatility': 'high'},
    
    # Tax season
    'tax': {'peak_months': [1, 2, 3, 4], 'pattern': 'taxseason', 'volatility': 'medium'},
    
    # Low/stable seasonality
    'pet': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'dog': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'cat': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'baby': {'peak_months': [], 'pattern': 'stable', 'volatility': 'low'},
    'kitchen': {'peak_months': [11, 12], 'pattern': 'slight_holiday', 'volatility': 'low'},
    'phone': {'peak_months': [11, 12], 'pattern': 'slight_holiday', 'volatility': 'low'},
    'headphone': {'peak_months': [11, 12], 'pattern': 'slight_holiday', 'volatility': 'low'},
}


def detect_category_seasonality(category_tree, title):
    """Detect seasonality based on category and title keywords"""
    text = ((category_tree or '') + ' ' + (title or '')).lower()
    
    for keyword, config in SEASONAL_CATEGORIES.items():
        if keyword in text:
            return config
    
    return {'peak_months': [], 'pattern': 'unknown', 'volatility': 'unknown'}


def get_seasonal_position(peak_months, current_month=None):
    """Determine where we are in the seasonal cycle
    
    Returns: 'peak', 'rising', 'falling', 'off', or 'stable'
    """
    if current_month is None:
        current_month = datetime.now().month
    
    if not peak_months:
        return 'stable'
    
    if current_month in peak_months:
        return 'peak'
    
    # Check if approaching peak (within 2 months)
    for pm in peak_months:
        months_until = (pm - current_month) % 12
        if 1 <= months_until <= 2:
            return 'rising'
    
    # Check if just past peak (within 2 months)
    for pm in peak_months:
        months_since = (current_month - pm) % 12
        if 1 <= months_since <= 2:
            return 'falling'
    
    return 'off'


def get_bsr_trend(bsr_history):
    """Determine BSR trend direction from history
    
    Returns: 'improving', 'declining', 'stable', or 'unknown'
    """
    if not bsr_history or len(bsr_history) < 2:
        return 'unknown'
    
    first = bsr_history[0]
    last = bsr_history[-1]
    
    if first <= 0:
        return 'unknown'
    
    change = (first - last) / first * 100  # Positive = improving (BSR decreased)
    
    if change > 15:
        return 'improving'
    elif change < -15:
        return 'declining'
    return 'stable'


def calculate_seasonality_modifier(seasonal_config, position, bsr_trend):
    """Calculate score modifier based on seasonality
    
    Returns: modifier value (-10 to +10) and list of flags
    """
    modifier = 0
    flags = []
    
    pattern = seasonal_config.get('pattern', 'unknown')
    volatility = seasonal_config.get('volatility', 'unknown')
    
    if pattern == 'stable' or pattern == 'unknown':
        return 0, []
    
    # Extreme seasonality warning
    if volatility == 'extreme':
        flags.append({
            'flag': 'extreme_seasonality',
            'severity': 'warning',
            'detail': f'Extreme seasonal product ({pattern}) - limited selling window'
        })
        modifier -= 5
    
    # Position-based modifiers
    if position == 'off':
        if bsr_trend == 'improving':
            # Off-season with improving BSR = genuine demand
            modifier += 10
            flags.append({
                'flag': 'off_season_strength',
                'severity': 'positive',
                'detail': 'BSR improving in off-season indicates genuine demand'
            })
        elif bsr_trend == 'stable':
            modifier += 5
    
    elif position == 'peak':
        if bsr_trend == 'declining':
            # Declining during peak = serious concern
            modifier -= 5
            flags.append({
                'flag': 'peak_decline',
                'severity': 'critical',
                'detail': 'BSR declining during peak season - serious concern'
            })
        else:
            flags.append({
                'flag': 'peak_season',
                'severity': 'warning',
                'detail': 'Currently in peak season - data may be inflated'
            })
    
    elif position == 'rising':
        modifier -= 3
        flags.append({
            'flag': 'approaching_peak',
            'severity': 'warning',
            'detail': 'Approaching peak season - recent improvement may be seasonal'
        })
    
    elif position == 'falling':
        if bsr_trend == 'stable':
            modifier += 5
            flags.append({
                'flag': 'post_peak_stable',
                'severity': 'positive',
                'detail': 'Stable BSR post-peak indicates sustained demand'
            })
        else:
            flags.append({
                'flag': 'entering_offseason',
                'severity': 'warning',
                'detail': 'Entering off-season - expect demand decrease'
            })
    
    return modifier, flags


def analyze_seasonality(category_tree, title, bsr_history):
    """Complete seasonality analysis
    
    Returns dict with:
        - config: seasonal configuration
        - position: current seasonal position
        - bsr_trend: BSR trend direction
        - modifier: score modifier
        - flags: list of warning/info flags
        - interpretation: human-readable summary
    """
    config = detect_category_seasonality(category_tree, title)
    position = get_seasonal_position(config.get('peak_months', []))
    bsr_trend = get_bsr_trend(bsr_history)
    modifier, flags = calculate_seasonality_modifier(config, position, bsr_trend)
    
    # Generate interpretation
    pattern = config.get('pattern', 'unknown')
    if pattern == 'stable' or pattern == 'unknown':
        interpretation = "Year-round demand, no seasonal adjustment"
    elif position == 'off' and bsr_trend == 'improving':
        interpretation = "Strong signal: BSR improving in off-season indicates genuine demand"
    elif position == 'peak':
        interpretation = f"Currently in peak season for {pattern} products - data may be inflated"
    elif position == 'rising':
        interpretation = f"Approaching peak season - recent BSR improvement may be seasonal, not organic"
    elif position == 'falling':
        interpretation = "Past peak season - expect gradual decline in demand"
    else:
        interpretation = f"Off-season for {pattern} products - good time to verify true demand"
    
    return {
        'config': config,
        'position': position,
        'bsr_trend': bsr_trend,
        'modifier': modifier,
        'flags': flags,
        'interpretation': interpretation
    }


# Standalone test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 2:
        title = " ".join(sys.argv[1:])
        result = analyze_seasonality("", title, [100000, 80000, 60000, 50000])
        
        print(f"Title: {title}", file=sys.stderr)
        print(f"Pattern: {result['config'].get('pattern', 'unknown')}", file=sys.stderr)
        print(f"Position: {result['position']}", file=sys.stderr)
        print(f"BSR Trend: {result['bsr_trend']}", file=sys.stderr)
        print(f"Modifier: {result['modifier']:+d}", file=sys.stderr)
        print(f"Interpretation: {result['interpretation']}", file=sys.stderr)

        if result['flags']:
            print("\nFlags:", file=sys.stderr)
            for f in result['flags']:
                print(f"  [{f['severity']}] {f['flag']}: {f['detail']}", file=sys.stderr)
    else:
        print("Usage: python3 seasonality_module.py <product title>", file=sys.stderr)
        print("Example: python3 seasonality_module.py 'Hawaiian Tropic Sunscreen SPF 50'", file=sys.stderr)
