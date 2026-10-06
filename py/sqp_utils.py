"""Shared constants and helpers for the Squirrel Papers site.

Every step imports paths, the release date, the IRI builders and the canonical
writers from here. Two reasons: moving a directory stays a one-line change, and
the output stays deterministic because there is exactly one place that decides
how a file is written. Large parts are copied from fdo-squirrel-registry
(py/registry_utils.py), together with the reasoning behind them (PRIMER A3:
copied code carries its checks with it).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------

# The one date that may appear in generated output. Never datetime.now(): an
# artefact must change exactly when data or model changed, otherwise its diff
# is noise and nobody reads it any more (PRIMER A3).
RELEASE = "2026-10-06"

# ---------------------------------------------------------------------------
# The journal
# ---------------------------------------------------------------------------

JOURNAL_TITLE = "Squirrel Papers"
JOURNAL_ISSN = "2750-560X"
JOURNAL_WIKIDATA = "Q89658875"
PUBLISHER = "Research Squirrel Engineers Network"
EDITOR = {"name": "Thiery, Florian", "orcid": "0000-0002-3246-3531"}
LANGUAGES = ("en", "de")          # en is served at /, de at /de/ (PRIMER A4)

# ---------------------------------------------------------------------------
# Namespaces and IRIs (PRIMER A6)
# ---------------------------------------------------------------------------

BASE = "https://w3id.org/squirrelpapers/"
SITE = "https://squirrelpapers.github.io/"
ONTOLOGY_NS = BASE + "ontology#"
TYPE_NS = BASE + "type/"
PERSON_NS = BASE + "person/"
EVENT_NS = BASE + "event/"
JOURNAL_IRI = BASE

# Every prefix used in generated graphs is bound here, in one place, so that
# Turtle output reads the same in every file (see bind_remaining()).
PREFIXES = {
    "sqp": ONTOLOGY_NS,
    "sqpt": TYPE_NS,
    "bibo": "http://purl.org/ontology/bibo/",
    "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    "crmdig": "http://www.ics.forth.gr/isl/CRMdig/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dcatap": "http://data.europa.eu/r5r/",
    "dct": "http://purl.org/dc/terms/",
    "fabio": "http://purl.org/spar/fabio/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "lrmoo": "http://iflastandards.info/ns/lrm/lrmoo/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "prism": "http://prismstandard.org/namespaces/basic/2.0/",
    "prov": "http://www.w3.org/ns/prov#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "https://schema.org/",
    "sh": "http://www.w3.org/ns/shacl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "wd": "http://www.wikidata.org/entity/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def volume_path(volume: int) -> str:
    """'v7' - the path segment shared by IRI and site URL."""
    return f"v{int(volume)}"


def issue_path(volume: int, issue: int) -> str:
    return f"{volume_path(volume)}/i{int(issue)}"


def entry_path(volume: int, issue: int, entry: int) -> str:
    """'v7/i4/e5'. ASCII only: the sigil (λ, §, 𝒬, #) never enters an IRI."""
    return f"{issue_path(volume, issue)}/e{int(entry)}"


def volume_iri(volume: int) -> str:
    return BASE + volume_path(volume)


def issue_iri(volume: int, issue: int) -> str:
    return BASE + issue_path(volume, issue)


def entry_iri(volume: int, issue: int, entry: int) -> str:
    return BASE + entry_path(volume, issue, entry)


def page_url(path: str, lang: str = "en") -> str:
    """Site URL of a page. Pages are folders, so every URL ends in '/'."""
    prefix = "" if lang == "en" else f"{lang}/"
    path = path.strip("/")
    return SITE + prefix + (f"{path}/" if path else "")


def citation_label(volume: int, issue: int, sigil: str, entry: int) -> str:
    """'7(4), λ5' - the form used in BibTeX `pages` and in the citation box."""
    return f"{int(volume)}({int(issue)}), {sigil}{int(entry)}"


def slugify(text: str) -> str:
    """ASCII, lower case, hyphens - stable across runs and safe in an IRI."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-") or "unnamed"


def zenodo_record_id(doi: str) -> str:
    """'10.5281/zenodo.3345715', a DOI URL, or a bare '3345715' -> '3345715'."""
    doi = doi.strip()
    if doi.isdigit():
        return doi
    match = re.search(r"zenodo\.(\d+)", doi)
    if not match:
        raise ValueError(f"not a Zenodo DOI or record id: {doi}")
    return match.group(1)


def normalise_doi(value: str) -> str:
    """Any of 'https://doi.org/10.…', 'doi:10.…', 'DOI: 10.…' -> '10.…' (lower case).

    DOIs are case-insensitive; lower-casing them here is what lets the S2
    migration recognise the same record written two ways in two repositories.
    """
    value = value.strip()
    value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I)
    return value.lower()


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"               # the source of truth (PRIMER A3)
JOURNAL_YAML = CONTENT / "journal.yaml"
PLACES_YAML = CONTENT / "places.yaml"
VOCAB_DIR = CONTENT / "vocab"
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_VOLUMES_MD = RAW / "volumes-md"      # snapshot of squirrelpapers-volumes
RAW_PUB = RAW / "pub"                    # snapshot of florianthiery/pub
RAW_ZENODO = RAW / "zenodo"              # harvest cache, one JSON per record
RAW_WIKIDATA = RAW / "wikidata"          # harvest cache, one JSON per QID
RAW_SITE = RAW / "site"                  # saved pages of the old WordPress site
DERIVED = DATA / "derived"
ENTRIES_JSON = DERIVED / "entries.json"
DIST = ROOT / "dist"
REPORTS = DIST / "reports"
DOCS = ROOT / "docs"                     # GitHub Pages (generated)
ASSETS = ROOT / "assets"                 # CSS, images, vendored JS (sources)
TEMPLATES = ROOT / "py" / "templates"


def volume_yaml(volume: int) -> Path:
    return CONTENT / f"vol{int(volume)}.yaml"


def volume_yamls() -> list[Path]:
    """content/vol<N>.yaml, sorted by N (not by name: vol10 after vol9)."""
    found = [p for p in CONTENT.glob("vol*.yaml") if re.fullmatch(r"vol\d+", p.stem)]
    return sorted(found, key=lambda p: int(p.stem[3:]))


def ensure_dirs(*paths: Path) -> None:
    """Create generated directories on demand, so none sit empty in git."""
    for path in paths or (DERIVED, DIST, DOCS):
        path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Deterministic writers
# ---------------------------------------------------------------------------


def rel(path: Path) -> str:
    """Repository-relative path with forward slashes, for anything written to a file.

    `Path.relative_to()` gives backslashes on Windows, so a report naming its
    inputs would differ between two machines that built the same thing.
    """
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path):
    import yaml  # imported here so --list stays cheap

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> Path:
    """Write a generated text file with LF endings on every platform.

    `Path.write_text()` translates "\\n" to `os.linesep`, so the same generator
    would produce CRLF on Windows and LF elsewhere.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_json(data, path: Path) -> Path:
    """Sorted keys, real UTF-8, trailing newline - so diffs mean something."""
    text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
    return write_text(path, text + "\n")


def write_yaml(data, path: Path, header: str = "") -> Path:
    """YAML for files people edit by hand: keys in the order given, real UTF-8.

    Unlike JSON, key order is NOT sorted - content/*.yaml is read top to bottom
    by a person, and `title` before `creators` before `doi` is part of what
    makes it editable. Determinism comes from the caller building the dicts in
    a fixed order.
    """
    import yaml

    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=100)
    return write_text(path, (header.rstrip() + "\n\n" if header else "") + body)


