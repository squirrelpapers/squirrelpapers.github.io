"""S10 - Conference places as GeoJSON, read from the published graph.

    dist/squirrelpapers.ttl (S7)  ->  dist/events.geojson            one Point per event
                                      web/downloads/events.geojson   the same, on the site
                                      web/map/events.js              the same, for the map page

The features come from the graph, not from entries.json: event IRIs, the
clustering of talks into events and the place geometries are decided once, in
S7, and the map shows exactly that. Online events have no place in the graph
and are left out on purpose (PRIMER A4).

Acceptance (PRIMER S10): every published entry whose event took place on site
at a place with a Wikidata QID must appear on the map. The step checks that
against entries.json - a second route to the same facts - and fails otherwise.
The site step renders the map page (docs/map/) and its list of events.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    BASE, DERIVED, DIST, ENTRIES_JSON, ROOT, cached_run, prune, read_json, rel, skipped,
    store_run, tracking, warn, write_text,
)

GRAPH = DIST / "squirrelpapers.ttl"
GEOJSON = DIST / "events.geojson"
WEB = DERIVED / "web"

QUERY = """
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <https://schema.org/>
PREFIX sqp: <https://w3id.org/squirrelpapers/ontology#>
SELECT ?event ?name ?start ?end ?place ?placeLabel ?placeNote ?wkt ?same
       ?entry ?label ?title ?issued
WHERE {
  ?entry a bibo:Document ;
         bibo:presentedAt ?event ;
         sqp:citationLabel ?label ;
         dct:title ?title ;
         dct:issued ?issued .
  ?event rdfs:label ?name ;
         schema:location ?place .
  OPTIONAL { ?event schema:startDate ?start }
  OPTIONAL { ?event schema:endDate ?end }
  ?place rdfs:label ?placeLabel ;
         geo:hasGeometry/geo:asWKT ?wkt .
  OPTIONAL { ?place schema:description ?placeNote }
  OPTIONAL { ?place owl:sameAs ?same }
}
"""
POINT = re.compile(r"^POINT\(\s*(-?[0-9.]+)\s+(-?[0-9.]+)\s*\)$")


def text(value) -> str | None:
    return None if value is None else str(value)


def build_features(graph) -> list[dict]:
    """One Feature per event; its entries, sorted in journal order."""
    events: dict[str, dict] = {}
    for row in graph.query(QUERY):
        iri = str(row.event)
        match = POINT.match(str(row.wkt))
        if not match:
            raise ValueError(f"{iri}: geometry is not a WKT point: {row.wkt}")
        feature = events.setdefault(iri, {
            "type": "Feature",
            "id": iri,
            "geometry": {"type": "Point",
                         "coordinates": [float(match.group(1)), float(match.group(2))]},
            "properties": {
                "name": str(row.name), "start": text(row.start), "end": text(row.end),
                "place": {"iri": str(row.place), "label": str(row.placeLabel),
                          "description": text(row.placeNote), "wikidata": None},
                "entries": {},
            },
        })
        if row.same is not None and "wikidata.org/entity/" in str(row.same):
            feature["properties"]["place"]["wikidata"] = str(row.same).rsplit("/", 1)[-1]
        entry = str(row.entry)
        path = entry[len(BASE):]
        feature["properties"]["entries"][entry] = {
            "iri": entry, "path": path, "label": str(row.label), "title": str(row.title),
            "issued": str(row.issued),
            "sort": [int(n) for n in re.findall(r"\d+", path)],
        }
    features = []
    for feature in events.values():
        entries = sorted(feature["properties"]["entries"].values(), key=lambda e: e["sort"])
        for e in entries:
            del e["sort"]
        feature["properties"]["entries"] = entries
        features.append(feature)
    features.sort(key=lambda f: (f["properties"]["start"] or "", f["properties"]["name"]),
                  reverse=True)
    return features


def acceptance(features: list[dict], data: dict) -> tuple[list[str], list[str]]:
    """Entries that should be on the map but are not; and what was left out."""
    on_map = {e["iri"] for f in features for e in f["properties"]["entries"]}
    missing, online = [], 0
    for e in data["entries"]:
        event = e.get("event") or {}
        if e.get("draft") or not event.get("name"):
            continue
        if event.get("online"):
            online += 1
            continue
        place = event.get("place")
        if isinstance(place, dict) and place.get("wikidata") and e["iri"] not in on_map:
            missing.append(f"{e['citation_label']} ({event['name']})")
    no_place = sum(1 for e in data["entries"]
                   if not e.get("draft") and (e.get("event") or {}).get("name")
                   and not (e.get("event") or {}).get("online")
                   and not isinstance((e.get("event") or {}).get("place"), dict))
    notes = [f"left out: {online} entries at online events (on purpose)"]
    if no_place:
        notes.append(f"left out: {no_place} entries at events without a known place")
    return missing, notes


def main(strict: bool = False) -> None:
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    if not GRAPH.exists():
        skipped(f"{rel(GRAPH)} missing (S7)")
        return
    inputs = [GRAPH, ENTRIES_JSON, Path(__file__).resolve()]

    def mine(path: str) -> bool:
        return path.startswith("map/") or path == "downloads/events.geojson"

    record = cached_run("map", inputs)
    if record:
        prune(WEB, {os.path.abspath(ROOT / p) for p in record["outputs"]}, mine)
        for line in record["summary"]:
            print(line)
        print("graph and entries unchanged since the last run: map data kept")
        return
    with tracking() as produced:
        summary = build(strict)
    prune(WEB, produced, mine)
    for line in summary:
        print(line)
    store_run("map", inputs, produced, summary=summary)


def build(strict: bool) -> list[str]:
    from rdflib import Graph

    graph = Graph()
    graph.parse(GRAPH, format="turtle")
    features = build_features(graph)
    missing, notes = acceptance(features, read_json(ENTRIES_JSON))
    if missing:
        raise RuntimeError(f"{len(missing)} entries at an on-site event with a Wikidata "
                           f"place are not on the map: {', '.join(missing[:10])}")

    collection = {"type": "FeatureCollection",
                  "name": "Squirrel Papers - conference places",
                  "features": features}
    body = json.dumps(collection, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    write_text(GEOJSON, body)
    write_text(WEB / "downloads" / "events.geojson", body)
    # As a script, so the map page works from file:// too (no fetch).
    write_text(WEB / "map" / "events.js", "window.SQP_EVENTS = "
               + json.dumps(collection, sort_keys=True, ensure_ascii=False) + ";\n")

    places = {f["properties"]["place"]["iri"] for f in features}
    entries = sum(len(f["properties"]["entries"]) for f in features)
    without_qid = sorted({f["properties"]["place"]["label"] for f in features
                          if not f["properties"]["place"]["wikidata"]})
    if without_qid:
        warn(f"places on the map without a Wikidata QID: {', '.join(without_qid)}", strict)
    return [f"{len(features)} events at {len(places)} places with {entries} entries "
            f"-> {rel(GEOJSON)}, {rel(WEB)}/map/",
            "acceptance: every entry at an on-site event with a Wikidata place is on the map",
            *notes]


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
