"""Run a single Amazon Seller operation; dry-run is the default."""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    """Keep the Nexscope API key on the configured origin."""

    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def valid_type(value, expected):
    types = {"integer": int, "string": str, "object": dict, "boolean": bool}
    return expected in types and type(value) is types[expected]


def validate(operation, payload, confirm_write):
    fields = {f["name"]: f for f in operation["fields"]}
    if not isinstance(payload, dict) or payload.keys() - fields.keys():
        raise ValueError("Use a JSON object with only documented fields.")
    for name, field in fields.items():
        if name not in payload:
            if field["required"]:
                raise ValueError(f"Missing required field: {name}.")
        elif not valid_type(payload[name], field["type"]):
            raise ValueError(f"Invalid type for {name}; expected {field['type']}.")
    if "connectionId" in payload and payload["connectionId"] <= 0:
        raise ValueError("connectionId must be a positive integer.")
    if "pathParams" in fields:
        placeholders = set(re.findall(r"\{([^}]+)\}", operation["amazonPath"]))
        values = payload.get("pathParams", {})
        if placeholders != values.keys() or any(
            not isinstance(value, str) or not value.strip() for value in values.values()
        ):
            raise ValueError("Supply all path placeholders as non-empty strings.")
    if payload.get("queryString", "").startswith("?"):
        raise ValueError("queryString must not start with '?'.")
    action = payload.get("action", "preview")
    if action not in ("preview", "confirm"):
        raise ValueError("action must be preview or confirm.")
    if action == "confirm" and not payload.get("confirmationToken"):
        raise ValueError("Use the confirmation token issued for this preview.")
    if operation["operation"] == "disconnect" and payload.get("confirm") is not True:
        raise ValueError("Disconnect requires confirm=true and the latest revision.")
    if (action == "confirm" or operation["operation"] == "disconnect") and not confirm_write:
        raise ValueError("This call requires explicit --confirm-write approval.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-write", action="store_true")
    args = parser.parse_args()
    spec_path = Path(__file__).resolve().parents[1] / "references" / "api.json"
    catalog = json.loads(spec_path.read_text(encoding="utf-8"))["operations"]
    if args.list:
        for row in catalog:
            print(row["slug"] + (" (Amazon sandbox only)" if row["sandboxOnly"] else ""))
        return
    operation = next((item for item in catalog if item["slug"] == args.slug), None)
    if not operation or not args.input:
        parser.error("Choose a listed API slug and provide --input.")
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        validate(operation, payload, args.confirm_write)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if not args.execute:
        print(json.dumps({"mode": "dry-run", "method": "POST", "endpoint": operation["endpoint"]}))
        return
    key = os.environ.get("NEXSCOPE_API_KEY", "").strip()
    if not key:
        parser.error("Set NEXSCOPE_API_KEY before sending a request.")
    base = os.environ.get("NEXSCOPE_PROXY_BASE", "https://api.nexscope.ai")
    url = urlsplit(base)
    if (
        url.scheme != "https" or not url.hostname or url.username is not None
        or url.path not in ("", "/") or url.query or url.fragment
    ):
        parser.error("NEXSCOPE_PROXY_BASE must be an HTTPS origin.")
    request = Request(
        base.rstrip("/") + operation["endpoint"],
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with build_opener(NoRedirect()).open(request, timeout=45) as answer:
            result = json.load(answer)
    except HTTPError as error:
        retry_after = error.headers.get("Retry-After", "")
        delay = f" Retry-After: {retry_after}." if retry_after.isdecimal() else ""
        parser.exit(1, f"Nexscope HTTP {error.code}.{delay} No automatic retry was sent.\n")
    except (URLError, TimeoutError, ValueError):
        parser.exit(1, "Request failed or had an ambiguous result. No automatic retry was sent.\n")
    print(json.dumps(result, ensure_ascii=False))
    if not isinstance(result, dict) or result.get("code") != 0:
        raise SystemExit(1)
    data = result.get("data")
    upstream = data.get("response") if isinstance(data, dict) else None
    if isinstance(upstream, dict) and isinstance(upstream.get("httpStatus"), int):
        if upstream["httpStatus"] >= 400:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
