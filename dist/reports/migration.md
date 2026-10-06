# Migration report (S2)

Source: squirrelpapers-volumes @ `d00e0b7b5d76ba40eb5c335fffc99cc8d9de859c` (2026-04-18), florianthiery/pub @ `ac6636043ca06bff91c5ed9b84bd6622ee7f5b77`.

## Volumes

| Volume | Issues | Entries | of which draft | distinct DOIs |
|---|---|---|---|---|
| 1 | 7 | 41 | 0 | 41 |
| 2 | 3 | 5 | 0 | 5 |
| 3 | 4 | 18 | 0 | 17 |
| 4 | 4 | 31 | 10 | 20 |
| 5 | 6 | 26 | 0 | 24 |
| 6 | 5 | 52 | 5 | 45 |
| 7 | 5 | 47 | 0 | 45 |
| 8 | 6 | 23 | 5 | 14 |
| **all** | 40 | 243 | 20 | 212 |

## Volume 1 from florianthiery/pub

- items read (talks + posters, up to 2019): 37
- added as new entries: 32
- merged into an existing Vol 1 entry: 5
- already in a later volume, left there: 0

## DOI check

- Zenodo DOIs written anywhere in the old volumes (plain regex): 179
- DOIs read by the parser from the old volumes: 179
- DOIs in content/ (incl. related_dois and pub): 212
- set aside on purpose (link target disagreed with link text): 10.5281/zenodo.14886032, 10.5281/zenodo.817496
- **lost: 0**

## Places

54 distinct non-online locations written to `content/places.yaml`; 0 with a QID.

## Review list

| Kind | Count |
|---|---|
| `bibtex-editors` | 1 |
| `date-unparsed` | 1 |
| `doi-mismatch` | 2 |
| `doi-placeholder` | 12 |
| `doi-repeated` | 3 |
| `doi-typo` | 1 |
| `draft` | 20 |
| `empty-issue` | 5 |
| `no-bullet` | 4 |
| `no-type` | 39 |
| `orcid-name-filled` | 1 |
| `orcid-without-name` | 1 |
| `pub-cleanup` | 1 |
| `pub-title-elsewhere` | 1 |
| `pub-title-match` | 1 |

