"""S10 - Event places as dist/events.geojson for the Leaflet map.

Online events are left out on purpose (PRIMER A4).

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
    pending("S10")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
