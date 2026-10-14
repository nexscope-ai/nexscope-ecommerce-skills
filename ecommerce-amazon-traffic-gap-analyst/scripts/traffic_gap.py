#!/usr/bin/env python3
"""Collect existing Nexscope data and render an evidence-linked traffic-gap report."""

import argparse
import datetime as dt
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

SLUGS = {
    "keywords": "amazon-asin-keywords", "summary": "amazon-asin-traffic-summary",
    "detail": "amazon-product-detail", "reviews": "amazon-reviews-list",
    "competitors": "amazon-competitor-lookup", "related": "amazon-related-asins",
    "aba": "amazon-keyword-intelligence", "overview": "amazon-keyword-overview",
    "fallback": "amazon-traffic-keywords", "search": "amazon-search",
}
COUNTRIES = {"US": ("amazon.com", "com"), "UK": ("amazon.co.uk", "co.uk"),
             "DE": ("amazon.de", "de"), "JP": ("amazon.co.jp", "co.jp"),
             "CA": ("amazon.ca", "ca"), "FR": ("amazon.fr", "fr"),
             "ES": ("amazon.es", "es"), "IT": ("amazon.it", "it"),
             "MX": ("amazon.com.mx", "com.mx"), "AU": ("amazon.com.au", "com.au"),
             "AE": ("amazon.ae", "ae"), "BR": ("amazon.com.br", "com.br"),
             "SA": ("amazon.sa", "sa")}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)


def api_base():
    base = os.environ.get("NEXSCOPE_PROXY_BASE", "https://api.nexscope.ai").rstrip("/")
    url = urllib.parse.urlsplit(base)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in {"", "/"}:
        raise ValueError("NEXSCOPE_PROXY_BASE must be an origin without credentials or a path.")
    if url.scheme != "https" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Use HTTPS except for a local test server.")
    return base


def post(operation, params, folder, timeout=150):
    key = os.environ.get("NEXSCOPE_API_KEY")
    if not key:
        raise ValueError("Set NEXSCOPE_API_KEY. Never put a key in command arguments or files.")
    if any(ord(c) < 32 or ord(c) > 126 for c in key):
        raise ValueError("NEXSCOPE_API_KEY must be an ASCII header value.")
    request = urllib.request.Request(
        api_base() + "/api/skill-api/v1/skills/" + SLUGS[operation] + "/run",
        data=json.dumps(params, allow_nan=False).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "Nexscope-Traffic-Gap/1.0"})
    # Reserve the result before charging; a network failure is never auto-retried.
    path = folder / (operation + "-" + uuid.uuid4().hex + ".json")
    with path.open("x", encoding="utf-8") as stream:
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                result = json.loads(raw)
                receipt = {k: response.headers.get(k) for k in ("X-Cost-Credit", "X-Cost-Token", "X-Trace-Id") if response.headers.get(k) is not None}
                record = {"operation": operation, "request": params, "response": result, "billingHeaders": receipt}
                json.dump(record, stream, ensure_ascii=False, indent=2)
        except urllib.error.HTTPError as error:
            json.dump({"operation": operation, "httpStatus": error.code, "error": "HTTP request failed; no automatic retry."}, stream)
            raise ValueError(f"HTTP {error.code}: see {path}; 401 authentication, 402 credits. Do not substitute accounts or markets.") from None
        except (OSError, ValueError) as error:
            stream.seek(0)
            stream.truncate()
            json.dump({"operation": operation, "error": "Transport or malformed response; no automatic retry."}, stream)
            raise ValueError(f"Request failed; see {path}. Reconcile before any additional paid call.") from error
    if not isinstance(result, dict) or type(result.get("code")) is not int or result["code"] != 0:
        raise ValueError(f"Platform error; see {path}. HTTP 200 alone is not success.")
    data = result.get("data")
    if not isinstance(data, (dict, list)):
        raise ValueError(f"Missing business data; see {path}.")
    return data, path.name


