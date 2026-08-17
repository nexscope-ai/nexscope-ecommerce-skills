#!/usr/bin/env python3
"""Manage an Amazon connection without exposing provider credentials."""
import json, os, sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip().rstrip("/")
KEY = os.environ.get("NEXSCOPE_API_KEY", "").strip()
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
ROUTES = {'authorize': ('POST', '/api/skill/amazon/connections/amazon-ads/authorize'), 'status': ('GET', '/api/skill/amazon/connections/amazon-ads/status'), 'connections': ('GET', '/api/skill/amazon/connections/amazon-ads'), 'profiles': ('GET', '/api/skill/amazon/connections/amazon-ads/profiles')}

def main():
    if len(sys.argv) != 2:
        raise ValueError("Provide exactly one JSON object argument")
    params = json.loads(sys.argv[1])
    if not isinstance(params, dict):
        raise ValueError("The argument must be a JSON object")
    action = str(params.pop("action", "authorize")).lower()
    if action not in ROUTES:
        raise ValueError("Unknown action")
    method, path = ROUTES[action]
    if not BASE or not KEY:
        raise ValueError("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    data = None
    if method == "GET":
        if params:
            path += "?" + urlencode(params)
    else:
        data = json.dumps(params).encode()
    request = Request(BASE + path, data=data, headers={"Authorization": "Bearer " + KEY,
        "Content-Type": "application/json", "Accept": "application/json"}, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES: raise RuntimeError("Gateway response exceeds 32 MiB limit")
            value = json.loads(raw.decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"Gateway HTTP {error.code}") from error
    except URLError as error:
        raise RuntimeError("Gateway request failed") from error
    if not isinstance(value, dict) or value.get("code") != 0:
        raise RuntimeError("Gateway application failure" if isinstance(value, dict) else "Invalid gateway response")
    print(json.dumps(value.get("data"), indent=2, ensure_ascii=True))

if __name__ == "__main__":
    try: main()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr); raise SystemExit(1)
