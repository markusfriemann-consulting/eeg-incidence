# eeg-incidence
 
Databricks lakehouse analysing the geographic incidence of German EEG payments in 2024 — which Bundesländer are net winners and which are net payers in the renewable energy subsidy system.
 
**Headline finding:** In 2024, Bayern is the largest absolute net winner (+€2.03 Bn), Nordrhein-Westfalen the largest net payer (−€1.85 Bn). Per capita, Mecklenburg-Vorpommern leads (+€398/inhabitant), Hamburg trails (−€368/inhabitant). About €2.07 Bn flows to offshore wind in the Ausschließliche Wirtschaftszone (AWZ) — paid for by all Bundesländer, received by none.
 
See [`docs/methodology.md`](docs/methodology.md) for the full methodology and `docs/eeg_2024_editorial.html` for the published infographic.
 
## The question, precisely
 
For 2024, separately for each of the 16 Bundesländer plus the offshore zone:
 
- **Vergütung erhalten** (Flow A) — the EEG payments received by renewable installations physically located in the Bundesland, derived from per-Anlage payment records of all 4 ÜNB joined to the Marktstammdatenregister
- **Finanzierungslast** (Flow B) — the Bundesland's pro-rata share of the federal budget transfer to the EEG-Konto, allocated by the Bundesland's contribution to federal tax revenue
- **Netto-Position = Flow A − Flow B**, expressed in absolute euros and per capita
The post-2022 EEG financing regime is straightforward: the Bundeshaushalt pays the difference between guaranteed Vergütungssätze and market revenue. Tax-contribution-based allocation reflects that legal mechanism directly. Why 2024 specifically? Because it's the first "normal" year after the 2022 energy-crisis surplus on the EEG-Konto was depleted — the structural cost is again borne by the federal budget rather than market windfalls.
 
## Why scope to 2024?
 
The original plan covered 2010–today. We narrowed to 2024-only because:
 
- The detailed per-Anlage Bewegungsdaten that drives Flow A is only published for the most recent settlement year. Older years are taken offline by netztransparenz.de under §51 EnFG.
- The 2023 EEG-Konto was unusually self-funding due to high market prices in 2022; not representative.
- Pre-2023 years used the EEG-Umlage on electricity bills, not the federal budget — that's a different methodology entirely.
The pipeline auto-extends each year when new Bewegungsdaten is published in September.
 
## Stack
 
- **Databricks Free Edition** — Unity Catalog enforced, serverless compute only
- **Auto Loader (`cloudFiles`)** — incremental file ingestion to bronze with schema evolution and metadata-based lineage
- **Delta Lake** — all bronze, silver, gold tables; ACID semantics, time travel, schema enforcement
- **PySpark + Spark SQL** — transformations across medallion layers (DataFrame API for parameterised pipelines, SQL for ad-hoc analysis)
- **Custom HTML/SVG infographics** — final published artefacts, hand-crafted in `docs/` for LinkedIn-quality output
Stretch-goal items from the original plan — Lakeflow DLT, Asset Bundles, MLflow — are deferred to future iterations.
 
## Architecture
 
