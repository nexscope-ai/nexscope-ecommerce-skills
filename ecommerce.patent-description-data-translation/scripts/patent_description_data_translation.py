#!/usr/bin/env python3
"""Standard-library proxy client for /zhihuiya/descriptionDataTranslated."""
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_PATH = '/zhihuiya/descriptionDataTranslated'

def call_api(params):
    base = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip()
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not base or not key:
        raise SystemExit("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    body = json.dumps(params, ensure_ascii=False).encode("utf-8")
    request = Request(base.rstrip("/") + API_PATH, data=body, method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace") if error.fp else ""
        try:
            return json.loads(raw)
        except ValueError:
            return {"error": "HTTP {}: {}".format(error.code, error.reason), "details": raw}
    except URLError as error:
        return {"error": "Connection failed: {}".format(error.reason)}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: {} '<JSON object>'".format(sys.argv[0]))
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as error:
        raise SystemExit("Invalid JSON parameters: {}".format(error))
    if not isinstance(params, dict):
        raise SystemExit("Parameters must be a JSON object")
    print(json.dumps(call_api(params), ensure_ascii=False))

if __name__ == "__main__":
    main()
