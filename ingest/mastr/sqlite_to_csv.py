"""Export already-parsed MaStR data from the local SQLite to CSVs.

Assumes the bulk parse has already happened (data exists in
~/.open-MaStR/data/sqlite/open-mastr.db). If you need to re-parse
from a fresh ZIP, use bulk_parse.py instead.
"""
import shutil
from pathlib import Path

from open_mastr import Mastr

SNAPSHOT = "20260503"

OUTPUT_ROOT = Path("data_inbox/mastr")

CSV_EXPORT_CATEGORIES = [
    "wind",
    "solar",
    "biomass",
    "hydro",
    "market_actors",
]


def main() -> None:
    output_dir = OUTPUT_ROOT / SNAPSHOT
    output_dir.mkdir(parents=True, exist_ok=True)

    db = Mastr()  # Connects to existing SQLite, no download triggered

    print(f"Exporting CSVs from existing SQLite database...")
    db.to_csv(tables=CSV_EXPORT_CATEGORIES)

    # open-mastr uses ISO date format (YYYY-MM-DD) for the output folder
    snapshot_iso = f"{SNAPSHOT[:4]}-{SNAPSHOT[4:6]}-{SNAPSHOT[6:]}"
    default_dir = Path.home() / ".open-MaStR" / "data" / f"dataversion-{snapshot_iso}"
    if not default_dir.exists():
        raise RuntimeError(f"Expected open-mastr output at {default_dir}, not found")

    moved = 0
    for csv_file in default_dir.glob("*.csv"):
        target = output_dir / csv_file.name
        shutil.move(str(csv_file), str(target))
        print(f"  {csv_file.name} -> {target}")
        moved += 1

    print(f"\nDone. {moved} CSVs ready in {output_dir}")


if __name__ == "__main__":
    main()