"""Provider-neutral implementation documentation."""

from __future__ import annotations

import json
import os
import re
import secrets
import time
from typing import Optional


_SAFE_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_slug(slug: str, fallback: str = "nexscope") -> str:
    """Provider-neutral implementation documentation."""
    s = _SAFE_SLUG_RE.sub("-", (slug or "").strip())
    s = s.strip("-._")[:80].rstrip("-._")
    return s or fallback


def get_api_base() -> str:
    """value：env NEXSCOPE_PROXY_BASE value，value。"""
    base = (os.environ.get("NEXSCOPE_PROXY_BASE") or "").rstrip("/")
    if not base:
        raise RuntimeError("Set NEXSCOPE_PROXY_BASE before running this gateway client")
    return base
_SESSION_CACHE: dict[str, str] = {}


def _format_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def _session_id(ts: float) -> str:
    """value env SESSION_ID；value HHMMSS-<6 hex> value（value）。"""
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = (
            time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
        )
    return _SESSION_CACHE["_auto"]


def _nexscope_root() -> str:
    """Provider-neutral implementation documentation."""
    cached = _SESSION_CACHE.get("_root")
    if cached:
        return cached
    candidates = []
    # 1. NEXSCOPE_WORKSPACES（implementation，implementation）
    acpx = (os.environ.get("NEXSCOPE_WORKSPACES") or "").strip()
    if acpx:
        acpx = acpx.split(os.pathsep)[0].strip()
        if acpx:
            candidates.append(os.path.join(acpx, "nexscope"))
    # 2. implementation
    candidates.append(os.path.join(os.getcwd(), "nexscope"))
    # 3. implementation
    candidates.append(os.path.join(os.path.expanduser("~"), "nexscope"))
    # 4. implementation
    import tempfile
    candidates.append(os.path.join(tempfile.gettempdir(), "nexscope"))

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
    fallback = os.path.abspath(candidates[-1])
    _SESSION_CACHE["_root"] = fallback
    return fallback


def _ensure_session(ts: float) -> tuple[str, str]:
    """value (nexscope_root, session_dir)；session_dir value。"""
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    sid = _session_id(ts)
    root = _nexscope_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _ensure_meta(root, session_dir, date_str, sid, ts)
    return root, session_dir


def _timestamp_suffix(ts: float) -> str:
    """value，value。"""
    return str(int(ts * 1_000_000))


def _ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    """value _meta.json，value index.jsonl value。"""
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


def _update_meta(session_dir: str, *, skill: str, kind: str, file_rel: str, ts: float) -> None:
    """value _meta.json value。kind ∈ {data, deliverable, media}。"""
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
    if file_rel not in files:  # implementation：implementation
        files.append(file_rel)
    meta["last_used_at"] = _format_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def resolve_data_path(slug: str, ts: float, ext: str = "json") -> str:
    """standard skill value <session>/data/<slug>-<ts>.<ext>。"""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "data")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{_safe_slug(slug)}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="data", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


def resolve_report_path(slug: str, ts: float, ext: str) -> str:
    """value（report-generator）value <session>/reports/<slug>-<ts>.<ext>。"""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "reports")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{_safe_slug(slug, 'nexscope-report')}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="deliverable", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


def resolve_media_path(slug: str, ts: float, ext: str) -> str:
    """value/value/value <session>/media/<slug>-<ts>.<ext>。"""
    _, session_dir = _ensure_session(ts)
    sub = os.path.join(session_dir, "media")
    os.makedirs(sub, exist_ok=True)
    out = os.path.join(sub, f"{_safe_slug(slug)}-{int(ts * 1_000_000)}.{ext}")
    _update_meta(session_dir, skill=slug, kind="media", file_rel=os.path.relpath(out, session_dir), ts=ts)
    return out


def session_root(ts: Optional[float] = None) -> str:
    """value session value（value）。"""
    if ts is None:
        ts = time.time()
    _, session_dir = _ensure_session(ts)
    return session_dir


def _get_agent_base() -> str:
    """tool-gateway value：NEXSCOPE_PROXY_BASE value，value。"""
    base = (os.environ.get("NEXSCOPE_PROXY_BASE") or "").rstrip("/")
    if not base:
        raise RuntimeError("Set NEXSCOPE_PROXY_BASE before running this gateway client")
    return base