```
┌──────────────────────────────────────────────────────────────────────┐
│                         OUTSIDE DATABRICKS                           │
│                                                                      │
│  ingest/mastr/        ingest/jahresabrechnung/   data_inbox/bmf/    │
│  open-mastr Python    Manual ZIP download        Manual XLSX        │
│  bulk parse → CSV     from netztransparenz.de    download           │
│       │                       │                       │              │
│       ▼                       ▼                       ▼              │
│            Databricks CLI: databricks fs cp                          │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  UNITY CATALOG: eeg_dev                              │
│                                                                      │
│  raw_files.landing (Volume)                                          │
│  ├── mastr/20260503/      → 7 CSVs (~5.3 GB)                        │
│  ├── jahresabrechnung/2024/                                          │
│  │   ├── 50hertz/         → 2 CSVs                                   │
│  │   ├── amprion/         → 14 CSVs                                  │
│  │   ├── tennet/          → 4 CSVs                                   │
│  │   └── transnetbw/      → 2 CSVs (~530 MB total)                   │
│  ├── bmf/                 → BMF Übersicht 5a (Steueraufkommen)       │
│  └── destatis/            → Bevölkerung 2024                         │
│                  │                                                   │
│                  ▼ Auto Loader (cloudFiles)                          │
│                                                                      │
│  bronze.*  (raw, all-string, append-only)                            │
│  ├── mastr_solar, _wind, _biomass, _hydro, _gsgk, _deleted_units     │
│  ├── mastr_market_actors                                             │
│  ├── ntp_jahresabrechnung_bewegungsdaten   (8.18 M rows, 4 ÜNB)      │
│  ├── bmf_steueraufkommen_bund_2024                                   │
│  └── destatis_bevoelkerung_2024                                      │
│                  │                                                   │
│                  ▼ PySpark transformations (cast, normalise, join)   │
│                                                                      │
│  silver.* (typed, conformed, business-friendly)                      │
│  ├── dim_anlage                            (6.15 M renewable units)  │
│  ├── dim_bundesland                        (17 rows: 16 + AWZ)       │
│  ├── fct_eeg_zahlung_jaehrlich             (matched: 99.7% by €)     │
│  └── fct_eeg_zahlung_jaehrlich_unmatched   (quarantine)              │
│                  │                                                   │
│                  ▼ Aggregations + Flow B allocation                  │
│                                                                      │
│  gold.* (analytical aggregates)                                      │
│  ├── netto_incidence_per_land_2024         (the headline)            │
│  └── bundesland_overview_2024              (wide table for vis)      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        VISUALISATIONS                                │
│                                                                      │
│  docs/eeg_2024_editorial.html         — Editorial infographic        │
│  docs/eeg_2024_technology_breakdown.html — Stacked bars by tech      │
└──────────────────────────────────────────────────────────────────────┘
```
 
## Data sources
 
| Source | Provides | Volume in lakehouse |
|---|---|---|
| Marktstammdatenregister (BNetzA) | Every German renewable installation: location, capacity, technology, EEG/Mast IDs | 5.3 GB CSV → 6.15 M rows in `silver.dim_anlage` |
| EEG-Bewegungsdaten 2024 (4 ÜNB: 50Hertz, Amprion, TenneT, TransnetBW) | Per-Anlage annual EEG payment records | 530 MB CSV → 8.18 M rows in bronze |
| BMF Übersicht 5a (Q4 2024) | Bund-Anteil der Steuern per Bundesland 2024 | 1 KB CSV → 16 rows |
| Destatis | Bevölkerung per Bundesland (Stand 31.12.2024) | 1 KB CSV → 16 rows |
 
All sources are public. License details in `docs/data-sources.md`.
 
## Pipeline walkthrough
 
### Bronze: ingest with Auto Loader
 
Files land in the `eeg_dev.raw_files.landing` Volume via `databricks fs cp` from the local `ingest/` scripts. Each bronze notebook reads from a Volume path with `cloudFiles` format, writes to a Delta table, and tracks processed files via a checkpoint.
 
Two bronze notebooks:
 
- `bronze/mastr_bronze.py` — 7 MaStR categories (solar, wind, biomass, hydro, gsgk, market_actors, deleted_units). Schema hints force `Gemeindeschluessel` and `Postleitzahl` to string (avoids inference picking int from sample, then failing on Austrian codes like `'A-6793'` or PLZ leading zeros).
- `bronze/jahresabrechnung_bronze.py` — All 4 ÜNB unified into one table `ntp_jahresabrechnung_bewegungsdaten`. Header normalisation (lowercase + transliteration) handles inconsistencies: Amprion uses UPPERCASE, TenneT uses real umlauts (`ü`, `ä`, `ß`), the others use ASCII (`ue`, `ae`, `ss`).
- `bronze/flow_b_bronze.py` — Two small static reference files (BMF Steueraufkommen, Destatis Bevölkerung), read directly without Auto Loader.
All bronze tables keep columns as STRING; type casting happens in silver to maintain replay-ability.
 
