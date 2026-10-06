"""S3 - Fetch Zenodo records and Wikidata places into data/raw/.

The only step that reaches the network (PRIMER A3). It is not part of the
default run; start it on purpose:

    python main.py --only harvest

What it does, in this order:

1. Zenodo: one JSON per record under data/raw/zenodo/<record id>.json for every
   DOI in content/vol*.yaml (`doi` and `related_dois`). Records already in the
   cache are not fetched again unless SQP_REFRESH=1 is set. The volatile `stats`
   block (views, downloads) is dropped before writing, so a refresh changes the
   file only when the record itself changed.
2. Wikidata, places with a QID: labels, coordinates, country and type, reduced
   to data/raw/wikidata/<QID>.json (countries are fetched too, for their labels).
3. Wikidata, places without a QID: a search per place; the raw search answers
   go to data/raw/wikidata-search/<key>.json, the candidate items into
   data/raw/wikidata/. Nothing in content/ is changed - the proposal is
   written to dist/reports/places.proposed.yaml for review.
4. The report dist/reports/harvest.md, built from the cache alone
   (`python py/step_harvest.py --report` rebuilds it offline).

Settings (environment variables, all optional):

    SQP_REFRESH=1           fetch Zenodo records again even if cached
    SQP_ZENODO_API          default https://zenodo.org/api
    SQP_WIKIDATA_API        default https://www.wikidata.org/w/api.php
    SQP_ZENODO_DELAY        seconds between Zenodo requests, default 1.0
                            (guest limit is 60 requests per minute)
"""

from __future__ import annotations

import difflib
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqp_utils import (  # noqa: E402
    PLACES_YAML, RAW, RAW_WIKIDATA, RAW_ZENODO, REPORTS, read_json, read_yaml,
    rel, skipped, volume_yamls, write_json, write_text, zenodo_record_id,
)

ZENODO_API = os.environ.get("SQP_ZENODO_API", "https://zenodo.org/api").rstrip("/")
WIKIDATA_API = os.environ.get("SQP_WIKIDATA_API", "https://www.wikidata.org/w/api.php")
ZENODO_DELAY = float(os.environ.get("SQP_ZENODO_DELAY", "1.0"))
WIKIDATA_DELAY = 0.2
USER_AGENT = ("squirrelpapers-site-harvester/0.1 "
              "(+https://github.com/squirrelpapers/squirrelpapers.github.io)")

RAW_SEARCH = RAW / "wikidata-search"
ZENODO_STATUS = RAW_ZENODO / "_status.json"     # records that did not answer 200
REPORT = REPORTS / "harvest.md"
PROPOSAL = REPORTS / "places.proposed.yaml"

COUNTRY_WORDS = {
    "germany", "deutschland", "france", "italy", "spain", "spanien", "austria",
    "poland", "croatia", "ireland", "greece", "usa", "uk", "united kingdom",
    "england", "scotland", "netherlands", "norway",
}


# ---------------------------------------------------------------------------
# Inputs from content/
# ---------------------------------------------------------------------------


def content_entries():
    """(volume, issue, sigil, entry) for every entry in content/vol*.yaml."""
    for path in volume_yamls():
        doc = read_yaml(path)
        for issue in doc.get("issues", []):
            for entry in issue.get("entries", []):
                yield doc["volume"], issue["issue"], issue.get("sigil", "#"), entry


def wanted_records() -> dict[str, list[str]]:
    """Zenodo record id -> where it is used ('7(4) λ5', ...), sorted by id."""
    wanted: dict[str, list[str]] = {}
    for volume, issue, sigil, entry in content_entries():
        for doi in [entry.get("doi"), *entry.get("related_dois", [])]:
            if doi and "zenodo." in doi:
                wanted.setdefault(zenodo_record_id(doi), []).append(
                    f"{volume}({issue}) {sigil}{entry['n']}")
    return dict(sorted(wanted.items(), key=lambda kv: int(kv[0])))


