"""
Shared chart styling helpers for all ecommerce skills.
Source of truth: chart_style.json (derived from display-rules.md)

Usage in any skill script:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from ecommerce_chart_helpers import load_style, apply_style, save_chart
"""

import json
import os
import sys

# Default style matching display-rules.md — used if chart_style.json not found
_DEFAULT_STYLE = {
    "colors": {
        "hot":       "#EF5350",
        "good":      "#4CAF50",
        "warning":   "#FFC107",
        "primary":   "#2196F3",
        "secondary": "#FF9800",
        "muted":     "#90A4AE",
        "bg_box":    "#FFF9C4",
        "bg_success":"#E8F5E9",
        "bg_error":  "#FFEBEE"
    },
    "platform_colors": {
        "amazon":  "#FF9900",
        "ebay":    "#E53238",
        "walmart": "#0071CE",
        "tiktok":  "#FF0050",
        "google":  "#4285F4"
    },
    "verdict_colors": {
        "Hot Trend": "#EF5350",
        "Rising":    "#4CAF50",
        "Stable":    "#FFC107",
        "Declining": "#90A4AE"
    },
    "maturity_colors": {
        "emerging": "#4CAF50",
        "growing":  "#2196F3",
        "mature":   "#90A4AE"
    },
    "score_colors": {
        "high":   "#4CAF50",
        "medium": "#FFC107",
        "low":    "#EF5350"
    },
    "score_breakdown_colors": ["#EF5350", "#FF9800", "#4CAF50", "#2196F3"],
    "palette": ["#2196F3", "#4CAF50", "#FF9800", "#EF5350", "#9C27B0", "#00BCD4", "#795548", "#607D8B"],
    "font": {
        "family": ["DejaVu Sans", "sans-serif"],
        "title":  14,
        "axis":   11,
        "tick":   10,
        "legend": 10,
        "label":  10
    },
    "bar": {
        "edgecolor": "white",
        "linewidth": 1.5,
        "height": 0.6
    },
    "export": {
        "dpi": 150,
        "bbox_inches": "tight",
        "facecolor": "white"
    },
    "spines_hide": ["top", "right"]
}

_cached_style = None


def load_style(skill_dir=None):
    """Load chart style. Checks skill-local chart_style.json first, then shared default."""
    global _cached_style
    if _cached_style is not None:
        return _cached_style

    # Try skill-local chart_style.json
    paths_to_try = []
    if skill_dir:
        paths_to_try.append(os.path.join(skill_dir, 'scripts', 'chart_style.json'))
        paths_to_try.append(os.path.join(skill_dir, 'chart_style.json'))

    # Try shared location
    shared_path = os.path.join(os.path.dirname(__file__), 'chart_style.json')
    paths_to_try.append(shared_path)

    for path in paths_to_try:
        try:
            with open(path) as f:
                _cached_style = json.load(f)
                return _cached_style
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    _cached_style = _DEFAULT_STYLE
    return _cached_style


def apply_style(ax, style=None):
    """Apply common axis styling: hide spines, etc."""
    if style is None:
        style = load_style()
    for spine in style.get('spines_hide', ['top', 'right']):
        ax.spines[spine].set_visible(False)


def save_chart(fig, path, style=None):
    """Save chart with standardized export settings."""
    import matplotlib.pyplot as _plt
    if style is None:
        style = load_style()
    export = style.get('export', {})
    fig.tight_layout()
    fig.savefig(path,
                dpi=export.get('dpi', 150),
                bbox_inches=export.get('bbox_inches', 'tight'),
                facecolor=export.get('facecolor', 'white'))
    _plt.close(fig)


def get_color(key, style=None):
    """Get a color by key from the style. Searches colors, verdict_colors, etc."""
    if style is None:
        style = load_style()
    # Direct color lookup
    if key in style.get('colors', {}):
        return style['colors'][key]
    if key in style.get('verdict_colors', {}):
        return style['verdict_colors'][key]
    if key in style.get('maturity_colors', {}):
        return style['maturity_colors'][key]
    if key in style.get('platform_colors', {}):
        return style['platform_colors'][key]
    if key in style.get('score_colors', {}):
        return style['score_colors'][key]
    return '#90A4AE'  # fallback muted


def get_palette(n=8, style=None):
    """Get a list of n colors from the palette."""
    if style is None:
        style = load_style()
    palette = style.get('palette', _DEFAULT_STYLE['palette'])
    # Cycle if n > palette length
    return [palette[i % len(palette)] for i in range(n)]


