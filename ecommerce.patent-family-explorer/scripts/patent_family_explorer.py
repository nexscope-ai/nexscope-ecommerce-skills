#!/usr/bin/env python3
"""
Patent Family Explorer v1.0.0
Explore patent families across multiple countries.
Data Source: Zhihuiya - International Patent Database
"""

import json
import os
import sys
import argparse
from urllib.request import Request, urlopen
from datetime import datetime
from typing import Optional
from collections import Counter

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

# Major markets for e-commerce
MAJOR_MARKETS = {
    'US': {'name': 'United States', 'importance': 'HIGH', 'emoji': '🇺🇸'},
    'CN': {'name': 'China', 'importance': 'HIGH', 'emoji': '🇨🇳'},
    'EP': {'name': 'European Patent', 'importance': 'HIGH', 'emoji': '🇪🇺'},
    'DE': {'name': 'Germany', 'importance': 'HIGH', 'emoji': '🇩🇪'},
    'GB': {'name': 'United Kingdom', 'importance': 'HIGH', 'emoji': '🇬🇧'},
    'FR': {'name': 'France', 'importance': 'MEDIUM', 'emoji': '🇫🇷'},
    'JP': {'name': 'Japan', 'importance': 'HIGH', 'emoji': '🇯🇵'},
    'KR': {'name': 'Korea', 'importance': 'MEDIUM', 'emoji': '🇰🇷'},
    'CA': {'name': 'Canada', 'importance': 'MEDIUM', 'emoji': '🇨🇦'},
    'AU': {'name': 'Australia', 'importance': 'MEDIUM', 'emoji': '🇦🇺'},
    'IN': {'name': 'India', 'importance': 'MEDIUM', 'emoji': '🇮🇳'},
    'BR': {'name': 'Brazil', 'importance': 'LOW', 'emoji': '🇧🇷'},
    'MX': {'name': 'Mexico', 'importance': 'LOW', 'emoji': '🇲🇽'},
    'WO': {'name': 'WIPO (PCT)', 'importance': 'INFO', 'emoji': '🌐'},
}

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

def get_patent_family(patent_numbers: str = '', patent_ids: str = '') -> dict:
    """Get patent family information"""
    payload = {}
    
    if patent_ids:
        payload['patentId'] = patent_ids
    elif patent_numbers:
        payload['patentNumber'] = patent_numbers
    else:
        return {'error': 'Either patentNumber or patentId is required'}
    
    result = api_call('patentFamily', payload)
    
    if not result:
        return {'error': 'API call failed', 'data': []}
    
    return {
        'total': result.get('total', 0),
        'data': result.get('data', [])
    }

def get_legal_status(patent_numbers: str) -> dict:
    """Get legal status for family members"""
    if not patent_numbers:
        return {}
    
    result = api_call('legalStatus', {'patentNumber': patent_numbers})
    
    if not result:
        return {}
    
    status_map = {}
    for item in result.get('data', []):
        pn = item.get('pn', '')
        status_map[pn] = {
            'simple_status': item.get('simpleLegalStatus', []),
            'detailed_status': item.get('legalStatus', []),
            'is_active': 'Active' in item.get('simpleLegalStatus', [])
        }
    
    return status_map

def extract_country(patent_number: str) -> str:
    """Extract country code from patent number"""
    if not patent_number:
        return ''
    
    # Remove spaces and normalize
    pn = patent_number.strip().upper()
    
    # Common patterns
    if pn.startswith('US'):
        return 'US'
    elif pn.startswith('CN'):
        return 'CN'
    elif pn.startswith('EP'):
        return 'EP'
    elif pn.startswith('WO'):
        return 'WO'
    elif pn.startswith('JP'):
        return 'JP'
    elif pn.startswith('KR'):
        return 'KR'
    elif pn.startswith('DE'):
        return 'DE'
    elif pn.startswith('GB'):
        return 'GB'
    elif pn.startswith('FR'):
        return 'FR'
    elif pn.startswith('CA'):
        return 'CA'
    elif pn.startswith('AU'):
        return 'AU'
    elif pn.startswith('IN'):
        return 'IN'
    elif pn.startswith('BR'):
        return 'BR'
    elif pn.startswith('MX'):
        return 'MX'
    elif pn.startswith('TW'):
        return 'TW'
    elif pn.startswith('RU'):
        return 'RU'
    else:
        # Try first 2 characters
        return pn[:2] if len(pn) >= 2 else ''

