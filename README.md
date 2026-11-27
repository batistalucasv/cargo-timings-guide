# The Rust Compile Journal (`cargo-timings-guide`)

> **Issue #01 — Taming an 883-Package Rust Workspace Across Multi-Worktree AI Agents**  
> *Real telemetry from **1,091 Cargo runs**, **14 configuration profiles**, and controlled hardware/linker/cache experiments — with zero private code leaked.*

[![Telemetry Runs](https://img.shields.io/badge/telemetry-1%2C091_real_runs-blue)](#headline-results)
[![Profiles Tested](https://img.shields.io/badge/profiles-14_configs-orange)](#table-of-contents)
[![Privacy Gate](https://img.shields.io/badge/privacy-automated_sanitization-brightgreen)](issues/04-privacy-preserving-cargo-telemetry.md)

---

## Editorial Context: What Kind of Project We Build

Most Rust compile-time guides assume **one developer editing one checkout**. Our setup is the opposite:

- **Project shape:** A large, cross-platform Rust desktop & WebAssembly application workspace (**15 internal crates** spanning UI, layout engine, document/graphics core, PDF/file-format pipelines, rendering, geometry, CLI, and `xtask` automation), pulling **883 packages** in `Cargo.lock` and up to **754 compilation units** in a single heavy UI/test build.
- **Delivery model:** Continuous, high-concurrency development across **multiple parallel Git worktrees** driven by autonomous coding agents and human reviewers. Every fix is shipped as an **atomic, single-commit PR** validated locally before CI runs the full Linux/macOS/Windows matrix on GitHub Actions.
- **Hardware envelope:** 8-core / 16-thread Linux workstation (`Ryzen 7 5700X`), **30.26 GiB RAM with 0 GiB swap**, and mixed storage (**SATA SSD at ~430 MB/s** vs **spinning HDDs at ~90 MB/s**).

### The Five Sizes of Cargo in Our Daily Loop

Not all `cargo` commands behave the same. Across `1,091` recorded runs in [`data/summary.json`](data/summary.json), our workload splits into five distinct tiers:

| Workload Tier | Typical Commands | Count | Median | Mean | p90 | Max | Avg / Peak RAM |
|---|---|---:|---:|---:|---:|---:|---:|
| **1. Micro / Formatting** | `cargo fmt --all -- --check` | 318 | 3.58s | 3.98s | 3.74s | 20.32s | 151 / 246 MiB |
| **2. Repo Automation** | `cargo xtask layers`, `assets`, etc. | 61 | 1.29s | 3.08s | 7.21s | 24.13s | 230 / 267 MiB |
| **3. Focused Iteration** | `clippy -p <crate>`, `nextest/test --lib <filter>` | 686 | 16.09s | 34.91s | 81.52s | 489.30s | 1,900 / 5,819 MiB |
| **4. Full Verification** | `cargo xtask wasm` | 8 | 23.86s | 30.03s | 56.39s | 109.31s | 782 / 887 MiB |
| **5. Release Profiling** | `build/run --release --example <probe>` | 18 | 169.07s | 153.82s | 231.61s | 424.70s | 4,416 / 5,826 MiB |

---

## Headline Results: Baseline vs. Final Profile

Comparing our initial baseline (`a6ef96503714`, `n=64`) against our stabilized production configuration (`9edf022122b2`, `n=640`):

| Metric | Baseline (`a6ef96503714`) | Final Active (`9edf022122b2`) | Delta |
|---|---:|---:|---:|
| **Overall Mean Wall Time** | 38.00s | **23.08s** | **-39.3%** |
| **Overall p90 Wall Time** | 117.72s | **58.43s** | **-50.4%** |
| **`cargo clippy` Mean** | 63.42s | **15.65s** | **-75.3% (4.1x faster)** |
| **`cargo nextest` Mean / Median** | 52.76s / 26.23s | **32.62s / 15.85s** | **-38.2% / -39.6%** |
| **Average Peak RAM** | 1,646 MiB | **1,238 MiB** | **-24.8%** |

---

## Table of Contents

| Issue | Title | Key Takeaway |
|---|---|---|
| **Issue 01** | [Context, Workload Taxonomy & The Multi-Agent OOM Problem](issues/01-context-and-multi-agent-oom.md) | Why `flock` serialization + `jobs = 14` + `--lib` filtering beats parallel Cargo chaos |
| **Issue 02** | [Storage & `sccache`: SSD vs. HDD vs. `/dev/shm`](issues/02-storage-and-sccache-benchmarks.md) | Moving `sccache` from 93 MB/s HDD to 433 MB/s SSD cut hot `nextest` to **7.83s** without burning RAM |
| **Issue 03** | [Linker Wars & Profile Tuning (`mold`, `wild`, Incremental, `line-tables-only`)](issues/03-linker-and-profile-experiments.md) | Why `CARGO_INCREMENTAL=0` hurt local iteration and how `mold` + `opt-level=0` + `codegen-units=256` won |
| **Issue 04** | [Publishing Real Cargo Telemetry Without Leaking Private Data](issues/04-privacy-preserving-cargo-telemetry.md) | Our two-layer anonymization pipeline + automated `check_privacy.py` gate |

---

## Reproducible Kit

Want to apply and measure the same setup on your own Rust workspace?

- [`kit/config.toml`](kit/config.toml) — Drop-in `~/.cargo/config.toml` template (`mold`, `sccache` on SSD, `line-tables-only`, `split-debuginfo = "unpacked"`, `codegen-units = 256`).
- [`kit/analyze.py`](kit/analyze.py) — Statistical analyzer (`p50`, `mean`, `p90`, `max`, RSS, `sccache` hit rate) over anonymized `runs-public.jsonl`.
- [`scripts/check_privacy.py`](scripts/check_privacy.py) — Automated privacy gate ensuring zero local paths, repo names, or test identifiers ever enter the public repository.
- [`data/summary.json`](data/summary.json) & [`data/runs-public.jsonl`](data/runs-public.jsonl) — Full sanitized dataset (`1,091` runs).
