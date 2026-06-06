# Data Dictionary

## fact_rent_observation

| Column | Type | Description |
| --- | --- | --- |
| rent_observation_key | integer | Surrogate key. |
| reference_year | integer | Rental Market Survey reference year. |
| geography_id | text | Source geography identifier. |
| unit_type | text | Studio, 1 Bedroom, 2 Bedroom, 3 Bedroom+, or Total. |
| average_rent | decimal | Average monthly rent. Null when suppressed or unavailable. |
| vacancy_rate | decimal | Vacancy rate for the cell when available. |
| unit_count | integer | Rental unit universe/count when available. |
| is_suppressed | boolean | True when source value is suppressed or not reportable. |
| source_name | text | Data source label. |
| loaded_at | datetime | Warehouse load timestamp. |

## dim_geography

| Column | Type | Description |
| --- | --- | --- |
| geography_key | integer | Surrogate key. |
| geography_id | text | Source geography id or stable project geography code. |
| geography_name | text | Human-readable geography label. |
| geography_group | text | Optional grouping such as Downtown Toronto or Toronto East. |
| latitude | decimal | Optional centroid latitude for map visuals. |
| longitude | decimal | Optional centroid longitude for map visuals. |
| boundary_geojson | text | Optional GeoJSON polygon for shape-map workflows. |

## dim_unit_type

| Column | Type | Description |
| --- | --- | --- |
| unit_type_key | integer | Surrogate key. |
| unit_type | text | Normalized bedroom/unit type. |
| sort_order | integer | Display order for reports. |

## dim_year

| Column | Type | Description |
| --- | --- | --- |
| year_key | integer | Year key. |
| reference_year | integer | Calendar/survey year. |

## Source Caveats

CMHC Rental Market Survey data can include suppressed cells. Suppression is meaningful and should remain visible in analysis rather than being silently imputed.
