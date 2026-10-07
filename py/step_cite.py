"""S6 - CSL-JSON, BibTeX and RIS for every entry, issue and volume.

Reads data/derived/entries.json (S4). Writes

    dist/squirrelpapers.bib / .ris / .csl.json      the whole journal (citable products)
    data/derived/web/<v>/<i>/<e>/index.bib|.ris|.csl.json   per entry
    data/derived/web/<v>/<i>/index.bib|.ris                per issue
    data/derived/web/<v>/index.bib|.ris                    per volume
    data/derived/web/downloads/squirrelpapers.*            copy of the dist/ files
    data/derived/web/assets/js/citeproc.js                 citeproc-js, wrapped for the browser
    data/derived/web/assets/js/sqp-csl-data.js             the six styles and three locales

data/derived/web/ has the layout of docs/; the site step (S5) copies it in.
Drafts get no files.

Citation form (PRIMER A4): every entry is cited as an article in the Squirrel
Papers, "Squirrel Papers, 7(4), λ5" - volume, issue, and the sigil plus number
as the page. Entries with a `container` (the CoRDI proceedings, 7(5)) are cited
as conference papers in that book, with the label as page, as in the
hand-written vol7/bibtex.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    ASSETS, DERIVED, DIST, ENTRIES_JSON, prune, read_json, rel, skipped, tracking,
    write_json, write_text,
)

CITE_SUFFIXES = (".bib", ".ris", ".csl.json")     # what prune() may delete in web/

WEB = DERIVED / "web"
VENDOR = ASSETS / "vendor"

STYLES = {   # key -> (file, label) - order is the order of the drop-down
    "apa": ("apa.csl", "APA 7"),
    "chicago": ("chicago-author-date.csl", "Chicago (author-date)"),
    "harvard": ("harvard-cite-them-right.csl", "Harvard"),
    "ieee": ("ieee.csl", "IEEE"),
    "mla": ("modern-language-association.csl", "MLA 9"),
    "vancouver": ("nlm-citation-sequence.csl", "Vancouver"),
}
LOCALES = ["en-GB", "en-US", "de-DE"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
RIS_TYPES = {"conference-proceeding": "CPAPER", "data": "DATA", "ontology": "DATA",
             "software": "COMP"}


# ---------------------------------------------------------------------------
# Shared pieces
# ---------------------------------------------------------------------------


def date_parts(e: dict) -> list[int]:
    if e.get("date"):
        return [int(x) for x in str(e["date"]).split("-")]
    return [int(e["year"])] if e.get("year") else []


def proceedings(e: dict) -> dict | None:
    """The container of a proceedings paper, or None.

    content/ carries a `container` for every entry that had a block in
    vol7/bibtex.md - including 7(4) λ5, whose block is an @article. Only an
    @inproceedings block makes a conference paper (found when λ5 came out as
    @inproceedings with the journal as its book title, S6)."""
    container = e.get("container")
    return container if container and container.get("bibtex_type") == "inproceedings" else None


def page_of(e: dict) -> str:
    """'λ5' in a journal citation; the full label in a proceedings citation."""
    return e["citation_label"] if proceedings(e) else f"{e['sigil']}{e['n']}"


def bibkey(e: dict) -> str:
    return f"sp_vol{e['volume']}_iss{e['issue']}_e{e['n']}"


def type_label(e: dict, types: dict) -> str:
    return types[e["types"][0]]["label"]["en"]


# ---------------------------------------------------------------------------
# CSL-JSON
# ---------------------------------------------------------------------------


def csl_name(p: dict) -> dict:
    if p.get("given"):
        return {"family": p["family"], "given": p["given"]}
    return {"literal": p["family"]}


def csl_item(e: dict, journal: dict, types: dict) -> dict:
    item = {
        "id": e["id"],
        "type": "article-journal",
        "title": e["title"],
        "author": [csl_name(p) for p in e.get("creators", [])],
        "container-title": journal["title"],
        "ISSN": journal["issn"],
        "volume": str(e["volume"]),
        "issue": str(e["issue"]),
        "page": page_of(e),
        "genre": type_label(e, types),
    }
    parts = date_parts(e)
    if parts:
        item["issued"] = {"date-parts": [parts]}
    if e.get("doi"):
        item["DOI"] = e["doi"]
    else:
        item["URL"] = e["iri"]
    if e.get("language"):
        item["language"] = e["language"]
    if e.get("keywords"):
        item["keyword"] = ", ".join(e["keywords"])
    ev = e.get("event") or {}
    if ev.get("name"):
        item["event-title"] = ev["name"]
        item["event"] = ev["name"]           # older CSL processors read this one
        if ev.get("location") and not ev.get("online"):
            item["event-place"] = ev["location"]
    container = proceedings(e)
    if container:
        # The full label '7(5), 𝒬1' is the page; volume and issue would make
        # the styles print 'Vol. 7, No. 5' a second time, and a collection
        # title would repeat the publisher (both seen in the S6 browser test).
        item["type"] = "paper-conference"
        item["container-title"] = container.get("title", journal["title"])
        for key in ("volume", "issue"):
            item.pop(key)
        if container.get("editors"):
            item["editor"] = [csl_name(dict(zip(("family", "given"),
                                                [x.strip() for x in ed["name"].split(",", 1)] + [""])))
                              for ed in container["editors"]]
        if container.get("publisher"):
            item["publisher"] = container["publisher"]
        if container.get("place"):
            item["publisher-place"] = container["place"]
    if e.get("editors"):
        item["editor"] = [csl_name(p) for p in e["editors"]]
    return item


# ---------------------------------------------------------------------------
# BibTeX
# ---------------------------------------------------------------------------

LATEX = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%",
         "$": r"\$", "#": r"\#", "_": r"\_", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex(text: str) -> str:
    """Escape LaTeX specials; Unicode stays (biber / XeLaTeX / LuaLaTeX read it)."""
    return "".join(LATEX.get(ch, ch) for ch in re.sub(r"\s+", " ", str(text)).strip())


def bib_people(people: list[dict]) -> str:
    return " and ".join(f"{tex(p['family'])}, {tex(p['given'])}" if p.get("given")
                        else "{" + tex(p["family"]) + "}" for p in people)


def bibtex(e: dict, journal: dict, types: dict) -> str:
    fields: list[tuple[str, str]] = [("title", tex(e["title"]))]
    if e.get("creators"):
        fields.append(("author", bib_people(e["creators"])))
    container = proceedings(e)
    if container:
        kind = "inproceedings"
        fields.append(("booktitle", tex(container.get("title", journal["title"]))))
        if container.get("editors"):
            fields.append(("editor", " and ".join(tex(ed["name"]) for ed in container["editors"])))
        fields.append(("publisher", tex(container.get("publisher", journal["title"]))))
        if container.get("place"):
            fields.append(("address", tex(container["place"])))
        fields.append(("series", tex(journal["title"])))
    else:
        kind = "article"
        fields.append(("journal", tex(journal["title"])))
    fields += [("volume", str(e["volume"])), ("number", str(e["issue"])),
               ("pages", tex(page_of(e)))]
    parts = date_parts(e)
    if parts:
        fields.append(("year", str(parts[0])))
    if len(parts) > 1:
        fields.append(("month", MONTHS[parts[1] - 1]))          # bare macro, no braces
    fields.append(("issn", journal["issn"]))
    if e.get("doi"):
        fields.append(("doi", tex(e["doi"])))
    fields.append(("url", e.get("doi_url") or e["iri"]))
    if e.get("language"):
        fields.append(("language", {"en": "english", "de": "german"}.get(e["language"], e["language"])))
    if e.get("keywords"):
        fields.append(("keywords", tex(", ".join(e["keywords"]))))
    note = type_label(e, types)
    ev = e.get("event") or {}
    if ev.get("name"):
        note += f", {ev['name']}"
        if ev.get("location") and not ev.get("online"):
            note += f", {ev['location']}"
    fields.append(("note", tex(note)))
    body = ",\n".join(f"  {name} = {value}" if name == "month" else f"  {name} = {{{value}}}"
                      for name, value in fields)
    return f"@{kind}{{{bibkey(e)},\n{body}\n}}\n"


# ---------------------------------------------------------------------------
# RIS
# ---------------------------------------------------------------------------


def ris(e: dict, journal: dict, types: dict) -> str:
    container = proceedings(e)
    kind = "CPAPER" if container else RIS_TYPES.get(e["types"][0], "JOUR")
    lines = [("TY", kind), ("ID", bibkey(e)), ("TI", e["title"])]
    lines += [("AU", f"{p['family']}, {p['given']}" if p.get("given") else p["family"])
              for p in e.get("creators", [])]
    parts = date_parts(e)
    if parts:
        lines.append(("PY", str(parts[0])))
        lines.append(("DA", "/".join(f"{x:02d}" if i else str(x) for i, x in enumerate(parts))))
    if container:
        lines.append(("T2", container.get("title", journal["title"])))
        lines += [("A2", ed["name"]) for ed in container.get("editors", [])]
        lines.append(("PB", container.get("publisher", journal["title"])))
        if container.get("place"):
            lines.append(("CY", container["place"]))
        lines.append(("T3", journal["title"]))
    else:
        lines.append(("JO", journal["title"]))
    lines += [("VL", str(e["volume"])), ("IS", str(e["issue"])), ("SP", page_of(e)),
              ("SN", journal["issn"])]
    if e.get("doi"):
        lines.append(("DO", e["doi"]))
    lines.append(("UR", e.get("doi_url") or e["iri"]))
    if e.get("language"):
        lines.append(("LA", e["language"]))
    lines += [("KW", k) for k in e.get("keywords", [])]
    lines.append(("N1", type_label(e, types)))
    lines.append(("ER", ""))
    return "\n".join(f"{tag}  - {value}".rstrip() for tag, value in lines) + "\n"


# ---------------------------------------------------------------------------
# Browser bundle
# ---------------------------------------------------------------------------


def write_browser_files() -> None:
    js = WEB / "assets" / "js"
    source = (VENDOR / "citeproc" / "citeproc_commonjs.js").read_text(encoding="utf-8")
    # The npm build ends in `module.exports = CSL`; give it a private module
    # object and expose CSL, so nothing else lands in the global scope.
    write_text(js / "citeproc.js",
               "/* citeproc-js 2.4.63, CPAL-1.0 OR AGPL-1.0 - see assets/vendor/citeproc/LICENSE\n"
               " * in https://github.com/squirrelpapers/squirrelpapers.github.io */\n"
               "(function () {\nvar module = { exports: {} };\n"
               + source + "\n;window.CSL = module.exports;\n}());\n")
    data = {
        "styles": {key: (VENDOR / "csl" / "styles" / f).read_text(encoding="utf-8")
                   for key, (f, _) in STYLES.items()},
        "labels": {key: label for key, (_, label) in STYLES.items()},
        "order": list(STYLES),
        "locales": {loc: (VENDOR / "csl" / "locales" / f"locales-{loc}.xml").read_text(encoding="utf-8")
                    for loc in LOCALES},
    }
    write_text(js / "sqp-csl-data.js",
               "/* CSL styles and locales, CC BY-SA 3.0, citation-style-language.github.io */\n"
               "window.SQP_CSL = " + json.dumps(data, sort_keys=True, ensure_ascii=False) + ";\n")


# ---------------------------------------------------------------------------


def main(strict: bool = False) -> None:
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    data = read_json(ENTRIES_JSON)
    journal = data["journal"]
    types = {t["slug"]: t for t in data["types"]}
    entries = {e["id"]: e for e in data["entries"]}

    # No emptying of data/derived/web/: rdf and validate write there too, and
    # unchanged files stay untouched (S8b). What this step no longer produces
    # is pruned at the end - its own kinds of file only.
    with tracking() as produced:
        build(data, journal, types, entries)
    removed = prune(WEB, produced, lambda path: path.endswith(CITE_SUFFIXES)
                    or path in ("assets/js/citeproc.js", "assets/js/sqp-csl-data.js"))
    if removed:
        print(f"removed {len(removed)} stale files from {rel(WEB)}/")


def build(data: dict, journal: dict, types: dict, entries: dict) -> None:
    all_bib, all_ris, all_csl = [], [], []
    for volume in data["volumes"]:
        vol_bib, vol_ris = [], []
        for issue in volume["issues"]:
            iss_bib, iss_ris = [], []
            for entry_id in issue["entries"]:
                e = entries[entry_id]
                if e.get("draft"):
                    continue
                b, r, c = bibtex(e, journal, types), ris(e, journal, types), csl_item(e, journal, types)
                folder = WEB / e["path"]
                write_text(folder / "index.bib", b)
                write_text(folder / "index.ris", r)
                write_json([c], folder / "index.csl.json")
                iss_bib.append(b)
                iss_ris.append(r)
                all_csl.append(c)
            if iss_bib:
                write_text(WEB / issue["path"] / "index.bib", "\n".join(iss_bib))
                write_text(WEB / issue["path"] / "index.ris", "\n".join(iss_ris))
            vol_bib += iss_bib
            vol_ris += iss_ris
        if vol_bib:
            write_text(WEB / volume["path"] / "index.bib", "\n".join(vol_bib))
            write_text(WEB / volume["path"] / "index.ris", "\n".join(vol_ris))
        all_bib += vol_bib
        all_ris += vol_ris

    header = ("% Squirrel Papers (ISSN 2750-560X) - all published entries.\n"
              "% Generated from https://github.com/squirrelpapers/squirrelpapers.github.io\n"
              "% Metadata: CC BY 4.0. Each work carries its own licence.\n\n")
    for target_dir in (DIST, WEB / "downloads"):
        write_text(target_dir / "squirrelpapers.bib", header + "\n".join(all_bib))
        write_text(target_dir / "squirrelpapers.ris", "\n".join(all_ris))
        write_json(all_csl, target_dir / "squirrelpapers.csl.json")
    write_browser_files()

    print(f"{len(all_csl)} entries: BibTeX, RIS, CSL-JSON -> {rel(WEB)}/ and {rel(DIST)}/squirrelpapers.*")
    print(f"browser: {len(STYLES)} styles ({', '.join(label for _, label in STYLES.values())}), "
          f"{len(LOCALES)} locales")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
