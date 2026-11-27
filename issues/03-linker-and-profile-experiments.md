# Issue 03 — Linker Wars & Profile Tuning (`mold`, `wild`, Incremental, `line-tables-only`)

Across 14 `env_hash` configurations, we tested the classic Rust compile-time levers one by one and measured them on real workloads.

## 1. Linker Showdown: `mold` vs. `wild`

We benchmarked `mold 3.0.0` against `wild` (`-B<wild-bin>`) on the exact same `app-ui` target (`codegen-units = 256`, `opt-level = 0`, `line-tables-only`):

| `env_hash` | Linker | `clippy --all-targets` | `nextest` (cold) | `nextest` (warm) |
|---|---|---:|---:|---:|
| `29de672b6fc0` | **`mold 3.0.0`** (+ SSD `sccache`) | **9.53s (pass)** | — | **7.83s** |
| `c431e074d48a` | **`wild`** | **2.46s (FAILED)** | 401.90s | 9.98s |

`wild` failed during `clippy --all-targets` and was slower than `mold` in the warm test loop (`9.98s` vs `7.83s`). **`mold` remains the clear winner for daily reliability and speed.**

## 2. The `CARGO_INCREMENTAL = "0"` Trap

Many CI/sccache guides recommend setting `CARGO_INCREMENTAL = "0"` globally so `rustc` emits cacheable artifacts for `sccache` across branches/worktrees. We tested both:

- **`41a80f22062d` (`CARGO_INCREMENTAL = "0"` global, `n=133`):** `sccache` hit rate was only **1.6%** (`35 hits / 2,193 misses`), and `nextest` averaged **61.91s** (median **44.23s**). Why? Because every small edit to an internal crate invalidated incremental state and forced full crate recompilation.
- **`bbd0a3bbe7c0` & `9edf022122b2` (Incremental enabled + `sccache` on SSD):** `nextest` mean dropped to **32.62s** (median **15.85s**), and `sccache` hit rate rose to **39.6%** overall (and **63.8%** once stabilized on the final day).

**Lesson:** Use `CARGO_INCREMENTAL = "0"` in **CI**, not as a global setting for **local edit-compile-test loops**.

## 3. `codegen-units` (`64` vs `128` vs `256`)

When `CARGO_INCREMENTAL = "0"` is set, `rustc` silently drops `codegen-units` from `256` down to `16`, hurting LLVM parallelism on large crates. Explicitly pinning `codegen-units = 256` in `[profile.dev]` and `[profile.test]` alongside `split-debuginfo = "unpacked"` and `debug = "line-tables-only"` kept cold builds faster than `64` (`349.29s`) and `128` (`408.82s`) while preserving full panic backtraces.

## 4. The Winning Profile (`9edf022122b2`)

```toml
[profile.dev]
debug = "line-tables-only"
codegen-units = 256
split-debuginfo = "unpacked"

[profile.test]
opt-level = 0
debug = "line-tables-only"
codegen-units = 256
split-debuginfo = "unpacked"
```

- **`clippy` mean:** `63.42s` (baseline) → **`15.65s`** (**-75.3%**)
- **`nextest` mean:** `52.76s` (baseline) → **`32.62s`** (**-38.2%**)
- **Overall p90:** `117.72s` (baseline) → **`58.43s`** (**-50.4%**)
