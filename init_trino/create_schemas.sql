create schema if not exists minio.prod_bronze with (location = 's3a://bronze/');
create schema if not exists minio.prod_silver with (location = 's3a://silver/');

create table if not exists minio.prod_bronze.co2_emission_per_capita (
    entity VARCHAR,
    code VARCHAR,
    year INT,
    emissions_total_per_capita DECIMAL(10,8)
) WITH (
            external_location = 's3a://bronze/co2_emissions/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.co2_land_use (
    entity VARCHAR,
    code VARCHAR,
    year INT,
    emissions_from_land_use_change DECIMAL(10,2),
    emissions_total DECIMAL(10,2)
) WITH (
            external_location = 's3a://bronze/co2_land_use/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.energy_mix_sources (
    entity VARCHAR,
    code VARCHAR,
    year INT,
    fossil_fuels_per_capita__kwh DECIMAL(10,5),
    nuclear_per_capita__kwh__equivalent DECIMAL(10,5),
    renewables_per_capita__kwh__equivalent DECIMAL(10,5)
) WITH (
            external_location = 's3a://bronze/energy_mix/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.population (
    country_or_area VARCHAR,
    year INT,
    area VARCHAR,
    sex VARCHAR,
    record_type VARCHAR,
    reliability VARCHAR,
    source_year INT,
    value INT,
    value_footnotes INT
) WITH (
            external_location = 's3a://bronze/population/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_co2_emission_per_capita (
    entity VARCHAR,
    year INT,
    emissions_total_per_capita DECIMAL(10,8)
) WITH (
            external_location = 's3a://silver/co2_emissions/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_co2_land_use (
    entity VARCHAR,
    year INT,
    emissions_from_land_use_change DECIMAL(10,2),
    emissions_total DECIMAL(10,2)
) WITH (
            external_location = 's3a://silver/co2_land_use/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_energy_mix_sources (
    entity VARCHAR,
    year INT,
    fossil_fuels_per_capita__kwh DECIMAL(10,5),
    nuclear_per_capita__kwh__equivalent DECIMAL(10,5),
    renewables_per_capita__kwh__equivalent DECIMAL(10,5)
) WITH (
            external_location = 's3a://silver/energy_mix/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_world_population (
    coutry_or_area VARCHAR,
    year INT,
    area VARCHAR,
    value INT
) WITH (
            external_location = 's3a://silver/population/',
            format = 'CSV',
            skip_header_line_count=1
        );