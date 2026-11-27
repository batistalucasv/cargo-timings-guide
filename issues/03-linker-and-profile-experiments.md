<p align="center">
  <a href="../README.md">← Cover</a> ·
  <a href="01-context-and-multi-agent-oom.md">Issue 01</a> ·
  <a href="02-storage-and-sccache-benchmarks.md">Issue 02</a> ·
  <strong>Issue 03</strong> ·
  <a href="04-privacy-preserving-cargo-telemetry.md">Issue 04 →</a>
</p>

# Issue 03 · Linker Wars & Profile Tuning (`mold`, `wild`, Incremental, `line-tables-only`)

> *Controlled A/B results across 14 Cargo profiles—including why disabling incremental compilation backfired locally.*

---

## 1 · Linker Showdown: `mold 3.0` vs. `wild`

We tested `mold 3.0.0` head-to-head against `wild` (`-C link-arg=-B<wild-bin>`) on the exact same `app-ui` crate (`codegen-units = 256`, `opt-level = 0`, `debug = "line-tables-only"`):

| `env_hash` | Linker | `clippy --all-targets` | `nextest` (cold) | `nextest` (warm) |
|---|---|---:|---:|---:|
| **`29de672b6fc0`** | **`mold 3.0.0`** (+ SSD `sccache`) | **9.53s (pass)** | — | **7.83s** |
| `c431e074d48a` | `wild` | 2.46s (**FAILED**) | 401.90s | 9.98s |

> [!WARNING]
> In our tests, `wild` broke `cargo clippy --all-targets` and trailed `mold` by **+2.15s** on the warm test loop (`9.98s` vs `7.83s`). **`mold` remains our production recommendation on Linux.**

---

## 2 · The `CARGO_INCREMENTAL = "0"` Trap

Many CI tutorials advise setting `CARGO_INCREMENTAL = "0"` globally so `rustc` outputs artifacts that `sccache` can cache across branches. On a local workstation, we measured the exact opposite:

| `env_hash` | Incremental Setting | Runs | `sccache` Hit Rate | `nextest` Mean | `nextest` Median |
|---|---|---:|---:|---:|---:|
| `41a80f22062d` | `CARGO_INCREMENTAL = "0"` (global) | 133 | **1.6%** (35 / 2,193) | 61.91s | 44.23s |
| `bbd0a3bbe7c0` | Incremental ON in `dev`/`test` | 195 | 2.4% (31 / 1,239) | 40.31s | 17.44s |
| **`9edf022122b2`** | **Incremental ON + SSD `sccache` + `opt-level=0`** | **640** | **39.6%** (day 2: **63.8%**) | **32.62s** | **15.85s** |

**Why it happened:** Every minor edit to an internal workspace crate invalidated non-incremental compilation and forced `rustc` to re-codegen the whole crate from scratch. Keeping incremental compilation active locally while letting `sccache` cache external dependencies and unchanged crates delivered the best of both worlds.

---

## 3 · `codegen-units`, `line-tables-only`, and `split-debuginfo`

- **Hidden pitfall:** When `CARGO_INCREMENTAL = "0"` is set, `rustc` silently drops `codegen-units` from `256` to **`16`**, throttling LLVM parallelism on large crates.
- **Controlled test (`64` vs `128` vs `256`):** Cold rebuilds of `app-ui` took **349.29s** at `64` (`af06a50582b4`) and **408.82s** at `128` (`751159cacbde`). Pinning **`codegen-units = 256`** explicitly in `[profile.dev]` and `[profile.test]` preserved full LLVM parallelism.
- **`debug = "line-tables-only"` + `split-debuginfo = "unpacked"`:** Cut disk write volume (`fs_out`) by **~36%** (from 8.83M blocks down to 5.67M blocks on heavy UI test builds) while retaining complete file/line backtraces on panic.
- **`[profile.test] opt-level = 0`:** Eliminated unnecessary test-harness optimization time without slowing unit-test execution.

<p align="center">
  <img src="../assets/chart-baseline-vs-final.svg" alt="Baseline vs Final Profile Chart" width="100%"/>
</p>

---

<p align="center">
  <a href="02-storage-and-sccache-benchmarks.md">← Issue 02</a> ·
  <a href="../README.md">Cover</a> ·
  <a href="04-privacy-preserving-cargo-telemetry.md">Next: Issue 04 — Privacy-Preserving Telemetry →</a>
</p>
