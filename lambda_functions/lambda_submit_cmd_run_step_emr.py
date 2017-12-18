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
    ## command to run as steps in EMR
    if "NextStepNameAndCmd" in event.keys(): # is NextStepNameAndCmd name is passed as event use that one (priority)
        step_name = event["NextStepNameAndCmd"]["Step_Name"]
        cmd_run = event["NextStepNameAndCmd"]["Cmd_Run"]
    else: # by defauly, get current step function name from env variable
        step_name = os.environ['Step_Name']
        cmd_run = os.environ['Cmd_Run']

    # submit the step
    response_move_files = client_emr.add_job_flow_steps(
        JobFlowId=event["ClusterId"],
        Steps=[
            {
                'Name': step_name,
                'ActionOnFailure': 'CANCEL_AND_WAIT',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': cmd_run.split()
                }
            },
        ]
    )
    
    return {"ClusterId" : event['ClusterId'], "StepId" : response_move_files['StepIds'][0], "Status" : "SUBMITTED" }
	
