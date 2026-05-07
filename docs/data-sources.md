## Data sources
 
| Source | Provides | Volume in lakehouse |
|---|---|---|
| Marktstammdatenregister (BNetzA) | Every German renewable installation: location, capacity, technology, EEG/Mast IDs | 5.3 GB CSV → 6.15 M rows in `silver.dim_anlage` |
| EEG-Bewegungsdaten 2024 (4 ÜNB: 50Hertz, Amprion, TenneT, TransnetBW) | Per-Anlage annual EEG payment records | 530 MB CSV → 8.18 M rows in bronze |
| BMF Übersicht 5a (Q4 2024) | Bund-Anteil der Steuern per Bundesland 2024 | 1 KB CSV → 16 rows |
| Destatis | Bevölkerung per Bundesland (Stand 31.12.2024) | 1 KB CSV → 16 rows |
 
All sources are public. License details in `docs/data-sources.md`.
