-- Create  estadia tables
begin transaction;
--INSTALL spatial;
--LOAD spatial; 

-- create world map table from json file
--create table world_map as select * from read_json('geopackages\world_map.json', AUTO_DETECT=TRUE);

-- create portugal map from geopackage
--create table portugal_map_con as select * from ST_Read('geopackages\portugal_con.gpkg');
--create table portugal_map_freg as select * from ST_Read('geopackages\portugal_freg.gpkg');
--create table vdl_map_con as select * from ST_Read('geopackages\vdl_con.gpkg');
--create table vdl_map_freg as select * from ST_Read('geopackages\vdl_freg.gpkg');


create table estadias_concelho_m as select * from read_csv('clean_data\estadias_co.csv', AUTO_DETECT=TRUE);
create table estadias_freguesia_m as select * from read_csv('clean_data\estadias_fr.csv', AUTO_DETECT=TRUE);
create table estadias_seccao_m as select * from read_csv('clean_data\estadias_sc.csv', AUTO_DETECT=TRUE);

-- create deslocamento tables

create table deslocamento_concelho_h as select * from read_csv('clean_data\deslocamento_co.csv', AUTO_DETECT=TRUE);
create table deslocamento_freguesia_h as select * from read_csv('clean_data\deslocamento_fr.csv', AUTO_DETECT=TRUE);
create table deslocamento_seccao_h as select * from read_csv('clean_data\deslocamento_sc.csv', AUTO_DETECT=TRUE);

-- create permanencia tables

create table permanencia_concelho_d as select * from read_csv('clean_data\permanencia_co.csv', AUTO_DETECT=TRUE);
create table permanencia_freguesia_d as select * from read_csv('clean_data\permanencia_fr.csv', AUTO_DETECT=TRUE);
create table permanencia_seccao_d as select * from read_csv('clean_data\permanencia_sc.csv', AUTO_DETECT=TRUE);

COMMIT;
