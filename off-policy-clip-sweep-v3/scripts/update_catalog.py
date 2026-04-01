#!/usr/bin/env python3
"""
Update catalog.md with latest experiment results from WandB.

Usage:
    # Preview changes (dry run):
    python update_catalog.py --project Off-Policy-Study-v3 --dry-run

    # Update catalog.md:
    python update_catalog.py --project Off-Policy-Study-v3

    # With explicit entity:
    python update_catalog.py --project Off-Policy-Study-v3 --entity my-team
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

# All 10 experiments in the v3 sweep
EXPERIMENTS = [
    {"name": "offpol-v3-cL2.0-cH2.0-kl-off-s2.4", "clip_high": "2.0", "kl": "off"},
    {"name": "offpol-v3-cL2.0-cH2.0-kl-on-s2.4", "clip_high": "2.0", "kl": "on"},
    {"name": "offpol-v3-cL2.0-cH2.2-kl-off-s2.4", "clip_high": "2.2", "kl": "off"},
    {"name": "offpol-v3-cL2.0-cH2.2-kl-on-s2.4", "clip_high": "2.2", "kl": "on"},
    {"name": "offpol-v3-cL2.0-cH2.4-kl-off-s2.4", "clip_high": "2.4", "kl": "off"},
    {"name": "offpol-v3-cL2.0-cH2.4-kl-on-s2.4", "clip_high": "2.4", "kl": "on"},
    {"name": "offpol-v3-cL2.0-cH2.6-kl-off-s2.4", "clip_high": "2.6", "kl": "off"},
    {"name": "offpol-v3-cL2.0-cH2.6-kl-on-s2.4", "clip_high": "2.6", "kl": "on"},
    {"name": "offpol-v3-cL2.0-cH2.8-kl-off-s2.4", "clip_high": "2.8", "kl": "off"},
    {"name": "offpol-v3-cL2.0-cH2.8-kl-on-s2.4", "clip_high": "2.8", "kl": "on"},
]

METRIC_KEY = "val-core/guru_0.3-0.6/acc/mean@1"
CATALOG_PATH = Path(__file__).parent.parent / "catalog.md"


def fetch_results(project: str, entity: str | None) -> dict[str, dict]:
    """Fetch latest results from WandB for all experiment runs."""
    import wandb

    api = wandb.Api()
    path = f"{entity}/{project}" if entity else project

    results = {}
    try:
        runs = api.runs(path)
    except Exception as e:
        print(f"Error fetching runs: {e}")
        return results

    for run in runs:
        if not run.name.startswith("offpol-v3-"):
            continue

        # Get final and best reward from summary/history
        final_reward = run.summary.get(METRIC_KEY)
        status = run.state.upper()  # "finished" -> "FINISHED", "running" -> "RUNNING", etc.

        # Scan history for best reward and corresponding step
        best_reward = None
        best_step = None
        try:
            history = run.scan_history(keys=[METRIC_KEY, "_step"], page_size=1000)
            for row in history:
                val = row.get(METRIC_KEY)
                step = row.get("_step")
                if val is not None:
                    if best_reward is None or val > best_reward:
                        best_reward = val
                        best_step = step
        except Exception:
            pass

        wandb_url = run.url

        results[run.name] = {
            "status": status,
            "final_reward": f"{final_reward:.4f}" if final_reward is not None else "\u2014",
            "best_reward": f"{best_reward:.4f}" if best_reward is not None else "\u2014",
            "best_step": str(best_step) if best_step is not None else "\u2014",
            "wandb_url": wandb_url,
        }

    return results


def generate_catalog(results: dict[str, dict]) -> str:
    """Generate the catalog.md content."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Experiment Catalog",
        "",
        f"> Last updated: {now}",
        "",
        "| Experiment | clip_high | KL | Status | Final Reward | Best Reward | Best Step | WandB |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for exp in EXPERIMENTS:
        name = exp["name"]
        r = results.get(name, {})
        status = r.get("status", "\u2014")
        final_reward = r.get("final_reward", "\u2014")
        best_reward = r.get("best_reward", "\u2014")
        best_step = r.get("best_step", "\u2014")
        wandb_url = r.get("wandb_url")
        wandb_link = f"[link]({wandb_url})" if wandb_url else "\u2014"

        lines.append(
            f"| {name} | {exp['clip_high']} | {exp['kl']} "
            f"| {status} | {final_reward} | {best_reward} | {best_step} | {wandb_link} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Update experiment catalog from WandB")
    parser.add_argument("--project", required=True, help="WandB project name")
    parser.add_argument("--entity", default=None, help="WandB entity (uses WANDB_ENTITY if not set)")
    parser.add_argument("--dry-run", action="store_true", help="Print catalog without writing")
    args = parser.parse_args()

    entity = args.entity or os.environ.get("WANDB_ENTITY")

    print(f"Fetching results from WandB project: {args.project}")
    results = fetch_results(args.project, entity)
    print(f"Found {len(results)} matching runs")

    catalog = generate_catalog(results)

    if args.dry_run:
        print("\n--- DRY RUN (would write to catalog.md) ---\n")
        print(catalog)
    else:
        CATALOG_PATH.write_text(catalog)
        print(f"Updated {CATALOG_PATH}")
        print("Review with: git diff catalog.md")


if __name__ == "__main__":
    main()
