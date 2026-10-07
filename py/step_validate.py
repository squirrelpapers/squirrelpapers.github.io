"""S8 - SHACL gate over the graphs built in S7.

Three checks, each on its own graph:

    DCAT-AP 3.0.1   dist/squirrelpapers.ttl   + types + axioms   data/raw/shapes/dcat-ap-3.0.1/
    journal rules   dist/squirrelpapers.ttl   + types + axioms   shapes/sqp-shapes.ttl
    CRM rules       dist/squirrelpapers-crm.ttl                  shapes/crm-shapes.ttl

and a self-test first: a deliberately broken entry (shapes/selftest.ttl) must
be reported by every rule it lists, otherwise the gate itself is broken.

Violations fail the step under --strict and are reported as a warning
otherwise; warnings and infos never fail. Report: dist/reports/validation.md.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    DERIVED, DIST, PREFIXES, RAW, REPORTS, ROOT, cached_run, prune, rel, skipped,
    store_run, tracking, warn, write_text,
)

GRAPH = DIST / "squirrelpapers.ttl"
CRM_GRAPH = DIST / "squirrelpapers-crm.ttl"
TYPES = DIST / "vocab" / "types.ttl"
SHAPES = ROOT / "shapes"
DCAT_AP = RAW / "shapes" / "dcat-ap-3.0.1"
REPORT = REPORTS / "validation.md"
WEB_SHAPES = DERIVED / "web" / "shapes"     # published copies (docs/shapes/)
SH = "http://www.w3.org/ns/shacl#"


def load(*paths):
    from rdflib import Graph

    g = Graph()
    for path in paths:
        g.parse(path, format="turtle")
    return g


def dcat_ap_shapes():
    """Both DCAT-AP files as one graph, minus references to property shapes
    that 3.0.1 never defines (5 of them; pyshacl refuses to load the files
    otherwise). Returns the graph and the dropped references."""
    from rdflib import URIRef

    g = load(DCAT_AP / "dcat-ap-SHACL.ttl", DCAT_AP / "ranges.ttl")
    prop, path = URIRef(SH + "property"), URIRef(SH + "path")
    dangling = sorted({(s, o) for s, _, o in g.triples((None, prop, None)) if (o, path, None) not in g})
    for s, o in dangling:
        g.remove((s, prop, o))
    return g, dangling


def run(data, shapes):
    from pyshacl import validate

    conforms, report, _ = validate(data, shacl_graph=shapes, inference="none",
                                   allow_warnings=True)
    rows = report.query("""
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT ?focus ?path ?severity ?message ?value WHERE {
            ?r a sh:ValidationResult ; sh:focusNode ?focus ; sh:resultSeverity ?severity .
            OPTIONAL { ?r sh:resultPath ?path }
            OPTIONAL { ?r sh:resultMessage ?message }
            OPTIONAL { ?r sh:value ?value }
        }""")
    results = sorted({(str(r.focus), str(r.path or ""), str(r.severity).split("#")[-1],
                       str(r.message or ""), str(r.value or "")) for r in rows})
    return results


def short(iri: str) -> str:
    for prefix, ns in sorted(PREFIXES.items(), key=lambda kv: -len(kv[1])):
        if iri.startswith(ns):
            return f"{prefix}:{iri[len(ns):]}"
    return iri


def selftest(sqp_shapes, ap_shapes) -> list[str]:
    """Broken entry in, expected findings out. Returns the rules that stayed silent."""
    from rdflib import URIRef

    # Small graph: the broken entry, the vocabularies, and the issue and volume
    # it points to - enough for every rule, a fraction of the time.
    data = load(TYPES, SHAPES / "axioms.ttl", SHAPES / "selftest.ttl")
    full = load(GRAPH)
    for context in ("https://w3id.org/squirrelpapers/v7/i4", "https://w3id.org/squirrelpapers/v7"):
        for triple in full.triples((URIRef(context), None, None)):
            data.add(triple)
    focus = "https://w3id.org/squirrelpapers/v7/i4/e99"
    expects = {str(o) for o in load(SHAPES / "selftest.ttl").objects(
        URIRef("https://w3id.org/squirrelpapers/shapes#selftest"),
        URIRef("https://w3id.org/squirrelpapers/shapes#expects"))}
    all_sqp = run(data, sqp_shapes)
    sqp_results = [r for r in all_sqp if r[0] == focus]
    ap_results = [r for r in run(data, ap_shapes) if r[0] == focus]
    found = {r[1] for r in sqp_results + ap_results}
    silent = sorted(short(p) for p in expects - found)
    sparql_hits = [r for r in all_sqp if not r[1] and r[4] == focus]   # journal-level rules
    if len(sparql_hits) < 3:
        silent.append("SPARQL constraints (citation label, title language, IRI) - expected 3 findings, "
                      f"got {len(sparql_hits)}")
    return silent


def inputs() -> list[Path]:
    """Graphs, shapes and code: what a validation result depends on."""
    return [GRAPH, CRM_GRAPH, TYPES, *sorted(SHAPES.glob("*.ttl")),
            *sorted(DCAT_AP.glob("*.ttl")), Path(__file__).resolve()]


def main(strict: bool = False) -> None:
    if not GRAPH.exists():
        skipped(f"{rel(GRAPH)} missing (S7)")
        return
    # pyshacl over 12 000 triples is the slowest part of a run (S8b: 33 s on
    # Windows). Same graphs, same shapes, same code: same result.
    record = cached_run("validate", inputs())
    if record:
        for line in record["summary"]:
            print(line)
        print("graphs and shapes unchanged since the last run: result reused "
              "(python main.py --fresh re-validates)")
        prune(WEB_SHAPES, {os.path.abspath(ROOT / path) for path in record["outputs"]})
        if record["violations"]:
            warn(f"{record['violations']} SHACL violations, see {rel(REPORT)}", strict)
        return
    with tracking() as produced:
        summary, violations = check()
    prune(WEB_SHAPES, produced)
    for line in summary:
        print(line)
    store_run("validate", inputs(), produced, summary=summary, violations=violations)
    if violations:
        warn(f"{violations} SHACL violations, see {rel(REPORT)}", strict)


def check() -> tuple[list[str], int]:
    summary = []

    ap_shapes, dangling = dcat_ap_shapes()
    sqp_shapes = load(SHAPES / "sqp-shapes.ttl")
    crm_shapes = load(SHAPES / "crm-shapes.ttl")

    silent = selftest(sqp_shapes, ap_shapes)
    if silent:
        raise RuntimeError(f"SHACL self-test: these rules did not fire on the broken entry: {silent}")
    summary.append("self-test: every expected rule fired on the broken entry")

    data = load(GRAPH, TYPES, SHAPES / "axioms.ttl")
    checks = [
        ("DCAT-AP 3.0.1", rel(GRAPH), run(data, ap_shapes)),
        ("Journal rules", rel(GRAPH), run(data, sqp_shapes)),
        ("CIDOC CRM rules", rel(CRM_GRAPH), run(load(CRM_GRAPH), crm_shapes)),
    ]

    lines = ["# Validation report (S8)", "",
             "| Check | Graph | Violations | Warnings | Infos |", "|---|---|---|---|---|"]
    total_violations = 0
    for name, graph, results in checks:
        sev = Counter(r[2] for r in results)
        total_violations += sev["Violation"]
        lines.append(f"| {name} | `{graph}` | {sev['Violation']} | {sev['Warning']} | {sev['Info']} |")
        summary.append(f"{name}: {sev['Violation']} violations, {sev['Warning']} warnings, {sev['Info']} infos")
    lines += ["", "Self-test: a deliberately broken entry (`shapes/selftest.ttl`) was reported "
              "by every rule it lists before the real graphs were checked.", "",
              "DCAT-AP 3.0.1 refers to property shapes it never defines; these references were "
              "dropped when loading (the files themselves are unchanged):", ""]
    lines += [f"- `{short(str(s))}` → `{str(o).rsplit('/', 1)[-1]}`" for s, o in dangling]
    for name, _, results in checks:
        if not results:
            continue
        lines += ["", f"## {name}", "", "| Severity | Path | Message | Focus nodes | Example |",
                  "|---|---|---|---|---|"]
        groups: dict[tuple, list] = {}
        for focus, path, severity, message, value in results:
            groups.setdefault((severity, path, message), []).append(focus)
        for (severity, path, message), foci in sorted(groups.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
            lines.append(f"| {severity} | `{short(path)}` | {message.replace('|', '/')} | {len(foci)} | "
                         f"`{short(sorted(foci)[0])}` |")
    write_text(REPORT, "\n".join(lines) + "\n")
    # The rules are published next to the ontology, so anyone can check the
    # graph against the same shapes (docs/shapes/).
    for name in ("sqp-shapes.ttl", "crm-shapes.ttl"):
        write_text(WEB_SHAPES / name, (SHAPES / name).read_text(encoding="utf-8"))
    summary.append(f"report -> {rel(REPORT)}")
    return summary, total_violations


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
