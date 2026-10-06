# Primer — Squirrel Papers als datengetriebene Journal-Seite

Arbeitsplan für `squirrelpapers/squirrelpapers.github.io`: die Volumes und
Issues der Squirrel Papers (ISSN 2750-560X, Wikidata Q89658875) aus YAML
erzeugen — eine HTML-Seite je Volume, Issue und Entry, Zitation in mehreren
Stilen, BibTeX, RDF (DCAT 3 / DCAT-AP 3 mit CIDOC-CRM-Brücke), SHACL-Gate,
SPARQL- und Filterseite, Karte der Konferenzorte. Die Seite ersetzt
`squirrelpapers/squirrelpapers-volumes` und die WordPress-Seite
`squirrelpapers.net` vollständig.

**So wird es benutzt.** Es wird in jedem Chat vollständig hochgeladen (dazu das
Bundle nach A5). Danach genügt ein Satz: „Wir machen S3." Teil A gilt immer,
Teil B ist die Übersicht, Teil C beschreibt den einzelnen Schritt. Status in
Teil B und Beschlusslage in A4 werden am Ende jedes Chats nachgeführt.

---

# Teil A — Immer gültig

## A1. Ausgangslage

| Repo | Rolle | Stand |
|---|---|---|
| `squirrelpapers/squirrelpapers-volumes` | bisherige Inhaltsquelle, Vol 1–8 | wird nach S2 abgelöst und archiviert |
| `florianthiery/pub` | persönliche Publikationsliste (Jekyll) | liefert Poster und Vorträge bis 2019 für Vol 1 |
| `FDOx-squirrel/fdo-squirrel-registry` | Vorbild für SPARQL-Seite, Filter, CRM-Brücke, SHACL | Code wird kopiert, nicht referenziert |
| `squirrelpapers.net` (WordPress) | alte Website: Startseite, About, Impressum, Datenschutz | wird nach S13 auf GitHub Pages umgeleitet |
| `squirrelpapers/squirrelpapers.github.io` | **dieses Repo** | leer, beginnt mit S1 |

### Befunde (geprüft 2026-10-06, Klon mit `--depth 1`)

1. **Die Volumes sind Markdown, nicht HTML.** `docs/vol1…vol8/index.md`,
   gerendert von einer Jekyll-Action. Daneben `docs/vol7/bibtex.md` (von Hand
   gepflegtes BibTeX) und `docs/wikidata/wikidata.md` (QIDs für Journal,
   Volumes, Issues).
2. **Drei Markdown-Dialekte in einem Repo.** Vol 1–2: `#1 Titel` + Spiegelstriche
   ohne Feldnamen (`* Florian Thiery, Timo Homburg`, `* 10.5281/zenodo.…`).
   Vol 1 (teilweise) bis Vol 6: `**#1 [`Typ`] Titel**` + `* **Authors**: …`.
   Ab Vol 7: Feldnamen in Backticks (`* **`Event`** …`). Der Parser in S2 muss
   alle drei kennen; was er nicht zuordnen kann, landet im Prüfbericht statt
   stillschweigend im Müll.
3. **Entry-Sigel wechseln.** `#` bis Vol 6, `λ` in Vol 7, `§` in Vol 8, `𝒬` für
   die CoRDI-Proceedings (Vol 7, Issue 5). `vol7/bibtex.md` zeigt die
   gewollte Zitierform: `pages = {7(5), 𝒬1}` bzw. `{λ5}` — das Sigel ist Teil
   der Zitation, nicht Dekoration.
4. **Umfang.** 8 Volumes, 4–7 Issues je Volume, grob 200 Entries (Zählung per
   Regex, unterzählt Vol 1–2), **178 verschiedene Zenodo-DOIs**. Nicht jede
   Entry hat eine DOI: z. B. Vol 6, Issue 1, #1 verweist auf eine Datei auf
   Wikimedia Commons.
5. **Typ-Label sind Handarbeit.** 20+ Varianten, darunter Synonyme
   (`Presentation`/`Talk`), Mehrfachtypen (`[Presentation] [Conference Paper]`)
   und projekteigene (`FDO`, `Methodological Working Paper`). Vol 2 und Teile
   von Vol 3/4 haben gar keine Typ-Tags.