def load_places() -> list[dict]:
    if not PLACES_YAML.exists():
        return []
    return read_yaml(PLACES_YAML).get("places", []) or []


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def session():
    import requests

    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    s.headers["Accept"] = "application/json"
    return s


def get_json(http, url: str, params: dict | None = None, tries: int = 4):
    """GET with polite retries on 429/5xx. Returns (status, json or None)."""
    for attempt in range(tries):
        try:
            response = http.get(url, params=params, timeout=30)
        except Exception as error:                 # network down, DNS, TLS ...
            if attempt == tries - 1:
                return f"error: {type(error).__name__}", None
            time.sleep(2 ** attempt)
            continue
        if response.status_code == 429 or response.status_code >= 500:
            wait = response.headers.get("Retry-After")
            time.sleep(float(wait) if wait and wait.isdigit() else 2 ** (attempt + 1))
            continue
        if response.status_code != 200:
            return response.status_code, None
        return 200, response.json()
    return "error: gave up after retries", None


# ---------------------------------------------------------------------------
# 1. Zenodo
# ---------------------------------------------------------------------------


def harvest_zenodo(http, wanted: dict[str, list[str]]) -> dict[str, str]:
    refresh = bool(os.environ.get("SQP_REFRESH"))
    status = read_json(ZENODO_STATUS) if ZENODO_STATUS.exists() else {}
    fetched = 0
    for number, record_id in enumerate(wanted, start=1):
        path = RAW_ZENODO / f"{record_id}.json"
        if path.exists() and not refresh:
            continue
        if record_id in status and not refresh:
            continue                         # known 404 etc.; SQP_REFRESH retries it
        code, data = get_json(http, f"{ZENODO_API}/records/{record_id}")
        fetched += 1
        if code == 200 and isinstance(data, dict):
            data.pop("stats", None)
            write_json(data, path)
            status.pop(record_id, None)
            print(f"  [{number}/{len(wanted)}] {record_id} ok")
        else:
            status[record_id] = str(code)
            print(f"  [{number}/{len(wanted)}] {record_id} -> {code}")
        time.sleep(ZENODO_DELAY)
    write_json(dict(sorted(status.items())), ZENODO_STATUS)
    print(f"zenodo: {fetched} requests, {len(wanted) - len(status)} of {len(wanted)} cached")
    return status


# ---------------------------------------------------------------------------
# 2./3. Wikidata
# ---------------------------------------------------------------------------


def reduce_entity(entity: dict) -> dict:
    """Keep what the site needs from a Wikidata item: labels, coordinates, country, type."""
    def claim_ids(prop):
        out = []
        for claim in entity.get("claims", {}).get(prop, []):
            value = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(value, dict) and "id" in value:
                out.append(value["id"])
        return sorted(set(out))

    reduced = {
        "id": entity["id"],
        "labels": {lang: v["value"] for lang, v in sorted(entity.get("labels", {}).items())
                   if lang in ("en", "de")},
        "descriptions": {lang: v["value"] for lang, v in
                         sorted(entity.get("descriptions", {}).items()) if lang in ("en", "de")},
        "country": claim_ids("P17"),
        "instance_of": claim_ids("P31"),
    }
    for claim in entity.get("claims", {}).get("P625", [])[:1]:
        value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        if "latitude" in value:
            reduced["coordinates"] = {"lat": round(value["latitude"], 6),
                                      "lon": round(value["longitude"], 6)}
    return reduced


def fetch_entities(http, qids: list[str]) -> list[str]:
    """wbgetentities in batches of 50 -> data/raw/wikidata/<QID>.json. Returns failures."""
    failed = []
    qids = sorted(set(qids))
    for start in range(0, len(qids), 50):
        batch = qids[start:start + 50]
        code, data = get_json(http, WIKIDATA_API, {
            "action": "wbgetentities", "ids": "|".join(batch), "format": "json",
            "props": "labels|descriptions|claims", "languages": "en|de",
        })
        if code != 200 or not data:
            failed += batch
            continue
        for qid, entity in data.get("entities", {}).items():
            if "missing" in entity:
                failed.append(qid)
                continue
            write_json(reduce_entity(entity), RAW_WIKIDATA / f"{qid}.json")
        time.sleep(WIKIDATA_DELAY)
    return failed


