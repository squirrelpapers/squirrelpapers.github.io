"""S16 - The data model, explained: content/model.yaml + the graphs -> data/derived/model.json.

The site step renders /model/ and /de/model/ from the result; the diagrams are
Mermaid, drawn in the browser by a copy of Mermaid served from this site.

Two parts are generated rather than written:

- `example`: the triples of one real entry (content/model.yaml: example),
  drawn twice - from the DCAT graph and from the CIDOC CRM graph - so the page
  shows what the graph says, not what someone remembered it to say.
- `rules`: the SHACL shapes of shapes/sqp-shapes.ttl and crm-shapes.ttl with
  their targets and messages.

And one check keeps the hand-written parts honest: every CURIE in a diagram or
a table (dcat:Dataset, crm:P14_carried_out_by, ...) must occur in the
published graphs - as a class, a property, a node or a datatype - unless the
section lists it under `inverse_ok` (CRM inverses such as P94i, which the
graph states in their forward direction only). A misspelt or outdated name
fails the build.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    BASE, CONTENT, DERIVED, DIST, PREFIXES, ROOT, cached_run, read_yaml, rel, skipped,
    store_run, tracking, write_json,
)

MODEL_YAML = CONTENT / "model.yaml"
MODEL_JSON = DERIVED / "model.json"
GRAPHS = [DIST / "squirrelpapers.ttl", DIST / "squirrelpapers-crm.ttl",
          DIST / "vocab" / "types.ttl", DIST / "ontology" / "sqp.ttl"]
SHAPES = [ROOT / "shapes" / "sqp-shapes.ttl", ROOT / "shapes" / "crm-shapes.ttl"]
CURIE = re.compile(r"(?<![\w/#.-])(" + "|".join(sorted(PREFIXES, key=len, reverse=True))
                   + r"):([A-Za-z_][\w-]*)")
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def short(iri: str) -> str:
    for prefix, namespace in sorted(PREFIXES.items(), key=lambda kv: -len(kv[1])):
        if iri.startswith(namespace) and iri != namespace:
            return f"{prefix}:{iri[len(namespace):]}"
    if iri.startswith(BASE):
        return "/" + iri[len(BASE):]
    return iri


# ---------------------------------------------------------------------------
# The CURIE check
# ---------------------------------------------------------------------------


def known_iris(graph) -> set[str]:
    from rdflib import Literal, URIRef

    known = set()
    for s, p, o in graph:
        known.add(str(p))
        for term in (s, o):
            if isinstance(term, URIRef):
                known.add(str(term))
            elif isinstance(term, Literal) and term.datatype is not None:
                known.add(str(term.datatype))
    return known


def check_curies(sections: list[dict], known: set[str]) -> list[str]:
    unknown = []
    for section in sections:
        allowed = set(section.get("inverse_ok", []))
        texts = [section.get("diagram", "")]
        for row in (section.get("table") or {}).get("rows", []):
            texts += [cell for cell in row if isinstance(cell, str)]
        for text in texts:
            for prefix, local in CURIE.findall(text or ""):
                curie = f"{prefix}:{local}"
                if curie not in allowed and PREFIXES[prefix] + local not in known:
                    unknown.append(f"{section['id']}: {curie}")
    return sorted(set(unknown))


# ---------------------------------------------------------------------------
# The example, drawn from the graphs
# ---------------------------------------------------------------------------


class Drawing:
    """A small Mermaid flowchart built from triples, with stable node ids."""

    def __init__(self, graph, classdefs: str, crm_view: bool):
        self.graph = graph
        self.classdefs = classdefs
        # Each drawing names the classes of its own layer only.
        self.layer = lambda t: t.startswith(("crm:", "crmdig:", "lrmoo:")) == crm_view
        self.nodes: dict[str, tuple[str, str, str]] = {}   # key -> (id, label, class)
        self.edges: list[tuple[str, str, str]] = []

    def kind(self, iri: str) -> str:
        types = {str(o) for o in self.graph.objects(self._ref(iri), self._ref(RDF_TYPE))}
        if any(t.endswith(("Person", "E21_Person", "Event", "E7_Activity", "Place", "E53_Place"))
               for t in types):
            return "real"
        if any(t.endswith("Concept") for t in types) or "/type/" in iri:
            return "term"
        return "inst" if iri.startswith(BASE) else "ext"

    def _ref(self, iri):
        from rdflib import URIRef

        return URIRef(iri)

    def label(self, iri: str) -> str:
        from rdflib import URIRef
        from rdflib.namespace import RDFS

        for predicate in (RDFS.label,):
            for value in self.graph.objects(URIRef(iri), predicate):
                return str(value)
        return short(iri)

    def node(self, term) -> str:
        from rdflib import Literal

        if isinstance(term, Literal):
            key = "lit:" + str(term)
            text = str(term)
            text = text if len(text) <= 48 else text[:45] + "…"
            label, cls = f'[/"{escape(text)}"/]', "prop"
        else:
            key = str(term)
            types = sorted(t for t in (short(str(o)) for o in self.graph.objects(term, self._ref(RDF_TYPE)))
                           if self.layer(t))
            caption = escape(self.label(key))
            if types:
                caption += "<br><small>" + escape(" · ".join(types[:2])) + "</small>"
            cls = self.kind(key)
            label = f'("{caption}")' if cls in ("inst", "real", "term") else f'["{caption}"]'
        if key not in self.nodes:
            self.nodes[key] = (f"n{len(self.nodes)}", label, cls)
        return self.nodes[key][0]

    def edge(self, s, p, o) -> None:
        self.edges.append((self.node(s), short(str(p)), self.node(o)))

    def mermaid(self) -> str:
        lines = ["flowchart LR"]
        for node_id, label, cls in self.nodes.values():
            lines.append(f"  {node_id}{label}:::{cls}")
        for a, p, b in self.edges:
            lines.append(f'  {a} -->|"{p}"| {b}')
        return "\n".join(lines) + "\n" + self.classdefs


def escape(text: str) -> str:
    return text.replace('"', "#quot;").replace("<", "#lt;").replace(">", "#gt;")


def example_dcat(graph, entry_iri: str, classdefs: str) -> str:
    from rdflib import URIRef

    N = {k: v for k, v in PREFIXES.items()}
    d = Drawing(graph, classdefs, crm_view=False)
    e = URIRef(entry_iri)
    for p in ("sqp:citationLabel", "dct:issued", "dcat:inSeries", "dct:type", "dct:creator",
              "bibo:presentedAt", "dcat:distribution", "owl:sameAs"):
        prefix, local = p.split(":")
        for o in sorted(graph.objects(e, URIRef(N[prefix] + local)), key=str)[:2]:
            d.edge(e, URIRef(N[prefix] + local), o)
    for event in graph.objects(e, URIRef(N["bibo"] + "presentedAt")):
        for place in graph.objects(event, URIRef(N["schema"] + "location")):
            d.edge(event, URIRef(N["schema"] + "location"), place)
            for same in graph.objects(place, URIRef(N["owl"] + "sameAs")):
                d.edge(place, URIRef(N["owl"] + "sameAs"), same)
    for dist in graph.objects(e, URIRef(N["dcat"] + "distribution")):
        for p in ("dcat:mediaType", "dcat:byteSize"):
            prefix, local = p.split(":")
            for o in graph.objects(dist, URIRef(N[prefix] + local)):
                d.edge(dist, URIRef(N[prefix] + local), o)
    for person in graph.objects(e, URIRef(N["dct"] + "creator")):
        for same in graph.objects(person, URIRef(N["owl"] + "sameAs")):
            d.edge(person, URIRef(N["owl"] + "sameAs"), same)
    return d.mermaid()


def example_crm(graph, entry_iri: str, classdefs: str) -> str:
    from rdflib import URIRef

    crm = PREFIXES["crm"]
    d = Drawing(graph, classdefs, crm_view=True)
    e = URIRef(entry_iri)

    def P(name):
        return URIRef(crm + name)

    for creation in graph.subjects(P("P94_has_created"), e):
        d.edge(creation, P("P94_has_created"), e)
        for person in graph.objects(creation, P("P14_carried_out_by")):
            d.edge(creation, P("P14_carried_out_by"), person)
        for span in graph.objects(creation, P("P4_has_time-span")):
            d.edge(creation, P("P4_has_time-span"), span)
            for begin in graph.objects(span, P("P82a_begin_of_the_begin")):
                d.edge(span, P("P82a_begin_of_the_begin"), begin)
    for p in ("P102_has_title", "P1_is_identified_by"):
        for node in graph.objects(e, P(p)):
            d.edge(e, P(p), node)
            for content in graph.objects(node, P("P190_has_symbolic_content")):
                d.edge(node, P("P190_has_symbolic_content"), content)
    for p in ("P2_has_type", "P106i_forms_part_of"):
        for node in graph.objects(e, P(p)):
            d.edge(e, P(p), node)
    for activity in graph.subjects(P("P16_used_specific_object"), e):
        d.edge(activity, P("P16_used_specific_object"), e)
        for place in graph.objects(activity, P("P7_took_place_at")):
            d.edge(activity, P("P7_took_place_at"), place)
            for wkt in graph.objects(place, P("P168_place_is_defined_by")):
                d.edge(place, P("P168_place_is_defined_by"), wkt)
    for pdf in graph.subjects(P("P165_incorporates"), e):
        d.edge(pdf, P("P165_incorporates"), e)
    return d.mermaid()


# ---------------------------------------------------------------------------
# The rules, read from the shapes
# ---------------------------------------------------------------------------


def rules() -> list[dict]:
    from rdflib import Graph, Namespace, URIRef
    from rdflib.namespace import RDF

    SH = Namespace("http://www.w3.org/ns/shacl#")
    out = []
    for path in SHAPES:
        g = Graph().parse(path, format="turtle")
        for shape in sorted(set(g.subjects(RDF.type, SH.NodeShape)), key=str):
            targets = [short(str(t)) for t in g.objects(shape, SH.targetClass)]
            targets += [short(str(t)) for t in g.objects(shape, SH.targetNode)]
            messages = []
            for part in list(g.objects(shape, SH.property)) + list(g.objects(shape, SH.sparql)):
                for message in g.objects(part, SH.message):
                    messages.append(str(message))
                if not list(g.objects(part, SH.message)):
                    paths = [short(str(p)) for p in g.objects(part, SH.path) if isinstance(p, URIRef)]
                    if paths:
                        messages.append(f"{paths[0]} " + describe(g, part, SH))
            if not targets:
                continue
            out.append({"file": rel(path), "shape": short(str(shape)).split("#")[-1],
                        "targets": targets, "rules": sorted(set(messages))})
    return out


def describe(g, part, SH) -> str:
    """A rule without a message, put in words from its counts."""
    lo = next(iter(g.objects(part, SH.minCount)), None)
    hi = next(iter(g.objects(part, SH.maxCount)), None)
    if lo is not None and hi is not None:
        return f"exactly {lo}" if str(lo) == str(hi) else f"{lo} to {hi}"
    if lo is not None:
        return f"at least {lo}"
    if hi is not None:
        return f"at most {hi}"
    return "constrained"


# ---------------------------------------------------------------------------


def inputs() -> list[Path]:
    return [MODEL_YAML, *GRAPHS, *SHAPES, Path(__file__).resolve()]


def main(strict: bool = False) -> None:
    if not MODEL_YAML.exists():
        skipped(f"{rel(MODEL_YAML)} missing")
        return
    missing = [rel(p) for p in GRAPHS if not p.exists()]
    if missing:
        skipped(f"graphs missing (S7): {', '.join(missing)}")
        return
    record = cached_run("model", inputs())
    if record:
        for line in record["summary"]:
            print(line)
        print("model, graphs and shapes unchanged since the last run: page data kept")
        return
    with tracking() as produced:
        summary = build()
    for line in summary:
        print(line)
    store_run("model", inputs(), produced, summary=summary)


def build() -> list[str]:
    from rdflib import Graph

    config = read_yaml(MODEL_YAML)
    for section in config["sections"]:
        # An unquoted comma in a YAML flow mapping splits a title silently
        # ("Die Regeln, die ..." became two keys); demand exactly en and de.
        for key in ("title", "text"):
            if set(section.get(key) or {}) != {"en", "de"}:
                raise ValueError(f"{rel(MODEL_YAML)}: section {section.get('id')}: '{key}' "
                                 f"needs exactly 'en' and 'de' (quote texts with commas)")
    graph = Graph()
    for path in GRAPHS:
        graph.parse(path, format="turtle")
    unknown = check_curies(config["sections"], known_iris(graph))
    if unknown:
        raise RuntimeError("content/model.yaml names terms the published graphs do not use:\n  "
                           + "\n  ".join(unknown))

    dcat, crm = Graph(), Graph()
    dcat.parse(GRAPHS[0], format="turtle")
    dcat.parse(GRAPHS[2], format="turtle")
    crm.parse(GRAPHS[1], format="turtle")
    crm.parse(GRAPHS[0], format="turtle")          # labels of people, places, events
    classdefs = config["classdefs"].rstrip("\n")
    sections, diagrams = [], 0
    for section in config["sections"]:
        out = {k: v for k, v in section.items() if k != "inverse_ok"}
        if section.get("diagram"):
            out["diagram"] = section["diagram"].rstrip("\n") + "\n" + classdefs
            diagrams += 1
        if section.get("generated") == "example":
            out["diagrams"] = [{"label": "DCAT", "source": example_dcat(dcat, config["example"], classdefs)},
                               {"label": "CIDOC CRM", "source": example_crm(crm, config["example"], classdefs)}]
            diagrams += 2
        if section.get("generated") == "rules":
            out["rules"] = rules()
        sections.append(out)
    write_json({"sections": sections, "example": config["example"]}, MODEL_JSON)
    curies = sum(len(CURIE.findall(text)) for s in config["sections"]
                 for text in [s.get("diagram") or ""] + [c for row in (s.get("table") or {}).get("rows", [])
                                                         for c in row if isinstance(c, str)])
    return [f"{len(sections)} sections, {diagrams} diagrams ({diagrams - 2} written, 2 drawn "
            f"from the graphs) -> {rel(MODEL_JSON)}",
            f"term check: {curies} CURIEs in the written diagrams and tables, all in the graphs"]


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
