# Architecture

## Pipeline

```text
CMHC Rental Market Survey XLSX/CSV
        |
        v
Python ETL cleaning and validation
        |
        v
SQL warehouse dimensional model
        |
        v
Power BI semantic model and map dashboard
```

## Why This Shape

The project separates ingestion, transformation, storage, and BI modeling so each part can be discussed in a portfolio interview:

- Python demonstrates reproducible ETL and data cleaning.
- SQL demonstrates dimensional modeling and analytical view design.
- Power BI demonstrates semantic modeling, DAX, and map-based storytelling.
- Documentation demonstrates awareness of data suppression and survey limitations.

## Data Grain

The fact table grain is:

```text
one row per reference_year + geography_id + unit_type
```

This keeps the dashboard simple and makes it easy to filter by year, unit type, and geography.

## Data Quality Rules

- Suppression markers such as `a`, `--`, and `n/a` become null rents with `is_suppressed = true`.
- Negative rents are invalid.
- Years before 1990 or after 2100 are flagged by validation.
- Missing required fields stop the load.

## Future Enhancements

- Add full Toronto neighbourhood boundary ingestion with centroid generation.
- Convert GeoJSON to TopoJSON for Power BI Shape Map.
- Add Azure SQL deployment scripts.
- Add scheduled checks for newly released CMHC Rental Market Survey tables.
- Add a Streamlit prototype for public web preview while Power BI remains the main BI artifact.
