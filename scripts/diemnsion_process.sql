-- hive script for dimension processing
-- it will overwrite all existing data

-- set hive configurations
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
set hive.merge.mapredfiles=true;
set hive.merge.mapfiles=true;
-- set hive.merge.reducefiles=true;
set dfs.block.size=268435456;
set hive.merge.size.per.task=134217728;
set hive.merge.smallfiles.avgsize=67108864;
set hive.exec.max.dynamic.partitions.pernode=1000;

-- insert data with overwrite option
insert overwrite table dimension_db.sample_country_dim select * from stg_dimension_db.sample_country_dim;
-- update metadata for the table
MSCK REPAIR TABLE dimension_db.sample_country_dim;
