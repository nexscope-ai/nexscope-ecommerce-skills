#!/usr/bin/env python3
"""Provider-neutral implementation documentation."""
from __future__ import annotations

import sys as _nexscope_help_sys
if "--help" in _nexscope_help_sys.argv or "-h" in _nexscope_help_sys.argv:
    print('Usage: python onboarding.py [arguments]')
    raise SystemExit(0)


import argparse
import base64
import io
import json
import os
import re
import secrets
import sys
import tempfile
import time
import urllib.error
from urllib.request import urlopen, Request

# Windows implementation GBK，reconfigure implementation QR ASCII implementation。
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8")
        except Exception:
            pass

try:
    import requests
except ImportError:
    requests = None  # implementation/agent-user implementation

TAG = "[real]"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36")

# implementation uid header（implementation）
_LOGIN_FIXED_UID = (os.environ.get("NEXSCOPE_LOGIN_FIXED_UID")
                    or "eyJhX2lkIjoiNmEyMmM4YjA1YmM5MTZhIiwiZF9pZCI6IiJ9")

AGREEMENTS = {
    "user_agreement": "",
    "service_agreement": "",
    "privacy_policy": "",
}
PAY_METHOD_MAP = {"wechat": "WX_PAY", "alipay": "ALI_PAY"}
_ORDER_STATE_MAP = {
    "wait_pay": "unpaid", "paid": "paid", "finished": "paid",
    "expire": "expired", "expired": "expired",
    "cancel": "cancelled", "cancelled": "cancelled",
}


# ============================================================
# Env / implementation
# ============================================================

def _env_base(name: str, default: str, *fallbacks: str) -> str:
    for n in (name, *fallbacks):
        v = os.environ.get(n)
        if v:
            return v.rstrip("/")
    return default.rstrip("/")


def _agent_base() -> str:
    return _env_base("NEXSCOPE_AGENT_API_BASE", "")


def _login_base() -> str:
    return _env_base("NEXSCOPE_LOGIN_API_BASE", "")


def _agent_user_base() -> str:
    return _env_base("NEXSCOPE_AGENT_USER_API_BASE", "")


def _api_key() -> str:
    return os.environ.get("NEXSCOPE_API_KEY") or os.environ.get("NEXSCOPE_API_KEY") or ""


def _mask_phone(phone: str) -> str:
    return f"{phone[:3]}****{phone[-4:]}" if len(phone) >= 7 else phone


def _b64url_json(part: str) -> dict:
    """base64url value JWT value（value padding），value dict。"""
    try:
        return json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
    except Exception:
        return {}


def _uid_header(access_token: str, user_id: str) -> str:
    """base64url({"a_id":<JWT header.a>,"d_id":<userId>})。"""
    parts = (access_token or "").split(".")
    hdr = _b64url_json(parts[1]) if len(parts) >= 2 else {}
    raw = json.dumps({"a_id": hdr.get("a", ""), "d_id": str(user_id)}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode()


def _jwt_uid() -> dict:
    """value NEXSCOPE_API_KEY value JWT payload value。value dict。"""
    parts = _api_key().split(".")
    return _b64url_json(parts[1]) if len(parts) >= 2 else {}


# ============================================================
# implementation + implementation
# ============================================================

_SESSION_ROOT: str | None = None


def _nexscope_root() -> str:
    global _SESSION_ROOT
    if _SESSION_ROOT:
        return _SESSION_ROOT
    candidates = []
    acpx = (os.environ.get("NEXSCOPE_WORKSPACES") or "").strip().split(os.pathsep)[0].strip()
    if acpx:
        candidates.append(os.path.join(acpx, "nexscope"))
    candidates += [
        os.path.join(os.getcwd(), "nexscope"),
        os.path.join(os.path.expanduser("~"), "nexscope"),
        os.path.join(tempfile.gettempdir(), "nexscope"),
    ]
    for root in candidates:
        try:
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8"):
                pass
            os.remove(probe)
            _SESSION_ROOT = os.path.abspath(root)
            return _SESSION_ROOT
        except OSError:
            continue
    _SESSION_ROOT = os.path.abspath(candidates[-1])
    return _SESSION_ROOT


def session_dir() -> str:
    ts = time.time()
    sid = (os.environ.get("SESSION_ID") or "").strip() or (
        time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3))
    path = os.path.join(_nexscope_root(), time.strftime("%Y-%m-%d", time.localtime(ts)), sid)
    os.makedirs(path, exist_ok=True)
    return path


