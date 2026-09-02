#!/usr/bin/env python3
"""NexScope proxy client for Shopee public product details."""

import hashlib
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

API_PATH = "/api/v1/tools/research/shopee/product/detail"
SLUG = "ecommerce-shopee-product-detail"
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
CREDIT_RATE = 0.001041
SUPPORTED_HOSTS = {
    "shopee.sg",
    "shopee.co.id",
    "shopee.com.my",
    "shopee.ph",
    "shopee.co.th",
    "shopee.tw",
    "shopee.vn",
    "shopee.com.br",
}
PRODUCT_SUFFIX = re.compile(r"-i\.(\d+)\.(\d+)$")


def validate_params(params):
    if not isinstance(params, dict):
        raise ValueError("Params must be a JSON object")
    if set(params) != {"productUrl"}:
        raise ValueError("Exactly one parameter is allowed: productUrl")
    product_url = params["productUrl"]
    if not isinstance(product_url, str) or not product_url.strip():
        raise ValueError("productUrl must be a non-empty string")
    parsed = urlsplit(product_url.strip())
    if parsed.scheme.lower() != "https":
        raise ValueError("productUrl must use HTTPS")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("productUrl contains an invalid port") from error
    if (parsed.hostname or "").lower() not in SUPPORTED_HOSTS:
        raise ValueError("productUrl host is not supported")
    if port not in (None, 443):
        raise ValueError("productUrl port must be omitted or 443")
    match = PRODUCT_SUFFIX.search(parsed.path.rstrip("/"))
    if not match:
        raise ValueError("productUrl path must end with -i.<shopId>.<itemId>")
    return match.group(1), match.group(2)


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    directory = os.path.join(os.getcwd(), "nexscope", ".cache", SLUG)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{SLUG}-{_cache_key(params)}.json")


def load_cache(params):
    path = _cache_path(params)
    if not os.path.isfile(path) or time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def save_cache(params, payload):
    try:
        with open(_cache_path(params), "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _nexscope_root():
    candidates = [
        os.path.join(os.getcwd(), "nexscope"),
        os.path.join(os.path.expanduser("~"), "nexscope"),
    ]
    for candidate in candidates:
        try:
            os.makedirs(candidate, exist_ok=True)
            probe = os.path.join(candidate, ".write-probe")
            with open(probe, "w", encoding="utf-8"):
                pass
            os.remove(probe)
            return os.path.abspath(candidate)
        except OSError:
            continue
    import tempfile

    return os.path.join(tempfile.gettempdir(), "nexscope")


def resolve_output(ts=None):
    ts = time.time() if ts is None else ts
    date_string = time.strftime("%Y-%m-%d", time.localtime(ts))
    session_id = os.environ.get("SESSION_ID", "").strip() or time.strftime(
        "%H%M%S", time.localtime(ts)
    )
    directory = os.path.join(_nexscope_root(), date_string, session_id, "data")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"{SLUG}-{int(ts * 1_000_000)}.json")


def _find_longest_list(value, prefix=""):
    best = (None, -1, None)
    if isinstance(value, list):
        return prefix, len(value), value
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            candidate = _find_longest_list(child, path)
            if candidate[1] > best[1]:
                best = candidate
    return best


def summarize(result):
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for key in ("errcode", "code", "errmsg", "msg", "total", "costToken", "costTime"):
        if key in result and isinstance(result[key], (int, float, bool, str)):
            print(f"  {key}: {result[key]}")
    path, count, values = _find_longest_list(result)
    if path and values:
        print(f"\nLongest list: `{path}` ({count} items)")
        print(json.dumps(values[:3], indent=2, ensure_ascii=False))


def _billing_from_headers(headers):
    """Return NexScope billing evidence derived from response headers."""
    if headers is None:
        return {}
    def header_value(name):
        value = headers.get(name)
        if isinstance(value, (list, tuple)):
            return value[-1] if value else None
        return value

    raw_token = header_value("X-Cost-Token")
    raw_credit = header_value("X-Cost-Credit")
    trace_id = header_value("X-Kong-Trace-Id")
    billing = {}
    if raw_token not in (None, ""):
        try:
            token = int(raw_token)
            billing["costToken"] = token
            billing["calculatedCredit"] = round(token * CREDIT_RATE, 6)
            billing["creditRate"] = CREDIT_RATE
        except (TypeError, ValueError):
            billing["costTokenRaw"] = str(raw_token)
    if raw_credit not in (None, ""):
        billing["reportedCostCredit"] = str(raw_credit)
    if trace_id:
        billing["traceId"] = str(trace_id)
    return billing


def call_api(params):
    validate_params(params)
    base = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip()
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not base or not key:
        raise SystemExit("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    headers = {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    for name in ("SESSION_ID", "MESSAGE_ID", "MODE_ID", "APP_NAME"):
        value = os.environ.get(name, "")
        if value:
            headers[name] = value
    request = Request(
        base.rstrip("/") + API_PATH,
        data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=150) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if isinstance(payload, dict):
                payload.setdefault("_nexscope", {})["billing"] = _billing_from_headers(
                    response.headers
                )
            return payload
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace") if error.fp else ""
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                payload.setdefault("_nexscope", {})["billing"] = _billing_from_headers(
                    error.headers
                )
            return payload
        except ValueError:
            return {"error": f"HTTP {error.code}: {error.reason}", "details": raw}
    except URLError as error:
        return {"error": f"Connection failed: {error.reason}"}


def validate_response(result, expected_shop_id, expected_item_id):
    if not isinstance(result, dict):
        return result
    envelope = result
    if "code" in envelope:
        if envelope.get("code") != 0:
            return {
                "error": "NexScope gateway error",
                "code": envelope.get("code"),
                "msg": envelope.get("msg"),
                "response": envelope,
            }
        result = envelope.get("data")
        if not isinstance(result, dict):
            return {"error": "Invalid NexScope business payload", "response": envelope}
    if result.get("errcode") != 200:
        return result
    products = result.get("data")
    if not isinstance(products, list) or len(products) != 1:
        return {"error": "Gateway success response must contain exactly one product", "response": result}
    product = products[0]
    if not isinstance(product, dict):
        return {"error": "Gateway returned an invalid product object", "response": result}
    if str(product.get("shopId")) != expected_shop_id or str(product.get("itemId")) != expected_item_id:
        return {"error": "Gateway returned a product that does not match the requested URL", "response": result}
    return envelope


def main():
    inline = "--inline" in sys.argv[1:]
    use_cache = "--no-cache" not in sys.argv[1:]
    arguments = [arg for arg in sys.argv[1:] if arg not in {"--inline", "--no-cache"}]
    if len(arguments) != 1:
        sys.exit(f"Usage: {sys.argv[0]} '<JSON params>' [--inline] [--no-cache]")
    try:
        params = json.loads(arguments[0])
        expected_shop_id, expected_item_id = validate_params(params)
    except (json.JSONDecodeError, ValueError) as error:
        sys.exit(f"Invalid parameters: {error}")

    result = load_cache(params) if use_cache else None
    if result is None:
        result = validate_response(call_api(params), expected_shop_id, expected_item_id)
        if use_cache:
            save_cache(params, result)

    serialized = json.dumps(result, ensure_ascii=False)
    output_path = resolve_output()
    try:
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
        print(f"Saved full response: {output_path} ({len(serialized)} bytes)")
        if isinstance(result, dict) and result.get("_cache", {}).get("hit"):
            print("Cache hit")
    except OSError as error:
        print(f"Failed to save to {output_path}: {error}", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
