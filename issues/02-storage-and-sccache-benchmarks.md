<p align="center">
  <a href="../README.md">← Cover</a> ·
  <a href="01-context-and-multi-agent-oom.md">Issue 01</a> ·
  <strong>Issue 02</strong> ·
  <a href="03-linker-and-profile-experiments.md">Issue 03</a> ·
  <a href="04-24h-statistical-savings-model.md">Issue 04</a> ·
  <a href="05-privacy-preserving-cargo-telemetry.md">Issue 05 →</a>
</p>

# Issue 02 · Storage & `sccache`: SSD vs. HDD vs. `/dev/shm`

> *Why placing `sccache` on a spinning HDD sabotaged our hot test loop—and why putting `target-dir` in RAM (`/dev/shm`) wasn't worth a single megabyte.*

---

## 1 · Measure Your Disks Before Moving Caches

Every Rust build is an intense storm of small-file reads and writes (`.rmeta`, `.rlib`, `.dwo`, incremental dep-graphs, and `sccache` blobs). Before changing any config, we benchmarked every storage tier on the workstation:

| Storage Role | Disk Tier | Sequential Write | Direct Read | Relative Throughput |
|---|---|---:|---:|---:|
| `target_dir_ssd` | Local SATA SSD | **421.0 MB/s** | **433.0 MB/s** | **4.7x faster** |
| `workspace_repos` | Spinning HDD #1 | 91.0 MB/s | 113.0 MB/s | 1.2x |
| `sccache_and_registry` | Spinning HDD #2 | 87.0 MB/s | 93.0 MB/s | 1.0x (baseline) |

Originally, our setup placed `target-dir` on the SSD (`421/433 MB/s`) but left `SCCACHE_DIR` (`25G`) on Spinning HDD #2 (`87/93 MB/s`) out of caution for SSD free space and write endurance.

**The hidden cost:** Every single `rustc` invocation wrapped by `sccache` computes hashes and checks or reads/writes compressed cache objects. On a spinning HDD, random seek latency averaged **`~0.231s` per cache hit**—turning a supposed accelerator into a brake on hot incremental iterations!

---

## 2 · Controlled Storage Matrix (`app-ui`)

<p align="center">
  <img src="../assets/chart-storage-bench.svg" alt="Storage Throughput and Controlled Warm Test Loop" width="100%"/>
</p>

Holding `jobs = 14`, `mold 3.0.0`, `debug = "line-tables-only"`, `codegen-units = 256`, `split-debuginfo = "unpacked"`, and `[profile.test] opt-level = 0` strictly constant, we benchmarked four storage configurations on the exact same `app-ui` `clippy --all-targets` + `nextest --lib` sequence:

| `env_hash` | Benchmark | `target-dir` | `sccache` Location | `clippy` | `nextest` (1st / 2nd) | Peak RAM (warm) | Verdict |
|---|---|---|---|---:|---:|---:|---|
| `1439ba1ce595` | **B0** | SSD | **HDD (`25G`)** | 9.68s | 73.10s / 12.64s | 2,014 MiB | HDD I/O slows hot loop |
| `b7c064c86a33` | **B1** | SSD | **Disabled** | 12.95s | 11.45s / 17.84s | 1,948 MiB | Slower `clippy` & warm loop |
| **`29de672b6fc0`** | **B2** | **SSD** | **SSD (`15G`)** | **9.53s** | **9.08s / 7.83s** | **1,949 MiB** | **Winner (`7.83s` warm)** |
| `f4aeb7cc66aa` | **B6** | **`/dev/shm` (RAM)** | HDD (`25G`) | — | 375.36s (cold) / 8.01s | 1,926 MiB (+tmpfs) | Ties SSD, wastes up to 16 GiB RAM |

---

## 3 · Three Non-Obvious Findings

### Finding A: `sccache` on SSD beat *both* HDD and "No `sccache`"
- Compared to `sccache` on HDD (`12.64s`), moving `SCCACHE_DIR` to the SSD cut the warm `nextest` loop to **`7.83s`** (**-38.1%**).
- Compared to disabling `sccache` completely (`12.95s` clippy, `11.45s–17.84s` warm `nextest`), SSD `sccache` was **faster on both `clippy` and `nextest`** while also preserving cross-worktree reuse.

### Finding B: `/dev/shm` (RAM Disk) Is a Trap on 30 GiB Machines
It is tempting to put `CARGO_TARGET_DIR=/dev/shm/cargo-target` in RAM. Our benchmark proved why that's a bad trade-off on a 30 GiB swapless system:
- Warm `nextest` on `/dev/shm` ran in **`8.01s`**—actually **0.18s slower** than our plain SATA SSD (`7.83s`) because the Linux page cache already keeps hot SSD target files in RAM automatically!
- Worse, a shared Rust `target-dir` easily grows to **12–16 GiB**, permanently stealing half your physical RAM from `rustc` and `mold` and bringing back OOM crashes.

### Finding C: Split Cold Read-Only Storage from Hot Build Storage
You do *not* need to put everything on your SSD to get 100% of the speed:

| Directory | Access Pattern | Recommended Disk |
|---|---|---|
| `target-dir` (`~/.cache/cargo-target`) | Heavy random read/write every build | **SSD (mandatory)** |
| `SCCACHE_DIR` (`~/.cache/sccache`, `15G`) | Latency-sensitive hash lookups & reads | **SSD (mandatory)** |
| `~/.cargo/registry` & `~/.cargo/git` | Read-once crate archives / git checkouts | **HDD (symlink OK)** |
| Git worktree source trees | Small text reads (OS page-cached quickly) | **HDD or SSD** |

> [!TIP]
> **Cache Stability Multiplier:** On Day 1—while switching between 14 different `env_hash` profiles—our aggregate `sccache` hit rate was only **18.0%** (`1,736` hits / `7,901` misses). On Day 2, running 100% on the stabilized SSD profile `9edf022122b2`, the `sccache` hit rate jumped to **63.8%** (`727` hits / `412` misses), cutting overall daily mean build time from `30.24s` to **`17.43s`**.

---

<p align="center">
  <a href="01-context-and-multi-agent-oom.md">← Issue 01</a> ·
  <a href="../README.md">Cover</a> ·
  <a href="03-linker-and-profile-experiments.md">Next: Issue 03 — Linker Wars &amp; Profiles →</a>
</p>