def search_terms(label: str) -> list[str]:
    """'Universidad de Barcelona, Spain' -> venue first, then the city.

    Parentheses become separate terms ('Technische Universität Hamburg (TUHH)'
    -> also 'TUHH'); a trailing country is dropped; the last remaining part is
    taken as the city.
    """
    terms = []
    acronyms = re.findall(r"\(([^()]+)\)", label)
    clean = re.sub(r"\s*\([^()]*\)", "", label).strip()
    parts = [p.strip() for p in re.split(r",|\s[–-]\s", clean) if p.strip()]
    while parts and parts[-1].lower() in COUNTRY_WORDS:
        parts.pop()
    # 'Mainz Germany' (comma missing) -> 'Mainz'
    parts = [re.sub(r"\s+(Germany|Deutschland)$", "", p) for p in parts]
    if parts:
        terms.append(parts[0])
        if len(parts) > 1:
            terms.append(parts[-1])
        elif len(parts[0].split()) > 3 and parts[0].split()[-1][:1].isupper():
            terms.append(parts[0].split()[-1])   # '... Mainz e.V. Mainz' -> 'Mainz'
    terms += acronyms
    seen, out = set(), []
    for term in terms:
        if term and term.lower() not in seen:
            seen.add(term.lower())
            out.append(term)
    return out


def search_places(http, places: list[dict]) -> list[str]:
    """Search Wikidata for every place without a QID. Returns candidate QIDs."""
    candidates = set()
    for place in places:
        if place.get("wikidata"):
            continue
        path = RAW_SEARCH / f"{place['key']}.json"
        if path.exists() and not os.environ.get("SQP_REFRESH"):
            answers = read_json(path)["answers"]
        else:
            answers = {}
            for term in search_terms(place["label"]):
                for lang in ("en", "de"):
                    code, data = get_json(http, WIKIDATA_API, {
                        "action": "wbsearchentities", "search": term, "language": lang,
                        "uselang": "en", "type": "item", "limit": 5, "format": "json",
                    })
                    hits = data.get("search", []) if code == 200 and data else []
                    answers[f"{term} [{lang}]"] = [
                        {"id": h["id"], "label": h.get("label", ""),
                         "description": h.get("description", "")} for h in hits]
                    time.sleep(WIKIDATA_DELAY)
            write_json({"label": place["label"], "answers": answers}, path)
        for hits in answers.values():
            candidates.update(h["id"] for h in hits[:3])
    return sorted(candidates)


# ---------------------------------------------------------------------------
# 4. Report - from the cache only
# ---------------------------------------------------------------------------


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def entity(qid: str) -> dict | None:
    path = RAW_WIKIDATA / f"{qid}.json"
    return read_json(path) if path.exists() else None


def rank_candidates(place: dict) -> list[dict]:
    """Candidates for one place, best first: term order, coordinates, label match."""
    path = RAW_SEARCH / f"{place['key']}.json"
    if not path.exists():
        return []
    answers = read_json(path)["answers"]
    scored: dict[str, float] = {}
    for rank_term, (term, hits) in enumerate(answers.items()):
        for rank_hit, hit in enumerate(hits[:3]):
            item = entity(hit["id"]) or {}
            score = 10 - rank_term - rank_hit * 0.5
            if item.get("coordinates"):
                score += 5
            label = item.get("labels", {}).get("en") or hit.get("label", "")
            score += 3 * difflib.SequenceMatcher(None, norm(label), norm(term.split(" [")[0])).ratio()
            scored[hit["id"]] = max(scored.get(hit["id"], -99), score)
    ordered = sorted(scored, key=lambda q: (-scored[q], int(q[1:])))
    out = []
    for qid in ordered[:3]:
        item = entity(qid) or {"id": qid}
        out.append({"id": qid,
                    "label": item.get("labels", {}).get("en") or item.get("labels", {}).get("de", ""),
                    "description": item.get("descriptions", {}).get("en", ""),
                    "coordinates": item.get("coordinates")})
    return out


