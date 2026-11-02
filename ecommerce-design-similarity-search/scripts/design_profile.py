#!/usr/bin/env python3
"""Retrieve design-registration details through Nexscope; preserve all source matches."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

PATH = "/api/v1/tools/research/ecDw/designProfile"
FIELDS = {"designRegistrationIds", "primaryIdentifier", "jurisdictionIso2"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate(params):
    if not isinstance(params, dict) or set(params) - FIELDS:
        raise ValueError("Use only documented registration detail fields.")
    if ("designRegistrationIds" in params) == ("primaryIdentifier" in params):
        raise ValueError("Provide exactly one of designRegistrationIds or primaryIdentifier.")
    def identifier(value):
        if not isinstance(value, str) or not 1 <= len(value) <= 128 or value != value.strip() or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in value):
            raise ValueError("Identifiers must be trimmed strings of 1–128 characters; preserve leading zeros.")
    if "designRegistrationIds" in params:
        values = params["designRegistrationIds"]
        if not isinstance(values, list) or not 1 <= len(values) <= 200:
            raise ValueError("designRegistrationIds must contain 1–200 unique strings; never split automatically.")
        for value in values:
            identifier(value)
        if len(set(values)) != len(values):
            raise ValueError("Registration IDs must be unique.")
        if "jurisdictionIso2" in params:
            raise ValueError("jurisdictionIso2 is only allowed with primaryIdentifier.")
    else:
        identifier(params["primaryIdentifier"])
        if "jurisdictionIso2" in params and (not isinstance(params["jurisdictionIso2"], str) or not re.fullmatch(r"[A-Za-z]{2}", params["jurisdictionIso2"])):
            raise ValueError("jurisdictionIso2 must contain exactly two English letters.")


def business(result):
    if not isinstance(result, dict) or type(result.get("code")) is not int or result["code"] != 0:
        raise ValueError("Nexscope platform failure; inspect the saved response. HTTP 200 alone is not success.")
    gateway = result.get("data")
    upstream = gateway.get("data") if isinstance(gateway, dict) else None
    if not isinstance(upstream, dict) or "error" in upstream or "error" in gateway or upstream.get("code") != "OK":
        raise ValueError("Source retrieval did not succeed; this is not an empty detail list.")
    data = upstream.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Missing registration items; do not treat malformed data as zero matches.")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params-file", required=True, help="UTF-8 JSON; BOM accepted. Do not store credentials.")
    parser.add_argument("--out", default="nexscope/design-profile")
    parser.add_argument("--execute", action="store_true", help="Send one approved request. Invoking the API consumes credits.")
    parser.add_argument("--no-cache", action="store_true", help="Refresh deliberately; may consume credits again.")
    parser.add_argument("--inline", action="store_true")
    args = parser.parse_args()
    params = json.loads(Path(args.params_file).read_text(encoding="utf-8-sig"))
    validate(params)
    if not args.execute:
        print(json.dumps({"mode": "plan", "endpoint": PATH, "fields": sorted(params), "note": "No request sent. Invoking the API consumes credits."}))
        return
    key = os.environ.get("NEXSCOPE_API_KEY")
    if not key:
        raise ValueError("Set NEXSCOPE_API_KEY. Do not pass other credentials.")
    if any(ord(c) < 32 or ord(c) > 126 for c in key):
        raise ValueError("NEXSCOPE_API_KEY must be an ASCII header value.")
    origin = os.environ.get("NEXSCOPE_PROXY_BASE", "https://api.nexscope.ai").rstrip("/")
    url = urllib.parse.urlsplit(origin)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in {"", "/"}:
        raise ValueError("NEXSCOPE_PROXY_BASE must be an origin without credentials or a path.")
    if url.scheme != "https" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Use HTTPS except for a local test server.")
    folder = Path(args.out).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    fingerprint = hashlib.sha256((origin + PATH + hashlib.sha256(key.encode()).hexdigest() + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    cache = folder / ("cache-" + fingerprint + ".json")
    if not args.no_cache and cache.exists() and 0 <= time.time() - cache.stat().st_mtime < 86400:
        saved = json.loads(cache.read_text(encoding="utf-8"))
        data = business(saved["response"])
        print(json.dumps({"cacheHit": True, "newRequest": False, "file": str(cache), "itemCount": len(data["items"]), "note": "Cached fees belong to the original request; key validity has not been rechecked online."}))
        return
    path = folder / ("result-" + uuid.uuid4().hex + ".json")
    with path.open("x", encoding="utf-8") as stream:
        request = urllib.request.Request(origin + PATH, method="POST", data=json.dumps(params).encode(),
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "Nexscope-Design-Profile/1.0"})
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=150) as response:
                result = json.loads(response.read().decode("utf-8"))
                receipt = {h: response.headers.get(h) for h in ("X-Cost-Credit", "X-Cost-Token", "X-Trace-Id") if response.headers.get(h) is not None}
                saved = {"response": result, "billingHeaders": receipt}
                json.dump(saved, stream, ensure_ascii=False, indent=2)
        except urllib.error.HTTPError as error:
            json.dump({"httpStatus": error.code, "error": "HTTP failure. No retry or redirect."}, stream)
            raise ValueError(f"HTTP {error.code}; see {path}. 401: Nexscope authentication; 402: insufficient credits.") from None
        except (ValueError, OSError) as error:
            stream.seek(0)
            stream.truncate()
            json.dump({"error": "Transport or malformed response. No automatic retry."}, stream)
            raise ValueError(f"Request failed; see {path}. Do not resubmit automatically.") from error
    data = business(result)
    cache.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.inline:
        print(json.dumps(saved, ensure_ascii=False))
    else:
        print(json.dumps({"file": str(path), "itemCount": len(data["items"]), "items": data["items"][:3],
                          "returned": data.get("returned"), "execution": data.get("execution"), "billingHeaders": receipt}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print("Error: " + str(error), file=sys.stderr)
        raise SystemExit(1)
