from __future__ import annotations

import argparse
from pathlib import Path

from .db import connect, export_tables, load_rent_observations
from .io import read_table, write_powerbi_tables
from .settings import load_settings
from .sources import discover_toronto_boundary_resources
from .transform import clean_rent_observations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Toronto rent heatmap ETL commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_sample = subparsers.add_parser("load-sample", help="Load bundled sample rent data.")
    load_sample.add_argument("--database", default="data/rent_heatmap.sqlite")

    load_cmhc = subparsers.add_parser("load-cmhc", help="Load a CMHC CSV/XLSX file into SQLite.")
    load_cmhc.add_argument("path", help="Path to a CMHC-derived normalized CSV/XLSX file.")
    load_cmhc.add_argument("--database", default="data/rent_heatmap.sqlite")
    load_cmhc.add_argument("--sheet-name", default=0)
    load_cmhc.add_argument("--config", default="config/sources.yml")

    export = subparsers.add_parser("export-powerbi", help="Export Power BI-ready CSV tables.")
    export.add_argument("--database", default="data/rent_heatmap.sqlite")
    export.add_argument("--output", default="exports/powerbi")

    discover = subparsers.add_parser("discover-boundaries", help="Search Toronto Open Data resources.")
    discover.add_argument("--query", default="neighbourhood boundary")

    return parser


def _load_frame_to_database(frame_path: Path, database: str, config: str, sheet_name: str | int = 0) -> None:
    settings = load_settings(config)
    frame = read_table(frame_path, sheet_name=sheet_name)
    cleaned = clean_rent_observations(
        frame,
        unit_mapping=settings.unit_type_mapping,
        suppression_markers=settings.suppression_markers,
    )
    with connect(database) as connection:
        load_rent_observations(connection, cleaned)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "load-sample":
        sample_path = Path("data/sample/rent_observations_sample.csv")
        _load_frame_to_database(sample_path, args.database, "config/sources.yml")
        print(f"Loaded sample rent observations into {args.database}")
        return 0

    if args.command == "load-cmhc":
        _load_frame_to_database(Path(args.path), args.database, args.config, args.sheet_name)
        print(f"Loaded CMHC rent observations into {args.database}")
        return 0

    if args.command == "export-powerbi":
        with connect(args.database) as connection:
            write_powerbi_tables(export_tables(connection), args.output)
        print(f"Exported Power BI tables to {args.output}")
        return 0

    if args.command == "discover-boundaries":
        for resource in discover_toronto_boundary_resources(query=args.query):
            print(f"{resource.package_name}\t{resource.format}\t{resource.resource_name}\t{resource.url}")
        return 0

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
