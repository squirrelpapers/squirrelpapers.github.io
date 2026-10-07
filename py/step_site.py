"""S5 - Render docs/ in English (/) and German (/de/) for GitHub Pages.

Reads data/derived/entries.json (S4), content/ui.yaml (interface strings) and
content/pages/*.html (legal pages), writes one folder per page:

    docs/index.html                     home
    docs/volumes/index.html             volumes and issues
    docs/v7/index.html                  volume
    docs/v7/i4/index.html               issue
    docs/v7/i4/e5/index.html            entry (drafts are not published)
    docs/impressum/, docs/privacy/      legal pages
    docs/de/...                         the same in German

Pages link to each other with relative paths, so docs/ works from disk
(`python main.py --open`) and under any host. Every page carries its canonical
URL; entry pages carry schema.org JSON-LD. Products of S6/S7/S10 that belong
on the web (BibTeX, Turtle, JSON-LD per entry, the dumps) are written by those
steps to data/derived/web/ in the docs/ layout; this step copies that tree
into docs/ and links what it finds.

The site step owns docs/: it writes changed files only and afterwards deletes
what it did not produce, except the paths in KEEP_IN_DOCS (S9 runs afterwards
and adds its page).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    ASSETS, CONTENT, DIST, DOCS, ENTRIES_JSON, LANGUAGES, SITE, copy_file, prune, read_json,
    read_yaml, rel, script_json, sha256_file, skipped, sync_tree, template_environment, tracking,
    warn,
    write_text,
)

UI_YAML = CONTENT / "ui.yaml"
PAGES_DIR = CONTENT / "pages"
ASSET_FILES = ["css/sqp.css", "img/sqp-logo.png", "img/network.svg", "js/sqp-cite.js",
               "js/sqp-preview.js", "js/sqp-search.js", "js/sqp-sparql.js", "js/sqp-map.js",
               "js/sqp-model.js"]
# Copied whole: pdf.js with its fonts (S8b), Pyodide with the rdflib wheels (S9),
# Leaflet and the Natural Earth background (S10), Mermaid (S16).
ASSET_DIRS = ["vendor/pdfjs", "vendor/pyodide", "vendor/leaflet", "vendor/naturalearth",
              "vendor/mermaid"]
MODEL_JSON = Path(__file__).resolve().parent.parent / "data" / "derived" / "model.json"  # S16
EVENTS_GEOJSON = DIST / "events.geojson"                                     # S10
QUERIES_JSON = Path(__file__).resolve().parent.parent / "data" / "derived" / "queries.json"  # S9
SPARQL_MAX_ROWS = 500   # rendered rows; an unlimited table can hang a phone
# Files in docs/ that other steps or people own; prune() leaves them alone.
# CNAME: a custom domain set on GitHub (S13). S9 adds its own entry here.
KEEP_IN_DOCS = ("CNAME",)
WEB = Path(__file__).resolve().parent.parent / "data" / "derived" / "web"   # S6/S7/S10 products
DOWNLOAD_FORMATS = (("bib", "BibTeX"), ("ris", "RIS"), ("csl.json", "CSL-JSON"),
                    ("ttl", "Turtle"), ("jsonld", "JSON-LD"), ("crm.ttl", "CIDOC CRM (Turtle)"))

SCHEMA_TYPES = {
    "journal-article": "ScholarlyArticle", "conference-paper": "ScholarlyArticle",
    "conference-proceeding": "ScholarlyArticle", "preprint": "ScholarlyArticle",
    "working-paper": "ScholarlyArticle", "methodological-working-paper": "ScholarlyArticle",
    "position-paper": "ScholarlyArticle", "abstract": "ScholarlyArticle",
    "presentation": "PresentationDigitalDocument", "poster": "CreativeWork",
    "data": "Dataset", "ontology": "Dataset", "software": "SoftwareSourceCode",
    "book": "Book", "book-section": "Chapter", "report": "Report",
    "image": "ImageObject", "video": "VideoObject",
}


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def make_formatters(t: dict, lang: str):
    months = t["months"]

    def fmt_date(iso: str) -> str:
        parts = str(iso).split("-")
        if len(parts) != 3:
            return str(iso)
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{d}. {months[m - 1]} {y}" if lang == "de" else f"{d} {months[m - 1]} {y}"

    def fmt_range(start: str, end: str | None) -> str:
        if not end or end == start:
            return fmt_date(start)
        (y1, m1, d1), (y2, m2, d2) = ([int(x) for x in s.split("-")] for s in (start, end))
        if (y1, m1) == (y2, m2):
            return (f"{d1}.–{d2}. {months[m1 - 1]} {y1}" if lang == "de"
                    else f"{d1}–{d2} {months[m1 - 1]} {y1}")
        return f"{fmt_date(start)} – {fmt_date(end)}"

    return fmt_date, fmt_range


def html_escape(text: str) -> str:
    import html

    return html.escape(str(text), quote=True)


def simple_citation(e: dict, journal: dict) -> str:
    """APA-like citation as HTML. S6 adds CSL styles; this one is the default
    that every entry page shows even without them."""
    def initials(given: str) -> str:
        parts = re.findall(r"[A-ZÄÖÜ][a-zäöüß]*\.?", given)
        return " ".join(p[0] + "." for p in parts)

    names = [f"{p['family']}, {initials(p['given'])}".strip(", ") for p in e.get("creators", [])]
    if len(names) > 1:
        authors = ", ".join(names[:-1]) + ", & " + names[-1]
    else:
        authors = names[0] if names else ""
    year = e.get("year") or "n.d."
    parts = [html_escape(authors), f"({year}).", f"{html_escape(e['title'])}.",
             f"<em>{html_escape(journal['title'])}</em>, {html_escape(e['citation_label'])}."]
    if e.get("doi"):
        parts.append(f'<a href="{e["doi_url"]}">{e["doi_url"]}</a>')
    else:
        parts.append(f'<a href="{e["iri"]}">{e["iri"]}</a>')
    return " ".join(p for p in parts if p)


def jsonld_for(e: dict, journal: dict, issue: dict, types: dict) -> str:
    primary = e["types"][0]
    data = {
        "@context": "https://schema.org",
        "@type": SCHEMA_TYPES.get(primary, "CreativeWork"),
        "@id": e["iri"],
        "name": e["title"],
        "url": SITE + e["path"] + "/",
        "author": [{"@type": "Person", "name": f"{p['given']} {p['family']}".strip(),
                    **({"@id": f"https://orcid.org/{p['orcid']}"} if p.get("orcid") else {})}
                   for p in e.get("creators", [])],
        "isPartOf": {
            "@type": "PublicationIssue", "@id": issue["iri"], "issueNumber": str(e["issue"]),
            "isPartOf": {
                "@type": "PublicationVolume", "@id": e["iri"].rsplit("/", 2)[0],
                "volumeNumber": str(e["volume"]),
                "isPartOf": {"@type": "Periodical", "@id": journal["iri"],
                             "name": journal["title"], "issn": journal["issn"]},
            },
        },
        "genre": types[primary]["label"]["en"],
    }
    if e.get("date"):
        data["datePublished"] = e["date"]
    elif e.get("year"):
        data["datePublished"] = str(e["year"])
    if e.get("doi"):
        data["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": e["doi"]}
        data["sameAs"] = [e["doi_url"]]
    if e.get("abstract"):
        data["abstract"] = e["abstract"][:2000]
    if e.get("keywords"):
        data["keywords"] = e["keywords"]
    if e.get("language"):
        data["inLanguage"] = e["language"]
    if e.get("licence", {}).get("url"):
        data["license"] = e["licence"]["url"]
    if e.get("event", {}).get("name"):
        ev = e["event"]
        event = {"@type": "Event", "name": ev["name"]}
        if ev.get("start"):
            event["startDate"] = ev["start"]
        if ev.get("end"):
            event["endDate"] = ev["end"]
        place = ev.get("place")
        if place:
            event["location"] = {"@type": "Place", "name": place.get("name", place["label"]),
                                 **({"sameAs": f"http://www.wikidata.org/entity/{place['wikidata']}"}
                                    if place.get("wikidata") else {})}
            if "lat" in place:
                event["location"]["geo"] = {"@type": "GeoCoordinates",
                                            "latitude": place["lat"], "longitude": place["lon"]}
        elif ev.get("online"):
            event["eventAttendanceMode"] = "https://schema.org/OnlineEventAttendanceMode"
        data["recordedAt"] = event
    return script_json(data)


# ---------------------------------------------------------------------------
# Link check
# ---------------------------------------------------------------------------


# href="..." and src="..." as Jinja writes them (always double quotes); not
# data-src or the like. A regex instead of html.parser: same links, a tenth of
# the time over 524 pages (S8b).
_LINK = re.compile(r'(?<![\w-])(?:href|src)="([^"]+)"')


def check_links(root: Path) -> list[str]:
    """Every relative href/src in docs/ must point to an existing file."""
    import html
    import posixpath

    files = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    folders = {posixpath.dirname(f) for f in files}
    broken = []
    for page in sorted(root.rglob("*.html")):
        here = posixpath.dirname(page.relative_to(root).as_posix())
        for link in _LINK.findall(page.read_text(encoding="utf-8")):
            link = html.unescape(link)
            parsed = urlparse(link)
            if parsed.scheme or link.startswith(("#", "mailto:", "//")):
                continue
            target = posixpath.normpath(posixpath.join(here, parsed.path)) if parsed.path else here
            if parsed.path.endswith("/") or target in folders or target == ".":
                target = posixpath.normpath(posixpath.join(target, "index.html"))
            if target.startswith("../") or target not in files:
                broken.append(f"{rel(page)} -> {link}")
    return broken


# ---------------------------------------------------------------------------


def map_view(events: dict) -> dict:
    """Counts and the event list for the map page (S10)."""
    features = []
    for f in events["features"]:
        anchor = "event-" + f["id"].rstrip("/").rsplit("/", 1)[-1]
        features.append({**f, "anchor": anchor})
    return {"features": features, "events": len(features),
            "places": len({f["properties"]["place"]["iri"] for f in features}),
            "entries": sum(len(f["properties"]["entries"]) for f in features),
            "years": sorted({(f["properties"]["start"] or "")[:4] for f in features
                             if f["properties"]["start"]}, reverse=True)}


def sparql_view(sparql: dict, lang: str) -> dict:
    """What the SPARQL template needs from data/derived/queries.json (S9)."""
    queries = []
    for q in sparql["queries"]:
        text = q["sparql"].rstrip("\n")
        queries.append({**q, "sparql": text, "rows": max(5, text.count("\n") + 2)})
    sep = "," if lang == "en" else "."
    return {**sparql, "queries": queries,
            "triples_fmt": f"{sparql['triples']:,}".replace(",", sep)}


def sparql_config(sparql: dict, t: dict, lang: str) -> str:
    """The page script's configuration. The page sits at /sparql/ or /de/sparql/,
    so the site root is one or two levels up."""
    ui = {key[len("sparql_"):]: value for key, value in t.items() if key.startswith("sparql_")}
    return script_json({
        "lang": lang, "root": "../" if lang == "en" else "../../",
        "prefixes": sparql["prefixes"], "graphs": [g["url"] for g in sparql["graphs"]],
        "wheels": sparql["wheels"], "max_rows": SPARQL_MAX_ROWS,
        "queries": {q["id"]: q["sparql"].rstrip("\n") for q in sparql["queries"]}, "ui": ui})


def render_site(data: dict, ui: dict, journal: dict, types: dict, entries: dict) -> tuple[int, list]:
    """Write every page and copy every file of docs/; returns pages and volumes."""
    write_text(DOCS / ".nojekyll", "")
    if WEB.exists():
        sync_tree(WEB, DOCS)

    def downloads_for(path: str, prefix: str = "index") -> list[dict]:
        # Looked up in web/, not docs/: docs/ may still hold a stale file that
        # prune() removes only after rendering.
        folder = WEB / path if path else WEB
        # Relative to the site root: the files exist once, the pages twice (EN, DE).
        return [{"href": (f"{path}/" if path else "") + f"{prefix}.{suffix}", "label": label}
                for suffix, label in DOWNLOAD_FORMATS if (folder / f"{prefix}.{suffix}").exists()]

    sparql = read_json(QUERIES_JSON) if QUERIES_JSON.exists() else None
    events = read_json(EVENTS_GEOJSON) if EVENTS_GEOJSON.exists() else None
    model = read_json(MODEL_JSON) if MODEL_JSON.exists() else None
    csl_items = {}
    for e in data["entries"]:
        path = WEB / e["path"] / "index.csl.json"
        if path.exists():
            csl_items[e["id"]] = read_json(path)[0]
    for asset in ASSET_FILES:
        copy_file(ASSETS / asset, DOCS / "assets" / asset)
    for folder in ASSET_DIRS:
        sync_tree(ASSETS / folder, DOCS / "assets" / folder)

    # volumes with resolved, published entries
    volumes = []
    for v in data["volumes"]:
        issues = []
        for issue in v["issues"]:
            items = [entries[i] for i in issue["entries"] if not entries[i].get("draft")]
            issues.append({**issue, "published": items})
        years = (v.get("coverage", "").replace("/", "–") if v.get("coverage")
                 else str(v.get("year", "")))
        volumes.append({**v, "issues": issues, "label_years": years,
                        "count": sum(len(i["published"]) for i in issues)})
    volumes.sort(key=lambda v: -v["volume"])
    latest = volumes[0] if volumes else None

    env = template_environment()
    editor = journal["editor"]["name"].split(", ")
    editor_name = f"{editor[1]} {editor[0]}" if len(editor) == 2 else journal["editor"]["name"]
    pages_written = 0

    versions: dict[str, str] = {}

    def version(relpath: str) -> str:
        """Short content hash for a stylesheet or script in docs/.

        Appended as ?v=... so a browser never pairs a new page with a cached
        old stylesheet: GitHub Pages lets browsers keep files for ten minutes,
        and the map page of S10 came up without its map that way."""
        if relpath not in versions:
            versions[relpath] = sha256_file(DOCS / relpath)[:10]
        return versions[relpath]

    def render(template: str, path: str, lang: str, **context) -> None:
        nonlocal pages_written
        depth = (path.count("/") + 1 if path else 0) + (1 if lang != "en" else 0)
        root = "../" * depth
        context.setdefault("asset", lambda relpath: f"{root}{relpath}?v={version(relpath)}")
        home = root + ("" if lang == "en" else f"{lang}/")
        other = "de" if lang == "en" else "en"
        other_home = root + ("" if other == "en" else f"{other}/")
        t = ui[lang]
        fmt_date, fmt_range = make_formatters(t, lang)
        prefix = "" if lang == "en" else f"{lang}/"
        # Machine-readable twins of the page (S7), announced in the <head>.
        folder = WEB / path if path else WEB
        context.setdefault("data_links", [
            {"type": mime, "href": root + (f"{path}/" if path else "") + f"index.{suffix}"}
            for suffix, mime in (("ttl", "text/turtle"), ("jsonld", "application/ld+json"))
            if (folder / f"index.{suffix}").exists()])
        html = env.get_template(template).render(
            lang=lang, t=t, root=root, home=home, journal=journal, types=types,
            editor_name=editor_name, other_lang=other,
            other_lang_href=other_home + (f"{path}/" if path else ""),
            canonical=SITE + prefix + (f"{path}/" if path else ""),
            alternates=[{"lang": lg, "url": SITE + ("" if lg == "en" else f"{lg}/")
                         + (f"{path}/" if path else "")} for lg in LANGUAGES],
            fmt_date=fmt_date, fmt_range=fmt_range,
            **{"jsonld": None, "description": None, **context})
        target = DOCS / prefix / path / "index.html" if path else DOCS / prefix / "index.html"
        write_text(target, html)
        pages_written += 1

    for lang in LANGUAGES:
        t = ui[lang]
        render("home.html.j2", "", lang, page_title=f"Squirrel Papers – {t['hero_claim']}",
               nav="home", volumes=volumes, latest=latest)
        render("volumes.html.j2", "volumes", lang, page_title=f"{t['nav_volumes']} – Squirrel Papers",
               nav="volumes", volumes=volumes,
               downloads=downloads_for("downloads", "squirrelpapers"))
        render("search.html.j2", "search", lang, page_title=f"{t['nav_search']} – Squirrel Papers",
               nav="search", search_ui=script_json({
                   # entry links relative to /search/ or /de/search/: one level up
                   # is the home of the page's own language
                   "lang": lang, "home": "../",
                   "facets": {f: t[f"facet_{f}"] for f in
                              ("type", "year", "volume", "event", "person", "language")},
                   "one": t["search_one"], "many": t["search_many"], "none": t["search_none"],
                   "more": t["search_show_more"], "fewer": t["search_show_fewer"]}))
        if model:
            render("model.html.j2", "model", lang, page_title=f"{t['nav_model']} – Squirrel Papers",
                   nav="model", model=model)
        if events:
            render("map.html.j2", "map", lang, page_title=f"{t['nav_map']} – Squirrel Papers",
                   nav="map", map=map_view(events), map_ui=script_json({"home": "../", "lang": lang}))
        if sparql:
            render("sparql.html.j2", "sparql", lang, page_title=f"SPARQL – Squirrel Papers",
                   nav="sparql", sparql=sparql_view(sparql, lang),
                   sparql_config=sparql_config(sparql, t, lang))
        for slug, nav, heading in (("impressum", "impressum", t["nav_impressum"]),
                                   ("privacy", "privacy", t["nav_privacy"])):
            body = (PAGES_DIR / f"{slug}.{lang}.html").read_text(encoding="utf-8")
            render("page.html.j2", slug, lang, page_title=f"{heading} – Squirrel Papers",
                   nav=nav, heading=heading, body=body)
        for v in volumes:
            render("volume.html.j2", v["path"], lang,
                   page_title=f"{t['volume']} {v['volume']} – Squirrel Papers", nav="volumes", v=v,
                   downloads=downloads_for(v["path"]))
            for issue in v["issues"]:
                render("issue.html.j2", issue["path"], lang,
                       page_title=f"{t['volume']} {v['volume']}, {t['issue']} {issue['issue']} – Squirrel Papers",
                       nav="volumes", v=v, issue=issue, downloads=downloads_for(issue["path"]))
                for e in issue["published"]:
                    downloads = downloads_for(e["path"])
                    render("entry.html.j2", e["path"], lang,
                           page_title=f"{e['title']} – Squirrel Papers {e['citation_label']}",
                           nav="volumes", v=v, issue=issue, e=e,
                           citation=simple_citation(e, journal), downloads=downloads,
                           csl_item=script_json(csl_items.get(e["id"], {})),
                           jsonld=jsonld_for(e, journal, issue, types))

    return pages_written, volumes


def main(strict: bool = False) -> None:
    if not ENTRIES_JSON.exists():
        skipped(f"{rel(ENTRIES_JSON)} missing (S4)")
        return
    data = read_json(ENTRIES_JSON)
    ui = read_yaml(UI_YAML)
    # Jinja looks up `t.copy` as the dict method before the key: a UI string
    # named like a dict method renders as "<built-in method ...>" (S5, found
    # on the first screenshot). Refuse such keys.
    clashes = sorted({k for lang in LANGUAGES for k in ui[lang] if hasattr(dict, k)})
    if clashes:
        raise KeyError(f"content/ui.yaml: keys clash with dict methods: {clashes}")
    journal = data["journal"]
    types = {t["slug"]: t for t in data["types"]}
    entries = {e["id"]: e for e in data["entries"]}

    # docs/ is no longer emptied first: unchanged pages stay untouched and
    # whatever this step did not produce is pruned afterwards (S8b).
    with tracking() as produced:
        pages_written, volumes = render_site(data, ui, journal, types, entries)
    removed = prune(DOCS, produced, lambda path: not path.startswith(KEEP_IN_DOCS))
    if removed:
        print(f"removed {len(removed)} stale files from {rel(DOCS)}/")

    broken = check_links(DOCS)
    published = sum(v["count"] for v in volumes)
    print(f"{pages_written} pages ({published} entries × {len(LANGUAGES)} languages) -> {rel(DOCS)}/")
    if broken:
        for b in broken[:20]:
            print(f"  broken link: {b}")
        warn(f"{len(broken)} broken internal links", strict)
    else:
        print("link check: no broken internal links")


if __name__ == "__main__":
    main(strict="--strict" in sys.argv)