def render_qr(content: str, out_dir: str) -> dict:
    try:
        import qrcode
    except ImportError:
        err = "missing qrcode value，value: pip install qrcode pillow"
        print(f"{TAG} render_qr: {err}", file=sys.stderr)
        return {"png_path": None, "ascii_qr": None, "error": err}
    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, f"qr-{int(time.time() * 1_000_000)}.png")
    qr = qrcode.QRCode(border=1)
    qr.add_data(content)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(png_path)
    buf = io.StringIO()
    qr.print_ascii(out=buf, invert=True)
    return {"png_path": png_path, "ascii_qr": buf.getvalue()}


# ============================================================
# HTTP：requests implementation/agent-user implementation，urllib implementation
# ============================================================

def _require_requests() -> None:
    if requests is None:
        raise RuntimeError("missing requests value，value: pip install requests")


def _http_post(url: str, body: dict, headers: dict, timeout: int = 30) -> dict:
    """value requests POST，value JSON value {_error, _body}。"""
    try:
        _require_requests()
    except RuntimeError as e:
        return {"_error": str(e)}
    try:
        r = requests.post(url, json=body or {}, headers=headers, timeout=timeout)
        return r.json()
    except Exception as e:
        body_text = ""
        resp = getattr(e, "response", None)
        if resp is not None:
            try:
                body_text = resp.text[:500]
            except Exception:
                pass
        return {"_error": str(e), "_body": body_text}


def _headers(source: str, origin_host: str, *, access_token: str = "",
             user_id: str = "", group_id: str = "") -> dict:
    """value headers；access_token value authorization+uid。"""
    h = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": f"https://{origin_host}",
        "Referer": f"https://{origin_host}/",
        "source": source,
        "User-Agent": UA,
    }
    if access_token:
        h["authorization"] = access_token
        h["uid"] = _uid_header(access_token, user_id) if user_id else _LOGIN_FIXED_UID
    if group_id:
        h["tid"] = group_id
    return h


def _login_post(path: str, body: dict) -> dict:
    return _http_post(f"{_login_base()}{path}", body,
                      _headers("ai-nexscope-web", "ai.nexscope.com", access_token=""))


def _gateway(method: str, path: str, body: dict | None = None) -> dict:
    """value HTTP。401/402/403 value，5xx value 3 value。"""
    url = f"{_agent_base()}{path}"
    body_bytes = json.dumps(body or {}).encode() if method == "POST" else None
    last_exc: Exception = RuntimeError("unknownError")
    for attempt in range(3):
        if attempt:
            time.sleep(1 << (attempt - 1))
        headers = {"Authorization": _api_key()}
        if method == "POST":
            headers["Content-Type"] = "application/json"
        req = Request(url, method=method, data=body_bytes, headers=headers)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read().decode()[:300]
            if status == 401:
                raise RuntimeError(f"text（401），text NEXSCOPE_API_KEY text NEXSCOPE_API_KEY：{raw}")
            if status == 402:
                raise RuntimeError(f"text（402），text：{raw}")
            if status == 403:
                raise RuntimeError(f"text（403）：{raw}")
            last_exc = RuntimeError(f"HTTP {status}: {raw}")
            if status not in (408, 429, 500, 502, 503, 504):
                raise last_exc
        except Exception as e:
            last_exc = RuntimeError(f"text: {e}")
            print(f"{TAG} gateway_{method.lower()} attempt {attempt+1}/3 text: {e}", file=sys.stderr)
    raise last_exc


# ============================================================
# implementation：implementation / implementation / implementation
# ============================================================

def _check_biz(resp: dict, tag: str) -> dict:
    if resp.get("errcode") not in (None, 200):
        raise RuntimeError(f"{tag} textError: {resp}")
    return resp


def fetch_user_info() -> dict:
    return _check_biz(_gateway("GET", "/account/currentByAPI"), "currentByAPI")


def fetch_packages(package_type: int) -> list:
    resp = _check_biz(_gateway("POST", "/package/getByTypeByAPI", {"packageType": package_type}),
                      "getByTypeByAPI")
    return resp.get("packageList") or []


