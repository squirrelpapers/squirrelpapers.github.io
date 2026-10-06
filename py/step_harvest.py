"""S3 - Fetch Zenodo records and Wikidata places into data/raw/.

The only step that reaches the network (PRIMER A3), so it runs on the
maintainer's machine or in the Action, never in a default build. Caches one
JSON per Zenodo record under data/raw/zenodo/ and one per QID under
data/raw/wikidata/.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import volume_yamls, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    if not volume_yamls():
        skipped("no content/vol*.yaml yet - nothing to harvest (S2 first)")
        return
    pending("S3")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
