# eeg-incidence

Databricks lakehouse analysing the geographic incidence of German EEG payments — where the money flows, where the financing comes from, year by year from 2010 to today.

## Status

🚧 Work in progress. See [`docs/methodology.md`](docs/methodology.md) for the analytical approach and assumptions.

## The question

For each year between 2010 and today, which Bundesländer are net winners and losers from the German EEG (Erneuerbare-Energien-Gesetz) mechanism?

- **Flow A — Money in:** EEG payments received by renewable installations physically located in each Bundesland, derived from per-Anlage payment data joined to the Marktstammdatenregister.
- **Flow B — Money out:** Each Bundesland's pro-rata share of the financing burden. Two regimes:
  - 2010–2022: financed via the per-kWh EEG-Umlage on electricity bills → allocated by electricity consumption per Land.
  - 2023+: financed from the federal budget → allocated by federal-tax contribution per Land.
- **Net incidence per Land per year = Flow A − Flow B**, expressed in absolute €, € per capita, and € per kWh consumed.

## Stack

- **Databricks Free Edition** — Unity Catalog enforced, serverless compute only
- **Lakeflow Declarative Pipelines** — silver layer, with expectations as data tests
- **Auto Loader** — bronze layer ingest with schema evolution
- **Asset Bundles** — Infrastructure-as-Code for jobs and pipelines
- **MLflow** (optional, week 6 stretch) — forecast model tracking

## Repository layout

eeg-incidence/
├── README.md                    # This file
├── LICENSE                      # MIT (code only — data licenses differ, see below)
├── .gitignore                   # Excludes raw data, secrets, local Databricks state
├── pyproject.toml               # Python dependencies for ingest scripts and tests
│
├── ingest/                      # Code that runs OUTSIDE Databricks (local + GitHub Actions)
│   │                            # Pulls from public sources, lands files in UC Volume
│   ├── mastr/                   # Marktstammdatenregister bulk download via open-mastr
│   ├── jahresabrechnung/        # ÜNB EEG-Jahresabrechnung Bewegungsdaten (4 ÜNB × ~14 years)
│   ├── netztransparenz/         # OAuth-authenticated API calls (EEG-Konto, Finanzierungsbedarf)
│   └── destatis/                # Manual XLSX uploads (tax revenue, electricity consumption, population)
│
├── databricks/                  # Code that runs INSIDE Databricks
│   ├── databricks.yml           # Asset Bundle root — defines jobs, pipelines, targets
│   ├── resources/               # Bundle resource definitions
│   │   ├── pipelines.yml        # Lakeflow Declarative Pipeline configs
│   │   └── jobs.yml             # Job/workflow configs
│   ├── src/                     # Notebook and Python module sources
│   │   ├── bronze/              # Auto Loader notebooks per source (one per dataset)
│   │   ├── silver/              # @dlt.table modules building dim_* and fct_* tables
│   │   └── gold/                # Aggregation queries producing analytical outputs
│   └── dashboards/              # Lakeview dashboard JSON exports (version-controlled)
│
├── tests/                       # Local pytest suite for transformation logic
│   └── unit/                    # Pure-Python unit tests (no Spark required)
│
├── docs/                        # Project documentation
│   ├── methodology.md           # How Flow A and Flow B are computed; assumptions
│   ├── architecture.md          # Diagrams and design decisions
│   └── data-sources.md          # Catalogue of every external dataset used
│
└── data_inbox/                  # GITIGNORED — local-only, raw downloads before upload to UC Volume
# Never commit anything from here

## Layer responsibilities

The codebase is split into two halves with a deliberate boundary.

**Outside Databricks (`ingest/`):**
The Free Edition workspace has restricted outbound network access, so all external API calls and file downloads happen here — on your laptop or in GitHub Actions. Each ingest script's job is to fetch a public dataset, do minimal cleanup (e.g. unzip, normalise headers across the 4 ÜNB), and push the result to the `eeg_dev.raw_files.landing` Volume in Unity Catalog. Nothing in `ingest/` knows about Spark or DLT.

**Inside Databricks (`databricks/`):**
Once files land in the Volume, everything else — bronze, silver, gold, MLflow, dashboards — runs on Databricks compute. Bronze uses Auto Loader to pick up new files. Silver is a Lakeflow Declarative Pipeline that defines `dim_*` and `fct_*` tables with data quality expectations. Gold contains the analytical aggregates that power the dashboard.

## Unity Catalog structure

eeg_dev (catalog)
├── bronze (schema)             # Raw ingested data, one table per source dataset
├── silver (schema)             # Cleaned and conformed dim/fct tables
├── gold (schema)               # Analytical aggregates feeding the dashboard
└── raw_files (schema)
└── landing (volume)        # File landing zone — /Volumes/eeg_dev/raw_files/landing/

## Data sources and licenses

| Source | What it provides | License |
|---|---|---|
| Marktstammdatenregister (Bundesnetzagentur) | All renewable installations: location, capacity, technology, commissioning date | DL-DE-BY-2.0 |
| netztransparenz.de (4 ÜNB: 50Hertz, Amprion, TenneT, TransnetBW) | Per-Anlage annual EEG payments; EEG-Konto monthly statements | Public, attribution required |
| Destatis (Statistisches Bundesamt) | Tax revenue per Bundesland; electricity consumption per Land; population | Destatis terms (free reuse with attribution) |
| Suche-Postleitzahl.org / OpenPLZ | PLZ and Bundesland geometry for choropleth maps | Open data |

## Running locally

Once Week 0 setup is complete (Databricks Free Edition workspace + CLI configured + Volume created):

```bash
# Install ingest dependencies
pip install -e .

# Run a one-off ingest script (example: MaStR bulk to local CSVs)
python -m ingest.mastr.bulk_to_csv

# Upload to Databricks Volume
databricks fs cp data_inbox/mastr/ dbfs:/Volumes/eeg_dev/raw_files/landing/mastr/ --recursive
```

For Databricks-side code, deploy via the bundle:

```bash
cd databricks
databricks bundle validate
databricks bundle deploy --target dev
databricks bundle run pipeline_silver --target dev
```

## Methodology disclaimer

This project quantifies a politically charged question with public data. The headline finding — which Bundesländer are net winners or losers — depends materially on how Flow B is allocated, especially the 2023 regime change from per-kWh Umlage to federal-budget financing. All assumptions are documented in [`docs/methodology.md`](docs/methodology.md). Multiple denominators (absolute €, per capita, per kWh consumed) are presented in parallel rather than picking one definitive answer. Do not cite a single number from this project without its accompanying assumption.

## License

- **Code:** MIT (see `LICENSE`)
- **Data:** Each source has its own license — see the table above and `docs/data-sources.md`. The aggregated/derived datasets in `eeg_dev.gold.*` inherit the most restrictive upstream license, which in practice means attribution is required for any reuse.

## Author

Markus Friemann — Freelance Data Platform Architect — [The Coding Mentor](https://youtube.com) / [LinkedIn]