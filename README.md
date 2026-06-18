# Toronto Rent Heatmap Lab

A city-data analytics project that turns official rental market data into an interactive Toronto rent heatmap. The target workflow is:

```text
Official data sources -> Python ETL -> SQL warehouse -> Power BI map dashboard
```

The project is inspired by the land-value overlays in city-building games: choose a bedroom type, year, and geography, then see where rent pressure is highest across Toronto.

## Live Demo

- Interactive GitHub Pages app: https://xxstvxx.github.io/Toronto-Rent-Heatmap-Lab/
- Repository: https://github.com/XXStvXX/Toronto-Rent-Heatmap-Lab

The live demo uses a locked regional choropleth instead of a zoomable street map. This keeps the page fast, avoids repeated map-tile requests, and focuses the viewer on area-level rent comparison.

## Project Goals

- Ingest official rental market data from CMHC Rental Market Survey tables.
- Join rent observations to Toronto geography boundaries from the City of Toronto Open Data portal.
- Model the cleaned data in SQL with fact and dimension tables.
- Build Power BI-ready outputs for choropleth maps, tooltips, KPI cards, and time-series analysis.
- Keep the data pipeline reproducible enough to update when new CMHC rental tables are released.

## AI-Assisted Workflow

This project uses AI-assisted prototyping and documentation as part of a human-in-the-loop workflow. AI helps with project structure, implementation ideas, debugging prompts, and clearer explanations, while source assumptions, data limitations, and final technical claims are reviewed manually.

See [`docs/AI_ASSISTED_WORKFLOW.md`](docs/AI_ASSISTED_WORKFLOW.md) for the workflow note.

## MVP Scope

The first release focuses on Toronto zones and neighbourhood-like geographies where public data is dense enough to map responsibly.

Supported unit types:

- Studio
- 1 Bedroom
- 2 Bedroom
- 3 Bedroom+
- Total

Core dashboard interactions:

- Year selector
- Unit type selector
- Geography selector
- Rent heatmap
- Vacancy and unit-count tooltips
- Top/bottom rent ranking table
- Year-over-year rent change

## Data Sources

Primary rental data:

- CMHC Rental Market Survey data tables, especially average apartment rents by geography and bedroom type.
- CMHC Rental Market Survey methodology documentation for definitions of average rent, vacancy, and survey coverage.

Geography data:

- City of Toronto Open Data boundary datasets, including neighbourhood and planning geographies.
- Toronto Neighbourhood Profiles for geography metadata and context.

The repository includes a small sample dataset so the SQL model, tests, and Power BI setup can be developed without redistributing full CMHC tables.

## Repository Structure

```text
.
├── app.py                  # Optional Streamlit prototype, not the main deployment
├── site/                   # GitHub Pages static interactive app
├── config/                 # Data-source and pipeline configuration
├── data/sample/            # Small synthetic/sample files for development
├── docs/                   # Architecture, data dictionary, source notes
├── powerbi/                # Power BI model guide and DAX measures
├── sql/                    # Warehouse schema and analytical views
├── src/rent_heatmap/       # Python ETL package
├── tests/                  # Unit tests for cleaning and validation logic
└── .github/workflows/      # CI and Pages deployment checks
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

rent-heatmap load-sample --database data/rent_heatmap.sqlite
rent-heatmap export-powerbi --database data/rent_heatmap.sqlite --output exports/powerbi
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Importing CMHC Tables

Normalized long table:

```bash
rent-heatmap load-cmhc data/raw/cmhc/toronto_rents_long.csv --database data/rent_heatmap.sqlite
```

CMHC-style wide bedroom table:

```bash
rent-heatmap load-cmhc data/raw/cmhc/toronto_rents_wide.xlsx \
  --wide \
  --year 2025 \
  --geography-id-column zone_id \
  --geography-name-column zone_name \
  --database data/rent_heatmap.sqlite
```

See [`docs/CMHC_IMPORT_GUIDE.md`](docs/CMHC_IMPORT_GUIDE.md) for the expected input formats.

## SQL Workflow

The warehouse schema is defined in [`sql/001_schema.sql`](sql/001_schema.sql). Analytical views for Power BI are in [`sql/002_views.sql`](sql/002_views.sql).

For local development, the CLI can load the same dimensional model into SQLite. For a portfolio-grade BI workflow, the SQL scripts are written in a SQL Server-friendly style and can be adapted to Azure SQL or PostgreSQL.

## Power BI Workflow

1. Run the ETL export command to produce clean CSV tables.
2. Import the CSV tables or connect Power BI directly to SQL Server.
3. Use the measures in [`powerbi/measures.dax`](powerbi/measures.dax).
4. Use the map visual with geography polygons or latitude/longitude centroids.
5. Add slicers for year, unit type, and geography group.

Detailed dashboard notes live in [`powerbi/README.md`](powerbi/README.md).

## Ethical Use

This project maps aggregate rents by geography. It should not be used to infer individual household rent, landlord behaviour, or building-level affordability. Suppressed, missing, or low-sample cells should remain flagged rather than silently filled.

## Status

Interactive GitHub Pages demo plus foundation build: ETL package, sample data, SQL schema, Power BI modeling notes, and CI.