def _parse_endpoint(endpoint: str) -> tuple[str, str]:
    """Provider-neutral implementation documentation."""
    ep = (endpoint or "").strip().rstrip("/")
    if ep.startswith("https://"):
        return ep, ep[len("https://"):]
    if ep.startswith("http://"):
        return ep, ep[len("http://"):]
    return f"https://{ep}", ep


def get_sts_voucher() -> dict:
    """Provider-neutral implementation documentation."""
    import sys
    import urllib.error
    from urllib.request import urlopen, Request

    base = _get_agent_base()
    api_token = os.environ.get("NEXSCOPE_API_KEY") or ""
    url = f"{base}/oss/getStsVoucherByAPI"

    last_exc: Exception = RuntimeError("unknownError")
    body: dict = {}
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))  # 1s, 2s
        req = Request(
            url,
            method="POST",
            data=b"{}",
            headers={"Content-Type": "application/json", "Authorization": api_token},
        )
        try:
            with urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode())
            break
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read().decode()[:300]
            last_exc = RuntimeError(f"getStsVoucherByAPI HTTP {status}: {raw}")
            if status not in (408, 429, 500, 502, 503, 504):
                raise last_exc
        except Exception as e:
            last_exc = RuntimeError(f"getStsVoucherByAPI text: {e}")
            print(f"[get_sts_voucher] attempt {attempt+1}/3 text: {e}", file=sys.stderr)
    else:
        raise last_exc

    if not isinstance(body, dict):
        raise RuntimeError(f"getStsVoucherByAPI text: {body!r}")

    errcode = body.get("errcode")
    if errcode is not None and errcode != 200:
        raise RuntimeError(
            f"getStsVoucherByAPI textError: errcode={errcode}, "
            f"msg={body.get('errmsg', body.get('message', ''))}"
        )

    raw_voucher = body.get("data") if isinstance(body.get("data"), dict) else body
    if not isinstance(raw_voucher, dict):
        raise RuntimeError(f"getStsVoucherByAPI textmissingtext: {body!r}")

    if "ErrorCode" in raw_voucher:
        raise RuntimeError(
            f"STS text: {raw_voucher['ErrorCode']} - {raw_voucher.get('ErrorMessage', '')}"
        )

    voucher = dict(raw_voucher)
    for key in ("maxFileSize", "maxFileCount"):
        val = voucher.get(key)
        if isinstance(val, str) and val.strip().isdigit():
            voucher[key] = int(val.strip())

    return voucher


def upload_file(
    local_path: str,
    *,
    slug: Optional[str] = None,
    ts: Optional[float] = None,
    voucher: Optional[dict] = None,
) -> dict:
    """Provider-neutral implementation documentation."""
    try:
        import oss2
    except ImportError:
        raise RuntimeError("missing oss2 value，value: pip install oss2")

    import uuid as _uuid

    if ts is None:
        ts = time.time()
    if slug is None:
        slug = os.path.splitext(os.path.basename(local_path))[0]

    ext = os.path.splitext(local_path)[1].lstrip(".").lower()
    if not ext:
        ext = "bin"

    if voucher is None:
        voucher = get_sts_voucher()

    file_size = os.path.getsize(local_path)

    max_size = voucher.get("maxFileSize")
    if isinstance(max_size, int) and max_size > 0 and file_size > max_size:
        raise RuntimeError(
            f"text {file_size} text OSS text {max_size} text"
            f"（text {max_size // (1024 * 1024)}MB）: {local_path}"
        )

    supported = voucher.get("supportedTypes")
    if isinstance(supported, str) and supported.strip():
        allowed = {t.strip().lower() for t in supported.split(",") if t.strip()}
        if allowed and ext not in allowed:
            raise RuntimeError(
                f"text .{ext} text OSS text：{sorted(allowed)}（{local_path}）"
            )

    dir_ = (voucher.get("dir") or "tmp").rstrip("/")
    date_prefix = time.strftime("%Y/%m", time.localtime(ts))
    object_key = f"{dir_}/{date_prefix}/{_uuid.uuid4().hex}.{ext}"

    endpoint_url, endpoint_host = _parse_endpoint(voucher["endpoint"])
    bucket_name = voucher["bucketName"]

    auth = oss2.StsAuth(
        voucher["accessKeyId"],
        voucher["accessKeySecret"],
        voucher["securityToken"],
    )
    bucket = oss2.Bucket(auth, endpoint_url, bucket_name)

    with open(local_path, "rb") as f:
        bucket.put_object(object_key, f)

    url = f"https://{bucket_name}.{endpoint_host}/{object_key}"

    _, session_dir = _ensure_session(ts)
    _update_meta(session_dir, skill=slug, kind="deliverable", file_rel=url, ts=ts)

    return {
        "url": url,
        "path": object_key,
        "name": os.path.basename(local_path),
        "size": file_size,
        "ext": ext,
    }


