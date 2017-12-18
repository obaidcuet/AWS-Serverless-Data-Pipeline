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


## S3 location to store state info
state_info_file_s3_bucket = os.environ['State_Info_File_S3_Bucket']
state_info_file_s3_key = os.environ['State_Info_File_S3_Key']


## S3 client
client_s3 = boto3.client(
    's3',
    region_name= emr_region
)


## invoke lambda function
def lambda_handler(event, context):
    return_val = None
    
    # write to s3
    client_s3.put_object(Body=event['ClusterId'], Bucket=state_info_file_s3_bucket, Key=state_info_file_s3_key)

    # read from s3 again to for verification ourpose
    ClusterId = client_s3.get_object(Bucket=state_info_file_s3_bucket, Key=state_info_file_s3_key)['Body'].read().decode('utf-8')

    # make suure cluster is written properly state infor file on s3
    if ClusterId == event['ClusterId']:
        return_val = {"ClusterId":ClusterId, "Status": "SUCCESS" }
    else:
        return_val = {"ClusterId":ClusterId, "Status": "FAIL" }
        
    return return_val