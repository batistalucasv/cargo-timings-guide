#!/usr/bin/env python3
"""Generate crisp, data-driven editorial SVG charts for The Rust Compile Journal."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SUMMARY_PATH = ROOT / "data" / "summary.json"
RUNS_PATH = ROOT / "data" / "runs-public.jsonl"


def write_banner() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 340" width="1200" height="340" role="img" aria-label="The Rust Compile Journal — Issue 01">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b101b"/>
      <stop offset="55%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#1c1512"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f97316"/>
      <stop offset="50%" stop-color="#fb923c"/>
      <stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#ffffff" stroke-opacity="0.035" stroke-width="1"/>
    </pattern>
  </defs>

  <rect width="1200" height="340" rx="18" fill="url(#bg)"/>
  <rect width="1200" height="340" rx="18" fill="url(#grid)"/>
  <rect x="0" y="0" width="1200" height="5" fill="url(#accent)"/>
  <rect x="0.5" y="0.5" width="1199" height="339" rx="18" fill="none" stroke="#334155" stroke-opacity="0.6"/>

  <!-- Top editorial masthead bar -->
  <text x="56" y="54" fill="#fb923c" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13" font-weight="700" letter-spacing="2.5">ENGINEERING FIELD REPORT  ·  ISSUE #01  ·  OPEN TELEMETRY</text>
  <rect x="964" y="34" width="180" height="28" rx="14" fill="#0f291e" stroke="#10b981" stroke-opacity="0.5"/>
  <circle cx="984" cy="48" r="4.5" fill="#10b981"/>
  <text x="998" y="52.5" fill="#6ee7b7" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" font-weight="600">0 LEAKS VERIFIED</text>

  <!-- Main magazine title -->
  <text x="56" y="122" fill="#f8fafc" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="50" font-weight="800" letter-spacing="-1">The Rust Compile Journal</text>
  <text x="56" y="162" fill="#cbd5e1" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="21" font-weight="400">Taming an 883-Package Workspace Across Multi-Worktree AI Agents</text>
  <text x="56" y="191" fill="#94a3b8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13.5">1,091 real Cargo runs  ·  14 env_hash profiles  ·  mold vs wild  ·  SSD vs HDD vs /dev/shm  ·  flock queue</text>

  <!-- KPI strip cards -->
  <g transform="translate(56, 222)">
    <!-- Card 1 -->
    <rect x="0" y="0" width="252" height="82" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.2"/>
    <text x="18" y="26" fill="#94a3b8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11.5" font-weight="600" letter-spacing="1">CLIPPY MEAN TIME</text>
    <text x="18" y="60" fill="#fb923c" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="30" font-weight="800">-75.3%</text>
    <text x="136" y="58" fill="#cbd5e1" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">63.4s → 15.7s</text>

    <!-- Card 2 -->
    <rect x="278" y="0" width="252" height="82" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.2"/>
    <text x="296" y="26" fill="#94a3b8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11.5" font-weight="600" letter-spacing="1">OVERALL P90 WALL</text>
    <text x="296" y="60" fill="#38bdf8" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="30" font-weight="800">-50.4%</text>
    <text x="414" y="58" fill="#cbd5e1" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">117.7s → 58.4s</text>

    <!-- Card 3 -->
    <rect x="556" y="0" width="252" height="82" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.2"/>
    <text x="574" y="26" fill="#94a3b8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11.5" font-weight="600" letter-spacing="1">HOT NEXTEST LOOP</text>
    <text x="574" y="60" fill="#34d399" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="30" font-weight="800">7.83s</text>
    <text x="670" y="58" fill="#cbd5e1" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">SSD sccache</text>

    <!-- Card 4 -->
    <rect x="834" y="0" width="254" height="82" rx="12" fill="#0f172a" stroke="#1e293b" stroke-width="1.2"/>
    <text x="852" y="26" fill="#94a3b8" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11.5" font-weight="600" letter-spacing="1">AVG RAM / OOM KILLS</text>
    <text x="852" y="60" fill="#a78bfa" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="30" font-weight="800">-24.8%</text>
    <text x="970" y="58" fill="#cbd5e1" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">0 OOMs (0 swap)</text>
  </g>
</svg>
"""
    (ASSETS / "banner.svg").write_text(svg, encoding="utf-8")


