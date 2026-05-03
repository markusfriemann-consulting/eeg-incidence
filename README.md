# eeg-incidence

Databricks lakehouse analysing the geographic incidence of German EEG payments — where the money flows, where the financing comes from, year by year from 2010 to today.

## Status
🚧 Work in progress.

## Stack
- Databricks Free Edition (Unity Catalog, serverless)
- Lakeflow Declarative Pipelines
- Auto Loader
- Asset Bundles

## Data sources
- Marktstammdatenregister (Bundesnetzagentur) — DL-DE-BY-2.0
- netztransparenz.de (ÜNB) — EEG-Jahresabrechnung Bewegungsdaten
- Destatis — Steueraufkommen, Energiebilanzen, Bevölkerung

## Methodology
See `docs/methodology.md` (todo).

## License
Code: MIT. Data: see source-specific licenses linked above.
