#!/usr/bin/env python3
"""
Patent Risk Checker v1.1.0 (Zhihuiya Edition)
Assess patent infringement risk via image search.
Data Source: Zhihuiya - International Patent Database
"""

import json
import os
import sys
import argparse
from urllib.request import Request, urlopen
from datetime import datetime
from typing import Optional
from collections import defaultdict

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

# Risk weights (simplified without TRO/AI Radar)
WEIGHT_SIMILARITY = 0.50
WEIGHT_LEGAL_STATUS = 0.30
WEIGHT_LITIGATION = 0.20

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
        print(f"API Error: {e}", file=sys.stderr)
        return None

def search_design_patents(image_url: str, countries: str = '', limit: int = 50) -> dict:
    """Search design patents by image using Zhihuiya"""
    payload = {
        'url': image_url,
        'patentType': 'D',  # Design patent
        'model': 1,  # Smart association (recommended)
        'limit': min(limit, 100),
        'simpleLegalStatus': '1',  # Active patents only
        'lang': 'en',  # Chinese titles
        'field': 'SCORE',  # Sort by similarity
        'isHttps': 1
    }
    
    if countries:
        payload['country'] = countries
    
    result = api_call('patentImageSearch', payload)
    
    if not result:
        return {'count': 0, 'patents': [], 'error': 'API call failed'}
    
    patents = result.get('data', [])
    return {
        'count': len(patents),
        'total_in_db': result.get('allRecordsCount', 0),
        'patents': patents
    }

def search_utility_patents(image_url: str, countries: str = '', limit: int = 50) -> dict:
    """Search utility patents by image using Zhihuiya"""
    payload = {
        'url': image_url,
        'patentType': 'U',  # Utility patent
        'model': 4,  # Match shape/pattern/color (recommended)
        'limit': min(limit, 100),
        'simpleLegalStatus': '1',  # Active patents only
        'lang': 'en',
        'field': 'SCORE',
        'isHttps': 1
    }
    
    if countries:
        payload['country'] = countries
    
    result = api_call('patentImageSearch', payload)
    
    if not result:
        return {'count': 0, 'patents': [], 'error': 'API call failed'}
    
    patents = result.get('data', [])
    return {
        'count': len(patents),
        'total_in_db': result.get('allRecordsCount', 0),
        'patents': patents
    }

def get_legal_status(patent_ids: list) -> dict:
    """Get legal status for patents"""
    if not patent_ids:
        return {}
    
    # Batch query (max 100)
    ids_str = ','.join(patent_ids[:100])
    payload = {'patentId': ids_str}
    
    result = api_call('legalStatus', payload)
    
    if not result:
        return {}
    
    status_map = {}
    for item in result.get('data', []):
        pid = item.get('patentId', '')
        legal_status_list = item.get('legalStatus', [])
        # eventStatus is not returned by this API endpoint;
        # best-effort: check legalStatus list for any litigation-related terms
        has_litigation = any(
            'litigation' in s.lower() or 'dispute' in s.lower() or 'lawsuit' in s.lower()
            for s in legal_status_list
        )
        status_map[pid] = {
            'simple_status': item.get('simpleLegalStatus', []),
            'legal_status': legal_status_list,
            'events': [],
            'has_litigation': has_litigation
        }
    
    return status_map

