from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_table(path: str | Path, sheet_name: str | int | None = 0) -> pd.DataFrame:
    table_path = Path(path)
    suffix = table_path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(table_path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(table_path, sheet_name=sheet_name)
    if suffix == ".parquet":
        return pd.read_parquet(table_path)
    raise ValueError(f"Unsupported table format: {table_path.suffix}")


def write_powerbi_tables(tables: dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(out / f"{name}.csv", index=False)
