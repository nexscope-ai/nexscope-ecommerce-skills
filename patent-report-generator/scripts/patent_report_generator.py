#!/usr/bin/env python3
"""
Patent Report Generator v1.0.0
Generate comprehensive patent risk reports for products.
Integrates all patent analysis tools into one actionable report.
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

# Major markets
MAJOR_MARKETS = {
    'US': '🇺🇸 United States',
    'CN': '🇨🇳 China',
    'EP': '🇪🇺 European Patent',
    'DE': '🇩🇪 Germany',
    'GB': '🇬🇧 United Kingdom',
    'JP': '🇯🇵 Japan',
    'KR': '🇰🇷 Korea',
    'FR': '🇫🇷 France',
    'CA': '🇨🇦 Canada',
    'AU': '🇦🇺 Australia',
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
        with urlopen(_proxy_req, timeout=30) as _proxy_resp:
            _proxy_result = json.loads(_proxy_resp.read().decode('utf-8'))
        if isinstance(_proxy_result, dict) and 'code' in _proxy_result:
            return _proxy_result.get('data', _proxy_result) if _proxy_result.get('code') == 0 else None
        return _proxy_result
    except Exception as e:
        print(f"API Error [{endpoint}]: {e}", file=sys.stderr)
        return None

def search_design_patents(image_url: str, countries: str = '', limit: int = 30) -> list:
    """Search design patents by image"""
    payload = {
        'url': image_url,
        'patentType': 'D',
        'model': 1,
        'limit': limit,
        'simpleLegalStatus': '1',
        'lang': 'en',
        'field': 'SCORE',
        'isHttps': 1
    }
    if countries:
        payload['country'] = countries
    
    result = api_call('patentImageSearch', payload)
    return result.get('data', []) if result else []

def search_utility_patents(image_url: str, limit: int = 30) -> list:
    """Search utility patents by image"""
    payload = {
        'url': image_url,
        'patentType': 'U',
        'model': 4,
        'limit': limit,
        'simpleLegalStatus': '1',
        'lang': 'en',
        'field': 'SCORE',
        'isHttps': 1
    }
    
    result = api_call('patentImageSearch', payload)
    return result.get('data', []) if result else []

def get_legal_status(patent_ids: list) -> dict:
    """Get legal status for patents"""
    if not patent_ids:
        return {}
    
    result = api_call('legalStatus', {'patentId': ','.join(patent_ids[:100])})
    
    status_map = {}
    if result:
        for item in result.get('data', []):
            pid = item.get('patentId', '')
            simple = item.get('simpleLegalStatus', [])
            status_map[pid] = {
                'status': simple[0] if simple else 'Unknown',
                'is_active': 'Active' in simple,
                'events': item.get('eventStatus', [])
            }
    return status_map

def get_patent_family(patent_ids: list) -> dict:
    """Get patent family information"""
    if not patent_ids:
        return {}
    
    result = api_call('patentFamily', {'patentId': ','.join(patent_ids[:20])})
    
    family_map = {}
    if result:
        for item in result.get('data', []):
            pid = item.get('patentId', '')
            patsnap = item.get('patsnapFamily', [])
            countries = set()
            for member in patsnap:
                if isinstance(member, dict):
                    countries.add(member.get('country', ''))
            family_map[pid] = {
                'family_size': len(patsnap),
                'countries': list(countries)
            }
    return family_map

def get_claims(patent_ids: list, lang: str = 'cn') -> dict:
    """Get translated claims"""
    if not patent_ids:
        return {}
    
    result = api_call('claimDataTranslated', {
        'patentId': ','.join(patent_ids[:10]),
        'lang': lang,
        'replaceByRelated': 1
    })
    
    claims_map = {}
    if result:
        for item in result.get('data', []):
            pid = item.get('patentId', '')
            claims_map[pid] = item.get('claims', '')[:2000]  # Truncate
    return claims_map

def calculate_risk_score(design_patents: list, utility_patents: list) -> dict:
    """Calculate overall risk score"""
    
    design_max = max([float(p.get('score') or 0) for p in design_patents] or [0])
    utility_max = max([float(p.get('score') or 0) for p in utility_patents] or [0])

    max_similarity = max(design_max, utility_max)

    # Count high-risk patents
    high_risk_count = sum(1 for p in design_patents if float(p.get('score') or 0) >= 0.7)
    high_risk_count += sum(1 for p in utility_patents if float(p.get('score') or 0) >= 0.7)
    
    # Calculate score
    similarity_score = max_similarity * 100
    volume_bonus = min(high_risk_count * 5, 25)  # Up to 25 points for volume
    
    overall_score = min(similarity_score * 0.7 + volume_bonus, 100)
    
    if overall_score >= 76:
        level, emoji, recommendation = 'CRITICAL', '🔴', 'DO NOT PROCEED. High infringement risk.'
    elif overall_score >= 51:
        level, emoji, recommendation = 'HIGH', '🟠', 'PROCEED WITH CAUTION. Legal review strongly recommended.'
    elif overall_score >= 26:
        level, emoji, recommendation = 'MEDIUM', '🟡', 'REVIEW RECOMMENDED. Some concerns identified.'
    else:
        level, emoji, recommendation = 'LOW', '🟢', 'SAFE TO PROCEED. Minimal patent risks detected.'
    
    return {
        'overall_score': round(overall_score, 1),
        'level': level,
        'emoji': emoji,
        'recommendation': recommendation,
        'design_max_similarity': round(design_max, 3),
        'utility_max_similarity': round(utility_max, 3),
        'high_risk_count': high_risk_count
    }

def format_top_risks(patents: list, legal_status: dict, family_map: dict, 
                     claims_map: dict, limit: int = 10) -> list:
    """Format top risk patents with full details"""
    
    sorted_patents = sorted(patents, key=lambda x: -float(x.get('score') or 0))
    
    risks = []
    for p in sorted_patents[:limit]:
        pid = p.get('patentId', '')
        score = float(p.get('score') or 0)
        
        status = legal_status.get(pid, {})
        family = family_map.get(pid, {})
        claims = claims_map.get(pid, '')
        
        # Risk level
        if score >= 0.85:
            risk_level = '🔴 CRITICAL'
        elif score >= 0.70:
            risk_level = '🟠 HIGH'
        elif score >= 0.50:
            risk_level = '🟡 MEDIUM'
        else:
            risk_level = '🟢 LOW'
        
        risks.append({
            'patent_number': p.get('patentPn', ''),
            'title': p.get('title', ''),
            'similarity': round(score, 3),
            'similarity_pct': f"{score:.1%}",
            'risk_level': risk_level,
            'country': p.get('authority', ''),
            'assignee': p.get('currentAssignee') or p.get('originalAssignee', ''),
            'legal_status': status.get('status', 'Unknown'),
            'is_active': status.get('is_active', None),
            'legal_events': status.get('events', []),
            'family_size': family.get('family_size', 0),
            'family_countries': family.get('countries', []),
            'claims_preview': claims[:1000] if claims else None,
            'image_url': p.get('url', '')
        })
    
    return risks

def analyze_geography(design_patents: list, utility_patents: list, 
                      family_map: dict, target_markets: str) -> dict:
    """Analyze geographic patent coverage"""
    
    all_countries = Counter()
    
    for p in design_patents + utility_patents:
        country = p.get('authority', '')
        if country:
            all_countries[country] += 1
        
        pid = p.get('patentId', '')
        if pid in family_map:
            for c in family_map[pid].get('countries', []):
                all_countries[c] += 1
    
    # Check target markets
    targets = [m.strip().upper() for m in target_markets.split(',')]
    market_coverage = {}
    
    for market in targets:
        if market in all_countries:
            market_coverage[market] = {
                'covered': True,
                'patent_count': all_countries[market],
                'name': MAJOR_MARKETS.get(market, market),
                'status': '⚠️ Patents found'
            }
        else:
            market_coverage[market] = {
                'covered': False,
                'patent_count': 0,
                'name': MAJOR_MARKETS.get(market, market),
                'status': '✅ No patents found'
            }
    
    return {
        'all_countries': dict(all_countries.most_common(20)),
        'target_market_coverage': market_coverage,
        'safe_markets': [m for m, v in market_coverage.items() if not v['covered']],
        'risky_markets': [m for m, v in market_coverage.items() if v['covered']]
    }

def generate_markdown_report(report: dict) -> str:
    """Generate markdown report"""
    
    md = []
    
    # Header
    md.append(f"# 🔍 Patent Clearance Report")
    md.append(f"**Patent Clearance Report**")
    md.append(f"")
    md.append(f"- **Generated**: {report['report_date']}")
    md.append(f"- **Product Name**: {report['product_info'].get('name', 'N/A')}")
    md.append(f"- **Data Source**: Zhihuiya (Zhihuiya)")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    
    # Executive Summary
    risk = report['risk_assessment']
    md.append(f"## 📊 Risk Assessment Summary")
    md.append(f"")
    md.append(f"| Metric | Value |")
    md.append(f"|------|-----|")
    md.append(f"| **Overall Risk Score** | **{risk['overall_score']} {risk['emoji']}** |")
    md.append(f"| **Risk Level** | **{risk['level']}** |")
    md.append(f"| Max Design Patent Similarity | {risk['design_max_similarity']:.1%} |")
    md.append(f"| Max Utility Patent Similarity | {risk['utility_max_similarity']:.1%} |")
    md.append(f"| High Risk Patent Count | {risk['high_risk_count']} |")
    md.append(f"")
    md.append(f"> **Recommendation**: {risk['recommendation']}")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    
    # Geographic Analysis
    geo = report['geographic_analysis']
    md.append(f"## 🌍 Geographic Coverage Analysis")
    md.append(f"")
    md.append(f"### Target Market Status")
    md.append(f"")
    md.append(f"| Market | Status | Patent Count |")
    md.append(f"|------|------|--------|")
    for market, info in geo['target_market_coverage'].items():
        md.append(f"| {info['name']} | {info['status']} | {info['patent_count']} |")
    md.append(f"")
    
    if geo['safe_markets']:
        md.append(f"**✅ Safe Markets**: {', '.join(geo['safe_markets'])}")
    if geo['risky_markets']:
        md.append(f"**⚠️ Risky Markets**: {', '.join(geo['risky_markets'])}")
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    
    # Top Risks
    md.append(f"## 🚨 High Risk Patent Details")
    md.append(f"")
    
    for i, r in enumerate(report['top_risks'][:10], 1):
        md.append(f"### {i}. {r['patent_number']}")
        md.append(f"")
        md.append(f"| Attribute | Value |")
        md.append(f"|------|-----|")
        md.append(f"| **Title** | {r['title'][:50]}{'...' if len(r['title']) > 50 else ''} |")
        md.append(f"| **Similarity** | {r['similarity_pct']} {r['risk_level']} |")
        md.append(f"| **Assignee** | {r['assignee'][:30] if r['assignee'] else 'N/A'} |")
        md.append(f"| **Legal Status** | {'✅ Active' if r['is_active'] else '❌ Inactive' if r['is_active'] is False else '❓ Unknown'} |")
        md.append(f"| **Family Size** | {r['family_size']} patents |")
        if r['family_countries']:
            md.append(f"| **Covered Countries** | {', '.join(r['family_countries'][:5])} |")
        md.append(f"")
        
        if r.get('claims_preview'):
            md.append(f"<details>")
            md.append(f"<summary>📋 Claims Preview</summary>")
            md.append(f"")
            md.append(f"```")
            md.append(r['claims_preview'][:500])
            md.append(f"```")
            md.append(f"</details>")
            md.append(f"")
    
    md.append(f"---")
    md.append(f"")
    
    # Recommendations
    md.append(f"## ✅ Recommendations")
    md.append(f"")
    
    level = risk['level']
    if level == 'CRITICAL':
        md.append(f"1. ❌ **Stop immediately** product development or sourcing")
        md.append(f"2. 🔄 Redesign product to avoid infringement")
        md.append(f"3. ⚖️ Consult a patent attorney to assess legal risk")
    elif level == 'HIGH':
        md.append(f"1. ⚠️ **Proceed with caution** this product")
        md.append(f"2. ⚖️ Professional legal assessment recommended")
        md.append(f"3. 🔍 Analyze claims of high-risk patents in detail")
        md.append(f"4. 🔄 Consider design modifications to reduce risk")
    elif level == 'MEDIUM':
        md.append(f"1. 📋 **Review** flagged patent details")
        md.append(f"2. 🔍 Confirm differences between product features and patent claims")
        md.append(f"3. 📝 Document design-around rationale")
    else:
        md.append(f"1. ✅ Safe to proceed with product development")
        md.append(f"2. 📋 Keep this report as due diligence record")
        md.append(f"3. 🔄 Recheck periodically (quarterly)")
    
    md.append(f"")
    md.append(f"---")
    md.append(f"")
    md.append(f"*This report was generated by Patent Report Generator v1.0.0 automatically*")
    md.append(f"*Data Source: Zhihuiya (Zhihuiya) | For reference only, does not constitute legal advice*")
    
    return '\n'.join(md)

def generate_charts(report: dict, output_dir: str):
    """Generate visualization charts"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not available", file=sys.stderr)
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid')
    
    risk = report['risk_assessment']
    
    # Chart 1: Risk Gauge
    fig, ax = plt.subplots(figsize=(10, 6))
    
    score = risk['overall_score']
    colors = [get_color('good'), get_color('warning'), get_color('secondary'), get_color('hot')]
    
    theta = np.linspace(0, np.pi, 100)
    for start, end, color in [(0, 25, colors[0]), (25, 50, colors[1]), 
                               (50, 75, colors[2]), (75, 100, colors[3])]:
        mask = (theta >= start/100*np.pi) & (theta <= end/100*np.pi)
        ax.fill_between(theta[mask], 0.6, 1.0, alpha=0.3, color=color)
    
    ax.text(np.pi/2, 0.1, f'{score:.0f}', fontsize=48, ha='center', fontweight='bold')
    ax.text(np.pi/2, -0.15, risk['level'], fontsize=24, ha='center',
            color=colors[min(int(score/25), 3)])
    ax.text(np.pi/2, 1.15, 'PATENT RISK SCORE', fontsize=16, ha='center')
    
    ax.set_xlim(-0.2, np.pi + 0.2)
    ax.set_ylim(-0.3, 1.3)
    ax.axis('off')
    
    plt.savefig(f'{output_dir}/1_risk_gauge.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 1: Risk Gauge", file=sys.stderr)
    
    # Chart 2: Risk Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top_risks = report['top_risks'][:15]
    if top_risks:
        labels = [r['patent_number'][:12] for r in top_risks]
        sims = [r['similarity'] for r in top_risks]
        colors = [get_color('hot') if s >= 0.85 else get_color('secondary') if s >= 0.70 
                  else get_color('warning') if s >= 0.50 else get_color('good') for s in sims]
        
        ax.barh(range(len(labels)), sims, color=colors)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.set_xlabel('Similarity Score')
        ax.set_title('Similarity Score Distribution (Top Risk Patents)')
        ax.axvline(x=0.85, color='red', linestyle='--', alpha=0.5)
        ax.axvline(x=0.70, color='orange', linestyle='--', alpha=0.5)
        ax.set_xlim(0, 1)
        ax.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/2_similarity_distribution.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 2: Similarity Distribution", file=sys.stderr)
    
    # Chart 3: Geographic Coverage
    fig, ax = plt.subplots(figsize=(10, 6))
    
    geo = report['geographic_analysis']
    countries = list(geo['all_countries'].keys())[:10]
    counts = [geo['all_countries'][c] for c in countries]
    
    if countries:
        ax.barh(range(len(countries)), counts, color=get_color('primary'))
        ax.set_yticks(range(len(countries)))
        ax.set_yticklabels(countries)
        ax.set_xlabel('Number of Patents')
        ax.set_title('Patent Coverage by Country')
        ax.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/3_geography.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("  ✓ Chart 3: Geography", file=sys.stderr)

    # Chart 4: Patent Expiration Timeline
    try:
        top_risks = report.get('top_risks', [])
        # Build synthetic expiration years from patent number prefix (design patents ~15yr, utility ~20yr)
        # We derive an estimated expiry year from patent number where possible; fall back to bucketing by risk level.
        from datetime import datetime as _dt
        current_year = _dt.now().year

        timeline_data = {}  # year -> count
        for r in top_risks:
            pn = r.get('patent_number', '')
            # Heuristic: extract 4-digit year from patent number (e.g. US20190123456 → 2019)
            import re as _re
            year_match = _re.search(r'(19|20)\d{2}', pn)
            if year_match:
                filing_year = int(year_match.group())
                # Design patent: 15 yr term; utility: 20 yr
                term = 15 if pn.upper().startswith('USD') or pn.upper().startswith('CN3') else 20
                expiry_year = filing_year + term
            else:
                # Fallback: spread across next 5 years based on similarity bucket
                sim = r.get('similarity', 0)
                expiry_year = current_year + (1 if sim >= 0.85 else 3 if sim >= 0.70 else 5)
            timeline_data[expiry_year] = timeline_data.get(expiry_year, 0) + 1

        if timeline_data:
            years = sorted(timeline_data.keys())
            counts = [timeline_data[y] for y in years]
            bar_colors = [get_color('hot') if y <= current_year + 3 else get_color('warning') if y <= current_year + 7
                          else get_color('good') for y in years]

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh([str(y) for y in years], counts, color=bar_colors,
                           edgecolor='white', linewidth=1.5)

            for bar, cnt in zip(bars, counts):
                ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                        str(cnt), va='center', ha='left', fontsize=10, fontweight='bold')

            ax.set_xlabel('Number of Patents Expiring', fontsize=11, fontweight='bold')
            ax.set_title('PATENT EXPIRATION TIMELINE', fontsize=14, fontweight='bold', pad=15)
            ax.axvline(x=0, color='black', linewidth=0.8)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Legend
            from matplotlib.patches import Patch as _Patch
            legend_elements = [
                _Patch(facecolor=get_color('hot'), label='Expires ≤ 3 years'),
                _Patch(facecolor=get_color('warning'), label='Expires 4–7 years'),
                _Patch(facecolor=get_color('good'), label='Expires > 7 years'),
            ]
            ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

            plt.tight_layout()
            plt.savefig(f'{output_dir}/4_timeline.png', dpi=150, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close()
            print("  ✓ Chart 4: Timeline", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Could not generate timeline chart: {e}", file=sys.stderr)

    # Chart 5: Risk Matrix (similarity score vs legal status risk)
    try:
        top_risks = report.get('top_risks', [])
        if len(top_risks) >= 2:
            # Map legal status to a numeric axis value
            def _legal_risk_score(r):
                status = (r.get('legal_status') or '').lower()
                is_active = r.get('is_active')
                if is_active is True or 'active' in status or 'grant' in status:
                    return 0.9
                elif 'pending' in status or 'examination' in status:
                    return 0.6
                elif 'expired' in status or 'lapse' in status or 'abandon' in status:
                    return 0.1
                else:
                    return 0.5

            x_vals = [r.get('similarity', 0) for r in top_risks]
            y_vals = [_legal_risk_score(r) for r in top_risks]
            labels = [r.get('patent_number', '')[:12] for r in top_risks]

            point_colors = []
            for x, y in zip(x_vals, y_vals):
                combined = (x + y) / 2
                if combined >= 0.75:
                    point_colors.append(get_color('hot'))
                elif combined >= 0.55:
                    point_colors.append(get_color('secondary'))
                elif combined >= 0.40:
                    point_colors.append(get_color('warning'))
                else:
                    point_colors.append(get_color('good'))

            fig, ax = plt.subplots(figsize=(10, 8))
            scatter = ax.scatter(x_vals, y_vals, c=point_colors, s=120,
                                 alpha=0.85, edgecolors='white', linewidth=1.5, zorder=3)

            for lbl, x, y in zip(labels, x_vals, y_vals):
                ax.annotate(lbl, (x, y), textcoords='offset points', xytext=(6, 4),
                            fontsize=8, color='#333333')

            # Quadrant dividers
            ax.axhline(y=0.5, color='#BDBDBD', linestyle='--', linewidth=1.2)
            ax.axvline(x=0.6, color='#BDBDBD', linestyle='--', linewidth=1.2)

            # Quadrant labels
            ax.text(0.95, 0.95, 'CRITICAL\nRISK', transform=ax.transAxes,
                    fontsize=9, color=get_color('hot'), ha='right', va='top', fontweight='bold')
            ax.text(0.05, 0.95, 'Legal Risk\nOnly', transform=ax.transAxes,
                    fontsize=9, color=get_color('secondary'), ha='left', va='top')
            ax.text(0.95, 0.05, 'Similarity Risk\nOnly', transform=ax.transAxes,
                    fontsize=9, color=get_color('secondary'), ha='right', va='bottom')
            ax.text(0.05, 0.05, 'LOW\nRISK', transform=ax.transAxes,
                    fontsize=9, color=get_color('good'), ha='left', va='bottom', fontweight='bold')

            ax.set_xlabel('Similarity Score', fontsize=11, fontweight='bold')
            ax.set_ylabel('Legal Status Risk', fontsize=11, fontweight='bold')
            ax.set_title('RISK MATRIX: Similarity vs Legal Status', fontsize=14,
                         fontweight='bold', pad=15)
            ax.set_xlim(-0.05, 1.05)
            ax.set_ylim(-0.05, 1.1)
            ax.set_yticks([0.1, 0.5, 0.9])
            ax.set_yticklabels(['Expired/Lapsed', 'Pending', 'Active/Granted'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Legend
            from matplotlib.lines import Line2D as _Line2D
            legend_elements = [
                _Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('hot'), markersize=10, label='Critical'),
                _Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('secondary'), markersize=10, label='High'),
                _Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('warning'), markersize=10, label='Medium'),
                _Line2D([0], [0], marker='o', color='w', markerfacecolor=get_color('good'), markersize=10, label='Low'),
            ]
            ax.legend(handles=legend_elements, loc='center right', fontsize=9)

            plt.tight_layout()
            plt.savefig(f'{output_dir}/5_risk_matrix.png', dpi=150, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close()
            print("  ✓ Chart 5: Risk Matrix", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Could not generate risk matrix chart: {e}", file=sys.stderr)
    return [
        os.path.join(output_dir, name)
        for name in sorted(os.listdir(output_dir))
        if name.lower().endswith('.png')
    ]

def main():
    parser = argparse.ArgumentParser(description='Patent Report Generator')
    parser.add_argument('params', help='JSON parameters')
    parser.add_argument('--chart', help='Output directory for charts')
    parser.add_argument('--output', help='Output directory for report files')
    args = parser.parse_args()
    
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON: {e}'}, ensure_ascii=False))
        sys.exit(1)
    
    image_url = params.get('imageUrl', params.get('image_url', ''))
    product_name = params.get('productName', params.get('product_name', 'Unknown Product'))
    product_desc = params.get('productDescription', params.get('product_description', ''))
    target_markets = params.get('targetMarkets', params.get('target_markets', 'US,CN'))
    lang = params.get('lang', 'cn')
    top_risks_count = params.get('topRisks', params.get('top_risks', 10))
    include_claims = params.get('includeClaims', params.get('include_claims', False))
    
    if not image_url:
        print(json.dumps({'error': 'imageUrl is required'}, ensure_ascii=False))
        sys.exit(1)
    
    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'api_version': 'v1.0.0',
        'data_source': 'Zhihuiya (Zhihuiya)',
        'product_info': {
            'name': product_name,
            'description': product_desc,
            'image_url': image_url,
            'target_markets': target_markets
        }
    }
    
    # Step 1: Search design patents
    print(f"[1/6] Searching design patents...", file=sys.stderr)
    design_patents = search_design_patents(image_url, '', 50)
    print(f"    ✓ Found {len(design_patents)} design patents", file=sys.stderr)
    
    # Step 2: Search utility patents
    print(f"[2/6] Searching utility patents...", file=sys.stderr)
    utility_patents = search_utility_patents(image_url, 30)
    print(f"    ✓ Found {len(utility_patents)} utility patents", file=sys.stderr)
    
    # Step 3: Get legal status
    print(f"[3/6] Checking legal status...", file=sys.stderr)
    all_patent_ids = [p.get('patentId') for p in design_patents + utility_patents if p.get('patentId')]
    legal_status = get_legal_status(all_patent_ids[:100])
    print(f"    ✓ Got status for {len(legal_status)} patents", file=sys.stderr)
    
    # Step 4: Get patent families
    print(f"[4/6] Analyzing patent families...", file=sys.stderr)
    top_ids = [p.get('patentId') for p in sorted(design_patents + utility_patents, 
               key=lambda x: -float(x.get('score') or 0))[:20] if p.get('patentId')]
    family_map = get_patent_family(top_ids)
    print(f"    ✓ Got families for {len(family_map)} patents", file=sys.stderr)
    
    # Step 5: Get claims for top risks (optional — slow, skip unless includeClaims=true)
    claims_map = {}
    if include_claims:
        print(f"[5/6] Fetching claims...", file=sys.stderr)
        claims_map = get_claims(top_ids[:10], lang)
        print(f"    ✓ Got claims for {len(claims_map)} patents", file=sys.stderr)
    else:
        print(f"[5/6] Skipping claims (pass includeClaims:true to enable)", file=sys.stderr)
    
    # Step 6: Generate analysis
    print(f"[6/6] Generating report...", file=sys.stderr)
    
    # Risk assessment
    report['risk_assessment'] = calculate_risk_score(design_patents, utility_patents)
    
    # Top risks
    all_patents = design_patents + utility_patents
    report['top_risks'] = format_top_risks(all_patents, legal_status, family_map, 
                                           claims_map, top_risks_count)
    
    # Geographic analysis
    report['geographic_analysis'] = analyze_geography(design_patents, utility_patents,
                                                       family_map, target_markets)
    
    # Statistics
    report['statistics'] = {
        'design_patents_found': len(design_patents),
        'utility_patents_found': len(utility_patents),
        'total_patents_analyzed': len(all_patents),
        'active_patents': sum(1 for v in legal_status.values() if v.get('is_active')),
        'countries_with_patents': len(report['geographic_analysis']['all_countries'])
    }
    
    # Generate markdown report
    report['markdown_report'] = generate_markdown_report(report)
    
    # Generate charts
    if args.chart:
        print(f"Generating charts in {args.chart}...", file=sys.stderr)
        report['charts'] = generate_charts(report, args.chart) or []
    
    # Save report files
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        with open(f"{args.output}/report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        with open(f"{args.output}/report.md", 'w', encoding='utf-8') as f:
            f.write(report['markdown_report'])
        print(f"Report saved to {args.output}/", file=sys.stderr)
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
