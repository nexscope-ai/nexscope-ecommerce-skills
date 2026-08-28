"""AI platform API unified call layer with web search via multi-turn tool use."""
import json, os, re, time, threading
from datetime import date
from urllib.parse import unquote
import requests

GATEWAY_BASE_URL = os.environ.get("MODEL_BASE_URL", "https://agent-aigw-test.nexscope.ai/v1")
GATEWAY_API_KEY = os.environ.get("MODEL_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
CURRENT_YEAR = str(date.today().year)

_WEB_SEARCH_TOOL = {"type": "function", "function": {
    "name": "web_search",
    "description": "Search the web for current product information, prices, and availability. Use sparingly - max 2 searches.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]}
}}


def _headers():
    return {"Authorization": f"Bearer {GATEWAY_API_KEY}", "Content-Type": "application/json"}


class _SearchRateLimiter:
    """Global rate limiter for DuckDuckGo to prevent triggering anti-bot."""
    def __init__(self, max_concurrent=1, min_interval=2.0):
        self._sem = threading.Semaphore(max_concurrent)
        self._lock = threading.Lock()
        self._last_request = 0
        self._min_interval = min_interval

    def acquire(self):
        self._sem.acquire()
        with self._lock:
            now = time.time()
            wait = self._min_interval - (now - self._last_request)
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.time()

    def release(self):
        self._sem.release()


_ddg_limiter = _SearchRateLimiter(max_concurrent=1, min_interval=2.0)


def _execute_web_search(query):
    """Execute web search via DuckDuckGo with global rate limiting and retry."""
    for attempt in range(3):
        _ddg_limiter.acquire()
        try:
            resp = requests.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query}, timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
            )
            results = []
            pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.+?)</a>.*?<a class="result__snippet"[^>]*>(.+?)</a>'
            for match in re.finditer(pattern, resp.text, re.DOTALL):
                url, title, snippet = match.groups()
                title = re.sub(r"<[^>]+>", "", title).strip()
                snippet = re.sub(r"<[^>]+>", "", snippet).strip()
                if url.startswith("//duckduckgo.com/l/?uddg="):
                    url = unquote(url.split("uddg=")[1].split("&")[0])
                results.append({"title": title, "url": url, "snippet": snippet})
                if len(results) >= 8:
                    break
            if results:
                return results
            if attempt < 2:
                time.sleep(4 + attempt * 3)
        except Exception:
            if attempt < 2:
                time.sleep(4 + attempt * 3)
        finally:
            _ddg_limiter.release()
    return []


def call_with_web_search(model, query, system_prompt="", temperature=0.7, timeout=120, max_search_rounds=2):
    """Multi-turn tool use: model requests web_search -> we execute -> feed back -> model answers with citations."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})

    all_search_results = []
    all_search_queries = []
    total_latency = 0
    temp = temperature

    for round_num in range(max_search_rounds + 1):
        payload = {"model": model, "messages": messages, "tools": [_WEB_SEARCH_TOOL], "temperature": temp, "max_tokens": 4096}
        started = time.perf_counter()
        try:
            resp = requests.post(f"{GATEWAY_BASE_URL}/chat/completions", headers=_headers(), json=payload, timeout=timeout)
        except requests.Timeout:
            return {"status": "error", "error": "timeout", "latency_ms": int((time.perf_counter() - started) * 1000)}
        round_latency = int((time.perf_counter() - started) * 1000)
        total_latency += round_latency

        if resp.status_code != 200:
            error_text = resp.text[:500].lower()
            if "temperature" in error_text and temp != 1:
                temp = 1
                continue
            return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text[:500]}", "latency_ms": total_latency}

        data = resp.json()
        msg = data["choices"][0]["message"]

        if msg.get("tool_calls"):
            messages.append(msg)
            for tc in msg["tool_calls"]:
                fn = tc["function"]
                args = json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"]
                search_query = args.get("query", "")
                all_search_queries.append(search_query)
                results = _execute_web_search(search_query)
                all_search_results.extend(results)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(results[:6], ensure_ascii=False)})
        else:
            return {
                "status": "success",
                "data": data,
                "latency_ms": total_latency,
                "search_queries": all_search_queries,
                "search_results": all_search_results,
                "raw_response": data
            }

    # Force final answer without tools if max rounds exceeded
    messages.append({"role": "user", "content": "Based on the search results above, give your final answer now with Markdown citations that include each source title and URL."})
    payload = {"model": model, "messages": messages, "temperature": temp, "max_tokens": 4096}
    started = time.perf_counter()
    try:
        resp = requests.post(f"{GATEWAY_BASE_URL}/chat/completions", headers=_headers(), json=payload, timeout=timeout)
    except requests.Timeout:
        return {"status": "error", "error": "timeout on forced answer", "latency_ms": total_latency}
    total_latency += int((time.perf_counter() - started) * 1000)
    if resp.status_code == 200:
        return {"status": "success", "data": resp.json(), "latency_ms": total_latency,
                "search_queries": all_search_queries, "search_results": all_search_results, "raw_response": resp.json()}
    return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text[:500]}", "latency_ms": total_latency}


def extract_response_text(api_result):
    if api_result.get("status") != "success":
        return ""
    choices = api_result.get("data", {}).get("choices", [])
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "") or ""


def extract_citations(api_result):
    if api_result.get("status") != "success":
        return []
    citations = []
    seen = set()
    choices = api_result.get("data", {}).get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        for i, ann in enumerate(message.get("annotations", [])):
            if ann.get("type") == "url_citation":
                url = ann.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    citations.append({"title": ann.get("title", ""), "url": url, "snippet": ann.get("text", ""), "position": len(citations) + 1})

    # Extract markdown links from response text
    text = extract_response_text(api_result)
    for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
        url = match.group(2)
        if url not in seen:
            seen.add(url)
            citations.append({"title": match.group(1), "url": url, "snippet": "", "position": len(citations) + 1})

    # Also include search_results from the multi-turn loop as supplementary
    for sr in api_result.get("search_results", []):
        url = sr.get("url", "")
        if url and url not in seen:
            seen.add(url)
            citations.append({"title": sr.get("title", ""), "url": url, "snippet": sr.get("snippet", ""), "source": "web_search", "position": len(citations) + 1})

    return citations


def build_ecommerce_query(template, context=None):
    ctx = {"year": CURRENT_YEAR}
    if context:
        ctx.update(context)
    result = template
    for key, value in ctx.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result
