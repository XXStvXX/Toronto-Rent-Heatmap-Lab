from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

DEFAULT_UNIT_MAPPING = {
    "bachelor": "Studio",
    "studio": "Studio",
    "0 bedroom": "Studio",
    "1 bedroom": "1 Bedroom",
    "one bedroom": "1 Bedroom",
    "2 bedroom": "2 Bedroom",
    "two bedroom": "2 Bedroom",
    "3 bedroom +": "3 Bedroom+",
    "3 bedroom plus": "3 Bedroom+",
    "total": "Total",
}

DEFAULT_SUPPRESSION_MARKERS = {"a", "b", "c", "d", "**", "--", "n/a", "na", ""}

UNIT_SORT_ORDER = {
    "Studio": 1,
    "1 Bedroom": 2,
    "2 Bedroom": 3,
    "3 Bedroom+": 4,
    "Total": 5,
}

RENT_REQUIRED_COLUMNS = {
    "reference_year",
    "geography_id",
    "geography_name",
    "unit_type",
    "average_rent",
}

WIDE_UNIT_COLUMNS = {
    "studio": "Studio",
    "bachelor": "Studio",
    "1 bedroom": "1 Bedroom",
    "one bedroom": "1 Bedroom",
    "2 bedroom": "2 Bedroom",
    "two bedroom": "2 Bedroom",
    "3 bedroom +": "3 Bedroom+",
    "3 bedroom+": "3 Bedroom+",
    "3 bedroom plus": "3 Bedroom+",
    "total": "Total",
}


@dataclass(frozen=True)
class ValidationIssue:
    column: str
    message: str


def _compact(value: object) -> str:
    return " ".join(str(value).strip().lower().replace("+", " plus").split())


def normalize_unit_type(value: object, mapping: dict[str, str] | None = None) -> str:
    lookup = mapping or DEFAULT_UNIT_MAPPING
    text = str(value).strip()
    compact_lookup = {_compact(k): v for k, v in lookup.items()}
    return compact_lookup.get(_compact(text), text)


def parse_money(value: object, suppression_markers: Iterable[str] | None = None) -> float | None:
    markers = {str(item).strip().lower() for item in (suppression_markers or DEFAULT_SUPPRESSION_MARKERS)}
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in markers:
        return None
    cleaned = text.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def reshape_cmhc_wide_rent_table(
    frame: pd.DataFrame,
    reference_year: int,
    geography_id_column: str = "geography_id",
    geography_name_column: str = "geography_name",
) -> pd.DataFrame:
    """Convert a CMHC-style bedroom wide table into normalized rent observations.

    Expected wide columns include geography columns plus bedroom columns such as
    `Studio`, `1 Bedroom`, `2 Bedroom`, `3 Bedroom +`, and `Total`.
    """

    if geography_id_column not in frame.columns or geography_name_column not in frame.columns:
        raise ValueError("Wide CMHC tables need geography id and geography name columns.")

    normalized_columns = {_compact(column): column for column in frame.columns}
    value_columns: list[str] = []
    renamed_unit_types: dict[str, str] = {}
    for compact_name, unit_type in WIDE_UNIT_COLUMNS.items():
        source_column = normalized_columns.get(_compact(compact_name))
        if source_column:
            value_columns.append(source_column)
            renamed_unit_types[source_column] = unit_type

    if not value_columns:
        raise ValueError("No bedroom rent columns were found in the wide CMHC table.")

    long = frame.melt(
        id_vars=[geography_id_column, geography_name_column],
        value_vars=value_columns,
        var_name="unit_type",
        value_name="average_rent",
    )
    long["unit_type"] = long["unit_type"].map(renamed_unit_types)
    long["reference_year"] = reference_year
    return long.rename(
        columns={
            geography_id_column: "geography_id",
            geography_name_column: "geography_name",
        }
    )[["reference_year", "geography_id", "geography_name", "unit_type", "average_rent"]]


def clean_rent_observations(
    frame: pd.DataFrame,
    unit_mapping: dict[str, str] | None = None,
    suppression_markers: Iterable[str] | None = None,
) -> pd.DataFrame:
    missing = RENT_REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required rent columns: {sorted(missing)}")

    cleaned = frame.copy()
    cleaned["reference_year"] = pd.to_numeric(cleaned["reference_year"], errors="coerce").astype("Int64")
    cleaned["geography_id"] = cleaned["geography_id"].astype(str).str.strip()
    cleaned["geography_name"] = cleaned["geography_name"].astype(str).str.strip()
    cleaned["unit_type"] = cleaned["unit_type"].map(lambda value: normalize_unit_type(value, unit_mapping))
    cleaned["average_rent"] = cleaned["average_rent"].map(
        lambda value: parse_money(value, suppression_markers)
    )

    if "vacancy_rate" in cleaned.columns:
        cleaned["vacancy_rate"] = pd.to_numeric(cleaned["vacancy_rate"], errors="coerce")
    else:
        cleaned["vacancy_rate"] = pd.NA

    if "unit_count" in cleaned.columns:
        cleaned["unit_count"] = pd.to_numeric(cleaned["unit_count"], errors="coerce").astype("Int64")
    else:
        cleaned["unit_count"] = pd.NA

    cleaned["is_suppressed"] = cleaned["average_rent"].isna()
    cleaned["unit_sort_order"] = cleaned["unit_type"].map(lambda value: UNIT_SORT_ORDER.get(value, 99))
    cleaned = cleaned.dropna(subset=["reference_year", "geography_id", "unit_type"])

    output_columns = [
        "reference_year",
        "geography_id",
        "geography_name",
        "unit_type",
        "average_rent",
        "vacancy_rate",
        "unit_count",
        "is_suppressed",
    ]
    return cleaned.sort_values(
        ["reference_year", "geography_name", "unit_sort_order"]
    )[output_columns].reset_index(drop=True)


def validate_rent_observations(frame: pd.DataFrame) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in RENT_REQUIRED_COLUMNS:
        if column not in frame.columns:
            issues.append(ValidationIssue(column, "required column is missing"))

    if "average_rent" in frame.columns:
        numeric = pd.to_numeric(frame["average_rent"], errors="coerce")
        if (numeric.dropna() < 0).any():
            issues.append(ValidationIssue("average_rent", "rent values cannot be negative"))

    if "reference_year" in frame.columns:
        years = pd.to_numeric(frame["reference_year"], errors="coerce")
        if years.dropna().lt(1990).any() or years.dropna().gt(2100).any():
            issues.append(ValidationIssue("reference_year", "year is outside the expected range"))

    return issues
