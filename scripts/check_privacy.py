#!/usr/bin/env python3
"""Privacy gate: fails if hardcoded local paths, PR worktree tags, or denylist terms appear."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GENERIC_PATTERNS = [
    (r"/home/[a-zA-Z0-9._-]+", "hardcoded home directory"),
    (r"/mnt/[a-zA-Z0-9._ /-]+", "hardcoded mount path"),
    (r"C:\\Users\\[a-zA-Z0-9._-]+", "hardcoded Windows user path"),
    (r"\bpr-\d{3,5}\b", "PR worktree identifier"),
]


def load_denylist(path: Path | None) -> list[tuple[str, str]]:
    if not path or not path.exists():
        return []
    patterns = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        term = raw.strip()
        if not term or term.startswith("#"):
            continue
        patterns.append((rf"\b{re.escape(term)}\b", "private denylist match"))
    return patterns


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan public repo for accidental private leaks.")
    default_deny = os.environ.get("CARGO_TIMINGS_DENYLIST")
    if not default_deny:
        sibling = ROOT.parent / "cargo-timings" / "scripts" / "privacy_denylist.txt"
        default_deny = str(sibling) if sibling.exists() else ""
    parser.add_argument("--denylist", type=Path, default=Path(default_deny) if default_deny else None)
    args = parser.parse_args()

    patterns = GENERIC_PATTERNS + load_denylist(args.denylist)
    violations: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, reason in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(f"{rel}:{lineno}: [{reason}] {line.strip()[:120]}")

    if violations:
        print("PRIVACY CHECK FAILED! Found potentially private data:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print("Privacy check passed: 0 leaks detected across public repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
