# Issue 04 — Publishing Real Cargo Telemetry Without Leaking Private Data

Real engineering benchmarks are only credible when backed by real numbers—but raw Cargo telemetry contains sensitive information:
- Repository, branch, and worktree names (internal codenames, PR worktree tags)
- Test function names and CLI arguments
- Local usernames, hostnames, and filesystem mount paths (home directories and storage mounts)
- `--timings` HTML reports with full crate graphs

## Our Two-Repository + Two-Layer Sanitization Architecture

1. **Private Telemetry Repository (Local / Private GitHub):**
   - Stores raw `runs.jsonl`, `--timings` HTML reports, per-unit JSONs, and exact hardware/path snapshots.
   - Never made public (because Git history itself contains raw commit messages and paths).

2. **Public Journal Repository (`cargo-timings-guide`):**
   - Receives **only** anonymized, aggregated outputs via an exporter script (`export_public.py`):
     - Strips `repo`, `branch`, `cwd`, `hostname`, `args`, and test filter strings.
     - Maps internal crate names to generic architectural roles (`app-ui`, `app-engine`, `app-layout`, `app-render`, `app-pdf`, `app-cli`).
     - Preserves **100% authentic Cargo metrics**: `env_hash`, `subcommand`, `scope`, normalized flags (`--lib`, `--release`, `--all-targets`), `wall_ms`, `cpu_pct`, `max_rss_kb`, `queue_wait_ms`, `sccache_hits`, and `sccache_misses`.

3. **Automated Privacy Gate (`scripts/check_privacy.py`):**
   - Before any commit or push to the public repository, `python3 scripts/check_privacy.py` scans every tracked file against a strict denylist of usernames, hostnames, mount paths, internal project names, and PR/worktree patterns.
   - If a single match is found, it fails with exit code `1` and pinpoints the exact file and line.
