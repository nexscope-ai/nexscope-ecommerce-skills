#!/usr/bin/env python3
"""
Patent Legal Status v1.0.0
Query patent legal status (valid/invalid/expired).
Data Source: Zhihuiya (Zhihuiya) - International Patent Database
"""

import json
import os
import sys
import argparse
from urllib.request import Request, urlopen
from datetime import datetime
from typing import Optional

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

# Status mappings
SIMPLE_STATUS_MAP = {
    'Active': {'icon': '✅', 'is_valid': True, 'cn': 'Active'},
    'Inactive': {'icon': '❌', 'is_valid': False, 'cn': 'Inactive'},
    'Pending': {'icon': '⏳', 'is_valid': None, 'cn': 'Pending'},
    'Undetermined': {'icon': '❓', 'is_valid': None, 'cn': 'Undetermined'},
    'PCT designated period': {'icon': '🌐', 'is_valid': None, 'cn': 'PCT designated period'},
    'PCT designated expiration': {'icon': '🌐', 'is_valid': None, 'cn': 'PCT designated expiration'},
}

RISK_EVENTS = ['Litigation', 'Transfer', 'License', 'Pledge', 'Opposition',
               'Re-examination', 'Invalid-procedure']

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
        if isinstance(_proxy_result, dict):
            if 'code' in _proxy_result:
                if _proxy_result.get('code') == 0:
                    return _proxy_result.get('data', _proxy_result)
                else:
                    print(f"API Error [{endpoint}]: code={_proxy_result.get('code')}, msg={_proxy_result.get('msg', '')}", file=sys.stderr)
                    return None
            if 'errcode' in _proxy_result:
                print(f"API Error [{endpoint}]: errcode={_proxy_result.get('errcode')}, errmsg={_proxy_result.get('errmsg', '')}", file=sys.stderr)
                return None
        return _proxy_result
    except Exception as e:
        print(f"API Error: {e}", file=sys.stderr)
        return None

def get_legal_status(patent_numbers: str = '', patent_ids: str = '') -> dict:
    """Get legal status for patents"""
    payload = {}
    
    if patent_ids:
        payload['patentId'] = patent_ids
    elif patent_numbers:
        payload['patentNumber'] = patent_numbers
    else:
        return {'error': 'Either patentNumber or patentId is required'}
    
    result = api_call('legalStatus', payload)
    
    if not result:
        return {'error': 'API call failed', 'data': []}
    
    return {
        'total': result.get('total', 0),
        'data': result.get('data', [])
    }

def get_bibliography(patent_numbers: str = '', patent_ids: str = '') -> dict:
    """Get patent bibliography for additional details.
    
    Uses /bibliography endpoint (simpleBibliography is deprecated/broken upstream).
    Normalizes the richer response structure into a flat lookup dict.
    """
    payload = {}
    
    if patent_ids:
        payload['patentId'] = patent_ids
    elif patent_numbers:
        payload['patentNumber'] = patent_numbers
    else:
        return {}
    
    result = api_call('bibliography', payload)
    
    if not result:
        return {}
    
    # Create lookup by patent ID and number
    bib_map = {}
    for item in result.get('data', []):
        pid = item.get('patentId', '')
        pn = item.get('pn', item.get('publicationNumber', ''))
        
        # Normalize fields to match what format_results expects
        normalized = {}
        
        # Title: inventionTitle is a list of {text, lang}
        inv_titles = item.get('inventionTitle', [])
        if isinstance(inv_titles, list) and inv_titles:
            normalized['title'] = inv_titles[0].get('text', '')
        else:
            normalized['title'] = ''
        
        # Country from publicationReference
        pub_ref = item.get('publicationReference', {})
        normalized['country'] = pub_ref.get('country', '')
        normalized['publicationCountry'] = pub_ref.get('country', '')
        
        # Dates
        app_ref = item.get('applicationReference', {})
        app_date = app_ref.get('date')
        if app_date:
            try:
                normalized['applicationDate'] = datetime.strptime(str(int(app_date)), '%Y%m%d').strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                normalized['applicationDate'] = ''
        else:
            normalized['applicationDate'] = ''
        
        pub_date = pub_ref.get('date')
        if pub_date:
            try:
                normalized['publicationDate'] = datetime.strptime(str(int(pub_date)), '%Y%m%d').strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                normalized['publicationDate'] = ''
        else:
            normalized['publicationDate'] = ''
        
        # Applicants: list of {name, address, ...} → extract names
        raw_applicants = item.get('applicants', [])
        normalized['applicants'] = [a.get('name', '') for a in raw_applicants if isinstance(a, dict) and a.get('name')]
        
        # Assignees: same format
        raw_assignees = item.get('assignees', [])
        normalized['assignees'] = [a.get('name', '') for a in raw_assignees if isinstance(a, dict) and a.get('name')]
        
        # Patent type
        normalized['patentType'] = item.get('patentType', '')
        
        if pid:
            bib_map[pid] = normalized
        if pn:
            bib_map[pn] = normalized
    
    return bib_map

