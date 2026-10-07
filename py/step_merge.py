"""S4 - Merge content/*.yaml with the harvest cache into data/derived/entries.json.

Every later step (citations, RDF, map, site, query page) reads this one file
and nothing else from content/ or data/raw/. Rules (PRIMER Teil C, S4, A4):

- content/ wins. Zenodo only fills what content/ leaves open: type (for the
  entries migrated without one), date, licence, abstract, keywords, files,
  language, version.
- Types are mapped onto the SKOS scheme in content/vocab/types.yaml. An
  unknown slug is an error under --strict.
- People are aligned by ORCID. A person without ORCID is matched to a known
  ORCID by family name and compatible initials ('A.W. Mees' -> 'Mees, Allard
  W.'); what stays ambiguous is reported, never guessed.
- Places come from content/places.yaml plus the Wikidata cache; a
  `coordinates` field there takes precedence.
- Drafts stay in the file (`draft: true`) so their IRIs stay reserved; the
  site does not publish them.

Output: data/derived/entries.json and dist/reports/merge.md.
"""

from __future__ import annotations

import difflib
import html
from urllib.parse import quote
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    BASE, ENTRIES_JSON, JOURNAL_YAML, PERSON_NS, PLACES_YAML, RAW_WIKIDATA,
    RAW_ZENODO, REPORTS, TYPE_NS, VOCAB_DIR, citation_label, entry_iri,
    entry_path, issue_iri, issue_path, read_json, read_yaml, rel, skipped,
    slugify, volume_iri, volume_path, volume_yamls, warn, write_json,
    write_text, zenodo_record_id,
)

REPORT = REPORTS / "merge.md"
TYPES_YAML = VOCAB_DIR / "types.yaml"

LANGUAGE_3_TO_2 = {"eng": "en", "deu": "de", "ger": "de", "fra": "fr", "ita": "it",
                   "spa": "es", "enc": "en"}
LICENCES = {
    "cc-by-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-sa-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "cc-zero": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "mit-license": "https://spdx.org/licenses/MIT.html",
    "mit": "https://spdx.org/licenses/MIT.html",
    "gpl-2.0": "https://spdx.org/licenses/GPL-2.0-only.html",
    "gpl-3.0": "https://spdx.org/licenses/GPL-3.0-only.html",
    "apache-2.0": "https://spdx.org/licenses/Apache-2.0.html",
    "other-open": None,          # Zenodo's "Other (Open)": no URL to point to
}
PARTICLES = {"von", "van", "der", "de", "den", "thor", "zu", "du", "la", "le", "di", "da"}
SAFE_TAGS = {"p", "br", "em", "strong", "i", "b", "ul", "ol", "li", "a", "code", "sub", "sup"}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


GERMAN = {"der", "die", "das", "und", "mit", "von", "für", "im", "in", "zur", "zum", "den",
          "dem", "des", "ein", "eine", "einer", "auf", "über", "zwischen", "bei", "als", "wie",
          "oder", "nach", "aus", "am", "vom", "ist", "sind", "neue", "digitale", "daten"}
ENGLISH = {"the", "and", "of", "for", "with", "to", "in", "on", "a", "an", "from", "by", "as",
           "how", "using", "into", "towards", "between", "is", "are", "new", "data"}


def guess_language(title: str) -> str | None:
    """'de' or 'en' from function words in the title, or None if unclear.

    114 of 210 published entries carry no language in content/ or on Zenodo,
    and citation styles title-case every title they believe is English
    ("Brückenbau Zwischen LOD Und RSE", S6). A guess is better than English by
    default; it is marked `language_guessed` and content/ always wins."""
    words = re.findall(r"[a-zäöüß]+", title.lower())
    de = sum(w in GERMAN for w in words) + 2 * len(re.findall(r"[äöüß]", title.lower()))
    en = sum(w in ENGLISH for w in words)
    if de > en and de >= 2:
        return "de"
    if en > de and en >= 1:
        return "en"
    return None


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