def config(path):
    cfg = read_json(path)
    if not isinstance(cfg, dict):
        raise ValueError("Config must be an object.")
    country = cfg.get("country", "US")
    if country not in COUNTRIES:
        raise ValueError("Unsupported country; choose a documented marketplace.")
    groups = cfg.get("products")
    if not isinstance(groups, list) or len(groups) < 2 or len(groups) > 11:
        raise ValueError("Provide an own product and 1–10 competitors; 3–5 competitors recommended.")
    own_count, all_asins, ids = 0, set(), set()
    for group in groups:
        if not isinstance(group, dict) or not re.fullmatch(r"[A-Za-z0-9_-]{1,50}", str(group.get("id", ""))):
            raise ValueError("Each group needs a unique safe id.")
        if group["id"] in ids or group.get("role") not in {"own", "competitor"}:
            raise ValueError("Group IDs must be unique; role is own or competitor.")
        ids.add(group["id"])
        own_count += group["role"] == "own"
        asins = group.get("asins")
        if not isinstance(asins, list) or not asins or len(asins) > 30:
            raise ValueError("List 1–30 confirmed child ASINs per product; do not silently select one variant.")
        for asin in asins:
            if not isinstance(asin, str) or not re.fullmatch(r"[A-Z0-9]{10}", asin) or asin in all_asins:
                raise ValueError("ASINs must be ten uppercase letters/digits and unique across groups.")
            all_asins.add(asin)
    if own_count != 1:
        raise ValueError("Exactly one product group must have role=own.")
    if cfg.get("days", 7) not in {7, 30}:
        raise ValueError("days must be 7 or 30; use the same period for all products.")
    for field, default, maximum in (("page_size", 50, 100), ("max_pages", 10, 100)):
        value = cfg.get(field, default)
        minimum = 10 if field == "page_size" else 1
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"{field} must be an integer from {minimum} to {maximum}.")
    return cfg


def rows(data):
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        if not all(isinstance(row, dict) for row in data["data"]):
            raise ValueError("Unexpected non-object record in data array.")
        return data["data"]
    if isinstance(data, list) and all(isinstance(row, dict) for row in data):
        return data
    raise ValueError("Unexpected business data shape. Inspect the saved response; do not treat it as empty.")


def collect(args):
    cfg = config(args.config)
    if cfg.get("days", 7) == 30:
        end = dt.datetime.now(dt.timezone.utc).date()
        cfg["summaryDateRange"] = {"startDate": (end - dt.timedelta(days=29)).isoformat(), "endDate": end.isoformat()}
    count = sum(len(g["asins"]) for g in cfg["products"])
    bound = count * (cfg.get("max_pages", 10) + 3)
    if not args.execute:
        print(json.dumps({"mode": "plan", "asins": count, "maximumCalls": bound,
                          "note": "Keywords paginated, summary/detail/reviews once per child. Calls consume credits. No requests sent."}))
        return
    if args.max_calls is None or args.max_calls < 1:
        raise ValueError("--execute requires an explicitly approved --max-calls budget.")
    folder = Path(args.out).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    dataset = {"schemaVersion": 1, "collectedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
               "config": cfg, "calls": [], "keywords": {}, "complete": {}, "status": "COLLECTING"}
    index = folder / "dataset.json"
    calls = 0

    def save():
        index.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    def call(op, params):
        nonlocal calls
        if calls >= args.max_calls:
            raise ValueError("Approved call budget exhausted; partial evidence saved. Request approval before continuing.")
        calls += 1
        data, filename = post(op, params, folder)
        dataset["calls"].append({"operation": op, "request": params, "file": filename})
        save()
        return data, filename

    save()
    try:
        for group in cfg["products"]:
            for asin in group["asins"]:
                dataset["keywords"][asin] = []
                dataset["complete"][asin] = False
                fingerprints = set()
                for page in range(1, cfg.get("max_pages", 10) + 1):
                    data, source = call("keywords", {"asin": asin, "country": cfg.get("country", "US"),
                        "timePieceType": "latelyDay", "timePieceValue": str(cfg.get("days", 7)),
                        "pageNum": page, "pageSize": cfg.get("page_size", 50)})
                    page_rows = rows(data)
                    fingerprint = hashlib.sha256(json.dumps(page_rows, sort_keys=True).encode()).hexdigest()
                    if page_rows and fingerprint in fingerprints:
                        raise ValueError("Provider repeated a page; completeness is unknown. Inspect saved evidence.")
                    fingerprints.add(fingerprint)
                    dataset["keywords"][asin].extend({"record": row, "source": source} for row in page_rows)
                    total_pages = data.get("totalPage") if isinstance(data, dict) else None
                    if not page_rows or (type(total_pages) is int and total_pages >= 1 and page >= total_pages):
                        dataset["complete"][asin] = True
                        break
                    save()
                call("summary", {"searchValue": asin, "country": cfg.get("country", "US"),
                                 "last7d": cfg.get("days", 7) == 7, "pageNum": 1, "pageSize": 10000,
                                 **cfg.get("summaryDateRange", {})})
                domain, review_domain = COUNTRIES[cfg.get("country", "US")]
                call("detail", {"asins": asin, "amazonDomain": domain})
                call("reviews", {"asin": asin, "domainCode": review_domain,
                                 "star1Num": 3, "star2Num": 3, "star3Num": 2, "star4Num": 1, "star5Num": 1})
        dataset["status"] = "COLLECTED"
    except (ValueError, OSError):
        dataset["status"] = "PARTIAL_FAILURE"
        raise
    finally:
        save()
    print(json.dumps({"dataset": str(index), "calls": calls, "complete": dataset["complete"]}))


