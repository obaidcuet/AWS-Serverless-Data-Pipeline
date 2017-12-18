-- hive script for fact processing
-- it will append data to an existing data

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

-- insert data with partition option
insert into fact_db.sample_country_tx_fact partition(date_id) select * from stg_fact_db.sample_country_tx_fact;

-- partition discovery in metastore
MSCK REPAIR TABLE fact_db.sample_country_tx_fact;
