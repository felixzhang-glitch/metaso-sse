from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


PRUNE_DIRS = {
    "__pycache__",
    "tests",
    "test",
    "testing",
    "docs",
    "doc",
    "examples",
    "example",
}

PRUNE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so.old",
}

PRUNE_GLOBS = {
    "*.dist-info",
    "*.egg-info",
    "*.egg",
    "*.whl",
    "*.md",
    "*.rst",
    "LICENSE*",
    "COPYING*",
    "NOTICE*",
}


def prune(target: Path) -> None:
    if not target.exists() or not target.is_dir():
        print(f"Target not found or not a directory: {target}", file=sys.stderr)
        sys.exit(1)

    # Remove common cache and test/docs dirs
    for root, dirs, files in os.walk(target, topdown=True):
        # mutate dirs in-place to avoid descending into pruned dirs
        pruned = []
        for d in list(dirs):
            if d in PRUNE_DIRS:
                p = Path(root) / d
                shutil.rmtree(p, ignore_errors=True)
                dirs.remove(d)
                pruned.append(str(p))
        # Remove compiled/temp files
        for f in list(files):
            if any(f.endswith(suf) for suf in PRUNE_SUFFIXES):
                p = Path(root) / f
                try:
                    p.unlink()
                except OSError:
                    pass

    # Remove metadata and extra files by glob
    for pattern in PRUNE_GLOBS:
        for p in target.rglob(pattern):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                try:
                    p.unlink()
                except OSError:
                    pass


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/prune_package.py <target_dir>", file=sys.stderr)
        sys.exit(2)
    prune(Path(sys.argv[1]).resolve())


if __name__ == "__main__":
    main()