def get_bar_kwargs(style=None):
    """Get standard bar chart kwargs."""
    if style is None:
        style = load_style()
    bar = style.get('bar', {})
    return {
        'edgecolor': bar.get('edgecolor', 'white'),
        'linewidth': bar.get('linewidth', 1.5),
    }


def get_font_size(element='label', style=None):
    """Get font size for an element (title, axis, tick, legend, label)."""
    if style is None:
        style = load_style()
    return style.get('font', {}).get(element, 10)


def setup_plt(style=None):
    """Configure matplotlib rcParams from style."""
    import matplotlib.pyplot as _plt
    if style is None:
        style = load_style()
    font = style.get('font', {})
    _plt.rcParams['font.family'] = font.get('family', ['DejaVu Sans', 'sans-serif'])


def _find_items(data, data_key=None):
    """Find the primary list of result items in a batch JSON object."""
    preferred_keys = [data_key] if data_key else []
    preferred_keys.extend(['trends', 'competitors', 'keywords', 'products', 'results', 'items'])

    for key in preferred_keys:
        if key and isinstance(data, dict) and isinstance(data.get(key), list):
            return key, data[key]

    if isinstance(data, dict):
        for parent_value in data.values():
            if isinstance(parent_value, dict):
                for key in preferred_keys:
                    if key and isinstance(parent_value.get(key), list):
                        return key, parent_value[key]

        largest_key = None
        largest_items = []
        for key, value in data.items():
            if isinstance(value, list) and len(value) > len(largest_items):
                largest_key = key
                largest_items = value
        if largest_key:
            return largest_key, largest_items

    return data_key or 'items', []


