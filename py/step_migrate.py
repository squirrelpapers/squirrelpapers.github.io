"""S2 - Migrate the old Markdown volumes and florianthiery/pub into content/*.yaml.

One-off and NOT in the default run: it writes content/vol<N>.yaml and
content/places.yaml, which are edited by hand afterwards. Run it only with

    python main.py --only migrate            refuses if content/vol*.yaml exist
    set SQP_FORCE=1 && python main.py --only migrate    overwrites them

Inputs are the snapshots under data/raw/volumes-md/ and data/raw/pub/
(PRIMER A3: raw data unchanged, read-only). Output besides the YAML:
dist/reports/migration.md, the review list.

Rules (PRIMER Teil C, S2):
- Volumes 2-8 keep exactly the issue and entry structure they had.
- Volume 1 additionally receives the posters and talks from pub up to and
  including 2019, filed by year into the existing 'Conferences <year>' issues.
- Duplicates are found by DOI first, by identical normalised title second.
  A duplicate enriches the existing entry; it never becomes a second one.
- Nothing is dropped silently: entries without DOI or link are kept with
  `draft: true`, every irregularity is listed in the report.
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from migrate_parsers import (  # noqa: E402
    Notes, build_entry, parse_bibtex_md, parse_pub_md, parse_volume_md,
    parse_wikidata_md,
)
from sqp_utils import (  # noqa: E402
    PLACES_YAML, RAW_PUB, RAW_VOLUMES_MD, REPORTS, citation_label, entry_iri,
    read_yaml, rel, skipped, slugify, volume_yaml, volume_yamls, write_text,
    write_yaml,
)

REPORT = REPORTS / "migration.md"

# pub years -> the Vol 1 issue that already collects that year's conferences
# (docs/vol1/index.md: '2019:(1)2 => SI: Conferences 2019', '(1)3 ... 2014' ...).
VOL1_CONFERENCE_ISSUE = {2019: 2, 2014: 3, 2015: 4, 2016: 5, 2017: 6, 2018: 7}
PUB_TYPE = {"talk": "presentation", "poster": "poster"}

YAML_HEADER = """\
# Squirrel Papers - Volume {volume}
#
# Source of truth for this volume (PRIMER A3). Edit here, never in docs/.
# Migrated in S2 from squirrelpapers-volumes{extra}; see
# dist/reports/migration.md for what needed attention.
#
# Entry IRI: https://w3id.org/squirrelpapers/v<volume>/i<issue>/e<n>
# Citation:  <volume>(<issue>), <sigil><n>
# `types` are slugs of the old labels; S4 maps them onto the SKOS scheme.
# `creators` are written as they appeared; S4 aligns them with Zenodo/ORCID.
"""


def place_key(location: str, limit: int = 48) -> str:
    """Readable, bounded slug: cut at a hyphen, never inside a word."""
    key = slugify(location)
    if len(key) > limit:
        key = key[:limit].rsplit("-", 1)[0]
    return key


def similar(a: str, b: str, threshold: float = 0.6) -> bool:
    import difflib

    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio() >= threshold


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def load_sources() -> dict:
    meta = read_yaml(RAW_VOLUMES_MD / "SOURCE.yaml")
    volumes = sorted(int(p.parent.name[3:]) for p in RAW_VOLUMES_MD.glob("vol*/index.md"))
    return {"meta": meta, "volumes": volumes}


def ordered_entry(entry: dict) -> dict:
    """Fixed key order, so content/*.yaml reads the same after every migration."""
    order = ["n", "types", "title", "creators", "et_al", "doi", "related_dois",
             "language", "date", "version", "release_label", "event", "editors",
             "contributors", "container", "wikidata", "isbn", "links", "context",
             "notes", "legacy_citation", "draft", "from"]
    extra = sorted(set(entry) - set(order))
    if extra:
        raise KeyError(f"unexpected keys {extra} in entry {entry.get('title')!r}")
    out = {key: entry[key] for key in order if key in entry}
    if "event" in out:
        ev_order = ["name", "start", "end", "date_text", "session", "location",
                    "place", "online"]
        out["event"] = {k: out["event"][k] for k in ev_order if k in out["event"]}
    return out


def main(strict: bool = False) -> None:
    if not (RAW_VOLUMES_MD / "SOURCE.yaml").exists():
        skipped(f"{rel(RAW_VOLUMES_MD)}/SOURCE.yaml missing - no source snapshot")
        return
    if volume_yamls() and not os.environ.get("SQP_FORCE"):
        print("refusing: content/vol*.yaml exist and are edited by hand.")
        print("  To migrate again on purpose: set SQP_FORCE=1 (cmd: set SQP_FORCE=1)")
        return

    notes = Notes()
    sources = load_sources()
    vol_qids, issue_qids = parse_wikidata_md(
        (RAW_VOLUMES_MD / "wikidata" / "wikidata.md").read_text(encoding="utf-8"))
    bibtex = parse_bibtex_md(
        (RAW_VOLUMES_MD / "vol7" / "bibtex.md").read_text(encoding="utf-8"))

    # -- 1. parse every volume -------------------------------------------------
    volumes: dict[int, dict] = {}
    for v in sources["volumes"]:
        path = RAW_VOLUMES_MD / f"vol{v}" / "index.md"
        source = f"volumes-md/vol{v}/index.md"
        parsed = parse_volume_md(path.read_text(encoding="utf-8"), v, source, notes)
        for issue in parsed["issues"]:
            built = []
            for raw in issue["entries"]:
                entry = build_entry(raw, notes)
                entry["_sigil"] = raw["sigil"]
                entry["from"] = raw["where"]
                built.append(entry)
            issue["entries"] = built
        volumes[v] = parsed

    # -- 1b. a creator given only by ORCID gets the name used most for it ------
    orcid_names: dict[str, Counter] = defaultdict(Counter)
    for vol in volumes.values():
        for issue in vol["issues"]:
            for e in issue["entries"]:
                for person in e.get("creators", []):
                    if person.get("orcid") and person.get("name"):
                        orcid_names[person["orcid"]][person["name"]] += 1
    for vol in volumes.values():
        for issue in vol["issues"]:
            for e in issue["entries"]:
                for person in e.get("creators", []):
                    if "name" not in person and person["orcid"] in orcid_names:
                        name = orcid_names[person["orcid"]].most_common(1)[0][0]
                        person_ = {"name": name, "orcid": person.pop("orcid")}
                        person.update(person_)
                        notes.add(e["from"], "orcid-name-filled",
                                  f"{person_['orcid']} -> {name!r}")

    # -- 2. sigil per issue, numbering checks ---------------------------------
    for v, vol in volumes.items():
        previous = "#"
        for issue in vol["issues"]:
            where = f"vol{v} issue {issue['issue']}"
            sigils = Counter(e["_sigil"] for e in issue["entries"])
            if len(sigils) > 1:
                notes.add(where, "mixed-sigils", dict(sigils).__repr__())
            issue["sigil"] = sigils.most_common(1)[0][0] if sigils else previous
            previous = issue["sigil"]
            numbers = Counter(e["n"] for e in issue["entries"])
            for n, count in numbers.items():
                if count > 1:
                    notes.add(where, "duplicate-number", f"{issue['sigil']}{n} appears {count}x")
        issue_numbers = Counter(i["issue"] for i in vol["issues"])
        for n, count in issue_numbers.items():
            if count > 1:
                notes.add(f"vol{v}", "duplicate-issue", f"issue {n} appears {count}x")

    # -- 3. index by DOI and title ---------------------------------------------
    by_doi: dict[str, list[tuple[int, dict, dict]]] = defaultdict(list)
    by_title: dict[str, list[tuple[int, dict, dict]]] = defaultdict(list)
    for v, vol in volumes.items():
        for issue in vol["issues"]:
            for e in issue["entries"]:
                if e.get("doi"):
                    by_doi[e["doi"]].append((v, issue, e))
                by_title[norm_title(e["title"])].append((v, issue, e))
    for doi, hits in sorted(by_doi.items()):
        if len(hits) > 1:
            places = ", ".join(f"{v}({i['issue']}) {i['sigil']}{e['n']}" for v, i, e in hits)
            notes.add(doi, "doi-repeated", f"same DOI in {len(hits)} entries: {places}")
    old_dois = set(by_doi)

    # -- 4. bibtex.md (Vol 7): container data for proceedings -----------------
    for doi, bib in sorted(bibtex.items()):
        hits = by_doi.get(doi)
        if not hits:
            notes.add(doi, "bibtex-unmatched", "BibTeX block without matching entry")
            continue
        f = bib["fields"]
        container = {"bibtex_type": bib["type"]}
        if f.get("booktitle"):
            container["title"] = f["booktitle"]
        if f.get("editor"):
            container["editors"] = [{"name": n.strip()} for n in f["editor"].split(" and ")]
        if f.get("publisher"):
            container["publisher"] = f["publisher"]
        if f.get("address"):
            container["place"] = f["address"]
        for v, issue, e in hits:
            e["container"] = container
            expected = citation_label(v, issue["issue"], issue["sigil"], e["n"])
            pages = f.get("pages", "")
            if pages and pages != expected and not expected.endswith(pages):
                notes.add(doi, "bibtex-pages", f"pages={pages!r}, expected {expected!r}")
    editor_sets = Counter(
        f["fields"].get("editor") for f in bibtex.values() if f["fields"].get("editor"))
    if len(editor_sets) > 1:
        notes.add("volumes-md/vol7/bibtex.md", "bibtex-editors",
                  f"editor spellings differ: {dict(editor_sets)}")

    # -- 5. pub: talks and posters up to 2019 -> Vol 1 -------------------------
    pub_items = []
    for name, kind in (("talks.md", "talk"), ("poster.md", "poster")):
        text = (RAW_PUB / name).read_text(encoding="utf-8")
        pub_items += parse_pub_md(text, kind, f"pub/{name}", notes)

    vol1 = volumes[1]
    vol1_issues = {i["issue"]: i for i in vol1["issues"]}
    added = enriched = skipped_other = 0
    for item in sorted(pub_items, key=lambda x: (x["event"].get("start") or "", x["title"])):
        # A DOI match anywhere is the same record. A title match only counts
        # inside Vol 1: a 2018 talk and a 2022 preprint may share a title and
        # still be two works (found for 'Taming Ambiguity', Vol 4(4) #2).
        hits = by_doi.get(item["doi"] or "", [])
        if not hits:
            title_hits = by_title.get(norm_title(item["title"]), [])
            hits = [h for h in title_hits if h[0] == 1]
            for v, issue, e in title_hits:
                if v != 1:
                    notes.add(item["where"], "pub-title-elsewhere",
                              f"same title as Vol {v}({issue['issue']}) {issue['sigil']}{e['n']} "
                              f"({e.get('doi')}), different DOI {item['doi']}; added to Vol 1 anyway")
        # Same DOI but clearly another title: one of the two DOIs is a copy
        # error (pub cites 2540522 for a 2014 and a 2016 talk; Zenodo says it
        # is the 2016 one). Merging would swallow a work, so both stay as
        # separate entries and the case goes to the report (S3 finding).
        if hits and item["doi"] and not similar(item["title"], hits[0][2]["title"]):
            v, issue, e = hits[0]
            notes.add(item["where"], "doi-shared-different-title",
                      f"{item['doi']} is also used by {v}({issue['issue']}) {issue['sigil']}{e['n']} "
                      f"{e['title'][:50]!r}; kept as a separate entry")
            hits = []
        if hits:
            v, issue, e = hits[0]
            how = "DOI" if item["doi"] and e.get("doi") == item["doi"] else "title"
            if v != 1:
                skipped_other += 1
                notes.add(item["where"], "pub-elsewhere",
                          f"already in Vol {v}({issue['issue']}) by {how}; left there")
                continue
            enriched += 1
            if how == "title" and item["doi"] and item["doi"] != e.get("doi"):
                e.setdefault("related_dois", []).append(item["doi"])
                notes.add(item["where"], "pub-title-match",
                          f"same title as Vol 1({issue['issue']}) {issue['sigil']}{e['n']}, "
                          f"different DOI {item['doi']} vs {e.get('doi')}; kept as related_dois")
            e.setdefault("language", item["language"])
            ev = e.setdefault("event", {})
            for key, value in item["event"].items():
                ev.setdefault(key, value)
            if PUB_TYPE[item["kind"]] not in e["types"]:
                e["types"].append(PUB_TYPE[item["kind"]])
            continue

        target = VOL1_CONFERENCE_ISSUE.get(item["year"])
        if target is None or target not in vol1_issues:
            notes.add(item["where"], "pub-no-issue", f"no Vol 1 issue for {item['year']}")
            continue
        issue = vol1_issues[target]
        n = max((e["n"] for e in issue["entries"]), default=0) + 1
        entry = {"n": n, "types": [PUB_TYPE[item["kind"]]], "title": item["title"],
                 "creators": item["creators"], "language": item["language"],
                 "event": dict(item["event"]), "from": item["where"], "_sigil": issue["sigil"]}
        if item["doi"]:
            entry["doi"] = item["doi"]
            by_doi[item["doi"]].append((1, issue, entry))
        else:
            entry["draft"] = True
        by_title[norm_title(item["title"])].append((1, issue, entry))
        issue["entries"].append(entry)
        added += 1

    # -- 6. places -------------------------------------------------------------
    old_places = {}
    if PLACES_YAML.exists():                       # keep QIDs Flo already filled in
        for p in read_yaml(PLACES_YAML).get("places", []):
            old_places[p["key"]] = p
    place_count: Counter = Counter()
    place_label: dict[str, str] = {}
    for vol in volumes.values():
        for issue in vol["issues"]:
            for e in issue["entries"]:
                ev = e.get("event")
                if not ev or not ev.get("location") or ev.get("online"):
                    continue
                key = place_key(ev["location"])
                ev["place"] = key
                place_count[key] += 1
                place_label.setdefault(key, ev["location"])
    places = []
    for key in sorted(place_count):
        previous = old_places.get(key, {})
        places.append({"key": key, "label": place_label[key],
                       "wikidata": previous.get("wikidata"), "entries": place_count[key]})

    # -- 7. write --------------------------------------------------------------
    meta = sources["meta"]
    for v, vol in sorted(volumes.items()):
        issues_out = []
        for issue in sorted(vol["issues"], key=lambda i: i["issue"]):
            entries = [ordered_entry({k: x for k, x in e.items() if not k.startswith("_")})
                       for e in sorted(issue["entries"], key=lambda e: e["n"])]
            out = {"issue": issue["issue"], "sigil": issue["sigil"]}
            if issue["title"]:
                out["title"] = {"en": issue["title"]}
            out["special"] = bool(issue["title"])
            qid = issue_qids.get((v, issue["issue"]))
            if qid:
                out["wikidata"] = qid
            out["entries"] = entries
            issues_out.append(out)
        year = vol["year"] or (2019 if v == 1 else 2018 + v)
        doc = {"volume": v, "year": year}
        if v == 1:
            doc["coverage"] = "2014/2019"
        if vol_qids.get(v):
            doc["wikidata"] = vol_qids[v]
        doc["issues"] = issues_out
        extra = (f" @ {meta['commit'][:7]}"
                 + (f" and florianthiery/pub @ {read_yaml(RAW_PUB / 'SOURCE.yaml')['commit'][:7]}"
                    if v == 1 else ""))
        write_yaml(doc, volume_yaml(v), YAML_HEADER.format(volume=v, extra=extra))

    write_yaml({"places": places}, PLACES_YAML,
               "# Event places (PRIMER A1, Befund 7). Fill in `wikidata` by hand;\n"
               "# S3 fetches coordinates for every QID. Online events are not listed.\n"
               "# `key` is referenced from event.place in content/vol<N>.yaml.")

    # -- 8. check and report ---------------------------------------------------
    for v, vol in sorted(volumes.items()):
        for issue in vol["issues"]:
            if not issue["entries"]:
                notes.add(f"vol{v} issue {issue['issue']}", "empty-issue",
                          "no entries (TBD in the source, nothing from pub)")

    new_dois = set()
    totals = []
    for v, vol in sorted(volumes.items()):
        n_entries = sum(len(i["entries"]) for i in vol["issues"])
        n_draft = sum(1 for i in vol["issues"] for e in i["entries"] if e.get("draft"))
        n_doi = len({e["doi"] for i in vol["issues"] for e in i["entries"] if e.get("doi")})
        totals.append((v, len(vol["issues"]), n_entries, n_draft, n_doi))
        for i in vol["issues"]:
            for e in i["entries"]:
                if e.get("doi"):
                    new_dois.add(e["doi"])
                new_dois.update(e.get("related_dois", []))
    # Independent of the parser: every Zenodo DOI written anywhere in the old
    # volumes, found by a plain regex. A parser bug cannot hide a loss here.
    raw_dois = set()
    for path in sorted(RAW_VOLUMES_MD.glob("vol*/index.md")):
        text = path.read_text(encoding="utf-8").replace("zenodo..", "zenodo.")
        raw_dois.update(f"10.5281/zenodo.{n}" for n in re.findall(r"10\.5281/zenodo\.(\d+)", text))
    lost = sorted(raw_dois - new_dois - notes.rejected_dois)

    lines = ["# Migration report (S2)", "",
             f"Source: squirrelpapers-volumes @ `{meta['commit']}` ({meta['date']}), "
             f"florianthiery/pub @ `{read_yaml(RAW_PUB / 'SOURCE.yaml')['commit']}`.", "",
             "## Volumes", "",
             "| Volume | Issues | Entries | of which draft | distinct DOIs |",
             "|---|---|---|---|---|"]
    for v, ni, ne, nd, nk in totals:
        lines.append(f"| {v} | {ni} | {ne} | {nd} | {nk} |")
    lines.append(f"| **all** | {sum(t[1] for t in totals)} | {sum(t[2] for t in totals)} | "
                 f"{sum(t[3] for t in totals)} | {len(new_dois)} |")
    lines += ["", "## Volume 1 from florianthiery/pub", "",
              f"- items read (talks + posters, up to 2019): {len(pub_items)}",
              f"- added as new entries: {added}",
              f"- merged into an existing Vol 1 entry: {enriched}",
              f"- already in a later volume, left there: {skipped_other}", "",
              "## DOI check", "",
              f"- Zenodo DOIs written anywhere in the old volumes (plain regex): {len(raw_dois)}",
              f"- DOIs read by the parser from the old volumes: {len(old_dois)}",
              f"- DOIs in content/ (incl. related_dois and pub): {len(new_dois)}",
              f"- set aside on purpose (link target disagreed with link text): "
              f"{', '.join(sorted(notes.rejected_dois)) or 'none'}",
              f"- **lost: {len(lost)}**" + (f" — {', '.join(lost)}" if lost else ""), "",
              "## Places", "",
              f"{len(places)} distinct non-online locations written to `{rel(PLACES_YAML)}`; "
              f"{sum(1 for p in places if p['wikidata'])} with a QID.", "",
              "## Review list", "",
              "| Kind | Count |", "|---|---|"]
    for kind, count in sorted(notes.by_kind().items()):
        lines.append(f"| `{kind}` | {count} |")
    lines += ["", "| Where | Kind | Detail |", "|---|---|---|"]
    for where, kind, text in sorted(notes.items, key=lambda x: (x[1], x[0])):
        detail = str(text).replace("|", "\\|")
        lines.append(f"| `{where}` | `{kind}` | {detail} |")
    write_text(REPORT, "\n".join(lines) + "\n")

    print(f"wrote {len(volumes)} volumes to content/, {len(places)} places")
    print(f"pub: {len(pub_items)} read, {added} added, {enriched} merged, "
          f"{skipped_other} elsewhere")
    print(f"DOIs in old volumes {len(raw_dois)}, in content/ {len(new_dois)}, "
          f"set aside {len(notes.rejected_dois)}, lost {len(lost)}")
    print(f"{len(notes.items)} review notes -> {rel(REPORT)}")
    if lost:
        raise RuntimeError(f"{len(lost)} DOIs from the old volumes are missing: {lost}")
    print(f"example IRI: {entry_iri(7, 4, 5)}")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
