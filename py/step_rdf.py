"""S7 - Build the DCAT 3 / DCAT-AP 3 graph with the CIDOC CRM bridge into dist/.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import ENTRIES_JSON, rel, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    pending("S7")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
