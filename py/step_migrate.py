"""S2 - Migrate the old Markdown volumes and florianthiery/pub into content/*.yaml.

One-off and NOT in the default run: it writes content/, which is edited by
hand afterwards. Reads the snapshots under data/raw/volumes-md/ and
data/raw/pub/, writes content/vol<N>.yaml, content/places.yaml and
dist/reports/migration.md.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import RAW_VOLUMES_MD, rel, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    if not RAW_VOLUMES_MD.exists():
        skipped(f"{rel(RAW_VOLUMES_MD)} missing - the source snapshot is taken in S2")
        return
    pending("S2")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