def normalize_package(p: dict) -> dict | None:
    """value（price=0）value None value。"""
    if float(p.get("packagePrice", 0) or 0) == 0:
        return None
    try:
        ext = json.loads(p.get("extJson") or "{}")
    except Exception:
        ext = {}
    return {
        "plan_id": p.get("packageId", ""),
        "name": p.get("packageName", ""),
        "price": p.get("packagePrice", 0),
        "price_string": p.get("packagePriceString", ""),
        "original_price": p.get("originalPrice", 0),
        "original_price_string": p.get("originalPriceString", ""),
        "currency": "CNY",
        "credits": p.get("creditAmount", 0),
        "validity_period": p.get("validityPeriod", ""),
        "validity_period_type": p.get("validityPeriodType", ""),
        "description": p.get("description", ""),
        "is_recommend": bool(ext.get("isRecommend", False)),
        "logo_url": ext.get("logo", ""),
        "features": ext.get("features", []),
        "available_methods": ["wechat", "alipay"],
    }


def create_order(plan_id: str, method: str) -> dict:
    if method not in PAY_METHOD_MAP:
        raise ValueError(f"text {method}，text wechat/alipay")
    user = fetch_user_info()
    is_team = bool(user.get("isTeamUser"))
    member_id = _jwt_uid().get("uid", "")
    if not member_id:
        raise RuntimeError("value JWT value uid，value NEXSCOPE_API_KEY value NEXSCOPE_API_KEY")
    body = {
        "packageId": plan_id, "payType": PAY_METHOD_MAP[method], "payDeviceType": "PC",
        "memberId": member_id, "groupId": user.get("currentGroupId", ""),
    }
    path = "/order/createTeamOrderByAPI" if is_team else "/order/createByAPI"
    print(f"{TAG} text path={path} isTeamUser={is_team} groupId={body['groupId']}", file=sys.stderr)
    resp = _check_biz(_gateway("POST", path, body), "value")
    return {
        "order_id": resp.get("orderId", ""),
        "qr_content": resp.get("payQrcode") or resp.get("payUrl", ""),
        "pay_url": resp.get("payUrl", ""),
        "pay_price": resp.get("payPrice", ""),
        "original_price": resp.get("originalPrice", ""),
        "discount_price": resp.get("discountPrice", ""),
        "state": resp.get("state", ""),
        "time_left": resp.get("timeLeft", 0),
        "expire_date": resp.get("expireDate", ""),
        "trade_no": resp.get("tradeNo", ""),
        "product": resp.get("product", ""),
        "pay_type": resp.get("payType", ""),
    }


def query_order(order_id: str) -> dict:
    resp = _check_biz(_gateway("POST", "/order/getByAPI", {"orderId": order_id}), "value")
    state = resp.get("state", "")
    return {
        "order_id": order_id,
        "status": _ORDER_STATE_MAP.get(state, "unknown"),
        "state": state,
        "paid_at": resp.get("payDate") or None,
        "pay_price": resp.get("payPrice", ""),
        "time_left": resp.get("timeLeft", 0),
        "expire_date": resp.get("expireDate", ""),
        "trade_no": resp.get("tradeNo", ""),
        "product": resp.get("product", ""),
    }


# ============================================================
# implementation + implementation key
# ============================================================

def send_verify_code(phone: str) -> dict:
    masked = _mask_phone(phone)
    if not re.fullmatch(r"\d{11}", phone):
        return {"sent": False, "phone": masked, "errmsg": f"text（text 11 text）: {phone}"}
    resp = _login_post("/user/v1/web/login", {
        "type": "sms", "method": "getVerifyCode",
        "data": {"authPhone": phone, "areaCode": "+86", "clientChannel": "NexScopeAgent"},
    })
    if "_error" in resp:
        return {"sent": False, "phone": masked, "errmsg": resp.get("_body") or resp["_error"]}
    if resp.get("success") or resp.get("code") == "OK":
        return {"sent": True, "phone": masked, "area_code": "+86", "agreements": AGREEMENTS}
    return {"sent": False, "phone": masked, "errmsg": resp.get("message") or json.dumps(resp, ensure_ascii=False)}


