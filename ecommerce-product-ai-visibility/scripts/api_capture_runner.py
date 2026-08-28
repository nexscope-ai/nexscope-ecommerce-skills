"""API-based capture runner with per-engine concurrency and 429 retry backoff."""
import json, os, sys, time, csv, random, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from api_client_base import call_with_web_search, extract_response_text, extract_citations, build_ecommerce_query, CURRENT_YEAR

ECOMMERCE_SYSTEM_PROMPT = (
    "You are a product research assistant with web search capability. "
    "Search for current product information, then recommend products. "
    "Rules:\n"
    "1. Use web_search to find current prices and availability\n"
    "2. Mention specific product names and brands\n"
    "3. Include price ranges from search results\n"
    "4. Cite sources as Markdown links that include the source title and URL\n"
    "5. Mention where to buy (Amazon, Walmart, brand website, etc.)\n"
    "6. Compare pros and cons\n"
    "7. After 1-2 searches, write your final answer with citations\n"
    "8. IMPORTANT: If web_search returns no results or fails, you MUST still answer using your training knowledge. Never apologize or say you cannot help. Always provide product recommendations.\n"
    f"Current year: {CURRENT_YEAR}. Recommend current products only."
)

ENGINE_MODELS = {
    "chatgpt": "gpt-5.5-azure",
    "claude": "global.anthropic.claude-sonnet-4-6",
    "gemini": "gemini-2.5-flash",
    "deepseek": "deepseek-v4-flash",
}

DEFAULT_ENGINE_CONCURRENCY = {
    "chatgpt": 5,
    "claude": 5,
    "gemini": 5,
    "deepseek": 2,
}

MAX_RETRIES = 3
BACKOFF_SCHEDULE = [15, 30, 60]


class _EngineThrottle:
    """Per-engine concurrency semaphore with adaptive throttling."""
    def __init__(self, engine, max_concurrent):
        self._engine = engine
        self._sem = threading.Semaphore(max_concurrent)
        self._lock = threading.Lock()
        self._consecutive_429 = 0
        self._circuit_open = False

    @property
    def circuit_open(self):
        return self._circuit_open

    def acquire(self):
        self._sem.acquire()

    def release(self):
        self._sem.release()

    def record_success(self):
        with self._lock:
            self._consecutive_429 = 0

    def record_429(self):
        with self._lock:
            self._consecutive_429 += 1
            if self._consecutive_429 >= 5:
                self._circuit_open = True


def _is_retryable(result):
    """Check if a failed result should be retried (429 or 5xx)."""
    error = result.get("error", "")
    if not error:
        return False
    if "429" in str(error):
        return True
    if any(f"HTTP {code}" in str(error) for code in [500, 502, 503, 504]):
        return True
    return False


def _is_429(result):
    return "429" in str(result.get("error", ""))


def capture_single_with_retry(engine, query_dict, config, output_dir, throttle):
    """Capture a single query with retry logic and per-engine throttling."""
    if throttle.circuit_open:
        return _make_failed_result(engine, query_dict, "Circuit breaker open: too many consecutive 429s")

    model = config.get("engine_models", {}).get(engine, ENGINE_MODELS.get(engine, "gpt-4o"))
    query_text = build_ecommerce_query(query_dict["text"])
    query_id = query_dict["id"]
    timeout = config.get("capture_timeout_ms", 60000) // 1000

    last_result = None
    for attempt in range(MAX_RETRIES + 1):
        if throttle.circuit_open:
            return _make_failed_result(engine, query_dict, "Circuit breaker open: too many consecutive 429s")

        throttle.acquire()
        try:
            result = call_with_web_search(model=model, query=query_text, system_prompt=ECOMMERCE_SYSTEM_PROMPT, timeout=timeout)
        finally:
            throttle.release()

        response_text = extract_response_text(result)

        if response_text:
            throttle.record_success()
            return _save_capture(result, response_text, engine, query_id, query_text, model, output_dir)

        last_result = result

        if not _is_retryable(result):
            break

        if _is_429(result):
            throttle.record_429()

        if attempt < MAX_RETRIES:
            backoff = BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]
            jitter = backoff * random.uniform(-0.2, 0.2)
            sleep_time = backoff + jitter
            time.sleep(sleep_time)

    return _save_capture(last_result or result, "", engine, query_id, query_text, model, output_dir)


