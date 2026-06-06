import pandas as pd

from rent_heatmap.transform import clean_rent_observations, normalize_unit_type, parse_money


def test_normalize_unit_type_aliases():
    assert normalize_unit_type("Bachelor") == "Studio"
    assert normalize_unit_type("1 bedroom") == "1 Bedroom"
    assert normalize_unit_type("3 Bedroom +") == "3 Bedroom+"


def test_parse_money_handles_currency_and_suppression():
    assert parse_money("$2,450") == 2450.0
    assert parse_money("a") is None
    assert parse_money("--") is None


def test_clean_rent_observations_flags_suppressed_values():
    frame = pd.DataFrame(
        {
            "reference_year": [2025, 2025],
            "geography_id": ["DT01", "DT01"],
            "geography_name": ["Downtown Core", "Downtown Core"],
            "unit_type": ["Bachelor", "1 bedroom"],
            "average_rent": ["a", "$2,500"],
            "vacancy_rate": ["--", "1.5"],
            "unit_count": [100, 200],
        }
    )

    cleaned = clean_rent_observations(frame)

    assert cleaned.loc[0, "unit_type"] == "Studio"
    assert bool(cleaned.loc[0, "is_suppressed"])
    assert cleaned.loc[1, "average_rent"] == 2500.0
