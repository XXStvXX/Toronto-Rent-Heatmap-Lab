# Interview Notes: Toronto Rent Heatmap Lab

## 60-Second Explanation

I built the Toronto Rent Heatmap Lab to demonstrate an end-to-end data-analytics workflow around a local public-data problem: comparing rental pressure across Toronto geographies.

The project is designed to take rental-market and geography data through Python cleaning, validation, SQL-style modeling, and interactive reporting. The live demo presents a regional heatmap so a nontechnical reviewer can quickly compare rent patterns by area.

The main point of the project is not only the map. It is the workflow: source data, cleaning assumptions, reproducible outputs, dashboard design, and honest limitations around geography matching and missing or suppressed data.

## Problem

Rental affordability is often discussed at a citywide level, but actual pressure can vary by geography and unit type. A useful dashboard should help answer questions such as:

- Which areas appear more expensive under the available data?
- How do rent levels differ by unit type?
- What information should be treated cautiously because of missing, suppressed, or aggregated data?

## Approach

1. Identify public rental-market and geography data sources.
2. Prepare a reproducible Python ETL workflow.
3. Model cleaned observations in SQL-style fact and dimension tables.
4. Export Power BI-ready tables and maintain a lightweight interactive demo.
5. Document assumptions, limitations, and ethical boundaries.

## Design Decisions

- I focused on a regional choropleth instead of a detailed street-level map because the data is aggregate and should not imply building-level precision.
- I separated sample development data from the intended official-data workflow so the project can be developed without redistributing full source tables.
- I included ethical-use notes because aggregate rent data can be misread if missing values or geography limitations are hidden.
- I structured the repository around a portfolio-grade analytics workflow rather than a single notebook.

## Limitations

- Geography matching can introduce ambiguity when source boundaries do not align perfectly.
- Some data cells may be missing, suppressed, or based on limited coverage.
- Area-level averages do not describe individual buildings or households.
- The current project still needs stronger real-data findings and visible screenshots for recruiter review.

## What I Would Improve Next

- Add 3-5 clearly stated findings from official rental data.
- Add dashboard or live-demo screenshots to the README.
- Document exact source tables, access dates, and transformation steps.
- Add a clearer explanation of how missing or suppressed cells are handled.
- Verify the live demo across desktop and mobile.

## Interview Questions To Prepare

### Why this project?

It connects data analysis to a real local issue and lets me demonstrate a full workflow: sourcing data, cleaning it, modeling it, visualizing it, and explaining limitations.

### Why not use building-level data?

The available public data is aggregate and should be interpreted at the geography level. Showing too much detail could create a false sense of precision.

### What did you personally build?

I built the repository structure, documentation, Python ETL foundation, SQL-style modeling approach, Power BI-ready workflow notes, and interactive GitHub Pages demo.

### What makes the project credible?

The project is credible when it clearly separates official data from sample data, documents source assumptions, preserves limitations, and avoids claiming more precision than the data supports.
