import sqlite3

import pandas as pd

from rent_heatmap.db import export_tables, load_rent_observations
from rent_heatmap.transform import clean_rent_observations


def test_load_and_export_tables():
    raw = pd.DataFrame(
        {
            "reference_year": [2025],
            "geography_id": ["DT01"],
            "geography_name": ["Downtown Core"],
            "unit_type": ["1 Bedroom"],
            "average_rent": ["2500"],
            "vacancy_rate": [1.5],
            "unit_count": [1000],
        }
    )
    cleaned = clean_rent_observations(raw)

    connection = sqlite3.connect(":memory:")
    load_rent_observations(connection, cleaned)
    tables = export_tables(connection)

    assert len(tables["dim_geography"]) == 1
    assert len(tables["dim_unit_type"]) == 1
    assert len(tables["fact_rent_observation"]) == 1
    assert tables["vw_rent_map"].loc[0, "average_rent"] == 2500.0