def calculate_risk_score(design_results: dict, utility_results: dict, legal_status: dict) -> dict:
    """Calculate overall risk score"""
    
    design_patents = design_results.get('patents', [])
    utility_patents = utility_results.get('patents', [])
    
    # Find highest similarity scores
    design_max_score = 0
    utility_max_score = 0
    litigation_count = 0
    active_count = 0
    
    all_patents = []
    
    for p in design_patents:
        score = float(p.get('score') or 0)
        if score > design_max_score:
            design_max_score = score
        all_patents.append(('design', p))

    for p in utility_patents:
        score = float(p.get('score') or 0)
        if score > utility_max_score:
            utility_max_score = score
        all_patents.append(('utility', p))
    
    # Check legal status
    for patent_type, p in all_patents:
        pid = p.get('patentId', '')
        status = legal_status.get(pid, {})
        
        if status.get('has_litigation'):
            litigation_count += 1
        
        simple_status = status.get('simple_status', [])
        if 'Active' in simple_status or not simple_status:
            active_count += 1
    
    # Calculate component scores
    max_similarity = max(design_max_score, utility_max_score)
    similarity_score = max_similarity * 100
    
    # Legal status score (more active patents = higher risk)
    total_patents = len(all_patents)
    if total_patents > 0:
        active_ratio = active_count / total_patents
        legal_score = active_ratio * 100
    else:
        legal_score = 0
    
    # Litigation score
    litigation_score = 100 if litigation_count > 0 else 0
    
    # Overall risk score
    overall_score = (
        similarity_score * WEIGHT_SIMILARITY +
        legal_score * WEIGHT_LEGAL_STATUS +
        litigation_score * WEIGHT_LITIGATION
    )
    
    # Determine level
    if overall_score >= 76:
        level = 'CRITICAL'
        emoji = '🔴'
    elif overall_score >= 51:
        level = 'HIGH'
        emoji = '🟠'
    elif overall_score >= 26:
        level = 'MEDIUM'
        emoji = '🟡'
    else:
        level = 'LOW'
        emoji = '🟢'
    
    # Type-specific risks
    design_risk = design_max_score * 100 * 0.7 + (30 if litigation_count > 0 else 0)
    utility_risk = utility_max_score * 100 * 0.7 + (30 if litigation_count > 0 else 0)
    
    return {
        'overall_score': round(overall_score, 1),
        'level': level,
        'emoji': emoji,
        'design_patent_risk': round(min(design_risk, 100), 1),
        'utility_patent_risk': round(min(utility_risk, 100), 1),
        'components': {
            'similarity': round(similarity_score, 1),
            'legal_status': round(legal_score, 1),
            'litigation': round(litigation_score, 1)
        },
        'statistics': {
            'design_patents_found': len(design_patents),
            'utility_patents_found': len(utility_patents),
            'total_active_patents': active_count,
            'litigation_flagged': litigation_count,
            'design_max_similarity': round(design_max_score, 3),
            'utility_max_similarity': round(utility_max_score, 3)
        }
    }

def generate_alerts(design_results: dict, utility_results: dict, legal_status: dict) -> list:
    """Generate risk alerts"""
    alerts = []
    
    design_patents = design_results.get('patents', [])
    utility_patents = utility_results.get('patents', [])
    
    # Check design patents
    for p in design_patents[:20]:
        score = float(p.get('score') or 0)
        pid = p.get('patentId', '')
        status = legal_status.get(pid, {})
        
        # Litigation Alert
        if status.get('has_litigation'):
            alerts.append({
                'type': 'LITIGATION_HISTORY',
                'severity': 'CRITICAL',
                'patent_type': 'Design',
                'patent_number': p.get('patentPn', ''),
                'title': p.get('title', ''),
                'similarity': score,
                'applicant': p.get('currentAssignee') or p.get('originalAssignee', ''),
                'message': 'Patent has litigation history. High legal risk.'
            })
        
        # High Similarity Alert
        if score >= 0.8:
            alerts.append({
                'type': 'HIGH_SIMILARITY',
                'severity': 'HIGH',
                'patent_type': 'Design',
                'patent_number': p.get('patentPn', ''),
                'title': p.get('title', ''),
                'similarity': score,
                'image_url': p.get('url', ''),
                'message': f'Visual similarity {score:.0%} with active design patent.'
            })
        elif score >= 0.6:
            alerts.append({
                'type': 'MODERATE_SIMILARITY',
                'severity': 'MEDIUM',
                'patent_type': 'Design',
                'patent_number': p.get('patentPn', ''),
                'title': p.get('title', ''),
                'similarity': score,
                'message': f'Moderate visual similarity {score:.0%}. Review recommended.'
            })
    
    # Check utility patents
    for p in utility_patents[:20]:
        score = float(p.get('score') or 0)
        pid = p.get('patentId', '')
        status = legal_status.get(pid, {})
        
        # Litigation Alert
        if status.get('has_litigation'):
            alerts.append({
                'type': 'LITIGATION_HISTORY',
                'severity': 'CRITICAL',
                'patent_type': 'Utility',
                'patent_number': p.get('patentPn', ''),
                'title': p.get('title', ''),
                'similarity': score,
                'message': 'Utility patent has litigation history.'
            })
        
        # High similarity
        if score >= 0.7:
            alerts.append({
                'type': 'HIGH_SIMILARITY',
                'severity': 'HIGH',
                'patent_type': 'Utility',
                'patent_number': p.get('patentPn', ''),
                'title': p.get('title', ''),
                'similarity': score,
                'message': f'Functional similarity {score:.0%} with utility patent.'
            })
    
    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    alerts.sort(key=lambda x: (severity_order.get(x['severity'], 99), -x.get('similarity', 0)))
    
    return alerts

