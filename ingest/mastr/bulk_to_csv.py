"""Parse the MaStR bulk export and produce CSVs — full pipeline.

Uses parallelized processing. Assumes the ZIP is already at
~/.open-MaStR/data/xml_download/Gesamtdatenexport_20260503.zip.
"""
import os

# MUST be set BEFORE importing open_mastr — it reads the env var at import time
os.environ["USE_RECOMMENDED_NUMBER_OF_PROCESSES"] = "True"

import shutil
from pathlib import Path

from open_mastr import Mastr

SNAPSHOT = "20260503"
SNAPSHOT_ISO = f"{SNAPSHOT[:4]}-{SNAPSHOT[4:6]}-{SNAPSHOT[6:]}"

OUTPUT_ROOT = Path("data_inbox/mastr")

DOWNLOAD_CATEGORIES = ["wind", "solar", "biomass", "hydro", "market"]
CSV_EXPORT_CATEGORIES = ["wind", "solar", "biomass", "hydro", "market_actors"]


def main() -> None:
    output_dir = OUTPUT_ROOT / SNAPSHOT
    output_dir.mkdir(parents=True, exist_ok=True)

    db = Mastr()

    print(f"Parsing MaStR bulk for snapshot {SNAPSHOT} (parallelized)...")
    db.download(method="bulk", data=DOWNLOAD_CATEGORIES, date=SNAPSHOT)

    print(f"Exporting CSVs...")
    db.to_csv(tables=CSV_EXPORT_CATEGORIES)

    default_dir = Path.home() / ".open-MaStR" / "data" / f"dataversion-{SNAPSHOT_ISO}"
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