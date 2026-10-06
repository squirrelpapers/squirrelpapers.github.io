# Squirrel Papers

Site generator for the **Squirrel Papers** (ISSN 2750-560X,
[Wikidata Q89658875](https://www.wikidata.org/wiki/Q89658875)), the Open Access
journal of the Research Squirrel Engineers Network for Linked Open Data,
Research Software Engineering, Cultural Heritage and the Geo-Sciences.

The journal is built from YAML: one page per volume, issue and entry, in
English and German, with suggested citations in several styles, BibTeX, a
DCAT 3 / DCAT-AP 3 graph with a CIDOC CRM bridge, SHACL validation, a browser
SPARQL page and a map of conference venues. Persistent identifiers follow the
pattern `https://w3id.org/squirrelpapers/v<volume>/i<issue>/e<entry>`.

> **Status:** under construction. The work plan, decisions and step status
> live in [`PRIMER.md`](PRIMER.md) (German).

## Usage

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

`python main.py --list` shows all steps. Two steps are not part of the default
run and are only executed when named: `migrate` (one-off import from the old
volumes) and `harvest` (the only step that reaches the network):

```cmd
python main.py --only harvest
```

Other options: `--only`, `--from`, `--skip`, `--dry-run`, `--strict` (what CI
runs), `--open`, `--serve`.

## Layout

| Path | Contents |
|---|---|
| `content/` | **source of truth**: `journal.yaml`, `vol<N>.yaml`, vocabularies |
| `data/raw/` | inputs as obtained: source snapshots, Zenodo and Wikidata cache |
| `data/derived/` | intermediate files (generated) |
| `dist/` | citable products: graph, GeoJSON, BibTeX, reports (generated) |
| `docs/` | the website served by GitHub Pages (generated) |
| `assets/` | stylesheet, logo and vendored scripts copied into `docs/` |
| `py/` | one module per step, `sqp_utils.py` for shared helpers |

Edit `content/`, never `docs/`.

## Licence

Code: [MIT](LICENSE). Journal metadata and texts: [CC BY 4.0](LICENSE-CONTENT).
The listed papers, posters, data and software carry their own licences on
their Zenodo records.

## Citation

See [`CITATION.cff`](CITATION.cff).