def format_results(legal_data: list, bib_map: dict) -> list:
    """Format legal status results"""
    results = []
    
    for item in legal_data:
        patent_id = item.get('patentId', '')
        patent_number = item.get('pn', '')
        
        # Get simple status
        simple_status_list = item.get('simpleLegalStatus', [])
        simple_status = simple_status_list[0] if simple_status_list else 'Unknown'
        
        # Get status info
        status_info = SIMPLE_STATUS_MAP.get(simple_status, {
            'icon': '❓', 'is_valid': None, 'cn': simple_status
        })
        
        # Get detailed status
        detailed_status = item.get('legalStatus', [])
        
        # Get legal events
        legal_events = item.get('eventStatus', [])
        
        # Check for risk events
        has_risk_events = any(event in RISK_EVENTS for event in legal_events)
        has_litigation = any('Litigation' in event for event in legal_events)
        
        # Get bibliography info if available
        bib = bib_map.get(patent_id, bib_map.get(patent_number, {}))
        
        # Format status date
        legal_date = item.get('legalDate')
        status_date = ''
        if legal_date:
            try:
                status_date = datetime.strptime(str(int(legal_date)), '%Y%m%d').strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
        
        result = {
            'patent_id': patent_id,
            'patent_number': patent_number,
            'title': bib.get('title', ''),
            'simple_status': simple_status,
            'simple_status_cn': status_info.get('cn', simple_status),
            'status_icon': status_info['icon'],
            'is_valid': status_info['is_valid'],
            'detailed_status': detailed_status,
            'legal_events': legal_events,
            'has_risk_events': has_risk_events,
            'has_litigation': has_litigation,
            'status_date': status_date,
            'country': bib.get('country', bib.get('publicationCountry', '')),
            'application_date': bib.get('applicationDate', ''),
            'publication_date': bib.get('publicationDate', ''),
            'applicants': bib.get('applicants', []),
            'assignees': bib.get('assignees', [])
        }
        
        results.append(result)
    
    return results

def generate_summary(results: list) -> dict:
    """Generate summary statistics"""
    summary = {
        'total': len(results),
        'active': 0,
        'inactive': 0,
        'pending': 0,
        'unknown': 0,
        'with_litigation': 0,
        'with_risk_events': 0
    }
    
    for r in results:
        if r['is_valid'] is True:
            summary['active'] += 1
        elif r['is_valid'] is False:
            summary['inactive'] += 1
        elif r['simple_status'] in ['Pending']:
            summary['pending'] += 1
        else:
            summary['unknown'] += 1
        
        if r['has_litigation']:
            summary['with_litigation'] += 1
        if r['has_risk_events']:
            summary['with_risk_events'] += 1
    
    return summary

