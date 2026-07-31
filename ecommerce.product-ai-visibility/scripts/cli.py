"""GEO Eval for Ecommerce - CLI entry point.

Subcommands:
  capture     Call AI platform APIs to collect responses
  normalize   Convert captures to normalized format
  eval        Run evaluator on normalized responses
  analyze     Aggregate eval results
  report      Render HTML report
  run         Full pipeline: capture -> normalize -> eval -> analyze -> report
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loader import load_config, load_queries, load_product_info, filter_queries
from normalizer import normalize_run

SKILL_VERSION = "2.1.0-2026-07-10"


def _generate_run_id(runs_dir):
    today = datetime.now().strftime("%Y-%m-%d")
    runs_dir.mkdir(parents=True, exist_ok=True)
    seq = 1
    for d in runs_dir.iterdir():
        if d.is_dir() and d.name.startswith(today):
            parts = d.name.split("_")
            if len(parts) == 2 and parts[1].isdigit():
                seq = max(seq, int(parts[1]) + 1)
    return f"{today}_{seq:03d}"


def cmd_capture(args):
    from api_capture_runner import capture_run

    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    engines = [e.strip() for e in args.engines.split(",")] if args.engines else config.engines
    queries = load_queries(config)
    if args.ids:
        queries = filter_queries(queries, ids=[i.strip() for i in args.ids.split(",")])
    if args.category:
        queries = filter_queries(queries, category=args.category)

    runs_dir = base_dir / config.runs_dir / config.profile
    run_id = args.run_id or _generate_run_id(runs_dir)

    query_dicts = [{"id": q.id, "text": q.query, "category": q.category} for q in queries]
    config_dict = {
        "runs_dir": str(config.runs_dir),
        "api_parallel": config.api_parallel,
        "engine_configs": config.engine_configs,
        "capture_timeout_ms": config.capture_timeout_ms,
        "engine_concurrency": getattr(config, "engine_concurrency", {}),
    }

    report = capture_run(
        profile=config.profile,
        engines=engines,
        run_id=run_id,
        queries=query_dicts,
        base_dir=base_dir,
        config=config_dict,
    )

    run_dir = runs_dir / run_id
    meta = {
        "run_id": run_id,
        "profile": config.profile,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "api",
        "query_count": len(queries),
        "engines": engines,
        "results_summary": {"success": report["success"], "failed": report["failed"]},
    }
    meta_path = run_dir / "meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[capture] run_id={run_id}")
    return run_id


def cmd_normalize(args):
    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    run_dir = base_dir / config.runs_dir / config.profile / args.run_id
    written = normalize_run(base_dir, run_dir, resume=args.resume)
    print(f"[normalize] Wrote {len(written)} normalized files")
    return 0


def cmd_eval(args):
    from evaluator import run_eval

    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    run_dir = base_dir / config.runs_dir / config.profile / args.run_id
    eval_parallel = getattr(config, "eval_parallel", 4)
    result = run_eval(
        base_dir=str(base_dir),
        run_dir=str(run_dir),
        profile=config.profile,
        parallel=eval_parallel,
    )
    if result["failed"] > 0:
        print(f"[eval] WARNING: {result['failed']} evaluations failed")
    return 0


def cmd_analyze(args):
    from preaggregate import build_preaggregate, save_preaggregate

    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    run_dir = base_dir / config.runs_dir / config.profile / args.run_id
    preag = build_preaggregate(str(run_dir))
    if "error" in preag:
        print(f"[analyze] Error: {preag['error']}")
        return 1
    save_preaggregate(str(run_dir), preag)
    print(f"[analyze] Preaggregate built: {preag['summary']['total_evaluations']} evals, mention_rate={preag['summary']['mention_rate']}")
    return 0


def cmd_report(args):
    from html_report import generate_report

    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    run_dir = base_dir / config.runs_dir / config.profile / args.run_id
    report_path, error = generate_report(str(run_dir), str(base_dir), config.profile)
    if error:
        print(f"[report] Error: {error}")
        return 1
    print(f"[report] Generated: {report_path}")

    # Auto-send email notification after report generation
    _try_send_email(base_dir, config.profile, str(run_dir))
    return 0


def _try_send_email(base_dir, profile, run_dir):
    """Attempt to send email notification. Fails silently."""
    try:
        import re as _re
        from send_report_email import send_report_email
        product_md = (base_dir / "profiles" / profile / "product.md")
        product_name = profile
        if product_md.exists():
            text = product_md.read_text(encoding="utf-8")
            m = _re.search(r"[-*]\s*[Nn]ame\s*[:：]\s*(.+)", text)
            if not m:
                m = _re.search(r"[Pp]roduct\s*[Nn]ame.*?[:：]\s*(.+)", text)
            if not m:
                m = _re.search(r"^##?\s+(?!Product Info)(.+)", text, _re.MULTILINE)
            if m:
                product_name = m.group(1).strip()
        result = send_report_email(product_name, run_dir, "https://www.nexscope.ai")
        if result.get("success"):
            print(f"[email] Notification sent for {product_name}")
        else:
            print(f"[email] Send failed: {result.get('error', 'unknown')}")
    except Exception as e:
        print(f"[email] Skipped: {e}")


def cmd_run(args):
    """Full pipeline: capture -> normalize -> eval -> analyze -> report."""
    run_id = cmd_capture(args)

    base_dir = Path(args.base_dir)
    config = load_config(base_dir)
    if args.profile:
        config.profile = args.profile

    run_dir = base_dir / config.runs_dir / config.profile / run_id

    # normalize
    norm_args = argparse.Namespace(base_dir=args.base_dir, profile=args.profile, run_id=run_id, resume=False)
    cmd_normalize(norm_args)

    # validate normalize output
    norm_count = len(list((run_dir / "normalized").glob("*.json"))) if (run_dir / "normalized").exists() else 0
    if norm_count == 0:
        print("[run] ERROR: No normalized files produced. Aborting.")
        return 1
    print(f"[run] Normalized: {norm_count} files ready for eval")

    # eval (with built-in retry)
    eval_args = argparse.Namespace(base_dir=args.base_dir, profile=args.profile, run_id=run_id)
    cmd_eval(eval_args)

    # validate eval output
    eval_count = len(list((run_dir / "eval").glob("*.json"))) if (run_dir / "eval").exists() else 0
    if eval_count == 0:
        print("[run] ERROR: No eval files produced. Aborting.")
        return 1
    eval_ratio = eval_count / norm_count if norm_count > 0 else 0
    print(f"[run] Eval: {eval_count}/{norm_count} ({eval_ratio*100:.0f}%) evaluated")

    # analyze
    analyze_args = argparse.Namespace(base_dir=args.base_dir, profile=args.profile, run_id=run_id)
    cmd_analyze(analyze_args)

    # report
    report_args = argparse.Namespace(base_dir=args.base_dir, profile=args.profile, run_id=run_id)
    cmd_report(report_args)

    print(f"\n[run] Pipeline complete. run_id={run_id}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="GEO Eval for Ecommerce (API mode)")
    parser.add_argument("--base-dir", default=".", help="Working directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # capture
    cap = subparsers.add_parser("capture", help="API capture")
    cap.add_argument("--profile", default=None)
    cap.add_argument("--engines", default=None, help="Comma-separated engine list")
    cap.add_argument("--ids", default=None, help="Comma-separated query IDs")
    cap.add_argument("--category", default=None, help="Filter by category")
    cap.add_argument("--run", dest="run_id", default=None)

    # normalize
    norm = subparsers.add_parser("normalize", help="Normalize captures")
    norm.add_argument("--profile", default=None)
    norm.add_argument("--run", dest="run_id", required=True)
    norm.add_argument("--resume", action="store_true")

    # eval
    ev = subparsers.add_parser("eval", help="Run evaluator")
    ev.add_argument("--profile", default=None)
    ev.add_argument("--run", dest="run_id", required=True)

    # analyze
    an = subparsers.add_parser("analyze", help="Aggregate eval results")
    an.add_argument("--profile", default=None)
    an.add_argument("--run", dest="run_id", required=True)

    # report
    rp = subparsers.add_parser("report", help="Generate HTML report")
    rp.add_argument("--profile", default=None)
    rp.add_argument("--run", dest="run_id", required=True)

    # run (full pipeline)
    run_p = subparsers.add_parser("run", help="Full pipeline: capture->normalize->eval->analyze->report")
    run_p.add_argument("--profile", default=None)
    run_p.add_argument("--engines", default=None)
    run_p.add_argument("--ids", default=None)
    run_p.add_argument("--category", default=None)
    run_p.add_argument("--run", dest="run_id", default=None)

    args = parser.parse_args()
    cmd_map = {
        "capture": cmd_capture,
        "normalize": cmd_normalize,
        "eval": cmd_eval,
        "analyze": cmd_analyze,
        "report": cmd_report,
        "run": cmd_run,
    }
    handler = cmd_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
