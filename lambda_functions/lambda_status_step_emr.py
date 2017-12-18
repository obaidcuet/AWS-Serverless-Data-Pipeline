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

## parse configuration file
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
    return_val = None
	
	# get staus of the step
    response_status_step = client_emr.describe_step(
        ClusterId=event['ClusterId'],
        StepId=event['StepId']
    )
    
    step_status = response_status_step['Step']['Status']['State']
    
    # check status
    if step_status == 'CANCELLED' or step_status == 'FAILED':
        return_val = { "ClusterId" : event['ClusterId'], 'StepId' : event['StepId'], "Status" : "ERROR" }
    elif step_status == 'COMPLETED':
        return_val = { "ClusterId" : event['ClusterId'], 'StepId' : event['StepId'], "Status" : "SUCCESS" }
    else:
        return_val = { "ClusterId" : event['ClusterId'], 'StepId' : event['StepId'], "Status" : "SUBMITTED" }
		
    return return_val