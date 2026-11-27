#!/usr/bin/env python3
"""Analyze anonymized Cargo telemetry (data/runs-public.jsonl or local runs.jsonl)."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS = ROOT / "data" / "runs-public.jsonl"


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize anonymized Cargo timing logs.")
    parser.add_argument("--input", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--scope", choices=["fmt", "xtask", "focused", "full", "other"])
    args = parser.parse_args()

    runs = [json.loads(ln) for ln in args.input.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if args.scope:
        runs = [r for r in runs if r.get("scope") == args.scope]

    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in runs:
        sub = r.get("subcommand") or "?"
        if r.get("xtask_kind"):
            sub = f"xtask:{r['xtask_kind']}"
        groups[(r.get("env_hash") or "?", r.get("scope") or "other", sub)].append(r)

    print(f"Total runs: {len(runs)}\n")
    print(f"{'env_hash':<13} {'scope':<8} {'cmd':<15} {'n':>4} {'p50(s)':>7} {'mean(s)':>7} {'p90(s)':>7} {'max(s)':>7} {'rss(MiB)':>8} {'sc_hit%':>7}")
    for (env_hash, scope, sub), grp in sorted(groups.items()):
        walls = sorted(r["wall_ms"] / 1000.0 for r in grp if r.get("wall_ms") is not None)
        rss = [r["max_rss_kb"] / 1024.0 for r in grp if r.get("max_rss_kb")]
        hits = sum(r.get("sccache_hits", 0) for r in grp)
        misses = sum(r.get("sccache_misses", 0) for r in grp)
        hit_pct = f"{hits / (hits + misses) * 100:.1f}%" if (hits + misses) else "n/a"
        avg_rss = f"{sum(rss) / len(rss):.0f}" if rss else "n/a"
        print(
            f"{env_hash:<13} {scope:<8} {sub:<15} {len(grp):>4} "
            f"{percentile(walls, 0.5):>7.2f} {sum(walls)/len(walls):>7.2f} "
            f"{percentile(walls, 0.9):>7.2f} {max(walls):>7.2f} {avg_rss:>8} {hit_pct:>7}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
