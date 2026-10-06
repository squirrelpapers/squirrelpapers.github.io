"""S4 - Merge content/*.yaml with the harvest cache into data/derived/entries.json.

YAML wins over Zenodo; Zenodo fills gaps. Every later step reads
entries.json and nothing else from content/ or data/raw/zenodo/.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import volume_yamls, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    if not volume_yamls():
        skipped("no content/vol*.yaml yet (S2)")
        return
    pending("S4")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
