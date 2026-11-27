# Issue 01 — Context, Workload Taxonomy & The Multi-Agent OOM Problem

## The Environment

When multiple AI coding agents and human developers share a single **30.26 GiB RAM (0 GiB swap)** Linux workstation across parallel `git worktree` checkouts, the #1 failure mode is not slow compilation—it is **simultaneous Cargo contention**:

1. Two `cargo nextest` or `rustc` invocations running concurrently can easily spike past 10–15 GiB RSS each, hitting the kernel OOM killer on a swapless machine.
2. Leaving all 16 hardware threads (`jobs = 16`) saturated starves the OS, IDE, language servers (`rust-analyzer`), and agent processes.
3. Running unfiltered `cargo nextest run -p app-ui` compiles every integration test binary and example (`ui_shot`, `perf_probe`, etc.), adding **~100+ seconds** to what should be a 10–15s unit-test check.

## Solution 1: Single-File Queue Serialization (`flock`) + `jobs = 14`

Instead of throttling `jobs` down to `4` or `6` per agent, we keep **`jobs = 14`** (leaving 2 of 16 threads for the OS and agents) and enforce a **single global queue** via `flock /tmp/cargo-agent.lock` inside a unified wrapper (`cargo-timed`).

- **Only 1 Cargo process executes at a time** on the machine.
- That single process gets **14 threads** and **~30 GiB of uncontended RAM**.
- Peak RSS in focused runs stays around **1.2–3.8 GiB** (and **5.8 GiB** even during `--release` profiling builds), with zero OOM kills across 1,091 runs.

## Solution 2: Surgical Target Filtering (`--lib`)

In a multi-target crate (like our `app-ui` crate with >840 unit tests plus integration/screenshot/benchmark binaries), omitting `--lib` forces Cargo to compile and link multiple extra binaries even when filtering to a single test name.

**Rule enforced across all workflows:**
```bash
# Always pass --lib unless explicitly targeting --test <name> or --example <name>
cargo nextest run -p app-ui --lib <module::tests::test_name>
```

## Solution 3: Decoupled Local vs. CI Validation

Rather than running `--workspace` or full `xtask ci` suites locally on every edit:
- **Local pre-PR loop (~15–30s):** `cargo fmt --all -- --check` → `cargo clippy -p <crate> --all-targets -- -D warnings` → focused `nextest --lib <test>` → lightweight architecture checks (`xtask layers`).
- **GitHub Actions CI:** owns the full multi-platform regression suite (Linux, macOS, Windows).
