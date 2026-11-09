#!/usr/bin/env python3
"""Common CLI helpers for ecommerce.1688-procurement scripts."""

import json
import os
import re
import secrets
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SLUG = "ecommerce.1688-procurement"
TIMEOUT_SECONDS = 150
SMALL_THRESHOLD = 8000

ENDPOINTS = {
    "authorizeUrl": "/api/v1/tools/research/alibaba1688/authorizeUrl",
    "authorizedStores": "/api/v1/tools/research/alibaba1688/authorizedStores",
    "receiveAddressList": "/api/v1/tools/research/alibaba1688/receiveAddressList",
    "sku": "/api/v1/tools/research/alibaba1688/sku",
    "orderPreview": "/api/v1/tools/research/alibaba1688/orderPreview",
    "createOrder": "/api/v1/tools/research/alibaba1688/createOrder",
    "paymentUrl": "/api/v1/tools/research/alibaba1688/paymentUrl",
    "orderStatus": "/api/v1/tools/research/alibaba1688/orderStatus",
    "logistics": "/api/v1/tools/research/alibaba1688/logistics",
    "logisticsTrace": "/api/v1/tools/research/alibaba1688/logisticsTrace",
    "confirmReceive": "/api/v1/tools/research/alibaba1688/confirmReceive",
    "cancelOrder": "/api/v1/tools/research/alibaba1688/cancelOrder",
    "invoiceAmount": "/api/v1/tools/research/alibaba1688/invoiceAmount",
    "invoiceApply": "/api/v1/tools/research/alibaba1688/invoiceApply",
}

CONFIRM_FIELDS = {
    "createOrder": "confirmCreateOrder",
    "paymentUrl": "confirmGetPaymentUrl",
    "confirmReceive": "confirmReceive",
    "cancelOrder": "confirmCancel",
    "invoiceApply": "confirmApplyInvoice",
}

ORDER_FLOW_OPERATIONS = {"orderPreview", "createOrder"}
VALID_ORDER_FLOWS = {"general", "fenxiao", "boutiquefenxiao"}
VALID_USE_RED_ENVELOPE = {"y", "n"}

AUTH_PRECHECK_EXEMPT_OPERATIONS = {"authorizeUrl", "authorizedStores"}

SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "appsecret",
    "access_token",
    "accesstoken",
    "refresh_token",
    "refreshtoken",
    "sessionkey",
    "jwt",
    "token",
    "secret",
}

HIDDEN_OUTPUT_KEYS = {
    "tokenexpiresat",
}

_SESSION_CACHE = {}


def get_api_base():
    return (os.environ.get("NEXSCOPE_PROXY_BASE") or "https://api.nexscope.ai").rstrip("/")


def get_api_key():
    """Read the user's Nexscope API key without displaying it."""
    key = (os.environ.get("NEXSCOPE_API_KEY") or "").strip()
    if not key:
        raise SystemExit("API key not configured. Set NEXSCOPE_API_KEY.")
    return key


def _is_sensitive_key(key):
    normalized = str(key).replace("-", "").replace("_", "").lower()
    return normalized in SENSITIVE_KEYS


def _is_hidden_output_key(key):
    normalized = str(key).replace("-", "").replace("_", "").lower()
    return normalized in HIDDEN_OUTPUT_KEYS


