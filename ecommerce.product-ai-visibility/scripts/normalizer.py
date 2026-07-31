"""Convert API capture results to normalized format."""

import json
from pathlib import Path


def normalize_api_capture(capture_path):
    """Convert a single API capture to normalized format."""
    capture = json.loads(Path(capture_path).read_text(encoding="utf-8"))

    if capture.get("status") == "failed":
        return None

    response_text = capture.get("response_text", "")
    if not response_text:
        return None

    citations = capture.get("citations", [])
    search_results = [
        {
            "title": c.get("title", ""),
            "url": c.get("url", ""),
            "snippet": c.get("snippet", ""),
            "source": "api_citation",
            "rank": c.get("position", i + 1),
            "domain": _extract_domain(c.get("url", "")),
        }
        for i, c in enumerate(citations)
    ]

    return {
        "schema_version": "normalized_response.v1",
        "query_id": capture["query_id"],
        "engine": capture["engine"],
        "timestamp": capture.get("timestamp", ""),
        "query_meta": {"category": capture.get("category", "")},
        "messages": [
            {"role": "user", "content": capture.get("query_text", "")},
            {"role": "assistant", "content": response_text},
        ],
        "response_content": response_text,
        "citations": citations,
        "search_queries": capture.get("search_queries", []),
        "search_results": search_results,
        "engine_metadata": {
            "model_label": capture.get("model", ""),
            "response_id": None,
            "conversation_id": None,
            "message_id": None,
            "raw_network_url": None,
        },
        "quality": {
            "structured_network_used": True,
            "dom_fallback_used": False,
            "partial": False,
            "missing_fields": [],
        },
        "latency_ms": capture.get("latency_ms", 0),
    }


def normalize_run(base_dir, run_dir, resume=False):
    """Normalize all capture files in a run directory."""
    capture_dir = run_dir / "captures"
    normalized_dir = run_dir / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    existing = set()
    if resume and normalized_dir.exists():
        existing = {p.stem for p in normalized_dir.glob("*.json")}

    written = []
    for capture_path in sorted(capture_dir.glob("*.json")):
        if capture_path.stem.endswith(".task"):
            continue
        if resume and capture_path.stem in existing:
            continue

        normalized = normalize_api_capture(capture_path)
        if normalized is None:
            continue

        output_path = normalized_dir / capture_path.name
        output_path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written.append(output_path)

    return written


def _extract_domain(url):
    """Extract domain from URL."""
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return ""
