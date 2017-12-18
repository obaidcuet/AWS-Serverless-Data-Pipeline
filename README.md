AWS Services used:
	A. S3
    B. Lambda Functions
    C. Step Functions
    D. CloudWatch
    E. SNS
    F. Athena
    G. Glue
    H. EMR	

0. configure glue as default metastore for Athena and launch all EMR pointing metastire to glue.

1. create staging databases (stg_dimension_db & stg_fact_db) location:
   s3://workarea-<aws_region>/data-workflows/stage/STG_DWH/stg_dimension_db
   s3://workarea-<aws_region>/data-workflows/stage/STG_DWH/stg_fact_db
   

2. create staging databases (dimension_db & fact_db) location:
   s3://workarea-<aws_region>/data-workflows/prod/DWH/dimension_db
   s3://workarea-<aws_region>/data-workflows/prod/DWH/fact_db
   

3. create STG_DWH & DWH databases on glue (or from hive pointing metastore to glue"
    create database stg_dimension_db;
    create database stg_fact_db;
    create database dimension_db;
    create database fact_db;
    
    
4. create staging external tables on glue, pointing to STG_DWH s3 location. Files here will be pain text.
    Table: stg_dimension_db.sample_country_dim 
    Location: s3://workarea-<aws_region>/data-workflows/stage/STG_DWH/stg_dimension_db/sample_country_dim

    Table: stg_fact_db.sample_country_tx_fact 
    Location: s3://workarea-<aws_region>/data-workflows/stage/STG_DWH/stg_fact_db/sample_country_tx_fact

4. create prod external tables on glue, pointing to DWH s3 location. Files here will be pain orc and properly partitioned.
    Table: dimension_db.sample_country_dim
    Location: s3://workarea-<aws_region>/data-workflows/prod/DWH/dimension_db/sample_country_dim

    Table: fact_db.sample_country_tx_fact
    Location: s3://workarea-<aws_region>/data-workflows/prod/DWH/fact_db/sample_country_tx_fact


5. Create S3 location to place all the external libraries and scripts
   s3://workarea-<aws_region>/data-workflows/prod/libs/

6. place hive scripts to load data from staging tables to prod tables in s3 locations (sample scripts provided in ./scripts folder)
    s3://workarea-<aws_region>/data-workflows/prod/libs/hive-scripts/diemnsion_process.sql
    s3://workarea-<aws_region>/data-workflows/prod/libs/hive-scripts/diemnsion_process.sql

7. Place configuration file in s3 location
    s3://workarea-<aws_region>data-workflows/prod/libs/lambda_fn_config/config.ini
    Note: in the lambda function(if needed) below will be environment variables for this file:
        Config_File_S3_Bucket = workarea-<aws_region>
        Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
        
 8. create a s3 location to store state info (now only storing CluaterId)
    s3://workarea-<aws_region>/data-workflows/prod/state_info/data_pipeline_ClusterId.info
    Note: in the lambda function(if needed) below will be environment variables for this file:
        State_Info_File_S3_Bucket = workarea-<aws_region>
        State_Info_File_S3_Key = data-workflows/prod/state_info/data_pipeline_ClusterId.info
       
 9. create landing locations for each tables ( files will be pushed/pulled to this area from external systems) 
    Landing area: s3://workarea-<aws_region>/data-workflows/landing/DWH
    for table sample_country_dim: s3://workarea-<aws_region>/data-workflows/landing/DWH/dimensions/sample_country_dim
    for table sample_country_tx_fact: s3://workarea-<aws_region>/data-workflows/landing/DWH/facts/sample_country_tx_fact

 9. create archive locations for each tables. After data loading done, files will be archived here
    Archive area: s3://workarea-<aws_region>/data-workflows/archive/DWH/
    for table sample_country_dim: s3://workarea-<aws_region>/data-workflows/archive/DWH/dimensions/sample_country_dim
    for table sample_country_tx_fact: s3://workarea-<aws_region>/data-workflows/archive/DWH/facts/sample_country_tx_fact

 10. Create a SNS Email topic and add subscribers to it. 
     Example topic here: arn:aws:sns:<aws_region>:<aws_accountid>:data_pipeline
     
 11. Then create lambda function using the scripts in "./lambda_functions" and with below corresponding environment variables: Mames lambda functions refering to the purpose/usage.
     a. lambda function name: lambda_add_worker_instances_emr
         Script: ./lambda_functions/lambda_add_worker_instances_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_add_worker_instances_emr:data_pipeline
     
     b. lambda function name: lambda_check_duplicate_emr
         Script: ./lambda_functions/lambda_check_duplicate_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_check_duplicate_emr
         
     c. lambda function name: lambda_check_duplicate_stepfunction
         Script: ./lambda_functions/lambda_check_duplicate_stepfunction.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_check_duplicate_stepfunction

     d. lambda function name: lambda_launch_emr
         Script: ./lambda_functions/lambda_launch_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_launch_emr         

     e. lambda function name: lambda_read_state_info_from_s3
         Script: ./lambda_functions/lambda_read_state_info_from_s3.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Key = data-workflows/prod/state_info/data_pipeline_ClusterId.info
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_read_state_info_from_s3

     f. lambda function name: lambda_remove_state_info_from_s3
         Script: ./lambda_functions/lambda_remove_state_info_from_s3.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Key = data-workflows/prod/state_info/data_pipeline_ClusterId.info
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_remove_state_info_from_s3
         
     g. lambda function name: lambda_send_msg_sns
         Script: ./lambda_functions/lambda_send_msg_sns.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
                TopicArn = arn:aws:sns:<aws_region>:<aws_accountid>:data_pipeline
                Subject = data_pipeline Step Workflow Status
         Alias name: data_pipeline
         Note: 
            - in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
            - Here we will used Topic ARN from step 10 (in environment variable "TopicArn")
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_send_msg_sns
         
     h. lambda function name: lambda_status_add_worker_instances_emr
         Script: ./lambda_functions/lambda_status_add_worker_instances_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_status_add_worker_instances_emr    
 
     i. lambda function name: lambda_status_emr
         Script: ./lambda_functions/lambda_status_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_status_emr
  
     j. lambda function name: lambda_status_step_emr
         Script: ./lambda_functions/lambda_status_step_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_status_step_emr

     k. lambda function name: lambda_status_stepfunction
         Script: ./lambda_functions/lambda_status_stepfunction.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_status_stepfunction        
         
     l. lambda function name: lambda_submit_cmd_run_step_emr
         Script: ./lambda_functions/lambda_submit_cmd_run_step_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: 
            - in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
            - "Step_Name" & "Cmd_Run" can be passed as environment variables or using event(event["NextStepNameAndCmd"]["Step_Name"] & event["NextStepNameAndCmd"]["Cmd_Run"])
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_submit_cmd_run_step_emr  

     m. lambda function name: lambda_submit_stepfunction
         Script: ./lambda_functions/lambda_submit_stepfunction.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_submit_stepfunction

     n. lambda function name: lambda_terminate_emr
         Script: ./lambda_functions/lambda_terminate_emr.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_terminate_emr 

     o. lambda function name: lambda_write_state_info_to_s3
         Script: ./lambda_functions/lambda_write_state_info_to_s3.py
         Environment Variables:
                Config_File_S3_Key = data-workflows/prod/libs/lambda_fn_config/config.ini
                Config_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Bucket = workarea-<aws_region>
                State_Info_File_S3_Key = data-workflows/prod/state_info/data_pipeline_ClusterId.info
         Alias name: data_pipeline
         Note: in the steps function scripts (./step_functions), replace below(Example ARN) with your created lambda_function's alias's ARN
         Example ARN: arn:aws:lambda:<aws_region>:<aws_accountid>:function:lambda_write_state_info_to_s3
 		 
     Note:
		- These are reusable lambda functions. One lambda function can do multiple jobs based on event/environment variables.
        
 12. Create step functions/state machine/workflow using scripts in "./step_functions". 
     Important!!: Replace the lambda function ARN ("Resource":) with proper one from above step.
     Note: Here idea is, seperate indipendent group of tasks in a single state machine and use the master state machine to orchestrate all.
	 
	 State Machines involved in Sample Data Pipeline:
			data_pipeline_v2.0_Launch_EMR_Cluster.json
				- To launch EMR cluster 
				
			data_pipeline_v2.0_Terminate_EMR_Cluster.json
				- Toterminate Cluster

			data_pipeline_v2.0_Add_EMR_Workers_data.json
				- Add additional EMR worker

			data_pipeline_v2.0_Dimension_Process.json
				- Process dimension data

			data_pipeline_v2.0_Fact_Process.json
				- Process Fact data

			data_pipeline_v2.0_Master.json
				- Call above state machines with below squence:
					 i. data_pipeline_v2.0_Launch_EMR_Cluster
					ii. data_pipeline_v2.0_Dimension_Process
				   iii. data_pipeline_v2.0_Add_EMR_Workers_data (considering more node needed for Fact data processing)
					iv. data_pipeline_v2.0_Fact_Process
					 v. data_pipeline_v2.0_Terminate_EMR_Cluster
		 
	 
 13. Schedule the master step function with cloudwatch. If any of the child step fails, we can only the the related step functions manually, as we seperated independet tasks in steps functions.
     
 
 14. we can test run by placing source files into corresponding landing folder and running steps manually. Sample datafiles are provided in "./data" folder, filnames are table names.

 
 15. Security
    - Use least privileged IAM Roles to execute services (Step Functions & Lambda)
	- Isolate using VPC (even S3 access policy strict to VPC)
	- Provide role based access on S3 data to users/groups based of least privilege

	
 
 