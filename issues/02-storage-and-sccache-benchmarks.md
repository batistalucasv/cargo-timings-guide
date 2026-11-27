# Issue 02 — Storage & `sccache`: SSD vs. HDD vs. `/dev/shm`

## Measured Storage Tiers

Before moving caches around, we benchmarked sequential read/write throughput on every storage tier available on the workstation:

| Role | Mount Tier | Write (MB/s) | Direct Read (MB/s) |
|---|---|---:|---:|
| `target_dir_ssd` | Local SATA SSD | **421.0** | **433.0** |
| `workspace_repos` | Spinning HDD #1 | 91.0 | 113.0 |
| `sccache_and_registry` | Spinning HDD #2 | 87.0 | 93.0 |

Originally, `SCCACHE_DIR` (`25G`) was placed on the secondary HDD (`87/93 MB/s`) to "save SSD wear". Our telemetry proved that was a major bottleneck.

## Controlled Benchmark: Where Should `sccache` and `target-dir` Live?

We ran identical focused `clippy` + `nextest` loops on `app-ui` across four storage setups (with `mold` and `[profile.test] opt-level = 0`):

| `env_hash` | Setup | `clippy` | `nextest` (1st / 2nd) | Notes |
|---|---|---:|---:|---|
| `1439ba1ce595` | `target-dir` SSD, `sccache` **HDD** (`25G`) | 9.68s | 73.10s / 12.64s | HDD latency slows hot cache checks |
| `b7c064c86a33` | `target-dir` SSD, **`sccache` disabled** | 12.95s | 11.45s / 17.84s | Slower `clippy` & warm loop |
| `29de672b6fc0` | `target-dir` SSD, **`sccache` SSD** (`15G`) | 9.53s | **9.08s / 7.83s** | **Fastest warm loop (7.83s)** |
| `f4aeb7cc66aa` | `CARGO_TARGET_DIR=/dev/shm` (**RAM**), `sccache` HDD | — | 375.36s (cold) / 8.01s | Virtually tied with SSD (8.01s vs 7.83s), but consumes RAM |

## Key Findings

1. **Put `sccache` on SSD (with a reasonable cap like `15G`), not HDD:** Moving `sccache` from an 87 MB/s HDD to a 421 MB/s SSD cut the warm `nextest` loop from **12.64s → 7.83s** (-38%).
2. **Skip `/dev/shm` on 30 GiB machines:** Using a RAM-backed `target-dir` did not beat a good SATA SSD in warm runs (`8.01s` vs `7.83s`), while eating up to 16 GiB of physical RAM that is much better spent keeping `rustc` and `mold` out of OOM territory.
3. **Keep `~/.cargo/registry` and `~/.cargo/git` on HDD if needed:** Those are mostly read-once / unpacked into `target-dir`, so keeping them on HDD saves SSD space without hurting incremental iteration.
