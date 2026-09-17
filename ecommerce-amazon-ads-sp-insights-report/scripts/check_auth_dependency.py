#!/usr/bin/env python3
"""
Dependency Check - ecommerce.amazon-ads-sp-insights-report
========================================================

Check whether the current runtime has installed or loaded the dependency Skill
`ecommerce.amazon-ads-api-access`.

Usage:
    python check_auth_dependency.py            # Default check
    python check_auth_dependency.py --json     # Print the result as JSON

Exit codes (for programmatic parsing by the agent):
    0   → Dependency satisfied (found SKILL.md for ecommerce.amazon-ads-api-access)
    42  → DEPENDENCY_MISSING: Dependency Skill not found; the agent must trigger installation

Structured stderr signals:
    - If the dependency is missing, the first stderr line starts with `DEPENDENCY_MISSING:`,
      followed by a JSON payload containing the required Skill name and recommended installation action.
    - On success, stderr starts with `DEPENDENCY_OK:`.

Note:
    This local discovery script **does not access the network**. It only checks common Skill installation paths on the filesystem.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

REQUIRED_SKILL = "ecommerce.amazon-ads-api-access"
DEPENDENCY_EXIT_CODE = 42


def _split_path_list(raw: Optional[str]) -> list[Path]:
    if not raw or not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(os.pathsep) if p.strip()]
    return [Path(p).expanduser() for p in parts]


def candidate_skill_roots() -> list[Path]:
    roots: list[Path] = []

    for env_var in ("NEXSCOPE_SKILLS_DIR", "SKILLS_DIR", "CURSOR_SKILLS_DIR"):
        p = os.environ.get(env_var)
        if p:
            roots.append(Path(p).expanduser())

    roots.extend(_split_path_list(os.environ.get("HERMES_SKILLS_EXTERNAL_DIRS")))

    for env_var in ("OPENCLAW_WORKSPACE", "OPENCLAW_ROOT", "OPENCLAW_WORKDIR"):
        ws = os.environ.get(env_var)
        if ws:
            w = Path(ws).expanduser()
            roots.append(w / "skills")
            roots.append(w / ".agents" / "skills")

    oc_skills = os.environ.get("OPENCLAW_SKILLS_DIR")
    if oc_skills:
        roots.append(Path(oc_skills).expanduser())

    try:
        cwd = Path.cwd()
        roots.append(cwd / "skills")
        roots.append(cwd / ".agents" / "skills")
    except OSError:
        pass

    here = Path(__file__).resolve()
    if len(here.parents) >= 3:
        roots.append(here.parents[2])
    if len(here.parents) >= 5:
        roots.append(here.parents[4] / "E-commerce-Skills-main")

    home = Path.home()
    roots.extend([
        home / ".claude" / "skills",
        home / ".cursor" / "skills",
        home / ".cursor" / "skills-cursor",
        home / ".nexscope" / "skills",
    ])
    roots.extend([
        home / ".openclaw" / "skills",
        home / ".hermes" / "skills",
    ])

    seen: set[Path] = set()
    unique: list[Path] = []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            rr = r
        if rr not in seen:
            seen.add(rr)
            unique.append(r)
    return unique


def _hermes_category_skill_md(hermes_skills_root: Path) -> Optional[Path]:
    if not hermes_skills_root.is_dir():
        return None
    for category_dir in sorted(hermes_skills_root.iterdir()):
        if not category_dir.is_dir():
            continue
        name = category_dir.name
        if name.startswith(".") or name == ".hub":
            continue
        candidate = category_dir / REQUIRED_SKILL / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def _hermes_plugin_skill_md(home: Path) -> Optional[Path]:
    plugins_root = home / ".hermes" / "plugins"
    if not plugins_root.is_dir():
        return None
    for plugin_dir in sorted(plugins_root.iterdir()):
        if not plugin_dir.is_dir():
            continue
        candidate = plugin_dir / "skills" / REQUIRED_SKILL / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def locate_dependency() -> Optional[Path]:
    home = Path.home()

    for root in candidate_skill_roots():
        target = root / REQUIRED_SKILL / "SKILL.md"
        if target.is_file():
            return target

    hermes_default = home / ".hermes" / "skills"
    found = _hermes_category_skill_md(hermes_default)
    if found is not None:
        return found

    hsh = os.environ.get("HERMES_SKILLS_HOME")
    if hsh:
        found = _hermes_category_skill_md(Path(hsh).expanduser())
        if found is not None:
            return found

    found = _hermes_plugin_skill_md(home)
    if found is not None:
        return found

    return None


def searched_locations_for_report() -> list[str]:
    home = Path.home()
    out: list[str] = [str(p) for p in candidate_skill_roots()]
    out.append(str(home / ".hermes" / "skills"))
    out.append(str(home / ".hermes" / "plugins"))
    hsh = os.environ.get("HERMES_SKILLS_HOME")
    if hsh:
        out.append(str(Path(hsh).expanduser()))
    seen: set[str] = set()
    unique: list[str] = []
    for s in out:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def emit(as_json: bool, ok: bool, payload: dict) -> None:
    prefix = "DEPENDENCY_OK:" if ok else "DEPENDENCY_MISSING:"
    body = json.dumps(payload, ensure_ascii=False)
    if as_json:
        out = dict(payload)
        out["status"] = "ok" if ok else "missing"
        print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"{prefix} {body}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check required dependency skill availability.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout.")
    args = parser.parse_args()

    found = locate_dependency()

    if found is not None:
        emit(as_json=args.json, ok=True, payload={
            "skill": REQUIRED_SKILL,
            "skillMdPath": str(found),
        })
        sys.exit(0)

    payload = {
        "missingSkill": REQUIRED_SKILL,
        "reason": (
            f"ecommerce.amazon-ads-sp-insights-report requires `{REQUIRED_SKILL}`, "
            "but its SKILL.md was not found in common Skill installation paths."
        ),
        "searchedRoots": searched_locations_for_report(),
        "suggestedActions": [
            f"If a skill installer tool is available (e.g. install_skill / skill marketplace MCP), invoke it to install '{REQUIRED_SKILL}' immediately.",
            "Otherwise, ask the user to install the skill from https://www.nexscope.ai/help/skills-external-access?co-from=skillNS and retry.",
            "Do NOT bypass the dependency by calling /api/v1/tools/research/amazonAds/authorizeUrl or /api/v1/tools/research/amazonAds/storeTokens directly from this skill.",
        ],
        "marketplaceUrl": "https://www.nexscope.ai/help/skills-external-access?co-from=skillNS",
    }
    emit(as_json=args.json, ok=False, payload=payload)
    sys.exit(DEPENDENCY_EXIT_CODE)


if __name__ == "__main__":
    main()
