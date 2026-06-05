from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS dim_geography (
        geography_key INTEGER PRIMARY KEY AUTOINCREMENT,
        geography_id TEXT NOT NULL UNIQUE,
        geography_name TEXT NOT NULL,
        geography_group TEXT,
        latitude REAL,
        longitude REAL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dim_unit_type (
        unit_type_key INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_type TEXT NOT NULL UNIQUE,
        sort_order INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS dim_year (
        year_key INTEGER PRIMARY KEY,
        reference_year INTEGER NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fact_rent_observation (
        rent_observation_key INTEGER PRIMARY KEY AUTOINCREMENT,
        reference_year INTEGER NOT NULL,
        geography_id TEXT NOT NULL,
        unit_type TEXT NOT NULL,
        average_rent REAL,
        vacancy_rate REAL,
        unit_count INTEGER,
        is_suppressed INTEGER NOT NULL DEFAULT 0,
        source_name TEXT NOT NULL DEFAULT 'CMHC Rental Market Survey',
        FOREIGN KEY (geography_id) REFERENCES dim_geography(geography_id),
        FOREIGN KEY (unit_type) REFERENCES dim_unit_type(unit_type),
        FOREIGN KEY (reference_year) REFERENCES dim_year(reference_year)
    )
    """,
]

UNIT_SORT_ORDER = {
    "Studio": 1,
    "1 Bedroom": 2,
    "2 Bedroom": 3,
    "3 Bedroom+": 4,
    "Total": 5,
}


def connect(database: str | Path) -> sqlite3.Connection:
    db_path = Path(database)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def initialize_schema(connection: sqlite3.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()


def load_rent_observations(connection: sqlite3.Connection, rent_frame: pd.DataFrame) -> None:
    initialize_schema(connection)
    geographies = rent_frame[["geography_id", "geography_name"]].drop_duplicates().copy()
    geographies["geography_group"] = None
    geographies["latitude"] = None
    geographies["longitude"] = None
    geographies.to_sql("_tmp_geography", connection, if_exists="replace", index=False)
    connection.execute(
        """
        INSERT OR IGNORE INTO dim_geography
            (geography_id, geography_name, geography_group, latitude, longitude)
        SELECT geography_id, geography_name, geography_group, latitude, longitude
        FROM _tmp_geography
        """
    )

    unit_types = pd.DataFrame(
        {
            "unit_type": sorted(rent_frame["unit_type"].dropna().unique(), key=lambda x: UNIT_SORT_ORDER.get(x, 99)),
        }
    )
    unit_types["sort_order"] = unit_types["unit_type"].map(lambda value: UNIT_SORT_ORDER.get(value, 99))
    unit_types.to_sql("_tmp_unit_type", connection, if_exists="replace", index=False)
    connection.execute(
        """
        INSERT OR IGNORE INTO dim_unit_type (unit_type, sort_order)
        SELECT unit_type, sort_order FROM _tmp_unit_type
        """
    )

    years = pd.DataFrame({"reference_year": sorted(rent_frame["reference_year"].dropna().unique())})
    years["year_key"] = years["reference_year"]
    years[["year_key", "reference_year"]].to_sql("_tmp_year", connection, if_exists="replace", index=False)
    connection.execute(
        """
        INSERT OR IGNORE INTO dim_year (year_key, reference_year)
        SELECT year_key, reference_year FROM _tmp_year
        """
    )

    fact = rent_frame.copy()
    fact["is_suppressed"] = fact["is_suppressed"].astype(int)
    fact[
        [
            "reference_year",
            "geography_id",
            "unit_type",
            "average_rent",
            "vacancy_rate",
            "unit_count",
            "is_suppressed",
        ]
    ].to_sql("fact_rent_observation", connection, if_exists="append", index=False)
    connection.commit()


def export_tables(connection: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    return {
        "dim_geography": pd.read_sql_query("SELECT * FROM dim_geography", connection),
        "dim_unit_type": pd.read_sql_query("SELECT * FROM dim_unit_type", connection),
        "dim_year": pd.read_sql_query("SELECT * FROM dim_year", connection),
        "fact_rent_observation": pd.read_sql_query("SELECT * FROM fact_rent_observation", connection),
        "vw_rent_map": pd.read_sql_query(
            """
            SELECT
                f.reference_year,
                g.geography_id,
                g.geography_name,
                g.geography_group,
                g.latitude,
                g.longitude,
                f.unit_type,
                f.average_rent,
                f.vacancy_rate,
                f.unit_count,
                f.is_suppressed
            FROM fact_rent_observation f
            JOIN dim_geography g ON f.geography_id = g.geography_id
            """,
            connection,
        ),
    }