### Silver: clean, type, conform
 
Three silver outputs:
 
- `silver/dim_anlage.py` — Unifies the 5 technology bronze tables into one 16-column dimension via `unionByName`. Renames German MaStR columns to project conventions (`EinheitMastrNummer` → `mastr_nummer`, `Bruttoleistung` → `brutto_leistung_kw`, etc.). Casts capacity to double, dates to date. Filters NULL Bundesland for onshore Anlagen but **preserves offshore wind** (which is registered without a Bundesland) by relabelling them as `"Ausschließliche Wirtschaftszone"`. Capacity reconciles to BNetzA published numbers within ±5%: solar 100 GW (correct, Germany passed 100 GW PV in late 2024), wind 62.5 GW (incl. offshore), biomass 8.8 GW, hydro 4.6 GW (excl. Pumpspeicher).
- `silver/fct_eeg_zahlung_jaehrlich.py` — Aggregates per-Anlage payments from bronze, casts German decimals (`'1054,35'` → `1054.35`), filters Veräußerungsform=5 (bookkeeping-only), and joins to `dim_anlage` with a **dual-key fallback**: matches on `eeg_mastr_nummer` (EEG... prefix) OR on `mastr_nummer` (SEE... prefix). Achieves 99.68% match by € across €22.67 Bn total payments. Unmatched rows go to a quarantine table.
- `silver/dim_bundesland.py` — Joins BMF tax revenue per Bundesland (€185.7 Bn total Bund-Anteil) with population (~83.6 M total). Computes `bund_anteil_share` per Land. Adds an offshore (AWZ) row with NULL values so it aligns with `dim_anlage`'s geography.
### Gold: the analytical answer
 
Two gold tables drive the entire dashboard:
 
- `gold/netto_incidence_per_land_2024.py` — The headline. Joins Flow A (sum of `verguetung_eur` per Bundesland from silver fct) with Flow B (€18.49 Bn × `bund_anteil_share` per Bundesland). Computes `netto_position_eur` and per-capita variants.
- `gold/bundesland_overview_2024.py` — Wide table with per-technology breakdown (solar/wind/biomass/hydro/gsgk in € and capacity), Anlagen counts, ISO 3166-2 codes, and all the netto numbers — a single denormalised source for the visualisation layer.
### Visualisations
 
Two standalone HTML files in `docs/` produce the published artefacts:
 
- `docs/eeg_2024_editorial.html` — Editorial-style infographic. Trophies for top 3 winners (Bayern, Niedersachsen, Brandenburg), inverted-trophy markers for top 3 payers (NRW, Hessen, Berlin), and an offshore-wind callout. Rendered at 1080×1620 for LinkedIn.
- `docs/eeg_2024_technology_breakdown.html` — Horizontal stacked bar chart of EEG payments per Bundesland by technology (solar/wind/biomass/hydro/geothermie). Sorted by total payments descending.
Both are pure SVG inside HTML — no JS framework, no compilation. Open the file in a browser, screenshot for posting.
 
## Repository layout
 
