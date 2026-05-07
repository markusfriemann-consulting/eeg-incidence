"""Export already-parsed MaStR data from the local SQLite to CSVs.

Assumes the bulk parse has already happened (data exists in
~/.open-MaStR/data/sqlite/open-mastr.db). If you need to re-parse
from a fresh ZIP, use bulk_to_csv.py instead.

Notes on snapshot date:
  - SNAPSHOT below is the LOGICAL snapshot date used for the project's
    Volume layout, NOT necessarily the date open-mastr last downloaded.
  - Open-mastr always writes its CSV output to ~/.open-MaStR/data/dataversion-<latest_iso>/
    where <latest_iso> is the date of its most recent download.
  - This script finds whatever dataversion-* folder open-mastr produced last
    and moves CSVs into our project's data_inbox/mastr/<SNAPSHOT>/ folder.
"""
import shutil
from pathlib import Path

from open_mastr import Mastr

# Logical snapshot for the project — keep aligned with what's already in UC Volume.
SNAPSHOT = "20260503"

OUTPUT_ROOT = Path("data_inbox/mastr")

# All categories needed for the EEG incidence project.
# After the bulk_to_csv re-run on 20260505, SQLite contains tables for all of these.
CSV_EXPORT_CATEGORIES = [
    "wind",
    "solar",
    "biomass",
    "hydro",
    "market_actors",
    "gsgk",            # Geothermie / Solarthermie / Grubengas / Klärgas
    "deleted_units",   # Decommissioned units (still in payment streams)
]


def find_latest_dataversion_dir() -> Path:
    """Find the most recent dataversion-* directory open-mastr produced."""
    base = Path.home() / ".open-MaStR" / "data"
    candidates = sorted(base.glob("dataversion-*"))
    if not candidates:
        raise RuntimeError(f"No dataversion-* directory found in {base}")
    return candidates[-1]   # newest by name (ISO date sorts naturally)


def main() -> None:
    output_dir = OUTPUT_ROOT / SNAPSHOT
    output_dir.mkdir(parents=True, exist_ok=True)

    db = Mastr()  # Connects to existing SQLite, no download triggered

    print(f"Exporting CSVs from existing SQLite database...")
    print(f"Categories: {CSV_EXPORT_CATEGORIES}")
    db.to_csv(tables=CSV_EXPORT_CATEGORIES)

    source_dir = find_latest_dataversion_dir()
    print(f"\nopen-mastr wrote to: {source_dir}")
    print(f"Moving CSVs to:      {output_dir}")

    moved = 0
    skipped = 0
    for csv_file in source_dir.glob("*.csv"):
        target = output_dir / csv_file.name
        if target.exists():
            print(f"  SKIP (already present): {csv_file.name}")
            skipped += 1
            continue
        shutil.move(str(csv_file), str(target))
        print(f"  MOVED: {csv_file.name}")
        moved += 1

    print(f"\nDone. {moved} CSVs moved, {skipped} skipped (already in destination).")
    print(f"Output directory contents:")
    for f in sorted(output_dir.iterdir()):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name}  ({size_mb:,.1f} MB)")


if __name__ == "__main__":
    main()