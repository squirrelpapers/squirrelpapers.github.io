"""S7 - The knowledge graph: DCAT 3 / DCAT-AP 3 with BIBO, FaBiO, PRISM,
schema.org, FOAF, GeoSPARQL and PROV, plus a CIDOC CRM bridge.

Reads data/derived/entries.json (S4). Writes

    dist/squirrelpapers.ttl          the catalogue: journal, volumes, issues,
                                     published entries, people, events, places
    dist/squirrelpapers-crm.ttl      the CIDOC CRM / CRMdig / LRMoo view of the same
                                     resources, kept apart (PRIMER A4) so that the
                                     DCAT graph stays readable on its own
    dist/vocab/types.ttl             the SKOS scheme of entry types
    dist/ontology/sqp.ttl            copy of ontology/sqp.ttl
    dist/reports/rdf.md              counts per class and property
    data/derived/web/...             per resource index.ttl and index.jsonld for docs/,
                                     the dumps under downloads/, ontology/ and vocab/

Every node has an IRI (no blank nodes): positions in author lists are
rdf:Seq nodes with their own IRI, distributions and time-spans are hash
IRIs under their resource. Drafts are not in the graph.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    BASE, DERIVED, DIST, ENTRIES_JSON, EVENT_NS, JOURNAL_IRI, ONTOLOGY_NS, ORG_NS,
    PLACE_NS, PREFIXES, RELEASE, REPORTS, ROOT, SITE, TYPE_NS, bind_prefixes,
    cached_run, canonical_turtle, copy_file, prune, read_json, rel, skipped, slugify,
    store_run, tracking, write_canonical_turtle, write_text,
)

WEB = DERIVED / "web"
GRAPH = DIST / "squirrelpapers.ttl"
CRM_GRAPH = DIST / "squirrelpapers-crm.ttl"
TYPES_TTL = DIST / "vocab" / "types.ttl"
ONTOLOGY_SRC = ROOT / "ontology" / "sqp.ttl"
ONTOLOGY_OUT = DIST / "ontology" / "sqp.ttl"
REPORT = REPORTS / "rdf.md"

LANG_EU = {"en": "ENG", "de": "DEU", "fr": "FRA", "it": "ITA", "es": "SPA"}
PUBLISHER = ORG_NS + "research-squirrel-engineers"


def ns():
    """Namespaces, used as N["dct"]["title"] - never N["dct"].title: rdflib's
    Namespace is a str, so .title, .format, .count ... are string methods and
    would silently become the predicate (found on the first S7 run)."""
    from rdflib import Namespace

    return {k: Namespace(v) for k, v in PREFIXES.items()}


def _event_slug(name: str) -> str:
    slug = slugify(name)
    return slug[:70].rsplit("-", 1)[0] if len(slug) > 70 else slug


def collect_events(entries: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    """-> (event IRI -> event, entry id -> event IRI).

    An event is one name in one year, and talks at it start within 14 days of
    each other - so the two EAA 2018 talks share one event, while the
    "Text+ Show and Tell" sessions of 2025 (March, May, July) stay three.
    The year is appended *after* shortening the name: cutting the joined
    slug lost it and merged CAA-UK 2018 with CAA-UK 2019 (S7).
    """
    from datetime import date

    talks = sorted(((e["event"].get("start") or "", e["id"], e["event"]) for e in entries
                    if not e.get("draft") and (e.get("event") or {}).get("name")),
                   key=lambda t: (t[2]["name"], t[0], t[1]))
    events: dict[str, dict] = {}
    by_entry: dict[str, str] = {}
    open_: dict[tuple[str, str], tuple[str, str]] = {}      # (slug, year) -> (iri, first start)
    for start, entry_id, ev in talks:
        slug, year = _event_slug(ev["name"]), start[:4]
        key = (slug, year)
        iri = None
        if key in open_:
            known_iri, first = open_[key]
            if not start or not first or (date.fromisoformat(start) - date.fromisoformat(first)).days <= 14:
                iri = known_iri
        if iri is None:
            # 'NFDI4Objects Community Meeting 2025' already carries its year
            iri = EVENT_NS + (f"{slug}-{year}" if year and not slug.endswith(year) else slug)
            if iri in events:                                  # second series date in a year
                iri = EVENT_NS + f"{slug}-{start}"
            open_[key] = (iri, start)
            events[iri] = dict(ev)
        known = events[iri]
        for field, pick in (("start", min), ("end", max)):
            values = [x for x in (known.get(field), ev.get(field)) if x]
            if values:
                known[field] = pick(values)
        if not isinstance(known.get("place"), dict) and isinstance(ev.get("place"), dict):
            known["place"] = ev["place"]
        by_entry[entry_id] = iri
    return events, by_entry


class Builder:
    """Collects triples into two graphs: the DCAT view and the CRM view."""

    def __init__(self, data: dict):
        from rdflib import Graph

        self.data = data
        self.N = ns()
        self.g = Graph()
        self.crm = Graph()
        bind_prefixes(self.g)
        bind_prefixes(self.crm)
        self.types = {t["slug"]: t for t in data["types"]}
        self.journal = data["journal"]
        self.seen_people: set[str] = set()
        self.seen_events: set[str] = set()
        self.seen_places: set[str] = set()
        self.events, self.event_of = collect_events(data["entries"])

    # -- helpers --------------------------------------------------------------

    def U(self, iri: str):
        from rdflib import URIRef

        return URIRef(iri)

    def L(self, value, lang: str | None = None, dtype: str | None = None):
        from rdflib import Literal, URIRef

        if dtype:
            return Literal(value, datatype=URIRef(dtype))
        return Literal(value, lang=lang) if lang else Literal(value)

    def date(self, iso: str):
        x = self.N["xsd"]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
            return self.L(iso, dtype=str(x.date))
        if re.fullmatch(r"\d{4}", iso):
            return self.L(iso, dtype=str(x.gYear))
        return self.L(iso)

    def add(self, s, p, o, graph=None):
        (graph if graph is not None else self.g).add((s, p, o))

    def typed(self, node, cls):
        """Type a node we only point to (a landing page, a language, a media
        type). DCAT-AP checks the class of these objects with sh:class (S8),
        and the authority files that define them are not loaded here."""
        self.g.add((node, self.N["rdf"]["type"], cls))
        return node

    # -- journal, volumes, issues ---------------------------------------------

    def journal_node(self):
        N, j = self.N, self.journal
        J = self.U(JOURNAL_IRI)
        A = self.add
        for cls in (N["dcat"]["Catalog"], N["fabio"]["Journal"], N["bibo"]["Periodical"],
                    N["schema"]["Periodical"]):
            A(J, N["rdf"]["type"], cls)
        A(J, N["dct"]["title"], self.L(j["title"], "en"))
        for lang, text in j["description"].items():
            A(J, N["dct"]["description"], self.L(text.strip(), lang))
        A(J, N["bibo"]["issn"], self.L(j["issn"]))
        A(J, N["prism"]["issn"], self.L(j["issn"]))
        A(J, N["dct"]["identifier"], self.L(f"ISSN {j['issn']}"))
        A(J, N["owl"]["sameAs"], N["wd"][j["wikidata"]])
        A(J, N["dcat"]["landingPage"], self.typed(self.U(SITE), N["foaf"]["Document"]))
        A(J, N["foaf"]["homepage"], self.typed(self.U(SITE), N["foaf"]["Document"]))
        A(J, N["dct"]["license"], self.U(j["licence"]["content"]))
        A(J, N["dct"]["modified"], self.L(RELEASE, dtype=str(N["xsd"]["date"])))
        for lang in j.get("languages", []):
            A(J, N["dct"]["language"], self.typed(N["eulang"][LANG_EU[lang]], N["dct"]["LinguisticSystem"]))
        A(J, N["dcat"]["themeTaxonomy"], self.U(TYPE_NS))
        # publisher and editor
        P = self.U(PUBLISHER)
        A(J, N["dct"]["publisher"], P)
        A(P, N["rdf"]["type"], N["foaf"]["Organization"])
        A(P, N["foaf"]["name"], self.L(j["publisher"], "en"))
        editor = j["editor"]
        E = self.person_node({"family": editor["name"].split(", ")[0],
                              "given": editor["name"].split(", ")[1],
                              "orcid": editor["orcid"],
                              "iri": BASE + "person/" + editor["orcid"]})
        A(J, N["bibo"]["editor"], E)
        A(J, N["schema"]["editor"], E)
        # CRM view
        C = self.crm
        A(J, N["rdf"]["type"], N["lrmoo"]["F18_Serial_Work"], C)
        A(J, N["rdf"]["type"], N["crm"]["E73_Information_Object"], C)
        A(J, N["crm"]["P1_is_identified_by"], self.identifier(J, "issn", j["issn"]), C)
        return J

    def volume_node(self, v: dict, J):
        N, A = self.N, self.add
        V = self.U(v["iri"])
        for cls in (N["dcat"]["DatasetSeries"], N["fabio"]["JournalVolume"]):
            A(V, N["rdf"]["type"], cls)
        years = v.get("coverage", str(v.get("year", ""))).replace("/", "–")
        A(V, N["dct"]["title"], self.L(f"Squirrel Papers, Volume {v['volume']} ({years})", "en"))
        A(V, N["dct"]["title"], self.L(f"Squirrel Papers, Band {v['volume']} ({years})", "de"))
        A(V, N["dct"]["description"], self.L(
            f"Volume {v['volume']} of the Squirrel Papers, covering {years}.", "en"))
        A(V, N["prism"]["volume"], self.L(str(v["volume"])))
        A(V, N["dct"]["isPartOf"], J)
        A(J, N["dcat"]["dataset"], V)
        # not dct:hasPart: DCAT-AP reserves it on a catalogue for sub-catalogues (S8)
        A(V, N["dcat"]["landingPage"], self.typed(self.U(SITE + v["path"] + "/"), N["foaf"]["Document"]))
        if v.get("wikidata"):
            A(V, N["owl"]["sameAs"], N["wd"][v["wikidata"]])
        A(V, N["rdf"]["type"], N["crm"]["E73_Information_Object"], self.crm)
        A(V, N["crm"]["P106i_forms_part_of"], J, self.crm)
        return V

    def issue_node(self, v: dict, issue: dict, V):
        N, A = self.N, self.add
        I = self.U(issue["iri"])
        for cls in (N["dcat"]["DatasetSeries"], N["fabio"]["JournalIssue"]):
            A(I, N["rdf"]["type"], cls)
        title_en = (issue.get("title") or {}).get("en")
        title_de = (issue.get("title") or {}).get("de")
        A(I, N["dct"]["title"], self.L(f"Squirrel Papers, Volume {v['volume']}, Issue {issue['issue']}"
                                    + (f": {title_en}" if title_en else ""), "en"))
        A(I, N["dct"]["title"], self.L(f"Squirrel Papers, Band {v['volume']}, Heft {issue['issue']}"
                                    + (f": {title_de}" if title_de else ""), "de"))
        A(I, N["dct"]["description"], self.L(
            title_en or f"Issue {issue['issue']} of volume {v['volume']} of the Squirrel Papers.", "en"))
        A(I, N["prism"]["number"], self.L(str(issue["issue"])))
        A(I, N["prism"]["volume"], self.L(str(v["volume"])))
        A(I, N["dcat"]["inSeries"], V)
        A(I, N["dct"]["isPartOf"], V)
        A(V, N["dct"]["hasPart"], I)
        A(I, N["sqp"]["sigil"], self.L(issue["sigil"]))
        A(I, N["sqp"]["specialIssue"], self.L(bool(issue.get("special"))))
        A(I, N["dcat"]["landingPage"], self.typed(self.U(SITE + issue["path"] + "/"), N["foaf"]["Document"]))
        if issue.get("wikidata"):
            A(I, N["owl"]["sameAs"], N["wd"][issue["wikidata"]])
        A(I, N["rdf"]["type"], N["crm"]["E73_Information_Object"], self.crm)
        A(I, N["crm"]["P106i_forms_part_of"], V, self.crm)
        return I

    # -- people, places, events -------------------------------------------------

    def person_node(self, p: dict):
        N, A = self.N, self.add
        P = self.U(p["iri"])
        if p["iri"] in self.seen_people:
            return P
        self.seen_people.add(p["iri"])
        for cls in (N["foaf"]["Person"], N["schema"]["Person"]):
            A(P, N["rdf"]["type"], cls)
        name = f"{p.get('given', '')} {p['family']}".strip()
        A(P, N["foaf"]["name"], self.L(name))
        A(P, N["foaf"]["familyName"], self.L(p["family"]))
        if p.get("given"):
            A(P, N["foaf"]["givenName"], self.L(p["given"]))
        A(P, N["rdfs"]["label"], self.L(name))
        A(P, N["rdf"]["type"], N["crm"]["E21_Person"], self.crm)
        if p.get("orcid"):
            orcid = self.U(f"https://orcid.org/{p['orcid']}")
            A(P, N["owl"]["sameAs"], orcid)
            A(P, N["schema"]["identifier"], orcid)
            A(P, N["crm"]["P1_is_identified_by"], self.identifier(P, "orcid", p["orcid"]), self.crm)
        return P

    def place_node(self, place: dict):
        N, A = self.N, self.add
        P = self.U(PLACE_NS + place["key"])
        if place["key"] in self.seen_places:
            return P
        self.seen_places.add(place["key"])
        for cls in (N["dct"]["Location"], N["schema"]["Place"], N["geo"]["Feature"]):
            A(P, N["rdf"]["type"], cls)
        A(P, N["rdfs"]["label"], self.L(place.get("name") or place["label"]))
        A(P, N["schema"]["description"], self.L(place["label"]))
        if place.get("wikidata"):
            A(P, N["owl"]["sameAs"], N["wd"][place["wikidata"]])
        if place.get("country"):
            A(P, N["schema"]["addressCountry"], N["wd"][place["country"]["wikidata"]])
        if "lat" in place:
            G = self.U(PLACE_NS + place["key"] + "#geometry")
            wkt = f"POINT({place['lon']} {place['lat']})"
            A(P, N["geo"]["hasGeometry"], G)
            A(P, N["geo"]["hasDefaultGeometry"], G)
            A(G, N["rdf"]["type"], N["geo"]["Geometry"])
            A(G, N["geo"]["asWKT"], self.L(wkt, dtype=str(N["geo"]["wktLiteral"])))
            A(P, N["dcat"]["centroid"], self.L(wkt, dtype=str(N["geo"]["wktLiteral"])))
            A(P, N["schema"]["latitude"], self.L(place["lat"]))
            A(P, N["schema"]["longitude"], self.L(place["lon"]))
            A(P, N["crm"]["P168_place_is_defined_by"],
              self.L(wkt, dtype=str(N["geo"]["wktLiteral"])), self.crm)
        A(P, N["rdf"]["type"], N["crm"]["E53_Place"], self.crm)
        return P

    def event_node(self, entry_id: str):
        N, A = self.N, self.add
        E = self.U(self.event_of[entry_id])
        if str(E) in self.seen_events:
            return E
        self.seen_events.add(str(E))
        ev = self.events[str(E)]
        for cls in (N["event"]["Event"], N["schema"]["Event"]):
            A(E, N["rdf"]["type"], cls)
        A(E, N["rdfs"]["label"], self.L(ev["name"]))
        A(E, N["schema"]["name"], self.L(ev["name"]))
        if ev.get("start"):
            A(E, N["schema"]["startDate"], self.date(ev["start"]))
        if ev.get("end"):
            A(E, N["schema"]["endDate"], self.date(ev["end"]))
        if ev.get("online"):
            A(E, N["schema"]["eventAttendanceMode"], N["schema"]["OnlineEventAttendanceMode"])
        place = ev.get("place")
        if isinstance(place, dict):
            P = self.place_node(place)
            A(E, N["schema"]["location"], P)
            A(E, N["event"]["place"], P)
        # CRM view
        C = self.crm
        A(E, N["rdf"]["type"], N["crm"]["E7_Activity"], C)
        A(E, N["crm"]["P1_is_identified_by"], self.appellation(E, ev["name"]), C)
        if isinstance(place, dict):
            A(E, N["crm"]["P7_took_place_at"], self.U(PLACE_NS + place["key"]), C)
        if ev.get("start"):
            A(E, N["crm"]["P4_has_time-span"], self.timespan(E, ev["start"], ev.get("end")), C)
        return E

    # -- CRM helpers ------------------------------------------------------------

    def identifier(self, owner, kind: str, value: str):
        N, A, C = self.N, self.add, self.crm
        I = self.U(f"{owner}#{kind}")
        A(I, N["rdf"]["type"], N["crm"]["E42_Identifier"], C)
        A(I, N["crm"]["P190_has_symbolic_content"], self.L(value), C)
        A(I, N["crm"]["P2_has_type"], self.U(BASE + "identifier-type/" + kind), C)
        return I

    def appellation(self, owner, text: str):
        N, A, C = self.N, self.add, self.crm
        T = self.U(f"{owner}#name")
        A(T, N["rdf"]["type"], N["crm"]["E41_Appellation"], C)
        A(T, N["crm"]["P190_has_symbolic_content"], self.L(text), C)
        return T

    def timespan(self, owner, start: str, end: str | None, name: str = "time-span"):
        """A time-span node at <owner base>#<name>. An IRI has at most one '#',
        so a hash owner (e5#creation) gets e5#creation-time-span."""
        N, A, C = self.N, self.add, self.crm
        base, _, frag = str(owner).partition("#")
        T = self.U(f"{base}#{frag}-{name}" if frag else f"{base}#{name}")
        A(T, N["rdf"]["type"], N["crm"]["E52_Time-Span"], C)
        begin = start if len(start) == 10 else f"{start[:4]}-01-01"
        finish = end or start
        finish = finish if len(finish) == 10 else f"{finish[:4]}-12-31"
        A(T, N["crm"]["P82a_begin_of_the_begin"], self.L(f"{begin}T00:00:00", dtype=str(N["xsd"]["dateTime"])), C)
        A(T, N["crm"]["P82b_end_of_the_end"], self.L(f"{finish}T23:59:59", dtype=str(N["xsd"]["dateTime"])), C)
        return T

    # -- entries ----------------------------------------------------------------

    def entry_node(self, e: dict, I):
        N, A, C = self.N, self.add, self.crm
        E = self.U(e["iri"])
        primary = self.types[e["types"][0]]
        A(E, N["rdf"]["type"], N["dcat"]["Dataset"])
        A(E, N["rdf"]["type"], N["fabio"][primary.get("fabio", "Expression")])
        A(E, N["rdf"]["type"], N["bibo"]["Document"])
        lang = e.get("language")
        A(E, N["dct"]["title"], self.L(e["title"], lang))
        if e.get("abstract"):
            A(E, N["dct"]["description"], self.L(e["abstract"], lang))
            A(E, N["bibo"]["abstract"], self.L(e["abstract"], lang))
        else:
            # DCAT-AP makes dct:description mandatory for a dataset.
            A(E, N["dct"]["description"], self.L(
                f"{primary['label']['en']} published in the Squirrel Papers {e['citation_label']}.", "en"))
        for slug in e["types"]:
            A(E, N["dct"]["type"], self.U(TYPE_NS + slug))
            A(E, N["dcat"]["theme"], self.U(TYPE_NS + slug))
        A(E, N["dcat"]["inSeries"], I)
        A(E, N["dct"]["isPartOf"], I)
        A(I, N["dct"]["hasPart"], E)
        A(E, N["sqp"]["entryNumber"], self.L(e["n"], dtype=str(N["xsd"]["positiveInteger"])))
        A(E, N["sqp"]["citationLabel"], self.L(e["citation_label"]))
        A(E, N["bibo"]["locator"], self.L(f"{e['sigil']}{e['n']}"))
        A(E, N["prism"]["volume"], self.L(str(e["volume"])))
        A(E, N["prism"]["number"], self.L(str(e["issue"])))
        A(E, N["dcat"]["landingPage"], self.typed(self.U(SITE + e["path"] + "/"), N["foaf"]["Document"]))
        A(E, N["dct"]["publisher"], self.U(PUBLISHER))
        if e.get("date"):
            A(E, N["dct"]["issued"], self.date(e["date"]))
        elif e.get("year"):
            A(E, N["dct"]["issued"], self.date(str(e["year"])))
        if lang:
            A(E, N["dct"]["language"], self.typed(N["eulang"][LANG_EU.get(lang, lang.upper())], N["dct"]["LinguisticSystem"]))
            if e.get("language_guessed"):
                A(E, N["sqp"]["languageGuessed"], self.L(True))
        if e.get("doi"):
            A(E, N["bibo"]["doi"], self.L(e["doi"]))
            A(E, N["dct"]["identifier"], self.L(e["doi_url"]))
            A(E, N["owl"]["sameAs"], self.U(e["doi_url"]))
            A(E, N["crm"]["P1_is_identified_by"], self.identifier(E, "doi", e["doi"]), C)
        for doi in e.get("related_dois", []):
            A(E, N["dct"]["relation"], self.U(f"https://doi.org/{doi}"))
        if e.get("wikidata"):
            A(E, N["owl"]["sameAs"], N["wd"][e["wikidata"]])
        if e.get("version"):
            A(E, N["dcat"]["version"], self.L(str(e["version"])))
        for kw in e.get("keywords", []):
            A(E, N["dcat"]["keyword"], self.L(kw))
        if e.get("licence", {}).get("url"):
            A(E, N["dct"]["license"], self.U(e["licence"]["url"]))
            A(self.U(e["licence"]["url"]), N["rdf"]["type"], N["dct"]["LicenseDocument"])
        if e.get("zenodo"):
            A(E, N["prov"]["wasDerivedFrom"], self.U(e["zenodo"]["url"]))
        links = e.get("links") or {}
        if links.get("repository"):
            A(E, N["schema"]["codeRepository"], self.U(links["repository"]))
        for key in ("video", "link", "release"):
            if links.get(key):
                A(E, N["rdfs"]["seeAlso"], self.U(links[key]))

        # people, in order
        creators = e.get("creators", [])
        if creators:
            S = self.U(e["iri"] + "#authors")
            A(E, N["bibo"]["authorList"], S)
            A(S, N["rdf"]["type"], N["rdf"]["Seq"])
            for i, p in enumerate(creators, start=1):
                P = self.person_node(p)
                A(E, N["dct"]["creator"], P)
                A(S, N["rdf"][f"_{i}"], P)
        for p in e.get("editors", []):
            A(E, N["bibo"]["editor"], self.person_node(p))
        for p in e.get("contributors", []):
            A(E, N["dct"]["contributor"], self.person_node(p))

        # event
        ev = e.get("event") or {}
        if ev.get("name"):
            EV = self.event_node(e["id"])
            A(E, N["bibo"]["presentedAt"], EV)
            A(EV, N["crm"]["P16_used_specific_object"], E, C)

        # distributions
        if e.get("pdf"):
            D = self.U(e["iri"] + "#pdf")
            A(E, N["dcat"]["distribution"], D)
            A(D, N["rdf"]["type"], N["dcat"]["Distribution"])
            A(D, N["dct"]["title"], self.L(e["pdf"]["key"]))
            A(D, N["dcat"]["accessURL"], self.U(e["zenodo"]["url"]))
            A(D, N["dcat"]["downloadURL"], self.U(e["pdf"]["download"]))
            A(D, N["dcat"]["mediaType"], self.typed(N["iana"]["application/pdf"], N["dct"]["MediaType"]))
            A(D, N["dct"]["format"], self.typed(N["eufiletype"]["PDF"], N["dct"]["MediaTypeOrExtent"]))
            pdf_file = next((f for f in e.get("files", []) if f["key"] == e["pdf"]["key"]), {})
            if pdf_file.get("size"):
                A(D, N["dcat"]["byteSize"], self.L(pdf_file["size"], dtype=str(N["xsd"]["nonNegativeInteger"])))
            if str(pdf_file.get("checksum", "")).startswith("md5:"):
                K = self.U(e["iri"] + "#pdf-checksum")
                A(D, N["spdx"]["checksum"], K)
                A(K, N["rdf"]["type"], N["spdx"]["Checksum"])
                A(K, N["spdx"]["algorithm"], self.typed(N["spdx"]["checksumAlgorithm_md5"], N["spdx"]["ChecksumAlgorithm"]))
                A(K, N["spdx"]["checksumValue"], self.L(pdf_file["checksum"][4:], dtype=str(N["xsd"]["hexBinary"])))
            if e.get("licence", {}).get("url"):
                A(D, N["dct"]["license"], self.U(e["licence"]["url"]))
            # CRM view: the file is a digital object carrying the expression
            A(D, N["rdf"]["type"], N["crmdig"]["D1_Digital_Object"], C)
            A(D, N["crm"]["P165_incorporates"], E, C)
        else:
            # A way to the work for records without a PDF: the Zenodo record,
            # the DOI, a link, or - for software releases without a DOI (7 of
            # them, S8) - the release or repository on GitHub.
            target = ((e.get("zenodo") or {}).get("url") or e.get("doi_url") or links.get("link")
                      or links.get("release") or links.get("repository"))
            if target:
                D = self.U(e["iri"] + "#landing")
                A(E, N["dcat"]["distribution"], D)
                A(D, N["rdf"]["type"], N["dcat"]["Distribution"])
                A(D, N["dct"]["title"], self.L("Landing page of the record", "en"))
                A(D, N["dcat"]["accessURL"], self.U(target))
                if e.get("licence", {}).get("url"):
                    A(D, N["dct"]["license"], self.U(e["licence"]["url"]))

        # CRM view of the entry itself
        A(E, N["rdf"]["type"], N["crm"]["E73_Information_Object"], C)
        A(E, N["rdf"]["type"], N["lrmoo"]["F2_Expression"], C)
        A(E, N["crm"]["P106i_forms_part_of"], I, C)
        A(E, N["crm"]["P102_has_title"], self.title(E, e["title"]), C)
        for slug in e["types"]:
            A(E, N["crm"]["P2_has_type"], self.U(TYPE_NS + slug), C)
        CR = self.U(e["iri"] + "#creation")
        A(CR, N["rdf"]["type"], N["crm"]["E65_Creation"], C)
        A(CR, N["rdf"]["type"], N["lrmoo"]["F28_Expression_Creation"], C)
        A(CR, N["crm"]["P94_has_created"], E, C)
        A(CR, N["lrmoo"]["R17_created"], E, C)
        for p in creators:
            A(CR, N["crm"]["P14_carried_out_by"], self.U(p["iri"]), C)
        date = e.get("date") or (str(e["year"]) if e.get("year") else None)
        if date:
            A(CR, N["crm"]["P4_has_time-span"], self.timespan(CR, date, None), C)
        return E

    def title(self, owner, text: str):
        N, A, C = self.N, self.add, self.crm
        T = self.U(f"{owner}#title")
        A(T, N["rdf"]["type"], N["crm"]["E35_Title"], C)
        A(T, N["crm"]["P190_has_symbolic_content"], self.L(text), C)
        return T

    # -- types --------------------------------------------------------------------

    def types_graph(self):
        from rdflib import Graph

        N = self.N
        g = Graph()
        bind_prefixes(g)
        S = self.U(TYPE_NS)
        g.add((S, N["rdf"]["type"], N["skos"]["ConceptScheme"]))
        g.add((S, N["dct"]["title"], self.L("Squirrel Papers entry types", "en")))
        g.add((S, N["dct"]["title"], self.L("Eintragstypen der Squirrel Papers", "de")))
        g.add((S, N["dct"]["license"], self.U("https://creativecommons.org/licenses/by/4.0/")))
        for t in self.data["types"]:
            C = self.U(TYPE_NS + t["slug"])
            g.add((C, N["rdf"]["type"], N["skos"]["Concept"]))
            g.add((C, N["rdf"]["type"], N["crm"]["E55_Type"]))
            g.add((C, N["skos"]["inScheme"], S))
            g.add((C, N["skos"]["notation"], self.L(t["slug"])))
            for lang, label in t["label"].items():
                g.add((C, N["skos"]["prefLabel"], self.L(label, lang)))
            if t.get("broader"):
                g.add((C, N["skos"]["broader"], self.U(TYPE_NS + t["broader"])))
                g.add((self.U(TYPE_NS + t["broader"]), N["skos"]["narrower"], C))
            else:
                g.add((S, N["skos"]["hasTopConcept"], C))
                g.add((C, N["skos"]["topConceptOf"], S))
            match = N["skos"]["closeMatch"] if t.get("match") == "close" else N["skos"]["exactMatch"]
            if t.get("coar"):
                g.add((C, match, self.U(f"http://purl.org/coar/resource_type/{t['coar']}")))
            if t.get("fabio"):
                g.add((C, N["rdfs"]["seeAlso"], N["fabio"][t["fabio"]]))
        return g


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def index_by_subject(graphs) -> dict[str, list]:
    """Triples grouped by subject without fragment (e5#pdf files under e5)."""
    index: dict[str, list] = {}
    for g in graphs:
        for triple in g:
            index.setdefault(str(triple[0]).split("#", 1)[0], []).append(triple)
    return index


def subgraph(index: dict[str, list], subjects: set[str]):
    """All triples about `subjects` and the hash IRIs under them."""
    from rdflib import Graph

    out = Graph()
    bind_prefixes(out)
    for subject in subjects:
        for triple in index.get(subject, []):
            out.add(triple)
    return out


def jsonld(graph) -> str:
    """Compact JSON-LD with a fixed context, nodes and values sorted.

    rdflib emits nodes in set order; sorting makes the file stable."""
    context = {k: v for k, v in PREFIXES.items()}
    raw = json.loads(graph.serialize(format="json-ld", context=context, auto_compact=True))
    nodes = raw.get("@graph", [raw] if "@id" in raw else [])

    def norm(value):
        if isinstance(value, list):
            return sorted((norm(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False))
        if isinstance(value, dict):
            return {k: norm(v) for k, v in value.items()}
        return value

    nodes = sorted((norm({k: v for k, v in n.items() if k != "@context"}) for n in nodes),
                   key=lambda n: n.get("@id", ""))
    return json.dumps({"@context": context, "@graph": nodes}, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"


def turtle(graph) -> str:
    """Canonical Turtle of a small graph."""
    return canonical_turtle(graph)


# ---------------------------------------------------------------------------


# Everything the graph is made from. Unchanged inputs and intact outputs let a
# run skip this step (S8b: 25 s of a 94 s Windows run).
INPUTS = [ENTRIES_JSON, ONTOLOGY_SRC, Path(__file__).resolve()]


def main(strict: bool = False) -> None:
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    record = cached_run("rdf", INPUTS)
    if record:
        summary = record["summary"] + ["inputs unchanged since the last run: graph and "
                                       "files kept (python main.py --fresh rebuilds)"]
        produced = {os.path.abspath(ROOT / path) for path in record["outputs"]}
    else:
        with tracking() as produced:
            summary = build()
    # Own kinds of file only: shapes/*.ttl in web/ belong to validate.
    removed = prune(WEB, produced, lambda path: path.endswith((".ttl", ".jsonld"))
                    and not path.startswith("shapes/"))
    for line in summary:
        print(line)
    if record:
        if removed:
            print(f"removed {len(removed)} stale files from {rel(WEB)}/")
        return
    if removed:
        print(f"removed {len(removed)} stale files from {rel(WEB)}/")
    store_run("rdf", INPUTS, produced, summary=summary)


def build() -> list[str]:
    from rdflib import BNode, Graph

    data = read_json(ENTRIES_JSON)
    b = Builder(data)
    entries = {e["id"]: e for e in data["entries"]}

    J = b.journal_node()
    resources = []          # (path, subjects) for the per-resource files
    for v in data["volumes"]:
        V = b.volume_node(v, J)
        vol_subjects = {v["iri"]}
        for issue in v["issues"]:
            I = b.issue_node(v, issue, V)
            for eid in issue["entries"]:
                e = entries[eid]
                if e.get("draft"):
                    continue
                b.entry_node(e, I)
                subjects = {e["iri"]} | {p["iri"] for role in ("creators", "editors", "contributors")
                                          for p in e.get(role, [])}
                if (e.get("event") or {}).get("name"):
                    subjects.add(b.event_of[e["id"]])
                    if isinstance(e["event"].get("place"), dict):
                        subjects.add(PLACE_NS + e["event"]["place"]["key"])
                resources.append((e["path"], subjects))
            resources.append((issue["path"], {issue["iri"]}))
        resources.append((v["path"], vol_subjects))

    for graph in (b.g, b.crm):
        assert not any(isinstance(t, BNode) for triple in graph for t in triple), "blank node in graph"

    # dumps
    write_canonical_turtle(b.g, GRAPH)
    write_canonical_turtle(b.crm, CRM_GRAPH)
    types = b.types_graph()
    write_canonical_turtle(types, TYPES_TTL)
    ontology = Graph().parse(ONTOLOGY_SRC, format="turtle")
    write_canonical_turtle(ontology, ONTOLOGY_OUT)

    # web copies
    index = index_by_subject((b.g, b.crm))
    for path, subjects in resources:
        sub = subgraph(index, subjects)
        write_text(WEB / path / "index.ttl", turtle(sub))
        write_text(WEB / path / "index.jsonld", jsonld(sub))
    journal_sub = subgraph(index, {JOURNAL_IRI, PUBLISHER})
    write_text(WEB / "index.ttl", turtle(journal_sub))
    write_text(WEB / "index.jsonld", jsonld(journal_sub))
    for src, target in ((GRAPH, "downloads/squirrelpapers.ttl"),
                        (CRM_GRAPH, "downloads/squirrelpapers.crm.ttl"),
                        (TYPES_TTL, "vocab/types.ttl"),
                        (ONTOLOGY_OUT, "ontology/index.ttl")):
        copy_file(src, WEB / target)
    merged = Graph()
    bind_prefixes(merged)
    for g in (b.g, b.crm):
        for t in g:
            merged.add(t)
    write_text(WEB / "downloads" / "squirrelpapers.jsonld", jsonld(merged))

    write_report(b, types, ontology, resources)
    return [f"{len(b.g)} triples (DCAT) + {len(b.crm)} (CRM) -> {rel(GRAPH)}, {rel(CRM_GRAPH)}",
            f"{len(resources)} resources with index.ttl and index.jsonld; "
            f"{len(b.seen_people)} people, {len(b.seen_events)} events, {len(b.seen_places)} places"]


def write_report(b: Builder, types, ontology, resources) -> None:
    N = b.N
    def classes(g):
        return Counter(str(o) for _, p, o in g if p == N["rdf"]["type"])
    def props(g):
        return Counter(str(p) for _, p, _ in g)
    def short(iri):
        for k, v in sorted(PREFIXES.items(), key=lambda kv: -len(kv[1])):
            if iri.startswith(v):
                return f"{k}:{iri[len(v):]}"
        return iri
    lines = ["# RDF report (S7)", "",
             f"- `{rel(GRAPH)}`: {len(b.g)} triples",
             f"- `{rel(CRM_GRAPH)}`: {len(b.crm)} triples",
             f"- `{rel(TYPES_TTL)}`: {len(types)} triples",
             f"- `{rel(ONTOLOGY_OUT)}`: {len(ontology)} triples",
             f"- resources with their own `index.ttl` / `index.jsonld`: {len(resources) + 1}", "",
             "## Classes (DCAT graph)", "", "| Class | Instances |", "|---|---|"]
    for c, n in sorted(classes(b.g).items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{short(c)}` | {n} |")
    lines += ["", "## Classes (CRM graph)", "", "| Class | Instances |", "|---|---|"]
    for c, n in sorted(classes(b.crm).items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{short(c)}` | {n} |")
    lines += ["", "## Properties (both graphs)", "", "| Property | Triples |", "|---|---|"]
    both = props(b.g) + props(b.crm)
    for p, n in sorted(both.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{short(p)}` | {n} |")
    write_text(REPORT, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
