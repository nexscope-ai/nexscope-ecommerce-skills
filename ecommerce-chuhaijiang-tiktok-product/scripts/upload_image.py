#!/usr/bin/env python3
"""Upload local image files or base64 image data to the Chuhaijiang provider.

Usage:
  python upload_image.py /path/to/local/image.png
  python upload_image.py "data:image/jpeg;base64,/9j/4AAQ..."
  python upload_image.py "/9j/4AAQ..."                                    # pure base64 (auto-detected)

Flow:
  1. POST fileName through the Nexscope research gateway to the original presign API
  2. PUT image bytes to the returned temporary upload URL
  3. Print the provider osKey for image search

Requires: NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY environment variables.
"""
import base64
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PRESIGN_PATH = "/api/v1/tools/research/chuhaijiang/upload/presigned-url"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}

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


def _upload_to_provider(base, key, file_bytes, file_name, content_type):
    request = Request(base.rstrip("/") + PRESIGN_PATH,
                      data=json.dumps({"fileName": file_name}).encode("utf-8"),
                      method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=180) as response:
            envelope = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return {"error": "HTTP {}: {}".format(error.code, error.reason)}
    except (URLError, json.JSONDecodeError) as error:
        return {"error": str(error)}

    if not isinstance(envelope, dict):
        return {"error": "Invalid provider presign response"}
    provider = envelope.get("data")
    provider = provider.get("data") if isinstance(provider, dict) else None
    if envelope.get("code") != 0 or not isinstance(provider, dict):
        return {"error": envelope.get("msg") or "Provider presign failed"}
    upload_url = provider.get("url")
    os_key = provider.get("os_key")
    if not isinstance(upload_url, str) or not upload_url.startswith("https://") or not os_key:
        return {"error": "Provider presign response lacks upload URL or os_key"}

    put_request = Request(upload_url, data=file_bytes, method="PUT",
                          headers={"Content-Type": content_type})
    try:
        with urlopen(put_request, timeout=180) as response:
            if not 200 <= response.status < 300:
                return {"error": "Provider upload returned HTTP {}".format(response.status)}
    except HTTPError as error:
        return {"error": "Provider upload returned HTTP {}".format(error.code)}
    except URLError:
        return {"error": "Provider upload network error"}
    return {"osKey": os_key}


def upload_bytes(file_bytes, file_name, content_type, base, key):
    """Upload bytes through the original presign API on the Nexscope gateway."""
    file_size = len(file_bytes)
    ext = os.path.splitext(file_name)[1].lower()
    if not ext:
        ext = _detect_meta_from_bytes(file_bytes)[0]

    if file_size == 0 or file_size > MAX_FILE_SIZE:
        return {"error": True, "input": file_name,
                "message": "File too large: {} bytes (max {})".format(file_size, MAX_FILE_SIZE)}
    if content_type not in ALLOWED_CONTENT_TYPES or ext not in (".jpg", ".jpeg", ".png"):
        return {"error": True, "input": file_name,
                "message": "Unsupported image format. Use JPG, JPEG, or PNG."}

    response = _upload_to_provider(base, key, file_bytes, file_name, content_type)
    if not response.get("osKey"):
        message = response.get("error")
        return {"error": True, "input": file_name,
                "message": message or "Provider upload failed"}
    return {
        "osKey": response["osKey"],
        "name": file_name,
        "size": file_size,
        "ext": ext.lstrip("."),
    }


def upload_file(local_path, base, key):
    """Upload a local file through the original provider presign API."""
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