class _Cleaner(HTMLParser):
    """Zenodo descriptions are HTML. Keep a small safe subset for the page and
    a plain-text version for RDF and citations."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in SAFE_TAGS:
            if tag == "a":
                href = dict(attrs).get("href") or ""
                if href.startswith(("http://", "https://")):
                    self.html.append(f'<a href="{html.escape(href, quote=True)}" rel="noopener">')
                else:
                    self.html.append("<a>")
            else:
                self.html.append(f"<{tag}>")
        if tag in ("p", "br", "li"):
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in SAFE_TAGS and tag != "br":
            self.html.append(f"</{tag}>")

    def handle_data(self, data):
        self.html.append(html.escape(data, quote=False))
        self.text.append(data)


def clean_description(raw: str | None) -> tuple[str, str]:
    if not raw:
        return "", ""
    parser = _Cleaner()
    parser.feed(raw)
    parser.close()
    text = re.sub(r"[ \t]+", " ", "".join(parser.text))
    text = re.sub(r"\s*\n\s*", "\n", text).strip()
    return "".join(parser.html).strip(), text


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


def load_types() -> tuple[dict, dict, dict]:
    """-> (concepts by slug, alias -> slug, zenodo type -> slug)."""
    doc = read_yaml(TYPES_YAML)
    concepts, aliases, zenodo = {}, {}, {}
    for concept in doc["concepts"]:
        slug = concept["slug"]
        concepts[slug] = concept
        aliases[slug] = slug
        for alias in concept.get("aliases", []):
            aliases[alias] = slug
        for z in concept.get("zenodo", []):
            zenodo[z] = slug
    return concepts, aliases, zenodo


def zenodo_type(record: dict) -> str | None:
    rt = record.get("metadata", {}).get("resource_type") or {}
    if not rt.get("type"):
        return None
    return f"{rt['type']}/{rt['subtype']}" if rt.get("subtype") else rt["type"]


# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------


TITLES = re.compile(r"\b(?:Dr|Prof|PD|Dipl\.-Ing|Mag|apl)\.\s*", re.I)
SUFFIXES = re.compile(r",?\s*\b(?:FSA|PhD|M\.A\.|MA|MSc|BSc)\b\.?\s*$")


def split_name(name: str) -> tuple[str, str]:
    """'Thiery, Florian' / 'Florian Thiery' / 'F. Thiery' / 'M. thor Straten'
    -> (family, given). Academic titles and post-nominals are dropped
    ('Dr. Allard Mees, FSA' -> ('Mees', 'Allard'))."""
    name = re.sub(r"\s+", " ", name).strip()
    name = SUFFIXES.sub("", TITLES.sub("", name)).strip(" ,")
    if "," in name:
        family, given = [p.strip() for p in name.split(",", 1)]
        return family, given
    tokens = name.split(" ")
    if len(tokens) == 1:
        return tokens[0], ""
    # 'Schmidt S.C.' - initials after the family name
    if re.fullmatch(r"(?:[A-Z]\.-?)+", tokens[-1]) and len(tokens) == 2:
        return tokens[0], tokens[1]
    # family name = last token plus any lower-case particles before it
    i = len(tokens) - 1
    while i - 1 > 0 and tokens[i - 1].lower() in PARTICLES:
        i -= 1
    return " ".join(tokens[i:]), " ".join(tokens[:i])


def initials(given: str) -> str:
    """'Allard W.' -> 'AW', 'A.W.' -> 'AW', 'A.-K.' -> 'AK', 'LK' -> 'LK'."""
    parts = re.findall(r"[A-ZÄÖÜ][a-zäöüß]*", given)
    return "".join(p[0] for p in parts)


def compatible(given_a: str, given_b: str) -> bool:
    """Initials of the shorter form are a prefix of the other's."""
    a, b = initials(given_a), initials(given_b)
    if not a or not b:
        return True
    return a.startswith(b) or b.startswith(a)