def _deep_get(data, path):
    current = data
    for part in path.split('.'):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _to_number(value, default=0):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned = value.replace(',', '').replace('%', '').replace('$', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return default
    return default


def _sort_value(item, sort_key):
    if not isinstance(item, dict):
        return 0

    if sort_key == 'sales':
        paths = ['tiktok.total_sales_30d', 'sales_30d', 'monthly_sales', 'estimated_sales', 'sales']
    elif sort_key == 'growth':
        paths = ['google_trends.trend_change', 'growth_rate', 'trend_change', 'growth', 'trend_pct']
    else:
        paths = ['trend_score.score', 'score', 'opportunity_score', 'priority_score', 'total_score']

    for path in paths:
        value = _deep_get(item, path) if '.' in path else item.get(path)
        if value is not None:
            return _to_number(value)
    return 0


def _item_identifier(item):
    if not isinstance(item, dict):
        return str(item)
    for key in ('keyword', 'asin', 'title', 'product_name', 'name', 'brand'):
        value = item.get(key)
        if value:
            return str(value)
    return json.dumps(item, sort_keys=True, ensure_ascii=False)[:120]


def merge_batch_results(json_files, data_key=None, sort_key="score"):
    """Merge batch JSON files, deduplicate items, and sort globally."""
    merged_items = {}
    detected_key = data_key
    batch_count = 0

    for json_file in json_files:
        with open(json_file, encoding='utf-8') as f:
            batch = json.load(f)
        batch_count += 1
        found_key, items = _find_items(batch, detected_key)
        if not detected_key and found_key:
            detected_key = found_key

        for item in items:
            identifier = _item_identifier(item)
            current = merged_items.get(identifier)
            if current is None or _sort_value(item, sort_key) > _sort_value(current, sort_key):
                merged_items[identifier] = item

    sorted_items = sorted(
        merged_items.values(),
        key=lambda item: _sort_value(item, sort_key),
        reverse=True
    )
    output_key = detected_key or data_key or 'items'

    return {
        'merged': True,
        'batch_count': batch_count,
        'total_items': len(sorted_items),
        'sort_key': sort_key,
        'data_key': output_key,
        output_key: sorted_items
    }


def generate_merged_charts(merged_result, chart_dir, chart_style_path=None):
    """Generate a unified ranking chart whose order matches the merged JSON."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as exc:
        print(f"Warning: matplotlib unavailable, using Pillow fallback for merged chart: {exc}", file=sys.stderr)
        return _generate_merged_chart_pillow(merged_result, chart_dir, chart_style_path)

    os.makedirs(chart_dir, exist_ok=True)
    style = None
    if chart_style_path:
        try:
            with open(chart_style_path, encoding='utf-8') as f:
                style = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            style = None
    if style is None:
        style = load_style()

    data_key = merged_result.get('data_key', 'items')
    items = merged_result.get(data_key, [])
    top_items = items[:25]
    if not top_items:
        return []

    sort_key = merged_result.get('sort_key', 'score')
    values = [_sort_value(item, sort_key) for item in top_items]
    labels = [f"#{idx + 1} {_item_identifier(item)}" for idx, item in enumerate(top_items)]
    colors = [
        get_color('hot', style) if value >= 90 else
        get_color('warning', style) if value >= 70 else
        get_color('good', style)
        for value in values
    ]

    setup_plt(style)
    height = max(5, len(top_items) * 0.42)
    fig, ax = plt.subplots(figsize=(12, height))
    positions = list(range(len(top_items)))
    ax.barh(positions, values, color=colors, **get_bar_kwargs(style))
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=get_font_size('tick', style))
    ax.invert_yaxis()
    ax.set_xlabel(sort_key.replace('_', ' ').title(), fontsize=get_font_size('axis', style))
    ax.set_title(
        f"Merged Ranking ({merged_result.get('total_items', len(items))} items, sorted by {sort_key})",
        fontsize=get_font_size('title', style),
        fontweight='bold'
    )
    apply_style(ax, style)

    max_value = max(values) if values else 0
    ax.set_xlim(0, max(max_value * 1.15, 100 if sort_key == 'score' else max_value + 1))
    for idx, value in enumerate(values):
        ax.text(value + max(max_value * 0.015, 0.5), idx, f"{value:g}", va='center',
                fontsize=get_font_size('label', style))

    chart_path = os.path.join(chart_dir, 'merged_ranking.png')
    save_chart(fig, chart_path, style)
    return [chart_path]


def _hex_to_rgb(value, fallback=(144, 164, 174)):
    if not isinstance(value, str):
        return fallback
    value = value.strip().lstrip('#')
    if len(value) != 6:
        return fallback
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return fallback


def _generate_merged_chart_pillow(merged_result, chart_dir, chart_style_path=None):
    """Small PNG fallback used when matplotlib is unavailable."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        print(f"Warning: Could not generate merged chart: {exc}", file=sys.stderr)
        return []

    os.makedirs(chart_dir, exist_ok=True)
    style = None
    if chart_style_path:
        try:
            with open(chart_style_path, encoding='utf-8') as f:
                style = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            style = None
    if style is None:
        style = load_style()

    data_key = merged_result.get('data_key', 'items')
    items = merged_result.get(data_key, [])[:25]
    if not items:
        return []

    sort_key = merged_result.get('sort_key', 'score')
    values = [_sort_value(item, sort_key) for item in items]
    max_value = max(values) if values else 1
    width = 1200
    row_height = 34
    top_margin = 72
    left_margin = 300
    right_margin = 120
    height = top_margin + len(items) * row_height + 36
    bar_width = width - left_margin - right_margin

    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    title = f"Merged Ranking ({merged_result.get('total_items', len(items))} items, sorted by {sort_key})"
    draw.text((24, 24), title, fill=(33, 33, 33), font=font)

    colors = {
        'hot': _hex_to_rgb(get_color('hot', style)),
        'warning': _hex_to_rgb(get_color('warning', style)),
        'good': _hex_to_rgb(get_color('good', style)),
        'muted': _hex_to_rgb(get_color('muted', style)),
    }

    for idx, item in enumerate(items):
        value = values[idx]
        y = top_margin + idx * row_height
        label = f"#{idx + 1} {_item_identifier(item)}"
        if len(label) > 38:
            label = label[:35] + '...'
        color = colors['hot'] if value >= 90 else colors['warning'] if value >= 70 else colors['good']
        length = int((value / max_value) * bar_width) if max_value else 0

        draw.text((24, y + 8), label, fill=(33, 33, 33), font=font)
        draw.rectangle((left_margin, y + 6, left_margin + bar_width, y + 24), fill=(238, 238, 238))
        draw.rectangle((left_margin, y + 6, left_margin + length, y + 24), fill=color)
        draw.text((left_margin + min(length + 8, bar_width + 8), y + 8), f"{value:g}", fill=(33, 33, 33), font=font)

    chart_path = os.path.join(chart_dir, 'merged_ranking.png')
    image.save(chart_path)
    return [chart_path]


def merge_and_chart(json_files, sort_key="score", chart_dir=None):
    """Merge batch results and optionally attach a unified chart."""
    merged = merge_batch_results(json_files, sort_key=sort_key)
    if chart_dir:
        merged['charts'] = generate_merged_charts(merged, chart_dir)
    return merged
