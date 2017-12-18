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
client_sfn = boto3.client(
    'stepfunctions',
    region_name= emr_region,  
)


## invoke lambda function
def lambda_handler(event, context):
    return_val = None
    	
    response_status_sfn = client_sfn.describe_execution(
        executionArn = event['executionArn']
    )
    
    sfn_status = response_status_sfn['status']
    
    # check status
    if sfn_status == 'FAILED' or sfn_status == 'TIMED_OUT' or sfn_status == 'ABORTED':
        return_val = { "executionArn" : event['executionArn'], "Status" : "ERROR" }
    elif sfn_status == 'SUCCEEDED':
        return_val = { "executionArn" : event['executionArn'], "Status" : "SUCCESS" }
    else:
        return_val = { "executionArn" : event['executionArn'], "Status" : "RUNNING" }

    return return_val