"""S9 - Facet filter index and the browser SPARQL page (rdflib under Pyodide).

Pattern copied from fdo-squirrel-registry: queries.yaml -> docs/sparql.html,
and every example query must return at least one row at build time.

Stub from S1: checks its precondition and says why it did nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import DOCS, skipped, pending  # noqa: E402


def main(strict: bool = False) -> None:
    if not (DOCS / "index.html").exists():
        skipped("docs/index.html missing (S5)")
        return
    pending("S9")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
