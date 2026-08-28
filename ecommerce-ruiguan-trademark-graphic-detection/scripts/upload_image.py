#!/usr/bin/env python3
"""Upload local image files or base64 image data via the Nexscope Skill Asset API.

Usage:
  python upload_image.py /path/to/local/image.png
  python upload_image.py "data:image/jpeg;base64,/9j/4AAQ..."
  python upload_image.py "/9j/4AAQ..."                                    # pure base64 (auto-detected)

Flow:
  1. POST /api/skill-asset/presign  -> get presigned PUT URL + assetId
  2. PUT file bytes directly to S3 presigned URL
  3. POST /api/skill-asset/confirm  -> verify upload + get public URL
  4. Print JSON array of results to stdout

Requires: NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY environment variables.
"""
import base64
import hashlib
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PRESIGN_PATH = "/api/skill-asset/presign"
CONFIRM_PATH = "/api/skill-asset/confirm"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# magic bytes -> (extension, content_type)
_MAGIC_MAP = [
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"GIF87a", ".gif", "image/gif"),
    (b"GIF89a", ".gif", "image/gif"),
    (b"RIFF", ".webp", "image/webp"),  # RIFF....WEBP
    (b"BM", ".bmp", "image/bmp"),
]

_DATA_URI_RE = re.compile(r"^data:([^;]*)(;base64)?,(.*)", re.IGNORECASE)


def _detect_meta_from_bytes(raw):
    """Sniff file type from magic bytes. Returns (ext, content_type)."""
    for magic, ext, ct in _MAGIC_MAP:
        if raw.startswith(magic):
            if ext == ".webp":
                # RIFF header needs further check for WEBP subtype
                if len(raw) > 11 and raw[8:12] == b"WEBP":
                    return ext, ct
                continue
            return ext, ct
    return ".jpg", "image/jpeg"


def _content_type(ext):
    """Map file extension to MIME content type."""
    mapping = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }
    return mapping.get(ext, "application/octet-stream")


def _api_post(base, key, path, body):
    """Send a JSON POST request and return the parsed response."""
    url = base.rstrip("/") + path
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=data, method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return {"error": "HTTP {}: {}".format(e.code, e.reason), "details": raw}


def _put_file(put_url, data, content_type):
    """Upload bytes directly to a presigned S3 PUT URL."""
    req = Request(put_url, data=data, method="PUT", headers={
        "Content-Type": content_type,
    })
    try:
        with urlopen(req, timeout=60) as resp:
            if resp.status not in (200, 201, 204):
                return False, "PUT returned HTTP {}".format(resp.status)
            return True, None
    except HTTPError as e:
        return False, "PUT failed: HTTP {}: {}".format(e.code, e.reason)
    except URLError as e:
        return False, "PUT connection failed: {}".format(e.reason)


