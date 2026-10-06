"""S8 - SHACL gate over the graph built in S7.

Own shapes plus the DCAT-AP 3 shapes. Under --strict a violation fails the
build.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import DIST, rel, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    graph = DIST / "squirrelpapers.ttl"
    if not graph.exists():
        skipped(f"{rel(graph)} missing (S7)")
        return
    pending("S8")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