def bind_prefixes(graph) -> None:
    for prefix, namespace in PREFIXES.items():
        graph.bind(prefix, namespace, override=True)


def bind_remaining(graph) -> list[str]:
    """Give every unbound namespace a prefix, assigned in a fixed order.

    rdflib invents ns1, ns2, ... in the order it meets namespaces, and that
    order comes out of a set - so one namespace is ns2 in one run and ns3 in
    the next. Binding them here, sorted by IRI, makes the label a function of
    the graph rather than of the process.
    """
    from rdflib import URIRef
    from rdflib.namespace import split_uri

    bound = {str(namespace) for _, namespace in graph.namespaces()}
    unbound = set()
    for triple in graph:
        for term in triple:
            if not isinstance(term, URIRef):
                continue
            try:
                namespace, _ = split_uri(str(term))
            except Exception:               # not splittable: written out in full
                continue
            if namespace not in bound:
                unbound.add(namespace)
    assigned = []
    for number, namespace in enumerate(sorted(unbound), start=1):
        graph.bind(f"ns{number:02d}", namespace)
        assigned.append(namespace)
    return assigned


def write_canonical_turtle(graph, path: Path, *, keep_nt: bool = True) -> Path:
    """Serialise a graph reproducibly: sorted N-Triples, Turtle made from those.

    Skolemise blank nodes before calling this - a blank node gets a fresh id on
    every parse and makes two otherwise identical runs differ.
    """
    from rdflib import Graph

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(
        line for line in graph.serialize(format="nt").splitlines() if line.strip()
    )
    nt_path = path.with_suffix(".nt")
    write_text(nt_path, "\n".join(lines) + "\n")

    canonical = Graph()
    bind_prefixes(canonical)
    for prefix, namespace in graph.namespaces():
        canonical.bind(prefix, namespace, override=False)
    canonical.parse(nt_path, format="nt")
    bind_remaining(canonical)
    write_text(path, canonical.serialize(format="turtle"))

    if not keep_nt:
        nt_path.unlink()
    return path


