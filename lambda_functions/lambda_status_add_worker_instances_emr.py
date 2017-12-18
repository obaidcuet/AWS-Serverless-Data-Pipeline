## libraries to load configuration from S3
from io import StringIO
import configparser

## to read env variables
import os

## boto3, python SDK for AWS Services
import boto3

## load configuration file from S3
s3 = boto3.client('s3')
config_file_data = s3.get_object(Bucket=os.environ['Config_File_S3_Bucket'], Key=os.environ['Config_File_S3_Key'])['Body'].read().decode('utf-8')

## parse confifuration file
config = configparser.ConfigParser()
config.sections()
config.readfp(StringIO(config_file_data))

## get all the configuration variables
#[basic]
emr_region = config['basic']['emr_region']

## initiate client
client_emr = boto3.client(
    'emr',
    region_name= emr_region,  
)

## invoke lambda function
def lambda_handler(event, context):
    ## check additional instance request status
    return_status ='ADDING'
    cluster_id =  event['ClusterId']
    worker_instance_fleet_id = event['WorkerInstanceFleetId']
    target_worker_count = event['TargetTotalWorkers']
    
    # wait until (new_spot_worker_count+ondemand_worker_count) instances are in running state
    current_runnung_workers=len(
        client_emr.list_instances(
            ClusterId=cluster_id,
            InstanceFleetId= worker_instance_fleet_id,
            InstanceStates=['RUNNING']
        )['Instances']
    )
    
    current_adding_workers=len(
        client_emr.list_instances(
            ClusterId=cluster_id,
            InstanceFleetId= worker_instance_fleet_id,
            InstanceStates=['PROVISIONING', 'BOOTSTRAPPING','AWAITING_FULFILLMENT']
        )['Instances']
    )
    
    current_stopped_workers=len(
        client_emr.list_instances(
            ClusterId=cluster_id,
            InstanceFleetId= worker_instance_fleet_id,
            InstanceStates=['TERMINATED']
        )['Instances']
    )
    
    if current_runnung_workers >= target_worker_count: # in case of transition we sum of adding+running could be more, so >=
        return_status = "SUCCESS"
    else:    
        if (current_runnung_workers+current_adding_workers) == target_worker_count:
            return_status = 'ADDING'
        elif (current_stopped_workers > 0) and (current_adding_workers == 0):
            return_status = 'ERROR'
    
    return {  "ClusterId" : cluster_id, 
              "WorkerInstanceFleetId" : worker_instance_fleet_id, 
              "TargetTotalWorkers" : target_worker_count, 
              "Status" : return_status
           }
