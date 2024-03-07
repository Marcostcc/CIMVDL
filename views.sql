-- create views
BEGIN TRANSACTION;

-- create base views for deslocamento
create or replace view deslocamento_national_concelho as select * from deslocamento_concelho_h where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view deslocamento_national_freguesia as select * from deslocamento_freguesia_h where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view deslocamento_national_seccao as select * from deslocamento_seccao_h where concelho_residencia IS NOT NULL AND NOT residente_VDL;

create or replace view deslocamento_regional_concelho as select * from deslocamento_concelho_h where residente_VDL AND geocodigo_residencia::text != substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text));
create or replace view deslocamento_regional_freguesia as select * from deslocamento_freguesia_h where residente_VDL AND geocodigo_residencia::text != substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text) - 2);
create or replace view deslocamento_regional_seccao as select * from deslocamento_seccao_h where residente_VDL AND geocodigo_residencia::text != substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text) - 5);

create or replace view deslocamento_local_concelho as select * from deslocamento_concelho_h where geocodigo_residencia::text = substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text));
create or replace view deslocamento_local_freguesia as select * from deslocamento_freguesia_h where geocodigo_residencia::text = substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text) - 2);
create or replace view deslocamento_local_seccao as select * from deslocamento_seccao_h where geocodigo_residencia::text = substring(geocodigo_analisado::text, 1, length(geocodigo_analisado::text) - 5);

--create or replace view agg_pais_tipo_dsh as select pais_origem, tipologia, sum(individuos) from estrangeiros_dsh group by pais_origem, tipologia;


-- creating base views for permanencia
create or replace view permanencia_internacional_concelho  as select * from permanencia_concelho_d where pais_origem != 'Portugal' and concelho_residencia IS NULL;
create or replace view permanencia_internacional_freguesia as select * from permanencia_freguesia_d where pais_origem != 'Portugal' and concelho_residencia IS NULL;
create or replace view permanencia_internacional_seccao as select * from permanencia_seccao_d where pais_origem != 'Portugal' and concelho_residencia IS NULL;

create or replace view permanencia_nacional_concelho  as select * from permanencia_concelho_d where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view permanencia_nacional_freguesia as select * from permanencia_freguesia_d where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view permanencia_nacional_seccao as select * from permanencia_seccao_d where concelho_residencia IS NOT NULL AND NOT residente_VDL;

create or replace view permanencia_regional_concelho  as select * from permanencia_concelho_d where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text));
create or replace view permanencia_regional_freguesia as select * from permanencia_freguesia_d where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 2);
create or replace view permanencia_regional_seccao as select * from permanencia_seccao_d where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 5);

create or replace view permanencia_local_concelho  as select * from permanencia_concelho_d where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text));
create or replace view permanencia_local_freguesia as select * from permanencia_freguesia_d where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 2);
create or replace view permanencia_local_seccao as select * from permanencia_seccao_d where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 5);


-- creating base views for estadia
create or replace view estadias_international_concelho  as select * from estadias_concelho_m where pais_origem != 'Portugal' and concelho_residencia IS NULL;
create or replace view estadias_international_freguesia as select * from estadias_freguesia_m where pais_origem != 'Portugal' and concelho_residencia IS NULL;
create or replace view estadias_international_seccao as select * from estadias_seccao_m where pais_origem != 'Portugal' and concelho_residencia IS NULL;

create or replace view estadias_national_concelho  as select * from estadias_concelho_m where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view estadias_national_freguesia as select * from estadias_freguesia_m where concelho_residencia IS NOT NULL AND NOT residente_VDL;
create or replace view estadias_national_seccao as select * from estadias_seccao_m where concelho_residencia IS NOT NULL AND NOT residente_VDL;

create or replace view estadias_regional_concelho  as select * from estadias_concelho_m where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) );
create or replace view estadias_regional_freguesia as select * from estadias_freguesia_m where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 2);
create or replace view estadias_regional_seccao as select * from estadias_seccao_m where residente_VDL AND concelho_residencia_codigo::text != substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 5);

create or replace view estadias_local_concelho  as select * from estadias_concelho_m where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text));
create or replace view estadias_local_freguesia as select * from estadias_freguesia_m where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 2);
create or replace view estadias_local_seccao as select * from estadias_seccao_m where concelho_residencia_codigo::text = substring(geo_area_codigo::text, 1, length(geo_area_codigo::text) - 5);

--create or replace view agg_pais_tipo_pfd as select pais_origem, tipologia, sum(individuos) from estrangeiros_pfd group by pais_origem, tipologia;

-- creating sub views

-- Quem dormiu?
create or replace view quem_dormiu_int_concelho as select pais_origem, geo_area_nome, sum(dormidas_totais) as dormidas_totais from estadias_international_concelho group by pais_origem, geo_area_nome;
create or replace view quem_dormiu_int_freguesia as select pais_origem, geo_area_nome,  sum(dormidas_totais) as dormidas_totais from estadias_international_freguesia group by pais_origem, geo_area_nome;

create or replace view quem_dormiu_nac_concelho as select pais_origem, geo_area_nome, concelho_residencia, sum(dormidas_totais) from estadias_national_concelho group by pais_origem, geo_area_nome, concelho_residencia,;
create or replace view quem_dormiu_nac_freguesia as select pais_origem, geo_area_nome, concelho_residencia, sum(dormidas_totais) from estadias_national_freguesia group by pais_origem, geo_area_nome, concelho_residencia,;

create or replace view quem_dormiu_reg_concelho as select pais_origem, geo_area_nome, concelho_residencia, sum(dormidas_totais) from estadias_regional_concelho group by pais_origem, geo_area_nome, concelho_residencia;
create or replace view quem_dormiu_reg_freguesia as select pais_origem, geo_area_nome, concelho_residencia, sum(dormidas_totais) from estadias_regional_freguesia group by pais_origem, geo_area_nome, concelho_residencia;

COMMIT;
