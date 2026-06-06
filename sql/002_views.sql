-- Analytical views for Power BI.

CREATE VIEW vw_rent_map AS
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
    f.is_suppressed,
    f.source_name
FROM fact_rent_observation f
JOIN dim_geography g ON f.geography_id = g.geography_id;
GO

CREATE VIEW vw_rent_yoy AS
WITH rent_base AS (
    SELECT
        reference_year,
        geography_id,
        unit_type,
        average_rent,
        LAG(average_rent) OVER (
            PARTITION BY geography_id, unit_type
            ORDER BY reference_year
        ) AS prior_year_average_rent
    FROM fact_rent_observation
    WHERE is_suppressed = 0
)
SELECT
    reference_year,
    geography_id,
    unit_type,
    average_rent,
    prior_year_average_rent,
    average_rent - prior_year_average_rent AS rent_change_dollars,
    CASE
        WHEN prior_year_average_rent IS NULL OR prior_year_average_rent = 0 THEN NULL
        ELSE (average_rent - prior_year_average_rent) / prior_year_average_rent
    END AS rent_change_percent
FROM rent_base;
GO

CREATE VIEW vw_geography_rent_rank AS
SELECT
    reference_year,
    unit_type,
    geography_id,
    average_rent,
    RANK() OVER (
        PARTITION BY reference_year, unit_type
        ORDER BY average_rent DESC
    ) AS high_rent_rank,
    RANK() OVER (
        PARTITION BY reference_year, unit_type
        ORDER BY average_rent ASC
    ) AS low_rent_rank
FROM fact_rent_observation
WHERE is_suppressed = 0;
GO