def redact(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if _is_hidden_output_key(key):
                continue
            result[key] = "***REDACTED***" if _is_sensitive_key(key) else redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def require_confirmation(operation, params):
    field = CONFIRM_FIELDS.get(operation)
    if not field:
        return
    if params.get(field) is True:
        return
    print(
        json.dumps(
            {
                "error": "confirmation_required",
                "operation": operation,
                "requiredField": field,
                "message": f"High-risk operation blocked locally. Provide JSON boolean {field}=true after separate explicit user confirmation.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(2)


def normalize_params(operation, params):
    params = dict(params)
    if operation == "createOrder":
        use_red_envelope = params.get("useRedEnvelope")
        if use_red_envelope is None or (isinstance(use_red_envelope, str) and not use_red_envelope.strip()):
            params["useRedEnvelope"] = "n"
        elif isinstance(use_red_envelope, str) and use_red_envelope.strip() in VALID_USE_RED_ENVELOPE:
            params["useRedEnvelope"] = use_red_envelope.strip()
        else:
            print(
                json.dumps(
                    {
                        "error": "invalid_parameter",
                        "operation": operation,
                        "field": "useRedEnvelope",
                        "message": "useRedEnvelope only supports y/n. Omit it to default to n.",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )
            sys.exit(2)

    if operation not in ORDER_FLOW_OPERATIONS:
        return params

    flow = params.get("flow")
    if flow is None or (isinstance(flow, str) and not flow.strip()):
        params["flow"] = "general"
        return params

    if isinstance(flow, str):
        normalized_flow = flow.strip()
        if normalized_flow in VALID_ORDER_FLOWS:
            params["flow"] = normalized_flow
            return params

    print(
        json.dumps(
            {
                "error": "invalid_parameter",
                "operation": operation,
                "field": "flow",
                "message": "flow only supports general/fenxiao/boutiquefenxiao. Ordinary procurement should use general.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(2)


def validate_params(operation, params):
    """Reject invalid requests locally before authorization or paid requests."""
    if operation not in ENDPOINTS or not isinstance(params, dict):
        raise ValueError("Unknown operation or non-object parameters.")

    def text(obj, key):
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a nonempty string.")
        return value

    def identifier(obj, key):
        value = text(obj, key)
        if re.fullmatch(r"[+-]?[0-9]+", value.strip()) is None or not -(2**63) <= int(value.strip()) < 2**63:
            raise ValueError(f"{key} must be a decimal ID string within the 64-bit range.")

    def items(key):
        values = params.get(key)
        if not isinstance(values, list) or not values:
            raise ValueError(f"{key} must be a nonempty array.")
        return values

    if operation == "authorizeUrl":
        text(params, "accountName")
    if operation == "sku":
        identifier(params, "offerId")
    if operation in {"orderStatus", "logistics", "logisticsTrace", "confirmReceive", "cancelOrder"}:
        identifier(params, "aliOrderId")
    if operation == "logisticsTrace" and params.get("logisticsId") is not None:
        if not isinstance(params["logisticsId"], str):
            raise ValueError("logisticsId must be a string.")
    if operation in {"paymentUrl", "invoiceAmount"}:
        for value in items("orderIdList" if operation == "paymentUrl" else "orderIds"):
            identifier({"orderId": value}, "orderId")
    if operation in ORDER_FLOW_OPERATIONS:
        if isinstance(params.get("addressId"), str) and params["addressId"].strip():
            text(params, "addressId")
        elif isinstance(params.get("addressParam"), dict):
            for key in ("fullName", "mobile", "address"):
                text(params["addressParam"], key)
        else:
            raise ValueError("Provide addressId or addressParam with fullName, mobile and address.")
        for cargo in items("cargoParamList"):
            if not isinstance(cargo, dict):
                raise ValueError("Each cargoParamList entry must be an object.")
            identifier(cargo, "offerId")
            if cargo.get("specId") is not None and not isinstance(cargo["specId"], str):
                raise ValueError("specId must be a string.")
            quantity = cargo.get("quantity")
            if type(quantity) is not int or quantity < 1:
                raise ValueError("quantity must be an integer >= 1.")
        business_type = params.get("isvBizType")
        if business_type is not None and (
            not isinstance(business_type, str)
            or (business_type.strip() and business_type not in ("cross", "cross_daigou", "cross_distribution"))
        ):
            raise ValueError("isvBizType must be cross, cross_daigou or cross_distribution.")
        if params.get("anonymousBuyer") is not None and type(params["anonymousBuyer"]) is not bool:
            raise ValueError("anonymousBuyer must be a JSON boolean.")
    if operation == "invoiceApply":
        for invoice in items("invoiceApplyModelList"):
            if not isinstance(invoice, dict):
                raise ValueError("Each invoiceApplyModelList entry must be an object.")
            identifier(invoice, "orderId")
            amount = invoice.get("amount")
            if type(amount) is not int or not 0 < amount <= 9223372036854775807:
                raise ValueError("amount must be positive 64-bit integer cents returned by invoiceAmount.")
            if invoice.get("invoiceType") not in ("VATAX_COMM", "VATAX_SPEC"):
                raise ValueError("invoiceType must be VATAX_COMM or VATAX_SPEC.")
            title = invoice.get("purchaserInvoiceTitleModel")
            if not isinstance(title, dict) or title.get("titleType") not in ("PERSONAL", "COMPANY"):
                raise ValueError("purchaserInvoiceTitleModel requires titleType PERSONAL or COMPANY.")
            text(title, "title")
            if title["titleType"] == "COMPANY":
                text(title, "taxpayerIdentify")
                if invoice["invoiceType"] == "VATAX_SPEC":
                    for key in ("bankName", "bankAccountId", "registerAddress", "registerPhone"):
                        text(title, key)
    return params


def unwrap_response(payload):
    """Preserve business payloads and retain Nexscope transport diagnostics."""
    if not isinstance(payload, dict):
        return {"error": "invalid_response", "message": "Expected a JSON object."}
    if "code" in payload and "data" in payload:
        metadata = {key: payload[key] for key in ("code", "msg", "traceId", "ts", "time", "cost") if key in payload}
        if type(payload["code"]) is not int or payload["code"] != 0:
            return {"error": "nexscope_error", "message": payload.get("msg"), "_nexscope": metadata}
        business = payload["data"]
        if not isinstance(business, dict):
            return {"error": "invalid_response", "message": "Expected business object.", "_nexscope": metadata}
        result = dict(business)
        result["_nexscope"] = metadata
        return result
    return payload


def business_failed(payload):
    if not isinstance(payload, dict) or payload.get("error"):
        return True
    if payload.get("errcode", 200) not in (200, "200"):
        return True
    if payload.get("code") in (1002, 1003, 1005, "1002", "1003", "1005"):
        return True
    if payload.get("success") is False or payload.get("status") is False:
        return True
    if isinstance(payload.get("data"), dict):
        return business_failed(payload["data"])
    return False


def _call_gateway_raw(operation, params):
    path = ENDPOINTS[operation]
    data = json.dumps(params, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": "Bearer " + get_api_key(),
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Nexscope-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(get_api_base() + path, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            result = unwrap_response(json.loads(body) if body else {})
            billing = {
                key: response.headers[key]
                for key in ("X-Cost-Token", "X-Cost-Credit", "X-Kong-Trace-Id")
                if response.headers.get(key) is not None
            }
            if billing:
                result["_billing"] = billing
            return result
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"details": body}
        return {"error": f"HTTP {exc.code}: {exc.reason}", "httpStatus": exc.code, "response": parsed}
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON response: {exc}"}


def _extract_stores(payload):
    if not isinstance(payload, dict):
        return []
    stores = payload.get("stores")
    if isinstance(stores, list):
        return stores
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("stores"), list):
        return data["stores"]
    return []


def _has_active_store(payload):
    if business_failed(payload):
        return False
    for store in _extract_stores(payload):
        if not isinstance(store, dict):
            continue
        status = str(store.get("status", "")).upper()
        if status == "ACTIVE" and store.get("expired") is False:
            return True
    return False


def _summarize_authorized_stores(payload):
    summary = []
    for store in _extract_stores(payload):
        if not isinstance(store, dict):
            continue
        summary.append(
            {
                "accountName": store.get("accountName"),
                "status": store.get("status"),
                "expired": store.get("expired"),
            }
        )
    return summary


def _authorization_failure(operation, auth_result):
    return {
        "error": "authorization_required",
        "operation": operation,
        "message": (
            "1688 OAuth authorization is required before this procurement operation. "
            "Run authorized_stores.py to inspect current-user authorization, or authorize_url.py to start OAuth."
        ),
        "authCheck": {
            "endpoint": "authorizedStores",
            "stores": _summarize_authorized_stores(auth_result),
            "raw": redact(auth_result),
        },
    }


def _require_1688_authorization(operation):
    if operation in AUTH_PRECHECK_EXEMPT_OPERATIONS:
        return None
    auth_result = _call_gateway_raw("authorizedStores", {})
    if business_failed(auth_result):
        return auth_result
    if _has_active_store(auth_result):
        return None
    return _authorization_failure(operation, auth_result)


def call_gateway(operation, params):
    params = normalize_params(operation, params)
    validate_params(operation, params)
    require_confirmation(operation, params)
    auth_error = _require_1688_authorization(operation)
    if auth_error:
        return auth_error
    return _call_gateway_raw(operation, params)


def _format_iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def _session_id(ts):
    env = os.environ.get("SESSION_ID")
    if env:
        return re.sub(r"[^a-zA-Z0-9_.-]", "_", env.strip())[:100] or "session"
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
    return _SESSION_CACHE["_auto"]


def _nexscope_root():
    candidates = []
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        first = acpx.split(os.pathsep)[0].strip()
        if first:
            candidates.append(os.path.join(first, "nexscope"))
    candidates.append(os.path.join(os.getcwd(), "nexscope"))
    candidates.append(os.path.join(os.path.expanduser("~"), "nexscope"))

    tmp_root = os.path.abspath(tempfile.gettempdir())
    for root in candidates:
        try:
            candidate = os.path.abspath(root)
            try:
                in_tmp = os.path.commonpath([candidate, tmp_root]) == tmp_root
            except ValueError:
                in_tmp = False
            if in_tmp:
                continue
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write("")
            os.remove(probe)
            return candidate
        except OSError:
            continue
    raise OSError("No writable nexscope output directory found.")


def save_response(operation, payload):
    ts = time.time()
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    session = _session_id(ts)
    out_dir = os.path.join(_nexscope_root(), date_str, session, "data")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{SLUG}-{operation}-{int(ts * 1_000_000)}.json")
    sanitized = redact(payload)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(sanitized, handle, ensure_ascii=False, indent=2)
    return path, sanitized


def _find_main_list(obj):
    best_path = None
    best_list = []

    def walk(node, path):
        nonlocal best_path, best_list
        if isinstance(node, list):
            if len(node) > len(best_list):
                best_path, best_list = path, node
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))

    walk(obj, "")
    return best_path, best_list


def summarize(payload):
    if not isinstance(payload, dict):
        print(f"Response type: {type(payload).__name__}")
        return
    print(f"Top-level keys: {list(payload.keys())}")
    for key in ("errcode", "errorCode", "code", "errmsg", "msg", "message", "success", "total", "costToken"):
        if key in payload and isinstance(payload[key], (str, int, float, bool)):
            print(f"  {key}: {payload[key]}")
    business = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    for key in ("successList", "failedList"):
        if isinstance(business.get(key), list):
            print(f"{key}: {len(business[key])} rows; inspect every row in the full result before further action.")
    list_path, items = _find_main_list(payload)
    if list_path and items:
        print(f"Main list field: `{list_path}` (length={len(items)})")
        print(json.dumps(items[:3], ensure_ascii=False, indent=2))


def run_cli(operation):
    argv = sys.argv[1:]
    inline = False
    force_save = False
    no_save = False
    if "--inline" in argv:
        inline = True
        argv = [item for item in argv if item != "--inline"]
    if "--save" in argv:
        force_save = True
        argv = [item for item in argv if item != "--save"]
    if "--no-save" in argv:
        no_save = True
        argv = [item for item in argv if item != "--no-save"]
    payload = None
    if "--payload-env" in argv:
        index = argv.index("--payload-env")
        try:
            env_name = argv[index + 1]
        except IndexError:
            print("--payload-env requires an environment variable name.", file=sys.stderr)
            sys.exit(1)
        payload = os.environ.get(env_name)
        if payload is None:
            print(f"Environment variable {env_name!r} is not set.", file=sys.stderr)
            sys.exit(1)
        del argv[index:index + 2]
    if "--payload-file" in argv:
        index = argv.index("--payload-file")
        try:
            payload_path = argv[index + 1]
        except IndexError:
            print("--payload-file requires a file path.", file=sys.stderr)
            sys.exit(1)
        with open(payload_path, encoding="utf-8") as handle:
            payload = handle.read()
        del argv[index:index + 2]
    if payload is None and argv:
        payload = argv[0]
    if payload is None:
        print(
            f"Usage: {os.path.basename(sys.argv[0])} '<JSON parameters>' [--inline] "
            "[--payload-env ENV_NAME] [--payload-file path.json]",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON parameters: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Parameters must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    try:
        result = call_gateway(operation, params)
    except ValueError as exc:
        print(json.dumps({"error": "invalid_parameter", "message": str(exc)}), file=sys.stderr)
        sys.exit(2)
    sanitized = redact(result)
    serialized = json.dumps(sanitized, ensure_ascii=False, indent=2)
    serialized_size = len(serialized.encode("utf-8"))
    env_save = os.environ.get("NEXSCOPE_SKILL_SAVE_RESPONSE", "").strip().lower() in {"1", "true", "yes"}
    env_no_save = os.environ.get("NEXSCOPE_SKILL_NO_SAVE", "").strip().lower() in {"1", "true", "yes"}
    should_save = (force_save or env_save or serialized_size > SMALL_THRESHOLD) and not (no_save or env_no_save)
    if should_save:
        path, _ = save_response(operation, sanitized)
        print(f"Saved full response: {path} ({serialized_size} bytes)")
    if inline or serialized_size <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(sanitized)
    if business_failed(result):
        sys.exit(1)