def script_json(value) -> str:
    """JSON to embed in a <script> block, marked `| safe` in the template.

    The HTML parser does not decode entities inside <script>, so autoescaped
    JSON breaks JSON.parse. Raw it must be - and raw means it must be unable to
    end the element, which the \\u00xx escapes below guarantee.
    """
    return (json.dumps(value, sort_keys=True, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026"))


def template_environment():
    """The Jinja environment every page generator uses. Escapes, and means it.

    Not `select_autoescape(["html"])`: it compares the end of the file name,
    templates here are `*.html.j2`, and `.j2` is not on its list - so nothing
    would be escaped (found the hard way in fdo-squirrel-registry, Befund 30).
    Deliberately raw output is marked `| safe` where it is written.
    """
    from jinja2 import Environment, FileSystemLoader

    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=True,
        keep_trailing_newline=True,
    )


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_fingerprint(*paths: Path) -> str:
    """Short hash over inputs and generator - provenance without a clock."""
    digest = hashlib.sha256()
    for path in sorted(paths, key=str):
        digest.update(rel(path).encode("utf-8"))
        digest.update(sha256_file(path).encode("ascii"))
    return digest.hexdigest()[:16]


def git_revision() -> str | None:
    """Short commit hash, or None outside a checkout. Never fails the build."""
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


# ---------------------------------------------------------------------------
# Step protocol
# ---------------------------------------------------------------------------


def skipped(reason: str) -> None:
    """Report a step that has nothing to do yet - neither fail nor pretend.

    Until the later steps exist, this is what makes `python main.py` a
    meaningful smoke test.
    """
    print(f"skipped (no input): {reason}")


def pending(step: str) -> None:
    """Report a step whose input is ready but whose code is not written yet.

    Raising here would stop the pipeline the moment an earlier step starts
    delivering, which is exactly when the smoke test becomes useful.
    """
    print(f"pending: input is ready; implemented in {step}")


class StrictError(RuntimeError):
    """Raised by warn() under --strict."""


def warn(message: str, strict: bool) -> None:
    """A warning that becomes an error under --strict (what CI runs)."""
    if strict:
        raise StrictError(message)
    print(f"WARNING: {message}")