def _login_v3(phone: str, code: str, channel: str) -> dict:
    resp = _login_post("/user/v3/web/login", {
        "type": "sms", "method": "login", "systemId": "NexScopeAgent",
        "data": {"areaCode": "+86", "authPhone": phone, "authCode": code,
                 "sourceChannel": channel or "skill"},
    })
    if "_error" in resp:
        return {"error": f"login: {resp.get('_body') or resp['_error']}"}
    if not (resp.get("success") or resp.get("code") == "OK"):
        return {"error": f"login: {resp.get('message') or json.dumps(resp, ensure_ascii=False)}"}
    data = resp.get("data") or {}
    access_token, user_id = data.get("accessToken"), data.get("userId")
    if not access_token or not user_id:
        return {"error": f"login: text accessToken/userId: {json.dumps(resp, ensure_ascii=False)}"}
    return {
        "access_token": access_token,
        "refresh_token": data.get("refreshToken", "") or "",
        "user_id": str(user_id),
        "nick_name": data.get("userName", ""),
        "is_new_user": bool(data.get("newUser") or data.get("isFirstRegister")),
    }


def _login_by_token(access_token: str, refresh_token: str) -> dict:
    """value。value。"""
    resp = _http_post(f"{_agent_user_base()}/account/loginByToken", {
        "token": access_token, "refreshToken": refresh_token,
        "device": {"aid": "3026344186", "did": "", "type": "Windows",
                   "os": "10", "model": "149.0.0.0", "brand": "Chrome"},
    }, _headers("agent-nexscope-web", "agent.nexscope.com", access_token=access_token))
    if "_error" in resp:
        return {"error": f"loginByToken: {resp.get('_body') or resp['_error']}"}
    if resp.get("errcode") != 200:
        return {"error": f"loginByToken: {resp.get('errmsg') or json.dumps(resp, ensure_ascii=False)}"}
    print(f"{TAG} loginByToken text，text", file=sys.stderr)
    return {}


def _fetch_user_info_v3(access_token: str, user_id: str) -> dict:
    """value userInfo value group_id / member_id。"""
    resp = _http_post(f"{_login_base()}/nexscopeApp/api/userCenter/userInfo", {},
                      _headers("agent-nexscope-web", "agent.nexscope.com",
                               access_token=access_token, user_id=user_id))
    if "_error" in resp:
        return {"error": f"userInfo: {resp.get('_body') or resp['_error']}"}
    if resp.get("code") != "OK":
        return {"error": f"userInfo: {resp.get('message') or json.dumps(resp, ensure_ascii=False)}"}
    teams = (resp.get("data") or {}).get("teamList") or []
    if not teams:
        return {"error": "userInfo: value，value  value"}
    selected = (next((t for t in teams if t.get("isSelect") == 1 and t.get("agentTeamId")), None)
                or next((t for t in teams if t.get("agentTeamId")), None))
    if not selected:
        return {"error": "userInfo: value agent value，value  value"}
    gid, mid = selected.get("agentTeamId"), selected.get("agentMemberId")
    if not gid or not mid:
        return {"error": f"userInfo: text agentTeamId/agentMemberId: {json.dumps(selected, ensure_ascii=False)}"}
    return {"group_id": str(gid), "member_id": str(mid), "team_name": selected.get("teamName", "")}


_TOKEN_KEYS = ("token", "apiToken", "api_token", "apiKey", "api_key")


def _extract_token(resp: dict) -> str:
    if not isinstance(resp, dict):
        return ""
    for src in (resp, resp.get("data") if isinstance(resp.get("data"), dict) else {}):
        for k in _TOKEN_KEYS:
            v = src.get(k)
            if isinstance(v, str) and v:
                return v
    d = resp.get("data")
    return d if isinstance(d, str) and d else ""


def _get_or_generate_api_token(access_token: str, user_id: str, group_id: str) -> dict:
    hdr = _headers("agent-nexscope-web", "ai.nexscope.com",
                   access_token=access_token, user_id=user_id, group_id=group_id)
    for path, source in (("/group/getApiToken", "existing"),
                         ("/group/generateApiToken", "generated")):
        resp = _http_post(f"{_agent_user_base()}{path}", {"id": group_id}, hdr)
        if "_error" in resp:
            return {"error": f"{path.rsplit('/', 1)[-1]}: {resp.get('_body') or resp['_error']}"}
        tok = _extract_token(resp)
        if tok:
            return {"api_key": tok, "source": source}
    return {"error": f"generateApiToken: text token，text: {json.dumps(resp, ensure_ascii=False)}"}


