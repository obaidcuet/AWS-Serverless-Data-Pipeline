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

## initiate client
client_emr = boto3.client(
    'emr',
    region_name= emr_region,  
)

## invoke lambda function
def lambda_handler(event, context):
    return_val = None

    # get current status of the cluster
    response_start = client_emr.describe_cluster(
        ClusterId=event["ClusterId"]
    )
    
    emr_status = response_start['Cluster']['Status']['State']
    
    # check status
    if emr_status == 'WAITING' or emr_status == 'RUNNING':
        return_val = { "ClusterId" : event['ClusterId'], "Status" : "STARTED" }
    elif emr_status == 'TERMINATING' or emr_status == 'TERMINATED' or emr_status == 'TERMINATED_WITH_ERRORS':
        return_val =  { "ClusterId" : event['ClusterId'], "Status" : "STOPPED" }
    else:
        return_val = { "ClusterId" : event['ClusterId'], "Status" : "STARTING" }
        
    return return_val
