#!/usr/bin/env python3
"""
Patent Claim Analyzer v1.0.0
Analyze patent claims to understand protection scope.
Data Source: Zhihuiya (Zhihuiya) - International Patent Database
"""

import json
import os
import sys
import argparse
import re
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

def get_claim_data(patent_numbers: str = '', patent_ids: str = '', 
                   replace_by_related: bool = True) -> dict:
    """Get original claim data"""
    payload = {'replaceByRelated': '1' if replace_by_related else '0'}
    
    if patent_ids:
        payload['patentId'] = patent_ids
    elif patent_numbers:
        payload['patentNumber'] = patent_numbers
    else:
        return {'error': 'Either patentNumber or patentId is required'}
    
    result = api_call('claimData', payload)
    
    if not result:
        return {'error': 'API call failed', 'data': []}
    
    return {
        'total': result.get('total', 0),
        'data': result.get('data', [])
    }

def get_claim_translated(patent_numbers: str = '', patent_ids: str = '',
                         lang: str = 'cn', replace_by_related: bool = True) -> dict:
    """Get translated claims"""
    payload = {
        'lang': lang,
        'replaceByRelated': 1 if replace_by_related else 0
    }
    
    if patent_ids:
        payload['patentId'] = patent_ids
    elif patent_numbers:
        payload['patentNumber'] = patent_numbers
    else:
        return {'error': 'Either patentNumber or patentId is required'}
    
    result = api_call('claimDataTranslated', payload)
    
    if not result:
        return {'error': 'API call failed', 'data': []}
    
    return {
        'total': result.get('total', 0),
        'data': result.get('data', [])
    }

def get_bibliography(patent_numbers: str) -> dict:
    """Get patent bibliography for context.
    
    Uses /bibliography endpoint (simpleBibliography is deprecated/broken upstream).
    Normalizes the richer response into a flat lookup dict.
    """
    if not patent_numbers:
        return {}
    
    result = api_call('bibliography', {'patentNumber': patent_numbers})
    
    if not result:
        return {}
    
    bib_map = {}
    for item in result.get('data', []):
        pn = item.get('pn', item.get('publicationNumber', ''))
        if not pn:
            continue
        
        # Normalize fields
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
        
        # Patent type
        normalized['patentType'] = item.get('patentType', '')
        
        bib_map[pn] = normalized
    
    return bib_map

def _analyze_claims_html(claims_text: str) -> dict:
    """Parse claims from Zhihuiya HTML format (indep-clm / dep-clm divs)."""
    independent = []
    dependent = []
    claim_structure = {}

    for match in re.finditer(
        r'<div\s[^>]*class="(indep|dep)-clm"[^>]*\bnum="(\d+)"(?:[^>]*\bparent="(\d+)")?',
        claims_text
    ):
        claim_type = match.group(1)
        num = int(match.group(2))
        parent = int(match.group(3)) if match.group(3) else None

        if claim_type == 'indep':
            independent.append(num)
            claim_structure[f'claim_{num}'] = {'type': 'independent'}
        else:
            dependent.append(num)
            claim_structure[f'claim_{num}'] = {'type': 'dependent', 'depends_on': parent}

    if not independent and not dependent:
        return {}

    return {
        'total_claims': len(independent) + len(dependent),
        'independent_claims': sorted(set(independent)),
        'dependent_claims': sorted(set(dependent)),
        'independent_count': len(independent),
        'dependent_count': len(dependent),
        'claim_structure': claim_structure
    }