def zenodo_title(record: dict) -> str:
    return record.get("metadata", {}).get("title") or record.get("title") or ""


def has_pdf(record: dict) -> bool:
    files = record.get("files") or []
    if isinstance(files, dict):                       # newer API shape: {"entries": {...}}
        files = list((files.get("entries") or {}).values())
    return any(str(f.get("key", "")).lower().endswith(".pdf") for f in files)


def write_report() -> None:
    wanted = wanted_records()
    status = read_json(ZENODO_STATUS) if ZENODO_STATUS.exists() else {}
    # Every entry that cites a record is checked, not just the first: two
    # entries sharing a DOI is exactly the case this check exists for.
    titles: dict[str, list[tuple[str, str]]] = {}
    for volume, issue, sigil, entry in content_entries():
        if entry.get("doi") and "zenodo." in entry["doi"]:
            titles.setdefault(zenodo_record_id(entry["doi"]), []).append(
                (f"{volume}({issue}) {sigil}{entry['n']}", entry["title"]))

    cached = [rid for rid in wanted if (RAW_ZENODO / f"{rid}.json").exists()]
    missing = [rid for rid in wanted if rid not in cached]
    no_pdf, other_id, mismatched = [], [], []
    for rid in cached:
        record = read_json(RAW_ZENODO / f"{rid}.json")
        if not has_pdf(record):
            no_pdf.append(rid)
        if str(record.get("id")) != rid:
            other_id.append((rid, record.get("id")))
        for used_in, mine in titles.get(rid, []):
            ratio = difflib.SequenceMatcher(None, norm(mine), norm(zenodo_title(record))).ratio()
            if ratio < 0.6:
                mismatched.append((rid, used_in, ratio, mine, zenodo_title(record)))

    places = load_places()
    with_qid = [p for p in places if p.get("wikidata")]
    qid_missing = [p for p in with_qid if not entity(p["wikidata"])]
    no_coords = [p for p in with_qid if entity(p["wikidata"]) and
                 not entity(p["wikidata"]).get("coordinates")]

    def cell(text) -> str:
        return str(text).replace("|", "\\|")

    lines = ["# Harvest report (S3)", "",
             "Built from the cache under `data/raw/` only; rebuild offline with "
             "`python py/step_harvest.py --report`.", "",
             "## Zenodo", "",
             f"- records referenced in content/: {len(wanted)}",
             f"- cached: {len(cached)}",
             f"- not available: {len(missing)}", ""]
    if missing:
        lines += ["| Record | Status | Used in |", "|---|---|---|"]
        for rid in missing:
            lines.append(f"| {rid} | {status.get(rid, 'not fetched yet')} | "
                         f"{', '.join(wanted[rid])} |")
        lines.append("")
    lines += ["### Title check", "",
              "Entries whose title in content/ differs clearly from the Zenodo title "
              "(similarity < 0.6) - the usual sign of a DOI copied from a neighbouring entry.", ""]
    if mismatched:
        lines += ["| Record | Used in | Similarity | content/ | Zenodo |", "|---|---|---|---|---|"]
        for rid, used_in, ratio, mine, theirs in mismatched:
            lines.append(f"| {rid} | {used_in} | {ratio:.2f} | "
                         f"{cell(mine)} | {cell(theirs)} |")
    else:
        lines.append("None.")
    lines += ["", "### Other observations", "",
              f"- records without a PDF file (no preview possible): {len(no_pdf)}"
              + (f" — {', '.join(no_pdf)}" if no_pdf else ""),
              f"- answered with a different record id (concept DOI -> latest version): "
              f"{len(other_id)}" + (" — " + ", ".join(f"{a} -> {b}" for a, b in other_id)
                                    if other_id else ""),
              "", "## Places", "",
              f"- places in `{rel(PLACES_YAML)}`: {len(places)}, with QID: {len(with_qid)}",
              f"- QID not found on Wikidata: {len(qid_missing)}"
              + (f" — {', '.join(p['key'] for p in qid_missing)}" if qid_missing else ""),
              f"- QID without coordinates: {len(no_coords)}"
              + (f" — {', '.join(p['key'] for p in no_coords)}" if no_coords else ""), ""]

    proposal = ["# Proposal from S3 - NOT the source of truth.",
                "# Review the `wikidata` values (first candidate) and the alternatives,",
                "# then copy this file over content/places.yaml.",
                "", "places:"]
    open_places = [p for p in places if not p.get("wikidata")]
    if open_places:
        lines += ["### Suggestions for places without a QID", "",
                  "| Place | Proposed | Alternatives |", "|---|---|---|"]
    for place in places:
        proposal.append(f"- key: {place['key']}")
        proposal.append(f"  label: {yaml_str(place['label'])}")
        if place.get("wikidata"):
            proposal.append(f"  wikidata: {place['wikidata']}")
        else:
            ranked = rank_candidates(place)
            if ranked:
                best = ranked[0]
                proposal.append(f"  wikidata: {best['id']}   # {describe(best)}")
                for alt in ranked[1:]:
                    proposal.append(f"  # alternative: {alt['id']}   {describe(alt)}")
                lines.append(f"| {cell(place['label'])} | {best['id']} {cell(describe(best))} | "
                             + "; ".join(f"{a['id']} {cell(describe(a))}" for a in ranked[1:])
                             + " |")
            else:
                proposal.append("  wikidata: null   # no candidate found")
                lines.append(f"| {cell(place['label'])} | – | – |")
        proposal.append(f"  entries: {place.get('entries', 0)}")
    write_text(REPORT, "\n".join(lines) + "\n")
    if places:
        write_text(PROPOSAL, "\n".join(proposal) + "\n")
    print(f"report: {rel(REPORT)}" + (f", proposal: {rel(PROPOSAL)}" if places else ""))


