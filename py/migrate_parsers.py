"""S2 - parsers for the legacy sources. Pure functions, no file writing.

Three Markdown dialects live side by side in squirrelpapers-volumes (PRIMER A1,
Befund 2), plus the one-line-per-item format of florianthiery/pub (Befund 6).
Everything here turns text into plain dicts; step_migrate.py decides where
they go. Every irregularity is reported through a `Notes` object instead of
being fixed silently - the report is what Flo reviews.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from sqp_utils import normalise_doi, slugify

# ---------------------------------------------------------------------------
# Notes - the review list
# ---------------------------------------------------------------------------


@dataclass
class Notes:
    items: list[tuple[str, str, str]] = field(default_factory=list)
    rejected_dois: set[str] = field(default_factory=set)   # lost on purpose, reported

    def add(self, where: str, kind: str, text: str) -> None:
        item = (where, kind, str(text))
        if item not in self.items:            # one finding, one line
            self.items.append(item)

    def by_kind(self) -> Counter:
        return Counter(kind for _, kind, _ in self.items)


# ---------------------------------------------------------------------------
# Small value parsers
# ---------------------------------------------------------------------------

SIGILS = ("#", "λ", "§", "𝒬")

ORCID_LINK = re.compile(
    r"\[!\[ORCID ID\]\([^)]*\)\]\((?:https?://)?orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\)"
)
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]*)\)")
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\]\)\[\"<>]+")
QID_RE = re.compile(r"\bQ\d+\b")

MONTHS = {
    "jan": 1, "january": 1, "januar": 1, "jänner": 1,
    "feb": 2, "february": 2, "februar": 2,
    "mar": 3, "march": 3, "märz": 3, "maerz": 3,
    "apr": 4, "april": 4,
    "may": 5, "mai": 5,
    "jun": 6, "june": 6, "juni": 6,
    "jul": 7, "july": 7, "juli": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "okt": 10, "oktober": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12, "dez": 12, "dezember": 12,
}
ONLINE_WORDS = ("online", "virtual", "virtuell")


def strip_md(text: str) -> str:
    """Drop emphasis and backticks, keep link text, collapse whitespace."""
    text = MD_LINK.sub(lambda m: m.group(1), text)
    text = text.replace("**", "").replace("`", "").replace("<br>", " ")
    return re.sub(r"\s+", " ", text).strip()


def first_href(text: str) -> str | None:
    match = MD_LINK.search(text)
    if match:
        return match.group(2)
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip(").,") if match else None


def extract_doi(text: str, where: str, notes: Notes) -> str | None:
    """The DOI in a field value; reports typos, placeholders and text/link mismatches."""
    if "zenodo.." in text:
        notes.add(where, "doi-typo", f"double dot repaired in {text.strip()!r}")
        text = text.replace("zenodo..", "zenodo.")
    text = text.replace("\t", "")
    found = []
    for raw in DOI_RE.findall(text):
        doi = normalise_doi(raw.rstrip(".,;"))
        if doi.startswith("10.5281/zenodo.") and not doi.split(".")[-1].isdigit():
            notes.add(where, "doi-placeholder", f"not a DOI: {doi}")
            continue
        if doi not in found:
            found.append(doi)
    if not found:
        return None
    if len(found) > 1:
        # Markdown link whose visible text and target disagree. The visible
        # text wins: in the one case checked by hand (Vol 7(3) λ4) the target
        # was copied from the entry above and the text was right. S3 confirms
        # against Zenodo; the case stays in the report until then.
        link = MD_LINK.search(text)
        shown = normalise_doi(link.group(1)) if link else ""
        chosen = next((d for d in found if d == shown), found[0])
        notes.rejected_dois.update(d for d in found if d != chosen)
        notes.add(where, "doi-mismatch", f"link text and target differ: {found}; kept {chosen}")
        return chosen
    return found[0]


def parse_date(text: str) -> tuple[str | None, str | None]:
    """Event dates in the forms seen in the sources -> (start, end) ISO dates.

    '05-08 September 2018', '2.-8. July 2023', '14 June 2024', '23 Jan 2025',
    '11st December 2019', '31st März 2015', '01.01.2024',
    '30 May - 2 June 2024'. Anything else -> (None, None); the caller keeps the
    original text, so nothing is lost.
    """
    t = text.strip().lower().replace("–", "-").replace("—", "-")
    t = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", t)
    t = re.sub(r"\s+", " ", t)

    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", t)
    if m:
        iso = f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}"
        return iso, iso

    month = r"([a-zä]+)\.?"
    m = re.fullmatch(rf"(\d{{1,2}})\.?\s*{month}\s*(\d{{4}})\s*-\s*(\d{{1,2}})\.?\s*{month}\s*(\d{{4}})", t)
    if m and m[2] in MONTHS and m[5] in MONTHS:
        return (f"{m[3]}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}",
                f"{m[6]}-{MONTHS[m[5]]:02d}-{int(m[4]):02d}")
    m = re.fullmatch(rf"(\d{{1,2}})\.?\s*{month}\s*-\s*(\d{{1,2}})\.?\s*{month}\s*(\d{{4}})", t)
    if m and m[2] in MONTHS and m[4] in MONTHS:
        y = m[5]
        return (f"{y}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}",
                f"{y}-{MONTHS[m[4]]:02d}-{int(m[3]):02d}")

    m = re.fullmatch(rf"(\d{{1,2}})\.?\s*-\s*(\d{{1,2}})\.?\s*{month}\s*(\d{{4}})", t)
    if m and m[3] in MONTHS:
        mo, y = MONTHS[m[3]], m[4]
        return f"{y}-{mo:02d}-{int(m[1]):02d}", f"{y}-{mo:02d}-{int(m[2]):02d}"

    m = re.fullmatch(rf"(\d{{1,2}})\.?\s*{month}\s*(\d{{4}})", t)
    if m and m[2] in MONTHS:
        iso = f"{m[3]}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}"
        return iso, iso

    return None, None


def is_online(location: str) -> bool:
    return any(word in location.lower() for word in ONLINE_WORDS)


def split_people(value: str, where: str, notes: Notes) -> tuple[list[dict], bool]:
    """'[orcid] F. Thiery; A.W. Mees' and five other spellings -> creators, et_al.

    Separators seen: ';', ' / ', ' - ', ', ', ' and ', ' & ', '/w'. The
    citation form 'Thiery, F., Homburg, T. & Schmidt, S.C.' is detected and
    split on the commas *after* the initials instead.
    """
    text = ORCID_LINK.sub(lambda m: f" ⟨{m.group(1)}⟩", value)
    text = strip_md(text)
    et_al = bool(re.search(r"\bet al\.?", text))
    text = re.sub(r"\bet al\.?", "", text)
    text = text.replace("/w", ",")

    if ";" in text:
        parts = text.split(";")
    elif " / " in text:
        parts = text.split(" / ")
    elif re.search(r"\s-\s", text):
        parts = re.split(r"\s-\s", text)
    elif re.match(r"^\s*(⟨[^⟩]+⟩\s*)?[\w'-]+, (?:[A-Z]\.\s?)+,", text):
        parts = re.split(r"(?<=\.)\s*(?:,|&)\s*", text)
    else:
        parts = re.split(r",|\s&\s|\sand\s", text)

    people = []
    for part in parts:
        orcid = None
        m = re.search(r"⟨([^⟩]+)⟩", part)
        if m:
            orcid = m.group(1)
            part = part.replace(m.group(0), "")
        name = part.strip(" ,-.;")
        if name.endswith(" F") or re.search(r"\b[A-Z]$", name):
            name += "."                       # 'A.W. Mees' survives, 'F' -> 'F.'
        if not name:
            if orcid:                         # name filled from other entries in S2
                notes.add(where, "orcid-without-name", f"ORCID {orcid} has no name next to it")
                people.append({"orcid": orcid})
            continue
        person = {"name": name}
        if orcid:
            person["orcid"] = orcid
        people.append(person)
    if not people:
        notes.add(where, "no-creators", f"could not read people from {value.strip()!r}")
    return people, et_al


# ---------------------------------------------------------------------------
# squirrelpapers-volumes: docs/vol<N>/index.md
# ---------------------------------------------------------------------------

ISSUE_NEW = re.compile(r"^###\s+Issue\s+(\d+)\s*$")
ISSUE_OLD = re.compile(r"^###\s+(\d{4}):\((\d+)\)(\d+)\s*(?:=>\s*SI:\s*(.+?))?\s*$")
ENTRY_HEAD = re.compile(r"^(?:[>*\-]\s*)*\**\s*(#|λ|§|𝒬)(\d+)\s+(.*)$")
TYPE_TAG = re.compile(r"^\[`?([^\]`]+)`?\]\s*")
FIELD = re.compile(r"^\*\*`?([A-Za-z][A-Za-z /-]*?)`?\*\*:?\s*(.*)$")
PLAIN_KEY = re.compile(r"^(DOI|Wikidata|ISBN|Link)\s*:\s*(.*)$", re.I)

KNOWN_FIELDS = {
    "authors", "doi", "event", "location", "session", "repository", "repo",
    "version", "release", "date", "link", "type", "editors", "contributors",
    "video", "youtube", "wikidata", "zenodo-community",
}


def _parse_entry_head(line: str) -> dict | None:
    m = ENTRY_HEAD.match(line.strip())
    if not m:
        return None
    sigil, n, rest = m.group(1), int(m.group(2)), m.group(3)
    rest = rest.replace("<br>", " ").strip()
    rest = re.sub(r"\*\*\s*$", "", rest).strip()
    labels = []
    while True:
        t = TYPE_TAG.match(rest)
        if not t:
            break
        labels.append(t.group(1).strip())
        rest = rest[t.end():]
    title = re.sub(r"\s+", " ", rest.replace("**", "")).strip().rstrip()
    return {"sigil": sigil, "n": n, "labels": labels, "title": title}


def parse_volume_md(text: str, volume: int, source: str, notes: Notes) -> dict:
    """One docs/vol<N>/index.md -> {'volume', 'year', 'issues': [...]}.

    Issues come in two header forms ('### Issue 4' with an italic title line
    below, and '### 2021:(3)1 => SI: Data & Software'). Entries in three.
    """
    issues: list[dict] = []
    issue: dict | None = None
    entry: dict | None = None
    year = None
    lines = text.splitlines()

    def close_entry():
        nonlocal entry
        if entry is not None and issue is not None:
            issue["entries"].append(entry)
        entry = None

    for number, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()
        where = f"{source}#L{number}"

        m_new, m_old = ISSUE_NEW.match(stripped), ISSUE_OLD.match(stripped)
        if m_new or m_old:
            close_entry()
            if m_new:
                issue = {"issue": int(m_new.group(1)), "title": None, "line": number}
            else:
                year = year or int(m_old.group(1))
                if int(m_old.group(2)) != volume:
                    notes.add(where, "volume-mismatch", f"header says volume {m_old.group(2)}")
                si = m_old.group(4)
                issue = {"issue": int(m_old.group(3)),
                         "title": f"Special Issue on {si.strip()}" if si else None,
                         "line": number}
            issue["entries"] = []
            issues.append(issue)
            continue

        if stripped.startswith("## ") or stripped.startswith("# "):
            close_entry()
            continue
        if issue is None:
            continue

        # The italic line under '### Issue N' is the special-issue title.
        if (entry is None and issue["title"] is None and not issue["entries"]
                and re.fullmatch(r"\*[^*].*\*", stripped)):
            issue["title"] = stripped.strip("*").strip()
            continue

        head = _parse_entry_head(stripped)
        if head and (stripped.startswith(("**", "#", ">", "* **")) and "Authors" not in stripped):
            close_entry()
            entry = {**head, "fields": [], "plain": [], "quotes": [], "line": number,
                     "where": where}
            continue

        if entry is None:
            if stripped and stripped not in ("TBD", "> TBD") and not stripped.startswith(">"):
                notes.add(where, "orphan-line", stripped[:120])
            continue

        if stripped.startswith(">"):
            quote = stripped.lstrip("> ").strip()
            if quote:
                entry["quotes"].append(quote)
            continue
        if stripped.startswith("* ") or stripped.startswith("- "):
            body = stripped[2:].strip()
            fm = FIELD.match(body)
            if fm:
                entry["fields"].append((fm.group(1).strip().lower(), fm.group(2).strip(),
                                        f"{source}#L{number}"))
            else:
                pk = PLAIN_KEY.match(body)
                if pk:
                    entry["fields"].append((pk.group(1).lower(), pk.group(2).strip(),
                                            f"{source}#L{number}"))
                else:
                    entry["plain"].append((body, f"{source}#L{number}"))
            continue
        if stripped:
            # Dialect 1 sometimes drops the bullet ('F. Thiery; A.W. Mees' on a
            # bare line under the heading). Inside an entry it is still data.
            entry["plain"].append((stripped, where))
            notes.add(where, "no-bullet", stripped[:120])

    close_entry()
    return {"volume": volume, "year": year, "issues": issues}


def build_entry(raw: dict, notes: Notes) -> dict:
    """Raw entry (header + field lines) -> the dict that goes into vol<N>.yaml."""
    where = raw["where"]
    out: dict = {"n": raw["n"], "types": [slugify(label) for label in raw["labels"]],
                 "title": raw["title"]}
    event: dict = {}
    links: dict = {}
    creators: list[dict] = []
    et_al = False

    # Dialect 1 (Vol 1-4): bare bullets. The first one that is not a DOI or a
    # URL is the author line; DOI/Wikidata/ISBN lines are recognised by content.
    for body, w in raw["plain"]:
        if re.fullmatch(r"(?i)doi:?\s*(tbd|n/?a|-)?", body.strip()):
            notes.add(w, "doi-placeholder", body.strip())
            continue
        if DOI_RE.search(body) or "doi.org" in body:
            doi = extract_doi(body, w, notes)
            if doi and "doi" not in out:
                out["doi"] = doi
            continue
        qid = QID_RE.search(body)
        if body.lower().startswith("wikidata") and qid:
            out["wikidata"] = qid.group(0)
            continue
        if body.lower().startswith("isbn"):
            out["isbn"] = body.split(":", 1)[-1].strip()
            continue
        if re.fullmatch(r"https?://\S+", body.strip()):
            links["link"] = body.strip()
            continue
        if not creators:
            creators, et_al = split_people(body, w, notes)
            continue
        notes.add(w, "unread-bullet", body[:120])

    for key, value, w in raw["fields"]:
        if key not in KNOWN_FIELDS and key not in ("isbn",):
            notes.add(w, "unknown-field", f"{key}: {value[:80]}")
            out.setdefault("notes", []).append(f"{key}: {strip_md(value)}")
            continue
        if key == "authors":
            creators, et_al = split_people(value, w, notes)
        elif key in ("editors", "contributors"):
            people, _ = split_people(value, w, notes)
            out[key] = people
        elif key in ("doi", "link"):
            doi = extract_doi(value, w, notes)
            if doi:
                if "doi" in out and out["doi"] != doi:
                    out.setdefault("related_dois", []).append(doi)
                else:
                    out["doi"] = doi
            else:
                href = first_href(value)
                if href and "doi.org/" in href:
                    pass                  # a DOI link to a placeholder is not a link
                elif href:
                    links["link"] = href
                elif value and value.lower() not in ("n/a", "tbd"):
                    notes.add(w, "unread-link", value[:120])
        elif key == "event":
            name = strip_md(value)
            m = re.search(r"\(([^()]*)\)\s*$", name)
            if m:
                start, end = parse_date(m.group(1))
                if start:
                    event["start"], event["end"] = start, end
                else:
                    event["date_text"] = m.group(1)
                    notes.add(w, "date-unparsed", m.group(1))
                name = name[: m.start()].strip()
            event["name"] = name
        elif key == "session":
            session = strip_md(value)
            if session.lower() not in ("n/a", "-", ""):
                event["session"] = session
        elif key == "location":
            location = strip_md(value)
            if location:
                event["location"] = location
                event["online"] = is_online(location)
        elif key in ("repository", "repo"):
            links["repository"] = first_href(value) or strip_md(value)
        elif key == "release":
            links["release"] = first_href(value) or strip_md(value)
            label = MD_LINK.search(value)
            if label:
                out.setdefault("release_label", label.group(1))
        elif key in ("video", "youtube"):
            links["video"] = first_href(value) or strip_md(value)
        elif key == "zenodo-community":
            links["zenodo_community"] = first_href(value) or strip_md(value)
        elif key == "version":
            out["version"] = strip_md(value)
        elif key == "wikidata":
            qid = QID_RE.search(value)
            if qid:
                out["wikidata"] = qid.group(0)
        elif key == "date":
            start, _ = parse_date(strip_md(value))
            if start:
                out["date"] = start
            else:
                notes.add(w, "date-unparsed", value)
        elif key == "type":
            out["context"] = strip_md(value)
        elif key == "isbn":
            out["isbn"] = strip_md(value)

    if creators:
        out["creators"] = creators
    if et_al:
        out["et_al"] = True
    if event:
        out["event"] = event
    if links:
        out["links"] = links
    if raw["quotes"]:
        out["legacy_citation"] = " ".join(strip_md(q) for q in raw["quotes"])
    if not raw["labels"]:
        notes.add(where, "no-type", f"{raw['sigil']}{raw['n']} {raw['title'][:60]}")
    if "doi" not in out and not links:
        out["draft"] = True
        notes.add(where, "draft", f"no DOI and no link: {raw['sigil']}{raw['n']} {raw['title'][:60]}")
    return out


# ---------------------------------------------------------------------------
# squirrelpapers-volumes: docs/wikidata/wikidata.md
# ---------------------------------------------------------------------------


def parse_wikidata_md(text: str) -> tuple[dict[int, str], dict[tuple[int, int], str]]:
    """'* Volume 4: Q114568632' and '* V4, I2: Q114568679' -> two lookup tables."""
    volumes, issues = {}, {}
    for line in text.splitlines():
        m = re.search(r"Volume\s+(\d+):\s*(Q\d+)", line)
        if m:
            volumes[int(m.group(1))] = m.group(2)
        m = re.search(r"V(\d+),\s*I(\d+):\s*(Q\d+)", line)
        if m:
            issues[(int(m.group(1)), int(m.group(2)))] = m.group(3)
    return volumes, issues


# ---------------------------------------------------------------------------
# squirrelpapers-volumes: docs/vol7/bibtex.md
# ---------------------------------------------------------------------------


def parse_bibtex_md(text: str) -> dict[str, dict]:
    """Hand-written BibTeX blocks -> {doi: {type, fields}}. Minimal on purpose:
    only `@type{key, name = {value}, ...}` with one field per line, as in the file."""
    out = {}
    for block in re.findall(r"@(\w+)\{[^,]+,(.*?)\n\}", text, flags=re.S):
        kind, body = block
        fields = {}
        for name, value in re.findall(r"^\s*(\w+)\s*=\s*\{(.*)\},?\s*$", body, flags=re.M):
            fields[name.lower()] = re.sub(r"[{}]", "", value).strip()
        if "doi" in fields:
            out[normalise_doi(fields["doi"])] = {"type": kind.lower(), "fields": fields}
    return out


# ---------------------------------------------------------------------------
# florianthiery/pub: _pages/talks.md and _pages/poster.md
# ---------------------------------------------------------------------------

PUB_LINE = re.compile(
    r"^-\s+!\[(?P<flag>[a-z]{2})\]\([^)]*\)\s*(?P<authors>.+?)\s*\((?P<year>\d{4})\)\.?\s*(?P<rest>.*)$"
)
FLAG_LANGUAGE = {"gb": "en", "de": "de"}


def parse_pub_md(text: str, kind: str, source: str, notes: Notes,
                 until_year: int = 2019) -> list[dict]:
    """One line per item: 'Authors (Year). _Title_, Event, City, Country, Date. DOI: [..](..).'"""
    items = []
    year = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        where = f"{source}#L{number}"
        m = re.match(r"^##\s+(\d{4})", line)
        if m:
            year = int(m.group(1))
            continue
        if year is None or year > until_year or not line.startswith("-"):
            continue
        m = PUB_LINE.match(line)
        if not m:
            notes.add(where, "pub-unparsed", line[:120])
            continue

        rest = m.group("rest")
        doi_part = re.search(r"DOI:\s*(.*)$", rest)
        doi = extract_doi(doi_part.group(1), where, notes) if doi_part else None
        body = rest[: doi_part.start()] if doi_part else rest

        italics = list(re.finditer(r"_([^_]+)_", body))
        if not italics:
            notes.add(where, "pub-no-title", line[:120])
            continue
        title = " ".join(i.group(1).strip().rstrip(",") for i in italics)
        tail = body[italics[-1].end():].strip(" ,.")
        parts = [p.strip() for p in tail.split(",") if p.strip()]

        event: dict = {}
        if len(parts) >= 3:
            start, end = parse_date(parts[-1])
            if start:
                event["start"], event["end"] = start, end
            else:
                event["date_text"] = parts[-1]
                notes.add(where, "date-unparsed", parts[-1])
            event_parts = parts[:-3]
            if event_parts and event_parts[0].lower().startswith("with "):
                notes.add(where, "pub-cleanup", f"dropped {event_parts[0]!r} from event name")
                event_parts = event_parts[1:]
            event["name"] = ", ".join(event_parts)
            event["location"] = f"{parts[-3]}, {parts[-2]}"
            event["online"] = is_online(event["location"]) or is_online(event["name"])
        else:
            notes.add(where, "pub-no-event", tail[:120])

        creators, _ = split_people(m.group("authors"), where, notes)
        items.append({
            "year": year,
            "kind": kind,
            "title": title,
            "creators": creators,
            "language": FLAG_LANGUAGE.get(m.group("flag"), m.group("flag")),
            "doi": doi,
            "event": event,
            "where": where,
        })
    return items