def analyze_claims(claims_text: str) -> dict:
    """Analyze claim structure"""

    if not claims_text:
        return {
            'total_claims': 0,
            'independent_claims': [],
            'dependent_claims': [],
            'claim_structure': {}
        }

    # Zhihuiya may return HTML with indep-clm / dep-clm div attributes
    if 'indep-clm' in claims_text or 'dep-clm' in claims_text:
        html_result = _analyze_claims_html(claims_text)
        if html_result:
            return html_result

    # Split into individual claims
    # Common patterns: "1.", "1:", "Claim 1", etc.
    claim_pattern = r'(?:^|\n)\s*(?:Claim\s+)?(\d+)[.:\s]'
    
    claims_split = re.split(claim_pattern, claims_text)
    
    claim_texts = {}
    current_num = None
    
    for i, part in enumerate(claims_split):
        if part.isdigit():
            current_num = int(part)
        elif current_num is not None:
            claim_texts[current_num] = part.strip()
            current_num = None
    
    if not claim_texts:
        # Fallback: try to count claims by looking for numbered items
        numbers = re.findall(r'(?:^|\n)\s*(\d+)[.:\s]', claims_text)
        total_claims = len(set(numbers)) if numbers else 1
        return {
            'total_claims': total_claims,
            'independent_claims': [1] if total_claims > 0 else [],
            'dependent_claims': list(range(2, total_claims + 1)) if total_claims > 1 else [],
            'claim_structure': {},
            'raw_claims': claims_text[:5000]  # First 5000 chars
        }
    
    # Identify independent vs dependent claims
    independent = []
    dependent = []
    claim_structure = {}
    
    # Patterns for dependent claims
    dep_patterns = [
        r'(?:of|in|according to|as claimed in|as defined in)\s+claim\s+(\d+)',
        r'claim\s+(\d+)\s*,?\s*(?:wherein|where|further|additionally)',
        r'(?:according to|based on)\s+claim\s+(\d+)',
        r'(?:as (?:set forth|recited|described) in)\s+claim\s+(\d+)',
    ]
    
    for claim_num, claim_text in sorted(claim_texts.items()):
        is_dependent = False
        depends_on = None
        
        for pattern in dep_patterns:
            match = re.search(pattern, claim_text, re.IGNORECASE)
            if match:
                is_dependent = True
                depends_on = int(match.group(1))
                break
        
        if is_dependent:
            dependent.append(claim_num)
            claim_structure[f'claim_{claim_num}'] = {
                'type': 'dependent',
                'depends_on': depends_on,
                'text_preview': claim_text[:300]
            }
        else:
            independent.append(claim_num)
            claim_structure[f'claim_{claim_num}'] = {
                'type': 'independent',
                'text_preview': claim_text[:500]
            }
    
    return {
        'total_claims': len(claim_texts),
        'independent_claims': independent,
        'dependent_claims': dependent,
        'independent_count': len(independent),
        'dependent_count': len(dependent),
        'claim_structure': claim_structure
    }

def extract_key_elements(claim_text: str) -> list:
    """Extract key elements from a claim"""
    
    if not claim_text:
        return []
    
    elements = []
    
    # Common claim element patterns
    # "comprising: A; B; and C"
    # "including: A; B; and C"

    # Split by semicolons and "and"
    parts = re.split(r'[;]|\band\b', claim_text)
    
    for part in parts:
        # Clean up
        part = part.strip()
        part = re.sub(r'^[\d.:\s]+', '', part)  # Remove leading numbers
        part = re.sub(r'^(?:comprising|including|having|wherein)\s*:?\s*', '', part, flags=re.IGNORECASE)
        
        if len(part) > 10 and len(part) < 500:
            # Truncate long elements
            if len(part) > 100:
                part = part[:100] + '...'
            elements.append(part)
    
    return elements[:10]  # Limit to 10 elements

