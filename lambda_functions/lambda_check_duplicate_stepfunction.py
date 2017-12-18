## check status of the step function

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

## initiate stepfunction client
client_sfn = boto3.client('stepfunctions', region_name= emr_region)

## invoke lambda function
def lambda_handler(event, context):

    if "currentStepName" in event.keys(): # is statemachine name is passed as event use that one (priority)
    	current_step_name = event["currentStepName"]
    else: # by defauly, get current step function name from env variable
        current_step_name = os.environ['currentStepName'] 
    	
    	
    return_val = { "Status" : "NOTRUNNING" }
    
    for dic in client_sfn.list_state_machines()['stateMachines']: # list step functions
        if dic['name']== current_step_name:
            # list step functions with status RUNNING
            if len(client_sfn.list_executions( stateMachineArn=dic['stateMachineArn'],statusFilter='RUNNING')['executions']) > 1: # more than 1 RUNNING(including current one)
                return_val = { "Status" : "RUNNING" }
            else:
                return_val = { "Status" : "NOTRUNNING" }
                
    return return_val
