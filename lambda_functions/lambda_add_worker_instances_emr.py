## this lambda function will increase current number of worket by variable mention in the config file 'spot_worker_increment_count'

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

#[instances]
worker_instance_type = config['instances']['worker_instance_type']
ondemand_worker_count = int(config['instances']['ondemand_worker_count'])

#[spot]
spot_worker_count = int(config['spot']['spot_worker_count'])
spot_worker_increment_count = int(config['spot']['spot_worker_increment_count'])

## initiate client
client_emr = boto3.client(
    'emr',
    region_name= emr_region,  
)

## invoke lambda function
def lambda_handler(event, context):
    
    # get cluster id from event
    cluster_id=event['ClusterId']
    
    # get worket instance fleet id, for later scaleup purpose 
    worker_instance_fleet_id=''
    for dic in client_emr.list_instance_fleets( ClusterId=cluster_id)['InstanceFleets']:
        if dic['InstanceFleetType']=='CORE':
            worker_instance_fleet_id=dic['Id']
    
    # add additiona instances 
    # try with spot for 10 minutes, it failes then go for on demand
    current_worker_count = len(
        client_emr.list_instances(
            ClusterId=cluster_id,
            InstanceFleetId= worker_instance_fleet_id,
            InstanceStates=['RUNNING']
        )['Instances']
    )
    
    # total spot worker after increment by spot_worker_increment_count
    new_spot_worker_count = current_worker_count - ondemand_worker_count + spot_worker_increment_count
    
    response_add_instances = client_emr.modify_instance_fleet(
        ClusterId=cluster_id,
        InstanceFleet={
            'InstanceFleetId': worker_instance_fleet_id,
            'TargetOnDemandCapacity' : ondemand_worker_count,
            'TargetSpotCapacity': new_spot_worker_count
        }
    )
    
    return {  "ClusterId" : cluster_id, 
              "WorkerInstanceFleetId" : worker_instance_fleet_id, 
              "TargetTotalWorkers" : new_spot_worker_count+ondemand_worker_count, 
              "Status" : "ADDING" 
           }



