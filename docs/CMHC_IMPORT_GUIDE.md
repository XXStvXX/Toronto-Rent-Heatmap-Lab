# CMHC Import Guide

The project supports two CMHC-style input shapes.

## 1. Normalized Long Table

Use this when you already have one row per year, geography, and unit type.

Required columns:

```text
reference_year, geography_id, geography_name, unit_type, average_rent
```

Optional columns:

```text
vacancy_rate, unit_count, geography_group, latitude, longitude
```

Command:

```bash
rent-heatmap load-cmhc data/raw/cmhc/toronto_rents_long.csv --database data/rent_heatmap.sqlite
```

## 2. Wide Bedroom Table

Use this when the CMHC export has bedroom types as columns.

Example columns:

```text
zone_id, zone_name, Studio, 1 Bedroom, 2 Bedroom, 3 Bedroom +, Total
```

Command:

```bash
rent-heatmap load-cmhc data/raw/cmhc/toronto_rents_wide.xlsx \
  --wide \
  --year 2025 \
  --geography-id-column zone_id \
  --geography-name-column zone_name \
  --database data/rent_heatmap.sqlite
```

## Suppressed Values

CMHC often marks unreliable or suppressed cells with letter codes. The ETL converts these to null `average_rent` values and sets `is_suppressed = true`.

Do not fill suppressed rent values without a clear statistical method. In the Power BI dashboard, show suppressed cells as unavailable.

## Recommended Workflow

1. Download CMHC table from the official CMHC Rental Market Data interface.
2. Save the raw file under `data/raw/cmhc/`.
3. Run `load-cmhc` with either normalized or wide-table settings.
4. Run `export-powerbi`.
5. Refresh Power BI from the exported CSVs or direct SQL connection.
