"""Evaluation task batch generator."""

import json
from pathlib import Path


def _read_file(path):
    if Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    return ""


def prepare_eval_tasks(config, run_dir, batch_size=None):
    """Generate eval batch task packages."""
    if batch_size is None:
        batch_size = config.eval_batch_size

    normalized_dir = run_dir / "normalized"
    eval_dir = run_dir / "eval"
    tasks_dir = run_dir / "tasks" / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir.mkdir(parents=True, exist_ok=True)

    skill_dir = Path(__file__).parent.parent
    evaluator_template = _read_file(skill_dir / "assets" / "prompts" / "evaluator.md")
    product_md = _read_file(config.base_dir / "profiles" / config.profile / "product.md")

    pending = []
    for nf in sorted(normalized_dir.glob("*.json")):
        eval_path = eval_dir / nf.name
        if not eval_path.exists():
            pending.append((nf, eval_path))

    tasks = []
    for batch_idx in range(0, len(pending), max(batch_size, 1)):
        batch = pending[batch_idx:batch_idx + batch_size]
        batch_name = f"batch-{batch_idx // batch_size + 1:03d}.md"
        task_path = tasks_dir / batch_name

        input_paths = [str(p[0].relative_to(run_dir)) for p in batch]
        output_paths = [str(p[1].relative_to(run_dir)) for p in batch]

        prompt_filled = evaluator_template.replace("{product_info}", product_md.strip())
        md_parts = [
            "# Eval Batch Task\n",
            "## Evaluator Prompt\n",
            prompt_filled,
            "\n---\n",
            "## File List\n",
            f"- Profile: `{config.profile}`",
            "- Input:",
            *[f"  - `{p}`" for p in input_paths],
            "- Output:",
            *[f"  - `{p}`" for p in output_paths],
            "\n## Execution Rules\n",
            "1. Generate independent eval JSON for each input file",
            "2. Strictly follow output schema",
            "3. product_recommendations must list all recommended products",
            "4. competitors_mentioned truncate to top 3",
        ]
        task_path.write_text("\n".join(md_parts), encoding="utf-8")

        tasks.append({
            "type": "eval_batch",
            "task_path": str(task_path.relative_to(run_dir)),
            "input_paths": input_paths,
            "output_paths": output_paths,
            "status": "pending",
        })

    manifest = {
        "schema_version": "task_manifest.v1",
        "run_id": run_dir.name,
        "profile": config.profile,
        "tasks": tasks,
    }
    manifest_path = run_dir / "tasks" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