```
eeg-incidence/
  README.md                    This file
  LICENSE                      MIT (code only — data licenses differ)
  .gitignore                   Excludes raw data, secrets, local Databricks state
  pyproject.toml               Python dependencies for ingest scripts and tests
 
  ingest/                      Code that runs OUTSIDE Databricks
    mastr/                     open-mastr bulk parse + SQLite-to-CSV export
      bulk_to_csv.py           Triggers the bulk download/parse + CSV export
      sqlite_to_csv.py         Re-exports CSVs from existing SQLite
    jahresabrechnung/          Inspection scripts for the 4 ÜNB ZIP downloads
 
  databricks/                  Code that runs INSIDE Databricks
    src/
      bronze/
        mastr_bronze.py        Auto Loader for 7 MaStR categories
        jahresabrechnung_bronze.py   Auto Loader for 4 ÜNB unified table
        flow_b_bronze.py       Static reference files (BMF, Destatis)
      silver/
        dim_anlage.py          6.15 M renewable installations
        dim_bundesland.py      17 Bundesländer (incl. AWZ) with tax + pop
        fct_eeg_zahlung_jaehrlich.py  Per-Anlage payments joined to dim
      gold/
        netto_incidence_per_land_2024.py    Flow A − Flow B
        bundesland_overview_2024.py         Wide visualisation source
 
  docs/                        Documentation and visual artefacts
    methodology.md             Detailed methodology and disclaimers
    architecture.md            Diagrams and design decisions
    data-sources.md            Catalogue of external datasets
    eeg_2024_editorial.html    Published infographic
    eeg_2024_technology_breakdown.html   Stacked bars by technology
 
  data_inbox/                  GITIGNORED — raw downloaded data lives here
    mastr/<snapshot>/          MaStR bulk export CSVs
    jahresabrechnung/          ÜNB ZIPs and extracted CSVs
    bmf/                       BMF Steueraufkommen XLSX/CSV
    destatis/                  Destatis Bevölkerung CSV
 
  tests/                       Local pytest suite for ingest scripts
```
 
## Unity Catalog structure
 
```
eeg_dev (catalog)
├── bronze (schema)
│   ├── mastr_solar, mastr_wind, mastr_biomass, mastr_hydro
│   ├── mastr_gsgk, mastr_market_actors, mastr_deleted_units
│   ├── ntp_jahresabrechnung_bewegungsdaten
│   ├── bmf_steueraufkommen_bund_2024
│   └── destatis_bevoelkerung_2024
├── silver (schema)
│   ├── dim_anlage
│   ├── dim_bundesland
│   ├── fct_eeg_zahlung_jaehrlich
│   └── fct_eeg_zahlung_jaehrlich_unmatched
├── gold (schema)
│   ├── netto_incidence_per_land_2024
│   └── bundesland_overview_2024
└── raw_files (schema)
    └── landing (Volume) — file landing zone at /Volumes/eeg_dev/raw_files/landing/
```
 
## Layer responsibilities
 
The codebase is split into two halves with a deliberate boundary.
 
**Outside Databricks (`ingest/`):** The Free Edition workspace has restricted outbound network access, so all external API calls and file downloads happen here — on a local machine. Each ingest script's job is to fetch a public dataset, do minimal cleanup (e.g. unzip ÜNB Bewegungsdaten archives, parse MaStR XML via `open-mastr`), and prepare CSVs in `data_inbox/`. Then `databricks fs cp` uploads them to the Volume. Nothing in `ingest/` knows about Spark.
 
**Inside Databricks (`databricks/`):** Once files land in the Volume, everything else — bronze, silver, gold — runs on Databricks serverless compute. Bronze uses Auto Loader to incrementally pick up files. Silver and gold are PySpark notebooks that materialise Delta tables. The visualisation layer is decoupled — it just reads the gold tables.
 
## Reproducing the lakehouse
 
Once Databricks Free Edition + CLI are configured (see Week 0 setup):
 