def write_baseline_vs_final() -> None:
    rows = [
        ("Overall p90 Wall", 117.72, 58.43, "-50.4%"),
        ("cargo clippy (mean)", 63.42, 15.65, "-75.3%"),
        ("cargo nextest (mean)", 52.76, 32.62, "-38.2%"),
        ("Overall Mean Wall", 38.00, 23.08, "-39.3%"),
        ("cargo nextest (p50)", 26.23, 15.85, "-39.6%"),
    ]
    max_val = 125.0
    bar_x = 250
    bar_w = 570
    row_h = 68
    start_y = 94
    height = start_y + len(rows) * row_h + 44

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 {height}" width="980" height="{height}" role="img" aria-label="Baseline vs Final Active Profile Comparison">',
        '  <rect width="980" height="' + str(height) + '" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '  <text x="32" y="40" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="20" font-weight="700">Baseline (a6ef96503714, n=64) vs. Final Active Profile (9edf022122b2, n=640)</text>',
        '  <text x="32" y="63" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="12.5">Lower is better (wall-clock seconds) · Measured across real multi-worktree development loops</text>',
        '  <rect x="690" y="24" width="12" height="12" rx="3" fill="#64748b"/>',
        '  <text x="708" y="34.5" fill="#c9d1d9" font-family="ui-monospace, monospace" font-size="12">Baseline</text>',
        '  <rect x="792" y="24" width="12" height="12" rx="3" fill="#f97316"/>',
        '  <text x="810" y="34.5" fill="#c9d1d9" font-family="ui-monospace, monospace" font-size="12">Final (SSD + mold)</text>',
    ]

    # vertical gridlines
    for sec in (0, 30, 60, 90, 120):
        gx = bar_x + (sec / max_val) * bar_w
        parts.append(f'  <line x1="{gx:.1f}" y1="{start_y - 12}" x2="{gx:.1f}" y2="{height - 32}" stroke="#21262d" stroke-dasharray="3,4"/>')
        parts.append(f'  <text x="{gx:.1f}" y="{height - 14}" text-anchor="middle" fill="#6e7681" font-family="ui-monospace, monospace" font-size="11">{sec}s</text>')

    for idx, (label, base_v, fin_v, delta) in enumerate(rows):
        y = start_y + idx * row_h
        w_base = (base_v / max_val) * bar_w
        w_fin = (fin_v / max_val) * bar_w
        parts.append(f'  <text x="32" y="{y + 24}" fill="#e6edf3" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="14" font-weight="600">{label}</text>')
        # baseline bar
        parts.append(f'  <rect x="{bar_x}" y="{y + 2}" width="{w_base:.1f}" height="18" rx="4" fill="#475569"/>')
        parts.append(f'  <text x="{bar_x + w_base + 8:.1f}" y="{y + 15.5}" fill="#94a3b8" font-family="ui-monospace, monospace" font-size="12">{base_v:.2f}s</text>')
        # final bar
        parts.append(f'  <rect x="{bar_x}" y="{y + 24}" width="{w_fin:.1f}" height="18" rx="4" fill="#f97316"/>')
        parts.append(f'  <text x="{bar_x + w_fin + 8:.1f}" y="{y + 37.5}" fill="#fed7aa" font-family="ui-monospace, monospace" font-size="12" font-weight="700">{fin_v:.2f}s</text>')
        # delta pill
        parts.append(f'  <rect x="874" y="{y + 11}" width="78" height="24" rx="12" fill="#0f291e" stroke="#10b981" stroke-opacity="0.5"/>')
        parts.append(f'  <text x="913" y="{y + 27}" text-anchor="middle" fill="#6ee7b7" font-family="ui-monospace, monospace" font-size="12" font-weight="700">{delta}</text>')

    parts.append("</svg>")
    (ASSETS / "chart-baseline-vs-final.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_storage_and_linker_chart() -> None:
    # Dual panel: left = disk throughput (MB/s), right = controlled warm nextest loop (s)
    disks = [
        ("SATA SSD (target + sccache)", 421.0, 433.0, "#38bdf8"),
        ("HDD #1 (workspace repos)", 91.0, 113.0, "#64748b"),
        ("HDD #2 (old sccache + reg)", 87.0, 93.0, "#475569"),
    ]
    warm = [
        ("mold + sccache SSD", 7.83, "#10b981", "WINNER"),
        ("mold + /dev/shm (RAM)", 8.01, "#38bdf8", "Eats RAM"),
        ("wild linker + HDD", 9.98, "#a78bfa", "clippy fail"),
        ("mold + sccache HDD", 12.64, "#f59e0b", "HDD I/O"),
        ("mold + no sccache", 17.84, "#ef4444", "No cache"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 330" width="980" height="330" role="img" aria-label="Storage Throughput vs Controlled Warm Nextest Loop">',
        '  <rect width="980" height="330" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '  <line x1="470" y1="24" x2="470" y2="306" stroke="#21262d" stroke-width="1.5"/>',
        # Left panel header
        '  <text x="28" y="42" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="17" font-weight="700">Measured Storage Throughput</text>',
        '  <text x="28" y="62" fill="#8b949e" font-family="ui-monospace, monospace" font-size="11.5">Sequential Write / Direct Read (MB/s · Higher is better)</text>',
        # Right panel header
        '  <text x="498" y="42" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="17" font-weight="700">Controlled Warm Test Loop (app-ui)</text>',
        '  <text x="498" y="62" fill="#8b949e" font-family="ui-monospace, monospace" font-size="11.5">Same target &amp; test filter (seconds · Lower is better)</text>',
    ]

    for i, (name, wr, rd, col) in enumerate(disks):
        y = 92 + i * 70
        ww = (wr / 460.0) * 330
        rw = (rd / 460.0) * 330
        parts.append(f'  <text x="28" y="{y}" fill="#e6edf3" font-family="-apple-system, sans-serif" font-size="13" font-weight="600">{name}</text>')
        parts.append(f'  <rect x="28" y="{y + 10}" width="{ww:.1f}" height="15" rx="3.5" fill="{col}" fill-opacity="0.75"/>')
        parts.append(f'  <text x="{28 + ww + 8:.1f}" y="{y + 22}" fill="#cbd5e1" font-family="ui-monospace, monospace" font-size="11.5">W {wr:.0f} MB/s</text>')
        parts.append(f'  <rect x="28" y="{y + 29}" width="{rw:.1f}" height="15" rx="3.5" fill="{col}"/>')
        parts.append(f'  <text x="{28 + rw + 8:.1f}" y="{y + 41}" fill="#f8fafc" font-family="ui-monospace, monospace" font-size="11.5" font-weight="700">R {rd:.0f} MB/s</text>')

    for i, (label, val, col, note) in enumerate(warm):
        y = 88 + i * 44
        bw = (val / 20.0) * 265
        parts.append(f'  <text x="498" y="{y + 12}" fill="#e6edf3" font-family="-apple-system, sans-serif" font-size="12.5" font-weight="600">{label}</text>')
        parts.append(f'  <rect x="498" y="{y + 18}" width="{bw:.1f}" height="14" rx="3.5" fill="{col}"/>')
        parts.append(f'  <text x="{498 + bw + 8:.1f}" y="{y + 29.5}" fill="#f8fafc" font-family="ui-monospace, monospace" font-size="12" font-weight="700">{val:.2f}s</text>')
        parts.append(f'  <text x="952" y="{y + 29}" text-anchor="end" fill="#8b949e" font-family="ui-monospace, monospace" font-size="11">{note}</text>')

    parts.append("</svg>")
    (ASSETS / "chart-storage-bench.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_workloads_chart() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    by_scope = summary["by_scope"]
    tiers = [
        ("xtask", "Repo Automation (xtask)", "#38bdf8"),
        ("fmt", "Formatting (cargo fmt)", "#818cf8"),
        ("focused", "Focused Dev (clippy/test/nextest)", "#f97316"),
        ("full", "Full Verification (xtask wasm)", "#eab308"),
        ("other", "Release Profiling (--release)", "#ec4899"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 350" width="980" height="350" role="img" aria-label="Five Sizes of Cargo Workloads">',
        '  <rect width="980" height="350" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '  <text x="32" y="40" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="19" font-weight="700">The Five Sizes of Cargo (n = ' + f'{summary["total_runs"]:,}' + ' Real Runs)</text>',
        '  <text x="32" y="62" fill="#8b949e" font-family="ui-monospace, monospace" font-size="12">Median vs. p90 Wall Time (left) and Average vs. Peak RAM Footprint (right)</text>',
        '  <text x="278" y="88" fill="#8b949e" font-family="ui-monospace, monospace" font-size="11" font-weight="700">WALL TIME (p50 solid / p90 faded)</text>',
        '  <text x="688" y="88" fill="#8b949e" font-family="ui-monospace, monospace" font-size="11" font-weight="700">PEAK RAM (avg / max MiB)</text>',
    ]

    for i, (key, title, col) in enumerate(tiers):
        st = by_scope[key]
        y = 108 + i * 46
        p50 = st["p50_s"]
        p90 = st["p90_s"]
        w50 = max(4.0, (p50 / 250.0) * 330)
        w90 = max(w50, (p90 / 250.0) * 330)
        ram_avg = st["avg_rss_mib"]
        ram_max = st["max_rss_mib"]
        wr_avg = max(4.0, (ram_avg / 6200.0) * 200)
        wr_max = max(wr_avg, (ram_max / 6200.0) * 200)

        parts.append(f'  <text x="32" y="{y + 13}" fill="#e6edf3" font-family="-apple-system, sans-serif" font-size="13" font-weight="600">{title}</text>')
        parts.append(f'  <text x="32" y="{y + 29}" fill="#6e7681" font-family="ui-monospace, monospace" font-size="11">n = {st["count"]} runs</text>')

        # wall bars
        parts.append(f'  <rect x="278" y="{y + 4}" width="{w90:.1f}" height="18" rx="4" fill="{col}" fill-opacity="0.28"/>')
        parts.append(f'  <rect x="278" y="{y + 4}" width="{w50:.1f}" height="18" rx="4" fill="{col}"/>')
        parts.append(f'  <text x="{278 + w90 + 8:.1f}" y="{y + 17}" fill="#cbd5e1" font-family="ui-monospace, monospace" font-size="11.5">{p50:.1f}s / {p90:.1f}s</text>')

        # ram bars
        parts.append(f'  <rect x="688" y="{y + 4}" width="{wr_max:.1f}" height="18" rx="4" fill="#a78bfa" fill-opacity="0.28"/>')
        parts.append(f'  <rect x="688" y="{y + 4}" width="{wr_avg:.1f}" height="18" rx="4" fill="#a78bfa"/>')
        parts.append(f'  <text x="952" y="{y + 17}" text-anchor="end" fill="#cbd5e1" font-family="ui-monospace, monospace" font-size="11.5">{ram_avg:,} / {ram_max:,}</text>')

    parts.append("</svg>")
    (ASSETS / "chart-workloads.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    write_banner()
    write_baseline_vs_final()
    write_storage_and_linker_chart()
    write_workloads_chart()
    print(f"Generated 4 SVG assets in {ASSETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
