"""Send AI Visibility Report notification email."""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _read_metrics_from_run(run_dir):
    """Auto-read metrics from preaggregate.json in the run directory."""
    preag_path = Path(run_dir) / "preaggregate.json"
    if not preag_path.exists():
        return {"mention_rate": 0, "biggest_gap": "", "p0_action": "See full report"}

    preag = json.loads(preag_path.read_text(encoding="utf-8"))
    summary = preag.get("summary", {})
    mention_rate = summary.get("mention_rate", 0)

    # Find weakest LLM
    engine_stats = preag.get("engine_stats", {})
    weakest = ""
    lowest_rate = 999
    for engine, stats in engine_stats.items():
        rate = stats.get("mention_rate", 0)
        if rate < lowest_rate:
            lowest_rate = rate
            weakest = engine
    if weakest:
        biggest_gap = f"{weakest} ({int(lowest_rate*100)}% mention rate)"
    else:
        biggest_gap = "See full report"

    # Get P0 action from next_steps if available
    next_steps = preag.get("next_steps", [])
    if next_steps:
        p0_action = next_steps[0].get("title", "See full report")
    else:
        p0_action = "See full report"

    return {
        "mention_rate": mention_rate * 100 if mention_rate <= 1 else mention_rate,
        "biggest_gap": biggest_gap,
        "p0_action": p0_action
    }


def _build_subject(product_name, metrics):
    mention_rate = metrics.get("mention_rate", 0)
    return f"AI Visibility Report ready \u2014 {product_name} ({int(mention_rate)}% mention rate)"


def _build_body(product_name, metrics, report_url):
    mention_rate = int(metrics.get("mention_rate", 0))

    body = f"""Your **AI Visibility Report** for **{product_name}** is ready.

**AI Mention Rate: {mention_rate}%** \u2014 tested across ChatGPT, Claude, Gemini & DeepSeek.

Full breakdown, competitive rankings, and action steps are in your report.

**[View Report on Nexscope \u2192](https://www.nexscope.ai)**
"""
    return body


def send_report_email(product_name, run_dir, report_url):
    base_url = os.environ.get("NEXSCOPE_PROXY_BASE")
    api_key = os.environ.get("NEXSCOPE_API_KEY")

    if not base_url or not api_key:
        return {"success": False, "error": "Email service not available"}

    metrics = _read_metrics_from_run(run_dir)
    subject = _build_subject(product_name, metrics)
    markdown_body = _build_body(product_name, metrics, report_url)

    payload = {
        "subject": subject,
        "content": subject,
        "markdown": markdown_body,
        "serviceName": "AI Visibility Report",
        "status": "completed",
    }

    url = f"{base_url}/api/v1/tools/email/send"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw[:200]}
            if status < 200 or status >= 300:
                return {"success": False, "error": "Email delivery failed", "status": status}
            if isinstance(body, dict) and "code" in body and body["code"] != 0:
                return {"success": False, "error": body.get("msg") or body.get("message", "Email delivery failed")}
            return {"success": True, "status": status, "detail": body.get("message") or body.get("msg", "accepted")}
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        return {"success": False, "error": f"HTTP {e.code}", "detail": err_body}
    except Exception as ex:
        return {"success": False, "error": f"Email service unavailable: {type(ex).__name__}"}


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: send_report_email.py <product_name> <run_dir> <report_url>")
        sys.exit(1)

    product_name = sys.argv[1]
    run_dir = sys.argv[2]
    report_url = sys.argv[3]

    result = send_report_email(product_name, run_dir, report_url)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
