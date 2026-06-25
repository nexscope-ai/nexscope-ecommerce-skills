#!/usr/bin/env python3
"""
Design Patent Analyzer v1.0.0
Deep analysis of design patent similarity using dual-model search.
Data Source: Zhihuiya - International Patent Database
"""

import json
import os
import sys
import argparse
from urllib.request import Request, urlopen
from datetime import datetime
from typing import Optional
from collections import defaultdict, Counter

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

# API Configuration

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')

def api_call(endpoint: str, payload: dict) -> Optional[dict]:
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured", file=sys.stderr)
        return None
    _proxy_url = f"{NEXSCOPE_PROXY_BASE}/api/v1/tools/linkfox/zhihuiya/{endpoint}"
    _proxy_req = Request(_proxy_url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
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
        print(f"API Error [{endpoint}]: {e}", file=sys.stderr)
        return None

def search_design_patents(image_url: str, model: int, countries: str = '', 
                          limit: int = 30, active_only: bool = True) -> dict:
    """Search design patents by image using specified model"""
    payload = {
        'url': image_url,
        'patentType': 'D',  # Design patent
        'model': model,
        'limit': min(limit, 100),
        'lang': 'cn',
        'field': 'SCORE',
        'isHttps': 1
    }
    
    if active_only:
        payload['simpleLegalStatus'] = '1'  # Active only
    
    if countries:
        payload['country'] = countries
    
    result = api_call('patentImageSearch', payload)
    
    if not result:
        return {'count': 0, 'patents': [], 'error': 'API call failed'}
    
    patents = result.get('data', [])
    return {
        'count': len(patents),
        'total_in_db': result.get('allRecordsCount', 0),
        'patents': patents,
        'model': model
    }

def get_legal_status(patent_ids: list) -> dict:
    """Get legal status for patents"""
    if not patent_ids:
        return {}
    
    ids_str = ','.join(patent_ids[:100])
    payload = {'patentId': ids_str}
    
    result = api_call('legalStatus', payload)
    
    if not result:
        return {}
    
    status_map = {}
    for item in result.get('data', []):
        pid = item.get('patentId', '')
        status_map[pid] = {
            'simple_status': item.get('simpleLegalStatus', []),
            'legal_status': item.get('legalStatus', []),
            'events': item.get('eventStatus', [])
        }
    
    return status_map

def analyze_conflicts(smart_results: dict, exact_results: dict) -> dict:
    """Analyze design patent conflicts"""
    
    # Combine results, prefer exact match scores when same patent appears in both
    all_patents = {}
    
    for p in smart_results.get('patents', []):
        pid = p.get('patentId', p.get('patentPn', ''))
        all_patents[pid] = {
            'patent': p,
            'smart_score': float(p.get('score') or 0),
            'exact_score': 0,
            'source': 'smart'
        }

    for p in exact_results.get('patents', []):
        pid = p.get('patentId', p.get('patentPn', ''))
        if pid in all_patents:
            all_patents[pid]['exact_score'] = float(p.get('score') or 0)
            all_patents[pid]['source'] = 'both'
        else:
            all_patents[pid] = {
                'patent': p,
                'smart_score': 0,
                'exact_score': float(p.get('score') or 0),
                'source': 'exact'
            }
    
    # Calculate max similarity (use higher of the two scores)
    max_similarity = 0
    for pid, data in all_patents.items():
        max_sim = max(data['smart_score'], data['exact_score'])
        if max_sim > max_similarity:
            max_similarity = max_sim
    
    # Count conflicts by level
    conflict_counts = {'likely': 0, 'high': 0, 'potential': 0, 'none': 0}
    for pid, data in all_patents.items():
        max_sim = max(data['smart_score'], data['exact_score'])
        if max_sim >= 0.85:
            conflict_counts['likely'] += 1
        elif max_sim >= 0.70:
            conflict_counts['high'] += 1
        elif max_sim >= 0.50:
            conflict_counts['potential'] += 1
        else:
            conflict_counts['none'] += 1
    
    # Determine conflict level
    if max_similarity >= 0.85:
        level = 'LIKELY_CONFLICT'
        emoji = '🔴'
        recommendation = 'Do not use this design. High infringement risk.'
    elif max_similarity >= 0.70:
        level = 'HIGH_SIMILARITY'
        emoji = '🟠'
        recommendation = 'Significant redesign recommended before proceeding.'
    elif max_similarity >= 0.50:
        level = 'POTENTIAL'
        emoji = '🟡'
        recommendation = 'Review specific features and consider modifications.'
    else:
        level = 'NO_CONFLICT'
        emoji = '🟢'
        recommendation = 'Design appears sufficiently different. Safe to proceed.'
    
    return {
        'level': level,
        'emoji': emoji,
        'max_similarity': round(max_similarity, 3),
        'max_similarity_pct': f"{max_similarity:.1%}",
        'total_patents_found': len(all_patents),
        'conflict_counts': conflict_counts,
        'recommendation': recommendation,
        'all_patents': all_patents
    }

def analyze_loc(patents: list) -> dict:
    """Analyze LOC (Locarno) classifications"""
    loc_counter = Counter()
    loc_patents = defaultdict(list)
    
    for p in patents:
        locs = p.get('loc', [])
        for loc in locs:
            loc_counter[loc] += 1
            loc_patents[loc].append(p.get('patentPn', ''))
    
    # Top LOC classifications
    top_locs = loc_counter.most_common(10)
    
    # Predict product LOC based on most common
    predicted_loc = top_locs[0][0] if top_locs else None
    
    return {
        'predicted_product_loc': predicted_loc,
        'total_loc_matches': sum(loc_counter.values()),
        'unique_classifications': len(loc_counter),
        'top_classifications': [
            {'loc': loc, 'count': count, 'patents': loc_patents[loc][:5]}
            for loc, count in top_locs
        ]
    }

def analyze_assignees(patents: list) -> dict:
    """Analyze patent assignees (owners)"""
    assignee_counter = Counter()
    assignee_patents = defaultdict(list)
    
    for p in patents:
        assignee = p.get('currentAssignee') or p.get('originalAssignee') or 'Unknown'
        assignee_counter[assignee] += 1
        assignee_patents[assignee].append({
            'patent_number': p.get('patentPn', ''),
            'similarity': float(p.get('score') or 0)
        })
    
    top_assignees = assignee_counter.most_common(10)
    
    return {
        'unique_assignees': len(assignee_counter),
        'top_assignees': [
            {
                'name': name,
                'patent_count': count,
                'max_similarity': max(p['similarity'] for p in assignee_patents[name]),
                'patents': sorted(assignee_patents[name], key=lambda x: -x['similarity'])[:3]
            }
            for name, count in top_assignees
        ]
    }

def format_top_conflicts(all_patents: dict, legal_status: dict, limit: int = 15) -> list:
    """Format top conflicting patents"""
    
    # Sort by max similarity
    sorted_patents = sorted(
        all_patents.items(),
        key=lambda x: max(x[1]['smart_score'], x[1]['exact_score']),
        reverse=True
    )
    
    conflicts = []
    for pid, data in sorted_patents[:limit]:
        p = data['patent']
        max_sim = max(data['smart_score'], data['exact_score'])
        
        # Convert timestamps
        apdt = p.get('apdt')
        pbdt = p.get('pbdt')
        try:
            app_date = datetime.fromtimestamp(int(apdt)/1000).strftime('%Y-%m-%d') if apdt else ''
        except (ValueError, TypeError):
            app_date = ''
        try:
            pub_date = datetime.fromtimestamp(int(pbdt)/1000).strftime('%Y-%m-%d') if pbdt else ''
        except (ValueError, TypeError):
            pub_date = ''
        
        # Determine conflict level
        if max_sim >= 0.85:
            conflict_level = '🔴 LIKELY'
        elif max_sim >= 0.70:
            conflict_level = '🟠 HIGH'
        elif max_sim >= 0.50:
            conflict_level = '🟡 POTENTIAL'
        else:
            conflict_level = '🟢 LOW'
        
        status = legal_status.get(p.get('patentId', ''), {})
        
        conflicts.append({
            'patent_id': p.get('patentId', ''),
            'patent_number': p.get('patentPn', ''),
            'title': p.get('title', ''),
            'similarity': round(max_sim, 3),
            'similarity_pct': f"{max_sim:.1%}",
            'conflict_level': conflict_level,
            'smart_score': round(data['smart_score'], 3),
            'exact_score': round(data['exact_score'], 3),
            'source': data['source'],
            'country': p.get('authority', ''),
            'loc': p.get('loc', []),
            'loc_match': p.get('locMatch', 0) == 1,
            'assignee': p.get('currentAssignee') or p.get('originalAssignee', ''),
            'inventor': p.get('inventor', ''),
            'application_date': app_date,
            'publication_date': pub_date,
            'image_url': p.get('url', ''),
            'legal_status': status.get('simple_status', [])
        })
    
    return conflicts

def generate_charts(report: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid')
    
    conflict = report['conflict_summary']
    
    # Chart 1: Conflict Gauge
    if not conflict:
        print(f"  ⚠️ 1_conflict_gauge.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        score = conflict['max_similarity'] * 100
        colors = [get_color('good'), get_color('warning'), get_color('secondary'), get_color('hot')]

        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        for i, (start, end, color) in enumerate([(0, 50, colors[0]), (50, 70, colors[1]),
                                                  (70, 85, colors[2]), (85, 100, colors[3])]):
            mask = (theta >= start/100*np.pi) & (theta <= end/100*np.pi)
            theta_section = theta[mask]
            ax.fill_between(theta_section, 0.6, 1.0, alpha=0.3, color=color)

        ax.text(np.pi/2, 0.1, f'{score:.1f}%', fontsize=48, ha='center', fontweight='bold')

        level_colors = {'NO_CONFLICT': colors[0], 'POTENTIAL': colors[1],
                        'HIGH_SIMILARITY': colors[2], 'LIKELY_CONFLICT': colors[3]}
        ax.text(np.pi/2, -0.15, conflict['level'].replace('_', ' '),
                fontsize=20, ha='center', color=level_colors.get(conflict['level'], 'black'))
        ax.text(np.pi/2, 1.15, 'Design Conflict Score', fontsize=16, ha='center')

        for angle, label in [(0, '100%'), (0.15*np.pi, '85%'), (0.3*np.pi, '70%'),
                             (0.5*np.pi, '50%'), (np.pi, '0%')]:
            ax.text(angle, 1.1, label, ha='center', fontsize=10)

        ax.set_xlim(-0.2, np.pi + 0.2)
        ax.set_ylim(-0.3, 1.3)
        ax.axis('off')

        plt.savefig(f'{output_dir}/1_conflict_gauge.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 1: Conflict Gauge", file=sys.stderr)
    
    # Chart 2: Model Comparison
    model_comparison = report.get('model_comparison', {})
    if not model_comparison:
        print(f"  ⚠️ 2_model_comparison.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        models = ['Smart Association\n(Model 1)', 'Exact Match\n(Model 2)']
        smart = model_comparison['smart_association']
        exact = model_comparison['exact_match']

        x = np.arange(len(models))
        width = 0.35

        counts = [smart['count'], exact['count']]
        max_sims = [smart['max_similarity'] * 100, exact['max_similarity'] * 100]

        ax1 = ax
        bars1 = ax1.bar(x - width/2, counts, width, label='Patents Found', color=get_color('primary'), alpha=0.7)
        ax1.set_ylabel('Patents Found', color=get_color('primary'))
        ax1.tick_params(axis='y', labelcolor=get_color('primary'))

        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + width/2, max_sims, width, label='Max Similarity %', color=get_color('hot'), alpha=0.7)
        ax2.set_ylabel('Max Similarity %', color=get_color('hot'))
        ax2.tick_params(axis='y', labelcolor=get_color('hot'))
        ax2.set_ylim(0, 100)

        ax1.set_xticks(x)
        ax1.set_xticklabels(models)
        ax1.set_title('Search Model Comparison')

        # Add value labels
        for bar, val in zip(bars1, counts):
            ax1.annotate(f'{val}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)
        for bar, val in zip(bars2, max_sims):
            ax2.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                         xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10, color=get_color('hot'))

        plt.savefig(f'{output_dir}/2_model_comparison.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 2: Model Comparison", file=sys.stderr)
    
    # Chart 3: Top Conflicts
    fig, ax = plt.subplots(figsize=(12, 8))
    
    conflicts = report['top_conflicts'][:15]
    if conflicts:
        labels = [f"{c['patent_number'][:15]}..." if len(c['patent_number']) > 15 
                  else c['patent_number'] for c in conflicts]
        sims = [c['similarity'] for c in conflicts]
        colors = [get_color('hot') if s >= 0.85 else get_color('secondary') if s >= 0.70 
                  else get_color('warning') if s >= 0.50 else get_color('good') for s in sims]
        
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, sims, color=colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Similarity Score')
        ax.set_title('Top Conflicting Patents')
        ax.axvline(x=0.85, color='red', linestyle='--', alpha=0.5, label='Likely (85%)')
        ax.axvline(x=0.70, color='orange', linestyle='--', alpha=0.5, label='High (70%)')
        ax.axvline(x=0.50, color='yellow', linestyle='--', alpha=0.5, label='Potential (50%)')
        ax.legend(loc='lower right', fontsize=8)
        ax.set_xlim(0, 1)
        ax.invert_yaxis()
    else:
        ax.text(0.5, 0.5, 'No Conflicts Found', ha='center', va='center', fontsize=16)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/3_top_conflicts.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 3: Top Conflicts", file=sys.stderr)
    
    # Chart 4: Assignee Distribution
    assignees = (report.get('assignee_analysis') or {}).get('top_assignees', [])[:8]
    if not assignees:
        print(f"  ⚠️ 4_assignees.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))

        names = [a['name'][:20] + '...' if len(a['name']) > 20 else a['name'] for a in assignees]
        counts = [a['patent_count'] for a in assignees]

        ax.barh(range(len(names)), counts, color='#9b59b6')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.set_xlabel('Number of Patents')
        ax.set_title('Top Patent Holders in Category')
        ax.invert_yaxis()

        for i, (count, assignee) in enumerate(zip(counts, assignees)):
            ax.annotate(f'{count} ({assignee["max_similarity"]:.0%})',
                        xy=(count, i), xytext=(5, 0), textcoords="offset points",
                        va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/4_assignees.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 4: Assignees", file=sys.stderr)
    
    # Chart 5: Conflict Level Distribution
    fig, ax = plt.subplots(figsize=(8, 8))
    
    counts = conflict['conflict_counts']
    labels = ['🔴 Likely\n(≥85%)', '🟠 High\n(70-85%)', '🟡 Potential\n(50-70%)', '🟢 None\n(<50%)']
    sizes = [counts['likely'], counts['high'], counts['potential'], counts['none']]
    colors = [get_color('hot'), get_color('secondary'), get_color('warning'), get_color('good')]
    
    # Filter out zeros
    non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
    if non_zero:
        labels, sizes, colors = zip(*non_zero)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90,
               textprops={'fontsize': 11})
        ax.set_title('Conflict Level Distribution')
    else:
        ax.text(0.5, 0.5, 'No Patents Found', ha='center', va='center', fontsize=16)
    
    plt.savefig(f'{output_dir}/5_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 5: Distribution", file=sys.stderr)
    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

def main():
    parser = argparse.ArgumentParser(description='Design Patent Analyzer')
    parser.add_argument('params', help='JSON parameters')
    parser.add_argument('--chart', help='Output directory for charts')
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON: {e}'}, ensure_ascii=False))
        sys.exit(1)
    
    image_url = params.get('imageUrl', params.get('image_url', ''))
    countries = params.get('countries', params.get('country', ''))
    limit = params.get('limit', 30)
    active_only = params.get('activeOnly', params.get('active_only', True))
    
    if not image_url:
        print(json.dumps({'error': 'imageUrl is required'}, ensure_ascii=False))
        sys.exit(1)
    
    report = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0',
        'data_source': 'Zhihuiya',
        'input': {
            'image_url': image_url,
            'countries': countries,
            'active_only': active_only
        }
    }
    
    # Search with Model 1 (Smart Association)
    print(f"[1/5] Smart Association search (Model 1)...", file=sys.stderr)
    smart_results = search_design_patents(image_url, model=1, countries=countries, 
                                          limit=limit, active_only=active_only)
    print(f"    ✓ Found {smart_results['count']} patents", file=sys.stderr)
    
    # Search with Model 2 (Exact Match)
    print(f"[2/5] Exact Match search (Model 2)...", file=sys.stderr)
    exact_results = search_design_patents(image_url, model=2, countries=countries,
                                          limit=limit, active_only=active_only)
    print(f"    ✓ Found {exact_results['count']} patents", file=sys.stderr)
    
    # Model comparison
    report['model_comparison'] = {
        'smart_association': {
            'count': smart_results['count'],
            'total_in_db': smart_results.get('total_in_db', 0),
            'max_similarity': max([float(p.get('score') or 0) for p in smart_results.get('patents', [])] or [0])
        },
        'exact_match': {
            'count': exact_results['count'],
            'total_in_db': exact_results.get('total_in_db', 0),
            'max_similarity': max([float(p.get('score') or 0) for p in exact_results.get('patents', [])] or [0])
        }
    }
    
    # Analyze conflicts
    print(f"[3/5] Analyzing conflicts...", file=sys.stderr)
    conflict_analysis = analyze_conflicts(smart_results, exact_results)
    report['conflict_summary'] = {
        'level': conflict_analysis['level'],
        'emoji': conflict_analysis['emoji'],
        'max_similarity': conflict_analysis['max_similarity'],
        'max_similarity_pct': conflict_analysis['max_similarity_pct'],
        'total_patents_found': conflict_analysis['total_patents_found'],
        'conflict_counts': conflict_analysis['conflict_counts'],
        'recommendation': conflict_analysis['recommendation']
    }
    
    # Get legal status
    print(f"[4/5] Fetching legal status...", file=sys.stderr)
    all_patent_ids = [p.get('patentId') for p in smart_results.get('patents', []) 
                     if p.get('patentId')]
    all_patent_ids += [p.get('patentId') for p in exact_results.get('patents', []) 
                      if p.get('patentId')]
    all_patent_ids = list(set(all_patent_ids))
    
    legal_status = get_legal_status(all_patent_ids) if all_patent_ids else {}
    
    # Format top conflicts
    report['top_conflicts'] = format_top_conflicts(
        conflict_analysis['all_patents'], legal_status
    )
    
    # Analyze LOC classifications
    all_patents_list = smart_results.get('patents', []) + exact_results.get('patents', [])
    report['loc_analysis'] = analyze_loc(all_patents_list)
    
    # Analyze assignees
    print(f"[5/5] Analyzing assignees...", file=sys.stderr)
    report['assignee_analysis'] = analyze_assignees(all_patents_list)
    
    # Generate charts
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
