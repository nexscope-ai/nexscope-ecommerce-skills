#!/usr/bin/env python3
"""
SP Search Term Impression Share Report - Nexscope Skill
Call the /api/v1/tools/research/amazonAds/developerProxy endpoint.

Usage:
  python get_sp_search_impression_share.py '<JSON parameters>'           # Automatic: print small results in full; save large results and print a summary
  python get_sp_search_impression_share.py '<JSON parameters>' --inline  # Force full output to stdout
  python get_sp_search_impression_share.py '<JSON parameters>' --no-cache # Bypass the 24h cache of successful results

Output policy (default script behavior):
  - **Always** save the full response to `<cwd>/nexscope/<YYYY-MM-DD>/<session>/data/ecommerce.amazon-ads-sp-insights-report-<timestamp>.json` (`<cwd>` is the working directory when the script runs, or the current project in Claude Code; `<session>` comes from SESSION_ID and groups outputs by user task; **do not write to /tmp**; fail if the working directory is not writable)
  - Response body <= 8 KB: save it, then print the complete JSON to stdout
  - Response body > 8 KB: save it, then print only a summary (top-level fields, common counts such as `total`/`costToken`, and the largest list length plus its first 3 items)
  - Add `--inline` to force full output to stdout (the response is still saved)
"""

import json
import re
import hashlib
import os
import sys
import time
import secrets
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from reporting_v1_workflow import run_report_workflow


API_PATH = "/api/v1/tools/research/amazonAds/developerProxy"
SLUG = "ecommerce.amazon-ads-sp-insights-report"
REPORT_KIND = "search-impression-share"
REQUIRED_SKILL = "ecommerce.amazon-ads-api-access"
DEPENDENCY_EXIT_CODE = 42

# Print responses up to this byte threshold in full; all responses are still saved
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60

_SESSION_CACHE: dict[str, str] = {}

def get_api_base() -> str:
    """Use NEXSCOPE_PROXY_BASE when set; otherwise use the production gateway base URL."""
    return (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").rstrip("/")

def get_api_url():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared"))
    return get_api_base() + API_PATH


def get_api_key():
    key = os.environ.get("NEXSCOPE_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://www.nexscope.ai/help/skills-external-access?co-from=skillNS to obtain your Key\n"
            "2. Set the environment variable: export NEXSCOPE_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def ensure_auth_skill_available():
    """Use the same local dependency guard as the existing Amazon Ads skills."""
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        print(
            "DEPENDENCY_MISSING: " + json.dumps({
                "missingSkill": REQUIRED_SKILL,
                "reason": "check_auth_dependency.py not found next to the entry script",
            }, ensure_ascii=False),
            file=sys.stderr,
        )
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)], capture_output=True, text=True, timeout=10
        )
    except Exception as exc:
        print(
            "DEPENDENCY_MISSING: " + json.dumps({
                "missingSkill": REQUIRED_SKILL,
                "reason": "Failed to run dependency check: %s" % exc,
            }, ensure_ascii=False),
            file=sys.stderr,
        )
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)





def _billing_from_headers(headers):
    """Return billing and trace evidence from Nexscope response headers."""
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
        except (TypeError, ValueError):
            billing["costTokenRaw"] = str(raw_token)
    if raw_credit not in (None, ""):
        billing["reportedCostCredit"] = str(raw_credit)
    if trace_id:
        billing["traceId"] = str(trace_id)
    return billing


def _unwrap_nexscope(payload, headers=None):
    """Validate the Nexscope envelope and return the business payload."""
    billing = _billing_from_headers(headers)
    if not isinstance(payload, dict):
        return {"error": "Invalid Nexscope response", "response": payload}
    if type(payload.get("code")) is not int or "data" not in payload:
        return {"error": "Invalid Nexscope response envelope", "response": payload}
    if payload.get("code") != 0:
        return {
            "error": "Nexscope gateway error",
            "code": payload.get("code"),
            "msg": payload.get("msg"),
            "response": payload,
            "_nexscope": {"billing": billing} if billing else {},
        }
    business = payload.get("data")
    if not isinstance(business, dict):
        return {"error": "Invalid Nexscope business payload", "response": payload}
    metadata = {key: payload.get(key) for key in ("code", "msg", "ts", "time", "cost", "traceId") if key in payload}
    if billing:
        metadata["billing"] = billing
    business = dict(business)
    business["_nexscope"] = metadata
    return business


REQUIRED_FIELDS = ()
SUPPORTED_COUNTRIES = {"br", "de", "es", "fr", "gb", "id", "it", "jp", "mx", "my", "ph", "sg", "th", "us", "vn"}