def _make_failed_result(engine, query_dict, error_msg):
    return {
        "schema_version": "capture.v2",
        "task_id": f"{query_dict['id']}__{engine}",
        "query_id": query_dict["id"],
        "engine": engine,
        "query_text": "",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "failed",
        "response_text": "",
        "citations": [],
        "search_queries": [],
        "search_results": [],
        "model": "",
        "latency_ms": 0,
        "error": error_msg,
    }


def _save_capture(result, response_text, engine, query_id, query_text, model, output_dir):
    citations = extract_citations(result) if response_text else []
    search_queries = result.get("search_queries", [])
    search_results = result.get("search_results", [])

    capture_result = {
        "schema_version": "capture.v2",
        "task_id": f"{query_id}__{engine}",
        "query_id": query_id,
        "engine": engine,
        "query_text": query_text,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success" if response_text else "failed",
        "response_text": response_text,
        "citations": citations,
        "search_queries": search_queries,
        "search_results": [{"url": sr["url"], "title": sr.get("title", ""), "snippet": sr.get("snippet", "")} for sr in search_results if sr.get("url")],
        "model": model,
        "latency_ms": result.get("latency_ms", 0),
        "error": result.get("error") if result.get("status") == "error" else None,
    }

    output_path = Path(output_dir) / f"{query_id}__{engine}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(capture_result, ensure_ascii=False, indent=2), encoding="utf-8")
    return capture_result


def capture_run(profile, engines, run_id, queries, base_dir, config):
    runs_dir = config.get("runs_dir", "data/runs")
    output_dir = Path(base_dir) / runs_dir / profile / run_id / "captures"
    output_dir.mkdir(parents=True, exist_ok=True)

    engine_concurrency = config.get("engine_concurrency", {})
    throttles = {}
    for engine in engines:
        max_c = engine_concurrency.get(engine, DEFAULT_ENGINE_CONCURRENCY.get(engine, 3))
        throttles[engine] = _EngineThrottle(engine, max_c)

    total_workers = sum(engine_concurrency.get(e, DEFAULT_ENGINE_CONCURRENCY.get(e, 3)) for e in engines)
    total_workers = min(total_workers, config.get("api_parallel", 5) * len(engines))

    all_results = []
    tasks_to_run = [(engine, query) for engine in engines for query in queries]

    print(f"[capture] Starting: {len(tasks_to_run)} tasks ({len(engines)} engines x {len(queries)} queries)")
    print(f"[capture] Per-engine concurrency: {{{', '.join(f'{e}: {engine_concurrency.get(e, DEFAULT_ENGINE_CONCURRENCY.get(e, 3))}' for e in engines)}}}")
    print(f"[capture] Retry: max {MAX_RETRIES} attempts, backoff {BACKOFF_SCHEDULE}s, circuit breaker at 5 consecutive 429s")

    with ThreadPoolExecutor(max_workers=total_workers) as executor:
        futures = {
            executor.submit(capture_single_with_retry, e, q, config, str(output_dir), throttles[e]): (e, q)
            for e, q in tasks_to_run
        }
        for future in as_completed(futures):
            engine, query = futures[future]
            try:
                result = future.result()
                icon = "OK" if result.get("status") == "success" else "FAIL"
                retry_note = ""
                if result.get("status") != "success" and throttles[engine].circuit_open:
                    retry_note = " [CIRCUIT OPEN]"
                print(f"  [{icon}] {query['id']}@{engine} latency={result.get('latency_ms', 0)}ms{retry_note}")
                all_results.append(result)
            except Exception as e:
                print(f"  [ERR] {query['id']}@{engine}: {str(e)[:100]}")
                all_results.append({"query_id": query["id"], "engine": engine, "status": "failed", "error": str(e), "latency_ms": 0})

    success = sum(1 for r in all_results if r.get("status") == "success")
    failed = len(all_results) - success
    print(f"[capture] Done: {success} success, {failed} failed out of {len(all_results)} total")

    if failed > 0:
        by_engine = {}
        for r in all_results:
            eng = r.get("engine", "?")
            if r.get("status") != "success":
                by_engine[eng] = by_engine.get(eng, 0) + 1
        for eng, count in by_engine.items():
            print(f"  [!] {eng}: {count} failed")

    return {"total": len(all_results), "success": success, "failed": failed, "results": all_results}
