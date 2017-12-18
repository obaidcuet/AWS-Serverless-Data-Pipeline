## check status of the emr cluster

## libraries to load configuration from S3
from io import StringIO
import configparser

## boto3, python SDK for AWS Services
import boto3

## to read env variables
import os

## load configuration file from S3
s3 = boto3.client('s3')
config_file_data = s3.get_object(Bucket=os.environ['Config_File_S3_Bucket'], Key=os.environ['Config_File_S3_Key'])['Body'].read().decode('utf-8')

## parse confifuration file
config = configparser.ConfigParser()
config.sections()
config.readfp(StringIO(config_file_data))

## get required configuration variables
emr_region = config['basic']['emr_region']
emr_name = config['basic']['emr_name']

## initiate client
client_emr = boto3.client(
    'emr',
    region_name= emr_region,  
)

## invoke lambda function
def lambda_handler(event, context):
    return_val = { "Status" : "NOTRUNNING" }

    # get current running clusters with same name
    response_list_cluster = client_emr.list_clusters(
        ClusterStates=['STARTING','BOOTSTRAPPING','RUNNING','WAITING']
    )

    for dic in response_list_cluster['Clusters']:
        if dic['Name']==emr_name: # cluster running with same name
            return_val = { "Status" : "RUNNING" }
        
    return return_val