def format_top_matches(patents: list, patent_type: str, legal_status: dict, limit: int = 10) -> list:
    """Format top patent matches for output"""
    matches = []
    
    for p in patents[:limit]:
        score = float(p.get('score') or 0)
        pid = p.get('patentId', '')
        status = legal_status.get(pid, {})

        # Parse YYYYMMDD integer date format returned by Zhihuiya API
        apdt = p.get('apdt')
        pbdt = p.get('pbdt')
        try:
            app_date = datetime.strptime(str(int(apdt)), '%Y%m%d').strftime('%Y-%m-%d') if apdt else ''
        except (ValueError, TypeError):
            app_date = ''
        try:
            pub_date = datetime.strptime(str(int(pbdt)), '%Y%m%d').strftime('%Y-%m-%d') if pbdt else ''
        except (ValueError, TypeError):
            pub_date = ''
        
        match = {
            'patent_id': pid,
            'patent_number': p.get('patentPn', ''),
            'application_number': p.get('apno', ''),
            'title': p.get('title', ''),
            'similarity': round(score, 3),
            'similarity_pct': f"{score:.1%}",
            'country': p.get('authority', ''),
            'loc_classification': p.get('loc', []),
            'loc_match': p.get('locMatch', 0) == 1,
            'original_assignee': p.get('originalAssignee', ''),
            'current_assignee': p.get('currentAssignee', ''),
            'inventor': p.get('inventor', ''),
            'application_date': app_date,
            'publication_date': pub_date,
            'image_url': p.get('url', ''),
            'legal_status': {
                'simple_status': status.get('simple_status', []),
                'detailed_status': status.get('legal_status', []),
                'events': status.get('events', []),
                'has_litigation': status.get('has_litigation', False)
            }
        }
        
        matches.append(match)
    
    return matches

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
    
    risk = report['risk_summary']
    
    # Chart 1: Risk Gauge
    fig, ax = plt.subplots(figsize=(10, 6))
    
    score = risk['overall_score']
    colors = [get_color('good'), get_color('warning'), get_color('secondary'), get_color('hot')]
    
    # Create gauge background
    theta = np.linspace(0, np.pi, 100)
    for i, (start, end, color) in enumerate([(0, 25, colors[0]), (25, 50, colors[1]), 
                                              (50, 75, colors[2]), (75, 100, colors[3])]):
        mask = (theta >= start/100*np.pi) & (theta <= end/100*np.pi)
        theta_section = theta[mask]
        ax.fill_between(theta_section, 0.6, 1.0, alpha=0.3, color=color)
    
    # Score display
    ax.text(np.pi/2, 0.1, f'{score:.0f}', fontsize=48, ha='center', fontweight='bold')
    ax.text(np.pi/2, -0.15, risk['level'], fontsize=24, ha='center', 
            color=colors[min(int(score/25), 3)])
    ax.text(np.pi/2, 1.15, 'Patent Risk Score (Zhihuiya)', fontsize=16, ha='center')
    
    # Labels
    for angle, label in [(0, '100'), (np.pi/4, '75'), (np.pi/2, '50'), (3*np.pi/4, '25'), (np.pi, '0')]:
        ax.text(angle, 1.1, label, ha='center', fontsize=10)
    
    ax.set_xlim(-0.2, np.pi + 0.2)
    ax.set_ylim(-0.3, 1.3)
    ax.axis('off')
    
    plt.savefig(f'{output_dir}/1_risk_gauge.png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 1: Risk Gauge", file=sys.stderr)
    
    # Chart 2: Component Breakdown
    fig, ax = plt.subplots(figsize=(10, 6))
    
    components = risk['components']
    labels = ['Similarity\n(50%)', 'Legal Status\n(30%)', 'Litigation\n(20%)']
    values = [components['similarity'], components['legal_status'], components['litigation']]
    weights = [WEIGHT_SIMILARITY, WEIGHT_LEGAL_STATUS, WEIGHT_LITIGATION]
    weighted_values = [v * w for v, w in zip(values, weights)]
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, values, width, label='Raw Score', color=get_color('primary'), alpha=0.7)
    bars2 = ax.bar(x + width/2, weighted_values, width, label='Weighted', color=get_color('hot'), alpha=0.7)
    
    ax.set_ylabel('Score')
    ax.set_title('Risk Score Components')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, 100)
    
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
    
    plt.savefig(f'{output_dir}/2_similarity.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 2: Components", file=sys.stderr)
    
    # Chart 3: Similarity Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Design patents
    design_matches = report['design_patents'].get('top_matches', [])
    design_sims = [m['similarity'] for m in design_matches]
    if design_sims:
        colors_d = [get_color('hot') if s >= 0.8 else get_color('warning') if s >= 0.6 else get_color('good') for s in design_sims]
        ax1.barh(range(len(design_sims)), design_sims, color=colors_d)
        ax1.set_yticks(range(len(design_sims)))
        ax1.set_yticklabels([f"P{i+1}" for i in range(len(design_sims))])
        ax1.axvline(x=0.8, color='red', linestyle='--', alpha=0.5, label='High (80%)')
        ax1.axvline(x=0.6, color='orange', linestyle='--', alpha=0.5, label='Medium (60%)')
        ax1.legend(fontsize=8)
        ax1.set_xlim(0, 1)
    else:
        ax1.text(0.5, 0.5, 'No Design Patents Found', ha='center', va='center', fontsize=14)
    ax1.set_xlabel('Similarity')
    ax1.set_title('Design Patent Similarity')
    
    # Utility patents
    utility_matches = report['utility_patents'].get('top_matches', [])
    utility_sims = [m['similarity'] for m in utility_matches]
    if utility_sims:
        colors_u = [get_color('hot') if s >= 0.7 else get_color('warning') if s >= 0.5 else get_color('good') for s in utility_sims]
        ax2.barh(range(len(utility_sims)), utility_sims, color=colors_u)
        ax2.set_yticks(range(len(utility_sims)))
        ax2.set_yticklabels([f"P{i+1}" for i in range(len(utility_sims))])
        ax2.axvline(x=0.7, color='red', linestyle='--', alpha=0.5, label='High (70%)')
        ax2.axvline(x=0.5, color='orange', linestyle='--', alpha=0.5, label='Medium (50%)')
        ax2.legend(fontsize=8)
        ax2.set_xlim(0, 1)
    else:
        ax2.text(0.5, 0.5, 'No Utility Patents Found', ha='center', va='center', fontsize=14)
    ax2.set_xlabel('Similarity')
    ax2.set_title('Utility Patent Similarity')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/3_regions.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 3: Similarity Distribution", file=sys.stderr)
    
    # Chart 4: Alert Summary
    alerts = report.get('alerts', [])
    severity_counts = defaultdict(int)
    for alert in alerts:
        severity_counts[alert['severity']] += 1

    severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    counts = [severity_counts.get(s, 0) for s in severities]

    if sum(counts) < 1:
        print(f"  ⚠️ 4_timeline.png skipped: need ≥1 items, got {sum(counts)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [get_color('hot'), get_color('secondary'), get_color('warning'), get_color('good')]

        bars = ax.bar(severities, counts, color=colors)
        ax.set_ylabel('Number of Alerts')
        ax.set_title('Alert Summary by Severity')

        for bar, count in zip(bars, counts):
            if count > 0:
                ax.annotate(f'{count}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            xytext=(0, 3), textcoords="offset points", ha='center',
                            fontsize=12, fontweight='bold')

        plt.savefig(f'{output_dir}/4_timeline.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 4: Alerts", file=sys.stderr)
    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

def main():
    parser = argparse.ArgumentParser(description='Patent Risk Checker (Zhihuiya)')
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
    limit = params.get('limit', 50)
    
    # Validate input
    if not image_url:
        print(json.dumps({'error': 'imageUrl is required'}, ensure_ascii=False))
        sys.exit(1)
    
    report = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.1.0',
        'data_source': 'Zhihuiya',
        'input': {
            'image_url': image_url,
            'countries': countries
        }
    }
    
    # Search design patents
    print(f"[1/4] Searching design patents (Zhihuiya)...", file=sys.stderr)
    design_results = search_design_patents(image_url, countries, limit)
    print(f"    ✓ Found {design_results['count']} design patents", file=sys.stderr)
    
    # Search utility patents
    print(f"[2/4] Searching utility patents (Zhihuiya)...", file=sys.stderr)
    utility_results = search_utility_patents(image_url, countries, limit)
    print(f"    ✓ Found {utility_results['count']} utility patents", file=sys.stderr)
    
    # Get legal status for all patents
    print(f"[3/4] Fetching legal status...", file=sys.stderr)
    all_patent_ids = []
    for p in design_results.get('patents', []):
        if p.get('patentId'):
            all_patent_ids.append(p['patentId'])
    for p in utility_results.get('patents', []):
        if p.get('patentId'):
            all_patent_ids.append(p['patentId'])
    
    legal_status = {}
    if all_patent_ids:
        legal_status = get_legal_status(all_patent_ids)
    print(f"    ✓ Got status for {len(legal_status)} patents", file=sys.stderr)
    
    # Calculate risk score
    print(f"[4/4] Calculating risk score...", file=sys.stderr)
    risk_score = calculate_risk_score(design_results, utility_results, legal_status)
    report['risk_summary'] = risk_score
    
    # Format results
    report['design_patents'] = {
        'count': design_results['count'],
        'total_in_database': design_results.get('total_in_db', 0),
        'highest_similarity': risk_score['statistics']['design_max_similarity'],
        'top_matches': format_top_matches(
            design_results.get('patents', []), 'design', legal_status
        )
    }
    
    report['utility_patents'] = {
        'count': utility_results['count'],
        'total_in_database': utility_results.get('total_in_db', 0),
        'highest_similarity': risk_score['statistics']['utility_max_similarity'],
        'top_matches': format_top_matches(
            utility_results.get('patents', []), 'utility', legal_status
        )
    }
    
    # Generate alerts
    alerts = generate_alerts(design_results, utility_results, legal_status)
    report['alerts'] = alerts[:20]
    report['alert_summary'] = {
        'total': len(alerts),
        'critical': len([a for a in alerts if a['severity'] == 'CRITICAL']),
        'high': len([a for a in alerts if a['severity'] == 'HIGH']),
        'medium': len([a for a in alerts if a['severity'] == 'MEDIUM']),
        'low': len([a for a in alerts if a['severity'] == 'LOW'])
    }
    print(f"    ✓ {len(alerts)} alerts generated", file=sys.stderr)
    
    # Generate charts
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
