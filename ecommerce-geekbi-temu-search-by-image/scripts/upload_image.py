#!/usr/bin/env python3
"""Upload one local image with the provider OSS presigned PUT flow through Nexscope.

Usage:
  python upload_image.py /path/to/product.jpg

The script prints a JSON object containing the public OSS URL and detected
content type. It never prints the API key or the query string from the
presigned upload URL.
"""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

PRESIGN_PATH = "/api/v1/tools/research/oss/file/presignedPut"
MAX_IMAGE_BYTES = 10_000_000
CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "bmp": "image/bmp",
}


def get_api_base() -> str:
    """Use the Nexscope gateway; provider credentials remain server-owned."""
    return (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").rstrip("/")


def _detect_content_type(header):
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header.startswith(b"GIF8"):
        return "image/gif"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    if header.startswith(b"BM"):
        return "image/bmp"
    return None


def _validate_local_image(local_path, expected_content_type):
    size = os.path.getsize(local_path)
    if size <= 0:
        raise RuntimeError("Image file is empty")
    if size > MAX_IMAGE_BYTES:
        raise RuntimeError("Image file exceeds the 10 MB limit")
    with open(local_path, "rb") as file:
        detected_content_type = _detect_content_type(file.read(12))
    if detected_content_type is None:
        raise RuntimeError("Image bytes must be JPEG, PNG, GIF, WebP, or BMP")
    if detected_content_type != expected_content_type:
        raise RuntimeError(
            "Image extension does not match the actual image byte format"
        )


def _api_key():
    key = os.environ.get("NEXSCOPE_API_KEY")
    if not key:
        raise RuntimeError("API Key not configured; set NEXSCOPE_API_KEY first")
    return key


def _presigned_url(content_type, extension):
    req = Request(
        get_api_base() + PRESIGN_PATH,
        data=json.dumps(
            {"contentType": content_type, "fileExtension": extension}
        ).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + _api_key(),
            "Content-Type": "application/json",
            "User-Agent": "Nexscope-Skill/2.0",
            "SESSION_ID": (os.environ.get("SESSION_ID") or "").strip(),
            "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
            "MODE_ID": os.environ.get("MODE_ID", ""),
            "APP_NAME": os.environ.get("APP_NAME", ""),
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(
            f"Unable to obtain upload URL: HTTP {exc.code} {exc.reason}"
        ) from None
    except URLError as exc:
        raise RuntimeError(f"Unable to obtain upload URL: {exc.reason}") from None
    except json.JSONDecodeError:
        raise RuntimeError("Upload service returned invalid JSON") from None

    if not isinstance(result, dict) or type(result.get("code")) is not int:
        raise RuntimeError("Upload service returned an invalid Nexscope envelope")
    if result["code"] != 0:
        raise RuntimeError(f"Unable to obtain upload URL: {result.get('msg') or 'unknown error'}")
    result = result.get("data")
    if not isinstance(result, dict):
        raise RuntimeError("Upload service returned an invalid business payload")
    url = result.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise RuntimeError("Upload service response is missing a valid HTTPS URL")
    return url


def _upload(presigned_url, local_path, content_type):
    with open(local_path, "rb") as file:
        payload = file.read()
    req = Request(
        presigned_url,
        data=payload,
        headers={
            "Content-Type": content_type,
            "x-oss-object-acl": "public-read",
        },
        method="PUT",
    )
    try:
        with urlopen(req, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Image upload failed with HTTP {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"Image upload failed with HTTP {exc.code}") from None
    except URLError as exc:
        raise RuntimeError(f"Image upload failed: {exc.reason}") from None


def _public_url(presigned_url):
    parts = urlsplit(presigned_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def main():
    if len(sys.argv) != 2:
        print("Usage: upload_image.py <local-image-path>", file=sys.stderr)
        sys.exit(1)

    local_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(local_path):
        print(json.dumps({"error": f"File not found: {local_path}"}, ensure_ascii=False))
        sys.exit(1)

    extension = os.path.splitext(local_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        supported = ", ".join(sorted(CONTENT_TYPE_MAP))
        print(
            json.dumps(
                {
                    "error": f"Unsupported image format: .{extension}",
                    "supported": supported,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    try:
        _validate_local_image(local_path, content_type)
        presigned_url = _presigned_url(content_type, extension)
        _upload(presigned_url, local_path, content_type)
        public_url = _public_url(presigned_url)
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    print(
        json.dumps(
            {
                "url": public_url,
                "contentType": content_type,
                "path": urlsplit(public_url).path.lstrip("/"),
                "name": os.path.basename(local_path),
                "size": os.path.getsize(local_path),
                "ext": extension,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