6. **`pub` für Vol 1.** `_pages/talks.md` (28 Einträge ≤ 2019) und
   `_pages/poster.md` (9 Einträge ≤ 2019) im Format
   `Autoren (Jahr). _Titel_, Event, Ort, Datum. DOI: …`. Die Flaggen-Icons
   (`gb`, `de`) sind die **Vortragssprache** → `dct:language`.
   Mehrere DOIs stehen schon in Vol 1 (z. B. 1410516, 1469298): Dubletten
   werden über die DOI erkannt, nicht über den Titel.
7. **Ortsangaben in `pub` sind teils falsch** („Bordeaux, Germany",
   „Vienna, Germany"). Orte werden deshalb nicht als Text übernommen, sondern
   über eine Wikidata-QID je Ort aufgelöst (S2 legt die Liste an, S3 holt
   Koordinaten).
8. **Netz in der Sandbox.** Erreichbar: GitHub, PyPI. **Nicht** erreichbar:
   `zenodo.org`, `api.datacite.org`, `doi.org`, `wikidata.org`,
   `squirrelpapers.net`, `cdn.jsdelivr.net`. Folge: Der Ernte-Schritt läuft
   immer auf Flos Rechner (oder in der Action); der Cache unter `data/raw/`
   wird committet und im Bundle mit hochgeladen. Seiten im Browser dürfen CDNs
   nutzen, der Build in der Sandbox nicht.
9. **SPARQL-Vorbild.** `fdo-squirrel-registry` nutzt rdflib unter Pyodide
   (`queries.yaml` → `py/step_sparql.py` + `py/templates/sparql.html.j2` →
   `docs/sparql.html`), jede Beispielabfrage wird beim Build ausgeführt und
   ein leeres Ergebnis bricht den Build ab. Der Filter auf der Startseite ist
   ein schlankes JSON-Index-Pattern (`registry-index.json`). Beides wird
   übernommen — so einfach wie möglich.
10. **Impressum.** Die alte Seite beruft sich auf „§ 5 TMG". Das TMG ist seit
    14.05.2024 durch das Digitale-Dienste-Gesetz (DDG) ersetzt; die
    Anbieterkennzeichnung steht jetzt in § 5 DDG. Den wörtlichen Text konnte
    ich nicht holen (WebFetch liefert nur Zusammenfassungen, Shell ist
    gesperrt) → siehe Teil D.
11. **Farben.** Aus `sqp_logo.png`: Pflaume `#892a69`, Magenta `#c94fa0`,
    Zwischenton `#b03686`. Website: grauer Kopf (`#767676`), dunkel-lila
    Netzwerk-Hintergrund, Initiale in Rot-Pink, Überschriften in fetter
    Sans-Serif.

## A2. Zielbild

```
data/raw/volumes-md/   (Snapshot squirrelpapers-volumes)  ┐
data/raw/pub/          (Snapshot florianthiery/pub)       ├─ S2 migrate (einmalig)
                                                          ┘        │
                                                                   ▼
                         content/journal.yaml, content/vol<N>.yaml  ← Quelle der Wahrheit
                                                                   │
   python main.py harvest  (Netz, nur bei Flo / in der Action)     │
   → data/raw/zenodo/<recid>.json, data/raw/wikidata/<QID>.json ───┤
                                                                   ▼
                                        S4 merge → data/derived/entries.json
                                                                   │
        ┌──────────────┬──────────────┬──────────────┬─────────────┼──────────────┐
        ▼              ▼              ▼              ▼             ▼              ▼
   S5 Seiten      S6 Zitation    S7 RDF         S8 SHACL      S9 SPARQL      S10 Karte
   docs/**.html   CSL-JSON,      dist/*.ttl     Gate          + Filter       GeoJSON,
   EN + /de/      BibTeX, RIS    DCAT3+CRM      (--strict)    docs/sparql    Leaflet/OSM
        └──────────────┴──────────────┴──────────────┴─────────────┴──────────────┘
                                         │
                            S11 GitHub Action → GitHub Pages
                            S12 w3id.org/squirrelpapers/ → Redirects + Conneg
```

Eigenschaften, an denen das Ergebnis gemessen wird:

1. **Jede Entry hat genau eine IRI** `https://w3id.org/squirrelpapers/v<N>/i<M>/e<K>`,
   und unter dieser IRI liefert die Seite HTML, Turtle, JSON-LD, BibTeX und
   CSL-JSON (prüfbar: Linkliste je Entry-Seite, `curl -H Accept:` nach S12).
2. **Keine Entry aus `squirrelpapers-volumes` geht verloren** (prüfbar:
   DOI-Menge alt ⊆ DOI-Menge neu, Bericht in S2).
3. **Der RDF-Dump besteht das SHACL-Gate** mit eigenen Shapes und den
   DCAT-AP-3-Shapes, ohne Verletzung (prüfbar: `python main.py --strict`).
4. **Zweimal bauen, `git status` sauber.**
5. **Der Build läuft offline** gegen `content/` und `data/raw/`.

## A3. Querschnittsregeln

- **Quelle der Wahrheit ist `content/*.yaml`.** Wer eine Entry ändert, ändert
  das YAML — nie das HTML in `docs/`.
- **Rohdaten unter `data/raw/`, unverändert, schreibgeschützt.** Zenodo- und
  Wikidata-Antworten werden so gespeichert, wie sie kamen (JSON, sortierte
  Schlüssel). Was daraus wird, geht nach `data/derived/`, `dist/` oder `docs/`.
- **Wiederverwendung heißt Kopieren.** Code aus `fdo-squirrel-registry` wird
  kopiert, mitsamt seinen Prüfungen (leere Abfrage = Build-Fehler).
- **Keine Uhr im Ergebnis.** Kein `datetime.now()`. Datumsangaben kommen aus
  `RELEASE` in `py/sqp_utils.py` oder aus den Daten.
- **Zweimal laufen lassen, `git status` bleibt sauber.** Turtle sortiert
  aus N-Triples, keine Blank Nodes (skolemisieren), JSON mit `sort_keys`.
- **Netz nur in `python main.py harvest`.** Der Standardlauf ist offline.
- **Sprache.** `PRIMER.md` deutsch. Code, Kommentare, README, Ontologie,
  Seiten: British English; die Seite zusätzlich auf Deutsch unter `/de/`.
  Titel und Abstracts bleiben in Originalsprache.
- **Plattform.** Befehle für Windows `cmd`, jeder auf einer Zeile.
- **Lieferung** als Patch-ZIP (nur Quellen), mit aktualisiertem `PRIMER.md`.

## A4. Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Was passiert mit `squirrelpapers-volumes`? | Vollständig migriert und ersetzt; danach archivieren | 2026-10-06 |
| Zenodo-Abfrage live oder gecacht? | Gecacht unter `data/raw/zenodo/`, committet; eigener Verb `harvest` | 2026-10-06 |
| Was kommt aus `florianthiery/pub` in Vol 1? | Poster und Vorträge bis einschließlich 2019, sonst nichts | 2026-10-06 |
| Volume-Zuschnitt | Vol 1 = alles bis 2019; ab Vol 2 ein Volume je Jahr | 2026-10-06 |
| IRI-Schema | `https://w3id.org/squirrelpapers/v<N>/i<M>/e<K>`, nur ASCII, `e<K>` = Position im Issue | 2026-10-06 |
| Entry-Sigel (#, λ, §, 𝒬) | Pro Issue im YAML (`sigil:`), nur Anzeige und Zitation, nie in der IRI | 2026-10-06 |
| Impressum/Datenschutz | Von der alten Seite übernehmen; Flo stellt danach die Weiterleitung um | 2026-10-06 |
| Sprachen | EN unter `/`, DE unter `/de/`; UI und Rahmentexte übersetzt, Inhalte in Originalsprache | 2026-10-06 |
| Zitierstile | CSL-JSON je Entry, im Browser gerendert mit citeproc-js und Stil-Auswahl wie bei Zenodo; Vorschlag Stile: APA 7, Chicago (author-date), Harvard (Cite Them Right), IEEE, MLA 9, Vancouver | Vorschlag |
| PDF-Vorschau | `iframe` auf den Zenodo-Previewer, PDF-Datei dynamisch aus dem Cache (erste PDF im Record) | 2026-10-06 |
| SPARQL | Muster aus `fdo-squirrel-registry`: rdflib unter Pyodide, `queries.yaml`; so einfach wie möglich | 2026-10-06 |
| Karte | Leaflet + OSM; Online-Veranstaltungen erscheinen nicht auf der Karte | 2026-10-06 |
| RDF-Umfang | So viel Semantik wie sinnvoll: DCAT 3 / DCAT-AP 3, DCTERMS, BIBO, FaBiO/PRISM, schema.org (JSON-LD in den Seiten), PROV-O, CIDOC CRM mit Erweiterungen (CRMdig, LRMoo); SHACL-Gate | 2026-10-06 |
| Typ-Vokabular | Eigenes SKOS-Schema `sqp:type/…`, gemappt auf COAR Resource Types, Zenodo `resource_type` und FaBiO | 2026-10-06 |
| Lizenzen | Code MIT, Inhalte/Metadaten CC BY 4.0 | 2026-10-06 |
| Quellrepos | Werden von Claude geklont, Snapshot nach `data/raw/` | 2026-10-06 |
| Modellierung Volume/Issue | Journal = `dcat:Catalog`; Volume und Issue = `dcat:DatasetSeries` (Issue `dcat:inSeries` Volume); Entry = `dcat:Dataset` + `fabio:`-Typ, `dcat:inSeries` Issue | Vorschlag |
| Seitengenerator | Python + Jinja2, kein Jekyll, kein Node-Build | Vorschlag |

## A5. Was in welchem Chat hochgeladen wird

Immer: `PRIMER.md` und das Repo-Bundle. Ab S3 enthält das Bundle den Cache.

```cmd
robocopy . %TEMP%\sqp-bundle /E /XD .git .venv docs dist data\derived __pycache__ /XF config.local.json
```

```cmd
powershell -Command "Compress-Archive -Path $env:TEMP\sqp-bundle\* -DestinationPath sqp-bundle.zip -Force"
```

**Nicht** hochladen: `.git/`, `.venv/`, `docs/` und `dist/` (werden gebaut),
`config.local.json`.

## A6. IRI-Landkarte

Basis: `https://w3id.org/squirrelpapers/`

| Pfad | Inhalt | Ziel des Redirects | Status |
|---|---|---|---|
| `/` | Journal (`dcat:Catalog`) | `https://squirrelpapers.github.io/` | beschlossen |
| `/v<N>` | Volume | `…/v<N>/` | beschlossen |
| `/v<N>/i<M>` | Issue | `…/v<N>/i<M>/` | beschlossen |
| `/v<N>/i<M>/e<K>` | Entry | `…/v<N>/i<M>/e<K>/` | beschlossen |
| `/ontology` | Ontologie `sqp:` | `…/ontology/` | geplant |
| `/type/<slug>` | SKOS-Typen | `…/vocab/type/` | geplant |
| `/person/<orcid-or-slug>` | Personen | `…/people/` | geplant |
| `/event/<slug>` | Veranstaltungen | `…/events/` | geplant |
| `/dump.ttl` | Gesamtgraph | `…/dist/squirrelpapers.ttl` | geplant |

Content Negotiation (S12): `Accept: text/turtle` → `index.ttl`,
`application/ld+json` → `index.jsonld`, `application/x-bibtex` → `index.bib`,
sonst HTML. Jede Entry-Seite liegt als Ordner mit diesen Dateien.

---

# Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen: IRI, Sigel, Sprachen, Typen, Primer | — | — | erledigt 2026-10-06 |
| S1 | Skelett: `main.py`, `sqp_utils.py`, Lizenz, Citation, Stil-Grundlage | dieses | S0 | offen |
| S2 | Migration Markdown + `pub` → `content/*.yaml`, Prüfbericht | dieses | S1 | offen |
| S3 | Harvest: Zenodo-Records, Wikidata-Orte/QIDs → `data/raw/` | dieses (läuft bei Flo) | S2 | offen |
| S4 | Merge + Normalisierung → `data/derived/entries.json`, SKOS-Typen | dieses | S2, S3 | offen |
| S5 | Seiten EN/DE: Journal, Volume, Issue, Entry, About, Impressum, Datenschutz; PDF-iframe | dieses | S4 | offen |
| S6 | Zitation: CSL-JSON, citeproc-js + Stilwahl, BibTeX/RIS je Ebene | dieses | S4 | offen |
| S7 | RDF: Ontologie, DCAT 3/DCAT-AP 3, BIBO/FaBiO, CRM/CRMdig/LRMoo, JSON-LD | dieses | S4 | offen |
| S8 | SHACL-Gate (eigene + DCAT-AP-3-Shapes), `--strict` | dieses | S7 | offen |
| S9 | Filter (JSON-Index) + SPARQL-Seite (rdflib/Pyodide) | dieses | S7 | offen |
| S10 | Karte der Konferenzorte + GeoJSON | dieses | S3, S4 | offen |
| S11 | GitHub Action: Build + Pages-Deploy, optional Harvest | dieses | S5–S10 | offen |
| S12 | w3id: `.htaccess` mit Content Negotiation, PR an perma-id | perma-id/w3id.org | S5, S7 | offen |
| S13 | Umstellung: Weiterleitung `squirrelpapers.net`, Archiv `squirrelpapers-volumes`, Wikidata-Pflege | — | S11, S12 | offen |

**Unabhängig.** Nach S4 laufen S5, S6, S7 und S10 in beliebiger Reihenfolge.
S9 braucht S7, S8 braucht S7. S12 kann parallel zu S8–S11 vorbereitet werden,
sobald die Ordnerstruktur aus S5 steht.

---

# Teil C — Die Schritte

## S0 — Festlegungen

**Ziel:** IRI-Schema, Sigel, Sprachen, Typ-Vokabular und Plan stehen fest.

### Erledigt 2026-10-06

Die drei Quellrepos geklont und gesichtet (Befunde 1–11). Beschlüsse in A4.
Zenodo, Wikidata, DataCite und die alte Website sind aus der Sandbox nicht
erreichbar (Befund 8) — daraus folgt, dass S3 ein lokaler Schritt ist.

## S1 — Skelett

**Ziel:** `python main.py` läuft und meldet für jeden Schritt „nothing to do".

**Uploads:** nur `PRIMER.md` (Repo ist noch leer).

- Layout nach `primer-repo`: `main.py`, `py/sqp_utils.py`, `py/step_*.py`
  (Stubs), `py/templates/`, `content/`, `data/raw/`, `data/derived/`, `dist/`,
  `docs/`, `assets/` (Logo, CSS, Hintergrund).
- Schritte in `main.py`: `migrate`, `harvest` (nicht im Standardlauf),
  `merge`, `site`, `cite`, `rdf`, `validate`, `sparql`, `map`.
- `assets/css/sqp.css` mit Farb-Tokens aus Befund 11, hell/dunkel.
- `LICENSE` (MIT), `LICENSE-CONTENT` (CC BY 4.0), `CITATION.cff`,
  `requirements.txt` (pyyaml, jinja2, rdflib, pyshacl, requests), `.gitignore`
  (ignoriert **nicht** `docs/` und `dist/`), `.nojekyll`.

**Abnahme:** `python main.py --list` zeigt alle Schritte; `python main.py`
läuft fehlerfrei; zweiter Lauf, `git status` sauber.

## S2 — Migration

**Ziel:** Alle Entries aus Vol 1–8 und die `pub`-Poster/Vorträge ≤ 2019 stehen
in `content/vol<N>.yaml`; ein Bericht listet, was nicht sauber ging.

**Uploads:** Bundle. (Claude klont die Quellen selbst nach `data/raw/`.)

YAML-Form (Vorschlag):

```yaml
volume: 7
year: 2025
wikidata: Q…
issues:
  - issue: 4
    sigil: "λ"
    title: {en: "Special Issue on NFDI related topics", de: "…"}
    entries:
      - n: 5                      # → e5, Zitation "7(4), λ5"
        type: presentation        # SKOS-Slug, S4 prüft gegen das Schema
        title: "…"
        creators:
          - {name: "Thiery, Florian", orcid: 0000-0002-3246-3531}
        doi: 10.5281/zenodo.16875678
        event: {name: "…", start: 2025-10-…, place: Q…, online: false}
        language: de
        links: {repository: …, release: …}
```

- Parser für die drei Dialekte (Befund 2) und das `pub`-Format (Befund 6).
- Dubletten über DOI; `pub`-Einträge, deren DOI schon in Vol 1 steht, werden
  nur ergänzt (Event, Ort, Sprache), nicht verdoppelt.
- Orte: Text wird zu einem Eintrag in `content/places.yaml` (Name → QID), den
  Flo einmal von Hand bestätigt (Befund 7).
- QIDs aus `wikidata.md` gehen in die Volume-/Issue-Köpfe.

**Abnahme:** `dist/reports/migration.md` mit Zahlen je Volume; DOI-Menge alt
⊆ DOI-Menge neu (Skript prüft, Ausnahme = leere Liste); jede Zeile, die der
Parser nicht zuordnen konnte, ist im Bericht aufgeführt.

## S3 — Harvest

**Ziel:** Für jede DOI liegt die Zenodo-Record-JSON unter
`data/raw/zenodo/<recid>.json`, für jede QID die Wikidata-JSON (gekürzt auf
Label, Koordinaten, Land) unter `data/raw/wikidata/<QID>.json`.

**Uploads:** Bundle (nach dem Lauf bei Flo, mit Cache).

- `python main.py harvest` — nur bei Flo bzw. in der Action. Höflich: Pause
  zwischen Anfragen, `--only-missing` als Standard, `--refresh` explizit.
- Concept-DOI vs. Version-DOI: beides speichern, Entry zeigt auf die im YAML
  genannte.

**Abnahme:** Bericht `dist/reports/harvest.md` mit Treffern, 404ern und
Records ohne PDF.

## S4 — Merge und Normalisierung

**Ziel:** `data/derived/entries.json` — eine Liste, aus der alle weiteren
Schritte lesen; YAML gewinnt vor Zenodo, Zenodo füllt Lücken.

- SKOS-Typschema `content/vocab/types.yaml` (Slug, Labels EN/DE, Mapping
  COAR / Zenodo / FaBiO), alle Handlabel aus Befund 5 abgedeckt.
- Personen-Normalisierung über ORCID (aus YAML und Zenodo `creators`).

**Abnahme:** Jede Entry hat Typ, mind. einen Creator, Jahr, IRI; Konflikte
YAML↔Zenodo stehen im Bericht.

## S5 — Seiten

**Ziel:** `docs/` enthält alle HTML-Seiten in EN und DE, im Look der alten
Website.

- Jinja2-Templates; Entry-Seite mit Metadaten, Zitierbox, Downloads,
  Zenodo-Preview-`iframe` (`https://zenodo.org/records/<id>/preview/<datei>`),
  JSON-LD im `<head>`.
- Rahmenseiten: Home, About, Volumes & Issues, Impressum, Datenschutz.

**Abnahme:** Linkprüfung über `docs/` ohne tote interne Links; jede Entry aus
`entries.json` hat genau eine Seite je Sprache.

## S6 — Zitation

**Ziel:** Zitiervorschlag mit Stilwahl und Exporte je Entry, Issue, Volume.

- CSL-JSON je Entry; citeproc-js + gewählte CSL-Stile + Locale `en-GB`/`de-DE`
  liegen unter `assets/` (kein CDN beim Build).
- Zitierform übernimmt das Sigel: `Squirrel Papers 7(4), λ5`.
- BibTeX (Form wie `vol7/bibtex.md`, Schlüssel `sp_vol7_iss4_e5`), RIS.

**Abnahme:** BibTeX parst mit `bibtexparser` ohne Fehler; Stichprobe gegen
`vol7/bibtex.md` stimmt inhaltlich.

## S7 — RDF

**Ziel:** `dist/squirrelpapers.ttl` plus je Entry `index.ttl`/`index.jsonld`.

- Ontologie `sqp:` (`https://w3id.org/squirrelpapers/ontology#`), klein,
  nur was DCAT/BIBO/FaBiO nicht haben (Sigel, Issue-Art).
- CRM-Brücke: Entry ≙ `crm:E73_Information_Object` / `lrmoo:F2_Expression`,
  PDF ≙ `crmdig:D1_Digital_Object`, Veranstaltung ≙ `crm:E7_Activity` mit
  `crm:P7_took_place_at` → `crm:E53_Place`, Zeit ≙ `crm:E52_Time-Span`.
  Wie in der Registry als eigene Datei, nicht im Hauptgraph vermischt.

**Abnahme:** Tripelzahl im Bericht; keine Blank Nodes; zweiter Lauf
byte-gleich.

## S8 — SHACL

**Ziel:** Gate gegen eigene Shapes und die DCAT-AP-3-Shapes (kopiert nach
`data/raw/shapes/`).

**Abnahme:** `python main.py --strict` scheitert bei einer absichtlich
kaputten Entry und läuft ohne sie durch.

## S9 — Filter und SPARQL

**Ziel:** Facettenfilter (Jahr, Typ, Volume, Event, Person, Sprache) auf der
Übersichtsseite und `docs/sparql.html`.

- `queries.yaml` + `step_sparql.py` + Template aus der Registry kopieren.

**Abnahme:** Jede Beispielabfrage liefert beim Build ≥ 1 Zeile.

## S10 — Karte

**Ziel:** `docs/map.html` und `dist/events.geojson`.

**Abnahme:** Jede Präsenz-Veranstaltung mit QID hat einen Punkt; Online-
Veranstaltungen fehlen absichtlich.

## S11 — GitHub Action

**Ziel:** Push auf `main` baut und deployt Pages.

**Abnahme:** grüner Lauf, Seite erreichbar unter `squirrelpapers.github.io`.

## S12 — w3id

**Ziel:** `.htaccess` für `w3id.org/squirrelpapers/` mit Content Negotiation,
als PR an `perma-id/w3id.org`.

**Abnahme:** `curl -I` auf eine Entry-IRI mit drei `Accept`-Headern liefert
die drei richtigen Ziele.

## S13 — Umstellung

**Ziel:** Alte Seite leitet um, altes Repo archiviert, Wikidata-Items zeigen
auf die neuen IRIs (P856 / P953 o. ä.).

---

# Teil D — Offene Punkte

1. **Wortlaut Impressum/Datenschutz.** Ich komme an den Originaltext nicht
   heran (Befund 10). Flo speichert die drei WordPress-Seiten als HTML nach
   `data/raw/site/` (oder kopiert den Text). Dabei klären: § 5 TMG → § 5 DDG;
   Datenschutzerklärung muss für GitHub Pages (Server-Logs bei GitHub,
   Zenodo-`iframe`, OSM-Kacheln, CDN für Pyodide) neu gefasst werden. Ich bin
   kein Jurist — der Text ist von Flo zu verantworten.
2. **Hintergrundgrafik der alten Seite** (Netzwerk-Muster). Hochladen oder
   als SVG neu zeichnen?
3. **Vol 2–8 Jahreszuschnitt prüfen**: die bestehenden Volumes sind schon je
   Jahr; gibt es Entries, die beim Jahr umziehen müssen?
4. **Neue Entries ab jetzt**: nur YAML von Hand, oder zusätzlich
   `python main.py add <doi>` als Komfort?
5. **DOI für Volumes/Issues** (Zenodo-Communities oder eigene Records)? Würde
   die Zitierfähigkeit der Issues verbessern.
