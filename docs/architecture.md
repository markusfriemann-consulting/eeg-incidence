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
