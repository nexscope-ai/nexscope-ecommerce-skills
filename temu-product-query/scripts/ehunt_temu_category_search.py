#!/usr/bin/env python3
import json, os, sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

NEXSCOPE_API_KEY = os.environ.get('NEXSCOPE_API_KEY', '')
NEXSCOPE_PROXY_BASE = os.environ.get('NEXSCOPE_PROXY_BASE', '')
API_PATH = '/api/v1/tools/linkfox/ehunt/temu/temuCategorySearch'

def get_api_url():
    if not NEXSCOPE_API_KEY:
        print('Error: NEXSCOPE_API_KEY not configured.', file=sys.stderr)
        sys.exit(1)
    if not NEXSCOPE_PROXY_BASE:
        print('Error: NEXSCOPE_PROXY_BASE not configured.', file=sys.stderr)
        sys.exit(1)
    return NEXSCOPE_PROXY_BASE.rstrip('/') + API_PATH

def call_api(params):
    url = get_api_url()
    data = json.dumps(params).encode('utf-8')
    req = Request(url, data=data, headers={'Authorization': f'Bearer {NEXSCOPE_API_KEY}', 'Content-Type': 'application/json', 'User-Agent': 'NexScope-Skill/1.0'}, method='POST')
    try:
        with urlopen(req, timeout=60) as response:
            raw = json.loads(response.read().decode('utf-8'))
            if raw.get('code') == 0 and 'data' in raw:
                return raw['data']
            return raw
    except HTTPError as e:
        body = e.read().decode('utf-8') if e.fp else ''
        return {'error': f'HTTP {e.code}: {e.reason}', 'details': body, 'url': url}
    except URLError as e:
        return {'error': f'Connection failed: {e.reason}', 'url': url}

def main():
    if len(sys.argv) < 2:
        print('Usage: ehunt_temu_category_search.py <JSON>', file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}', file=sys.stderr)
        sys.exit(1)
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