def format_table_output(results: list) -> str:
    """Format results as a simple table for display"""
    lines = []
    lines.append("=" * 80)
    lines.append(f"{'Patent Number':<25} {'Status':<10} {'Valid':<8} {'Events':<20}")
    lines.append("=" * 80)
    
    for r in results:
        pn = r['patent_number'][:24] if r['patent_number'] else r['patent_id'][:24]
        status = r['status_icon'] + ' ' + (r['simple_status_cn'] or r['simple_status'])[:8]
        valid = 'Yes' if r['is_valid'] else ('No' if r['is_valid'] is False else '?')
        events = ', '.join(r['legal_events'][:2]) if r['legal_events'] else '-'
        
        lines.append(f"{pn:<25} {status:<10} {valid:<8} {events[:20]:<20}")
    
    lines.append("=" * 80)
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Patent Legal Status')
    parser.add_argument('params', nargs='?', default='{}', help='JSON parameters')
    parser.add_argument('--table', action='store_true', help='Output as table')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON: {e}'}, ensure_ascii=False))
        sys.exit(1)
    
    patent_numbers = params.get('patentNumber', params.get('patent_number', ''))
    patent_ids = params.get('patentId', params.get('patent_id', ''))
    
    if not patent_numbers and not patent_ids:
        print(json.dumps({'error': 'Either patentNumber or patentId is required'}, ensure_ascii=False))
        sys.exit(1)
    
    # Count patents being queried
    query_count = len(patent_numbers.split(',')) if patent_numbers else len(patent_ids.split(','))
    print(f"[1/3] Querying legal status for {query_count} patent(s)...", file=sys.stderr)
    
    # Get legal status
    legal_result = get_legal_status(patent_numbers, patent_ids)
    
    if 'error' in legal_result and not legal_result.get('data'):
        print(json.dumps({'error': legal_result['error']}, ensure_ascii=False))
        sys.exit(1)
    
    print(f"    ✓ Got status for {len(legal_result.get('data', []))} patent(s)", file=sys.stderr)
    
    # Get bibliography for additional info
    print(f"[2/3] Fetching patent details...", file=sys.stderr)
    bib_map = get_bibliography(patent_numbers, patent_ids)
    print(f"    ✓ Got details for {len(bib_map)} patent(s)", file=sys.stderr)
    if len(bib_map) == 0 and query_count > 0:
        print(f"    ⚠️ Bibliography API returned no data; title/dates/applicants fields will be empty.", file=sys.stderr)
    
    # Format results
    print(f"[3/3] Formatting results...", file=sys.stderr)
    results = format_results(legal_result.get('data', []), bib_map)
    summary = generate_summary(results)
    
    report = {
        'query_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0',
        'data_source': 'Zhihuiya (Zhihuiya)',
        'total_queried': query_count,
        'total_found': len(results),
        'summary': summary,
        'results': results
    }
    
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []
    
    if args.table:
        print(format_table_output(results))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

# === Chart Generation ===

def generate_charts(report: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
    except ImportError:
        print("matplotlib not available, skipping charts", file=sys.stderr)
        return []
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
    
    GREEN = get_color('good')
    RED = get_color('hot')
    ORANGE = get_color('secondary')
    GRAY = get_color('muted')
    
    summary = report.get('summary', {})
    results = report.get('results', [])
    
    # Chart 1: Status Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    
    labels = ['Active', 'Inactive', 'Pending', 'Unknown']
    values = [
        summary.get('active', 0),
        summary.get('inactive', 0),
        summary.get('pending', 0),
        summary.get('unknown', 0)
    ]
    colors = [GREEN, RED, ORANGE, GRAY]
    
    # Filter out zeros
    non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if non_zero:
        labels, values, colors = zip(*non_zero)
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                   str(val), ha='center', fontsize=14, fontweight='bold')
        
        ax.set_ylabel('Number of Patents', fontsize=11)
        ax.set_title('PATENT LEGAL STATUS DISTRIBUTION', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_status_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Status Distribution", file=sys.stderr)
    
    # Chart 2: Risk Events
    if summary.get('with_litigation', 0) > 0 or summary.get('with_risk_events', 0) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['With Litigation', 'With Risk Events', 'Clean']
        clean = summary.get('total', 0) - summary.get('with_litigation', 0) - summary.get('with_risk_events', 0)
        values = [
            summary.get('with_litigation', 0),
            summary.get('with_risk_events', 0),
            max(0, clean)
        ]
        colors = [RED, ORANGE, GREEN]
        
        non_zero = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
        if non_zero:
            labels, values, colors = zip(*non_zero)
            
            wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,
                                               autopct='%1.0f%%', startangle=90)
            
            ax.set_title('PATENT RISK EVENTS', fontweight='bold', fontsize=12, pad=15)
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/2_risk_events.png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✓ Chart 2: Risk Events", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

if __name__ == '__main__':
    main()
