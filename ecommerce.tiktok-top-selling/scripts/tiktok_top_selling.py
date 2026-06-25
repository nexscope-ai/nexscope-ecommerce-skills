#!/usr/bin/env python3
"""TikTok Top Selling Rankings - NexScope Skill"""

import json, os, sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

NEXSCOPE_API_KEY = os.environ.get("NEXSCOPE_API_KEY", "")
NEXSCOPE_PROXY_BASE = os.environ.get("NEXSCOPE_PROXY_BASE", "")
API_PATH = "/api/v1/tools/linkfox/fastmoss/productRankTopSelling"


def get_api_url():
    if not NEXSCOPE_API_KEY:
        print("Error: NEXSCOPE_API_KEY not configured.", file=sys.stderr)
        sys.exit(1)
    if not NEXSCOPE_PROXY_BASE:
        print("Error: NEXSCOPE_PROXY_BASE not configured.", file=sys.stderr)
        sys.exit(1)
    return NEXSCOPE_PROXY_BASE.rstrip("/") + API_PATH


def call_api(params: dict) -> dict:
    url = get_api_url()
    data = json.dumps(params).encode("utf-8")
    req = Request(url, data=data, headers={
        "Authorization": f"Bearer {NEXSCOPE_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "NexScope-Skill/1.0",
    }, method="POST")
    try:
        with urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            if raw.get("code") == 0 and "data" in raw:
                return raw["data"]
            return raw
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: fastmoss_product_rank_top_selling.py '<JSON params>'", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
