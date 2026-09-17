"""Run evaluator prompt against normalized responses via API."""
import json, sys, os, re, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
from api_client_base import GATEWAY_BASE_URL, GATEWAY_API_KEY, CURRENT_YEAR
import requests


def _headers():
    return {"Authorization": f"Bearer {GATEWAY_API_KEY}", "Content-Type": "application/json"}


def _load_evaluator_prompt(base_dir, profile):
    """Load evaluator prompt template with product info injected."""
    prompt_path = Path(base_dir) / "assets" / "prompts" / "evaluator.md"
    product_path = Path(base_dir) / "profiles" / profile / "product.md"

    template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    product_info = product_path.read_text(encoding="utf-8") if product_path.exists() else ""
    return template.replace("{product_info}", product_info)


def _extract_json(text):
    """Extract JSON object from model response text."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


PRIMARY_SIGNALS = ["best overall", "top pick", "top choice", "#1 pick", "i recommend", "i\'d buy", "i\'d choose", "my top", "best option"]

def _fix_recommendation_strength(eval_result):
    """Override recommendation_strength to primary when quote clearly indicates first-choice."""
    if eval_result.get("recommendation_strength") == "primary":
        return
    quote = (eval_result.get("recommendation_quote") or "").lower()
    position = eval_result.get("position")
    if not quote:
        return
    for signal in PRIMARY_SIGNALS:
        if signal in quote:
            if position == 1 or "best overall" in quote:
                eval_result["recommendation_strength"] = "primary"
                return


def evaluate_single(normalized_path, eval_prompt, model="global.anthropic.claude-sonnet-4-6", timeout=90):
    """Evaluate a single normalized response."""
    normalized = json.loads(Path(normalized_path).read_text(encoding="utf-8"))

    query_text = normalized.get("messages", [{}])[0].get("content", "") if normalized.get("messages") else ""
    response_text = normalized.get("response_content", "")
    citations = normalized.get("citations", [])

    citation_text = ""
    if citations:
        citation_text = "\n\nCitations/URLs found in response:\n"
        for c in citations[:20]:
            citation_text += f"- [{c.get('title', '')}]({c.get('url', '')})\n"

    user_message = (
        f"## User Query\n\n{query_text}\n\n"
        f"## AI Engine Response ({normalized.get('engine', 'unknown')})\n\n{response_text}"
        f"{citation_text}\n\n"
        f"Now evaluate this response. Output JSON only."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": eval_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }

    resp = requests.post(f"{GATEWAY_BASE_URL}/chat/completions", headers=_headers(), json=payload, timeout=timeout)
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"

    data = resp.json()
    content = data["choices"][0]["message"].get("content", "")
    eval_result = _extract_json(content)

    if eval_result is None:
        return None, "Failed to parse JSON from response"

    # Ensure required fields
    eval_result["schema_version"] = "eval.v1"
    eval_result["query_id"] = normalized.get("query_id", "")
    eval_result["engine"] = normalized.get("engine", "")
    if "search_queries" not in eval_result:
        eval_result["search_queries"] = normalized.get("search_queries", [])

    # Post-process: fix recommendation_strength when quote contains clear primary signals
    _fix_recommendation_strength(eval_result)

    return eval_result, None


def run_eval(base_dir, run_dir, profile, parallel=4, model="global.anthropic.claude-sonnet-4-6", max_retries=2):
    """Run evaluator on all normalized files in a run with auto-resume and retry."""
    normalized_dir = Path(run_dir) / "normalized"
    eval_dir = Path(run_dir) / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)

    eval_prompt = _load_evaluator_prompt(base_dir, profile)
    normalized_files = sorted(normalized_dir.glob("*.json"))

    # Skip already evaluated (resume support)
    pending = []
    for nf in normalized_files:
        eval_path = eval_dir / nf.name
        if not eval_path.exists():
            pending.append(nf)

    if not pending:
        print(f"[eval] All {len(normalized_files)} files already evaluated")
        return {"total": len(normalized_files), "success": len(normalized_files), "failed": 0}

    print(f"[eval] Evaluating {len(pending)} of {len(normalized_files)} files (parallel={parallel}, retries={max_retries})...")
    success = 0
    failed_files = list(pending)

    for attempt in range(max_retries + 1):
        if attempt > 0:
            # Re-check which files still need eval
            still_pending = [nf for nf in failed_files if not (eval_dir / nf.name).exists()]
            if not still_pending:
                break
            failed_files = still_pending
            print(f"[eval] Retry {attempt}/{max_retries}: {len(still_pending)} files remaining...")
            time.sleep(2)
        else:
            still_pending = failed_files

        batch_failed = []
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(evaluate_single, str(nf), eval_prompt, model): nf for nf in still_pending}
            for future in as_completed(futures):
                nf = futures[future]
                try:
                    result, error = future.result()
                    if result:
                        eval_path = eval_dir / nf.name
                        eval_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                        print(f"  [OK] {nf.stem}")
                        success += 1
                    else:
                        print(f"  [FAIL] {nf.stem}: {error}")
                        batch_failed.append(nf)
                except Exception as e:
                    print(f"  [ERR] {nf.stem}: {str(e)[:80]}")
                    batch_failed.append(nf)

        failed_files = batch_failed
        if not failed_files:
            break

    final_failed = len(failed_files)
    print(f"[eval] Done: {success} success, {final_failed} failed (of {len(pending)} pending)")
    return {"total": len(pending), "success": success, "failed": final_failed}