def upload_bytes(file_bytes, file_name, content_type, base, key):
    """Upload raw bytes through the presign + PUT + confirm flow.

    Returns a dict with keys: url, assetId, name, size, ext on success,
    or error, input, message on failure.
    """
    file_size = len(file_bytes)
    ext = os.path.splitext(file_name)[1].lower()
    if not ext:
        ext = _detect_meta_from_bytes(file_bytes)[0]

    if file_size > MAX_FILE_SIZE:
        return {"error": True, "input": file_name,
                "message": "File too large: {} bytes (max {})".format(file_size, MAX_FILE_SIZE)}

    # Step 1: Get presigned URL
    presign = _api_post(base, key, PRESIGN_PATH, {
        "fileName": file_name,
        "contentType": content_type,
        "fileSize": file_size,
    })
    if "code" in presign:
        if presign["code"] != 0:
            return {"error": True, "input": file_name,
                    "message": "Presign failed: code={} msg={}".format(
                        presign.get("code"), presign.get("msg", ""))}
    elif presign.get("error"):
        return {"error": True, "input": file_name,
                "message": "Presign request failed: {}".format(presign.get("error"))}
    data = presign.get("data")
    if not data:
        return {"error": True, "input": file_name,
                "message": "Presign response missing data: {}".format(
                    json.dumps(presign, ensure_ascii=False)[:500])}

    put_url = data.get("putUrl")
    oss_key = data.get("ossKey")
    if not put_url:
        return {"error": True, "input": file_name,
                "message": "Presign response missing putUrl: {}".format(
                    json.dumps(data, ensure_ascii=False)[:500])}

    # Step 2: Upload directly to S3
    ok, err = _put_file(put_url, file_bytes, content_type)
    if not ok:
        return {"error": True, "input": file_name, "message": err}

    # Compute SHA-256 for verification
    sha256 = hashlib.sha256(file_bytes).hexdigest()

    # Step 3: Confirm upload
    confirm = _api_post(base, key, CONFIRM_PATH, {
        "ossKey": oss_key,
        "expectedSize": file_size,
        "expectedSha256": sha256,
    })
    if "code" in confirm:
        if confirm["code"] != 0:
            return {"error": True, "input": file_name,
                    "message": "Confirm failed: code={} msg={}".format(
                        confirm.get("code"), confirm.get("msg", ""))}
    elif confirm.get("error"):
        return {"error": True, "input": file_name,
                "message": "Confirm request failed: {}".format(confirm.get("error"))}

    confirm_data = confirm.get("data")
    if not confirm_data:
        return {"error": True, "input": file_name,
                "message": "Confirm response missing data: {}".format(
                    json.dumps(confirm, ensure_ascii=False)[:500])}

    public_url = confirm_data.get("publicUrl")
    asset_id = confirm_data.get("assetId")
    return {
        "url": public_url,
        "assetId": asset_id,
        "name": file_name,
        "size": file_size,
        "ext": ext.lstrip("."),
    }


def upload_file(local_path, base, key):
    """Upload a local file through the presign + PUT + confirm flow."""
    if not os.path.isfile(local_path):
        return {"error": True, "input": local_path, "message": "File not found"}

    file_name = os.path.basename(local_path)
    ext = os.path.splitext(file_name)[1].lower()
    content_type = _content_type(ext)

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    return upload_bytes(file_bytes, file_name, content_type, base, key)


def _parse_base64_input(raw_input):
    """Parse a base64 or data-URI string into (bytes, file_name, content_type).

    Returns None if the input does not look like base64.
    """
    content_type = "image/jpeg"
    file_name = "image.jpg"
    b64 = raw_input.strip()

    # Check for data URI prefix: data:image/png;base64,xxxx
    m = _DATA_URI_RE.match(b64)
    if m:
        ct = (m.group(1) or "image/jpeg").strip().lower()
        if ct:
            content_type = ct
        b64 = m.group(3)
        # Derive file name from content type
        ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
               "image/webp": ".webp", "image/bmp": ".bmp"}.get(content_type, ".jpg")
        file_name = "image" + ext

    # Quick heuristic: if it's > 100 chars and looks like base64 (no spaces, mostly alphanumeric+/=)
    # and is NOT a file path (no backslashes or forward slashes that look like a path)
    if not m and len(b64) < 100:
        return None  # too short to be base64, probably a file path

    if not m and ("\\" in b64 or ("/" in b64 and os.path.exists(b64))):
        return None  # looks like a file path

    try:
        decoded = base64.b64decode(b64, validate=True)
    except Exception:
        if m:
            # data URI but base64 decode failed — try without validation
            try:
                decoded = base64.b64decode(b64, validate=False)
            except Exception:
                return None
        else:
            return None

    if len(decoded) == 0:
        return None

    # Sniff actual type from decoded bytes to get correct extension
    ext, sniffed_ct = _detect_meta_from_bytes(decoded)
    if not m:
        content_type = sniffed_ct
        file_name = "image" + ext

    return decoded, file_name, content_type


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <local_path|base64_string|data:URI> [...]".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    base = os.environ.get("NEXSCOPE_PROXY_BASE", "").strip()
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not base or not key:
        print("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required", file=sys.stderr)
        sys.exit(1)

    results = []
    had_error = False
    for arg in sys.argv[1:]:
        # Try base64 first, then fall back to file path
        parsed = _parse_base64_input(arg)
        if parsed:
            raw_bytes, name, ct = parsed
            result = upload_bytes(raw_bytes, name, ct, base, key)
        else:
            result = upload_file(arg, base, key)

        results.append(result)
        if result.get("error"):
            had_error = True

    print(json.dumps(results, ensure_ascii=False, indent=2))
    if had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()