def yaml_str(text: str) -> str:
    import json

    return json.dumps(text, ensure_ascii=False)      # a JSON string is valid YAML


def describe(candidate: dict) -> str:
    text = candidate.get("label") or "?"
    if candidate.get("description"):
        text += f" - {candidate['description']}"
    if candidate.get("coordinates"):
        c = candidate["coordinates"]
        text += f" ({c['lat']:.3f}, {c['lon']:.3f})"
    return text


# ---------------------------------------------------------------------------


def main(strict: bool = False) -> None:
    wanted = wanted_records()
    if not wanted:
        skipped("no content/vol*.yaml with Zenodo DOIs yet (S2 first)")
        return

    http = session()
    print(f"zenodo: {len(wanted)} records referenced, API {ZENODO_API}")
    harvest_zenodo(http, wanted)

    places = load_places()
    qids = [p["wikidata"] for p in places if p.get("wikidata")]
    failed = fetch_entities(http, qids) if qids else []
    countries = sorted({c for q in qids if entity(q) for c in entity(q)["country"]})
    candidates = search_places(http, places)
    failed += fetch_entities(http, [q for q in countries + candidates
                                    if not (RAW_WIKIDATA / f"{q}.json").exists()])
    print(f"wikidata: {len(qids)} places with QID, {len(candidates)} candidates, "
          f"{len(failed)} failed")
    write_report()


if __name__ == "__main__":
    if "--report" in sys.argv:
        write_report()
    else:
        main(strict="--strict" in sys.argv)
