#!/usr/bin/env python3
"""Upload product images through the shared NexScope Skill Asset API.

Usage:
  python upload_image.py --confirm --confirm-mutation /path/to/product.png

Flow:
  1. POST /api/skill-asset/presign.
  2. PUT the image bytes to the returned presigned HTTPS URL.
  3. POST /api/skill-asset/confirm.
  4. Print the confirmed public URL and asset metadata as JSON.
"""

import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


PRESIGN_PATH = "/api/skill-asset/presign"
CONFIRM_PATH = "/api/skill-asset/confirm"
MAX_FILE_SIZE = 20 * 1024 * 1024
CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


class NoRedirect(HTTPRedirectHandler):
    """Refuse redirects so image bytes are sent only to the signed host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "Upload redirect refused", headers, fp)


def _configuration():
    base = (os.environ.get("NEXSCOPE_PROXY_BASE") or "").strip().rstrip("/")
    key = (os.environ.get("NEXSCOPE_API_KEY") or "").strip()
    if not base or not key:
        raise RuntimeError("NEXSCOPE_PROXY_BASE and NEXSCOPE_API_KEY are required")
    _https_url(base, "NEXSCOPE_PROXY_BASE")
    return base, key


def _https_url(value, name):
    parsed = urlsplit(value) if isinstance(value, str) else None
    if parsed is None or parsed.scheme.lower() != "https" or not parsed.hostname:
        raise RuntimeError(f"{name} must be a valid HTTPS URL")
    return value


def _api_post(base, key, path, body):
    request = Request(
        base + path,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise RuntimeError(
            f"Skill Asset API returned HTTP {exc.code}: {body_text[:500]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError("Skill Asset API request failed") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Skill Asset API returned non-JSON data") from exc
    if not isinstance(value, dict) or value.get("code") != 0 or not isinstance(value.get("data"), dict):
        code = value.get("code") if isinstance(value, dict) else "invalid"
        message = value.get("msg") if isinstance(value, dict) else "invalid response"
        raise RuntimeError(f"Skill Asset API application failure (code={code}, msg={message})")
    return value["data"]


def _read_image(path_value):
    source = Path(path_value).expanduser()
    if source.is_symlink():
        raise ValueError("The upload target must be a regular non-symlink file")
    path = source.resolve()
    if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("The upload target must be a regular non-symlink file")
    extension = path.suffix.lower()
    content_type = CONTENT_TYPES.get(extension)
    if not content_type:
        supported = ", ".join(sorted(CONTENT_TYPES))
        raise ValueError(f"Unsupported image format {extension or '(none)'}; supported: {supported}")
    size = path.stat().st_size
    if size <= 0:
        raise ValueError("The image is empty")
    if size > MAX_FILE_SIZE:
        raise ValueError("The image exceeds the 20 MiB upload limit")
    return path.read_bytes(), path.name, content_type


def _put_file(put_url, raw, content_type):
    _https_url(put_url, "Presigned upload URL")
    request = Request(put_url, data=raw, method="PUT", headers={"Content-Type": content_type})
    try:
        with build_opener(NoRedirect).open(request, timeout=60) as response:
            if response.status not in {200, 201, 204}:
                raise RuntimeError(f"Upload returned HTTP {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"Upload returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("Presigned upload request failed") from exc


def upload_bytes(raw, file_name, content_type, base, key):
    presign = _api_post(
        base,
        key,
        PRESIGN_PATH,
        {"fileName": file_name, "contentType": content_type, "fileSize": len(raw)},
    )
    put_url = _https_url(presign.get("putUrl"), "Presigned upload URL")
    oss_key = presign.get("ossKey")
    if not isinstance(oss_key, str) or not oss_key:
        raise RuntimeError("Presign response is missing ossKey")

    _put_file(put_url, raw, content_type)

    confirmed = _api_post(
        base,
        key,
        CONFIRM_PATH,
        {
            "ossKey": oss_key,
            "expectedSize": len(raw),
            "expectedSha256": hashlib.sha256(raw).hexdigest(),
        },
    )
    public_url = _https_url(confirmed.get("publicUrl"), "Public asset URL")
    asset_id = confirmed.get("assetId")
    if not isinstance(asset_id, str) or not asset_id:
        raise RuntimeError("Confirm response is missing assetId")
    return {
        "url": public_url,
        "assetId": asset_id,
        "name": file_name,
        "size": len(raw),
        "ext": Path(file_name).suffix.lower().lstrip("."),
    }


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: upload_image.py --confirm --confirm-mutation <local_image_path>")
        return

    required_confirmations = {"--confirm", "--confirm-mutation"}
    missing = required_confirmations.difference(sys.argv)
    if missing:
        print("Mutation blocked: pass both --confirm and --confirm-mutation.", file=sys.stderr)
        raise SystemExit(2)
    arguments = [arg for arg in sys.argv[1:] if arg not in required_confirmations]
    if len(arguments) != 1:
        print(
            "Usage: upload_image.py --confirm --confirm-mutation <local_image_path>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        base, key = _configuration()
        raw, file_name, content_type = _read_image(arguments[0])
        result = upload_bytes(raw, file_name, content_type, base, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
