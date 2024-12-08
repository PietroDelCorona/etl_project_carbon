create schema if not exists minio.prod_bronze with (location = 's3a://bronze/');
create schema if not exists minio.prod_silver with (location = 's3a://silver/');
create schema if not exists minio.prod_gold with (location = 's3a://gold/');



create table if not exists minio.prod_bronze.co2_emission_per_capita (
    entity VARCHAR,
    code VARCHAR,
    year VARCHAR,
    emissions_total_per_capita VARCHAR
) WITH (
            external_location = 's3a://bronze/co2_emissions/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.co2_land_use (
    entity VARCHAR,
    code VARCHAR,
    year VARCHAR,
    emissions_from_land_use_change VARCHAR,
    emissions_total VARCHAR
) WITH (
            external_location = 's3a://bronze/co2_land_use/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.energy_mix_sources (
    entity VARCHAR,
    code VARCHAR,
    year VARCHAR,
    fossil_fuels_per_capita__kwh VARCHAR,
    nuclear_per_capita__kwh__equivalent VARCHAR,
    renewables_per_capita__kwh__equivalent VARCHAR
) WITH (
            external_location = 's3a://bronze/energy_mix/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_bronze.population (
    country_or_area VARCHAR,
    year VARCHAR,
    area VARCHAR,
    sex VARCHAR,
    record_type VARCHAR,
    reliability VARCHAR,
    source_year VARCHAR,
    value VARCHAR,
    value_footnotes VARCHAR
) WITH (
            external_location = 's3a://bronze/population/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_co2_emission_per_capita (
    entity VARCHAR,
    year VARCHAR,
    emissions_total_per_capita VARCHAR
) WITH (
            external_location = 's3a://silver/co2_emissions/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_co2_land_use (
    entity VARCHAR,
    year VARCHAR,
    emissions_from_land_use_change VARCHAR,
    emissions_total VARCHAR
) WITH (
            external_location = 's3a://silver/co2_land_use/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_energy_mix_sources (
    entity VARCHAR,
    year VARCHAR,
    fossil_fuels_per_capita__kwh VARCHAR,
    nuclear_per_capita__kwh__equivalent VARCHAR,
    renewables_per_capita__kwh__equivalent VARCHAR
) WITH (
            external_location = 's3a://silver/energy_mix/',
            format = 'CSV',
            skip_header_line_count=1
        );


create table if not exists minio.prod_silver.cleansed_world_population (
    coutry_or_area VARCHAR,
    year VARCHAR,
    area VARCHAR,
    value VARCHAR
) WITH (
            external_location = 's3a://silver/population/',
            format = 'CSV',
            skip_header_line_count=1
        );