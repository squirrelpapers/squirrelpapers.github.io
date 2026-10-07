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
   Regex, unterzählt Vol 1–2), **178 verschiedene Zenodo-DOIs** (korrigiert 2026-10-06 in S2: 179 — `zenodo..5647827` hatte der erste Regex übersehen). Nicht jede
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
| Zitierstile | CSL-JSON je Entry, im Browser gerendert mit citeproc-js 2.4.63 und Stil-Auswahl wie bei Zenodo: APA 7, Chicago (author-date), Harvard (Cite Them Right), IEEE, MLA 9, Vancouver (= `nlm-citation-sequence`). Locale `en-GB` bzw. `de-DE` nach Seitensprache. Ohne JavaScript bleibt der vorgerenderte APA-ähnliche Text stehen | 2026-10-07 |
| PDF-Vorschau | `iframe` auf den Zenodo-Previewer, PDF-Datei dynamisch aus dem Cache (erste PDF im Record) | 2026-10-06 |
| SPARQL | Muster aus `fdo-squirrel-registry`: rdflib unter Pyodide, `queries.yaml`; so einfach wie möglich | 2026-10-06 |
| Karte | Leaflet + OSM; Online-Veranstaltungen erscheinen nicht auf der Karte | 2026-10-06 |
| RDF-Umfang | So viel Semantik wie sinnvoll: DCAT 3 / DCAT-AP 3, DCTERMS, BIBO, FaBiO/PRISM, schema.org (JSON-LD in den Seiten), PROV-O, CIDOC CRM mit Erweiterungen (CRMdig, LRMoo); SHACL-Gate | 2026-10-06 |
| Typ-Vokabular | Eigenes SKOS-Schema `sqp:type/…`, gemappt auf COAR Resource Types, Zenodo `resource_type` und FaBiO | 2026-10-06 |
| Lizenzen | Code MIT, Inhalte/Metadaten CC BY 4.0 | 2026-10-06 |
| Quellrepos | Werden von Claude geklont, Snapshot nach `data/raw/` | 2026-10-06 |
| Modellierung Volume/Issue | Journal = `dcat:Catalog` + `fabio:Journal`; Volume und Issue = `dcat:DatasetSeries` + `fabio:JournalVolume`/`JournalIssue` (Issue `dcat:inSeries` Volume); Entry = `dcat:Dataset` + `fabio:`-Typ, `dcat:inSeries` Issue | 2026-10-07 |
| Seitengenerator | Python + Jinja2, kein Jekyll, kein Node-Build | 2026-10-07 |
| Schritte außerhalb des Standardlaufs | `migrate` (einmalig, überschreibt `content/`) und `harvest` (Netz) laufen nur mit `--only`; Standardreihenfolge `merge → cite → rdf → validate → map → site → sparql` | 2026-10-06 |
| Schriften | Keine Webfonts, keine Drittanbieter-Anfrage für Typografie; Systemschrift-Stacks mit `Inter` an erster Stelle (greift, wo installiert) | Vorschlag |
| Akzentfarbe im Fließtext | Magenta `#c94fa0` hat auf Weiß nur 4,1 : 1 → nur für große Schrift/Deko (`--accent`); Sigel und Akzent in Textgröße hell `#b03686` (5,6 : 1), dunkel Magenta (`--accent-text`) | 2026-10-06 |
| Vol 2–8 beim Jahreszuschnitt | Bleiben, wie sie sind (Issues und Entries 1:1 aus dem alten Repo) | 2026-10-06 |
| `pub`-Einträge in Vol 1 | Nach Jahr in die vorhandenen Issues „Conferences <Jahr>" (2019 → i2, 2014 → i3 … 2018 → i7), sortiert nach Datum, Nummern hinter den vorhandenen | 2026-10-06 |
| Dubletten | DOI-Gleichheit überall = derselbe Datensatz; Titelgleichheit zählt nur innerhalb Vol 1 (gleicher Titel in Vol 4 war ein anderes Werk) | 2026-10-06 |
| Link-Text ≠ Link-Ziel bei einer DOI | Sichtbarer Text gewinnt (Vol 7(3) λ4: Ziel war vom Eintrag darüber kopiert); verworfene DOI steht im Bericht, S3 prüft gegen Zenodo | 2026-10-06 |
| Einträge ohne DOI und ohne Link | Bleiben im YAML mit `draft: true` (IRI und Nummer bleiben stabil), werden in S5 nicht veröffentlicht | Vorschlag |
| Leere Issues („TBD") | Bleiben im YAML mit `entries: []` | Vorschlag |
| `creators` und `types` nach der Migration | Wie in der Quelle geschrieben (`F. Thiery`, `Florian Thiery`, Slugs der Handlabel); Vereinheitlichung erst in S4 über ORCID/Zenodo bzw. SKOS | 2026-10-06 |
| Erneute Migration | `migrate` verweigert, sobald `content/vol*.yaml` existiert; bewusst neu nur mit `set SQP_FORCE=1`. Bereits eingetragene QIDs in `places.yaml` bleiben erhalten | 2026-10-06 |
| Zenodo-Cache | Antwort von `/api/records/<id>` unverändert bis auf den Block `stats` (Views/Downloads), der bei jedem Abruf anders ist; Nicht-200-Antworten in `data/raw/zenodo/_status.json`; vorhandene Records werden nur mit `SQP_REFRESH=1` neu geholt | 2026-10-06 |
| Wikidata-Cache | Je QID gekürzt auf Labels/Beschreibungen (en, de), P625, P17, P31; Abruf gebündelt über `wbgetentities` | 2026-10-06 |
| QID-Vorschläge für Orte | Harvest sucht für Orte ohne QID per `wbsearchentities` (Venue zuerst, dann Stadt, Akronym; en und de), schreibt **nicht** in `content/`, sondern `dist/reports/places.proposed.yaml` mit bestem Kandidaten und Alternativen als Kommentar; Flo prüft und kopiert | 2026-10-06 |
| Titelprüfung | Harvest vergleicht jeden Eintrag mit dem Zenodo-Titel seiner DOI (Ähnlichkeit < 0,6 → Bericht); damit lassen sich die doppelten DOIs aus S2 auflösen | 2026-10-06 |
| Gleiche DOI, deutlich anderer Titel (in `pub`) | Kein Zusammenführen; beide Einträge bleiben, Fall kommt in den Bericht (`doi-shared-different-title`). Migration deshalb einmal mit `SQP_FORCE` neu gelaufen, solange `content/` noch unbearbeitet war | 2026-10-06 |
| Link-Text ≠ Link-Ziel | Keine feste Regel mehr: „Text gewinnt" galt für 7(3) λ4, bei 1(6) #2 war das Ziel richtig. Entscheidet die Titelprüfung des Harvest; Korrektur von Hand in `content/` mit Kommentar | 2026-10-06 |
| Ab jetzt | `content/` wird von Hand gepflegt (erste Handkorrektur: 1(6) #2). `migrate` nie wieder ohne Not, `SQP_FORCE` würde Handkorrekturen überschreiben | 2026-10-06 |
| Ortsvorschläge: Land | Ranking berücksichtigt das Land aus dem Label (Treffer +4, anderes Land −4); ohne Land im Label leichter Bonus für Deutschland | 2026-10-06 |
| Einträge mit nicht abrufbarer DOI (404/410) | `draft: true` mit Kommentar im YAML (14 Einträge); später prüfen, ob die DOIs auf Zenodo veröffentlicht werden | 2026-10-06 |
| QIDs der Orte | Veranstaltungsort, wenn Wikidata ihn kennt, sonst die Stadt; die S3-Vorschläge sind übernommen (52 von 55), nachjustiert wird von Hand | 2026-10-06 |
| Suchhilfe für Orte | Optionales Feld `search: [Venue, Stadt]` in `content/places.yaml`; der Harvest sucht neu, sobald es sich ändert | 2026-10-06 |
| Fehlgeschlagene Abrufe | Werden nie gecacht: Netzfehler landen nicht in `_status.json`, gescheiterte Suchen nicht in `wikidata-search/` (gefunden, als ein Lauf ohne Netz leere Suchergebnisse gespeichert hatte) | 2026-10-06 |
| Koordinaten ohne P625 | Optionales Feld `coordinates: {lat, lon}` in `content/places.yaml`, nur wenn das Wikidata-Item keine hat; hat Vorrang vor Wikidata. Erster Fall: RGK (Q1425831), Koordinaten von ihrer Bibliothek Q28739191 im selben Haus am Palmengarten | 2026-10-07 |
| `entries.json` | Eine Datei für alle späteren Schritte: `journal`, `volumes` (mit Issues und Entry-IDs), `entries`, `people`, `places`, `types`. Entry-ID `v7-i4-e5`; Drafts bleiben drin (`draft: true`) | 2026-10-07 |
| Vorrang beim Merge | `content/` gewinnt; Zenodo füllt Typ (nur wenn `types` leer), Lizenz, Abstract, Schlagwörter, Dateien, Version, Sprache, Datum. Weicht der Zenodo-Titel stark ab, steht er als `title_zenodo` daneben | 2026-10-07 |
| Datum | `date` aus `content/`, sonst Event-Beginn, sonst Zenodo-`publication_date` — aber nur, wenn es ins Volume-Jahr fällt (Vol 1: 2014–2019). Sonst ist es das Datum der neuesten Version einer Concept-DOI und landet nur als `zenodo_date` im Eintrag | 2026-10-07 |
| Personen | ORCID ist der Schlüssel; Name je ORCID = häufigste Nachnamensschreibung, davon der längste Vorname, der mindestens ein Viertel so oft vorkommt wie der häufigste. Ohne ORCID: Zuordnung über Nachname + verträgliche Initialen, nur wenn eindeutig. Personen ohne ORCID mit gleichem Nachnamen und verträglichen Initialen werden zusammengeführt. Titel (Dr., Prof.) und Suffixe (FSA, PhD) fallen weg. Person-IRI `…/person/<ORCID>` bzw. `…/person/<slug>` | 2026-10-07 |
| Autorenliste | Die Liste aus `content/` gilt, auch wenn Zenodo mehr oder weniger Personen nennt (18 Fälle im Bericht); nur bei `et_al: true` wird aus Zenodo ergänzt | Vorschlag |
| Typvokabular | `content/vocab/types.yaml`, 23 Konzepte mit Labels EN/DE, Aliassen (`talk` → `presentation`), `broader`, Mappings auf COAR, FaBiO und Zenodo-`resource_type`; erster Typ = Haupttyp | 2026-10-07 |
| `docs/` | Gehört dem `site`-Schritt: wird bei jedem Lauf geleert und neu geschrieben. Produkte anderer Schritte für das Web (BibTeX, Turtle, Dumps …) schreiben diese nach `data/derived/web/` im Layout von `docs/` (git-ignoriert, sonst läge jede Datei doppelt im Repo); `site` kopiert sie hinein und verlinkt, was da ist. Geändert 2026-10-07 in S6: vorher `dist/web/` — `dist/` ist versioniert, die Kopie in `docs/` reicht | 2026-10-07 |
| Seitenlayout | Ein Ordner je Seite (`v7/i4/e5/index.html`), relative Links (funktioniert von der Platte und unter jedem Host), `canonical` und `hreflang` auf `squirrelpapers.github.io`, schema.org-JSON-LD je Entry | 2026-10-07 |
| PDF-Vorschau | Erst nach Klick (`iframe` auf den Zenodo-Previewer der Versions-Record-ID); vorher kein Drittanbieter-Request — geprüft mit Playwright | 2026-10-07 |
| Rechtliche Seiten | `content/pages/{impressum,privacy}.{de,en}.html`; Impressum auf § 5 DDG umgestellt, Datenschutz neu für GitHub Pages gefasst. **Entwurf**, von Flo vor dem Umschalten zu prüfen | 2026-10-07 |
| UI-Texte | `content/ui.yaml` (EN/DE); Schlüssel dürfen nicht wie Dict-Methoden heißen (`copy`, `items` …), der Build bricht sonst ab | 2026-10-07 |
| Zitierform | Jeder Eintrag als Artikel der Squirrel Papers: Band, Heft, Seite = Sigel + Nummer („Squirrel Papers, 7(4), λ5"); Typ als `genre`/`note`. Nur Einträge mit `@inproceedings`-Container (CoRDI, 7(5)) als Konferenzbeitrag im Tagungsband, Seite = volles Label „7(5), 𝒬1" — wie in Flos `vol7/bibtex.md` | 2026-10-07 |
| BibTeX-Schlüssel | `sp_vol<V>_iss<I>_e<N>` (ASCII); die alten Schlüssel aus `vol7/bibtex.md` (`…_l5`, `…_q1`) gelten nicht weiter | 2026-10-07 |
| Drittanbieter-Code | citeproc-js, 6 CSL-Stile und 3 Locales unverändert unter `assets/vendor/` mit `SOURCE.yaml` (Version/Commit, Lizenz); auf der Seite selbst gehostet, kein CDN | 2026-10-07 |
| Sprache, wenn unbekannt | S4 rät aus Funktionswörtern im Titel (`de`/`en`), markiert mit `language_guessed`; `content/` gewinnt immer. Grund: Zitierstile setzen sonst deutsche Titel in englischen Title Case | 2026-10-07 |
| Zwei Graphen | `dist/squirrelpapers.ttl` (DCAT/DCAT-AP, BIBO, FaBiO, PRISM, schema.org, FOAF, GeoSPARQL, PROV, SPDX) und `dist/squirrelpapers-crm.ttl` (CIDOC CRM, CRMdig, LRMoo) über dieselben IRIs; die CRM-Sicht liegt getrennt, damit der DCAT-Graph allein lesbar bleibt | 2026-10-07 |
| CRM-Abbildung | Entry = `E73`/`lrmoo:F2`, `P102` Titel (`E35`), `P1` DOI (`E42`), `P2` Typ; Entstehung = `E65`/`lrmoo:F28` mit `P14` Personen und `P4` Zeitspanne (`E52`); Veranstaltung = `E7` mit `P7` Ort (`E53`, `P168` WKT) und `P16` → Entry; PDF = `crmdig:D1` `P165` → Entry; Heft/Band/Journal per `P106i`; Journal `lrmoo:F18` | 2026-10-07 |
| Veranstaltungen | Eine Veranstaltung = gleicher Name, gleiches Jahr, Beginn innerhalb von 14 Tagen; Zeitraum = frühester Beginn bis spätestes Ende ihrer Vorträge. IRI `…/event/<name-slug>-<jahr>`, Jahr nicht doppelt; zweiter Termin einer Serie im selben Jahr `…-<datum>` | 2026-10-07 |
| Keine Blank Nodes | Autorenreihenfolge als `rdf:Seq` mit eigener IRI (`#authors`), Distribution, Prüfsumme, Zeitspannen als Hash-IRIs; der Build bricht bei einem Blank Node ab | 2026-10-07 |
| DCAT-AP-Pflichtfelder | Fehlt ein Abstract, bekommt der Eintrag eine erzeugte `dct:description` („Presentation published in the Squirrel Papers 7(4), λ5."); ohne PDF eine Distribution `#landing` auf Zenodo/DOI/Link; Sprachen als EU-Authority-IRIs | 2026-10-07 |
| Turtle-Präfixe | Feste Präfixe nur für Prädikate und Klassen; Subjekt- und Objekt-IRIs werden ausgeschrieben (vorher ein `nsNN`-Präfix pro Eintrag) | 2026-10-07 |
| SHACL-Gate | Drei Prüfungen: DCAT-AP 3.0.1 (offizielle Shapes, unverändert unter `data/raw/shapes/dcat-ap-3.0.1/`) und Journal-Regeln (`shapes/sqp-shapes.ttl`) auf dem DCAT-Graphen + Typenvokabular + `shapes/axioms.ttl`; CRM-Regeln (`shapes/crm-shapes.ttl`) auf dem CRM-Graphen. Verstöße = Fehler unter `--strict`, sonst Warnung | 2026-10-07 |
| Selbsttest | Vor jeder Prüfung muss ein absichtlich kaputter Eintrag (`shapes/selftest.ttl`) von jeder dort genannten Regel gemeldet werden, sonst bricht der Schritt ab — ein Gate, das nie anschlägt, schützt nichts | 2026-10-07 |
| Unterklassen-Axiome | Nur zur Validierung: `dcat:DatasetSeries ⊑ dcat:Dataset`, `foaf:Person`/`Organization ⊑ foaf:Agent` (aus den Spezifikationen); pyshacl folgt `rdfs:subClassOf` bei `sh:class`, der veröffentlichte Graph bleibt ohne Doppeltypisierung | 2026-10-07 |
| Typisierung verwiesener Knoten | Landing Pages `foaf:Document`, EU-Sprach-IRIs `dct:LinguisticSystem`, IANA-Medientyp `dct:MediaType`, EU-Dateityp `dct:MediaTypeOrExtent`, SPDX-Algorithmus `spdx:ChecksumAlgorithm` — im veröffentlichten Graphen, weil DCAT-AP sie per `sh:class` verlangt und die Normdateien nicht mitgeladen werden | 2026-10-07 |
| Konsistenzregeln über alle Einträge | Als SPARQL-Constraints am Journal-Knoten (eine Abfrage je Regel, fehlerhafter Eintrag als `sh:value`), nicht je Eintrag — 9 s → 0,1 s | 2026-10-07 |
| COAR-Codes | Gegen COAR Resource Types 3.2 (Stand 2024-12-03) geprüft: alle Codes in `types.yaml` existieren; `c_c94f` = „conference output" für Workshop/Abstract/Session (`closeMatch`) | 2026-10-07 |
| S14: Einreichen | `python main.py add` (CLI, prüft und sortiert ein) als Kern, Issue-Formular + Action, die daraus einen Pull Request macht, obendrauf | 2026-10-07 |
| S14: Bearbeiten | Der Editor kann auch bestehende Einträge laden und ändern (Ergebnis wieder als Schnipsel / Änderung über denselben Weg) | 2026-10-07 |
| S14: Zenodo | Nur optionale Anreicherung; jedes Feld lässt sich von Hand füllen, der Editor funktioniert vollständig ohne DOI und ohne Netz zu Zenodo | 2026-10-07 |
| Lizenzdatei für Inhalte | `LICENSE-CONTENT` verweist auf CC BY 4.0 (Link auf den Legal Code), kein Volltext im Repo | 2026-10-06 |

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
| `/` | Journal (`dcat:Catalog`) | `https://squirrelpapers.github.io/` | aktiv im Graph (S7) |
| `/v<N>` | Volume (`dcat:DatasetSeries`) | `…/v<N>/` | aktiv im Graph (S7) |
| `/v<N>/i<M>` | Issue (`dcat:DatasetSeries`, `dcat:inSeries` Volume) | `…/v<N>/i<M>/` | aktiv im Graph (S7) |
| `/v<N>/i<M>/e<K>` | Entry (`dcat:Dataset`); Hash-IRIs darunter: `#pdf`, `#landing`, `#authors`, `#creation`, `#title`, `#doi` | `…/v<N>/i<M>/e<K>/` | aktiv im Graph (S7) |
| `/ontology` | Ontologie `sqp:` (`ontology/sqp.ttl`) | `…/ontology/index.ttl` | aktiv (S7) |
| `/type/<slug>` | SKOS-Typen | `…/vocab/types.ttl` | aktiv (S7) |
| `/person/<orcid-or-slug>` | Personen (`foaf:Person`) | noch keine Seite | aktiv im Graph (S7), Seite offen |
| `/event/<slug>-<jahr>` | Veranstaltungen (`event:Event`, `crm:E7_Activity`) | noch keine Seite | aktiv im Graph (S7), Seite offen |
| `/place/<key>` | Orte (`dct:Location`, `geo:Feature`, `crm:E53_Place`) | Karte (S10) | aktiv im Graph (S7) |
| `/org/research-squirrel-engineers` | Herausgeber (`foaf:Organization`) | Startseite | aktiv im Graph (S7) |
| `/shapes/` | SHACL-Regeln des Journals (`sqp-shapes.ttl`, `crm-shapes.ttl`) | `…/shapes/` | aktiv (S8) |
| `/dump.ttl` | Gesamtgraph | `…/downloads/squirrelpapers.ttl` (CRM-Sicht: `squirrelpapers.crm.ttl`) | beschlossen, Redirect in S12 |

Content Negotiation (S12): `Accept: text/turtle` → `index.ttl`,
`application/ld+json` → `index.jsonld`, `application/x-bibtex` → `index.bib`,
sonst HTML. Jede Entry-Seite liegt als Ordner mit diesen Dateien.

---

# Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S0 | Festlegungen: IRI, Sigel, Sprachen, Typen, Primer | — | — | erledigt 2026-10-06 |
| S1 | Skelett: `main.py`, `sqp_utils.py`, Lizenz, Citation, Stil-Grundlage | dieses | S0 | erledigt 2026-10-06 |
| S2 | Migration Markdown + `pub` → `content/*.yaml`, Prüfbericht | dieses | S1 | erledigt 2026-10-06 |
| S3 | Harvest: Zenodo-Records, Wikidata-Orte/QIDs → `data/raw/` | dieses (läuft bei Flo) | S2 | erledigt 2026-10-06 |
| S4 | Merge + Normalisierung → `data/derived/entries.json`, SKOS-Typen | dieses | S2, S3 | erledigt 2026-10-07 |
| S5 | Seiten EN/DE: Journal, Volume, Issue, Entry, About, Impressum, Datenschutz; PDF-iframe | dieses | S4 | erledigt 2026-10-07 |
| S6 | Zitation: CSL-JSON, citeproc-js + Stilwahl, BibTeX/RIS je Ebene | dieses | S4 | erledigt 2026-10-07 |
| S7 | RDF: Ontologie, DCAT 3/DCAT-AP 3, BIBO/FaBiO, CRM/CRMdig/LRMoo, JSON-LD | dieses | S4 | erledigt 2026-10-07 |
| S8 | SHACL-Gate (eigene + DCAT-AP-3-Shapes), `--strict` | dieses | S7 | erledigt 2026-10-07 |
| S9 | Filter (JSON-Index) + SPARQL-Seite (rdflib/Pyodide) | dieses | S7 | offen |
| S10 | Karte der Konferenzorte + GeoJSON | dieses | S3, S4 | offen |
| S11 | GitHub Action: Build + Pages-Deploy, optional Harvest | dieses | S5–S10 | offen |
| S12 | w3id: `.htaccess` mit Content Negotiation, PR an perma-id | perma-id/w3id.org | S5, S7 | offen |
| S13 | Umstellung: Weiterleitung `squirrelpapers.net`, Archiv `squirrelpapers-volumes`, Wikidata-Pflege | — | S11, S12 | offen |
| S14 | Eintragseditor im Web: DOI → Formular → YAML-Schnipsel für `content/vol<N>.yaml` | neues Repo (Arbeitstitel `squirrelpapers-editor`) | S4, S11 | offen |
| S15 | Frontend überarbeiten: Navigation, Startseite, Feinschliff, Barrierefreiheit | dieses | S9, S10 | offen |

**Unabhängig.** Nach S4 laufen S5, S6, S7 und S10 in beliebiger Reihenfolge.
S14 braucht nur das YAML-Format aus S2/S4 und kann jederzeit parallel in
seinem eigenen Repo beginnen; die Einreichung (S14b) setzt S11 voraus. S15
kommt bewusst zuletzt, wenn alle Seiten (Filter, Karte, SPARQL) existieren.
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

### Erledigt 2026-10-06

- `main.py` aus `fdo-squirrel-registry` übernommen und angepasst: Schritte als
  `Step(name, module, description, default, why_not)`; statt eines
  `network`-Flags ein `default`-Flag, weil auch `migrate` (einmalig, schreibt
  `content/`) nie im Standardlauf laufen darf. `--list` nennt den Grund.
  stdout/stderr werden auf UTF-8 umgestellt (λ, §, 𝒬 in Windows-Konsolen).
- `py/sqp_utils.py`: `RELEASE`, Journal-Konstanten (ISSN, QID, Herausgeber),
  `PREFIXES` für alle geplanten Vokabulare, IRI-Bauer (`entry_iri(7,4,5)` →
  `…/v7/i4/e5`), `page_url()` (EN `/`, DE `/de/`), `citation_label()` →
  `7(5), 𝒬1`, `normalise_doi()` (für die Dublettenerkennung in S2), die
  kanonischen Schreiber aus der Registry (`write_text` mit LF,
  `write_json`, `write_canonical_turtle`, `bind_remaining`, `script_json`,
  `template_environment` mit `autoescape=True`) und neu `write_yaml`
  (Schlüsselreihenfolge bleibt, weil `content/` von Hand gelesen wird).
- Neun Schritt-Stubs `py/step_*.py`, je einzeln lauffähig; jeder prüft seine
  Vorbedingung und meldet `skipped (no input): …` mit dem Schritt, der sie
  liefert. Die Abnahme „nothing to do" aus dem Plan ist damit präziser
  erfüllt: jeder Schritt sagt, *worauf* er wartet.
- `content/journal.yaml` als Kopf des Katalogs, Texte von der alten
  Startseite (EN geglättet: „a free", „posters"), DE neu; Wikidata-Klassen
  aus `wikidata.md`.
- `assets/css/sqp.css` mit Tokens aus Befund 11, hell/dunkel; Kontraste
  geprüft (siehe A4). Logo als `assets/img/sqp-logo.png` (transparentes PNG,
  768 × 455).
- `LICENSE` (MIT), `LICENSE-CONTENT` (CC BY 4.0), `CITATION.cff`,
  `README.md`, `requirements.txt`, `.gitignore` (ignoriert `PATCH-README.md`
  und `dist/pipeline_report.txt`, **nicht** `docs/`/`dist/`),
  `.gitattributes` (LF überall).
- **Verschoben:** `.nojekyll` gehört nach `docs/` und wird in S5 vom
  `site`-Schritt geschrieben, nicht ins Wurzelverzeichnis gelegt.
- Geprüft: zwei Läufe, `git status` sauber; `--strict`, `--dry-run`,
  `--only harvest`, `--only migrate`, unbekannter Schrittname.

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

### Erledigt 2026-10-06

**Was entstanden ist.** `py/migrate_parsers.py` (reine Parser, keine
Dateizugriffe) und `py/step_migrate.py`. Quellen als Snapshot unter
`data/raw/volumes-md/` (Commit `d00e0b7`, 2026-04-18) und `data/raw/pub/`
(Commit `ac66360`, 2022-06-16), je mit `SOURCE.yaml`. Ergebnis:
`content/vol1.yaml` … `vol8.yaml`, `content/places.yaml`,
`dist/reports/migration.md`.

**Zahlen** (aus dem Bericht):

| Vol | Issues | Entries | davon draft | DOIs |
|---|---|---|---|---|
| 1 | 7 | 41 | 0 | 41 |
| 2 | 3 | 5 | 0 | 5 |
| 3 | 4 | 18 | 0 | 17 |
| 4 | 4 | 31 | 10 | 20 |
| 5 | 6 | 26 | 0 | 24 |
| 6 | 5 | 52 | 5 | 45 |
| 7 | 5 | 47 | 0 | 44 |
| 8 | 6 | 23 | 5 | 14 |
| **Σ** | 40 | 243 | 20 | 212 |

Aus `pub` (≤ 2019): 37 Einträge gelesen, 32 neu in Vol 1, 5 mit vorhandenen
Vol-1-Einträgen zusammengeführt (Sprache, Datum, Ort ergänzt).
**DOI-Prüfung:** 179 Zenodo-DOIs stehen per Regex (unabhängig vom Parser) in den
alten Volumes, 0 gehen verloren; 2 bewusst verworfene Link-Ziele siehe unten.
54 Präsenzorte in `places.yaml`, alle noch ohne QID.

**Befunde an den Quellen** (geprüft 2026-10-06; alle mit Zeilennummer im Bericht):

- *Gleiche DOI bei zwei Einträgen* — 3(1) #4/#12 (`5642976`), 5(3) #6/5(5) #4
  (`10260778`), 8(1) §1/§4 (`18441772`). Vermutlich je ein Kopierfehler.
- *Link-Text ≠ Link-Ziel* — 7(3) λ4 (Text `14898291`, Ziel `14886032` = λ3)
  und `pub` 2017 „Avalanches on Atlantis" (Text `817469`, Ziel `817496`).
- *Platzhalter-DOIs* — `zenodo.xyz`, `zenodo.TBD`, „DOI TBD": 12 Stellen,
  daraus 20 `draft`-Einträge (10 in Vol 4, 5 in Vol 6 = UK-Ireland DH 2024,
  5 in Vol 8 = FDO-Issue ohne Angaben).
- *Gleicher Titel, andere DOI* — „Linking potter, pots and places" (Vol 1(3)
  #1 `775019`, `pub` `292975`): als `related_dois` behalten. „Taming
  Ambiguity" (CAA-Talk 2018 `1200111` vs. Preprint 2022 in Vol 4(4) #2
  `7361759`): zwei Werke, beide behalten.
- *Kleinkram* — `zenodo..5647827` (repariert), Autorzeilen ohne
  Spiegelstrich (Vol 4, 2×), ein ORCID ohne Namen (Vol 1(7) #2, aus anderen
  Einträgen ergänzt), „Alalrd Mees" in `pub`, Herausgeber in
  `vol7/bibtex.md` einmal als „Paul, Groth", ein Datum „26.04.2024 /
  14.02.2024" (Vol 7(4) λ2) nicht auswertbar.
- *Länder in `pub`* falsch oder deutsch („Bordeaux, Germany", „Barcelona,
  Spanien") — bleiben als Text, die QID in `places.yaml` macht sie eindeutig.
- *39 Einträge ohne Typ* (Dialekt 1, Vol 1–4) — S4 holt den Typ aus Zenodo.

**Anders als geplant.** Die Abnahme „DOI-Menge alt ⊆ neu" prüfte zuerst gegen
die eigene Parser-Ausgabe; das hätte einen Parserfehler nicht bemerkt. Jetzt
zählt ein unabhängiger Regex über die Rohdateien.

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

### Erledigt 2026-10-06 (Code; der Lauf steht bei Flo aus)

`py/step_harvest.py`: Zenodo-Records, Wikidata-Entitäten für Orte mit QID
und deren Länder, Wikidata-Suche für Orte ohne QID, Bericht aus dem Cache
(`python py/step_harvest.py --report` baut ihn offline neu). Höflich:
1 s zwischen Zenodo-Abrufen (Gastlimit 60/min), Wiederholung bei 429/5xx mit
`Retry-After`, eigener User-Agent mit Repo-URL. Bei 212 Records dauert der
erste Lauf etwa 4–5 Minuten.

**Geprüft gegen nachgebaute APIs** (lokaler Testserver, nicht im Repo; Zenodo
und Wikidata sind aus der Sandbox gesperrt, Befund 8): 212 Records, ein 404,
ein 429 mit erfolgreicher Wiederholung, eine Concept-DOI-Weiterleitung, ein
Record ohne PDF, eine fehlende QID, ein absichtlich falscher Titel bei der
doppelten DOI 8(1) §1/§4 — alles landete richtig im Bericht. Zweiter Lauf:
0 Zenodo-Abrufe, `data/raw/` und Berichte byte-gleich. Die echten Antworten
sind damit **nicht** geprüft: die Feldnamen des Zenodo-JSON (`metadata.title`,
`files[].key`) sind aus der API-Doku, nicht aus einer echten Antwort.

### Erster echter Lauf 2026-10-06 (bei Flo, 402 s)

- **198 von 212 Records im Cache**, 14 nicht abrufbar: 13 × 404, 1 × 410
  (6(3) #2 `10774878`, gelöscht). Die 404er kommen in Serien
  (6(4) #9–#11, #15, #16; 7(3) λ11–λ15 = `15332813…927`; 8(3) §7/§8;
  7(1) λ2) — Muster von **reservierten, nie veröffentlichten DOIs**.
- **Echtes JSON wie angenommen**: `files` ist eine Liste mit `key`, `size`,
  `checksum`, `links.self`; `metadata.title`, `metadata.resource_type`
  (`type`/`subtype`), `conceptrecid`, `conceptdoi`.
- **169 der 198 Records sind über die Concept-DOI zitiert** — Zenodo
  antwortet mit der neuesten Version (`775019 → 292975`). Das ist gewollt und
  erklärt auch 1(3) #1: `775019` (Vol 1) und `292975` (`pub`) sind dasselbe
  Werk, Concept- und Versions-DOI.
- **39 Records ohne PDF** (Software- und Daten-Releases) — dort keine Vorschau.
- **Titelprüfung** fand die Kopierfehler: 1(6) #2 (`817469` ist ein
  IoT-Projektbericht; korrigiert auf `817496`), 1(3) #4 Labeling System
  (`2540522` gehört dem chronOntology-Vortrag 2016 — den hatte die Migration
  deshalb in den 2014er-Eintrag **verschluckt**; Migration korrigiert, Eintrag
  steht jetzt als 1(5) #2), 3(1) #12, 5(3) #6 / 5(5) #4, 8(1) §1. Übrige
  Treffer der Titelprüfung sind Kurztitel oder GitHub-Release-Namen, kein Fehler.
- **Ortsvorschläge**: von 54 Orten 51 mit Vorschlag; offensichtliche Fehlgriffe
  (Rom → Rome, Georgia; Athen → Athens, Georgia; LEIZA → Leitza, Spanien)
  hat die Länder-Gewichtung behoben. Weiter falsch bzw. leer: „RGK,
  Frankfurt am Mainz" (→ Flughafen in Russland), „DBM Bochum", „Alte
  Universität Heidelberg". Viele Vorschläge sind Städte statt Veranstaltungsorte.

### Nachbereitung 2026-10-06

Ortsranking überarbeitet, nachdem die erste Übernahme Fehler zeigte:
Reihenfolge der Suchbegriffe kommt aus den Begriffen selbst (der Cache
speichert sortiert und hatte „Bochum" vor „Deutsches Bergbau-Museum"
gestellt); Venue mit guter Namensähnlichkeit und Koordinaten +6; Bahnhöfe −8
(„U-Bahnhof Deutsches Bergbau-Museum"); Kandidaten mehr als 50 km von der
Stadt des Labels −8 („Hochschule für Technik und Wirtschaft" → HTW Berlin für
eine Dresdner Veranstaltung). Ergebnis: rund ein Dutzend Orte wechseln von der Stadt zum
Veranstaltungsort (u. a. Sapienza, UCC, University of Glasgow, RWTH,
Leibnizhaus, Wikimedia Deutschland).

## S4 — Merge und Normalisierung

**Ziel:** `data/derived/entries.json` — eine Liste, aus der alle weiteren
Schritte lesen; YAML gewinnt vor Zenodo, Zenodo füllt Lücken.

- SKOS-Typschema `content/vocab/types.yaml` (Slug, Labels EN/DE, Mapping
  COAR / Zenodo / FaBiO), alle Handlabel aus Befund 5 abgedeckt.
- Personen-Normalisierung über ORCID (aus YAML und Zenodo `creators`).

**Abnahme:** Jede Entry hat Typ, mind. einen Creator, Jahr, IRI; Konflikte
YAML↔Zenodo stehen im Bericht.

### Erledigt 2026-10-07

`py/step_merge.py` und `content/vocab/types.yaml`. Ergebnis
`data/derived/entries.json` (≈ 2 MB, vor allem Abstracts), Bericht
`dist/reports/merge.md`. Zwei Läufe byte-gleich; `--strict` läuft durch.

**Zahlen:** 244 Einträge (210 veröffentlicht, 34 Drafts), 112 Personen
(76 mit ORCID), 55 Orte. 162 veröffentlichte Einträge haben eine
PDF-Vorschau. Haupttypen: 91 Vorträge, 26 Daten, 22 Poster, 21 Software.

**Befunde:**
- 28 Einträge bekamen ihren Typ aus Zenodo (die typlosen aus Vol 1–4); einer
  bleibt `other`.
- **Concept-DOI-Datumsfalle:** 11 Einträge hätten das Datum der neuesten
  Version bekommen (2(2) #1: 2024 statt 2020) — jetzt abgefangen (A4).
- **Namen auf Zenodo sind nicht sauberer als im Markdown:** „Dr. Allard Mees,
  FSA" als Name, „Dr. Kasten Tolle" (Tippfehler für Karsten), „Allard W.,
  Mees" vertauscht. Deshalb die Häufigkeitsregel statt „Zenodo gewinnt".
- 6 Schreibweisen ohne ORCID zusammengeführt (Distel, Kasten, Mennenga,
  Visser, Alpino, …). Getrennt geblieben, weil verschiedene Personen:
  Florian/Peter/Susanne Thiery, Agnes/Nico Schneider.
- Offen im Bericht: „Bernhard Weisser" passt zu zwei ORCIDs; „Wolf, D.G."
  (Vol 4(1) #2) ist vermutlich Wigg-Wolf; „Quintana, Miguel Angel Dilena"
  hat einen Doppelnachnamen, den die Regel nicht erkennt.

## S5 — Seiten

**Ziel:** `docs/` enthält alle HTML-Seiten in EN und DE, im Look der alten
Website.

- Jinja2-Templates; Entry-Seite mit Metadaten, Zitierbox, Downloads,
  Zenodo-Preview-`iframe` (`https://zenodo.org/records/<id>/preview/<datei>`),
  JSON-LD im `<head>`.
- Rahmenseiten: Home, About, Volumes & Issues, Impressum, Datenschutz.

**Abnahme:** Linkprüfung über `docs/` ohne tote interne Links; jede Entry aus
`entries.json` hat genau eine Seite je Sprache.

### Erledigt 2026-10-07

`py/step_site.py`, Templates unter `py/templates/` (`base`, `_macros`,
`home`, `volumes`, `volume`, `issue`, `entry`, `page`), `content/ui.yaml`,
`content/pages/*.html`, `assets/img/network.svg` (Netzwerk-Hintergrund,
einmal deterministisch erzeugt, Seed 2750560) und Seiten-CSS in
`assets/css/sqp.css`.

**Ergebnis:** 524 Seiten (210 Einträge × 2 Sprachen, dazu Bände, Hefte,
Übersicht, Impressum, Datenschutz), ≈ 8,5 MB. Linkprüfung über alle Seiten im
Build: keine toten internen Links. Zwei Läufe: `docs/` byte-gleich.
Screenshots (Playwright, hell/dunkel, 1280 px und 390 px): kein horizontales
Scrollen.

**Befunde:**
- Die Linkprüfung fand sofort einen Migrationsfehler: 7(2) λ2 hatte als
  Release-Link `[TODO](https://…` — korrigiert in `content/vol7.yaml`.
- Jinja liest `t.copy` als Dict-Methode, auf der Seite stand „<built-in
  method copy …>" — Schlüssel umbenannt, Build-Wächter eingebaut (A4).
- Heft-Titel gab es nur englisch; für die 32 Hefte mit Titel steht jetzt
  zusätzlich `de:` in `content/vol*.yaml`.
- Lange Abstracts drückten Zitierbox und Vorschau weit nach unten; Reihenfolge
  auf der Entry-Seite jetzt: Zitation → Vorschau → Abstract.

**Ansehen:** lokal mit `python main.py --serve`; online, sobald GitHub Pages
auf „Deploy from a branch: main, /docs" steht (die Action kommt in S11).

## S6 — Zitation

**Ziel:** Zitiervorschlag mit Stilwahl und Exporte je Entry, Issue, Volume.

- CSL-JSON je Entry; citeproc-js + gewählte CSL-Stile + Locale `en-GB`/`de-DE`
  liegen unter `assets/` (kein CDN beim Build).
- Zitierform übernimmt das Sigel: `Squirrel Papers 7(4), λ5`.
- BibTeX (Form wie `vol7/bibtex.md`, Schlüssel `sp_vol7_iss4_e5`), RIS.

**Abnahme:** BibTeX parst mit `bibtexparser` ohne Fehler; Stichprobe gegen
`vol7/bibtex.md` stimmt inhaltlich.

### Erledigt 2026-10-07

`py/step_cite.py`, `assets/js/sqp-cite.js`, `assets/vendor/` (citeproc-js
2.4.63, CSL-Styles @ `0151fd1`, Locales @ `a89adec`). Anpassungen an
`step_site.py`, den Templates (Stil-Auswahl, Downloads auf Entry-, Heft-,
Band- und Übersichtsseite), `step_merge.py` (Sprachschätzung) und
`migrate_parsers.py` (Dialekt 4).

**Ergebnis:** 210 Einträge je als BibTeX, RIS, CSL-JSON; dazu je Heft und
Band BibTeX/RIS und das ganze Journal als `dist/squirrelpapers.{bib,ris,csl.json}`
(auch unter `docs/downloads/`). pybtex liest alle 210 Einträge (203 article,
7 inproceedings). Browser-Test (Playwright): alle 6 Stile auf EN- und
DE-Seiten, keine Konsolenfehler, keine Anfragen an Dritte. Zwei Läufe
byte-gleich. JavaScript auf Entry-Seiten: ≈ 1,4 MB (citeproc 0,97 MB, Stile
und Locales 0,46 MB), wird einmal geladen und gecacht.

**Befunde:**
- **7(4) λ5 kam als `@inproceedings` mit dem Journal als Buchtitel** heraus:
  `vol7/bibtex.md` hat auch für λ5 einen Block (ein `@article`), und die
  Migration hatte ihn als `container` übernommen. Nur `@inproceedings` zählt
  jetzt als Tagungsband. Inhaltlicher Abgleich mit `vol7/bibtex.md`: gleich,
  bis auf den Monat (Sep. statt Okt.: Event 30.9.–1.10., genommen wird der
  Beginn).
- **Vertauschter Herausgeber** „Paul, Groth" in einem CoRDI-Container
  (seit S2 im Bericht): in `content/vol7.yaml` korrigiert.
- **114 von 210 Einträgen ohne Sprache** → Chicago/MLA setzten deutsche
  Titel in Title Case. Jetzt geraten: 51 × en, 20 × de; 43 bleiben offen
  (meist Software-/Datentitel ohne Funktionswörter).
- **Ein vierter Markdown-Dialekt:** 8(3) §9 hatte Typ und Sprache als
  shields.io-Badges vor dem Titel, der Titel bestand aus Badge-Markdown. Von
  Hand in `content/vol8.yaml` korrigiert, Parser kennt das Muster jetzt (falls
  je wieder migriert wird). Kein weiterer Titel hat Markup-Reste.
- IEEE und Vancouver setzen eine Listennummer „[1]" vor den Eintrag — wird
  für die Einzelanzeige entfernt, damit sie nicht mitkopiert wird.

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

### Erledigt 2026-10-07

`py/step_rdf.py`, `ontology/sqp.ttl` (5 Properties: `sqp:sigil`,
`sqp:entryNumber`, `sqp:citationLabel`, `sqp:specialIssue`,
`sqp:languageGuessed`). Anpassungen: `sqp_utils.py` (Präfixe, `PLACE_NS`,
`ORG_NS`, `bind_remaining`), `step_merge.py` (Dateinamen URL-kodiert),
`step_site.py` (`<link rel="alternate">` auf Turtle/JSON-LD, Downloads).

**Ergebnis:** `dist/squirrelpapers.ttl` 12 374 Tripel, `-crm.ttl` 6 185,
`vocab/types.ttl` 234, `ontology/sqp.ttl` 48. 210 Einträge, 106 Personen,
70 Veranstaltungen, 51 Orte. 259 Ressourcen (Journal, 8 Bände, 40 Hefte,
210 Einträge) mit eigenem `index.ttl` und `index.jsonld` in `docs/`; die
Seiten verweisen per `<link rel="alternate">` darauf — Vorstufe der Content
Negotiation in S12. Keine Blank Nodes, zwei Läufe byte-gleich, Laufzeit ≈ 6 s.

**Befunde:**
- **rdflib-Falle:** `Namespace` ist ein `str`, also war `DCTERMS.title` die
  String-Methode `str.title` — der erste Lauf brach mit „Predicate <built-in
  method format …>" ab. Durchgängig `N["dct"]["title"]`.
- **Dateinamen mit Leerzeichen** auf Zenodo (`OL3DT _Oldenburg_….pdf`) ergaben
  ungültige IRIs; S4 kodiert sie jetzt (betrifft auch Download- und
  Vorschau-Links auf den Seiten).
- **Kürzen vor dem Jahr:** die erste Event-IRI schnitt lange Namen nach dem
  Anhängen des Datums ab und verschmolz CAA-UK 2018 mit 2019. Jetzt erst
  kürzen, dann Jahr anhängen; Serien wie „Text+ Show and Tell" 2025 bleiben
  drei Veranstaltungen.
- 7 Einträge haben weder PDF noch DOI noch Link und daher keine
  Distribution — für DCAT-AP zulässig (0..n), S8 prüft es trotzdem.

## S8 — SHACL

**Ziel:** Gate gegen eigene Shapes und die DCAT-AP-3-Shapes (kopiert nach
`data/raw/shapes/`).

**Abnahme:** `python main.py --strict` scheitert bei einer absichtlich
kaputten Entry und läuft ohne sie durch.

### Erledigt 2026-10-07

`py/step_validate.py`, `shapes/{sqp-shapes,crm-shapes,axioms,selftest}.ttl`,
DCAT-AP 3.0.1 unter `data/raw/shapes/dcat-ap-3.0.1/` (Commit `4470b8e`,
CC BY 4.0). Anpassungen in `step_rdf.py` (Typisierungen, kein `dct:hasPart`
am Katalog, Repository-Link als Distribution).

**Ergebnis:** DCAT-AP 3.0.1, Journal-Regeln und CRM-Regeln je **0 Verstöße,
0 Warnungen**. Selbsttest grün. Laufzeit ≈ 6 s. Bericht
`dist/reports/validation.md`. Abnahme geprüft: ein zusätzlich eingefügtes
Zitierlabel liefert 2 Verstöße und `--strict` bricht ab; eine entschärfte Regel
(Muster des Zitierlabels entfernt) lässt den Selbsttest scheitern.

**Befunde:**
- **DCAT-AP 3.0.1 ist so nicht ladbar:** `ranges.ttl` verweist auf
  Property-Shapes aus `dcat-ap-SHACL.ttl` (beide müssen zusammen geladen werden),
  und 5 `sh:property`-Verweise zeigen auf Shapes, die es in keiner der Dateien
  gibt. pyshacl bricht daran ab. Die Dateien bleiben unverändert; die 5
  Verweise werden beim Laden übersprungen und im Bericht aufgeführt. Wäre ein
  Issue bei SEMICeu/DCAT-AP wert.
- **Erster Lauf: ≈ 1 300 DCAT-AP-Verstöße**, alle `sh:class` auf Objekten
  (Personen nicht als `foaf:Agent`, Typen nicht als `skos:Concept`, Sprachen,
  Medientypen, Landing Pages). Gelöst über Axiome und Typisierung (A4).
- **Echter Modellierungsfehler:** `dct:hasPart` vom Journal zu den Bänden —
  DCAT-AP reserviert das am Katalog für Unterkataloge. Entfernt; die Bände
  hängen über `dcat:dataset` und `dct:isPartOf` am Journal.
- 7 Software-Releases ohne DOI hatten keine Distribution; jetzt der
  Release-/Repository-Link als `#landing`.
- 43 Titel ohne bekannte Sprache tragen kein Sprach-Tag — erlaubt; die Regel
  verlangt das Tag nur, wenn `dct:language` bekannt ist.

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

## S14 — Eintragseditor im Web (neues Repo)

**Ziel:** Ein neuer Eintrag entsteht, ohne YAML von Hand zu schreiben: eine
statische Webseite mit Formular erzeugt einen YAML-Schnipsel, der genau in
`content/vol<N>.yaml` passt und dort per Werkzeug eingetragen wird.

**Uploads:** `PRIMER.md`; das Repo dieses Journals holt Claude selbst.

**Ablauf (Vorschlag):**

```
DOI eingeben ─► Zenodo-API im Browser (CORS) ─► Titel, Personen + ORCID,
                                                 Datum, Typ, Sprache, Lizenz
Band/Heft wählen ◄── entries.json von squirrelpapers.github.io
                     (nächste freie Nummer, Sigel des Hefts)
Veranstaltung ─► Ort per Wikidata-Suche (wbsearchentities, origin=*)
                 oder aus content/places.yaml wählen
        │
        ▼
YAML-Schnipsel (+ ggf. neuer places.yaml-Eintrag) ─► kopieren / herunterladen
        │
        ▼
Einreichen (S14b, siehe Teil D 7): Issue-Formular, Pull Request oder CLI
```

- **S14a — Format festschreiben (in diesem Repo):** JSON Schema
  `content/schema/entry.schema.json` aus dem tatsächlichen YAML-Format, plus
  `python main.py check`, das alle `content/vol*.yaml` dagegen prüft. Der
  Editor und dieses Repo validieren gegen dieselbe Datei.
- **S14b — Einreichen (beschlossen 2026-10-07):** Kern ist
  `python main.py add <schnipsel.yaml>` in diesem Repo — prüft gegen das Schema,
  vergibt bei Bedarf die nächste freie Nummer, sortiert in
  `content/vol<N>.yaml` ein, lässt `--strict` laufen. Obendrauf ein
  Issue-Formular; eine Action ruft dasselbe `add` auf und öffnet einen Pull
  Request. Der Editor öffnet das vorausgefüllte Issue (kein Token im Browser).
- **Bearbeiten:** Der Editor lädt einen bestehenden Eintrag (aus
  `entries.json` bzw. dem YAML) und erzeugt die Änderung auf demselben Weg;
  `add` kennt dafür einen Modus, der einen vorhandenen Eintrag ersetzt.
- **Zenodo nur als Anreicherung:** Alle Felder sind von Hand ausfüllbar; die
  DOI-Abfrage füllt nur leere Felder vor und ist abschaltbar. Ohne Netz zu
  Zenodo funktioniert alles.
- Typen aus `content/vocab/types.yaml`, UI zweisprachig wie die Seite, Look
  der Squirrel Papers.

**Abnahme:** Für drei vorhandene Einträge (ein Vortrag, ein Software-Release,
ein CoRDI-Beitrag) erzeugt der Editor aus der DOI einen Schnipsel, der nach
dem Einfügen `python main.py --strict` besteht und dieselbe Eintragsseite
ergibt wie heute.

## S15 — Frontend überarbeiten

**Ziel:** Aus den einzeln gewachsenen Seiten wird eine Website aus einem Guss.

**Uploads:** `PRIMER.md`; Screenshots oder Notizen von Flo, was stört.

- Navigation um Filter/Suche (S9), Karte (S10), SPARQL (S9) und „Daten"
  (Downloads, Ontologie, Vokabular) erweitern; Seiten für Personen und
  Veranstaltungen (die IRIs existieren seit S7).
- Startseite: aktuelle Einträge, Zahlen, Einstieg in Karte und Filter.
- Entry-Seite: Faktenspalte straffen (z. B. „Titel auf Zenodo" nur zeigen,
  wenn er wirklich abweicht), Typ-Badges, Personen verlinken.
- Barrierefreiheit (Kontraste, Fokus, Tastatur, Screenreader-Labels),
  Druck-CSS, OpenGraph/Social Cards, Favicon-Satz, 404-Seite.
- Performance: citeproc (≈ 1 MB) erst bei Bedarf laden.

**Abnahme:** Screenshot-Durchgang mit Flo (hell/dunkel, Desktop/Mobil) über
alle Seitentypen; Lighthouse Accessibility ≥ 95 auf Start-, Heft- und
Eintragsseite; keine toten Links.

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
3. ~~Vol 2–8 Jahreszuschnitt prüfen~~ → entschieden 2026-10-06: bleibt (A4).
4. ~~Neue Entries ab jetzt~~ → wird S14 (Eintragseditor), 2026-10-07; die Einreichung ist Punkt 7.
5. **Falsche DOIs (aus S3, `dist/reports/harvest.md` → „Shared DOIs")** — die
   richtige DOI kennt nur Flo: 1(3) #4 Labeling System 2014; 3(1) #12 ARS3D
   Comparison Videos; 5(3) #6 bzw. 5(5) #4 (beide „Semantic Modelling …",
   die DOI gehört dem Vortrag „Sharing (Linked) Open Data …"); 8(1) §1 From
   Tables to Gazetteers.
   *(Flo liefert die DOIs nach, Stand 2026-10-06.)*
5a. ~~14 nicht abrufbare DOIs~~ → 2026-10-06 als `draft` markiert (A4). Offen:
   veröffentlichen oder endgültig streichen. Insgesamt 34 `draft`-Einträge.
5b. ~~Orte~~ → 52 QIDs übernommen (A4). Für RGK (DAI am Palmengarten,
   Frankfurt am Main), DBM (Deutsches Bergbau-Museum Bochum) und Alte
   Universität (Heidelberger Innenstadt) stehen Suchhilfen in `places.yaml`;
   der nächste Harvest schlägt QIDs vor, die von Hand übernommen werden.
   → 2026-10-07 übernommen: Alte Universität Q436344, Deutsches
   Bergbau-Museum Q896952, RGK Q1425831 (mit `coordinates`, siehe A4). Alle
   55 Orte haben eine QID. Nebenbei: Q1425831 auf Wikidata P625 zu geben, würde
   die Ausnahme überflüssig machen.
5d. **Impressum und Datenschutz prüfen** — Entwürfe in `content/pages/`
   (S5). Vor allem: Ist die Anschrift richtig, braucht es eine
   Verantwortlichen-Angabe nach § 18 MStV, und was muss für S9 (Pyodide von
   einem CDN) und S10 (Kartenkacheln) noch hinein?
5c. **Autorenlisten (aus S4)** — 18 Einträge, bei denen Zenodo eine andere
   Zahl Personen nennt als `content/` (`dist/reports/merge.md`,
   `creator-count`). Soll Zenodo dort gewinnen? Derzeit gilt `content/` (A4,
   Vorschlag).
6. **DOI für Volumes/Issues** (Zenodo-Communities oder eigene Records)? Würde
   die Zitierfähigkeit der Issues verbessern.

7. ~~S14b — wie kommt ein Schnipsel ins Verzeichnis?~~ → entschieden
   2026-10-07: (b) als Kern, (a) obendrauf, dazu Bearbeiten (A4, Teil C S14).
   Ursprüngliche Optionen:
   (a) GitHub-Issue-Formular in diesem Repo, eine Action macht daraus einen
   Pull Request auf `content/vol<N>.yaml` (Editor öffnet das vorausgefüllte
   Issue; kein Token im Browser); (b) `python main.py add schnipsel.yaml` als
   CLI, das den Eintrag einsortiert und prüft; (c) eine wiederverwendbare
   Action in einem anderen Repo (z. B. einem Paper-Repo), die bei einem
   Release einen PR hierher schickt. Lassen sich kombinieren — (a) für das
   Formular, (b) als gemeinsamer Kern. Flo entscheidet.
