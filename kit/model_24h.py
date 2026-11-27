#!/usr/bin/env python3
"""Stratified bootstrap model (10,000 resamples) projecting 24h Cargo time savings & M/G/1 queue impact."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS = ROOT / "data" / "runs-public.jsonl"
DEV_SUBS = ["fmt", "xtask", "clippy", "test", "nextest"]


def stratified_bootstrap(
    base_by_sub: dict[str, list[float]],
    final_by_sub: dict[str, list[float]],
    weights: dict[str, float],
    runs_per_24h: int,
    iters: int = 10_000,
    seed: int = 42,
) -> dict:
    rng = random.Random(seed)
    saved_h, pct_red, base_h_list, final_h_list = [], [], [], []
    for _ in range(iters):
        ma = sum(w * (sum(rng.choices(base_by_sub[s], k=len(base_by_sub[s]))) / len(base_by_sub[s])) for s, w in weights.items())
        mb = sum(w * (sum(rng.choices(final_by_sub[s], k=len(final_by_sub[s]))) / len(final_by_sub[s])) for s, w in weights.items())
        ta = ma * runs_per_24h / 3600.0
        tb = mb * runs_per_24h / 3600.0
        base_h_list.append(ta)
        final_h_list.append(tb)
        saved_h.append(ta - tb)
        pct_red.append((ma - mb) / ma * 100.0)
    saved_h.sort()
    pct_red.sort()
    return {
        "runs_24h": runs_per_24h,
        "base_h": round(statistics.mean(base_h_list), 2),
        "final_h": round(statistics.mean(final_h_list), 2),
        "saved_h": round(statistics.mean(saved_h), 2),
        "saved_ci95": [round(saved_h[int(0.025 * iters)], 2), round(saved_h[int(0.975 * iters)], 2)],
        "pct_reduction": round(statistics.mean(pct_red), 1),
        "pct_ci95": [round(pct_red[int(0.025 * iters)], 1), round(pct_red[int(0.975 * iters)], 1)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Project 24-hour compile-time savings via stratified bootstrap.")
    parser.add_argument("--input", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--iters", type=int, default=10_000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    runs = [json.loads(ln) for ln in args.input.read_text(encoding="utf-8").splitlines() if ln.strip()]
    base_by_sub: dict[str, list[float]] = defaultdict(list)
    final_by_sub: dict[str, list[float]] = defaultdict(list)
    mix_counts: Counter[str] = Counter()

    for r in runs:
        sub = r.get("subcommand")
        if sub not in DEV_SUBS or r.get("wall_ms") is None:
            continue
        w = r["wall_ms"] / 1000.0
        h = r.get("env_hash")
        if h == "a6ef96503714":
            base_by_sub[sub].append(w)
        elif h == "9edf022122b2":
            final_by_sub[sub].append(w)
            mix_counts[sub] += 1

    total_mix = sum(mix_counts.values())
    weights = {s: mix_counts[s] / total_mix for s in DEV_SUBS}

    scenarios = [
        ("Conservative (light day)", 500),
        ("Observed 24h Average", 872),
        ("Continuous 24h Active Pace", 985),
    ]

    results = []
    for label, n24 in scenarios:
        res = stratified_bootstrap(base_by_sub, final_by_sub, weights, n24, iters=args.iters)
        res["label"] = label
        rho_base = res["base_h"] / 24.0
        rho_final = res["final_h"] / 24.0
        # M/G/1 Pollaczek-Khinchine queue-wait scaling factor: (rho / (1 - rho)) * E[S]
        # Ratio of queue wait (assuming comparable coefficient of variation)
        q_ratio = ((rho_final / (1.0 - rho_final)) * res["final_h"]) / ((rho_base / (1.0 - rho_base)) * res["base_h"])
        res["rho_base_pct"] = round(rho_base * 100, 1)
        res["rho_final_pct"] = round(rho_final * 100, 1)
        res["queue_wait_drop_pct"] = round((1.0 - q_ratio) * 100, 1)
        results.append(res)

    if args.json:
        print(json.dumps({"total_runs": len(runs), "weights": {k: round(v * 100, 1) for k, v in weights.items()}, "scenarios": results}, indent=2))
        return 0

    print(f"Stratified Bootstrap 24h Model ({args.iters:,} resamples · {len(runs):,} runs)")
    print("Empirical dev mix:", ", ".join(f"{s}={weights[s]*100:.1f}%" for s in DEV_SUBS))
    print()
    print(f"{'Scenario':<28} {'Runs':>5} {'Base':>6} {'Final':>6} {'Saved':>7} {'95% CI (h)':>15} {'Red%':>6} {'Rho B->F':>13} {'Queue -%':>9}")
    for r in results:
        ci = f"[{r['saved_ci95'][0]:.2f}, {r['saved_ci95'][1]:.2f}]"
        rho = f"{r['rho_base_pct']:.1f}%->{r['rho_final_pct']:.1f}%"
        print(
            f"{r['label']:<28} {r['runs_24h']:>5} {r['base_h']:>5.2f}h {r['final_h']:>5.2f}h "
            f"{r['saved_h']:>6.2f}h {ci:>15} {r['pct_reduction']:>5.1f}% {rho:>13} {r['queue_wait_drop_pct']:>8.1f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
