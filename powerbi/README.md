# Power BI Dashboard Guide

## Recommended Pages

### 1. Rent Heatmap

Visuals:

- Filled map or Azure Maps choropleth using `dim_geography` boundaries or centroid fields.
- Slicers for `reference_year`, `unit_type`, and `geography_group`.
- KPI cards for average rent, median rent, vacancy rate, and total rental units.
- Tooltip page showing suppressed status, vacancy rate, unit count, and source.

### 2. Rent Ranking

Visuals:

- Bar chart: top 10 highest-rent geographies.
- Bar chart: top 10 lowest-rent geographies.
- Matrix: geography by bedroom type.
- Conditional formatting on average rent and YoY change.

### 3. Trend Explorer

Visuals:

- Line chart: average rent over time by unit type.
- Small multiples: geography group trends.
- Decomposition tree: rent by year, geography group, unit type.

## Data Model

Suggested relationships:

- `fact_rent_observation[geography_id]` -> `dim_geography[geography_id]`
- `fact_rent_observation[unit_type]` -> `dim_unit_type[unit_type]`
- `fact_rent_observation[reference_year]` -> `dim_year[reference_year]`

For time intelligence measures, add a calculated date column in `dim_year`:

```DAX
Date = DATE ( dim_year[reference_year], 1, 1 )
```

Mark `dim_year` as the date table using this `Date` column.

## Map Notes

Power BI can map Toronto geographies in two ways:

- Centroid map: easier, uses latitude and longitude.
- Shape map / Azure Maps choropleth: better visual match, requires boundary polygons or TopoJSON.

For portfolio presentation, choropleth is preferred because it resembles a city-planning heatmap.

## Design Notes

Use a restrained palette:

- Low rent: pale green / grey-green
- Mid rent: gold
- High rent: red / burgundy

Avoid implying that high rent means better neighbourhood quality. Label it as rent pressure or observed average rent.
