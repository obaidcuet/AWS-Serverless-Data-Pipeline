## libraries to load configuration from S3
from io import StringIO
import configparser

## to read env variables
import os

## boto3, python SDK for AWS Services
import boto3

## to get current timestamp
import datetime
import time

## to conver event dictionary to json string
import json

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

    if "nextStateMachineArn" in event.keys():  # is statemachine name is passed as event use that one (priority)
        state_machine_arn = event["nextStateMachineArn"]
    else: # by default get statemachine name from environment variable
        state_machine_arn = os.environ['stateMachineArn']

    # start state machine
    response_start_sfn = client_sfn.start_execution(
                           stateMachineArn = state_machine_arn,
                           name = state_machine_arn.split(':')[-1]+ '_' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S'),
                           input = json.dumps(event)
                           )
    
    return_val = { "executionArn" : response_start_sfn['executionArn'], "Status" : "SUBMITTED" }
    
    return return_val