class People:
    """Registry of persons, keyed by ORCID where there is one."""

    def __init__(self):
        self.names_by_orcid: dict[str, Counter] = defaultdict(Counter)

    def learn(self, name: str, orcid: str | None, weight: int = 1) -> None:
        if orcid and name:
            family, given = split_name(name)
            self.names_by_orcid[orcid][(family, given)] += weight

    def canonical(self, orcid: str, fallback: tuple[str, str] = ("", "")) -> tuple[str, str]:
        """Most frequent family spelling; of its given names, the longest one
        that is used at least a quarter as often as the most frequent - so
        'Allard W.' beats 'Allard', and a one-off typo ('Kasten' for
        'Karsten') does not win just by being there."""
        counts = self.names_by_orcid.get(orcid)
        if not counts:
            return fallback
        family = Counter()
        for (f, _), n in counts.items():
            family[f] += n
        best_family = sorted(family.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        givens = {g: n for (f, g), n in counts.items() if f == best_family}
        top = max(givens.values())
        frequent = [g for g, n in givens.items() if n * 4 >= top]
        return best_family, max(frequent, key=lambda g: (len(g), g))

    def match(self, family: str, given: str) -> list[str]:
        """ORCIDs whose canonical family name equals this one and whose
        initials are compatible."""
        hits = []
        for orcid in self.names_by_orcid:
            f, g = self.canonical(orcid)
            known_families = {norm(kf) for kf, _ in self.names_by_orcid[orcid]}
            if (norm(f) == norm(family) or norm(family) in known_families) and compatible(g, given):
                hits.append(orcid)
        return sorted(hits)


def person_record(family: str, given: str, orcid: str | None) -> dict:
    out = {"family": family, "given": given,
           "name": f"{family}, {given}" if given else family}
    if orcid:
        out["orcid"] = orcid
        out["iri"] = PERSON_NS + orcid
    else:
        out["iri"] = PERSON_NS + slugify(f"{family} {given}")
    return out


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------


def load_places() -> dict[str, dict]:
    places = {}
    for place in (read_yaml(PLACES_YAML) or {}).get("places", []) if PLACES_YAML.exists() else []:
        out = {"key": place["key"], "label": place["label"]}
        qid = place.get("wikidata")
        item = read_json(RAW_WIKIDATA / f"{qid}.json") if qid and (RAW_WIKIDATA / f"{qid}.json").exists() else {}
        if qid:
            out["wikidata"] = qid
            out["name"] = item.get("labels", {}).get("en") or item.get("labels", {}).get("de") or place["label"]
            if item.get("country"):
                country = item["country"][0]
                c_item = read_json(RAW_WIKIDATA / f"{country}.json") if (RAW_WIKIDATA / f"{country}.json").exists() else {}
                out["country"] = {"wikidata": country,
                                  "name": c_item.get("labels", {}).get("en", country)}
        coords = place.get("coordinates") or item.get("coordinates")
        if coords:
            out["lat"], out["lon"] = round(float(coords["lat"]), 6), round(float(coords["lon"]), 6)
        places[place["key"]] = out
    return places


# ---------------------------------------------------------------------------
# The merge
# ---------------------------------------------------------------------------


def zenodo_record(doi: str | None) -> dict | None:
    if not doi or "zenodo." not in doi:
        return None
    path = RAW_ZENODO / f"{zenodo_record_id(doi)}.json"
    return read_json(path) if path.exists() else None


def files_of(record: dict) -> list[dict]:
    files = record.get("files") or []
    if isinstance(files, dict):
        files = list((files.get("entries") or {}).values())
    out = []
    for f in sorted(files, key=lambda f: str(f.get("key", ""))):
        key = str(f.get("key", ""))
        out.append({"key": key, "size": f.get("size"),
                    "checksum": f.get("checksum"),
                    # File names on Zenodo may contain spaces; the URL must not
                    # (rdflib refused one in S7, browsers repair it silently).
                    "url": f"https://zenodo.org/records/{record['id']}/files/{quote(key)}?download=1"})
    return out


def main(strict: bool = False) -> None:
    yamls = volume_yamls()
    if not yamls:
        skipped("no content/vol*.yaml yet (S2)")
        return
    if not TYPES_YAML.exists():
        skipped(f"{rel(TYPES_YAML)} missing")
        return

    concepts, aliases, zenodo_types = load_types()
    places = load_places()
    journal = read_yaml(JOURNAL_YAML)
    notes: list[tuple[str, str, str]] = []

    def note(where, kind, text):
        notes.append((where, kind, str(text)))

    # -- pass 1: read everything, teach the people registry -------------------
    docs = [read_yaml(p) for p in yamls]
    people = People()
    for doc in docs:
        for issue in doc["issues"]:
            for e in issue["entries"]:
                for c in e.get("creators", []):
                    people.learn(c.get("name", ""), c.get("orcid"))
                record = zenodo_record(e.get("doi"))
                for c in (record or {}).get("metadata", {}).get("creators", []):
                    # Zenodo spellings are the full names; they count double.
                    people.learn(c.get("name", ""), c.get("orcid"), weight=2)

    def resolve(name: str, orcid: str | None, where: str, zen: list[dict] = ()) -> dict:
        """One person, whatever path they came in by: ORCID if known or
        uniquely matchable, the canonical spelling for that ORCID, else the
        fullest compatible spelling on the Zenodo record."""
        family, given = split_name(name)
        if not orcid:
            hits = people.match(family, given)
            if len(hits) == 1:
                orcid = hits[0]
            elif len(hits) > 1:
                note(where, "person-ambiguous", f"{name} -> {hits}")
        if orcid:
            family, given = people.canonical(orcid, (family, given))
        else:
            for zc in zen:
                zf, zg = split_name(zc.get("name", ""))
                if norm(zf) == norm(family) and compatible(zg, given) and len(zg) > len(given):
                    family, given = zf, zg
                    break
        return person_record(family, given, orcid)

    # -- pass 2: build entries --------------------------------------------------
    entries, volumes_out = [], []
    unknown_types = Counter()
    for doc in docs:
        v = doc["volume"]
        vol_out = {"volume": v, "year": doc.get("year"), "iri": volume_iri(v),
                   "path": volume_path(v), "issues": []}
        for key in ("coverage", "wikidata"):
            if doc.get(key):
                vol_out[key] = doc[key]
        for issue in doc["issues"]:
            i, sigil = issue["issue"], issue.get("sigil", "#")
            iss_out = {"issue": i, "sigil": sigil, "iri": issue_iri(v, i),
                       "path": issue_path(v, i), "special": bool(issue.get("special")),
                       "entries": []}
            if issue.get("title"):
                iss_out["title"] = issue["title"]
            if issue.get("wikidata"):
                iss_out["wikidata"] = issue["wikidata"]

            for e in issue["entries"]:
                n = e["n"]
                where = f"{v}({i}) {sigil}{n}"
                record = zenodo_record(e.get("doi"))
                meta = (record or {}).get("metadata", {})
                out = {
                    "volume": v, "issue": i, "n": n, "sigil": sigil,
                    "id": entry_path(v, i, n).replace("/", "-"),
                    "iri": entry_iri(v, i, n), "path": entry_path(v, i, n),
                    "citation_label": citation_label(v, i, sigil, n),
                    "title": e["title"],
                }
                if e.get("draft"):
                    out["draft"] = True

                # types
                slugs = []
                for t in e.get("types", []):
                    if t in aliases:
                        if aliases[t] not in slugs:
                            slugs.append(aliases[t])
                    else:
                        unknown_types[t] += 1
                        note(where, "unknown-type", t)
                if not slugs and record:
                    zt = zenodo_type(record)
                    slug = zenodo_types.get(zt) or zenodo_types.get((zt or "").split("/")[0])
                    if slug:
                        slugs.append(slug)
                        note(where, "type-from-zenodo", f"{zt} -> {slug}")
                if not slugs:
                    slugs = ["other"]
                    if not e.get("draft"):
                        note(where, "type-missing", "no type in content/ or Zenodo; 'other'")
                out["types"] = slugs

                # people
                creators = []
                zen_creators = meta.get("creators", [])
                for c in e.get("creators", []):
                    creators.append(resolve(c.get("name", ""), c.get("orcid"), where, zen_creators))
                if not creators and zen_creators:
                    creators = [resolve(zc["name"], zc.get("orcid"), where) for zc in zen_creators]
                    note(where, "creators-from-zenodo", len(creators))
                if zen_creators and e.get("creators") and len(zen_creators) != len(e["creators"]) \
                        and not e.get("et_al"):
                    note(where, "creator-count", f"content/ {len(e['creators'])}, Zenodo {len(zen_creators)}")
                if e.get("et_al") and len(zen_creators) > len(creators):
                    # 'F. Thiery et al.': Zenodo knows the full list
                    creators += [resolve(zc["name"], zc.get("orcid"), where)
                                 for zc in zen_creators[len(creators):]]
                    note(where, "et-al-completed", f"{len(creators)} creators from Zenodo")
                out["creators"] = creators
                for key in ("editors", "contributors"):
                    if e.get(key):
                        out[key] = [resolve(c.get("name", ""), c.get("orcid"), where) for c in e[key]]

                # identifiers and links
                if e.get("doi"):
                    out["doi"] = e["doi"]
                    out["doi_url"] = f"https://doi.org/{e['doi']}"
                if e.get("related_dois"):
                    out["related_dois"] = e["related_dois"]
                for key in ("wikidata", "isbn", "version", "release_label", "context",
                            "links", "container", "legacy_citation"):
                    if e.get(key):
                        out[key] = e[key]
                if record:
                    out["zenodo"] = {
                        "record": str(record["id"]),
                        "url": f"https://zenodo.org/records/{record['id']}",
                        "concept_doi": record.get("conceptdoi"),
                        "version_doi": record.get("doi"),
                    }
                    files = files_of(record)
                    if files:
                        out["files"] = files
                        pdf = next((f for f in files if f["key"].lower().endswith(".pdf")), None)
                        if pdf:
                            out["pdf"] = {
                                "key": pdf["key"],
                                "preview": f"https://zenodo.org/records/{record['id']}/preview/{quote(pdf['key'])}",
                                "download": pdf["url"],
                            }
                    if meta.get("version") and "version" not in out:
                        out["version"] = meta["version"]
                    if meta.get("keywords"):
                        out["keywords"] = sorted(set(meta["keywords"]), key=str.lower)
                    lic = (meta.get("license") or {}).get("id")
                    if lic:
                        out["licence"] = {"id": lic, "url": LICENCES.get(lic)}
                        if lic not in LICENCES:  # an unknown id, not "other-open"
                            note(where, "licence-unmapped", lic)
                    abstract_html, abstract = clean_description(meta.get("description"))
                    if abstract:
                        out["abstract"] = abstract
                        out["abstract_html"] = abstract_html
                    if similarity(e["title"], meta.get("title", "")) < 0.6:
                        out["title_zenodo"] = meta.get("title")
                elif e.get("doi") and not e.get("draft"):
                    note(where, "no-zenodo-record", e["doi"])

                # language and dates
                language = e.get("language") or LANGUAGE_3_TO_2.get(meta.get("language") or "")
                if not language:
                    language = guess_language(e["title"])
                    if language:
                        out["language_guessed"] = True
                if language:
                    out["language"] = language
                event = dict(e.get("event") or {})
                if event:
                    if event.get("place"):
                        place = places.get(event["place"])
                        if place:
                            event["place"] = place
                        else:
                            note(where, "place-unknown", event["place"])
                            event.pop("place")
                    out["event"] = event
                date = e.get("date") or event.get("start")
                zen_date = meta.get("publication_date")
                if not date and zen_date:
                    # A concept DOI answers with the *latest* version, whose
                    # date can be years after the entry (2(2) #1: 2024 in the
                    # volume of 2020). Such a date is kept for information only.
                    lo, hi = (2014, 2019) if v == 1 else (doc.get("year"), doc.get("year"))
                    if lo and not (lo <= int(zen_date[:4]) <= hi):
                        out["zenodo_date"] = zen_date
                        note(where, "zenodo-date-ignored",
                             f"{zen_date} (latest version) outside the volume; year from the volume")
                    else:
                        date = zen_date
                if date:
                    out["date"] = date
                    out["year"] = int(str(date)[:4])
                else:
                    out["year"] = doc.get("year")
                    if not e.get("draft") and "zenodo_date" not in out:
                        note(where, "no-date", "year taken from the volume")
                if out["year"] and doc.get("year") and v > 1 and out["year"] != doc["year"]:
                    note(where, "year-outside-volume", f"{date} in volume of {doc['year']}")

                entries.append(out)
                iss_out["entries"].append(out["id"])
            vol_out["issues"].append(iss_out)
        volumes_out.append(vol_out)

    # -- people without ORCID: one record per person ----------------------------
    # 'Distel, A.-K.' and 'Distel, Anne-Karoline' are one person if nothing
    # says otherwise: same family name, compatible initials, no ORCID on
    # either side. The fullest spelling wins.
    loose: dict[str, dict] = {}
    for e in entries:
        for role in ("creators", "editors", "contributors"):
            for p in e.get(role, []):
                if "orcid" not in p:
                    loose[p["iri"]] = p
    by_family = defaultdict(list)
    for p in loose.values():
        by_family[norm(p["family"])].append(p)
    rename: dict[str, dict] = {}
    for group in by_family.values():
        group = sorted(group, key=lambda p: (-len(p["given"]), p["given"]))
        for p in group:
            target = next(q for q in group if compatible(q["given"], p["given"]))
            if target["iri"] != p["iri"]:
                rename[p["iri"]] = target
                note(p["name"], "person-merged", f"-> {target['name']}")
    for e in entries:
        for role in ("creators", "editors", "contributors"):
            if role in e:
                e[role] = [dict(rename[p["iri"]]) if p["iri"] in rename else p for p in e[role]]

    # -- people index ------------------------------------------------------------
    person_index: dict[str, dict] = {}
    for e in entries:
        for role in ("creators", "editors", "contributors"):
            for p in e.get(role, []):
                rec = person_index.setdefault(p["iri"], {**p, "entries": []})
                if e["id"] not in rec["entries"]:
                    rec["entries"].append(e["id"])
    # Same name, one with ORCID and one without: reported, not merged.
    by_name = defaultdict(list)
    for p in person_index.values():
        by_name[norm(p["family"])].append(p)
    for family, group in sorted(by_name.items()):
        if len(group) > 1 and any("orcid" in p for p in group) and any("orcid" not in p for p in group):
            note(family, "person-split", " / ".join(sorted(p["name"] + (" (ORCID)" if "orcid" in p else "")
                                                           for p in group)))

    data = {
        "journal": {k: journal[k] for k in ("title", "issn", "wikidata", "iri", "homepage",
                                             "publisher", "editor", "licence", "description",
                                             "registration", "contact", "languages")
                    if k in journal},
        "volumes": volumes_out,
        "entries": entries,
        "people": sorted(person_index.values(), key=lambda p: (norm(p["family"]), norm(p["given"]), p["iri"])),
        "places": [places[k] for k in sorted(places)],
        "types": [{"slug": c["slug"], "iri": TYPE_NS + c["slug"], "label": c["label"],
                   **{k: c[k] for k in ("broader", "coar", "fabio", "match") if k in c}}
                  for c in concepts.values()],
        "base": BASE,
    }
    write_json(data, ENTRIES_JSON)
    write_report(data, notes)

    published = [e for e in entries if not e.get("draft")]
    print(f"{len(entries)} entries ({len(published)} published, {len(entries) - len(published)} drafts), "
          f"{len(data['people'])} people, {len(places)} places -> {rel(ENTRIES_JSON)}")
    print(f"{len(notes)} notes -> {rel(REPORT)}")
    if unknown_types:
        warn(f"unknown type slugs: {dict(unknown_types)}", strict)


def write_report(data: dict, notes: list[tuple[str, str, str]]) -> None:
    entries = data["entries"]
    published = [e for e in entries if not e.get("draft")]
    types = Counter(e["types"][0] for e in published)
    with_pdf = sum(1 for e in published if e.get("pdf"))
    with_orcid = sum(1 for p in data["people"] if p.get("orcid"))
    lines = ["# Merge report (S4)", "",
             f"- entries: {len(entries)} ({len(published)} published, {len(entries) - len(published)} drafts)",
             f"- published entries with a PDF preview: {with_pdf}",
             f"- people: {len(data['people'])}, of which with ORCID: {with_orcid}",
             f"- places: {len(data['places'])}", "",
             "## Primary types (published entries)", "", "| Type | Entries |", "|---|---|"]
    for slug, count in sorted(types.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {slug} | {count} |")
    lines += ["", "## Notes", "", "| Kind | Count |", "|---|---|"]
    for kind, count in sorted(Counter(k for _, k, _ in notes).items()):
        lines.append(f"| `{kind}` | {count} |")
    lines += ["", "| Where | Kind | Detail |", "|---|---|---|"]
    for where, kind, text in sorted(notes, key=lambda n: (n[1], n[0])):
        lines.append(f"| `{where}` | `{kind}` | {text.replace('|', chr(92) + '|')} |")
    write_text(REPORT, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