def finite(value):
    return value if type(value) in {int, float} and math.isfinite(value) else None


def generate(args):
    path = Path(args.dataset).resolve()
    dataset = read_json(path)
    cfg = dataset["config"]
    # Preserve all variants, but do not sum ratios or duplicate keyword demand.
    groups = {}
    for group in cfg["products"]:
        merged = {}
        for asin in group["asins"]:
            for item in dataset["keywords"].get(asin, []):
                row = item["record"]
                keyword = row.get("keyword")
                if not isinstance(keyword, str) or not keyword.strip():
                    continue
                merged.setdefault(keyword.casefold().strip(), []).append({**item, "childAsin": asin})
        groups[group["id"]] = merged
    own = next(g for g in cfg["products"] if g["role"] == "own")
    own_words = groups[own["id"]]
    gaps = []
    for group in cfg["products"]:
        if group["role"] == "own":
            continue
        for key, items in groups[group["id"]].items():
            own_items = own_words.get(key, [])
            ranks = [finite(i["record"].get("productNaturalRank")) for i in items]
            own_ranks = [finite(i["record"].get("productNaturalRank")) for i in own_items]
            best = min((v for v in ranks if v is not None and v > 0), default=None)
            own_best = min((v for v in own_ranks if v is not None and v > 0), default=None)
            if not own_items:
                kind = "Not observed in own source data; indexing unconfirmed"
            elif best is not None and own_best is not None and own_best - best > 10:
                kind = "Organic rank gap greater than 10 positions"
            else:
                continue
            volumes = {finite(i["record"].get("weeklySearchVolume")) for i in items}
            rates = {finite(i["record"].get("clickToPurchaseConversionRate")) for i in items}
            volumes.discard(None)
            rates.discard(None)
            volume = next(iter(volumes)) if len(volumes) == 1 else None
            rate = next(iter(rates)) if len(rates) == 1 else None
            estimate = volume * rate if volume is not None and rate is not None and 0 <= rate <= 1 else None
            gaps.append({"keyword": items[0]["record"]["keyword"], "competitor": group["id"],
                         "kind": kind, "ownBestOrganicRank": own_best, "competitorBestOrganicRank": best,
                         "weeklySearchVolume": volume, "sourceClickToPurchaseRate": rate,
                         "priorityProxy": estimate, "sources": sorted({i["source"] for i in items + own_items})})
    gaps.sort(key=lambda gap: (gap["priorityProxy"] is None, -(gap["priorityProxy"] or 0), gap["keyword"]))
    report = {"schemaVersion": 1, "collectionStatus": dataset["status"], "country": cfg.get("country", "US"),
              "days": cfg.get("days", 7), "variantGroups": cfg["products"], "paginationComplete": dataset["complete"],
              "gaps": gaps, "limitations": [
                  "Absence from source data does not prove that Amazon has not indexed a keyword.",
                  "priorityProxy = weekly search volume × source click-to-purchase rate, only when both are present and unambiguous; not a traffic forecast or own conversion rate.",
                  "Missing data remains unknown. Do not add traffic shares across child ASINs.",
                  "Source traffic scores are exposure indicators, not measured sessions or an actual conversion funnel.",
                  "An agent must inspect summaries, listing text and reviews, obtain targeted keyword/ABA evidence, and complete the narrative before final delivery."],
              "agentAnalysis": None}
    if args.analysis:
        analysis = read_json(args.analysis)
        if not isinstance(analysis, dict):
            raise ValueError("Analysis must be an object following references/report.md.")
        evidence = {item["file"] for item in dataset["calls"]}
        for field in ("trafficStructure", "indexingChecks", "reviewToListing", "listingActions", "fourWeekPlan"):
            entries = analysis.get(field)
            if not isinstance(entries, list) or not entries:
                raise ValueError("Analysis requires nonempty " + field + "; state missing evidence explicitly.")
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("text"), str) or not entry["text"].strip():
                    raise ValueError("Every analysis entry needs text and source filenames.")
                sources = entry.get("sources")
                if not isinstance(sources, list) or any(s not in evidence for s in sources):
                    raise ValueError("Analysis references an unknown evidence file.")
                if not sources and entry.get("status") != "missing":
                    raise ValueError("Unsupported observations must be marked status=missing.")
        report["agentAnalysis"] = analysis
    report["reportStatus"] = "PRELIMINARY"
    if report["agentAnalysis"]:
        has_missing = any(entry.get("status") == "missing" for field in
                          ("trafficStructure", "indexingChecks", "reviewToListing", "listingActions", "fourWeekPlan")
                          for entry in report["agentAnalysis"][field])
        report["reportStatus"] = "COMPLETE" if not has_missing and dataset["status"] == "COLLECTED" and all(dataset["complete"].values()) else "PARTIAL"
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / "analysis.json", report)
    esc = lambda value: html.escape(str(value if value is not None else "Data not provided"))
    table = "".join("<tr>" + "".join("<td>" + esc(row.get(field)) + "</td>" for field in
                    ("keyword", "competitor", "kind", "ownBestOrganicRank", "competitorBestOrganicRank", "priorityProxy"))
                    + "<td>" + esc(", ".join(row["sources"])) + "</td></tr>" for row in gaps)
    sections = ""
    for field, title in (("trafficStructure", "Traffic structure"), ("indexingChecks", "Indexing checks"),
                         ("reviewToListing", "Review evidence → listing benefits"),
                         ("listingActions", "Listing actions"), ("fourWeekPlan", "Four-week roadmap")):
        entries = report["agentAnalysis"].get(field, []) if report["agentAnalysis"] else []
        sections += "<h2>" + title + "</h2>" + ("".join("<p><strong>" + esc(e.get("status", "evidence-reviewed")) + ": </strong>" + esc(e["text"]) + " <small>Sources: " + esc(", ".join(e["sources"])) + "</small></p>" for e in entries) or "<p>Pending agent evidence review.</p>")
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Amazon Traffic Gap Analysis | Nexscope</title><style>body{font:16px/1.6 system-ui;margin:auto;max-width:1100px;padding:24px;color:#182236}h1,h2{color:#254dc4}.scroll{overflow:auto}table{border-collapse:collapse;min-width:680px;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}p,li,small{overflow-wrap:anywhere}small{display:block;color:#526079}.notice{padding:16px;background:#eef2ff}</style>
<h1>Amazon Traffic Gap Analysis</h1>"""
    page += "<p class='notice'>" + report["reportStatus"] + " — " + ("Agent-reviewed analysis" if report["reportStatus"] == "COMPLETE" else "Incomplete evidence or narrative review; do not treat this as a complete diagnosis") + "; collection: " + esc(dataset["status"]) + ".</p>"
    page += "<p>Marketplace: " + esc(report["country"]) + "; source window: " + esc(report["days"]) + " days.</p>"
    page += "<h2>Keyword gap evidence</h2><div class='scroll'><table><thead><tr><th>Keyword</th><th>Competitor</th><th>Observation</th><th>Own rank</th><th>Competitor rank</th><th>Priority proxy</th><th>Evidence files</th></tr></thead><tbody>" + table + "</tbody></table></div>" + sections
    page += "<h2>Coverage and limitations</h2><pre style='white-space:pre-wrap'>" + esc(json.dumps(dataset["complete"])) + "</pre><ul>" + "".join("<li>" + esc(text) + "</li>" for text in report["limitations"]) + "</ul><p>For advertising strategy, carry this report into an advertising optimization workflow; this expert does not write advertising changes.</p></html>"
    (out / "report.html").write_text(page, encoding="utf-8")
    print(json.dumps({"report": str(out / "report.html"), "analysis": str(out / "analysis.json"), "gaps": len(gaps)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gather = sub.add_parser("collect", help="Plan or collect bounded evidence; new calls consume credits.")
    gather.add_argument("--config", required=True)
    gather.add_argument("--out", required=True)
    gather.add_argument("--execute", action="store_true")
    gather.add_argument("--max-calls", type=int)
    gather.set_defaults(func=collect)
    render = sub.add_parser("report", help="Offline gap calculation and HTML rendering.")
    render.add_argument("--dataset", required=True)
    render.add_argument("--analysis", help="Agent-reviewed observations with source filenames.")
    render.add_argument("--out", required=True)
    render.set_defaults(func=generate)
    single = sub.add_parser("call", help="One additional existing API call; no retry.")
    single.add_argument("operation", choices=SLUGS)
    single.add_argument("--params-file", required=True)
    single.add_argument("--out", required=True)
    single.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.command == "call":
        params = read_json(args.params_file)
        if not isinstance(params, dict):
            raise ValueError("Parameters must be a JSON object.")
        if not args.execute:
            print(json.dumps({"slug": SLUGS[args.operation], "params": params, "mode": "plan"}))
            return
        folder = Path(args.out).resolve()
        folder.mkdir(parents=True, exist_ok=True)
        _, filename = post(args.operation, params, folder)
        dataset_path = folder / "dataset.json"
        if dataset_path.exists():
            data = read_json(dataset_path)
            data["calls"].append({"operation": args.operation, "request": params, "file": filename})
            dataset_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(folder / filename))
    else:
        args.func(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print("Error: " + str(error), file=sys.stderr)
        raise SystemExit(1)