def login_and_get_key(phone: str, code: str, channel: str) -> dict:
    masked = _mask_phone(phone)
    if not re.fullmatch(r"\d{11}", phone):
        return {"error": f"login: text: {phone}", "phone": masked}
    if not re.fullmatch(r"\d{4,8}", code):
        return {"error": f"login: text: {code}", "phone": masked}
    lg = _login_v3(phone, code, channel)
    if "error" in lg:
        return {"error": lg["error"], "phone": masked}
    if lg.get("is_new_user"):
        lbt = _login_by_token(lg["access_token"], lg["refresh_token"])
        if "error" in lbt:
            print(f"{TAG} {lbt['error']}（text key）", file=sys.stderr)
    info = _fetch_user_info_v3(lg["access_token"], lg["user_id"])
    if "error" in info:
        return {"error": info["error"], "phone": masked}
    tok = _get_or_generate_api_token(lg["access_token"], lg["user_id"], info["group_id"])
    if "error" in tok:
        return {"error": tok["error"], "phone": masked}
    return {
        "api_key": tok["api_key"], "phone": masked,
        "group_id": info["group_id"], "member_id": info["member_id"],
        "source": tok["source"], "nick_name": lg.get("nick_name", ""),
        "team_name": info.get("team_name", ""),
        "is_new_user": lg.get("is_new_user", False),
    }


# ============================================================
# argparse implementation
# ============================================================

def _emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _cmd_send_code(args) -> int:
    r = send_verify_code(args.phone.strip())
    _emit(r)
    if r.get("sent"):
        print(f"{TAG} text {r['phone']}", file=sys.stderr)
    return 0 if r.get("sent") else 1


def _cmd_login(args) -> int:
    r = login_and_get_key(args.phone.strip(), args.code.strip(), args.channel)
    _emit(r)
    if "api_key" in r:
        print(f"{TAG} text API key（text: {r['source']}）", file=sys.stderr)
        return 0
    return 1


def _cmd_list_plans(args) -> int:
    try:
        payload = _jwt_uid()
        if payload:
            print(f"{TAG} JWT uid={payload.get('uid')} name={payload.get('name')}", file=sys.stderr)
        user = fetch_user_info()
        is_team = bool(user.get("isTeamUser"))
        nick = user.get("nickName", "")
        print(f"{TAG} text {nick} isTeamUser={is_team}", file=sys.stderr)
        pkgs = fetch_packages(7 if is_team else 1)
        plans = [n for n in (normalize_package(p) for p in pkgs) if n is not None]
        _emit({"plans": plans, "user": {"nickName": nick, "isTeamUser": is_team}})
        return 0
    except RuntimeError as e:
        _emit({"error": True, "message": str(e)})
        return 1


def _cmd_order(args) -> int:
    try:
        pkgs = fetch_packages(7 if bool(fetch_user_info().get("isTeamUser")) else 1)
        match = next((n for n in (normalize_package(p) for p in pkgs)
                      if n and n["plan_id"] == args.plan_id), None)
        if match is None:
            _emit({"error": True, "message": f"unknowntext plan_id={args.plan_id}"})
            return 1
        if args.method not in match.get("available_methods", []):
            _emit({"error": True,
                   "message": f"text {args.plan_id} text {args.method}，text {match['available_methods']}"})
            return 1
        order = create_order(args.plan_id, args.method)
    except (RuntimeError, ValueError) as e:
        _emit({"error": True, "message": str(e)})
        return 1
    qr = render_qr(order["qr_content"], session_dir())
    order["png_path"] = qr.get("png_path")
    order["ascii_qr"] = qr.get("ascii_qr")
    if qr.get("error"):
        order["qr_render_error"] = qr["error"]
    _emit(order)
    return 0


def _cmd_query(args) -> int:
    try:
        _emit(query_order(args.order_id))
        return 0
    except RuntimeError as e:
        _emit({"error": True, "message": str(e)})
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="onboarding", description="NexScope value CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("send-code", help="value")
    p.add_argument("phone", help="11 value")
    p.set_defaults(func=_cmd_send_code)

    p = sub.add_parser("login", help="value API key")
    p.add_argument("phone")
    p.add_argument("code", help="value")
    p.add_argument("--channel", default="skill",
                   help="value，value skill；workbuddy value workbuddy")
    p.set_defaults(func=_cmd_login)

    sub.add_parser("list-plans", help="value").set_defaults(func=_cmd_list_plans)

    p = sub.add_parser("order", help="value")
    p.add_argument("plan_id")
    p.add_argument("method", choices=["wechat", "alipay"])
    p.set_defaults(func=_cmd_order)

    p = sub.add_parser("query", help="value")
    p.add_argument("order_id")
    p.set_defaults(func=_cmd_query)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())