def format_results(claim_data: list, translated_data: list, bib_map: dict, lang: str) -> list:
    """Format claim analysis results"""
    
    # Create lookup for translated claims
    translated_map = {}
    for item in translated_data:
        pn = item.get('pn', '')
        if pn:
            translated_map[pn] = item.get('claims', '')
    
    results = []
    
    for item in claim_data:
        patent_id = item.get('patentId', '')
        patent_number = item.get('pn', '')
        claims = item.get('claims', [])
        claim_count = int(item.get('claimCount', 0) or 0)
        pn_related = item.get('pnRelated', '')
        
        # Get bibliography
        bib = bib_map.get(patent_number, {})
        
        # Combine claims into text
        claims_text = ''
        if isinstance(claims, list):
            # Structured claims
            claim_texts = []
            for c in claims:
                if isinstance(c, dict):
                    claim_texts.append(c.get('text', str(c)))
                else:
                    claim_texts.append(str(c))
            claims_text = '\n'.join(claim_texts)
        elif isinstance(claims, str):
            claims_text = claims
        
        # Get translated text
        translated_text = translated_map.get(patent_number, '')
        
        # Analyze structure
        analysis = analyze_claims(translated_text or claims_text)
        
        # Extract key elements from first independent claim
        key_elements = []
        if analysis['independent_claims']:
            first_ind = analysis['independent_claims'][0]
            struct = analysis['claim_structure'].get(f'claim_{first_ind}', {})
            preview = struct.get('text_preview', '')
            key_elements = extract_key_elements(preview)
        
        result = {
            'patent_id': patent_id,
            'patent_number': patent_number,
            'title': bib.get('title', ''),
            'patent_type': bib.get('patentType', ''),
            'country': bib.get('country', ''),
            'claim_count': claim_count or analysis['total_claims'],
            'used_related_patent': pn_related if pn_related else None,
            'claims_original': claims_text[:10000] if claims_text else None,
            'claims_translated': translated_text[:10000] if translated_text else None,
            'translation_language': lang,
            'analysis': {
                'total_claims': analysis['total_claims'],
                'independent_count': analysis.get('independent_count', len(analysis['independent_claims'])),
                'dependent_count': analysis.get('dependent_count', len(analysis['dependent_claims'])),
                'independent_claims': analysis['independent_claims'],
                'dependent_claims': analysis['dependent_claims'][:20],  # Limit
                'claim_structure': dict(list(analysis['claim_structure'].items())[:10]),  # Limit
                'key_elements': key_elements
            }
        }
        
        results.append(result)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Patent Claim Analyzer')
    parser.add_argument('params', nargs='?', default='{}', help='JSON parameters')
    parser.add_argument('--chart', metavar='DIR', help='Generate charts to directory')
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON: {e}'}, ensure_ascii=False))
        sys.exit(1)
    
    patent_numbers = params.get('patentNumber', params.get('patent_number', ''))
    patent_ids = params.get('patentId', params.get('patent_id', ''))
    lang = params.get('lang', 'cn')
    replace_by_related = params.get('replaceByRelated', params.get('replace_by_related', True))
    
    if not patent_numbers and not patent_ids:
        print(json.dumps({'error': 'Either patentNumber or patentId is required'}, ensure_ascii=False))
        sys.exit(1)
    
    query_count = len(patent_numbers.split(',')) if patent_numbers else len(patent_ids.split(','))
    print(f"[1/4] Querying claim data for {query_count} patent(s)...", file=sys.stderr)
    
    # Get original claim data
    claim_result = get_claim_data(patent_numbers, patent_ids, replace_by_related)
    
    if 'error' in claim_result and not claim_result.get('data'):
        print(json.dumps({'error': claim_result['error']}, ensure_ascii=False))
        sys.exit(1)
    
    print(f"    ✓ Got claims for {len(claim_result.get('data', []))} patent(s)", file=sys.stderr)
    
    # Get translated claims
    print(f"[2/4] Getting translated claims ({lang})...", file=sys.stderr)
    translated_result = get_claim_translated(patent_numbers, patent_ids, lang, replace_by_related)
    print(f"    ✓ Got translations for {len(translated_result.get('data', []))} patent(s)", file=sys.stderr)
    
    # Get bibliography for context
    print(f"[3/4] Fetching patent details...", file=sys.stderr)
    bib_map = get_bibliography(patent_numbers) if patent_numbers else {}
    print(f"    ✓ Got details", file=sys.stderr)
    
    # Format results
    print(f"[4/4] Analyzing claims...", file=sys.stderr)
    results = format_results(
        claim_result.get('data', []),
        translated_result.get('data', []),
        bib_map,
        lang
    )
    
    # Generate summary
    total_claims = sum(r['claim_count'] for r in results)
    total_independent = sum(r['analysis']['independent_count'] for r in results)
    
    report = {
        'query_date': datetime.now().strftime('%Y-%m-%d'),
        'api_version': 'v1.0.0',
        'data_source': 'Zhihuiya (Zhihuiya)',
        'translation_language': lang,
        'total_patents': len(results),
        'summary': {
            'total_claims': total_claims,
            'total_independent': total_independent,
            'total_dependent': total_claims - total_independent
        },
        'results': results
    }
    
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []

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
    
    BLUE = get_color('primary')
    GREEN = get_color('good')
    ORANGE = get_color('secondary')
    
    results = report.get('results', [])
    if not results:
        return []
    
    # Chart 1: Claims Overview (for first patent)
    first = results[0]
    analysis = first.get('analysis', {})

    labels = ['Independent\nClaims', 'Dependent\nClaims']
    values = [analysis.get('independent_count', 0), analysis.get('dependent_count', 0)]
    if sum(values) < 1:
        print(f"  ⚠️ 1_claim_structure.png skipped: need ≥1 items, got {sum(values)}", file=sys.stderr)
    else:
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [BLUE, GREEN]

        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)

        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                       str(val), ha='center', fontsize=14, fontweight='bold')

        ax.set_ylabel('Number of Claims', fontsize=11)
        pn = first.get('patent_number', 'Unknown')[:20]
        ax.set_title(f'CLAIM STRUCTURE: {pn}', fontweight='bold', fontsize=12, pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/1_claim_structure.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 1: Claim Structure", file=sys.stderr)
    
    # Chart 2: Multi-patent comparison (if multiple)
    if len(results) > 1:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        patents = [r.get('patent_number', '')[:15] for r in results[:8]]
        claims = [r.get('claim_count', 0) for r in results[:8]]
        
        bars = ax.barh(patents, claims, color=BLUE, edgecolor='white', linewidth=2)
        
        for bar, val in zip(bars, claims):
            ax.text(val + max(claims)*0.02, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=10)
        
        ax.set_xlabel('Number of Claims', fontsize=11)
        ax.set_title('CLAIMS BY PATENT', fontweight='bold', fontsize=12, pad=15)
        ax.invert_yaxis()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/2_claims_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  ✓ Chart 2: Claims Comparison", file=sys.stderr)

    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

if __name__ == '__main__':
    main()