def validate_params(params):
    """Reject malformed or incomplete requests before any network call."""
    if not isinstance(params, dict):
        return "top-level JSON must be an object"
    missing = [key for key in REQUIRED_FIELDS if params.get(key) in (None, "")]
    if missing:
        return "missing required parameter(s): " + ", ".join(missing)
    if "country" in params:
        country = params.get("country")
        if not isinstance(country, str) or country.lower() not in SUPPORTED_COUNTRIES:
            return "country must be one of: " + ", ".join(sorted(SUPPORTED_COUNTRIES))
    for key in ("page", "size", "pageSize"):
        if key not in params:
            continue
        value = params[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            return key + " must be a positive integer"
        if key == "size" and value > 200:
            return "size must be between 1 and 200"
        if key == "pageSize" and value > 20:
            return "pageSize must be between 1 and 20"
    if isinstance(params.get("page"), int) and isinstance(params.get("size"), int):
        if params["page"] * params["size"] > 10000:
            return "page * size must not exceed 10000"
    if "date" in params and (not isinstance(params["date"], str) or not re.fullmatch(r"\d{8}", params["date"])):
        return "date must use YYYYMMDD"
    if "granularity" in params and str(params["granularity"]).lower() not in {"daily", "weekly", "monthly", "0", "1", "2"}:
        return "granularity must be daily, weekly, monthly, 0, 1, or 2"
    for key, value in params.items():
        if not key.endswith("Min"):
            continue
        peer = key[:-3] + "Max"
        if peer in params and isinstance(value, (int, float)) and isinstance(params[peer], (int, float)) and value > params[peer]:
            return key + " must not exceed " + peer
    return None


def call_api(params):
    api_url = get_api_url()
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "User-Agent": "Nexscope-Skill/1.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(
        api_url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return _unwrap_nexscope(payload, response.headers)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            payload = json.loads(body) if body else {"error": f"HTTP {e.code}: {e.reason}"}
            return _unwrap_nexscope(payload, e.headers)
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def _cache_key(params):
    raw = json.dumps({"reportKind": REPORT_KIND, "params": params}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "nexscope", ".cache", SLUG, _cache_session_id())
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _cache_session_id():
    """Keep caches isolated by explicit session while remaining stable across CLI processes."""
    raw = (os.environ.get("SESSION_ID") or "default").strip() or "default"
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in raw)[:80]
    return safe if safe and safe not in (".", "..") else "default"


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            for item in payload.get("dataFiles") or []:
                if isinstance(item, dict) and item.get("path") and not os.path.isfile(item["path"]):
                    return None
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _find_main_list(obj):
    """Recursively find the list field with the most items, without assuming field names or structure."""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """Print a compact summary."""
    envelope = result.get("_nexscope") if isinstance(result, dict) else None
    if isinstance(envelope, dict):
        print("Nexscope code: {}; msg: {}".format(envelope.get("code"), envelope.get("msg")))
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")

    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))

def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    """Create _meta.json for a new session and append an entry to index.jsonl."""
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _format_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _format_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass

def _nexscope_root() -> str:
    """Select a writable nexscope root directory.

    Priority: nexscope/ under the first $ACPX_WORKSPACES path, then nexscope/ under the current working directory.
    Fail explicitly if neither location is writable; do not fall back to the home or system temporary directory.
    Cache the selected directory in this process so all saved paths remain consistent within a run.
    """
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    # 1. ACPX_WORKSPACES (actual workspace, highest priority)
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(os.pathsep)[0].strip()
        if acpx:
            candidates.append(os.path.join(acpx, "nexscope"))
    # 2. Current working directory
    candidates.append(os.path.join(os.getcwd(), "nexscope"))
    for root in candidates:
        try:
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("")
            os.remove(probe)
        except OSError:
            continue
        root = os.path.abspath(root)
        _SESSION_CACHE["_root"] = root
        return root
    raise OSError("No writable workspace directory available for Nexscope outputs")

def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))

def _session_id(ts: float) -> str:
    """Use SESSION_ID when set; otherwise generate HHMMSS-<6 hex>, stable within this process."""
    env = os.environ.get("SESSION_ID")
    if env:
        raw = env.strip()
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in raw)[:80]
        if safe and safe not in (".", ".."):
            return safe
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = (
            time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
        )
    return _SESSION_CACHE["_auto"]

def _ensure_session(ts: float) -> tuple[str, str]:
    """Return (nexscope_root, session_dir), ensuring session_dir exists."""
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _nexscope_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir

def _update_meta(session_dir: str, *, skill: str, kind: str, file_rel: str, ts: float) -> None:
    """Register this output in its _meta.json category list; kind is one of {data, deliverable, media}."""
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    bucket = {"data": "data_files", "deliverable": "deliverables", "media": "media_files"}.get(
        kind, "data_files"
    )
    files = meta.setdefault(bucket, [])
    if file_rel not in files:  # Avoid duplicate entries when the same path is registered repeatedly or concurrently
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """Save raw Skill data to <session>/data/<slug>-<ts>.<ext>."""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "data")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{slug}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out

def _resolve_output_path(ts):
    """Save to the selected nexscope root under <date>/<session>/data/<slug>-<ts>.json, grouping by SESSION_ID."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_shared"))
    return resolve_data_path(SLUG, ts)


def main():
    argv = sys.argv[1:]
    inline = False
    use_cache = True
    if "--inline" in argv:
        inline = True
        argv = [a for a in argv if a != "--inline"]
    if "--no-cache" in argv:
        use_cache = False
        argv = [a for a in argv if a != "--no-cache"]

    if not argv:
        print(
            "Usage: get_sp_search_impression_share.py '<JSON parameters>' [--inline] [--no-cache]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    ensure_auth_skill_available()

    validation_error = validate_params(params)
    if validation_error:
        print("Invalid parameters: " + validation_error, file=sys.stderr)
        sys.exit(1)

    cache_path = _cache_path(params)
    result = _load_cache(cache_path) if use_cache else None
    if result is None:
        result = run_report_workflow(params, call_api, resolve_data_path, REPORT_KIND, SLUG)
        if use_cache and result.get("_cacheable", True):
            _save_cache(cache_path, result)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = time.time()
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
        if result.get("_cache", {}).get("hit"):
            print(f"Cache hit: {cache_path}")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        if result.get("_cache", {}).get("hit"):
            print(f"Cache hit: {cache_path}", file=sys.stderr)
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