def parse_family_member(member) -> tuple:
    """Parse family member (can be string or dict)"""
    if isinstance(member, str):
        return member, extract_country(member)
    elif isinstance(member, dict):
        country = member.get('country', '')
        doc_num = member.get('doc_number', '')
        kind = member.get('kind', '')
        # Construct patent number
        pn = f"{country}{doc_num}{kind}" if country and doc_num else ''
        return pn, country
    return '', ''

def analyze_family(family_data: dict, legal_status: dict) -> dict:
    """Analyze patent family data"""
    
    patent_id = family_data.get('patentId', '')
    patent_number = family_data.get('pn', '')
    
    # Get family members
    simple_family = family_data.get('simpleFamily', [])
    inpadoc_family = family_data.get('inpadocFamily', [])
    patsnap_family = family_data.get('patsnapFamily', [])
    
    # Extract countries from each family type
    simple_countries = set()
    inpadoc_countries = set()
    patsnap_countries = set()
    
    simple_members = []
    inpadoc_members = []
    patsnap_members = []
    
    for member in simple_family:
        pn, country = parse_family_member(member)
        if country:
            simple_countries.add(country)
        if pn:
            simple_members.append(pn)
    
    for member in inpadoc_family:
        pn, country = parse_family_member(member)
        if country:
            inpadoc_countries.add(country)
        if pn:
            inpadoc_members.append(pn)
    
    for member in patsnap_family:
        pn, country = parse_family_member(member)
        if country:
            patsnap_countries.add(country)
        if pn:
            patsnap_members.append(pn)
    
    # All unique countries (union of all families)
    all_countries = simple_countries | inpadoc_countries | patsnap_countries
    
    # Assess geographic risk
    major_markets_covered = []
    high_importance_covered = []
    
    for country in all_countries:
        if country in MAJOR_MARKETS:
            market_info = MAJOR_MARKETS[country]
            major_markets_covered.append({
                'country': country,
                'name': market_info['name'],
                'importance': market_info['importance'],
                'emoji': market_info['emoji']
            })
            if market_info['importance'] == 'HIGH':
                high_importance_covered.append(country)
    
    # Determine risk level
    if 'US' in all_countries and 'CN' in all_countries and ('EP' in all_countries or 'DE' in all_countries):
        risk_level = 'HIGH'
        risk_emoji = '🔴'
        risk_description = 'Major markets (US, CN, EU) all protected'
    elif ('US' in all_countries and 'CN' in all_countries) or ('US' in all_countries and 'EP' in all_countries):
        risk_level = 'MEDIUM'
        risk_emoji = '🟠'
        risk_description = 'Key market combinations protected'
    elif 'US' in all_countries or 'CN' in all_countries:
        risk_level = 'LOW'
        risk_emoji = '🟡'
        risk_description = 'Single major market protected'
    else:
        risk_level = 'MINIMAL'
        risk_emoji = '🟢'
        risk_description = 'No major e-commerce markets protected'
    
    # Find safe markets (major markets not covered)
    all_major = set(MAJOR_MARKETS.keys())
    safe_markets = all_major - all_countries - {'WO'}  # WO is just PCT application
    
    # Format family members with status
    family_members = []
    
    # Simple family first (most important)
    for pn in simple_members:
        country = extract_country(pn)
        status = legal_status.get(pn, {})
        family_members.append({
            'patent_number': pn,
            'country': country,
            'country_name': MAJOR_MARKETS.get(country, {}).get('name', country),
            'family_type': 'simple',
            'is_active': status.get('is_active', None)
        })
    
    # Add INPADOC members not in simple
    simple_set = set(simple_members)
    for pn in inpadoc_members:
        if pn not in simple_set:
            country = extract_country(pn)
            status = legal_status.get(pn, {})
            family_members.append({
                'patent_number': pn,
                'country': country,
                'country_name': MAJOR_MARKETS.get(country, {}).get('name', country),
                'family_type': 'inpadoc',
                'is_active': status.get('is_active', None)
            })
    
    return {
        'patent_id': patent_id,
        'patent_number': patent_number,
        'family_ids': {
            'simple_family_id': family_data.get('simpleFamilyId'),
            'inpadoc_family_id': family_data.get('inpadocFamilyId'),
            'patsnap_family_id': family_data.get('patsnapFamilyId')
        },
        'family_sizes': {
            'simple': len(simple_family),
            'inpadoc': len(inpadoc_family),
            'patsnap': len(patsnap_family)
        },
        'countries': {
            'simple': sorted(list(simple_countries)),
            'inpadoc': sorted(list(inpadoc_countries)),
            'patsnap': sorted(list(patsnap_countries)),
            'all': sorted(list(all_countries))
        },
        'geographic_risk': {
            'level': risk_level,
            'emoji': risk_emoji,
            'description': risk_description,
            'total_countries': len(all_countries),
            'major_markets_covered': major_markets_covered,
            'high_importance_count': len(high_importance_covered),
            'safe_markets': sorted(list(safe_markets))
        },
        'family_members': family_members[:50]  # Limit to 50
    }

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
    
    results = report.get('results', [])
    if not results:
        return []
    
    # Use first result for charts
    first = results[0]
    
    # Chart 1: Family Size Comparison
    family_types = ['Simple Family', 'INPADOC Family', 'PatSnap Family']
    sizes = [
        first['family_sizes']['simple'],
        first['family_sizes']['inpadoc'],
        first['family_sizes']['patsnap']
    ]
    if sum(sizes) < 1:
        print(f"  ⚠️ 1_world_map.png skipped: need ≥1 items, got {sum(sizes)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [get_color('primary'), get_color('hot'), get_color('good')]

        bars = ax.bar(family_types, sizes, color=colors)
        ax.set_ylabel('Number of Patents')
        ax.set_title(f'Patent Family Sizes for {first["patent_number"]}')

        for bar, size in zip(bars, sizes):
            ax.annotate(f'{size}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        xytext=(0, 3), textcoords="offset points", ha='center',
                        fontsize=14, fontweight='bold')

        plt.savefig(f'{output_dir}/1_world_map.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 1: Family Sizes", file=sys.stderr)
    
    # Chart 2: Geographic Coverage
    countries = first['countries']['all']
    if not countries:
        print(f"  ⚠️ 2_family_types.png skipped: need ≥1 items, got 0", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(12, 6))

        # Count patents per country from family members
        country_counts = Counter()
        for member in first['family_members']:
            country_counts[member['country']] += 1

        sorted_countries = sorted(country_counts.items(), key=lambda x: -x[1])[:15]
        countries_list = [c[0] for c in sorted_countries]
        counts = [c[1] for c in sorted_countries]

        # Color by importance
        colors = []
        for c in countries_list:
            info = MAJOR_MARKETS.get(c, {})
            imp = info.get('importance', 'LOW')
            if imp == 'HIGH':
                colors.append(get_color('hot'))
            elif imp == 'MEDIUM':
                colors.append(get_color('warning'))
            else:
                colors.append(get_color('primary'))

        bars = ax.barh(range(len(countries_list)), counts, color=colors)
        ax.set_yticks(range(len(countries_list)))
        ax.set_yticklabels([f"{c} ({MAJOR_MARKETS.get(c, {}).get('name', c)[:15]})"
                           for c in countries_list])
        ax.set_xlabel('Number of Family Patents')
        ax.set_title('Geographic Coverage')
        ax.invert_yaxis()

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=get_color('hot'), label='HIGH importance'),
            Patch(facecolor=get_color('warning'), label='MEDIUM importance'),
            Patch(facecolor=get_color('primary'), label='Other')
        ]
        ax.legend(handles=legend_elements, loc='lower right')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_family_types.png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()
        print("  ✓ Chart 2: Geographic Coverage", file=sys.stderr)
    
    # Chart 3: Risk Assessment
    fig, ax = plt.subplots(figsize=(8, 8))
    
    risk = first['geographic_risk']
    
    # Create a simple risk indicator
    risk_colors = {'HIGH': get_color('hot'), 'MEDIUM': get_color('warning'), 'LOW': get_color('warning'), 'MINIMAL': get_color('good')}
    risk_color = risk_colors.get(risk['level'], '#95a5a6')
    
    circle = plt.Circle((0.5, 0.5), 0.4, color=risk_color, alpha=0.3)
    ax.add_patch(circle)
    ax.text(0.5, 0.5, risk['emoji'], fontsize=80, ha='center', va='center')
    ax.text(0.5, 0.15, risk['level'], fontsize=24, ha='center', fontweight='bold')
    ax.text(0.5, 0.05, risk['description'], fontsize=11, ha='center', wrap=True)
    ax.text(0.5, 0.92, 'Geographic Risk Level', fontsize=16, ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.savefig(f'{output_dir}/3_timeline.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 3: Risk Assessment", file=sys.stderr)
    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

def main():
    parser = argparse.ArgumentParser(description='Patent Family Explorer')
    parser.add_argument('params', help='JSON parameters')
    parser.add_argument('--chart', help='Output directory for charts')
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
    
    query_count = len(patent_numbers.split(',')) if patent_numbers else len(patent_ids.split(','))
    print(f"[1/3] Querying patent families for {query_count} patent(s)...", file=sys.stderr)
    
    # Get family data
    family_result = get_patent_family(patent_numbers, patent_ids)
    
    if 'error' in family_result and not family_result.get('data'):
        print(json.dumps({'error': family_result['error']}, ensure_ascii=False))
        sys.exit(1)
    
    print(f"    ✓ Got family data for {len(family_result.get('data', []))} patent(s)", file=sys.stderr)
    
    # Collect all family member numbers for legal status
    print(f"[2/3] Fetching legal status for family members...", file=sys.stderr)
    all_family_members = set()
    for item in family_result.get('data', []):
        for member in item.get('simpleFamily', []):
            pn, _ = parse_family_member(member)
            if pn:
                all_family_members.add(pn)
        for member in item.get('inpadocFamily', [])[:50]:  # Limit
            pn, _ = parse_family_member(member)
            if pn:
                all_family_members.add(pn)
    
    legal_status = {}
    if all_family_members:
        # Query in batches of 100
        members_list = list(all_family_members)[:100]
        legal_status = get_legal_status(','.join(members_list))
    
    print(f"    ✓ Got status for {len(legal_status)} patents", file=sys.stderr)
    
    # Analyze each patent's family
    print(f"[3/3] Analyzing families...", file=sys.stderr)
    results = []
    for item in family_result.get('data', []):
        analysis = analyze_family(item, legal_status)
        results.append(analysis)
    
    # Generate summary
    total_countries = set()
    for r in results:
        total_countries.update(r['countries']['all'])
    
    report = {
        'query_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0',
        'data_source': 'Zhihuiya',
        'total_queried': query_count,
        'total_found': len(results),
        'summary': {
            'total_unique_countries': len(total_countries),
            'all_countries': sorted(list(total_countries))
        },
        'results': results
    }
    
    # Generate charts
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
