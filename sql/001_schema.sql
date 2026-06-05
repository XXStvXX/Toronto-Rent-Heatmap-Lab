-- Toronto Rent Heatmap Lab warehouse schema
-- SQL Server-friendly dimensional model.

CREATE TABLE dim_geography (
    geography_key INT IDENTITY(1,1) PRIMARY KEY,
    geography_id NVARCHAR(64) NOT NULL UNIQUE,
    geography_name NVARCHAR(255) NOT NULL,
    geography_group NVARCHAR(255) NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    boundary_geojson NVARCHAR(MAX) NULL
);

CREATE TABLE dim_unit_type (
    unit_type_key INT IDENTITY(1,1) PRIMARY KEY,
    unit_type NVARCHAR(50) NOT NULL UNIQUE,
    sort_order INT NOT NULL
);

CREATE TABLE dim_year (
    year_key INT PRIMARY KEY,
    reference_year INT NOT NULL UNIQUE
);

CREATE TABLE fact_rent_observation (
    rent_observation_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    reference_year INT NOT NULL,
    geography_id NVARCHAR(64) NOT NULL,
    unit_type NVARCHAR(50) NOT NULL,
    average_rent DECIMAL(12,2) NULL,
    vacancy_rate DECIMAL(8,4) NULL,
    unit_count INT NULL,
    is_suppressed BIT NOT NULL DEFAULT 0,
    source_name NVARCHAR(255) NOT NULL DEFAULT 'CMHC Rental Market Survey',
    loaded_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_fact_year FOREIGN KEY (reference_year) REFERENCES dim_year(reference_year),
    CONSTRAINT fk_fact_geography FOREIGN KEY (geography_id) REFERENCES dim_geography(geography_id),
    CONSTRAINT fk_fact_unit_type FOREIGN KEY (unit_type) REFERENCES dim_unit_type(unit_type)
);

CREATE INDEX ix_fact_rent_year_unit ON fact_rent_observation(reference_year, unit_type);
CREATE INDEX ix_fact_rent_geo ON fact_rent_observation(geography_id);
