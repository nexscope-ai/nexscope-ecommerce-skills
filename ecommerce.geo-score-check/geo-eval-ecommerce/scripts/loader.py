"""Load configuration and queries."""

import csv
import json
from datetime import date
from pathlib import Path


CURRENT_YEAR = str(date.today().year)


class AppConfig:
    """App runtime configuration."""
    def __init__(self, profile, engines, engine_configs=None, runs_dir="data/runs",
                 api_parallel=4, eval_parallel=4, eval_batch_size=3, subagent_parallelism=2,
                 capture_timeout_ms=60000, eval_timeout_s=120, eval_max_retries=2,
                 engine_concurrency=None, base_dir=None):
        self.profile = profile
        self.engines = engines
        self.engine_configs = engine_configs or {}
        self.runs_dir = Path(runs_dir)
        self.api_parallel = api_parallel
        self.eval_parallel = eval_parallel
        self.eval_batch_size = eval_batch_size
        self.subagent_parallelism = subagent_parallelism
        self.capture_timeout_ms = capture_timeout_ms
        self.eval_timeout_s = eval_timeout_s
        self.eval_max_retries = eval_max_retries
        self.engine_concurrency = engine_concurrency or {}
        self.base_dir = base_dir or Path(".")


class Query:
    """Single evaluation query."""
    def __init__(self, id, query, category="", user_persona="", notes=""):
        self.id = id
        self.query = query
        self.category = category
        self.user_persona = user_persona
        self.notes = notes


def load_config(base_dir=None):
    """Load config.json and return AppConfig."""
    base_dir = Path(base_dir) if base_dir else Path(".")
    config_path = base_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))

    engines = raw.get("engines", [])
    if isinstance(engines, list) and engines and isinstance(engines[0], dict):
        engine_names = [e["name"] for e in engines]
        engine_configs = {e["name"]: e for e in engines}
    elif isinstance(engines, list):
        engine_names = engines
        engine_configs = {}
    else:
        engine_names = []
        engine_configs = {}

    return AppConfig(
        profile=raw.get("profile", ""),
        engines=engine_names,
        engine_configs=engine_configs,
        runs_dir=raw.get("runs_dir", "data/runs"),
        api_parallel=int(raw.get("api_parallel", 4)),
        eval_parallel=int(raw.get("eval_parallel", 4)),
        eval_batch_size=int(raw.get("eval_batch_size", 3)),
        subagent_parallelism=int(raw.get("subagent_parallelism", 2)),
        capture_timeout_ms=int(raw.get("capture_timeout_ms", 60000)),
        eval_timeout_s=int(raw.get("eval_timeout_s", 120)),
        eval_max_retries=int(raw.get("eval_max_retries", 2)),
        engine_concurrency=raw.get("engine_concurrency", {}),
        base_dir=base_dir,
    )


def load_queries(config, profile=None):
    """Load queries from profiles/{profile}/queries.csv with {{year}} injection."""
    profile_name = profile or config.profile
    csv_path = config.base_dir / "profiles" / profile_name / "queries.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"queries.csv not found: {csv_path}")

    queries = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            query_id = (row.get("id") or "").strip()
            query_text = (row.get("query") or "").strip()
            if not query_id or not query_text:
                continue
            # Inject current year
            query_text = query_text.replace("{{year}}", CURRENT_YEAR)
            queries.append(Query(
                id=query_id,
                query=query_text,
                category=(row.get("category") or "").strip(),
                user_persona=(row.get("user_persona") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            ))
    return queries


def load_product_info(config, profile=None):
    """Load product.md for the given profile."""
    profile_name = profile or config.profile
    path = config.base_dir / "profiles" / profile_name / "product.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def filter_queries(queries, ids=None, category=None):
    """Filter queries by ID list or category."""
    if ids:
        id_set = set(ids)
        return [q for q in queries if q.id in id_set]
    if category:
        return [q for q in queries if q.category == category]
    return queries