NL_PLACEHOLDER = "⏎"


def encode_nl(text: str) -> str:
    """Provider-neutral implementation documentation."""
    if not isinstance(text, str):
        return text
    # implementation（implementation）
    text = text.replace("\\r\\n", NL_PLACEHOLDER)
    text = text.replace("\\n", NL_PLACEHOLDER)
    text = text.replace("\\r", NL_PLACEHOLDER)
    # implementation
    text = text.replace("\r\n", NL_PLACEHOLDER)
    text = text.replace("\r", NL_PLACEHOLDER)
    text = text.replace("\n", NL_PLACEHOLDER)
    return text


def decode_nl(text: str) -> str:
    """value ⏎ value \\n。"""
    if not isinstance(text, str):
        return text
    return text.replace(NL_PLACEHOLDER, "\n")


def decode_nl_in_obj(obj):
    """value dict/list，value string value decode_nl。"""
    if isinstance(obj, str):
        return decode_nl(obj)
    if isinstance(obj, list):
        return [decode_nl_in_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {k: decode_nl_in_obj(v) for k, v in obj.items()}
    return obj


def download_media(url: str, slug: str, ts: Optional[float] = None, ext: Optional[str] = None, timeout: int = 300) -> Optional[str]:
    """Provider-neutral implementation documentation."""
    import sys
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
    import posixpath

    if not url or not isinstance(url, str):
        return None

    if url.split(":", 1)[0].lower() not in ("http", "https"):
        print(f"[download_media] Unsupported URL scheme: {url[:80]}", file=sys.stderr)
        return None

    if ts is None:
        ts = time.time()

    # implementation URL implementation
    guessed_ext = ext
    if not guessed_ext:
        path_part = url.split("?")[0]
        candidate = posixpath.splitext(path_part)[1].lstrip(".")
        if candidate and len(candidate) <= 5 and candidate.isalnum():
            guessed_ext = candidate
        else:
            guessed_ext = "bin"

    # implementation（implementation media/ implementation，implementation .tmp- implementation）
    _, session_dir = _ensure_session(ts)
    media_dir = os.path.join(session_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    tmp_filename = f".tmp-{_safe_slug(slug)}-{int(ts * 1_000_000)}.download"
    tmp_path = os.path.join(media_dir, tmp_filename)

    req = Request(url, headers={"User-Agent": "NexScope-Skill/2.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            # implementation Content-Type implementation
            if guessed_ext == "bin":
                ct = resp.headers.get("Content-Type", "")
                if "mp4" in ct:
                    guessed_ext = "mp4"
                elif "webm" in ct:
                    guessed_ext = "webm"
                elif "png" in ct:
                    guessed_ext = "png"
                elif "jpeg" in ct or "jpg" in ct:
                    guessed_ext = "jpg"
                elif "webp" in ct:
                    guessed_ext = "webp"
                elif "gif" in ct:
                    guessed_ext = "gif"

            # implementation
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)

        # implementation：implementation（implementation），rename，implementation _meta
        ts_us = int(ts * 1_000_000)
        final_path = os.path.join(media_dir, f"{_safe_slug(slug)}-{ts_us}.{guessed_ext}")
        os.replace(tmp_path, final_path)
        _update_meta(session_dir, skill=slug, kind="media", file_rel=os.path.relpath(final_path, session_dir), ts=ts)
        return final_path

    except Exception as e:
        print(f"[download_media] Failed to download {url}: {e}", file=sys.stderr)
        # implementation
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        return None