| Where | Kind | Detail |
|---|---|---|
| `volumes-md/vol7/bibtex.md` | `bibtex-editors` | editor spellings differ: {'Sure-Vetter, York and Groth, Paul': 6, 'Sure-Vetter, York and Paul, Groth': 1} |
| `volumes-md/vol7/index.md#L254` | `date-unparsed` | 26.04.2024 / 14.02.2024 |
| `pub/talks.md#L89` | `doi-mismatch` | link text and target differ: ['10.5281/zenodo.817469', '10.5281/zenodo.817496']; kept 10.5281/zenodo.817469 |
| `volumes-md/vol7/index.md#L127` | `doi-mismatch` | link text and target differ: ['10.5281/zenodo.14898291', '10.5281/zenodo.14886032']; kept 10.5281/zenodo.14898291 |
| `volumes-md/vol4/index.md#L112` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol4/index.md#L116` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol4/index.md#L132` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol4/index.md#L22` | `doi-placeholder` | not a DOI: 10.5281/zenodo.xyz |
| `volumes-md/vol4/index.md#L73` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol4/index.md#L77` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol4/index.md#L85` | `doi-placeholder` | DOI TBD |
| `volumes-md/vol6/index.md#L354` | `doi-placeholder` | not a DOI: 10.5281/zenodo.tbd |
| `volumes-md/vol6/index.md#L361` | `doi-placeholder` | not a DOI: 10.5281/zenodo.tbd |
| `volumes-md/vol6/index.md#L368` | `doi-placeholder` | not a DOI: 10.5281/zenodo.tbd |
| `volumes-md/vol6/index.md#L375` | `doi-placeholder` | not a DOI: 10.5281/zenodo.tbd |
| `volumes-md/vol6/index.md#L389` | `doi-placeholder` | not a DOI: 10.5281/zenodo.tbd |
| `10.5281/zenodo.10260778` | `doi-repeated` | same DOI in 2 entries: 5(3) #6, 5(5) #4 |
| `10.5281/zenodo.18441772` | `doi-repeated` | same DOI in 2 entries: 8(1) §1, 8(1) §4 |
| `10.5281/zenodo.5642976` | `doi-repeated` | same DOI in 2 entries: 3(1) #4, 3(1) #12 |
| `volumes-md/vol3/index.md#L41` | `doi-typo` | double dot repaired in '[10.5281/zenodo..5647827](https://doi.org/10.5281/zenodo..5647827)' |
| `volumes-md/vol4/index.md#L103` | `draft` | no DOI and no link: #10 Collaborative Writing: Using GitHub as a tool for collaborat |
| `volumes-md/vol4/index.md#L110` | `draft` | no DOI and no link: #12 Little Minions: Our little minions IV: small tools with majo |
| `volumes-md/vol4/index.md#L114` | `draft` | no DOI and no link: #13 Workflows and experiences on collaborative working and commu |
| `volumes-md/vol4/index.md#L130` | `draft` | no DOI and no link: #17 Daten schaffen Daten! Quellcode sind auch Forschungsdaten! |
| `volumes-md/vol4/index.md#L20` | `draft` | no DOI and no link: #2 How to handle vagueness and uncertainty in graph-based LOD k |
| `volumes-md/vol4/index.md#L24` | `draft` | no DOI and no link: #3 Master-Thesis alt |
| `volumes-md/vol4/index.md#L26` | `draft` | no DOI and no link: #4 Master-Thesis new |
| `volumes-md/vol4/index.md#L71` | `draft` | no DOI and no link: #2 Linked Pipes @ CAA SIG SSLA Meeting |
| `volumes-md/vol4/index.md#L75` | `draft` | no DOI and no link: #3 Linked Pipes @ Pelagios Network Annotation Activity Meeting |
| `volumes-md/vol4/index.md#L83` | `draft` | no DOI and no link: #5 Problem stories concerning thesaurus building and using cont |
| `volumes-md/vol6/index.md#L349` | `draft` | no DOI and no link: #1 Og(h)am from Ireland and the UK – Open Science and FAIR meth |
| `volumes-md/vol6/index.md#L356` | `draft` | no DOI and no link: #2 OG(H)AM in 3D-Digitisation, digital epigraphy and crosssecto |
| `volumes-md/vol6/index.md#L363` | `draft` | no DOI and no link: #3 OG(H)AM in 3D |
| `volumes-md/vol6/index.md#L370` | `draft` | no DOI and no link: #4 Og(h)am and Linked Open Data |
| `volumes-md/vol6/index.md#L384` | `draft` | no DOI and no link: #6 Ogham stones on OpenStreetMap |
| `volumes-md/vol8/index.md#L149` | `draft` | no DOI and no link: §1 CHUIS/1 |
| `volumes-md/vol8/index.md#L151` | `draft` | no DOI and no link: §2 GEARS/1 |
| `volumes-md/vol8/index.md#L153` | `draft` | no DOI and no link: §3 Jupyter Notebooks for Wikidata and LOD resources (FAIR Digit |
| `volumes-md/vol8/index.md#L155` | `draft` | no DOI and no link: §4 o3d-epidoc-extractor (FAIR Digital Object) |
| `volumes-md/vol8/index.md#L157` | `draft` | no DOI and no link: §5 ogham-analysis (FAIR Digital Object) |
| `vol2 issue 3` | `empty-issue` | no entries (TBD in the source, nothing from pub) |
| `vol3 issue 2` | `empty-issue` | no entries (TBD in the source, nothing from pub) |
| `vol3 issue 4` | `empty-issue` | no entries (TBD in the source, nothing from pub) |
| `vol8 issue 4` | `empty-issue` | no entries (TBD in the source, nothing from pub) |
| `vol8 issue 6` | `empty-issue` | no entries (TBD in the source, nothing from pub) |
| `volumes-md/vol4/index.md#L119` | `no-bullet` | F. Thiery; A.W. Mees; J.B. Kiesling |
| `volumes-md/vol4/index.md#L120` | `no-bullet` | 10.5281/zenodo.7105005 |
| `volumes-md/vol4/index.md#L88` | `no-bullet` | F. Thiery; A.W. Mees; K. Tolle; D.G. Wigg-Wolf |
| `volumes-md/vol4/index.md#L89` | `no-bullet` | 10.5281/zenodo.6043048 |
| `volumes-md/vol1/index.md#L15` | `no-type` | #1 Hic sunt dracones! The modern unknown data dragons |
| `volumes-md/vol1/index.md#L19` | `no-type` | #2 Archaeology 4.0: Archaeology in the Third Era of Computing |
| `volumes-md/vol1/index.md#L23` | `no-type` | #3 Sphere 7 Data: LOUD and FAIR Data for the Research Community |
| `volumes-md/vol1/index.md#L27` | `no-type` | #4 topi.link: the northern and southern ontology |
| `volumes-md/vol1/index.md#L31` | `no-type` | #5 SPARQLing Unicorn QGIS Plugin |
| `volumes-md/vol2/index.md#L15` | `no-type` | #1 The SPARQL Unicorn: An introduction |
| `volumes-md/vol2/index.md#L20` | `no-type` | #2 QGIS - A SPARQLing Unicorn? Eine Einführung in Linked Open G |
| `volumes-md/vol2/index.md#L27` | `no-type` | #1 Linked Open Samian Ware |
| `volumes-md/vol2/index.md#L31` | `no-type` | #2 Linked Open Samian Ware [RGZM/samian-lod: 2020-12-04] |
| `volumes-md/vol2/index.md#L35` | `no-type` | #3 Linked Open Samian Ware [RGZM/samian-lod: 2020-12-10] |
| `volumes-md/vol3/index.md#L15` | `no-type` | #1 Digitale Vernetzung von Sammlungsdaten |
| `volumes-md/vol3/index.md#L19` | `no-type` | #2 African Red Slip Ware digital (ARS3D) - The Portal |
| `volumes-md/vol3/index.md#L23` | `no-type` | #3 Linked Open African Red Slip Ware |
| `volumes-md/vol4/index.md#L103` | `no-type` | #10 Collaborative Writing: Using GitHub as a tool for collaborat |
| `volumes-md/vol4/index.md#L106` | `no-type` | #11 Hic sunt dracones - Real-world data-driven knowledge modelli |
| `volumes-md/vol4/index.md#L110` | `no-type` | #12 Little Minions: Our little minions IV: small tools with majo |
| `volumes-md/vol4/index.md#L114` | `no-type` | #13 Workflows and experiences on collaborative working and commu |
| `volumes-md/vol4/index.md#L118` | `no-type` | #14 Challenges in research community building: integrating Terra |
| `volumes-md/vol4/index.md#L122` | `no-type` | #15 NAVIS.one: Challenges and Opportunities for RSE and RDM by d |
| `volumes-md/vol4/index.md#L126` | `no-type` | #16 Typologie-Handling zur Dokumentation mit Hilfe künstlicher I |
| `volumes-md/vol4/index.md#L130` | `no-type` | #17 Daten schaffen Daten! Quellcode sind auch Forschungsdaten! |
| `volumes-md/vol4/index.md#L15` | `no-type` | #1 African Red Slip Ware - Additional Iconography Catalogue |
| `volumes-md/vol4/index.md#L20` | `no-type` | #2 How to handle vagueness and uncertainty in graph-based LOD k |
| `volumes-md/vol4/index.md#L24` | `no-type` | #3 Master-Thesis alt |
| `volumes-md/vol4/index.md#L26` | `no-type` | #4 Master-Thesis new |
| `volumes-md/vol4/index.md#L28` | `no-type` | #5 Software Review for the Software PointSamplingTool (Archäolo |
| `volumes-md/vol4/index.md#L38` | `no-type` | #1 Ceramic Typologies Ontology (CeraTyOnt) - Version v0.2 |
| `volumes-md/vol4/index.md#L42` | `no-type` | #2 CeraTyOnt @ AMT - Version v1.0 |
| `volumes-md/vol4/index.md#L46` | `no-type` | #3 Linked Pipe: Linked Open Samian Ware |
| `volumes-md/vol4/index.md#L67` | `no-type` | #1 How to navigate the coding archaeology world: An introductio |
| `volumes-md/vol4/index.md#L71` | `no-type` | #2 Linked Pipes @ CAA SIG SSLA Meeting |
| `volumes-md/vol4/index.md#L75` | `no-type` | #3 Linked Pipes @ Pelagios Network Annotation Activity Meeting |
| `volumes-md/vol4/index.md#L79` | `no-type` | #4 ARS3D: Close to the Original-Erfassung archäologischer Objek |
| `volumes-md/vol4/index.md#L83` | `no-type` | #5 Problem stories concerning thesaurus building and using cont |
| `volumes-md/vol4/index.md#L87` | `no-type` | #6 How to handle vagueness and uncertainty in graph-based LOD k |
| `volumes-md/vol4/index.md#L91` | `no-type` | #7 Challenges & Opportunities from real world archaeological da |
| `volumes-md/vol4/index.md#L95` | `no-type` | #8 Linked Open Time: Reproducible LOD-driven workflows and rese |
| `volumes-md/vol4/index.md#L99` | `no-type` | #9 Linked Pipes: A Little Minion for reproducible research |
| `volumes-md/vol8/index.md#L134` | `no-type` | §9 ![TYPE](https://img.shields.io/badge/TYPE-Talk-blue) ![TYPE] |
| `volumes-md/vol1/index.md#L62` | `orcid-name-filled` | 0000-0002-3246-3531 -> 'F. Thiery' |
| `volumes-md/vol1/index.md#L63` | `orcid-without-name` | ORCID 0000-0002-3246-3531 has no name next to it |
| `pub/talks.md#L77` | `pub-cleanup` | dropped 'with Allard Mees' from event name |
| `pub/talks.md#L81` | `pub-title-elsewhere` | same title as Vol 4(4) #2 (10.5281/zenodo.7361759), different DOI 10.5281/zenodo.1200111; added to Vol 1 anyway |
| `pub/poster.md#L45` | `pub-title-match` | same title as Vol 1(3) #1, different DOI 10.5281/zenodo.292975 vs 10.5281/zenodo.775019; kept as related_dois |
