"""S9 - Search index and example queries, checked against the published graph.

Two ways into the journal, built from two sources so each can check the other:

    search index   data/derived/entries.json (S4)  -> web/search/index.json, index.js
    queries        content/queries.yaml             -> web/sparql/queries/<id>.rq
                   + the graphs from S7                data/derived/queries.json

The site step (S5) renders the search page and the SPARQL page from these; this
step writes no HTML, so docs/ keeps a single owner.

Pattern copied from FDOx-squirrel/fdo-squirrel-registry (step_sparql.py):

- Every query runs here against the same files the page loads, and **a query
  that returns no rows fails the build**. SPARQL does not fail on a mistyped
  IRI; it returns nothing, so an empty result is the usual sign of a broken
  graph rather than of a dull question.
- A query may declare a `crosscheck` against a facet of the search index. The
  index comes from entries.json, the query from the graph; if they count
  differently, one of the two routes is wrong and the build stops.

The browser runs the queries with rdflib under Pyodide, both served from this
site (assets/vendor/pyodide/, PRIMER A4) - no endpoint, no CDN, nothing the
reader types leaves their machine.
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    ASSETS, CONTENT, DERIVED, ENTRIES_JSON, ROOT, cached_run, prune, read_json, read_yaml,
    rel, skipped, store_run, tracking, warn, write_json, write_text,
)

QUERIES_YAML = CONTENT / "queries.yaml"
WEB = DERIVED / "web"
QUERIES_JSON = DERIVED / "queries.json"      # read by the site step
PYODIDE_DIR = ASSETS / "vendor" / "pyodide"
PYODIDE_VERSION = "314.0.7"                  # see assets/vendor/SOURCE.yaml

# Entries per facet value shown before "show all" on the search page is the
# page's business; the index itself is complete.
FACETS = ("type", "year", "volume", "event", "person", "language")
LANGUAGE_LABELS = {"en": {"en": "English", "de": "Englisch"},
                   "de": {"en": "German", "de": "Deutsch"}}


# ---------------------------------------------------------------------------
# Search index
# ---------------------------------------------------------------------------


def person_name(p: dict) -> str:
    return f"{p.get('given', '')} {p.get('family', '')}".strip() or p.get("name", "")


def build_index(data: dict) -> dict:
    """One record per published entry, plus the labels of every facet value.

    Facet values are keys (type slug, person IRI, ...) so a label can change
    without breaking a shared link to the search page (#type=poster)."""
    types = {t["slug"]: t["label"] for t in data["types"]}
    labels: dict[str, dict] = {facet: {} for facet in FACETS}
    records = []
    for e in data["entries"]:
        if e.get("draft"):
            continue
        people = [p for role in ("creators", "contributors", "editors") for p in e.get(role, [])]
        year = str(e.get("date") or e.get("year") or "")[:4]
        event = (e.get("event") or {}).get("name")
        facets = {
            "type": sorted(set(e.get("types", []))),
            "year": [year] if year else [],
            "volume": [str(e["volume"])],
            "event": [event] if event else [],
            "person": sorted({p["iri"] for p in people if p.get("iri")}),
            "language": [e["language"]] if e.get("language") else [],
        }
        for slug in facets["type"]:
            labels["type"][slug] = types[slug]
        for p in people:
            if p.get("iri"):
                labels["person"][p["iri"]] = person_name(p)
        if event:
            labels["event"][event] = event
        for value in facets["language"]:
            labels["language"][value] = LANGUAGE_LABELS.get(value, {"en": value, "de": value})
        text = " ".join(filter(None, [
            e["citation_label"], e["title"], e.get("title_zenodo"), event,
            " ".join(person_name(p) for p in people), e.get("doi"),
            " ".join(e.get("keywords") or []), e.get("abstract")]))
        records.append({
            "path": e["path"], "label": e["citation_label"], "title": e["title"],
            "sort": [e["volume"], e["issue"], e["n"]],
            "authors": [person_name(p) for p in e.get("creators", [])],
            "date": e.get("date") or str(e.get("year") or ""),
            "facets": facets, "text": " ".join(text.split()),
        })
    records.sort(key=lambda r: r["sort"])
    for value in sorted({r["facets"]["volume"][0] for r in records}, key=int):
        labels["volume"][value] = {"en": f"Volume {value}", "de": f"Band {value}"}
    for value in sorted({y for r in records for y in r["facets"]["year"]}):
        labels["year"][value] = value
    return {"facets": list(FACETS), "labels": labels, "entries": records}


def facet_counts(index: dict, facet: str) -> dict[str, int]:
    counted: dict[str, int] = {}
    for record in index["entries"]:
        for value in record["facets"][facet]:
            counted[value] = counted.get(value, 0) + 1
    return counted


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def load_config() -> dict:
    config = read_yaml(QUERIES_YAML) or {}
    for key in ("graphs", "prefixes", "queries"):
        if key not in config:
            raise SystemExit(f"{rel(QUERIES_YAML)} has no '{key}' section")
    seen: set[str] = set()
    for query in config["queries"]:
        for key in ("id", "title", "intro", "sparql"):
            if not query.get(key):
                raise SystemExit(f"a query in {rel(QUERIES_YAML)} has no '{key}'")
        for key in ("title", "intro"):
            if set(query[key]) != {"en", "de"}:
                raise SystemExit(f"query {query['id']}: '{key}' needs exactly 'en' and 'de'")
        if query["id"] in seen:
            raise SystemExit(f"duplicate query id: {query['id']}")
        seen.add(query["id"])
    return config


def load_graph(config: dict):
    from rdflib import Graph

    graph = Graph()
    for spec in config["graphs"]:
        graph.parse(ROOT / spec["source"], format="turtle")
    return graph


def run_queries(config: dict, graph) -> tuple[dict[str, list[dict]], list[str]]:
    """Run every query; returns the rows and the lines to print."""
    results: dict[str, list[dict]] = {}
    failures, lines = [], []
    for query in config["queries"]:
        try:
            rows = list(graph.query(config["prefixes"] + "\n" + query["sparql"]))
        except Exception as error:                      # noqa: BLE001
            lines.append(f"  !! {query['id']}: {type(error).__name__}: {error}")
            failures.append(query["id"])
            continue
        columns = [str(v) for v in rows[0].labels] if rows else []
        results[query["id"]] = [{c: (None if row[i] is None else str(row[i]))
                                 for i, c in enumerate(columns)} for row in rows]
        query["rows_at_build"] = len(rows)
        mark = "  " if rows else "!!"
        lines.append(f"  {mark} {query['id']:<16} {len(rows):4d} rows"
                     + ("" if rows else "  - parses, matches nothing"))
        if not rows:
            failures.append(query["id"])
    if failures:
        for line in lines:
            print(line)
        raise RuntimeError("queries returned no rows or did not run: " + ", ".join(failures))
    return results, lines


def crosscheck(config: dict, results: dict, index: dict) -> list[str]:
    """Each declared query must count exactly what the search index counts."""
    lines = []
    for query in config["queries"]:
        spec = query.get("crosscheck")
        if not spec:
            continue
        rows = results[query["id"]]
        if spec.get("entries"):
            expected = len(index["entries"])
            if len(rows) != expected:
                raise RuntimeError(f"{query['id']}: {len(rows)} rows, but the search index "
                                   f"has {expected} entries")
            lines.append(f"  ok {query['id']:<16} {expected} entries, as in the search index")
            continue
        counted = facet_counts(index, spec["facet"])
        answered: dict[str, int] = {}
        for row in rows:
            key = row[spec["value"]]
            answered[key] = max(answered.get(key, 0), int(row[spec["count"]]))
        if answered != counted:
            only_q = {k: v for k, v in answered.items() if counted.get(k) != v}
            only_i = {k: v for k, v in counted.items() if answered.get(k) != v}
            raise RuntimeError(f"{query['id']}: the query and the '{spec['facet']}' facet "
                               f"disagree.\n    query: {only_q}\n    index: {only_i}")
        lines.append(f"  ok {query['id']:<16} matches the '{spec['facet']}' facet "
                     f"({len(counted)} values)")
    return lines


def rq_text(config: dict, query: dict) -> str:
    intro = "\n".join(f"# {line}" for line in
                      textwrap.wrap(" ".join(query["intro"]["en"].split()), 76))
    return (f"# {query['title']['en']}\n{intro}\n#\n"
            f"# Squirrel Papers - https://squirrelpapers.github.io/sparql/\n"
            f"# Graphs: {', '.join(spec['url'] for spec in config['graphs'])}\n\n"
            f"{config['prefixes'].rstrip()}\n\n{query['sparql'].rstrip()}\n")


# ---------------------------------------------------------------------------


def inputs(config: dict | None = None) -> list[Path]:
    sources = [ROOT / spec["source"] for spec in (config or {}).get("graphs", [])]
    return [QUERIES_YAML, ENTRIES_JSON, *sources, Path(__file__).resolve()]


def main(strict: bool = False) -> None:
    if not QUERIES_YAML.exists():
        skipped(f"{rel(QUERIES_YAML)} missing")
        return
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    config = load_config()
    missing = [spec["source"] for spec in config["graphs"] if not (ROOT / spec["source"]).exists()]
    if missing:
        skipped(f"graphs missing (S7): {', '.join(missing)}")
        return

    def mine(path: str) -> bool:
        return path.startswith(("sparql/", "search/"))

    record = cached_run("sparql", inputs(config))
    if record:
        prune(WEB, {os.path.abspath(ROOT / p) for p in record["outputs"]}, mine)
        for line in record["summary"]:
            print(line)
        print("queries, graphs and entries unchanged since the last run: checks reused")
        return

    with tracking() as produced:
        summary = build(config, strict)
    prune(WEB, produced, mine)
    for line in summary:
        print(line)
    store_run("sparql", inputs(config), produced, summary=summary)


def build(config: dict, strict: bool) -> list[str]:
    import rdflib

    data = read_json(ENTRIES_JSON)
    index = build_index(data)
    write_json(index, WEB / "search" / "index.json")
    # The page loads the index as a script, so the search works from file://
    # too (a fetch() would not).
    write_text(WEB / "search" / "index.js", "window.SQP_INDEX = "
               + json.dumps(index, sort_keys=True, ensure_ascii=False) + ";\n")

    graph = load_graph(config)
    results, lines = run_queries(config, graph)
    lines += crosscheck(config, results, index)

    for query in config["queries"]:
        write_text(WEB / "sparql" / "queries" / f"{query['id']}.rq", rq_text(config, query))

    wheels = sorted(p.name for p in PYODIDE_DIR.glob("*.whl"))
    browser_rdflib = next((w.split("-")[1] for w in wheels if w.startswith("rdflib-")), None)
    write_json({"graphs": config["graphs"], "prefixes": config["prefixes"],
                "queries": config["queries"], "triples": len(graph),
                "pyodide": PYODIDE_VERSION, "rdflib": browser_rdflib, "wheels": wheels},
               QUERIES_JSON)

    summary = [f"search index: {len(index['entries'])} entries, facets "
               + ", ".join(f"{f} {len(index['labels'][f])}" for f in FACETS)
               + f" -> {rel(WEB)}/search/",
               f"{len(config['queries'])} queries over {len(graph)} triples "
               f"(rdflib {rdflib.__version__}):", *lines,
               f"  .rq files -> {rel(WEB)}/sparql/queries/"]
    if browser_rdflib != rdflib.__version__:
        # Same engine in the build check and in the browser is the point of
        # the pattern; a different version can answer an edge case differently.
        warn(f"the build checks with rdflib {rdflib.__version__}, the page runs "
             f"{browser_rdflib} (assets/vendor/pyodide/); pip install rdflib=={browser_rdflib}",
             False)
    return summary


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
