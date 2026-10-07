"""One-off: build assets/vendor/naturalearth/countries.js from Natural Earth.

The map page (S10) draws its own background from this file, so it shows the
conference places without asking anyone else's server. OpenStreetMap tiles are
added only when the reader asks for them.

    pip install shapely
    python py/tools/make_basemap.py path/to/ne_50m_admin_0_countries.geojson

Input: ne_50m_admin_0_countries.geojson from
https://github.com/nvkelso/natural-earth-vector (public domain). Geometries are
simplified (0.02 degrees, topology preserved), rounded to 0.01 degrees and
stripped of every attribute: about 0.8 MB instead of 3 MB. Not part of the
pipeline; run again only to change the background.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOLERANCE = 0.02
TARGET = Path(__file__).resolve().parents[2] / "assets" / "vendor" / "naturalearth" / "countries.js"


def rounded(coords):
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], 2), round(coords[1], 2)]
    return [rounded(c) for c in coords]


def main(source: str) -> None:
    from shapely.geometry import mapping, shape

    data = json.loads(Path(source).read_text(encoding="utf-8"))
    features = []
    for feature in data["features"]:
        geometry = shape(feature["geometry"]).simplify(TOLERANCE, preserve_topology=True)
        if geometry.is_empty:
            continue
        m = mapping(geometry)
        features.append({"type": "Feature", "properties": {},
                         "geometry": {"type": m["type"], "coordinates": rounded(m["coordinates"])}})
    text = json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":"))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("/* Natural Earth 1:50m admin-0 countries, public domain, simplified for the\n"
                      " * Squirrel Papers map by py/tools/make_basemap.py */\n"
                      "window.SQP_COUNTRIES = " + text + ";\n", encoding="utf-8", newline="\n")
    print(f"{len(features)} countries, {TARGET.stat().st_size // 1024} KB -> {TARGET}")


if __name__ == "__main__":
    main(sys.argv[1])