```bash
# 1. Install ingest dependencies
pip install -e .
 
# 2. Bulk-parse MaStR (~30-40 min, 5+ GB SQLite, do not interrupt)
python -m ingest.mastr.bulk_to_csv
 
# 3. Manually download Bewegungsdaten ZIPs from netztransparenz.de
#    See docs/data-sources.md for the exact URL and per-ÜNB filenames
 
# 4. Manually download BMF Steueraufkommen Übersicht 5a (Q4 2024)
#    and Destatis Bevölkerung 2024
 
# 5. Upload all files to UC Volume
databricks fs cp data_inbox/mastr/<snapshot>/ \
  dbfs:/Volumes/eeg_dev/raw_files/landing/mastr/<snapshot>/ --recursive
 
# (Repeat for jahresabrechnung, bmf, destatis)
 
# 6. In Databricks, run the notebooks in order:
#    bronze/mastr_bronze.py
#    bronze/jahresabrechnung_bronze.py
#    bronze/flow_b_bronze.py
#    silver/dim_anlage.py
#    silver/fct_eeg_zahlung_jaehrlich.py
#    silver/dim_bundesland.py
#    gold/bundesland_overview_2024.py
#    gold/netto_incidence_per_land_2024.py
```
 
Total runtime end-to-end: roughly 60-90 minutes on Free Edition serverless, dominated by the MaStR Auto Loader pass (~15-25 min for 5+ GB CSV).
 
## Key technical decisions
 
A handful of choices that meaningfully shaped the project:
 
**Single unified Bewegungsdaten table.** All 4 ÜNB are written to the same bronze table with a `_uenb` discriminator column rather than 4 separate tables. Simplifies silver (one source instead of four), enables `SELECT * GROUP BY _uenb` for sanity checks, and trivially extends to future years.
 
**Header normalisation at bronze read time.** Lowercasing column names and transliterating umlauts (`ü → ue` etc.) at the moment of reading from CSV, not in silver. Means downstream code never sees the inconsistencies between ÜNBs.
 
**Dual-key join in silver.** The Bewegungsdaten files use either EEG-prefixed (`EEG...`) or unit-prefixed (`SEE...`) IDs depending on the ÜNB and Anlagen-type. Joining on `eeg_mastr_nr = eeg_mastr_nummer OR eeg_mastr_nr = mastr_nummer` recovers the cases where one prefix matches but not the other.
 
**Offshore wind preserved with synthetic Bundesland.** Filtering NULL Bundesland would have dropped all offshore wind farms (in the AWZ, not in any state) — €2.07 Bn in 2024. Instead they're relabelled `"Ausschließliche Wirtschaftszone"` and become a separate row in `dim_bundesland`. The dashboard surfaces this explicitly.
 
**Veräußerungsform=5 filtered in silver.** Bookkeeping/correction entries have payment=0 by construction. Including them in the sum is harmless; excluding them is cleaner. Filtered before aggregation.
 
## Methodology disclaimer
 
This project quantifies a politically charged question with public data. Two important caveats:
 
- **The €18.49 Bn allocation is a model.** Each Bundesland's "Finanzierungslast" is computed as its share of the €185.7 Bn Bund-Anteil multiplied by the actual €18.49 Bn EEG transfer. This treats EEG financing as proportionally drawn from each Land's tax contribution — defensible but a model, not a measurement.
- **Receipts vs. burden are different concepts.** The sum across all Bundesländer of `verguetung_erhalten_eur` (€22.67 Bn) exceeds the sum of `finanzierungslast_eur` (€18.49 Bn) by ~€4.2 Bn — the Vermarktungserlöse the ÜNB earn by selling EEG-generated electricity at the Strombörse. This is documented in [`docs/methodology.md`](docs/methodology.md).
Do not cite a single number from this project without its accompanying methodology page.
 
## License
 
- **Code:** MIT (see `LICENSE`)
- **Data:** Each upstream source has its own license — see `docs/data-sources.md`. The aggregated/derived datasets in `eeg_dev.gold.*` inherit the most restrictive upstream license, which in practice means attribution is required for any reuse.
## Author
 
Markus Friemann — Freelance Data Platform Architect — [LinkedIn]([https://linkedin.com/in/markusfriemann](https://www.linkedin.com/in/markus-friemann-221b3814b/))
